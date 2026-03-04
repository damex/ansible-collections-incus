#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: Roman Kuzmitskii <ansible@damex.org>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

"""Gather Incus network info."""

from __future__ import annotations

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.damex.incus.plugins.module_utils.incus import (
    INCUS_COMMON_ARGS,
    run_info_module,
)

DOCUMENTATION = r"""
---
module: incus_network_info
short_description: Gather information about Incus networks
description:
  - Gather information about Incus networks via the Incus REST API.
  - Returns information about all networks or a specific network.
extends_documentation_fragment: [damex.incus.common, damex.incus.common.project]
options:
  name:
    description:
      - Name of the network to query.
      - If not specified, all networks in the project are returned.
    type: str
"""

EXAMPLES = r"""
- name: Get all networks
  damex.incus.incus_network_info:
    project: default
  register: result

- name: Get specific network
  damex.incus.incus_network_info:
    name: incusbr0
    project: default
  register: result

- name: Get networks from remote server
  damex.incus.incus_network_info:
    url: https://incus.example.com:8443
    client_cert: /etc/incus/client.crt
    client_key: /etc/incus/client.key
  register: result
"""

RETURN = r"""
networks:
  description: List of network information.
  elements: dict
  type: list
  contains:
    name:
      description: Name of the network.
      type: str
    description:
      description: Network description.
      type: str
    type:
      description: Network type (bridge, macvlan, etc.).
      type: str
    status:
      description: Status of the network.
      type: str
    config:
      description: Network configuration.
      type: dict
    managed:
      description: Whether the network is managed by Incus.
      type: bool
  returned: always
"""

__all__ = ['DOCUMENTATION', 'EXAMPLES', 'RETURN', 'main']


def main():
    """Run module."""
    argument_spec = {'name': {'type': 'str'}, 'project': {'type': 'str', 'default': 'default'}}
    argument_spec.update(INCUS_COMMON_ARGS)
    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=True)
    run_info_module(module, 'networks', 'networks')


if __name__ == '__main__':
    main()
