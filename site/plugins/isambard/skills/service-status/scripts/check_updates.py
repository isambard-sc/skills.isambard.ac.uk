#!/usr/bin/env python3
"""Report recent Isambard platform changes.

Covers the docs site (last deploy time, pages added/removed since the
previous run) and the isambard-sc GitHub organisation (repositories pushed
within the window, recent commits, latest releases of key user-facing
repositories). Usage:

    python3 check_updates.py [--days N]      # default 14

Standard library only. Uses the unauthenticated GitHub API (60 requests per
hour per IP); set GITHUB_TOKEN to raise the limit.

@author Shiran
"""
import json
import os
import re
import sys
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

DOCS = "https://docs.isambard.ac.uk/"
ORG = "isambard-sc"
KEY_RELEASE_REPOS = ("clifton", "skills.isambard.ac.uk", "buildit")
CACHE_DIR = Path.home() / ".cache" / "isambard-service-status"
MAX_REPOS_DETAILED = 6


def http_get(url):
    headers = {"User-Agent": "isambard-skill"}
    token = os.environ.get("GITHUB_TOKEN")
    if token and url.startswith("https://api.github.com/"):
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.read().decode("utf-8", "replace"), resp.headers


def gh_json(url):
    body, _ = http_get(url)
    return json.loads(body)


def report_docs():
    print("=" * 72)
    print(f"DOCS SITE  <{DOCS}>")
    print("=" * 72)
    try:
        # the homepage omits Last-Modified; sub-pages carry the deploy time
        _, headers = http_get(DOCS + "service-status/")
        print(f"Site last deployed: {headers.get('Last-Modified', 'unknown')}")
    except Exception as exc:
        print(f"Could not fetch site: {exc}")

    try:
        sitemap, _ = http_get(DOCS + "sitemap.xml")
        urls = sorted(set(re.findall(r"<loc>(.*?)</loc>", sitemap)))
        print(f"Pages in sitemap: {len(urls)}")
        cache = CACHE_DIR / "sitemap-urls.txt"
        if cache.exists():
            previous = set(cache.read_text().splitlines())
            for url in (u for u in urls if u not in previous):
                print(f"  + added:   {url}")
            for url in sorted(previous.difference(urls)):
                print(f"  - removed: {url}")
            if previous == set(urls):
                print("No pages added or removed since the last check "
                      "(content edits inside existing pages are not "
                      "detectable).")
        else:
            print("First run — sitemap cached; future runs will diff it.")
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        cache.write_text("\n".join(urls))
    except Exception as exc:
        print(f"Could not process sitemap: {exc}")
    print()


def report_github(days):
    since = datetime.now(timezone.utc) - timedelta(days=days)
    print("=" * 72)
    print(f"GITHUB org {ORG} — activity in the last {days} days")
    print("=" * 72)
    try:
        repos = gh_json(
            f"https://api.github.com/orgs/{ORG}/repos?sort=pushed&per_page=100"
        )
    except Exception as exc:
        print(f"GitHub API failed: {exc}")
        print(f"Fallback: https://github.com/{ORG}/<repo>/commits/main.atom")
        return

    def pushed_at(repo):
        return datetime.strptime(
            repo["pushed_at"], "%Y-%m-%dT%H:%M:%SZ"
        ).replace(tzinfo=timezone.utc)

    active = [r for r in repos if r.get("pushed_at") and pushed_at(r) >= since]
    if not active:
        print("No repositories pushed in this window.")
    for repo in active[:MAX_REPOS_DETAILED]:
        print(f"--- {repo['full_name']}  (pushed {repo['pushed_at']})")
        if repo.get("description"):
            print(f"    {repo['description']}")
        try:
            commits = gh_json(
                f"https://api.github.com/repos/{repo['full_name']}/commits"
                f"?since={since:%Y-%m-%dT%H:%M:%SZ}&per_page=10"
            )
            for commit in commits:
                date = commit["commit"]["author"]["date"][:10]
                message = commit["commit"]["message"].splitlines()[0][:90]
                print(f"    {date}  {commit['sha'][:7]}  {message}")
            if not commits:
                print("    (no commits on the default branch in this window)")
        except Exception as exc:
            print(f"    commits unavailable: {exc}")
        print()
    skipped = active[MAX_REPOS_DETAILED:]
    if skipped:
        print("Not detailed (rate-limit budget): "
              + ", ".join(r["name"] for r in skipped) + "\n")

    print("--- Latest releases of key user-facing repositories")
    for name in KEY_RELEASE_REPOS:
        try:
            release = gh_json(
                f"https://api.github.com/repos/{ORG}/{name}/releases/latest"
            )
            print(f"    {name}: {release.get('tag_name')} "
                  f"({(release.get('published_at') or '')[:10]}) — "
                  f"{release.get('html_url')}")
        except Exception:
            print(f"    {name}: no releases")


def main():
    args = sys.argv[1:]
    days = 14
    if "--days" in args:
        try:
            days = int(args[args.index("--days") + 1])
        except (IndexError, ValueError):
            sys.exit("Usage: python3 check_updates.py [--days N]")
    print(f"Checked at: {datetime.now(timezone.utc):%Y-%m-%d %H:%M UTC}\n")
    report_docs()
    report_github(days)


if __name__ == "__main__":
    main()
