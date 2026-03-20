# -*- coding: utf-8 -*-
# Copyright: Roman Kuzmitskii <ansible@damex.org>
# SPDX-License-Identifier: GPL-3.0-or-later

"""
Incus source and query helpers.
"""

from __future__ import annotations

from typing import Any
from urllib.parse import quote

from ansible.module_utils.basic import AnsibleModule

__all__ = [
    'INCUS_KNOWN_REMOTES',
    'INCUS_SOURCE_ARGS',
    'incus_build_query',
    'incus_build_source',
]

INCUS_KNOWN_REMOTES = {
    'images': ('https://images.linuxcontainers.org', 'simplestreams'),
    'ubuntu': ('https://cloud-images.ubuntu.com/releases', 'simplestreams'),
    'ubuntu-daily': ('https://cloud-images.ubuntu.com/daily', 'simplestreams'),
    'docker': ('https://docker.io', 'oci'),
}

INCUS_SOURCE_ARGS = {
    'source': {'type': 'str'},
    'source_server': {'type': 'str'},
    'source_protocol': {
        'type': 'str',
        'default': 'simplestreams',
        'choices': [
            'simplestreams',
            'incus',
            'oci',
        ],
    },
}


def incus_build_query(
    project: str | None = None,
    target: str | None = None,
    recursion: int | None = None,
) -> str:
    """
    Build query string.

    >>> incus_build_query(
    ...     project='myproject',
    ...     recursion=1,
    ... )
    '?project=myproject&recursion=1'
    >>> incus_build_query()
    ''
    """
    params = []
    if project:
        params.append(f'project={quote(project, safe="")}')
    if target:
        params.append(f'target={quote(target, safe="")}')
    if recursion is not None:
        params.append(f'recursion={recursion}')
    return f'?{"&".join(params)}' if params else ''


def incus_build_source(module: AnsibleModule) -> dict[str, Any]:
    """
    Build image source.

    >>> incus_build_source(module)
    {'type': 'image', 'alias': 'debian/13', 'server': 'https://images.linuxcontainers.org', 'protocol': 'simplestreams'}
    """
    raw = module.params['source']
    server = module.params.get('source_server')
    protocol = module.params.get('source_protocol') or 'simplestreams'

    alias = raw
    if ':' in raw and not server:
        remote, alias = raw.split(':', 1)
        if remote not in INCUS_KNOWN_REMOTES:
            module.fail_json(msg=f"Unknown remote '{remote}'. Set source_server explicitly.")
        server, protocol = INCUS_KNOWN_REMOTES[remote]

    source = {'type': 'image', 'alias': alias}
    if server:
        source['server'] = server
        source['protocol'] = protocol
    return source
