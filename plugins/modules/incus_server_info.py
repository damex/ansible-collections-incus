#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: Roman Kuzmitskii <ansible@damex.org>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

"""
Ensure Incus server information is gathered.
"""

from __future__ import annotations

DOCUMENTATION = r"""
---
module: incus_server_info
short_description: Ensure Incus server information is gathered
author: Roman Kuzmitskii (@damex) <ansible@damex.org>
description:
  - Gather information about the Incus server via the Incus REST API.
  - Returns server configuration, environment, and API details.
extends_documentation_fragment: [damex.incus.common]
"""

EXAMPLES = r"""
- name: Ensure server information is gathered
  damex.incus.incus_server_info:
    socket_path: /var/lib/incus/unix.socket
  register: result

- name: Ensure server information is gathered from remote server
  damex.incus.incus_server_info:
    url: https://incus.example.com:8443
    client_cert_path: /etc/incus/client.crt
    client_key_path: /etc/incus/client.key
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

from ansible_collections.damex.incus.plugins.module_utils.incus_client import (
    IncusClientException,
    incus_create_client,
)
from ansible_collections.damex.incus.plugins.module_utils.incus import (
    incus_create_info_module,
)

__all__ = ['DOCUMENTATION', 'EXAMPLES', 'RETURN', 'main']


def main() -> None:
    """
    Run module.

    >>> main()
    """
    module = incus_create_info_module({})
    try:
        with incus_create_client(module) as client:
            response = client.get('/1.0')
            server = response.get('metadata') or {}
    except IncusClientException as e:
        module.fail_json(msg=str(e))
        return
    module.exit_json(server=server)


if __name__ == '__main__':
    main()
