#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: Roman Kuzmitskii <ansible@damex.org>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

"""
Ensure Incus network zone information is gathered.
"""

from __future__ import annotations

DOCUMENTATION = r"""
---
module: incus_network_zone_info
short_description: Ensure Incus network zone information is gathered
author: Roman Kuzmitskii (@damex) <ansible@damex.org>
description:
  - Gather information about Incus network zones via the Incus REST API.
  - Returns information about all network zones or a specific network zone.
extends_documentation_fragment:
  - damex.incus.common
  - damex.incus.common.project
options:
  name:
    description:
      - Name of the network zone to query.
      - If not specified, all network zones in the project are returned.
    type: str
"""

EXAMPLES = r"""
- name: Ensure network zone information is gathered
  damex.incus.incus_network_zone_info:
    project: default
  register: result

- name: Ensure specific network zone information is gathered
  damex.incus.incus_network_zone_info:
    name: example.com
    project: default
  register: result
"""

RETURN = r"""
network_zones:
  description: List of network zone information.
  elements: dict
  type: list
  contains:
    name:
      description: Name of the network zone.
      type: str
    description:
      description: Network zone description.
      type: str
    config:
      description: Network zone configuration.
      type: dict
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
    incus_ensure_info('network-zones', 'network_zones', project_scoped=True)


if __name__ == '__main__':
    main()
