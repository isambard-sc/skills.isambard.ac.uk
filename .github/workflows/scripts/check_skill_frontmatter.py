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
# Length limits from the Agent Skills specification
# (https://agentskills.io/specification); harnesses may reject or truncate
# longer values.
MAX_LENGTH = {"name": 64, "description": 1024, "compatibility": 500}


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

    for key, limit in MAX_LENGTH.items():
        value = data.get(key)
        if isinstance(value, str) and len(value.strip()) > limit:
            errors.append(
                f"{path}: '{key}' is {len(value.strip())} characters; "
                f"the limit is {limit}"
            )

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
