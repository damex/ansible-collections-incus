#!/usr/bin/python
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

from urllib.parse import quote

from ansible_collections.damex.incus.plugins.module_utils.incus import (
    incus_create_info_module,
    incus_run_info_module,
)

__all__ = ['DOCUMENTATION', 'EXAMPLES', 'RETURN', 'main']


def main() -> None:
    """
    Run module.

    >>> main()
    """
    module = incus_create_info_module({
        'pool': {'type': 'str', 'required': True},
        'name': {'type': 'str'},
        'project': {'type': 'str', 'default': 'default'},
    })
    encoded_pool = quote(module.params['pool'], safe='')
    resource = f'storage-pools/{encoded_pool}/volumes/custom'
    incus_run_info_module(module, resource, 'storage_volumes')


if __name__ == '__main__':
    main()
