#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: Roman Kuzmitskii <ansible@damex.org>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

"""Ensure Incus network zone record information is gathered."""

from __future__ import annotations

DOCUMENTATION = r"""
---
module: incus_network_zone_record_info
short_description: Ensure Incus network zone record information is gathered
author: Roman Kuzmitskii (@damex) <ansible@damex.org>
description:
  - Gather information about Incus network zone records via the Incus REST API.
  - Returns information about all records in a zone or a specific record.
  - Network zone records are project-scoped resources within a zone.
extends_documentation_fragment:
  - damex.incus.common
  - damex.incus.common.project
options:
  zone:
    description:
      - Name of the network zone to query records from.
    type: str
    required: true
  name:
    description:
      - Name of the network zone record to query.
      - If not specified, all records in the zone are returned.
    type: str
"""

EXAMPLES = r"""
- name: Ensure network zone record information is gathered
  damex.incus.incus_network_zone_record_info:
    zone: example.com
  register: result

- name: Ensure specific network zone record information is gathered
  damex.incus.incus_network_zone_record_info:
    zone: example.com
    name: web
  register: result

- name: Ensure network zone record information is gathered from project
  damex.incus.incus_network_zone_record_info:
    zone: example.com
    project: myproject
  register: result
"""

RETURN = r"""
network_zone_records:
  description: List of network zone record information.
  type: list
  returned: always
  elements: dict
  contains:
    name:
      description: Name of the record.
      type: str
    description:
      description: Record description.
      type: str
    config:
      description: Record configuration.
      type: dict
    entries:
      description: DNS entries.
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
        'zone': {'type': 'str', 'required': True},
        'name': {'type': 'str'},
        'project': {'type': 'str', 'default': 'default'},
    })
    encoded_zone = quote(module.params['zone'], safe='')
    resource = f'network-zones/{encoded_zone}/records'
    incus_run_info_module(module, resource, 'network_zone_records')


if __name__ == '__main__':
    main()
