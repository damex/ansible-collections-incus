# -*- coding: utf-8 -*-
# Copyright: Roman Kuzmitskii <ansible@damex.org>
# SPDX-License-Identifier: GPL-3.0-or-later

"""Tests for incus_instance_info module."""

from __future__ import annotations

from ansible_collections.damex.incus.plugins.modules.incus_instance_info import main
from ansible_collections.damex.incus.tests.unit.conftest import (
    assert_info_by_name,
    assert_info_not_found,
    assert_info_all,
    assert_info_fail,
)

__all__ = [
    'test_return_instance_by_name',
    'test_return_empty_for_missing_instance',
    'test_return_all_instances',
    'test_fail_on_instance_exception',
]


def test_return_instance_by_name() -> None:
    """Return instance by name."""
    meta = assert_info_by_name(main, 'instances', {'name': 'test', 'status': 'Running'})
    assert meta['name'] == 'test'


def test_return_empty_for_missing_instance() -> None:
    """Return empty list for missing instance."""
    assert_info_not_found(main, 'instances')


def test_return_all_instances() -> None:
    """Return all instances."""
    assert_info_all(main, 'instances', [{'name': 'a'}, {'name': 'b'}])


def test_fail_on_instance_exception() -> None:
    """Fail on client exception."""
    assert_info_fail(main)
