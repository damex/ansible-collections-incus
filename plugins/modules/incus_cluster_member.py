#!/usr/bin/python
# Copyright: Roman Kuzmitskii <ansible@damex.org>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

"""
Ensure Incus cluster member.
"""

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
      - Use joined to generate a join token for a new member.
      - Use present to update an existing member.
    type: str
    choices:
      - present
      - joined
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
    state: joined
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

import base64
import json
from typing import Any
from urllib.parse import quote

from ansible_collections.damex.incus.plugins.module_utils.incus_client import (
    IncusClientException,
    IncusNotFoundException,
    incus_create_client,
)
from ansible_collections.damex.incus.plugins.module_utils.incus import (
    INCUS_COMMON_ARGUMENT_SPEC,
    incus_build_result,
    incus_create_write_module,
    incus_wait,
)
from ansible_collections.damex.incus.plugins.module_utils.common import (
    incus_common_stringify_dict,
)

__all__ = ['DOCUMENTATION', 'EXAMPLES', 'RETURN', 'main']

_IMMUTABLE_ROLES = frozenset({
    'database',
    'database-leader',
    'database-standby',
})

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


def _create_join_token(client: Any, name: str) -> dict[str, Any]:
    """
    Create join token for new cluster member.

    >>> _create_join_token(client, 'node2')
    {'changed': True, 'join_token': '...', 'join_fingerprint': '...', 'join_addresses': [...]}
    """
    response = client.post('/1.0/cluster/members', {'server_name': name})
    metadata = response.get('metadata', {}).get('metadata', {})
    token_dict: dict[str, Any] = {
        'server_name': name,
        'fingerprint': metadata.get('fingerprint', ''),
        'addresses': metadata.get('addresses', []),
        'secret': metadata.get('secret', ''),
    }
    expires_at = metadata.get('expires_at', '')
    if expires_at:
        token_dict['expires_at'] = expires_at
    return {
        'changed': True,
        'join_token': base64.standard_b64encode(
            json.dumps(token_dict, separators=(',', ':')).encode(),
        ).decode(),
        'join_fingerprint': metadata.get('fingerprint', ''),
        'join_addresses': metadata.get('addresses', []),
    }


def _ensure_cluster_member_present(
    module: Any,
    client: Any,
    current: dict[str, Any],
) -> dict[str, Any]:
    """
    Ensure cluster member is present.

    >>> _ensure_cluster_member_present(module, client, {})
    {'changed': False, 'changed_keys': []}
    """
    # incus rejects PUT on single-node clusters due to database-client role validation bug
    members = client.get('/1.0/cluster/members').get('metadata') or []
    desired: dict[str, Any] = {
        'description': module.params['description'],
        'config': incus_common_stringify_dict(module.params['config'] or {}),
        'roles': sorted(current.get('roles', [])),
        'groups': sorted(current.get('groups', [])),
        'failure_domain': current.get('failure_domain', ''),
    }
    if module.params.get('roles') is not None:
        current_immutable = [role for role in current.get('roles', []) if role in _IMMUTABLE_ROLES]
        desired['roles'] = sorted(set(module.params['roles']) | set(current_immutable))
    if module.params.get('groups') is not None:
        desired['groups'] = sorted(module.params['groups'])
    if module.params.get('failure_domain'):
        desired['failure_domain'] = module.params['failure_domain']

    def _comparable(value: Any) -> Any:
        return sorted(value) if isinstance(value, list) else value
    before = {
        field_key: current.get(field_key)
        for field_key in desired
    }
    changed = len(members) > 1 and not all(
        field_key in current and _comparable(current[field_key]) == field_value
        for field_key, field_value in desired.items()
    )
    if not changed:
        return incus_build_result(False)
    encoded_name = quote(module.params['name'], safe='')
    if not module.check_mode:
        incus_wait(
            module,
            client,
            client.put(
                f'/1.0/cluster/members/{encoded_name}',
                desired,
            ),
        )
    return incus_build_result(True, before=before, after=desired)


def _ensure_cluster_member(module: Any) -> dict[str, Any]:
    """
    Ensure cluster member.

    >>> _ensure_cluster_member(module)
    {'changed': False, 'changed_keys': []}
    """
    with incus_create_client(module) as client:
        name = module.params['name']
        encoded_name = quote(name, safe='')

        try:
            current = client.get(f'/1.0/cluster/members/{encoded_name}').get('metadata') or {}
            exists = True
        except IncusNotFoundException:
            current = {}
            exists = False

        if module.params['state'] == 'joined':
            if not exists and not module.check_mode:
                return _create_join_token(client, name)
            return incus_build_result(not exists)

        if module.params['state'] == 'present':
            if not exists:
                return incus_build_result(False)
            return _ensure_cluster_member_present(module, client, current)

        if not exists:
            return incus_build_result(False)
        if not module.check_mode:
            incus_wait(
                module,
                client,
                client.delete(f'/1.0/cluster/members/{encoded_name}'),
            )
        return incus_build_result(
            True,
            before={
                'description': current.get('description', ''),
                'config': current.get('config', {}),
                'roles': sorted(current.get('roles', [])),
                'groups': sorted(current.get('groups', [])),
            },
            after={},
        )


def main() -> None:
    """
    Run module.

    >>> main()
    """
    argument_spec: dict[str, Any] = {
        'state': {
            'type': 'str',
            'default': 'present',
            'choices': [
                'present',
                'joined',
                'absent',
            ],
        },
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
    }
    for spec_key, spec_value in INCUS_COMMON_ARGUMENT_SPEC.items():
        if spec_key not in argument_spec:
            argument_spec[spec_key] = spec_value
    module = incus_create_write_module(argument_spec)
    try:
        result = _ensure_cluster_member(module)
        changed = result['changed']
        changed_keys = result.get('changed_keys', [])
        diff = result.get('diff')
        join_token = result.get('join_token')
        if join_token:
            module.exit_json(
                changed=changed,
                changed_keys=changed_keys,
                join_token=join_token,
                join_fingerprint=result.get('join_fingerprint', ''),
                join_addresses=result.get('join_addresses', []),
            )
        elif diff:
            module.exit_json(
                changed=changed,
                diff=diff,
                changed_keys=changed_keys,
            )
        else:
            module.exit_json(
                changed=changed,
                changed_keys=changed_keys,
            )
    except IncusClientException as exception:
        module.fail_json(msg=str(exception))


if __name__ == '__main__':
    main()
