#!/usr/bin/env python3
"""README.md contains illustrative CLI transcripts (Claude Code /skills
output, a Cursor plugin-details listing) that hardcode the skill count
and skill names. These have gone stale before (a skill was added without
updating them) and will again unless something checks them. Compares
both transcripts against the actual skill directories on disk. Exits
non-zero and prints a diagnostic on any mismatch.
"""

import glob
import os
import re
import sys

SKILL_GLOB = "site/plugins/*/skills/*/"


def discover_skill_names():
    names = set()
    for d in glob.glob(SKILL_GLOB):
        names.add(os.path.basename(d.rstrip("/")))
    return names


def check_claude_code_transcript(readme, actual_names):
    errors = []
    count_match = re.search(r"^\s*(\d+) skills? · Space to cycle", readme, re.MULTILINE)
    if not count_match:
        return ["could not find the '/skills' transcript's 'N skills ·' line in README.md"]

    count = int(count_match.group(1))
    listed_names = set(re.findall(r"isambard:([a-z0-9-]+) · plugin", readme))

    if count != len(actual_names):
        errors.append(
            f"'/skills' transcript says {count} skills, but {len(actual_names)} exist on disk"
        )
    missing = actual_names - listed_names
    extra = listed_names - actual_names
    if missing:
        errors.append(f"'/skills' transcript is missing: {', '.join(sorted(missing))}")
    if extra:
        errors.append(f"'/skills' transcript lists skills that no longer exist: {', '.join(sorted(extra))}")
    return errors


def check_cursor_transcript(readme, actual_names):
    errors = []
    match = re.search(r"Skills: (\d+) \(([^)]*)\)", readme)
    if not match:
        return ["could not find the Cursor 'Skills: N (...)' line in README.md"]

    count = int(match.group(1))
    listed_names = {n.strip() for n in match.group(2).split(",") if n.strip()}

    if count != len(actual_names):
        errors.append(
            f"Cursor transcript says {count} skills, but {len(actual_names)} exist on disk"
        )
    missing = actual_names - listed_names
    extra = listed_names - actual_names
    if missing:
        errors.append(f"Cursor transcript is missing: {', '.join(sorted(missing))}")
    if extra:
        errors.append(f"Cursor transcript lists skills that no longer exist: {', '.join(sorted(extra))}")
    return errors


def main():
    actual_names = discover_skill_names()
    if not actual_names:
        print("No skill directories found under site/plugins/*/skills/*/")
        sys.exit(1)

    with open("README.md", encoding="utf-8") as f:
        readme = f.read()

    errors = check_claude_code_transcript(readme, actual_names) + check_cursor_transcript(readme, actual_names)

    if errors:
        for e in errors:
            print(f"FAIL {e}")
        sys.exit(1)

    print("OK — README.md example transcripts match the skills on disk")


if __name__ == "__main__":
    main()
