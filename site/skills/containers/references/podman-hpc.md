# Podman-HPC on Isambard

Podman-HPC (`podman-hpc`) is a wrapper around Podman providing HPC-specific configuration.
It exposes all standard Podman subcommands plus HPC-specific ones.

## HPC-Specific Subcommands

| Subcommand | Purpose |
|-----------|---------|
| `podman-hpc pull` | Pull image and automatically migrate it to `$SCRATCH` as squashfs |
| `podman-hpc migrate <image>` | Convert a locally-built image to squashfs on `$SCRATCH` |
| `podman-hpc images` | List images; `R/O = true` means migrated to `$SCRATCH` (usable on compute nodes) |
| `podman-hpc rmsqi` | Remove a squashed image |
| `podman-hpc infohpc` | Dump HPC configuration info |

> **Always use `podman-hpc`, not `podman` directly.** The wrapper is required to run
> migrated/squashed images on compute nodes.

---

## The Migrate Requirement

Images built locally exist only on the login node's local filesystem. To run on a compute node,
they must be migrated to shared `$SCRATCH` storage as a squashfs image:

```bash
podman-hpc migrate my_container
```

Images pulled with `podman-hpc pull` are **migrated automatically**. Only manually-built images
need explicit migration.

Check migration status with `podman-hpc images` — `R/O = true` = migrated and ready.

---

## Example: Pull and Run

```bash
# Pull (auto-migrates to $SCRATCH)
podman-hpc pull quay.io/podman/hello

# Check images — R/O=true means ready for compute nodes
podman-hpc images

# Run on login node
podman-hpc run quay.io/podman/hello

# Run on a compute node
srun --nodes 1 podman-hpc run quay.io/podman/hello
```

---

## Example: Build a Custom Image

```bash
# Write a Containerfile (or Dockerfile)
cat > Containerfile << 'EOF'
FROM docker.io/ubuntu:latest
ENTRYPOINT ["echo", "Hello, World!"]
EOF

# Build
podman-hpc build . --tag my_container

# Test locally
podman-hpc run my_container:latest

# Migrate before running on compute nodes
podman-hpc migrate my_container

# Now run on compute node
srun --nodes 1 podman-hpc run my_container:latest
```

> **Back up your images!** Login node local storage is erased at end of session.
> Push to Docker Hub before logging out:
> ```bash
> podman-hpc login docker.io
> podman-hpc push my_container:latest docker.io/<USERNAME>/my_container:latest
> ```

---

## Example: GPU Access

```bash
# Using explicit device flag (all GPUs)
srun --nodes 1 --gpus=4 podman-hpc run --device=nvidia.com/gpu=all ubuntu:latest nvidia-smi --list-gpus

# Shorthand flag
srun --nodes 1 --gpus=4 podman-hpc run --gpu ubuntu:latest nvidia-smi --list-gpus
```

---

## Multi-node: `--openmpi-pmi2`

The `--openmpi-pmi2` flag mounts host NCCL, OpenMPI, and PMI2 into the container and sets
an entrypoint script at `/host/adapt.sh` that configures the environment.

**Important:** The entrypoint script replaces the container's default entrypoint. If your
container has its own entrypoint, run it manually after `/host/adapt.sh`, or suppress the
adaptation with `--entrypoint=`.

### Building inside a container against host MPI/NCCL

```bash
# Pull the NGC PyTorch container (aarch64)
podman-hpc pull nvcr.io/nvidia/pytorch:25.05-py3

# Clone the benchmark source
git clone https://github.com/NVIDIA/nccl-tests.git
cd nccl-tests

# Build inside container, mounting current directory
podman-hpc run -it --rm --openmpi-pmi2 -v $PWD:$PWD -w $PWD \
    nvcr.io/nvidia/pytorch:25.05-py3 bash
# Inside container:
# make -j 8 MPI=1 NCCL_HOME=/host/nccl MPI_HOME=/host/openmpi CUDA_HOME=/usr/local/cuda
# exit
```

Flags used:
- `-it` — interactive
- `--rm` — remove container on exit
- `--openmpi-pmi2` — mount host MPI/NCCL/PMI2
- `-v $PWD:$PWD` — mount working directory at same path
- `-w $PWD` — set working directory inside container
- `bash` — needed for entrypoint script to run interactively

### Running the multi-node job

```bash
export ALL_REDUCE_BIN=$PWD/build/all_reduce_perf

srun -N 2 --gpus=8 --mpi=pmi2 --cpus-per-task 72 --ntasks-per-node 1 \
    podman-hpc run --openmpi-pmi2 --gpu -v $PWD:$PWD -w $PWD \
    nvcr.io/nvidia/pytorch:25.05-py3 \
    ${ALL_REDUCE_BIN} -b 32KB -e 8GB -f 2 -g 4
```

Key Slurm flag: `--mpi=pmi2` — required for Slurm to interface with PMI2.

Expected peak `busbw`: ~74 GB/s across 8 GPUs over 2 nodes.

---

## Slingshot 11 Host Libraries (mounted at `/host/`)

| Path | Contents |
|------|---------|
| `/host/openmpi/` | OpenMPI built for Slingshot 11 |
| `/host/nccl/` | NCCL built against libfabric |
| `/host/adapt.sh` | Environment setup script |
