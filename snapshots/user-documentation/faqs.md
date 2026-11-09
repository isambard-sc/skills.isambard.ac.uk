<!-- Snapshot of https://docs.isambard.ac.uk/user-documentation/faqs/ made by snapshot_docs.py. Do not edit. -->

# Frequently Asked Questions

This page contains a series of brief how-to style questions. Users are directed to also consult the main documentation before raising a support request.

## Systems and access

### How do I access Isambard?

Isambard-AI and Isambard 3 are two different supercomputer services with different funding sources, access routes and associated eligibility criteria.

- Isambard 3 is a CPU-based supercomputer optimised for traditional numerical simulation workloads. It is funded via UKRI and access calls are open to users eligible via UKRI tier 2 calls, or calls run internally to the GW4 alliance.
- Isambard-AI consists of two separate machines- Phase 1 and Phase 2. Both are very large GPU-based supercomputers optimised for artificial intelligence and machine learning workloads. Although Phase 2 is much larger than Phase 1, every compute node in both machines has the same architecture and compute performance. The service is funded by DBIST and access calls are open to users from non-traditional sectors.

Further details can be found on the access page, and further funding information on the acknowledgements page.

### Can I get access from outside the UK?

There are several compliance and technical reasons why you may not be able to connect from outside the UK. These are almost always outside the control of BriCS and so our ability to help is limited. If you are unable to connect and you believe this to be an issue with a BriCS service, please raise a helpdesk ticket.

### What is Isambard 3 MACS?

The Multi-Architecture Comparison System (MACS) nodes is a collection of different types of hardware available on Isambard 3. Further information can be found on the system specifications page.

### How can I invite someone to my project?

Only those with the Principal Investigator (PI) role may invite users to a project. Within the parameters of their responsibilities they may invite anyone to join, including collaborators and members of local RSE or technical teams.

### Could you extend my project or add more node hours?

We do not have any control over the allocation of node hours or the duration of projects. Please contact the allocator for your project to request an extension or additional node hours.

### Can you delay the start of my project?

No. BriCS does not have the authority to delay the start of a project. Please contact the allocator for your project to request a delay.

### My student has just graduated and is now an alumnus or is no longer at the university. Can they keep their account?

No. BriCS accounts must be backed by valid professional or institutional email addresses. These demonstrate that the person using the service is a member of the organisation or institution that issued that email address, and that this institution is accepting liability for the actions of that person (the Access Terms are an agreement between the University of Bristol and the legal entity representing the employer or institution of the user). If a user leaves their institution, they must also leave the service. The Project Lead is responsible for managing user access and ensuring compliance with these terms. Note that many universities provide routes by which students can be granted "visiting" or "honorary" or "associate" status, whereby the university continues to accept liability for the actions of that person. You should contact your university to see if this is possible in your case.

### Can you extend the grace period so I can finish copying back my data?

No. BriCS does not have the authority to extend the grace period for an individual project. The Project Lead is responsible for ensuring that copying back of data is completed within the 30-day grade period provided to each project. Extensions can only be granted by the allocating body. Please contact the allocator for your project to request an extension.

## Getting started

### My invitation link isn't working — what should I do?

There are a few reasons why your invitation link may not work.

It has expired. If you are the Project Lead, contact the support email address provided in the invitation. Otherwise, ask your Project Lead to resend the invitation via the appropriate portal (e.g. Awards Portal or the BriCS Portal).

It is for a different email address. The invitation must use the exact address your institution registers with MyAccessID. Some universities register a standardised format, e.g. `[email protected]`, rather than a human-readable alias, e.g. `[email protected]`. MyAccessID does not treat these as the same address, so an invitation sent to the human-readable alias will not work - you must be invited using the `[email protected]` form. The login error message shows the address that was used, so you can check which one you need. Ask your Project Lead to resend the invitation to the correct address; invitations cannot be forwarded to a different address yourself.

There is an outage. Please consult the status page to check.

(Academic users) Your institution doesn't support MyAccessID. A small number of UK academic institutions have limited or no support for MyAccessID. Please contact your institution's IT team in the first instance. If this is not successful, please contact your Project Lead and ask them to raise a helpdesk ticket to request an 'IDP of last resort' account.

