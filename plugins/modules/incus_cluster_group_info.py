#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: Roman Kuzmitskii <ansible@damex.org>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

"""
Ensure Incus cluster group information is gathered.
"""

from __future__ import annotations

DOCUMENTATION = r"""
---
module: incus_cluster_group_info
short_description: Ensure Incus cluster group information is gathered
author: Roman Kuzmitskii (@damex) <ansible@damex.org>
description:
  - Gather information about Incus cluster groups via the Incus REST API.
  - Returns information about all cluster groups or a specific group.
extends_documentation_fragment: [damex.incus.common]
options:
  name:
    description:
      - Name of the cluster group to query.
      - If not specified, all cluster groups are returned.
    type: str
"""

EXAMPLES = r"""
- name: Ensure cluster group information is gathered
  damex.incus.incus_cluster_group_info:
    socket_path: /var/lib/incus/unix.socket
  register: result

- name: Ensure specific cluster group information is gathered
  damex.incus.incus_cluster_group_info:
    name: dpu
  register: result
"""

RETURN = r"""
cluster_groups:
  description: List of cluster group information.
  type: list
  elements: dict
  returned: always
  contains:
    name:
      description: Name of the cluster group.
      type: str
    description:
      description: The description of the cluster group.
      type: str
    members:
      description: List of members in this group.
      type: list
      elements: str
"""

from ansible_collections.damex.incus.plugins.module_utils.incus import (
    incus_ensure_info,
)

__all__ = ['DOCUMENTATION', 'EXAMPLES', 'RETURN', 'main']


def main() -> None:
    """
    Run module.

    >>> main()
    """
    incus_ensure_info('cluster/groups', 'cluster_groups')


if __name__ == '__main__':
    main()
