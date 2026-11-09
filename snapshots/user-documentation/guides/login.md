<!-- Snapshot of https://docs.isambard.ac.uk/user-documentation/guides/login/ made by snapshot_docs.py. Do not edit. -->

# Log in (SSH and Clifton)

## Setting your UNIX short name

Before you can log in to any of the BriCS facilities you will need to set your UNIX short name. This is a short name that is unique to you and is used to identify you on the system. Make sure you have set your UNIX short name by following the instructions in the guide.

## Generating your SSH key pair

The first step is to make sure you have an SSH key pair. This is used to authenticate you when you try to log into any of the centre's supercomputers using SSH.

Supported SSH key types

We only support modern SSH keys (i.e. RSA keys of 3072 bits or more, or Ed25519, or any other modern, post-2014 key type). We do not support DSA keys, or RSA keys of less than 3072 bits. Any key generated using a modern version of `ssh-keygen` should be fine, e.g. the private key must contain `-----BEGIN OPENSSH PRIVATE KEY-----`

If you already have a key pair then feel free to use it. But if you don't have an SSH key then you can generate one using `ssh-keygen`.

```
ssh-keygen -t ed25519 -C "[email protected]"

```

For more detailed information on generating and managing SSH keys, see GitHub's documentation on generating an SSH key.

Setting up an `ssh-agent` (as described in the documentation above) is not a requirement, but it is recommended as it can simplify key management.

## Connecting using `clifton`

To connect to one of the BriCS facilities using SSH you will need to use signed SSH certificates. We provide a command line tool called Clifton for obtaining SSH certificates and configuring your SSH client to use these. The certificates are valid for 12 hours.

### Install

The latest release of Clifton is available at GitHub but we describe below automatic ways to install it. To install Clifton choose your operating system from the tabs below:

=== "macOS"

Download the binary of Clifton using `curl`:

=== "Apple Silicon (Arm)"

```
curl --location https://github.com/isambard-sc/clifton/releases/latest/download/clifton-macos-aarch64 --output clifton
chmod u+x clifton

```

=== "Intel"

```
curl --location https://github.com/isambard-sc/clifton/releases/latest/download/clifton-macos-x86_64 --output clifton
chmod u+x clifton

```

If you want it accessible from any directory on your computer, you can place the binary in `/usr/local/bin` with:

```
sudo mv clifton /usr/local/bin/

```

If you don't, you will need to specify the path to the executable when running it. So instead of `clifton auth` as described below you would run e.g. `./clifton auth` or `~/clifton auth`.

To update Clifton, run those same commands again.

Allowing Clifton to run on macOS

If you download the Clifton through your web browser rather than with `curl`, you may be presented with a macOS warning dialog when trying to run the executable, e.g.

"clifton" can't be opened because Apple cannot check it for malicious software.

If this occurs you will have to go into "System Settings > Privacy & Security" and allow use of the `clifton` executable (see Open a Mac app from an unidentified developer from the macOS documentation). Note that you will need to have admin privileges to change the settings in "Privacy & Security".

=== "Linux (including WSL)"

=== "x86_64"

```
curl --location https://github.com/isambard-sc/clifton/releases/latest/download/clifton-linux-musl-x86_64 --output clifton
chmod u+x clifton

```

=== "AArch64"

```
curl --location https://github.com/isambard-sc/clifton/releases/latest/download/clifton-linux-musl-aarch64 --output clifton
chmod u+x clifton

```

If you want it accessible from any directory on your computer, you can place the binary in `~/.local/bin` (or any directory on your `$PATH` you wish) with:

```
mkdir -p ~/.local/bin
mv clifton ~/.local/bin/

```

If you don't, you will need to specify the path to the executable when running it. So instead of `clifton auth` as described below you would run e.g. `./clifton auth` or `~/clifton auth`.

To update Clifton, run those same commands again.

Alternatively, a tool like `mise` can install it for you with `mise use -g ubi:isambard-sc/clifton`.

=== "Windows"

Clifton is available through WinGet. WinGet is a package installer from Microsoft which is installed by default on most Windows computers.

Open a terminal window (search for "Terminal" or "Powershell" in the search bar at the bottom) and run:

```
winget install clifton

```

You will then need to close and reopen the terminal window before you can run any `clifton` commands.

To update clifton, run `winget upgrade clifton`.