### How do I log in via SSH?

You need to be a member of a project with access to Isambard-AI or Isambard3 to be able to log in. If you are a member of a project, then you can connect via SSH using the "clifton" tool that we provide. This is used to obtain a signed SSH certificate that will grant you access.

Full details are provided on the getting started page.

### Where do I find `clifton`?

`-bash: clifton: command not found`

If you obtain an error like the above, then ensure you have followed the instructions to download and install clifton.

Note that a minority of Linux systems do not have `~/.local/bin/` in the `$PATH`. Several workarounds may be appropriate, depending on the restrictions on your machine:

- Add `~/.local/bin/` to your `$PATH`
- Move `clifton` to a different location that is in your `$PATH`
- Keep `clifton` in your `$HOME` directory and launch e.g. using `$HOME/clifton`

### How do I get SSH access to my new project?

All new projects are initiated with an invitation email to the PI, which must be accepted before expiry. The PI must then invite users to this project, who must also accept their invitations. After this, new users should follow the getting started guide. Users working via SSH that already have an existing project should rerun `clifton auth` and then `clifton ssh-config write`.

If this is not successful, users should log out and trigger a fresh login. Do this by visiting account.isambard.ac.uk and log out by clicking on your name and repeating the above advice.

Please also see the follow-on projects guide.

### Why is my SSH session ending?

SSH session will automatically be closed after a period of inactivity. If you are finding that your session is getting closed too early you can modify your `~/.ssh/config` file to so that a signal is sent at regular intervals to prevent this time out. The parameter is `ServerAliveInterval` and can be set like so:

```
Match originalhost *.isambard
    ServerAliveInterval 60

```

You should not need to set the value to below 60, or above 480.

### How do I add additional SSH config to Clifton-generated config?

The SSH config file generated by Clifton should not be edited manually as future runs of Clifton may overwrite it. Instead, you can add config to your normal `~/.ssh/config` file.

See here for an example.

### How do I set my short name?

`"Something went wrong: User short name is empty."`

You will see this error if you have not set your UNIX username in the portal. To set your UNIX username, please follow these instructions.

### How do I submit a helpdesk ticket?

To submit a helpdesk ticket, you will need to be a member of an active project. Log in to the helpdesk and click the plus icon at the bottom left of the screen. This will open up a window where you can type in the title and detail of your ticket. Also see the helpdesk guide.

## General use and software

### Can you install my application for me?

The Isambard supercomputers use a self-service model for applications. The range of applications, versions and other variants required by our diverse user base is too large for this approach to work. Moreover, a self-service approach encourages best practice with regards to traceability and reproducibility. In some cases, licencing conditions preclude central installation although individual projects may be able to share executables using the `/projects/[PROJECT]` directory.

To support users, we have provided a range of guides that allow easy installation of many widely used applications:

- Conda and Python
- Spack
- Containers

Where possible we will provide information for specific applications. PIs may also invite additional users to provide support, such as local RSE teams.

### My application isn't working, what should I do?

For general issues with running software on the BriCS services:

- Check the documentation for your application.
- If running on Isambard-AI or Isambard 3, ensure that your installation is compatible with Isambard's aarch-64 architecture.
- Ensure that the appropriate modules are loaded.
- Verify that your environment setup is consistent with your package's requirements.

We recommend building and running your software in a container where possible. Containers bundle the exact dependencies, compilers, and libraries the software expects, which can avoid the common pain of resolving version mismatches or missing libraries on the host system.

More detailed tutorials, guides and information on commonly used applications are available in the user documentation. Open a support ticket if you believe you have encountered an issue with the BriCS service. Please note that we are unable to help users with installation or use of their software.

### How can I use a different version of CUDA?

We only provide the system bundled CUDA on Isambard-AI. The available version can be seen by running `module av cudatoolkit`.

There are two options for using a different version of CUDA other than building from source:

- Conda can be used to install CUDA, see anaconda.org for the versions available for `aarch64`.
- Containers from Nvidia GPU Cloud (NGC) provide every version of CUDA.

Please follow the following guides for using Conda or containers on BriCS facilities:

- Python and Conda
- Containers

### How can I use a package that is not built for Arm architecture (aarch64)?

Support for aarch64 in common package managers is improving significantly and build recipes should be usable with minimal modification. For compiled applications, tools such as Spack can significantly simplify the process. For Python packages, please see the Python: Building from Source on aarch64 guide.

Note the x86 binaries compiled for eg AMD or Intel processors will not run on Isambard 3 or Isambard-AI compute nodes.

### How do I set the timezone?

Internally, the Isambard services use UTC as the system time. You can change the timezone you see by setting the `TZ` environment variable, for example:

```
export TZ=GB

```

A full list of timezones can be found at this wikipedia page.

### Can I have access to `sudo`?

No, we do not allow users to use `sudo` to run commands as root. This is important to maintain the security and integrity of our systems and user data.

Application installers can sometimes default to installing in directories which require privileged access. These should be changed to somewhere more appropriate within `$HOME` or `$PROJECTDIR`.

If an installer needs `sudo` to install operating system packages (e.g. with `dnf` or `apt`), you can instead install it in a container as root by using `--fakeroot` with Apptainer or `--user=root` with Podman. See the containers guide for more information.

### How can I use Large Language Models (LLMs) to help me with my work?

You are free to use LLMs to help you with your work, but as ever YOU (the human) are responsible for what is run. We have encountered cases where popular LLMs have given advice that conflicts with the Acceptable Use Policy - it is up to you to prevent this.

The primary way to get accurate, up-to-date help from an AI coding agent, such as Claude, is to install the official [Isambard skills][using-ai-agents]. These extend the agent with knowledge of the Isambard HPC environment - job scheduling, modules, and resource limits - so it can give better answers without needing to be told about the documentation each time. See our [guide to using AI agents with Isambard][using-ai-agents] for installation instructions and recommended workflows.

As a secondary approach, if you're chatting with an LLM directly rather than using an agent with the Isambard skills installed, you can tell it about the BriCS documentation by pasting the URL `https://docs.isambard.ac.uk` into your prompt. If it is capable of browsing the web, this will allow the LLM to use the documentation as a reference when generating output. If using an LLM without this capability, you can achieve a similar result by copying and pasting relevant sections of the documentation into your prompt.

### Why am I getting rate limited by HuggingFace?

HuggingFace rate limits unauthenticated API traffic per IP address. To use your personal account-level limit instead of the shared IP-level limit, authenticate with HuggingFace. This can be done using `uv`:

```
$ uvx hf auth login

```

### Why am I seeing low inter-node bandwidth?

If `nccl-tests` shows bandwidth well below ~23 GB/s, NCCL is not using the Slingshot network. Look for a line in the output like:

```
NCCL WARN No transport found ... falling back to net

```

This usually means `aws-ofi-nccl` is not loaded, or was built against a different CUDA or NCCL version than the one in use. Check that the OFI plugin library path appears in `LD_LIBRARY_PATH` and that it was built against matching CUDA, NCCL, and libfabric versions. See the NCCL guide for the environment variables needed to configure the plugin correctly.

### Can I change my login shell to be something other than bash (zsh, csh, fish, etc.)?

No, we do not offer support for alternative shells such as `zsh`, `fish`, or `tcsh`, and we have no plans to introduce this in future. If you do attempt to invoke another shell manually within your session, or to change the login shell you are running, you do so at your own risk. Be aware that your environment may not behave as expected and we are unable to provide assistance if this is the case.

### My application is showing "Resource temporarily unavailable" errors on login nodes

This error usually indicates that one of the login node resource limits has been reached. Linux uses cgroups to enforce resource limits on processes, and each user session on the login nodes runs inside a cgroup. On Isambard-AI, each session is limited to 100% CPU (equivalent to one full CPU core), 4 GiB of memory, and 500 tasks. These limits are in place to keep the login nodes responsive for interactive work. Login nodes do not have GPUs, so GPU workloads should be run on compute nodes.

