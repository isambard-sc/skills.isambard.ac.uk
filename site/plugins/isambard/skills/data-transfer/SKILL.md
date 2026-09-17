---
name: data-transfer
description: >
  Guide for transferring data to, from, and between BriCS Isambard facilities
  (Isambard-AI Phase 1, Isambard-AI Phase 2, Isambard 3). Covers the standard
  scp/rsync-over-SSH workflow (including clifton for project-to-project
  transfers and submitting large transfers as Slurm jobs) and the early-access
  data mover service (S3-compatible staging storage accessed via rclone or
  AWS CLI, with Netham for temporary credentials). Use this skill whenever a
  user asks how to copy, upload, download, sync, or move files/data to or
  from Isambard, between projects, or between BriCS clusters, or asks about
  scp, rsync, tar transfers, the data mover, rclone, AWS CLI, Netham, or S3
  staging buckets on Isambard — even if the user doesn't name a specific tool.
license: >
  CC-BY-SA-4.0. Markdown/image content derived from
  https://docs.isambard.ac.uk/, © Bristol Centre for Supercomputing (BriCS).
compatibility: >
  Isambard-AI (Phase 1 and Phase 2) and Isambard 3. The scp/rsync workflow
  requires SSH access set up via clifton. The data mover service additionally
  requires the user to have been granted early access, and its client tools
  (Netham, rclone/AWS CLI) are only supported on Mac and Linux — Windows
  users need WSL.
metadata:
  author: isambard-sc
  version: "1.1"
  source_url: https://docs.isambard.ac.uk/user-documentation/guides/file_transfer/
  supplementary_urls:
    - https://docs.isambard.ac.uk/user-documentation/tutorials/data-mover/
    - https://docs.isambard.ac.uk/user-documentation/information/system-storage/
---

# Data Transfer on Isambard

There are two ways to move data to, from, and between BriCS Isambard facilities:

| Method | Status | Best for |
|--------|--------|----------|
| `scp` / `rsync` over SSH (via `clifton`) | **Stable** — default method for all users | Local machine ↔ facility, project ↔ project on the same facility |
| Data mover (S3 staging + `rclone`/AWS CLI + `netham`) | **Early access** — requires being granted access, under active development | Large-scale parallel transfers, and transfers between different facilities (e.g. Isambard-AI Phase 2 and Isambard 3) |

BriCS staff do not copy or move data on behalf of users, and bespoke transfers
cannot be arranged by exception. Every transfer described here is one the
user runs themselves.

> **No storage on Isambard is backed up.** All storage on BriCS facilities —
> `$HOME`, `$PROJECTDIR`, `$SCRATCHDIR`, and the data mover's S3 staging area
> alike — is working storage only. It is not backed up and is not intended
> for long-term or archival storage of data. Users are responsible for
> regularly backing up important data to another location throughout the
> project, and for copying off any data that should remain accessible before
> the project end date — data cannot be recovered once it is lost.

## Critical Rules

- ⚠️ **No storage is backed up.** Never let a user assume any Isambard
  storage area is durable or recoverable. Proactively raise data
  egress/backup planning for a whole-project timeline, not just at the end —
  see the warning above.
- ⚠️ **The data mover is early access.** Only suggest it to a user who has
  confirmed they have been granted access. Its endpoints, configuration, and
  behaviour may change without notice, and it is under active development —
  do not present it as a stable, general-availability service.
- Never run a large transfer directly on a login node. Login node sessions
  are resource-limited (on Isambard-AI, the equivalent of one CPU core and
  4 GiB of memory); a large `scp`/`rsync`/`rclone` copy started there is
  likely to be killed by the out-of-memory killer. Submit it as a Slurm job
  instead.
- Never treat data mover S3 staging storage as persistent storage or a
  backup. Data not modified for 30 days is automatically deleted, and it is
  separate from `$HOME`/`$PROJECTDIR`.
