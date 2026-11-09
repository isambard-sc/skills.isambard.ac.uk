<!-- Snapshot of https://docs.isambard.ac.uk/user-documentation/guides/spack/setup/ made by snapshot_docs.py. Do not edit. -->

# Setting up Spack

Isambard-AI and Isambard 3 Grace have similar architecture based on ARM (or more specifically aarch64) based on the Nvidia Grace design. Isambard-AI will obviously support using CUDA whilst Isambard 3 Grace is a traditional CPU. Isambard 3 MACS contains a number of different processors, details are in the specifications and it is recommended to build code on the required architecture. This will become visible when installing software.

## Downloading Spack

First a decision has to be made to stay with a stable version or keep to the latest development version. For beginners we would recommend sticking with a stable numbered version. Change to a location such as your home directory or project location.

```
$ git clone --depth=2 --branch=releases/v1.1 https://github.com/spack/spack.git

```

Spack repository size

Spack is a large repository with a long history and large number of files. Using the recommended git command limits the size of the download.

## Making Spack available

The easiest way to make Spack available is to load the setup script which provides everything you need to start with Spack.

```
$ . spack/share/spack/setup-env.sh

```

Spack version conflicts

The cache used by Spack in `$HOME/.spack` can cause issues between different versions of Spack. If a previous version of Spack has been used you can either move or delete `$HOME/.spack` to always use the currently recommended version. If multiple versions of Spack are to be used then set `SPACK_USER_CACHE_PATH=$PWD/spack-cache` to use a different directory in the current location when each version is used.

The command `spack` should now work and one simple check would be to use `spack arch`.

```
$ spack arch
linux-sles15-neoverse_v2

```

The output shows that Spack has detected the platform as `linux`, the operating system as `sles15` and the target architecture as `neoverse_v2`. On Isambard 3 MACS, this will show similar but the target architecture will be based on `x86_64` such as `linux-sles15-zen3`.

## Initial configuration

To help with an initial configuration, we have created another repository which can be cloned, either at particular version or the latest version by omitting `--branch=releases/v2.1`.

```
$ git clone --depth 1 --branch=releases/v2.1 https://github.com/isambard-sc/buildit.git

```

Sense check

There should now be 2 directories, `spack` and `buildit`.

## Creating an environment

Using easy-to-load spack environments helps to isolate software (similar to python environments). A basic environment can be used, including a known working basic configuration. To resolve conflicts with user configuration, set `SPACK_DISABLE_LOCAL_CONFIG=true`.

```
$ export SPACK_DISABLE_LOCAL_CONFIG=true

```

Setting default values

Environment variables such as `SPACK_DISABLE_LOCAL_CONFIG` can be set in `.bash_profile`

To create a spack environment using a local directory.

```
$ spack env create --dir myenv
==> Created independent environment in: ./myenv
==> Activate with: spack env activate ./myenv

```

As described the environment can be activated.

```
$ spack env activate ./myenv

```

## Initialising the environment

An environment can be configured modifying the `spack.yaml` inside the directory `./myenv`. It is easier to use `spack` commands to perform validation of options. Note the use of Spack version and facility name.

=== "Isambard-AI Phase 1"

```
$ spack config add --file buildit/config/aip1/v1.1/packages.yaml
$ spack config add config:build_jobs:8
$ spack config add view:true
$ spack config add concretizer:unify:true
$ spack config add concretizer:reuse:false

```

=== "Isambard-AI Phase 2"

```
$ spack config add --file buildit/config/aip2/v1.1/packages.yaml
$ spack config add config:build_jobs:8
$ spack config add view:true
$ spack config add concretizer:unify:true
$ spack config add concretizer:reuse:false

```

=== "Isambard 3 Grace"

```
$ spack config add --file buildit/config/3/v1.1/packages.yaml
$ spack config add config:build_jobs:8
$ spack config add view:true
$ spack config add concretizer:unify:true
$ spack config add concretizer:reuse:false

```

=== "Isambard 3 MACS"

```
$ spack config add --file buildit/config/macs3/v1.1/packages.yaml
$ spack config add config:build_jobs:8
$ spack config add view:true
$ spack config add concretizer:unify:true
$ spack config add concretizer:reuse:false

```

The environment can be checked by listing available compilers.

```
$ spack compiler list

```

=== "Isambard-AI Phase 1"

```
-- cce sles15-aarch64 -------------------------------------------
[e]  [email protected]  [e]  [email protected]

-- gcc sles15-aarch64 -------------------------------------------
[e]  [email protected]  [e]  [email protected]  [e]  [email protected]

-- nvhpc sles15-aarch64 -----------------------------------------
[e]  [email protected]

```

=== "Isambard-AI Phase 2"

```
==> Available compilers
-- cce sles15-aarch64 -------------------------------------------
[e]  [email protected]  [e]  [email protected]

-- gcc sles15-aarch64 -------------------------------------------
[e]  [email protected]  [e]  [email protected]  [e]  [email protected]

-- nvhpc sles15-aarch64 -----------------------------------------
[e]  [email protected]

```

