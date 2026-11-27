#!/usr/bin/env python3
"""Say whether a change could alter which skill an agent picks.

An agent chooses a skill from its name and description alone, so routing only
needs re-testing when one of those changes, a skill is added or removed, or a
routing dataset changes. Edits to a skill's body don't count.

    python3 .github/workflows/scripts/routing_inputs_changed.py BASE_REF

Prints one reason per line and exits 0 if routing should run, or prints
nothing and exits 1 if not. Run from the repo root with BASE_REF fetched.
"""

import glob
import subprocess
import sys

import yaml

SKILL_FILES = "site/plugins/*/skills/*/SKILL.md"
EVALS_PATHSPEC = "site/plugins/*/skills/*/evals/*"


def git(*args):
    return subprocess.run(
        ["git", *args], capture_output=True, text=True, check=False
    )


def routing_fields(text):
    """Return (name, description) from SKILL.md text, or None if unparseable."""
    parts = text.split("---\n", 2)
    if not text.startswith("---\n") or len(parts) < 3:
        return None
    try:
        data = yaml.safe_load(parts[1])
    except yaml.YAMLError:
        return None
    if not isinstance(data, dict):
        return None
    return data.get("name"), " ".join(str(data.get("description", "")).split())


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    base = sys.argv[1]
    reasons = []

    listed = git("ls-tree", "-r", "--name-only", base, "--", "site/plugins")
    if listed.returncode:
        sys.exit(f"can't list {base}: {listed.stderr.strip()}")
    base_skills = {
        p for p in listed.stdout.splitlines() if p.endswith("/SKILL.md")
        and p.count("/") == 5
    }
    head_skills = set(glob.glob(SKILL_FILES))

    for path in sorted(head_skills - base_skills):
        reasons.append(f"added: {path}")
    for path in sorted(base_skills - head_skills):
        reasons.append(f"removed: {path}")
    for path in sorted(head_skills & base_skills):
        old = routing_fields(git("show", f"{base}:{path}").stdout)
        with open(path, encoding="utf-8") as f:
            new = routing_fields(f.read())
        if old != new:
            reasons.append(f"name or description changed: {path}")

    evals = git("diff", "--name-only", base, "--", EVALS_PATHSPEC)
    reasons += [f"routing dataset changed: {p}" for p in evals.stdout.split()]

    for reason in reasons:
        print(reason)
    sys.exit(0 if reasons else 1)


if __name__ == "__main__":
    main()
