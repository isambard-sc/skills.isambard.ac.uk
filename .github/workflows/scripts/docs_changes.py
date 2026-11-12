#!/usr/bin/env python3
"""Report which skills cite docs pages that changed between two docs commits.

Each SKILL.md names the docs.isambard.ac.uk pages it was derived from in
`metadata.source_url` and `metadata.supplementary_urls`. This maps those URLs
to Markdown files in a checkout of the docs repo at the --to commit (following
pymdownx.snippets `--8<--` includes, so example scripts count as part of the
page), then diffs those files between --from and --to.

It writes a Markdown report (changed pages, the skills citing each, and cited
URLs that no longer map to a page) to stdout, and with --diff, a unified diff
of the changed pages to a file. The diff file is empty when no cited page
changed.

The docs repo is private while this repo and its pull requests are public, so
the report contains docs paths and commit hashes only, never commit subjects
or authors, and the diff is built from the files with HTML comments (which the
published site doesn't show) removed.

Usage (from the repo root):
  python3 .github/workflows/scripts/docs_changes.py \\
      --docs-repo ../docs.isambard.ac.uk --from <commit> [--to <commit>]
"""

import argparse
import difflib
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
COMMENT_RE = re.compile(r"<!--.*?-->", re.DOTALL)


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
    """The file at rev without HTML comments, or "" if it doesn't exist."""
    if not exists(repo, rev, path):
        return ""
    return COMMENT_RE.sub("", git(repo, "show", f"{rev}:{path}"))


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
            entry = by_path.setdefault(path, {"urls": set(), "skills": set()})
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

    if args.diff:
        with open(args.diff, "w", encoding="utf-8") as f:
            for path in changed:
                old = published_text(repo, base, path).splitlines(keepends=True)
                new = published_text(repo, head, path).splitlines(keepends=True)
                f.writelines(difflib.unified_diff(old, new, f"a/{path}", f"b/{path}"))


if __name__ == "__main__":
    main()
