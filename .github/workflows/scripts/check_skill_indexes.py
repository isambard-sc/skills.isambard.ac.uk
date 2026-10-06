#!/usr/bin/env python3
"""Every skill directory under site/plugins/*/skills/*/ must be listed in
site/marketplace.json, site/index.html, and README.md. This is the
regression this repo keeps hitting: a skill gets created but one of the
three public indexes is never updated, so it's invisible there even
though it's live on the site.
"""

import json
import sys

from skills_lib import discover_skills, report_and_exit


def main():
    skills = discover_skills()
    if not skills:
        print("No skill directories found under site/plugins/*/skills/*/")
        sys.exit(1)

    with open("site/marketplace.json", encoding="utf-8") as f:
        marketplace_urls = {s["url"] for s in json.load(f)["skills"]}

    with open("site/index.html", encoding="utf-8") as f:
        index_html = f.read()

    with open("README.md", encoding="utf-8") as f:
        readme = f.read()

    errors = []
    for skill in skills:
        plugin, name = skill["plugin"], skill["name"]
        url = f"https://skills.isambard.ac.uk/plugins/{plugin}/skills/{name}/SKILL.md"
        rel_href = f"plugins/{plugin}/skills/{name}/SKILL.md"
        rel_readme_path = f"site/plugins/{plugin}/skills/{name}/SKILL.md"

        if url not in marketplace_urls:
            errors.append(f"{name}: missing from site/marketplace.json (expected url {url})")
        if rel_href not in index_html:
            errors.append(f"{name}: no skill card in site/index.html (expected href {rel_href})")
        if rel_readme_path not in readme and url not in readme:
            errors.append(f"{name}: missing from README.md skills table (expected link to {rel_readme_path})")

    report_and_exit(
        errors,
        f"OK — all {len(skills)} skills are indexed in marketplace.json, index.html, and README.md",
    )


if __name__ == "__main__":
    main()
