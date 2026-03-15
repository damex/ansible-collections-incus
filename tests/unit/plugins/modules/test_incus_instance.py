# -*- coding: utf-8 -*-
# Copyright: Roman Kuzmitskii <ansible@damex.org>
# SPDX-License-Identifier: GPL-3.0-or-later

"""Tests for incus_instance module."""

from __future__ import annotations

from unittest.mock import MagicMock

from ansible_collections.damex.incus.plugins.module_utils.incus import IncusNotFoundException
from ansible_collections.damex.incus.plugins.modules.incus_instance import (
    _get_instance,
    _create_instance,
    _update_instance,
    _delete_instance,
    _manage_state,
    main,
)
from ansible_collections.damex.incus.tests.unit.conftest import (
    CONNECTION_PARAMS,
    assert_get_found,
    assert_get_not_found,
    assert_crud,
    assert_crud_skip,
    assert_write_check_mode,
    assert_write_delete,
    assert_write_delete_missing,
    assert_write_fail_create,
    run_module_main,
)

__all__ = [
    'test_get_instance_found',
    'test_get_instance_not_found',
    'test_create_instance',
    'test_create_instance_check_mode',
    'test_update_instance',
    'test_update_instance_check_mode',
    'test_delete_instance',
    'test_delete_instance_check_mode',
    'test_manage_state_start_stopped',
    'test_manage_state_stop_running',
    'test_manage_state_restart_running',
    'test_manage_state_restart_stopped_noop',
    'test_manage_state_already_started',
    'test_manage_state_already_stopped',
    'test_main_create_and_start',
    'test_main_delete_existing',
    'test_main_delete_nonexistent',
    'test_main_update_changed_config',
    'test_main_skip_matching',
    'test_main_filter_volatile_config',
    'test_main_fail_missing_source',
    'test_main_check_mode_create',
    'test_main_start_stopped_existing',
]

MODULE = 'ansible_collections.damex.incus.plugins.modules.incus_instance'


def test_get_instance_found() -> None:
    """Return metadata for existing instance."""
    meta = assert_get_found(_get_instance, {'name': 'test', 'status': 'Running'}, 'default', 'test')
    assert meta['name'] == 'test'


def test_get_instance_not_found() -> None:
    """Return empty dict for missing instance."""
    assert_get_not_found(_get_instance, 'default', 'test')


def test_create_instance() -> None:
    """Post instance creation request."""
    assert_crud(_create_instance, 'post', 'default', 'test', {'description': ''})


def test_create_instance_check_mode() -> None:
    """Skip post in check mode."""
    assert_crud_skip(_create_instance, 'post', 'default', 'test', {'description': ''})


def test_update_instance() -> None:
    """Put instance update request."""
    assert_crud(_update_instance, 'put', 'default', 'test', {'description': 'new'})


def test_update_instance_check_mode() -> None:
    """Skip put in check mode."""
    assert_crud_skip(_update_instance, 'put', 'default', 'test', {'description': 'new'})


def test_delete_instance() -> None:
    """Delete instance request."""
    assert_crud(_delete_instance, 'delete', 'default', 'test')


def test_delete_instance_check_mode() -> None:
    """Skip delete in check mode."""
    assert_crud_skip(_delete_instance, 'delete', 'default', 'test')


def test_manage_state_start_stopped() -> None:
    """Start stopped instance."""
    module = MagicMock()
    module.check_mode = False
    client = MagicMock()
    client.put.return_value = {'type': 'sync'}
    result = _manage_state(module, client, '/1.0/instances/test/state', 'started', 'Stopped')
    assert result is True
    client.put.assert_called_once()
    assert client.put.call_args[0][1] == {'action': 'start'}


def test_manage_state_stop_running() -> None:
    """Stop running instance."""
    module = MagicMock()
    module.check_mode = False
    client = MagicMock()
    client.put.return_value = {'type': 'sync'}
    result = _manage_state(module, client, '/1.0/instances/test/state', 'stopped', 'Running')
    assert result is True
    assert client.put.call_args[0][1] == {'action': 'stop', 'force': True}


def test_manage_state_restart_running() -> None:
    """Restart running instance."""
    module = MagicMock()
    module.check_mode = False
    client = MagicMock()
    client.put.return_value = {'type': 'sync'}
    result = _manage_state(module, client, '/1.0/instances/test/state', 'restarted', 'Running')
    assert result is True
    assert client.put.call_args[0][1] == {'action': 'restart', 'force': True}


def test_manage_state_restart_stopped_noop() -> None:
    """Skip restart for stopped instance."""
    module = MagicMock()
    module.check_mode = False
    client = MagicMock()
    result = _manage_state(module, client, '/1.0/instances/test/state', 'restarted', 'Stopped')
    assert result is False


