---
name: nccl
description: >
  Guide for using NCCL (NVIDIA Collective Communications Library) on Isambard AI (BriCS)
  supercomputers. Use this skill whenever a user asks about NCCL on Isambard, multi-node
  GPU communication, the aws-ofi-nccl plugin, Slingshot 11 RDMA for GPU collectives,
  the brics/nccl module, NCCL environment variables (NCCL_NET, NCCL_SOCKET_IFNAME,
  FI_CXI_* variables), building NCCL or aws-ofi-nccl from source, benchmarking NCCL
  with nccl-tests, NCCL in containers (Apptainer/Singularity), or diagnosing slow
  multi-node GPU bandwidth on Isambard-AI.
  Also trigger for questions about GPUDirect RDMA on Slingshot, distributed training
  performance, or getting full interconnect bandwidth for GPU collective operations —
  even if the user doesn't explicitly say "NCCL".
  Note: NCCL is only supported on Isambard-AI Phase 1 and Phase 2 — not Isambard 3.
compatibility: >
  Isambard-AI only. Requires access to an Isambard-AI login node, GPU compute
  resources, and the brics/nccl module.
metadata:
  author: isambard-sc
  version: "1.0"
  source_url: https://docs.isambard.ac.uk/user-documentation/guides/nccl/
---

# NCCL on Isambard

NCCL (NVIDIA Collective Communications Library) provides direct GPU-to-GPU communication
for collective operations (all-reduce, broadcast, etc.). On Isambard-AI it uses **RDMA via
GPUDirect** over the **Slingshot 11** high-speed network.

> **Supported systems:** Isambard-AI Phase 1 ✓ and Phase 2 ✓ only.
> Isambard 3 does not support NCCL (no GPUs).

The critical component is the **`aws-ofi-nccl`** network plugin, which bridges NCCL to
`libfabric` and enables RDMA on Slingshot. Without it, NCCL falls back to TCP sockets
and bandwidth collapses — from ~163 GB/s to ~2.3 GB/s on an 8-GPU all-reduce.

---

## The Fast Path: `brics/nccl` Module

For most workloads, simply load the BriCS-provided module:

```bash
module load brics/nccl
```

This provides a system-built NCCL and `aws-ofi-nccl`, pre-configured for Slingshot 11,
and sets all required environment variables automatically.

Use this unless you need a specific NCCL version, are building for a container with a
different CUDA runtime, or are doing application-specific tuning.

---

## Environment Variables

The `brics/nccl` module sets these automatically. You only need to set them manually
if building your own NCCL or tuning for a specific application.

### Core NCCL variables

```bash
export NCCL_NET="AWS Libfabric"    # Force use of aws-ofi-nccl plugin (required)
export NCCL_SOCKET_IFNAME="hsn"    # Use the high-speed Slingshot NIC
export NCCL_DEBUG="VERSION"        # Print NCCL version at startup (use INFO to debug)
export NCCL_NET_GDR_LEVEL="PHB"   # P2P when GPUs share the same NUMA node
export NCCL_CROSS_NIC="1"         # Allow rings/trees to span multiple NICs
export NCCL_MIN_NCHANNELS="4"     # Minimum communication channels (app-dependent)
export NCCL_GDRCOPY_ENABLE="1"
export NCCL_NET_FORCE_FLUSH="0"
```

### libfabric (FI) tuning for Slingshot

```bash
export FI_CXI_DEFAULT_CQ_SIZE="131072"       # App-dependent
export FI_CXI_DEFAULT_TX_SIZE="2048"         # App-dependent
export FI_CXI_DISABLE_NON_INJECT_MSG_IDC="1"
export FI_HMEM_CUDA_USE_GDRCOPY="1"
export FI_CXI_DISABLE_HOST_REGISTER="1"
export FI_MR_CACHE_MONITOR="userfaultfd"
export FI_CXI_RDZV_PROTO="alt_read"
export FI_CXI_RDZV_THRESHOLD="0"
export FI_CXI_RDZV_GET_MIN="0"
export FI_CXI_RDZV_EAGER_SIZE="0"
export FI_CXI_RX_MATCH_MODE="hybrid"
```

