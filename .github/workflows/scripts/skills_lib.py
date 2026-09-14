"""Shared helpers for the SKILL.md validation scripts in this directory.

All of these scripts are invoked as `python3 .github/workflows/scripts/<name>.py`
from the repo root by validate.yml, which puts this directory on sys.path
automatically (Python adds the running script's own directory), so a plain
`import skills_lib` from a sibling script just works.
"""

import glob
import os
import sys

import yaml

SKILL_GLOB = "site/plugins/*/skills/*/"


def discover_skills():
    """Return every skill on disk as a list of {"plugin", "name", "dir"} dicts,
    sorted by directory path.
    """
    skills = []
    for d in sorted(glob.glob(SKILL_GLOB)):
        dir_path = d.rstrip("/")
        # site/plugins/<plugin>/skills/<name>
        plugin, name = dir_path.split(os.sep)[-3], dir_path.split(os.sep)[-1]
        skills.append({"plugin": plugin, "name": name, "dir": dir_path})
    return skills


def load_frontmatter(path):
    """Parse the YAML frontmatter of a SKILL.md file. Returns (data, error) —
    exactly one of which is None.
    """
    with open(path, encoding="utf-8") as f:
        text = f.read()

    if not text.startswith("---\n"):
        return None, "does not start with '---' frontmatter delimiter"

    parts = text.split("---\n", 2)
    if len(parts) < 3:
        return None, "missing closing '---' frontmatter delimiter"

    try:
        data = yaml.safe_load(parts[1])
    except yaml.YAMLError as e:
        return None, f"invalid YAML: {e}"

    if not isinstance(data, dict):
        return None, "frontmatter did not parse to a mapping"

    return data, None


def report_and_exit(errors, ok_message):
    """Print one FAIL line per error and exit 1, or print ok_message and exit 0."""
    if errors:
        for e in errors:
            print(f"FAIL {e}")
        sys.exit(1)
    print(ok_message)
