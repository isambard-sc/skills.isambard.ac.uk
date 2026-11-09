<!-- Snapshot of https://docs.isambard.ac.uk/user-documentation/guides/nccl/ made by snapshot_docs.py. Do not edit. -->

- ✓ AIP1 Isambard-AI Phase 1 supported
- ✓ AIP2 Isambard-AI Phase 2 supported
- ✗ I3 Isambard 3 unsupported
- ✗ BC5 BlueCrystal 5 unsupported

# NCCL

The NVIDIA Collective Communication Library (NCCL) provides direct GPU-GPU communication for NVIDIA GPUs. This guide will show how NCCL can be used on Isambard-AI's HPE Slingshot 11 high speed network.

NCCL provides RDMA (Remote Direct Memory Access) via GPUDirect. To use this on the Slingshot network, you must use the `aws-ofi-nccl` network plugin.

NCCL and `aws-ofi-nccl` are provided on the system as follows:

```
$ module load brics/nccl

```

The rest of this guide explains optimisations to NCCL on Slingshot as they are application dependent.

## Environment Variables

NCCL Environment variables are used to optimise the performance on the Slingshot network. The official NCCL documentation has in-depth explanations of the environment variables.

These variables are set in the module `brics/nccl`, but are explained here for application-specific optimisation or if you are building your own version.

```
# Force NCCL to use the aws-ofi-nccl libfabric plugin
export NCCL_NET="AWS Libfabric"
# Use the high speed network interface
export NCCL_SOCKET_IFNAME="hsn"
# Print the NCCL version at startup
export NCCL_DEBUG="VERSION"
# Use P2P when GPUs share the same NUMA node
export NCCL_NET_GDR_LEVEL="PHB"
# Allow rings/trees to span multiple NICs
export NCCL_CROSS_NIC="1"
export NCCL_MIN_NCHANNELS="4"
export NCCL_GDRCOPY_ENABLE="1"
export NCCL_NET_FORCE_FLUSH="0"

# Libfabric (FI) tuning for Slingshot
export FI_CXI_DEFAULT_CQ_SIZE="131072"
export FI_CXI_DEFAULT_TX_SIZE="2048"
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

Click here to download the file: env_vars.sh

Some optimisations are application dependent

The default system settings optimise for a wide range of scenarios. However, it is important to note the optimisations are application dependent, namely `NCCL_MIN_NCHANNELS`, `FI_CXI_DEFAULT_CQ_SIZE`, and `FI_CXI_DEFAULT_TX_SIZE`.

For more information see The official NCCL documentation on environment variables.

NCCL and AWS Libfabric

The environment variable `NCCL_NET="AWS Libfabric"` will force NCCL to use the `aws-ofi-nccl` plugin. If the plugin isn't setup in your environment you will get the following error:

```
NCCL WARN Error: network AWS Libfabric not found.

```

Debugging

When debugging NCCL ensure you set `NCCL_DEBUG=INFO` to get the NCCL debug logs.

## Build NCCL

### Installing `nccl`

If you need a specific version of NCCL - or you are trying to build a custom container, you can build NCCL with the following instructions:

install_nccl.sh
```
#!/bin/bash

cd $HOME
module load cudatoolkit PrgEnv-gnu
git clone --branch "v2.27.7-1" https://github.com/NVIDIA/nccl.git
cd nccl
mkdir build
make -j 8 src.build PREFIX=$(realpath build)

```

### Installing `aws-ofi-nccl`

The NCCL network plugin `aws-ofi-nccl` must be built for NCCL to use the Slingshot high speed network. It depends on CUDA and Libfabric. Ensure you use a version that is tagged with `aws`. The network plugin can be installed as follows:

install_aws_ofi_nccl.sh
```
#!/bin/bash

cd $HOME
module load cudatoolkit PrgEnv-gnu
git clone --branch "v1.7.x-aws" https://github.com/aws/aws-ofi-nccl.git
cd aws-ofi-nccl
./autogen.sh
export LIBFABRIC_HOME=/opt/cray/libfabric/1.22.0 CC=/usr/bin/gcc-12 CXX=/usr/bin/g++-12
mkdir build
./configure --prefix=$(realpath build) --with-cuda=${CUDA_HOME} --with-libfabric=${LIBFABRIC_HOME} --disable-tests
make -j 8 install

```

## Benchmark NCCL with `nccl-tests`

NCCL tests depends on MPI, NCCL, and CUDA. We can build it with the following instructions:

build_nccl_tests.sh
```
#!/bin/bash