If WinGet is not available then you can download the file manually using

```
curl.exe --location https://github.com/isambard-sc/clifton/releases/latest/download/clifton-windows-x86_64.exe --output clifton.exe

```

If you have downloaded Clifton manually, when running it you will need to specify the path. So instead of `clifton auth` as described below you would run e.g. `./clifton auth` or `~/clifton auth`.

### Authenticate

To use Clifton to obtain an SSH certificate, run this in a terminal window:

```
clifton auth

```

Specify an SSH key for Clifton to use

By default Clifton will look for existing SSH keys in standard locations (e.g. `~/.ssh/id_ed25519`). If your SSH key is in a non-standard location, you can tell Clifton which key to use to create the certificate by using the `--identity` option, e.g.

```
clifton auth --identity /path/to/ssh_key

```

Missing short name

If you see the error "Something went wrong: User short name is empty." then this means that you have not set your UNIX short name. Please follow the instructions in this guide to set your shortname, then try again.

The `auth` command will open your browser and direct you to the portal, where you can authorise access to Clifton. Use the same account to log in as you did during the setup stage. Alternatively, you can scan the QR code on your mobile. On successful authentication you will see something like the following:

```
Successfully authenticated as YOUR_EMAIL_ADDRESS (YOUR_SHORT_NAME) and downloaded SSH certificate for projects:
 - PROJECT_NAME

Certificate file written to ~/.ssh/id_ed25519-cert.pub
Certificate valid for 11 hours and 59 minutes.
You may now want to run `clifton ssh-config write` to configure your SSH config aliases.

```

Using the `ssh-config write` command, Clifton will write an ssh config file `~/.ssh/config_clifton` and `Include` it in your main ssh config `~/.ssh/config` automatically:

```
clifton ssh-config write

```

It will also print out the list of SSH host aliases available to you, to be used in the next step. Each host alias is a dotted name containing your project ID and the name of the resource you can connect to.

When to run `clifton`

You only need to run `clifton ssh-config write` if you have been added to a new project since the last time you ran it. However, you will need to run `clifton auth` each day that you want to use the service.

### Connect

You will now be able to log in using your project-specific account into a BriCS facility that the project is authorised to access, as shown by the output of `clifton ssh-config write`. For example, to connect to your account for the project `EXAMPLE_PROJECT` (Replace `EXAMPLE_PROJECT` with your actual project code):

=== "Isambard-AI"

```
ssh EXAMPLE_PROJECT.aip2.isambard

```

=== "Isambard 3"

```
ssh EXAMPLE_PROJECT.3.isambard

```

=== "Isambard 3 MACS"

```
ssh EXAMPLE_PROJECT.macs3.isambard

```

=== "BlueCrystal 5"

```
ssh EXAMPLE_PROJECT.bc5.digital-labs

```

UoB VPN

When working away from campus, or when connected to a network other than eduroam, you will need to be connected to UoB's Virtual Private Network to log in to BlueCrystal 5.

SSH Certificates are only valid for 12 Hours

Your signed SSH certificates are only valid for 12 hours. After 12 hours, you will need to rerun `clifton auth`

Shell timeout

Bash will terminate the session if no input is received within 24 hours. This limit is set to reduce issues with long running shell sessions (e.g. via software such as `tmux`) on the login node.

## Host fingerprints

The first time you log in you may be asked to confirm the identity of the remote server. These are the possible fingerprints of the host keys which are displayed:

=== "ai.login.isambard.ac.uk"

Remote login server

| Host Key Type | Fingerprint |
| ECDSA | `SHA256:U3sr8Uxo1JF/cgfpXRTs/D4E6wk8watGKGHdU9EjsJM` |
| ED25519 | `SHA256:WT11ouKX6R4Xw81pzLuvfxR0OU5xmf2jBkKESBA8Sfw` |
| RSA | `SHA256:bkNkrY6OpeBvbkyyKtGe5sAaDj713jIRDMFuHzjXarU` |

=== "ai-p2.access.isambard.ac.uk"

Isambard-AI Phase 2

| Host Key Type | Fingerprint |
| ECDSA | `SHA256:asi1gSKS17jZs0WaX3P6FhMCzEjRH52EidZTQ/Qh9+g` |
| ED25519 | `SHA256:jLwRcG3g1kDJwTHBqc3JdgZA99UQ5baO6ALIaNMZTyA` |
| RSA | `SHA256:rPLDdQhhWXbIp5ezSTK07isq78QKK8eb9Q5gfwFeRXY` |

