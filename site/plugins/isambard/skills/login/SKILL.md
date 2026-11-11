---
name: login
description: >
  Guide for getting access to and logging in to BriCS Isambard facilities
  (Isambard-AI and Isambard 3, including MACS) over SSH with Clifton. Covers
  first-time portal setup (identity providers, accepting policies and
  invitations), setting the permanent UNIX short name, installing Clifton,
  clifton auth and clifton ssh-config write, the 12-hour SSH certificate, host
  aliases such as PROJECT.aip2.isambard, checking host key fingerprints, and
  the rules and resource limits on login nodes. Use this skill whenever a user
  can't log in or connect, sees "User short name is empty", "You are not
  authorised to connect", "clifton: command not found", dropped SSH sessions,
  or "Resource temporarily unavailable" / EAGAIN errors on a login node, or
  asks about SSH config, VS Code Remote-SSH, MobaXterm or tmux on Isambard —
  even if they don't mention Clifton.
license: >
  CC-BY-SA-4.0. Markdown/image content derived from
  https://docs.isambard.ac.uk/, © Bristol Centre for Supercomputing (BriCS).
compatibility: >
  Isambard-AI and Isambard 3 (Grace and MACS). Clifton runs on the user's own
  machine (macOS, Linux including WSL, or Windows). The portal steps and the
  browser step of clifton auth must be done by the user.
metadata:
  author: isambard-sc
  version: "1.0"
  source_url: https://docs.isambard.ac.uk/user-documentation/guides/login/
  supplementary_urls:
    - https://docs.isambard.ac.uk/user-documentation/guides/shortname/
    - https://docs.isambard.ac.uk/user-documentation/tutorials/setup/
    - https://docs.isambard.ac.uk/user-documentation/getting_started/
    - https://docs.isambard.ac.uk/user-documentation/information/how-isambard-works/
    - https://docs.isambard.ac.uk/user-documentation/guides/mobaxterm/
    - https://docs.isambard.ac.uk/user-documentation/guides/using_ai_agents/
    - https://docs.isambard.ac.uk/user-documentation/faqs/
---

# Logging in to Isambard

Source docs:

- https://docs.isambard.ac.uk/user-documentation/guides/login/
- https://docs.isambard.ac.uk/user-documentation/tutorials/setup/
- https://docs.isambard.ac.uk/user-documentation/guides/shortname/
- https://docs.isambard.ac.uk/user-documentation/getting_started/

## ⚠️ Critical Rules

- **The user authenticates, not the agent.** Portal login and the browser
  step of `clifton auth` happen in the user's browser with their own
  identity provider. Never ask for, read, or store the user's password or
  SSH private key.
