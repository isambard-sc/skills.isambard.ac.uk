#!/usr/bin/env python3
"""Validate SKILL.md frontmatter against the schema documented in
.github/agents/skills-agent.md. Exits non-zero and prints one line per
violation if any required field is missing or empty.
"""

import glob
import sys

import yaml

REQUIRED_TOP_LEVEL = ["name", "description", "license"]
REQUIRED_METADATA = ["author", "version", "source_url"]


def load_frontmatter(path):
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


def check(path):
    errors = []
    data, err = load_frontmatter(path)
    if err:
        return [f"{path}: {err}"]

    for key in REQUIRED_TOP_LEVEL:
        if not data.get(key):
            errors.append(f"{path}: missing or empty required field '{key}'")

    metadata = data.get("metadata")
    if not isinstance(metadata, dict):
        errors.append(f"{path}: missing or invalid 'metadata' block")
    else:
        for key in REQUIRED_METADATA:
            if not metadata.get(key):
                errors.append(
                    f"{path}: missing or empty required field 'metadata.{key}'"
                )

    return errors


def main():
    paths = sorted(glob.glob("site/plugins/*/skills/*/SKILL.md"))
    if not paths:
        print("No SKILL.md files found under site/plugins/*/skills/*/")
        sys.exit(1)

    all_errors = []
    for path in paths:
        all_errors.extend(check(path))

    if all_errors:
        for e in all_errors:
            print(f"FAIL {e}")
        sys.exit(1)

    print(f"OK — {len(paths)} SKILL.md files conform to the required schema")


if __name__ == "__main__":
    main()
