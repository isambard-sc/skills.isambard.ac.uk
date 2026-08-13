---
name: service-status
description: >
  Check the LIVE operational status of Isambard facilities and report recent
  platform changes. Use this skill whenever a user asks whether Isambard-AI,
  Isambard 3 (Grace or MACS), or BlueCrystal 5 is down, degraded, or in
  maintenance, reports login failures or unexpected job problems, asks about
  known issues, outages, or upcoming maintenance windows, or asks what
  changed recently (documentation updates, new clifton releases, isambard-sc
  GitHub activity). Always run the bundled scripts to fetch live pages —
  never answer service-status questions from memory or training data.
compatibility: >
  Runs on the user's local machine with Python 3.8+ and outbound HTTPS
  (standard library only). Does not require access to an Isambard login
  node.
metadata:
  author: Shiran
  version: "1.0"
  source_url: https://docs.isambard.ac.uk/service-status/
  supplementary_urls:
    - https://docs.isambard.ac.uk/service-status/known_issues/
    - https://docs.isambard.ac.uk/service-status/planned_maintenance/
    - https://docs.isambard.ac.uk/service-status/archived_issues/
---

# Service Status — Agent Skill

Full documentation: <https://docs.isambard.ac.uk/service-status/>

## ⚠️ Critical Rules

- **Never report Isambard service status from memory or training data.**
  Run `scripts/check_status.py` (or fetch the status pages directly) on
  every status question, every time.
- Always state the source URL and the page's `Last-Modified` time in the
  answer, so the user knows how fresh the information is.
- If the live fetch fails, report the status as **UNKNOWN** and give the
  user the URL to check — do not guess or assume "no known issues".
- When a user reports an error (login failure, job stuck, service
  unreachable), check known issues **before** starting to debug — many
  reported "bugs" are documented outages.
- Treat maintenance windows as UK time (Europe/London) unless the page
  states otherwise.
- The unauthenticated GitHub API allows 60 requests/hour per IP. Do not
  call `check_updates.py` in a loop; set `GITHUB_TOKEN` if it returns 403.

## Overview

The authoritative status source is the service-status section of
`docs.isambard.ac.uk` (`status.isambard.ac.uk` redirects there; there is
no separate status platform and no JSON status API). It reports a
plain-text status per facility — Isambard-AI, Isambard 3 Grace, Isambard 3
MACS, and BlueCrystal 5 — plus known-issues and planned-maintenance pages.

Pages sit behind a CDN cache of up to ~10 minutes; the `Last-Modified`
HTTP header is the honest freshness signal and both scripts print it.

## Check current status

```bash
python3 scripts/check_status.py          # overview + known issues + maintenance
python3 scripts/check_status.py --all    # also include archived (resolved) issues
```

Report status **per system** and name the system the user cares about
explicitly. Quote the relevant status text rather than paraphrasing labels.

## Check recent updates

```bash
python3 scripts/check_updates.py --days 14
```

Reports, in one pass:

- when the docs site was last redeployed (`Last-Modified`),
- documentation pages added or removed since the previous run (sitemap
  diff, cached under `~/.cache/isambard-service-status/`),
- `isambard-sc` GitHub repositories pushed within the window, their recent
  commits, and the latest releases of key user-facing repositories
  (clifton, skills.isambard.ac.uk, buildit).

The sitemap diff cannot detect content changes inside an existing page —
say so if the user asks whether a specific page changed.

## Common Issues

- **Script cannot reach the network**: fetch
  <https://docs.isambard.ac.uk/service-status/> with a web tool instead,
  and mention which method was used.
- **GitHub section returns 403**: unauthenticated rate limit exhausted;
  export `GITHUB_TOKEN` and re-run.
- **First run of `check_updates.py`**: the sitemap is only being cached,
  so no page diff is available until the next run.

## Further Reading

- Service status: <https://docs.isambard.ac.uk/service-status/>
- Known issues: <https://docs.isambard.ac.uk/service-status/known_issues/>
- Planned maintenance:
  <https://docs.isambard.ac.uk/service-status/planned_maintenance/>
- Getting support: <https://docs.isambard.ac.uk/getting_support/>
