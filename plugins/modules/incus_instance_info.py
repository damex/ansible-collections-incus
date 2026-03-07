#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: Roman Kuzmitskii <ansible@damex.org>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

"""Ensure Incus instance info is gathered."""

from __future__ import annotations

DOCUMENTATION = r"""
---
module: incus_instance_info
short_description: Ensure Incus instance information is gathered
author: Roman Kuzmitskii (@damex) <ansible@damex.org>
description:
  - Gather information about Incus instances via the Incus REST API.
  - Returns information about all instances or a specific instance.
extends_documentation_fragment: [damex.incus.common, damex.incus.common.project]
options:
  name:
    description:
      - Name of the instance to query.
      - If not specified, all instances in the project are returned.
    type: str
"""

EXAMPLES = r"""
- name: Get all instances
  damex.incus.incus_instance_info:
    project: default
  register: result

- name: Get specific instance
  damex.incus.incus_instance_info:
    name: myinstance
    project: default
  register: result

- name: Get instances from remote server
  damex.incus.incus_instance_info:
    url: https://incus.example.com:8443
    client_cert: /etc/incus/client.crt
    client_key: /etc/incus/client.key
  register: result
"""

RETURN = r"""
instances:
  description: List of instance information.
  returned: always
  type: list
  elements: dict
  contains:
    name:
      description: Name of the instance.
      type: str
    status:
      description: Status of the instance.
      type: str
    type:
      description: Type of the instance (container or virtual-machine).
      type: str
    project:
      description: Project the instance belongs to.
      type: str
    config:
      description: Instance configuration.
      type: dict
    devices:
      description: Instance devices.
      type: dict
    profiles:
      description: Profiles applied to the instance.
      type: list
      elements: str
"""

from ansible_collections.damex.incus.plugins.module_utils.incus import (
    incus_ensure_project_info,
)

__all__ = ['DOCUMENTATION', 'EXAMPLES', 'RETURN', 'main']


def main() -> None:
    """Run module."""
    incus_ensure_project_info('instances', 'instances')


if __name__ == '__main__':
    main()