When a limit is hit, the symptoms depend on which resource was exhausted.

- CPU: your commands may become noticeably slower because the session's CPU usage is throttled to the limit.
- Memory: processes may be killed, or you may see errors such as `Killed`, `Cannot allocate memory`, or out of memory messages.
- Tasks: the kernel may refuse new `fork()` or `clone()` calls, which often appears as:

- Shell: `-bash: fork: retry: Resource temporarily unavailable` or `-bash: fork: Resource temporarily unavailable`.
- Python: `BlockingIOError: [Errno 11] Resource temporarily unavailable`, `OSError: [Errno 11] Resource temporarily unavailable`, or `RuntimeError: can't start new thread`.
- Node.js (used by VS Code, Claude Code, and other developer tools): `Error: spawn EAGAIN` or `Error: spawnSync EAGAIN`.
- VS Code / IDE terminals and extensions: may show `Unable to start process` or `Terminal process failed to launch`, or surface the underlying Python or Node.js errors above, depending on which component hit the limit.

Watch out for misleading secondary errors

The root cause is often not obvious from the error message the application reports. A language server, debugger, or extension process may fail to spawn, causing the IDE to report an apparently unrelated error such as a lost connection or an unresponsive environment — even though the underlying cause is a resource limit.

The login nodes are shared interactive resources and these limits exist to ensure fair use and preserve interactive performance for all users. If your workload needs more CPU time or memory, use the `interactive` reservation or run it as a batch job on the compute nodes rather than directly on the login node. Tasks that spawn large numbers of processes or threads — such as parallel builds, data preprocessing pipelines, or applications with large thread pools — should be run on the compute nodes.

## Project accounting

### What is a NHR?

NHR stands for 'node hour' and is the unit of measurement for using Isambard supercomputer compute nodes.

Each project is allocated a total limit of node hours (NHRs). Jobs will only run if there are enough node hours remaining in your project account.

Projects are responsible for managing node hour consumption. Further information can be found on the accounting guide.

### How do I estimate my node hour (NHR) requirements for my project?

It is very difficult to accurately estimate the run time of an application on a new system. The observed performance depends on factors that vary from platform to platform including compute performance, total memory, memory latency/bandwidth, interconnect performance and storage performance. Generally, estimates are made on the basis of comparison to measured performance on other systems.

In general we recommend making a higher estimate for the required node hours because allocations cannot be extended once exhausted, as described in the project management guide.

### What happens when my project runs out of node hours?

Users will only be able to run jobs that are within the remaining budget of node hours. Any jobs submitted that go over this limit will be queued but not run. At this stage, Slurm will raise an error when you try to submit jobs.

Note that users can still access the login nodes, for example to allow data transfer, once node hour credits are exhausted.

### Why does my awarded node hour balance look wrong?

BriCS performs accounting for compute on our services in units of node hours (NHR), and the project balance is displayed in these units in the portal. However, allocating organisations such as UKRI/DBIST may use different units in their application processes.

For Isambard-AI projects, a common point of confusion for new users is that a quarter of the expected value is displayed in the portal at the start of the project. This is because each Isambard-AI node consists of 4 GH200 superchips, such that 1 NHR = 4 GPU hours. For example, an award of 10,000 GPU hours will be displayed in the portal as 2,500 NHR. Jobs can be run on a single GPU, i.e. consuming 0.25 NHR per wall clock hour.

For further information, please see the accounting guide — what is a node hour?.

### Can I get more node hours or extend my project?

You will need to ask the allocating organisation. BriCS does not have the authority to add more NHR or extend projects. Please see the relevant section of the access page for further information.

## Working with Slurm

### Why isn't my job running?

There are several reasons why your job may not be running. These include:

- The system is busy. See the below FAQs for further information.
- There is a reservation for planned maintenance or other purposes. See the status page for information on planned and unplanned outages.
- Your project may have run out of node hours (NHR).
- The job has a dependency on another job or specific node.
- A mistake in your request that you need to debug.

See the Slurm guide for further information.

### Why do I see `AssocGrp*Limit` or accounting/QOS policy errors?

