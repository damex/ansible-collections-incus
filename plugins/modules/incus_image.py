#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: Roman Kuzmitskii <ansible@damex.org>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

"""Ensure Incus images."""

from __future__ import annotations

DOCUMENTATION = r"""
---
module: incus_image
short_description: Ensure Incus images
author: Roman Kuzmitskii (@damex) <ansible@damex.org>
description:
  - Copy and delete Incus images via the Incus REST API.
  - Images are project-scoped resources identified by alias.
  - Copying from remote servers uses the C(remote:alias) format (e.g. C(images:debian/13)).
extends_documentation_fragment:
  - damex.incus.common
  - damex.incus.common.source
  - damex.incus.common.project
  - damex.incus.common.write
options:
  alias:
    description:
      - Alias for the image on the local server.
      - Used to check existence and as the alias assigned on copy.
    type: str
    required: true
  type:
    description:
      - Image type to request from the remote server.
    type: str
    choices: [container, virtual-machine]
    default: container
  state:
    description:
      - Desired state of the image.
    type: str
    choices: [present, absent]
    default: present
  copy_aliases:
    description:
      - Copy all aliases from the source image.
    type: bool
    default: false
  auto_update:
    description:
      - Automatically update the image when a new build is available on the source server.
    type: bool
    default: false
  public:
    description:
      - Make the image available to unauthenticated users.
    type: bool
    default: false
"""

EXAMPLES = r"""
- name: Copy Debian 13 container image
  damex.incus.incus_image:
    alias: debian/13
    source: images:debian/13

- name: Copy Ubuntu 24.04 VM image
  damex.incus.incus_image:
    alias: ubuntu/24.04
    source: images:ubuntu/24.04
    type: virtual-machine

- name: Copy image with auto-update
  damex.incus.incus_image:
    alias: debian/13
    source: images:debian/13
    auto_update: true

- name: Delete an image
  damex.incus.incus_image:
    alias: debian/13
    state: absent
"""

RETURN = r"""
"""

from typing import Any

from ansible_collections.damex.incus.plugins.module_utils.incus import (
    INCUS_SOURCE_ARGS,
    IncusNotFoundException,
    incus_build_source,
    incus_create_client,
    incus_create_write_module,
    incus_run_write_module,
    incus_wait,
)

__all__ = ['DOCUMENTATION', 'EXAMPLES', 'RETURN', 'main']


def main() -> None:
    """Run module."""
    module = incus_create_write_module({
        'alias': {'type': 'str', 'required': True},
        'state': {'type': 'str', 'default': 'present', 'choices': ['present', 'absent']},
        'project': {'type': 'str', 'default': 'default'},
        **INCUS_SOURCE_ARGS,
        'type': {'type': 'str', 'default': 'container', 'choices': ['container', 'virtual-machine']},
        'copy_aliases': {'type': 'bool', 'default': False},
        'auto_update': {'type': 'bool', 'default': False},
        'public': {'type': 'bool', 'default': False},
    })

    def _ensure_image() -> bool:
        client = incus_create_client(module)
        alias = module.params['alias']
        project = module.params['project']
        query = f'?project={project}'

        if module.params['state'] == 'present':
            try:
                client.get(f'/1.0/images/aliases/{alias}{query}')
                return False
            except IncusNotFoundException:
                pass
            if not module.params['source']:
                module.fail_json(msg="'source' is required when creating an image")
            source = incus_build_source(module)
            source['image_type'] = module.params['type']
            if module.params['copy_aliases']:
                source['copy_aliases'] = True
            data: dict[str, Any] = {
                'source': source,
                'aliases': [{'name': alias}],
                'auto_update': module.params['auto_update'],
                'public': module.params['public'],
            }
            if not module.check_mode:
                incus_wait(module, client, client.post(f'/1.0/images{query}', data))
            return True

        try:
            meta = client.get(f'/1.0/images/aliases/{alias}{query}').get('metadata') or {}
            fingerprint = meta.get('target')
        except IncusNotFoundException:
            return False
        if fingerprint and not module.check_mode:
            incus_wait(module, client, client.delete(f'/1.0/images/{fingerprint}{query}'))
        return bool(fingerprint)

    incus_run_write_module(module, _ensure_image)


if __name__ == '__main__':
    main()
