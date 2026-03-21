#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: Roman Kuzmitskii <ansible@damex.org>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

"""
Ensure Incus network zone.
"""

from __future__ import annotations

DOCUMENTATION = r"""
---
module: incus_network_zone
short_description: Ensure Incus network zone
author: Roman Kuzmitskii (@damex) <ansible@damex.org>
description:
  - Create, update, and delete Incus network zones via the Incus REST API.
  - Network zones provide automatic DNS record management for instances
    across Incus networks (bridge and OVN).
extends_documentation_fragment:
  - damex.incus.common
  - damex.incus.common.project
  - damex.incus.common.write
options:
  name:
    description:
      - Name of the network zone.
    type: str
    required: true
  state:
    description:
      - Desired state of the network zone.
    type: str
    choices:
      - present
      - absent
    default: present
  description:
    description:
      - Description of the network zone.
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
"""

EXAMPLES = r"""
- name: Ensure network zone for forward DNS
  damex.incus.incus_network_zone:
    name: example.com
    description: Forward DNS zone

- name: Ensure network zone with user config
  damex.incus.incus_network_zone:
    name: example.com
    config:
      - name: note
        value: Primary zone

- name: Ensure network zone is absent
  damex.incus.incus_network_zone:
    name: example.com
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
    }
    for spec_key, spec_value in INCUS_COMMON_ARGUMENT_SPEC.items():
        argument_spec[spec_key] = spec_value
    module = incus_create_write_module(argument_spec)
    desired: dict[str, Any] = {
        'description': module.params['description'],
        'config': incus_common_flatten_key_value_to_config('user', module.params.get('config')),
    }
    incus_run_write_module(module, lambda: incus_ensure_resource(module, 'network-zones', desired))


if __name__ == '__main__':
    main()
