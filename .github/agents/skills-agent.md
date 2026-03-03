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

```
skills/
  <skill-name>/
    <skill-name>.md
```

Rules:
- The skill name must be lowercase, using hyphens instead of spaces
  (e.g. `slurm`, `python-venv`, `mpi-profiling`).
- Each skill lives in its own subdirectory under `skills/`.
- The primary skill file must be named `<skill-name>.md` and placed
  directly inside `skills/<skill-name>/`.
- If a skill needs supplementary files (examples, schemas, images), they
  may be added inside the same `skills/<skill-name>/` directory.

Examples:

| Skill topic | Directory | Primary file |
|---|---|---|
| Slurm job management | `skills/slurm/` | `skills/slurm/slurm.md` |
| Python virtual environments | `skills/python-venv/` | `skills/python-venv/python-venv.md` |
| MPI profiling | `skills/mpi-profiling/` | `skills/mpi-profiling/mpi-profiling.md` |

---

## Skill File Structure

Every skill file must begin with a level-1 heading that describes the
skill, followed by a one-sentence summary. The rest of the file is
structured Markdown that an AI agent reads as instructions or reference
material.

Required sections (add in this order where applicable):

1. **Title** (`# <Skill Name> — Agent Skill`)
2. **One-sentence summary** immediately after the title
3. **Link to full documentation** (canonical `docs.isambard.ac.uk` URL)
4. **Critical Rules** — any hard constraints the agent must never violate
   (use `⚠️` emoji and a clear prohibition list)
5. **Overview** — brief context about the technology
6. **How-to sections** — step-by-step instructions, command examples,
   code blocks
7. **Common Issues / Troubleshooting**
8. **Further Reading** — links to `docs.isambard.ac.uk` and other sources

Skill files must use fenced code blocks (triple backticks with language
hint) for all command and script examples.

---

## Updating `marketplace.json`

Every skill must have an entry in `marketplace.json` at the root of the
repository. The JSON structure is:

```json
{
  "name": "Isambard AI Skills",
  "description": "AI agent skills for Isambard HPC systems",
  "url": "https://skills.isambard.ac.uk",
  "skills": [
    {
      "name": "<Human-readable skill name>",
      "description": "<One or two sentence description>",
      "url": "https://skills.isambard.ac.uk/skills/<skill-name>/<skill-name>.md"
    }
  ]
}
```

When adding a new skill:
1. Add a new object to the `"skills"` array.
2. Use the canonical `https://skills.isambard.ac.uk/...` URL — never the
   raw GitHub URL.
3. Keep the array sorted alphabetically by `"name"`.

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
  <a href="skills/<skill-name>/<skill-name>.md">View skill file &rarr;</a>
</div>
```

4. Keep the skill cards in alphabetical order.
5. Do **not** change the site's CSS or layout when adding a skill card.

---

## Creating a New Skill — Checklist

When creating a new skill, complete the following steps in order:

- [ ] Create the directory `skills/<skill-name>/`
- [ ] Create `skills/<skill-name>/<skill-name>.md` with the required
      sections listed above
- [ ] Add an entry to `marketplace.json`
- [ ] Add a skill card to `index.html`
- [ ] Update `README.md` skills table if present

---

## Updating an Existing Skill

- Edit `skills/<skill-name>/<skill-name>.md` directly.
- Update the `"description"` in `marketplace.json` if the summary changed.
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
