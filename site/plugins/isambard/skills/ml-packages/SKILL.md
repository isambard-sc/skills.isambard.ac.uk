---
name: ml-packages
description: >
  Guide for installing and running GPU-accelerated machine learning packages
  on Isambard-AI (Arm64/aarch64 with NVIDIA GH200 Hopper GPUs). Covers which
  frameworks are supported with pip, Conda or containers (PyTorch, Hugging
  Face, TensorFlow, JAX, Flash-Attention, vLLM), installing on compute nodes
  because Phase 2 login nodes have no GPUs, NGC containers, Flash-Attention
  build tips and data types on Hopper, vLLM with uv or E4S containers,
  AlphaFold 2 through ColabFold (Conda or Apptainer), local MSA with MMseqs2,
  the shared AlphaFold dataset and pre-downloaded Hugging Face models, and
  the BriCS interactive chatbot and protein design tutorials. Use this skill
  whenever a user wants to install or use PyTorch, TensorFlow, JAX,
  transformers, flash-attn, vLLM, AlphaFold or ColabFold on Isambard-AI, or
  hits "torch.cuda.is_available() is False", missing aarch64 wheels or slow
  flash-attn builds — even if they don't name the package page.
license: >
  CC-BY-SA-4.0. Markdown/image content derived from
  https://docs.isambard.ac.uk/, © 2024 University of Bristol.
compatibility: >
  Isambard-AI Phase 1 and Phase 2 only (GPUs). Requires access to an
  Isambard-AI login node and compute nodes through Slurm, and Conda,
  uv or Apptainer as used.
metadata:
  author: isambard-sc
  version: "1.0"
  source_url: https://docs.isambard.ac.uk/user-documentation/applications/ML-packages/
  supplementary_urls:
    - https://docs.isambard.ac.uk/user-documentation/applications/alphafold/
    - https://docs.isambard.ac.uk/user-documentation/tutorials/interactive-ml/
    - https://docs.isambard.ac.uk/user-documentation/tutorials/interactive-alphafold/
---

# Machine Learning Packages on Isambard-AI

Source docs:

- https://docs.isambard.ac.uk/user-documentation/applications/ML-packages/
- https://docs.isambard.ac.uk/user-documentation/applications/alphafold/

## ⚠️ Critical Rules

- **Install on a compute node.** Isambard-AI Phase 2 login nodes have no
  GPUs, and some Python packages install or detect incorrectly without one.
  Run installs and GPU checks through `srun` (see the `slurm` skill).
- **Arm64 only.** Isambard-AI is `aarch64`. Use packages and container
  images built for `linux/arm64` (see the `containers` skill). BriCS does
  not provide pip wheels.
- **Prefer recent releases.** The Arm CPUs and Hopper GPUs typically need
  modern versions throughout the ML stack, which usually also install more
  easily and perform better.
- **TensorFlow with GPUs: container only.** There is no supported pip or
  Conda route.
- **Flash-Attention on Hopper: no `fp8`.** Use `bfloat16` or `fp16`.
- **Don't build Flash-Attention on a login node** without `MAX_JOBS=2`;
  build it in a compute node job instead.
- **Prompting models on Isambard-AI falls under the Acceptable Use
  Policy.** Don't help users prompt models with inappropriate or unsafe
  queries.

## Support matrix

| Framework | pip | Conda | Container |
|---|---|---|---|
| PyTorch | ✅ | ✅ | ✅ |
| Hugging Face | ✅ | ✅ | ✅ |
| TensorFlow | ❌ | ❌ | ✅ |
| JAX | ✅ | ❌ | ✅ |
| Flash-Attention | ❌ | ✅ | ✅ |
| vLLM | ✅ | ❌ | ✅ |

