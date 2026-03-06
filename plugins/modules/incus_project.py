#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: Roman Kuzmitskii <ansible@damex.org>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

"""Manage Incus projects."""

from __future__ import annotations

DOCUMENTATION = r"""
---
module: incus_project
short_description: Manage Incus projects
author: Roman Kuzmitskii (@damex) <ansible@damex.org>
description:
  - Create, configure, and delete Incus projects via the Incus REST API.
  - Global resource — not scoped to a project.
extends_documentation_fragment: [damex.incus.common, damex.incus.common.write]
options:
  name:
    description:
      - Name of the project.
    type: str
    required: true
  state:
    description:
      - Desired state of the project.
    type: str
    choices: [present, absent]
    default: present
  description:
    description:
      - Description of the project.
    type: str
    default: ''
  config:
    description:
      - Project configuration.
      - All values are sent as strings to the Incus API.
    type: dict
    default: {}
"""

EXAMPLES = r"""
- name: Create project
  damex.incus.incus_project:
    name: myproject
    description: My project
    config:
      features.images: true
      features.networks: false

- name: Remove project
  damex.incus.incus_project:
    name: myproject
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
        'description': {'type': 'str', 'default': ''},
        'config': {'type': 'dict', 'default': {}},
    })
    desired = incus_build_desired(module)
    incus_run_write_module(module, lambda: incus_ensure_resource(module, 'projects', desired))


if __name__ == '__main__':
    main()
