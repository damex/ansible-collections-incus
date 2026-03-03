#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: Roman Kuzmitskii <ansible@damex.org>
# SPDX-License-Identifier: GPL-3.0-or-later

"""Gather Incus cluster member info."""

from __future__ import annotations

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.damex.incus.plugins.module_utils.incus import (
    INCUS_COMMON_ARGS,
    run_info_module,
)

DOCUMENTATION = r"""
---
module: incus_cluster_info
short_description: Gather information about Incus cluster members
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
- name: Get all cluster members
  damex.incus.incus_cluster_info:
    socket_path: /var/lib/incus/unix.socket
  register: result

- name: Get specific cluster member
  damex.incus.incus_cluster_info:
    name: node1
  register: result

- name: Get cluster member from remote server
  damex.incus.incus_cluster_info:
    url: https://incus.example.com:8443
    client_cert: /etc/incus/client.crt
    client_key: /etc/incus/client.key
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
"""

__all__ = ['DOCUMENTATION', 'EXAMPLES', 'RETURN', 'main']


def main():
    """Run module."""
    argument_spec = {'name': {'type': 'str'}}
    argument_spec.update(INCUS_COMMON_ARGS)
    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=True)
    run_info_module(module, 'cluster/members', 'cluster_members')


if __name__ == '__main__':
    main()
