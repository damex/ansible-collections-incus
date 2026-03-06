# -*- coding: utf-8 -*-
# Copyright: Roman Kuzmitskii <ansible@damex.org>
# SPDX-License-Identifier: GPL-3.0-or-later

"""Tests for incus_project_info module."""

from __future__ import annotations

from ansible_collections.damex.incus.plugins.modules.incus_project_info import main
from ansible_collections.damex.incus.tests.unit.conftest import (
    assert_info_by_name,
    assert_info_not_found,
    assert_info_all,
    assert_info_fail,
)

__all__ = [
    'test_return_project_by_name',
    'test_return_empty_for_missing_project',
    'test_return_all_projects',
    'test_fail_on_project_exception',
]


def test_return_project_by_name() -> None:
    """Return project by name."""
    meta = assert_info_by_name(main, 'projects', {'name': 'default', 'description': 'Default'}, project=None)
    assert meta['name'] == 'default'


def test_return_empty_for_missing_project() -> None:
    """Return empty list for missing project."""
    assert_info_not_found(main, 'projects', project=None)


def test_return_all_projects() -> None:
    """Return all projects."""
    assert_info_all(main, 'projects', [{'name': 'a'}, {'name': 'b'}], project=None)


def test_fail_on_project_exception() -> None:
    """Fail on client exception."""
    assert_info_fail(main, project=None)
