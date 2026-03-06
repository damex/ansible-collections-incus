# -*- coding: utf-8 -*-
# Copyright: Roman Kuzmitskii <ansible@damex.org>
# SPDX-License-Identifier: GPL-3.0-or-later

"""Tests for incus_cluster_info module."""

from __future__ import annotations

from ansible_collections.damex.incus.plugins.modules.incus_cluster_info import main
from ansible_collections.damex.incus.tests.unit.conftest import (
    assert_info_by_name,
    assert_info_not_found,
    assert_info_all,
    assert_info_fail,
)

__all__ = [
    'test_return_cluster_member_by_name',
    'test_return_empty_for_missing_cluster_member',
    'test_return_all_cluster_members',
    'test_fail_on_cluster_exception',
]


def test_return_cluster_member_by_name() -> None:
    """Return cluster member by name."""
    meta = assert_info_by_name(
        main, 'cluster_members', {'server_name': 'node1', 'status': 'Online'},
        name='node1', project=None,
    )
    assert meta['server_name'] == 'node1'


def test_return_empty_for_missing_cluster_member() -> None:
    """Return empty list for missing cluster member."""
    assert_info_not_found(main, 'cluster_members', project=None)


def test_return_all_cluster_members() -> None:
    """Return all cluster members."""
    assert_info_all(main, 'cluster_members', [{'server_name': 'a'}, {'server_name': 'b'}], project=None)


def test_fail_on_cluster_exception() -> None:
    """Fail on client exception."""
    assert_info_fail(main, project=None)
