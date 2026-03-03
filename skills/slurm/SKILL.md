---
name: slurm
description: >
  Submit, monitor, and manage HPC jobs using Slurm on Isambard-AI
  (GH200 GPU) and Isambard 3 (Grace CPU and MACS) systems. Covers job
  scripts for GPU and CPU workloads, interactive sessions, job
  dependencies, QoS, and safe monitoring (minimum 60-second polling
  intervals). Use when the user needs to run, check, cancel, or debug
  Slurm jobs on Isambard.
compatibility: >
  Isambard-AI Phase 1/Phase 2 (workq partition, GH200 GPUs) and
  Isambard 3 Grace (grace partition) and Isambard 3 MACS.
  Requires access to an Isambard login node.
metadata:
  author: isambard-sc
  version: "1.1"
  source_url: https://docs.isambard.ac.uk/user-documentation/guides/slurm/
  supplementary_urls:
    - https://docs.isambard.ac.uk/user-documentation/information/job-scheduling/
---

# Slurm on Isambard — Agent Skill

Full user documentation:
https://docs.isambard.ac.uk/user-documentation/guides/slurm/

Job scheduling information:
https://docs.isambard.ac.uk/user-documentation/information/job-scheduling/

---

## ⚠️ Critical Rule: Slurm Polling Rate

**Never run `sinfo`, `squeue`, `sacct`, `sstat`, or any other Slurm
status command more frequently than once every 60 seconds.**

