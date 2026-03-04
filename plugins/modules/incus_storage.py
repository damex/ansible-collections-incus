#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: Roman Kuzmitskii <ansible@damex.org>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

"""Manage Incus storage pools."""

from __future__ import annotations

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.damex.incus.plugins.module_utils.incus import (
    INCUS_COMMON_ARGS,
    INCUS_COMMON_ARGUMENT_SPEC,
    IncusNotFoundException,
    build_desired,
    incus_client_from_module,
    run_write_module,
)

DOCUMENTATION = r"""
---
module: incus_storage
short_description: Manage Incus storage pools
description:
  - Create, update, and delete Incus storage pools via the Incus REST API.
  - Storage pools are global resources, not project-scoped.
  - The storage driver is set on creation and cannot be changed afterwards.
extends_documentation_fragment: [damex.incus.common]
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

__all__ = ['DOCUMENTATION', 'EXAMPLES', 'RETURN', 'main']


def _get_storage(client, name):
    """Return (metadata dict, exists bool) for the storage pool."""
    try:
        return client.get(f'/1.0/storage-pools/{name}').get('metadata') or {}, True
    except IncusNotFoundException:
        return {}, False


def _create_storage(module, client, name, driver, desired):
    """Create storage pool."""
    if not module.check_mode:
        client.post('/1.0/storage-pools', {'name': name, 'driver': driver, **desired})
    return True


def _update_storage(module, client, name, desired):
    """Update storage pool configuration."""
    if not module.check_mode:
        client.put(f'/1.0/storage-pools/{name}', desired)
    return True


def _delete_storage(module, client, name):
    """Delete storage pool."""
    if not module.check_mode:
        client.delete(f'/1.0/storage-pools/{name}')
    return True


def main():
    """Run module."""
    argument_spec = {
        **INCUS_COMMON_ARGUMENT_SPEC,
        'driver': {
            'type': 'str',
            'choices': [
                'dir', 'btrfs', 'lvm', 'zfs', 'ceph', 'cephfs', 'cephobject', 'linstor', 'truenas',
            ],
        },
        'config': {'type': 'dict', 'default': {}},
        'description': {'type': 'str', 'default': ''},
    }
    argument_spec.update(INCUS_COMMON_ARGS)
    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=True)
    driver = module.params['driver']
    name = module.params['name']
    desired = build_desired(module)

    def _ensure_storage():
        client = incus_client_from_module(module)
        current, exists = _get_storage(client, name)
        if module.params['state'] == 'present':
            if not exists:
                if not driver:
                    module.fail_json(msg="'driver' is required when creating a storage pool")
                return _create_storage(module, client, name, driver, desired)
            if (current.get('description', '') == desired['description']
                    and current.get('config', {}) == desired['config']):
                return False
            return _update_storage(module, client, name, desired)
        return _delete_storage(module, client, name) if exists else False

    run_write_module(module, _ensure_storage)


if __name__ == '__main__':
    main()
