#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: Roman Kuzmitskii <ansible@damex.org>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

"""
Ensure Incus project information is gathered.
"""

from __future__ import annotations

DOCUMENTATION = r"""
---
module: incus_project_info
short_description: Ensure Incus project information is gathered
author: Roman Kuzmitskii (@damex) <ansible@damex.org>
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
- name: Ensure project information is gathered
  damex.incus.incus_project_info:
    socket_path: /var/lib/incus/unix.socket
  register: result

- name: Ensure specific project information is gathered
  damex.incus.incus_project_info:
    name: default
  register: result

- name: Ensure project information is gathered from remote server
  damex.incus.incus_project_info:
    url: https://incus.example.com:8443
    client_cert_path: /etc/incus/client.crt
    client_key_path: /etc/incus/client.key
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

from ansible_collections.damex.incus.plugins.module_utils.incus import (
    incus_ensure_info,
)

__all__ = ['DOCUMENTATION', 'EXAMPLES', 'RETURN', 'main']


def main() -> None:
    """
    Run module.

    >>> main()
    """
    incus_ensure_info('projects', 'projects')


if __name__ == '__main__':
    main()