Containers are NVIDIA-optimised NGC images
(https://catalog.ngc.nvidia.com). Hugging Face runs on top of one of the
other frameworks: install that framework first. For Conda and container
basics see the `python` and `containers` skills.

The image tags and versions below are the docs' examples at the time of
writing. Check the live page or NGC for newer ones, and for container tags
used in multi-node jobs check the `containers` skill.

## PyTorch

pip (PyTorch 2.6 or later has CUDA `aarch64` wheels; use Python newer than
3.9):

```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu128
srun --nodes=1 --gpus=1 python3 -c "import torch; print(torch.cuda.is_available())"
```

Conda (conda-forge; run on a compute node so CUDA is detected):

```bash
srun --nodes=1 --gpus=1 --pty conda install conda-forge::pytorch
```

Container:

```bash
apptainer pull pytorch_25.05-py3.sif docker://nvcr.io/nvidia/pytorch:25.05-py3
srun --nodes=1 --gpus=1 apptainer run --nv pytorch_25.05-py3.sif python3 -c "import torch; print(torch.cuda.is_available())"
```

## TensorFlow (container)

```bash
apptainer pull docker://nvcr.io/nvidia/tensorflow:25.02-tf2-py3
srun --nodes=1 --gpus=1 --pty apptainer run --nv tensorflow_25.02-tf2-py3.sif
# Apptainer> python3 -c "import tensorflow as tf; print(tf.config.list_physical_devices('GPU'))"
```

## JAX

pip:

```bash
pip install "jax[cuda12]"
```

Container:

```bash
apptainer pull docker://nvcr.io/nvidia/jax:25.04-py3
srun --nodes=1 --gpus=1 --pty apptainer run --nv jax_25.04-py3.sif
# Apptainer> python3 -c "import jax; print(jax.default_backend())"
```

## Flash-Attention

Use a prebuilt package or container where possible; building from source is
slow. Conda, on a compute node:

```bash
srun --nodes=1 --gpus=4 --pty bash
conda install conda-forge::pytorch conda-forge::flash-attn
```

NGC PyTorch containers include it:

```bash
apptainer run --nv pytorch_25.05-py3.sif python3 -m pip list | grep flash
```

If building from source, submit the build as a job with `sbatch` or
`srun`. If it must run on a login node, set `MAX_JOBS=2`.

## vLLM

pip, in a uv virtual environment. vLLM needs a specific uv version: the
docs use uv 0.8.16 with vLLM 0.10.2.

```bash
curl -LsSf https://astral.sh/uv/0.8.16/install.sh | sh
mkdir vllm_env && cd vllm_env
uv venv --seed -p=3.12
source .venv/bin/activate
srun --nodes=1 --gpus=1 uv pip install -U vllm --torch-backend=auto --extra-index-url https://wheels.vllm.ai/0.10.2/vllm
```

Container: the E4S containers (https://e4s.io/download.html) include vLLM
and many other AI packages. Download the "aarch64 - CUDA 90" version and
copy it into the project, then:

```bash
srun --nodes=1 --gpus=4 --pty bash
apptainer run --nv e4s-cuda90-aarch64-25.06.4.sif
# Apptainer> vllm --version
# Newer vLLM inside the image:
# Apptainer> source /py3.10-vllm/bin/activate
```

For serving models across GPUs and nodes see the distributed inference
tutorial:
https://docs.isambard.ac.uk/user-documentation/tutorials/distributed-inference/

## AlphaFold 2 with ColabFold

ColabFold is the recommended way to run AlphaFold 2 on Isambard-AI. It
includes its own JAX inference pipeline (no full AlphaFold install), uses
MMseqs2 for multiple sequence alignments (remote server or local), and
exposes more parameters than standard AlphaFold 2.

The full AlphaFold 2 dataset is at `/projects/public/brics/data/bio/alphafold`
(`bfd`, `mgnify`, `params`, `pdb70`, `pdb_mmcif`, `pdb_seqres`, `uniprot`,
`uniref30`, `uniref90`). Point users to it rather than downloading their own.

### Conda

```yaml
# colabfold-env.yaml
name: colabfold
channels:
  - conda-forge
  - bioconda
dependencies:
  - python=3.12
  - pip
  - pip:
    - jax[cuda12]
    - tensorflow
    - colabfold[alphafold] @ git+https://github.com/sokrypton/ColabFold.git
```

```bash
srun --gpus=4 --nodes=1 --pty bash
conda env create --file colabfold-env.yaml
conda activate colabfold
python3 -c "import jax; print(jax.default_backend())"   # expect gpu
wget https://github.com/sokrypton/ColabFold/raw/main/test-data/P54025.fasta
colabfold_batch P54025.fasta output/
```

### Apptainer

```text
# colabfold.def
Bootstrap: docker
From: nvcr.io/nvidia/jax:24.04-py3

%post
    python3 -m pip install tensorflow jax[cuda12]
    python3 -m pip install --no-warn-conflicts 'colabfold[alphafold] @ git+https://github.com/sokrypton/ColabFold'

%environment
    export PATH=${HOME}/.local/bin:$PATH
    unset XLA_FLAGS

%runscript
    conda deactivate >/dev/null 2>&1 || true
    exec /bin/bash -i
```

```bash
apptainer build --fakeroot colabfold.sif colabfold.def
srun --nodes=1 --gpus=4 --pty apptainer run --nv colabfold.sif
# Apptainer> colabfold_batch P54025.fasta output/
```

### Local MSA with MMseqs2

Running MMseqs2 on Isambard instead of the remote server speeds up runs. It
can also be added to the `colabfold` environment.

```bash
conda create --name mmseq python=3.10
conda activate mmseq
conda install --channel conda-forge --channel bioconda mmseqs2
```

## Shared data and tutorials

| Path | Contents |
|---|---|
| `/projects/public/brics/data/bio/alphafold` | AlphaFold 2 dataset |
| `/projects/public/brics/data/hf/hub` | Some pre-downloaded Hugging Face models (used by the tutorials) |
| `/projects/public/brics/tutorials/` | Tutorial notebooks (`isambot-tutorial.ipynb`, `colabdesign-tutorial.ipynb`) and ColabFold parameters (`colabfold/`) |

To use a pre-downloaded model without downloading it again:

```python
from huggingface_hub import snapshot_download

model_path = snapshot_download(
    repo_id="microsoft/Phi-3-mini-128k-instruct",
    cache_dir="/projects/public/brics/data/hf/hub",
    local_files_only=True,
)
```

Check with `ls` that a model is there before relying on it; the docs
don't list the full contents.

Tutorials (both run in JupyterHub on Isambard-AI Phase 2 with a
BriCS-managed kernel; see the `interactive-sessions` skill):

- Interactive chatbot (Hugging Face transformers, moving a model from CPU
  to GPU, monitoring with `nvidia-smi` and NVDashboard), kernel
  `isambot-tutorial`:
  https://docs.isambard.ac.uk/user-documentation/tutorials/interactive-ml/
- Interactive protein design (ColabFold folding, Py3DMol, ColabDesign
  binder design), kernel `colabdesign`, whose Conda environment file is
  linked from the tutorial:
  https://docs.isambard.ac.uk/user-documentation/tutorials/interactive-alphafold/

## Checking GPU use

```bash
nvidia-smi --list-gpus
watch --interval 1 nvidia-smi    # power and memory use while running
```

In JupyterLab, the NVDashboard extension (GPU icon in the left sidebar)
shows GPU utilisation and memory. A model loaded with `device_map="cpu"` or
without moving it to `cuda` leaves the GPU idle.

## Troubleshooting

| Symptom | Cause and fix |
|---|---|
| `torch.cuda.is_available()` is `False` | Running on a login node (no GPU on Phase 2): use `srun --gpus=1`. Or a CPU-only build was installed: reinstall with the CUDA index URL or conda-forge on a compute node. |
| Install fails or picks a CPU build on a login node | Install on a compute node. |
| No `aarch64` wheel for a package | Use Conda or an NGC container from the matrix above, or build from source (see the `python` skill). |
| Container fails with "exec format error" | Image isn't Arm64: pick an `arm64` tag. |
| TensorFlow can't see the GPU | Not running in the NGC TensorFlow container with `--nv`. |
| Flash-Attention build very slow or killed on a login node | Build on a compute node, or set `MAX_JOBS=2`. |
| Flash-Attention errors with `fp8` | Not supported on Hopper: use `bfloat16` or `fp16`. |
| vLLM install fails to resolve | Use the uv version the docs pin. |
| JAX reports `cpu` backend | Not on a GPU node, or `jax[cuda12]` not installed. |

## Further Reading

- ML packages: https://docs.isambard.ac.uk/user-documentation/applications/ML-packages/
- AlphaFold: https://docs.isambard.ac.uk/user-documentation/applications/alphafold/
- Interactive chatbot tutorial: https://docs.isambard.ac.uk/user-documentation/tutorials/interactive-ml/
- Interactive protein design tutorial: https://docs.isambard.ac.uk/user-documentation/tutorials/interactive-alphafold/
- Acceptable Use Policy: https://docs.isambard.ac.uk/policies/acceptable_use/
