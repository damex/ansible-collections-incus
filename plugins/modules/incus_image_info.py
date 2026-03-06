#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: Roman Kuzmitskii <ansible@damex.org>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

"""Gather Incus image info."""

from __future__ import annotations

DOCUMENTATION = r"""
---
module: incus_image_info
short_description: Gather information about Incus images
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
- name: Get all images
  damex.incus.incus_image_info:
    project: default
  register: result

- name: Get specific image by alias
  damex.incus.incus_image_info:
    name: debian/13
    project: default
  register: result

- name: Get images from remote server
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

from ansible_collections.damex.incus.plugins.module_utils.incus import (
    IncusClientException,
    IncusNotFoundException,
    incus_create_client,
    incus_create_info_module,
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
    result: list[Any] = []

    try:
        client = incus_create_client(module)
        if name:
            try:
                alias_meta = client.get(f'/1.0/images/aliases/{name}?project={project}').get('metadata') or {}
                fingerprint = alias_meta.get('target')
                if fingerprint:
                    image = client.get(f'/1.0/images/{fingerprint}?project={project}').get('metadata')
                    result = [image] if image else []
            except IncusNotFoundException:
                result = []
        else:
            response = client.get(f'/1.0/images?project={project}&recursion=1')
            result = response.get('metadata') or []
    except IncusClientException as exc:
        module.fail_json(msg=str(exc))

    module.exit_json(images=result)


if __name__ == '__main__':
    main()
