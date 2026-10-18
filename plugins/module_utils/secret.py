# Copyright: Roman Kuzmitskii <ansible@damex.org>
# SPDX-License-Identifier: GPL-3.0-or-later

"""
Incus config secret discovery and registration.
"""

from __future__ import annotations

import re
from typing import Any

try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False

from ansible.module_utils.secrets import register_secrets

from ansible_collections.damex.incus.plugins.module_utils.cloud_init import CLOUD_INIT_USER_KEYS
from ansible_collections.damex.incus.plugins.module_utils.common import incus_common_stringify_value

__all__ = [
    'incus_secret_collect_config',
    'incus_secret_register_config',
]


def _incus_secret_collect_values(data: Any, options: dict[str, Any]) -> set[str]:
    """
    Collect no_log values by spec.

    >>> sorted(_incus_secret_collect_values(
    ...     {'users': [{'name': 'admin', 'passwd': 'hash'}]},
    ...     {'users': {'type': 'list', 'options': {'passwd': {'type': 'str', 'no_log': True}}}},
    ... ))
    ['hash']
    """
    secrets: set[str] = set()
    if not isinstance(data, dict):
        return secrets
    for option_key, option_spec in options.items():
        option_value = data.get(option_key)
        if option_value is None:
            continue
        if option_spec.get('no_log') is True:
            secrets.add(incus_common_stringify_value(option_value))
            continue
        suboptions = option_spec.get('options')
        if suboptions is None:
            continue
        items = option_value if isinstance(option_value, list) else [option_value]
        for item in items:
            secrets = secrets.union(_incus_secret_collect_values(
                item,
                suboptions,
            ))
    return secrets


def _incus_secret_collect_cloud_init(config_value: str, options: dict[str, Any]) -> set[str]:
    """
    Collect no_log values from cloud-init.

    >>> sorted(_incus_secret_collect_cloud_init(
    ...     '#cloud-config\\npassword: pass\\n',
    ...     {'password': {'type': 'str', 'no_log': True}},
    ... ))
    ['#cloud-config\\npassword: pass\\n', 'pass']
    """
    if not HAS_YAML:
        return {config_value}
    try:
        data = yaml.safe_load(config_value)
    except yaml.YAMLError:
        return {config_value}
    secrets = _incus_secret_collect_values(data, options)
    if secrets:
        secrets.add(config_value)
    return secrets


def _incus_secret_collect_list(
    config: dict[str, str],
    list_prefix: str,
    element_options: dict[str, Any],
) -> set[str]:
    """
    Collect no_log values from flattened lists.

    >>> sorted(_incus_secret_collect_list(
    ...     {'bgp.peers.router.password': 'pass', 'bgp.peers.router.asn': '64601'},
    ...     'bgp.peers',
    ...     {'password': {'type': 'str', 'no_log': True}, 'asn': {'type': 'int'}},
    ... ))
    ['pass']
    """
    secrets: set[str] = set()
    key_pattern = re.compile(rf'{re.escape(list_prefix)}\.[^.]+\.(?P<field>.+)')
    for config_key, config_value in config.items():
        key_match = key_pattern.fullmatch(config_key)
        if key_match is None:
            continue
        field_spec = element_options.get(key_match.group('field'))
        if field_spec is not None and field_spec.get('no_log') is True:
            secrets.add(config_value)
    return secrets


def incus_secret_collect_config(
    config: dict[str, str],
    config_options: dict[str, Any],
    config_lists: dict[str, str] | None = None,
) -> set[str]:
    """
    Collect no_log values from config.

    >>> sorted(incus_secret_collect_config(
    ...     {'loki.auth.password': 'pass', 'loki.api.url': 'http://loki'},
    ...     {'loki.auth.password': {'type': 'str', 'no_log': True}, 'loki.api.url': {'type': 'str'}},
    ... ))
    ['pass']
    """
    secrets: set[str] = set()
    for config_key, config_value in config.items():
        option_spec = config_options.get(config_key)
        if option_spec is None:
            continue
        if option_spec.get('no_log') is True:
            secrets.add(config_value)
        elif config_key in CLOUD_INIT_USER_KEYS:
            secrets = secrets.union(_incus_secret_collect_cloud_init(
                config_value,
                option_spec.get('options', {}),
            ))
    if config_lists is not None:
        for list_key, list_prefix in config_lists.items():
            secrets = secrets.union(_incus_secret_collect_list(
                config,
                list_prefix,
                config_options.get(list_key, {}).get('options', {}),
            ))
    return secrets


def incus_secret_register_config(
    config: dict[str, str],
    config_options: dict[str, Any],
    config_lists: dict[str, str] | None = None,
) -> None:
    """
    Register no_log values from config.

    >>> incus_secret_register_config(
    ...     {'loki.auth.password': 'pass'},
    ...     {'loki.auth.password': {'type': 'str', 'no_log': True}},
    ... )
    """
    register_secrets(incus_secret_collect_config(
        config,
        config_options,
        config_lists,
    ))