=== "Isambard 3 Grace"

```
==> Available compilers
-- acfl sles15-aarch64 ------------------------------------------
[e]  [email protected]

-- cce sles15-aarch64 -------------------------------------------
[e]  [email protected]

-- gcc sles15-aarch64 -------------------------------------------
[e]  [email protected]  [e]  [email protected]

-- nvhpc sles15-aarch64 -----------------------------------------
[e]  [email protected]

```

=== "Isambard 3 MACS"

```
==> Available compilers
-- aocc sles15-x86_64 -------------------------------------------
[e]  [email protected]

-- cce sles15-x86_64 --------------------------------------------
[e]  [email protected]

-- gcc sles15-x86_64 --------------------------------------------
[e]  [email protected]  [e]  [email protected]

-- nvhpc sles15-x86_64 ------------------------------------------
[e]  [email protected]

```

## Configuring your environment

Some useful configuration is to include a useful software repository and to add software.

### Adding a repository

Spack comes with a huge catalogue of Spack packages (just try typing `spack list`)

Sometimes a package is not available or requires a fix, one way to provide this is via an alternative repository.

```
$ spack repo add ./buildit/repo/v1.1/spack_repo/isamrepo
==> Added repo to config with name 'isamrepo'.

```

This can provide extra packages that can eventually be fed upstream into Spack.

### Adding software

Inside an environment we can add software. This does not install any software, just adds the software to the environment.

```
$ spack add osu-micro-benchmarks
==> Adding osu-micro-benchmarks to environment ./myenv

```

This will use the default compiler and providers for libraries such as MPI. The command `spack concretize` will make sure all software added to the environment is consistent.

```
$ spack concretize
=> Concretized 1 spec:
 -   whrp4zl  [email protected]~cuda~graphing~papi~rocm build_system=autotools platform=linux os=sles15 target=neoverse_v2 %c,[email protected]
 -   oleirhf      ^[email protected] build_system=generic platform=linux os=sles15 target=neoverse_v2 
[e]  tcx7zqr      ^[email protected]~cuda~rocm+wrappers build_system=generic platform=linux os=sles15 target=aarch64 %[email protected]
[e]  2p2ponw          ^[email protected]~cuda~debug~kdreg~level_zero~rocm~uring build_system=autotools fabrics:=cxi platform=linux os=sles15 target=aarch64 
[e]  zvpy3g3      ^[email protected]~binutils+bootstrap~graphite~mold~nvptx~piclibs~profiled~strip build_system=autotools build_type=RelWithDebInfo languages:='c,c++,fortran' platform=linux os=sles15 target=aarch64 
 -   rifqxyn      ^[email protected] build_system=generic platform=linux os=sles15 target=neoverse_v2 
[e]  alti7xg      ^[email protected] build_system=autotools platform=linux os=sles15 target=aarch64 
[e]  xr4vobq      ^[email protected]~guile build_system=generic platform=linux os=sles15 target=aarch64 
 -   3uhzjpc      ^gnuconfig@2024-07-27 build_system=generic platform=linux os=sles15 target=neoverse_v2  

```

If the concretize provides a sensible set of options the package can be installed.

```
$ spack install
...

```

This will produce a lot of output for the first-time and will be installed in `spack/opt/spack/linux-sles15-neoverse_v2` but the environment will create a "view" of the install for the user to easily use. After an install it is worth deactivating and activating the environment to make sure it is all loaded.

```
$ spack env deactivate && spack env activate ./myenv

```

Check that the application was installed, in this case `osu_latency` should now be found.

```
$ which osu_latency
./myenv/.spack-env/view/libexec/osu-micro-benchmarks/mpi/pt2pt/osu_latency

```

The installed packages can also be found using `spack find`. For example on an ARM architecture it has built the code targeting `neoverse_v2` that will take advantage of the most appropriate features of the CPU.

```
$ spack find
==> In environment ./myenv
==> 1 root specs
-- no arch / no compilers ---------------------------------------
[+] osu-micro-benchmarks

-- linux-sles15-aarch64 / %[email protected] -------------------------
[email protected]

-- linux-sles15-aarch64 / no compilers --------------------------
[email protected]  [email protected]  [email protected]  [email protected]

-- linux-sles15-neoverse_v2 / %c,[email protected] -----------------
[email protected]

-- linux-sles15-neoverse_v2 / no compilers ----------------------
[email protected]  [email protected]  gnuconfig@2024-07-27
==> 9 installed packages
==> 0 concretized packages to be installed (show with `spack find -c`)

```

## Deactivating an environment

Deactivating an environment is a simple command

```
$ spack env deactivate

```

## Summary

In summary the use of Spack with environments gives a clear record of what was installed and in a consistent unified way. The applications are installed without the need to use modules to load the software and are available from the command line.
