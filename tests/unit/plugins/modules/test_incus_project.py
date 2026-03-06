# -*- coding: utf-8 -*-
# Copyright: Roman Kuzmitskii <ansible@damex.org>
# SPDX-License-Identifier: GPL-3.0-or-later

"""Tests for incus_project module."""

from __future__ import annotations

from unittest.mock import MagicMock

from ansible_collections.damex.incus.plugins.modules.incus_project import main
from ansible_collections.damex.incus.tests.unit.conftest import (
    CONNECTION_PARAMS,
    assert_write_create,
    assert_write_skip,
    assert_write_update,
    assert_write_delete,
    assert_write_delete_missing,
    assert_write_check_mode,
)

__all__ = [
    'test_create',
    'test_skip_matching',
    'test_update_changed_description',
    'test_update_changed_config',
    'test_delete_existing',
    'test_delete_nonexistent',
    'test_check_mode',
]

MODULE = 'ansible_collections.damex.incus.plugins.modules.incus_project'


def _mock_module(state: str = 'present', check_mode: bool = False) -> MagicMock:
    """Build mock module."""
    module = MagicMock()
    module.params = {
        **CONNECTION_PARAMS,
        'name': 'myproject',
        'state': state,
        'description': '',
        'config': {},
    }
    module.check_mode = check_mode
    return module


def test_create() -> None:
    """Create missing project."""
    assert_write_create(main, MODULE, _mock_module())


def test_skip_matching() -> None:
    """Skip matching project."""
    assert_write_skip(main, MODULE, _mock_module(), {'description': '', 'config': {}})


def test_update_changed_description() -> None:
    """Update project with changed description."""
    module = _mock_module()
    module.params['description'] = 'new desc'
    assert_write_update(main, MODULE, module, {'description': 'old', 'config': {}})


def test_update_changed_config() -> None:
    """Update project with changed config."""
    module = _mock_module()
    module.params['config'] = {'features.images': 'true'}
    assert_write_update(main, MODULE, module, {'description': '', 'config': {}})


def test_delete_existing() -> None:
    """Delete existing project."""
    assert_write_delete(main, MODULE, _mock_module(state='absent'))


def test_delete_nonexistent() -> None:
    """Skip delete for missing project."""
    assert_write_delete_missing(main, MODULE, _mock_module(state='absent'))


def test_check_mode() -> None:
    """Skip API calls in check mode."""
    assert_write_check_mode(main, MODULE, _mock_module(check_mode=True))
