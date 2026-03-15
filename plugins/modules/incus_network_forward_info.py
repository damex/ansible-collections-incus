#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: Roman Kuzmitskii <ansible@damex.org>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

"""Ensure Incus network forward information is gathered."""

from __future__ import annotations

DOCUMENTATION = r"""
---
module: incus_network_forward_info
short_description: Ensure Incus network forward information is gathered
author: Roman Kuzmitskii (@damex) <ansible@damex.org>
description:
  - Gather information about Incus network forwards via the Incus REST API.
  - Returns information about all forwards in a network or a specific forward.
  - Network forwards are project-scoped resources within a network.
extends_documentation_fragment:
  - damex.incus.common
  - damex.incus.common.project
options:
  network:
    description:
      - Name of the network to query forwards from.
    type: str
    required: true
  name:
    description:
      - Listen address of the network forward to query.
      - If not specified, all forwards in the network are returned.
    type: str
"""

EXAMPLES = r"""
- name: Ensure network forward information is gathered
  damex.incus.incus_network_forward_info:
    network: incusbr0
  register: result

- name: Ensure specific network forward information is gathered
  damex.incus.incus_network_forward_info:
    network: incusbr0
    name: 192.168.1.100
  register: result

- name: Ensure network forward information is gathered from project
  damex.incus.incus_network_forward_info:
    network: incusbr0
    project: myproject
  register: result
"""

RETURN = r"""
network_forwards:
  description: List of network forward information.
  type: list
  returned: always
  elements: dict
  contains:
    listen_address:
      description: Listen address of the forward.
      type: str
    description:
      description: Forward description.
      type: str
    config:
      description: Forward configuration.
      type: dict
    ports:
      description: Port forwarding rules.
      type: list
"""

from urllib.parse import quote

from ansible_collections.damex.incus.plugins.module_utils.incus import (
    incus_create_info_module,
    incus_run_info_module,
)

__all__ = ['DOCUMENTATION', 'EXAMPLES', 'RETURN', 'main']


def main() -> None:
    """Run module."""
    module = incus_create_info_module({
        'network': {'type': 'str', 'required': True},
        'name': {'type': 'str'},
        'project': {'type': 'str', 'default': 'default'},
    })
    encoded_network = quote(module.params['network'], safe='')
    resource = f'networks/{encoded_network}/forwards'
    incus_run_info_module(module, resource, 'network_forwards')


if __name__ == '__main__':
    main()
