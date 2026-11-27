---
name: storage
description: >
  Guide for storage on BriCS Isambard facilities (Isambard-AI and Isambard 3,
  including MACS). Covers the storage areas ($HOME, $SCRATCHDIR/$SCRATCH,
  $PROJECTDIR, $PROJECTDIR_PUBLIC, $LOCALDIR), their paths, permissions,
  capacity and file-count (inode) quotas, checking usage with lfs quota or du,
  data retention and deletion (including the 60-day scratch purge on
  Isambard 3 and deletion at project end), the lack of backups, a full $HOME
  blocking SSH, sharing data within and between projects, packaging datasets
  of many small files with SquashFS (mksquashfs, squashfuse, Apptainer
  bind), and detecting the system with ISAMBARD_HOST. Use this skill whenever
  a user asks where to put data, how much space they have, why they've hit a
  quota or "Disk quota exceeded", whether data is backed up or will be
  deleted, how to share files, why many small files are slow, or which
  Isambard system their code is running on — even if they don't say
  "storage".
license: >
  CC-BY-SA-4.0. Markdown/image content derived from
  https://docs.isambard.ac.uk/, © 2024 University of Bristol.
compatibility: >
  Isambard-AI and Isambard 3 (Grace and MACS). Requires a shell on an
  Isambard login or compute node. The storage environment variables are set
  by the brics/userenv module, which is loaded by default.
metadata:
  author: isambard-sc
  version: "1.0"
  source_url: https://docs.isambard.ac.uk/user-documentation/information/system-storage/
  supplementary_urls:
    - https://docs.isambard.ac.uk/user-documentation/information/environment_variables/
    - https://docs.isambard.ac.uk/user-documentation/tutorials/datasets-in-squashfs/
    - https://docs.isambard.ac.uk/user-documentation/guides/modules/
    - https://docs.isambard.ac.uk/user-documentation/faqs/
---

# Storage on Isambard

Source docs:

- https://docs.isambard.ac.uk/user-documentation/information/system-storage/
- https://docs.isambard.ac.uk/user-documentation/tutorials/datasets-in-squashfs/
- https://docs.isambard.ac.uk/user-documentation/information/environment_variables/

## ⚠️ Critical Rules

- **Nothing is backed up.** All storage is working storage and lost data
  cannot be recovered. Remind users to keep copies of important data
  elsewhere throughout the project, not just at the end.
- **All project data is deleted after the project ends**, including
  `$HOME` and `$SCRATCHDIR`, after a 30-day grace period. Jobs can't be
  submitted once a project has expired, so copy data off before the end
  date (see the `data-transfer` skill).
- **On Isambard 3, files in `$SCRATCHDIR` not accessed for 60 days are
  deleted.** Move data to keep into `$PROJECTDIR` or off the system.
- **Never fill `$HOME`.** A full `$HOME` or exceeded quota can block SSH
  login. Put large files in `$PROJECTDIR` or `$SCRATCHDIR`.
- **`$PROJECTDIR_PUBLIC` is readable by every user on the system**, from
  every project. Never put sensitive, personal or restrictively licensed data
  or software there, even briefly.
- **Use environment variables, not hard-coded paths**, e.g. `$SCRATCHDIR`
  rather than `/scratch/<PROJECT>/<USER>.<PROJECT>`.
- **Quota increases go to the allocator, not BriCS.** BriCS can't grant
  larger quotas (see the `projects-and-accounting` skill).

## Storage areas

| Area | Shared across nodes? | Use for | Retained until |
|---|---|---|---|
| `$HOME` | Yes | Config files, scripts, job output; not large data | Project end |
| `$SCRATCHDIR` (alias `$SCRATCH`) | Yes | Your working data for running jobs: checkpoints, intermediate files, container images | Isambard 3: 60 days since last access. Isambard-AI: project end |
| `$PROJECTDIR` | Yes | Data shared within the project: datasets, shared Conda environments, shared container images | Project end |
| `$PROJECTDIR_PUBLIC` | Yes | Sharing files read-only with other projects | Project end |
| `$LOCALDIR` | No, local to one node | Fast temporary space where the shared filesystem is unsuitable (e.g. building rootless containers) | End of job (compute) or session (login) |

