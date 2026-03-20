#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: Roman Kuzmitskii <ansible@damex.org>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

"""
Ensure Incus network address set.
"""

from __future__ import annotations

DOCUMENTATION = r"""
---
module: incus_network_address_set
short_description: Ensure Incus network address set
author: Roman Kuzmitskii (@damex) <ansible@damex.org>
description:
  - Create, update, and delete Incus network address sets via the Incus REST API.
  - Network address sets define reusable groups of IPv4 and IPv6 addresses
    that can be referenced in network ACL rules.
  - Address sets are referenced in ACL source and destination fields
    using a dollar sign prefix (e.g. $set_name).
extends_documentation_fragment:
  - damex.incus.common
  - damex.incus.common.project
  - damex.incus.common.write
options:
  name:
    description:
      - Name of the network address set.
    type: str
    required: true
  state:
    description:
      - Desired state of the network address set.
    type: str
    choices:
      - present
      - absent
    default: present
  description:
    description:
      - Description of the network address set.
    type: str
    default: ''
  config:
    description:
      - Network address set configuration key-value pairs.
      - Only user-defined keys (user.*) are supported.
    type: dict
    default: {}
  addresses:
    description:
      - List of IPv4 or IPv6 addresses, with or without CIDR suffix.
      - A mix of IPv4, IPv6, and CIDR notation is supported.
    type: list
    elements: str
"""

EXAMPLES = r"""
- name: Ensure network address set with IPv4 addresses
  damex.incus.incus_network_address_set:
    name: web_servers
    description: Web server addresses
    addresses:
      - 10.0.0.5
      - 10.0.0.6

- name: Ensure network address set with mixed addresses
  damex.incus.incus_network_address_set:
    name: dns_servers
    addresses:
      - 10.0.0.10
      - 2001:db8::1
      - 192.168.1.0/24

- name: Ensure network address set is absent
  damex.incus.incus_network_address_set:
    name: web_servers
    state: absent
"""

RETURN = r"""
"""

from ansible_collections.damex.incus.plugins.module_utils.incus import (
    INCUS_COMMON_ARGUMENT_SPEC,
    incus_build_desired,
    incus_create_write_module,
    incus_ensure_resource,
    incus_run_write_module,
)

__all__ = ['DOCUMENTATION', 'EXAMPLES', 'RETURN', 'main']


def main() -> None:
    """
    Run module.

    >>> main()
    """
    module = incus_create_write_module({
        **INCUS_COMMON_ARGUMENT_SPEC,
        'project': {'type': 'str', 'default': 'default'},
        'description': {'type': 'str', 'default': ''},
        'config': {'type': 'dict', 'default': {}},
        'addresses': {
            'type': 'list',
            'elements': 'str',
        },
    })
    desired = incus_build_desired(module)
    desired['addresses'] = sorted(module.params.get('addresses') or [])
    incus_run_write_module(module, lambda: incus_ensure_resource(module, 'network-address-sets', desired))


if __name__ == '__main__':
    main()
