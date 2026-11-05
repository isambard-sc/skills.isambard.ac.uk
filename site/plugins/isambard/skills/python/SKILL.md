---
name: python
description: >
  Guide for installing and managing Python environments on Isambard AI (BriCS) supercomputers.
  Use this skill whenever a user asks about Python on Isambard, setting up Conda/Miniforge,
  using uv, installing pip packages, building from source on aarch64/Arm64, mpi4py on HPC,
  virtual environments on Isambard, or troubleshooting Python package builds for Linux Arm64.
  Also trigger for questions about Cray Python, build isolation, pyproject.toml on Arm, or
  finding aarch64-compatible packages — even if the user doesn't say "Isambard" explicitly
  but is clearly working on an HPC or Arm Linux environment.
license: CC-BY-SA-4.0. Markdown/image content derived from https://docs.isambard.ac.uk/, © Bristol Centre for Supercomputing (BriCS).
compatibility: >
  Isambard-AI and Isambard 3. Requires access to an Isambard login node and Python
  environment tools such as Miniforge, pip, or uv.
metadata:
  author: isambard-sc
  version: "1.1"
  source_url: https://docs.isambard.ac.uk/user-documentation/guides/python/
  supplementary_urls:
    - https://docs.isambard.ac.uk/user-documentation/guides/python-advanced/
    - https://docs.isambard.ac.uk/user-documentation/guides/python-troubleshooting/
    - https://docs.isambard.ac.uk/user-documentation/guides/mpi/
  docs_commit: e994565
---

# Python on Isambard AI

Isambard supercomputers run **Linux on Arm64 (`aarch64`)** — this shapes almost every aspect of Python environment management, since many packages lack prebuilt `aarch64` wheels and must be compiled from source.

Python and packages can be managed with `pip`, `conda`, or `uv`. **Conda and `uv` are both reasonable defaults** when starting from scratch; install Conda via **Miniforge**. All workflows should use **virtual environments** to isolate dependencies.

Use:
- **Conda** when you need non-Python dependencies too (e.g. compilers, `cuda`, system libraries).
- **uv** when you want fast installs, lockfiles, or are working from a `pyproject.toml`.
- **pip + venv** (e.g. with Cray Python) when you already have a `pip`/`venv`-based workflow and don't want to change it.

## Critical Rules

- Always use a virtual environment for every project.
- Never install packages into the Conda `base` environment.
- Do not run `conda init`; activate Miniforge manually.
- Always use `python3 -m pip` rather than bare `pip`.
- Never use a plain `conda install mpi4py` (or conda OpenMPI) for multi-node MPI — it
  bypasses Cray MPICH and the Slingshot interconnect. See *MPI libraries* below.

---

## Conda: Miniforge (Recommended)

