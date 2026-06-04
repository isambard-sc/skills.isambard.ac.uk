# Agent: Create and Update Skills from docs.isambard.ac.uk

## Purpose

Use this agent to create a new skill file or update an existing one by fetching the authoritative content from `https://docs.isambard.ac.uk`.

Invoke this agent when:

- A new documentation page on docs.isambard.ac.uk should become a skill
- A user asks whether an existing skill is up to date
- The docs site has been updated and skills derived from it need refreshing

---

## Known Documentation Sources

The table below maps docs.isambard.ac.uk pages to their corresponding skill names. Use this as the starting point for create or update tasks.

### Guides

| docs.isambard.ac.uk page | Skill name | Skill file | Status |
|---|---|---|---|
| https://docs.isambard.ac.uk/user-documentation/guides/slurm/ | `slurm` | `skills/slurm/SKILL.md` | ✅ exists |
| https://docs.isambard.ac.uk/user-documentation/guides/login/ | `login` | `skills/login/SKILL.md` | ❌ not yet created |
| https://docs.isambard.ac.uk/user-documentation/guides/file_transfer/ | `file-transfer` | `skills/file-transfer/SKILL.md` | ❌ not yet created |
| https://docs.isambard.ac.uk/user-documentation/guides/python/ | `python` | `skills/python/SKILL.md` | ✅ |
| https://docs.isambard.ac.uk/user-documentation/guides/containers/ | `containers` | `skills/containers/SKILL.md` | ✅ |
| https://docs.isambard.ac.uk/user-documentation/guides/modules/ | `modules-and-compilers` | `skills/modules-and-compilers/SKILL.md` | ✅ |
| https://docs.isambard.ac.uk/user-documentation/guides/jupyter/ | `jupyter` | `skills/jupyter/SKILL.md` | ❌ not yet created |
| https://docs.isambard.ac.uk/user-documentation/guides/vscode/ | `vscode` | `skills/vscode/SKILL.md` | ❌ not yet created |
| https://docs.isambard.ac.uk/user-documentation/guides/mpi/ | `mpi` | `skills/mpi/SKILL.md` | ✅ |
| https://docs.isambard.ac.uk/user-documentation/guides/spack/ | `spack` | `skills/spack/SKILL.md` | ✅ |
| https://docs.isambard.ac.uk/user-documentation/guides/nccl/ | `nccl` | `skills/nccl/SKILL.md` | ✅ |
| https://docs.isambard.ac.uk/user-documentation/guides/accounting/ | `accounting` | `skills/accounting/SKILL.md` | ❌ not yet created |

### Applications

| docs.isambard.ac.uk page | Skill name | Skill file | Status |
|---|---|---|---|
| https://docs.isambard.ac.uk/user-documentation/applications/ML-packages/ | `ml-packages` | `skills/ml-packages/SKILL.md` | ❌ not yet created |
| https://docs.isambard.ac.uk/user-documentation/applications/alphafold/ | `alphafold` | `skills/alphafold/SKILL.md` | ❌ not yet created |

### Information

| docs.isambard.ac.uk page | Skill name | Skill file | Status |
|---|---|---|---|
| https://docs.isambard.ac.uk/user-documentation/information/job-scheduling/ | *(supplementary to `slurm`)* | — | — |

When new pages appear on docs.isambard.ac.uk that are not listed above, add them to the appropriate table before proceeding.

---

## Workflow A: Create a New Skill from a Docs Page

Follow these steps in order.

### Step 1 — Confirm the docs page exists and is in scope

Fetch the docs page URL to confirm it loads and contains actionable content that would help an AI agent assist users.

Good candidates:
- How-to guides with concrete commands and examples
- Pages that describe system-specific behaviour or constraints
- Pages that have "Critical Rules" (rate limits, forbidden commands,
  resource policies)

Poor candidates:
- Pure prose overviews with no commands
- Pages that are primarily links to other pages
- Policy pages (reference them in skill "Further Reading" instead)

### Step 2 — Read the existing skills-agent.md

Read `.github/agents/skills-agent.md` in full to confirm the current folder structure, frontmatter schema, and file creation checklist before writing any files.

### Step 3 — Fetch the source documentation

Fetch the docs page. If the content is paginated or truncated, fetch additional chunks until you have the full page. Also fetch any linked sub-pages that are important to the skill topic.

For the Slurm skill, the supplementary job-scheduling page was also fetched:
https://docs.isambard.ac.uk/user-documentation/information/job-scheduling/

### Step 4 — Identify Critical Rules

Before writing the skill, identify any constraints mentioned in the docs that an agent must never violate. Examples from existing skills:

- Polling rate limits (e.g. never run squeue faster than 60 s)
- Resource policies (e.g. never run compute work on login nodes)
- Fair-use rules (e.g. always set --time on salloc)

