---
name: brics-hpc-ai-code
description: >
  Guidance for writing, reviewing, and running AI-generated code responsibly on
  Bristol Centre for Supercomputing (BriCS) shared HPC resources: Isambard-AI
  and Isambard 3. Use this skill whenever generating, adapting, or debugging
  code intended to run on BriCS facilities, writing Slurm job scripts, managing
  storage, installing software, or ensuring compliance with BriCS policies.
license: Proprietary. See https://docs.isambard.ac.uk/policies/ for terms.
compatibility: >
  Designed for use with BriCS facilities (Isambard-AI Phase 1/2, Isambard 3
  Grace/MACS). Assumes Linux aarch64 (Arm64) on Isambard-AI and Isambard 3
  Grace; x86_64 on Isambard 3 MACS. Requires Slurm, SSH/Clifton access.
metadata:
  author: Bristol Centre for Supercomputing (BriCS)
  docs: https://docs.isambard.ac.uk/
  support: https://support.isambard.ac.uk
  status: https://status.isambard.ac.uk
---

# BriCS HPC Responsible AI-Generated Code Skill

This skill guides agents in producing correct, safe, and policy-compliant code
for the Bristol Centre for Supercomputing (BriCS) HPC facilities.

---

## Core Principles

Always follow these rules when generating or suggesting code for BriCS systems.

| Principle | Rule |
|---|---|
| **Shared resource respect** | Never generate code that runs heavy workloads directly on login nodes |
| **Accurate resource requests** | Always estimate realistic `--time`, `--gpus`, `--ntasks` in job scripts |
| **Storage awareness** | Use the correct storage area; never assume data persists after project end |
| **Policy compliance** | All generated code must be consistent with the BriCS Acceptable Use Policy |
| **Architecture awareness** | Isambard-AI and Isambard 3 Grace are **aarch64 (Arm64)**; MACS has mixed archs |
| **Verify before submit** | Always review AI-generated scripts before `sbatch`—especially resource flags |

---

## Quick Decision Table

| Task | Correct approach |
|---|---|
| Run a short test command | `srun --time=00:05:00 [--gpus=1] <cmd>` |
| Run a batch workload | Write a script; submit with `sbatch` |
| Install Python packages | Conda (Miniforge) or `uv`; never `pip install --user` in $HOME |
| Share data with project members | Write to `$PROJECTDIR` |
| Share data with all users | Write to `$PROJECTDIR_PUBLIC` |
| Temporary/intermediate data | Use `$SCRATCHDIR` (auto-deleted after 60 days on Isambard 3) |
| Fast in-job scratch | Use `$LOCALDIR` (wiped at job end) |
| Long job (>24h) | Break into chained jobs with `--dependency=afterok:<JOBID>` |
| Check quota | `lfs quota -hp $(lfs project -d $SCRATCHDIR \| awk '{print $1}') $SCRATCHDIR` |

---

## Slurm Job Scripts

### Isambard-AI (GPU — GH200)

Each GPU requested allocates **1 Grace Hopper Superchip** = 1 GH200 GPU + 72 CPU cores + 115 GiB RAM.

```bash
#!/bin/bash
#SBATCH --job-name=my_job
#SBATCH --output=my_job_%j.out
#SBATCH --gpus=1                # Required: always specify GPU resource
#SBATCH --time=01:00:00         # Required: set a realistic time limit (max 24h)

module load cray-python         # Or activate your Conda/venv environment
python3 my_script.py
```

**Gotchas for Isambard-AI:**
- You MUST specify `--gpus` (or `--gpus-per-*`). Jobs without GPU directives will fail.
- The default partition is `workq`. Do not specify a partition unless you have a reason.
- Maximum walltime is **24 hours**. For longer jobs, use `--dependency=afterok:<JOBID>`.
- Project GPU limit: **32 GPUs** across all running jobs (`32gpu_qos`).

### Isambard 3 (CPU — Grace)

```bash
#!/bin/bash
#SBATCH --job-name=my_cpu_job
#SBATCH --output=my_cpu_job_%j.out
#SBATCH --ntasks=4
#SBATCH --time=02:00:00         # Max 24h on grace partition

module load cray-python
srun python3 my_script.py
```

### Multi-step / parallel job steps

```bash
# Run two job steps concurrently on separate GPUs
srun --ntasks=1 --gpus=1 --exclusive step_a.sh &
srun --ntasks=1 --gpus=1 --exclusive step_b.sh &
wait
```

