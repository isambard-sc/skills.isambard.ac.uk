<!-- Snapshot of https://docs.isambard.ac.uk/user-documentation/guides/slurm-advanced/ made by snapshot_docs.py. Do not edit. -->

# Slurm: Advanced

This guide builds on Slurm: Basics and covers more advanced job management topics. It assumes familiarity with `sbatch`, `srun`, `squeue`, and `scancel`.

## Monitoring jobs

### Checking job history: `sacct`

`sacct` shows your current and recently completed jobs, including exit codes and resource usage. Unlike `squeue`, which only shows active jobs, `sacct` provides a record of past runs. It is highly customisable and further information can be found in the Slurm documentation.

### Debugging a running job: `srun --jobid`

You can attach an interactive shell to a job that is already running, which is useful for inspecting the environment or monitoring progress without interfering with the job itself.

First, find the job ID with `squeue --me`, then use `srun` with `--jobid` and `--overlap`:

```
user.project@nid001040:~> sbatch script.sh
Submitted batch job 22886

user.project@nid001040:~> squeue --me
JOBID         USER PARTITION    NAME ST TIME_LIMIT    TIME TIME_LEFT NODES NODELIST(REASON)
22886 user.project     workq  script  R      10:00    0:03      9:57     1 nid001005

user.project@nid001040:~> srun --ntasks=1 --gpus=1 --jobid=22886 --overlap --pty /bin/bash -l
user.project@nid001005:~> nvidia-smi --list-gpus
GPU 0: GH200 120GB (UUID: GPU-f00d9a03-840c-5ea2-a748-243383b6efbc)
user.project@nid001005:~> exit
logout

```

After exiting the interactive shell, the original job continues running.

## Submitting jobs

### Multi-node jobs

When your workload needs more resources than a single node can provide — for example, an MPI application or a distributed training job — use `--nodes` to request more than one node. `srun` will launch processes across all allocated nodes automatically.

=== "Isambard-AI"

Request full nodes by combining `--nodes` with `--gpus-per-node=4`. Each node contains four GH200 Superchips, so `--gpus-per-node=4` ensures your job uses whole nodes and avoids leaving partially-used nodes in the queue.

```
#!/bin/bash

#SBATCH --job-name=multi_node
#SBATCH --output=multi_node.out
#SBATCH --nodes=2
#SBATCH --gpus-per-node=4
#SBATCH --time=01:00:00

srun ./my_application

```

=== "Isambard 3"

Use `--ntasks-per-node` to control how many MPI ranks (or tasks) run on each node. Each Grace node has 144 CPU cores across two Superchips.

```
#!/bin/bash

#SBATCH --job-name=multi_node
#SBATCH --output=multi_node.out
#SBATCH --nodes=2
#SBATCH --ntasks-per-node=144
#SBATCH --time=01:00:00

srun ./my_mpi_application

```

Useful environment variables set by Slurm for multi-node jobs:

| Variable | Value |
| `$SLURM_JOB_NUM_NODES` | Number of nodes allocated. |
| `$SLURM_NODELIST` | Hostnames of all allocated nodes. |
| `$SLURM_NTASKS` | Total number of tasks across all nodes. |
| `$SLURM_NODEID` | Index of the node the current process is running on (0-based). |

See the example scripts for downloadable templates.

### Hybrid MPI/OpenMP jobs

Hybrid parallelism combines MPI for communication between processes with OpenMP for threading within each process. The key Slurm directives are:

- `--ntasks-per-node` — number of MPI ranks per node
- `--cpus-per-task` — CPU cores allocated to each rank (used for OpenMP threads)

Set `OMP_NUM_THREADS=$SLURM_CPUS_PER_TASK` in your script so the thread count always matches the allocation. The product of `--ntasks-per-node` × `--cpus-per-task` should equal the cores you want to use per node.

=== "Isambard-AI"

Each node contains four GH200 Superchips, each with 72 Arm Neoverse cores and one GPU. A natural mapping is one MPI rank per Superchip with 72 OpenMP threads per rank:

```
#!/bin/bash

#SBATCH --job-name=hybrid_mpi_omp
#SBATCH --output=hybrid_mpi_omp.out
#SBATCH --nodes=2
#SBATCH --gpus-per-node=4
#SBATCH --ntasks-per-node=4
#SBATCH --cpus-per-task=72
#SBATCH --time=01:00:00

export OMP_NUM_THREADS=$SLURM_CPUS_PER_TASK

srun ./my_hybrid_application

```

