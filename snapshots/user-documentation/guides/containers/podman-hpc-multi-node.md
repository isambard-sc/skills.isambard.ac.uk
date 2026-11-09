<!-- Snapshot of https://docs.isambard.ac.uk/user-documentation/guides/containers/podman-hpc-multi-node/ made by snapshot_docs.py. Do not edit. -->

# Podman-HPC Multi-node

Prerequisites

Please make sure you are familiar with Podman-HPC, MPI, and PMI guides.

On Isambard-AI `podman-hpc` has been set-up with this flag:

- `--openmpi-pmi2`: This adds NCCL, OpenMPI, and PMI2.

This flag will mount the required host dependencies into the container. An entrypoint script (`/host/adapt.sh`) will also set the environment. Below are examples that show how to use this flag in conjunction with `osu-micro-benchmarks` (for MPI applications) and `nccl-tests` (for NCCL / AI workloads).

Entrypoints

The `podman-hpc` flags will modify the entrypoint of the container to execute `/host/adapt.sh`. You will have to execute your entrypoint manually after starting the container for it to run. If you would like to not run the `adapt.sh` entrypoint you can set it as empty `podman-hpc run --entrypoint= <CONTAINER_IMAGE>`.

## Example: Running `nccl-tests` with Podman-HPC

Using NGC containers?

If you are running NGC (Nvidia GPU Cloud) containers it is recommended that you use `--openmpi-pmi2` to adapt the MPI in the container for the system.

Here shown is an example of how to build `nccl-tests` on an NGC container without rebuilding the container itself. This is built using the host's MPI. We use the nccl-tests repository and the nvcr.io/nvidia/pytorch:25.05-py3 NGC container to have access to its compiler suite. First `nccl-tests` is cloned, and the current working directories are mounted in the container for the build to persist.

```
$ podman-hpc pull nvcr.io/nvidia/pytorch:25.05-py3
$ git clone https://github.com/NVIDIA/nccl-tests.git
$ cd nccl-tests
$ podman-hpc run --interactive --tty --rm --openmpi-pmi2 --volume $PWD:$PWD --workdir $PWD nvcr.io/nvidia/pytorch:25.05-py3 bash

This container has been adapted to run MPI and NCCL applications on Isambard-AI.
Please go to the documentation for more information: https://docs.isambard.ac.uk/user-documentation/guides/containers/

user.project@nid001040:~$ make -j 8 MPI=1 NCCL_HOME=/host/nccl MPI_HOME=/host/openmpi CUDA_HOME=/usr/local/cuda
[build output...]
user.project@nid001040:~$ exit

```

In the execution of the container with `podman-hpc run` note the use of the following flags:

- `--interactive --tty` Run interactively.
- `--rm` Remove the container after exiting.
- `--openmpi-pmi2` Add NCCL, OpenMPI and PMI2 to the container.
- `--volume $PWD:$PWD` Mount the current working directory in the same path.
- `--workdir $PWD` Set the same working directory inside the container.
- `bash` This has to be added for the entrypoint script to execute interactively.

After exiting the container we can now `srun` to dispatch our job. To execute the benchmarks we must add `--mpi=pmi2` for Slurm to interface using PMI2, and the `--openmpi-pmi2` flag to `podman-hpc`:

podman_hpc_all_reduce.sh
```
#!/bin/bash

export ALL_REDUCE_BIN=$PWD/build/all_reduce_perf
srun --nodes=2 --gpus=8 --mpi=pmi2 --cpus-per-task 72 --ntasks-per-node 1 \
    podman-hpc run --openmpi-pmi2 --gpu --volume $PWD:$PWD --workdir $PWD \
    nvcr.io/nvidia/pytorch:25.05-py3 ${ALL_REDUCE_BIN} -b 32KB -e 8GB -f 2 -g 4

```

Example output:

```
Isambard-AI. Container adapted to run OpenMPI and NCCL on nid001018. https://docs.isambard.ac.uk/user-documentation/guides/containers/

# Collective test starting: all_reduce_perf
# nThread 1 nGpus 4 minBytes 32768 maxBytes 8589934592 step: 2(factor) warmup iters: 5 iters: 20 agg iters: 1 validation: 1 graph: 0
#
# Using devices
#  Rank  0 Group  0 Pid 246269 on  nid001018 device  0 [0009:01:00] NVIDIA GH200 120GB
#  Rank  1 Group  0 Pid 246269 on  nid001018 device  1 [0019:01:00] NVIDIA GH200 120GB
#  Rank  2 Group  0 Pid 246269 on  nid001018 device  2 [0029:01:00] NVIDIA GH200 120GB
#  Rank  3 Group  0 Pid 246269 on  nid001018 device  3 [0039:01:00] NVIDIA GH200 120GB
#  Rank  4 Group  0 Pid 235800 on  nid001019 device  0 [0009:01:00] NVIDIA GH200 120GB
#  Rank  5 Group  0 Pid 235800 on  nid001019 device  1 [0019:01:00] NVIDIA GH200 120GB
#  Rank  6 Group  0 Pid 235800 on  nid001019 device  2 [0029:01:00] NVIDIA GH200 120GB
#  Rank  7 Group  0 Pid 235800 on  nid001019 device  3 [0039:01:00] NVIDIA GH200 120GB
NCCL version 2.21.5+cuda12.2
#
#                                                              out-of-place                       in-place          
#       size         count      type   redop    root     time   algbw   busbw #wrong     time   algbw   busbw #wrong
#        (B)    (elements)                               (us)  (GB/s)  (GB/s)            (us)  (GB/s)  (GB/s)       
       32768          8192     float     sum      -1    57.69    0.57    0.99      0    51.90    0.63    1.10      0
       65536         16384     float     sum      -1    145.9    0.45    0.79      0    139.7    0.47    0.82      0
      131072         32768     float     sum      -1    461.9    0.28    0.50      0    461.8    0.28    0.50      0
      262144         65536     float     sum      -1    937.8    0.28    0.49      0    902.0    0.29    0.51      0
      524288        131072     float     sum      -1    902.4    0.58    1.02      0    893.5    0.59    1.03      0
     1048576        262144     float     sum      -1    873.1    1.20    2.10      0    858.6    1.22    2.14      0
     2097152        524288     float     sum      -1    816.7    2.57    4.49      0    843.5    2.49    4.35      0
     4194304       1048576     float     sum      -1   2808.1    1.49    2.61      0   2813.4    1.49    2.61      0
     8388608       2097152     float     sum      -1   2824.0    2.97    5.20      0   2775.0    3.02    5.29      0
    16777216       4194304     float     sum      -1   2802.7    5.99   10.48      0   2809.8    5.97   10.45      0
    33554432       8388608     float     sum      -1   2821.8   11.89   20.81      0   2816.7   11.91   20.85      0
    67108864      16777216     float     sum      -1   2891.1   23.21   40.62      0   2948.9   22.76   39.83      0
   134217728      33554432     float     sum      -1   3149.7   42.61   74.57      0   3186.8   42.12   73.70      0
   268435456      67108864     float     sum      -1   6346.6   42.30   74.02      0   6320.7   42.47   74.32      0
   536870912     134217728     float     sum      -1    12698   42.28   73.99      0    12683   42.33   74.08      0
  1073741824     268435456     float     sum      -1    25327   42.40   74.19      0    25402   42.27   73.97      0
  2147483648     536870912     float     sum      -1    50818   42.26   73.95      0    50669   42.38   74.17      0
  4294967296    1073741824     float     sum      -1   100961   42.54   74.45      0   101077   42.49   74.36      0
  8589934592    2147483648     float     sum      -1   201633   42.60   74.55      0   200953   42.75   74.81      0
# Out of bounds values : 0 OK
# Avg bus bandwidth    : 32.0711 
#
# Collective test concluded: all_reduce_perf

```

Under Bus Bandwidth (busbw) we can get `74.55` GB/s between 8 gpus placed over 2 nodes.