cd $HOME
module load cudatoolkit PrgEnv-gnu
git clone https://github.com/NVIDIA/nccl-tests.git
cd nccl-tests
export MPI_HOME=/opt/cray/pe/mpich/8.1.32/ofi/gnu/12.3/
# Make sure you set NCCL_HOME to your build directory
export NCCL_HOME=$(realpath ../nccl/build)
make -j 8 MPI=1 MPI_HOME=${MPI_HOME} NCCL_HOME=${NCCL_HOME} CUDA_HOME=${CUDA_HOME}

```

We can now run an All Reduce benchmark to measure the network bandwidth for collectives. Running without the plugin, we see we have a maximum Bus Bandwidth of `busbw 2.32 GB/s`.

all_reduce_no_plugin.sh
```
#!/bin/bash

cd $HOME/nccl-tests
srun --nodes=2 --gpus=8 --network=disable_rdzv_get $(realpath ./build/all_reduce_perf) -b 32KB -e 8GB -f 2 -g 4

```

Example output:

```
# nccl-tests version 2.17.6 nccl-headers=21903 nccl-library=21903
# Collective test starting: all_reduce_perf
# nThread 1 nGpus 4 minBytes 8 maxBytes 4294967296 step: 2(factor) warmup iters: 1 iters: 20 agg iters: 1 validation: 1 graph: 0
#
# Using devices
#  Rank  0 Group  0 Pid 123253 on  nid001024 device  0 [0009:01:00] NVIDIA GH200 120GB
[...]
#
#                                                              out-of-place                       in-place          
#       size         count      type   redop    root     time   algbw   busbw  #wrong     time   algbw   busbw  #wrong 
#        (B)    (elements)                               (us)  (GB/s)  (GB/s)             (us)  (GB/s)  (GB/s)         
[...]
  8589934592    2147483648     float     sum      -1  6492425    1.32    2.32       0  6488797    1.32    2.32       0
# Out of bounds values : 0 OK
# Avg bus bandwidth    : 1.3806
#
# Collective test concluded: all_reduce_perf

```

The above shows very slow performance indicating that NCCL is not using RDMA and is instead using a TCP Socket interface. To enable RDMA, we will source the environment variables above and add the plugin to our environment:

all_reduce_with_plugin.sh
```
#!/bin/bash

cd $HOME/nccl-tests
export LD_LIBRARY_PATH=$(realpath ../aws-ofi-nccl/build/lib):${LD_LIBRARY_PATH:-}
# Ensure you source the environment variables from above
srun --nodes=2 --gpus=8 --cpus-per-task 72 --network=disable_rdzv_get ./build/all_reduce_perf -b 32KB -e 8GB -f 2 -g 4

```

Example output:

```
# nccl-tests version 2.17.6 nccl-headers=21903 nccl-library=21903
# Collective test starting: all_reduce_perf
# nThread 1 nGpus 4 minBytes 32768 maxBytes 8589934592 step: 2(factor) warmup iters: 1 iters: 20 agg iters: 1 validation: 1 graph: 0
#
# Using devices
#  Rank  0 Group  0 Pid 125488 on  nid001024 device  0 [0009:01:00] NVIDIA GH200 120GB
#  Rank  1 Group  0 Pid 125488 on  nid001024 device  1 [0019:01:00] NVIDIA GH200 120GB
#  Rank  2 Group  0 Pid 125488 on  nid001024 device  2 [0029:01:00] NVIDIA GH200 120GB
#  Rank  3 Group  0 Pid 125488 on  nid001024 device  3 [0039:01:00] NVIDIA GH200 120GB
#  Rank  4 Group  0 Pid 136269 on  nid001025 device  0 [0009:01:00] NVIDIA GH200 120GB
#  Rank  5 Group  0 Pid 136269 on  nid001025 device  1 [0019:01:00] NVIDIA GH200 120GB
#  Rank  6 Group  0 Pid 136269 on  nid001025 device  2 [0029:01:00] NVIDIA GH200 120GB
#  Rank  7 Group  0 Pid 136269 on  nid001025 device  3 [0039:01:00] NVIDIA GH200 120GB
NCCL version 2.19.3+cuda12.3
#
#                                                              out-of-place                       in-place          
#       size         count      type   redop    root     time   algbw   busbw  #wrong     time   algbw   busbw  #wrong 
#        (B)    (elements)                               (us)  (GB/s)  (GB/s)             (us)  (GB/s)  (GB/s)         
[...]
  8589934592    2147483648     float     sum      -1  92400.1   92.96  162.69       0  92381.3   92.98  162.72       0
# Out of bounds values : 0 OK
# Avg bus bandwidth    : 62.3908 
#
# Collective test concluded: all_reduce_perf