=== "Isambard 3"

Each node has 144 CPU cores across two Grace CPU Superchips (72 cores each). A typical mapping is one MPI rank per Superchip with 72 OpenMP threads per rank:

```
#!/bin/bash

#SBATCH --job-name=hybrid_mpi_omp
#SBATCH --output=hybrid_mpi_omp.out
#SBATCH --nodes=2
#SBATCH --ntasks-per-node=2
#SBATCH --cpus-per-task=72
#SBATCH --time=01:00:00

export OMP_NUM_THREADS=$SLURM_CPUS_PER_TASK

srun ./my_hybrid_application

```

For finer control over how processes and threads are bound to CPU cores, see the `--cpu-bind` option in the srun man page.

### Holding an allocation with `salloc`

`salloc` reserves compute resources as a named allocation, then lets you run individual `srun` commands against that allocation from the login node. This can be useful when you want to run several short-lived commands without repeatedly waiting for the queue.

```
user.project@nid001040:~> salloc --nodes=1 --gpus=1 --time=00:10:00
salloc: Granted job allocation 19130
user.project@nid001040:~> srun hostname
nid001016
user.project@nid001040:~> srun nvidia-smi --list-gpus
GPU 0: GH200 120GB (UUID: GPU-4833ca67-f003-3dbd-1d44-a5c7645a5ae3)

```

Release allocations when finished

Always set a `--time` limit with `salloc`, and cancel the allocation with `scancel <JOBID>` when you are done. An idle allocation holds resources that other users cannot use, and uses allocated node hour credits.

### `interactive` reservation (Isambard-AI Phase 2)

The `interactive` reservation provides a dedicated pool of nodes on Isambard-AI Phase 2 for interactive, short-lived or exploratory work. Use it when you need shorter queue times for tasks such as debugging, development, or exploratory analysis.

To start a shell on the `interactive` reservation, use `srun` with `--reservation=interactive`:

```
user.project@login40:~> srun --gpus=1 --reservation=interactive --pty bash -i
srun: job 22900 queued and waiting for resources
srun: job 22900 has been allocated resources
user.project@nid001005:~>

```

If you do not specify `--time`, the job will run for the default walltime of 30 minutes. The reservation accepts a maximum of 4 nodes (16 GPUs) per job and an 8-hour maximum walltime — see `interactive` reservation in the job scheduling reference for the full limits.

Use `--partition=interactive` to see these jobs in `squeue`

The `interactive` partition is hidden, so jobs running in the reservation do not appear in the output of `squeue --me` on its own. Add `--partition=interactive` to list them:

```
user.project@login40:~> squeue --me --partition=interactive
JOBID         USER   PARTITION    NAME ST TIME_LIMIT    TIME TIME_LEFT NODES NODELIST(REASON)
22900 user.project interactive    bash  R      30:00    2:14     27:46     1 nid001005

```

Alternatively, `squeue --me --all` lists your jobs across every partition, including hidden ones.

This affects `squeue` only, which reads the queue. It does not change how jobs are submitted — see the warning below.

Do not also specify `--partition`

Do not add a `--partition` flag to a command that also sets `--reservation=interactive`. Slurm selects the `interactive` partition and applies its `interactive_qos` limits based on the reservation alone — requesting `--reservation=interactive` on its own, as shown above, is sufficient.

Overriding this is not an acceptable way to use the reservation, and is considered an activity that is detrimental to the operation of BriCS facilities, a form of Unacceptable Use under the Acceptable Use Policy.

Jobs submitted this way may be cancelled without warning. Repeated or deliberate use of the reservation in this way will be subject to the procedures set out in the Penalties for Misuse section of the Acceptable Use Policy.

Short-lived work only

The nodes in the `interactive` reservation are shared and in high demand, so they are reserved for short-lived work only. Running long-running or high-throughput jobs on the reservation is not permitted. Usage is monitored.

Billed at a premium

Jobs on the `interactive` reservation are charged at a 50% premium. One node-hour (NHR) on the `interactive` reservation is billed as 1.5 NHR.

