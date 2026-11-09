#!/usr/bin/env python3
"""Save the main text of every docs page a skill cites, so docs changes show
up as git diffs.

Each SKILL.md names the docs.isambard.ac.uk pages it was derived from in
`metadata.source_url` and `metadata.supplementary_urls`. This fetches each
page from the public site, keeps only the article body (dropping navigation,
theme and footer, which change site-wide), converts it to plain text and
writes it to snapshots/<url-path>.md. Snapshots of pages no skill cites any
more are removed.

The committed snapshots are the docs as the skills were last checked against
them, so after a refresh `git diff -- snapshots/` is exactly what changed in
the docs since. Fixing a flagged skill is Workflow B in
.github/agents/update-skills-from-docs.md; commit the refreshed snapshots with
the skill update.

Prints a Markdown report of changed, new, removed and unfetchable pages and
the skills citing each. Always exits 0: a docs change is a prompt to review,
not a failure.

Usage (from the repo root):
  python3 .github/workflows/scripts/snapshot_docs.py [--report report.md]
"""

import argparse
import os
import re
import sys
import urllib.request
from html.parser import HTMLParser

from skills_lib import discover_skills, load_frontmatter

DOCS_SITE = "https://docs.isambard.ac.uk"
SNAPSHOT_DIR = "snapshots"

# Pages that change constantly for reasons a skill shouldn't track: a skill
# links to service status so the agent checks it live, not to copy its content.
VOLATILE_PREFIXES = ("service-status/",)

BLOCK_TAGS = {"p", "div", "pre", "table", "ul", "ol", "dl", "dt", "dd",
              "blockquote", "details", "summary", "hr", "br"}
SKIP_TAGS = {"script", "style", "svg", "button"}
VOID_TAGS = {"br", "hr", "img", "input", "wbr", "meta", "link", "source"}
# Permalink anchors and the "last updated" footer, if the theme adds one.
SKIP_CLASSES = {"headerlink", "md-source-file"}


class ArticleText(HTMLParser):
    """Collect the text of the first <article class="md-content__inner ...">,
    with light Markdown-like structure (headings, lists, tables, code blocks,
    content tabs) so diffs stay readable and show which system a value is for.
    """

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.out = []
        self.depth = 0  # nesting depth inside the article; 0 = outside
        self.done = False
        self.skip = 0  # depth of the outermost skipped element, 0 = none
        self.pre = False
        self.tabsets = []  # open content-tab sets: {"depth", "labels", "next"}
        self.labels = 0  # depth of the open tabbed-labels element, 0 = none

    def handle_starttag(self, tag, attrs):
        if self.done:
            return
        classes = set((dict(attrs).get("class") or "").split())
        if self.depth == 0:
            if tag == "article" and "md-content__inner" in classes:
                self.depth = 1
            return
        if tag not in VOID_TAGS:
            self.depth += 1
        if self.skip or tag in SKIP_TAGS or classes & SKIP_CLASSES:
            if not self.skip and tag not in VOID_TAGS:
                self.skip = self.depth
            return
        if self.labels:
            if tag == "label":
                self.tabsets[-1]["labels"].append("")
            return
        if "tabbed-set" in classes:
            self.tabsets.append({"depth": self.depth, "labels": [], "next": 0})
        elif "tabbed-labels" in classes and self.tabsets:
            self.labels = self.depth
        elif "tabbed-block" in classes and self.tabsets:
            tabs = self.tabsets[-1]
            label = tabs["labels"][tabs["next"]] if tabs["next"] < len(tabs["labels"]) else ""
            tabs["next"] += 1
            self.out.append(f'\n\n=== "{label.strip()}"\n')
        elif re.fullmatch(r"h[1-6]", tag):
            self.out.append("\n\n" + "#" * int(tag[1]) + " ")
        elif tag == "li":
            self.out.append("\n- ")
        elif tag == "pre":
            self.pre = True
            self.out.append("\n```\n")
        elif tag == "code" and not self.pre:
            self.out.append("`")
        elif tag == "tr":
            self.out.append("\n|")
        elif tag in ("td", "th"):
            self.out.append(" ")
        elif tag in BLOCK_TAGS:
            self.out.append("\n")

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in VOID_TAGS:
            self.handle_endtag(tag)

    def handle_endtag(self, tag):
        if self.done or self.depth == 0 or tag in VOID_TAGS:
            return
        if tag == "article" and self.depth == 1:
            self.depth = 0
            self.done = True
            return
        closing = self.depth
        self.depth -= 1
        if self.skip:
            if closing == self.skip:
                self.skip = 0
            return
        if self.labels:
            if closing == self.labels:
                self.labels = 0
            return
        if self.tabsets and closing == self.tabsets[-1]["depth"]:
            self.tabsets.pop()
        if tag == "pre":
            self.pre = False
            self.out.append("\n```\n")
        elif tag == "code" and not self.pre:
            self.out.append("`")
        elif tag in ("td", "th"):
            self.out.append(" |")
        elif re.fullmatch(r"h[1-6]", tag) or tag in BLOCK_TAGS:
            self.out.append("\n")

    def handle_data(self, data):
        if not self.depth or self.skip or self.done:
            return
        if self.labels:
            if self.tabsets[-1]["labels"]:
                self.tabsets[-1]["labels"][-1] += data
        else:
            self.out.append(data if self.pre else re.sub(r"\s+", " ", data))

    def text(self):
        raw = "".join(self.out)
        # Tidy everything outside code blocks; keep code blocks verbatim.
        parts = re.split(r"(\n```\n.*?\n```\n)", raw, flags=re.DOTALL)
        for i in range(0, len(parts), 2):
            lines = [re.sub(r" {2,}", " ", line).strip() for line in parts[i].split("\n")]
            parts[i] = "\n".join(lines)
        return re.sub(r"\n{3,}", "\n\n", "".join(parts)).strip() + "\n"


