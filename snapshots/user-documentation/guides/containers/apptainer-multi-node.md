<!-- Snapshot of https://docs.isambard.ac.uk/user-documentation/guides/containers/apptainer-multi-node/ made by snapshot_docs.py. Do not edit. -->

# Apptainer Multi-node

To run Apptainer (formerly Singularity) containers on multiple nodes, you will need to load the following module:

```
$ module load brics/apptainer-multi-node

```

This module will populate the `APPTAINER_BINDPATH` environment variable to bind the required host dependencies into the container. Inside your container, you must `source /host/adapt.sh` for the changes to take place. Here is an example of how to do this with an ubuntu container:

```
$ apptainer pull docker://ubuntu:latest
$ apptainer run --nv ubuntu_latest.sif 
Apptainer> source /host/adapt.sh

This container has been adapted to run MPI and NCCL applications on Isambard-AI.
Please go to the documentation for more information: https://docs.isambard.ac.uk/user-documentation/guides/containers/

Apptainer>

```

Existing runscripts

If your container already has an existing runscript/entrypoint, this can be executed as so:

```
Apptainer> /.singularity.d/runscript

```

## Example: `mpicc` and `ompi_info`

The MPI C Compiler (`mpicc`) wrapper is configured inside a multi-node container. Next we will check which `mpicc` is being used and verify the installation prefix. We show you how to do this using the `apptainer exec` command:

```
$ apptainer exec --nv ubuntu_latest.sif /host/adapt.sh bash

This container has been adapted to run MPI and NCCL applications on Isambard-AI.
Please go to the documentation for more information: https://docs.isambard.ac.uk/user-documentation/guides/containers/

Apptainer> which mpicc
/host/openmpi/bin/mpicc
Apptainer> mpicc -show
/usr/bin/gcc-12 -I/host/openmpi/include -L/host/openmpi/lib -L/tools/brics/apps/linux-sles15-neoverse_v2/gcc-12.3.0/hwloc-2.11.1-exva2bctb5orrxuniin42m422e4land7/lib -L/tools/brics/apps/linux-sles15-neoverse_v2/gcc-12.3.0/libevent-2.1.12-tg7v5ywzz5wthjw5wmp4ajwkosv36bg7/lib -Wl,-rpath -Wl,/host/openmpi/lib -Wl,-rpath -Wl,/tools/brics/apps/linux-sles15-neoverse_v2/gcc-12.3.0/hwloc-2.11.1-exva2bctb5orrxuniin42m422e4land7/lib -Wl,-rpath -Wl,/tools/brics/apps/linux-sles15-neoverse_v2/gcc-12.3.0/libevent-2.1.12-tg7v5ywzz5wthjw5wmp4ajwkosv36bg7/lib -lmpi
Apptainer> ompi_info
...

```

This verifies that `mpicc` is correctly including the header files and linking against the appropriate libraries. `ompi_info` can also show you more about how OpenMPI has been built. Note that you will have to include your own C compiler (e.g. `gcc`) or use a container with a compiler suite built-in.

## Example: Running `nccl-tests` in Apptainer

We will now run `nccl-tests` to show how to get the full bandwidth of the interconnect. For this we will use the nccl-tests repository and the nvcr.io/nvidia/pytorch:24.04-py3 NGC container to have access to its compiler suite.

```
$ git clone https://github.com/NVIDIA/nccl-tests.git
$ apptainer pull docker://nvcr.io/nvidia/pytorch:25.05-py3
$ apptainer exec --nv --bind $TMPDIR pytorch_25.05-py3.sif /host/adapt.sh bash
Apptainer>

```

Inside the container we will now enter the nccl-tests directory and build using the host OpenMPI:

