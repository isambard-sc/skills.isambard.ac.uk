# Slurm: Troubleshooting

Problems organised by when they occur. For full Slurm error code reference see the
[Slurm documentation](https://slurm.schedmd.com/).

---

## Job Submission Fails

These errors appear immediately when running `sbatch` or `srun`.

**`Unable to allocate resources: Job violates accounting/QOS policy`**

Your project has reached a resource limit. Slurm reserves credits based on **requested**
resources × **requested** walltime — not actual usage. The reservation is held until the
job finishes.

- Wait for running jobs to complete, then resubmit.
- Set `--time` as close to the expected runtime as possible.
- Check your project's allocation at the [portal](https://portal.isambard.ac.uk).
- See also: `AssocGrpGRESMinutesLimit` in the PENDING section below.

**`error: Invalid generic resource (GRES) specification`**

The `--gpus` or `--gres` value is not valid for the partition. On Isambard-AI, request GPUs
with `--gpus=<n>`. Check the [basics guide](https://docs.isambard.ac.uk/user-documentation/guides/slurm/)
for the correct syntax per system.

**`Batch job submission failed: Requested node configuration is not available`**

The combination of resources requested does not match anything available. Check the
[system specifications](https://docs.isambard.ac.uk/specs/) and
[job scheduling page](https://docs.isambard.ac.uk/user-documentation/information/job-scheduling/)
for valid directives on your target system.

**`error: Invalid account or account/partition combination specified`**

The project name in the job script does not match your account. Run:

```bash
sacctmgr show user $(whoami) withassoc
```

This shows your valid accounts and the partitions associated with each.

---

## Job in PENDING

Check the reason with `squeue --me`. The `NODELIST(REASON)` column explains why the job
has not started.

| Reason | What to do |
|--------|-----------|
| `Priority` | Normal queue behaviour — wait for resources. Your job will run when it reaches the front of the queue. |
| `Resources` | Resources are currently in use — wait. |
| `Dependency` | A job this one depends on has not completed. Check with `squeue` or `sacct`. |
| `PartitionTimeLimit` | `--time` exceeds the partition maximum (24 hours). Reduce it, or chain jobs with `--dependency=afterok`. |
| `ReqNodeNotAvail` | A specific node requested with `--nodelist` is unavailable. Remove the constraint or wait. |
| `AssocGrpCPUMinutesLimit` | Project CPU-minute allocation limit reached. See submission error fix above. |
| `AssocGrpGRESMinutesLimit` | Project GPU-minute allocation limit reached. See submission error fix above. |
| `AssocGrpMemMinutesLimit` | Project memory-minute allocation limit reached. See submission error fix above. |
| `QOSMaxSubmitJobPerUserLimit` | Too many jobs queued. Wait for some to complete before submitting more. |
| `JobHoldMaxRequeue` | Job failed to start repeatedly after node faults. Cancel with `scancel` and resubmit. |
| `BeginTime` | Job has a `--begin` time set; it will not start before that time. |

---

## Job Failure

Check the final state with `sacct` and inspect the output file (`--output`) for errors.

**`TIMEOUT`**

Job hit its `--time` walltime limit and was killed. Either increase `--time` or break the
workload into smaller chunks chained with `--dependency=afterok`.

**`OUT_OF_MEMORY`**

Job was killed by the out-of-memory manager. Options:
- Reduce the memory footprint of your application.
- Request more resources. On Isambard-AI, each additional GPU also allocates an additional
  Superchip's worth of CPU memory.

**`NODE_FAIL`**

A hardware fault on a compute node terminated the job. Eligible jobs are automatically
requeued on a different node — check `squeue` to confirm. If the job does not requeue,
cancel and resubmit. See [job requeues and restarts](advanced.md#job-requeues-and-restarts).

**`FAILED` (non-zero exit code)**

The job script or application exited with an error. Check the `--output` file and any
application logs. The `sacct` exit code format is `<app_exit>:<signal>`:

| Exit code | Meaning |
|-----------|---------|
| `0:0` | Completed successfully |
| `0:15` | Killed by signal (e.g. SIGTERM from time limit) |
| `1:0` | Application exited with error code 1 |
| `N:0` | Application exited with error code N |

**Job shows `COMPLETED` but results are missing or wrong**

- Check that `--output` points to the correct path and the filesystem is accessible from
  compute nodes.
- If using `--array`, confirm `%a` is in the output filename — without it, tasks overwrite
  each other's output.
- Check that output files are not being written to a path only accessible on the login node.