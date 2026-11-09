<!-- Snapshot of https://docs.isambard.ac.uk/user-documentation/guides/containers/ made by snapshot_docs.py. Do not edit. -->

# Using Containers

Container engines can be used to deploy software packages in lightweight, standalone, and reproducible environments.

Isambard supercomputers provide 2 container engines:

- Podman-HPC
- Apptainer

## Using Containers On Multiple Nodes (MPI & NCCL)

To achieve optimal multi-node performance with containers on Isambard-AI and Isambard 3 they must be able to communicate with the Network Interface Cards (NICs). These guides explain how to set this up. MPI (Message Passing Interface) is required for CPU workloads, while both MPI and NCCL (NVIDIA Collective Communications Library) are required for GPUs.

Prerequisites

These guides assumes familiarity with MPI and the specifications of Isambard-AI:

- MPI documentation.
- System specifications, mainly the interconnect.

Isambard-AI and Isambard 3 are HPE Cray systems based on the Slingshot 11 (SS11) interconnect. To achieve optimal latency and bandwidth the relevant dependencies are mounted inside the `/host/` directory of the container to avoid interfering with other software in the container. They are then added to `PATH` and `LD_LIBRARY_PATH`.

Information for specific container engines:

- Podman-HPC Multi-node
- Apptainer Multi-node

## Using Arm compatible container images

Isambard supercomputers mainly use the Arm 64 CPU architecture (see Specifications), also known as `aarch64`. Due to this, only container images that support this architecture can be used. For instance, if you visit the Nvidia GPU Cloud (NGC) container website and look under the "Tags" page, you will see they support varying architectures:

If you expand the drop down you will see which architectures are supported:
