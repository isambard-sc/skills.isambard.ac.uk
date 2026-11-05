#!/usr/bin/env python3
"""Report skills whose source docs pages changed after the skill last did.

Each SKILL.md names the docs.isambard.ac.uk pages it was derived from in
`metadata.source_url` and `metadata.supplementary_urls`. This maps those URLs
to Markdown files in a local checkout of the docs repo (following
pymdownx.snippets `--8<--` includes), then compares the docs repo history for
those files since the skill was last synced: `metadata.docs_commit` (the docs
commit the skill was checked against) if set, otherwise the date of the skill
directory's last commit here.

A skill is:
  ok      no source page changed since the skill was last committed
  drift   at least one source page changed since then
  broken  a source URL doesn't resolve to a page in the docs repo

Unlike the other scripts in this directory this one is report-only: it always
exits 0 unless --fail-on is given, because drift is a prompt for a human (or an
agent opening a PR for a human) to look, not a build failure.

The docs repo is private while this repo, its Actions logs and issues are
public, so the Markdown report deliberately omits docs commit subjects and
authors. Pass --show-subjects for local runs only.

Usage (from the repo root):
  python3 .github/workflows/scripts/check_docs_drift.py --docs-repo ../docs.isambard.ac.uk
"""

import argparse
import json
import os
import re
import subprocess
import sys

from skills_lib import discover_skills, load_frontmatter

DOCS_SITE = "https://docs.isambard.ac.uk"

# Pages that change constantly for reasons a skill shouldn't track: a skill
# links to service status so the agent checks it live, not to copy its content.
VOLATILE_PREFIXES = ("service-status/",)

SNIPPET_RE = re.compile(r'^\s*--8<--\s+"([^"]+)"', re.MULTILINE)


def git(repo, *args):
    return subprocess.run(
        ["git", "-C", repo, *args], check=True, capture_output=True, text=True
    ).stdout.strip()


def url_to_page(url, docs_repo):
    """Map a docs site URL to a repo-relative Markdown path, or None."""
    if not url.startswith(DOCS_SITE):
        return None
    rel = url[len(DOCS_SITE):].split("#")[0].strip("/")
    candidates = [f"docs/{rel}/index.md"] if rel else ["docs/index.md"]
    if rel:
        candidates.insert(0, f"docs/{rel}.md")
    for c in candidates:
        if os.path.isfile(os.path.join(docs_repo, c)):
            return c
    return None


def with_snippets(page, docs_repo):
    """Return the page plus any files it pulls in via --8<-- (base_path is
    !relative in mkdocs.yml, so includes resolve against the page's directory).
    """
    paths = [page]
    with open(os.path.join(docs_repo, page), encoding="utf-8") as f:
        text = f.read()
    for inc in SNIPPET_RE.findall(text):
        p = os.path.normpath(os.path.join(os.path.dirname(page), inc))
        if os.path.isfile(os.path.join(docs_repo, p)):
            paths.append(p)
    return paths


