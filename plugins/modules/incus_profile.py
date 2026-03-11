#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: Roman Kuzmitskii <ansible@damex.org>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

"""Ensure Incus profile."""

from __future__ import annotations

DOCUMENTATION = r"""
---
module: incus_profile
short_description: Ensure Incus profile
author: Roman Kuzmitskii (@damex) <ansible@damex.org>
description:
  - Create, update, and delete Incus profiles via the Incus REST API.
  - Profiles are project-scoped resources.
extends_documentation_fragment:
  - damex.incus.common
  - damex.incus.common.instance_config
  - damex.incus.common.write
  - damex.incus.common.project
  - damex.incus.devices
options:
  name:
    description:
      - Name of the profile.
    type: str
    required: true
  state:
    description:
      - Desired state of the profile.
    type: str
    choices:
      - present
      - absent
    default: present
  description:
    description:
      - Profile description.
    type: str
    default: ''
"""

EXAMPLES = r"""
- name: Ensure profile
  damex.incus.incus_profile:
    name: base
    description: Base profile
    config:
      limits.cpu: "2"
      limits.memory: 2GiB
    devices:
      - name: root
        type: disk
        path: /
        pool: default
      - name: eth0
        type: nic
        network: incusbr0

- name: Ensure profile is absent
  damex.incus.incus_profile:
    name: base
    state: absent
"""

RETURN = r"""
"""

from ansible_collections.damex.incus.plugins.module_utils.device import (
    INCUS_DEVICE_OPTIONS,
)

from ansible_collections.damex.incus.plugins.module_utils.incus import (
    INCUS_INSTANCE_CONFIG_OPTIONS,
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
        'description': {'type': 'str', 'default': ''},
        'devices': {'type': 'list', 'elements': 'dict', 'default': [], 'options': INCUS_DEVICE_OPTIONS},
        'config': {'type': 'dict', 'default': {}, 'options': INCUS_INSTANCE_CONFIG_OPTIONS},
    }, require_yaml=True)
    desired = incus_build_desired(module)
    incus_run_write_module(module, lambda: incus_ensure_resource(module, 'profiles', desired))


if __name__ == '__main__':
    main()
