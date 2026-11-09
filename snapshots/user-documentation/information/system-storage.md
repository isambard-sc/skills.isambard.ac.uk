<!-- Snapshot of https://docs.isambard.ac.uk/user-documentation/information/system-storage/ made by snapshot_docs.py. Do not edit. -->

# Storage spaces

## Overview

Each project and user has storage space allocated to them for the duration of the project. Each area is intended for specific data usage, and the performance characteristics and quota limitations of each area reflect that expected usage.

Various storage spaces are provided to projects and their members, and are allocated upon creation of a project in the BriCS portal or upon addition of a person to a project. The underlying physical storage and policies applied to them vary across the BriCS facilities with Lustre, VAST Data (NFS), and local EXT4 being used. The storage areas are organised into two types, Parallel Access Storage, which is share across all nodes within a cluster, and Local Access Storage, which is physically installed into a node, and thus unique to each node. Details of which mounts referenced by their environment variable (i.e. run 'echo $HOME' to see the path) are which are detailed below.

### Parallel Access Storage Areas

The storage areas listed below are presented to all compute and login nodes within a cluster. The files written on one node will be visible on all other nodes.

#### `$HOME`

User-specific storage area for user's data (e.g. configuration files, submission scripts, job output files). It is owned by the user and, by default, is accessible to the user and members of their project group according to the filesystem permissions, and is not intended for storage of large volumes of data.

#### `$SCRATCHDIR`

User-specific storage area for working data (e.g. job checkpoint data, input/output data for intermediate processing steps, container images). This is intended as a user's working space for short-lived data that supports running jobs.

Files on $SCRATCHDIR that have not been accessed for 60 days will be deleted.

Scratch storage uses high-performance storage designed for active job I/O. Data to be kept should be copied to `$PROJECTDIR` or to external storage as soon as practicable. Note that user storage is not backed up and cannot be recovered.

#### `$PROJECTDIR`

Project-specific storage area, for data sharing amongst project members (e.g. input datasets, shared Conda environments, shared container images). The storage is accessible only to members of the project.

#### `$PROJECTDIR_PUBLIC`

Project-specific storage area, for "public shared" data, for sharing files with other projects. The directory is readable by all users on the system, including members of other projects, but only users of the owning project have write permission.

### Local Access Storage Areas

The storage listed below is accessible only locally on the node that files are written on. Unlike the parallel access storage areas, the disks are physically located in the nodes, and thus each area on a node is separate from every other node's local access storage.

#### `$LOCALDIR`

Fast local scratch storage on nodes. On compute nodes, `$LOCALDIR` is typically implemented as a tmpfs RAM disk, so available capacity is limited by the node's memory but I/O is very fast; on login nodes, `$LOCALDIR` is backed by local solid-state disks, which offer different performance and capacity characteristics. Temporary storage space intended for use in situations where the shared filesystem is unsuitable (such as building rootless containers). This is ephemeral storage, which is wiped at the end of a job/session, and its size and implementation may differ between login and compute nodes.

## Paths and Permissions

Below is the path of each storage area, and its associated environment variable (env), default filesystem ownership details, and default file system permissions (expressed in octal notation).

| Path | Env | Default Ownership | Default File Perms |
| `/home/<PROJECT>/<USER>.<PROJECT>` | $HOME | Owner: User, Group: Project | Octal: 0750 |
| `/scratch/<PROJECT>/<USER>.<PROJECT>` | $SCRATCHDIR, $SCRATCH | Owner: User, Group: User | Octal: 0750 |
| `/projects/<PROJECT>` | $PROJECTDIR | Owner: Root, Group: Project | Octal: 2770 |
| `/projects/public/<PROJECT>` | $PROJECTDIR_PUBLIC | Owner: Root, Group: Project | Octal: 2775 |
| `/local/user/<UID>`1 | $LOCALDIR | Owner: User, Group: User | Octal: 0750 2 |

## Quotas

### Capacity Limits

Quotas are enforced across all file systems to ensure runaway usage does not impact other users.

