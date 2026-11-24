#!/usr/bin/env python3
"""Report which skills cite docs pages that changed between two docs commits.

Each SKILL.md names the docs.isambard.ac.uk pages it was derived from in
`metadata.source_url` and `metadata.supplementary_urls`. This maps those URLs
to Markdown files in a checkout of the docs repo at the --to commit (following
pymdownx.snippets `--8<--` includes, so example scripts count as part of the
page), then diffs those files between --from and --to.

It writes a Markdown report (changed pages, the skills citing each, and cited
URLs that no longer map to a page) to stdout. With --diff, it writes a unified
diff of the changed pages to a file, each hunk header tagged with an id
([D1], [D2], ...) that the sync agent uses to say which docs change each skill
edit follows. With --hunks, it writes the same hunks as JSON for
render_sync_pr.py. Both are empty when no cited page changed.

The docs repo is private while this repo and its pull requests are public, so
the report contains docs paths and commit hashes only, never commit subjects
or authors, and the diff is built from the files with what the published site
doesn't show (front matter and HTML comments, closed or not) removed. The
hunks go into public PR bodies verbatim.

Usage (from the repo root):
  python3 .github/workflows/scripts/docs_changes.py \\
      --docs-repo ../docs.isambard.ac.uk --from <commit> [--to <commit>]
"""

import argparse
import difflib
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
# An unclosed comment hides the rest of the page, so it runs to the end.
COMMENT_RE = re.compile(r"<!--.*?(?:-->|\Z)", re.DOTALL)
# YAML front matter: page settings the site doesn't display.
FRONT_MATTER_RE = re.compile(r"\A---[ \t]*\n.*?^---[ \t]*\n", re.DOTALL | re.MULTILINE)


def git(repo, *args):
    return subprocess.run(
        ["git", "-C", repo, *args], check=True, capture_output=True, text=True
    ).stdout


def exists(repo, rev, path):
    return subprocess.run(
        ["git", "-C", repo, "cat-file", "-e", f"{rev}:{path}"], capture_output=True
    ).returncode == 0


def url_to_page(url, repo, rev):
    """Map a docs site URL to a repo-relative Markdown path at rev, or None."""
    rel = url[len(DOCS_SITE):].split("#")[0].strip("/")
    candidates = [f"docs/{rel}.md", f"docs/{rel}/index.md"] if rel else ["docs/index.md"]
    return next((c for c in candidates if exists(repo, rev, c)), None)


def published_text(repo, rev, path):
    """The file at rev without what the site doesn't display (front matter
    and HTML comments), or "" if it doesn't exist. The diff of this goes into
    public PRs, so this is the line between the private repo and the public
    one: keep it in step with anything else the docs build hides."""
    if not exists(repo, rev, path):
        return ""
    text = git(repo, "show", f"{rev}:{path}")
    return COMMENT_RE.sub("", FRONT_MATTER_RE.sub("", text, count=1))


def with_snippets(page, repo, rev):
    """Return the page plus any files it pulls in via --8<-- (base_path is
    !relative in mkdocs.yml, so includes resolve against the page's directory).
    """
    paths = [page]
    for inc in SNIPPET_RE.findall(git(repo, "show", f"{rev}:{page}")):
        p = os.path.normpath(os.path.join(os.path.dirname(page), inc))
        if exists(repo, rev, p):
            paths.append(p)
    return paths


