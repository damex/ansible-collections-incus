#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: Roman Kuzmitskii <ansible@damex.org>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

"""Ensure Incus network zone record."""

from __future__ import annotations

DOCUMENTATION = r"""
---
module: incus_network_zone_record
short_description: Ensure Incus network zone record
author: Roman Kuzmitskii (@damex) <ansible@damex.org>
description:
  - Create, update, and delete Incus network zone records via the Incus REST API.
  - Network zone records define DNS entries within a network zone.
  - Records are identified by name within a given zone.
extends_documentation_fragment:
  - damex.incus.common
  - damex.incus.common.project
  - damex.incus.common.write
options:
  zone:
    description:
      - Name of the network zone containing the record.
    type: str
    required: true
  name:
    description:
      - Name of the network zone record.
    type: str
    required: true
  state:
    description:
      - Desired state of the network zone record.
    type: str
    choices:
      - present
      - absent
    default: present
  description:
    description:
      - Description of the network zone record.
    type: str
    default: ''
  config:
    description:
      - Network zone record configuration key-value pairs.
      - Only user-defined keys (user.*) are supported.
    type: dict
    default: {}
  entries:
    description:
      - List of DNS entries for the record.
      - Entries are sorted by type and value for stable idempotency.
    type: list
    elements: dict
    suboptions:
      type:
        description:
          - DNS record type (A, AAAA, CNAME, etc.).
        type: str
        required: true
      value:
        description:
          - DNS record value.
        type: str
        required: true
      ttl:
        description:
          - Time to live in seconds.
        type: int
"""

EXAMPLES = r"""
- name: Ensure network zone record with A entry
  damex.incus.incus_network_zone_record:
    zone: example.com
    name: web
    entries:
      - type: A
        value: 10.0.0.5

- name: Ensure network zone record with multiple entries
  damex.incus.incus_network_zone_record:
    zone: example.com
    name: mail
    description: Mail server records
    entries:
      - type: A
        value: 10.0.0.10
      - type: AAAA
        value: fd42::10
        ttl: 300

- name: Ensure network zone record is absent
  damex.incus.incus_network_zone_record:
    zone: example.com
    name: web
    state: absent
"""

RETURN = r"""
"""

from typing import Any
from urllib.parse import quote

from ansible_collections.damex.incus.plugins.module_utils.incus import (
    INCUS_COMMON_ARGUMENT_SPEC,
    incus_build_desired,
    incus_create_write_module,
    incus_ensure_resource,
    incus_run_write_module,
)

__all__ = ['DOCUMENTATION', 'EXAMPLES', 'RETURN', 'main']

INCUS_NETWORK_ZONE_RECORD_ENTRY_OPTIONS = {
    'type': {
        'type': 'str',
        'required': True,
    },
    'value': {
        'type': 'str',
        'required': True,
    },
    'ttl': {'type': 'int'},
}


def _normalize_entries(entries: list[dict[str, Any]] | None) -> list[dict[str, Any]]:
    """Normalize entries with defaults and stable sort."""
    normalized = []
    for entry in (entries or []):
        normalized.append({
            'type': entry['type'],
            'value': entry['value'],
            'ttl': entry.get('ttl') or 0,
        })
    normalized.sort(key=lambda e: (e['type'], e['value']))
    return normalized


def main() -> None:
    """Run module."""
    module = incus_create_write_module({
        **INCUS_COMMON_ARGUMENT_SPEC,
        'zone': {'type': 'str', 'required': True},
        'project': {'type': 'str', 'default': 'default'},
        'description': {'type': 'str', 'default': ''},
        'config': {'type': 'dict', 'default': {}},
        'entries': {
            'type': 'list',
            'elements': 'dict',
            'options': INCUS_NETWORK_ZONE_RECORD_ENTRY_OPTIONS,
        },
    })
    encoded_zone = quote(module.params['zone'], safe='')
    resource = f'network-zones/{encoded_zone}/records'
    desired = incus_build_desired(module)
    desired['entries'] = _normalize_entries(module.params.get('entries'))
    incus_run_write_module(module, lambda: incus_ensure_resource(module, resource, desired))


if __name__ == '__main__':
    main()
