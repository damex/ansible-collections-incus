# -*- coding: utf-8 -*-
# Copyright: Roman Kuzmitskii <ansible@damex.org>
# SPDX-License-Identifier: GPL-3.0-or-later

"""Tests for incus_profile_info module."""

from __future__ import annotations

from ansible_collections.damex.incus.plugins.modules.incus_profile_info import main
from ansible_collections.damex.incus.tests.unit.conftest import (
    assert_info_by_name,
    assert_info_not_found,
    assert_info_all,
    assert_info_fail,
)

__all__ = [
    'test_return_profile_by_name',
    'test_return_empty_for_missing_profile',
    'test_return_all_profiles',
    'test_fail_on_profile_exception',
]


def test_return_profile_by_name() -> None:
    """Return profile by name."""
    meta = assert_info_by_name(main, 'profiles', {'name': 'default', 'description': 'Default'})
    assert meta['name'] == 'default'


def test_return_empty_for_missing_profile() -> None:
    """Return empty list for missing profile."""
    assert_info_not_found(main, 'profiles')


def test_return_all_profiles() -> None:
    """Return all profiles."""
    assert_info_all(main, 'profiles', [{'name': 'a'}, {'name': 'b'}])


def test_fail_on_profile_exception() -> None:
    """Fail on client exception."""
    assert_info_fail(main)
