# -*- coding: utf-8 -*-
# Copyright: Roman Kuzmitskii <ansible@damex.org>
# SPDX-License-Identifier: GPL-3.0-or-later

"""Tests for incus_cluster_member_info module."""

from __future__ import annotations

from ansible_collections.damex.incus.plugins.modules.incus_cluster_member_info import main
from ansible_collections.damex.incus.tests.unit.conftest import (
    assert_info_by_name,
    assert_info_not_found,
    assert_info_all,
    assert_info_fail,
)

__all__ = [
    'test_get_cluster_member_by_name',
    'test_get_missing_cluster_member',
    'test_get_all_cluster_members',
    'test_get_cluster_members_fail',
]


def test_get_cluster_member_by_name() -> None:
    """Return single cluster member by name."""
    result = assert_info_by_name(main, 'cluster_members', {
        'server_name': 'node1',
        'url': 'https://node1:8443',
        'roles': ['database'],
        'status': 'Online',
        'config': {},
    }, name='node1', project=None)
    assert result['server_name'] == 'node1'
    assert result['status'] == 'Online'


def test_get_missing_cluster_member() -> None:
    """Return empty list for missing cluster member."""
    assert_info_not_found(main, 'cluster_members', project=None)


def test_get_all_cluster_members() -> None:
    """Return all cluster members."""
    assert_info_all(main, 'cluster_members', [
        {'server_name': 'node1', 'status': 'Online'},
        {'server_name': 'node2', 'status': 'Online'},
    ], project=None)


def test_get_cluster_members_fail() -> None:
    """Fail on client exception."""
    assert_info_fail(main, project=None)
