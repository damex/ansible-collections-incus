#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: Roman Kuzmitskii <ansible@damex.org>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

"""Ensure Incus instance."""

from __future__ import annotations

DOCUMENTATION = r"""
---
module: incus_instance
short_description: Ensure Incus instance
author: Roman Kuzmitskii (@damex) <ansible@damex.org>
description:
  - Create, configure, and manage the lifecycle of Incus instances via the Incus REST API.
  - Instances are project-scoped resources.
  - The instance type and source are set on creation and cannot be changed afterwards.
extends_documentation_fragment:
  - damex.incus.common
  - damex.incus.instance_config
  - damex.incus.common.project
  - damex.incus.common.write
  - damex.incus.common.source
  - damex.incus.devices
options:
  name:
    description:
      - Name of the instance.
    type: str
    required: true
  state:
    description:
      - Desired state of the instance.
      - C(started) ensures the instance exists and is running.
      - C(stopped) ensures the instance exists and is stopped.
      - C(restarted) restarts the instance if it is running.
      - C(absent) ensures the instance does not exist.
    type: str
    choices: [started, stopped, restarted, absent]
    default: started
  target:
    description:
      - Cluster member to place the instance on.
      - Only used during creation — ignored for existing instances.
    type: str
  type:
    description:
      - Instance type.
      - Set on creation only — cannot be changed afterwards.
    type: str
    choices: [container, virtual-machine]
    default: container
  ephemeral:
    description:
      - Whether the instance is ephemeral (deleted on stop).
      - Set on creation only — cannot be changed afterwards.
    type: bool
    default: false
  profiles:
    description:
      - List of profiles to apply to the instance.
    type: list
    elements: str
    default: [default]
  description:
    description:
      - Instance description.
    type: str
    default: ''
"""

EXAMPLES = r"""
- name: Ensure container is started
  damex.incus.incus_instance:
    name: mycontainer
    source: ubuntu/22.04
    profiles:
      - default
    config:
      limits.cpu: "2"
      limits.memory: 2GiB

- name: Ensure instance is stopped
  damex.incus.incus_instance:
    name: mycontainer
    state: stopped

- name: Ensure instance on specific cluster member
  damex.incus.incus_instance:
    name: mycontainer
    source: ubuntu/22.04
    target: node1
    profiles:
      - default

- name: Ensure instance is absent
  damex.incus.incus_instance:
    name: mycontainer
    state: absent
"""

RETURN = r"""
"""

from typing import Any, NamedTuple
from urllib.parse import quote

from ansible_collections.damex.incus.plugins.module_utils.device import (
    INCUS_DEVICE_OPTIONS,
)

from ansible_collections.damex.incus.plugins.module_utils.incus import (
    INCUS_INSTANCE_CONFIG_OPTIONS,
    INCUS_SOURCE_ARGS,
    IncusClient,
    IncusNotFoundException,
    incus_build_desired,
    incus_build_query,
    incus_build_source,
    incus_create_client,
    incus_create_write_module,
    incus_run_write_module,
    incus_wait,
)

__all__ = ['DOCUMENTATION', 'EXAMPLES', 'RETURN', 'main']


class IncusInstanceDesired(NamedTuple):
    """
    Desired state for an Incus instance.

    >>> desired = IncusInstanceDesired(
    ...     description='test',
    ...     config={'limits.cpu': '2'},
    ...     preserved_config={'volatile.x': '1'},
    ...     devices={},
    ...     profiles=['default'],
    ... )
    >>> desired.description
    'test'
    """

    description: str
    config: dict[str, Any]
    preserved_config: dict[str, Any]
    devices: dict[str, Any]
    profiles: list[str]


def _build_config(
    preserved: dict[str, Any],
    desired: dict[str, Any],
) -> dict[str, Any]:
    """
    Build full instance config from preserved and desired keys.

    >>> _build_config({'volatile.x': '1'}, {'limits.cpu': '2'})
    {'volatile.x': '1', 'limits.cpu': '2'}
    """
    result = {}
    for key, value in preserved.items():
        result[key] = value
    for key, value in desired.items():
        result[key] = value
    return result


def _get_instance(
    client: IncusClient,
    query: str,
    encoded_name: str,
) -> tuple[dict[str, Any], bool]:
    """Return (metadata dict, exists bool) for the instance."""
    try:
        return client.get(f'/1.0/instances/{encoded_name}{query}').get('metadata') or {}, True
    except IncusNotFoundException:
        return {}, False


def _create_instance(
    module: Any,
    client: IncusClient,
    create_query: str,
    payload: dict[str, Any],
) -> bool:
    """Create instance from image source (stopped state)."""
    if not module.check_mode:
        incus_wait(
            module,
            client,
            client.post(f'/1.0/instances{create_query}', payload),
        )
    return True


