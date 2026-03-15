#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: Roman Kuzmitskii <ansible@damex.org>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

"""Ensure Incus cluster member information is gathered."""

from __future__ import annotations

DOCUMENTATION = r"""
---
module: incus_cluster_member_info
short_description: Ensure Incus cluster member information is gathered
author: Roman Kuzmitskii (@damex) <ansible@damex.org>
description:
  - Gather information about Incus cluster members via the Incus REST API.
  - Returns information about all cluster members or a specific member.
  - Returns empty list when the node is not part of a cluster.
extends_documentation_fragment: [damex.incus.common]
options:
  name:
    description:
      - Name of the cluster member to query.
      - If not specified, all cluster members are returned.
    type: str
"""

EXAMPLES = r"""
- name: Ensure cluster member information is gathered
  damex.incus.incus_cluster_member_info:
    socket_path: /var/lib/incus/unix.socket
  register: result

- name: Ensure specific cluster member information is gathered
  damex.incus.incus_cluster_member_info:
    name: node1
  register: result
"""

RETURN = r"""
cluster_members:
  description: List of cluster member information. Empty if node is not clustered.
  type: list
  elements: dict
  returned: always
  contains:
    server_name:
      description: Name of the cluster member.
      type: str
    url:
      description: URL of the cluster member.
      type: str
    roles:
      description: Roles assigned to the cluster member.
      type: list
      elements: str
    status:
      description: Status of the cluster member.
      type: str
    database:
      description: Whether the member is a database node.
      type: bool
    config:
      description: Member configuration.
      type: dict
    description:
      description: Member description.
      type: str
    groups:
      description: Cluster groups for the member.
      type: list
      elements: str
    failure_domain:
      description: Failure domain of the member.
      type: str
"""

from ansible_collections.damex.incus.plugins.module_utils.incus import (
    incus_ensure_info,
)

__all__ = ['DOCUMENTATION', 'EXAMPLES', 'RETURN', 'main']


def main() -> None:
    """Run module."""
    incus_ensure_info('cluster/members', 'cluster_members')


if __name__ == '__main__':
    main()
