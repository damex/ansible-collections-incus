#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: Roman Kuzmitskii <ansible@damex.org>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

"""
Ensure Incus network forward.
"""

from __future__ import annotations

DOCUMENTATION = r"""
---
module: incus_network_forward
short_description: Ensure Incus network forward
author: Roman Kuzmitskii (@damex) <ansible@damex.org>
description:
  - Create, update, and delete Incus network forwards via the Incus REST API.
  - Network forwards allow external IP addresses to be forwarded to internal
    addresses inside bridge and OVN networks.
  - Forwards are identified by their listen address within a given network.
extends_documentation_fragment:
  - damex.incus.common
  - damex.incus.common.project
  - damex.incus.common.write
options:
  network:
    description:
      - Name of the network containing the forward.
    type: str
    required: true
  name:
    description:
      - Listen address of the network forward.
    type: str
    required: true
  state:
    description:
      - Desired state of the network forward.
    type: str
    choices:
      - present
      - absent
    default: present
  description:
    description:
      - Description of the network forward.
    type: str
    default: ''
  config:
    description:
      - Network forward configuration key-value pairs.
      - Boolean values are converted to lowercase strings.
    type: dict
    default: {}
    suboptions:
      target_address:
        description:
          - Default target address for traffic not matching any port rule.
        type: str
  ports:
    description:
      - List of port forwarding rules.
    type: list
    elements: dict
    suboptions:
      protocol:
        description:
          - Network protocol to forward.
        type: str
        required: true
        choices:
          - tcp
          - udp
      listen_port:
        description:
          - Port or port range to listen on.
        type: str
        required: true
      target_address:
        description:
          - Target address to forward traffic to.
        type: str
        required: true
      target_port:
        description:
          - Target port or port range.
          - Defaults to listen port if not specified.
        type: str
      description:
        description:
          - Description of the port rule.
        type: str
      snat:
        description:
          - Whether to rewrite traffic source address.
          - Only supported on bridge networks with nftables.
        type: bool
"""

EXAMPLES = r"""
- name: Ensure network forward with default target
  damex.incus.incus_network_forward:
    network: incusbr0
    name: 192.168.1.100
    config:
      target_address: 10.0.0.5

- name: Ensure network forward with port rules
  damex.incus.incus_network_forward:
    network: incusbr0
    name: 192.168.1.100
    description: Web server forward
    ports:
      - protocol: tcp
        listen_port: 80,443
        target_address: 10.0.0.5
      - protocol: udp
        listen_port: "53"
        target_address: 10.0.0.10
        description: DNS forward

- name: Ensure network forward is absent
  damex.incus.incus_network_forward:
    network: incusbr0
    name: 192.168.1.100
    state: absent
"""

RETURN = r"""
"""

from typing import Any
from urllib.parse import quote

from ansible_collections.damex.incus.plugins.module_utils.incus import (
    INCUS_COMMON_ARGUMENT_SPEC,
    IncusResourceOptions,
    incus_build_desired,
    incus_create_write_module,
    incus_ensure_resource,
    incus_run_write_module,
)

__all__ = ['DOCUMENTATION', 'EXAMPLES', 'RETURN', 'main']

INCUS_NETWORK_FORWARD_CONFIG_OPTIONS = {
    'target_address': {'type': 'str'},
}

INCUS_NETWORK_FORWARD_PORT_OPTIONS = {
    'protocol': {
        'type': 'str',
        'required': True,
        'choices': [
            'tcp',
            'udp',
        ],
    },
    'listen_port': {
        'type': 'str',
        'required': True,
    },
    'target_address': {
        'type': 'str',
        'required': True,
    },
    'target_port': {'type': 'str'},
    'description': {'type': 'str'},
    'snat': {'type': 'bool'},
}


def _normalize_ports(ports: list[dict[str, Any]] | None) -> list[dict[str, Any]]:
    """
    Normalize ports with defaults.

    >>> _normalize_ports([{'protocol': 'p', 'listen_port': '0', 'target_address': 'a'}])
    [{'description': '', 'protocol': 'p', 'listen_port': '0', 'target_port': '', 'target_address': 'a', 'snat': False}]
    """
    normalized = []
    for port in (ports or []):
        normalized.append({
            'description': port.get('description') or '',
            'protocol': port['protocol'],
            'listen_port': port['listen_port'],
            'target_port': port.get('target_port') or '',
            'target_address': port['target_address'],
            'snat': bool(port.get('snat')),
        })
    return normalized


def main() -> None:
    """
    Run module.

    >>> main()
    """
    argument_spec: dict[str, Any] = {
        'network': {'type': 'str', 'required': True},
        'project': {'type': 'str', 'default': 'default'},
        'description': {'type': 'str', 'default': ''},
        'config': {
            'type': 'dict',
            'default': {},
            'options': INCUS_NETWORK_FORWARD_CONFIG_OPTIONS,
        },
        'ports': {
            'type': 'list',
            'elements': 'dict',
            'options': INCUS_NETWORK_FORWARD_PORT_OPTIONS,
        },
    }
    for spec_key, spec_value in INCUS_COMMON_ARGUMENT_SPEC.items():
        argument_spec[spec_key] = spec_value
    module = incus_create_write_module(argument_spec)
    encoded_network = quote(module.params['network'], safe='')
    resource = f'networks/{encoded_network}/forwards'
    desired = incus_build_desired(module)
    desired['ports'] = _normalize_ports(module.params.get('ports'))
    incus_run_write_module(
        module,
        lambda: incus_ensure_resource(module, resource, desired, IncusResourceOptions(name_key='listen_address')),
    )


if __name__ == '__main__':
    main()
