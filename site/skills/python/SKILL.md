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
compatibility: >
  Isambard-AI and Isambard 3. Requires access to an Isambard login node and Python
  environment tools such as Miniforge, pip, or uv.
metadata:
  author: isambard-sc
  version: "1.0"
  source_url: https://docs.isambard.ac.uk/user-documentation/guides/python/
---

# Python on Isambard AI

Isambard supercomputers run **Linux on Arm64 (`aarch64`)** — this shapes almost every aspect of Python environment management, since many packages lack prebuilt `aarch64` wheels and must be compiled from source.

Python and packages can be managed with `pip`, `conda`, or `uv`. **Conda via Miniforge** is the recommended approach. All workflows should use **virtual environments** to isolate dependencies.

Use:
- **Conda** for reproducible environment management, binary packages, and complex dependency sets.
- **uv** for fast venv creation and lightweight dependency installation when system Python is not required.
- **Cray Python** only when the environment is already module-managed and you want the system-supported runtime.

## Critical Rules

- Always use a virtual environment for every project.
- Never install packages into the Conda `base` environment.
- Do not run `conda init`; activate Miniforge manually.
- Always use `python3 -m pip` rather than bare `pip`.
- Prefer Conda on Isambard, and use `uv` only when you need a simpler local venv workflow.

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

Conda's `mpi4py` installs its own MPI, which won't use the system high-speed interconnect (Slingshot 11). Force a source build against the Cray MPI stack instead:

```bash
module load PrgEnv-gnu
python3 -m pip install --no-cache --no-binary mpi4py mpi4py
```

For simple use-cases, `module load cray-mpich-abi` can help pip find the correct MPI library without a source build.

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
| General Python environment management | Conda (Miniforge) |
| Fast pip/venv workflows | uv |
| System Python already available | `module load cray-python` + `venv` |
| Package not on conda, no `aarch64` wheel | Build from source; set `CC`/`CXX`; try `--no-build-isolation` |
| MPI (mpi4py) | `module load PrgEnv-gnu` + `pip install --no-binary mpi4py mpi4py` |
| Checking package compatibility | Search anaconda.org filtered to `linux-aarch64`; inspect GitHub Actions workflows |

---

## Useful Resources

- [Isambard documentation](https://docs.isambard.ac.uk)
- [Miniforge on GitHub](https://github.com/conda-forge/miniforge)
- [uv docs](https://docs.astral.sh/uv/)
- [Anaconda.org package search](https://anaconda.org)
- [Arm Python guide](https://learn.arm.com/learning-paths/laptops-and-desktops/win_python/how-to-1/)
- [mpi4py docs](https://mpi4py.readthedocs.io)