### Chaining long workloads (>24h)

```bash
# Chain jobs that save/restore state
JOBID_1=$(sbatch --parsable job_part1.sh)
JOBID_2=$(sbatch --parsable --dependency=afterok:${JOBID_1} job_part2.sh)
```

---

## Storage Spaces

All storage is **working storage — not backed up**. Data is deleted at project end.

| Variable | Path | Purpose | Quota (Isambard-AI) | Retention |
|---|---|---|---|---|
| `$HOME` | `/home/<PROJECT>/<USER>.<PROJECT>` | Config files, scripts, job outputs | 100 GiB | Project end |
| `$SCRATCHDIR` | `/scratch/<PROJECT>/<USER>.<PROJECT>` | Intermediate job data, containers | 5 TiB | 60 days (i3) / Project end (iAI) |
| `$PROJECTDIR` | `/projects/<PROJECT>` | Shared datasets, shared environments | 200 TiB | Project end |
| `$PROJECTDIR_PUBLIC` | `/projects/public/<PROJECT>` | Data readable by all users | 200 TiB | Project end |
| `$LOCALDIR` | `/local/user/<UID>` | Fast RAM-backed in-job scratch | 48 GiB (compute) | End of job/session |

**Critical reminders:**
- **Never use `/tmp` directly.** `/tmp` is node-local, may have very limited space, and is not reliably available or cleaned up across the cluster. Always reference storage locations through their environment variables (`$SCRATCHDIR`, `$LOCALDIR`, etc.) and use `set -eu` at the top of job scripts to catch unset variables early:

```bash
#!/bin/bash
set -eu   # Exit on error (-e); treat unset variables as errors (-u)

WORKDIR="${SCRATCHDIR}/myjob_${SLURM_JOB_ID}"
mkdir -p "${WORKDIR}"

# ... your work here ...

# Explicitly clean up at end of job — do not rely on automated deletion
rm -rf "${WORKDIR}"
```

- `$HOME` is for scripts and configs — **not large datasets**.
- `$LOCALDIR` on compute nodes is a **tmpfs RAM disk** — very fast but limited.
- Never assume `$LOCALDIR` data survives between jobs.
- Backup important results off-system before the project end date.

---

## Login Nodes — What NOT to Do

Login nodes are **shared** and must not be used for compute-intensive or long-running work.

| Allowed on login node | NOT allowed on login node |
|---|---|
| Editing files | Running model training |
| Compiling small programs | Running data preprocessing pipelines |
| Submitting/monitoring jobs | Running benchmarks or tests |
| File transfer and compression | Long `python` / `bash` loops |
| Building containers | Using `watch` with `squeue -i` repeatedly |

> Using `squeue -i` or `watch squeue` excessively disrupts **all users** and is a breach of the Acceptable Use Policy. Use `squeue --me` once to check, or set a reasonable interval.

---

## Software and Environments

### Python — Recommended approach

```bash
# Install Miniforge (once per user)
cd $HOME
curl --location --remote-name \
  "https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-$(uname)-$(uname -m).sh"
bash Miniforge3-$(uname)-$(uname -m).sh
rm Miniforge3-$(uname)-$(uname -m).sh

# Activate (each session — do NOT use conda init)
source ~/miniforge3/bin/activate

# Create and use isolated environments
conda create -n myenv python=3.11
conda activate myenv
conda install 
```

**Gotchas:**
- Do NOT run `conda init` — it modifies shell startup scripts and causes problems.
- Do NOT install packages in the base Conda environment.
- Do NOT use `pip install --user`; it installs into `$HOME/.local` which is shared across architectures (aarch64 and x86_64 on Isambard 3) — use venvs instead.
- Isambard-AI and Isambard 3 Grace are **aarch64**. Many PyPI wheels do not support aarch64; use conda-forge or build from source.

### Architecture check in scripts

```bash
# In .bashrc or setup scripts, guard architecture-specific code:
if [ "$(arch)" == "x86_64" ]; then
    source ~/miniforge3/bin/activate  # x86_64 env
elif [ "$(arch)" == "aarch64" ]; then
    source ~/miniforge3_arm/bin/activate  # aarch64 env
fi
```

### Modules

```bash
module avail          # List available modules
module load cray-python   # Load Cray Python (pre-installed)
```

---

## Connecting to BriCS (Clifton + SSH)

