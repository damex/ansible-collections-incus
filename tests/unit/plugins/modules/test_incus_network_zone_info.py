# -*- coding: utf-8 -*-
# Copyright: Roman Kuzmitskii <ansible@damex.org>
# SPDX-License-Identifier: GPL-3.0-or-later

"""Tests for incus_network_zone_info module."""

from __future__ import annotations

from ansible_collections.damex.incus.plugins.modules.incus_network_zone_info import main
from ansible_collections.damex.incus.tests.unit.conftest import (
    assert_info_by_name,
    assert_info_not_found,
    assert_info_all,
    assert_info_fail,
)

__all__ = [
    'test_get_network_zone_by_name',
    'test_get_missing_network_zone',
    'test_get_all_network_zones',
    'test_get_network_zones_fail',
]


def test_get_network_zone_by_name() -> None:
    """Return single network zone by name."""
    result = assert_info_by_name(main, 'network_zones', {
        'name': 'test',
        'description': 'Forward DNS zone',
        'config': {},
    }, name='test')
    assert result['name'] == 'test'
    assert result['description'] == 'Forward DNS zone'


def test_get_missing_network_zone() -> None:
    """Return empty list for missing network zone."""
    assert_info_not_found(main, 'network_zones')


def test_get_all_network_zones() -> None:
    """Return all network zones."""
    assert_info_all(main, 'network_zones', [
        {'name': 'example.com', 'description': '', 'config': {}},
        {'name': 'internal.lan', 'description': '', 'config': {}},
    ])


def test_get_network_zones_fail() -> None:
    """Fail on client exception."""
    assert_info_fail(main)
