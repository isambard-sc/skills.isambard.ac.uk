<!-- Snapshot of https://docs.isambard.ac.uk/user-documentation/guides/slurm/ made by snapshot_docs.py. Do not edit. -->

# Slurm: Basics

Isambard-AI and Isambard 3 use the Slurm Workload Manager to schedule and run jobs on compute nodes. This guide covers the day-to-day commands for monitoring the queue, submitting jobs, and managing them.

For advanced topics including multi-node jobs, `salloc`, scheduler flexibility, complex job dependencies, QOS limits, and `--exclusive` across platforms, see the advanced guide.

## Monitoring the queue

### Checking jobs in the queue: `squeue`

`squeue` lists jobs currently in the queue, and can be combined with `--me` to show only your own jobs:

```
user.project@nid001040:~> squeue --me
JOBID         USER PARTITION       NAME ST TIME_LIMIT    TIME TIME_LEFT NODES NODELIST(REASON)
19130 user.project     workq    my_job  R    1:00:00    0:12    0:48     1 nid001038
19131 user.project     workq my_array PD    1:00:00    0:00   1:00:00    1 (Priority)

```

The `squeue` command is highly customisable but is not covered here. Please consult the Slurm documentation for further information.

Avoid excessively polling the queue

Running `squeue` or `sinfo` in a rapid loop — using `watch` or the `--iterate` flag with a short interval — floods the Slurm scheduler with queries. This can slow down job scheduling for every user on the system, not just your own jobs.

Instead:

- Run `squeue --me` or `sinfo` manually when you need a status update.
- Use `sacct` to review completed jobs (see Slurm: Advanced).
- If you must poll from a script, use an interval of at least 60 seconds and do so from a single terminal only.

Disruptive polling is a breach of the acceptable use policy. Accounts may be suspended to protect the service.

Other users' jobs may not be visible

On some BriCS services, we have disabled the ability to see other users' jobs in the queue.

For details on partitions, time limits, and per-project resource limits on each system, see the job scheduling page.

### Checking available resources: `sinfo`

`sinfo` shows the partitions available on the system and the current state of their nodes.

```
user.project@nid001040:~> sinfo
PARTITION AVAIL  TIMELIMIT  NODES  STATE NODELIST
workq*       up 1-00:00:00     36  idle~ nid[001001-001036]
workq*       up 1-00:00:00      2  drain nid[001037-001038]

```

Avoid over-interpretation of `sinfo`

The information displayed by `sinfo` can be difficult to interpret and should only be used to gain a general impression of node availability.

## Submitting jobs

At the basic level, there are two ways to submit work to the compute nodes. Non-interactive 'batch' jobs using the `sbatch` command and interactive jobs using `srun`. Both types are submitted to the queue.

The examples below cover single-node jobs. Running a job across multiple nodes is a common requirement and is covered in the advanced guide.

Two common mistakes when specifying resources

- Resources spread across nodes: Requesting GPUs or tasks without `--nodes=1` allows Slurm to draw resources from more than one node. Most single-node workloads will fail or perform poorly as a result. The examples below include `--nodes=1` to prevent this.
- Accidental node reservation with `--exclusive`: Adding `--exclusive` to an `sbatch` script reserves an entire node regardless of how many GPUs or cores you actually use. This increases your queue wait time and reduces overall system utilisation. Avoid it unless your workload specifically requires it — see the advanced guide for details.

### Batch jobs: `sbatch`

Jobs submitted using `sbatch` allow you to submit jobs to the queue to run whether you are currently logged in or not, for example overnight or at weekends. It consists of writing a batch script containing `#SBATCH` directives and submitting it with `sbatch`. The scheduler queues the script and runs it when the requested resources are available.

Always set a time limit

Use `--time` to set a walltime limit for your job. The maximum walltime on all Isambard systems is 24 hours — see the job scheduling page. If your workload needs to run for longer, see job dependencies in the advanced guide. Setting a shorter walltime may result in better queuing times, noting that jobs will be terminated when they reach their time limit.

