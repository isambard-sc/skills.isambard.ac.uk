---
name: distributed-training
description: >
  Guide for distributed machine learning on Isambard-AI: multi-GPU and
  multi-node PyTorch training, LLM pre-training and fine-tuning, and serving
  LLMs across GPUs and nodes. Covers launching torch.distributed and
  DistributedDataParallel jobs with srun and PMI ranks (MASTER_ADDR, RANK,
  LOCAL_RANK, WORLD_SIZE), the NCCL backend over the Slingshot high speed
  network with brics/nccl, torchrun in NGC containers, Megatron-LM and
  Megatron Bridge pre-training in FP8 with the NeMo image, QLoRA fine-tuning
  with Hugging Face TRL and PEFT, vLLM serving on one node or across nodes
  with Ray, gated Hugging Face models, checkpoints across time-limited jobs,
  and the BriCS pre-downloaded weights and datasets. Use this skill whenever
  a user wants to train, fine-tune or serve a model on more than one GPU or
  node on Isambard-AI, sees slow multi-node training or a hanging process
  group, or asks about torchrun, DDP, gloo vs nccl, Megatron, LoRA/QLoRA, Ray
  or vLLM tensor parallelism — even if they don't say "distributed".
license: >
  CC-BY-SA-4.0. Markdown/image content derived from
  https://docs.isambard.ac.uk/, © 2024 University of Bristol.
compatibility: >
  Isambard-AI (the tutorials target Phase 2). Requires access to an
  Isambard-AI login node and GPU compute nodes through Slurm, uv, and
  Apptainer for the container-based steps. Gated models need a Hugging Face
  account and token, which the user sets up.
metadata:
  author: isambard-sc
  version: "1.0"
  source_url: https://docs.isambard.ac.uk/user-documentation/tutorials/distributed-training/
  supplementary_urls:
    - https://docs.isambard.ac.uk/user-documentation/tutorials/distributed-inference/
    - https://docs.isambard.ac.uk/user-documentation/tutorials/llms/pre-training/
    - https://docs.isambard.ac.uk/user-documentation/tutorials/llms/fine-tuning/
---

# Distributed Training and Inference on Isambard-AI

Source docs:

- https://docs.isambard.ac.uk/user-documentation/tutorials/distributed-training/
- https://docs.isambard.ac.uk/user-documentation/tutorials/distributed-inference/
- https://docs.isambard.ac.uk/user-documentation/tutorials/llms/pre-training/
- https://docs.isambard.ac.uk/user-documentation/tutorials/llms/fine-tuning/

## ⚠️ Critical Rules

- **Use the NCCL backend and `module load brics/nccl` for GPU
  communication across nodes.** `gloo` copies data through CPU memory and is
  much slower. See the `nccl` skill for the plugin and environment details.
- **Launch processes with `srun`**, never `mpirun` or `mpiexec` (see the
  `mpi` skill).
- **Install GPU packages on a compute node** (`srun --gpus=1 ...`) so CUDA
  builds are installed, and with no Conda environment active when creating
  uv environments.
- **Jobs have a time limit.** For long training runs, checkpoint and chain
  jobs with dependencies (see the `slurm` skill). Megatron Bridge resumes
  from the latest checkpoint when the same script is resubmitted.
- **Cancel serving jobs when finished.** A vLLM server holds its nodes, and
  is charged, until it is cancelled or times out.
- **The user authenticates to Hugging Face, not the agent.** Never ask for
  or handle the token. The user accepts gated model licences (e.g. Llama
  3.1) and runs `uvx hf auth login` themselves.
- **Ray lets any client run arbitrary code** on the cluster. Be careful
  what can reach it.
- **Checkpoints and datasets are large** (e.g. 105 GiB per Llama 3.1 8B
  checkpoint). Keep them in `$PROJECTDIR`, limit how many are saved, and
  clean up (see the `storage` skill).

## How the pieces fit

