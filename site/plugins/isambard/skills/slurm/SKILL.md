---
name: slurm
description: >
  Guide for submitting, monitoring, and managing HPC jobs using the Slurm workload manager
  on Isambard-AI (GH200 GPU nodes) and Isambard 3 (Grace CPU and MACS nodes).
  Use this skill whenever a user asks about Slurm on Isambard, writing sbatch scripts,
  requesting GPUs or CPU resources, srun or salloc, job arrays, job dependencies,
  multi-node jobs, hybrid MPI/OpenMP jobs, partitions, QOS limits, the Isambard-AI
  Phase 2 interactive reservation, scheduler flexibility (--time-min, --nodes range),
  --exclusive, sacct, polling intervals, job accounting, or why a job is stuck in
  PENDING, failing, or hitting resource limits.
  Also trigger for questions about acceptable use of the Slurm queue, what PENDING reasons
  mean, how to chain jobs, or how to debug a running job — even if the user doesn't
  explicitly say "Slurm".
license: CC-BY-SA-4.0. Markdown/image content derived from https://docs.isambard.ac.uk/, © Bristol Centre for Supercomputing (BriCS).
compatibility: >
  Isambard-AI and Isambard 3. Requires access to an Isambard login node, Slurm
  commands, and the scheduler environment.
metadata:
  author: isambard-sc
  version: "1.1"
  source_url: https://docs.isambard.ac.uk/user-documentation/guides/slurm/
  supplementary_urls:
    - https://docs.isambard.ac.uk/user-documentation/guides/slurm-advanced/
    - https://docs.isambard.ac.uk/user-documentation/guides/slurm-troubleshooting/
    - https://docs.isambard.ac.uk/user-documentation/guides/slurm-examples/
    - https://docs.isambard.ac.uk/user-documentation/information/job-scheduling/
  docs_commit: e994565
---

# Slurm on Isambard