#### Running a single batch job

To run a batch job, you must write a batch file, and then submit it using the `sbatch` command.

=== "Isambard-AI"

Requesting one GPU allocates one complete GH200 Superchip:

```
#!/bin/bash

#SBATCH --job-name=my_job
#SBATCH --output=my_job.out
#SBATCH --nodes=1
#SBATCH --gpus=1
#SBATCH --time=00:05:00

hostname
nvidia-smi --list-gpus

```

```
user.project@nid001040:~> sbatch my_job.sh
Submitted batch job 19159
user.project@nid001040:~> cat my_job.out
nid001038
GPU 0: GH200 120GB (UUID: GPU-f9fc6950-574a-5310-dc7c-b8d02cc529db)

```

=== "Isambard 3"

```
#!/bin/bash

#SBATCH --job-name=my_job
#SBATCH --output=my_job.out
#SBATCH --nodes=1
#SBATCH --time=00:05:00

hostname
numactl -s

```

```
user.project@login02:~> sbatch my_job.sh
Submitted batch job 19159
user.project@login02:~> cat my_job.out
x3003c0s31b2n0
policy: default
preferred node: current
physcpubind: 0
cpubind: 0
nodebind: 0
membind: 0 1

```

#### Running multiple tasks in parallel

Use `srun` inside a batch script to run a command across multiple tasks simultaneously. The following example runs a Python script on four tasks in parallel, one per GPU:

=== "Isambard-AI"

```
#!/bin/bash

#SBATCH --job-name=parallel_tasks
#SBATCH --output=parallel_tasks.out
#SBATCH --nodes=1
#SBATCH --gpus=4
#SBATCH --ntasks-per-gpu=1
#SBATCH --time=00:05:00

module load cray-python

srun python3 pysrun.py

```

=== "Isambard 3"

```
#!/bin/bash

#SBATCH --job-name=parallel_tasks
#SBATCH --output=parallel_tasks.out
#SBATCH --nodes=1
#SBATCH --ntasks=3
#SBATCH --time=00:05:00

module load cray-python

srun python3 pysrun.py

```

Running independent job steps concurrently

You can run several independent `srun` steps at the same time within a batch script by appending `&` to each and adding `wait` at the end:

```
srun --ntasks=1 --gpus=1 --exclusive job_step_a &
srun --ntasks=1 --gpus=1 --exclusive job_step_b &
wait

```

The `--exclusive` flag ensures each step uses only the resources it requests, allowing them to run concurrently without interfering with each other. See the advanced guide for a full discussion of `--exclusive`.

`srun` inside `sbatch` vs `srun` on the command line

`srun` appears in two contexts that can be confusing at first. Inside a batch script, `srun` launches a job step within the resources already allocated by `sbatch` — it does not submit a new job to the queue. On the command line, `srun` submits an entirely new job to the queue and waits for it to start. The same command behaves differently depending on whether it is running inside an existing allocation or not.

### Interactive jobs: `srun`

If you want to work on a compute node interactively, use `srun`. Note that the job ends if you close the terminal.

#### Running a single command

=== "Isambard-AI"

```
user.project@nid001040:~> srun --nodes=1 --gpus=1 --time=00:02:00 nvidia-smi --list-gpus
srun: job 19164 queued and waiting for resources
srun: job 19164 has been allocated resources
GPU 0: GH200 120GB (UUID: GPU-4833ca67-f003-3dbd-1d44-a5c7645a5ae3)

```

=== "Isambard 3"

```
user.project@login02:~> srun --nodes=1 --time=00:02:00 numactl -s
policy: default
preferred node: current
physcpubind: 0
cpubind: 0
nodebind: 0
membind: 0 1

```

#### Starting an interactive shell

Use `--pty` to start an interactive shell on a compute node:

=== "Isambard-AI"