1. `srun` starts one process per GPU across the allocated nodes.
2. Slurm's PMI gives each process its ranks.
3. PyTorch uses those to form a process group, then NCCL moves data
   GPU-to-GPU over Slingshot with RDMA.

Rank variables by `srun --mpi` type:

| Meaning | `cray_shasta` | `pmi2` | `pmix` |
|---|---|---|---|
| World size | `SLURM_NTASKS` | `SLURM_NTASKS` | `SLURM_NTASKS` |
| Number of nodes | `SLURM_NNODES` | `SLURM_NNODES` | `SLURM_NNODES` |
| Global rank | `PMI_RANK` | `PMI_RANK` | `PMIX_RANK` |
| Node rank | `SLURM_NODEID` | `SLURM_NODEID` | `SLURM_NODEID` |
| Local rank | `SLURM_LOCALID` | `SLURM_LOCALID` | `SLURM_LOCALID` |

Each Isambard-AI node has 4 GH200s (4 GPUs, 72 CPU cores each).
`torch.distributed.launch` has been replaced by `torchrun`.

## Multi-node PyTorch (DDP)

Environment (uv, from the tutorial; versions are its tested pins):

```bash
uv venv --seed --python=3.10
srun --nodes=1 --gpus=1 --pty uv pip install torch==2.9.0 torchvision transformers --extra-index-url https://download.pytorch.org/whl/cu128
source .venv/bin/activate
srun --nodes=1 --gpus=1 python3 -c "import torch; print(torch.cuda.is_available())"
```

Job script, 2 nodes × 4 GPUs:

```bash
#!/bin/bash
#SBATCH --job-name=Torch_Distributed
#SBATCH --nodes=2
#SBATCH --gpus=8
#SBATCH --time=00:10:00
#SBATCH --ntasks-per-node=4

module load brics/nccl brics/aws-ofi-nccl
source .venv/bin/activate

export MASTER_ADDR=$(scontrol show hostname $SLURM_NODELIST | head -n 1)
export MASTER_PORT=29600

srun --nodes=2 \
    --gpus=8 \
    --mpi=pmi2 \
    --ntasks-per-node=4 \
    bash -c 'export WORLD_SIZE=$SLURM_GPUS; export RANK=$PMI_RANK; export LOCAL_RANK=$SLURM_LOCALID; python3 train.py'
```

Set the resource options in both `#SBATCH` and `srun`. In the training
script, call `dist.init_process_group("nccl", ...)`, set the CUDA device
from `LOCAL_RANK`, and wrap the model in `DistributedDataParallel`.

Checklist for using the high speed network:

- `module load brics/nccl` is in the job script.
- The backend is `nccl` in `init_process_group()`.
- `MASTER_ADDR` is set from `scontrol show hostname $SLURM_NODELIST`.
- Each process uses the GPU given by `LOCAL_RANK`.
- `export NCCL_DEBUG=INFO` shows whether NCCL is using the network.

The same applies in containers if the multi-node container setup is
followed (`brics/apptainer-multi-node`, `/host/adapt.sh`; see the
`containers` skill).

## LLM pre-training (Megatron Bridge, NeMo container)

The tutorial pre-trains Llama 3.1 8B in FP8 on 2 nodes (8 GPUs) for 100
iterations (about 40 minutes), exports to Hugging Face format and serves it
with vLLM. Outline:

1. Gated model access and `uvx hf auth login` (user).
2. `export WORK_PATH=${PROJECTDIR}/${USER}/llm-pre-training`.
3. Clone Megatron-LM and Megatron Bridge at the tag matching the NeMo
   image, and get the NeMo image as a `.sif`. A copy is at
   `/projects/public/brics/tutorials/llms/pre-training/nemo.sif`.
4. Prepare data (FineWeb sample, tokenised with Megatron's
   `preprocess_data.py`), or link the prepared data:
   `ln -s /projects/public/brics/tutorials/llms/pre-training/* ${WORK_PATH}/`.
