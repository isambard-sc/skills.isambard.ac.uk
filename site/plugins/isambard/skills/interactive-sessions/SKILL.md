---
name: interactive-sessions
description: >
  Guide for interactive sessions on compute nodes of BriCS Isambard
  facilities (Isambard-AI Phase 1 and Phase 2, Isambard 3) with Jupyter and
  VS Code. Covers the JupyterHub web service on Isambard-AI Phase 2
  (apps.isambard.ac.uk/aip2-jupyter, Server Options, the interactive
  reservation, checking time left, stopping the server, failed spawner jobs),
  running JupyterLab as a Slurm job and connecting through an SSH tunnel
  (ssh -L) to the compute node's high speed network address, creating and
  managing custom Jupyter kernels from Conda or virtual environments with
  ipykernel, and VS Code remote tunnels (code tunnel) on a compute node with
  GitHub authentication from a browser or the desktop app. Use this skill
  whenever a user wants a notebook, JupyterLab, JupyterHub or VS Code
  session with a GPU or compute node on Isambard, can't connect to one,
  can't see their environment as a kernel, or asks how to stop one — even if
  they don't say "interactive".
license: >
  CC-BY-SA-4.0. Markdown/image content derived from
  https://docs.isambard.ac.uk/, © 2024 University of Bristol.
compatibility: >
  JupyterHub: Isambard-AI Phase 2 only. Jupyter over an SSH tunnel:
  Isambard-AI Phase 1, Phase 2 and Isambard 3 Grace. VS Code tunnels: documented
  for Isambard-AI. Requires Clifton SSH access for everything except
  JupyterHub, and a GitHub account for VS Code tunnels. Browser sign-in and
  GitHub device authentication must be done by the user.
metadata:
  author: isambard-sc
  version: "1.0"
  source_url: https://docs.isambard.ac.uk/user-documentation/guides/jupyterhub/
  supplementary_urls:
    - https://docs.isambard.ac.uk/user-documentation/guides/jupyter/
    - https://docs.isambard.ac.uk/user-documentation/guides/vscode/
    - https://docs.isambard.ac.uk/user-documentation/guides/slurm-advanced/
    - https://docs.isambard.ac.uk/user-documentation/information/how-isambard-works/
---

# Interactive Sessions on Isambard

Source docs:

- https://docs.isambard.ac.uk/user-documentation/guides/jupyterhub/
- https://docs.isambard.ac.uk/user-documentation/guides/jupyter/
- https://docs.isambard.ac.uk/user-documentation/guides/vscode/

## ⚠️ Critical Rules

- **Run notebooks and IDE servers on compute nodes, never login nodes.**
  VS Code over SSH to a login node is allowed for light editing only (see
  the `login` skill).
- **Stop the session when finished.** A running session holds the
  resources and is charged to the project for its whole length, whether or
  not it is being used (see the `projects-and-accounting` skill). Stop
  JupyterHub from the Hub Control Panel; `scancel` other jobs.
- **Sessions end at the time limit without warning.** Tell the user to
  save work often and to request a time that covers the planned work.
- **JupyterHub with the `interactive` reservation: leave Partition empty.**
  Setting a partition with it is Unacceptable Use under the Acceptable Use
  Policy, and such sessions may be cancelled without warning.
- **The user signs in and runs the tunnel, not the agent.** The JupyterHub
  sign-in, the GitHub device code for VS Code, and the `ssh -L` tunnel are
  done by the user. Don't hold a persistent connection to Isambard (see the
  `login` skill).
- **Never copy workarounds from the Known Issues page into answers.** Send
  the user to https://docs.isambard.ac.uk/service-status/known_issues/ when
  something in a session misbehaves.

## Choosing a method

| Method | Systems | Best for |
|---|---|---|
| JupyterHub (web form) | Isambard-AI Phase 2 | Notebooks without the command line. JupyterHub submits the Slurm job. |
| JupyterLab job + SSH tunnel | Isambard-AI Phase 1, Phase 2, Isambard 3 Grace | Notebooks on systems without JupyterHub, or full control of the job script |
| VS Code tunnel job | Isambard-AI (documented) | Editing and debugging in VS Code on a compute node |
| Shell on a compute node | All | Command-line work: `srun --pty` or the Phase 2 `interactive` reservation (see the `slurm` skill) |

All of them go through Slurm, so all may wait in the queue; the browser or
terminal waits until a node is allocated.

## JupyterHub (Isambard-AI Phase 2)

Prerequisites: membership of a project with Isambard-AI Phase 2 access, and
a UNIX short name set (see the `login` skill).

1. Go to https://apps.isambard.ac.uk/aip2-jupyter and sign in with the
   usual identity provider.
