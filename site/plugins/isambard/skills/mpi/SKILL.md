---
name: mpi
description: >
  Guide for using MPI on Isambard AI (BriCS) supercomputers (Isambard-AI and Isambard 3).
  Use this skill whenever a user asks about MPI on Isambard, running multi-node MPI jobs,
  Cray MPICH, cray-mpich, PrgEnv-gnu or PrgEnv-cray for MPI, the PMI or PMIx process
  manager interface, srun --mpi flags (cray_shasta, pmi2, pmix), installing OpenMPI or
  MPICH with conda or from source, mpi4py on Isambard, libfabric and Slingshot 11 MPI
  performance, or why mpirun and mpiexec should not be used on Isambard.
  Also trigger for questions about linking MPI libraries, compiler wrappers with MPI
  (mpicc, mpicxx, mpif90), or any multi-node communication setup on an HPE Cray system.
compatibility: >
  Isambard-AI and Isambard 3. Requires access to an Isambard login node and the
  Cray MPI environment.
metadata:
  author: isambard-sc
  version: "1.0"
  source_url: https://docs.isambard.ac.uk/user-documentation/guides/mpi/
---

# MPI on Isambard

MPI (Message Passing Interface) enables parallel communication across compute nodes. On
Isambard-AI and Isambard 3, MPI must communicate with the **Slingshot 11 (SS11)**
high-speed interconnect via `libfabric` to achieve optimal latency and bandwidth.

```
MPI application → libfabric → Slingshot 11 NIC → network
```

> **Never use `mpirun` or `mpiexec`.** Always launch MPI applications with `srun` so
> you can supply the correct `--mpi` flag for the PMI type. Using `mpirun`/`mpiexec`
> bypasses Slurm's process management and will not work correctly.

## Critical Rules

- Always start MPI jobs with `srun` on Isambard.
- Never use `mpirun` or `mpiexec` on Isambard.
- Always choose the `--mpi` value that matches the MPI implementation in use.
- Load MPI through a Cray `PrgEnv` or a Conda/MPI build that is explicitly configured
  for Slingshot 11.
- Do not mix raw GCC invocations with Cray compiler wrappers in the same build.

---

## Default MPI: Cray MPICH

The recommended MPI is **Cray MPICH**, provided by the `cray-mpich` module. It is loaded
automatically with any Cray Programming Environment:

```bash
module load PrgEnv-gnu    # recommended
# or
module load PrgEnv-cray
```

After loading, verify the MPI link flags:

```bash
# With PrgEnv-gnu
mpicc -show
# gcc -I/opt/cray/pe/mpich/.../ofi/gnu/12.3/include -L.../lib -lmpi_gnu_123

# With PrgEnv-cray
mpicc -show
# craycc -I/opt/cray/pe/mpich/.../ofi/cray/17.0/include -L.../lib -lmpi_cray
```

The `-lmpi_gnu_*` or `-lmpi_cray` library is the Cray MPICH build tuned for Slingshot.

> **aarch64 known issues:** Cray MPICH support for aarch64 was recently added and some
> environment variable workarounds may be needed. Check the
> [Known Issues page](https://docs.isambard.ac.uk/service-status/known_issues/) for
> current advice before running.

---

## PMI — Process Manager Interface

MPI processes need a Process Manager Interface (PMI) to coordinate ranks across nodes
through Slurm. The correct `--mpi` flag to `srun` depends on which MPI library is in use.

List available PMI types on the system:

```bash
srun --mpi=list
# cray_shasta
# none
# pmi2
# pmix  (pmix_v4)
```

### Choosing the right `--mpi` flag

| MPI library | `--mpi` flag | Notes |
|-------------|-------------|-------|
| Cray MPICH (default) | `cray_shasta` | Default; usually works without specifying |
| OpenMPI ≤ 4.x | `pmi2` | Required for older OpenMPI |
| OpenMPI ≥ 5.0 | `pmix` | Required for modern OpenMPI |

```bash
# Cray MPICH (cray_shasta is the default, but explicit is clearer)
srun --mpi=cray_shasta ./mpi_app

# OpenMPI ≤ 4.x
srun --mpi=pmi2 ./mpi_app

# OpenMPI ≥ 5.0
srun --mpi=pmix ./mpi_app
```

> If you do not need to specify a custom PMI and are using Cray MPICH, `srun` without
> `--mpi` will use `cray_shasta` by default.

---

## Installing a Different MPI Version

The system Cray MPICH is recommended for performance. If you need a different version
(e.g. for software that requires OpenMPI), you have two options.

### Option 1: Conda (easiest)

See the [Python/Conda guide](https://docs.isambard.ac.uk/user-documentation/guides/python/)
to set up Miniforge first, then:

```bash
# MPICH via conda-forge
conda install -c conda-forge mpich

# OpenMPI via conda-forge
conda install -c conda-forge openmpi
```

> **Note:** Conda-installed MPI will not use the Slingshot 11 interconnect and will have
> lower multi-node performance than Cray MPICH. Use only when necessary for software
> compatibility.

### Option 2: Build OpenMPI from source

For maximum control or when Slingshot integration is needed with OpenMPI:

- [OpenMPI v5 build instructions](https://docs.open-mpi.org/en/v5.0.x/installing-open-mpi/quickstart.html#building-from-source)
- [Legacy OpenMPI (≤4.x) build instructions](https://www-lb.open-mpi.org/faq/?category=building#easy-build)

### mpi4py

For Python MPI, see the [Python guide](https://docs.isambard.ac.uk/user-documentation/guides/python/)
— specifically the section on building `mpi4py` from source against the Cray MPI stack
using `module load PrgEnv-gnu` and `pip install --no-binary mpi4py mpi4py`.

---

## Quick Reference

| Goal | Command / setting |
|------|------------------|
| Load default MPI (recommended) | `module load PrgEnv-gnu` |
| Check MPI link flags | `mpicc -show` |
| Run an MPI job (Cray MPICH) | `srun --mpi=cray_shasta ./mpi_app` |
| Run an MPI job (OpenMPI ≤4) | `srun --mpi=pmi2 ./mpi_app` |
| Run an MPI job (OpenMPI ≥5) | `srun --mpi=pmix ./mpi_app` |
| List available PMI types | `srun --mpi=list` |
| Install OpenMPI via conda | `conda install -c conda-forge openmpi` |
| Install MPICH via conda | `conda install -c conda-forge mpich` |
| Install mpi4py (source, Slingshot-aware) | `module load PrgEnv-gnu` + `pip install --no-binary mpi4py mpi4py` |
| MPI in containers (Podman-HPC) | `--openmpi-pmi2` flag + `srun --mpi=pmi2` |
| MPI in containers (Apptainer) | `module load brics/apptainer-multi-node` + `source /host/adapt.sh` |

---

## Related Resources

- [Isambard Known Issues](https://docs.isambard.ac.uk/service-status/known_issues/) — check for current Cray MPICH aarch64 workarounds
- [Isambard Modules and Compilers guide](https://docs.isambard.ac.uk/user-documentation/guides/modules/)
- [Isambard NCCL guide](https://docs.isambard.ac.uk/user-documentation/guides/nccl/)
- [Isambard Containers guide](https://docs.isambard.ac.uk/user-documentation/guides/containers/)
- [Cray Programming Environment docs](https://cpe.ext.hpe.com/docs/latest)
- [Argonne PMI2 paper](https://www.mcs.anl.gov/papers/P1760.pdf)
