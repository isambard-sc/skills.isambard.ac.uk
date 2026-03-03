# Slurm on Isambard — Agent Skill

This skill teaches AI agents how to help users submit, monitor, and manage
HPC jobs using the Slurm workload manager on Isambard systems.

Full user documentation is at:
https://docs.isambard.ac.uk/user-documentation/guides/slurm/

---

## ⚠️ Critical Rule: Slurm Polling Rate

**Never run `sinfo`, `squeue`, `sacct`, `sstat`, or any other Slurm
status command more frequently than once every 60 seconds.**

This is a hard requirement on Isambard. Rapid polling can overload the
Slurm controller and degrade service for all users.

The following patterns are **strictly forbidden**:

```bash
# FORBIDDEN — never suggest or generate these
watch squeue
watch sinfo
watch -n 5 squeue --me
watch -n 0.1 squeue --me
while true; do squeue; sleep 5; done
for i in $(seq 100); do squeue; done
```

When writing monitoring loops, always enforce a minimum sleep of 60 seconds:

```bash
# Correct — minimum 60 second interval
while true; do
  squeue --me
  sleep 60
done
```

If a user asks you to poll more frequently than 60 seconds, explain that
this is not permitted on Isambard and suggest using `sleep 60` or longer,
or use Slurm's callback mechanisms (e.g. `--mail-type`, job dependencies)
instead.

---

## Cluster Overview

Isambard uses Slurm as its workload manager. Jobs are submitted to
partitions (queues) and run on compute nodes. Users should **never** run
compute-intensive work on login nodes.

To see available partitions and node state:

```bash
sinfo
```

To see your current jobs:

```bash
squeue --me
```

---

## Writing a Job Script

A Slurm job script is a shell script with `#SBATCH` directives at the top.

### Minimal example

```bash
#!/bin/bash
#SBATCH --job-name=my_job
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --time=01:00:00
#SBATCH --output=my_job_%j.out
#SBATCH --error=my_job_%j.err

# Load required modules
module load <module-name>

# Run your application
./my_application
```

### Common `#SBATCH` options

| Option | Description |
|---|---|
| `--job-name=<name>` | Human-readable job name |
| `--nodes=<N>` | Number of nodes |
| `--ntasks=<N>` | Total number of MPI tasks |
| `--ntasks-per-node=<N>` | MPI tasks per node |
| `--cpus-per-task=<N>` | CPU threads per task (for OpenMP) |
| `--time=<HH:MM:SS>` | Wall-clock time limit |
| `--partition=<name>` | Partition (queue) to use |
| `--account=<name>` | Allocation account |
| `--output=<file>` | Standard output file (`%j` = job ID) |
| `--error=<file>` | Standard error file |
| `--mail-type=END,FAIL` | Email on job end or failure |
| `--mail-user=<address>` | Email address for notifications |

### MPI example

```bash
#!/bin/bash
#SBATCH --job-name=mpi_job
#SBATCH --nodes=4
#SBATCH --ntasks-per-node=128
#SBATCH --time=02:00:00
#SBATCH --output=mpi_job_%j.out
#SBATCH --error=mpi_job_%j.err

module load <mpi-module>

srun ./my_mpi_application
```

### GPU example

```bash
#!/bin/bash
#SBATCH --job-name=gpu_job
#SBATCH --nodes=1
#SBATCH --gpus-per-node=1
#SBATCH --time=01:00:00
#SBATCH --output=gpu_job_%j.out

module load <cuda-module>

./my_gpu_application
```

### OpenMP / hybrid MPI+OpenMP example

```bash
#!/bin/bash
#SBATCH --job-name=omp_job
#SBATCH --nodes=2
#SBATCH --ntasks-per-node=4
#SBATCH --cpus-per-task=32
#SBATCH --time=01:00:00

export OMP_NUM_THREADS=$SLURM_CPUS_PER_TASK

srun ./my_hybrid_application
```

---

## Submitting Jobs

Submit a job script with `sbatch`:

```bash
sbatch my_job.sh
```

