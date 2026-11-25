# Agent guidance for skills.isambard.ac.uk

## Branch safety

**Never commit or push directly to `main`.**
Before making any changes, check the current branch with
`git branch --show-current`. If on `main`, stop and ask the user to create a
feature branch first. All changes must go through a PR against `main`.

## Commit messages

Write commit messages that a colleague can understand from the git log alone:
this repository and its history are public.

- Use a short subject line (under 72 characters) in the imperative mood:
  "Add login skill", not "Added" or "Adding".
- If the change needs more explanation, add a blank line and a body that says
  *why* the change was made, not just what changed.
- Avoid vague messages like "update skills", "fix", "wip" or "changes".

## Project overview

This repository publishes AI agent skills for the Bristol Centre for
Supercomputing (BriCS) Isambard systems. GitHub Pages serves the `site/`
directory at https://skills.isambard.ac.uk, and users install the skills as a
Claude Code plugin or copy them into other agent tools (see `README.md`).

- Skills: `site/plugins/<plugin>/skills/<skill>/SKILL.md`, with optional
  `references/`, `scripts/` and `assets/` alongside.
- Indexes that must list every skill: `site/marketplace.json`,
  `site/index.html` and the tables and example transcripts in `README.md`.
- CI checks: `.github/workflows/validate.yml` and the scripts it runs in
  `.github/workflows/scripts/`.

## Detailed guidance

Read the relevant file before creating or editing a skill, and follow it
rather than duplicating its rules here:

- [`.github/agents/skills-agent.md`](.github/agents/skills-agent.md): skill
  structure, required frontmatter and sections, and the checklists for adding
  or updating a skill, plugin or index.
- [`.github/agents/update-skills-from-docs.md`](.github/agents/update-skills-from-docs.md):
  creating a skill from a docs page and checking an existing skill against the
  docs.

## Source of truth

[docs.isambard.ac.uk](https://docs.isambard.ac.uk) is the source of truth.
Skills are a derived, agent-facing subset of it.

- Take every Isambard-specific fact from a published docs page, and list that
  page in the skill's `metadata.source_url` or `metadata.supplementary_urls`.
- If the docs are wrong or missing something, raise it against the docs
  rather than correcting it only in a skill.
- Link to policy pages under https://docs.isambard.ac.uk/policies/; never
  summarise or paraphrase them.
- Prefer telling the agent how to check a value that changes (a command to
  run, a page to fetch live) over embedding the value. Never copy service
  status or incident text into a skill.
- The docs source repository is private and this one is public. Use only
  content from the published site: no unpublished or draft pages, and nothing
  from the docs repository's commit messages, issues or pull requests.

## Writing style

- Write for an AI agent, not a human reader: direct, imperative instructions,
  with Critical Rules first (see `skills-agent.md`).
- Use British English, as docs.isambard.ac.uk does.
- In commands and examples, use long-form flags rather than short ones, as
  docs.isambard.ac.uk does: `srun --nodes 2 --gpus 8`, not `srun -N 2 --gpus 8`.
  Keep the short form where there is no long one (e.g. `ssh -L`, `scp -r`,
  `make -j`, `python -m`, `bash -c`) and for the familiar `cp -r` and
  `mkdir -p`.
- Wrap Markdown at 80 characters (`.vscode/settings.json` sets this up).
  docs.isambard.ac.uk uses one sentence per line instead, so re-wrap text
  copied from there.
- Keep each `SKILL.md` under 500 lines; move detail into `references/`.

## Validation

CI runs these on every pull request. Run them from the repository root before
raising one:

```bash
pip install pyyaml
python3 .github/workflows/scripts/check_skill_frontmatter.py
python3 .github/workflows/scripts/check_skill_indexes.py
python3 .github/workflows/scripts/check_readme_examples.py
```

`validate.yml` also checks that every `https://skills.isambard.ac.uk/` URL in
`site/marketplace.json` and `README.md` resolves to a file under `site/`.

## Published URLs

Never rename or move a published skill: users and other tools already
reference its URL. Increment `metadata.version` when a change is significant.
