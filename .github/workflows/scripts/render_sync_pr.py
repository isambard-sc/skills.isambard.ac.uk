#!/usr/bin/env python3
"""Write the body of a docs sync PR, pairing each docs change with the skill
lines that follow it.

The review of a sync PR is one question: do the skill changes say what the
docs changes say? The docs are the source of truth. So for each change the
body shows the docs hunk (from docs_changes.py --hunks) above the skill lines
it led to, with a link to those lines in the PR's Files changed tab.

The sync agent only says which docs hunk goes with which skill lines (its
final answer, a JSON object; see docs_sync.sh). Both diffs are drawn here from
trusted sources, so the agent can't misquote either side, and anything its
answer leaves out is listed under "Not covered", so nothing is hidden by a
bad answer. If the answer can't be read at all, every change ends up there.

Usage (in the sync worktree, after the agent's edits are committed):
  render_sync_pr.py --hunks HUNKS.json --agent-output OUT --base SHA
      --repo-url URL [--pr N] --from SHA --to SHA --checks FILE [--checks-failed]
      [--report REPORT.md] [--agent-link MD]
"""

import argparse
import hashlib
import json
import re
import subprocess
import sys

DOCS_SITE = "https://docs.isambard.ac.uk"
# GitHub caps a PR body at 65,536 characters.
BUDGET = 60_000
MAX_BLOCK_LINES = 60  # lines of one diff block shown before cutting it short


def fence_for(text):
    """A code fence longer than any backtick run in text, so a ``` line in
    the diff (indented one space by the diff) can't close it early."""
    longest = max((len(run) for run in re.findall(r"`+", text)), default=0)
    return "`" * max(3, longest + 1)


def clean(text, limit):
    """Agent-written text, made safe for one line of the public PR body: no
    HTML, no @-mentions (they would notify people), no line breaks."""
    text = " ".join(str(text or "").split())[:limit]
    return text.replace("<", "&lt;").replace(">", "&gt;").replace("@", "&#64;")


def skill_hunks(base):
    """The -U0 hunks of the skill changes since base: (path, start, end,
    lines), where start..end are new-file lines (a pure deletion covers the
    line before it and the one after)."""
    out = subprocess.run(
        ["git", "diff", "-U0", "--no-color", base, "HEAD", "--", "site", "README.md"],
        capture_output=True, text=True, check=True,
    ).stdout
    hunks, path = [], None
    for line in out.splitlines(keepends=True):
        if line.startswith("+++ "):
            path = line[6:].rstrip("\n") if line.startswith("+++ b/") else None
        elif line.startswith(("--- ", "diff ", "index ", "new file", "deleted file", "similarity", "rename ")):
            continue
        elif line.startswith("@@"):
            m = re.match(r"@@ -\d+(?:,\d+)? \+(\d+)(?:,(\d+))? @@", line)
            start, length = int(m.group(1)), int(m.group(2) or 1)
            end = start + length - 1 if length else start + 1
            hunks.append({"path": path, "start": start, "end": end, "lines": [], "next": start})
        elif hunks and line[:1] in "+-":
            h = hunks[-1]
            # Each line with its new-file number (None for a removed line), so
            # a section can show just the added lines it cites.
            num = None
            if line[0] == "+":
                num, h["next"] = h["next"], h["next"] + 1
            h["lines"].append((num, line if line.endswith("\n") else line + "\n"))
    return [h for h in hunks if h["path"]]


def read_answer(path):
    """The agent's JSON answer: the last {...} object in its output."""
    try:
        text = open(path, encoding="utf-8").read()
    except OSError:
        return None, "the agent's answer is missing"
    for start in [m.start() for m in re.finditer(r"\{", text)]:
        try:
            data, _ = json.JSONDecoder().raw_decode(text[start:])
        except ValueError:
            continue
        if isinstance(data, dict) and "changes" in data:
            return data, None
    return None, "the agent's answer has no JSON object with a \"changes\" list"