5. `sbatch pretrain.sh`. Key parts:

   ```bash
   module reset
   module load brics/nccl
   module load brics/apptainer-multi-node
   HEAD_NODE=$(scontrol show hostnames $SLURM_NODELIST | head -n1)
   export HEAD_NODE_IP=$(dig +short ${HEAD_NODE})
   export MASTER_ADDR=$HEAD_NODE_IP
   export MASTER_PORT=29600
   export CUDA_DEVICE_MAX_CONNECTIONS=${CUDA_DEVICE_MAX_CONNECTIONS:-1}

   srun --mpi=pmi2 \
       apptainer run --nv \
           --mount type=bind,source=${WORK_PATH},destination=${WORK_PATH} \
           ... ${WORK_PATH}/nemo.sif \
           /projects/public/brics/tutorials/llms/pre-training/adapt.sh \
           torchrun \
           --nproc_per_node=$SLURM_GPUS_ON_NODE \
           --nnodes=$SLURM_NNODES \
           --node_rank=\$SLURM_PROCID \
           --master_addr=$HEAD_NODE_IP \
           --master_port=29600 \
           ${WORK_PATH}/train.py --config-file ${WORK_PATH}/config.yaml
   ```

   The tutorial's `adapt.sh` sets NCCL and libfabric variables for RDMA
   inside the container, which uses CUDA forward compatibility.
6. Convert a checkpoint with Megatron Bridge's `convert_checkpoints.py
   export`, then serve it with `vllm serve` in the same image.

Training logs report the loss and TFLOP/s per GPU. Use the full job
scripts from the tutorial page rather than rebuilding them.

## LLM fine-tuning (QLoRA, single GPU)

QLoRA quantises the frozen base model to 4-bit and trains small LoRA
adapters, so fine-tuning Llama 3.1 8B fits on one GH200 (96 GiB):

| Method | Approx. memory for weights + optimiser state |
|---|---|
| Full fine-tuning | ~119 GiB (needs sharding across GPUs) |
| LoRA | ~16 GiB |
| QLoRA | ~5 GiB |

Outline:

1. Gated model access and `uvx hf auth login` (user).
2. `export WORK_PATH=${PROJECTDIR}/${USER}/llm-fine-tuning`.
3. Build two uv environments in a GPU job, `.venv-train` (torch,
   transformers, TRL, PEFT, bitsandbytes) and `.venv-serve` (vLLM). They are
   separate because vLLM and TRL can need conflicting torch and
   transformers versions. Pin exact versions; these libraries change their
   APIs often.
4. `sbatch sft.sh`: a 1-GPU job running TRL's `SFTTrainer`. Set
   `HF_HUB_CACHE` and `HF_DATASETS_CACHE` under `$WORK_PATH` so downloads
   don't fill `$HOME`.
5. Merge the adapter into the base model (`merge_and_unload`, base loaded
   in bfloat16) to get a normal Hugging Face model (~16 GiB).
6. Serve the base and fine-tuned models with vLLM in turn and compare.

Datasets for `SFTTrainer`: `prompt`/`completion` columns (loss only on the
completion; good for base models), a `messages` column (needs a tokenizer
chat template, so suits `Instruct` models), or a `formatting_func`.

## Serving LLMs with vLLM

Environment (tested pins from the tutorial):

```bash
uv venv --seed --python=3.12
srun --nodes=1 --gpus=1 --pty bash -c "
    source .venv/bin/activate
    uv pip install -U vllm[flashinfer]==0.15.1 ray[default] \
        --torch-backend=auto \
        --extra-index-url https://wheels.vllm.ai/0.15.1/vllm
"
```

If CUDA errors appear, `uv pip list | grep torch` should show a CUDA build
such as `torch 2.9.1+cu129`.

**One node, 4 GPUs (tensor parallel):** in an exclusive 1-node job,
`module load brics/nccl`, activate the environment, then:

```bash
srun --nodes=$SLURM_NNODES --gpus=$SLURM_GPUS --cpus-per-task 72 --ntasks-per-node 1 \
    vllm serve $MODEL_PATH --served-model-name $MODEL_NAME \
    --host 0.0.0.0 --port 8000 --tensor_parallel_size=4
