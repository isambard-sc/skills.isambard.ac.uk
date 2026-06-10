# Building NCCL from Source (Bare-metal)

Use these instructions when you need a specific NCCL version on the host system,
or to build `nccl-tests` for bandwidth benchmarking.

Prerequisites: `module load cudatoolkit PrgEnv-gnu`

---

## 1. Build NCCL

```bash
module load cudatoolkit PrgEnv-gnu

git clone --branch "v2.27.7-1" https://github.com/NVIDIA/nccl.git
cd nccl
mkdir build
make -j 8 src.build PREFIX=$(realpath build)
```

The built library lands in `nccl/build/`. Note the path — it is needed for the steps below.

---

## 2. Build `aws-ofi-nccl`

`aws-ofi-nccl` is the plugin that enables NCCL to use Slingshot 11 RDMA via `libfabric`.
It depends on CUDA and libfabric. Always use a tag ending in `-aws`.

```bash
module load cudatoolkit PrgEnv-gnu

git clone --branch "v1.7.x-aws" https://github.com/aws/aws-ofi-nccl.git
cd aws-ofi-nccl
./autogen.sh

export LIBFABRIC_HOME=/opt/cray/libfabric/1.22.0
export CC=/usr/bin/gcc-12
export CXX=/usr/bin/g++-12

mkdir build
./configure \
    --prefix=$(realpath build) \
    --with-cuda=${CUDA_HOME} \
    --with-libfabric=${LIBFABRIC_HOME} \
    --disable-tests
make -j 8 install
```

---

## 3. Build `nccl-tests`

`nccl-tests` provides collective benchmarks (all-reduce, all-gather, etc.) and depends
on MPI, NCCL, and CUDA.

```bash
module load cudatoolkit PrgEnv-gnu

git clone https://github.com/NVIDIA/nccl-tests.git
cd nccl-tests

export MPI_HOME=/opt/cray/pe/mpich/8.1.32/ofi/gnu/12.3/
export NCCL_HOME=$(realpath ../nccl/build)   # adjust to your NCCL build path

make -j 8 MPI=1 MPI_HOME=${MPI_HOME} NCCL_HOME=${NCCL_HOME} CUDA_HOME=${CUDA_HOME}
```

---

## 4. Run the Benchmark

### Without `aws-ofi-nccl` (baseline — expect very slow)

```bash
srun --nodes 2 --gpus 8 --network=disable_rdzv_get \
    nccl-tests/build/all_reduce_perf -b 32KB -e 8GB -f 2 -g 4
```

Expected: ~2.3 GB/s bus bandwidth — NCCL is using TCP sockets, not RDMA.

### With `aws-ofi-nccl` + Slingshot env vars (full performance)

```bash
# Add the plugin to the library path
export LD_LIBRARY_PATH=$(realpath aws-ofi-nccl/build/lib):$LD_LIBRARY_PATH

# Source all Slingshot NCCL environment variables
# Download from: https://docs.isambard.ac.uk/user-documentation/guides/example-data/nccl/env_vars.sh
source env_vars.sh

srun --nodes 2 --gpus 8 --cpus-per-task 72 --network=disable_rdzv_get \
    nccl-tests/build/all_reduce_perf -b 32KB -e 8GB -f 2 -g 4
```

Expected: ~163 GB/s bus bandwidth (8 × GH200 across 2 nodes).

If you still see low bandwidth after adding the plugin:
1. Check `NCCL_DEBUG=INFO` output for the transport selected
2. Confirm `NCCL_NET="AWS Libfabric"` is set
3. Confirm the `aws-ofi-nccl` `.so` is on `LD_LIBRARY_PATH` and was built against
   the correct `libfabric` version