These errors usually mean your project has reached, or temporarily exceeded, an allocation accounting limit. Common examples include `AssocGrpCPUMinutesLimit`, `AssocGrpGRESMinutes` or `AssocGrpGRESMinutesLimit`, and `AssocGrpMemMinutes` or `AssocGrpMemMinutesLimit`.

This can happen even when your overall usage appears to be within allocation, because Slurm reserves credits using requested resources and requested wall time. Large job arrays with high `--time` values can temporarily reserve enough credits to block new submissions until some jobs complete.

For practical steps and examples, see the Slurm allocation limit guidance.

### How long will my job queue?

This will depend on how busy the system is overall. At the strategic level, node hours (NHR) are allocated to projects with consideration of the total resource available. Projects and users are encouraged to run their work early in the project. Applied across many projects this helps flatten demand, improving queueing time for all.

### Why is my job queueing for so long? How can I make my job run sooner?

Resources on the Isambard supercomputers are finite, and on a well-utilised system it is normal and expected to queue and all users are treated equally. There are, however, some practical steps you can take to improve your queueing time:

- Use the `interactive` reservation (Isambard-AI Phase 2 only).
- Request the minimum number of nodes/GPUs needed.
- Request the minimum amount of time needed.
- Don't cancel and resubmit - you will go to the back of the queue.
- Be a good citizen.

See the Slurm guide for further information on the queueing system.

### How do I run interactively on a compute node?

On Isambard-AI Phase 2, the `interactive` reservation provides a dedicated pool of nodes suitable for short-lived work such as debugging, development, and exploratory analysis. Use `srun` with `--reservation=interactive` to start an `interactive` shell:

```
user.project@login40:~> srun --gpus=1 --reservation=interactive --pty bash -i

```

Do not add a `--partition` flag to this command — Slurm selects the correct partition and applies the reservation's limits automatically. Overriding this is not an acceptable way to use the reservation: such jobs may be cancelled without warning, and repeated or deliberate use in this way is subject to the Penalties for Misuse section of the Acceptable Use Policy.

Jobs running in this reservation are limited in the number of nodes and hours they use and usage is charged at a premium — see the `interactive` reservation reference for full details.

The `interactive` partition is hidden, so these jobs do not appear in the output of `squeue --me` on its own. Use `squeue --me --partition=interactive` to list them, or `squeue --me --all` to list your jobs across every partition.

### Why can't I see other people's jobs?

This is deliberate to support confidentiality and prevent unacceptable behaviour towards other users.

Within the portal, all members of a project can view the node hours used by each team member on that project for the current or previous months. First select your project to reach the 'Project Dashboard' screen. Then select the 'Resources' tab and choose the resource of interest, eg Isambard-AI Phase 2. Then click on the 'Usage' tab where you will be able to explore and download the data.

### How long is the maximum job run time?

The maximum runtime of a job submitted to Slurm is 24 hours. This has been chosen to balance the needs of users and requirements for system maintenance and patching. More details about how Slurm works on BriCS systems and how to use job dependencies can be found in the Slurm guide.

### Can you relax the maximum job run time so my team can run longer jobs?

No. The maximum job run time was decided in partnership with the allocating organisations and is a compromise between the needs of users and requirements for system maintenance and patching. It is not possible to relax this limit. Please contact your allocator if you have a strong use case for longer jobs.

### Can you grant my project a larger storage quota?

No. The storage quotas have been agreed in partnership with our allocating organisations, with the aim of ensuring projects have a fair share of this limited resource. Please contact your allocator if you have a strong use case for larger storage.

### Can you relax resource limits so my team can run more and/or larger jobs?

The queue limits have been set to provide a good experience for all users and in general will not be altered. If your project has a strong use case, please raise a helpdesk ticket.

### Can I receive job status notifications via e-mail?

We do not currently support job status notification e-mails. Job status can only be checked via Slurm commands from the command line. Please avoid frequent polling, as excessive queries can affect system performance.

Also, please see the Slurm guide.

## Data and Storage

### How do I copy files to and from the Isambard supercomputers?

