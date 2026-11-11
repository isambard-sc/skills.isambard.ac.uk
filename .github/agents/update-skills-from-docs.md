# Agent: Create and Update Skills from docs.isambard.ac.uk

## Purpose

Use this agent to create a new skill file or update an existing one by fetching the authoritative content from `https://docs.isambard.ac.uk`.

Invoke this agent when:

- A new documentation page on docs.isambard.ac.uk should become a skill
- A user asks whether an existing skill is up to date
- The docs site has been updated and skills derived from it need refreshing

---

## Docs Coverage

Each skill's `metadata.source_url` and `metadata.supplementary_urls` are the
record of which docs pages it covers, and the docs sync reads them, so they
are not repeated here. This section records what frontmatter can't: pages
planned to become skills, pages waiting on a decision, and pages that
deliberately have no skill. Paths are relative to
`https://docs.isambard.ac.uk/`.

When new pages appear on docs.isambard.ac.uk, add each one to an existing
skill's `supplementary_urls` or to one of the tables below before
proceeding.

### Planned skills

Names are working names; settle them when the skill is created.

| Skill | Docs pages |
|---|---|
| `login` | `user-documentation/guides/login/`, `user-documentation/guides/shortname/`, `user-documentation/guides/mobaxterm/`, `user-documentation/tutorials/setup/`, `user-documentation/getting_started/`, `user-documentation/information/how-isambard-works/` |
| `accounting` | `user-documentation/guides/accounting/`, `user-documentation/guides/manage_project/`, `user-documentation/guides/follow_on_project/`, `user-documentation/guides/awards_portal/`, `user-documentation/information/portals/`, `user-documentation/information/project-policies/` |
| `storage` | `user-documentation/information/system-storage/`, `user-documentation/information/environment_variables/`, `user-documentation/tutorials/datasets-in-squashfs/` |
| `interactive-sessions` | `user-documentation/guides/jupyter/`, `user-documentation/guides/jupyterhub/`, `user-documentation/guides/vscode/` |
| `ml-packages` | `user-documentation/applications/ML-packages/`, `user-documentation/applications/alphafold/`, `user-documentation/tutorials/interactive-ml/`, `user-documentation/tutorials/interactive-alphafold/` |
| `distributed-training` | `user-documentation/tutorials/distributed-training/`, `user-documentation/tutorials/distributed-inference/`, `user-documentation/tutorials/llms/pre-training/`, `user-documentation/tutorials/llms/fine-tuning/` |

### Pending a decision

Do not create skills for these pages until the team decides how to cover
them.

| Docs pages | Open question |
|---|---|
| `user-documentation/guides/inference/`, `user-documentation/guides/kubernetes/` (and its pages), `user-documentation/tutorials/data-mover/` | These services are invite-only early access, and the pages are excluded from the docs site search. `data-transfer` already cites the data mover tutorial, so the decision applies to it too. |
| `user-documentation/faqs/bc5-launch/` | Whether BlueCrystal 5 belongs in the `isambard` plugin. The page says it is temporary and will be merged into the main docs. |

### No skill

| Docs pages | Why |
|---|---|
| `service-status/` (and its pages) | Changes daily. Skills link to it so the agent reads it live, and the sync ignores it. Never copy its content, including known-issue workarounds, into a skill. |
| `policies/` (and its pages) | Legal text. Link from Further Reading; `brics-hpc-ai-code` cites `policies/acceptable_use/` for its rules. |
| `training/`, `events/` (and their pages) | Dated event pages. |
| `user-documentation/guides/e4s/` | Only links to the external E4S docs. Link it from Further Reading. |
| `user-documentation/applications/relion/`, `user-documentation/applications/orca/` | Niche application guides. Reconsider if users ask about them. |
| `index`, `about/`, `access/`, `acknowledge/`, and the section index pages | Navigation or one-line facts. Link them where relevant. |

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

Create `site/plugins/<plugin-name>/skills/<skill-name>/SKILL.md` with:

**Frontmatter:**

```yaml
---
name: <skill-name>
description: >
  <One to two sentences covering: what the skill does, what commands it
  covers, and when an agent should activate it. Include keywords a user
  would say when they need this skill.>
license: CC-BY-SA-4.0. Markdown/image content derived from https://docs.isambard.ac.uk/, © Bristol Centre for Supercomputing (BriCS).
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
- Keep body under 500 lines; move reference detail to `site/plugins/<plugin-name>/skills/<skill-name>/references/` if needed

### Step 7 — Register the skill

Follow the checklist from `skills-agent.md` exactly:

- [ ] Add entry to `site/marketplace.json` `skills` array (keep sorted alphabetically by `"name"`)
- [ ] Add skill card to `site/index.html` (keep in alphabetical order)
- [ ] Update `README.md` skills table
- [ ] Update the skill count and name lists in `README.md`'s example CLI transcripts (the `/skills` output and the Cursor `Skills: N (...)` line) — `validate.yml` checks these against the skills on disk and will fail the build if they're stale

### Step 8 — Update Docs Coverage

Remove the skill's row from "Planned skills" in this file
(`.github/agents/update-skills-from-docs.md`), and move any of its pages the
skill doesn't cite to another table.

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

If you are working from a docs sync (see "Checking All Skills for Staleness"), you are given the diff of the changed pages' source, which shows exactly what changed. Use it as the record of changes, and fetch the published pages for their full current text.

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

Edit `site/plugins/<plugin-name>/skills/<skill-name>/SKILL.md`:

- Apply the minimum diff needed — preserve existing structure where accurate, only change what is actually different
- Increment `metadata.version` (e.g. `"1.0"` → `"1.1"`)
- Do **not** rename or move the file

Also update descriptions in both `marketplace.json` files if the skill
summary has changed materially.

---

## Checking All Skills for Staleness

The docs repo (private) is the single source of truth, and this repo keeps
no copy of it. `.github/docs-sync-commit` records the docs commit the skills
were last synced with. `docs_changes.py` diffs a clone of the docs repo from
that commit to the latest, keeps only the pages skills cite (including files
they include with `--8<--`), and reports which skills cite each changed page:

```bash
python3 .github/workflows/scripts/docs_changes.py \
    --docs-repo ../docs.isambard.ac.uk --from "$(cat .github/docs-sync-commit)" --to origin/main
```

`docs_sync.sh` in the same directory runs the whole sync: if any cited page
changed, it runs Claude Code headless to apply Workflow B to the affected
skills, records the new docs commit and opens a draft PR for review. Run it
with `--dry-run` to see the report only. It skips while an earlier sync PR is
still open. Run it locally, or let the `docs-sync.yml` workflow run it every
weekday once its secrets are set (see the comments in that file).

The sync only watches pages listed in `source_url`/`supplementary_urls`, so
also check for new docs pages relevant to a skill and file them as
described in "Docs Coverage". To check every skill by hand:

1. List all `SKILL.md` files:
   `find site/plugins -name SKILL.md`

2. For each file, read `metadata.source_url` and `metadata.supplementary_urls` from the frontmatter.

3. Fetch each source URL (and supplementary URLs) and compare against the skill body using the comparison criteria in Workflow B, Step 3.

4. Report which skills are up to date, which need minor updates, and which need significant rewrites.

5. For each stale skill, apply Workflow B.