def test_manage_state_already_started() -> None:
    """Skip start for running instance."""
    module = MagicMock()
    module.check_mode = False
    client = MagicMock()
    result = _manage_state(module, client, '/1.0/instances/test/state', 'started', 'Running')
    assert result is False


def test_manage_state_already_stopped() -> None:
    """Skip stop for stopped instance."""
    module = MagicMock()
    module.check_mode = False
    client = MagicMock()
    result = _manage_state(module, client, '/1.0/instances/test/state', 'stopped', 'Stopped')
    assert result is False


def _mock_module(state: str = 'started', check_mode: bool = False,
                 source: str | None = 'images:debian/13') -> MagicMock:
    """Build mock module."""
    module = MagicMock()
    module.params = {
        **CONNECTION_PARAMS,
        'name': 'test',
        'state': state,
        'project': 'default',
        'source': source,
        'source_server': None,
        'source_protocol': 'simplestreams',
        'type': 'container',
        'ephemeral': False,
        'profiles': ['default'],
        'config': {},
        'devices': [],
        'description': '',
    }
    module.check_mode = check_mode
    return module


def test_main_create_and_start() -> None:
    """Create and start new instance."""
    module = _mock_module()
    client = MagicMock()
    client.get.side_effect = IncusNotFoundException('not found')
    client.post.return_value = {'type': 'sync'}
    client.put.return_value = {'type': 'sync'}
    run_module_main(MODULE, module, client, main)
    module.exit_json.assert_called_once()
    assert module.exit_json.call_args[1]['changed'] is True
    client.post.assert_called_once()


def test_main_delete_existing() -> None:
    """Delete existing instance."""
    assert_write_delete(main, MODULE, _mock_module(state='absent'),
                        {'name': 'test', 'status': 'Running'})


def test_main_delete_nonexistent() -> None:
    """Skip delete for missing instance."""
    assert_write_delete_missing(main, MODULE, _mock_module(state='absent'))


def test_main_update_changed_config() -> None:
    """Update instance with changed config."""
    module = _mock_module()
    module.params['config'] = {'limits.cpu': '4'}
    client = MagicMock()
    client.get.return_value = {'metadata': {
        'name': 'test', 'status': 'Running', 'architecture': 'x86_64',
        'description': '', 'config': {'limits.cpu': '2'}, 'devices': {}, 'profiles': ['default'],
    }}
    client.put.return_value = {'type': 'sync'}
    run_module_main(MODULE, module, client, main)
    module.exit_json.assert_called_once()
    assert module.exit_json.call_args[1]['changed'] is True


def test_main_skip_matching() -> None:
    """Skip matching instance."""
    module = _mock_module()
    client = MagicMock()
    client.get.return_value = {'metadata': {
        'name': 'test', 'status': 'Running', 'architecture': 'x86_64',
        'description': '', 'config': {}, 'devices': {}, 'profiles': ['default'],
    }}
    run_module_main(MODULE, module, client, main)
    module.exit_json.assert_called_once_with(changed=False)


def test_main_filter_volatile_config() -> None:
    """Filter volatile and image config keys."""
    module = _mock_module()
    client = MagicMock()
    client.get.return_value = {'metadata': {
        'name': 'test', 'status': 'Running', 'architecture': 'x86_64',
        'description': '', 'config': {
            'volatile.uuid': 'abc', 'image.os': 'debian',
        }, 'devices': {}, 'profiles': ['default'],
    }}
    run_module_main(MODULE, module, client, main)
    module.exit_json.assert_called_once_with(changed=False)


def test_main_fail_missing_source() -> None:
    """Fail when source missing on create."""
    assert_write_fail_create(main, MODULE, _mock_module(source=None))


def test_main_check_mode_create() -> None:
    """Skip API calls in check mode."""
    assert_write_check_mode(main, MODULE, _mock_module(check_mode=True))


def test_main_start_stopped_existing() -> None:
    """Start stopped existing instance without config change."""
    module = _mock_module()
    client = MagicMock()
    client.get.return_value = {'metadata': {
        'name': 'test', 'status': 'Stopped', 'architecture': 'x86_64',
        'description': '', 'config': {}, 'devices': {}, 'profiles': ['default'],
    }}
    client.put.return_value = {'type': 'sync'}
    run_module_main(MODULE, module, client, main)
    module.exit_json.assert_called_once()
    assert module.exit_json.call_args[1]['changed'] is True
    client.put.assert_called_once()
    assert client.put.call_args[0][1] == {'action': 'start'}