- On compute nodes `$LOCALDIR` is usually a tmpfs RAM disk: very fast, but
  its capacity comes out of the node's memory. On login nodes it is on local
  SSD.
- The shared filesystems are Lustre or VAST (NFS) depending on the system.
- Isambard-AI Phase 1 and Phase 2 are separate machines with separate
  storage; files on one are not visible on the other.

## Paths and permissions

| Variable | Path | Owner, group | Mode |
|---|---|---|---|
| `$HOME` | `/home/<PROJECT>/<USER>.<PROJECT>` | user, project | `0750` |
| `$SCRATCHDIR`, `$SCRATCH` | `/scratch/<PROJECT>/<USER>.<PROJECT>` | user, user | `0750` |
| `$PROJECTDIR` | `/projects/<PROJECT>` | root, project | `2770` |
| `$PROJECTDIR_PUBLIC` | `/projects/public/<PROJECT>` | root, project | `2775` |
| `$LOCALDIR` | `/local/user/<UID>` (`echo $UID`) | user, user | `0750` (`0700` on Isambard-AI compute nodes) |

Accounts and storage are per project: a user in two projects has two
separate `$HOME` directories.

## Quotas

### Capacity

| Area | Isambard-AI | Isambard 3 |
|---|---|---|
| `$HOME` | 100 GiB (on NFS on Phase 2) | 100 GiB |
| `$PROJECTDIR` | 200 TiB | 20 TiB |
| `$SCRATCHDIR` | 5 TiB | 5 TiB |
| `$LOCALDIR`, compute node | 48 GiB | 512 GiB |
| `$LOCALDIR`, login node | 512 GiB | 512 GiB |

### File count (inodes)

On Isambard-AI: `$SCRATCHDIR` 1,000,000 files, `$PROJECTDIR` 50,000,000
files. A dataset of many small files can hit the file limit long before the
space limit; package it with SquashFS (below).

### Checking usage

Lustre areas (substitute the directory):

```bash
lfs quota -hp $(lfs project -d $SCRATCHDIR | awk '{print $1}') $SCRATCHDIR
lfs quota -hp $(lfs project -d $PROJECTDIR | awk '{print $1}') $PROJECTDIR
```

`$HOME` on Isambard-AI Phase 2 is on NFS, which can't report quota usage.
Compare this against the 100 GiB limit instead:

```bash
du -xsh $HOME
```

## Sharing data

- **Within a project:** use `$PROJECTDIR`. If a member's files have
  permissions that are too restrictive, ask the owner to `chmod` them. If
  the owner can't (e.g. has left), the Project Lead asks BriCS support to fix
  the permissions or ownership.
- **With other projects:** put files in `$PROJECTDIR_PUBLIC` and make them
  readable (`chmod o+r <file>`, `chmod o+rx <directory>`, or
  `chmod --recursive o+rX <directory>`). Everyone on the system can then
  read them. The Project Lead is legally responsible for any privacy or
  licensing breach.
- **Copying between projects:** see the `data-transfer` skill.

## Many small files: SquashFS

Parallel filesystems handle large sequential I/O well but many small files
badly: each file access is a metadata request, and file counts count
against the inode quota. SquashFS packs a directory tree into one compressed,
read-only image file that is mounted and read like a directory. This
suits datasets written once and read many times, such as ML datasets of
millions of images or text files.

### Create the image

Best for new data: create it on the user's own machine before uploading, so
the individual files never touch the parallel filesystem. Install
`squashfs-tools` (`brew install squashfs` on macOS,
`sudo apt install squashfs-tools` on Ubuntu/WSL), then:

```bash
mksquashfs /path/to/dataset mydata.squashfs -no-compression -no-xattrs
```

