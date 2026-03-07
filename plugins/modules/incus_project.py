#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: Roman Kuzmitskii <ansible@damex.org>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

"""Ensure Incus project."""

from __future__ import annotations

DOCUMENTATION = r"""
---
module: incus_project
short_description: Ensure Incus project
author: Roman Kuzmitskii (@damex) <ansible@damex.org>
description:
  - Create, configure, and delete Incus projects via the Incus REST API.
  - Global resource — not scoped to a project.
extends_documentation_fragment: [damex.incus.common, damex.incus.common.write]
options:
  name:
    description:
      - Name of the project.
    type: str
    required: true
  state:
    description:
      - Desired state of the project.
    type: str
    choices: [present, absent]
    default: present
  description:
    description:
      - Description of the project.
    type: str
    default: ''
  config:
    description:
      - Project configuration.
      - All values are sent as strings to the Incus API.
    type: dict
    default: {}
    suboptions:
      features.images:
        description:
          - Enable separate image store for the project.
        type: bool
      features.networks:
        description:
          - Enable separate network management for the project.
        type: bool
      features.networks.zones:
        description:
          - Enable separate network zone management for the project.
        type: bool
      features.profiles:
        description:
          - Enable separate profile store for the project.
        type: bool
      features.storage.buckets:
        description:
          - Enable separate storage bucket management for the project.
        type: bool
      features.storage.volumes:
        description:
          - Enable separate storage volume management for the project.
        type: bool
      limits.containers:
        description:
          - Maximum number of containers in the project.
        type: int
      limits.cpu:
        description:
          - Maximum number of CPUs allocated to the project.
        type: int
      limits.disk:
        description:
          - Maximum disk space used by the project.
        type: str
      limits.instances:
        description:
          - Maximum number of instances in the project.
        type: int
      limits.memory:
        description:
          - Maximum memory used by the project.
        type: str
      limits.networks:
        description:
          - Maximum number of networks in the project.
        type: int
      limits.processes:
        description:
          - Maximum number of processes in the project.
        type: int
      limits.virtual-machines:
        description:
          - Maximum number of virtual machines in the project.
        type: int
      restricted:
        description:
          - Whether to block access to security-sensitive features.
        type: bool
      restricted.backups:
        description:
          - Prevent instance or volume backups.
        type: str
        choices: [allow, block]
      restricted.cluster.groups:
        description:
          - Comma-separated list of allowed cluster groups.
        type: str
      restricted.cluster.target:
        description:
          - Whether to allow targeting cluster members.
        type: str
        choices: [allow, block]
      restricted.containers.interception:
        description:
          - Whether to allow system call interception in containers.
        type: str
        choices: [allow, block, full]
      restricted.containers.lowlevel:
        description:
          - Whether to allow low-level container options.
        type: str
        choices: [allow, block]
      restricted.containers.nesting:
        description:
          - Whether to allow nesting in containers.
        type: str
        choices: [allow, block]
      restricted.containers.privilege:
        description:
          - Control privileged container settings.
        type: str
        choices: [unprivileged, isolated, allow]
      restricted.devices.disk:
        description:
          - Control which disk devices can be used.
        type: str
        choices: [allow, block, managed]
      restricted.devices.disk.paths:
        description:
          - Comma-separated list of allowed disk source paths.
        type: str
      restricted.devices.gpu:
        description:
          - Whether to allow GPU devices in the project.
        type: str
        choices: [allow, block]
      restricted.devices.infiniband:
        description:
          - Whether to allow InfiniBand devices in the project.
        type: str
        choices: [allow, block]
      restricted.devices.nic:
        description:
          - Control which network devices can be used.
        type: str
        choices: [allow, block, managed]
      restricted.devices.pci:
        description:
          - Whether to allow PCI devices in the project.
        type: str
        choices: [allow, block]
      restricted.devices.proxy:
        description:
          - Whether to allow proxy devices in the project.
        type: str
        choices: [allow, block]
      restricted.devices.unix-block:
        description:
          - Whether to allow Unix block devices in the project.
        type: str
        choices: [allow, block]
      restricted.devices.unix-char:
        description:
          - Whether to allow Unix character devices in the project.
        type: str
        choices: [allow, block]
      restricted.devices.unix-hotplug:
        description:
          - Whether to allow Unix hotplug devices in the project.
        type: str
        choices: [allow, block]
      restricted.devices.usb:
        description:
          - Whether to allow USB devices in the project.
        type: str
        choices: [allow, block]
      restricted.idmap.gid:
        description:
          - Allowed host GID ranges for raw.idmap.
        type: str
      restricted.idmap.uid:
        description:
          - Allowed host UID ranges for raw.idmap.
        type: str
      restricted.networks.access:
        description:
          - Comma-separated list of allowed networks for access.
        type: str
      restricted.networks.integrations:
        description:
          - Comma-separated list of allowed network integrations.
        type: str
      restricted.networks.subnets:
        description:
          - Comma-separated list of allowed network subnets.
        type: str
      restricted.networks.uplinks:
        description:
          - Comma-separated list of allowed network uplinks.
        type: str
      restricted.networks.zones:
        description:
          - Comma-separated list of allowed network zones.
        type: str
      restricted.snapshots:
        description:
          - Prevent instance or volume snapshots.
        type: str
        choices: [allow, block]
      restricted.virtual-machines.lowlevel:
        description:
          - Whether to allow low-level virtual machine options.
        type: str
        choices: [allow, block]
      backups.compression_algorithm:
        description:
          - Compression algorithm for backups.
        type: str
        choices: [bzip2, gzip, lz4, lzma, xz, zstd, none]
      images.auto_update_cached:
        description:
          - Whether to auto-update cached images.
        type: bool
      images.auto_update_interval:
        description:
          - Interval in hours between image auto-updates.
        type: int
      images.compression_algorithm:
        description:
          - Compression algorithm for images.
        type: str
        choices: [bzip2, gzip, lz4, lzma, xz, zstd, none]
      images.default_architecture:
        description:
          - Default architecture for images.
        type: str
      images.remote_cache_expiry:
        description:
          - Number of days before cached remote images expire.
        type: int
      network.hwaddr_pattern:
        description:
          - Pattern for automatically generated MAC addresses.
        type: str
"""

