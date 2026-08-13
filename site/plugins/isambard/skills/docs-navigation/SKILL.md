---
name: docs-navigation
description: >
  Locate the correct page on docs.isambard.ac.uk for any Isambard question
  and answer from the live page instead of memory. Use this skill whenever a
  user asks how to do something on Isambard-AI or Isambard 3 — getting
  access, logging in (clifton/SSH), transferring files, storage and quotas,
  Jupyter, VS Code, project management, accounting, applications, policies,
  training — and no more specific Isambard skill covers it, or whenever an
  answer should cite official Isambard documentation.
compatibility: >
  Requires outbound HTTPS. Works with any web-fetch tool; a stdlib Python
  fetcher is bundled for agents without one.
metadata:
  author: Shiran
  version: "1.0"
  source_url: https://docs.isambard.ac.uk/
---

# Docs Navigation — Agent Skill

Full documentation: <https://docs.isambard.ac.uk/>

## ⚠️ Critical Rules

- **Answer from the live page, not from memory.** Generic HPC knowledge is
  often wrong here: Isambard-AI and Isambard 3 Grace are aarch64/Arm64,
  use clifton for SSH access, and have site-specific Slurm limits.
- Cite the exact `docs.isambard.ac.uk` URL for every substantive claim.
- Quote commands, module names, partition names, and paths **verbatim from
  the fetched page** — do not invent or "correct" them.
- Prefer a more specific installed Isambard skill (slurm, python,
  containers, mpi, nccl, cuda, spack, modules, service-status) when one
  matches the question; use this skill for everything else and for finding
  canonical links.
- If a mapped path returns 404, re-check
  <https://docs.isambard.ac.uk/sitemap.xml> — the site may have been
  restructured — and answer from the current location.

## Overview

`docs.isambard.ac.uk` is the canonical documentation for the Bristol
Centre for Supercomputing (BriCS) facilities: Isambard-AI (GH200, aarch64),
Isambard 3 Grace (Arm CPU), Isambard 3 MACS (multi-architecture), and
BlueCrystal 5 early access. The site has ~95 pages;
`references/url-map.md` maps question topics to exact page URLs.

## How to answer a documentation question

1. Pick the single best-matching page in `references/url-map.md`.
2. Fetch it — with the available web-fetch tool, or the bundled fallback:

   ```bash
   python3 scripts/fetch_page.py user-documentation/guides/login/
   ```

3. Answer from the fetched content and cite the URL. If the page defers to
   another guide, fetch that guide too rather than guessing.

## Common Issues

- **No web-fetch tool available**: `scripts/fetch_page.py` needs only
  Python 3.8+ and prints the page as plain text with its `Last-Modified`
  header.
- **Question spans several pages** (e.g. "train a model" = login + storage
  + python + slurm): fetch each relevant page; do not stitch an answer from
  memory.
- **Status-related questions** ("is it down?", maintenance): use the
  `service-status` skill instead — status must never be answered from
  static content.

## Further Reading

- Documentation home: <https://docs.isambard.ac.uk/>
- Getting started:
  <https://docs.isambard.ac.uk/user-documentation/getting_started/>
- Getting support: <https://docs.isambard.ac.uk/getting_support/>
- AI-agent usage policy:
  <https://docs.isambard.ac.uk/user-documentation/guides/using_ai_agents/>
