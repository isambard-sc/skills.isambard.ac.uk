<!-- Snapshot of https://docs.isambard.ac.uk/user-documentation/tutorials/data-mover/ made by snapshot_docs.py. Do not edit. -->

- ✓ AIP1 Isambard-AI Phase 1 supported
- ✓ AIP2 Isambard-AI Phase 2 supported
- ✓ I3 Isambard 3 supported
- ✗ BC5 BlueCrystal 5 unsupported

# Moving data with the early access data mover service

Abstract

This tutorial introduces the data mover service for the transfer of data to and from BriCS services. Please note that this service is early access and is under active development.

Prerequisites

Users will need to have been granted access to the early access data mover service. Familiarity with the Linux command line assumed.

Only Mac and Linux systems are supported at this time.

Windows users are recommended to use Windows Subsystem for Linux (WSL).

Learning Objectives

By the end of this tutorial, users will have an understanding of:

- The purpose of the data mover service.
- The basic usage of rclone and AWS CLI for data transfer.
- How to setup a data transfer pipeline with data mover.

## Table of Contents

- Table of Contents
- Introduction

- Data transfer flow

- Transfers between a BriCS cluster and an external endpoint
- Transfers between two BriCS clusters

- Buckets, quotas and lifecycles

- Setup

- Install and configure an S3 client
- Install and configure the Netham client

- Using your S3 bucket

- Uploading data
- Downloading data
- Performance tuning
- Deleting data

- What's next

## Introduction

The data mover service can be used to easily transfer data to and from BriCS services. Data mover provides token-authenticated access to on-premise S3 object storage, which is accessible over the internet and internally across BriCS clusters. The storage is short-lived and intended to facilitate ingress/egress of data to cluster-attached storage, or lateral movement of data between projects and clusters (e.g. Isambard-AI Phase 2 and Isambard 3). Data stored in the on-premise S3 storage is independent to the data stored in home and projects directories on our clusters.

Previously, we have recommended the use of `scp` and `rsync` to copy data to and from BriCS systems over SSH; see the guide here. The data mover provides a significant improvement upon this by facilitating highly parallel, large scale data transfers over a direct network path that is separate to SSH traffic.

### Data transfer flow

To transfer data to a BriCS cluster using the data mover, the data must be first transferred from the origin location to the S3 staging area. From there, data can then be copied to cluster-attached storage, such as your `$PROJECTDIR` and `$HOME` directories. Similarly, to egress data from a BriCS cluster the data must first be transferred from cluster-attached storage to the S3 staging area and then onward to your destination.

#### Transfers between a BriCS cluster and an external endpoint

#### Transfers between two BriCS clusters

### Buckets, quotas and lifecycles

- Each project is assigned one S3 bucket with a capacity of 20TiB, and with the number of files capped at 5,000,000.
- All users within a project are able to read/write/delete/update all files within the project bucket.
- Data stored in the per-project staging bucket is ephemeral and will be deleted 30 days after last modification.

## Setup

### Install and configure an S3 client

To manage transfer of data you will need to install an S3 client such as rclone and AWS CLI.

For installation instructions, please see the documented installation instructions for rclone and AWS CLI. To simplify installation of these tools, we also provide example scripts for installing `rclone` and AWS CLI on BriCS clusters or your local Linux/Mac machine.

Compatibility with `rclone`

Please ensure that you are using `rclone` >= v1.61.0. Older versions are incompatible with the data mover service.

=== "rclone"

Click here to download the file: install-rclone.sh.

Alternatively, you can use `curl` to directly download the script:

```
$ curl -fsSLO https://docs.isambard.ac.uk/user-documentation/tutorials/data-mover/install-rclone.sh

```

Install `rclone` by running:

```
$ bash install-rclone.sh

```

Once `rclone` is installed, run the following command to configure the data mover service S3 storage as a remote:

```
$ rclone config create datamover-s3 s3 provider=Other env_auth=true endpoint=https://lb.staging.datamover.isambard.ac.uk no_check_bucket=true acl=""

```

=== "AWS CLI"

Click here to download the file: install-awscli.sh

Alternatively, you can use `curl` to directly download the script:

```
$ curl -fsSLO https://docs.isambard.ac.uk/user-documentation/tutorials/data-mover/install-awscli.sh

```

Install AWS CLI by running:

```
$ bash install-awscli.sh

```

Once AWS CLI is installed, no further configuration is required.

### Install and configure the Netham client

Next we need to install Netham on the computers that will be running the transfer. This is a command line tool that enables you to authenticate using the single federated identity you use across BriCS services and acquire temporary S3 credentials to access your per-project staging bucket for data movement. Netham is designed to be similar to Clifton, as used to acquire temporary SSH certificates for SSH login to BriCS facilities.

