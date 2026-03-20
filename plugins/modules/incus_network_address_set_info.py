#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: Roman Kuzmitskii <ansible@damex.org>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

"""
Ensure Incus network address set information is gathered.
"""

from __future__ import annotations

DOCUMENTATION = r"""
---
module: incus_network_address_set_info
short_description: Ensure Incus network address set information is gathered
author: Roman Kuzmitskii (@damex) <ansible@damex.org>
description:
  - Gather information about Incus network address sets via the Incus REST API.
  - Returns information about all network address sets or a specific address set.
extends_documentation_fragment:
  - damex.incus.common
  - damex.incus.common.project
options:
  name:
    description:
      - Name of the network address set to query.
      - If not specified, all network address sets in the project are returned.
    type: str
"""

EXAMPLES = r"""
- name: Ensure network address set information is gathered
  damex.incus.incus_network_address_set_info:
    project: default
  register: result

- name: Ensure specific network address set information is gathered
  damex.incus.incus_network_address_set_info:
    name: web_servers
    project: default
  register: result
"""

RETURN = r"""
network_address_sets:
  description: List of network address set information.
  elements: dict
  type: list
  contains:
    name:
      description: Name of the network address set.
      type: str
    description:
      description: Network address set description.
      type: str
    config:
      description: Network address set configuration.
      type: dict
    addresses:
      description: List of addresses in the set.
      type: list
      elements: str
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
    incus_ensure_info('network-address-sets', 'network_address_sets', project_scoped=True)


if __name__ == '__main__':
    main()
