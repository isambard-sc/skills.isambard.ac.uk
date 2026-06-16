# Apptainer on Isambard

Apptainer (formerly Singularity) is available on all Isambard login and compute nodes.

> **Name note:** Isambard-AI Phase 2 has `apptainer`; Isambard 3 has `singularity`.
> The commands are compatible — substitute `singularity` for `apptainer` on Isambard 3.
> See [Apptainer/Singularity compatibility docs](https://apptainer.org/docs/user/1.0/singularity_compatibility.html).

Apptainer's native image format is the **SIF file** (`.sif`). SIF images are single files
on the shared filesystem — no migration step needed; they're usable on any node immediately.

---

## Pulling and Building Images

Images are pulled from OCI registries and converted to SIF format:

```bash
mkdir $HOME/sif-images && cd $HOME/sif-images

# From Docker Hub
apptainer build ubuntu.sif docker://ubuntu
apptainer build ubuntu_jammy.sif docker://ubuntu:jammy

# From NGC (use nvcr.io registry)
apptainer build pytorch.sif docker://nvcr.io/nvidia/pytorch:25.05-py3

# From Quay.io
apptainer build myimage.sif docker://quay.io/someorg/someimage:tag
```

> **aarch64 only.** Choose tags that support `linux/arm64` on the registry.

---

## Running Containers

```bash
# Run the container's default entrypoint/runscript
apptainer run image.sif

# Run a specific command
apptainer exec image.sif <command> [args...]

# Interactive shell (current directory is bind-mounted automatically)
apptainer shell image.sif
# Apptainer> exit
```

`$HOME` is bind-mounted into the container by default — files created inside persist on the host.
See [Apptainer bind paths docs](https://docs.sylabs.io/guides/latest/user-guide/bind_paths_and_mounts.html)
for customising mounts.

---

## Submitting Apptainer Jobs via Slurm

```bash
#!/bin/bash
#SBATCH --job-name=apptainer-test
#SBATCH --output=apptainer-test.out
#SBATCH --gpus=1        # one GH200 (also allocates 72 CPU cores + 115 GB memory)
#SBATCH --ntasks=1
#SBATCH --time=1
#SBATCH --mem-per-cpu=1G
#SBATCH --cpus-per-task=1

apptainer exec lolcow.sif cowsay moo
```

```bash
sbatch myjob.sbatch
```

---

## GPU Access with `--nv`

```bash
# Build a CUDA image
apptainer build cuda.sif docker://nvcr.io/nvidia/cuda:12.5.0-devel-ubuntu22.04

# Run with GPU access (--nv exposes NVIDIA drivers)
srun --gpus=1 --ntasks=1 --time=1 \
    apptainer exec --nv cuda.sif nvidia-smi --list-gpus
```

The `--nv` flag mounts NVIDIA drivers and CUDA libraries from the host into the container.
See [Apptainer GPU support docs](https://apptainer.org/docs/user/1.0/gpu.html).

---

## Rootless Builds with `--fakeroot`

User accounts on Isambard are configured for Linux user namespace mapping, allowing `--fakeroot`
mode. This lets an unprivileged user act as root inside the container — required for installing
packages during a build.

### Start a root shell in an existing image

```bash
apptainer pull ubuntu.sif docker://index.docker.io/library/ubuntu:latest
apptainer shell --fakeroot ubuntu.sif
# Apptainer> whoami  → root
```

### Build from a definition file with root privileges

Create a definition file (e.g. `ubuntu-htop.def`):

```
Bootstrap: docker
Registry: index.docker.io
From: library/ubuntu:latest

%post
    apt-get update
    apt-get install --assume-yes --no-install-recommends htop
```

Build and run:

```bash
apptainer build --fakeroot ubuntu-htop.sif ubuntu-htop.def

# Run without --fakeroot (standard user is fine for execution)
apptainer shell ubuntu-htop.sif
# Apptainer> htop
```

See [Apptainer definition files docs](https://apptainer.org/docs/user/latest/definition_files.html)
for the full definition file format.

---

## Multi-node: `brics/apptainer-multi-node`

For multi-node jobs, load the BriCS module first:

```bash
module load brics/apptainer-multi-node
```

This sets `APPTAINER_BINDPATH` to mount the Slingshot 11 MPI/NCCL libraries at `/host/`
inside the container.

**You must `source /host/adapt.sh`** inside every container instance for the environment
to be configured. Two patterns:

**Pattern 1: Interactive shell**
```bash
apptainer run --nv ubuntu_latest.sif
# Apptainer> source /host/adapt.sh
```

**Pattern 2: Pass as entrypoint to `exec` (for `srun` jobs)**
```bash
apptainer exec --nv --bind $PWD:$PWD pytorch.sif /host/adapt.sh bash -c "your_command"
```

If your container already has a runscript/entrypoint, run it manually:
```bash
Apptainer> /.singularity.d/runscript
```

### Verify MPI is correctly configured

```bash
apptainer exec --nv ubuntu_latest.sif /host/adapt.sh bash
# Apptainer> which mpicc       → /host/openmpi/bin/mpicc
# Apptainer> mpicc -show       → shows correct include/lib paths
# Apptainer> ompi_info         → shows OpenMPI build details
```

Note: you need your own C compiler (`gcc`) or a container image that includes one.

### Multi-node nccl-tests Example

```bash
# 1. Pull image and clone benchmark source
apptainer pull docker://nvcr.io/nvidia/pytorch:25.05-py3
git clone https://github.com/NVIDIA/nccl-tests.git

# 2. Build nccl-tests inside container (using host MPI/NCCL)
apptainer exec --nv --bind $TMPDIR pytorch_25.05-py3.sif /host/adapt.sh bash
# Apptainer> cd nccl-tests/
# Apptainer> make -j 72 MPI=1 NCCL_HOME=/host/nccl MPI_HOME=/host/openmpi CUDA_HOME=/usr/local/cuda
# Apptainer> exit

# 3. Run across 2 nodes (4 GPUs per node = 8 total)
srun --nodes=2 --gpus=8 --ntasks-per-node 1 --cpus-per-task 72 \
    apptainer exec --nv --bind $PWD:$PWD pytorch_25.05-py3.sif \
    /host/adapt.sh bash -c "nccl-tests/build/all_reduce_perf -b 32KB -e 8GB -f 2 -g 4"
```

Expected peak `busbw`: ~90 GB/s across 8 GPUs over 2 nodes (higher than Podman-HPC due
to Apptainer's direct binding approach).

---

## Slingshot 11 Host Libraries (mounted at `/host/`)

| Path | Contents |
|------|---------|
| `/host/openmpi/` | OpenMPI built for Slingshot 11 |
| `/host/nccl/` | NCCL built against libfabric |
| `/host/adapt.sh` | Environment setup script — **must be sourced** |

---

## Resources

- [Apptainer and MPI](https://apptainer.org/docs/user/1.0/mpi.html)
- [Introduction to MPI with containers](https://permedcoe.github.io/mpi-in-container/)
- [Apptainer definition files](https://apptainer.org/docs/user/latest/definition_files.html)
- [Apptainer GPU support](https://apptainer.org/docs/user/1.0/gpu.html)
