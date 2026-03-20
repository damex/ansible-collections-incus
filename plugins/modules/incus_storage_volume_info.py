#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: Roman Kuzmitskii <ansible@damex.org>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

"""
Ensure Incus storage volume information is gathered.
"""

from __future__ import annotations

DOCUMENTATION = r"""
---
module: incus_storage_volume_info
short_description: Ensure Incus storage volume information is gathered
author: Roman Kuzmitskii (@damex) <ansible@damex.org>
description:
  - Gather information about Incus custom storage volumes via the Incus REST API.
  - Returns information about all custom volumes in a pool or a specific volume.
  - Storage volumes are project-scoped resources within a storage pool.
extends_documentation_fragment:
  - damex.incus.common
  - damex.incus.common.project
options:
  pool:
    description:
      - Name of the storage pool to query volumes from.
    type: str
    required: true
  name:
    description:
      - Name of the storage volume to query.
      - If not specified, all custom volumes in the pool are returned.
    type: str
"""

EXAMPLES = r"""
- name: Ensure storage volume information is gathered
  damex.incus.incus_storage_volume_info:
    pool: default
  register: result

- name: Ensure specific storage volume information is gathered
  damex.incus.incus_storage_volume_info:
    pool: default
    name: data
  register: result

- name: Ensure storage volume information is gathered from project
  damex.incus.incus_storage_volume_info:
    pool: default
    project: myproject
  register: result
"""

RETURN = r"""
storage_volumes:
  description: List of storage volume information.
  type: list
  returned: always
  elements: dict
  contains:
    name:
      description: Name of the storage volume.
      type: str
    description:
      description: Storage volume description.
      type: str
    content_type:
      description: Content type (filesystem or block).
      type: str
    config:
      description: Storage volume configuration.
      type: dict
"""

from typing import Any
from urllib.parse import quote

from ansible.module_utils.basic import AnsibleModule

from ansible_collections.damex.incus.plugins.module_utils.incus import (
    INCUS_COMMON_ARGS,
    INCUS_COMMON_MUTUALLY_EXCLUSIVE,
    INCUS_COMMON_REQUIRED_BY,
    INCUS_COMMON_REQUIRED_TOGETHER,
    IncusClientException,
    IncusNotFoundException,
    incus_build_query,
    incus_create_client,
)

__all__ = ['DOCUMENTATION', 'EXAMPLES', 'RETURN', 'main']


def main() -> None:
    """
    Run module.

    >>> main()
    """
    argument_spec: dict[str, Any] = {
        'pool': {'type': 'str', 'required': True},
        'name': {'type': 'str'},
        'project': {'type': 'str', 'default': 'default'},
    }
    for spec_key, spec_value in INCUS_COMMON_ARGS.items():
        argument_spec[spec_key] = spec_value
    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
        mutually_exclusive=INCUS_COMMON_MUTUALLY_EXCLUSIVE,
        required_together=INCUS_COMMON_REQUIRED_TOGETHER,
        required_by=INCUS_COMMON_REQUIRED_BY,
    )

    name = module.params.get('name')
    pool = module.params['pool']
    project = module.params.get('project')
    base_path = f'/1.0/storage-pools/{quote(pool, safe="")}/volumes/custom'
    result: list[Any] = []

    try:
        client = incus_create_client(module)

        if name:
            encoded_name = quote(name, safe='')
            query = incus_build_query(project=project)
            try:
                response = client.get(f'{base_path}/{encoded_name}{query}')
                metadata = response.get('metadata')
                result = [metadata] if metadata else []
            except IncusNotFoundException:
                result = []
        else:
            query = incus_build_query(project=project, recursion=1)
            response = client.get(f'{base_path}{query}')
            result = response.get('metadata') or []

    except IncusClientException as exc:
        module.fail_json(msg=str(exc))

    module.exit_json(storage_volumes=result)


if __name__ == '__main__':
    main()