- Always verify `rclone --version` is `>= v1.61.0` before configuring it for
  the data mover — older versions are incompatible with the service.
- Always use a dry run before deleting from a shared data mover bucket
  (`rclone delete --dry-run` or `aws s3 rm --dryrun`) — every member of a
  project shares full read/write/delete access to that project's bucket.
- Always copy data out of an expiring project before its end date. Once a
  project has expired, jobs can no longer be submitted from it (so large
  Slurm-based transfers are unavailable), leaving only slow login-node
  transfers during the 30-day grace period — or a job run from a still-active
  project that pulls the data across.
- Never use `mpirun`/`mpiexec`, and never assume a graphical SFTP client is
  officially supported — none is currently documented.

---

## Overview

For the vast majority of transfers — to/from a local machine, or between
projects on the same facility — use `scp` or `rsync` over SSH. This is the
default, fully supported method and requires no extra setup beyond the SSH
access already configured via `clifton` (see the Isambard login guide).

The data mover service is a newer, early-access alternative. It provides
token-authenticated access to on-premise S3 object storage that acts as a
staging area, reachable over the internet and internally across BriCS
clusters. It exists to support highly parallel, large-scale transfers over a
network path that is separate from SSH traffic, and to make it easier to move
data laterally between different BriCS clusters (e.g. Isambard-AI Phase 2 and
Isambard 3), which the SSH-based workflow cannot do directly. Only recommend
it once a user has confirmed they have early access, and always caveat it as
early access / under active development.

---

## Transferring data over SSH (scp / rsync)

### Local machine ↔ facility

```bash
# Copy a remote file to the local machine
scp PROJECT.FACILITY.isambard:remote_file.txt .
rsync --archive --verbose --compress PROJECT.FACILITY.isambard:remote_file.txt .

# Copy a local file to the facility
scp local_file.txt PROJECT.FACILITY.isambard:
rsync --archive --verbose --compress local_file.txt PROJECT.FACILITY.isambard:

# Copy a directory recursively
scp -r local_dir PROJECT.FACILITY.isambard:
rsync --archive --verbose --compress local_dir PROJECT.FACILITY.isambard:
```

`PROJECT` and `FACILITY` are the values that appear in SSH host names
generated by `clifton`. On macOS, the bundled `rsync` is old and slow —
recommend installing a newer version (`brew install rsync` or
`sudo port install rsync`) before large transfers.

### Many small files

Transferring a large number of small files is inefficient — each file needs
a separate access/transfer/check round trip. Package them first with `tar`:

```bash
# Local -> facility
tar c local_dir | ssh PROJECT.FACILITY.isambard 'cat > remote_file.tar'
# ... or extract automatically on the remote side:
tar c local_dir | ssh PROJECT.FACILITY.isambard 'tar x'

# Facility -> local
ssh PROJECT.FACILITY.isambard 'tar c remote_dir' > local_file.tar
# ... or pipe directly into tar to extract:
ssh PROJECT.FACILITY.isambard 'tar c remote_dir' | tar x
```

### Project ↔ project on the same facility

⚠️ Confirm the user has permission from the source project's PI before
transferring data between projects — this can raise privacy or licensing
concerns, and the PI is legally responsible for any breach.

Two options:

1. **Project public shared storage** — `cp -r` a directory into
   `/projects/public/PROJECT`, which is writeable by project members and
   readable by all users of the facility.
2. **`scp`/`rsync` via `clifton`** — install and authenticate `clifton` in
   the source project account, run `clifton ssh-config write`, then comment
   out the `ProxyJump` directive for the relevant `Host` in
   `~/.ssh/config_clifton`. Transfer as normal:

   ```bash
   scp -r dir PROJECT2.FACILITY.isambard:
   rsync --archive --verbose --compress dir PROJECT2.FACILITY.isambard:
   ```

### Large transfers as a Slurm job

