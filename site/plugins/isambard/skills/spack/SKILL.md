---
name: spack
description: >
  Guide for installing, configuring, and using Spack to build software on Isambard AI (BriCS)
  supercomputers (Isambard-AI Phase 1, Phase 2, Isambard 3 Grace, Isambard 3 MACS).
  Use this skill whenever a user asks about Spack on Isambard, setting up a Spack environment,
  using the buildit configuration repository, concretizing or installing Spack packages,
  adding the isamrepo repository, targeting neoverse_v2 or aarch64 with Spack, or
  troubleshooting Spack builds on Cray HPE systems with Slingshot 11.
  Also trigger for questions about building HPC software from source on Isambard,
  managing Spack environments, or using system compilers and MPI within Spack — even if
  the user doesn't explicitly say "Spack" but is clearly trying to build software with
  dependency management on Isambard.
compatibility: >
  Isambard-AI and Isambard 3. Requires access to an Isambard login node and a
  Spack installation or clone.
metadata:
  author: isambard-sc
  version: "1.0"
  source_url: https://docs.isambard.ac.uk/user-documentation/guides/spack/
---

# Spack on Isambard

[Spack](https://spack.readthedocs.io) is a package manager for building HPC software and its
dependencies in a consistent, reproducible way, taking into account the target machine's
architecture and interconnect.

> **Note:** Not every package is guaranteed to be supported. Only configurations outlined here
> have been tested by BriCS. Known issues will be listed in the
> [upstream docs](https://docs.isambard.ac.uk/user-documentation/guides/spack/) as they are reported.

**Prerequisites:** Familiarity with [modules](https://docs.isambard.ac.uk/user-documentation/guides/modules/),
[MPI](https://docs.isambard.ac.uk/user-documentation/guides/mpi/), and
[system specs](https://docs.isambard.ac.uk/specs/) (especially the Slingshot 11 interconnect).

## Critical Rules

- Install and run Spack only from a supported Spack clone and the BriCS `buildit` config.
- Set `SPACK_DISABLE_LOCAL_CONFIG=true` to avoid conflicts with local `~/.spack` settings.
- Always source `spack/share/spack/setup-env.sh` before using `spack`.
- Always activate a Spack environment before running `spack install`, `spack add`, or
  `spack env create`.
- Match the Spack version to the `buildit` config branch.

---

## Architecture Notes by System

| System | Architecture | Spack target |
|--------|-------------|--------------|
| Isambard-AI Phase 1 | aarch64 / NVIDIA Grace | `neoverse_v2` |
| Isambard-AI Phase 2 | aarch64 / NVIDIA Grace | `neoverse_v2` |
| Isambard 3 Grace | aarch64 / NVIDIA Grace | `neoverse_v2` |
| Isambard 3 MACS | x86_64 (mixed) | `zen3` or similar — build on the target node |

Slingshot 11 (SS11) is the high-speed interconnect on all systems. The `buildit` config ensures
correct dependencies are used to exploit it.

---

## Step 1 — Download Spack

Clone a stable release into your home or project directory. The `--depth=2` flag limits
download size (Spack has a long history):

```bash
git clone --depth=2 --branch=releases/v1.1 https://github.com/spack/spack.git
```

> **Cache conflicts:** If you have used a previous version of Spack, `$HOME/.spack` can cause
> issues. Either delete/move it, or isolate caches per version:
> ```bash
> export SPACK_USER_CACHE_PATH=$PWD/spack-cache
> ```

---

## Step 2 — Activate Spack

Source the setup script to make the `spack` command available:

```bash
. spack/share/spack/setup-env.sh
```

Verify it works and check the detected architecture:

```bash
spack arch
# linux-sles15-neoverse_v2   (Isambard-AI / Isambard 3 Grace)
# linux-sles15-zen3          (Isambard 3 MACS, approx.)
```

---

## Step 3 — Download the BriCS `buildit` Config

BriCS provides a configuration repository that pre-configures compilers, MPI, and libraries
correctly for each system. Clone it alongside the `spack` directory:

```bash
git clone --depth 1 --branch=releases/v2.1 https://github.com/isambard-sc/buildit.git
```

You should now have two directories: `spack/` and `buildit/`.

---

## Step 4 — Create a Spack Environment

Disable local user config to avoid conflicts, then create an isolated environment:

```bash
export SPACK_DISABLE_LOCAL_CONFIG=true   # add to .bash_profile to make permanent
spack env create --dir myenv
spack env activate ./myenv
```

---

## Step 5 — Initialise the Environment

Apply the BriCS-provided packages config for your specific system, then set common options:

**Isambard-AI Phase 1**
```bash
spack config add --file buildit/config/aip1/v1.1/packages.yaml
```

**Isambard-AI Phase 2**
```bash
spack config add --file buildit/config/aip2/v1.1/packages.yaml
```

**Isambard 3 Grace**
```bash
spack config add --file buildit/config/3/v1.1/packages.yaml
```

**Isambard 3 MACS**
```bash
spack config add --file buildit/config/macs3/v1.1/packages.yaml
```

Then apply the same common settings for all systems:

```bash
spack config add config:build_jobs:8
spack config add view:true
spack config add concretizer:unify:true
spack config add concretizer:reuse:false
```

Verify compilers were found:

```bash
spack compiler list
# Expect: cce, gcc (multiple versions), nvhpc on aarch64 systems
# MACS also shows: aocc (x86_64)
```

---

## Step 6 — Add the Isambard Package Repository (Optional)

The `buildit` repo provides extra packages and fixes not yet upstream in Spack:

```bash
spack repo add ./buildit/repo/v1.1/spack_repo/isamrepo
# ==> Added repo to config with name 'isamrepo'.
```

Browse all available packages with `spack list`.

---

## Step 7 — Add, Concretize, and Install Software

**Add** a package to the environment (does not install yet):
```bash
spack add osu-micro-benchmarks
```

**Concretize** — resolve all dependencies consistently:
```bash
spack concretize
# Shows the full resolved dependency tree targeting neoverse_v2
```

Review the concretized output. If it looks correct, **install**:
```bash
spack install
# Installs to spack/opt/spack/linux-sles15-neoverse_v2/
# Environment view created at ./myenv/.spack-env/view/
```

After install, reload the environment to ensure everything is on `PATH`:
```bash
spack env deactivate && spack env activate ./myenv
```

Verify the install:
```bash
which osu_latency
# ./myenv/.spack-env/view/libexec/osu-micro-benchmarks/mpi/pt2pt/osu_latency

spack find
# Shows installed packages with their target (e.g. neoverse_v2)
```

---

## Deactivating an Environment

```bash
spack env deactivate
```

---

## Quick Reference

| Goal | Command |
|------|---------|
| Activate Spack | `. spack/share/spack/setup-env.sh` |
| Check detected arch | `spack arch` |
| Disable local config | `export SPACK_DISABLE_LOCAL_CONFIG=true` |
| Create environment | `spack env create --dir myenv` |
| Activate environment | `spack env activate ./myenv` |
| Apply BriCS config | `spack config add --file buildit/config/<system>/v1.1/packages.yaml` |
| List compilers | `spack compiler list` |
| Add Isambard repo | `spack repo add ./buildit/repo/v1.1/spack_repo/isamrepo` |
| Browse packages | `spack list` |
| Add package to env | `spack add <package>` |
| Resolve dependencies | `spack concretize` |
| Install | `spack install` |
| List installed | `spack find` |
| Deactivate environment | `spack env deactivate` |

---

## Key Points to Remember

- **Always use the `buildit` config** for the correct system — it wires up Slingshot 11 MPI, system compilers, and scientific libraries correctly. Skipping this and letting Spack build its own MPI will produce binaries that don't use the high-speed interconnect.
- **`view:true`** means installed binaries are symlinked into `./myenv/.spack-env/view/` and available on `PATH` without loading modules.
- **`concretizer:reuse:false`** forces fresh builds rather than reusing cached installs — recommended for correctness on Isambard.
- **Isambard 3 MACS** has mixed CPU types — build on the node that matches your target architecture.
- The `spack/opt/` install tree is per-architecture (e.g. `linux-sles15-neoverse_v2`).

---

## Further Resources

- [Spack documentation](https://spack.readthedocs.io)
- [Spack tutorial](https://spack-tutorial.readthedocs.io)
- [Spack environments tutorial](https://spack-tutorial.readthedocs.io/en/latest/tutorial_environments.html)
- [Spack FAQ](https://spack.readthedocs.io/en/latest/frequently_asked_questions.html)
- [buildit repository](https://github.com/isambard-sc/buildit)
- [Isambard MPI guide](https://docs.isambard.ac.uk/user-documentation/guides/mpi/)
- [Isambard modules guide](https://docs.isambard.ac.uk/user-documentation/guides/modules/)