class Body:
    def __init__(self, args):
        self.args = args
        self.out = []
        self.budget = BUDGET
        self.cut = 0

    def line(self, text=""):
        self.out.append(text)
        self.budget -= len(text) + 1

    def diff_block(self, lines):
        lines = [l[1] if isinstance(l, tuple) else l for l in lines]
        shown = lines[:MAX_BLOCK_LINES]
        if sum(len(l) for l in shown) > self.budget - 5_000:
            self.cut += 1
            self.line("*Not shown, to keep this description under GitHub's size limit.*")
            return
        text = "".join(shown).rstrip("\n")
        fence = fence_for(text)
        self.line(f"{fence}diff")
        for l in text.split("\n"):
            self.line(l)
        self.line(fence)
        if len(lines) > len(shown):
            self.line(f"*{len(lines) - len(shown)} more lines not shown.*")

    def skill_link(self, path, start, end):
        h = hashlib.sha256(path.encode()).hexdigest()
        pr = self.args.pr or "PR"
        anchor = f"R{start}" if start == end else f"R{start}-R{end}"
        where = f"line {start}" if start == end else f"lines {start}–{end}"
        return f"[`{path.split('/skills/', 1)[-1]}` {where}]({self.args.repo_url}/pull/{pr}/files#diff-{h}{anchor})"


def docs_link(h):
    links = []
    for url in h["urls"]:
        text = url[len(DOCS_SITE):].strip("/")
        if h.get("section"):
            title, anchor = h["section"]
            links.append(f"[{text} › {clean(title, 120)}]({url}#{anchor})")
        else:
            links.append(f"[{text}]({url})")
    prefix = "" if h["is_page"] else f"`{h['path'].rsplit('/', 1)[-1]}`, included in "
    return prefix + ", ".join(links)