def _update_instance(
    module: Any,
    client: IncusClient,
    query: str,
    encoded_name: str,
    payload: dict[str, Any],
) -> bool:
    """Update instance config, devices, and profiles."""
    if not module.check_mode:
        incus_wait(
            module,
            client,
            client.put(f'/1.0/instances/{encoded_name}{query}', payload),
        )
    return True


def _delete_instance(
    module: Any,
    client: IncusClient,
    query: str,
    encoded_name: str,
) -> bool:
    """Delete instance."""
    if not module.check_mode:
        incus_wait(module, client, client.delete(f'/1.0/instances/{encoded_name}{query}'))
    return True


def _manage_state(
    module: Any,
    client: IncusClient,
    state_path: str,
    state: str,
    status: str,
) -> bool:
    """Start, stop, or restart the instance based on desired state."""
    if state == 'started' and status != 'Running':
        if not module.check_mode:
            incus_wait(module, client, client.put(state_path, {'action': 'start'}))
        return True
    if state == 'stopped' and status != 'Stopped':
        if not module.check_mode:
            incus_wait(module, client, client.put(state_path, {'action': 'stop', 'force': True}))
        return True
    if state == 'restarted' and status == 'Running':
        if not module.check_mode:
            incus_wait(module, client, client.put(state_path, {'action': 'restart', 'force': True}))
        return True
    return False


def main() -> None:
    """Run module."""
    module = incus_create_write_module(
        {
            'name': {'type': 'str', 'required': True},
            'state': {
                'type': 'str',
                'default': 'started',
                'choices': [
                    'started',
                    'stopped',
                    'restarted',
                    'absent',
                ],
            },
            'target': {'type': 'str'},
            'project': {'type': 'str', 'default': 'default'},
            'type': {
                'type': 'str',
                'default': 'container',
                'choices': [
                    'container',
                    'virtual-machine',
                ],
            },
            'ephemeral': {'type': 'bool', 'default': False},
            'profiles': {
                'type': 'list',
                'elements': 'str',
                'default': ['default'],
            },
            'description': {'type': 'str', 'default': ''},
            'config': {
                'type': 'dict',
                'default': {},
                'options': INCUS_INSTANCE_CONFIG_OPTIONS,
            },
            'devices': {
                'type': 'list',
                'elements': 'dict',
                'default': [],
                'options': INCUS_DEVICE_OPTIONS,
            },
        } | INCUS_SOURCE_ARGS,
        require_yaml=True,
    )
    state = module.params['state']
    project = module.params['project']
    target = module.params.get('target')
    name = module.params['name']
    query = incus_build_query(project, None)
    create_query = incus_build_query(project, target)

    def _ensure_instance() -> bool:
        client = incus_create_client(module)
        encoded_name = quote(name, safe='')
        current, exists = _get_instance(client, query, encoded_name)
        built = incus_build_desired(
            module,
            config_key_values={'environment_variables': 'environment'},
        )
        desired = IncusInstanceDesired(
            description=built['description'],
            config=built['config'],
            preserved_config={
                key: value for key, value in current.get('config', {}).items()
                if key.startswith(('volatile.', 'image.'))
            },
            devices=built['devices'],
            profiles=module.params['profiles'],
        )

        if state == 'absent':
            return _delete_instance(module, client, query, encoded_name) if exists else False

        status = current.get('status', 'Stopped') if exists else 'Stopped'
        state_path = f'/1.0/instances/{encoded_name}/state{query}'
        changed = False

        if not exists:
            if not module.params['source']:
                module.fail_json(msg="'source' is required when creating an instance")
            _create_instance(
                module,
                client,
                create_query,
                {
                    'name': name,
                    'description': desired.description,
                    'config': desired.config,
                    'devices': desired.devices,
                    'profiles': desired.profiles,
                    'type': module.params['type'],
                    'ephemeral': module.params['ephemeral'],
                    'source': incus_build_source(module),
                },
            )
            changed = True
        else:
            current_config = {
                key: value for key, value in current.get('config', {}).items()
                if not key.startswith(('volatile.', 'image.'))
            }
            if (current.get('description', '') != desired.description
                    or current_config != desired.config
                    or current.get('devices', {}) != desired.devices
                    or current.get('profiles', []) != desired.profiles):
                _update_instance(
                    module,
                    client,
                    query,
                    encoded_name,
                    {
                        'architecture': current['architecture'],
                        'description': desired.description,
                        'config': _build_config(desired.preserved_config, desired.config),
                        'devices': desired.devices,
                        'profiles': desired.profiles,
                    },
                )
                changed = True

        return _manage_state(module, client, state_path, state, status) or changed

    incus_run_write_module(module, _ensure_instance)


if __name__ == '__main__':
    main()