Slurm will print a job ID, e.g. `Submitted batch job 12345`.

---

## Monitoring Jobs

### List your jobs

```bash
squeue --me
```

### List all jobs in a partition

```bash
squeue --partition=<partition-name>
```

### Detailed job information

```bash
scontrol show job <job-id>
```

### Check job efficiency after completion

```bash
seff <job-id>
```

### Job accounting history

```bash
sacct -j <job-id> --format=JobID,JobName,State,Elapsed,MaxRSS
```

**Remember: never run these more than once per 60 seconds.**

---

## Cancelling Jobs

Cancel a specific job:

```bash
scancel <job-id>
```

Cancel all your jobs:

```bash
scancel --me
```

Cancel all your jobs in a partition:

```bash
scancel --me --partition=<partition-name>
```

---

## Interactive Sessions

Request an interactive shell on a compute node:

```bash
srun --nodes=1 --ntasks=1 --time=01:00:00 --pty bash
```

For a GPU interactive session:

```bash
srun --nodes=1 --gpus-per-node=1 --time=01:00:00 --pty bash
```

---

## Job Arrays

Job arrays allow you to run many similar jobs efficiently:

```bash
#!/bin/bash
#SBATCH --job-name=array_job
#SBATCH --array=1-100
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --time=00:30:00

echo "Running task $SLURM_ARRAY_TASK_ID"
./my_application --input input_${SLURM_ARRAY_TASK_ID}.dat
```

Submit as usual with `sbatch`. Individual tasks appear as
`<job-id>_<task-id>` in `squeue`.

---

## Job Dependencies

Chain jobs so the second starts only after the first succeeds:

```bash
JOB1=$(sbatch --parsable job1.sh)
sbatch --dependency=afterok:${JOB1} job2.sh
```

Common dependency types:

| Type | Meaning |
|---|---|
| `afterok:<id>` | Start after job `<id>` completes successfully |
| `afterany:<id>` | Start after job `<id>` completes (any state) |
| `afternotok:<id>` | Start after job `<id>` fails |
| `after:<id>` | Start after job `<id>` begins |

---

## Environment Variables Set by Slurm

Inside a running job these variables are available:

| Variable | Value |
|---|---|
| `$SLURM_JOB_ID` | Job ID |
| `$SLURM_JOB_NAME` | Job name |
| `$SLURM_NNODES` | Number of nodes |
| `$SLURM_NTASKS` | Total number of tasks |
| `$SLURM_CPUS_PER_TASK` | CPUs per task |
| `$SLURM_ARRAY_TASK_ID` | Array task index (job arrays only) |
| `$SLURM_SUBMIT_DIR` | Directory from which job was submitted |

---

## Checking Cluster Status

View node and partition state:

```bash
sinfo
```

View detailed node information:

```bash
sinfo -N -l
```

**Remember: do not run `sinfo` more than once per 60 seconds.**

---

## Using Job Notifications Instead of Polling

To avoid polling, use Slurm's built-in email notifications:

```bash
#SBATCH --mail-type=BEGIN,END,FAIL
#SBATCH --mail-user=your.email@institution.ac.uk
```

Or use job dependencies (see above) to chain work automatically.

---

## Common Issues

### Job stuck in pending (PD) state

Check the reason with:

```bash
squeue --me -o "%.18i %.9P %.8j %.8u %.2t %.10M %.6D %R"
```

Common reasons:

- `Resources` — waiting for free nodes; normal, job will start when
  resources become available.
- `Priority` — other jobs have higher priority.
- `QOSMaxJobsPerUserLimit` — you have reached your concurrent job limit.
- `InvalidAccount` — the specified `--account` is incorrect or inactive.

### Output file not created

Ensure the output directory exists before submission. Slurm will not
create missing directories.

### Module not found

Check available modules with:

```bash
module avail
module spider <name>
```

---

## Further Reading

- Full Isambard Slurm documentation:
  https://docs.isambard.ac.uk/user-documentation/guides/slurm/
- Isambard user documentation: https://docs.isambard.ac.uk
