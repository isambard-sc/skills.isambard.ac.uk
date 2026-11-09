<!-- Snapshot of https://docs.isambard.ac.uk/user-documentation/guides/python-troubleshooting/ made by snapshot_docs.py. Do not edit. -->

# Python: Troubleshooting

Common problems installing and building Python packages on Isambard systems. For everyday Conda, `uv`, and `pip`/`venv` usage, see the basics guide. For background on building packages from source on `aarch64`, see the advanced guide.

## Installing a package fails

`ERROR: Could not find a version that satisfies the requirement <package>` / `ERROR: No matching distribution found for <package>`

No wheel is published for `aarch64` (or for your Python version), and pip could not build the package from source either. Check whether the package is available through Conda instead — see finding aarch64-compatible packages. If not, you will need to build it from source; see the advanced guide.

Package fails to build with a compiler error (see `CC`/`CXX`)

The default system compiler is often too old to build modern research software. Set `CC` and `CXX` to a newer compiler, as described in compilers in the advanced guide, and retry the install.

Build succeeds, but fails to detect a pre-installed dependency (e.g. `torch`) or ARM-specific compiler flags

Pip's isolated build environment can hide pre-installed packages and system compiler flags from the build process. Try again with `--no-build-isolation` — see disabling build isolation in the advanced guide.

`mpi4py` installs but fails at runtime, or brings in its own MPI implementation

The default Conda package for `mpi4py` bundles its own MPI implementation, which does not support the system's high-speed interconnect or the Slurm process manager. Use the conda-forge external-MPICH build, which binds to the system Cray MPICH at run time — see MPI libraries in the advanced guide.

## Environment problems

`conda: command not found` after starting a new session or an interactive job on a compute node

Conda is not activated in this shell. Activation does not persist between the login node and compute nodes, so run `source ~/miniforge3/bin/activate` again in the new session.

A package is installed, but `import <package>` still fails

This usually means the package was installed into the wrong environment, or `pip`/`python3` is not resolving to the environment you think it is. Check the active environment with `which python3`, and use `python3 -m pip` rather than a bare `pip` to be sure which installation is being used — see `pip` vs `python3 -m pip` in the basics guide.