Both Isambard-AI and Isambard 3 use the [Slurm Workload Manager](https://slurm.schedmd.com/)
to schedule jobs on compute nodes. Jobs are submitted to a queue and run when the requested
resources become available.

> **Never poll the queue rapidly.** Running `squeue` or `sinfo` in a tight loop (`watch`
> with a short interval, or `--iterate`) floods the scheduler and slows job scheduling for
> every user. Minimum polling interval from scripts: **60 seconds**. Disruptive polling
> is a breach of the acceptable use policy and may result in account suspension.

## Critical Rules

- Never poll `squeue`, `sinfo`, or any scheduler status command in a tight loop.
- Always submit jobs with `sbatch` or launch commands with `srun`; do not use `mpirun`
  or `mpiexec` on Isambard.
- Always set explicit `--time`, `--nodes`, and `--gpus` when applicable.
- Use `--exclusive` only when the workload truly requires an entire node.
- Do not request GPUs on Isambard 3 Grace. On Isambard 3 MACS, GPUs exist only on the
  `ampere`, `hopper` and `instinct` partitions.
- Request the Isambard-AI Phase 2 `interactive` reservation with
  `--reservation=interactive` only. Never add `--partition` to the same command —
  doing so is Unacceptable Use under the AUP and the job may be cancelled without
  warning.

---

## System Differences

| System | GPU resource flag | Cores per node | Notes |
|--------|------------------|---------------|-------|
| Isambard-AI | `--gpus=<n>` | 72 per GH200 Superchip (4 per node) | 1 GPU = 1 full GH200 Superchip (72 cores + memory) |
| Isambard 3 Grace | — | 144 (2 × 72-core Superchips) | CPU-only; shared between users by default |
| Isambard 3 MACS | GPU partitions only | Varies | x86_64 nodes; not for production workloads |

### Partitions and limits

| System | Partitions (default first) | QoS | Key limits |
|--------|---------------------------|-----|------------|
| Isambard-AI Phase 1 | `workq` | `workq_qos`, `32gpu_qos` | Max 32 GPUs per project |
| Isambard-AI Phase 2 | `workq`; hidden `interactive` (via reservation) | `workq_qos`, `interactive_qos` | Per user: 256 running jobs, 512 pending + running jobs; max array size 1000 |
| Isambard 3 Grace | `grace` | `grace_qos` | Per user: 1000 pending + running jobs (limits under review) |
| Isambard 3 MACS | `milan`, `genoa`, `berg`, `spr`, `sprhbm`, `ampere` (4×A100), `hopper` (4×H100), `instinct` (4×MI100) | `macs_qos` | Per project: max 2 GPUs, 20 pending + running jobs |

Max walltime is **24 hours** on all general-purpose partitions; the `interactive`
reservation allows up to **8 hours**. On Isambard-AI Phase 2, a submission that
would exceed a per-user limit is rejected immediately — resubmit once the job count
drops. Limits may be tightened temporarily; check the
[service status page](https://docs.isambard.ac.uk/service-status/). See the
[job scheduling page](https://docs.isambard.ac.uk/user-documentation/information/job-scheduling/)
for current values.

---

## Monitoring

```bash
squeue --me                    # your jobs only
squeue --me --Format="JobID,Name,StateCompact:6,TimeUsed,ReasonList,Dependency:32"
sinfo                          # partition and node state (general impression only)
sacct                          # current and recently completed jobs with exit codes
```

On some BriCS services other users' jobs are not visible in `squeue`.

Common job states: `R` = running, `PD` = pending, `CG` = completing, `F` = failed, `TO` = timed out.

---

## Submitting Jobs

### Two common mistakes

- **Resources spread across nodes:** Always include `--nodes=1` for single-node jobs. Without it, Slurm may draw GPUs or tasks from multiple nodes.
- **Accidental node reservation:** `--exclusive` as an `#SBATCH` directive reserves an entire node regardless of actual usage. You are charged for the whole node. Use only when your workload genuinely requires it.

### Batch jobs (`sbatch`)

```bash
sbatch my_job.sh
cat my_job.out    # output appears here once job completes
```

**Isambard-AI — single GPU job:**
```bash
#!/bin/bash
#SBATCH --job-name=my_job
#SBATCH --output=my_job.out
#SBATCH --nodes=1
#SBATCH --gpus=1
#SBATCH --time=00:05:00

hostname
nvidia-smi --list-gpus
```

**Isambard 3 Grace — single node job:**
```bash
#!/bin/bash
#SBATCH --job-name=my_job
#SBATCH --output=my_job.out
#SBATCH --nodes=1
#SBATCH --time=00:05:00

hostname
numactl -s
```

Always set `--time` — shorter walltimes usually mean shorter queue waits.

### Interactive jobs (`srun`)

```bash
# Run a single command on a compute node
srun --nodes=1 --gpus=1 --time=00:02:00 nvidia-smi --list-gpus

# Start an interactive shell (job ends when you close the terminal)
srun --nodes=1 --gpus=1 --time=00:15:00 --pty /bin/bash --login
```

### `interactive` reservation (Isambard-AI Phase 2)

Use for short-lived debugging, development or exploratory work that needs a compute
node without waiting in the normal queue:

```bash
srun --gpus=1 --reservation=interactive --pty bash -i
squeue --me --partition=interactive   # reservation jobs are hidden from plain squeue --me
```

- Default walltime 30 minutes; max 8 hours; max 4 nodes (16 GPUs) per job.
- Max 1 running and 1 queued job per user.
- Billed at a 50% premium: 1 node-hour is charged as 1.5 NHR.
- Never add `--partition`. Never use it for long-running or high-throughput work.

See `references/advanced.md` for details.

### Running multiple tasks in parallel

```bash
# Inside a batch script: 4 tasks, one per GPU
#SBATCH --gpus=4
#SBATCH --ntasks-per-gpu=1
srun python3 myscript.py

# Concurrent independent job steps
srun --ntasks=1 --gpus=1 --exclusive step_a &
srun --ntasks=1 --gpus=1 --exclusive step_b &
wait
```

`--exclusive` on `srun` (not `#SBATCH`) prevents steps from over-subscribing the allocation
and allows them to run concurrently. This is the *safe* use of `--exclusive`.

---

## Managing Jobs

### Job arrays

```bash
#SBATCH --array=1-4                # tasks 1, 2, 3, 4
#SBATCH --output=my_array_%a.out   # %a = task ID
#SBATCH --array=1-100%4            # limit to 4 concurrent tasks
#SBATCH --array=0-90:10            # step: 0, 10, 20 ... 90

# Inside script, task ID is:
echo $SLURM_ARRAY_TASK_ID
```

Array tasks appear as `JOBID_TASKID` in `squeue`. Cancel one task: `scancel JOBID_TASKID`.
Cancel the whole array: `scancel JOBID`.

> For many short tasks, prefer concurrent `srun` steps in one batch job over a large array
> — reduces scheduler overhead and avoids exhausting credit reservations.

### Job dependencies

```bash
# Run job2 only after job1 succeeds (exit code 0)
JOBID_1=$(sbatch --parsable job1.sh)
JOBID_2=$(sbatch --parsable --dependency=afterok:${JOBID_1} job2.sh)

# Only one job with this name runs at a time
sbatch --dependency=singleton my_job.sh
sbatch --dependency=singleton my_job.sh   # waits for the first to finish
```

View dependencies: `squeue --me --Format="JobID,Name,StateCompact:6,ReasonList,Dependency:32"`

Other types: `afterany` (regardless of exit code), `afternotok` (only if failed). See the [sbatch man page](https://slurm.schedmd.com/sbatch.html).

### Cancelling jobs

```bash
scancel <JOBID>         # cancel a job or array task
scancel <JOBID_TASKID>  # cancel one array task
scancel --me            # cancel all your jobs
```

---

## Advanced Topics

See **`references/advanced.md`** for full detail on:
- `sacct` for job history and exit codes
- Attaching an interactive shell to a running job (`srun --jobid --overlap`)
- Multi-node jobs (`--nodes`, `--gpus-per-node`, `--ntasks-per-node`)
- Hybrid MPI/OpenMP jobs (`--ntasks-per-node`, `--cpus-per-task`, `OMP_NUM_THREADS`)
- Interactive allocations (`salloc`) and the Phase 2 `interactive` reservation
- Scheduler flexibility (`--time-min`, `--nodes` range)
- `--exclusive` at the job level — when it's needed and what it costs
- QOS limits, `sacctmgr`, and allocation limit errors
- Job requeues, restarts, and `SLURM_RESTART_COUNT`
- Large jobs (256+ nodes) and scheduling etiquette

Read this file when helping with any of these topics.

---

## Troubleshooting

See **`references/troubleshooting.md`** for a full symptom → cause → fix reference covering:
- Job submission errors (`QOS policy`, `Invalid GRES`, `node configuration not available`, `invalid account`)
- PENDING reasons (`Priority`, `None`, `Dependency`, `PartitionTimeLimit`, `ReqNodeNotAvail`, `AssocGrpGRESMinutesLimit`, `JobHoldMaxRequeue`)
- Job failures (`TIMEOUT`, `OUT_OF_MEMORY`, `NODE_FAIL`, `FAILED` with non-zero exit code)
- Job shows `COMPLETED` but results are missing or wrong

Read this file when a user is asking why their job won't start, is failing, or is behaving unexpectedly.

---

## Quick Reference

| Goal | Command |
|------|---------|
| View your jobs | `squeue --me` |
| Check job history + exit codes | `sacct` |
| Submit batch job | `sbatch my_job.sh` |
| Interactive command | `srun --nodes=1 --gpus=1 --time=00:05:00 <cmd>` |
| Interactive shell | `srun --nodes=1 --gpus=1 --time=00:15:00 --pty /bin/bash --login` |
| Reserve allocation | `salloc --nodes=1 --gpus=1 --time=00:10:00` |
| Interactive shell (Phase 2 reservation) | `srun --gpus=1 --reservation=interactive --pty bash -i` |
| List reservation jobs | `squeue --me --partition=interactive` |
| Cancel job | `scancel <JOBID>` |
| Cancel all my jobs | `scancel --me` |
| Chain jobs | `sbatch --parsable` + `--dependency=afterok:<ID>` |
| Limit array concurrency | `--array=1-100%4` |
| Attach to running job | `srun --jobid=<ID> --overlap --pty /bin/bash -l` |
| Check QOS limits | `sacctmgr show qos workq_qos` |
| Check my accounts | `sacctmgr show user $(whoami) withassoc` |

---

## Related Resources

- [Isambard job scheduling page](https://docs.isambard.ac.uk/user-documentation/information/job-scheduling/)
- [Isambard acceptable use policy](https://docs.isambard.ac.uk/policies/acceptable_use/)
- [Isambard portal (allocation usage)](https://portal.isambard.ac.uk)
- [Slurm sbatch man page](https://slurm.schedmd.com/sbatch.html)
- [Slurm srun man page](https://slurm.schedmd.com/srun.html)
- [Slurm QOS documentation](https://slurm.schedmd.com/qos.html)