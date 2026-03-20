#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: Roman Kuzmitskii <ansible@damex.org>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

"""
Ensure Incus profile information is gathered.
"""

from __future__ import annotations

DOCUMENTATION = r"""
---
module: incus_profile_info
short_description: Ensure Incus profile information is gathered
author: Roman Kuzmitskii (@damex) <ansible@damex.org>
description:
  - Gather information about Incus profiles via the Incus REST API.
  - Returns information about all profiles or a specific profile.
extends_documentation_fragment: [damex.incus.common, damex.incus.common.project]
options:
  name:
    description:
      - Name of the profile to query.
      - If not specified, all profiles in the project are returned.
    type: str
"""

EXAMPLES = r"""
- name: Ensure profile information is gathered
  damex.incus.incus_profile_info:
    project: default
  register: result

- name: Ensure specific profile information is gathered
  damex.incus.incus_profile_info:
    name: default
    project: default
  register: result

- name: Ensure profile information is gathered from remote server
  damex.incus.incus_profile_info:
    url: https://incus.example.com:8443
    client_cert_path: /etc/incus/client.crt
    client_key_path: /etc/incus/client.key
  register: result
"""

RETURN = r"""
profiles:
  description: List of profile information.
  type: list
  elements: dict
  contains:
    name:
      description: Name of the profile.
      type: str
    description:
      description: Profile description.
      type: str
    config:
      description: Profile configuration.
      type: dict
    devices:
      description: Profile devices.
      type: dict
  returned: always
"""

from ansible_collections.damex.incus.plugins.module_utils.incus import (
    incus_ensure_info,
)

__all__ = ['DOCUMENTATION', 'EXAMPLES', 'RETURN', 'main']


def main() -> None:
    """
    Run module.

    >>> main()
    """
    incus_ensure_info('profiles', 'profiles', project_scoped=True)


if __name__ == '__main__':
    main()
