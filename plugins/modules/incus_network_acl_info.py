#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: Roman Kuzmitskii <ansible@damex.org>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

"""
Ensure Incus network ACL information is gathered.
"""

from __future__ import annotations

DOCUMENTATION = r"""
---
module: incus_network_acl_info
short_description: Ensure Incus network ACL information is gathered
author: Roman Kuzmitskii (@damex) <ansible@damex.org>
description:
  - Gather information about Incus network ACLs via the Incus REST API.
  - Returns information about all network ACLs or a specific network ACL.
extends_documentation_fragment:
  - damex.incus.common
  - damex.incus.common.project
options:
  name:
    description:
      - Name of the network ACL to query.
      - If not specified, all network ACLs in the project are returned.
    type: str
"""

EXAMPLES = r"""
- name: Ensure network ACL information is gathered
  damex.incus.incus_network_acl_info:
    project: default
  register: result

- name: Ensure specific network ACL information is gathered
  damex.incus.incus_network_acl_info:
    name: web
    project: default
  register: result
"""

RETURN = r"""
network_acls:
  description: List of network ACL information.
  elements: dict
  type: list
  contains:
    name:
      description: Name of the network ACL.
      type: str
    description:
      description: Network ACL description.
      type: str
    config:
      description: Network ACL configuration.
      type: dict
    ingress:
      description: List of ingress rules.
      type: list
      elements: dict
    egress:
      description: List of egress rules.
      type: list
      elements: dict
  returned: always
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
    incus_ensure_info('network-acls', 'network_acls', project_scoped=True)


if __name__ == '__main__':
    main()
