#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: Roman Kuzmitskii <ansible@damex.org>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

"""
Ensure Incus cluster group.
"""

from __future__ import annotations

DOCUMENTATION = r"""
---
module: incus_cluster_group
short_description: Ensure Incus cluster group
author: Roman Kuzmitskii (@damex) <ansible@damex.org>
description:
  - Create, update, and delete Incus cluster groups via the Incus REST API.
  - Cluster groups allow launching instances on a cluster member that belongs to a subset of all available members.
  - The members list is managed as a full replacement — members not listed are removed.
extends_documentation_fragment:
  - damex.incus.common
  - damex.incus.common.write
options:
  name:
    description:
      - Name of the cluster group.
    type: str
    required: true
  state:
    description:
      - Desired state of the cluster group.
    type: str
    choices:
      - present
      - absent
    default: present
  description:
    description:
      - The description of the cluster group.
    type: str
    default: ''
  members:
    description:
      - List of members in this group.
      - Managed as a full replacement — members not listed are removed from the group.
    type: list
    elements: str
"""

EXAMPLES = r"""
- name: Ensure cluster group for ARM64 DPU nodes
  damex.incus.incus_cluster_group:
    name: dpu
    description: ARM64 DPU nodes
    members:
      - arm64-node1
      - arm64-node2

- name: Ensure empty cluster group
  damex.incus.incus_cluster_group:
    name: staging

- name: Ensure cluster group is absent
  damex.incus.incus_cluster_group:
    name: dpu
    state: absent
"""

RETURN = r"""
"""

from typing import Any
from urllib.parse import quote

from ansible_collections.damex.incus.plugins.module_utils.incus import (
    INCUS_COMMON_ARGUMENT_SPEC,
    IncusNotFoundException,
    incus_create_client,
    incus_create_write_module,
    incus_ensure_resource,
    incus_run_write_module,
    incus_wait,
)

__all__ = ['DOCUMENTATION', 'EXAMPLES', 'RETURN', 'main']


def _incus_ensure_cluster_group_absent(module: Any) -> bool:
    """
    Ensure cluster group is absent, clearing members before deletion.

    >>> _incus_ensure_cluster_group_absent(module)
    True
    """
    with incus_create_client(module) as client:
        name = quote(module.params['name'], safe='')
        try:
            current = client.get(f'/1.0/cluster/groups/{name}').get('metadata') or {}
        except IncusNotFoundException:
            return False
        if not module.check_mode:
            if current.get('members'):
                incus_wait(
                    module,
                    client,
                    client.put(
                        f'/1.0/cluster/groups/{name}',
                        {'description': current.get('description', ''), 'members': []},
                    ),
                )
            incus_wait(
                module,
                client,
                client.delete(f'/1.0/cluster/groups/{name}'),
            )
        return True


def main() -> None:
    """
    Run module.

    >>> main()
    """
    argument_spec: dict[str, Any] = {
        'description': {'type': 'str', 'default': ''},
        'members': {
            'type': 'list',
            'elements': 'str',
        },
    }
    for spec_key, spec_value in INCUS_COMMON_ARGUMENT_SPEC.items():
        argument_spec[spec_key] = spec_value
    module = incus_create_write_module(argument_spec)
    desired: dict[str, Any] = {
        'description': module.params['description'],
        'members': sorted(module.params.get('members') or []),
    }
    if module.params['state'] == 'absent':
        incus_run_write_module(
            module,
            lambda: _incus_ensure_cluster_group_absent(module),
        )
    else:
        incus_run_write_module(
            module,
            lambda: incus_ensure_resource(module, 'cluster/groups', desired),
        )


if __name__ == '__main__':
    main()
