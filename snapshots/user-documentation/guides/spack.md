<!-- Snapshot of https://docs.isambard.ac.uk/user-documentation/guides/spack/ made by snapshot_docs.py. Do not edit. -->

# Using Spack

Spack is a package management tool popular for building software and its dependencies in a consistent manner, taking into account the attributes of the machine it is being built on.

Availability of your software

Please be aware of the following points:

- We cannot guarantee every software package is supported.
- We have only tested the configurations outlined in this documentation.
- We will list common issues on this page as they are reported.

## Locations for support

There are many sources of help regarding the use of Spack. However, Spack's own documentation and tutorials are a good starting point:

- Spack documentation
- Spack tutorial
- Spack basics
- Spack environments
- Spack configuration

There is also the Spack Slack channel and Github pages:

- Spack FAQ

## Setting up Spack

Prerequisites

This guide assumes familiarity with modules, MPI and system specficiations:

- Modules.
- MPI documentation.
- System specifications, mainly the interconnect.

To help Spack, an initial configuration can be used to find already installed compilers and libraries. The available compilers and libraries can vary depending on requirements. For a guide to setup Spack see:

- Setting up Spack

Isambard-AI and Isambard 3 are HPE Cray systems based on the Slingshot 11 (SS11) interconnect between the nodes. To achieve optimal latency and bandwidth the relevant dependencies provided in the setting up of the environments need to be used when building software.

## Example applications

This section will provide instructions for common applications used on the systems.