Use [Miniforge](https://github.com/conda-forge/miniforge), not the main Anaconda distribution (which requires a license).

### Install

```bash
cd $HOME
curl --location --remote-name \
  "https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-$(uname)-$(uname -m).sh"
bash Miniforge3-$(uname)-$(uname -m).sh
rm Miniforge3-$(uname)-$(uname -m).sh
```

`$(uname)` → OS name (e.g. `Linux`); `$(uname -m)` → architecture (e.g. `aarch64`).

**Do not run `conda init`** — it modifies shell startup scripts and can cause complications. Instead, activate manually:

```bash
source ~/miniforge3/bin/activate
```

### Create and use environments

Never install packages into `base`. Always create a named environment:

```bash
(base) $ conda create --name myenv python=3.10
(base) $ conda activate myenv
(myenv) $ conda install scipy
```

To create from a YAML spec file:

```bash
conda env create --file environment.yml
```

Useful commands: `conda list` (list packages), `conda deactivate` (exit environment).

### Finding `aarch64`-compatible Conda packages

Search [anaconda.org](https://anaconda.org) and filter **Platform → `linux-aarch64`** to confirm a package is available for this architecture before attempting to install.

---

## uv: Fast Python Package Manager

[uv](https://docs.astral.sh/uv/) is a fast pip/venv-compatible tool useful for creating virtual environments and resolving dependencies. It also manages Python versions and tracks exact dependency lockfiles.

### Install

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Create a venv and install packages

```bash
mkdir myproject && cd myproject
uv venv                          # creates .venv in current directory
source .venv/bin/activate
uv pip install numpy
```

---

## Cray Python (Pre-installed Module)

A system Python is available via the modules system:

```bash
module avail               # list all available modules
module load cray-python
which python3              # /opt/cray/pe/python/3.11.5/bin/python3
```

### Virtual environments with Cray Python

```bash
mkdir -p ~/.virtualenvs
python3 -m venv --upgrade-deps ~/.virtualenvs/myenv
source ~/.virtualenvs/myenv/bin/activate
python3 -m pip install scipy
python3 -m pip list
deactivate
```

> **Tip:** Always use `python3 -m pip` rather than bare `pip` to ensure you're targeting the correct environment.

---

## Building Python Packages from Source on `aarch64`

Many packages don't ship `aarch64` wheels. If a package isn't on conda or in a container, it must be built from source. The sections below cover the main friction points.

### Compilers

The OS default compilers are often too old for research software. Set `CC`/`CXX` explicitly:

```bash
# List available g++ versions
ls /usr/bin/g++*
# /usr/bin/g++  /usr/bin/g++-12  /usr/bin/g++-13  /usr/bin/g++-7

CC=/usr/bin/gcc-12 CXX=/usr/bin/g++-12 pip install <PACKAGE>
```

### MPI libraries (`mpi4py`)

A plain `conda install mpi4py` bundles its own MPI runtime, which does not know about the Slingshot interconnect or the Slurm process manager, so it will not work correctly across multiple nodes.

**Recommended:** use the conda-forge *external* MPICH build, which binds to the vendor Cray MPICH at run time:

```bash
conda create --name mpi4py-mpich \
    --channel conda-forge/label/mpi-external \
    --channel conda-forge \
    mpi4py "mpich=*=external_*"
```

In the job script, load the Cray environment and point the dynamic linker at the Cray MPICH ABI libraries before launching with `srun`:

```bash
module reset
module load PrgEnv-gnu
source ~/miniforge3/bin/activate
conda activate mpi4py-mpich
export LD_LIBRARY_PATH="${MPICH_DIR}/lib-abi-mpich:${LD_LIBRARY_PATH:-}"
srun python mpi_hello.py
```

**Best performance (production MPI workloads):** build `mpi4py` from source against Cray MPICH using the `cc` wrapper, in a minimal environment:

```bash
module reset
module load PrgEnv-gnu
conda create --name mpi4py-source python pip
conda activate mpi4py-source
MPICC="cc -shared" python -m pip install \
    --force-reinstall --no-cache-dir --no-binary mpi4py mpi4py
```

Load `PrgEnv-gnu` in the job script too (no `LD_LIBRARY_PATH` change needed). Conda OpenMPI is **not** a supported configuration on Isambard — it does not work correctly with `srun`. See the [MPI guide](https://docs.isambard.ac.uk/user-documentation/guides/mpi/) for test programs and full job scripts.

### Build isolation

By default, pip builds packages in an isolated environment. On `aarch64` this can block access to:
- System compilers with ARM-specific flags (`-march=armv8-a`)
- CUDA compilers (`nvcc`)
- Pre-installed packages like `torch` that some builds need to detect

Disable build isolation when standard installation fails:

```bash
CC=/usr/bin/gcc-12 CXX=/usr/bin/g++-12 pip install --no-build-isolation <PACKAGE>
```

Or via exported variables:

```bash
export CC="/usr/bin/gcc-12"
export CXX="/usr/bin/g++-12"
export CFLAGS="-march=native -O3"
export CXXFLAGS="-march=native -O3"
pip install --no-build-isolation <PACKAGE>
```

> **Trade-off:** Disabling isolation can cause dependency conflicts. Use when standard installation fails and ARM-specific optimisations are needed.

### Inspecting `setup.py` and `pyproject.toml`

Check whether a package's build script supports `aarch64` before installing:

**`setup.py`** — look for platform conditionals:
```python
import sys, platform
if sys.platform == "linux" and platform.uname().machine == "aarch64":
    extra_compile_args = ["-march=armv8-a"]
```

**`pyproject.toml`** — check the build backend:
```toml
[build-system]
requires = ["setuptools", "wheel"]
build-backend = "setuptools.build_meta"
```

On Isambard-AI, `sys.platform` returns `"linux"` and `platform.uname().machine` returns `"aarch64"`.

### Checking dependencies for `aarch64` support

- **`setup.py`**: look for `install_requires` or `requirements.txt` references
- **`pyproject.toml`**: check `[project.dependencies]`, `[tool.poetry.dependencies]`, or equivalent

**GitHub Actions CI** is a reliable signal: if `.github/workflows` only builds `linux_x86_64.whl`, the package has no official `aarch64` wheel and requires source compilation or a workaround.

---

## Machine Learning Packages

Support for popular ML packages on `aarch64` is documented on the [Isambard ML packages applications page](https://docs.isambard.ac.uk/user-documentation/applications/ML-packages/).

---

## Quick Decision Guide

| Situation | Recommended approach |
|-----------|---------------------|
| Need non-Python dependencies (compilers, `cuda`, system libraries) | Conda (Miniforge) |
| Fast installs, lockfiles, or a `pyproject.toml` project | uv |
| Existing `pip`/`venv` workflow | `module load cray-python` + `venv` |
| Package not on conda, no `aarch64` wheel | Build from source; set `CC`/`CXX`; try `--no-build-isolation` |
| MPI (mpi4py) | Conda env with `mpi4py "mpich=*=external_*"` from `conda-forge/label/mpi-external`; source build with `MPICC="cc -shared"` for best performance |
| Checking package compatibility | Search anaconda.org filtered to `linux-aarch64`; inspect GitHub Actions workflows |

---

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| `ERROR: Could not find a version that satisfies the requirement <package>` / `No matching distribution found` | No `aarch64` wheel (or none for this Python version). Check Conda (`linux-aarch64` on anaconda.org); otherwise build from source |
| Build fails with a compiler error | Default system compiler is too old — set `CC`/`CXX` (e.g. `/usr/bin/gcc-12`, `/usr/bin/g++-12`) and retry |
| Build can't detect a pre-installed dependency (e.g. `torch`) or ARM compiler flags | Retry with `--no-build-isolation` |
| `mpi4py` installs but fails at runtime, or brings its own MPI | Use the conda-forge external-MPICH build (see *MPI libraries*) |
| `conda: command not found` in a new session or an interactive job on a compute node | Activation doesn't persist between login and compute nodes — run `source ~/miniforge3/bin/activate` again |
| Package installed but `import <package>` fails | Wrong environment — check `which python3` and use `python3 -m pip`, not bare `pip` |

---

## Useful Resources

- [Isambard documentation](https://docs.isambard.ac.uk)
- [Python: building from source on aarch64](https://docs.isambard.ac.uk/user-documentation/guides/python-advanced/)
- [Python: troubleshooting](https://docs.isambard.ac.uk/user-documentation/guides/python-troubleshooting/)
- [Isambard MPI guide](https://docs.isambard.ac.uk/user-documentation/guides/mpi/)
- [Miniforge on GitHub](https://github.com/conda-forge/miniforge)
- [uv docs](https://docs.astral.sh/uv/)
- [Anaconda.org package search](https://anaconda.org)
- [Arm Python guide](https://learn.arm.com/learning-paths/laptops-and-desktops/win_python/how-to-1/)
- [mpi4py docs](https://mpi4py.readthedocs.io)
