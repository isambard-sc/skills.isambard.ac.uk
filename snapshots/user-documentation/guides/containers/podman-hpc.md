<!-- Snapshot of https://docs.isambard.ac.uk/user-documentation/guides/containers/podman-hpc/ made by snapshot_docs.py. Do not edit. -->

# Podman-HPC

## Introduction

Podman is a daemonless, open source, Linux native tool designed to make it easy to find, run, build, share and deploy applications using Open Containers Initiative (OCI) Containers and Container Images.

For ease of management of OCI containers in an HPC environment, Podman-HPC has been adopted for use on Isambard systems. Podman-HPC (`podman-hpc`) is a wrapper script around Podman (`podman`), which provides HPC specific configuration and infrastructure for the Podman ecosystem.

## Podman-HPC Specific Subcommands

Podman-HPC exposes all available Podman subcommands and arguments, and additionally provides specific subcommands for managing containers and container images in an HPC environment:

```
$ podman-hpc --help
Manage pods, containers and images ... on HPC!

Description:
  The podman-hpc utility is a wrapper script around the podman container
  engine. It provides additional subcommands for ease of use and
  configuration of podman in a multi-node, multi-user high performance
  computing environment.

Usage: podman-hpc [options] COMMAND [ARGS]...

Options:
  --additional-stores TEXT  Specify other storage locations
  --squash-dir TEXT         Specify alternate squash directory location
  --help                    Show this message and exit.

Commands:
  infohpc     Dump configuration information for podman_hpc.
  migrate     Migrate an image to squashed.
  pull        Pulls an image to a local repository and makes a squashed...
  rmsqi       Removes a squashed image.
  shared-run  Launch a single container and exec many threads in it This is...

```

## Preparing Locally Built Images to Run on Compute Nodes

When Podman-HPC builds a container image, it is written out to a local filesystem. To run a container image on a different node from where it was built, it must be moved to a shared filesystem.

System Storage

Ensure you are familiar with the System Storage specifications to support your understanding of how a container image is migrated from the login node to the compute node.

In particular it is important be aware that node-local scratch storage is not persistent.

This can be achieved with the `podman-hpc migrate` subcommand (not to be confused the Podman `podman system migrate` command) to convert it to a squashfs container image, which will be written out to your `$SCRATCH` directory. Please see the example below for running a container on a compute node.

To see which images you have available as squashfs on `$SCRATCH` you can run `podman-hpc images`, the `R/O` column will be `true` where images are migrated to `$SCRATCH` storage.

Images which you pulled using `podman-hpc pull` will already have a squashfs copy put onto `$SCRATCH`.

Don't use `podman`

Once an image has been migrated it can be run on any compute node using the `podman-hpc` wrapper. Remember to always use the `podman-hpc` wrapper and not `podman` directly as the wrapper is needed to run containers which have been migrated.

## Example: Pulling and Running Images

```
$ podman-hpc pull quay.io/podman/hello
Trying to pull quay.io/podman/hello:latest...
Getting image source signatures
Copying blob 1ff9adeff444 done  
Copying config 83fc7ce122 done  
Writing manifest to image destination
Storing signatures
83fc7ce1224f5ed3885f6aaec0bb001c0bbb2a308e3250d7408804a720c72a32
INFO: Migrating image to /scratch/brics/<user-name>/storage

```

We can now run `podman-hpc images` to list the currently available images. Since pulling an image will automatically migrate it to your `$SCRATCH` directory, we can see `true` on the `R/O` (read-only) column, `true` means the image has been migrated to `$SCRATCH` or shared storage:

```
$ podman-hpc images
REPOSITORY                TAG                               IMAGE ID      CREATED       SIZE        R/O
quay.io/podman/hello      latest                            83fc7ce1224f  4 months ago  580 kB      false
quay.io/podman/hello      latest                            83fc7ce1224f  4 months ago  580 kB      true

```

We can now run this container, which will automatically execute the entrypoint:

