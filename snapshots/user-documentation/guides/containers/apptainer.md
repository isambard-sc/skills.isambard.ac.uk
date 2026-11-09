<!-- Snapshot of https://docs.isambard.ac.uk/user-documentation/guides/containers/apptainer/ made by snapshot_docs.py. Do not edit. -->

# Apptainer (formerly Singularity)

Apptainer is available on Isambard-AI and Isambard 3 login and compute nodes.

Apptainer vs Singularity

Note that Isambard-AI Phase 2 has `apptainer`, while Isambard 3 has `singularity`.

Apptainer is a rename of the popular containerisation software. Read the documentation on compatibility between them here: Apptainer Compatibility with Singularity.

## Pulling & Building Images with Apptainer

Apptainer can pull and build images from many registries, first let's look at pulling and building an Apptainer image from Docker Hub:

```
$ mkdir $HOME/sif-images
$ cd $HOME/sif-images
$ apptainer build lolcow.sif docker://sylabsio/lolcow
$ file lolcow.sif
lolcow.sif: a /usr/bin/env run-singularity script executable (binary data)

```

You will see that the image `lolcow.sif` has been built. Apptainer's native image format is the read-only Singularity Image File (.sif) file.

Apptainer can also pull other images from Docker Hub. Let's see what happens when we build the Ubuntu image from Docker Hub:

```
$ apptainer build ubuntu.sif docker://ubuntu
$ file ubuntu.sif
ubuntu.sif: a /usr/bin/env run-singularity script executable (binary data)

```

This pulls a Docker (OCI) image from Docker Hub and converts it to a SIF image, suitable for running using `apptainer`.

By default, if you don't specify a tag the `latest` image will be pulled. You can pull images by their tag like so:

```
$ apptainer build ubuntu_jammy.sif docker://ubuntu:jammy

```

This pulls and builds the newest Ubuntu image that has been tagged with `jammy`.

Using containers from other registries

Apptainer can pull containers from other OCI container registries such as Quay.io by adding the registry address to the `docker://` URI. See the Apptainer documentation on Support for Docker and OCI Containers for details.

## Running Apptainer Containers

Let's try running the lolcow Apptainer container. The command `apptainer run` invokes the runscript of a container (provided it exists), try:

```
$ apptainer run lolcow.sif

```

you will see something like the following:

```
 _____________________________
< Thu Jul 4 15:23:31 UTC 2024 >
 -----------------------------
        \   ^__^
         \  (oo)\_______
            (__)\       )\/\
                ||----w |
                ||     ||

```

To run a custom command in an Apptainer container, we have to use the command `apptainer exec`. Try the following:

```
$ apptainer exec lolcow.sif cowsay moo
 _____
< moo >
 -----
        \   ^__^
         \  (oo)\_______
            (__)\       )\/\
                ||----w |
                ||     ||

```

So far in this example we have been running Apptainer on the login node, we can run the above example on Isambard-AI on one of the compute nodes using the following batch script:

lolcow.sbatch
```
#!/bin/bash

#SBATCH --job-name=apptainer-test
#SBATCH --output=apptainer-test.out
#SBATCH --gpus=1    # one Grace Hopper, this also allocates 72 CPU cores and 115GB memory
#SBATCH --ntasks=1
#SBATCH --time=1
#SBATCH --mem-per-cpu=1G
#SBATCH --cpus-per-task=1

apptainer exec lolcow.sif cowsay moo

```

If the above batch script is named `lolcow.sbatch`, then you can submit the job and check the output as follows:

```
$ sbatch lolcow.sbatch
$ cat apptainer-test.out
 _____
< moo >
 -----
        \   ^__^
         \  (oo)\_______
            (__)\       )\/\
                ||----w |
                ||     ||

```

Please see the Slurm documentation for more details on job submission.

## Apptainer Shell

You can start a shell in your container, using the `apptainer shell` command, like so:

```
$ apptainer shell ubuntu.sif 
Apptainer> 

```

You will see the `Apptainer>` prompt, indicating we are inside the container. Try running:

```
Apptainer> ls
lolcow.sbatch lolcow.sif  ubuntu_jammy.sif  ubuntu.sif

```

We can see the files in the current working directory that we launched the container shell from. Try running:

```
Apptainer> grep PRETTY /etc/os-release
PRETTY_NAME="Ubuntu 24.04 LTS"

```

This shows the OS of the container, confirming that we are inside the container.

You can also create new files that will persist on your local filesystem. Try using `touch` to create a new file:

```
Apptainer> touch myfile.txt

```

To exit the container, run:

```
Apptainer> exit

```

If you now run `ls`, you will see that the file `myfile.txt` has persisted.

So what's happening here? Apptainer binds some of the directories from the host machine to the container, including the $HOME directory. This is why `myfile.txt` exists even after you have exited the container.

For details on which paths are bound into Apptainer containers by default and how to customise bind mounting, see the Apptainer documentation on Bind Paths and Mounts.

## Using GPUs with Apptainer

Apptainer works with GPUs out-of-the-box, and you can use Nvidia containers available on Nvidia GPU Cloud:

build_cuda_container.sh
```
#!/bin/bash

apptainer build cuda_12.5.0-devel-ubuntu22.04.sif docker://nvcr.io/nvidia/cuda:12.5.0-devel-ubuntu22.04
file cuda_12.5.0-devel-ubuntu22.04.sif

```

Example output:

```
cuda_12.5.0-devel-ubuntu22.04.sif: a /usr/bin/env run-singularity script executable (binary data)

```

To access GPUs inside your Apptainer container, simply add the `--nv` flag. Try running the following on Isambard-AI on one of the compute nodes using `srun` and `apptainer exec`:

run_cuda_container.sh
```
#!/bin/bash

srun --gpus=1 --ntasks=1 --time=1 apptainer exec --nv cuda_12.5.0-devel-ubuntu22.04.sif nvidia-smi --list-gpus

```

Example output:

```
GPU 0: GH200 120GB (UUID: GPU-4acc6b4e-152a-8a52-5a31-2c4be6fe2d11)

```

For details on how the `--nv` flag works, see the Apptainer documentation on GPU Support

## Building and running containers in rootless mode using `--fakeroot`

User accounts on Isambard-AI and Isambard 3 are configured to allow Linux user namespace mapping of user and group IDs. This allows Apptainer to be run in "rootless" mode, where a user can use different user and group IDs within a running container to those they can access outside of the container.

A key use of rootless mode is to allow a unprivileged (standard) user to run a container as root (user ID 0) and perform actions that require administrative privileges, such as installing packages within the container. This is often necessary when building containers from Apptainer definition files.

To use Apptainer in rootless mode, simply add the `--fakeroot` flag to the `apptainer` commands, as shown in the following examples.

### Example 1: Start a root shell in a container from an existing image

Pull the latest official Ubuntu image from Docker Hub and convert to SIF format

```
apptainer pull ubuntu.sif docker://index.docker.io/library/ubuntu:latest

```

Start a root shell in the container using the `--fakeroot` option

```
$ apptainer shell --fakeroot ubuntu.sif

```

```
Apptainer> whoami
root

```

### Example 2: Build a container image from a definition file with root privileges

Create an Apptainer definition file that requires root privileges to build, e.g. install the `htop` package into the latest official Ubuntu image from Docker Hub

ubuntu-htop.def
```
Bootstrap: docker
Registry: index.docker.io
From: library/ubuntu:latest

%post
apt-get update
apt-get install --assume-yes --no-install-recommends htop

```

Build a container image from the definition file, using `--fakeroot` to run the build as root

```
$ apptainer build --fakeroot ubuntu-htop.sif ubuntu-htop.def

```

`htop` can be run from a standard user shell in the container (without `--fakeroot`)

```
$ apptainer shell ubuntu-htop.sif

```

```
Apptainer> htop

```

## Multi-node apptainer Containers

See the guide on using Apptainer across multiple nodes for specific guidance on obtaining good performance when running Apptainer over multiple nodes.