=== "ai-p1.access.isambard.ac.uk"

Isambard-AI Phase 1

| Host Key Type | Fingerprint |
| ECDSA | `SHA256:UePsqQ/AaDzDspJF4kxDIK2RS1W/a+T8w++Zb21fEtk` |
| ED25519 | `SHA256:mIqtQibJXK/Z1UtX66RMz9A/f7qhwF0gk+qb3ZHIlS4` |
| RSA | `SHA256:RRRxm5WIRd+rLA3xg0SVwvmvxGgmiB6lGuO6DEEtudk` |

=== "i3.access.isambard.ac.uk"

Isambard 3

| Host Key Type | Fingerprint |
| ECDSA | `SHA256:8kFv9/ywom3dJ2JUZbQEjc8yaRprsFJ2sho6a2sE1/g` |
| ED25519 | `SHA256:xoWObzEBWd71ZhUFmDxzsVHB1vHX4OexFfkY0m0rnkE` |
| RSA | `SHA256:o3+orD115AU8QlUhoLjrQBXCh47EeZzMkVfFHOYeW0I` |

=== "i3macs.access.isambard.ac.uk"

Isambard 3 MACS

| Host Key Type | Fingerprint |
| ECDSA | `SHA256:8kFv9/ywom3dJ2JUZbQEjc8yaRprsFJ2sho6a2sE1/g` |
| ED25519 | `SHA256:xoWObzEBWd71ZhUFmDxzsVHB1vHX4OexFfkY0m0rnkE` |
| RSA | `SHA256:o3+orD115AU8QlUhoLjrQBXCh47EeZzMkVfFHOYeW0I` |

=== "digital-labs.bristol.ac.uk"

BlueCrystal 5

| Host Key Type | Fingerprint |
| ECDSA | `SHA256:/A0V4pKSeyrDA7OXTZEeeHngt7KbqQNTU9g337WrNF4` |
| ED25519 | `SHA256:w3BN2vpTK2+JsJyblHGLI2D0LnTQm1oz9uEBPUfGi0M` |
| RSA | `SHA256:vwt7pgfLD4AxysrFlUlRWAX43OA3C8yfeuHh6yiTaRM` |

## Working on the login node

Once you have connected to the facility using `ssh`, an interactive command line session on a login node of the chosen facility (e.g. Isambard-AI, Isambard 3) will start, e.g.

=== "Isambard-AI"

isambard-session
```
$ ssh project.aip1.isambard
 ___                _                 _      _   ___
|_ _|___ __ _ _ __ | |__  __ _ _ _ __| |___ /_\ |_ _|
 | |(_-</ _` | '  \| '_ \/ _` | '_/ _` |___/ _ \ | |
|___/__/\__,_|_|_|_|_.__/\__,_|_| \__,_|  /_/ \_\___|

User Documentation: https://docs.isambard.ac.uk
BriCS Helpdesk: https://support.isambard.ac.uk
Service Status: https://status.isambard.ac.uk

user.project@nid001040:~>

```

=== "Isambard 3"

isambard-session
```
$ ssh project.3.isambard 
 ___                _                 _   ____
