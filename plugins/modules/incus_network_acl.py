#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: Roman Kuzmitskii <ansible@damex.org>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

"""
Ensure Incus network ACL.
"""

from __future__ import annotations

DOCUMENTATION = r"""
---
module: incus_network_acl
short_description: Ensure Incus network ACL
author: Roman Kuzmitskii (@damex) <ansible@damex.org>
description:
  - Create, update, and delete Incus network ACLs via the Incus REST API.
  - Network ACLs define traffic rules that control access between instances
    connected to the same network, and access to and from other networks.
  - Rules are automatically ordered by action priority (drop, reject, allow-stateless, allow).
extends_documentation_fragment:
  - damex.incus.common
  - damex.incus.common.project
  - damex.incus.common.write
options:
  name:
    description:
      - Name of the network ACL.
    type: str
    required: true
  state:
    description:
      - Desired state of the network ACL.
    type: str
    choices:
      - present
      - absent
    default: present
  description:
    description:
      - Description of the network ACL.
    type: str
    default: ''
  config:
    description:
      - ACL configuration key-value pairs.
      - Only user-defined keys (user.*) are supported.
    type: dict
    default: {}
  ingress:
    description:
      - List of ingress (inbound) traffic rules.
      - Rules are order-independent and automatically sorted by action priority.
    type: list
    elements: dict
    suboptions:
      action:
        description:
          - Action to perform on rule match.
        type: str
        required: true
        choices:
          - allow
          - allow-stateless
          - reject
          - drop
      state:
        description:
          - State of the rule.
        type: str
        choices:
          - enabled
          - disabled
          - logged
        default: enabled
      description:
        description:
          - Description of the rule.
        type: str
      source:
        description:
          - Source address (CIDR, IP range, or selector).
        type: str
      destination:
        description:
          - Destination address (CIDR, IP range, or selector).
        type: str
      protocol:
        description:
          - Network protocol to match.
        type: str
        choices:
          - icmp4
          - icmp6
          - tcp
          - udp
      source_port:
        description:
          - Source port or port range for TCP/UDP.
        type: str
      destination_port:
        description:
          - Destination port or port range for TCP/UDP.
        type: str
      icmp_type:
        description:
          - ICMP type number.
        type: str
      icmp_code:
        description:
          - ICMP code number.
        type: str
  egress:
    description:
      - List of egress (outbound) traffic rules.
      - Rules are order-independent and automatically sorted by action priority.
    type: list
    elements: dict
    suboptions:
      action:
        description:
          - Action to perform on rule match.
        type: str
        required: true
        choices:
          - allow
          - allow-stateless
          - reject
          - drop
      state:
        description:
          - State of the rule.
        type: str
        choices:
          - enabled
          - disabled
          - logged
        default: enabled
      description:
        description:
          - Description of the rule.
        type: str
      source:
        description:
          - Source address (CIDR, IP range, or selector).
        type: str
      destination:
        description:
          - Destination address (CIDR, IP range, or selector).
        type: str
      protocol:
        description:
          - Network protocol to match.
        type: str
        choices:
          - icmp4
          - icmp6
          - tcp
          - udp
      source_port:
        description:
          - Source port or port range for TCP/UDP.
        type: str
      destination_port:
        description:
          - Destination port or port range for TCP/UDP.
        type: str
      icmp_type:
        description:
          - ICMP type number.
        type: str
      icmp_code:
        description:
          - ICMP code number.
        type: str
"""

EXAMPLES = r"""
- name: Ensure network ACL allowing web traffic
  damex.incus.incus_network_acl:
    name: web
    description: Web server ACL
    ingress:
      - action: allow
        source: "@internal"
        protocol: tcp
        destination_port: 80,443
        description: Allow HTTP and HTTPS
    egress:
      - action: allow
        destination: 8.8.8.8/32,8.8.4.4/32
        protocol: udp
        destination_port: "53"
        description: Allow DNS queries to Google DNS

- name: Ensure network ACL blocking all traffic
  damex.incus.incus_network_acl:
    name: deny-all
    ingress:
      - action: drop
    egress:
      - action: drop

- name: Ensure network ACL is absent
  damex.incus.incus_network_acl:
    name: web
    state: absent
"""

