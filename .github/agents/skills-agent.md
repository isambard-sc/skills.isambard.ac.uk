# Agent Instructions: Creating and Updating Skills

This file tells AI agents (e.g. GitHub Copilot, Claude Code) how to create
or update skills in this repository and how to keep the public site up to
date.

---

## What is a Skill?

A skill is a plain Markdown file that gives an AI agent the knowledge and
rules it needs to assist users with a specific HPC or software topic on
Isambard systems. Skills are served as static files from
`https://skills.isambard.ac.uk` and are consumed by agent-based coding
tools such as Claude Code.

---

## Folder and Naming Conventions

Skills follow the [AgentSkills specification](https://agentskills.io/specification).

```
skills/
  <skill-name>/
    SKILL.md           # Required — primary skill file with YAML frontmatter
    references/        # Optional — supplementary reference files
    scripts/           # Optional — helper scripts
    assets/            # Optional — static resources
```

Rules:
- The skill name must be lowercase, using hyphens instead of spaces
  (e.g. `slurm`, `python-venv`, `mpi-profiling`).
- Each skill lives in its own subdirectory under `skills/`.
- The primary skill file **must be named `SKILL.md`** (uppercase) and
  placed directly inside `skills/<skill-name>/`.
- The `SKILL.md` file must start with YAML frontmatter (see below).
- Supplementary files may be added in `references/`, `scripts/`, or
  `assets/` subdirectories within the skill directory.

Examples:

| Skill topic | Directory | Primary file |
|---|---|---|
| Slurm job management | `skills/slurm/` | `skills/slurm/SKILL.md` |
| Python virtual environments | `skills/python-venv/` | `skills/python-venv/SKILL.md` |
| MPI profiling | `skills/mpi-profiling/` | `skills/mpi-profiling/SKILL.md` |

---

## Skill File Structure

Every `SKILL.md` file must begin with YAML frontmatter followed by
Markdown content, per the AgentSkills specification.

### Required YAML frontmatter

```yaml
---
name: <skill-name>
description: >
  <One to two sentences: what the skill does and when to use it.
  Be specific — include keywords agents use to identify relevant tasks.>
compatibility: >
  <Environment requirements — intended system, required tools, network
  access needs, etc.>
metadata:
  author: isambard-sc
  version: "1.0"
  source_url: https://docs.isambard.ac.uk/<path-to-source-page>/
  supplementary_urls:            # optional — list additional docs pages
    - https://docs.isambard.ac.uk/<path-to-supplementary-page>/
---
```

- `name`: must match the parent directory name exactly (lowercase,
  hyphens, 1–64 characters)
- `description`: required, max 1024 characters, should describe what
  the skill does AND when to use it
- `compatibility`: optional but recommended for Isambard-specific skills
- `metadata.version`: increment when making significant changes
- `metadata.source_url`: the primary docs.isambard.ac.uk URL this skill
  was derived from; used by the update agent to detect stale content
- `metadata.supplementary_urls`: optional list of additional
  docs.isambard.ac.uk pages that contributed content to this skill

### Markdown body sections

Required sections (add in this order where applicable):

1. **Title** (`# <Skill Name> — Agent Skill`)
2. **Links to full documentation** (canonical `docs.isambard.ac.uk` URLs)
3. **Critical Rules** — any hard constraints the agent must never violate
   (use `⚠️` emoji and a clear prohibition list)
4. **Overview** — brief context about the technology
5. **How-to sections** — step-by-step instructions, command examples,
   code blocks
6. **Common Issues / Troubleshooting**
7. **Further Reading** — links to `docs.isambard.ac.uk` and other sources

Skill files must use fenced code blocks (triple backticks with language
hint) for all command and script examples.

Keep `SKILL.md` under 500 lines. Move detailed reference material to
`references/` files if needed.

---

## Updating `.claude-plugin/marketplace.json`

Every skill must have an entry in `.claude-plugin/marketplace.json` for
Claude Code plugin marketplace support. The plugin entry format is:

```json
{
  "name": "<skill-name>",
  "source": "./skills/<skill-name>",
  "description": "<One or two sentence description>",
  "version": "<semver>",
  "author": { "name": "Isambard SC" },
  "homepage": "https://skills.isambard.ac.uk",
  "repository": "https://github.com/isambard-sc/skills.isambard.ac.uk",
  "agents": ["./SKILL.md"]
}
```

When adding a new skill, append to the `"plugins"` array and keep the
array sorted alphabetically by `"name"`.

## Updating `marketplace.json`

Also add an entry to the simple `marketplace.json` at the root (used by
other agent tools). The structure is:

```json
{
  "name": "<Human-readable skill name>",
  "description": "<One or two sentence description>",
  "url": "https://skills.isambard.ac.uk/skills/<skill-name>/SKILL.md"
}
```

Use the canonical `https://skills.isambard.ac.uk/...` URL — never the
raw GitHub URL. Keep the array sorted alphabetically by `"name"`.

---

## Updating `index.html`

The main page at `index.html` lists all available skills with a short
description and a link to the skill file. When adding or updating a skill:

1. Open `index.html`.
2. Locate the `<div class="skills-grid">` element inside the
   `<section id="skills">` section.
3. Add a new `<div class="skill-card">` block following this template:

```html
<div class="skill-card">
  <h3><Skill Name></h3>
  <p>
    <Short description of what the skill covers — one to two sentences.>
  </p>
  <a href="skills/<skill-name>/SKILL.md">View skill file &rarr;</a>
</div>
```

4. Keep the skill cards in alphabetical order.
5. Do **not** change the site's CSS or layout when adding a skill card.

---

## Creating a New Skill — Checklist

When creating a new skill, complete the following steps in order:

- [ ] Create the directory `skills/<skill-name>/`
- [ ] Create `skills/<skill-name>/SKILL.md` with YAML frontmatter and
      the required sections listed above
- [ ] Add an entry to `.claude-plugin/marketplace.json` `plugins` array
- [ ] Add an entry to `marketplace.json` `skills` array
- [ ] Add a skill card to `index.html`
- [ ] Update `README.md` skills table

---

## Updating an Existing Skill

- Edit `skills/<skill-name>/SKILL.md` directly.
- Increment `metadata.version` in the frontmatter for significant changes.
- Update the `"description"` in both `marketplace.json` files if the
  summary changed.
- Update the skill card description in `index.html` if the summary changed.
- Do **not** rename or move skill files once published — existing
  integrations may already reference the URL.

---

## Style and Content Guidelines

- Write skills for an AI agent audience, not a human reader. Instructions
  should be direct and unambiguous.
- Use imperative mood: "Run `sbatch job.sh`" not "You can run `sbatch`".
- Always include a **Critical Rules** section for any skill where there
  are hard constraints (rate limits, forbidden commands, security rules).
- Keep code examples short and self-contained.
- All URLs in skill files must point to `https://skills.isambard.ac.uk/…`
  or `https://docs.isambard.ac.uk/…`, not to raw GitHub URLs.
- Markdown files should wrap at 80 characters (VS Code settings enforce
  this automatically via `.vscode/settings.json`).
