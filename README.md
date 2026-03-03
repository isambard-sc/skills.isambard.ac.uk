# skills.isambard.ac.uk

A curated collection of **AI agent skills** for Isambard HPC systems,
served at [skills.isambard.ac.uk](https://skills.isambard.ac.uk).

Agent skills are plain Markdown instruction files that teach AI coding
assistants (such as [Claude Code](https://claude.ai/code)) how to perform
specific tasks correctly in your environment. Loading a skill gives the
agent up-to-date, site-specific knowledge without you having to explain
the environment from scratch every session.

---

## Available Skills

| Skill | Description | URL |
|---|---|---|
| [Slurm](skills/slurm/slurm.md) | Submit, monitor and manage HPC jobs on Isambard using the Slurm workload manager | `https://skills.isambard.ac.uk/skills/slurm/slurm.md` |

---

## Using a Skill

### Claude Code

Add a single skill:

```
/add-skill https://skills.isambard.ac.uk/skills/slurm/slurm.md
```

Add the full marketplace (all skills at once):

```
/add-marketplace https://skills.isambard.ac.uk/marketplace.json
```

### Other agent-based tools

Paste the skill URL into the tool's context or skill configuration. The
raw Markdown content is served directly from this site.

---

## Repository Structure

```
.github/
  agents/
    skills-agent.md        # Instructions for AI agents on creating skills
.vscode/
  settings.json            # Word-wrap settings for Markdown/.chatagent files
skills/
  slurm/
    slurm.md               # Slurm skill file
index.html                 # Public site landing page
marketplace.json           # Skills index for agent tools
CNAME                      # Custom domain configuration
README.md                  # This file
```

---

## Contributing / Adding a New Skill

See [`.github/agents/skills-agent.md`](.github/agents/skills-agent.md)
for the full conventions on how skills are structured, named, and
registered in the marketplace.

For full Isambard documentation visit
[docs.isambard.ac.uk](https://docs.isambard.ac.uk).
