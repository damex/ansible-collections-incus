# -*- coding: utf-8 -*-
# Copyright: Roman Kuzmitskii <ansible@damex.org>
# SPDX-License-Identifier: GPL-3.0-or-later

"""Shared test fixtures and helpers."""

from __future__ import annotations

from typing import Any, Callable
from unittest.mock import MagicMock, patch

import pytest

from ansible_collections.damex.incus.plugins.module_utils.incus import (
    IncusClientException,
    IncusNotFoundException,
)

__all__ = [
    'CONNECTION_PARAMS',
    'INCUS_UTILS',
    'assert_get_found',
    'assert_get_not_found',
    'assert_crud',
    'assert_crud_skip',
    'run_main',
    'assert_info_by_name',
    'assert_info_not_found',
    'assert_info_all',
    'assert_info_fail',
    'assert_write_create',
    'assert_write_skip',
    'assert_write_update',
    'assert_write_delete',
    'assert_write_delete_missing',
    'assert_write_check_mode',
    'run_module_main',
    'assert_module_create',
    'assert_module_delete',
    'assert_module_delete_missing',
    'assert_module_check_mode_create',
    'assert_module_fail_missing',
]

CONNECTION_PARAMS: dict[str, Any] = {
    'socket_path': '/var/lib/incus/unix.socket',
    'url': None,
    'client_cert': None,
    'client_key': None,
    'server_cert': None,
    'token': None,
    'validate_certs': True,
    'wait': True,
}

INCUS_UTILS: str = 'ansible_collections.damex.incus.plugins.module_utils.incus'


def assert_get_found(
    func: Callable[..., tuple[dict[str, Any], bool]],
    metadata: dict[str, Any],
    *args: Any,
) -> dict[str, Any]:
    """Call get helper and assert resource exists."""
    client = MagicMock()
    client.get.return_value = {'metadata': metadata}
    meta, exists = func(client, *args)
    assert exists is True
    return meta


def assert_get_not_found(
    func: Callable[..., tuple[dict[str, Any], bool]],
    *args: Any,
) -> None:
    """Call get helper and assert resource missing."""
    client = MagicMock()
    client.get.side_effect = IncusNotFoundException('not found')
    meta, exists = func(client, *args)
    assert exists is False
    assert meta == {}


def assert_crud(func: Callable[..., bool], method: str, *args: Any) -> None:
    """Call CRUD helper and assert API method called."""
    module = MagicMock()
    module.check_mode = False
    client = MagicMock()
    getattr(client, method).return_value = {'type': 'sync'}
    result = func(module, client, *args)
    assert result is True
    getattr(client, method).assert_called_once()


def assert_crud_skip(func: Callable[..., bool], method: str, *args: Any) -> None:
    """Call CRUD helper in check mode and assert no API call."""
    module = MagicMock()
    module.check_mode = True
    client = MagicMock()
    result = func(module, client, *args)
    assert result is True
    getattr(client, method).assert_not_called()


def run_main(
    mock_create_module: MagicMock,
    mock_create_client: MagicMock,
    module: MagicMock,
    client: MagicMock,
    main_func: Callable[[], None],
) -> None:
    """Wire mock factories and run module main."""
    mock_create_module.return_value = module
    mock_create_client.return_value = client
    main_func()


def _info_module(name: str | None, project: str | None) -> MagicMock:
    """Build mock info module."""
    module = MagicMock()
    module.params = {'name': name}
    if project is not None:
        module.params['project'] = project
    return module


def assert_info_by_name(
    main_func: Callable[[], None], return_key: str,
    metadata: dict[str, Any], *, name: str = 'test',
    project: str | None = 'default',
) -> dict[str, Any]:
    """Call info main and assert single resource returned."""
    module = _info_module(name, project)
    client = MagicMock()
    client.get.return_value = {'metadata': metadata}
    with patch(f'{INCUS_UTILS}.incus_create_info_module', return_value=module), \
         patch(f'{INCUS_UTILS}.incus_create_client', return_value=client):
        main_func()
    result: list[dict[str, Any]] = module.exit_json.call_args[1][return_key]
    assert len(result) == 1
    return result[0]


def assert_info_not_found(
    main_func: Callable[[], None], return_key: str, *,
    name: str = 'missing', project: str | None = 'default',
) -> None:
    """Call info main and assert empty list for missing name."""
    module = _info_module(name, project)
    client = MagicMock()
    client.get.side_effect = IncusNotFoundException('not found')
    with patch(f'{INCUS_UTILS}.incus_create_info_module', return_value=module), \
         patch(f'{INCUS_UTILS}.incus_create_client', return_value=client):
        main_func()
    module.exit_json.assert_called_once_with(**{return_key: []})


def assert_info_all(
    main_func: Callable[[], None], return_key: str,
    items: list[dict[str, Any]], *, project: str | None = 'default',
) -> None:
    """Call info main and assert all resources returned."""
    module = _info_module(None, project)
    client = MagicMock()
    client.get.return_value = {'metadata': items}
    with patch(f'{INCUS_UTILS}.incus_create_info_module', return_value=module), \
         patch(f'{INCUS_UTILS}.incus_create_client', return_value=client):
        main_func()
    result = module.exit_json.call_args[1][return_key]
    assert len(result) == len(items)


def assert_info_fail(
    main_func: Callable[[], None], *,
    project: str | None = 'default',
) -> None:
    """Call info main and assert failure on client exception."""
    module = _info_module(None, project)
    client = MagicMock()
    client.get.side_effect = IncusClientException('connection refused')
    with patch(f'{INCUS_UTILS}.incus_create_info_module', return_value=module), \
         patch(f'{INCUS_UTILS}.incus_create_client', return_value=client):
        main_func()
    module.fail_json.assert_called_once_with(msg='connection refused')