EXAMPLES = r"""
- name: Create project
  damex.incus.incus_project:
    name: myproject
    description: My project
    config:
      features.images: true
      features.networks: false

- name: Remove project
  damex.incus.incus_project:
    name: myproject
    state: absent
"""

RETURN = r"""
"""

from ansible_collections.damex.incus.plugins.module_utils.incus import (
    INCUS_COMMON_ARGUMENT_SPEC,
    incus_build_desired,
    incus_create_write_module,
    incus_ensure_resource,
    incus_run_write_module,
)

__all__ = ['DOCUMENTATION', 'EXAMPLES', 'RETURN', 'main']


def main() -> None:
    """Run module."""
    module = incus_create_write_module({
        **INCUS_COMMON_ARGUMENT_SPEC,
        'description': {'type': 'str', 'default': ''},
        'config': {'type': 'dict', 'default': {}, 'options': {
            'features.images': {'type': 'bool'},
            'features.networks': {'type': 'bool'},
            'features.networks.zones': {'type': 'bool'},
            'features.profiles': {'type': 'bool'},
            'features.storage.buckets': {'type': 'bool'},
            'features.storage.volumes': {'type': 'bool'},
            'limits.containers': {'type': 'int'},
            'limits.cpu': {'type': 'int'},
            'limits.disk': {'type': 'str'},
            'limits.instances': {'type': 'int'},
            'limits.memory': {'type': 'str'},
            'limits.networks': {'type': 'int'},
            'limits.processes': {'type': 'int'},
            'limits.virtual-machines': {'type': 'int'},
            'restricted': {'type': 'bool'},
            'restricted.backups': {'type': 'str', 'choices': ['allow', 'block']},
            'restricted.cluster.groups': {'type': 'str'},
            'restricted.cluster.target': {'type': 'str', 'choices': ['allow', 'block']},
            'restricted.containers.interception': {'type': 'str', 'choices': ['allow', 'block', 'full']},
            'restricted.containers.lowlevel': {'type': 'str', 'choices': ['allow', 'block']},
            'restricted.containers.nesting': {'type': 'str', 'choices': ['allow', 'block']},
            'restricted.containers.privilege': {'type': 'str', 'choices': ['unprivileged', 'isolated', 'allow']},
            'restricted.devices.disk': {'type': 'str', 'choices': ['allow', 'block', 'managed']},
            'restricted.devices.disk.paths': {'type': 'str'},
            'restricted.devices.gpu': {'type': 'str', 'choices': ['allow', 'block']},
            'restricted.devices.infiniband': {'type': 'str', 'choices': ['allow', 'block']},
            'restricted.devices.nic': {'type': 'str', 'choices': ['allow', 'block', 'managed']},
            'restricted.devices.pci': {'type': 'str', 'choices': ['allow', 'block']},
            'restricted.devices.proxy': {'type': 'str', 'choices': ['allow', 'block']},
            'restricted.devices.unix-block': {'type': 'str', 'choices': ['allow', 'block']},
            'restricted.devices.unix-char': {'type': 'str', 'choices': ['allow', 'block']},
            'restricted.devices.unix-hotplug': {'type': 'str', 'choices': ['allow', 'block']},
            'restricted.devices.usb': {'type': 'str', 'choices': ['allow', 'block']},
            'restricted.idmap.gid': {'type': 'str'},
            'restricted.idmap.uid': {'type': 'str'},
            'restricted.networks.access': {'type': 'str'},
            'restricted.networks.integrations': {'type': 'str'},
            'restricted.networks.subnets': {'type': 'str'},
            'restricted.networks.uplinks': {'type': 'str'},
            'restricted.networks.zones': {'type': 'str'},
            'restricted.snapshots': {'type': 'str', 'choices': ['allow', 'block']},
            'restricted.virtual-machines.lowlevel': {'type': 'str', 'choices': ['allow', 'block']},
            'backups.compression_algorithm': {'type': 'str', 'choices': [
                'bzip2', 'gzip', 'lz4', 'lzma', 'xz', 'zstd', 'none',
            ]},
            'images.auto_update_cached': {'type': 'bool'},
            'images.auto_update_interval': {'type': 'int'},
            'images.compression_algorithm': {'type': 'str', 'choices': [
                'bzip2', 'gzip', 'lz4', 'lzma', 'xz', 'zstd', 'none',
            ]},
            'images.default_architecture': {'type': 'str'},
            'images.remote_cache_expiry': {'type': 'int'},
            'network.hwaddr_pattern': {'type': 'str'},
        }},
    })
    desired = incus_build_desired(module)
    incus_run_write_module(module, lambda: incus_ensure_resource(module, 'projects', desired))


if __name__ == '__main__':
    main()
