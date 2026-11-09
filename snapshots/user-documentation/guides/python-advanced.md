<!-- Snapshot of https://docs.isambard.ac.uk/user-documentation/guides/python-advanced/ made by snapshot_docs.py. Do not edit. -->

# Python: Building from Source on aarch64

Isambard supercomputers mainly use the Arm64 CPU architecture (see Specifications). Many Python packages don't build wheels (precompiled binaries) for `aarch64`. If your package isn't available through Conda or a container, this necessitates building the package from source. This guide covers the parts of the Python build systems that most often need attention on `aarch64`.

For everyday Conda, `uv`, and `pip`/`venv` usage, see the basics guide. If a build or install actually fails, see the troubleshooting guide.

Machine learning packages

Support for `aarch64` by popular machine learning packages is listed in our applications page.

## Compilers

The default compilers on Isambard supercomputers are older versions which form part of the underlying operating system build toolchain, and are typically unsuitable for building research software. It is recommended to set the `CC` and `CXX` environment variables to ensure `pip` uses modern C and C++ compilers. Often this can allow a package to be installed using `pip` on Arm.

In the following example the available GCC C++ compilers are listed and the `CC` and `CXX` variables are used to specify a specific version to use for installing a Python package:

```
user.project@nid001040:~> ls /usr/bin/g++*
/usr/bin/g++  /usr/bin/g++-12  /usr/bin/g++-13  /usr/bin/g++-7
user.project@nid001040:~> CC=/usr/bin/gcc-12 CXX=/usr/bin/g++-12 python3 -m pip install <PACKAGE_NAME>

```

## MPI libraries

A plain `conda install mpi4py` will not work correctly across multiple nodes on Isambard because the bundled MPI runtime does not know about the Slingshot interconnect or the Slurm process manager. The recommended approach is to use the conda-forge external-MPICH build, which binds to the vendor Cray MPICH at run time:

```
conda create --name mpi4py-mpich \
    --channel conda-forge/label/mpi-external \
    --channel conda-forge \
    mpi4py "mpich=*=external_*"

```

For full details — including a test program, the matching job script, and alternative approaches such as building mpi4py from source — see the MPI guide.

## Disabling build isolation

Pip creates an isolated build environment when building a package, where the build dependencies are installed. This helps prevent dependency conflicts between the build environment of separate packages.

However, this isolation can prevent access to system compilers with ARM-specific optimisations or to CUDA compilers such as `nvcc`. The isolated environment may use a basic compiler without access to ARM-specific flags like `-march=armv8-a`. Disabling build isolation can also allow detection of pre-installed packages like `torch` that some builds need to detect.

To work around this, you can disable build isolation with `--no-build-isolation`, e.g. using inline environment variables:

```
$ CC=/usr/bin/gcc-12 CXX=/usr/bin/g++-12 pip install --no-build-isolation <PACKAGE_NAME>

```

Options to pass compiler flags to `pip` builds

Alternatively, you can export environment variables as follows:

```
$ export CC="/usr/bin/gcc-12"
$ export CXX="/usr/bin/g++-12"
$ export CFLAGS="-march=native -O3"
$ export CXXFLAGS="-march=native -O3"
$ pip install --no-build-isolation <PACKAGE_NAME>

```

Trade-offs

Disabling build isolation can lead to dependency conflicts if the package's build requirements clash with your environment. Use this approach when standard installation fails and you need ARM-specific optimisations.

## Inspecting a package's build configuration

A package's `setup.py` (or `pyproject.toml`) can show conditional logic based on `sys.platform` or `platform`. The `setup.py` file is the traditional build script for Python packages. For example:

```
import sys
import platform
if sys.platform == "linux" and platform.uname().machine == "aarch64":
    extra_compile_args = ["-march=armv8-a"]

```

Modern Python packages often use `pyproject.toml` instead of `setup.py`. It is important to review that the `[build-system]` section specifies a compatible build backend like `setuptools` or `poetry`.

```
[build-system]
requires = ["setuptools", "wheel"]
build-backend = "setuptools.build_meta"

```

### Checking `sys.platform` and `platform()`

When building Python packages, the system's platform and architecture are often used to determine compatibility. Python provides tools like `sys.platform` and `platform()` for this purpose:

-
`sys.platform`: A string that identifies the operating system. Common values include:

- `"linux"` for Linux systems.
- `"darwin"` for macOS.
- `"win32"` for Windows.

-
`platform.uname()`: Provides detailed system information, including the machine architecture (e.g., `x86_64`, `aarch64`).

For example, here is the result of running these on Isambard-AI:

```
>>> import sys
>>> sys.platform
'linux'
>>> import platform
>>> platform.uname()
uname_result(system='Linux', node='nid001041', release='5.14.21-150500.55.31_13.0.53-cray_shasta_c_64k', 
version='#1 SMP Mon Dec 4 22:56:47 UTC 2023 (03d3f83)', machine='aarch64')
>>> platform.uname().machine
'aarch64'

```

This is particularly useful when inspecting a package's `setup.py` or `pyproject.toml` to ensure compatibility with `aarch64`.

### Checking dependencies

In `setup.py` look for `install_requires()` or `requirements.txt` references. Ensure all dependencies are available for `aarch64`.

For `pyproject.toml`, check for dependencies under `[project.dependencies]`, `[tool.poetry.dependencies]`, or equivalent sections.

### Checking CI/CD build targets

CI/CD or GitHub Actions

In a Python package's repository, GitHub Actions workflows often indicate which platforms and architectures the package is built for. You will see wheels are often packaged with a name in the form:

```
{PACKAGE_NAME}-linux_x86_64.whl

```

Look for `.github/workflows` in the repository. For example:

```
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: "3.8"
      - name: Build wheel
        run: python3 setup.py bdist_wheel

```

This can help you determine if `aarch64` is supported or if modifications are needed.

## Useful resources

- Arm python guide.
