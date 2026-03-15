# -*- coding: utf-8 -*-
# Copyright: Roman Kuzmitskii <ansible@damex.org>
# SPDX-License-Identifier: GPL-3.0-or-later

"""Tests for incus_network_address_set_info module."""

from __future__ import annotations

from ansible_collections.damex.incus.plugins.modules.incus_network_address_set_info import main
from ansible_collections.damex.incus.tests.unit.conftest import (
    assert_info_by_name,
    assert_info_not_found,
    assert_info_all,
    assert_info_fail,
)

__all__ = [
    'test_get_network_address_set_by_name',
    'test_get_missing_network_address_set',
    'test_get_all_network_address_sets',
    'test_get_network_address_sets_fail',
]


def test_get_network_address_set_by_name() -> None:
    """Return single network address set by name."""
    result = assert_info_by_name(main, 'network_address_sets', {
        'name': 'test',
        'description': 'Web servers',
        'config': {},
        'addresses': ['10.0.0.5', '10.0.0.6'],
    }, name='test')
    assert result['name'] == 'test'
    assert result['description'] == 'Web servers'
    assert len(result['addresses']) == 2


def test_get_missing_network_address_set() -> None:
    """Return empty list for missing network address set."""
    assert_info_not_found(main, 'network_address_sets')


def test_get_all_network_address_sets() -> None:
    """Return all network address sets."""
    assert_info_all(main, 'network_address_sets', [
        {'name': 'web', 'description': '', 'config': {}, 'addresses': ['10.0.0.5']},
        {'name': 'dns', 'description': '', 'config': {}, 'addresses': ['10.0.0.10']},
    ])


def test_get_network_address_sets_fail() -> None:
    """Fail on client exception."""
    assert_info_fail(main)
