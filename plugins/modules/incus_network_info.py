#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: Roman Kuzmitskii <ansible@damex.org>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

"""Ensure Incus network information is gathered."""

from __future__ import annotations

DOCUMENTATION = r"""
---
module: incus_network_info
short_description: Ensure Incus network information is gathered
author: Roman Kuzmitskii (@damex) <ansible@damex.org>
description:
  - Gather information about Incus networks via the Incus REST API.
  - Returns information about all networks or a specific network.
extends_documentation_fragment: [damex.incus.common, damex.incus.common.project]
options:
  name:
    description:
      - Name of the network to query.
      - If not specified, all networks in the project are returned.
    type: str
"""

EXAMPLES = r"""
- name: Ensure network information is gathered
  damex.incus.incus_network_info:
    project: default
  register: result

- name: Ensure specific network information is gathered
  damex.incus.incus_network_info:
    name: incusbr0
    project: default
  register: result

- name: Ensure network information is gathered from remote server
  damex.incus.incus_network_info:
    url: https://incus.example.com:8443
    client_cert: /etc/incus/client.crt
    client_key: /etc/incus/client.key
  register: result
"""

RETURN = r"""
networks:
  description: List of network information.
  elements: dict
  type: list
  contains:
    name:
      description: Name of the network.
      type: str
    description:
      description: Network description.
      type: str
    type:
      description: Network type (bridge, macvlan, etc.).
      type: str
    status:
      description: Status of the network.
      type: str
    config:
      description: Network configuration.
      type: dict
    managed:
      description: Whether the network is managed by Incus.
      type: bool
  returned: always
"""

from ansible_collections.damex.incus.plugins.module_utils.incus import (
    incus_ensure_project_info,
)

__all__ = ['DOCUMENTATION', 'EXAMPLES', 'RETURN', 'main']


def main() -> None:
    """Run module."""
    incus_ensure_project_info('networks', 'networks')


if __name__ == '__main__':
    main()
