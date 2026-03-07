#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: Roman Kuzmitskii <ansible@damex.org>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

"""Ensure Incus storage pools."""

from __future__ import annotations

DOCUMENTATION = r"""
---
module: incus_storage
short_description: Ensure Incus storage pools
author: Roman Kuzmitskii (@damex) <ansible@damex.org>
description:
  - Create, update, and delete Incus storage pools via the Incus REST API.
  - Storage pools are global resources, not project-scoped.
  - The storage driver is set on creation and cannot be changed afterwards.
extends_documentation_fragment: [damex.incus.common, damex.incus.common.write]
options:
  name:
    description:
      - Name of the storage pool.
    type: str
    required: true
  state:
    description:
      - Desired state of the storage pool.
    type: str
    choices: [present, absent]
    default: present
  driver:
    description:
      - Storage driver.
      - Required when creating a new storage pool.
      - Ignored on update — driver cannot be changed after creation.
    type: str
    choices:
      - dir
      - btrfs
      - lvm
      - zfs
      - ceph
      - cephfs
      - cephobject
      - linstor
      - truenas
  description:
    description:
      - Storage pool description.
    type: str
    default: ''
  config:
    description:
      - Storage pool configuration key-value pairs.
      - Boolean values are converted to lowercase strings.
    type: dict
    default: {}
"""

EXAMPLES = r"""
- name: Create dir storage pool
  damex.incus.incus_storage:
    name: default
    driver: dir

- name: Create ZFS storage pool
  damex.incus.incus_storage:
    name: tank
    driver: zfs
    config:
      zfs.pool_name: tank

- name: Remove storage pool
  damex.incus.incus_storage:
    name: default
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
        'driver': {
            'type': 'str',
            'choices': [
                'dir', 'btrfs', 'lvm', 'zfs', 'ceph', 'cephfs', 'cephobject', 'linstor', 'truenas',
            ],
        },
        'config': {'type': 'dict', 'default': {}},
        'description': {'type': 'str', 'default': ''},
    })
    desired = incus_build_desired(module)
    incus_run_write_module(module, lambda: incus_ensure_resource(module, 'storage-pools', desired, ['driver']))


if __name__ == '__main__':
    main()