def cited_pages(only=None):
    """Map each cited docs URL (without fragment) to the skills citing it."""
    pages = {}
    for skill in discover_skills():
        if only and skill["name"] != only:
            continue
        data, err = load_frontmatter(os.path.join(skill["dir"], "SKILL.md"))
        if err:
            continue
        meta = data.get("metadata") or {}
        urls = [meta.get("source_url")] + list(meta.get("supplementary_urls") or [])
        for url in filter(None, urls):
            url = url.split("#")[0]
            if not url.startswith(DOCS_SITE):
                continue
            rel = url[len(DOCS_SITE):].strip("/")
            if (rel + "/").startswith(VOLATILE_PREFIXES):
                continue
            pages.setdefault(url, set()).add(skill["name"])
    return pages


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--docs-repo", required=True, help="path to a docs.isambard.ac.uk clone")
    ap.add_argument("--from", dest="base", required=True, help="docs commit the skills were last synced with")
    ap.add_argument("--to", default="HEAD", help="docs commit to compare against (default: HEAD)")
    ap.add_argument("--skill", help="only check the pages this skill cites")
    ap.add_argument("--diff", help="write the diff of the changed pages to this file")
    ap.add_argument("--hunks", help="write the diff's hunks as JSON (for render_sync_pr.py) to this file")
    args = ap.parse_args()

    repo = args.docs_repo
    base = git(repo, "rev-parse", "--verify", f"{args.base}^{{commit}}").strip()
    head = git(repo, "rev-parse", "--verify", f"{args.to}^{{commit}}").strip()

    pages = cited_pages(args.skill)
    if args.skill and not pages:
        sys.exit(f"skill {args.skill!r} not found or cites no docs pages")

    by_path, broken = {}, []
    for url, skills in sorted(pages.items()):
        page = url_to_page(url, repo, head)
        if page is None:
            broken.append((url, skills))
            continue
        for path in with_snippets(page, repo, head):
            entry = by_path.setdefault(path, {"urls": set(), "skills": set(), "is_page": False})
            entry["is_page"] |= path == page
            entry["urls"].add(url)
            entry["skills"] |= skills

    changed = git(repo, "diff", "--name-only", base, head, "--", *by_path).split()

    lines = ["## Docs changes", "", f"Docs `{base[:12]}`..`{head[:12]}`.", ""]
    if changed:
        lines += ["### Changed pages", ""]
        for path in changed:
            e = by_path[path]
            urls = ", ".join(sorted(e["urls"]))
            skills = ", ".join(f"`{s}`" for s in sorted(e["skills"]))
            lines.append(f"- `{path}` ({urls}): cited by {skills}")
        lines.append("")
    else:
        lines += ["No cited page changed.", ""]
    if broken:
        lines += ["### Cited URLs with no docs page", ""]
        for url, skills in broken:
            lines.append(f"- {url}: cited by " + ", ".join(f"`{s}`" for s in sorted(skills)))
        lines.append("")
    sys.stdout.write("\n".join(lines))

    hunks = []
    for path in changed:
        old = published_text(repo, base, path).splitlines(keepends=True)
        new = published_text(repo, head, path).splitlines(keepends=True)
        e = by_path[path]
        for group in difflib.SequenceMatcher(None, old, new).get_grouped_opcodes(3):
            lines = []
            for tag, i1, i2, j1, j2 in group:
                if tag == "equal":
                    lines += [" " + l for l in old[i1:i2]]
                    continue
                lines += ["-" + l for l in old[i1:i2]]
                lines += ["+" + l for l in new[j1:j2]]
            hunks.append({
                "id": f"D{len(hunks) + 1}",
                "path": path,
                "urls": sorted(e["urls"]),
                "is_page": e["is_page"],
                "skills": sorted(e["skills"]),
                "header": unified_header(group),
                # The heading the change sits under, for a link to that section.
                "section": section_above(new, first_change(group)) if e["is_page"] else None,
                # A missing newline at the end of a file would join two lines.
                "lines": [l if l.endswith("\n") else l + "\n" for l in lines],
            })

    if args.diff:
        with open(args.diff, "w", encoding="utf-8") as f:
            for i, h in enumerate(hunks):
                if i == 0 or hunks[i - 1]["path"] != h["path"]:
                    f.write(f"--- a/{h['path']}\n+++ b/{h['path']}\n")
                f.write(f"{h['header']} [{h['id']}]\n")
                f.writelines(h["lines"])

    if args.hunks:
        with open(args.hunks, "w", encoding="utf-8") as f:
            json.dump(hunks, f, indent=1)


def section_above(lines, index):
    """(heading text, anchor) of the last Markdown heading before lines[index],
    skipping fenced code blocks (where # starts a comment), or None. The
    anchor follows MkDocs' default toc slugify."""
    found, fence = None, None
    for line in lines[:index]:
        m = re.match(r"\s*(`{3,}|~{3,})", line)
        if m:
            mark = m.group(1)
            if fence is None:
                fence = mark
            elif mark[0] == fence[0] and len(mark) >= len(fence):
                fence = None
            continue
        h = re.match(r"(#{1,6})\s+(.+?)\s*#*\s*$", line)
        if fence is None and h:
            text = re.sub(r"\{[^}]*\}\s*$", "", h.group(2)).strip()  # attr_list {#id}
            custom = re.search(r"\{\s*#([\w-]+)", h.group(2))
            # Keep link text, drop link targets and inline markup.
            plain = re.sub(r"\[([^\]]*)\](?:\([^)]*\)|\[[^\]]*\])", r"\1", text)
            plain = re.sub(r"[`*_]", "", plain)
            slug = custom.group(1) if custom else re.sub(
                r"[-\s]+", "-", re.sub(r"[^\w\s-]", "", plain).strip().lower())
            found = (plain, slug)
    return found


def first_change(group):
    """Index in the new file just past the first changed line, so a heading
    that is itself the change counts as the section."""
    tag, _, _, j1, j2 = next(op for op in group if op[0] != "equal")
    return j1 + (1 if j2 > j1 else 0)


def unified_header(group):
    """The @@ line for a group of opcodes, as difflib.unified_diff writes it."""
    def rng(start, stop):
        length = stop - start
        if length == 1:
            return f"{start + 1}"
        return f"{start if length == 0 else start + 1},{length}"
    first, last = group[0], group[-1]
    return f"@@ -{rng(first[1], last[2])} +{rng(first[3], last[4])} @@"


if __name__ == "__main__":
    main()
