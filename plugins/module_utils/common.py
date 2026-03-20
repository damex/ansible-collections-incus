# -*- coding: utf-8 -*-
# Copyright: Roman Kuzmitskii <ansible@damex.org>
# SPDX-License-Identifier: GPL-3.0-or-later

"""Common data conversion utilities."""

from __future__ import annotations

from typing import Any

__all__ = [
    'incus_common_flatten_key_value_to_config',
    'incus_common_flatten_to_config',
    'incus_common_named_list_to_dict',
    'incus_common_stringify_value',
    'incus_common_stringify_dict',
    'incus_common_strip_none',
]


def incus_common_flatten_key_value_to_config(
    prefix: str,
    items: list[dict[str, Any]] | None,
) -> dict[str, str]:
    """
    Flatten key-value list to dotted config keys.

    >>> incus_common_flatten_key_value_to_config('environment', [{'name': 'HTTP_PROXY', 'value': 'http://proxy'}])
    {'environment.HTTP_PROXY': 'http://proxy'}
    """
    return {
        f'{prefix}.{item["name"]}': incus_common_stringify_value(item['value'])
        for item in (items or [])
    }


def incus_common_stringify_value(value: Any) -> str:
    """Stringify a value, converting bool to lowercase."""
    if isinstance(value, bool):
        return str(value).lower()
    return str(value)


def incus_common_stringify_dict(data: dict[str, Any] | None) -> dict[str, str]:
    """Stringify dict values, converting bools to lowercase and skipping None."""
    return {key: incus_common_stringify_value(value) for key, value in (data or {}).items() if value is not None}


def incus_common_named_list_to_dict(items: list[dict[str, Any]] | None) -> dict[str, Any]:
    """
    Convert named list to dict keyed by name.

    >>> incus_common_named_list_to_dict([{'name': 'router', 'address': '10.0.0.1', 'asn': 64601}])
    {'router': {'address': '10.0.0.1', 'asn': 64601}}
    """
    return {
        item['name']: {
            key: value
            for key, value in item.items()
            if key != 'name' and value is not None
        }
        for item in (items or [])
    }


def incus_common_flatten_to_config(prefix: str, data: dict[str, dict[str, Any]]) -> dict[str, str]:
    """
    Flatten nested dict to dotted config keys with stringified values.

    >>> incus_common_flatten_to_config('bgp.peers', {'router': {'address': '10.0.0.1'}})
    {'bgp.peers.router.address': '10.0.0.1'}
    """
    config: dict[str, str] = {}
    for name, properties in data.items():
        for key, value in properties.items():
            config[f'{prefix}.{name}.{key}'] = incus_common_stringify_value(value)
    return config


def incus_common_strip_none(data: Any) -> Any:
    """Strip None values recursively."""
    if isinstance(data, dict):
        return {key: incus_common_strip_none(value) for key, value in data.items() if value is not None}
    if isinstance(data, list):
        return [incus_common_strip_none(item) for item in data if item is not None]
    return data
