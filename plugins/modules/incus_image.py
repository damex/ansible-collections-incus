#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: Roman Kuzmitskii <ansible@damex.org>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

"""Ensure Incus image."""

from __future__ import annotations

DOCUMENTATION = r"""
---
module: incus_image
short_description: Ensure Incus image
author: Roman Kuzmitskii (@damex) <ansible@damex.org>
description:
  - Copy, update, and delete Incus images via the Incus REST API.
  - Images are project-scoped resources identified by alias.
  - Copying from remote servers uses the C(remote:alias) format (e.g. C(images:debian/13)).
  - Supports OCI registries such as Docker Hub using the C(docker:image) format.
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
- name: Ensure Debian 13 container image
  damex.incus.incus_image:
    alias: debian/13
    source: images:debian/13

- name: Ensure Ubuntu 24.04 VM image
  damex.incus.incus_image:
    alias: ubuntu/24.04
    source: images:ubuntu/24.04
    type: virtual-machine

- name: Ensure image with auto-update
  damex.incus.incus_image:
    alias: debian/13
    source: images:debian/13
    auto_update: true

- name: Ensure image is public
  damex.incus.incus_image:
    alias: debian/13
    source: images:debian/13
    public: true

- name: Ensure nginx OCI image from Docker Hub
  damex.incus.incus_image:
    alias: nginx
    source: docker:library/nginx

- name: Ensure image from custom OCI registry
  damex.incus.incus_image:
    alias: myapp
    source: myapp/backend
    source_server: https://ghcr.io
    source_protocol: oci

- name: Ensure image is absent
  damex.incus.incus_image:
    alias: debian/13
    state: absent
"""

RETURN = r"""
"""

from typing import Any
from urllib.parse import quote

from ansible_collections.damex.incus.plugins.module_utils.incus import (
    INCUS_SOURCE_ARGS,
    IncusClient,
    incus_build_query,
    incus_build_source,
    incus_create_client,
    incus_resolve_image_alias,
    incus_create_write_module,
    incus_run_write_module,
    incus_wait,
)

__all__ = ['DOCUMENTATION', 'EXAMPLES', 'RETURN', 'main']


def _update_image(
    module: Any, client: IncusClient, encoded_fingerprint: str, query: str,
) -> bool:
    """Update image properties if they differ from desired state."""
    image = client.get(f'/1.0/images/{encoded_fingerprint}{query}').get('metadata') or {}
    desired_auto_update = module.params['auto_update']
    desired_public = module.params['public']
    if image.get('auto_update', False) == desired_auto_update and image.get('public', False) == desired_public:
        return False
    if not module.check_mode:
        incus_wait(module, client, client.put(f'/1.0/images/{encoded_fingerprint}{query}', {
            'auto_update': desired_auto_update,
            'public': desired_public,
            'properties': image.get('properties') or {},
            'expires_at': image.get('expires_at', ''),
        }))
    return True


def main() -> None:
    """Run module."""
    argument_spec: dict[str, Any] = {
        'alias': {'type': 'str', 'required': True},
        'state': {
            'type': 'str',
            'default': 'present',
            'choices': [
                'present',
                'absent',
            ],
        },
        'project': {'type': 'str', 'default': 'default'},
        'type': {
            'type': 'str',
            'default': 'container',
            'choices': [
                'container',
                'virtual-machine',
            ],
        },
        'copy_aliases': {'type': 'bool', 'default': False},
        'auto_update': {'type': 'bool', 'default': False},
        'public': {'type': 'bool', 'default': False},
    }
    for spec_key, spec_value in INCUS_SOURCE_ARGS.items():
        argument_spec[spec_key] = spec_value
    module = incus_create_write_module(argument_spec)

    def _ensure_image() -> bool:
        client = incus_create_client(module)
        alias = module.params['alias']
        project = module.params['project']
        query = incus_build_query(project=project)

        if module.params['state'] == 'present':
            fingerprint = incus_resolve_image_alias(client, alias, query)
            if fingerprint:
                encoded_fingerprint = quote(fingerprint, safe='')
                return _update_image(module, client, encoded_fingerprint, query)
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

        fingerprint = incus_resolve_image_alias(client, alias, query)
        if not fingerprint:
            return False
        if not module.check_mode:
            encoded_fingerprint = quote(fingerprint, safe='')
            incus_wait(module, client, client.delete(f'/1.0/images/{encoded_fingerprint}{query}'))
        return True

    incus_run_write_module(module, _ensure_image)


if __name__ == '__main__':
    main()