def assert_write_create(
    main_func: Callable[[], None], module_path: str, module: MagicMock,
) -> MagicMock:
    """Call write main with not-found resource and assert created."""
    client = MagicMock()
    client.get.side_effect = IncusNotFoundException('not found')
    client.post.return_value = {'type': 'sync'}
    with patch(f'{module_path}.incus_create_write_module', return_value=module), \
         patch(f'{INCUS_UTILS}.incus_create_client', return_value=client):
        main_func()
    module.exit_json.assert_called_once_with(changed=True)
    client.post.assert_called_once()
    return client


def assert_write_skip(
    main_func: Callable[[], None], module_path: str,
    module: MagicMock, current: dict[str, Any],
) -> None:
    """Call write main with matching resource and assert no change."""
    client = MagicMock()
    client.get.return_value = {'metadata': current}
    with patch(f'{module_path}.incus_create_write_module', return_value=module), \
         patch(f'{INCUS_UTILS}.incus_create_client', return_value=client):
        main_func()
    module.exit_json.assert_called_once_with(changed=False)


def assert_write_update(
    main_func: Callable[[], None], module_path: str,
    module: MagicMock, current: dict[str, Any],
) -> None:
    """Call write main with changed resource and assert updated."""
    client = MagicMock()
    client.get.return_value = {'metadata': current}
    client.put.return_value = {'type': 'sync'}
    with patch(f'{module_path}.incus_create_write_module', return_value=module), \
         patch(f'{INCUS_UTILS}.incus_create_client', return_value=client):
        main_func()
    module.exit_json.assert_called_once_with(changed=True)


def assert_write_delete(
    main_func: Callable[[], None], module_path: str, module: MagicMock,
) -> None:
    """Call write main and assert resource deleted."""
    client = MagicMock()
    client.get.return_value = {'metadata': {'description': '', 'config': {}}}
    client.delete.return_value = {'type': 'sync'}
    with patch(f'{module_path}.incus_create_write_module', return_value=module), \
         patch(f'{INCUS_UTILS}.incus_create_client', return_value=client):
        main_func()
    module.exit_json.assert_called_once_with(changed=True)
    client.delete.assert_called_once()


def assert_write_delete_missing(
    main_func: Callable[[], None], module_path: str, module: MagicMock,
) -> None:
    """Call write main and assert skip for missing resource."""
    client = MagicMock()
    client.get.side_effect = IncusNotFoundException('not found')
    with patch(f'{module_path}.incus_create_write_module', return_value=module), \
         patch(f'{INCUS_UTILS}.incus_create_client', return_value=client):
        main_func()
    module.exit_json.assert_called_once_with(changed=False)


def assert_write_check_mode(
    main_func: Callable[[], None], module_path: str, module: MagicMock,
) -> None:
    """Call write main in check mode and assert no API calls."""
    client = MagicMock()
    client.get.side_effect = IncusNotFoundException('not found')
    with patch(f'{module_path}.incus_create_write_module', return_value=module), \
         patch(f'{INCUS_UTILS}.incus_create_client', return_value=client):
        main_func()
    module.exit_json.assert_called_once_with(changed=True)
    client.post.assert_not_called()


def run_module_main(
    module_path: str, module: MagicMock, client: MagicMock,
    main_func: Callable[[], None],
) -> None:
    """Patch module-level factories and run main."""
    with patch(f'{module_path}.incus_create_write_module', return_value=module), \
         patch(f'{module_path}.incus_create_client', return_value=client):
        main_func()


def assert_module_create(
    main_func: Callable[[], None], module_path: str, module: MagicMock,
) -> MagicMock:
    """Call module main with not-found resource and assert created."""
    client = MagicMock()
    client.get.side_effect = IncusNotFoundException('not found')
    client.post.return_value = {'type': 'sync'}
    run_module_main(module_path, module, client, main_func)
    client.post.assert_called_once()
    return client


def assert_module_delete(
    main_func: Callable[[], None], module_path: str,
    module: MagicMock, current: dict[str, Any],
) -> None:
    """Call module main and assert resource deleted."""
    client = MagicMock()
    client.get.return_value = {'metadata': current}
    client.delete.return_value = {'type': 'sync'}
    run_module_main(module_path, module, client, main_func)
    module.exit_json.assert_called_once_with(changed=True)
    client.delete.assert_called_once()


def assert_module_delete_missing(
    main_func: Callable[[], None], module_path: str, module: MagicMock,
) -> None:
    """Call module main and assert skip for missing resource."""
    client = MagicMock()
    client.get.side_effect = IncusNotFoundException('not found')
    run_module_main(module_path, module, client, main_func)
    module.exit_json.assert_called_once_with(changed=False)


def assert_module_check_mode_create(
    main_func: Callable[[], None], module_path: str, module: MagicMock,
) -> None:
    """Call module main in check mode and assert no API calls."""
    client = MagicMock()
    client.get.side_effect = IncusNotFoundException('not found')
    run_module_main(module_path, module, client, main_func)
    assert module.exit_json.call_args[1]['changed'] is True
    client.post.assert_not_called()


def assert_module_fail_missing(
    main_func: Callable[[], None], module_path: str, module: MagicMock,
) -> None:
    """Call module main and assert fail_json for missing required param."""
    module.fail_json.side_effect = SystemExit(1)
    client = MagicMock()
    client.get.side_effect = IncusNotFoundException('not found')
    with pytest.raises(SystemExit):
        run_module_main(module_path, module, client, main_func)
    module.fail_json.assert_called_once()
