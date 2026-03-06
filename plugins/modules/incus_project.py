#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: Roman Kuzmitskii <ansible@damex.org>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

"""Manage Incus projects."""

from __future__ import annotations

DOCUMENTATION = r"""
---
module: incus_project
short_description: Manage Incus projects
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


def _get_project(client: IncusClient, name: str) -> tuple[dict[str, Any], bool]:
    """Return (metadata dict, exists bool) for the project."""
    try:
        return client.get(f'/1.0/projects/{name}').get('metadata') or {}, True
    except IncusNotFoundException:
        return {}, False


def _create_project(module: Any, client: IncusClient, name: str, desired: dict[str, Any]) -> bool:
    """Create project."""
    if not module.check_mode:
        maybe_wait(module, client, client.post('/1.0/projects', {'name': name, **desired}))
    return True


def _update_project(module: Any, client: IncusClient, name: str, desired: dict[str, Any]) -> bool:
    """Update project configuration."""
    if not module.check_mode:
        maybe_wait(module, client, client.put(f'/1.0/projects/{name}', desired))
    return True


def _delete_project(module: Any, client: IncusClient, name: str) -> bool:
    """Delete project."""
    if not module.check_mode:
        maybe_wait(module, client, client.delete(f'/1.0/projects/{name}'))
    return True


def main() -> None:
    """Run module."""
    module = incus_create_write_module({
        **INCUS_COMMON_ARGUMENT_SPEC,
        'description': {'type': 'str', 'default': ''},
        'config': {'type': 'dict', 'default': {}},
    })
    name = module.params['name']
    desired = build_desired(module)

    def _ensure_project() -> bool:
        client = incus_client_from_module(module)
        current, exists = _get_project(client, name)
        if module.params['state'] == 'present':
            if not exists:
                return _create_project(module, client, name, desired)
            if (current.get('description', '') == desired['description']
                    and current.get('config', {}) == desired['config']):
                return False
            return _update_project(module, client, name, desired)
        return _delete_project(module, client, name) if exists else False

    run_write_module(module, _ensure_project)


if __name__ == '__main__':
    main()
