# Copyright: Roman Kuzmitskii <ansible@damex.org>
# SPDX-License-Identifier: GPL-3.0-or-later

"""
Incus config secret discovery and registration.
"""

from __future__ import annotations

import collections.abc
import itertools
from typing import Any

try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False

from ansible.module_utils.secrets import register_secrets

from ansible_collections.damex.incus.plugins.module_utils.cloud_init import CLOUD_INIT_USER_KEYS

__all__ = [
    'incus_secret_collect_config',
    'incus_secret_register_configs',
]


def _incus_secret_collect_list(
    config: dict[str, str],
    list_prefix: str,
    element_options: dict[str, Any],
) -> set[str]:
    """
    Collect no_log values from flattened list.

    >>> sorted(_incus_secret_collect_list(
    ...     {'bgp.peers.edge.router.password': 'pass', 'bgp.peers.edge.router.asn': '64601'},
    ...     'bgp.peers',
    ...     {'password': {'type': 'str', 'no_log': True}, 'asn': {'type': 'int'}},
    ... ))
    ['pass']
    """
    no_log_suffixes = tuple(
        f'.{field_key}'
        for field_key, field_spec in element_options.items()
        if field_spec.get('no_log') is True
    )
    return {
        config_value
        for config_key, config_value in config.items()
        if config_key.startswith(f'{list_prefix}.') and config_key.endswith(no_log_suffixes)
    }


def _incus_secret_collect_node(node: yaml.Node, document: str) -> set[str]:
    """
    Collect node value and rendered text.

    >>> document = "'it''s'"
    >>> sorted(_incus_secret_collect_node(yaml.compose(document, Loader=yaml.SafeLoader), document))
    ["'it''s'", "it's"]
    """
    rendered = ''.join(itertools.islice(
        document,
        node.start_mark.index,
        node.end_mark.index,
    ))
    if isinstance(node, yaml.ScalarNode):
        return {node.value, rendered}
    return {rendered}


def _incus_secret_collect_nodes(
    node: yaml.Node | None,
    options: dict[str, Any],
    document: str,
) -> set[str]:
    """
    Collect no_log node values by spec.

    >>> document = 'users:\\n- name: admin\\n  passwd: hash\\n'
    >>> sorted(_incus_secret_collect_nodes(
    ...     yaml.compose(document, Loader=yaml.SafeLoader),
    ...     {'users': {'type': 'list', 'options': {'passwd': {'type': 'str', 'no_log': True}}}},
    ...     document,
    ... ))
    ['hash']
    """
    secrets: set[str] = set()
    if not isinstance(node, yaml.MappingNode):
        return secrets
    for key_node, value_node in node.value:
        if not isinstance(key_node, yaml.ScalarNode):
            continue
        option_spec = options.get(key_node.value)
        if option_spec is None:
            continue
        if option_spec.get('no_log') is True:
            secrets = secrets.union(_incus_secret_collect_node(value_node, document))
            continue
        suboptions = option_spec.get('options')
        if suboptions is None:
            continue
        items = value_node.value if isinstance(value_node, yaml.SequenceNode) else [value_node]
        for item in items:
            secrets = secrets.union(_incus_secret_collect_nodes(
                item,
                suboptions,
                document,
            ))
    return secrets


def _incus_secret_collect_cloud_init(config_value: str, options: dict[str, Any]) -> set[str]:
    """
    Collect no_log values from cloud-init.

    >>> sorted(_incus_secret_collect_cloud_init(
    ...     '#cloud-config\\npassword: pass\\n',
    ...     {'password': {'type': 'str', 'no_log': True}},
    ... ))
    ['pass']
    """
    if not HAS_YAML:
        return {config_value}
    try:
        node = yaml.compose(config_value, Loader=yaml.SafeLoader)
    except yaml.YAMLError:
        return {config_value}
    return _incus_secret_collect_nodes(node, options, config_value)


def incus_secret_collect_config(
    config: dict[str, str],
    config_options: dict[str, Any],
    config_lists: dict[str, str] | None = None,
) -> set[str]:
    """
    Collect no_log values from config.

    >>> peer_options = {'password': {'type': 'str', 'no_log': True}}
    >>> sorted(incus_secret_collect_config(
    ...     {'loki.auth.password': 'pass', 'bgp.peers.router.password': 'peer'},
    ...     {
    ...         'loki.auth.password': {'type': 'str', 'no_log': True},
    ...         'bgp_peers': {'type': 'list', 'options': peer_options},
    ...     },
    ...     {'bgp_peers': 'bgp.peers'},
    ... ))
    ['pass', 'peer']
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


def incus_secret_register_configs(
    configs: collections.abc.Iterable[dict[str, str]],
    config_options: dict[str, Any],
    config_lists: dict[str, str] | None = None,
) -> None:
    """
    Register no_log values from configs.

    >>> incus_secret_register_configs(
    ...     [{'loki.auth.password': 'old'}, {'loki.auth.password': 'new'}],
    ...     {'loki.auth.password': {'type': 'str', 'no_log': True}},
    ... )
    """
    secrets: set[str] = set()
    for config in configs:
        secrets = secrets.union(incus_secret_collect_config(
            config,
            config_options,
            config_lists,
        ))
    register_secrets(secrets)
