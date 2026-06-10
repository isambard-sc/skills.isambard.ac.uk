---
name: containers
description: >
  Guide for using containers on Isambard AI (BriCS) supercomputers with Podman-HPC and
  Apptainer (formerly Singularity). Use this skill whenever a user asks about running
  containers on Isambard, using podman-hpc or apptainer/singularity, pulling or building
  container images, running containers on compute nodes or across multiple nodes with MPI
  or NCCL, GPU access inside containers, squashfs image migration, the brics/nccl or
  brics/apptainer-multi-node modules, using NGC (Nvidia GPU Cloud) containers on Isambard,
  or getting full Slingshot 11 interconnect bandwidth from containerised workloads.
  Also trigger for questions about aarch64-compatible container images, --fakeroot builds,
  the /host/adapt.sh entrypoint, or any container-related workflow on an HPE Cray system.
compatibility: >
  Isambard-AI and Isambard 3. Requires access to an Isambard login node and the
  Podman-HPC or Apptainer runtime.
metadata:
  author: isambard-sc
  version: "1.0"
  source_url: https://docs.isambard.ac.uk/user-documentation/guides/containers/
---

# Containers on Isambard

Two container engines are available on Isambard-AI and Isambard 3:

| Engine | Command | Best for |
|--------|---------|----------|
| **Podman-HPC** | `podman-hpc` | OCI/Docker-style workflows; building custom images on-system |
| **Apptainer** | `apptainer` (AIP2) / `singularity` (Isambard 3) | SIF-based HPC workflows; rootless builds from definition files |

Both engines support single-node and multi-node operation. Multi-node jobs require extra setup to use the **Slingshot 11** high-speed interconnect — skip this at the cost of severely degraded bandwidth.

> **aarch64 images only.** Isambard uses Arm64 (`aarch64`). Only images built for this architecture
> will run. When browsing registries like [NGC](https://catalog.ngc.nvidia.com/orgs/nvidia/containers/pytorch/tags),
> filter tags by `linux/arm64` before pulling.

## Critical Rules

- Only use container images built for `linux/arm64` on Isambard.
- Never run x86 or `amd64` images on Isambard compute nodes.
- Multi-node container jobs must use the host MPI/NCCL libraries and `/host/adapt.sh`.
- Use `--nv` for GPU containers in Apptainer and `--device=nvidia.com/gpu=all` or
  `--gpu` for Podman-HPC.
- Do not rely on non-shared local image stores on compute nodes; use shared filesystem paths
  or container migration tools.

---

## Multi-node Networking Overview

To achieve full Slingshot 11 performance, the host's MPI and NCCL libraries must be visible inside the container. Both engines handle this by mounting them under `/host/` and adjusting `PATH` and `LD_LIBRARY_PATH` via an entrypoint script `/host/adapt.sh`.

- **CPU workloads (MPI only):** Use host MPI via `/host/openmpi`
- **GPU workloads (MPI + NCCL):** Use both; build against `NCCL_HOME=/host/nccl MPI_HOME=/host/openmpi`

The mechanism differs between engines — see the reference files below.

---

## Which engine should I use?

Choose **Podman-HPC** if you:
- Are pulling OCI/Docker images and want them ready to run immediately
- Want to build images directly on the system (Containerfile/Dockerfile)
- Are running NGC containers for GPU workloads (use `--openmpi-pmi2` flag)

Choose **Apptainer** if you:
- Already use Singularity/Apptainer workflows
- Need to build custom images from definition files with root-like privileges (`--fakeroot`)
- Are on Isambard 3 (where `singularity` is the installed command)

---

## Podman-HPC Reference

See **`references/podman-hpc.md`** for full detail on:
- Pulling, building, and pushing images
- Migrating images to `$SCRATCH` for use on compute nodes
- Running containers with GPUs
- Multi-node usage with `--openmpi-pmi2` and `nccl-tests` example

Read this file when helping with any Podman-HPC task.

---

## Apptainer Reference

See **`references/apptainer.md`** for full detail on:
- Building SIF images from Docker Hub and other registries
- Running containers with `apptainer run`, `exec`, and `shell`
- GPU access with `--nv`
- Rootless builds with `--fakeroot`
- Multi-node usage with `brics/apptainer-multi-node` module and `nccl-tests` example

Read this file when helping with any Apptainer/Singularity task.

---

## Quick Reference

| Task | Podman-HPC | Apptainer |
|------|-----------|-----------|
| Pull image | `podman-hpc pull <image>` | `apptainer build img.sif docker://<image>` |
| Run image | `podman-hpc run <image>` | `apptainer run img.sif` |
| Run command | `podman-hpc run <image> <cmd>` | `apptainer exec img.sif <cmd>` |
| Interactive shell | `podman-hpc run -it <image> bash` | `apptainer shell img.sif` |
| GPU access | `--device=nvidia.com/gpu=all` or `--gpu` | `--nv` |
| Build from file | `podman-hpc build . --tag <name>` | `apptainer build img.sif def.def` |
| Rootless/fakeroot build | N/A | `apptainer build --fakeroot img.sif def.def` |
| Make available on compute nodes | `podman-hpc migrate <image>` | Images (`.sif`) are files on shared FS already |
| Multi-node setup | `--openmpi-pmi2` flag | `module load brics/apptainer-multi-node` + `source /host/adapt.sh` |
| Slurm MPI interface | `--mpi=pmi2` | standard `srun` |

---

## Related Resources

- [Isambard MPI guide](https://docs.isambard.ac.uk/user-documentation/guides/mpi/)
- [Isambard NCCL guide](https://docs.isambard.ac.uk/user-documentation/guides/nccl/)
- [System storage docs](https://docs.isambard.ac.uk/user-documentation/information/system-storage/)
- [NGC container registry](https://catalog.ngc.nvidia.com/containers)
- [NERSC Podman-HPC tutorial](https://docs.nersc.gov/development/containers/podman-hpc/podman-beginner-tutorial/)
- [Apptainer documentation](https://apptainer.org/docs/user/main/)