2. Fill in **Server Options**:

   | Setting | Meaning |
   |---|---|
   | Project | Project whose storage and node hours the session uses |
   | Job duration | Session length; it ends after this time |
   | Number of GH200s | 1–4 (up to one node). Each comes with exclusive use of its CPU cores, memory and GPU. |
   | Partition | Usually empty (default partition). Must be empty with the `interactive` reservation. |
   | Reservation | Optional, e.g. `interactive` or a reservation granted to the project |

3. Select **Start**. A status page shows the job pending, then the browser
   opens JupyterLab on the compute node.
4. Use notebooks, consoles and terminals. The project's storage areas are
   available. The JupyterLab NVdashboard extension (GPU icon in the left
   sidebar) shows GPU utilisation. BriCS-managed kernels, such as the one
   for the interactive chatbot tutorial, appear in the Launcher.
5. Stop: **File > Hub Control Panel > Stop My Server**. **Start My Server**
   returns to Server Options.

Time used and left, from a JupyterLab terminal:

```bash
squeue --me --name="spawner-jupyterhub"
```

### Failed or stopped JupyterHub sessions

```bash
sacct --name spawner-jupyterhub --user "$USER"
less jupyterhub_slurmspawner_<JOB_ID>.log
```

| State | Meaning |
|---|---|
| `OUT_OF_MEMORY` | Exceeded the memory allocation: request more GH200s |
| `TIMEOUT` | Reached the job duration |
| `FAILED` | Exited with an error: check the log |
| `CANCELLED` | Cancelled (by the user, or e.g. for misuse of a reservation) |

If it's still unclear, the user raises a ticket with the job ID, the `sacct`
output and the log (see the `getting-support` skill).

## JupyterLab as a job with an SSH tunnel

Use on Isambard-AI Phase 1, Isambard 3 Grace, or Phase 2 when not using
JupyterHub. Requires Conda in the user's home (see the `python` skill).

### 1. Create the Jupyter environment (login node, once)

```yaml
# jupyter-user-environment.yml
name: jupyter-user-env
channels:
  - conda-forge
  - nodefaults
dependencies:
  - jupyterlab >=4.2,<5.0
  - notebook >=7.2,<8.0
```

```bash
source ~/miniforge3/bin/activate
conda env create --file jupyter-user-environment.yml
```

### 2. Submit the job

The server listens on the compute node's Slingshot high speed network
(HSN) address. Isambard-AI Phase 2 version:

```bash
#!/bin/bash
#SBATCH --job-name=jupyter_user_session
#SBATCH --nodes=1
#SBATCH --gpus=1  # this also allocates 72 CPU cores and 115GB memory
#SBATCH --time=01:00:00

source ~/miniforge3/bin/activate jupyter-user-env

# Add pre-installed kernelspecs to the Jupyter data search path
export JUPYTER_PATH="/tools/brics/jupyter/jupyter_data${JUPYTER_PATH:+:}${JUPYTER_PATH:-}"

HSN_FQDN="$(hostname).hsn.ai-p2.isambard.ac.uk"
LISTEN_IP=$(dig "${HSN_FQDN}" A +short | tail -n 1)
LISTEN_PORT=8888

set -o xtrace
jupyter lab --no-browser --ip="${LISTEN_IP}" --port="${LISTEN_PORT}"
```

Per system:

| System | `HSN_FQDN` domain | HSN address | Resources in the docs' script |
|---|---|---|---|
| Isambard-AI Phase 1 | `hsn.ai-p1.isambard.ac.uk` | `10.253.x.y` | `--gpus=1` |
| Isambard-AI Phase 2 | `hsn.ai-p2.isambard.ac.uk` | `10.242.x.y` | `--gpus=1` |
| Isambard 3 Grace | `hsn.cm.i3.isambard.ac.uk` | `10.243.x.y` | `--ntasks=1 --mem=0 --exclusive` (whole node, no `--gpus`) |

Adjust `--time` and resources to the planned work, then
`sbatch <script>` and note the job ID.

### 3. Get the address and token

When the job runs, read `slurm-<JOB_ID>.out` for a URL such as:

```text
http://10.242.8.242:8888/lab?token=c5185e5adb2574941d4f5136a7df23e3a441b56452bf9db0
```

This gives `<IP_ADDRESS>`, `<PORT>` and `<TOKEN>`.

### 4. Open the tunnel and browser (user's own machine)

Using the Clifton-generated host alias (see the `login` skill):

```bash
ssh -T -L localhost:8888:<IP_ADDRESS>:<PORT> <PROJECT>.aip2.isambard
```

Use `<PROJECT>.aip1.isambard` on Phase 1 and `<PROJECT>.3.isambard` on
Isambard 3. The command prints nothing when it works; leave it running.
Then open `http://localhost:8888/lab?token=<TOKEN>` in a browser.

### 5. Stop

**File > Shut Down** in JupyterLab ends the job. If that fails, run
`scancel <JOB_ID>` on a login node. Then stop the `ssh -T -L` command
(Ctrl+C or close the terminal).

## Custom Jupyter kernels