| Storage Space | Isambard 3 | Isambard-AI Phase 1 | Isambard-AI Phase 2 | BlueCrystal 5 |
| $HOME | 100GiB | 100GiB | 100GiB (NFS)3 | 100GiB |
| $PROJECTDIR | 20TiB | 200TiB | 200TiB | 20TiB |
| $SCRATCHDIR | 5TiB | 5TiB | 5TiB | 5TiB |
| $LOCALDIR (compute node) | 512GiB | 48GiB | 48GiB | N/A |
| $LOCALDIR (login node) | 512GiB | 512GiB | 512GiB | N/A |

### File (inode) Limits

In addition to the space limits shown above, file systems also enforce limits on the number of files and directories (inode quotas). These inode (file-count) limits remain important for workloads that create very large numbers of small files, even when total space usage is well below the size quota. The values below are the maximum inode counts currently applied on each storage space.

| Storage Space | Isambard-AI Phase 1 | Isambard-AI Phase 2 |
| $SCRATCHDIR | 1,000,000 files | 1,000,000 files |
| $PROJECTDIR | 50,000,000 files | 50,000,000 files |

### Checking Quotas

Lustre quotas are based on Lustre Project Quotas. They can be checked by getting the Project ID of a directory, and then listing the quota information for that ID.

To check a quota you can run the following one line command: `lfs quota -hp $(lfs project -d <DIRECTORY> | awk '{print $1}') <DIRECTORY>`

As an example, to check scratch space: `lfs quota -hp $(lfs project -d $SCRATCHDIR | awk '{print $1}') $SCRATCHDIR`

## Data Retention Policies

All storage space is working storage, thus is not backed up, nor is intended for long-term archival of data.

The data written out to the various storage areas is generally retained until the end date of a project. There are a few notable exceptions to this, which can be viewed in the table hereunder:

| Storage Space | Isambard 3 | Isambard-AI Phase 1 | Isambard-AI Phase 2 |
| $HOME | Project End Date | Project End Date | Project End Date |
| $PROJECTDIR | Project End Date | Project End Date | Project End Date |
| $SCRATCHDIR | Last Access >60 days | Project End Date | Project End Date |
| $LOCALDIR (compute node) | End of Job | End of Job | End of Job |
| $LOCALDIR (login node) | End of Session | End of Session | End of Session |

Users have a 30-day grace period following project expiration to copy or back up their data. After this period, data may be permanently deleted and will no longer be recoverable. Users are advised to ensure all important data is secured within this timeframe

## Important Considerations

Storage expires at the project end date

The storage allocated to each user and project is only accessible for the duration of the project.

After a project's end date project members will no longer able to access or use any storage previously allocated to the project and any data remaining in the project storage area will be deleted. This applies to project-specific shared storage under `/projects` as well as user storage under `/home/<PROJECT>` and `/scratch/<PROJECT>`.

All storage is working storage

Storage on BriCS facilities is working storage. It is not backed up and is not intended for long-term or archival storage of data.

Please ensure that important data is regularly backed up in another location during the project and that any data that should remain accessible to project members after the end of the project is copied off the system before the project end date.

Isambard 3 Grace and MACS

The filesystem (Lustre) is shared between Isambard 3 Grace and Isambard 3 MACS. The architectures of the system are different (`aarch64` vs. `x86_64`). Any files that may be used on both, such as `.bashrc`, should have appropriate checks, e.g. inside `.bashrc` architecture specific commands, such as Conda initialisation, can be protected by:

```
if [ "$(arch)" == "x86_64" ]; then
...
elif [ "$(arch)" == "aarch64" ]; then
...
fi

```

This can also include Python `pip` environments installed by `--user` which are installed in `$HOME/.local`. Use of virtual environments should be used instead.

$HOME Storage and SSH

If your `$HOME` directory storage is full, or if you have exceeded your storage quota, you may not be able to access using SSH. To avoid this problem do not use your home directory to store large files and instead use one of the other storage areas provided.

If you are not able to access a system due to exceeding your quota you will need to contact the BriCS Helpdesk and ask them to delete or move files so that you are under the storage quota. When making this request, please have a list of files ready.

-
UID can be found by running 'echo $UID' ↩

-
LOCALDIR on compute on Isambard-AI has octal 0700. ↩

-
Isambard-AI Phase 2 has its home directories ($HOME) on NFS storage, which unfortunately does not provide a means to display the quota usage. The nearest equivalent is to check the usage against the figures in the Limits table, with the following command: `du -xsh $HOME`. ↩
