# -*- coding: utf-8 -*-
# Copyright: Roman Kuzmitskii <ansible@damex.org>
# SPDX-License-Identifier: GPL-3.0-or-later

"""Tests for incus_network_info module."""

from __future__ import annotations

from ansible_collections.damex.incus.plugins.modules.incus_network_info import main
from ansible_collections.damex.incus.tests.unit.conftest import (
    assert_info_by_name,
    assert_info_not_found,
    assert_info_all,
    assert_info_fail,
)

__all__ = [
    'test_return_network_by_name',
    'test_return_empty_for_missing_network',
    'test_return_all_networks',
    'test_fail_on_network_exception',
]


def test_return_network_by_name() -> None:
    """Return network by name."""
    meta = assert_info_by_name(main, 'networks', {'name': 'incusbr0', 'type': 'bridge'})
    assert meta['name'] == 'incusbr0'


def test_return_empty_for_missing_network() -> None:
    """Return empty list for missing network."""
    assert_info_not_found(main, 'networks')


def test_return_all_networks() -> None:
    """Return all networks."""
    assert_info_all(main, 'networks', [{'name': 'a'}, {'name': 'b'}])


def test_fail_on_network_exception() -> None:
    """Fail on client exception."""
    assert_info_fail(main)
