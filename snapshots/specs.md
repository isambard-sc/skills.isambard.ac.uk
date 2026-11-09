<!-- Snapshot of https://docs.isambard.ac.uk/specs/ made by snapshot_docs.py. Do not edit. -->

# System Specifications

This page details the system specifications for the BriCS supercomputers.

=== "Isambard-AI Phase 1"

Isambard-AI Phase 1 consists of 42 nodes based on aarch64 architecture. Each node has 4 NVIDIA GH200 Grace Hopper Superchips. In total, there are 168 NVIDIA GH200 Grace Hopper Superchips. Each superchip contains one Grace CPU and one Hopper H100 GPU. The interconnect is based on Slingshot 11 where each node has 4 x Cassini NICs, each NIC operating at 200Gbps.

Compute node specs:

| Superchip | Processors | Cores | CPU Memory | GPUs | GPU Memory | Internal Interconnect |
| 4 × NVIDIA GH200 Grace Hopper Superchip | 4 × Grace CPU | 4 × 72 | 4 × 120 GB | 4 × H100 Tensor Core GPU | 4 × 96 GB | NVIDIA NVLink-C2C |

Each node has 460 GB of usable CPU memory (115 GB is usable for each CPU), and 384 GB of GPU memory. In total, there is 844 GB of CPU + GPU memory per node.

Login node specs:

| Superchip | Processors | Cores | CPU Memory | GPUs | GPU Memory | Internal Interconnect |
| 4 × NVIDIA GH200 Grace Hopper Superchip | 4 × Grace CPU | 4 × 72 | 4 × 120 GB | 4 × H100 Tensor Core GPU | 4 × 96 GB | NVIDIA NVLink-C2C |

The resources available to each user on the login node is limited to maintain quality of service. Login nodes should not be used for long running or intensive workloads.

The power management settings for Isambard-AI caps each GH200 to 660 Watts, shared dynamically between the CPU and GPU.

Grace uses the CPU architecture ARM (also known as aarch64). As such, code needs to be compiled for aarch64 and container images need to support aarch64. Existing code compiled for x86_64 (including Conda environments) will not work.

=== "Isambard-AI Phase 2"

Isambard-AI Phase 2 consists of 1,320 nodes based on aarch64 architecture. Each node has 4 NVIDIA GH200 Grace Hopper Superchips. In total, there are 5,280 NVIDIA GH200 Grace Hopper Superchips. Each superchip contains one Grace CPU and one Hopper H100 GPU. The interconnect is based on Slingshot 11 where each node has 4 x Cassini NICs, each NIC operating at 200Gbps.

Compute node specs:

| Superchip | Processors | Cores | CPU Memory | GPUs | GPU Memory | Internal Interconnect |
| 4 × NVIDIA GH200 Grace Hopper Superchip | 4 × Grace CPU | 4 × 72 | 4 × 120 GB | 4 × H100 Tensor Core GPU | 4 × 96 GB | NVIDIA NVLink-C2C |

Each node has 460 GB of usable CPU memory (115 GB is usable for each CPU), and 384 GB of GPU memory. In total, there is 844 GB of CPU + GPU memory per node.

The power management settings for Isambard-AI caps each GH200 to 660 Watts, shared dynamically between the CPU and GPU.

Login node specs:

| Superchip | Processors | Cores | CPU Memory | Internal Interconnect |
| 1 × NVIDIA Grace CPU Superchip | 2 × Grace CPU | 2 × 72 | 2 × 120 GB | NVIDIA NVLink-C2C |

Note that the login nodes do not have a GPU.

The resources available to each user on the login node is limited to maintain quality of service. Login nodes should not be used for long running or intensive workloads.

Grace uses the CPU architecture ARM (also known as aarch64). As such, code needs to be compiled for aarch64 and container images need to support aarch64. Existing code compiled for x86_64 (including Conda environments) will not work.

=== "Isambard 3 Grace"

