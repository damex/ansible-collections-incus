#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: Roman Kuzmitskii <ansible@damex.org>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

"""
Ensure Incus cluster information is gathered.
"""

from __future__ import annotations

DOCUMENTATION = r"""
---
module: incus_cluster_info
short_description: Ensure Incus cluster information is gathered
author: Roman Kuzmitskii (@damex) <ansible@damex.org>
description:
  - Gather information about the Incus cluster via the Incus REST API.
  - Returns cluster state including whether clustering is enabled.
extends_documentation_fragment: [damex.incus.common]
"""

EXAMPLES = r"""
- name: Ensure cluster information is gathered
  damex.incus.incus_cluster_info:
    socket_path: /var/lib/incus/unix.socket
  register: result
"""

RETURN = r"""
cluster:
  description: Cluster information.
  type: dict
  returned: always
  contains:
    enabled:
      description: Whether clustering is enabled.
      type: bool
    server_name:
      description: Name of the cluster member answering the request.
      type: str
    member_config:
      description: Configuration keys for joining members.
      type: list
      elements: dict
"""

from ansible_collections.damex.incus.plugins.module_utils.incus import (
    IncusClientException,
    incus_create_client,
    incus_create_info_module,
)

__all__ = ['DOCUMENTATION', 'EXAMPLES', 'RETURN', 'main']


def main() -> None:
    """
    Run module.

    >>> main()
    """
    module = incus_create_info_module({})
    try:
        client = incus_create_client(module)
        response = client.get('/1.0/cluster')
        cluster = response.get('metadata') or {}
    except IncusClientException as exc:
        module.fail_json(msg=str(exc))
        return
    module.exit_json(cluster=cluster)


if __name__ == '__main__':
    main()