### Scheduler flexibility

The scheduler builds a view of resource availability over time and assigns jobs to gaps in that schedule. Giving the scheduler more flexibility about when and where your job runs can result in it starting sooner.

#### Flexible time: `--time-min`

`--time-min` sets the minimum time your job needs to run, while `--time` sets the maximum. The scheduler can then place your job into a gap that is shorter than `--time` but at least `--time-min` long — a technique known as backfill scheduling.

For example, specifying `--time-min=01:00:00` and `--time=12:00:00` allows your job to run on nodes that are reserved for another job starting in, say, 90 minutes — a slot that would otherwise be wasted:

```
#SBATCH --time=12:00:00
#SBATCH --time-min=01:00:00

```

Your job will always run for as long as resources allow, up to `--time`.

#### Flexible node count: `--nodes`

`--nodes` accepts a range in the form `<min>-<max>`. The scheduler will start your job with as many nodes as are available, between the minimum and maximum:

```
#SBATCH --nodes=1-4

```

Inside the job, `$SLURM_JOB_NUM_NODES` contains the actual number of nodes allocated. Your job script must be written to handle a variable node count.

### Resource isolation with `--exclusive`

The `--exclusive` flag controls whether a job or job step shares allocated resources with others. Its behaviour differs depending on whether it is used at the job level (in an `sbatch` directive) or the step level (on an `srun` command).

#### At the job step level (srun command)

When running concurrent `srun` steps within a batch job, `--exclusive` prevents steps from over-subscribing the allocation. Each step uses only the resources it requests, allowing multiple steps to run in parallel:

```
srun --ntasks=1 --gpus=1 --exclusive step_a &
srun --ntasks=1 --gpus=1 --exclusive step_b &
wait

```

Without `--exclusive`, both steps would inherit the full job allocation and may conflict.

#### At the job level (sbatch directive)

`--exclusive` used as an `#SBATCH` directive (or passed to `sbatch`) prevents other jobs from sharing the same physical node:

```
#SBATCH --exclusive

```

=== "Isambard-AI"

On Isambard-AI, each GPU request allocates one complete Grace Hopper Superchip. A single node contains four Superchips (four GPUs). Without `--exclusive`, jobs from different users may share the same physical node, each using separate Superchips. Adding `--exclusive` reserves the entire node for your job, preventing any sharing. This is appropriate when your workload is sensitive to noise from other tenants on the same node, but note that it may reduce your priority or increase queue wait times.

=== "Isambard 3"

On Isambard 3 Grace, nodes can be shared between users by default. Adding `--exclusive` reserves the entire node — all cores and memory — for your job. This is useful when your workload requires access to all NUMA domains or all cores on a node, or when you need consistent, repeatable performance without interference from co-located jobs.

You are charged for the whole node when using `--exclusive` at the job level

When `--exclusive` is set at the job level, the entire node is reserved for your job regardless of how much of it you actually use. For example, on Isambard-AI a node contains four GH200 Superchips. If you request `--gpus=1` with `--exclusive`, you will be allocated and charged for all four Superchips even though only one is used. Only use `--exclusive` at the job level when your workload genuinely requires it.

### Large jobs and being a good citizen

If you are planning to run a job requiring 256 or more nodes, please consider scheduling it to run outside of normal working hours (Bristol time). You can do this using `--begin` when calling `sbatch`, or by adding `#SBATCH --begin=` to your batch script:

```
#SBATCH --begin=YYYY-MM-DDTHH:MM:SS

```

An example of the full syntax can be found on the sbatch man page. Note that the begin time is the earliest your job may start; it may run later if resources are not available.

Running large jobs outside of working hours helps other users run smaller jobs during the day. This is entirely optional, and we recognise it is not always possible.

## Managing jobs

### Job dependencies

Job dependencies allow you to control the order in which jobs execute. Specify dependencies using the `--dependency` flag on `sbatch`.

The basics guide introduces the `singleton` dependency type. The `afterok` type is also commonly used — it makes a job start only after one or more specified jobs have completed successfully (exit code 0):

```
user.project@login02:~> sbatch submit_dependency.sh
Submitted batch job 52646
user.project@login02:~> sbatch --dependency=afterok:52646 submit_dependency.sh
Submitted batch job 52647
user.project@login02:~> sbatch --dependency=afterok:52647 submit_dependency.sh
Submitted batch job 52648

```

