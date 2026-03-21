# -*- coding: utf-8 -*-
# Copyright: Roman Kuzmitskii <ansible@damex.org>
# SPDX-License-Identifier: GPL-3.0-or-later

"""Tests for incus_cluster_group_info module."""

from __future__ import annotations

from ansible_collections.damex.incus.plugins.modules.incus_cluster_group_info import main
from ansible_collections.damex.incus.tests.unit.conftest import (
    assert_info_all,
    assert_info_by_name,
    assert_info_fail,
    assert_info_not_found,
)

__all__ = [
    'test_get_cluster_group_by_name',
    'test_get_missing_cluster_group',
    'test_get_all_cluster_groups',
    'test_get_cluster_groups_fail',
]


def test_get_cluster_group_by_name() -> None:
    """Return single cluster group by name."""
    result = assert_info_by_name(main, 'cluster_groups', {
        'name': 'dpu',
        'description': 'ARM64 DPU nodes',
        'members': ['arm64-node1', 'arm64-node2'],
    }, name='dpu', project=None)
    assert result['name'] == 'dpu'
    assert result['members'] == ['arm64-node1', 'arm64-node2']


def test_get_missing_cluster_group() -> None:
    """Return empty list for missing cluster group."""
    assert_info_not_found(main, 'cluster_groups', project=None)


def test_get_all_cluster_groups() -> None:
    """Return all cluster groups."""
    assert_info_all(main, 'cluster_groups', [
        {'name': 'dpu', 'members': ['arm64-node1']},
        {'name': 'staging', 'members': []},
    ], project=None)


def test_get_cluster_groups_fail() -> None:
    """Fail on client exception."""
    assert_info_fail(main, project=None)
