---
name: cuda
description: >
  Guide for using GPUs and CUDA on Isambard AI (BriCS) supercomputers (Isambard-AI Phase 1
  and Phase 2, which have NVIDIA GH200 Grace Hopper GPUs). Use this skill whenever a user
  asks about CUDA on Isambard, loading the cudatoolkit or nvhpc modules, compiling CUDA
  kernels with nvcc, the correct -arch flag for the GH200 (sm_90), CUDA forward
  compatibility, using a newer CUDA version than the installed driver supports, the NVIDIA
  HPC SDK on Isambard, NGC container images for GPU workloads, nvidia-smi on compute nodes,
  or diagnosing CUDA version mismatches. Also trigger for general GPU programming setup
  questions on Isambard, even if the user doesn't say "CUDA" explicitly.
  Note: GPUs are only on Isambard-AI (Phase 1 and Phase 2) — not Isambard 3.
compatibility: >
  Isambard-AI only. Requires access to an Isambard-AI login node, GPU compute
  resources, and CUDA toolkit or container runtime support.
metadata:
  author: isambard-sc
  version: "1.0"
  source_url: https://docs.isambard.ac.uk/user-documentation/guides/gpus_and_cuda/
---

# GPUs and CUDA on Isambard

Isambard-AI compute nodes are equipped with **NVIDIA GH200 120GB Grace Hopper** GPUs
(compute capability **sm_90**, Hopper architecture). CUDA is the foundation for all GPU
workloads — frameworks like PyTorch depend on it, and every library and tool links against
a specific CUDA toolkit version.

> **GPU systems only:** Isambard-AI Phase 1 and Phase 2. Isambard 3 has no GPUs.

---

## Check Driver and Supported CUDA Version

Run `nvidia-smi` on a compute node to see the installed driver and the maximum natively
supported CUDA version:

```bash
srun --gpus=1 --ntasks=1 --time=00:00:10 nvidia-smi
```

Example output (as of April 2026):
```
Driver Version: 565.57.01      CUDA Version: 12.7
GPU: NVIDIA GH200 120GB
```