def cited_pages():
    """Map each cited docs URL (without fragment) to the skills citing it."""
    pages = {}
    for skill in discover_skills():
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


def snapshot_path(url):
    rel = url[len(DOCS_SITE):].strip("/")
    return os.path.join(SNAPSHOT_DIR, (rel or "index") + ".md")


def fetch_text(url):
    req = urllib.request.Request(url, headers={"User-Agent": "skills.isambard.ac.uk snapshot_docs"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        html = resp.read().decode("utf-8", errors="replace")
    parser = ArticleText()
    parser.feed(html)
    if not parser.done:
        raise ValueError("no <article class=\"md-content__inner\"> element")
    return parser.text()


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--report", help="also write the Markdown report to this file")
    args = ap.parse_args()

    pages = cited_pages()
    changes = {"changed": [], "new": [], "removed": [], "error": []}

    for url in sorted(pages):
        path = snapshot_path(url)
        try:
            text = f"<!-- Snapshot of {url} made by snapshot_docs.py. Do not edit. -->\n\n" + fetch_text(url)
        except Exception as e:  # keep the old snapshot; report and carry on
            changes["error"].append((url, path, f"{type(e).__name__}: {e}"))
            continue
        old = None
        if os.path.exists(path):
            with open(path, encoding="utf-8") as f:
                old = f.read()
        if text != old:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "w", encoding="utf-8") as f:
                f.write(text)
            changes["new" if old is None else "changed"].append((url, path, None))

    wanted = {snapshot_path(u) for u in pages}
    for root, _, files in os.walk(SNAPSHOT_DIR):
        for name in files:
            path = os.path.join(root, name)
            if path not in wanted:
                os.remove(path)
                changes["removed"].append((path, path, None))

    lines = ["## Docs snapshot refresh", ""]
    if not any(changes.values()):
        lines.append(f"No changes in the {len(pages)} cited docs pages.")
    labels = {"changed": "Changed", "new": "New (no previous snapshot)",
              "removed": "Removed (no longer cited)", "error": "Could not fetch (snapshot kept)"}
    for kind, label in labels.items():
        if not changes[kind]:
            continue
        lines += [f"### {label}", ""]
        for url, path, err in changes[kind]:
            skills = ", ".join(f"`{s}`" for s in sorted(pages.get(url, ())))
            entry = f"- `{path}`" + (f" ({skills})" if skills else "")
            lines.append(entry + (f": {err}" if err else ""))
        lines.append("")
    if changes["changed"]:
        lines.append("Review with `git diff -- snapshots/`.")
    report = "\n".join(lines).rstrip() + "\n"

    sys.stdout.write(report)
    if args.report:
        with open(args.report, "w", encoding="utf-8") as f:
            f.write(report)


if __name__ == "__main__":
    main()
