---
name: getting-support
description: >
  Guidance on how to get help with Isambard-AI and Isambard 3, including
  when and how to raise a support ticket on the BriCS helpdesk, checking
  service status and known issues first, and what to include in a ticket.
  Use this skill whenever a user hits an error or blocker on Isambard,
  asks how to contact support, report a bug, request help, or check for
  an outage, or before telling a user to "raise a ticket" or "contact
  support".
compatibility: >
  Isambard-AI and Isambard 3 (Grace, MACS). No special access required —
  the helpdesk and status pages are reachable from any browser.
metadata:
  author: isambard-sc
  version: "1.0"
  source_url: https://docs.isambard.ac.uk/getting_support/
  supplementary_urls:
    - https://docs.isambard.ac.uk/service-status/
    - https://docs.isambard.ac.uk/service-status/known_issues/
    - https://docs.isambard.ac.uk/user-documentation/faqs/
---

# Getting Support on Isambard — Agent Skill

https://docs.isambard.ac.uk/getting_support/
https://docs.isambard.ac.uk/service-status/
https://docs.isambard.ac.uk/service-status/known_issues/
https://docs.isambard.ac.uk/user-documentation/faqs/

## ⚠️ Critical Rule: Check Before You Raise a Ticket

- Never tell a user to email BriCS for support.
  All support goes through the helpdesk at https://support.isambard.ac.uk.
- Before raising a ticket, check, in order:
  1. The [User Documentation](https://docs.isambard.ac.uk) search bar —
     the issue may already be covered by a guide.
  2. [Known Issues](https://docs.isambard.ac.uk/service-status/known_issues/)
     — the problem may be a known, already-reported issue.
  3. [Service Status](https://status.isambard.ac.uk) — the problem may be
     part of an ongoing outage or planned maintenance.
  4. [FAQs](https://docs.isambard.ac.uk/user-documentation/faqs/) — the
     question may already be answered.
- Raising a ticket for a known outage or already-documented issue creates
  unnecessary load on the helpdesk — always check status first.
- Submit **one ticket per issue** — do not bundle unrelated problems into
  a single ticket.
- Raising a helpdesk ticket requires membership of an active project.
- **Never submit an AI-generated ticket unreviewed.** Draft the ticket
  content for the user to check, don't submit it on their behalf without
  review — speculative diagnoses or assumptions in a ticket slow down
  resolution rather than helping.

## Overview

BriCS (Bristol Centre for Supercomputing) provides support for Isambard-AI
and Isambard 3 through a web-based helpdesk. The
helpdesk is built on Zammad and reached at https://support.isambard.ac.uk,
using federated login via institutional identity (the same login used for
Isambard systems).

## Checking Service Status First

Before raising a ticket, always check:

- **Service status:** https://status.isambard.ac.uk — shows current and
  recent outages across Isambard-AI and Isambard 3.
- **Known issues:** https://docs.isambard.ac.uk/service-status/known_issues/
  — lists issues that are already known and being tracked.
- **Planned maintenance:** listed alongside service status — scheduled
  downtime is not a fault and does not need a ticket.

If the issue matches a known outage or planned maintenance window, do not
raise a ticket — wait for the status page to be updated instead.

## Raising a Support Ticket

1. Go to https://support.isambard.ac.uk in a browser, click **"Click here
   to login"**, choose **University Login (MyAccessID)**, then select your
   institution and authenticate with institutional credentials.
2. Click the **green plus (+) icon** in the bottom section of the sidebar
   to open a new ticket.
3. Enter a clear, specific title and fill in the description with:
   - Your **project name** (as shown on the BriCS portal)
   - The **facility** involved (Isambard-AI Phase 1/2, Isambard 3 Grace/MACS)
   - Your **UNIX username**, if applicable
   - What you were trying to do, and the exact command(s) run
   - Full diagnostic information — paste the actual error output, including
     tracebacks or stack traces, rather than describing it generically
   - When the issue occurred
4. Attach supporting material if helpful — a screenshot, or a `.txt` file
   of the terminal session (job ID, `sacct`/`squeue` output, error logs).
5. Leave **State** set to "new" and click **Create**. A member of the
   Isambard team will respond during normal working hours.

Open one ticket per distinct issue — do not add unrelated problems to an
existing ticket.

## After Submitting a Ticket

- Optionally opt in to **email notifications** for ticket updates — this
  option is available when creating a ticket or posting a reply on
  https://support.isambard.ac.uk.
- The ticket interface is a web chat — add further information, logs, or
  context to an open ticket at any time through this interface.
- Once the issue is resolved, close the ticket using the **State**
  dropdown menu.

## Troubleshooting

| Situation | What to do |
|---|---|
| User asks for a support email address | There isn't one — direct them to https://support.isambard.ac.uk |
| User can't submit a ticket | Confirm they are a member of an active project; helpdesk access requires this |
| User has multiple unrelated issues | Open a separate ticket for each one |
| User reports something that looks systemic (many users affected) | Check https://status.isambard.ac.uk first — it may already be tracked |
| User wants to know if others are affected | Point them to Known Issues and Service Status rather than speculating |
| User wants help installing or debugging their own third-party software | BriCS support cannot help with installation or use of user software — point them to relevant guides/tutorials first; only raise a ticket if the problem looks like a platform issue |

## Further Reading

- Getting Support: https://docs.isambard.ac.uk/getting_support/
- Service Status: https://status.isambard.ac.uk
- Known Issues: https://docs.isambard.ac.uk/service-status/known_issues/
- FAQs: https://docs.isambard.ac.uk/user-documentation/faqs/
- Full documentation: https://docs.isambard.ac.uk/
