# docs.isambard.ac.uk URL map

Pick the ONE page that best matches the question, fetch it, and answer from
it. All paths are relative to `https://docs.isambard.ac.uk`. If a path
returns 404, re-check `https://docs.isambard.ac.uk/sitemap.xml`.

## Start here / orientation

- `/` — landing page and top-level navigation
- `/user-documentation/getting_started/` — first steps once access is
  granted (accounts, portal, first login)
- `/user-documentation/tutorials/setup/` — end-to-end setup tutorial:
  clifton install, auth, SSH config, first job
- `/user-documentation/tutorials/intro-tour/` — guided tour for new users
- `/user-documentation/information/how-isambard-works/` — architecture:
  login vs compute nodes, how the pieces fit together
- `/specs/` — hardware specs: GH200 nodes, Grace nodes, MACS, interconnect
- `/user-documentation/faqs/` — FAQ index
  (`/user-documentation/faqs/bc5-launch/` for BlueCrystal 5)

## Access & projects

- `/access/` — how to apply for time on Isambard
- `/user-documentation/information/portals/` — the web portals and what
  each is for
- `/user-documentation/guides/awards_portal/` — awards/allocation portal
- `/user-documentation/guides/manage_project/` — PI tasks: adding members,
  managing the project
- `/user-documentation/guides/follow_on_project/` — follow-on projects
- `/user-documentation/guides/accounting/` — GPU-hour/CPU-hour usage and
  allocation accounting
- `/user-documentation/guides/aws_accounts/` — linked AWS accounts
- `/user-documentation/information/project-policies/` — project lifecycle,
  data retention at project end

## Connecting & transferring data

- `/user-documentation/guides/login/` — SSH login via clifton
  (certificates valid 12 h → `clifton auth` daily)
- `/user-documentation/guides/shortname/` — setting the UNIX short name
- `/user-documentation/guides/mobaxterm/` — Windows / MobaXterm setup
- `/user-documentation/guides/file_transfer/` — scp/rsync data transfer
- `/user-documentation/tutorials/data-mover/` — data-mover nodes for large
  transfers
- `/user-documentation/guides/vscode/` — VS Code Remote-SSH
- `/user-documentation/guides/jupyter/` — Jupyter on compute nodes
- `/user-documentation/guides/jupyterhub/` — the BriCS JupyterHub service

## Jobs & scheduling (Slurm)

- `/user-documentation/guides/slurm/` — Slurm basics; `--gpus` is required
  on Isambard-AI
- `/user-documentation/guides/slurm-examples/` — ready-made job scripts
- `/user-documentation/guides/slurm-advanced/` — arrays, dependencies,
  chaining jobs beyond 24 h, job steps
- `/user-documentation/guides/slurm-troubleshooting/` — pending/failed
  jobs, common Slurm errors
- `/user-documentation/information/job-scheduling/` — partitions, QoS,
  walltime and GPU limits, fair-share
- `/user-documentation/guides/argo-workflows/` — Argo Workflows service

## Storage

- `/user-documentation/information/system-storage/` — `$HOME`,
  `$SCRATCHDIR`, `$PROJECTDIR`, `$LOCALDIR`, quotas, retention
- `/user-documentation/tutorials/datasets-in-squashfs/` — packing
  many-file datasets into SquashFS

## Software environments

- `/user-documentation/guides/modules/` — module system, Cray PrgEnv,
  compiler wrappers
- `/user-documentation/guides/environment_variables/` — predefined
  environment variables
- `/user-documentation/guides/python/` — Miniforge/conda, uv, venvs,
  aarch64 wheel pitfalls
- `/user-documentation/guides/spack/` (and `spack/setup/`) — building
  software with Spack and the buildit configs
- `/user-documentation/guides/e4s/` — E4S software stack
- `/user-documentation/guides/containers/` — Podman-HPC vs Apptainer
  overview (single/multi-node pages live under this path)
- `/user-documentation/guides/gpus_and_cuda/` — CUDA toolkits, sm_90,
  forward compatibility
- `/user-documentation/guides/mpi/` — Cray MPICH/OpenMPI, `srun --mpi`
- `/user-documentation/guides/nccl/` — NCCL over Slingshot 11
- `/user-documentation/guides/using_ai_agents/` — policy and guidance for
  using AI agents with Isambard

## ML & applications

- `/user-documentation/applications/ML-packages/` — PyTorch/JAX/TensorFlow
  on GH200
- `/user-documentation/tutorials/distributed-training/` — multi-node
  distributed PyTorch
- `/user-documentation/tutorials/distributed-inference/` — multi-node vLLM
- `/user-documentation/tutorials/interactive-ml/` — interactive ML session
- `/user-documentation/applications/alphafold/` — AlphaFold (see also
  `/user-documentation/tutorials/interactive-alphafold/`)
- `/user-documentation/applications/relion/` — Relion (cryo-EM)
- `/user-documentation/applications/orca/` — ORCA (quantum chemistry)

## Service status (use the service-status skill)

- `/service-status/` — current per-system status overview
- `/service-status/known_issues/` — active known issues
- `/service-status/planned_maintenance/` — upcoming maintenance windows
- `/service-status/archived_issues/` — resolved past issues

## Support, policies, misc

- `/getting_support/` — how to raise a ticket
- `/policies/` — acceptable use, access terms, privacy, licensing,
  resource management, shared responsibility
- `/acknowledge/` — acknowledging Isambard in publications
- `/training/` — training events (materials under `/training/<event>/`)
- `/events/` — Isambard Summit and open days
- `/about/` — about the documentation site
