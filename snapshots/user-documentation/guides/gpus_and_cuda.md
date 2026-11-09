<!-- Snapshot of https://docs.isambard.ac.uk/user-documentation/guides/gpus_and_cuda/ made by snapshot_docs.py. Do not edit. -->

# GPUs and CUDA

CUDA (Compute Unified Device Architecture) is NVIDIA's parallel programming platform and API. It is a common foundation of GPU computing on Isambard-AI: application code, frameworks, and every higher-level component are all compiled against and depend on a specific CUDA toolkit version.

For information on the CUDA programming model, see NVIDIA's CUDA Programming Guide.

## NVIDIA Driver version and supported CUDA versions

You can check the driver version and natively supported CUDA version at any time by running `nvidia-smi` on a compute node.

The CUDA version shown in the top-right corner is the maximum version supported by the installed driver, it does not reflect the toolkit version loaded via modules.

```
$ srun --nodes=1 --gpus=1 --ntasks=1 --time=00:00:10 nvidia-smi

```

Example nvidia-smi output

This output shows the installed NVIDIA driver as of April 2026.

```
Thu Apr  9 16:46:06 2026
+-----------------------------------------------------------------------------------------+
| NVIDIA-SMI 565.57.01              Driver Version: 565.57.01      CUDA Version: 12.7     |
|-----------------------------------------+------------------------+----------------------+
| GPU  Name                 Persistence-M | Bus-Id          Disp.A | Volatile Uncorr. ECC |
| Fan  Temp   Perf          Pwr:Usage/Cap |           Memory-Usage | GPU-Util  Compute M. |
|                                         |                        |               MIG M. |
|=========================================+========================+======================|
|   0  NVIDIA GH200 120GB             On  |   00000009:01:00.0 Off |                    0 |
| N/A   24C    P0             97W /  900W |       1MiB /  97871MiB |      0%      Default |
|                                         |                        |             Disabled |
+-----------------------------------------+------------------------+----------------------+

+-----------------------------------------------------------------------------------------+
| Processes:                                                                              |
|  GPU   GI   CI        PID   Type   Process name                              GPU Memory |
|        ID   ID                                                               Usage      |
|=========================================================================================|
|  No running processes found                                                             |
+-----------------------------------------------------------------------------------------+

```

## Running GPU applications

The CUDA library is available as a module on Isambard-AI. GPU-accelerated applications, such as PyTorch which supply their own CUDA runtime, will work without any additional setup. See our Distributed PyTorch Training tutorial for an example. For other applications that do not provide a CUDA runtime, you will need to load the CUDA toolkit module.

## Loading the CUDA toolkit

When you need to compile CUDA code or use NVIDIA's compilers and libraries explicitly, load the toolkit via modules.

Two modules are available:

- `cudatoolkit` — CUDA-focused; sets `$CUDA_HOME`, adds `nvcc` and the CUDA compilers, libraries, and tools to your environment.
- `nvhpc` — development-focused; additionally sets include paths such as `CPLUS_INCLUDE_PATH`, making it more suitable for building software against the SDK headers.

Load whichever is appropriate for your use case:

```
$ module load cudatoolkit

```

Verify the loaded CUDA version with:

```
$ nvcc --version
nvcc: NVIDIA (R) Cuda compiler driver
...
Build cuda_12.6.r12.6/compiler.34431801_0

```

See the modules guide for more information.

## Example: compiling a simple CUDA kernel

The following example illustrates the basic CUDA compile-and-run cycle on Isambard-AI. It is a simple "Hello, World!" program that executes on the GPU.

```
// helloworld.cu — prints "Hello, World!" from the GPU
#include <cstdio>

__global__ void cuda_hello(){
    printf("Hello, World!\n");
}

int main() {
    // Launch kernel
    cuda_hello<<<1, 1>>>();

    // Check for launch errors
    cudaError_t err = cudaGetLastError();
    if (err != cudaSuccess) {
        printf("Kernel launch failed: %s\n", cudaGetErrorString(err));
        return 1;
    }

    // Wait for GPU to finish
    cudaDeviceSynchronize();

    printf("Success!\n");
    return 0;
}

```

Compile and run:

```
$ module load cudatoolkit
$ nvcc -o helloworld helloworld.cu -arch=sm_90
$ srun --nodes=1 --gpus=1 --ntasks=1 --time=00:00:30 ./helloworld
Success!

```

Target architecture

The Hopper GPU (H100) uses compute capability sm_90. Always pass `-arch=sm_90` (or `-gencode arch=compute_90,code=sm_90`) to `nvcc` to generate optimised code for the Hopper architecture.

Error checking in production code

The example above is a simple example of a CUDA kernel. When writing code that uses CUDA API calls such as `cudaMalloc`, `cudaMemcpy` and `cudaFree`, make sure to check every return value against `cudaSuccess`. You should also call `cudaGetLastError()` after launching the kernel to catch any errors that occurred during execution.

Silent failures from unchecked errors are a common source of hard-to-diagnose bugs.

## CUDA Forward Compatibility

Some applications, such as running frontier LLMs, may require CUDA features provided by newer CUDA versions which aren't natively supported by the current NVIDIA driver. Newer CUDA versions can be configured using CUDA forward compatibility, a feature available for NVIDIA's datacenter GPUs; such as the GH200s in Isambard-AI.

How CUDA forward compatibility works

Forward compatibility works by placing `libcuda_compat` earlier in `LD_LIBRARY_PATH` than the system `libcuda.so`, intercepting CUDA API calls and translating them to what the installed driver understands. Both approaches below rely on this mechanism — the difference is whether it is set up automatically or manually.

There are three ways of using newer CUDA version via forward compatibility:

