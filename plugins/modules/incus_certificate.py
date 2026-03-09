#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: Roman Kuzmitskii <ansible@damex.org>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

"""Ensure Incus certificate."""

from __future__ import annotations

DOCUMENTATION = r"""
---
module: incus_certificate
short_description: Ensure Incus certificate
author: Roman Kuzmitskii (@damex) <ansible@damex.org>
description:
  - Add, update, and remove trusted certificates in the Incus trust store via the Incus REST API.
  - Certificates are identified by their friendly name.
  - Cluster-wide resource — not scoped to a project.
extends_documentation_fragment: [damex.incus.common, damex.incus.common.write]
options:
  name:
    description:
      - Friendly name for the certificate in the trust store.
    type: str
    required: true
  state:
    description:
      - Desired state of the certificate.
    type: str
    choices: [present, absent]
    default: present
  certificate:
    description:
      - PEM-encoded client certificate to add.
      - Required when creating a new trust store entry.
      - Ignored on update.
    type: str
  type:
    description:
      - Certificate type.
    type: str
    choices: [client, metrics]
    default: client
  restricted:
    description:
      - Whether the certificate is restricted to specific projects.
    type: bool
    default: false
  projects:
    description:
      - Projects the certificate is restricted to.
      - Only effective when O(restricted=true).
    type: list
    elements: str
    default: []
"""

EXAMPLES = r"""
- name: Ensure client certificate
  damex.incus.incus_certificate:
    name: ansible
    certificate: "{{ lookup('file', '/etc/incus/client.crt') }}"

- name: Ensure restricted certificate
  damex.incus.incus_certificate:
    name: ci-runner
    certificate: "{{ lookup('file', 'ci.crt') }}"
    restricted: true
    projects:
      - default
      - staging

- name: Ensure certificate is absent
  damex.incus.incus_certificate:
    name: old-client
    state: absent
"""

RETURN = r"""
"""

from typing import Any

from ansible_collections.damex.incus.plugins.module_utils.incus import (
    incus_create_client,
    incus_create_write_module,
    incus_run_write_module,
    incus_wait,
)

__all__ = ['DOCUMENTATION', 'EXAMPLES', 'RETURN', 'main']


def _find_cert_or_none(client: Any, name: str) -> dict[str, Any] | None:
    """Find certificate by name, returning None when absent."""
    certs = client.get('/1.0/certificates?recursion=1').get('metadata') or []
    for cert in certs:
        if cert.get('name') == name:
            result: dict[str, Any] = cert
            return result
    return None


def _ensure_certificate(module: Any) -> bool:
    """Ensure certificate state."""
    client = incus_create_client(module)
    name = module.params['name']
    current = _find_cert_or_none(client, name)

    if module.params['state'] == 'present':
        if current is None:
            cert_pem = module.params.get('certificate')
            if not cert_pem:
                module.fail_json(msg="'certificate' is required when adding a new trust store entry")
            if not module.check_mode:
                incus_wait(module, client, client.post('/1.0/certificates', {
                    'name': name,
                    'type': module.params['type'],
                    'certificate': cert_pem,
                    'restricted': module.params['restricted'],
                    'projects': module.params['projects'],
                }))
            return True
        desired_restricted = module.params['restricted']
        desired_projects = sorted(module.params['projects'])
        current_restricted = current.get('restricted', False)
        current_projects = sorted(current.get('projects') or [])
        if current_restricted == desired_restricted and current_projects == desired_projects:
            return False
        if not module.check_mode:
            fingerprint = current['fingerprint']
            incus_wait(module, client, client.put(f'/1.0/certificates/{fingerprint}', {
                'name': name,
                'type': current.get('type', 'client'),
                'restricted': desired_restricted,
                'projects': module.params['projects'],
            }))
        return True

    if current is not None:
        if not module.check_mode:
            fingerprint = current['fingerprint']
            incus_wait(module, client, client.delete(f'/1.0/certificates/{fingerprint}'))
        return True
    return False


def main() -> None:
    """Run module."""
    module = incus_create_write_module({
        'name': {'type': 'str', 'required': True},
        'state': {'type': 'str', 'default': 'present', 'choices': ['present', 'absent']},
        'certificate': {'type': 'str'},
        'type': {'type': 'str', 'default': 'client', 'choices': ['client', 'metrics']},
        'restricted': {'type': 'bool', 'default': False},
        'projects': {'type': 'list', 'elements': 'str', 'default': []},
    })
    incus_run_write_module(module, lambda: _ensure_certificate(module))


if __name__ == '__main__':
    main()
