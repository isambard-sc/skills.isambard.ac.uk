<!-- Snapshot of https://docs.isambard.ac.uk/user-documentation/guides/slurm-examples/ made by snapshot_docs.py. Do not edit. -->

# Slurm: Example Scripts

This page collects ready-to-use batch scripts for common job patterns on Isambard systems. Each script can be downloaded and adapted for your own workload.

For an explanation of the directives used, see the Slurm basics guide and advanced guide.

## Single job

Runs a single set of commands on one node. Useful as a starting point for any new workload.

=== "Isambard-AI"

single_job_iai.sh
```
#!/bin/bash

#SBATCH --job-name=single_job
#SBATCH --output=single_job.out
#SBATCH --nodes=1
#SBATCH --gpus=1
#SBATCH --time=00:30:00

hostname
nvidia-smi --list-gpus

```

=== "Isambard 3"

single_job_i3.sh
```
#!/bin/bash

#SBATCH --job-name=single_job
#SBATCH --output=single_job.out
#SBATCH --nodes=1
#SBATCH --time=00:30:00

hostname
numactl -s

```

## Multi-node jobs

Distributes work across more than one node. On Isambard-AI, `--gpus-per-node=4` requests full nodes. On Isambard 3, `--ntasks-per-node` controls the number of MPI ranks per node. See multi-node jobs in the advanced guide for guidance on environment variables and workload design.

=== "Isambard-AI"

multi_node_iai.sh
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

multi_node_i3.sh
```
#!/bin/bash

#SBATCH --job-name=multi_node
#SBATCH --output=multi_node.out
#SBATCH --nodes=2
#SBATCH --ntasks-per-node=144
#SBATCH --time=01:00:00

srun ./my_mpi_application

```

## Parallel tasks

Runs the same application across multiple tasks simultaneously using `srun`. Replace `./my_application` with the command you want to run.

=== "Isambard-AI"

Requests four GPUs and runs one task per GPU.

parallel_tasks_iai.sh
```
#!/bin/bash

#SBATCH --job-name=parallel_tasks
#SBATCH --output=parallel_tasks.out
#SBATCH --nodes=1
#SBATCH --gpus=4
#SBATCH --ntasks-per-gpu=1
#SBATCH --time=01:00:00

srun ./my_application

```

=== "Isambard 3"

Requests four CPU tasks distributed across the node.

parallel_tasks_i3.sh
```
#!/bin/bash

#SBATCH --job-name=parallel_tasks
#SBATCH --output=parallel_tasks.out
#SBATCH --nodes=1
#SBATCH --ntasks=4
#SBATCH --time=01:00:00

srun ./my_application

```

## Job array

Submits many similar jobs in a single `sbatch` command. Each task receives a unique value in `SLURM_ARRAY_TASK_ID` which your script can use to process a different input file, configuration, or dataset.

=== "Isambard-AI"

job_array_iai.sh
```
#!/bin/bash

#SBATCH --job-name=job_array
#SBATCH --output=job_array_%a.out
#SBATCH --array=1-10
#SBATCH --nodes=1
#SBATCH --gpus=1
#SBATCH --time=01:00:00

echo "Array task ${SLURM_ARRAY_TASK_ID} running on $(hostname)"

# Example: use the task ID to select a different input per task
# python train.py --config configs/config_${SLURM_ARRAY_TASK_ID}.yaml

```

=== "Isambard 3"

job_array_i3.sh
```
#!/bin/bash

#SBATCH --job-name=job_array
#SBATCH --output=job_array_%a.out
#SBATCH --array=1-10
#SBATCH --nodes=1
#SBATCH --time=01:00:00

echo "Array task ${SLURM_ARRAY_TASK_ID} running on $(hostname)"

# Example: use the task ID to select a different input per task
# python process.py --input data/file_${SLURM_ARRAY_TASK_ID}.csv

```

## Dependency chain

Runs jobs one after another, where each job only starts if the previous one completed successfully. The script below can be submitted multiple times using `--dependency=afterok:<JOBID>` to build a chain. See the advanced guide for how to script this automatically using `--parsable`.

submit_dependency.sh
```
#!/bin/bash
#SBATCH --job-name=dependency_example
#SBATCH --time=1
#SBATCH --nodes=1

echo "${SLURM_JOB_ID} on $(hostname) at $(date --iso-8601=seconds)"
sleep 30

```

## Scheduler flexibility

Allows the scheduler to start the job sooner by accepting a range of node counts and a minimum run time. The job will run on however many nodes are available (between `--nodes` min and max) for at least `--time-min`, up to `--time`. Replace `./my_application` with a command that can adapt to `$SLURM_JOB_NUM_NODES` at runtime.

scheduler_flexibility.sh
```
#!/bin/bash

#SBATCH --job-name=flexible_job
#SBATCH --output=flexible_job.out
#SBATCH --nodes=1-4
#SBATCH --time=12:00:00
#SBATCH --time-min=01:00:00

echo "Running on ${SLURM_JOB_NUM_NODES} node(s)"

srun ./my_application

```
