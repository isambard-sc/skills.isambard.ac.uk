#!/usr/bin/env python3
"""Generates the OpenCode HTTP skills catalog.

OpenCode (opencode.ai) discovers skills from directories or HTTP catalogs.
A catalog is an index.json that lists, per skill, the files to download
from <base-url>/<skill-name>/<file>; writing the catalog next to the
skills it indexes means the site already serves those paths.

The catalog covers the isambard plugin only. Each entry is keyed by its
directory name — OpenCode derives skill IDs from paths, and the entry name
becomes the download subdirectory — and carries a content-hash `version`
so OpenCode clients refresh their caches whenever a skill file changes.

Run with no arguments to (re)write the catalog, or with --check (used by
validate.yml) to fail if the committed catalog is missing or stale.
"""

import argparse
import hashlib
import json
import os
import sys

SKILLS_DIR = os.path.join("site", "plugins", "isambard", "skills")
CATALOG_PATH = os.path.join(SKILLS_DIR, "index.json")


def build_catalog():
    entries = []
    for name in sorted(os.listdir(SKILLS_DIR)):
        skill_dir = os.path.join(SKILLS_DIR, name)
        if not os.path.isdir(skill_dir):
            continue
        files = []
        for root, _, file_names in os.walk(skill_dir):
            for file_name in sorted(file_names):
                files.append(os.path.relpath(os.path.join(root, file_name), skill_dir))
        files.sort()
        h = hashlib.sha256(name.encode("utf-8"))
        for rel_path in files:
            h.update(rel_path.encode("utf-8"))
            with open(os.path.join(skill_dir, rel_path), "rb") as f:
                h.update(f.read())
        entries.append({"name": name, "version": h.hexdigest()[:12], "files": files})
    return {"skills": entries}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="fail if the committed catalog is missing or stale")
    args = parser.parse_args()

    catalog = build_catalog()
    expected = json.dumps(catalog, indent=2) + "\n"
    current = None
    if os.path.exists(CATALOG_PATH):
        with open(CATALOG_PATH, encoding="utf-8") as f:
            current = f.read()

    if args.check:
        if current == expected:
            print(f"OK — {CATALOG_PATH} matches the skills on disk")
        else:
            print(f"FAIL {CATALOG_PATH} is missing or stale — run 'python3 .github/workflows/scripts/generate_opencode_catalog.py' and commit the result")
            sys.exit(1)
    else:
        with open(CATALOG_PATH, "w", encoding="utf-8") as f:
            f.write(expected)
        print(f"OK — wrote {CATALOG_PATH} with {len(catalog['skills'])} skills")


if __name__ == "__main__":
    main()
