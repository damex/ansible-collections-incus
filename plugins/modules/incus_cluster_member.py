#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: Roman Kuzmitskii <ansible@damex.org>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

"""Ensure Incus cluster member."""

from __future__ import annotations

DOCUMENTATION = r"""
---
module: incus_cluster_member
short_description: Ensure Incus cluster member
author: Roman Kuzmitskii (@damex) <ansible@damex.org>
description:
  - Ensures Incus cluster members via the Incus REST API.
  - When creating a new member, generates a join token and returns it.
  - When updating an existing member, ensures description, config, roles, groups, and failure domain.
  - When removing a member, deletes it from the cluster.
extends_documentation_fragment:
  - damex.incus.common
  - damex.incus.common.write
options:
  name:
    description:
      - Name of the cluster member.
    type: str
    required: true
  state:
    description:
      - Desired state of the cluster member.
    type: str
    choices:
      - present
      - absent
    default: present
  description:
    description:
      - Description of the cluster member.
    type: str
    default: ''
  config:
    description:
      - Cluster member configuration key-value pairs.
    type: dict
    default: {}
    suboptions:
      scheduler.instance:
        description:
          - Controls how instances are scheduled to run on this member.
        type: str
        choices:
          - all
          - manual
          - group
  roles:
    description:
      - List of roles assigned to the cluster member.
    type: list
    elements: str
  groups:
    description:
      - List of cluster groups for the member.
    type: list
    elements: str
  failure_domain:
    description:
      - Failure domain of the cluster member.
    type: str
"""

EXAMPLES = r"""
- name: Ensure cluster member join token
  damex.incus.incus_cluster_member:
    name: node2
  register: result

- name: Ensure cluster member config
  damex.incus.incus_cluster_member:
    name: node1
    config:
      scheduler.instance: all
    description: Primary node

- name: Ensure cluster member roles
  damex.incus.incus_cluster_member:
    name: node1
    roles:
      - database

- name: Ensure cluster member is absent
  damex.incus.incus_cluster_member:
    name: node2
    state: absent
"""

RETURN = r"""
join_token:
  description: Join secret for the cluster member.
  type: str
  returned: when creating a new member
join_fingerprint:
  description: Fingerprint of the cluster network certificate.
  type: str
  returned: when creating a new member
join_addresses:
  description: Addresses of existing online cluster members.
  type: list
  elements: str
  returned: when creating a new member
"""

from typing import Any
from urllib.parse import quote

from ansible_collections.damex.incus.plugins.module_utils.incus import (
    INCUS_COMMON_ARGUMENT_SPEC,
    IncusClientException,
    IncusNotFoundException,
    incus_create_client,
    incus_create_write_module,
    incus_wait,
)
from ansible_collections.damex.incus.plugins.module_utils.common import (
    incus_common_stringify_dict,
)

__all__ = ['DOCUMENTATION', 'EXAMPLES', 'RETURN', 'main']

INCUS_CLUSTER_MEMBER_CONFIG_OPTIONS = {
    'scheduler.instance': {
        'type': 'str',
        'choices': [
            'all',
            'manual',
            'group',
        ],
    },
}


def _ensure_cluster_member(module: Any) -> dict[str, Any]:
    """Ensure cluster member."""
    client = incus_create_client(module)
    name = module.params['name']
    encoded_name = quote(name, safe='')

    try:
        current = client.get(f'/1.0/cluster/members/{encoded_name}').get('metadata') or {}
        exists = True
    except IncusNotFoundException:
        current = {}
        exists = False

    if module.params['state'] == 'present':
        if not exists:
            if module.check_mode:
                return {'changed': True}
            response = client.post('/1.0/cluster/members', {'server_name': name})
            operation = incus_wait(module, client, response)
            metadata = operation.get('metadata', {}) if operation else {}
            return {
                'changed': True,
                'join_token': metadata.get('secret', ''),
                'join_fingerprint': metadata.get('fingerprint', ''),
                'join_addresses': metadata.get('addresses', []),
            }
        desired: dict[str, Any] = {
            'description': module.params['description'],
            'config': incus_common_stringify_dict(module.params['config'] or {}),
        }
        roles = module.params.get('roles')
        if roles is not None:
            desired['roles'] = sorted(roles)
        groups = module.params.get('groups')
        if groups is not None:
            desired['groups'] = sorted(groups)
        failure_domain = module.params.get('failure_domain')
        if failure_domain is not None:
            desired['failure_domain'] = failure_domain
        if all(k in current and current[k] == v for k, v in desired.items()):
            return {'changed': False}
        if not module.check_mode:
            incus_wait(module, client, client.put(
                f'/1.0/cluster/members/{encoded_name}',
                desired,
            ))
        return {'changed': True}

    if exists:
        if not module.check_mode:
            incus_wait(module, client, client.delete(
                f'/1.0/cluster/members/{encoded_name}',
            ))
        return {'changed': True}
    return {'changed': False}


def main() -> None:
    """Run module."""
    module = incus_create_write_module({
        **INCUS_COMMON_ARGUMENT_SPEC,
        'description': {'type': 'str', 'default': ''},
        'config': {
            'type': 'dict',
            'default': {},
            'options': INCUS_CLUSTER_MEMBER_CONFIG_OPTIONS,
        },
        'roles': {
            'type': 'list',
            'elements': 'str',
        },
        'groups': {
            'type': 'list',
            'elements': 'str',
        },
        'failure_domain': {'type': 'str'},
    })
    try:
        result = _ensure_cluster_member(module)
        module.exit_json(**result)
    except IncusClientException as exc:
        module.fail_json(msg=str(exc))


if __name__ == '__main__':
    main()
