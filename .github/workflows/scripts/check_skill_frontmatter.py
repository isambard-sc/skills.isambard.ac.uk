#!/usr/bin/env python3
"""Validate every SKILL.md against the rules documented in
.github/agents/skills-agent.md: its directory name must match the
frontmatter `name`, and the required frontmatter fields must be present
and non-empty.
"""

import os
import sys

from skills_lib import discover_skills, load_frontmatter, report_and_exit

REQUIRED_TOP_LEVEL = ["name", "description", "license"]
REQUIRED_METADATA = ["author", "version", "source_url"]


def check(skill):
    path = os.path.join(skill["dir"], "SKILL.md")
    data, err = load_frontmatter(path)
    if err:
        return [f"{path}: {err}"]

    errors = []

    if data.get("name") != skill["name"]:
        errors.append(
            f"{path}: directory name '{skill['name']}' does not match "
            f"frontmatter name '{data.get('name')}'"
        )

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
    skills = discover_skills()
    if not skills:
        print("No skill directories found under site/plugins/*/skills/*/")
        sys.exit(1)

    errors = []
    for skill in skills:
        errors.extend(check(skill))

    report_and_exit(
        errors,
        f"OK — {len(skills)} SKILL.md files match their directory name "
        "and conform to the required schema",
    )


if __name__ == "__main__":
    main()
