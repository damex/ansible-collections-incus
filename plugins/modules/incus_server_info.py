#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: Roman Kuzmitskii <ansible@damex.org>
# SPDX-License-Identifier: GPL-3.0-or-later

"""Gather Incus server info."""

from __future__ import annotations

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.damex.incus.plugins.module_utils.incus import (
    INCUS_COMMON_ARGS,
    IncusClientException,
    incus_client_from_module,
)

DOCUMENTATION = r"""
---
module: incus_server_info
short_description: Gather information about the Incus server
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

__all__ = ['DOCUMENTATION', 'EXAMPLES', 'RETURN', 'main']


def main():
    """Run module."""
    argument_spec = {}
    argument_spec.update(INCUS_COMMON_ARGS)
    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=True)
    try:
        client = incus_client_from_module(module)
        response = client.get('/1.0')
        server = response.get('metadata') or {}
    except IncusClientException as e:
        module.fail_json(msg=str(e))
    module.exit_json(server=server)


if __name__ == '__main__':
    main()