Submit anything beyond a handful of files as a job rather than running it on
the login node — the transfer is limited by storage/network throughput, not
by compute, so request a single task on a single node (one GPU on
Isambard-AI, to get a whole GH200 Superchip's allocation).

```bash
#!/bin/bash
#SBATCH --job-name=project-transfer
#SBATCH --output=project-transfer.out
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --gpus=1          # omit this line on Isambard 3
#SBATCH --time=06:00:00

rsync --archive --verbose --partial --human-readable dir PROJECT2.FACILITY.isambard:
```

```bash
sbatch project-transfer.sh
```

- `rsync --partial` keeps partially transferred files, so re-running the
  same job resumes rather than restarting if it is interrupted or runs out
  of time.
- The job can be run as a **push** (from the source project) or a **pull**
  (from the destination project, with the source path as the argument) —
  `clifton` must be authenticated in whichever project account starts the
  job. If one project has expired, run the job from the still-active
  project and pull.
- A transfer job consumes node hours like any other job (e.g. one GPU on
  Isambard-AI costs 0.25 node hours per wall-clock hour). Budget for this
  in the project's allocation — it will not run once node hours are
  exhausted, and the login node is never a "free" substitute.
- SSH certificates from `clifton` last 12 hours and are checked when the
  job **starts**, not when it is submitted. Run `clifton auth` shortly
  before submitting, allowing for expected queue time.

---

## Using the early-access data mover service

⚠️ Only walk a user through this section if they have confirmed access to
the early-access data mover service. Always describe it as early access.

### How it works

Data moves via a per-project S3 staging bucket, not directly between
facilities:

- To bring data **onto** a BriCS cluster: origin → S3 staging bucket →
  cluster-attached storage (`$PROJECTDIR`, `$HOME`).
- To take data **off** a cluster: cluster-attached storage → S3 staging
  bucket → destination.

Each project gets one bucket, capped at 20 TiB and 5,000,000 files. All
project members share full read/write/delete/update access. Data not
modified for 30 days is deleted automatically — the bucket is a staging
area, not persistent storage.

### Setup

1. **Install an S3 client** — `rclone` (>= v1.61.0) or AWS CLI.

   ```bash
   rclone config create datamover-s3 s3 provider=Other env_auth=true \
     endpoint=https://lb.staging.datamover.isambard.ac.uk \
     no_check_bucket=true acl=""
   ```

   The AWS CLI needs no further client-side configuration.

2. **Install Netham** — the tool that exchanges a federated-identity login
   for temporary S3 credentials, similar in spirit to `clifton` for SSH.
   Install it on *every* machine involved in a transfer (e.g. both the
   Isambard-AI Phase 2 login node and the user's laptop for an egress
   transfer):

   ```bash
   # via pip
   python3.11 -m venv --upgrade-deps netham-venv
   source netham-venv/bin/activate
   python -m pip install git+https://github.com/bristol-supercomputing/netham-early-access.git@0.1.0

   # via uv
   uv tool install git+https://github.com/bristol-supercomputing/netham-early-access.git@0.1.0
   ```

3. **Configure Netham** — create `netham.toml`:

   ```toml
   issuer_url = "https://keycloak.isambard.ac.uk/realms/isambard"
   client_id = "netham"
   role_arn = "arn:vast::default:role/PROJECTID.datamover"
   sts_endpoint_url = "https://lb.staging.datamover.isambard.ac.uk"
   assumed_role_duration_minutes = 1440
   ```

   `PROJECTID` is the project's ID/shortcode; all members use the same
   `role_arn`. Credentials last at most 24 hours (1440 minutes) — reduce
   `assumed_role_duration_minutes`, or pass
   `netham auth --assumed-role-duration`, for a shorter lifetime.

4. **Authenticate and load credentials:**

   ```bash
   netham --config $HOME/netham/netham.toml auth
   # open the printed URL, authenticate, and grant access when prompted
   source creds_env.sh
   ```

   `creds_env.sh` sets the standard `AWS_ACCESS_KEY_ID`,
   `AWS_SECRET_ACCESS_KEY`, `AWS_SESSION_TOKEN`, and `AWS_ENDPOINT_URL_S3`
   environment variables, which both `rclone` and AWS CLI read
   automatically. Re-run `netham auth` once credentials expire.

### Everyday operations

```bash
# List bucket contents
rclone lsl datamover-s3:PROJECTID.datamover
aws s3 ls s3://PROJECTID.datamover

# Upload
rclone copy --progress /path/to/file datamover-s3:PROJECTID.datamover
aws s3 cp /path/to/file s3://PROJECTID.datamover

# Download
rclone copy --progress datamover-s3:PROJECTID.datamover/file .
aws s3 cp s3://PROJECTID.datamover/file .

# Delete (dry run first!)
rclone delete --dry-run datamover-s3:PROJECTID.datamover/file
aws s3 rm --dryrun s3://PROJECTID.datamover/file
```

### Performance tuning

Default concurrency settings are conservative. Tune to the workload:

```bash
# rclone: few large files — raise per-file concurrency and chunk size
rclone copy --progress --transfers 4 --s3-upload-concurrency 16 \
  --s3-chunk-size 128M SOURCE datamover-s3:PROJECTID.datamover

# rclone: many small files — raise parallel transfers/checkers instead
rclone copy --progress --transfers 32 --checkers 16 \
  SOURCE/ datamover-s3:PROJECTID.datamover

# AWS CLI: persistent config, applies to all subsequent commands
aws configure set default.s3.max_concurrent_requests 20
aws configure set default.s3.multipart_chunksize 128MB
aws configure set default.s3.multipart_threshold 128MB
```

Treat these values as starting points — actual optimal settings depend on
file sizes, network conditions, and available memory. As with SSH transfers,
running data mover clients on a login node is still subject to per-session
resource limits.

### Feedback

The data mover team wants feedback during early access. Report issues or
suggestions via a service desk ticket titled with a **`DATAMOVER`** prefix.

---

## Troubleshooting

| Symptom | Likely cause | Fix |
|---------|-------------|-----|
| `scp`/`rsync` transfer killed partway through on a login node | Login node CPU/memory limit hit | Resubmit as a Slurm job (see above) |
| Slurm transfer job fails immediately at start | SSH certificate (from `clifton`) expired before the job started | Run `clifton auth` right before submitting; allow for queue time |
| `rclone` reports incompatibility or auth errors against the data mover endpoint | `rclone` version `< v1.61.0` | Upgrade `rclone`; check with `rclone version` |
| Data mover commands fail with expired/invalid credential errors | Netham credentials expired (max 24h lifetime) | Re-run `netham auth` and re-source `creds_env.sh` |
| Data mover upload fails with a quota/limit error | Project bucket at its 20 TiB or 5,000,000-file cap | Clean up old objects (dry run first) or contact support |
| File missing from the data mover bucket after 30+ days | Automatic 30-day expiry on unmodified objects | Expected behaviour — the bucket is a staging area, not storage |
| Project-to-project transfer fails after setting up `clifton` | `ProxyJump` directive still active in `~/.ssh/config_clifton` | Comment it out for the relevant `Host`, per the setup steps above |

---

## Further Reading

- [File Transfer guide](https://docs.isambard.ac.uk/user-documentation/guides/file_transfer/)
- [Data mover tutorial (early access)](https://docs.isambard.ac.uk/user-documentation/tutorials/data-mover/)
- [Login guide (SSH setup, clifton)](https://docs.isambard.ac.uk/user-documentation/guides/login/)
- [System storage (backup policy)](https://docs.isambard.ac.uk/user-documentation/information/system-storage/)
- [Job scheduling](https://docs.isambard.ac.uk/user-documentation/information/job-scheduling/)
- [Accounting guide](https://docs.isambard.ac.uk/user-documentation/guides/accounting/)
- [Isambard service desk](https://support.isambard.ac.uk/)
