---
name: modules
description: >
  Guide for using the modules system, programming environments, compilers, and profiling tools
  on Isambard AI (BriCS) supercomputers (Isambard-AI and Isambard 3).
  Use this skill whenever a user asks about loading modules on Isambard, the Cray Programming
  Environment (PrgEnv-gnu, PrgEnv-cray), compiler wrappers (cc, CC, ftn), GCC or NVIDIA
  compilers, compiler flags for Arm/Grace (neoverse-v2), BriCS-supplied modules (brics/nccl,
  brics/tmux, etc.), profiling with gprof, Cray perftools, or Nvidia Nsight Systems.
  Also trigger for questions about linking MPI or scientific libraries on Isambard, or
  troubleshooting compiler and build issues on the Cray HPE system — even if the user
  doesn't explicitly say "modules".
compatibility: >
  Isambard-AI and Isambard 3. Requires access to an Isambard login node and the
  Cray Programming Environment module system.
metadata:
  author: isambard-sc
  version: "1.0"
  source_url: https://docs.isambard.ac.uk/user-documentation/guides/modules/
---

# Modules and Compilers on Isambard

Both Isambard-AI and Isambard 3 are HPE/Cray systems and use the **Cray Programming Environment** for managing compilers, MPI, and scientific libraries through a modular software system.

---

## Module Commands

| Command | Effect |
|---------|--------|
| `module avail` | List all available modules |
| `module load <name>` | Load a module into the current session |
| `module unload <name>` | Unload a module from the current session |
| `module list` | List all currently loaded modules |
| `module purge` | Unload all loaded modules |
| `module spider <name>` | Search for a module and show details |

---

## BriCS-Supplied Modules

BriCS provides the following utility modules (available on AIP1, AIP2, and Isambard 3 unless noted):

| Module | Description |
|--------|-------------|
| `brics/default` | Default user environment (loaded automatically) |
| `brics/userenv` | Sets `$LOCALDIR`, `$SCRATCHDIR`, and `$TMPDIR` — see the [storage docs](https://docs.isambard.ac.uk/user-documentation/information/system-storage/) |
| `brics/emacs` | Emacs text editor |
| `brics/nano` | nano text editor |
| `brics/tmux` | tmux terminal multiplexer — reload the module when restarting a terminal; sessions persist |
| `brics/nccl` | **Required for multi-node GPU workflows.** Provides NCCL (built against `libfabric`) and the NCCL AWS-OFI plugin for Slingshot high-speed network support |
| `brics/apptainer-multi-node` | Support for multi-node Apptainer jobs — see the [Apptainer multi-node docs](https://docs.isambard.ac.uk/user-documentation/guides/containers/apptainer-multi-node/) |

---

## Programming Environments

### Available environments

```bash
module av PrgEnv           # quick list
module spider PrgEnv       # detailed view
```

```
PrgEnv-cray/8.5.0    PrgEnv-gnu/8.5.0
```

**`PrgEnv-gnu` is recommended** — good performance, familiar behaviour, all dependencies loaded automatically:

```bash
module load PrgEnv-gnu
module list
# Loads: brics/userenv, brics/default, gcc-native/13.2, craype, craype-arm-grace,
#        libfabric, craype-network-ofi, cray-libsci, cray-mpich, PrgEnv-gnu
```

Key components loaded by `PrgEnv-gnu`:

| Module | Purpose |
|--------|---------|
| `gcc-native/13.2` | GCC 13.2 compiler suite |
| `libfabric` | Communication library for Slingshot 11 high-speed interconnect |
| `cray-libsci` | Scientific and math libraries (BLAS, LAPACK, etc.) |
| `cray-mpich` | MPI libraries |

### Cray compiler wrappers

With a `PrgEnv` loaded, use the **Cray compiler wrappers** rather than invoking GCC directly:

| Wrapper | Language | GCC equivalent |
|---------|----------|----------------|
| `cc` | C | `gcc` |
| `CC` | C++ | `g++` |
| `ftn` | Fortran | `gfortran` |

The wrappers automatically link to loaded Cray PE libraries (MPI, LibSci, etc.). Do not mix wrapper commands and raw GCC commands in the same build.

To see exactly what the wrapper passes to the underlying compiler:

```bash
ftn -craype-verbose -o hello hello.f90
# Shows full flags, include paths, and linked libraries
```

---

## Compiler Options

### Targeting the NVIDIA Grace Superchip (Arm Neoverse V2)

Use `-mcpu=neoverse-v2` to target the Grace CPU architecture. Note this differs from x86 (`-march`):

```bash
cc -mcpu=neoverse-v2 -O3 mycode.c -o mycode
```

For further tuning guidance see the [NVIDIA Grace Performance Tuning Guide](https://docs.nvidia.com/grace-perf-tuning-guide/index.html).

---

## NVIDIA Compilers

Load just the NVIDIA compiler suite (without a full programming environment):

```bash
module load nvidia
nvc --version      # C
nvc++ --version    # C++
nvfortran --version
# All target: linuxarm64, aarch64, neoverse-v2
```

> **Note:** Loading only `module load nvidia` does **not** load MPI libraries automatically. For MPI, load a full `PrgEnv` instead, or see the [MPI guide](https://docs.isambard.ac.uk/user-documentation/guides/mpi/).

---

## Profiling Tools

### gprof

Available without loading any modules:

```bash
gprof ./a.out
```

### Cray Perftools

```bash
module load perftools-base
pat_run ./a.out
```

Full docs: [HPE Cray Performance Tools](https://cpe.ext.hpe.com/docs/latest/performance-tools/index.html)

### NVIDIA Nsight Systems

```bash
module load cudatoolkit
nsys profile ./a.out
```

Full docs: [NVIDIA Nsight Systems User Guide](https://docs.nvidia.com/nsight-systems/UserGuide/index.html)

---

## Quick Reference

| Goal | Command |
|------|---------|
| Recommended build environment | `module load PrgEnv-gnu` |
| Compile C | `cc -mcpu=neoverse-v2 -O3 myfile.c` |
| Compile C++ | `CC -mcpu=neoverse-v2 -O3 myfile.cpp` |
| Compile Fortran | `ftn -mcpu=neoverse-v2 -O3 myfile.f90` |
| Debug wrapper flags | `cc -craype-verbose ...` |
| Multi-node GPU jobs | `module load brics/nccl` |
| Profile with Cray tools | `module load perftools-base` → `pat_run` |
| Profile with NVIDIA tools | `module load cudatoolkit` → `nsys` |
| Spack builds | See [Spack guide](https://docs.isambard.ac.uk/user-documentation/guides/spack/) for compiler config |

---

## Related Resources

- [Isambard MPI guide](https://docs.isambard.ac.uk/user-documentation/guides/mpi/)
- [Isambard Spack guide](https://docs.isambard.ac.uk/user-documentation/guides/spack/)
- [Cray Programming Environment docs](https://cpe.ext.hpe.com/docs/latest)
- [NVIDIA Grace Performance Tuning Guide](https://docs.nvidia.com/grace-perf-tuning-guide/index.html)
