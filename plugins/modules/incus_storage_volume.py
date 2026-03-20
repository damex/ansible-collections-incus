#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: Roman Kuzmitskii <ansible@damex.org>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

"""
Ensure Incus storage volume.
"""

from __future__ import annotations

DOCUMENTATION = r"""
---
module: incus_storage_volume
short_description: Ensure Incus storage volume
author: Roman Kuzmitskii (@damex) <ansible@damex.org>
description:
  - Create, update, and delete Incus custom storage volumes via the Incus REST API.
  - Storage volumes are project-scoped resources within a storage pool.
  - The content type is set on creation and cannot be changed afterwards.
extends_documentation_fragment:
  - damex.incus.common
  - damex.incus.common.project
  - damex.incus.common.write
options:
  pool:
    description:
      - Name of the storage pool containing the volume.
    type: str
    required: true
  name:
    description:
      - Name of the storage volume.
    type: str
    required: true
  content_type:
    description:
      - Content type of the storage volume.
      - Only used when creating a new volume.
      - Ignored on update — content type cannot be changed after creation.
    type: str
    choices:
      - filesystem
      - block
    default: filesystem
  description:
    description:
      - Storage volume description.
    type: str
    default: ''
  target:
    description:
      - Cluster member to create the storage volume on.
    type: str
  state:
    description:
      - Desired state of the storage volume.
    type: str
    choices:
      - present
      - absent
    default: present
  config:
    description:
      - Storage volume configuration key-value pairs.
      - Boolean values are converted to lowercase strings.
    type: dict
    default: {}
    suboptions:
      size:
        description:
          - Size of the storage volume.
        type: str
      snapshots.expiry:
        description:
          - Automatic expiry time for snapshots.
        type: str
      snapshots.pattern:
        description:
          - Pongo2 template for snapshot names.
        type: str
      snapshots.schedule:
        description:
          - Cron expression for automatic snapshots.
        type: str
      block.filesystem:
        description:
          - Filesystem type for block volumes.
        type: str
      block.mount_options:
        description:
          - Mount options for block volumes.
        type: str
      zfs.blocksize:
        description:
          - Block size for the ZFS volume.
        type: str
      zfs.block_mode:
        description:
          - Whether to use a ZFS volume as a block device.
        type: bool
      zfs.delegate:
        description:
          - Whether to delegate ZFS dataset to the instance.
        type: bool
      zfs.remove_snapshots:
        description:
          - Whether to remove snapshots on volume removal.
        type: bool
"""

EXAMPLES = r"""
- name: Ensure filesystem storage volume
  damex.incus.incus_storage_volume:
    pool: default
    name: data

- name: Ensure block storage volume with size
  damex.incus.incus_storage_volume:
    pool: zfs
    name: disk1
    content_type: block
    config:
      size: 50GiB

- name: Ensure storage volume with snapshots
  damex.incus.incus_storage_volume:
    pool: default
    name: backups
    config:
      snapshots.schedule: "@daily"
      snapshots.expiry: 7d

- name: Ensure storage volume in project
  damex.incus.incus_storage_volume:
    pool: default
    name: data
    project: myproject

- name: Ensure storage volume on cluster member
  damex.incus.incus_storage_volume:
    pool: local
    name: data
    target: node1

- name: Ensure storage volume is absent
  damex.incus.incus_storage_volume:
    pool: default
    name: data
    state: absent
"""

RETURN = r"""
"""

from typing import Any
from urllib.parse import quote

from ansible_collections.damex.incus.plugins.module_utils.incus import (
    INCUS_COMMON_ARGUMENT_SPEC,
    IncusResourceOptions,
    incus_build_desired,
    incus_create_write_module,
    incus_ensure_resource,
    incus_run_write_module,
)

__all__ = ['DOCUMENTATION', 'EXAMPLES', 'RETURN', 'main']

INCUS_STORAGE_VOLUME_CONFIG_OPTIONS = {
    'size': {'type': 'str'},
    'snapshots.expiry': {'type': 'str'},
    'snapshots.pattern': {'type': 'str'},
    'snapshots.schedule': {'type': 'str'},
    'block.filesystem': {'type': 'str'},
    'block.mount_options': {'type': 'str'},
    'zfs.blocksize': {'type': 'str'},
    'zfs.block_mode': {'type': 'bool'},
    'zfs.delegate': {'type': 'bool'},
    'zfs.remove_snapshots': {'type': 'bool'},
}


def main() -> None:
    """
    Run module.

    >>> main()
    """
    argument_spec: dict[str, Any] = {
        'pool': {'type': 'str', 'required': True},
        'project': {'type': 'str', 'default': 'default'},
        'target': {'type': 'str'},
        'content_type': {
            'type': 'str',
            'default': 'filesystem',
            'choices': [
                'filesystem',
                'block',
            ],
        },
        'description': {'type': 'str', 'default': ''},
        'config': {'type': 'dict', 'default': {}, 'options': INCUS_STORAGE_VOLUME_CONFIG_OPTIONS},
    }
    for spec_key, spec_value in INCUS_COMMON_ARGUMENT_SPEC.items():
        argument_spec[spec_key] = spec_value
    module = incus_create_write_module(argument_spec)
    encoded_pool = quote(module.params['pool'], safe='')
    resource = f'storage-pools/{encoded_pool}/volumes/custom'
    desired = incus_build_desired(module)
    options = IncusResourceOptions(create_only_params=['content_type'])
    incus_run_write_module(
        module,
        lambda: incus_ensure_resource(module, resource, desired, options),
    )


if __name__ == '__main__':
    main()
