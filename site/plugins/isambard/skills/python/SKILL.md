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
license: CC-BY-SA-4.0. Markdown/image content derived from https://docs.isambard.ac.uk/, © 2024 University of Bristol.
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

### PyTorch on `aarch64` with CUDA

The default PyPI `torch` wheel for `aarch64` is **not** the CUDA build. Take it
from the PyTorch index and pin the local version explicitly, or the resolver
will quietly give you a CPU build:

```bash
pip install --index-url https://download.pytorch.org/whl/cu126 "torch==2.9.1+cu126"
python3 -c "import torch; print(torch.__version__, torch.version.cuda)"
# want: 2.9.1+cu126 12.6      not: 2.9.1+cpu None
```

Adding `--extra-index-url https://pypi.org/simple` to that command is enough to
let the CPU build win. Verify, don't assume.

### PyTorch Geometric companion packages

`torch-scatter`, `torch-cluster` and `pyg-lib` ship **no `aarch64` wheels**.
They are source builds, and the OS default `g++` is gcc-7-era, which fails on
modern C++ with errors that look unrelated to the compiler:

```
error: 'unordered_map' is not a member of 'std'
error: 'move' is not a member of 'std'
error: 'isfinite' was not declared in this scope
```

Point the build at a modern compiler and, for CUDA extensions, restrict the
architecture so the compile finishes in minutes rather than an hour:

```bash
module load cudatoolkit/24.11_12.6
export CC=/usr/bin/gcc-12 CXX=/usr/bin/g++-12   # also g++-13, g++-14 available
export TORCH_CUDA_ARCH_LIST="9.0"               # GH200 is Hopper = sm_90
pip install --no-build-isolation "torch_scatter==2.1.2"
```

`--no-build-isolation` matters: the build needs to see the already-installed
`torch`.

### A dependency you import may not be the one that needs building

`torch-cluster` can be required without appearing anywhere in your code.
`graphein`, for instance, calls `torch_geometric.nn.pool.knn_graph`, which
raises at runtime unless `torch-cluster` or `pyg-lib` is installed:

```
ImportError: 'knn_graph' requires 'pyg-lib>=0.6.0'
```

Grepping your own source for `torch_cluster` will not find this. Check what
your dependencies call.

For k-NN graph construction specifically, a dense substitute avoids the build
altogether and is exact for the graph sizes typical of protein structures (a
few hundred to a few thousand nodes):

```python
def knn_graph(x, k, batch=None, loop=False, flow="source_to_target"):
    """Drop-in for torch_cluster.knn_graph using cdist + topk."""
    n = x.shape[0]
    if batch is None:
        batch = torch.zeros(n, dtype=torch.long, device=x.device)
    dist = torch.cdist(x.float(), x.float())
    dist = dist.masked_fill(batch.view(-1, 1) != batch.view(1, -1), float("inf"))
    if not loop:
        dist.fill_diagonal_(float("inf"))
    idx = dist.topk(k, dim=-1, largest=False).indices
    query = torch.arange(n, device=x.device).repeat_interleave(k)
    neighbour = idx.reshape(-1)
    # source_to_target returns [neighbour, query] so messages flow j -> i
    return torch.stack([neighbour, query] if flow == "source_to_target"
                       else [query, neighbour], dim=0)
```

Caveats: it is O(N²) in memory, so it suits graphs of thousands of nodes rather
than millions; and exact distance ties may break differently from
`torch_cluster` (`topk` orders by index), which changes *which* of two
equidistant neighbours is chosen, not the method.

### Reusing a prebuilt extension

A compiled extension can be copied between environments when the interpreter
version, architecture and the `torch` version it was built against all match
(e.g. `cp312`, `aarch64`, `torch 2.9.1`). This is a legitimate way to avoid a
long rebuild — but it is ABI-sensitive, so pin the same `torch` version first
and verify the import before relying on it:

```bash
python3 -c "from torch_scatter import scatter_add; import torch; \
  print(scatter_add(torch.ones(4,2).cuda(), torch.tensor([0,0,1,1]).cuda(), dim=0))"
```

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
