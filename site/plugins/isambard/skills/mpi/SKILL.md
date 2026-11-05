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
license: CC-BY-SA-4.0. Markdown/image content derived from https://docs.isambard.ac.uk/, © Bristol Centre for Supercomputing (BriCS).
compatibility: >
  Isambard-AI and Isambard 3. Requires access to an Isambard login node and the
  Cray MPI environment.
metadata:
  author: isambard-sc
  version: "1.1"
  source_url: https://docs.isambard.ac.uk/user-documentation/guides/mpi/
  supplementary_urls:
    - https://docs.isambard.ac.uk/user-documentation/guides/python-advanced/
    - https://docs.isambard.ac.uk/user-documentation/guides/modules/
  docs_commit: e994565
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
> bypasses Slurm's process management and will not work correctly. The only
> documented exception is conda-forge OpenMPI, an unsupported configuration — see
> [Option 3: OpenMPI from conda-forge](#option-3-openmpi-from-conda-forge-unsupported).

## Critical Rules

- Always start MPI jobs with `srun` on Isambard.
- Never use `mpirun` or `mpiexec` on Isambard. Exception: conda-forge OpenMPI cannot
  be launched with `srun` and must use its own `mpirun` — this is not a supported
  configuration; steer users to the MPICH options first.
- Never use a plain conda-forge `mpich` or `openmpi` install for multi-node jobs —
  each rank forms its own single-rank MPI world and the job silently fails to
  communicate.
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

> **aarch64 known issues:** Cray MPICH support for aarch64 was recently added. If you
> hit MPICH problems, check the
> [Known Issues page](https://docs.isambard.ac.uk/service-status/known_issues/) for
> any current advice on environment variables.

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

The system Cray MPICH is recommended for performance. You may build your own MPI from
source, or use conda (set up Miniforge first — see the
[Python/Conda guide](https://docs.isambard.ac.uk/user-documentation/guides/python/)).

> **A plain conda MPI install will not run across multiple nodes.** Installing `mpich`
> or `openmpi` directly from conda-forge (e.g.
> `conda install --channel conda-forge mpich`) brings a self-contained MPI runtime that
> does not know about Slurm or Slingshot. Launched with `srun` across nodes, every
> process starts its own single-rank MPI world. Use one of the approaches below.

Recommend these conda approaches in this order (`mpi4py` is used as the example; the
same ideas apply to any conda-installed MPI application):

1. **MPICH external build** (recommended) — simplest correct option, good performance.
2. **`mpi4py` built from source against Cray MPICH** — best performance; use for
   production MPI workloads.
3. **OpenMPI from conda-forge** — only if the application requires OpenMPI; not a
   supported configuration on Isambard.

### Test program

Use this `mpi_hello.py` to confirm every rank joins one MPI world spanning all nodes:

```python
#!/usr/bin/env python3
"""Check that mpi4py forms a single MPI world spanning every rank and node."""

from collections import Counter
import socket
import sys

from mpi4py import MPI

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()
host = socket.gethostname()

total = comm.allreduce(1, op=MPI.SUM)
hosts = comm.gather(host, root=0)

if rank != 0:
    sys.exit(0)

ranks_per_host = Counter(hosts)
print(f"MPI library: {MPI.Get_library_version().splitlines()[0]}")
print(f"world size: {size}")
print(f"allreduce sum: {total} (expected {size})")
print(f"nodes in world: {len(ranks_per_host)}")
for name, count in sorted(ranks_per_host.items()):
    print(f"  {name}: {count} ranks")

if size > 1 and total == size:
    print("RESULT: PASS - one MPI world spans every rank")
    sys.exit(0)

print("RESULT: FAIL - ranks did not join a single MPI world")
sys.exit(1)
```

A working multi-node launch prints `RESULT: PASS`. A broken setup makes every process
report `world size: 1` and `RESULT: FAIL`.

### Option 1: MPICH external build (recommended)

conda-forge publishes *external* MPICH builds that contain no MPI runtime and bind to
the system MPICH at run time. Cray MPICH is MPICH ABI-compatible, so the environment
uses Cray MPICH and the Slingshot interconnect while `mpi4py` comes from conda.

```bash
conda create --name mpi4py-mpich \
    --channel conda-forge/label/mpi-external \
    --channel conda-forge \
    mpi4py "mpich=*=external_*"
```

Job script:

```bash
#!/usr/bin/env bash
#SBATCH --job-name=mpi4py-mpich
#SBATCH --nodes=2
#SBATCH --ntasks-per-node=4
#SBATCH --cpus-per-task=1
#SBATCH --time=00:01:00
#SBATCH --output=mpi4py-mpich-%j.out

set -euo pipefail

module reset
module load PrgEnv-gnu

# adjust this line to where your conda is located
source ~/miniforge3/bin/activate
conda activate mpi4py-mpich

# Load the vendor Cray MPICH runtime in place of the conda placeholder
export LD_LIBRARY_PATH="${MPICH_DIR}/lib-abi-mpich:${LD_LIBRARY_PATH:-}"

srun --ntasks 8 --ntasks-per-node 4 --cpus-per-task 1 --cpu-bind cores \
    python mpi_hello.py
```

This uses Slingshot correctly but is not as well optimised as an MPI built for the
system. For production workloads where MPI performance matters, use Option 2.

### Option 2: Build `mpi4py` from source against Cray MPICH

Build with the Cray compiler wrapper `cc`, which links Cray MPICH, libfabric, and the
Slingshot libraries directly:

```bash
module reset
module load PrgEnv-gnu

conda create --name mpi4py-source python pip
conda activate mpi4py-source

MPICC="cc -shared" python -m pip install \
    --force-reinstall --no-cache-dir --no-binary mpi4py mpi4py
```

Submit with the same job script as Option 1 (activating `mpi4py-source`), but **omit
the `LD_LIBRARY_PATH` line** — the build is already linked against the Cray libraries.
Keep `module reset` and `module load PrgEnv-gnu` in the job script.

For CUDA-aware `mpi4py` on Isambard-AI, additional CUDA modules and build flags are
needed.

### Option 3: OpenMPI from conda-forge (unsupported)

> **Not a supported configuration on Isambard.** Running conda OpenMPI with `srun`
> does not work correctly, the launcher flags are complex and error-prone, and testing
> could not confirm it uses the Slingshot interconnect. Use only if the application
> specifically requires OpenMPI and a source build is not possible.

```bash
conda create --name mpi4py-openmpi --channel conda-forge mpi4py openmpi
```

This is the one case where `mpirun` is used: launch with OpenMPI's own `mpirun`,
telling it to use Slurm for resource allocation and process launch. Do **not** load
the Cray programming environment:

```bash
#!/usr/bin/env bash
#SBATCH --job-name=mpi4py-openmpi
#SBATCH --nodes=2
#SBATCH --ntasks-per-node=4
#SBATCH --cpus-per-task=1
#SBATCH --time=00:01:00
#SBATCH --output=mpi4py-openmpi-%j.out

set -euo pipefail

module reset

# adjust this line to where your conda is located
source ~/miniforge3/bin/activate
conda activate mpi4py-openmpi

mpirun --prtemca ras slurm --prtemca plm slurm \
    --np 8 --map-by ppr:4:node:PE=1 --bind-to core \
    python mpi_hello.py
```

### Building OpenMPI from source

- [OpenMPI v5 build instructions](https://docs.open-mpi.org/en/v5.0.x/installing-open-mpi/quickstart.html#building-from-source)
- [Legacy OpenMPI (≤4.x) build instructions](https://www-lb.open-mpi.org/faq/?category=building#easy-build)

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
| Conda MPI (recommended) | `conda create ... --channel conda-forge/label/mpi-external ... mpi4py "mpich=*=external_*"` + `LD_LIBRARY_PATH=${MPICH_DIR}/lib-abi-mpich:...` |
| mpi4py from source (best performance) | `module load PrgEnv-gnu` + `MPICC="cc -shared" python -m pip install --force-reinstall --no-cache-dir --no-binary mpi4py mpi4py` |
| Conda OpenMPI (unsupported) | `mpirun --prtemca ras slurm --prtemca plm slurm ...` (not `srun`) |
| MPI in containers (Podman-HPC) | `--openmpi-pmi2` flag + `srun --mpi=pmi2` |
| MPI in containers (Apptainer) | `module load brics/apptainer-multi-node` + `source /host/adapt.sh` |

---

## Related Resources

- [Isambard Known Issues](https://docs.isambard.ac.uk/service-status/known_issues/)
- [Isambard Advanced Python guide](https://docs.isambard.ac.uk/user-documentation/guides/python-advanced/) — conda and `mpi4py`
- [Isambard Modules and Compilers guide](https://docs.isambard.ac.uk/user-documentation/guides/modules/)
- [Isambard NCCL guide](https://docs.isambard.ac.uk/user-documentation/guides/nccl/)
- [Isambard Containers guide](https://docs.isambard.ac.uk/user-documentation/guides/containers/)
- [Cray Programming Environment docs](https://cpe.ext.hpe.com/docs/latest)
- [Argonne PMI2 paper](https://www.mcs.anl.gov/papers/P1760.pdf)