```
$ podman-hpc run quay.io/podman/hello 
!... Hello Podman World ...!

         .--"--.           
       / -     - \         
      / (O)   (O) \        
   ~~~| -=(,Y,)=- |         
    .---. /`  \   |~~      
 ~/  o  o \~~~~.----. ~~   
  | =(X)= |~  / (O (O) \   
   ~~~~~~~  ~| =(Y_)=-  |   
  ~~~~    ~~~|   U      |~~ 

```

## Example: Building and pushing images

To build a custom container, we can create a `Containerfile` (or `Dockerfile`). For example, here's a "Hello, World!" Containerfile based on the latest version of ubuntu:

```
FROM docker.io/ubuntu:latest

ENTRYPOINT ["echo", "Hello, World!"]

```

In the directory where your Containerfile exists, you can build the container and execute as following, adding the `--tag` flag to tag your container's name:

```
$ podman-hpc build . --tag my_container
STEP 1/3: FROM ubuntu:latest
STEP 2/3: ENV "PODMANHPC_MODULES_DIR"="/etc/podman_hpc/modules.d"
--> 13a3c609ddd
STEP 3/3: ENTRYPOINT ["echo", "Hello, World!"]
COMMIT my_container
--> 4265376f573
Successfully tagged localhost/my_container:latest
4265376f5735af8eab16f06d204edb8be4d89bc1a520f3fcf13ab38569a03eb2

$ podman-hpc images
REPOSITORY                TAG                               IMAGE ID      CREATED       SIZE        R/O
localhost/my_container    latest                            4265376f5735  18 seconds ago  103 MB      false

$ podman-hpc run my_container:latest
Hello, World!

```

Note that your image currently only resides on the login node and needs to be migrated before running on the compute nodes.

Docker hub account

To backup your container images you must first have an account on Docker hub. Sign up using this link.

Before doing so we highly recommend pushing your images to a repository to back them up, since your local storage will be erased at the end of your login.

To do so we will first login to docker.io:

```
$ podman-hpc login docker.io
Username: <USERNAME>
Password: 
Login Succeeded!

```

We can then push our image to our personal container registry like so:

```
$ podman-hpc push my_container:latest docker.io/<USERNAME>/my_container:latest
Getting image source signatures
Copying blob 5b17151e9710 skipped: already exists  
Copying config a71e464f1a done  
Writing manifest to image destination
Storing signatures

```

## Example: Migrating and Running on a Compute node

Let's try and run our recently built image on a compute node using `srun`:

```
$ srun --nodes=1 podman-hpc run localhost/my_container:latest
Trying to pull localhost/my_container:latest...
Error: initializing source docker://localhost/my_container:latest: pinging container registry localhost: Get "https://localhost/v2/": dial tcp [::1]:443: connect: connection refused
[...]

```

You can see that podman-hpc is interpreting localhost as a host for a registry which does not exist. Let's migrate our image first then run our container:

```
$ podman-hpc images
REPOSITORY                TAG                               IMAGE ID      CREATED       SIZE        R/O
localhost/my_container    latest                            4265376f5735  18 seconds ago  103 MB      false
$ podman-hpc migrate my_container

```

After migrating your container, you can see `R/O` is set as true, and we can successfully run our container on a compute node:

```
$ podman-hpc images
REPOSITORY                TAG                               IMAGE ID      CREATED       SIZE        R/O
localhost/my_container    latest                            4265376f5735  18 seconds ago  103 MB      false
localhost/my_container    latest                            4265376f5735  18 seconds ago  103 MB      true
$ srun --nodes=1 podman-hpc run my_container:latest
srun: job 23835 queued and waiting for resources
srun: job 23835 has been allocated resources
Hello, World!

```

## Example: Using a GPU

To expose GPUs to your container you can use the flag `--device=nvidia.com/gpu=all` to pass all the available GPUs to the container

podman_hpc_gpu_device.sh
```
#!/bin/bash

podman-hpc pull ubuntu:latest
srun --nodes=1 --gpus=4 podman-hpc run --device=nvidia.com/gpu=all ubuntu:latest nvidia-smi --list-gpus

```

Example output:

```
GPU 0: GH200 120GB (UUID: GPU-0f0087e6-4361-40a9-1238-b0315bbf3aba)
GPU 1: GH200 120GB (UUID: GPU-2d90c7dc-ef64-9248-a136-0c3e1a5510c9)
GPU 2: GH200 120GB (UUID: GPU-fecec81d-6144-b2f2-e8f9-28114a76df4a)
GPU 3: GH200 120GB (UUID: GPU-7efbc5d6-a5e2-0971-7e70-849491e05a02)

```

You can also simply use the `--gpu` argument to podman-hpc.

podman_hpc_gpu_flag.sh
```
#!/bin/bash

srun --nodes=1 --gpus=4 podman-hpc run --gpu ubuntu:latest nvidia-smi --list-gpus

```

Example output:

```
GPU 0: GH200 120GB (UUID: GPU-0f0087e6-4361-40a9-1238-b0315bbf3aba)
GPU 1: GH200 120GB (UUID: GPU-2d90c7dc-ef64-9248-a136-0c3e1a5510c9)
GPU 2: GH200 120GB (UUID: GPU-fecec81d-6144-b2f2-e8f9-28114a76df4a)
GPU 3: GH200 120GB (UUID: GPU-7efbc5d6-a5e2-0971-7e70-849491e05a02)

```

## Multi-node Containers

See the guide on using Podman-HPC across multiple nodes for specific guidance on obtaining good performance when running containers over multiple nodes.

## Resources

- NERSC's Podman-HPC beginners tutorial.
