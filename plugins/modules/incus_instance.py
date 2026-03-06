#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: Roman Kuzmitskii <ansible@damex.org>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

"""Manage Incus instances."""

from __future__ import annotations

DOCUMENTATION = r"""
---
module: incus_instance
short_description: Manage Incus instances
author: Roman Kuzmitskii (@damex) <ansible@damex.org>
description:
  - Create, configure, and manage the lifecycle of Incus instances via the Incus REST API.
  - Instances are project-scoped resources.
  - The instance type and source are set on creation and cannot be changed afterwards.
extends_documentation_fragment:
  - damex.incus.common
  - damex.incus.common.project
  - damex.incus.common.write
  - damex.incus.common.devices
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
  source:
    description:
      - Image alias to use when creating the instance, e.g. C(debian/13) or C(images:debian/13).
      - The C(remote:alias) format auto-resolves well-known remotes (C(images), C(ubuntu), C(ubuntu-daily)).
      - Required when creating a new instance. Ignored on update.
    type: str
  source_server:
    description:
      - URL of the image server to pull from, e.g. C(https://images.linuxcontainers.org).
      - Takes precedence over auto-resolved remotes when C(source) uses the C(remote:alias) format.
      - Not required for local images or when using a well-known remote prefix.
    type: str
  source_protocol:
    description:
      - Protocol used to communicate with C(source_server).
      - Defaults to C(simplestreams) when C(source_server) is set.
    type: str
    choices: [simplestreams, lxd]
    default: simplestreams
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
  config:
    description:
      - Instance configuration key-value pairs.
      - Booleans are converted to lowercase strings; cloud-init dict values are serialized to YAML.
    type: dict
    default: {}
"""

EXAMPLES = r"""
- name: Create and start a container
  damex.incus.incus_instance:
    name: mycontainer
    source: ubuntu/22.04
    profiles:
      - default
    config:
      limits.cpu: "2"
      limits.memory: 2GiB

- name: Stop an instance
  damex.incus.incus_instance:
    name: mycontainer
    state: stopped

- name: Delete an instance
  damex.incus.incus_instance:
    name: mycontainer
    state: absent
"""

RETURN = r"""
"""

from typing import Any

from ansible_collections.damex.incus.plugins.module_utils.device import (
    INCUS_DEVICE_OPTIONS,
)

from ansible_collections.damex.incus.plugins.module_utils.incus import (
    IncusClient,
    IncusNotFoundException,
    incus_build_desired,
    incus_client_from_module,
    incus_create_write_module,
    incus_maybe_wait,
    incus_run_write_module,
)

__all__ = ['DOCUMENTATION', 'EXAMPLES', 'RETURN', 'main']

_KNOWN_REMOTES = {
    'images': ('https://images.linuxcontainers.org', 'simplestreams'),
    'ubuntu': ('https://cloud-images.ubuntu.com/releases', 'simplestreams'),
    'ubuntu-daily': ('https://cloud-images.ubuntu.com/daily', 'simplestreams'),
}


def _build_source(module: Any) -> dict[str, str]:
    """Build source dict for instance creation from source/source_server/source_protocol params."""
    raw = module.params['source']
    server = module.params.get('source_server')
    protocol = module.params.get('source_protocol') or 'simplestreams'

    alias = raw
    if ':' in raw:
        remote, alias = raw.split(':', 1)
        if not server:
            if remote not in _KNOWN_REMOTES:
                module.fail_json(msg=f"Unknown remote '{remote}'. Set source_server explicitly.")
            server, protocol = _KNOWN_REMOTES[remote]

    source = {'type': 'image', 'alias': alias}
    if server:
        source['server'] = server
        source['protocol'] = protocol
    return source


def _get_instance(client: IncusClient, project: str, name: str) -> tuple[dict[str, Any], bool]:
    """Return (metadata dict, exists bool) for the instance."""
    try:
        return client.get(f'/1.0/instances/{name}?project={project}').get('metadata') or {}, True
    except IncusNotFoundException:
        return {}, False


