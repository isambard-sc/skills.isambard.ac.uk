<!-- Snapshot of https://docs.isambard.ac.uk/user-documentation/guides/modules/ made by snapshot_docs.py. Do not edit. -->

# Modules and Compilers

## Modules

A modular software environment is available on Isambard-AI and Isambard 3. Here is a list of common module commands:

-
`module avail`
Shows the modules available on the system

-
`module load`
Load a module into your current session

-
`module unload`
Unload a module from your current session

-
`module list`
List all the modules loaded in your current session

-
`module purge`
Unload all the modules from your current session

## BriCS-supplied Modules

BriCS provide the following modules to help the user's experience:

| Module Name | Description | Default | AIP1 | AIP2 | Isambard 3 |
| `brics/default` | Default module for the user environment. | | | | |
| `brics/userenv` | Sets `$LOCALDIR`, `$SCRATCHDIR`, and `$TMPDIR`. See the system storage page for more information. | | | | |
| `brics/emacs` | Provides the Emacs text editor. | | | | |
| `brics/nano` | Provides the nano text editor. | | | | |
| `brics/tmux` | Provides the tmux terminal multiplexer. Please ensure you reload the module when restarting your terminal and your sessions will persist. | | | | |
| `brics/nccl` | This module is required for multi-node GPU workflows. This provides both NCCL (compiled against `libfabric`) and the NCCL AWS-OFI plugin to support the high speed network (Slingshot). | | | | |
| `brics/apptainer-multi-node` | This module provides support for multi-node apptainer jobs. Please read the apptainer Multi-node documentation. | | | | |

## Arm Performance Libraries (Arm PL) on Isambard 3

Arm Performance Libraries (Arm PL) are available on Isambard 3 at `/opt/arm/`. They provide optimised numerical routines for AArch64 systems. This documentation is intentionally minimal and focuses on signposting relevant components and upstream resources. For more information visit the Arm Performance Libraries math functions documentation.

Arm PL provides the `libamath` library, which includes:

- An optimised subset of standard `math.h` functions
- Scalar implementations (compatible with `libm` naming)
- Vectorised implementations

To use these functions in C/C++ code:

```
#include <amath.h>

```

## Programming environments

Both Isambard-AI and Isambard 3 are from HPE/Cray and therefore use Cray Programming Environments.

To see available programming environments perform a `module av PrgEnv` or for more detail `module spider PrgEnv`.

```
$ module av PrgEnv
---------------------- /opt/cray/pe/lmod/modulefiles/core ----------------------
   PrgEnv-cray/8.5.0    PrgEnv-gnu/8.5.0

```

The recommended programming environment is `PrgEnv-gnu`. This should provide moderately good performance and users are more likely to be familiar with its behaviour. It consists of a suite of libraries and packages which have been built with the GNU compiler (i.e. `gcc`).

Loading a programming environment brings in all dependencies automatically, e.g.

```
user.project@login02:~> module load PrgEnv-gnu
user.project@login02:~> module list

  Currently Loaded Modules:
    1) brics/userenv/2.4   5) craype-arm-grace      9) cray-mpich/8.1.30
    2) brics/default/1.0   6) libfabric/1.22.0     10) PrgEnv-gnu/8.5.0
    3) gcc-native/13.2     7) craype-network-ofi
    4) craype/2.7.32       8) cray-libsci/24.07.0

```

The version of `gcc` used in the environment can be seen in the `gcc-native` modules (i.e. 13.2). `libfabric` is the communication library for the high-speed interconnect (Slingshot 11). `cray-libsci` is a library of common scientific packages (LAPACK, BLAS etc). `cray-mpich` provides the MPI libraries.

The Cray Programming Environment provides the Cray compiler wrappers: `CC` for C++, `cc` for C, `ftn` for Fortran. The underlying compiler invoked by the wrapper is based on the `PrgEnv` loaded, e.g. `PrgEnv-gnu`.

```
user.project@login02:~> CC --version
g++-13 (SUSE Linux) 13.2.1 20240206 [revision 67ac78caf31f7cb3202177e6428a46d829b70f23]
Copyright (C) 2023 Free Software Foundation, Inc.
This is free software; see the source for copying conditions.  There is NO
warranty; not even for MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.

user.project@login02:~> cc --version
gcc-13 (SUSE Linux) 13.2.1 20240206 [revision 67ac78caf31f7cb3202177e6428a46d829b70f23]
Copyright (C) 2023 Free Software Foundation, Inc.
This is free software; see the source for copying conditions.  There is NO
warranty; not even for MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.

user.project@login02:~> ftn --version
GNU Fortran (SUSE Linux) 13.2.1 20240206 [revision 67ac78caf31f7cb3202177e6428a46d829b70f23]
Copyright (C) 2023 Free Software Foundation, Inc.
This is free software; see the source for copying conditions.  There is NO
warranty; not even for MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.

```

When compiling software with the `PrgEnv-gnu` module loaded, we recommend use the Cray compiler wrappers (`CC`, `cc`, and `ftn`) rather than the standard commands for invoking GCC compilers (`g++`, `gcc`, `gfortran`) unless you have a good reason not to use the compiler wrappers.

