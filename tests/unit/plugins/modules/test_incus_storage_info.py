# -*- coding: utf-8 -*-
# Copyright: Roman Kuzmitskii <ansible@damex.org>
# SPDX-License-Identifier: GPL-3.0-or-later

"""Tests for incus_storage_info module."""

from __future__ import annotations

from ansible_collections.damex.incus.plugins.modules.incus_storage_info import main
from ansible_collections.damex.incus.tests.unit.conftest import (
    assert_info_by_name,
    assert_info_not_found,
    assert_info_all,
    assert_info_fail,
)

__all__ = [
    'test_return_storage_pool_by_name',
    'test_return_empty_for_missing_storage_pool',
    'test_return_all_storage_pools',
    'test_fail_on_storage_exception',
]


def test_return_storage_pool_by_name() -> None:
    """Return storage pool by name."""
    meta = assert_info_by_name(main, 'storage_pools', {'name': 'default', 'driver': 'dir'}, project=None)
    assert meta['name'] == 'default'


def test_return_empty_for_missing_storage_pool() -> None:
    """Return empty list for missing storage pool."""
    assert_info_not_found(main, 'storage_pools', project=None)


def test_return_all_storage_pools() -> None:
    """Return all storage pools."""
    assert_info_all(main, 'storage_pools', [{'name': 'a'}, {'name': 'b'}], project=None)


def test_fail_on_storage_exception() -> None:
    """Fail on client exception."""
    assert_info_fail(main, project=None)
