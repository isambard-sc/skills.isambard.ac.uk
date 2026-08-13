#!/usr/bin/env python3
"""Fetch the live Isambard service status from docs.isambard.ac.uk.

Prints the status overview, known issues, and planned maintenance as plain
text, each with the page's Last-Modified header. Pass --all to include
archived (resolved) issues. Exits non-zero if any page could not be fetched.

Standard library only; requires outbound HTTPS.

@author Shiran
"""
import re
import sys
import urllib.request
from datetime import datetime, timezone
from html.parser import HTMLParser

BASE = "https://docs.isambard.ac.uk/service-status/"
PAGES = [
    ("SERVICE STATUS OVERVIEW", BASE),
    ("KNOWN ISSUES", BASE + "known_issues/"),
    ("PLANNED MAINTENANCE", BASE + "planned_maintenance/"),
]
ARCHIVE = ("ARCHIVED ISSUES (resolved)", BASE + "archived_issues/")


class ArticleText(HTMLParser):
    """Reduce a MkDocs <article> block to readable plain text."""

    SKIP = {"script", "style", "nav", "footer", "aside"}

    def __init__(self):
        super().__init__()
        self.parts = []
        self.skip = 0

    def handle_starttag(self, tag, attrs):
        if tag in self.SKIP:
            self.skip += 1
        elif tag in ("h1", "h2", "h3", "h4", "h5"):
            self.parts.append("\n\n" + "#" * int(tag[1]) + " ")
        elif tag == "li":
            self.parts.append("\n- ")
        elif tag in ("p", "tr", "br", "pre"):
            self.parts.append("\n")
        elif tag in ("td", "th"):
            self.parts.append(" | ")

    def handle_endtag(self, tag):
        if tag in self.SKIP and self.skip:
            self.skip -= 1

    def handle_data(self, data):
        if not self.skip:
            self.parts.append(data)


def fetch_page(url):
    """Return (plain_text, last_modified) for a docs page."""
    req = urllib.request.Request(url, headers={"User-Agent": "isambard-skill"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        html = resp.read().decode("utf-8", "replace")
        last_modified = resp.headers.get("Last-Modified", "unknown")
    match = re.search(r"<article[^>]*>(.*?)</article>", html, re.S)
    parser = ArticleText()
    parser.feed(match.group(1) if match else html)
    text = "".join(parser.parts).replace("¶", "")
    lines = [re.sub(r"[ \t]+", " ", ln).strip() for ln in text.splitlines()]
    collapsed = "\n".join(lines)
    return re.sub(r"\n{3,}", "\n\n", collapsed).strip(), last_modified


def main():
    pages = PAGES + [ARCHIVE] if "--all" in sys.argv[1:] else PAGES
    print(f"Fetched at: {datetime.now(timezone.utc):%Y-%m-%d %H:%M UTC}")
    print("Note: pages may be CDN-cached for up to ~10 minutes.\n")
    failures = 0
    for title, url in pages:
        print("=" * 72)
        print(f"{title}  <{url}>")
        try:
            text, last_modified = fetch_page(url)
            print(f"Page last modified: {last_modified}")
            print("=" * 72)
            print(text or "(no content extracted — read the URL directly)")
        except Exception as exc:
            failures += 1
            print("=" * 72)
            print(f"FETCH FAILED: {exc}")
            print("Report status as UNKNOWN and point the user at the URL.")
        print()
    sys.exit(1 if failures else 0)


if __name__ == "__main__":
    main()