- **Never bypass the 12-hour SSH certificate.** Do not leave `tmux`,
  `screen` or similar sessions running on a login node after disconnecting,
  and do not give an agent a persistent connection to Isambard. Persistent
  sessions keep an authenticated connection alive indefinitely, are against
  BriCS security policy, and may be terminated without warning. Bypassing
  the time-limited certificates, including by AI agents, violates the
  [Access Terms](https://docs.isambard.ac.uk/policies/access_terms/). When the
  certificate expires, run `clifton auth` again.
- **Never run long-running or compute-intensive work on a login node.** This
  includes large data transfers, parallel builds and anything that spawns
  many processes or threads. It is Unacceptable Use under the
  [Acceptable Use Policy](https://docs.isambard.ac.uk/policies/acceptable_use/)
  and may be stopped without warning. Submit it to the compute nodes with
  Slurm.
- **Never run an AI agent itself on a login node.** Keep the agent on the
  user's own machine; see
  https://docs.isambard.ac.uk/user-documentation/guides/using_ai_agents/.
- **The UNIX short name is permanent.** Never choose or submit one on the
  user's behalf, and make sure they know it cannot be changed and will be
  visible to their project and collaborators.
- **Never guess host aliases.** Use the aliases printed by
  `clifton ssh-config write`; they depend on the user's projects.
- **Never tell the user to accept an unrecognised host key.** Compare the
  fingerprint shown with the live list at
  https://docs.isambard.ac.uk/user-documentation/guides/login/#host-fingerprints
  first.
- **Never edit `~/.ssh/config_clifton`.** Clifton overwrites it. Put custom
  SSH config in `~/.ssh/config`.
- **Award activation delays go to the Project Lead, not BriCS support.**
  Activation is managed by the allocator.

## Overview

Getting from "added to a project" to a shell prompt on Isambard:

1. The award becomes active (projects created from an Awards Portal only).
2. Log in to the BriCS portal (https://portal.isambard.ac.uk) with an
   identity provider.
3. Accept the access terms and policies.
4. Accept the project invitation (projects created directly on the BriCS
   portal only).
5. Set a UNIX short name.
6. Install Clifton, then run `clifton auth` (every day) and
   `clifton ssh-config write` (after joining a new project).
7. Connect with `ssh PROJECT.<facility>.isambard`.

Steps 1–5 are one-off. When diagnosing a login problem, find the first step
that hasn't been completed.

## 1. Award activation

If the project came from an award (e.g. AIRRPortal), the user cannot connect
to any BriCS system until the award is active. In the Awards Portal a pending
award shows a "Pending" badge; once active it shows "Active" and a
"Go to project" button.

- Setup takes up to 5 working days, counted from when any allocator embargo
  is lifted, not from the project start date. Embargoes can last much longer.
- If it seems too slow, the user contacts their Project Lead, who follows it
  up with the allocator. Do not suggest contacting BriCS support.

## 2. First portal login

The user logs in at https://portal.isambard.ac.uk ("Click here to login")
and picks an identity provider:

| Identity provider | Who uses it |
|---|---|
| University Login (MyAccessID) | Anyone with a university account. Most users. |
| AISI (Okta login) | AI Security Institute staff |
| NCC Login | NCC staff invited at an `@nccuk.com` address |
| Other Login (IdP of last resort) | People without a supported university account. Uses an AWS Identity Center account that BriCS creates, up to 3 working days after joining an award. See https://docs.isambard.ac.uk/user-documentation/guides/aws_accounts/ |
| BriCS | Administrators only. Never use. |

To be let in, the user must be in an active award (added by the Project Lead)
or have an invitation to a project on the BriCS portal.

## 3–4. Policies and invitation

- On first login the portal shows the Access Terms, then at least the
  Acceptable Use Policy and Data Privacy Policy. The user reads each and types
  `accept`. They are asked again only if a policy changes.
- Direct BriCS portal projects only: the user clicks "Accept Invitation" in
  the email from `noreply@support.isambard.ac.uk` (check spam), in the same
  browser they logged in with. "Cancel invitation" blocks the account; if
  clicked by accident, ask the inviter to resend.

## 5. UNIX short name

Required before any SSH login. In the portal: user button (top right) →
"User Dashboard" → "Edit" tab → "UNIX username" row → pen icon → "Submit".

Rules: 5–20 characters, lower-case letters and digits only, starting with a
letter. It **cannot be changed** once set.

## 6. Clifton

Clifton gets a signed SSH certificate (valid for 12 hours) and writes SSH
config for the user's projects. It runs on the user's own machine.

### SSH key

Clifton needs an SSH key pair. Supported: Ed25519, or RSA of 3072 bits or
more (any modern key type). DSA and RSA under 3072 bits are not supported.
The private key must contain `-----BEGIN OPENSSH PRIVATE KEY-----`. To create
one:

```bash
ssh-keygen -t ed25519 -C "your_email@example.com"
```

### Install

macOS (Apple Silicon; use `clifton-macos-x86_64` on Intel):

```bash
curl --location https://github.com/isambard-sc/clifton/releases/latest/download/clifton-macos-aarch64 --output clifton
chmod u+x clifton
sudo mv clifton /usr/local/bin/
```

Linux, including WSL (x86_64; use `clifton-linux-musl-aarch64` on Arm):

```bash
curl --location https://github.com/isambard-sc/clifton/releases/latest/download/clifton-linux-musl-x86_64 --output clifton
chmod u+x clifton
mkdir -p ~/.local/bin
mv clifton ~/.local/bin/
```

Windows (then close and reopen the terminal):

```powershell
winget install clifton
```

- Update by repeating the same commands (`winget upgrade clifton` on
  Windows).
- If the binary isn't on `$PATH`, run it by path, e.g. `./clifton auth`.
- On macOS, a binary downloaded with a browser may be blocked ("Apple cannot
  check it for malicious software"). Allow it in System Settings → Privacy &
  Security (needs admin rights), or download with `curl` instead.

### Authenticate and configure

```bash
clifton auth                    # every day you use the service
clifton ssh-config write        # after joining a new project
```

- `clifton auth` opens the browser (or shows a QR code) to authorise in the
  portal with the same account used at setup. It looks for keys in standard
  locations such as `~/.ssh/id_ed25519`; for another key use
  `clifton auth --identity /path/to/ssh_key`.
- Success looks like:

  ```text
  Successfully authenticated as YOUR_EMAIL_ADDRESS (YOUR_SHORT_NAME) and downloaded SSH certificate for projects:
   - PROJECT_NAME

  Certificate file written to ~/.ssh/id_ed25519-cert.pub
  Certificate valid for 11 hours and 59 minutes.
  ```

- `clifton ssh-config write` writes `~/.ssh/config_clifton`, adds an
  `Include` for it to `~/.ssh/config`, and prints the host aliases the user
  can connect to.

### Connect

Aliases have the form `PROJECT.<facility>.isambard`, for example:

```bash
ssh PROJECT.aip2.isambard     # Isambard-AI
ssh PROJECT.3.isambard        # Isambard 3
ssh PROJECT.macs3.isambard    # Isambard 3 MACS
```

The account on the facility is project-specific (the prompt shows
`user.project@...`). On first connection, check the host key fingerprint
against https://docs.isambard.ac.uk/user-documentation/guides/login/#host-fingerprints.

## Working on login nodes

Login nodes are for preparing and managing jobs: editing files, file
transfer and compression, software and container builds, submitting and
checking jobs. Everything heavy goes to the compute nodes through Slurm (see
the `slurm` skill).

- Login nodes are assigned at random on each connection. The user cannot
  choose one, and may not reach the same one again.
- Login nodes may have different hardware to compute nodes, so software
  built on a login node with hardware auto-detection may not be optimal on
  the compute nodes.
- Login nodes have no GPUs.
- Bash ends a session after **24 hours** with no input.
- On Isambard-AI each login session has cgroup limits, at the time of
  writing: **1 CPU core, 4 GiB memory, 500 tasks**. Check the current values
  in the FAQ entry on "Resource temporarily unavailable" errors
  (https://docs.isambard.ac.uk/user-documentation/faqs/).
- `tmux` and `screen` may be used to manage windows within one SSH session,
  but not as persistent sessions (see Critical Rules).
- VS Code (or a similar IDE) over SSH to a login node is allowed for
  lightweight work such as editing, as long as it isn't running
  compute-intensive or long-running processes in the background. For heavier
  work, run VS Code on a compute node:
  https://docs.isambard.ac.uk/user-documentation/guides/vscode/

### Environment

- The only supported shell is `bash`. Other shells are used at the user's
  own risk and are not supported.
- There is no `sudo`. Point installers at `$HOME` or `$PROJECTDIR`; for
  packages that need root to install OS packages, use a container with
  `--fakeroot` (Apptainer) or `--user=root` (Podman-HPC).
- System time is UTC. Set `export TZ=GB` (or another zone) to change what
  the user sees.

## SSH config

To stop idle sessions from being closed early, add this to `~/.ssh/config`
(not `~/.ssh/config_clifton`). Values between 60 and 480 are enough:

```ssh
Match originalhost *.isambard
    ServerAliveInterval 60
```

## MobaXterm

MobaXterm is **not supported by BriCS** and its guide is due to be
deprecated. Recommend Clifton with a standard SSH client instead. If the user
insists, point them to
https://docs.isambard.ac.uk/user-documentation/guides/mobaxterm/ and note
that MobaXterm fails silently without a valid certificate, so run
`clifton auth` first.

## Troubleshooting

| Symptom | Cause and fix |
|---|---|
| `Something went wrong: User short name is empty.` | Short name not set. Set it in the portal (step 5). If it's set but the error persists, log out of the portal, then sign out at https://account.isambard.ac.uk, and log in again. |
| `clifton: command not found` | Not installed, or not on `$PATH` (some Linux systems lack `~/.local/bin` in `$PATH`). Add it to `$PATH`, move `clifton` to a directory on `$PATH`, or run it by path. |
| "You are not authorised to connect" in the portal | Award not active yet (up to 5 working days after any embargo), or logged in with a different email address from the one invited. The error shows the address used. |
| Invitation link doesn't work | Expired (the Project Lead resends it), sent to a different address from the one the institution gives MyAccessID (e.g. `ab12345@university.ac.uk` vs `first.last@...`; the Project Lead must re-invite at the right address), or an outage (check https://docs.isambard.ac.uk/service-status/). |
| "Your invitation ... is under review" | A manual review, normally within 72 hours. If longer, email support@isambard.ac.uk or ask the Project Lead to raise a ticket. |
| Institution not in MyAccessID list | Try "Other Login (IdP of last resort)". If the institution has limited MyAccessID support, contact its IT team first, then ask the Project Lead to raise a ticket for an IdP of last resort account. |
| Portal login loops or fails | Try a private browser window. If that works, clear the site's cookies. |
| SSH fails after working earlier | Certificate expired (12 hours). Run `clifton auth`. |
| New project's alias missing, or no access to it | Run `clifton auth` then `clifton ssh-config write`. If still missing, sign out at https://account.isambard.ac.uk and repeat. |
| SSH session closes when idle | Add `ServerAliveInterval` (see SSH config). Bash also ends sessions after 24 hours with no input. |
| `fork: Resource temporarily unavailable`, `BlockingIOError: [Errno 11]`, `RuntimeError: can't start new thread`, `spawn EAGAIN` | Login node task limit reached. |
| `Killed`, `Cannot allocate memory` | Login node memory limit reached. |
| Commands very slow on login node | CPU throttled at the login node limit. |
| VS Code: "Unable to start process", "Terminal process failed to launch", lost connection | Often a login node limit hit by an extension or language server, not a network problem. |
| Can't connect from outside the UK | Often compliance or technical reasons outside BriCS's control. If it seems to be a BriCS service issue, raise a helpdesk ticket. |

For the resource limit rows: move the work to a compute node, with the
Isambard-AI Phase 2 `interactive` reservation or a batch job (see the
`slurm` skill).

## Further Reading

- Log in: https://docs.isambard.ac.uk/user-documentation/guides/login/
- Setup tutorial: https://docs.isambard.ac.uk/user-documentation/tutorials/setup/
- Getting started: https://docs.isambard.ac.uk/user-documentation/getting_started/
- How Isambard works: https://docs.isambard.ac.uk/user-documentation/information/how-isambard-works/
- Using AI agents: https://docs.isambard.ac.uk/user-documentation/guides/using_ai_agents/
- FAQs: https://docs.isambard.ac.uk/user-documentation/faqs/
- Acceptable Use Policy: https://docs.isambard.ac.uk/policies/acceptable_use/
- Clifton: https://github.com/isambard-sc/clifton
