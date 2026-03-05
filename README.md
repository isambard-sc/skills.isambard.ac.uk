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
| [Slurm](site/skills/slurm/SKILL.md) | Submit, monitor and manage HPC jobs on Isambard using the Slurm workload manager | `https://skills.isambard.ac.uk/skills/slurm/SKILL.md` |

---

## Using a Skill

### Claude Code

Add the Isambard marketplace (all skills at once):

```
/plugin marketplace add https://skills.isambard.ac.uk/.claude-plugin/marketplace.json
```

Install a specific skill by name:

```
/plugin install slurm@isambard-skills
```

Or add to your project's `.claude/settings.json` to enable automatically:

```json
{
  "extraKnownMarketplaces": {
    "isambard-skills": {
      "source": {
        "source": "url",
        "url": "https://skills.isambard.ac.uk/.claude-plugin/marketplace.json"
      }
    }
  },
  "enabledPlugins": { "slurm@isambard-skills": true }
}
```

### Other agent-based tools

Paste the skill URL into the tool's context or skill configuration. The
raw Markdown content is served directly from this site.

---

## Repository Structure

```
site/                      # All web-served content (GitHub Pages source)
  .claude-plugin/
    marketplace.json         # Claude Code plugin marketplace catalog
  skills/
    slurm/
      SKILL.md               # Slurm skill file (AgentSkills spec format)
    docs/
      SKILL.md               # User documentation skill file (AgentSkills spec format)
  index.html                 # Public site landing page
  marketplace.json           # Simple skills index for other agent tools
  CNAME                      # Custom domain configuration
.github/
  agents/
    skills-agent.md          # Instructions for AI agents on creating skills
.vscode/
  settings.json              # Word-wrap settings for Markdown/.chatagent files
README.md                    # This file
```

---

## Contributing / Adding a New Skill

See [`.github/agents/skills-agent.md`](.github/agents/skills-agent.md)
for the full conventions on how skills are structured, named, and
registered in the marketplace.

For full Isambard documentation visit
[docs.isambard.ac.uk](https://docs.isambard.ac.uk).