These must appear at the top of the skill body, before all other sections, under a `## ⚠️ Critical Rule: <Title>` heading.

### Step 5 — Determine the skill name

Derive the skill name from the docs page slug. Rules:

- Lowercase only
- Hyphens instead of spaces or underscores
- Match the last segment of the docs URL path (e.g. `file_transfer` → `file-transfer`, `ML-packages` → `ml-packages`)
- Must be 1–64 characters, no consecutive hyphens, no leading/trailing hyphen

### Step 6 — Create the SKILL.md file

Create `skills/<skill-name>/SKILL.md` with:

**Frontmatter:**

```yaml
---
name: <skill-name>
description: >
  <One to two sentences covering: what the skill does, what commands it
  covers, and when an agent should activate it. Include keywords a user
  would say when they need this skill.>
compatibility: >
  Isambard-AI and/or Isambard 3 (Grace, MACS). Requires access to an
  Isambard login node.
metadata:
  author: isambard-sc
  version: "1.0"
  source_url: <exact URL of the primary docs.isambard.ac.uk page fetched>
  supplementary_urls:            # include if additional pages were fetched
    - <URL of each supplementary docs page>
---
```

**Body — required sections in order:**

1. `# <Topic> on Isambard — Agent Skill`
2. Links to the source docs page(s) (plain URL, no Markdown link syntax)
3. `## ⚠️ Critical Rule: <Title>` for each hard constraint (if any)
4. `## System Overview` or equivalent context section
5. Detailed how-to sections with fenced code blocks
6. `## Troubleshooting` section
7. `## Further Reading` section with docs.isambard.ac.uk links

**Style rules:**
- Write for an AI agent reader, not a human
- Use imperative mood ("Run `cmd`", not "You can run `cmd`")
- Include actual command output examples where the docs provide them
- All code in fenced blocks with language hint (`bash`, `yaml`, etc.)
- Wrap lines at 80 characters
- Keep body under 500 lines; move reference detail to `skills/<skill-name>/references/` if needed

### Step 7 — Register the skill

Follow the checklist from `skills-agent.md` exactly:

- [ ] Add entry to `.claude-plugin/marketplace.json` `plugins` array
- [ ] Add entry to `marketplace.json` `skills` array
- [ ] Add skill card to `index.html`
- [ ] Update `README.md` skills table

### Step 8 — Update the Known Documentation Sources table

Update the table in this file (`.github/agents/update-skills-from-docs.md`) to mark the skill as `✅ exists` for the relevant row.

---

## Workflow B: Update an Existing Skill

Follow these steps to check whether a skill is stale and update it if
needed.

### Step 1 — Read the existing SKILL.md

Read the `SKILL.md` file for the skill. Note:
- `metadata.source_url` — the primary docs page it was derived from
- `metadata.supplementary_urls` — any additional docs pages that contributed content (may be absent if none were used)
- `metadata.version` — the current version

### Step 2 — Fetch the source docs pages

Fetch the URL in `metadata.source_url`. If the page is long, fetch in chunks to get the full content.

Also fetch every URL listed in `metadata.supplementary_urls`. These are additional docs pages whose content was incorporated into the skill and which may independently have changed.

### Step 3 — Compare content

Compare the fetched docs against the existing skill. Flag differences in:

- New commands, options, or features not yet in the skill
- Changed command syntax or options
- New partitions, hardware, or system configuration
- New Critical Rules or policy changes
- Removed or deprecated features

### Step 4 — Decide whether to update

Update the skill if any of the following are true:

- New commands or options are documented that would help users
- Existing commands in the skill are incorrect or outdated
- New Critical Rules or policy constraints exist in the docs
- Hardware or partition details have changed
- The docs contain new worked examples that significantly improve the skill

Do **not** update the skill for:

- Minor prose rewording with no information change
- New links in the docs that are already in the skill's Further Reading

### Step 5 — Write the update

Edit `skills/<skill-name>/SKILL.md`:

- Apply the minimum diff needed — preserve existing structure where accurate, only change what is actually different
- Increment `metadata.version` (e.g. `"1.0"` → `"1.1"`)
- Do **not** rename or move the file

Also update descriptions in both `marketplace.json` files if the skill
summary has changed materially.

---

## Checking All Skills for Staleness

To check every skill in the repository at once:

1. List all `SKILL.md` files:
   `find skills/ -name SKILL.md`

2. For each file, read `metadata.source_url` and `metadata.supplementary_urls` from the frontmatter.

3. Fetch each source URL (and supplementary URLs) and compare against the skill body using the comparison criteria in Workflow B, Step 3.

4. Report which skills are up to date, which need minor updates, and which need significant rewrites.

5. For each stale skill, apply Workflow B.
