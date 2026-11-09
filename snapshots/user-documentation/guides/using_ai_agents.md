<!-- Snapshot of https://docs.isambard.ac.uk/user-documentation/guides/using_ai_agents/ made by snapshot_docs.py. Do not edit. -->

# Using AI agents with Isambard

Prerequisites

This guide assumes you can already log in to Isambard systems. If not, follow the Getting Started guide first.

This guide explains how to use AI coding agents, such as Claude, safely and effectively with BriCS systems. It covers installing the official Isambard plugin, recommended workflows, and what to avoid.

## Recommended workflow

- Keep the agent running on your local machine and interact with Isambard in the normal way over SSH or JupyterHub.
- Use the skill that matches your current task - each skill corresponds to a guide on this site.
- Ask the agent to recommend commands or configurations, then copy them into your own terminal, review them against the documentation, and run them yourself.
- Do not grant the agent a persistent connection to Isambard or allow it to execute commands without your review.

## What to avoid

Do not run AI agents directly on Isambard login nodes

Login nodes are shared resources with strict limits on CPU time and network connections. Agents can open extra connections and run long-lived background processes that are not permitted on login nodes. This is considered Unacceptable Use under the Acceptable Use Policy. Run your agent locally and connect to Isambard separately.

- Do not share your Isambard password or SSH private key with any agent or plugin.
- Do not rely on an agent as the sole source of truth - verify important steps in the official documentation.
- Do not use agents to bypass access controls, authentication, or policy restrictions.
- As ever, you are responsible for what is run, not the agent - agents can suggest, or run, commands that conflict with the Acceptable Use Policy; it is up to you to catch this.

## Isambard skills

The official Isambard skills repository is hosted on GitHub.

It contains skill definitions that extend AI agents with knowledge of the Isambard HPC environment: job scheduling, modules, and resource limits. The skills can be used with Claude (via the `isambard-skills` marketplace described below) or copied manually into the plugin directories for other tools such as Cursor or Codex.

The Claude marketplace is the easiest starting point: it provides a ready-made `isambard-skills` plugin with one skill per guide on this documentation site.

## Install the `isambard` plugin

### Claude

#### Desktop

- Open the Claude desktop application.
- Click Customize in the left pane.
- Click + next to Personal Plugins, then Create plugin, then Add marketplace.
- Enter `isambard-sc/skills.isambard.ac.uk` in the URL field, then click Sync.
- Click + next to the Isambard plugin block to install it.
- Click the Isambard plugin block to view the available skills.

#### CLI

Tested on Claude Code `2.1.227`.

-
Open the Claude CLI.

-
Add the `isambard-skills` marketplace.

```
/plugin marketplace add https://github.com/isambard-sc/skills.isambard.ac.uk

```

-
Install the `isambard` plugin from that marketplace.

```
/plugin install isambard@isambard-skills

```

-
Reload plugins and skills.

```
/reload-plugins
/reload-skills

```

-
Verify the available skills.

```
/skills

```

### Codex

#### CLI

Tested on Codex CLI `0.147.0`.

```
$ codex plugin marketplace add isambard-sc/skills.isambard.ac.uk
$ codex plugin add isambard@isambard-skills

```

### Cursor

#### CLI

Tested on Cursor CLI `2026.08.04-aaa8809`.

```
$ agent plugin marketplace add https://github.com/isambard-sc/skills.isambard.ac.uk
Fetching plugins from https://github.com/isambard-sc/skills.isambard.ac.uk...
✓ Added marketplace isambard-skills (1 plugin)
  isambard - AI agent skills for Isambard HPC systems
Tip: use /plugins in interactive mode to install plugins from this marketplace.
$ agent
> /plugin marketplace list
 Marketplaces

 Global
    Cursor Plugin Marketplace • 223 plugins • 0 installed • Never indexed

 User
  → isambard-skills • 1 plugin • 0 installed • Last indexed 2026-08-11 14:14 UTC

 Enter for details • Esc to close
> [Press Enter]

 Marketplace details / isambard-skills

 Scope: User
 Plugins: 1
 Installed: 1 (isambard)
 Indexing: Last indexed 2026-08-11 14:14 UTC
 Source: https://github.com/isambard-sc/skills.isambard.ac.uk

  → Browse plugins
    Remove marketplace

 Enter to select • Esc to go back

> [Press Enter]
 Plugins Installed  Marketplace  (←/→ or tab to cycle)

 Install Plugins

 ┌──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
 │ ⌕ isambard-skills                                                                                                                        │
 └──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘

 → isambard (isambard-skills) [installed]
   AI agent skills for Isambard HPC systems

 Enter for details • Esc to clear

> [Press Enter]
 Plugins Installed  Marketplace  (←/→ or tab to cycle)

 Install Plugins

 ┌──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
 │ ⌕ isambard-skills                                                                                                                        │
 └──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘

 → isambard (isambard-skills)
   AI agent skills for Isambard HPC systems

 Enter for details • Esc to clear

> [Press Enter]
 Plugin details / isambard

 AI agent skills for Isambard HPC systems

 Marketplace: isambard-skills

 Skills: 9 (containers, cuda, brics-hpc-ai-code, modules, mpi, nccl, python, slurm, spack)

  → Install for you (user scope)
    Install for all collaborators on this repository (project scope)

 Enter to select • Esc to go back

> [Press Enter]

```

### Antigravity

#### CLI

Tested on Antigravity CLI `1.1.12`.

```
$ agy plugin install https://github.com/isambard-sc/skills.isambard.ac.uk/site
$ agy plugin enable isambard

```

## Getting help

If you are unsure whether a particular agent workflow is permitted, contact the Isambard support desk before proceeding. Do not use automation to recover from access or policy issues.
