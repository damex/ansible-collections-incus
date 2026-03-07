#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: Roman Kuzmitskii <ansible@damex.org>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

"""Ensure Incus networks."""

from __future__ import annotations

DOCUMENTATION = r"""
---
module: incus_network
short_description: Ensure Incus networks
author: Roman Kuzmitskii (@damex) <ansible@damex.org>
description:
  - Create, update, and delete Incus networks via the Incus REST API.
  - Networks are project-scoped resources.
  - The network type is set on creation and cannot be changed afterwards.
extends_documentation_fragment: [damex.incus.common, damex.incus.common.project, damex.incus.common.write]
options:
  name:
    description:
      - Name of the network.
    type: str
    required: true
  state:
    description:
      - Desired state of the network.
    type: str
    choices: [present, absent]
    default: present
  type:
    description:
      - Network type.
      - Required when creating a new network.
      - Ignored on update — type cannot be changed after creation.
    type: str
    choices:
      - bridge
      - macvlan
      - ovn
      - physical
      - sriov
  description:
    description:
      - Network description.
    type: str
    default: ''
  config:
    description:
      - Network configuration key-value pairs.
      - Boolean values are converted to lowercase strings.
    type: dict
    default: {}
"""

EXAMPLES = r"""
- name: Create bridge network
  damex.incus.incus_network:
    name: incusbr0
    type: bridge
    config:
      ipv4.address: 10.0.0.1/24
      ipv4.nat: true

- name: Remove network
  damex.incus.incus_network:
    name: incusbr0
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
    """Run module."""
    module = incus_create_write_module({
        **INCUS_COMMON_ARGUMENT_SPEC,
        'project': {'type': 'str', 'default': 'default'},
        'type': {'type': 'str', 'choices': ['bridge', 'macvlan', 'ovn', 'physical', 'sriov']},
        'config': {'type': 'dict', 'default': {}},
        'description': {'type': 'str', 'default': ''},
    })
    desired = incus_build_desired(module)
    incus_run_write_module(module, lambda: incus_ensure_resource(module, 'networks', desired, ['type']))


if __name__ == '__main__':
    main()
