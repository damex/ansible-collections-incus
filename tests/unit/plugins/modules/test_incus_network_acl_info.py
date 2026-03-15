# -*- coding: utf-8 -*-
# Copyright: Roman Kuzmitskii <ansible@damex.org>
# SPDX-License-Identifier: GPL-3.0-or-later

"""Tests for incus_network_acl_info module."""

from __future__ import annotations

from ansible_collections.damex.incus.plugins.modules.incus_network_acl_info import main
from ansible_collections.damex.incus.tests.unit.conftest import (
    assert_info_by_name,
    assert_info_not_found,
    assert_info_all,
    assert_info_fail,
)

__all__ = [
    'test_get_network_acl_by_name',
    'test_get_missing_network_acl',
    'test_get_all_network_acls',
    'test_get_network_acls_fail',
]


def test_get_network_acl_by_name() -> None:
    """Return single network ACL by name."""
    result = assert_info_by_name(main, 'network_acls', {
        'name': 'test',
        'description': 'Web ACL',
        'config': {},
        'ingress': [{'action': 'allow', 'protocol': 'tcp', 'destination_port': '80'}],
        'egress': [],
    }, name='test')
    assert result['name'] == 'test'
    assert result['description'] == 'Web ACL'
    assert len(result['ingress']) == 1


def test_get_missing_network_acl() -> None:
    """Return empty list for missing network ACL."""
    assert_info_not_found(main, 'network_acls')


def test_get_all_network_acls() -> None:
    """Return all network ACLs."""
    assert_info_all(main, 'network_acls', [
        {'name': 'web', 'description': '', 'config': {}, 'ingress': [], 'egress': []},
        {'name': 'db', 'description': '', 'config': {}, 'ingress': [], 'egress': []},
    ])


def test_get_network_acls_fail() -> None:
    """Fail on client exception."""
    assert_info_fail(main)
