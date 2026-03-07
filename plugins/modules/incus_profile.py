#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: Roman Kuzmitskii <ansible@damex.org>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

"""Ensure Incus profiles."""

from __future__ import annotations

DOCUMENTATION = r"""
---
module: incus_profile
short_description: Ensure Incus profiles
author: Roman Kuzmitskii (@damex) <ansible@damex.org>
description:
  - Create, update, and delete Incus profiles via the Incus REST API.
  - Profiles are project-scoped resources.
extends_documentation_fragment:
  - damex.incus.common
  - damex.incus.common.write
  - damex.incus.common.project
  - damex.incus.common.devices
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

from typing import Any

from ansible_collections.damex.incus.plugins.module_utils.device import (
    INCUS_DEVICE_OPTIONS,
)

from ansible_collections.damex.incus.plugins.module_utils.incus import (
    INCUS_COMMON_ARGUMENT_SPEC,
    IncusClient,
    IncusNotFoundException,
    incus_build_desired,
    incus_create_client,
    incus_create_write_module,
    incus_wait,
    incus_run_write_module,
)

__all__ = ['DOCUMENTATION', 'EXAMPLES', 'RETURN', 'main']


def _get_profile(client: IncusClient, project: str, name: str) -> tuple[dict[str, Any], bool]:
    """Return (metadata dict, exists bool) for the profile."""
    try:
        return client.get(f'/1.0/profiles/{name}?project={project}').get('metadata') or {}, True
    except IncusNotFoundException:
        return {}, False


def _create_profile(module: Any, client: IncusClient, project: str, name: str, desired: dict[str, Any]) -> bool:
    """Create profile."""
    if not module.check_mode:
        incus_wait(module, client, client.post(f'/1.0/profiles?project={project}', {'name': name, **desired}))
    return True


def _update_profile(module: Any, client: IncusClient, project: str, name: str, desired: dict[str, Any]) -> bool:
    """Update profile configuration and devices."""
    if not module.check_mode:
        incus_wait(module, client, client.put(f'/1.0/profiles/{name}?project={project}', desired))
    return True


def _delete_profile(module: Any, client: IncusClient, project: str, name: str) -> bool:
    """Delete profile."""
    if not module.check_mode:
        incus_wait(module, client, client.delete(f'/1.0/profiles/{name}?project={project}'))
    return True


def main() -> None:
    """Run module."""
    module = incus_create_write_module({
        **INCUS_COMMON_ARGUMENT_SPEC,
        'project': {'type': 'str', 'default': 'default'},
        'description': {'type': 'str', 'default': ''},
        'devices': {'type': 'list', 'elements': 'dict', 'default': [], 'options': INCUS_DEVICE_OPTIONS},
        'config': {'type': 'dict', 'default': {}},
    }, require_yaml=True)
    project = module.params['project']
    name = module.params['name']
    desired = incus_build_desired(module)

    def _ensure_profile() -> bool:
        client = incus_create_client(module)
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

    incus_run_write_module(module, _ensure_profile)


if __name__ == '__main__':
    main()
