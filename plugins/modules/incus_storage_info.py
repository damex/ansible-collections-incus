#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: Roman Kuzmitskii <ansible@damex.org>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

"""Ensure Incus storage information is gathered."""

from __future__ import annotations

DOCUMENTATION = r"""
---
module: incus_storage_info
short_description: Ensure Incus storage information is gathered
author: Roman Kuzmitskii (@damex) <ansible@damex.org>
description:
  - Gather information about Incus storage pools via the Incus REST API.
  - Returns information about all storage pools or a specific pool.
  - Storage pools are global resources, not project-scoped.
extends_documentation_fragment: [damex.incus.common]
options:
  name:
    description:
      - Name of the storage pool to query.
      - If not specified, all storage pools are returned.
    type: str
"""

EXAMPLES = r"""
- name: Ensure storage pool information is gathered
  damex.incus.incus_storage_info:
    socket_path: /var/lib/incus/unix.socket
  register: result

- name: Ensure specific storage pool information is gathered
  damex.incus.incus_storage_info:
    name: default
  register: result

- name: Ensure storage pool information is gathered from remote server
  damex.incus.incus_storage_info:
    url: https://incus.example.com:8443
    client_cert_path: /etc/incus/client.crt
    client_key_path: /etc/incus/client.key
  register: result
"""

RETURN = r"""
storage_pools:
  description: List of storage pool information.
  type: list
  returned: always
  elements: dict
  contains:
    name:
      description: Name of the storage pool.
      type: str
    description:
      description: Storage pool description.
      type: str
    driver:
      description: Storage driver (dir, zfs, btrfs, etc.).
      type: str
    status:
      description: Status of the storage pool.
      type: str
    config:
      description: Storage pool configuration.
      type: dict
"""

from ansible_collections.damex.incus.plugins.module_utils.incus import (
    incus_ensure_info,
)

__all__ = ['DOCUMENTATION', 'EXAMPLES', 'RETURN', 'main']


def main() -> None:
    """Run module."""
    incus_ensure_info('storage-pools', 'storage_pools')


if __name__ == '__main__':
    main()