You can follow the instructions for installing Netham within a Python virtual environment or, alternatively, as a `uv` tool.

Where should Netham be installed?

Netham needs to be installed on any machine that is attempting to access the data mover S3 staging area.

For example, if you wish to egress data from Isambard-AI Phase 2 to an external hard drive attached to your local machine, you will need to install and setup Netham on an Isambard-AI Phase 2 login node as well as on your local machine. This allows you to upload data from your user or project spaces on Isambard-AI Phase 2 to the S3 staging area, then download this data from the staging area to your local machine.

=== "python"

```
$ python3.11 -m venv --upgrade-deps netham-venv
$ source netham-venv/bin/activate
(netham-venv) $ python -m pip install git+https://github.com/bristol-supercomputing/[email protected]

```

Netham supports Python versions >= 3.11. Isambard-AI Phase 2 has `python3.11` pre-installed.

You must run `source netham-venv/bin/activate` to be able to use the `netham` tool.

=== "uv"

Follow the `uv` installation instructions.

```
$ uv tool install git+https://github.com/bristol-supercomputing/[email protected]

```

To validate that the installation was successful, run:

```
$ netham --help
usage: netham [-h] [--version] [--config FILE] {auth} ...

Acquire temporary AWS credentials via OpenID Connect.

options:
  -h, --help     show this help message and exit
  --version      show program's version number and exit
  --config FILE  Path to the local config file (default: ./netham.toml).

subcommands:
  {auth}
    auth         Authenticate and write temporary AWS credentials to a file.

```

Then, we will create our `netham` configuration file. In this example we create a dedicated folder in our home directory to hold this file:

```
$ mkdir -v -p $HOME/netham
$ cat > $HOME/netham/netham.toml <<EOF
$ issuer_url = "https://keycloak.isambard.ac.uk/realms/isambard"
$ client_id = "netham"
$ role_arn = "arn:vast::default:role/PROJECTID.datamover"
$ sts_endpoint_url = "https://lb.staging.datamover.isambard.ac.uk"
$ assumed_role_duration_minutes = 1440
$ EOF

```

For the `role_arn` parameter, `PROJECTID` should be set to the ID (or shortcode) of your project. All users within any given project will set the same `role_arn` in their `netham` configuration file.

Credentials are valid for 24 hours

The temporary S3 credentials produced by Netham have a max duration of 24 hours, or 1440 minutes. `netham` will emit an error if `assumed_role_duration_minutes` in the `netham.toml` configuration file is greater than the max duration. If you wish the credentials to have a shorter lifetime, reduce the value of `assumed_role_duration_minutes` in the configuration file or use the `netham auth --assumed-role-duration` CLI option to override the value in the configuration file. After the credentials have expired, you must re-run `netham` to produce new temporary credentials.

Next, run `netham auth` to obtain your temporary S3 credentials. This must point to the location of previously created the `netham` configuration file:

```
$ netham --config $HOME/netham/netham.toml auth
Open this URL in your browser:

https://keycloak.isambard.ac.uk/realms/isambard/device?user_code=CODE-EDOC

```

Open the URL in your browser. Then select your Identity Provider and authenticate as usual. Once you have authenticated, you need to grant access to Netham when the dialog box appears:

Once the authentication and authorisation flow has completed, your temporary credentials will be generated.

```
S3 temporary access credentials acquired for user $UNIX_SHORTNAME. Add these to your environment by running

source creds_env.sh

```

Use of `--config`

You can skip specifying `--config` if you place a configuration file `netham.toml` in the directory that you are running `netham` from.

Temporary S3 credentials are then acquired by Netham and stored as environment variables in `creds_env.sh`. These are well-known configuration environment variables that can be used by many S3-compatible tools, such as `rclone` and AWS CLI, to authenticate API calls to S3 endpoints.

```
$ cat creds_env.sh
#!/bin/bash
export AWS_ACCESS_KEY_ID=XXXX
export AWS_SECRET_ACCESS_KEY=XXXX
export AWS_SESSION_TOKEN=XXXX
export AWS_ENDPOINT_URL_S3=https://lb.staging.datamover.isambard.ac.uk

```

Finally, run the following command to add these S3 credentials to your environment:

```
$ source creds_env.sh

```

## Using your S3 bucket

After following the Setup section, you can now access your per-project S3 bucket. In the following examples, we will show how to transfer data between BriCS clusters and your data mover S3 bucket.

To list the data in your bucket:

=== "rclone"

```
$ rclone lsl datamover-s3:PROJECTID.datamover
   10 2026-06-18 12:29:15.994061000 my-test-file.txt

```

=== "AWS CLI"

```
$ aws s3 ls s3://PROJECTID.datamover
   10 2026-06-18 12:29:15.994061000 my-test-file.txt

```

### Uploading data