|_ _|___ __ _ _ __ | |__  __ _ _ _ __| | |__ /
 | |(_-</ _` | '  \| '_ \/ _` | '_/ _` |  |_ \
|___/__/\__,_|_|_|_|_.__/\__,_|_| \__,_| |___/

User Documentation: https://docs.isambard.ac.uk
BriCS Helpdesk:     https://support.isambard.ac.uk
Service Status:     https://status.isambard.ac.uk 

user.project@login02:~>

```

=== "Isambard 3 MACS"

isambard-session
```
$ ssh project.macs3.isambard
 ___                _                 _   ____
|_ _|___ __ _ _ __ | |__  __ _ _ _ __| | |__ /
 | |(_-</ _` | '  \| '_ \/ _` | '_/ _` |  |_ \
|___/__/\__,_|_|_|_|_.__/\__,_|_| \__,_| |___/

User Documentation: https://docs.isambard.ac.uk
BriCS Helpdesk:     https://support.isambard.ac.uk
Service Status:     https://status.isambard.ac.uk 

user.project@login05:~>

```

=== "BlueCrystal 5"

```
$ ssh project.bc5.digital-labs
    ____  __           ______                __        __   ______
   / __ )/ /_  _____  / ____/______  _______/ /_____ _/ /  / ____/
  / __  / / / / / _ \/ /   / ___/ / / / ___/ __/ __ `/ /  /___ \
 / /_/ / / /_/ /  __/ /___/ /  / /_/ (__  ) /_/ /_/ / /  ____/ /
/_____/_/\__,_/\___/\____/_/   \__, /____/\__/\__,_/_/  /_____/

[user.project@bc5-login01 ~]$

```

You can now use command line tools to access and work with files on the facility's shared filesystem storage spaces. You can also submit batch jobs to run on the facility's compute nodes and manage these jobs using the Slurm workload manager.

Login node assignment

Login nodes are assigned randomly at SSH connection time. Different sessions may connect to different login node servers, even when connecting from the same machine.

This random assignment is used to balance load across multiple machines and to accommodate the failure or unavailability of individual login nodes at any particular time. Users cannot specify a particular login node when logging in.

The login nodes may be used for interactive work needed to prepare compute jobs and deal with their results, e.g. file transfer/compression, software/container builds and installation, editing/manipulating files. They should not be used for long-running or compute-intensive workloads, which should always be submitted to compute nodes using the workload manager. This includes large data transfers, such as copying a project's data to another project: the login nodes are not a free transfer resource, and a large copy started on one is likely to be stopped for exceeding the memory limit. Submit these as a job instead, as described in transferring large amounts of data as a job. The login nodes also have cgroup-based resource limits on CPU, memory, and tasks in place to keep interactive sessions responsive for all users. For the current values, see the FAQ entry on login node resource limits. If your work needs more processing power, submit it as a job on the compute nodes using the Slurm workload manager.

Do not run long-running or compute-intensive jobs on login nodes

The login nodes are a shared resource which provide you and other users of the system with an interactive interface to shared storage systems and compute resources.

Running long-running or compute-intensive workloads on login nodes can impair their functionality for you and other users. This is considered an activity that is detrimental to the operation of BriCS facilities, a form of Unacceptable Use under the Acceptable Use Policy.

Any long-running or compute-intensive workloads running on login nodes may be stopped without warning by BriCS staff. Repeated and/or deliberate misuse of login nodes in this way will be subject to the procedures outlined in the Penalties for Misuse section of the Acceptable Use Policy.

Terminal multiplexers and persistent sessions

Terminal multiplexers such as `tmux` and `screen` may be used for managing multiple terminal windows within a single SSH session. However, we do not support the use of these tools for persistent sessions that continue after you disconnect.

Long-running `tmux`, `screen` or similar sessions left running on login nodes are against our security policy. Access to BriCS facilities relies on time-limited SSH certificates, which are valid for 12 hours. Persistent sessions would bypass this security boundary by maintaining an authenticated connection indefinitely, without requiring credentials to be refreshed. Additionally, because login nodes are assigned randomly and you cannot specify a particular login node, you may not be able to reconnect to a persistent session after disconnecting. Any persistent sessions may be terminated without warning by BriCS staff. Any attempt to bypass the intended functionality of the time-limited SSH certificates, including by AI agents, is a violation of the Access Terms. See our guide to using AI agents with Isambard for recommended workflows that keep agents within these limits.

For long-running workloads, please submit jobs to compute nodes using the Slurm workload manager.

Logging in via VS Code

Interacting with the login node over SSH via VS Code (or similar IDE) is allowed, as long as your usage adheres to the above policies and does not adversely affect the work of other users.

Lightweight interactive work, such as editing files, is permitted on the login node but compute-intensive work must be run on the compute nodes. Users should ensure that VS Code is not running compute-intensive or long-running processes in the background on login nodes. Any disruptive processes may be stopped without warning by BriCS staff. For the current values, see the FAQ entry on login node resource limits. If you need more processing power, submit the work to the compute nodes using the Slurm workload manager.

An interactive VS Code session can be run directly on a compute node.

## What's next?

Now that you have logged in to a supercomputer, you can start using the services provided by the Bristol Centre for Supercomputing.

Please explore the rest of the documentation to learn more. You can submit your first batch job using slurm, or go through the tutorial to create your own chatbot!

- Submit your first job using slurm
- Tutorials
