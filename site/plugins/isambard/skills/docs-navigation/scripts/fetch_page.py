#!/usr/bin/env python3
"""Print a docs.isambard.ac.uk page as plain text.

Fallback fetcher for agents without a web-fetch tool. Usage:

    python3 fetch_page.py <url-or-path>
    python3 fetch_page.py user-documentation/guides/slurm/

Standard library only; requires outbound HTTPS.

@author Shiran
"""
import re
import sys
import urllib.request
from html.parser import HTMLParser

BASE = "https://docs.isambard.ac.uk/"


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
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    target = sys.argv[1]
    url = target if target.startswith("http") else BASE + target.lstrip("/")
    if not url.endswith(("/", ".xml", ".txt", ".html")):
        url += "/"
    try:
        text, last_modified = fetch_page(url)
    except Exception as exc:
        sys.exit(f"FETCH FAILED for {url}: {exc}")
    print(f"SOURCE: {url}")
    print(f"LAST-MODIFIED: {last_modified}")
    print("-" * 72)
    print(text or "(no content extracted — read the URL directly)")


if __name__ == "__main__":
    main()
