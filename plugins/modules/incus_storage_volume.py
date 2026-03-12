#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: Roman Kuzmitskii <ansible@damex.org>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

"""Ensure Incus storage volume."""

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
      - Required when creating a new volume.
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

from urllib.parse import quote

from ansible_collections.damex.incus.plugins.module_utils.incus import (
    IncusNotFoundException,
    incus_build_query,
    incus_create_client,
    incus_create_write_module,
    incus_run_write_module,
    incus_stringify_config,
    incus_wait,
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
    """Run module."""
    module = incus_create_write_module({
        'pool': {'type': 'str', 'required': True},
        'name': {'type': 'str', 'required': True},
        'state': {
            'type': 'str',
            'default': 'present',
            'choices': [
                'present',
                'absent',
            ],
        },
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
    })

    def _ensure_volume() -> bool:
        client = incus_create_client(module)
        pool = module.params['pool']
        name = module.params['name']
        project = module.params['project']
        target = module.params.get('target')
        encoded_pool = quote(pool, safe='')
        encoded_name = quote(name, safe='')
        base_query = incus_build_query(project=project)
        target_query = incus_build_query(project=project, target=target)
        base_path = f'/1.0/storage-pools/{encoded_pool}/volumes/custom'

        desired = {
            'description': module.params['description'],
            'config': incus_stringify_config(module.params['config']),
        }

        try:
            current = client.get(f'{base_path}/{encoded_name}{target_query}').get('metadata') or {}
            exists = True
        except IncusNotFoundException:
            current = {}
            exists = False

        if module.params['state'] == 'present':
            if not exists:
                data = {
                    'name': name,
                    'content_type': module.params['content_type'],
                    **desired,
                }
                if not module.check_mode:
                    incus_wait(module, client, client.post(f'{base_path}{target_query}', data))
                return True
            if target:
                return False
            if all(key in current and current[key] == value for key, value in desired.items()):
                return False
            if not module.check_mode:
                incus_wait(module, client, client.put(f'{base_path}/{encoded_name}{base_query}', desired))
            return True

        if exists:
            if not module.check_mode:
                incus_wait(module, client, client.delete(f'{base_path}/{encoded_name}{base_query}'))
            return True
        return False

    incus_run_write_module(module, _ensure_volume)


if __name__ == '__main__':
    main()