```

Here you can see that NCCL is correctly using RDMA on Slingshot, achieving an All Reduce out-of-place bus bandwidth of `162.69 GB/s`.

GPU to NIC topology information

NCCL has an option through setting the environment variable `NCCL_TOPO_DUMP_FILE=topo.txt` to save topology information to a file e.g. `topo.txt`. The commands `cxi_stat` and `nvidia-smi -L` can list the Network Interface Cards (NICs) and GPUs respectively. This can confirm which Slingshot network device is used by each GPU.

## Build NCCL in a container

For container workloads, we recommend using Apptainer (formerly Singularity). The `brics/apptainer-multi-node` module injects the host MPI, NCCL, `aws-ofi-nccl` libraries into your container enabling multi-node workloads. The NCCL and `aws-ofi-nccl` host libraries are built against the CUDA runtime provided by the host system. More information on this module can be found in our Apptainer Multi-node guide.

If your container provides, or requires, a newer CUDA runtime than the host version, such as one provided in an NVIDIA GPU Cloud (NGC) image, you may need a compatible version of NCCL and the `aws-ofi-nccl` OFI plugin. Such container images may include a build of NCCL that is compatible with the CUDA runtime supplied - in this case we only need to build a compatible `aws-ofi-nccl` plugin.

To build compatible `nccl` and `aws-ofi-nccl` libraries, we will first build a base image containing our application. Then, we will run our container in order to build `nccl` and `aws-ofi-nccl` against the CUDA runtime within the container.

Note

These libraries should be built into a folder bind-mounted from the host, such as one within the home folder.

The folder containing these compiled libraries will need to be bind-mounted to the container each time it is run.

As an example, we will configure a container based on the PyTorch 26.01 NGC image to use RDMA over Slingshot with NCCL. This image provides a version of NCCL built against the CUDA runtime provided within the image, but we will build new, compatible versions of the NCCL and `aws-ofi-nccl` libraries. We will also build the `nccl-tests` benchmark suite to test that our container has been properly configured for RDMA.

```
Bootstrap: docker
From: nvcr.io/nvidia/pytorch:26.01-py3

%setup
    # Copy NCCL environment variables script, downloaded above, into container
    cp env_vars.sh ${SINGULARITY_ROOTFS}/opt