def overlaps(hunk, start, end):
    return hunk["start"] <= end + 1 and start <= hunk["end"] + 1


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--hunks", required=True)
    ap.add_argument("--agent-output", required=True)
    ap.add_argument("--base", required=True, help="skills commit the sync branched from")
    ap.add_argument("--repo-url", required=True)
    ap.add_argument("--pr", default="", help="PR number, for links to its lines (default: a placeholder)")
    ap.add_argument("--from", dest="docs_from", required=True)
    ap.add_argument("--to", dest="docs_to", required=True)
    ap.add_argument("--checks", required=True, help="validator output")
    ap.add_argument("--checks-failed", action="store_true")
    ap.add_argument("--report", help="docs_changes.py report, for cited URLs with no docs page")
    ap.add_argument("--agent-link", default="")
    args = ap.parse_args()

    docs = {h["id"]: h for h in json.load(open(args.hunks, encoding="utf-8"))}
    skill = skill_hunks(args.base)
    answer, problem = read_answer(args.agent_output)
    answer = answer or {"changes": [], "unpaired": [], "warnings": []}
    skill_paths = {h["path"] for h in skill}

    dropped = []

    def refs(items):
        """The agent's (path, start, end) references that point at changed lines."""
        good = []
        for r in items or []:
            try:
                path, (a, b) = str(r["file"]), (int(r["lines"][0]), int(r["lines"][-1]))
            except (KeyError, TypeError, ValueError, IndexError):
                dropped.append(1)
                continue
            a, b = min(a, b), max(a, b)
            if path in skill_paths and any(h["path"] == path and overlaps(h, a, b) for h in skill):
                good.append((path, a, b))
            else:
                dropped.append(1)
        return good

    def docs_ids(ids):
        good = [i for i in ids or [] if i in docs]
        dropped.extend([1] * (len(ids or []) - len(good)))
        return good

    used_docs, used_skill = set(), set()
    b = Body(args)
    b.line("**To review:** the docs are the source of truth. For each change below, check "
           "that the skill lines say what the docs lines say: nothing missing, and nothing the "
           "docs don't say. Each skill link opens those lines in **Files changed**. Docs "
           f"`{args.docs_from[:12]}`..`{args.docs_to[:12]}`; merging records "
           f"`{args.docs_to[:12]}` as synced.")
    b.line()

    # Sections first, so references dropped while building them can be
    # reported in the alerts above them.
    head, b = b, Body(args)
    b.budget = head.budget - 2_000
    alerts = []

    def flush_alerts():
        if dropped:
            alerts.append(f"{len(dropped)} of the agent's references pointed at no changed "
                          "skill lines or no docs hunk and were left out; the changes they "
                          "meant are under Not covered.")
        if alerts:
            head.line("> [!WARNING]")
            for a in alerts:
                head.line(f"> - {a}")
            head.line()
        head.out += b.out

    if args.checks_failed:
        alerts.append("The skill validators failed: see Validation below.")
    if problem:
        alerts.append(f"Couldn't read the agent's pairing ({problem}), so every change is "
                      "under Not covered.")
    alerts += [clean(w, 300) for w in answer.get("warnings") or [] if str(w).strip()]

    n = 0
    for change in answer.get("changes") or []:
        ids = docs_ids(change.get("docs"))
        srefs = refs(change.get("skill"))
        if not ids and not srefs:
            continue
        n += 1
        b.line(f"### {n}. {clean(change.get('title'), 120) or 'Change'}")
        b.line()
        for i in ids:
            used_docs.add(i)
            b.line(f"**Docs** · {docs_link(docs[i])}")
            b.diff_block(docs[i]["lines"])
        if not ids:
            b.line("**Docs** · no docs change given")
        for path, start, end in srefs:
            b.line(f"**Skill** · {b.skill_link(path, start, end)}")
            lines = []
            for k, h in enumerate(skill):
                if h["path"] == path and overlaps(h, start, end):
                    used_skill.add(k)
                    lines += [(num, l) for num, l in h["lines"]
                              if num is None or start <= num <= end]
            b.diff_block(lines)
        if not srefs:
            b.line("**Skill** · no change")
        note = clean(change.get("note"), 400)
        if note:
            b.line(note)
        b.line()

    unpaired = []
    for item in answer.get("unpaired") or []:
        for path, start, end in refs([item]):
            for k, h in enumerate(skill):
                if h["path"] == path and overlaps(h, start, end):
                    used_skill.add(k)
            unpaired.append(f"- {b.skill_link(path, start, end)}: {clean(item.get('why'), 300)}")
    if unpaired:
        b.line("### Not paired with a docs change")
        b.line()
        for u in unpaired:
            b.line(u)
        b.line()

    left_docs = [i for i in docs if i not in used_docs]
    left_skill = [h for k, h in enumerate(skill) if k not in used_skill]
    if left_docs or left_skill:
        b.line("### Not covered")
        b.line()
        b.line("The agent's answer didn't account for these. Check them against the docs as well.")
        b.line()
        for i in left_docs:
            b.line(f"**Docs** · {docs_link(docs[i])}")
            b.diff_block(docs[i]["lines"])
        for h in left_skill:
            b.line(f"**Skill** · {b.skill_link(h['path'], h['start'], h['end'])}")
            b.diff_block(h["lines"])
        b.line()

    if args.report:
        report = open(args.report, encoding="utf-8").read()
        m = re.search(r"^### Cited URLs with no docs page\n.*", report, re.M | re.S)
        if m:
            b.line(m.group(0).rstrip())
            b.line()

    checks = open(args.checks, encoding="utf-8").read().rstrip()
    b.line(f"<details{' open' if args.checks_failed else ''}><summary>Validation: "
           f"{'failed' if args.checks_failed else 'passed'}</summary>")
    b.line()
    b.line("```")
    b.line(checks.replace("```", "'''"))
    b.line("```")
    b.line()
    b.line("</details>")
    b.line()
    b.line("---")
    b.line("Opened by `.github/workflows/scripts/docs_sync.sh`.")
    if args.agent_link:
        b.line(f"🤖 Generated with {args.agent_link}")
    flush_alerts()
    sys.stdout.write("\n".join(head.out) + "\n")


if __name__ == "__main__":
    main()