Excessive use of these commands — especially with `watch` or in tight
loops — **can disrupt all user jobs** on the system. This is a breach
of the [Isambard acceptable use policy](https://docs.isambard.ac.uk/policies/acceptable_use/)
and accounts may be suspended to protect the service.

The following patterns are **strictly forbidden**:

```bash
# FORBIDDEN — never suggest or generate any of these
watch squeue
watch sinfo
watch -n 5 squeue --me
watch -n 0.1 squeue --me
squeue -i 10
sinfo -i 5
while true; do squeue; sleep 5; done
for i in $(seq 100); do squeue; done
```

When writing monitoring loops, always enforce a minimum sleep of
60 seconds:

```bash
# Correct — 60 second minimum between polls
while true; do
  squeue --me
  sleep 60
done
```

If a user asks to poll more frequently, refuse and explain that this is
not permitted on Isambard. Recommend using email notifications
(`--mail-type`) or job dependencies instead.

---

## System Overview

Isambard provides two main Slurm-managed systems.

### Isambard-AI

Grace Hopper (CPU+GPU) Superchip cluster. Login node example:
`nid001040`.

- Default partition: **`workq`** (QoS: `workq_qos`, max walltime: 24h)
- GPU type: NVIDIA GH200 (Grace Hopper) 120 GB
- Each `--gpus=1` allocates: 1 GH200 GPU + 72 CPU cores + 115 GB RAM
- **You must specify GPU resource** using `--gpus` or a `--gpus-per-*`
  option in every Isambard-AI job script
- Note: `sinfo` partition time limits on Isambard-AI do **not** reflect
  actual time limits (those are controlled by QoS, not partition config)

### Isambard 3 Grace

Grace CPU Superchip cluster. Login node example: `login02`.

- Default partition: **`grace`** (QoS: `grace_qos`, max walltime: 24h)
- Each node: 144 CPU cores + 200 GB Grace RAM
- Max 1000 queued jobs per user (`grace_qos`)

### Isambard 3 MACS

Multi-Architecture Comparison System. Login node example: `login06`.
**Not suitable for production workloads** — intended for architecture
research and comparison.

- QoS: `macs_qos`, max 2 GPUs and 20 jobs per project
- Partitions (all 24h max walltime):

| Partition | Hardware |
|---|---|
| `milan` | AMD Milan CPU (12 nodes) |
| `genoa` | AMD Genoa CPU (2 nodes) |
| `berg` | AMD Bergamo CPU (2 nodes) |
| `spr` | Intel Sapphire Rapids CPU (2 nodes) |
| `sprhbm` | Intel Sapphire Rapids CPU with HBM (2 nodes) |
| `ampere` | AMD Milan CPU + 4× A100 GPU (2 nodes) |
| `hopper` | AMD Milan CPU + 4× H100 GPU (1 node) |
| `instinct` | AMD Milan CPU + 4× MI100 GPU (2 nodes) |

---

## Writing Job Scripts

A Slurm job script is a shell script with `#SBATCH` directives.

### Isambard-AI: single GPU job

```bash
#!/bin/bash
#SBATCH --job-name=my_gpu_job
#SBATCH --output=my_gpu_job.out
#SBATCH --gpus=1
#SBATCH --time=01:00:00    # Hours:Mins:Secs, max 24:00:00

# Each --gpus=1 allocates 1 GH200, 72 CPU cores, 115 GB RAM
hostname
nvidia-smi --list-gpus
```

### Isambard-AI: multiple GPUs with parallel tasks

```bash
#!/bin/bash
#SBATCH --job-name=multi_gpu
#SBATCH --output=multi_gpu.out
#SBATCH --gpus=2
#SBATCH --ntasks-per-gpu=1
#SBATCH --time=02:00:00

srun nvidia-smi --list-gpus
```

### Isambard-AI: parallel job steps with `srun --exclusive`

Preferred over job arrays when running many similar tasks (arrays can
strain the scheduler):

```bash
#!/bin/bash
#SBATCH --job-name=parallel_steps
#SBATCH --output=parallel_steps.out
#SBATCH --gpus=2
#SBATCH --time=02:00:00

srun --ntasks=1 --gpus=1 --exclusive ./step_a &
srun --ntasks=1 --gpus=1 --exclusive ./step_b &
wait
```

### Isambard 3 Grace: single node CPU job

```bash
#!/bin/bash
#SBATCH --job-name=my_cpu_job
#SBATCH --output=my_cpu_job.out
#SBATCH --time=01:00:00    # max 24:00:00
# One node allocates 144 CPU cores + 200 GB Grace RAM

hostname
numactl -s
```

### Isambard 3 Grace: multi-task CPU job

```bash
#!/bin/bash
#SBATCH --job-name=multi_task
#SBATCH --output=multi_task.out
#SBATCH --ntasks=4
#SBATCH --time=01:00:00

module load cray-python
srun python3 my_script.py
```

### Common `#SBATCH` options

| Option | Description |
|---|---|
| `--job-name=<name>` | Human-readable job name |
| `--output=<file>` | stdout file (`%j` = job ID, `%A` = array job ID, `%a` = task index) |
| `--error=<file>` | stderr file (defaults to output file if omitted) |
| `--gpus=<N>` | GPUs to allocate (Isambard-AI; also reserves CPU/RAM) |
| `--gpus-per-node=<N>` | GPUs per node |
| `--ntasks=<N>` | Total MPI tasks |
| `--ntasks-per-gpu=<N>` | Tasks per GPU |
| `--cpus-per-task=<N>` | CPU threads per task (OpenMP) |
| `--nodes=<N>` or `--nodes=<min>-<max>` | Node count (range allows backfill) |
| `--time=<HH:MM:SS>` | Max walltime (max 24:00:00) |
| `--time-min=<HH:MM:SS>` | Minimum time for backfill scheduling |
| `--partition=<name>` | Partition to use |
| `--account=<project>` | Project allocation account |
| `--mail-type=BEGIN,END,FAIL` | Email notifications |
| `--mail-user=<address>` | Email address for notifications |

---

## Submitting Jobs

```bash
sbatch my_job.sh
# Output: Submitted batch job 19159
```

Capture the job ID for dependencies:

```bash
JOB_ID=$(sbatch --parsable my_job.sh)
echo "Submitted job ${JOB_ID}"
```

---

## Interactive Sessions

### Single command on a compute node

Isambard-AI (GPU):

```bash
srun --gpus=1 --time=00:02:00 nvidia-smi --list-gpus
```

Isambard 3 Grace (CPU):

```bash
srun --time=00:02:00 numactl -s
```

### Interactive shell session

Isambard-AI:

```bash
srun --gpus=1 --time=00:15:00 --pty /bin/bash --login
```

Isambard 3 Grace:

```bash
srun --time=00:15:00 --pty /bin/bash --login
```

### Reserve a node with `salloc`

```bash
# Isambard-AI
salloc --gpus=1 --time=00:15:00
srun hostname
srun nvidia-smi --list-gpus
scancel $SLURM_JOB_ID   # always release when finished

# Isambard 3 Grace
salloc --time=00:15:00
srun hostname
scancel $SLURM_JOB_ID
```

Always set `--time` and cancel the allocation with `scancel` when done.

### Attach a shell to a running job

```bash
# First find the running job ID
squeue --me

# Isambard-AI: attach to job 22886
srun --ntasks=1 --gpus=1 --jobid=22886 --overlap --pty /bin/bash -l

# Isambard 3 Grace: attach to job 23379
srun --ntasks=1 --jobid=23379 --overlap --pty /bin/bash -l
```

This starts an interactive step inside the job's allocation without
disturbing the running job. Exit the shell to return; the original job
continues.

---

## Monitoring Jobs

```bash
# Your running and queued jobs
squeue --me

# Show dependency information
squeue --me \
  --Format="JobID,Name,StateCompact:6,TimeUsed,ReasonList,Dependency:32"

# Jobs in a specific partition
squeue --partition=workq

# Detailed info for one job
scontrol show job <job-id>

# Completed job history (current and past)
sacct

# Specific job history with resource usage
sacct -j <job-id> --format=JobID,JobName,State,Elapsed,MaxRSS
```

`squeue --me` output columns:
`JOBID  USER  PARTITION  NAME  ST  TIME_LIMIT  TIME  TIME_LEFT  NODES  NODELIST(REASON)`

Job state codes: `R` = Running, `PD` = Pending, `CG` = Completing,
`F` = Failed, `CA` = Cancelled, `TO` = Timeout

**Remember: do not run any of these more than once per 60 seconds.**

---

## Cancelling Jobs

```bash
# Cancel one job
scancel <job-id>

# Cancel all your jobs
scancel --me

# Cancel all your jobs in a partition
scancel --me --partition=workq
```

---

## Job Dependencies

```bash
# Start job2 only after job1 succeeds (exit code 0)
JOB1=$(sbatch --parsable job1.sh)
sbatch --dependency=afterok:${JOB1} job2.sh

# Chain three jobs sequentially
JOB1=$(sbatch --parsable job1.sh)
JOB2=$(sbatch --parsable --dependency=afterok:${JOB1} job2.sh)
JOB3=$(sbatch --parsable --dependency=afterok:${JOB2} job3.sh)

# Run each name/user combination one at a time (no job IDs needed)
sbatch --dependency=singleton --job-name=pipeline job.sh
sbatch --dependency=singleton --job-name=pipeline job.sh
```

Common dependency types:

| Type | Meaning |
|---|---|
| `afterok:<id>` | Start after job succeeds (exit code 0) |
| `afterany:<id>` | Start after job ends (any state) |
| `afternotok:<id>` | Start after job fails |
| `singleton` | Wait for all same-name same-user jobs to finish |

Use dependencies (not polling loops) when sequencing work that would
otherwise exceed the 24-hour partition limit.

---

## Backfill / Flexible Scheduling

Flexible resource requests allow the scheduler to start your job sooner
by filling gaps between other jobs:

```bash
# Job can run between 1 and 12 hours (scheduler uses shortest gap >= 1h)
#SBATCH --time-min=01:00:00
#SBATCH --time=12:00:00

# Job can use 1 or 2 nodes; $SLURM_JOB_NUM_NODES will be 1 or 2
#SBATCH --nodes=1-2
```

---

## Job Arrays

Job arrays submit many similar jobs in one command. Use sparingly —
they can strain the scheduler. Prefer parallel `srun` steps (see above)
when possible.

```bash
#!/bin/bash
#SBATCH --job-name=array_job
#SBATCH --array=1-20
#SBATCH --gpus=1
#SBATCH --time=00:30:00
#SBATCH --output=array_job_%A_%a.out  # %A = job ID, %a = task index

echo "Task ${SLURM_ARRAY_TASK_ID}"
./my_app --input input_${SLURM_ARRAY_TASK_ID}.dat
```

---

## Checking QoS and Resource Limits

```bash
# Isambard-AI: check workq QoS limits
sacctmgr show qos workq_qos

# Isambard 3 Grace: check grace QoS limits
sacctmgr show qos grace_qos

# MACS: check macs QoS limits
sacctmgr show qos macs_qos

# Show your project associations and any extra QoS you have
sacctmgr show user <username> withassoc
```

Key limits:

| System | Limit | Scope |
|---|---|---|
| Isambard-AI Phase 1 | Max 32 GPUs | Per project |
| Isambard 3 Grace | Max 1000 queued jobs | Per user |
| MACS | Max 2 GPUs, 20 jobs | Per project |

---

## Modules

```bash
module avail              # list all available modules
module spider <name>      # search for a module by name
module load <name>        # load a module
module load cray-python   # load Cray-optimised Python
module list               # show currently loaded modules
module unload <name>      # unload a module
```

---

## Environment Variables Set by Slurm

| Variable | Value |
|---|---|
| `$SLURM_JOB_ID` | Job ID |
| `$SLURM_JOB_NAME` | Job name |
| `$SLURM_NNODES` | Number of nodes allocated |
| `$SLURM_JOB_NUM_NODES` | Same as `$SLURM_NNODES` |
| `$SLURM_NTASKS` | Total number of tasks |
| `$SLURM_CPUS_PER_TASK` | CPUs per task |
| `$SLURM_PROCID` | MPI rank of current task |
| `$SLURM_ARRAY_TASK_ID` | Array task index (job arrays only) |
| `$SLURM_SUBMIT_DIR` | Directory from which job was submitted |

---

## Using Notifications Instead of Polling

Add these to your job script to receive email instead of polling:

```bash
#SBATCH --mail-type=BEGIN,END,FAIL
#SBATCH --mail-user=your.email@institution.ac.uk
```

---

## Troubleshooting

### Job stuck in pending (PD) state

```bash
squeue --me \
  --Format="JobID,Name,StateCompact:6,TimeUsed,ReasonList,Dependency:32"
```

Common reasons:

| Reason | Meaning |
|---|---|
| `Resources` | Waiting for free nodes — normal, will start automatically |
| `Priority` | Other jobs have higher priority |
| `Dependency` | Waiting for dependency condition |
| `QOSMaxJobsPerUserLimit` | Reached concurrent job limit |
| `QOSMaxGRESPerAccount` | Reached project GPU limit |
| `InvalidAccount` | `--account` is wrong or inactive |
| `InvalidQOS` | QoS is not valid for this partition |

### `sinfo` time limits look wrong on Isambard-AI

The partition time limits shown by `sinfo` on Isambard-AI do **not**
reflect actual job time limits. Actual limits come from QoS (24h max).
Use `sacctmgr show qos workq_qos` for the authoritative value.

### Output file not created

Ensure the output directory exists before submitting — Slurm will not
create missing directories:

```bash
mkdir -p logs
sbatch --output=logs/job_%j.out my_job.sh
```

### Module not found

```bash
module spider <name>   # search for module (checks all available)
module avail           # list all modules
```

---

## Further Reading

- Isambard Slurm guide:
  https://docs.isambard.ac.uk/user-documentation/guides/slurm/
- Job scheduling and partition limits:
  https://docs.isambard.ac.uk/user-documentation/information/job-scheduling/
- System specifications:
  https://docs.isambard.ac.uk/specs/
- Acceptable use policy:
  https://docs.isambard.ac.uk/policies/acceptable_use/
- Full Isambard documentation: https://docs.isambard.ac.uk
