#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: Roman Kuzmitskii <ansible@damex.org>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

"""Ensure Incus certificate information is gathered."""

from __future__ import annotations

DOCUMENTATION = r"""
---
module: incus_certificate_info
short_description: Ensure Incus certificate information is gathered
author: Roman Kuzmitskii (@damex) <ansible@damex.org>
description:
  - Gather information about trusted certificates in the Incus trust store via the Incus REST API.
  - Returns information about all certificates or a specific certificate by name.
  - Certificates are global resources, not project-scoped.
extends_documentation_fragment: [damex.incus.common]
options:
  name:
    description:
      - Friendly name of the certificate to query.
      - If not specified, all certificates are returned.
    type: str
"""

EXAMPLES = r"""
- name: Ensure certificate information is gathered
  damex.incus.incus_certificate_info:
    socket_path: /var/lib/incus/unix.socket
  register: result

- name: Ensure specific certificate information is gathered
  damex.incus.incus_certificate_info:
    name: ansible
  register: result

- name: Ensure certificate information is gathered from remote server
  damex.incus.incus_certificate_info:
    url: https://incus.example.com:8443
    client_cert: /etc/incus/client.crt
    client_key: /etc/incus/client.key
  register: result
"""

RETURN = r"""
certificates:
  description: List of certificate information.
  type: list
  elements: dict
  returned: always
  contains:
    fingerprint:
      description: SHA-256 fingerprint of the certificate.
      type: str
    name:
      description: Friendly name of the certificate.
      type: str
    type:
      description: Certificate type.
      type: str
    restricted:
      description: Whether the certificate is restricted to specific projects.
      type: bool
    projects:
      description: Projects the certificate is restricted to.
      type: list
      elements: str
"""

from typing import Any

from ansible_collections.damex.incus.plugins.module_utils.incus import (
    IncusClientException,
    IncusNotFoundException,
    incus_create_client,
    incus_create_info_module,
)

__all__ = ['DOCUMENTATION', 'EXAMPLES', 'RETURN', 'main']


def main() -> None:
    """Run module."""
    module = incus_create_info_module({'name': {'type': 'str'}})
    name = module.params.get('name')
    result: list[dict[str, Any]] = []

    try:
        client = incus_create_client(module)

        if name:
            certs = client.get('/1.0/certificates?recursion=1').get('metadata') or []
            result = [c for c in certs if c.get('name') == name]
        else:
            result = client.get('/1.0/certificates?recursion=1').get('metadata') or []

    except IncusNotFoundException:
        result = []
    except IncusClientException as e:
        module.fail_json(msg=str(e))
        return

    module.exit_json(certificates=result)


if __name__ == '__main__':
    main()