The easiest way to copy files to Isambard-AI or Isambard 3 is to use scp or rsync. Full instructions can be found in the file transfer guide.

### How can I share or transfer data between projects?

There are various circumstances when a user may wish to share or transfer data between projects on the same machine. However, this must be done with care not to breach privacy or licencing, noting that the PI is legally responsible for any breach.

There are a few options:

=== "Via public directories"

Every project has such a directory located in `/projects/public/[PROJECT]`. This can be very quick and convenient, but any data stored there even for a moment is visible to ALL users of the platform.

To allow members of other projects to read files in your project's public shared storage area, you may need to run `chmod` to change the permissions of the files and directories you wish to share. To change the permissions of files and/or directories:

| Object | Command Example | Purpose |
| File | `chmod o+r <file>` | Allow other users to read the file |
| Directory | `chmod o+rx <directory>` | Allow other users to search |
| Multiple | `chmod --recursive o+rX <directory>` | Recursively update files & folders |

Notes on placeholders: - `<file>` / `<directory>` = specific files or folders inside `/projects/public/`

=== "Inter-project copy"

It is possible to use `scp` or `rsync` to copy from one project to another on the same machine. To do this, the user will first need to install and run `clifton` in their source project account.

The copy can be run in either direction: push from the source project, or pull from the destination project.

For large transfers, submit the copy as a Slurm job rather than running it on a login node. See How do I transfer a large amount of data between projects?.

=== "Via an external location"

Upload to an external location and download. This option may be excessively time consuming and disruptive to others using the finite network bandwidth.

Note that Isambard-AI Phase 1 and Phase 2 are physically separate machines with distinct storage, so you cannot see files on one platform from another. Use `scp`/`rsync` and `clifton` to transfer files between them.

See the file transfer guide for more information.

### How do I transfer a large amount of data between projects?

Submit the copy as a Slurm job rather than running it on a login node. The login nodes are shared and resource-limited, so a large copy started on one is likely to be killed for exceeding the memory limit before it finishes. Request a single task on a single node, and on Isambard-AI a single GPU. The transfer is limited by storage and network throughput, so a larger allocation will not make it faster.

The copy can be run as a pull as well as a push: run the job in the source project to push the data to the destination, or in the destination project to pull it from the source. The direction matters if one of the projects has expired, as only a project that is still active can submit jobs.

A transfer run as a job consumes node hours in the same way as any other job, and this is expected. The login nodes are not a free transfer resource, so plan data movement into your allocation rather than trying to avoid the cost.

See transferring large amounts of data as a job in the file transfer guide for an example job script.

### How can I access data in my project for which I do not have permissions?

If a user has created data with file permissions that are too restrictive, contact the data owner and request that the permissions be adjusted to allow access (e.g. using `chmod`).

It is recommended to use the project shared storage location `/projects/[PROJECT]` for sharing data between members of a project.

If the data owner is unable to adjust the permissions (e.g. has left the project), then the project PI should raise a request with BriCS support to have the permissions and/or ownership on the data adjusted to restore access.

### Can you move my files for me?

No. We do not move or copy data for users, as that violates our privacy policy, and bespoke transfers cannot be arranged by exception. Please consult the existing advice for copying between projects, and submit large transfers as a Slurm job.

### Is my data on Isambard backed up?

No. PIs are responsible for ensuring adequate backups are arranged for your project data. See the storage information page for details.

### How long do I have to retrieve my data after a project expires?

Users have a 30-day grace period following project expiration to copy or back up their data. Please be sure to download it before the end of this period. After this period, data may be permanently deleted and will no longer be recoverable. Users are advised to ensure all important data is secured within this timeframe.

Do not leave copying back your data until the grace period. Jobs cannot be submitted for a project once it has expired, so the Slurm job method is not available during the grace period. Copying from a login node is then the only option left, and for a large volume of data that is slow and difficult. Manage your data as part of your project and copy it out before the project end date.

The exception is a copy into another project that is still active, as that project can still submit jobs. In that case, run the transfer as a job from the active project and pull the data from the expired project.