Use these to make a Conda or virtual environment's packages available in
notebooks, with JupyterHub or a JupyterLab job. Run on a login node or in a
JupyterLab terminal. The environment **must contain `ipykernel`**.

Conda:

```bash
source ~/miniforge3/bin/activate
conda install --name <ENV_NAME> ipykernel   # if the environment exists
conda activate <ENV_NAME>
python -m ipykernel install --user --name "${CONDA_DEFAULT_ENV}" --display-name "Python (${CONDA_DEFAULT_ENV})"
conda deactivate
```

Python virtual environment:

```bash
module load cray-python
python -m venv --upgrade-deps ~/venvs/<VENV_NAME>
~/venvs/<VENV_NAME>/bin/python -m pip install ipykernel <PACKAGES>
source ~/venvs/<VENV_NAME>/bin/activate
python -m ipykernel install --user --name "$(basename ${VIRTUAL_ENV})" --display-name "Python ($(basename ${VIRTUAL_ENV}))"
deactivate
```

Kernel specs go in `~/.local/share/jupyter/kernels`. `--name` must be
unique; `--display-name` appears in the Launcher. In a new or running
session, choose the kernel from the Launcher or the kernel name at the top
right of a notebook.

Manage them where `jupyter` is available (e.g. in `jupyter-user-env`):

```bash
jupyter kernelspec list
jupyter kernelspec remove <KERNEL_NAME>
```

## VS Code on a compute node (remote tunnel)

Requires a GitHub account. Documented for Isambard-AI.

### 1. Install the VS Code CLI (login node, once)

```bash
curl --location --output vscode_cli.tar.gz "https://update.code.visualstudio.com/latest/cli-linux-arm64/stable"
mkdir -p ~/opt/vscode_cli
tar -C ~/opt/vscode_cli --extract --verbose --file vscode_cli.tar.gz
~/opt/vscode_cli/code --version
```

### 2. Submit the tunnel job

```bash
#!/bin/bash
#SBATCH --job-name=code_tunnel
#SBATCH --nodes=1
#SBATCH --gpus=1            # this also allocates 72 CPU cores and 115GB memory
#SBATCH --time=1:00:00
#SBATCH --output=code_tunnel_%j.out

# Start named VS Code tunnel for remote connection to compute node
~/opt/vscode_cli/code tunnel --name "i-ai_compute"
```

`sbatch` it, and when it runs read `code_tunnel_<JOB_ID>.out`. It gives a
device code: the user enters it at https://github.com/login/device. It also
gives a `https://vscode.dev/tunnel/<NAME>/...` link.

### 3. Connect

- **Browser:** open the `vscode.dev` link and choose GitHub as the account
  type. Try this first.
- **Desktop:** install the "Remote - Tunnels" extension (and optionally
  "Remote Explorer"). Run **Remote-Tunnels: Connect to Tunnel...** from the
  Command Palette, choose GitHub, sign in, and select the tunnel name
  (`i-ai_compute` above).

### 4. Stop

`scancel <JOB_ID>` from a login node (`squeue --me` to find it).

## Troubleshooting

| Symptom | Cause and fix |
|---|---|
| JupyterHub session pending a long time | Waiting in the Slurm queue. For short exploratory work, the `interactive` reservation has shorter queue times (leave Partition empty). |
| JupyterHub session ended unexpectedly | Check `sacct --name spawner-jupyterhub` and the spawner log (see above). |
| Session ended mid-work | Reached its time limit. Start a new session with a longer duration. |
| `$LOCALDIR` or `$TMPDIR` fails in a JupyterHub session | Check https://docs.isambard.ac.uk/service-status/known_issues/. |
| Browser can't reach `localhost:8888` | Tunnel not running, wrong `<IP_ADDRESS>:<PORT>`, or the job ended. Check the job with `squeue --me` and the address in `slurm-<JOB_ID>.out`. |
| SSH tunnel fails to connect | Certificate expired: run `clifton auth` (see the `login` skill). |
| Environment not listed as a kernel | `ipykernel` missing from it, or `python -m ipykernel install --user` not run in it. Check `jupyter kernelspec list`. |
| BriCS kernels missing in a JupyterLab job | `JUPYTER_PATH` line missing from the job script. |
| Jobs in the `interactive` reservation missing from `squeue --me` | The partition is hidden: `squeue --me --partition=interactive`. |
| VS Code desktop can't connect to the tunnel | Test the browser link first. Update VS Code, and try an empty profile (no extensions). |

## Further Reading

- JupyterHub: https://docs.isambard.ac.uk/user-documentation/guides/jupyterhub/
- Jupyter on a compute node: https://docs.isambard.ac.uk/user-documentation/guides/jupyter/
- VS Code: https://docs.isambard.ac.uk/user-documentation/guides/vscode/
- `interactive` reservation: https://docs.isambard.ac.uk/user-documentation/guides/slurm-advanced/
- How Isambard works: https://docs.isambard.ac.uk/user-documentation/information/how-isambard-works/
