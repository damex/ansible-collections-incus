#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: Roman Kuzmitskii <ansible@damex.org>
# SPDX-License-Identifier: GPL-3.0-or-later

"""Manage Incus projects."""

from __future__ import annotations

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.damex.incus.plugins.module_utils.incus import (
    INCUS_COMMON_ARGS,
    IncusClientException,
    IncusNotFoundException,
    incus_client_from_module,
)

DOCUMENTATION = r"""
---
module: incus_project
short_description: Manage Incus projects
description:
  - Create, configure, and delete Incus projects via the Incus REST API.
  - Global resource — not scoped to a project.
extends_documentation_fragment: [damex.incus.common]
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

__all__ = ['DOCUMENTATION', 'EXAMPLES', 'RETURN', 'main']


def _stringify_config(config):
    """Convert config values to strings as Incus stores them."""
    result = {}
    for k, v in (config or {}).items():
        if isinstance(v, bool):
            result[k] = str(v).lower()
        else:
            result[k] = str(v)
    return result


def _get_project(client, name):
    """Return (metadata dict, exists bool) for the project."""
    try:
        return client.get(f'/1.0/projects/{name}').get('metadata') or {}, True
    except IncusNotFoundException:
        return {}, False


def _create_project(module, client, name, desired):
    """Create project."""
    if not module.check_mode:
        client.post('/1.0/projects', {'name': name, **desired})
    return True


def _update_project(module, client, name, desired):
    """Update project configuration."""
    if not module.check_mode:
        client.put(f'/1.0/projects/{name}', desired)
    return True


def _delete_project(module, client, name):
    """Delete project."""
    if not module.check_mode:
        client.delete(f'/1.0/projects/{name}')
    return True


def main():
    """Run module."""
    argument_spec = {
        'name': {'type': 'str', 'required': True},
        'state': {'type': 'str', 'default': 'present', 'choices': ['present', 'absent']},
        'description': {'type': 'str', 'default': ''},
        'config': {'type': 'dict', 'default': {}},
    }
    argument_spec.update(INCUS_COMMON_ARGS)
    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=True)
    name = module.params['name']
    desired = {
        'description': module.params['description'],
        'config': _stringify_config(module.params['config']),
    }
    try:
        client = incus_client_from_module(module)
        current, exists = _get_project(client, name)
        if module.params['state'] == 'present':
            if not exists:
                changed = _create_project(module, client, name, desired)
            elif (current.get('description', '') == desired['description']
                    and current.get('config', {}) == desired['config']):
                changed = False
            else:
                changed = _update_project(module, client, name, desired)
        else:
            changed = _delete_project(module, client, name) if exists else False
        module.exit_json(changed=changed)
    except IncusClientException as e:
        module.fail_json(msg=str(e))


if __name__ == '__main__':
    main()
