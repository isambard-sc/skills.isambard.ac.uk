---
name: projects-and-accounting
description: >
  Guide for BriCS Isambard projects and node hour accounting (Isambard-AI and
  Isambard 3). Covers what a node hour (NHR) is and how a job's charge is
  calculated, NHR versus GPU hours, checking a project's budget and per-member
  usage in the BriCS Portal or Awards Portals (AIRRPortal, Allocate Portal),
  what happens when a project runs out of node hours, project roles (Project
  Lead, Project Co-Lead, Researcher), inviting and removing members,
  invitation expiry and approved email domains, follow-on projects, and who to
  ask for extensions, more node hours or a different Project Lead. Use this
  skill whenever a user asks how much budget or allocation is left, why the
  portal shows fewer hours than awarded, how much a job will cost, how to add
  or remove someone from a project, why an invitation failed, what happens at
  the end of a project, or how to get more node hours or an extension — even
  if they don't say "accounting".
license: >
  CC-BY-SA-4.0. Markdown/image content derived from
  https://docs.isambard.ac.uk/, © Bristol Centre for Supercomputing (BriCS).
compatibility: >
  Isambard-AI and Isambard 3. Budgets, usage and membership are managed in web
  portals (https://portal.isambard.ac.uk and the Awards Portals); there is no
  documented command-line tool for them. Membership changes can only be made
  by the Project Lead.
metadata:
  author: isambard-sc
  version: "1.0"
  source_url: https://docs.isambard.ac.uk/user-documentation/guides/accounting/
  supplementary_urls:
    - https://docs.isambard.ac.uk/user-documentation/guides/manage_project/
    - https://docs.isambard.ac.uk/user-documentation/guides/follow_on_project/
    - https://docs.isambard.ac.uk/user-documentation/guides/awards_portal/
    - https://docs.isambard.ac.uk/user-documentation/information/portals/
    - https://docs.isambard.ac.uk/user-documentation/information/project-policies/
    - https://docs.isambard.ac.uk/user-documentation/information/how-isambard-works/
    - https://docs.isambard.ac.uk/access/
    - https://docs.isambard.ac.uk/user-documentation/faqs/
---

# Projects and Accounting on Isambard

Source docs:

- https://docs.isambard.ac.uk/user-documentation/guides/accounting/
- https://docs.isambard.ac.uk/user-documentation/guides/manage_project/
- https://docs.isambard.ac.uk/user-documentation/information/portals/

## ⚠️ Critical Rules

- **BriCS cannot change an allocation.** BriCS cannot add node hours, extend
  a project, delay its start, extend the 30-day data grace period, raise
  storage quotas or relax job limits. These requests go from the Project
  Lead to the allocating body (see "Extensions and more node hours"). Never
  suggest a BriCS support ticket for them; support redirects such queries.
- **Only the Project Lead manages membership,** and cannot delegate it.
  Never suggest adding a second Project Lead to share the job; extra Leads
  are demoted to Project Co-Lead. Other members ask their Project Lead.
- **Invitations need a professional or institutional email address** in the
  award's approved domains. Never suggest inviting a personal address
  (Gmail, Outlook, etc.); exceptions go through the allocator.
- **Unused node hours are lost at the project end.** Projects are expected to
  use them evenly; hoarding them until the end causes long queues. Raise this
  with the user when a project is nearing its end with a large balance.
- **Project data is deleted after the project ends** (30-day grace period),
  and no storage is backed up. Jobs cannot be submitted once the project has
  expired, so plan copying data out well before the end date.
- **Don't invent a balance command.** Budgets and usage are documented only
  in the portals. If the user wants a number, send them to the portal.

## Node hours (NHR)

All usage is charged in node hours: one whole node for one hour is 1 NHR.
The charge is based on what Slurm **allocates**, not what was requested, and
time is rounded to the nearest second.

The fraction of a node charged is the **largest** of the fractions of each
resource allocated:

| System | Node | Fraction charged | Minimum |
|---|---|---|---|
| Isambard-AI | 4 GPUs, 288 CPU cores, 864 GB memory | max(GPUs / 4, cores / 288, memory / 864 GB) | 1 GPU (0.25 of a node) |
| Isambard 3 (Grace) | 144 CPU cores, 240 GB memory, no GPUs | max(cores / 144, memory / 240 GB) | 1 CPU core (1/144 of a node) |

Charge = fraction × nodes × wall-clock hours. Examples:

- Isambard-AI, 1 GPU and 1 CPU core for 1 hour: 0.25 NHR.
- Isambard-AI, 2 GPUs and all 288 cores for 1 hour: 1 NHR (all the CPUs).
- Isambard-AI, CPU-only work still gets at least 1 GPU: at least 0.25 NHR per
  hour.
- Isambard 3, 36 cores and 240 GB for 1 hour: 1 NHR (all the memory).
- 100 nodes for 5 seconds: 100 × 5 / 3600 ≈ 0.14 NHR.

The docs don't give charging rules for Isambard 3 MACS nodes; don't make
them up.

### NHR versus GPU hours

On Isambard-AI, **1 NHR = 4 GPU hours (GPUHR)**. Some allocators (e.g.
UKRI/DBIST) award GPUHR, so an award of 10,000 GPUHR in AIRRPortal shows as
2,500 NHR in the BriCS Portal. When a user says the portal shows a quarter of
what they were awarded, this is why.

### Estimating

Run time on a new system is hard to predict; estimate from measured
performance on other systems and err on the high side, because allocations
can't be topped up by BriCS.

## Checking budget and usage

| What | Where |
|---|---|
| Project total used and allocated | BriCS Portal (https://portal.isambard.ac.uk), or the project's card in its Awards Portal |
| Per-member usage, by day or month | "Usage Report" tab in the Awards Portal; hover a day for the per-member split; download as Excel or JSON |

## Running out of node hours

- A job starts only if the project has enough NHR left for it to run to
  completion; otherwise it is queued but not run, and Slurm may reject new
  submissions with `AssocGrp*Limit` errors such as
  `AssocGrpCPUMinutesLimit` or `AssocGrpGRESMinutesLimit`.
- Slurm reserves credit using the **requested** resources and `--time`, so
  large job arrays with long `--time` values can block new submissions even
  while the project appears to be within its allocation. Requesting a
  realistic `--time` helps. See the `slurm` skill for the fixes.
- Running jobs are never killed for lack of NHR, even if the balance goes
  negative.
- Login nodes stay available, e.g. to copy data off.
- When more NHR arrive (a new award, or a monthly tranche), jobs can start
  again.

## Roles

| Role (former name) | Can do |
|---|---|
| Researcher | Use the project's resources |
| Project Co-Lead (Co-Investigator) | Use the resources; query charges |
| Project Lead (Principal Investigator) | All of the above; manage membership; legally responsible for the project and its members' actions |

- There is one Project Lead per project. To change who it is, the Project
  Lead contacts the allocator.
- Every member can submit jobs that spend the project's node hours. There is
  no per-member limit or permission; the only control is membership.
- To query a charge, the Project Lead or a Project Co-Lead raises a ticket at
  https://support.isambard.ac.uk with the project and the specific charge.

## Which portal?

Most projects come from an award made through an **Awards Portal**; some are
created directly on the **BriCS Portal**.

| Task | Portal |
|---|---|
| First login, policies, UNIX username | BriCS Portal (see the `login` skill) |
| Budget and usage | BriCS Portal or the Awards Portal |
| Membership, project created from an award | The Awards Portal |
| Membership, project created on the BriCS Portal | BriCS Portal |

| Awards Portal | Awards |
|---|---|
| AIRRPortal (https://portal-airr.isambard.ac.uk) | AI Research Resource: DBIST/UKRI calls, Sovereign AI, AISI |
| Allocate Portal (https://allocate.isambard.ac.uk) | University of Bristol and GW4 allocations |

If unsure which applies, check the invitation email or ask the Project Lead.
Trying to manage an award-based project's membership on the BriCS Portal
shows a pop-up linking to the right Awards Portal.

## Managing members (Project Lead)

### Invite

1. In the right portal, open the award or project → "Team" → "Invitations".
2. "Add" → "Invite by mail", enter the email address and choose the role.
3. "Continue", optionally add a message, then "Send invitation".

- Invitations expire after **30 days** ("Expires at" column). Status shows
  "Pending" until accepted, then "Accepted". Use "Actions" → "Resend" or
  "Cancel".
- Use the address the person's institution gives MyAccessID. Some register
  a form like `ab12345@university.ac.uk` rather than `first.last@...`, and
  an invitation to the wrong form won't work. Invitations can't be
  forwarded; send a new one to the right address.
- Addresses outside the approved domains need the allocator's agreement
  (link in the invitation dialog).

### Remove or edit

"Team" → "Active" → "Actions":

- "Edit" changes the role or sets a date for automatic removal.
- "Remove" stops new logins and connections at once, but existing
  connections last until they expire and **running jobs keep running** (and
  charging). To stop them, or for an urgent removal, raise a ticket at
  https://support.isambard.ac.uk.
- Removing someone does not delete their files from project storage; the
  Project Lead is responsible for that data.
- Someone removed from all their projects can no longer log in to the
  portal.

A member who leaves their institution must leave the service: accounts must
be backed by a valid professional or institutional email. Some universities
offer visiting, honorary or associate status that keeps them eligible.

## Project end and follow-on projects

- After the end date, members can no longer use the project's compute or
  storage. There is a **30-day grace period** to copy data off; after that
  it may be deleted for good. Jobs can't be submitted for an expired
  project, so copying is limited to login nodes, which is slow for large
  data. The exception is pulling the data from another, still active
  project with a job run in that project (see the `data-transfer` skill).
- The allocator decides how work continues:
  - **Additional node hours** on the existing project (e.g. monthly):
    shown in the portal; data and members stay.
  - **A new project:** the Project Lead is added to a new award in the
    Awards Portal and invites members again. The old project still ends on
    its date. For a confirmed, immediate follow-on, the Project Lead may
    raise a ticket for help moving data. Requests to keep data for an
    unconfirmed follow-on are refused.

## Extensions and more node hours

The Project Lead asks the allocating body; other members go through their
Project Lead.

- **University of Bristol allocation** (project name starts with `uob`, or
  applied via allocate.isambard.ac.uk): follow the policy at
  https://apply.isambard.ac.uk/bristol/#research-use
- **All other projects:** contact the allocating body. Current contact
  details for each route (DBIST/UKRI, Sovereign AI, UKRI Tier 2, GW4
  institutions) are on https://docs.isambard.ac.uk/access/ — fetch it rather
  than guessing an address.

## Troubleshooting

| Symptom | Cause and fix |
|---|---|
| Portal shows a quarter of the awarded hours | GPUHR awarded, NHR displayed: 1 NHR = 4 GPUHR. |
| Jobs pending or rejected with `AssocGrp*Limit` | Project out of NHR, or credit reserved by queued jobs' `--time`. See "Running out of node hours". |
| Charge higher than expected | Charged on the largest resource fraction allocated (e.g. many CPU cores or much memory with few GPUs), with a minimum of 1 GPU on Isambard-AI. |
| Removed member still charging | Their running jobs continue. Raise a ticket to have them killed. |
| Invitation not arriving or not working | Expired (30 days), wrong address form, or domain not approved. Resend to the institutional address. |
| Can't manage members on the BriCS Portal | Project comes from an award; use the Awards Portal. |
| Award still "Pending" | Up to 5 working days after any embargo; the Project Lead follows up with the allocator (see the `login` skill). |

## Further Reading

- Accounting: https://docs.isambard.ac.uk/user-documentation/guides/accounting/
- Managing awards and projects: https://docs.isambard.ac.uk/user-documentation/guides/manage_project/
- Follow-on projects: https://docs.isambard.ac.uk/user-documentation/guides/follow_on_project/
- Portals overview: https://docs.isambard.ac.uk/user-documentation/information/portals/
- Project policies: https://docs.isambard.ac.uk/user-documentation/information/project-policies/
- Applying for access: https://docs.isambard.ac.uk/access/
- Storage and data retention: https://docs.isambard.ac.uk/user-documentation/information/system-storage/