```
Apptainer> cd nccl-tests/
Apptainer> make -j 72 MPI=1 NCCL_HOME=/host/nccl MPI_HOME=/host/openmpi CUDA_HOME=/usr/local/cuda
[build output...]
Apptainer> exit
$ srun --nodes=2 --gpus=8 --ntasks-per-node 1 --cpus-per-task 72 apptainer exec --nv --bind $PWD:$PWD pytorch_25.05-py3.sif /host/adapt.sh bash -c "nccl-tests/build/all_reduce_perf -b 32KB -e 8GB -f 2 -g 4"

This container has been adapted to run MPI and NCCL applications on Isambard-AI.
Please go to the documentation for more information: https://docs.isambard.ac.uk/user-documentation/guides/containers/

# nThread 1 nGpus 4 minBytes 32768 maxBytes 8589934592 step: 2(factor) warmup iters: 5 iters: 20 agg iters: 1 validation: 1 graph: 0
#
# Using devices
#  Rank  0 Group  0 Pid  81239 on  nid001003 device  0 [0009:01:00] NVIDIA GH200 120GB
#  Rank  1 Group  0 Pid  81239 on  nid001003 device  1 [0019:01:00] NVIDIA GH200 120GB
#  Rank  2 Group  0 Pid  81239 on  nid001003 device  2 [0029:01:00] NVIDIA GH200 120GB
#  Rank  3 Group  0 Pid  81239 on  nid001003 device  3 [0039:01:00] NVIDIA GH200 120GB
#  Rank  4 Group  0 Pid 173445 on  nid001021 device  0 [0009:01:00] NVIDIA GH200 120GB
#  Rank  5 Group  0 Pid 173445 on  nid001021 device  1 [0019:01:00] NVIDIA GH200 120GB
#  Rank  6 Group  0 Pid 173445 on  nid001021 device  2 [0029:01:00] NVIDIA GH200 120GB
#  Rank  7 Group  0 Pid 173445 on  nid001021 device  3 [0039:01:00] NVIDIA GH200 120GB
NCCL version 2.21.5+cuda12.2
#
#                                                              out-of-place                       in-place          
#       size         count      type   redop    root     time   algbw   busbw #wrong     time   algbw   busbw #wrong
#        (B)    (elements)                               (us)  (GB/s)  (GB/s)            (us)  (GB/s)  (GB/s)       
       32768          8192     float     sum      -1    47.26    0.69    1.21      0    43.43    0.75    1.32      0
       65536         16384     float     sum      -1    79.48    0.82    1.44      0    79.92    0.82    1.44      0
      131072         32768     float     sum      -1    121.6    1.08    1.89      0    120.7    1.09    1.90      0
      262144         65536     float     sum      -1    232.3    1.13    1.98      0    235.2    1.11    1.95      0
      524288        131072     float     sum      -1    232.2    2.26    3.95      0    233.2    2.25    3.93      0
     1048576        262144     float     sum      -1    247.4    4.24    7.42      0    248.1    4.23    7.40      0
     2097152        524288     float     sum      -1    276.4    7.59   13.28      0    274.5    7.64   13.37      0
     4194304       1048576     float     sum      -1    724.6    5.79   10.13      0    726.2    5.78   10.11      0
     8388608       2097152     float     sum      -1    727.1   11.54   20.19      0    730.1   11.49   20.11      0
    16777216       4194304     float     sum      -1    747.1   22.46   39.30      0    743.9   22.55   39.47      0
    33554432       8388608     float     sum      -1    797.6   42.07   73.62      0    798.3   42.03   73.56      0
    67108864      16777216     float     sum      -1   1361.9   49.28   86.23      0   1359.9   49.35   86.36      0
   134217728      33554432     float     sum      -1   2675.2   50.17   87.80      0   2677.3   50.13   87.73      0
   268435456      67108864     float     sum      -1   5260.5   51.03   89.30      0   5257.7   51.06   89.35      0
   536870912     134217728     float     sum      -1    10425   51.50   90.12      0    10425   51.50   90.13      0
  1073741824     268435456     float     sum      -1    20760   51.72   90.51      0    20762   51.72   90.50      0
  2147483648     536870912     float     sum      -1    41431   51.83   90.71      0    41434   51.83   90.70      0
  4294967296    1073741824     float     sum      -1    82764   51.89   90.81      0    82759   51.90   90.82      0
  8589934592    2147483648     float     sum      -1   165400   51.93   90.89      0   165443   51.92   90.86      0
# Out of bounds values : 0 OK
# Avg bus bandwidth    : 46.8888 
#

```

Under Bus Bandwidth (busbw) we can get `90.89` GB/s between 8 gpus placed over 2 nodes.

## Resources

- Apptainer and MPI
- Introduction to using MPI with containers