RETURN = r"""
"""

from typing import Any

from ansible_collections.damex.incus.plugins.module_utils.incus import (
    INCUS_COMMON_ARGUMENT_SPEC,
    incus_build_desired,
    incus_create_write_module,
    incus_ensure_resource,
    incus_run_write_module,
)

__all__ = ['DOCUMENTATION', 'EXAMPLES', 'RETURN', 'main']

_ACTION_ORDER = {
    'drop': 0,
    'reject': 1,
    'allow-stateless': 2,
    'allow': 3,
}

_RULE_FIELDS = [
    'state',
    'description',
    'source',
    'destination',
    'protocol',
    'source_port',
    'destination_port',
    'icmp_type',
    'icmp_code',
]

INCUS_NETWORK_ACL_RULE_OPTIONS = {
    'action': {
        'type': 'str',
        'required': True,
        'choices': [
            'allow',
            'allow-stateless',
            'reject',
            'drop',
        ],
    },
    'state': {
        'type': 'str',
        'default': 'enabled',
        'choices': [
            'enabled',
            'disabled',
            'logged',
        ],
    },
    'description': {'type': 'str'},
    'source': {'type': 'str'},
    'destination': {'type': 'str'},
    'protocol': {
        'type': 'str',
        'choices': [
            'icmp4',
            'icmp6',
            'tcp',
            'udp',
        ],
    },
    'source_port': {'type': 'str'},
    'destination_port': {'type': 'str'},
    'icmp_type': {'type': 'str'},
    'icmp_code': {'type': 'str'},
}


def _normalize_rules(rules: list[dict[str, Any]] | None) -> list[dict[str, Any]]:
    """
    Normalize rules with defaults and stable sort.

    >>> _normalize_rules([{'action': 'allow', 'protocol': 'tcp'}])
    [{'action': 'allow', 'protocol': 'tcp', 'state': 'enabled'}]
    """
    normalized = []
    for rule in (rules or []):
        entry: dict[str, Any] = {'action': rule['action']}
        for field in _RULE_FIELDS:
            value = rule.get(field) or ('enabled' if field == 'state' else '')
            if value:
                entry[field] = value
        normalized.append(entry)
    normalized.sort(key=lambda r: (
        _ACTION_ORDER.get(r['action'], 99),
        r.get('source', ''),
        r.get('destination', ''),
        r.get('protocol', ''),
        r.get('source_port', ''),
        r.get('destination_port', ''),
    ))
    return normalized


def main() -> None:
    """
    Run module.

    >>> main()
    """
    argument_spec: dict[str, Any] = {
        'project': {'type': 'str', 'default': 'default'},
        'description': {'type': 'str', 'default': ''},
        'config': {'type': 'dict', 'default': {}},
        'ingress': {
            'type': 'list',
            'elements': 'dict',
            'options': INCUS_NETWORK_ACL_RULE_OPTIONS,
        },
        'egress': {
            'type': 'list',
            'elements': 'dict',
            'options': INCUS_NETWORK_ACL_RULE_OPTIONS,
        },
    }
    for spec_key, spec_value in INCUS_COMMON_ARGUMENT_SPEC.items():
        argument_spec[spec_key] = spec_value
    module = incus_create_write_module(argument_spec)
    desired = incus_build_desired(module)
    desired['ingress'] = _normalize_rules(module.params.get('ingress'))
    desired['egress'] = _normalize_rules(module.params.get('egress'))
    incus_run_write_module(module, lambda: incus_ensure_resource(module, 'network-acls', desired))


if __name__ == '__main__':
    main()