Use `squeue` with the `--Format` flag to view dependency information:

```
user.project@login02:~> squeue --me --Format="JobID,Name,StateCompact:6,TimeUsed,ReasonList,Dependency:32"
JOBID               NAME                ST    TIME                NODELIST(REASON)    DEPENDENCY
52647               dependency_example  PD    0:00                (Dependency)        afterok:52646(unfulfilled)
52648               dependency_example  PD    0:00                (Dependency)        afterok:52647(unfulfilled)
52646               dependency_example  R     0:19                x3010c0s31b1n0      (null)

```

Capture job IDs in a script

The `--parsable` flag makes `sbatch` output only the job ID, which you can capture in a shell variable to use as a dependency:

```
user.project@login02:~> JOBID_1=$(sbatch --parsable submit_dependency.sh)
user.project@login02:~> JOBID_2=$(sbatch --parsable --dependency=afterok:${JOBID_1} submit_dependency.sh)
user.project@login02:~> echo "JOBID_1 = ${JOBID_1}, JOBID_2 = ${JOBID_2}"
JOBID_1 = 52650, JOBID_2 = 52651

```

Other dependency types, including `afterany`, `afternotok`, and combinations, are described in the sbatch man page.

### Job arrays

The basics guide covers the essentials of job arrays. Two additional options are useful for controlling array behaviour:

Limit concurrency — `%N` after the range limits how many tasks run simultaneously. This prevents a large array from monopolising the queue:

```
#SBATCH --array=1-100%4

```

Step through a range — a step value selects every Nth task ID:

```
#SBATCH --array=0-90:10

```

This submits tasks with IDs 0, 10, 20, 30, ... 90.

If you have a large number of short tasks, consider using concurrent `srun` job steps within a single batch job rather than an array — this reduces scheduler overhead and avoids holding many pending array tasks in the queue simultaneously.

### QOS and resource limits

Slurm uses Quality of Service (QOS) settings to enforce per-user and per-project resource limits. Each partition has a default QOS; additional QOS may be applied to your account.

To check the QOS settings for a partition:

```
user.project@nid001040:~> sacctmgr show qos workq_qos

```

To check your own account's QOS:

```
user.project@nid001040:~> sacctmgr show user user.project withassoc

```

The `MaxTRESPA` field limits the resources a project can use simultaneously (for example, number of GPUs or nodes).

#### Allocation limit errors

If a job submission fails with messages such as:

```
srun: error: AssocGrpCPUMinutesLimit
srun: error: AssocGrpGRESMinutesLimit
srun: error: AssocGrpMemMinutesLimit
srun: error: Unable to allocate resources: Job violates accounting/QOS policy (job submit limit, user's size and/or time limits)

```

This usually means your project has reached or temporarily exceeded an accounting limit. When a job is queued or running, Slurm reserves credits based on the requested resources and requested wall time. Only what is actually consumed is charged once the job completes, but the reservation is held until then. Large arrays with generous `--time` values can exhaust a project's reserved credit even when the overall allocation is not spent.

To resolve this:

- Wait for running jobs to complete, then retry.
- Set `--time` as close as possible to the expected runtime.
- Check your project's usage and allocation in the portal and discuss with your PI if needed.

For further guidance, see the Slurm troubleshooting guide.

### Job requeues and restarts

Jobs are automatically requeued if they fail due to a node fault or other system-level issue. This does not apply to jobs that fail because of errors in the job script or user-requested cancellations.

When a job is requeued:

- The job attempts to start on different nodes.
- The job ID remains the same.
- The job restarts from the beginning — there is no automatic checkpointing.

Slurm sets `SLURM_RESTART_COUNT` to indicate whether a job has been restarted:

- `0` — first run
- `>0` — job has been restarted at least once

You can check this at the start of your job script to skip work that was already completed in a previous run.

If a job fails to start repeatedly and exhausts the retry limit, it will enter a `PENDING` state with the reason `JobHoldMaxRequeue`. Cancel it with `scancel` and resubmit.

To opt out of automatic requeuing, use `--no-requeue` in your script or on the command line. This is recommended if restarting your job could cause duplicate writes, repeated API calls, or other unintended side effects.