The `CUDA Version` shown by `nvidia-smi` is the **maximum version the driver natively
supports** — not the toolkit version loaded via modules. See [CUDA Forward Compatibility](#cuda-forward-compatibility)
below to run applications requiring a newer CUDA than the driver natively supports.

---

## Running GPU Applications

**Applications that bundle their own CUDA runtime** (e.g. PyTorch installed via conda or
NGC containers) work without any additional module loading. See the
[Distributed PyTorch Training tutorial](https://docs.isambard.ac.uk/user-documentation/tutorials/distributed-training/)
for an example.

**Applications that require the system CUDA toolkit** (compiling CUDA code, using NVIDIA
compilers or libraries explicitly) — load a module first.

---

## Loading the CUDA Toolkit

Two modules are available — choose based on your use case:

| Module | Sets | Best for |
|--------|------|----------|
| `cudatoolkit` | `$CUDA_HOME`, `nvcc`, CUDA compilers, libraries, tools | Compiling CUDA code; general GPU development |
| `nvhpc` | Everything in `cudatoolkit` plus `CPLUS_INCLUDE_PATH` and SDK headers | Building software against NVIDIA HPC SDK headers (OpenACC, CUDA Fortran) |

```bash
module load cudatoolkit    # most common

# Verify
nvcc --version
# Build cuda_12.6.r12.6/...
```

---

## Compiling CUDA Code

### Target architecture

The GH200 uses compute capability **sm_90**. Always specify this to get optimised code:

```bash
nvcc -o myapp myapp.cu -arch=sm_90
# or equivalently:
nvcc -o myapp myapp.cu -gencode arch=compute_90,code=sm_90
```

Using a lower `-arch` value will produce correct but unoptimised code; omitting `-arch`
altogether will compile for a generic baseline that may not support all GH200 features.

### Hello World example

```cuda
// helloworld.cu
#include <cstdio>

__global__ void cuda_hello() {
    printf("Hello, World!\n");
}

int main() {
    cuda_hello<<<1, 1>>>();

    cudaError_t err = cudaGetLastError();
    if (err != cudaSuccess) {
        printf("Kernel launch failed: %s\n", cudaGetErrorString(err));
        return 1;
    }
    cudaDeviceSynchronize();
    printf("Success!\n");
    return 0;
}
```

```bash
module load cudatoolkit
nvcc -o helloworld helloworld.cu -arch=sm_90
srun --gpus=1 --ntasks=1 --time=00:00:30 ./helloworld
# Hello, World!
# Success!
```

> **Always check CUDA error returns in production code.** Check every `cudaMalloc`,
> `cudaMemcpy`, `cudaFree` return value against `cudaSuccess`, and call
> `cudaGetLastError()` after kernel launches. Silent unchecked errors are a common
> source of hard-to-diagnose bugs.

---

## CUDA Forward Compatibility

Some applications (e.g. frontier LLMs) require CUDA features from a **newer toolkit
version than the installed driver natively supports** (currently 12.7 as of April 2026).

Forward compatibility works by placing `libcuda_compat` **ahead of** the system
`libcuda.so` on `LD_LIBRARY_PATH`, intercepting CUDA API calls and translating them to
what the installed driver understands. It is available on datacenter GPUs like the GH200.

Three approaches — choose the one that fits your workflow:

### Option 1: NGC Containers (recommended — automatic)

NGC containers bundle CUDA, cuDNN, NCCL, and frameworks as a consistent version-matched
set. When running with `--nv` (Apptainer) or `--device=nvidia.com/gpu=all` (Podman-HPC),
the NVIDIA container runtime injects the forward compat libraries automatically alongside
the host driver. No manual `LD_LIBRARY_PATH` setup needed.

Key NGC base images (use `linux/arm64` / `aarch64` tags):

| Image | Contents | Use when |
|-------|----------|----------|
| `nvcr.io/nvidia/cuda:<ver>-devel-ubuntu24.04` | CUDA toolkit, `nvcc`, headers, libraries | Custom CUDA C/C++ |
| `nvcr.io/nvidia/nvhpc:<ver>-devel-cuda_multi-ubuntu24.04` | HPC SDK, CUDA, cuDNN, NCCL | OpenACC, CUDA Fortran, NVIDIA compilers |
| `nvcr.io/nvidia/pytorch:<tag>-py3` | PyTorch, CUDA, cuDNN, NCCL, APEX | Deep learning training/inference |

Check [NGC Catalog](https://catalog.ngc.nvidia.com/) for latest tags.
See the [containers guide](https://docs.isambard.ac.uk/user-documentation/guides/containers/)
for aarch64 image selection and multi-node setup.

### Option 2: NVIDIA HPC SDK (bare-metal install)

The HPC SDK is a self-contained tarball that includes its own CUDA toolkit and the
forward compat shim. Install it in your home or project directory.

> **Download the `aarch64` tarball** — not `x86_64`.

```bash
# Example: HPC SDK 26.3 with CUDA 13.1 forward compatibility
wget https://developer.download.nvidia.com/hpc-sdk/26.3/nvhpc_2026_263_Linux_aarch64_cuda_13.1.tar.gz
tar xpzf nvhpc_2026_263_Linux_aarch64_cuda_13.1.tar.gz
cd nvhpc_2026_263_Linux_aarch64_cuda_13.1

# Install to your project directory
NVHPC_SILENT="true" \
NVHPC_INSTALL_DIR=$PROJECTDIR/$USER/nvhpc \
NVHPC_INSTALL_TYPE="single" \
./install
```

Set up the environment (the compat path **must be first** on `LD_LIBRARY_PATH`):

```bash
export NVHPC_ROOT=<INSTALL_PATH>/Linux_aarch64/26.3

# compat path FIRST — this is what enables forward compatibility
export LD_LIBRARY_PATH=\
$NVHPC_ROOT/cuda/13.1/compat:\
$NVHPC_ROOT/cuda/13.1/lib64:\
$NVHPC_ROOT/compilers/lib:\
$NVHPC_ROOT/comm_libs/13.1/nccl/lib:\
$NVHPC_ROOT/comm_libs/13.1/nvshmem/lib:\
$NVHPC_ROOT/math_libs/13.1/lib64:\
$LD_LIBRARY_PATH

export PATH=$NVHPC_ROOT/compilers/bin:$NVHPC_ROOT/comm_libs/13.1/nccl/bin:$PATH
export CPATH=$NVHPC_ROOT/cuda/13.1/include:$NVHPC_ROOT/comm_libs/13.1/nccl/include:$NVHPC_ROOT/math_libs/13.1/include:$NVHPC_ROOT/compilers/include:$CPATH
export CUDA_HOME=$NVHPC_ROOT/cuda/13.1
export NCCL_HOME=$NVHPC_ROOT/comm_libs/13.1/nccl
```

Verify forward compatibility is active:

```bash
srun --gpus=1 --time=00:00:10 nvidia-smi | grep CUDA
# Should show: CUDA Version: 13.1  (not 12.7)

srun --gpus=1 --time=00:00:10 nvcc --version
# Should show: Build cuda_13.1.r13.1/...
```

### Option 3: Conda `cuda-compat` Package

```bash
conda install -c conda-forge cuda-compat
```

Then add the conda env's compat path to the front of `LD_LIBRARY_PATH` before any system
CUDA paths. Same mechanism as Option 2.

---

## Troubleshooting: Forward Compatibility Not Active

If `nvidia-smi` still shows the native CUDA version (12.7) after setup, the compat
library is not being picked up before the system `libcuda.so`. Check the path ordering:

```bash
echo $LD_LIBRARY_PATH | tr ':' '\n' | grep -E 'compat|cuda'
```

The compat path (e.g. `$NVHPC_ROOT/cuda/13.1/compat`) **must appear before** any system
CUDA path. Re-export `LD_LIBRARY_PATH` with the compat entry at the front.

---

## Quick Reference

| Goal | Command / action |
|------|-----------------|
| Check driver + max CUDA version | `srun --gpus=1 --ntasks=1 --time=00:00:10 nvidia-smi` |
| Load CUDA toolkit | `module load cudatoolkit` |
| Load NVIDIA HPC SDK headers | `module load nvhpc` |
| Compile for GH200 | `nvcc -arch=sm_90 -o out app.cu` |
| Use newer CUDA (containerised) | NGC image + `--nv` (Apptainer) or `--device=nvidia.com/gpu=all` (Podman-HPC) |
| Use newer CUDA (bare-metal) | Install NVIDIA HPC SDK `aarch64` tarball; put compat path first on `LD_LIBRARY_PATH` |
| Verify forward compat active | `nvidia-smi \| grep CUDA` should show the new version |
| Debug forward compat order | `echo $LD_LIBRARY_PATH \| tr ':' '\n' \| grep -E 'compat\|cuda'` |

---

## Related Resources

- [NVIDIA CUDA C++ Programming Guide](https://docs.nvidia.com/cuda/cuda-c-programming-guide/)
- [NVIDIA HPC SDK documentation](https://docs.nvidia.com/hpc-sdk/)
- [NGC Catalog](https://catalog.ngc.nvidia.com/)
- [CUDA Forward Compatibility docs](https://docs.nvidia.com/deploy/cuda-compatibility/)
- [Isambard Containers guide](https://docs.isambard.ac.uk/user-documentation/guides/containers/)
- [Isambard NCCL guide](https://docs.isambard.ac.uk/user-documentation/guides/nccl/)
- [Isambard Modules and Compilers guide](https://docs.isambard.ac.uk/user-documentation/guides/modules/)
- [Distributed PyTorch Training tutorial](https://docs.isambard.ac.uk/user-documentation/tutorials/distributed-training/)