Isambard 3 Grace consists of 384 nodes based on aarch64 architecture. Each node has a NVIDIA Grace CPU Superchip. Each superchip contains 2 Grace CPUs. The interconnect is based on Slingshot 11 where each node has a single Cassini NIC at 200Gbps.

Compute node specs:

| Superchip | Processors | Cores | CPU Memory | Internal Interconnect |
| 1 × NVIDIA Grace CPU Superchip | 2 × Grace CPU | 2 × 72 | 2 × 120 GB | NVIDIA NVLink-C2C |

Login node specs:

| Superchip | Processors | Cores | CPU Memory | Internal Interconnect |
| 1 × NVIDIA Grace CPU Superchip | 2 × Grace CPU | 2 × 72 | 2 × 120 GB | NVIDIA NVLink-C2C |

The resources available to each user on the login node is limited to maintain quality of service. Login nodes should not be used for long running or intensive workloads.

Grace uses the CPU architecture ARM (also known as aarch64). As such, code needs to be compiled for aarch64 and container images need to support aarch64. Existing code compiled for x86_64 (including Conda environments) will not work.

=== "Isambard 3 MACS"

The Isambard 3 MACS (Multi-Architecture Comparison System) contains nodes with different examples of architecture, currently all based on x86-64. The interconnect is based on Slingshot 11 where each node has a single Cassini NIC at 200Gbps. The Slurm partition names are included due to the subtle differences in each node.

Per Slurm partition specs:

| Partition | Processors per Node | Number of Nodes | Cores per Node | CPU Memory | GPUs per Node | GPU Memory | Internal Interconnect |
| milan | 2 × AMD EPYC 7713 (Milan) | 12 | 2 × 64 | 256 GB | 0 | 0 GB | AMD Infinity Fabric |
| genoa | 2 × AMD EPYC 9354 (Genoa) | 2 | 2 × 32 | 384 GB | 0 | 0 GB | AMD Infinity Fabric |
| berg | 1 × AMD EPYC 9754 (Bergamo) | 2 | 1 × 128 | 192 GB | 0 | 0 GB | AMD Infinity Fabric |
| spr | 2 × Intel(R) Xeon(R) Gold 6430 (Sapphire Rapids) | 2 | 2 × 32 | 256 GB | 0 | 0 GB | Intel Ultra Path Interconnect |
| sprhbm | 2 × Intel(R) Xeon(R) CPU Max 9462 (Sapphire Rapids) | 2 | 2 × 32 | 128 GB (HBM) | 0 | 0 GB | Intel Ultra Path Interconnect |
| ampere | 1 × AMD EPYC 7543P (Milan) | 2 | 1 × 32 | 256 GB | 4 × Nvidia A100 SXM4 | 40 GB | AMD Infinity Fabric |
| hopper | 1 × AMD EPYC 7543P (Milan) | 1 | 1 × 32 | 256 GB | 4 × Nvidia H100 PCIe | 80 GB | AMD Infinity Fabric |
| instinct | 1 × AMD EPYC 7543P (Milan) | 2 | 1 × 32 | 256 GB | 4 × Instinct MI100 | 32 GB | AMD Infinity Fabric |

The login node is notionally identical to the `milan` partition described above.

=== "BlueCrystal 5"

BlueCrystal 5 consists of 371 standard nodes, 4 large memory nodes and 4 A100 GPU nodes all based on x86_64 architecture.

Per node specs:

| Partition | Number of Nodes | CPU model | Cores | CPU Memory | Hyper-threaded | GPU |
| general | 330 | AMD EPYC 9655 | 32 | 128 GiB | | - |
| general | 41 | AMD EPYC 7713 | 32 | 128 GiB | | - |
| highmem | 4 | AMD EPYC 7713 | 56 | 448 GiB | | - |
| gpu | 4 | AMD EPYC 7713 | 16 | 128 GiB | | 1 × NVIDIA A100 |