To test the data mover pipeline, we will create a test file within the `$SCRATCHDIR` directory on a BriCS cluster (e.g. Isambard 3 or Isambard-AI Phase 2). First, connect to the cluster via SSH as usual. You can then create a file containing 1 GiB of random binary data using `dd`:

```
$ dd if=/dev/urandom of=${SCRATCHDIR}/file_1g_test bs=1M count=1024

```

To upload the file to the S3 bucket:

=== "rclone"

```
$ rclone copy --progress ${SCRATCHDIR}/file_1g_test datamover-s3:PROJECTID.datamover
Transferred:            1 GiB / 1 GiB, 100%, 189.736 MiB/s, ETA 0s
Transferred:            1 / 1, 100%
Elapsed time:        5.9s

```

=== "AWS CLI"

```
$ aws s3 cp ${SCRATCHDIR}/file_1g_test s3://PROJECTID.datamover
upload: ${SCRATCHDIR}/file_1g_test to s3://PROJECTID.datamover/file_1g_test

```

### Downloading data

You can then download the previously uploaded file from the S3 bucket to local storage. This could be when logged into another project you are a member of on the same BriCS cluster that the file was uploaded from, a different BriCS cluster, or a computer outside of the BriCS network (e.g. a laptop, workstation, or a node in another compute facility).

You will need to ensure that you have run `netham` on the computer downloading the data and added the output credentials to the shell environment so that the transfer tool (`rclone`, AWS CLI) is able to access the bucket.

=== "rclone"

```
$ rclone copy --progress datamover-s3:PROJECTID.datamover/file_1g_test .
Transferred:            1 GiB / 1 GiB, 100%, 189.736 MiB/s, ETA 0s
Transferred:            1 / 1, 100%
Elapsed time:        5.9s

```

=== "AWS CLI"

```
$ aws s3 cp s3://PROJECTID.datamover/file_1g_test .
download: s3://PROJECTID.datamover/file_1g_test to file_1g_test

```

### Performance tuning

By default, both `rclone` and the AWS CLI use conservative concurrency settings that may limit throughput. The optimal settings depend on the number and size of files being transferred. The values shown in the following examples are illustrative only.

=== "rclone"

For a small number of large files, increase the per-file upload and download concurrency and chunk size:

```
$ rclone copy --progress \
    --transfers 4 \
    --s3-upload-concurrency 16 \
    --s3-chunk-size 128M \
    ${SCRATCHDIR}/file_1g_test datamover-s3:PROJECTID.datamover

```

For many small files, increase the number of parallel transfers and checkers instead:

```
$ rclone copy --progress \
    --transfers 32 \
    --checkers 16 \
    ${SCRATCHDIR}/ datamover-s3:PROJECTID.datamover

```

The values above are reasonable starting points, actual optimal values will vary depending on file sizes, network conditions, and available memory. Refer to the rclone documentation for a full list of performance-related flags.

=== "AWS CLI"

The performance of the AWS CLI is tuned via persistent configuration rather than per-command flags. The following settings are most relevant for large transfers:

```
$ aws configure set default.s3.max_concurrent_requests 20
$ aws configure set default.s3.multipart_chunksize 128MB
$ aws configure set default.s3.multipart_threshold 128MB

```

These are written to `~/.aws/config` and apply to all subsequent `aws` commands.

Refer to the AWS CLI S3 documentation for a full list of performance-related settings.

Performance optimisation on login nodes

Please be aware when performing transfers on BriCS cluster login nodes that these are shared resources and are subject to per-user-session limits, for example on the maximum number of tasks.

### Deleting data

To delete data from the S3 bucket:

Prevent accidental data deletion

We recommend using `rclone delete --dry-run` or `aws s3 rm --dryrun` flags to avoid accidental data deletion. This is particularly important as all users have the same access permissions within a project bucket.

=== "rclone"

```
$ rclone delete --progress datamover-s3:PROJECTID.datamover/file_1g_test
Transferred:              0 B / 0 B, -, 0 B/s, ETA -
Checks:                 1 / 1, 100%, Listed 54
Deleted:                1 (files), 0 (dirs), 1 GiB (freed)
Elapsed time:         0.0s

```

=== "AWS CLI"

```
$ aws s3 rm s3://PROJECTID.datamover/file_1g_test
delete: s3://PROJECTID.datamover/file_1g_test

```

Note that, as mentioned previously, data not modified for 30 days will be deleted anyway.

## What's next

Thank you for participating in the early access period for the data mover service.

We welcome feedback on the service and are ready to assist with any issues you may encounter. We will use your feedback to help shape the data mover as it progresses towards full production.

To report an issue or provide feedback, please open a ticket in our service desk. To help us track and assign these tickets, please also add the prefix `DATAMOVER` to the ticket title.