- NGC containers (recommended) - CUDA forward compatibility is handled automatically by the NVIDIA container runtime.
- HPC SDK - install a newer NVIDIA HPC SDK in your home or project directory, which contains the CUDA forward compatibility shim.
- Conda - install the `cuda-compat` package from Conda Forge.

### NGC containers

NGC containers bundle the CUDA toolkit, NCCL, cuDNN, and application frameworks as a consistent, version-matched set. When `--nv` is passed to Apptainer, the NVIDIA container runtime automatically injects the forward compatibility libraries alongside the host driver — no manual setup is needed.

Key NGC base images:

| Base image | Includes | Best for |
| `nvcr.io/nvidia/cuda:<version>-devel-ubuntu24.04` | CUDA toolkit, `nvcc`, headers, libraries | Custom CUDA C/C++ applications |
| `nvcr.io/nvidia/nvhpc:<version>-devel-cuda_multi-ubuntu24.04` | HPC SDK (`nvc`, `nvc++`, `nvfortran`), CUDA, cuDNN, NCCL | HPC applications using OpenACC, CUDA Fortran, or the NVIDIA compilers |
| `nvcr.io/nvidia/pytorch:<tag>-py3` | PyTorch, CUDA, cuDNN, NCCL, APEX | Deep learning training and inference with PyTorch |

Check NGC for the latest tags

NVIDIA regularly publishes updated container images. Check the NGC Catalog for the latest available tags and release notes. Details of the contents of these images can be found in the NVIDIA Docs Hub.

For information regarding compatible container images for Isambard-AI, see our containers on ARM page. Follow our Using GPUs with Apptainer guide for information on using NGC images, and our NCCL and Apptainer Multi-node guides for information on using these containers over multiple nodes.

### NVIDIA HPC SDK

The NVIDIA HPC SDK is available as a self-contained tarball that can be installed in your home or project directory. The SDK includes its own CUDA toolkit and compat libraries; adding the compat path to `LD_LIBRARY_PATH` is all that is needed to enable forward compatibility on bare metal.

aarch64 tarball required

Isambard-AI uses ARM (aarch64) CPUs. Ensure you download the `aarch64` tarball, not `x86_64`.

As an example, here we will download the NVIDIA HPC SDK 26.3 with CUDA 13.1 forward compatibility.

Download and extract (replace the version and filename with the version you need):

```
$ wget https://developer.download.nvidia.com/hpc-sdk/26.3/nvhpc_2026_263_Linux_aarch64_cuda_13.1.tar.gz
$ tar xpzf nvhpc_2026_263_Linux_aarch64_cuda_13.1.tar.gz

```

Run the install script, ensuring that `NVHPC_INSTALL_DIR` is pointing to a folder in your home or project directory:

```
$ cd nvhpc_2026_263_Linux_aarch64_cuda_13.1
$ NVHPC_SILENT="true" NVHPC_INSTALL_DIR=$PROJECTDIR/$USER/nvhpc NVHPC_INSTALL_TYPE="single" ./install

```

Set up your environment (replace `<INSTALL_PATH>` and version numbers as appropriate):

```
$ export NVHPC_ROOT=<INSTALL_PATH>/Linux_aarch64/26.3
$ # Set our LD_LIBRARY_PATH, ensuring that the cuda compat folder is the first path
$ # This will enable CUDA forward compatibility
$ export LD_LIBRARY_PATH=$NVHPC_ROOT/cuda/13.1/compat:$NVHPC_ROOT/cuda/13.1/lib64:$NVHPC_ROOT/compilers/lib:$NVHPC_ROOT/comm_libs/13.1/nccl/lib:$NVHPC_ROOT/comm_libs/13.1/nvshmem/lib:$NVHPC_ROOT/math_libs/13.1/lib64:$LD_LIBRARY_PATH
$ export PATH=$NVHPC_ROOT/compilers/bin:$NVHPC_ROOT/comm_libs/13.1/nccl/bin:$PATH
$ export CPATH=$NVHPC_ROOT/cuda/13.1/include:$NVHPC_ROOT/comm_libs/13.1/nccl/include:$NVHPC_ROOT/math_libs/13.1/include:$NVHPC_ROOT/compilers/include:$CPATH
$ export CUDA_HOME=$NVHPC_ROOT/cuda/13.1
$ export NCCL_HOME=$NVHPC_ROOT/comm_libs/13.1/nccl

```

You can now verify that CUDA 13.1 forward compatibility has been enabled by running the following commands:

```
$ srun --nodes=1 --gpus=1 --time=00:00:10 nvidia-smi | grep CUDA
| NVIDIA-SMI 565.57.01              Driver Version: 565.57.01      CUDA Version: 13.1     |
$ srun --nodes=1 --gpus=1 --time=00:00:10 nvcc --version
nvcc: NVIDIA (R) Cuda compiler driver
...
Build cuda_13.1.r13.1/compiler.36836380_0

```

You should see that `nvidia-smi` shows you can run a CUDA runtime up to CUDA 13.1 and the available CUDA runtime, shown by `nvcc` is CUDA 13.1; meaning that you can now run applications which require a CUDA version up to and including 13.1.

### CUDA version mismatch or forward compatibility not active

If `nvidia-smi` still shows the native CUDA version (12.7) after setting up forward compatibility, the compat libraries are not on `LD_LIBRARY_PATH` before the system `libcuda.so`. Verify the ordering with:

```
$ echo $LD_LIBRARY_PATH | tr ':' '\n' | grep --extended-regexp 'compat|cuda'

```

The compat path (e.g. `$NVHPC_ROOT/cuda/13.1/compat`) must appear before any system CUDA library path.

## Resources

- NVIDIA CUDA C++ Programming Guide
- NVIDIA HPC SDK Documentation