```bash
# Install Clifton (Linux)
curl -L https://github.com/isambard-sc/clifton/releases/latest/download/clifton-linux-musl-x86_64 -o clifton
chmod u+x clifton && mv clifton ~/.local/bin/

# Authenticate (required daily)
clifton auth

# Write SSH config (only needed when added to a new project)
clifton ssh-config write

# Connect
ssh .aip2.isambard    # Isambard-AI Phase 2
ssh .3.isambard       # Isambard 3
```

**Gotchas:**
- SSH certificates are valid for **12 hours only** — run `clifton auth` each day.
- Login nodes are assigned randomly; you cannot request a specific login node.
- Do NOT leave persistent `tmux`/`screen` sessions on login nodes — they violate security policy and may be terminated without warning.

---

## Managing Jobs

```bash
squeue --me                        # View your running/pending jobs
sacct                              # View current and completed jobs
scancel                     # Cancel a job
salloc --gpus=1 --time=00:30:00    # Reserve a node interactively (always set --time)
```

**Gotchas:**
- Always cancel `salloc` allocations with `scancel <JOBID>` when finished.
- Use `--time-min` and `--time` together to allow backfill scheduling.
- Batch array jobs (`--array`) can strain the scheduler — prefer chained job steps where possible.

---

## Responsible AI-Generated Code Checklist

Before submitting any AI-generated code or job script to BriCS:

- [ ] **Resource requests are realistic** — `--time`, `--gpus`, `--ntasks` match your actual workload
- [ ] **No heavy computation on the login node** — all intensive work is inside a job script
- [ ] **Correct storage variable used** — large inputs/outputs go to `$SCRATCHDIR` or `$PROJECTDIR`, not `$HOME`
- [ ] **Architecture is correct** — code compiles/runs on aarch64 if targeting Isambard-AI or Isambard 3 Grace
- [ ] **Python packages are in a virtual environment** — not installed globally or with `--user`
- [ ] **No persistent sessions** — `tmux`/`screen` used only within a job, not left on login nodes
- [ ] **Quota checked** — storage usage is within limits before staging large datasets
- [ ] **Data backed up** — important results are copied off-system; nothing is assumed to persist
- [ ] **Policy compliance** — usage is consistent with the BriCS Acceptable Use Policy
- [ ] **Job output reviewed** — check `sacct` or output files after a job completes

---

## Common Gotchas Summary

| Mistake | Consequence | Fix |
|---|---|---|
| No `--gpus` on Isambard-AI | Job fails | Always include `--gpus=1` (or more) |
| Running compute on login node | Account suspension | Use `sbatch`/`srun` |
| `pip install --user` across archs | Package conflicts | Use Conda env or venv |
| `conda init` in `.bashrc` | Shell startup failures | Use `source ~/miniforge3/bin/activate` |
| Leaving data in `$SCRATCHDIR` for >60 days (Isambard 3) | Data deleted | Move to `$PROJECTDIR` or back up |
| Persistent `tmux` on login node | Session terminated | Submit long jobs via Slurm |
| Using `watch` with any Slurm command | Disrupts scheduler for all users; AUP violation | Never combine `watch` with `squeue`, `sinfo`, `sacct`, or similar — check once manually |
| Using `/tmp` directly in scripts | `/tmp` is node-local, not guaranteed to exist, and not cleaned up reliably | Use `$SCRATCHDIR`, `$LOCALDIR`, or a subdirectory of a known env variable |
| Leaving temp files in `$SCRATCHDIR` or `$LOCALDIR` after a job | Wastes quota; may cause future jobs to fail on space | Explicitly delete temp files at the end of your job script |
| Raising a support ticket for a known outage | Unnecessary load on the helpdesk | Always check https://status.isambard.ac.uk before submitting a ticket |
| Forgetting `clifton auth` | SSH fails | Run daily before connecting |

---

## Further Reading

- Full documentation: https://docs.isambard.ac.uk/
- Slurm job management: https://docs.isambard.ac.uk/user-documentation/guides/slurm/
- Storage spaces: https://docs.isambard.ac.uk/user-documentation/information/system-storage/
- Job scheduling & limits: https://docs.isambard.ac.uk/user-documentation/information/job-scheduling/
- Python guide: https://docs.isambard.ac.uk/user-documentation/guides/python/
- Login guide: https://docs.isambard.ac.uk/user-documentation/guides/login/
- Policies: https://docs.isambard.ac.uk/policies/
- Support: https://support.isambard.ac.uk
- Service status: https://status.isambard.ac.uk