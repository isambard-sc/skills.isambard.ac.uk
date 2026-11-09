<!-- Snapshot of https://docs.isambard.ac.uk/user-documentation/guides/slurm-troubleshooting/ made by snapshot_docs.py. Do not edit. -->

# Slurm: Troubleshooting

Common problems organised by when they occur. For a full reference to Slurm options and error codes, see the Slurm documentation.

## Job submission fails

These errors appear immediately when you run `sbatch` or `srun`.

`Unable to allocate resources: Job violates accounting/QOS policy`

This error appears either because your project has reached a resource limit, or because the job would exceed one of the user or project limits for the system.

If it's a resource limit, Slurm reserves credits based on the resources and time requested, not what is actually used. Wait for running jobs to finish (releasing their reserved credits), then resubmit. Set `--time` as close to the expected runtime as possible to minimise unnecessary reservation. Check your project's allocation in the portal.

If it's a user or project limit, resubmit once your running or queued job count drops below the limit.

`error: Invalid generic resource (GRES) specification`

The `--gpus` or `--gres` value is not valid for the partition. On Isambard-AI, request GPUs with `--gpus=<n>`. See the basics guide for the correct syntax for each system.

`Batch job submission failed: Requested node configuration is not available`

The combination of resources requested does not match anything available. Check the system specifications and job scheduling page for the correct directives for your target system.

`error: Invalid account or account/partition combination specified`

The project name in your job script does not match your account. Run `sacctmgr show user $(whoami) withassoc` to see your valid accounts and partitions.

## Job in PENDING

Check the reason with `squeue --me`. The `NODELIST(REASON)` column explains why the job has not started.

| Reason | What to do |
| `Priority` or `Resources` | Normal queue behaviour — wait for resources to become free. |
| `None` | The scheduler has not yet assigned a reason. This is not an issue on its own and can be due to a number of underlying causes. Your job is in the queue and there is no need to raise a support request. |
| `Dependency` | A job this one depends on has not completed yet. Check its status with `squeue` or `sacct`. |
| `PartitionTimeLimit` | `--time` exceeds the partition maximum (24 hours). Reduce it, or use job dependencies to chain jobs. |
| `ReqNodeNotAvail` | A specific node requested with `--nodelist` is unavailable. Remove the constraint or wait for the node to recover. |
| `AssocGrpCPUMinutesLimit`, `AssocGrpGRESMinutesLimit`, `AssocGrpMemMinutesLimit` | Project allocation limit reached. See the submission error above for what to do. |
| `QOSMaxSubmitJobPerUserLimit` | Too many jobs queued. Wait for some to complete before submitting more. |
| `JobHoldMaxRequeue` | The job failed to start repeatedly after node faults. Cancel with `scancel` and resubmit. |

## Job failure

Check the job's final state with `sacct` and look at the output file for error messages.

`TIMEOUT`

The job hit its `--time` limit and was killed. Increase `--time`, or break the workload into smaller chunks using job dependencies.

`OUT_OF_MEMORY`

The job was killed by the out-of-memory manager. Reduce the memory footprint of your application, or request more resources. On Isambard-AI, requesting an additional GPU also allocates an additional Superchip's worth of memory.

`NODE_FAIL`

A hardware fault on a compute node caused the job to be terminated. Eligible jobs are automatically requeued on a different node — check `squeue` to confirm. If the job does not requeue, cancel it and resubmit. See job requeues and restarts in the advanced guide.

`FAILED` (non-zero exit code)

The job script or application exited with an error. Check the output file (specified by `--output`) and any application logs for the cause. The exit code in `sacct` is in the format `<application_exit>:<signal>` — a value of `0:15` means the job was killed by a signal (for example, hitting the time limit), while `1:0` or higher means the application itself reported an error.

Job shows `COMPLETED` but results are missing or wrong

Check that `--output` points to the correct path and that the filesystem is accessible from the compute nodes. If using `--array`, confirm that `%a` is in the output filename so tasks do not overwrite each other.
