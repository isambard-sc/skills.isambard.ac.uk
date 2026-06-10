# NCCL in Containers on Isambard

Two approaches, depending on whether your container's CUDA runtime matches the host.

---

## Option A: Use Host NCCL (simplest)

If your container is compatible with the host CUDA runtime, use the `brics/apptainer-multi-node`
module, which injects the host NCCL and `aws-ofi-nccl` into the container automatically:

```bash
module load brics/apptainer-multi-node
```

Then follow the [Apptainer Multi-node guide](https://docs.isambard.ac.uk/user-documentation/guides/containers/apptainer-multi-node/)
to run `nccl-tests`. No custom NCCL build required.

---

## Option B: Build NCCL Inside a Container (custom CUDA runtime)

Use this when your container (e.g. an NGC PyTorch image) bundles a **newer CUDA runtime**
than the host provides. In that case you must build NCCL and `aws-ofi-nccl` against the
container's CUDA inside the container, then bind-mount the built libraries at runtime.

The built libraries live on the **host filesystem** (mounted into the container) — they
are not baked into the image.

### Step 1: Create the Apptainer definition file

Download template:
`https://docs.isambard.ac.uk/user-documentation/guides/example-data/apptainer/pytorch_multinode.def`

Also download the env vars script and place it alongside the `.def` file:
`https://docs.isambard.ac.uk/user-documentation/guides/example-data/nccl/env_vars.sh`

The definition file (based on NGC PyTorch 26.01) does the following:
- Copies `env_vars.sh` into `/opt/` inside the container
- Patches the `ld.so.conf.d` entries to use host `libfabric` and the custom `aws-ofi-nccl`
  build (replacing any pre-existing AWS EFA paths from the NGC image)
- Sets `CUDA_HOME`, `NCCL_HOME`, `LIBFABRIC_HOME`, and `LD_LIBRARY_PATH` in `%environment`

Key `%environment` block:
```
export NCCL_HOME=/opt/slingshot/nccl
export LIBFABRIC_HOME=/host/opt/cray/libfabric/1.22.0
export MPI_HOME=/usr/local/mpi
export LD_LIBRARY_PATH=$LIBFABRIC_HOME/lib64:$NCCL_HOME/lib:/opt/slingshot/aws-ofi-nccl/lib:$LD_LIBRARY_PATH:/host/usr/lib64
```

### Step 2: Build the SIF image

Requires a GPU node (for CUDA access during build):

```bash
mkdir $HOME/sif-images
srun --gpus=1 --time=00:30:00 \
    apptainer build --fakeroot $HOME/sif-images/pytorch.sif pytorch_multinode.def
```

### Step 3: Build NCCL and `aws-ofi-nccl` inside the container

Download the build job script:
`https://docs.isambard.ac.uk/user-documentation/guides/example-data/apptainer/build_nccl.sh`

This Slurm job script runs inside the container and builds:
1. NCCL (`v2.29.2-1`) — targeting `compute_90` (GH200)
2. `hwloc` (`v2.13`) — required by `aws-ofi-nccl`
3. `aws-ofi-nccl` (`v1.18.0`) — against container CUDA + host libfabric
4. `nccl-tests` (optional, for benchmarking)

All outputs land in `$HOME/nccl_build/` on the host filesystem (bind-mounted as
`/opt/slingshot` inside the container during the build).

Key bind mounts used during the build:
```bash
--bind /opt/cray/libfabric/1.22.0:/host/opt/cray/libfabric/1.22.0:ro
--bind /usr/lib64:/host/usr/lib64:ro
--bind $HOME/nccl_build:/opt/slingshot
```

Submit the build job:
```bash
sbatch build_nccl.sh
```

### Step 4: Run the container

Every time you run the container you must bind-mount the same three directories:

```bash
apptainer run --nv \
    --bind /opt/cray/libfabric/1.22.0:/host/opt/cray/libfabric/1.22.0:ro \
    --bind /usr/lib64:/host/usr/lib64:ro \
    --bind $HOME/nccl_build:/opt/slingshot \
    $HOME/sif-images/pytorch.sif bash
```

| Bind mount | Why it's needed |
|-----------|----------------|
| `/opt/cray/libfabric/1.22.0` | Host libfabric for Slingshot 11 |
| `/usr/lib64` | `libcxi` — Slingshot Cassini NIC driver |
| `$HOME/nccl_build` | Your custom-built NCCL + aws-ofi-nccl |

### Step 5: Benchmark with nccl-tests

Download the benchmark Slurm script:
`https://docs.isambard.ac.uk/user-documentation/guides/example-data/apptainer/bench_nccl.sh`

```bash
#!/bin/bash
#SBATCH --job-name=bench-nccl
#SBATCH --nodes=2
#SBATCH --gpus=8
#SBATCH --time=00:10:00
#SBATCH --output=%x-%j.out
#SBATCH --error=%x-%j.err

srun --nodes 2 --gpus 8 --cpus-per-task 72 --ntasks-per-node 1 \
    --network=disable_rdzv_get --mpi=pmi2 \
    apptainer exec --nv \
        --bind /opt/cray/libfabric/1.22.0:/host/opt/cray/libfabric/1.22.0:ro \
        --bind /usr/lib64:/host/usr/lib64:ro \
        --bind $HOME/nccl_build:/opt/slingshot \
        $HOME/sif-images/pytorch.sif \
        /opt/slingshot/nccl-tests/all_reduce_perf -b 32KB -e 8GB -f 2 -g 4
```

```bash
sbatch bench_nccl.sh
```

Expected: ~163 GB/s bus bandwidth (8 × GH200 across 2 nodes).

Note `--mpi=pmi2` — required when using OpenMPI (as provided in NGC containers) with Slurm.

---

## Troubleshooting

**`NCCL WARN Error: network AWS Libfabric not found`**
— `aws-ofi-nccl` is not on `LD_LIBRARY_PATH`, or the `.so` path is wrong.
Check the `%environment` block in the `.def` file and the bind mounts at runtime.

**Low bandwidth (~2 GB/s) despite bind mounts**
— The `aws-ofi-nccl` plugin may have been built against the wrong `libfabric`.
Confirm `LIBFABRIC_HOME` points to the host's `/opt/cray/libfabric/` during the build,
not an EFA path from the NGC image.

**Build fails on `hwloc`**
— Ensure `autoconf`, `automake`, and `libtool` are installed inside the container
(the `.def` file's `%post` section installs them via `apt-get`).
