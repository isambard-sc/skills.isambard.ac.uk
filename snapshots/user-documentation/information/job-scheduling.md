<!-- Snapshot of https://docs.isambard.ac.uk/user-documentation/information/job-scheduling/ made by snapshot_docs.py. Do not edit. -->

# Job scheduling

## Overview

The scheduling and allocation of resources to compute jobs on BriCS compute services (Isambard-AI Phase 1, Isambard-AI Phase 2, Isambard 3, etc.) are managed by the Slurm workload manager.

The configuration of the workload manager controls how jobs are scheduled, how resources are shared, and how resource limits are imposed. This configuration is tailored to each BriCS compute service based on the compute resources offered, the expected usage profile of the service, and the principles described in the Resource Management Model.

Key information about the configuration of the workload manager for each compute service is summarized below. For information on how to submit and manage jobs, see the Slurm Job Management guide.

## User and project limits

The following resource limits are effective at the user and project level.

Why do these limits exist?

Per-user and per-project limits may be imposed to prevent any single user or project from monopolising the scheduler queue, which would block others from running jobs. Any such limits in place are reviewed regularly and may be adjusted as the system evolves and usage patterns change. At times, temporary tighter limits may be imposed to ensure the integrity of the service — check the service status page for current restrictions.

=== "Isambard-AI Phase 1"

| Resource Limit | Value | Applies to | QoS name | Notes |
| Max GPUs allocated | 32 | Project | `32gpu_qos` | Maximum `gres/gpu` resource allocated to all jobs associated with a project |

=== "Isambard-AI Phase 2"

| Resource Limit | Value | Applies to | QoS name | Notes |
| Max running jobs | 256 | User | `workq_qos` | `workq` partition |
| Max jobs (pending + running) | 512 | User | `workq_qos` | Jobs pending or running for a user in the `workq` partition |
| Max running jobs | 1 | User | `interactive_qos` | `interactive` reservation only |
| Max queued jobs | 1 | User | `interactive_qos` | `interactive` reservation only |
| Max array size | 1000 | Job | N/A | Maximum number of tasks allowed in a job array |

All of the limits above apply per user, not per project.

What happens if I hit a limit?

On Isambard-AI Phase 2, a job submission that would exceed any of the limits above is rejected immediately at submit time, rather than being accepted and held in the queue until room becomes available. If this happens, resubmit once your running or queued job count drops below the limit. See Job submission fails in the Slurm troubleshooting guide for the error message to expect.

=== "Isambard 3 Grace"

Limits under review

Isambard 3 user and project resource limits have been temporarily relaxed while they are under review.

| Resource Limit | Value | Applies to | QoS name | Notes |
| Max queued jobs | 1000 | User | `grace_qos` | Maximum number of jobs pending or running for a user |

=== "Isambard 3 MACS"

| Resource Limit | Value | Applies to | QoS name | Notes |
| Max GPUs allocated | 2 | Project | `macs_qos` | Maximum `gres/gpu` resource allocated to all jobs associated with a project |
| Max queued jobs | 20 | Project | `macs_qos` | Maximum number of jobs pending or running associated with a project |

## Partition configuration

=== "Isambard-AI Phase 1"

| Partition name | User accessible | QoS name | Nodes | Maximum walltime | Notes |
| workq (*) | | `workq_qos` | 38 × 4 GH200 node | 24h | For general purpose AI/ML workloads |
| bricsonly | | N/A | 2 × 4 GH200 node | N/A | Test partition for BriCS administrators |

=== "Isambard-AI Phase 2"

| Partition name | User accessible | QoS name | Nodes | Maximum walltime | Notes |
| workq (*) | | `workq_qos` | 1320 × 4 GH200 node | 24h | For general purpose AI/ML workloads |
| interactive | | `interactive_qos` | Shared with `workq` (same 4 GH200 node pool) | 8h | Hidden partition applied automatically by the `interactive` reservation — do not select it directly, see `interactive` reservation |

Do not specify `--partition` with `--reservation=interactive`

