#!/usr/bin/python
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
  - The members list is managed as a full replacement. Members not listed are removed.
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
      - Managed as a full replacement. Members not listed are removed from the group.
    type: list
    elements: str
  config:
    description:
      - Cluster group configuration keys.
    type: dict
    suboptions:
      vm_cpu:
        description:
          - List of per-architecture virtual machine CPU definitions.
          - Each entry is converted to C(instances.vm.cpu.<architecture>.<key>) config keys internally.
        type: list
        elements: dict
        suboptions:
          architecture:
            description:
              - Incus architecture name.
            type: str
            required: true
            choices:
              - i686
              - x86_64
              - armv6l
              - armv7l
              - armv8l
              - aarch64
              - ppc
              - ppc64
              - ppc64le
              - s390x
              - mips
              - mips64
              - riscv32
              - riscv64
              - loongarch64
          baseline:
            description:
              - CPU base architecture name as listed by C(qemu -cpu ?).
            type: str
          flags:
            description:
              - Comma-separated CPU flags to add to or remove from the baseline.
            type: str
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

- name: Ensure cluster group with VM CPU baseline
  damex.incus.incus_cluster_group:
    name: amd
    description: AMD EPYC nodes
    members:
      - node1
      - node2
    config:
      vm_cpu:
        - architecture: x86_64
          baseline: EPYC-v2
          flags: -svm

- name: Ensure cluster group is absent
  damex.incus.incus_cluster_group:
    name: dpu
    state: absent
"""

RETURN = r"""
extends_documentation_fragment:
  - damex.incus.common.write_return
"""

from collections import Counter
from typing import Any
from urllib.parse import quote

from ansible_collections.damex.incus.plugins.module_utils.common import (
    incus_common_flatten_to_config,
)
from ansible_collections.damex.incus.plugins.module_utils.incus_client import (
    IncusNotFoundException,
    incus_create_client,
)
from ansible_collections.damex.incus.plugins.module_utils.incus import (
    INCUS_COMMON_ARGUMENT_SPEC,
    incus_build_result,
    incus_create_write_module,
    incus_ensure_resource,
    incus_run_write_module,
    incus_wait,
)

__all__ = ['DOCUMENTATION', 'EXAMPLES', 'RETURN', 'main']


def _incus_cluster_group_build_config(module: Any) -> dict[str, str]:
    """
    Build config keys from vm_cpu definitions.

    >>> _incus_cluster_group_build_config(module)
    {'instances.vm.cpu.x86_64.baseline': 'EPYC-v2'}
    """
    cpu_definitions = (module.params.get('config') or {}).get('vm_cpu') or []
    architecture_counts = Counter(
        cpu_definition['architecture']
        for cpu_definition in cpu_definitions
    )
    duplicate_architectures = sorted(
        architecture
        for architecture, occurrence_count in architecture_counts.items()
        if occurrence_count > 1
    )
    if duplicate_architectures:
        module.fail_json(msg=f"Duplicate vm_cpu architectures: {', '.join(duplicate_architectures)}")
    cpu_by_architecture = {
        cpu_definition['architecture']: {
            definition_key: definition_value
            for definition_key, definition_value in cpu_definition.items()
            if definition_key != 'architecture' and definition_value is not None
        }
        for cpu_definition in cpu_definitions
    }
    return incus_common_flatten_to_config('instances.vm.cpu', cpu_by_architecture)


def _incus_ensure_cluster_group_absent(module: Any) -> dict[str, Any]:
    """
    Ensure cluster group is absent, clearing members before deletion.

    >>> _incus_ensure_cluster_group_absent(module)
    {'changed': True, 'diff': {...}, 'changed_keys': [...]}
    """
    with incus_create_client(module) as client:
        name = quote(module.params['name'], safe='')
        try:
            current = client.get(f'/1.0/cluster/groups/{name}').get('metadata') or {}
        except IncusNotFoundException:
            return incus_build_result(False)
        current_members = sorted(current.get('members') or [])
        if not module.check_mode:
            if current_members:
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
        return incus_build_result(
            True,
            before={
                'description': current.get('description', ''),
                'members': current_members,
            },
            after={},
        )


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
        'config': {
            'type': 'dict',
            'options': {
                'vm_cpu': {
                    'type': 'list',
                    'elements': 'dict',
                    'options': {
                        'architecture': {
                            'type': 'str',
                            'required': True,
                            'choices': [
                                'i686',
                                'x86_64',
                                'armv6l',
                                'armv7l',
                                'armv8l',
                                'aarch64',
                                'ppc',
                                'ppc64',
                                'ppc64le',
                                's390x',
                                'mips',
                                'mips64',
                                'riscv32',
                                'riscv64',
                                'loongarch64',
                            ],
                        },
                        'baseline': {'type': 'str'},
                        'flags': {'type': 'str'},
                    },
                },
            },
        },
    }
    for spec_key, spec_value in INCUS_COMMON_ARGUMENT_SPEC.items():
        argument_spec[spec_key] = spec_value
    module = incus_create_write_module(argument_spec)
    desired: dict[str, Any] = {
        'description': module.params['description'],
        'members': sorted(module.params.get('members') or []),
        'config': _incus_cluster_group_build_config(module),
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