```

The server is ready when the log shows `Application startup complete`.

**Several nodes (Ray):** in an exclusive multi-node job, start a Ray head
on the first node and workers on the others (each with `srun --nodelist
... ray start --block ...` in the background, using HSN addresses from
`dig +short <node>`), check `ray status`, then run `vllm serve` on the head
node with `--distributed-executor-backend ray` and
`--tensor_parallel_size` equal to the total GPUs. Use the model's
directory path, not its name, as `MODEL_PATH`. Copy the tutorial's
`multi_node_serve.sh` rather than writing it from scratch. If vLLM stays at
`Waiting for 1 local, 0 remote core engine proc(s) to start`, cancel and
resubmit.

Parallelism: tensor parallelism (TP) splits each layer across GPUs;
pipeline parallelism (PP) puts different layers on different GPUs.
`tensor_parallel_size × pipeline_parallel_size` must equal the GPUs used. A
model that fits on fewer GPUs may run slower when spread across nodes.

Talking to a running server, from a login node:

```bash
source .venv/bin/activate
srun --overlap --jobid <JOB_ID> --nodes 1 --gpus 1 --pty vllm chat --model-name <MODEL_NAME>
```

`vllm bench serve --host <HEAD_NODE_IP> --port 8000 ...` measures
throughput. For other models, take settings from the vLLM recipes
(https://recipes.vllm.ai); new models may need a newer vLLM.

## BriCS shared files

| Path | Contents |
|---|---|
| `/projects/public/brics/data/hf` | `HF_HOME` with pre-downloaded weights, e.g. GPT-OSS-120B |
| `/projects/public/brics/distributed_vllm/` | vLLM config for GPT-OSS-120B on Hopper, and Tiktoken encodings |
| `/projects/public/brics/tutorials/llms/pre-training/` | NeMo image, `adapt.sh`, prepared FineWeb data and tokenizer |
| `/projects/public/brics/tutorials/distributed_torch/`, `.../distributed_vllm/` | Pre-built environments for scheduled workshops |

## Troubleshooting

| Symptom | Cause and fix |
|---|---|
| Multi-node training slow | Using `gloo`, or `brics/nccl` not loaded. Switch to `nccl` and check with `NCCL_DEBUG=INFO` (see the `nccl` skill). |
| Process group hangs at start | Wrong `MASTER_ADDR`/`MASTER_PORT`, or rank variables don't match the `--mpi` type (see the table). |
| All ranks use the same GPU | CUDA device not set from `LOCAL_RANK`. |
| `torch.cuda.is_available()` is `False` after install | Installed on a login node, or a CPU build. Reinstall with `srun --gpus=1`. |
| Job fails at once with no output file | The `--output` directory (e.g. `out/`) doesn't exist. `mkdir -p out` before `sbatch`. |
| Training stopped at the time limit | Resubmit to resume from the last checkpoint; chain jobs with dependencies. |
| Access denied downloading Llama | Licence not yet approved, or the user hasn't run `uvx hf auth login`. |
| vLLM stuck waiting for engine processes | Cancel and resubmit the multi-node job. |
| NCCL or Apptainer errors in multi-node containers | Check the `containers` skill and https://docs.isambard.ac.uk/service-status/known_issues/. |
| Quota exceeded during training | Checkpoints and datasets: clean up and save fewer checkpoints (see the `storage` skill). |

## Further Reading

- Distributed PyTorch training: https://docs.isambard.ac.uk/user-documentation/tutorials/distributed-training/
- Distributed vLLM inference: https://docs.isambard.ac.uk/user-documentation/tutorials/distributed-inference/
- LLM pre-training: https://docs.isambard.ac.uk/user-documentation/tutorials/llms/pre-training/
- LLM fine-tuning: https://docs.isambard.ac.uk/user-documentation/tutorials/llms/fine-tuning/
- PyTorch distributed: https://pytorch.org/docs/stable/distributed.html
