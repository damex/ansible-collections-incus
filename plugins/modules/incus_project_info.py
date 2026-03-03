#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: Roman Kuzmitskii <ansible@damex.org>
# SPDX-License-Identifier: GPL-3.0-or-later

"""Gather Incus project info."""

from __future__ import annotations

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.damex.incus.plugins.module_utils.incus import (
    INCUS_COMMON_ARGS,
    run_info_module,
)

DOCUMENTATION = r"""
---
module: incus_project_info
short_description: Gather information about Incus projects
description:
  - Gather information about Incus projects via the Incus REST API.
  - Returns information about all projects or a specific project.
  - Projects are global resources, not project-scoped.
extends_documentation_fragment: [damex.incus.common]
options:
  name:
    description:
      - Name of the project to query.
      - If not specified, all projects are returned.
    type: str
"""

EXAMPLES = r"""
- name: Get all projects
  damex.incus.incus_project_info:
    socket_path: /var/lib/incus/unix.socket
  register: result

- name: Get specific project
  damex.incus.incus_project_info:
    name: default
  register: result

- name: Get projects from remote server
  damex.incus.incus_project_info:
    url: https://incus.example.com:8443
    client_cert: /etc/incus/client.crt
    client_key: /etc/incus/client.key
  register: result
"""

RETURN = r"""
projects:
  description: List of project information.
  elements: dict
  returned: always
  type: list
  contains:
    name:
      description: Name of the project.
      type: str
    description:
      description: Project description.
      type: str
    config:
      description: Project configuration including enabled features.
      type: dict
"""

__all__ = ['DOCUMENTATION', 'EXAMPLES', 'RETURN', 'main']


def main():
    """Run module."""
    argument_spec = {'name': {'type': 'str'}}
    argument_spec.update(INCUS_COMMON_ARGS)
    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=True)
    run_info_module(module, 'projects', 'projects')


if __name__ == '__main__':
    main()