For data already on Isambard, create it on a compute node with
`mksquashfs.static`, as it can be resource intensive. On Isambard-AI:

```bash
srun --nodes 1 --gpus 1 --time 00:15:00 --pty /bin/bash --login
mksquashfs.static $SOURCE_DIR $PROJECTDIR/mydata.squashfs -no-compression -no-xattrs -processors 72
```

On Isambard 3, use `--nodes 1` without `--gpus`. `-no-compression` keeps
decompression from costing CPU time when the data is read.

### Use the image

Mount it with `squashfuse` in the job, read from the mount point, and
unmount at the end:

```bash
mkdir -p $SCRATCH/mydata
squashfuse $PROJECTDIR/mydata.squashfs $SCRATCH/mydata
python train.py --data-dir $SCRATCH/mydata
fusermount -u $SCRATCH/mydata
```

In an Apptainer container, bind the image directly:

```bash
apptainer shell --bind $PROJECTDIR/mydata.squashfs:/data:image-src=/ image.sif
```

Keep datasets separate from container images.

## Detecting the system

The `brics/userenv` module (loaded by default) sets `$LOCALDIR`,
`$SCRATCHDIR`, `$TMPDIR` and `ISAMBARD_HOST`:

| System | `ISAMBARD_HOST` |
|---|---|
| Isambard-AI Phase 1 | `I-AI_P1` |
| Isambard-AI Phase 2 | `I-AI_P2` |
| Isambard 3 (Grace) | `I3` |
| Isambard 3 MACS | `I3MACS` |

```python
import os

host = os.getenv("ISAMBARD_HOST", "Unknown System")
```

### Isambard 3 Grace and MACS share a filesystem

Grace is `aarch64` and MACS is `x86_64`, but they share the same Lustre
storage, including `$HOME`. Guard architecture-specific setup in files used
on both, such as `.bashrc` (e.g. Conda initialisation):

```bash
if [ "$(arch)" == "x86_64" ]; then
    : # MACS setup
elif [ "$(arch)" == "aarch64" ]; then
    : # Grace setup
fi
```

Avoid `pip install --user` (it installs to `$HOME/.local`, shared by both
architectures); use virtual environments instead.

## Troubleshooting

| Symptom | Cause and fix |
|---|---|
| "Disk quota exceeded" or writes fail with space left | Space or inode quota reached. Check with `lfs quota` (or `du -xsh $HOME` on Isambard-AI Phase 2). For many small files, package them with SquashFS. |
| Can't log in over SSH | `$HOME` may be full. The user contacts the BriCS helpdesk (https://support.isambard.ac.uk) with a list of files to delete or move. |
| Files gone from `$SCRATCHDIR` on Isambard 3 | Deleted after 60 days without access. They can't be recovered. |
| Slow I/O over many small files | Metadata load on the parallel filesystem. Use SquashFS. |
| Can't read a project member's files | Owner fixes permissions with `chmod`; if they've left, the Project Lead asks support. |
| `$LOCALDIR` or `$TMPDIR` missing in a JupyterHub session | Check https://docs.isambard.ac.uk/service-status/known_issues/ for current advice. |
| Software breaks on MACS but works on Grace (or vice versa) | Shared `$HOME`: guard `.bashrc` by architecture and use virtual environments, not `pip install --user`. |
| Need more space | The allocator decides quotas, not BriCS. |

## Further Reading

- Storage spaces: https://docs.isambard.ac.uk/user-documentation/information/system-storage/
- Packaging datasets with SquashFS: https://docs.isambard.ac.uk/user-documentation/tutorials/datasets-in-squashfs/
- Environment variables: https://docs.isambard.ac.uk/user-documentation/information/environment_variables/
- File transfer: https://docs.isambard.ac.uk/user-documentation/guides/file_transfer/
- Data Privacy Policy (data retention): https://docs.isambard.ac.uk/policies/data_privacy/
