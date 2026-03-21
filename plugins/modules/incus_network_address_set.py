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
      - User-defined configuration entries.
      - Each entry is flattened to a C(user.<name>) config key.
    type: list
    elements: dict
    suboptions:
      name:
        description:
          - Configuration key name (without the user. prefix).
        type: str
        required: true
      value:
        description:
          - Configuration value.
        type: str
        required: true
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

from typing import Any

from ansible_collections.damex.incus.plugins.module_utils.incus import (
    INCUS_COMMON_ARGUMENT_SPEC,
    incus_create_write_module,
    incus_ensure_resource,
    incus_run_write_module,
)
from ansible_collections.damex.incus.plugins.module_utils.common import (
    incus_common_flatten_key_value_to_config,
)

__all__ = ['DOCUMENTATION', 'EXAMPLES', 'RETURN', 'main']


def main() -> None:
    """
    Run module.

    >>> main()
    """
    argument_spec: dict[str, Any] = {
        'project': {'type': 'str', 'default': 'default'},
        'description': {'type': 'str', 'default': ''},
        'config': {
            'type': 'list',
            'elements': 'dict',
            'options': {
                'name': {
                    'type': 'str',
                    'required': True,
                },
                'value': {
                    'type': 'str',
                    'required': True,
                },
            },
        },
        'addresses': {
            'type': 'list',
            'elements': 'str',
        },
    }
    for spec_key, spec_value in INCUS_COMMON_ARGUMENT_SPEC.items():
        argument_spec[spec_key] = spec_value
    module = incus_create_write_module(argument_spec)
    desired: dict[str, Any] = {
        'description': module.params['description'],
        'config': incus_common_flatten_key_value_to_config('user', module.params.get('config')),
        'addresses': sorted(module.params.get('addresses') or []),
    }
    incus_run_write_module(module, lambda: incus_ensure_resource(module, 'network-address-sets', desired))


if __name__ == '__main__':
    main()
