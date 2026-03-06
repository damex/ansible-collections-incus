#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: Roman Kuzmitskii <ansible@damex.org>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

"""Gather Incus server info."""

from __future__ import annotations

DOCUMENTATION = r"""
---
module: incus_server_info
short_description: Gather information about the Incus server
author: Roman Kuzmitskii (@damex) <ansible@damex.org>
description:
  - Gather information about the Incus server via the Incus REST API.
  - Returns server configuration, environment, and API details.
extends_documentation_fragment: [damex.incus.common]
"""

EXAMPLES = r"""
- name: Get server info
  damex.incus.incus_server_info:
    socket_path: /var/lib/incus/unix.socket
  register: result

- name: Get server info from remote server
  damex.incus.incus_server_info:
    url: https://incus.example.com:8443
    client_cert: /etc/incus/client.crt
    client_key: /etc/incus/client.key
  register: result
"""

RETURN = r"""
server:
  description: Server information.
  returned: always
  type: dict
  contains:
    config:
      description: Server configuration including cluster.enabled.
      type: dict
    api_version:
      description: API version supported by the server.
      type: str
    environment:
      description: Server environment details.
      type: dict
    auth:
      description: Authentication state.
      type: str
"""

from ansible_collections.damex.incus.plugins.module_utils.incus import (
    IncusClientException,
    incus_create_client,
    incus_create_info_module,
)

__all__ = ['DOCUMENTATION', 'EXAMPLES', 'RETURN', 'main']


def main() -> None:
    """Run module."""
    module = incus_create_info_module({})
    try:
        client = incus_create_client(module)
        response = client.get('/1.0')
        server = response.get('metadata') or {}
    except IncusClientException as e:
        module.fail_json(msg=str(e))
    module.exit_json(server=server)


if __name__ == '__main__':
    main()
