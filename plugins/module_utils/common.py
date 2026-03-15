# -*- coding: utf-8 -*-
# Copyright: Roman Kuzmitskii <ansible@damex.org>
# SPDX-License-Identifier: GPL-3.0-or-later

"""Common data conversion utilities."""

from __future__ import annotations

from typing import Any

__all__ = [
    'incus_common_flatten_to_config',
    'incus_common_named_list_to_dict',
    'incus_common_stringify_value',
    'incus_common_strip_none',
]


def incus_common_stringify_value(value: Any) -> str:
    """Stringify a value, converting bool to lowercase."""
    if isinstance(value, bool):
        return str(value).lower()
    return str(value)


def incus_common_named_list_to_dict(items: list[dict[str, Any]] | None) -> dict[str, Any]:
    """Convert named list to dict keyed by name."""
    return {
        item['name']: {
            key: value
            for key, value in item.items()
            if key != 'name' and value is not None
        }
        for item in (items or [])
    }


def incus_common_flatten_to_config(prefix: str, data: dict[str, dict[str, Any]]) -> dict[str, str]:
    """Flatten nested dict to dotted config keys with stringified values."""
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