def _create_instance(module: Any, client: IncusClient, project: str, name: str, desired: dict[str, Any]) -> bool:
    """Create instance from image source (stopped state). desired must include source/type/ephemeral."""
    if not module.check_mode:
        response = client.post(f'/1.0/instances?project={project}', {'name': name, **desired})
        incus_maybe_wait(module, client, response)
    return True


def _update_instance(module: Any, client: IncusClient, project: str, name: str, desired: dict[str, Any]) -> bool:
    """Update instance config, devices, and profiles. desired must include architecture."""
    if not module.check_mode:
        incus_maybe_wait(module, client, client.put(f'/1.0/instances/{name}?project={project}', desired))
    return True


def _delete_instance(module: Any, client: IncusClient, project: str, name: str) -> bool:
    """Delete instance."""
    if not module.check_mode:
        incus_maybe_wait(module, client, client.delete(f'/1.0/instances/{name}?project={project}'))
    return True


def _manage_state(module: Any, client: IncusClient, state_path: str, state: str, status: str) -> bool:
    """Start, stop, or restart the instance based on desired state."""
    if state == 'started' and status != 'Running':
        if not module.check_mode:
            incus_maybe_wait(module, client, client.put(state_path, {'action': 'start'}))
        return True
    if state == 'stopped' and status != 'Stopped':
        if not module.check_mode:
            incus_maybe_wait(module, client, client.put(state_path, {'action': 'stop', 'force': True}))
        return True
    if state == 'restarted' and status == 'Running':
        if not module.check_mode:
            incus_maybe_wait(module, client, client.put(state_path, {'action': 'restart', 'force': True}))
        return True
    return False


def main() -> None:
    """Run module."""
    module = incus_create_write_module({
        'name': {'type': 'str', 'required': True},
        'state': {'type': 'str', 'default': 'started',
                  'choices': ['started', 'stopped', 'restarted', 'absent']},
        'project': {'type': 'str', 'default': 'default'},
        'source': {'type': 'str'},
        'source_server': {'type': 'str'},
        'source_protocol': {'type': 'str', 'default': 'simplestreams', 'choices': ['simplestreams', 'lxd']},
        'type': {'type': 'str', 'default': 'container', 'choices': ['container', 'virtual-machine']},
        'ephemeral': {'type': 'bool', 'default': False},
        'profiles': {'type': 'list', 'elements': 'str', 'default': ['default']},
        'description': {'type': 'str', 'default': ''},
        'config': {'type': 'dict', 'default': {}},
        'devices': {'type': 'list', 'elements': 'dict', 'default': [], 'options': INCUS_DEVICE_OPTIONS},
    }, require_yaml=True)
    state = module.params['state']
    project = module.params['project']
    name = module.params['name']
    desired = {**incus_build_desired(module), 'profiles': module.params['profiles']}

    def _ensure_instance() -> bool:
        client = incus_client_from_module(module)
        current, exists = _get_instance(client, project, name)

        if state == 'absent':
            return _delete_instance(module, client, project, name) if exists else False

        status = current.get('status', 'Stopped') if exists else 'Stopped'
        state_path = f'/1.0/instances/{name}/state?project={project}'
        changed = False

        if not exists:
            if not module.params['source']:
                module.fail_json(msg="'source' is required when creating an instance")
            create_desired = {
                **desired,
                'type': module.params['type'],
                'ephemeral': module.params['ephemeral'],
                'source': _build_source(module),
            }
            _create_instance(module, client, project, name, create_desired)
            changed = True
        else:
            current_config = {k: v for k, v in current.get('config', {}).items()
                              if not k.startswith(('volatile.', 'image.'))}
            if (current.get('description', '') != desired['description']
                    or current_config != desired['config']
                    or current.get('devices', {}) != desired['devices']
                    or current.get('profiles', []) != desired['profiles']):
                update_desired = {'architecture': current['architecture'], **desired}
                _update_instance(module, client, project, name, update_desired)
                changed = True

        return _manage_state(module, client, state_path, state, status) or changed

    incus_run_write_module(module, _ensure_instance)


if __name__ == '__main__':
    main()