Do not add a `--partition` flag when requesting the `interactive` reservation. Slurm selects the `interactive` partition and applies its `interactive_qos` limits based on the reservation alone. Overriding this is not an acceptable way to use the reservation, and such jobs may be cancelled — see `interactive` reservation below.

=== "Isambard 3 Grace"

| Partition name | User accessible | QoS name | Nodes | Maximum walltime | Notes |
| grace (*) | | `grace_qos` | 384 × 2 Grace CPU superchip node | 24h | For general purpose CPU workloads |

=== "Isambard 3 MACS"

| Partition name | User accessible | QoS name | Nodes | Maximum walltime |
| milan | | `macs_qos` | 12 × AMD Milan CPU node | 24h |
| genoa | | `macs_qos` | 2 × AMD Genoa CPU node | 24h |
| berg | | `macs_qos` | 2 × AMD Bergamo CPU node | 24h |
| spr | | `macs_qos` | 2 × Intel Sapphire Rapids CPU node | 24h |
| sprhbm | | `macs_qos` | 2 × Intel Sapphire Rapids CPU node (HBM) | 24h |
| ampere | | `macs_qos` | 2 × AMD Milan CPU + 4 A100 GPU node | 24h |
| hopper | | `macs_qos` | 1 × AMD Milan CPU + 4 H100 GPU node | 24h |
| instinct | | `macs_qos` | 2 × AMD Milan CPU + 4 MI100 GPU node | 24h |

Multi-Architecture Comparison System (MACS)

The Multi-Architecture Comparison System (MACS) comprises small numbers of compute nodes of varying architectures. The system is not suitable for production workloads, and is intended for use to research, evaluate, and compare different node architectures.

(*) Denotes the default partition that jobs are submitted to if no partition is specified.

## Interactive reservation (Isambard-AI Phase 2)

The `interactive` reservation on Isambard-AI Phase 2 provides a small, dedicated pool of nodes for short-lived work. Use it for tasks that require a compute node but where waiting in the normal queue would be disruptive, for example debugging, experimentation or exploratory analysis.

Not for large-scale batch compute

The `interactive` reservation must not be used to run large volumes of batch work. The total resource available to the reservation is finite, and usage is monitored.

Do not specify `--partition` with the `interactive` reservation

Request the `interactive` reservation with `--reservation=interactive` only — do not add a `--partition` flag. Slurm selects the `interactive` partition and applies its `interactive_qos` limits based on the reservation alone.

Overriding this is not an acceptable way to use the reservation: the nodes are set aside for everyone's short interactive work, and the limits below exist to keep them available. Doing so is considered an activity that is detrimental to the operation of BriCS facilities, a form of Unacceptable Use under the Acceptable Use Policy.

Jobs submitted this way may be cancelled without warning. Repeated or deliberate use of the reservation in this way will be subject to the procedures set out in the Penalties for Misuse section of the Acceptable Use Policy.

### Resource limits

| Limit | Value |
| Maximum job size | 4 nodes (16 GPUs) |
| Maximum walltime | 8 hours |
| Default walltime | 30 minutes |
| Maximum running jobs per user | 1 |
| Maximum queued jobs per user | 1 |

### Billing

Jobs run on the `interactive` reservation are charged at a 50% premium. One node-hour (NHR) on the `interactive` reservation is billed as 1.5 NHR.

For usage examples, see `interactive` reservation in the Slurm guide.

The 24-hour maximum walltime described above applies to general-purpose partitions such as `workq`; the `interactive` partition has its own 8-hour limit, enforced via `interactive_qos`.

Why is the maximum walltime 24 hours?

The 24-hour limit helps ensure fair scheduling across all users. Jobs that run for longer periods hold nodes that cannot be reassigned to other work, making it harder for the scheduler to backfill shorter jobs and increasing queue times for everyone. The limit also allows the operations team to apply system maintenance and security patches regularly without needing to forcibly terminate long-running jobs. It also protects your work: jobs running for days without checkpointing are vulnerable to any system interruption.

Workloads requiring longer than 24 hours should implement checkpointing to enable jobs to resume from where they left off. See the Slurm guide for information on job dependencies and resubmission.
