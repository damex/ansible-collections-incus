#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: Roman Kuzmitskii <ansible@damex.org>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

"""Manage Incus profiles."""

from __future__ import annotations

DOCUMENTATION = r"""
---
module: incus_profile
short_description: Manage Incus profiles
author: Roman Kuzmitskii (@damex) <ansible@damex.org>
description:
  - Create, update, and delete Incus profiles via the Incus REST API.
  - Profiles are project-scoped resources.
extends_documentation_fragment: [damex.incus.common, damex.incus.common.project]
options:
  name:
    description:
      - Name of the profile.
    type: str
    required: true
  state:
    description:
      - Desired state of the profile.
    type: str
    choices:
      - present
      - absent
    default: present
  description:
    description:
      - Profile description.
    type: str
    default: ''
  config:
    description:
      - Profile configuration key-value pairs.
      - Boolean values are converted to lowercase strings.
      - Dict values for C(cloud-init.*) keys are serialized to YAML.
    type: dict
    default: {}
  devices:
    description:
      - Profile devices as a list.
      - Each item must include a C(name) field used as the device key in the API.
      - Boolean values are converted to lowercase strings.
    type: list
    elements: dict
    default: []
    suboptions:
      name:
        description: Device name used as the key in the Incus API.
        type: str
        required: true
      type:
        description: Device type.
        type: str
        choices: [disk, nic]
        required: true
      path:
        description: Mount path (disk).
        type: str
      pool:
        description: Storage pool name (disk).
        type: str
      source:
        description: Source path or device (disk).
        type: str
      size:
        description: Disk size limit (disk).
        type: str
      readonly:
        description: Whether the disk is read-only (disk).
        type: bool
      network:
        description: Managed network to attach to (nic).
        type: str
      nictype:
        description: NIC type (nic).
        type: str
      parent:
        description: Parent host interface (nic).
        type: str
      hwaddr:
        description: MAC address (nic).
        type: str
      mtu:
        description: MTU override (nic).
        type: str
      ipv4.address:
        description: Static IPv4 address (nic).
        type: str
      ipv4.routes:
        description: IPv4 routes to add on host (nic).
        type: str
      ipv6.address:
        description: Static IPv6 address (nic).
        type: str
      ipv6.routes:
        description: IPv6 routes to add on host (nic).
        type: str
"""

EXAMPLES = r"""
- name: Create profile
  damex.incus.incus_profile:
    name: base
    description: Base profile
    config:
      limits.cpu: "2"
      limits.memory: 2GiB
    devices:
      - name: root
        type: disk
        path: /
        pool: default
      - name: eth0
        type: nic
        network: incusbr0

- name: Remove profile
  damex.incus.incus_profile:
    name: base
    state: absent
"""

RETURN = r"""
"""

try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.damex.incus.plugins.module_utils.incus import (
    INCUS_COMMON_ARGS,
    INCUS_COMMON_ARGUMENT_SPEC,
    IncusNotFoundException,
    incus_client_from_module,
    run_write_module,
)

__all__ = ['DOCUMENTATION', 'EXAMPLES', 'RETURN', 'main']

_CLOUD_INIT_USER_KEYS = frozenset({'cloud-init.user-data', 'cloud-init.vendor-data'})

_DEVICE_OPTIONS = {
    'name': {'type': 'str', 'required': True},
    'type': {'type': 'str', 'required': True, 'choices': ['disk', 'nic']},
    # disk
    'path': {'type': 'str'},
    'pool': {'type': 'str'},
    'source': {'type': 'str'},
    'size': {'type': 'str'},
    'readonly': {'type': 'bool'},
    # nic
    'network': {'type': 'str'},
    'nictype': {'type': 'str'},
    'parent': {'type': 'str'},
    'hwaddr': {'type': 'str'},
    'mtu': {'type': 'str'},
    'ipv4.address': {'type': 'str'},
    'ipv4.routes': {'type': 'str'},
    'ipv6.address': {'type': 'str'},
    'ipv6.routes': {'type': 'str'},
}


def _stringify_config(config):
    """Convert config values to strings as Incus stores them."""
    result = {}
    for k, v in (config or {}).items():
        if isinstance(v, (dict, list)):
            prefix = '#cloud-config\n' if k in _CLOUD_INIT_USER_KEYS else ''
            result[k] = prefix + yaml.dump(v, default_flow_style=False)
        elif isinstance(v, bool):
            result[k] = str(v).lower()
        else:
            result[k] = str(v)
    return result


def _devices_to_api(devices):
    """Convert list of devices to Incus API dict format."""
    api_devices = {}
    for device in (devices or []):
        device_name = device['name']
        device_config = {}
        for k, v in device.items():
            if k == 'name' or v is None:
                continue
            if isinstance(v, bool):
                device_config[k] = str(v).lower()
            else:
                device_config[k] = str(v)
        api_devices[device_name] = device_config
    return api_devices


def _get_profile(client, project, name):
    """Return (metadata dict, exists bool) for the profile."""
    try:
        return client.get(f'/1.0/profiles/{name}?project={project}').get('metadata') or {}, True
    except IncusNotFoundException:
        return {}, False


def _create_profile(module, client, project, name, desired):
    """Create profile."""
    if not module.check_mode:
        client.post(f'/1.0/profiles?project={project}', {'name': name, **desired})
    return True


def _update_profile(module, client, project, name, desired):
    """Update profile configuration and devices."""
    if not module.check_mode:
        client.put(f'/1.0/profiles/{name}?project={project}', desired)
    return True


def _delete_profile(module, client, project, name):
    """Delete profile."""
    if not module.check_mode:
        client.delete(f'/1.0/profiles/{name}?project={project}')
    return True


def main():
    """Run module."""
    argument_spec = {
        **INCUS_COMMON_ARGUMENT_SPEC,
        'project': {'type': 'str', 'default': 'default'},
        'description': {'type': 'str', 'default': ''},
        'devices': {'type': 'list', 'elements': 'dict', 'default': [], 'options': _DEVICE_OPTIONS},
        'config': {'type': 'dict', 'default': {}},
    }
    argument_spec.update(INCUS_COMMON_ARGS)
    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=True)
    if not HAS_YAML:
        module.fail_json(msg='PyYAML is required for this module')
    project = module.params['project']
    name = module.params['name']
    desired = {
        'description': module.params['description'],
        'config': _stringify_config(module.params['config']),
        'devices': _devices_to_api(module.params['devices']),
    }

    def _ensure_profile():
        client = incus_client_from_module(module)
        current, exists = _get_profile(client, project, name)
        if module.params['state'] == 'present':
            if not exists:
                return _create_profile(module, client, project, name, desired)
            if (current.get('description', '') == desired['description']
                    and current.get('config', {}) == desired['config']
                    and current.get('devices', {}) == desired['devices']):
                return False
            return _update_profile(module, client, project, name, desired)
        return _delete_profile(module, client, project, name) if exists else False

    run_write_module(module, _ensure_profile)


if __name__ == '__main__':
    main()