def check_skill(skill, docs_repo, show_subjects):
    data, err = load_frontmatter(os.path.join(skill["dir"], "SKILL.md"))
    meta = (data or {}).get("metadata") or {}
    urls = [meta.get("source_url")] + list(meta.get("supplementary_urls") or [])
    urls = [u for u in urls if u]

    result = {
        "skill": skill["name"],
        "dir": skill["dir"],
        "status": "ok",
        "broken_urls": [],
        "watched_paths": [],
        "changed_paths": [],
        "commits": [],
    }
    if err:
        result.update(status="broken", error=err)
        return result
    if not urls:
        result.update(status="broken", error="no metadata.source_url")
        return result

    for url in urls:
        rel = url[len(DOCS_SITE):].lstrip("/") if url.startswith(DOCS_SITE) else url
        if rel.startswith(VOLATILE_PREFIXES):
            continue
        page = url_to_page(url, docs_repo)
        if page is None:
            result["broken_urls"].append(url)
        else:
            result["watched_paths"].extend(with_snippets(page, docs_repo))
    result["watched_paths"] = sorted(set(result["watched_paths"]))

    baseline = git(".", "log", "-1", "--format=%cI", "--", skill["dir"])
    result["skill_last_commit"] = baseline
    if meta.get("docs_commit"):
        # Set by whoever last synced the skill: exact, and unaffected by
        # unrelated edits (renames, typo fixes) to the skill directory.
        try:
            base_rev = git(docs_repo, "rev-parse", "--verify", f"{meta['docs_commit']}^{{commit}}")
        except subprocess.CalledProcessError:
            result.update(status="broken", error=f"metadata.docs_commit {meta['docs_commit']} not in docs repo")
            return result
    else:
        # Fall back to the docs commit current when the skill was last touched.
        base_rev = git(docs_repo, "rev-list", "-1", f"--before={baseline}", "HEAD")
    result["docs_base_rev"] = base_rev

    if result["watched_paths"]:
        fmt = "%h %cs %s" if show_subjects else "%h %cs"
        log = git(docs_repo, "log", f"--format={fmt}", f"{base_rev}..HEAD",
                  "--", *result["watched_paths"])
        result["commits"] = log.splitlines() if log else []
        changed = git(docs_repo, "diff", "--name-only", f"{base_rev}..HEAD",
                      "--", *result["watched_paths"])
        result["changed_paths"] = changed.splitlines() if changed else []

    if result["broken_urls"]:
        result["status"] = "broken"
    elif result["changed_paths"]:
        result["status"] = "drift"
    return result


def markdown(results, docs_head):
    lines = [
        "## Skills vs docs drift",
        "",
        f"Docs repo at `{docs_head[:12]}`.",
        "",
        "| Skill | Status | Docs commits since skill | Changed pages |",
        "|---|---|---|---|",
    ]
    for r in results:
        icon = {"ok": "✅ ok", "drift": "⚠️ drift", "broken": "❌ broken"}[r["status"]]
        changed = "<br>".join(f"`{p}`" for p in r["changed_paths"]) or "—"
        lines.append(f"| `{r['skill']}` | {icon} | {len(r['commits'])} | {changed} |")

    for r in results:
        if r["status"] == "ok":
            continue
        lines += ["", f"### `{r['skill']}`", ""]
        if r.get("error"):
            lines.append(f"- Frontmatter: {r['error']}")
        for u in r["broken_urls"]:
            lines.append(f"- Source URL doesn't map to a docs page: {u}")
        if r["changed_paths"]:
            lines.append(f"- Docs changed since `{r['docs_base_rev'][:12]}` "
                         f"(skill last committed {r['skill_last_commit']}); "
                         f"review the diff with:")
            lines += ["", "```bash",
                      f"git -C <docs-repo> diff {r['docs_base_rev'][:12]}..HEAD -- "
                      + " ".join(r["changed_paths"]),
                      "```"]
    return "\n".join(lines) + "\n"


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--docs-repo", required=True, help="path to a docs.isambard.ac.uk checkout with full history")
    ap.add_argument("--json", help="also write machine-readable results here")
    ap.add_argument("--show-subjects", action="store_true",
                    help="include docs commit subjects (local use only: the docs repo is private)")
    ap.add_argument("--fail-on", choices=["broken", "drift"],
                    help="exit 1 if any skill is broken (or, with drift, broken or drifted)")
    args = ap.parse_args()

    results = [check_skill(s, args.docs_repo, args.show_subjects) for s in discover_skills()]
    docs_head = git(args.docs_repo, "rev-parse", "HEAD")

    sys.stdout.write(markdown(results, docs_head))
    if args.show_subjects:
        for r in results:
            if r["commits"]:
                print(f"\n{r['skill']}:")
                print("\n".join(f"  {c}" for c in r["commits"]))

    if args.json:
        with open(args.json, "w", encoding="utf-8") as f:
            json.dump({"docs_head": docs_head, "skills": results}, f, indent=2)

    failing = {"broken": {"broken"}, "drift": {"broken", "drift"}}.get(args.fail_on, set())
    sys.exit(1 if any(r["status"] in failing for r in results) else 0)


if __name__ == "__main__":
    main()