```
user.project@nid001040:~> srun --nodes=1 --gpus=1 --time=00:15:00 --pty /bin/bash --login
srun: job 22874 queued and waiting for resources
srun: job 22874 has been allocated resources
user.project@nid001005:~> hostname
nid001005
user.project@nid001005:~> nvidia-smi --list-gpus
GPU 0: GH200 120GB (UUID: GPU-f00d9a03-840c-5ea2-a748-243383b6efbc)

```

=== "Isambard 3"

```
user.project@login02:~> srun --nodes=1 --time=00:15:00 --pty /bin/bash --login
user.project@x3010c0s19b2n0:~> numactl -s
policy: default
preferred node: current
physcpubind: 0
cpubind: 0
nodebind: 0
membind: 0 1

```

## Managing jobs

### Job arrays

Job arrays allow you to submit many similar jobs with a single `sbatch` command. Each task in the array receives a unique value in the `SLURM_ARRAY_TASK_ID` environment variable, which your script can use to vary its behaviour (for example, to process a different input file per task).

=== "Isambard-AI"

```
#!/bin/bash

#SBATCH --job-name=my_array
#SBATCH --output=my_array_%a.out
#SBATCH --array=1-4
#SBATCH --nodes=1
#SBATCH --gpus=1
#SBATCH --time=00:05:00

echo "Array task ${SLURM_ARRAY_TASK_ID} running on $(hostname)"

```

=== "Isambard 3"

```
#!/bin/bash

#SBATCH --job-name=my_array
#SBATCH --output=my_array_%a.out
#SBATCH --array=1-4
#SBATCH --nodes=1
#SBATCH --time=00:05:00

echo "Array task ${SLURM_ARRAY_TASK_ID} running on $(hostname)"

```

Array tasks appear in `squeue` with the format `JOBID_TASKID`:

```
user.project@login02:~> squeue --me
JOBID         USER PARTITION      NAME ST TIME_LIMIT    TIME TIME_LEFT NODES NODELIST(REASON)
19200_1 user.project     workq my_array  R      5:00    0:01      4:59     1 nid001005
19200_2 user.project     workq my_array  R      5:00    0:01      4:59     1 nid001012
19200_3 user.project     workq my_array PD      5:00    0:00      5:00     1 (Priority)
19200_4 user.project     workq my_array PD      5:00    0:00      5:00     1 (Resources)

```

Arrays and scheduler load

Large arrays with short tasks can place extra load on the scheduler and consume allocated credits quickly. For many similar short tasks, consider using concurrent `srun` job steps within a single batch job instead. See the advanced guide for more on arrays and scheduler efficiency.

### Job dependencies

Job dependencies allow you to control the order in which jobs run. A common use case is chaining jobs so that the next step only starts if the previous one succeeded.

Dependencies are specified using the `--dependency` flag on `sbatch`. The `singleton` type ensures that only one job with a given name and user runs at a time:

```
user.project@login02:~> sbatch --dependency=singleton my_job.sh
Submitted batch job 52642
user.project@login02:~> sbatch --dependency=singleton my_job.sh
Submitted batch job 52643
user.project@login02:~> squeue --me --Format="JobID,Name,StateCompact:6,ReasonList,Dependency:32"
JOBID               NAME                ST    NODELIST(REASON)    DEPENDENCY
52643               my_job              PD    (Dependency)        singleton(unfulfilled)
52642               my_job               R    nid001005           (null)

```

For more dependency types — including `afterok` for conditional chains and tips on scripting with job IDs — see the advanced guide.

### Cancelling jobs: `scancel`

Use `scancel` followed by a job ID to cancel a job, e.g. to cancel one task of the array example above:

```
user.project@login02:~> scancel 19200_1

```

To cancel all your jobs at once:

```
user.project@login02:~> scancel --me

```

To cancel all tasks in a job array:

```
user.project@login02:~> scancel 19200

```
