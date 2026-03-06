#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: Roman Kuzmitskii <ansible@damex.org>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

"""Manage Incus networks."""

from __future__ import annotations

DOCUMENTATION = r"""
---
module: incus_network
short_description: Manage Incus networks
author: Roman Kuzmitskii (@damex) <ansible@damex.org>
description:
  - Create, update, and delete Incus networks via the Incus REST API.
  - Networks are project-scoped resources.
  - The network type is set on creation and cannot be changed afterwards.
extends_documentation_fragment: [damex.incus.common, damex.incus.common.project, damex.incus.common.write]
options:
  name:
    description:
      - Name of the network.
    type: str
    required: true
  state:
    description:
      - Desired state of the network.
    type: str
    choices: [present, absent]
    default: present
  type:
    description:
      - Network type.
      - Required when creating a new network.
      - Ignored on update — type cannot be changed after creation.
    type: str
    choices:
      - bridge
      - macvlan
      - sriov
      - physical
  description:
    description:
      - Network description.
    type: str
    default: ''
  config:
    description:
      - Network configuration key-value pairs.
      - Boolean values are converted to lowercase strings.
    type: dict
    default: {}
"""

EXAMPLES = r"""
- name: Create bridge network
  damex.incus.incus_network:
    name: incusbr0
    type: bridge
    config:
      ipv4.address: 10.0.0.1/24
      ipv4.nat: true

- name: Remove network
  damex.incus.incus_network:
    name: incusbr0
    state: absent
"""

RETURN = r"""
"""

from typing import Any

from ansible_collections.damex.incus.plugins.module_utils.incus import (
    INCUS_COMMON_ARGUMENT_SPEC,
    IncusClient,
    IncusNotFoundException,
    build_desired,
    incus_client_from_module,
    incus_create_write_module,
    maybe_wait,
    run_write_module,
)

__all__ = ['DOCUMENTATION', 'EXAMPLES', 'RETURN', 'main']


def _get_network(client: IncusClient, project: str, name: str) -> tuple[dict[str, Any], bool]:
    """Return (metadata dict, exists bool) for the network."""
    try:
        return client.get(f'/1.0/networks/{name}?project={project}').get('metadata') or {}, True
    except IncusNotFoundException:
        return {}, False


def _create_network(module: Any, client: IncusClient, project: str, name: str, desired: dict[str, Any]) -> bool:
    """Create network."""
    if not module.check_mode:
        maybe_wait(module, client, client.post(f'/1.0/networks?project={project}', {'name': name, **desired}))
    return True


def _update_network(module: Any, client: IncusClient, project: str, name: str, desired: dict[str, Any]) -> bool:
    """Update network configuration."""
    if not module.check_mode:
        maybe_wait(module, client, client.put(f'/1.0/networks/{name}?project={project}', desired))
    return True


def _delete_network(module: Any, client: IncusClient, project: str, name: str) -> bool:
    """Delete network."""
    if not module.check_mode:
        maybe_wait(module, client, client.delete(f'/1.0/networks/{name}?project={project}'))
    return True


def main() -> None:
    """Run module."""
    module = incus_create_write_module({
        **INCUS_COMMON_ARGUMENT_SPEC,
        'project': {'type': 'str', 'default': 'default'},
        'type': {'type': 'str', 'choices': ['bridge', 'macvlan', 'sriov', 'physical']},
        'config': {'type': 'dict', 'default': {}},
        'description': {'type': 'str', 'default': ''},
    })
    network_type = module.params['type']
    project = module.params['project']
    name = module.params['name']
    desired = build_desired(module)

    def _ensure_network() -> bool:
        client = incus_client_from_module(module)
        current, exists = _get_network(client, project, name)
        if module.params['state'] == 'present':
            if not exists:
                if not network_type:
                    module.fail_json(msg="'type' is required when creating a network")
                create_desired = {**desired, 'type': network_type}
                return _create_network(module, client, project, name, create_desired)
            if (current.get('description', '') == desired['description']
                    and current.get('config', {}) == desired['config']):
                return False
            return _update_network(module, client, project, name, desired)
        return _delete_network(module, client, project, name) if exists else False

    run_write_module(module, _ensure_network)


if __name__ == '__main__':
    main()