A downloadable copy is available at:
`https://docs.isambard.ac.uk/user-documentation/guides/example-data/nccl/env_vars.sh`

> **Application-dependent variables:** `NCCL_MIN_NCHANNELS`, `FI_CXI_DEFAULT_CQ_SIZE`,
> and `FI_CXI_DEFAULT_TX_SIZE` may need tuning per workload. The defaults optimise for
> a broad range of scenarios. See the
> [NCCL environment variable docs](https://docs.nvidia.com/deeplearning/nccl/user-guide/docs/env.html)
> for details.

**Debugging:** Set `NCCL_DEBUG=INFO` for verbose logs. If you see:
```
NCCL WARN Error: network AWS Libfabric not found.
```
the `aws-ofi-nccl` plugin is not on `LD_LIBRARY_PATH` or was not built correctly.

---

## Performance Benchmark: What to Expect

Using `nccl-tests` all_reduce across 2 nodes (8 × GH200 GPUs), 8 GB payload:

| Configuration | Bus Bandwidth |
|---------------|--------------|
| Without `aws-ofi-nccl` (TCP fallback) | ~2.3 GB/s |
| With `aws-ofi-nccl` + Slingshot RDMA | ~163 GB/s |

The difference is ~70×. Always verify RDMA is active before running production workloads.

---

## Topology Inspection

To check which Slingshot NIC is paired with which GPU:

```bash
# Dump NCCL topology to a file
export NCCL_TOPO_DUMP_FILE=topo.txt

# List NICs
cxi_stat

# List GPUs
nvidia-smi -L
```

---

## Building NCCL and nccl-tests from Source (bare-metal)

See **`references/build.md`** for step-by-step instructions covering:
- Building NCCL from source
- Building the `aws-ofi-nccl` plugin
- Building and running `nccl-tests` to benchmark bandwidth

Read this file when the user needs a custom NCCL version on the host system.

---

## NCCL in Containers

See **`references/containers.md`** for:
- Using the host NCCL via `brics/apptainer-multi-node` (simplest)
- Building NCCL and `aws-ofi-nccl` inside an Apptainer container against a container's
  own CUDA runtime (e.g. an NGC PyTorch image requiring a newer CUDA than the host)
- The full Apptainer definition file and Slurm build/benchmark job scripts

Read this file when the user is running containerised GPU workloads across multiple nodes.

---

## Quick Reference

| Goal | Action |
|------|--------|
| Use system NCCL (recommended) | `module load brics/nccl` |
| Use NCCL in Apptainer (host libs) | `module load brics/apptainer-multi-node` |
| Diagnose missing plugin | Check `NCCL_DEBUG=INFO`; look for `AWS Libfabric not found` |
| Diagnose low bandwidth | Confirm `aws-ofi-nccl` on `LD_LIBRARY_PATH`; source env vars |
| Inspect GPU–NIC topology | `NCCL_TOPO_DUMP_FILE=topo.txt`, `cxi_stat`, `nvidia-smi -L` |
| Benchmark bandwidth | Build `nccl-tests`; see `references/build.md` |
| Custom NCCL build | See `references/build.md` |
| NCCL in a custom container | See `references/containers.md` |

---

## Related Resources

- [Official NCCL documentation](https://docs.nvidia.com/deeplearning/nccl/user-guide/docs/index.html)
- [NCCL environment variable reference](https://docs.nvidia.com/deeplearning/nccl/user-guide/docs/env.html)
- [aws-ofi-nccl on GitHub](https://github.com/aws/aws-ofi-nccl)
- [Isambard MPI guide](https://docs.isambard.ac.uk/user-documentation/guides/mpi/)
- [Isambard Containers guide](https://docs.isambard.ac.uk/user-documentation/guides/containers/)
- [Isambard Apptainer Multi-node guide](https://docs.isambard.ac.uk/user-documentation/guides/containers/apptainer-multi-node/)