%post
    apt-get update && apt-get install -y --no-install-recommends \
        build-essential git autoconf automake libtool
    apt-get clean && rm -rf /var/lib/apt/lists/*

    # This is specific to this image
    #   - Overwrite ld cache for libfabric and the OFI plugin
    #   - Ensures that host libfabric is used, and compatible our aws-ofi-nccl plugin
    #   - We will build aws-ofi-nccl into the /opt/slingshot/aws-ofi-nccl folder
    sed -i 's|/opt/amazon/efa/lib|/host/opt/cray/libfabric/1.22.0/lib64|g' /etc/ld.so.conf.d/efa.conf
    sed -i 's|/opt/amazon/aws-ofi-nccl/lib|/opt/slingshot/aws-ofi-nccl/lib|g' /etc/ld.so.conf.d/aws-ofi-nccl.conf
    ldconfig
%environment
    # Set NCCL environment variables
    . /opt/env_vars.sh
    export CUDA_HOME=/usr/local/cuda
    export NCCL_HOME=/opt/slingshot/nccl
    export LIBFABRIC_HOME=/host/opt/cray/libfabric/1.22.0
    export MPI_HOME=/usr/local/mpi
    export TMPDIR=/tmp
    export LD_LIBRARY_PATH=$LIBFABRIC_HOME/lib64:$NCCL_HOME/lib:/opt/slingshot/aws-ofi-nccl/lib:$LD_LIBRARY_PATH:/host/usr/lib64
%runscript
    exec "$@"

```

Click here to download the complete file: pytorch_multinode.def

Before building, also download env_vars.sh and place it in the same directory as `pytorch_multinode.def`. The build process requires this file to be present alongside the `.def` file.

We now build our .sif image:

```
$ mkdir $HOME/sif-images
$ srun --gpus=1 --time=00:30:00 apptainer build --fakeroot $HOME/sif-images/pytorch.sif pytorch_multinode.def

```

Once complete, we can create a Slurm job script to build a NCCL and `aws-ofi-nccl` inside this container:

```
#!/bin/bash
#SBATCH --job-name=build-nccl
#SBATCH --nodes=1
#SBATCH --gpus=1
#SBATCH --ntasks=1
#SBATCH --time=00:30:00
#SBATCH --output=%x-%j.out
#SBATCH --error=%x-%j.err

# Directory on host to store built libraries and binaries
mkdir $HOME/nccl_build

apptainer exec --nv \
    --bind /opt/cray/libfabric/1.22.0:/host/opt/cray/libfabric/1.22.0:ro \
    --bind /usr/lib64:/host/usr/lib64:ro \
    --bind $HOME/nccl_build:/opt/slingshot \
    $HOME/sif-images/pytorch.sif bash -c '
        export CUDA_HOME=/usr/local/cuda
        export NCCL_HOME=/lib/aarch64-linux-gnu
        export LIBFABRIC_HOME=/host/opt/cray/libfabric/1.22.0
        export MPI_HOME=/usr/local/mpi
        export TMPDIR=/tmp

        # Build nccl library
        cd /tmp && LD_LIBRARY_PATH=/lib/aarch64-linux-gnu git clone --branch "v2.29.2-1" https://github.com/NVIDIA/nccl.git
        cd /tmp/nccl && mkdir /opt/slingshot/nccl
        make -j $(nproc) install src.build BUILDDIR=/opt/slingshot/nccl NVCC_GENCODE="-gencode=arch=compute_90,code=sm_90"
        export NCCL_HOME=/opt/slingshot/nccl

        # Build hwloc library, required to build aws-ofi-nccl
        cd /tmp && LD_LIBRARY_PATH=/lib/aarch64-linux-gnu git clone --branch "v2.13" https://github.com/open-mpi/hwloc.git
        cd /tmp/hwloc && ./autogen.sh
        ./configure --disable-nvml --prefix=/opt/slingshot/hwloc
        make -j $(nproc) install

        # Build aws-ofi-nccl
        cd /tmp && LD_LIBRARY_PATH=/lib/aarch64-linux-gnu git clone --branch "v1.18.0" https://github.com/aws/aws-ofi-nccl.git
        cd /tmp/aws-ofi-nccl && ./autogen.sh
        export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/host/usr/lib64
        ./configure --prefix=/opt/slingshot/aws-ofi-nccl \
            --with-cuda=${CUDA_HOME} \
            --with-libfabric=${LIBFABRIC_HOME} \
            --with-mpi=${MPI_HOME} \
            --with-hwloc=/opt/slingshot/hwloc \
            --disable-tests
        make -j $(nproc) install

        # Build nccl-tests, if required - this is optional but useful for testing purposes
        cd /tmp && LD_LIBRARY_PATH=/lib/aarch64-linux-gnu git clone https://github.com/NVIDIA/nccl-tests.git
        cd /tmp/nccl-tests && make -j $(nproc) MPI=1
        cp -r /tmp/nccl-tests/build /opt/slingshot/nccl-tests
    '

```

Click here to download the complete file: build_nccl.sh

Now we can submit the Slurm job:

```
$ sbatch build_nccl.sh

```

When running the container, you must bind-mount the build folder, in this example `$HOME/nccl_build`, into the same folder in the container used in the build process (`/opt/slingshot` in the example) as well as the `libfabric` directory and `/usr/lib64` (containing `libcxi` to allow communication with the Slingshot Cassini NICs).

```
$ apptainer run --nv \
    --bind /opt/cray/libfabric/1.22.0:/host/opt/cray/libfabric/1.22.0:ro \
    --bind /usr/lib64:/host/usr/lib64:ro \
    --bind $HOME/nccl_build:/opt/slingshot \
    $HOME/sif-images/pytorch.sif bash

```

## Benchmark NCCL in a container with nccl-tests

If you used NCCL and `aws-ofi-nccl` provided by the host system, you can follow the steps from our Apptainer Multi-node guide to run `nccl-tests`.

If you followed the Build NCCL in a container step, you can run the NCCL All Reduce benchmark between two compute nodes:

```
#!/bin/bash
#SBATCH --job-name=bench-nccl
#SBATCH --nodes=2
#SBATCH --gpus=8
#SBATCH --time=00:10:00
#SBATCH --output=%x-%j.out
#SBATCH --error=%x-%j.err

srun --nodes=2 \
    --gpus=8 \
    --cpus-per-task=72 \
    --ntasks-per-node=1 \
    --network=disable_rdzv_get \
    --mpi=pmi2 \
    apptainer exec --nv \
    --bind /opt/cray/libfabric/1.22.0:/host/opt/cray/libfabric/1.22.0:ro \
    --bind /usr/lib64:/host/usr/lib64:ro \
    --bind $HOME/nccl_build:/opt/slingshot \
    $HOME/sif-images/pytorch.sif /opt/slingshot/nccl-tests/all_reduce_perf -b 32KB -e 8GB -f 2 -g 4

```

Click here to download the complete file: bench_nccl.sh

## Resources

- Official NCCL documentation
- Demystifying NCCL: An In-depth Analysis of GPU Communication Protocols and Algorithms