The compiler wrapper commands and standard GCC compiler commands use the same underlying GCC compilers, e.g.

```
user@project@login02:~> gcc --version
gcc (SUSE Linux) 13.2.1 20240206 [revision 67ac78caf31f7cb3202177e6428a46d829b70f23]
Copyright (C) 2023 Free Software Foundation, Inc.
This is free software; see the source for copying conditions.  There is NO
warranty; not even for MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.

user.project@login02:~> cc --version
gcc-13 (SUSE Linux) 13.2.1 20240206 [revision 67ac78caf31f7cb3202177e6428a46d829b70f23]
Copyright (C) 2023 Free Software Foundation, Inc.
This is free software; see the source for copying conditions.  There is NO
warranty; not even for MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.

```

The Cray compiler wrappers will automatically link to other Cray Programming Environment libraries based on loaded modules (e.g. the Cray Scientific and Math Libraries, module `cray-libsci`, and Cray Message Passing Toolkit module `cray-mpich`). To ensure consistent builds, it is important not to mix use of the compiler wrapper commands (`cc`, `CC`, `ftn`) and the standard GCC commands (`gcc`, `g++`, `gfortran`).

Showing the compiler options used by Cray compiler wrappers

To view the full command forwarded to the underlying compiler by the wrapper, including the libraries and header files used, pass the `-craype-verbose` flag when compiling, e.g.

```
user@project@login02:~> ftn -craype-verbose -o hello hello.f90 
gfortran-13 -D__CRAY_ARM_GRACE -D__CRAY_AARCH64 -D__CRAYXT_COMPUTE_LINUX_TARGET -D__TARGET_LINUX__ -o hello hello.f90 -Wl,-Bdynamic -I/usr/include -I/opt/cray/pe/mpich/8.1.30/ofi/gnu/12.3/include -I/opt/cray/pe/libsci/24.07.0/GNU/12.3/aarch64/include -L/opt/cray/pe/mpich/8.1.30/ofi/gnu/12.3/lib -L/opt/cray/pe/libsci/24.07.0/GNU/12.3/aarch64/lib -Wl,--as-needed,-lmpifort_gnu_123,--no-as-needed -Wl,--as-needed,-lsci_gnu_mpi,--no-as-needed -Wl,--as-needed,-lmpi_gnu_123,--no-as-needed -Wl,--as-needed,-lsci_gnu,--no-as-needed -ldl -Wl,--as-needed,-lgfortran,--no-as-needed -Wl,--as-needed,-lpthread,--no-as-needed -Wl,--disable-new-dtags 

```

Spack

If you are using the Spack package management tool to build software, please see the Spack guide which provides guidance on configuring Spack to use the compilers provided on Isambard-AI and Isambard 3.

## Compiler options

For general information please refer to NVIDIA Grace Performance Tuning Guide

### GNU compilers

To instruct the compiler to target the Nvidia Grace Superchip, use the compiler option `-mcpu=neoverse-v2`. Note that this is different from how we would do this for x86 processors (eg Intel or AMD), where `-march` is used.

### Non-GNU compilers

When specifying a C++ standard (e.g. for Nvidia it can be set using `--std=c++23`) it may be necessary to check compatability with the default GCC version that non-GNU compilers can depend on. Compilers such as the Nvidia compiler have an option `--gcc-toolchain` to specify the version of GCC (and the required C++ standard support). For example `--gcc-toolchain=/usr/bin/gcc-13` will specify using GCC 13 instead of the default GCC version which may not support the C++ standard.

## Other useful compilers

Other modules can be loaded such as `module load nvidia` will load just the Nvidia compiler.

```
$ nvc --version
nvc 23.9-0 linuxarm64 target on aarch64 Linux -tp neoverse-v2 
NVIDIA Compilers and Tools
Copyright (c) 2023, NVIDIA CORPORATION & AFFILIATES.  All rights reserved.
$ nvc++ --version
nvc++ 23.9-0 linuxarm64 target on aarch64 Linux -tp neoverse-v2 
NVIDIA Compilers and Tools
Copyright (c) 2023, NVIDIA CORPORATION & AFFILIATES.  All rights reserved.
$ nvfortran --version
nvfortran 23.9-0 linuxarm64 target on aarch64 Linux -tp neoverse-v2 
NVIDIA Compilers and Tools
Copyright (c) 2023, NVIDIA CORPORATION & AFFILIATES.  All rights reserved.

```

Note that just loading just a compiler such as `module load nvidia` will not load any MPI libraries automatically. The Programming Environment support for the Nvidia compiler will be improved in future system updates.

For further information on MPI please see our MPI guide.

## Profiling tools

### gprof

gprof can be called without loading any modules:

`gprof ./a.out`

### Cray perftools

Access by loading the Cray perftools module:

`module load perftools-base`

Provides `pat_run` and other commands.

Detailed instructions can be found in the HPE Cray docs

### Nvidia Nsight Systems

`module load cudatoolkit`

Provides `nsys`.

Detailed instructions can be found in the Nvidia docs
