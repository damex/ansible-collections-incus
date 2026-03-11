#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: Roman Kuzmitskii <ansible@damex.org>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

"""Ensure Incus image information is gathered."""

from __future__ import annotations

DOCUMENTATION = r"""
---
module: incus_image_info
short_description: Ensure Incus image information is gathered
author: Roman Kuzmitskii (@damex) <ansible@damex.org>
description:
  - Gather information about Incus images via the Incus REST API.
  - Returns information about all images or a specific image by alias.
  - Images are project-scoped resources.
extends_documentation_fragment: [damex.incus.common, damex.incus.common.project]
options:
  name:
    description:
      - Alias of the image to query.
      - If not specified, all images in the project are returned.
    type: str
"""

EXAMPLES = r"""
- name: Ensure image information is gathered
  damex.incus.incus_image_info:
    project: default
  register: result

- name: Ensure specific image information is gathered
  damex.incus.incus_image_info:
    name: debian/13
    project: default
  register: result

- name: Ensure image information is gathered from remote server
  damex.incus.incus_image_info:
    url: https://incus.example.com:8443
    client_cert: /etc/incus/client.crt
    client_key: /etc/incus/client.key
  register: result
"""

RETURN = r"""
images:
  description: List of image information.
  returned: always
  type: list
  elements: dict
  contains:
    fingerprint:
      description: SHA-256 fingerprint of the image.
      type: str
    type:
      description: Image type (container or virtual-machine).
      type: str
    architecture:
      description: Image architecture.
      type: str
    public:
      description: Whether the image is publicly available.
      type: bool
    aliases:
      description: List of aliases for the image.
      type: list
      elements: dict
    properties:
      description: Image metadata properties.
      type: dict
    auto_update:
      description: Whether auto-update is enabled.
      type: bool
    size:
      description: Image size in bytes.
      type: int
"""

from typing import Any
from urllib.parse import quote

from ansible_collections.damex.incus.plugins.module_utils.incus import (
    IncusClientException,
    incus_build_query,
    incus_create_client,
    incus_create_info_module,
    incus_resolve_image_alias,
)

__all__ = ['DOCUMENTATION', 'EXAMPLES', 'RETURN', 'main']


def main() -> None:
    """Run module."""
    module = incus_create_info_module({
        'name': {'type': 'str'},
        'project': {'type': 'str', 'default': 'default'},
    })
    name = module.params.get('name')
    project = module.params['project']
    query = incus_build_query(project=project)
    result: list[Any] = []

    try:
        client = incus_create_client(module)
        if name:
            fingerprint = incus_resolve_image_alias(client, name, query)
            if fingerprint:
                encoded_fingerprint = quote(fingerprint, safe='')
                image = client.get(f'/1.0/images/{encoded_fingerprint}{query}').get('metadata')
                result = [image] if image else []
        else:
            list_query = incus_build_query(project=project, recursion=1)
            response = client.get(f'/1.0/images{list_query}')
            result = response.get('metadata') or []
    except IncusClientException as exc:
        module.fail_json(msg=str(exc))

    module.exit_json(images=result)


if __name__ == '__main__':
    main()
