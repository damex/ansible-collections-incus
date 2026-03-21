# -*- coding: utf-8 -*-
# Copyright: Roman Kuzmitskii <ansible@damex.org>
# SPDX-License-Identifier: GPL-3.0-or-later

"""Shared test fixtures and helpers."""

from __future__ import annotations

import collections.abc
from contextlib import contextmanager
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from ansible_collections.damex.incus.plugins.module_utils.incus_client import (
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
    'assert_write_fail_create',
    'mock_incus_client',
    'run_module_main',
]

CONNECTION_PARAMS: dict[str, Any] = {
    'socket_path': '/var/lib/incus/unix.socket',
    'url': None,
    'client_cert': None,
    'client_key': None,
    'server_cert': None,
    'client_cert_path': None,
    'client_key_path': None,
    'server_cert_path': None,
    'token': None,
    'validate_certs': True,
    'wait': True,
}

INCUS_UTILS: str = 'ansible_collections.damex.incus.plugins.module_utils.incus'


def mock_incus_client() -> MagicMock:
    """
    Create mock IncusClient with context manager support.

    >>> mock_incus_client()
    """
    client = MagicMock()
    client.__enter__ = MagicMock(return_value=client)
    client.__exit__ = MagicMock(return_value=False)
    return client


@contextmanager
def _write_patches(
    module_path: str, module: MagicMock, client: MagicMock,
) -> collections.abc.Generator[None, None, None]:
    """Patch write module factory and client at both import sites."""
    with patch(f'{module_path}.incus_create_write_module', return_value=module), \
         patch(f'{INCUS_UTILS}.incus_create_client', return_value=client), \
         patch(f'{module_path}.incus_create_client', return_value=client, create=True):
        yield


def assert_get_found(
    func: collections.abc.Callable[..., tuple[dict[str, Any], bool]],
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
    func: collections.abc.Callable[..., tuple[dict[str, Any], bool]],
    *args: Any,
) -> None:
    """Call get helper and assert resource missing."""
    client = MagicMock()
    client.get.side_effect = IncusNotFoundException('not found')
    meta, exists = func(client, *args)
    assert exists is False
    assert meta == {}


def assert_crud(func: collections.abc.Callable[..., bool], method: str, *args: Any) -> None:
    """Call CRUD helper and assert API method called."""
    module = MagicMock()
    module.check_mode = False
    client = MagicMock()
    getattr(client, method).return_value = {'type': 'sync'}
    result = func(module, client, *args)
    assert result is True
    getattr(client, method).assert_called_once()


def assert_crud_skip(func: collections.abc.Callable[..., bool], method: str, *args: Any) -> None:
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
    main_func: collections.abc.Callable[[], None],
) -> None:
    """Wire mock factories and run module main."""
    client.__enter__ = MagicMock(return_value=client)
    client.__exit__ = MagicMock(return_value=False)
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
    main_func: collections.abc.Callable[[], None], return_key: str,
    metadata: dict[str, Any], *, name: str = 'test',
    project: str | None = 'default',
) -> dict[str, Any]:
    """Call info main and assert single resource returned."""
    module = _info_module(name, project)
    client = mock_incus_client()
    client.get.return_value = {'metadata': metadata}
    with patch(f'{INCUS_UTILS}.incus_create_info_module', return_value=module), \
         patch(f'{INCUS_UTILS}.incus_create_client', return_value=client):
        main_func()
    result: list[dict[str, Any]] = module.exit_json.call_args[1][return_key]
    assert len(result) == 1
    return result[0]


def assert_info_not_found(
    main_func: collections.abc.Callable[[], None], return_key: str, *,
    name: str = 'missing', project: str | None = 'default',
) -> None:
    """Call info main and assert empty list for missing name."""
    module = _info_module(name, project)
    client = mock_incus_client()
    client.get.side_effect = IncusNotFoundException('not found')
    with patch(f'{INCUS_UTILS}.incus_create_info_module', return_value=module), \
         patch(f'{INCUS_UTILS}.incus_create_client', return_value=client):
        main_func()
    module.exit_json.assert_called_once_with(**{return_key: []})


def assert_info_all(
    main_func: collections.abc.Callable[[], None], return_key: str,
    items: list[dict[str, Any]], *, project: str | None = 'default',
) -> None:
    """Call info main and assert all resources returned."""
    module = _info_module(None, project)
    client = mock_incus_client()
    client.get.return_value = {'metadata': items}
    with patch(f'{INCUS_UTILS}.incus_create_info_module', return_value=module), \
         patch(f'{INCUS_UTILS}.incus_create_client', return_value=client):
        main_func()
    result = module.exit_json.call_args[1][return_key]
    assert len(result) == len(items)


def assert_info_fail(
    main_func: collections.abc.Callable[[], None], *,
    project: str | None = 'default',
) -> None:
    """Call info main and assert failure on client exception."""
    module = _info_module(None, project)
    client = mock_incus_client()
    client.get.side_effect = IncusClientException('connection refused')
    with patch(f'{INCUS_UTILS}.incus_create_info_module', return_value=module), \
         patch(f'{INCUS_UTILS}.incus_create_client', return_value=client):
        main_func()
    module.fail_json.assert_called_once_with(msg='connection refused')


def assert_write_create(
    main_func: collections.abc.Callable[[], None], module_path: str, module: MagicMock,
) -> MagicMock:
    """Call write main with not-found resource and assert created."""
    client = mock_incus_client()
    client.get.side_effect = IncusNotFoundException('not found')
    client.post.return_value = {'type': 'sync'}
    with _write_patches(module_path, module, client):
        main_func()
    module.exit_json.assert_called_once_with(changed=True)
    client.post.assert_called_once()
    return client


def assert_write_skip(
    main_func: collections.abc.Callable[[], None], module_path: str,
    module: MagicMock, current: dict[str, Any],
) -> None:
    """Call write main with matching resource and assert no change."""
    client = mock_incus_client()
    client.get.return_value = {'metadata': current}
    with _write_patches(module_path, module, client):
        main_func()
    module.exit_json.assert_called_once_with(changed=False)


def assert_write_update(
    main_func: collections.abc.Callable[[], None], module_path: str,
    module: MagicMock, current: dict[str, Any] | list[dict[str, Any]],
) -> dict[str, Any]:
    """Call write main with changed resource and assert updated."""
    client = mock_incus_client()
    if isinstance(current, list):
        client.get.side_effect = current
    else:
        client.get.return_value = {'metadata': current}
    client.put.return_value = {'type': 'sync'}
    with _write_patches(module_path, module, client):
        main_func()
    module.exit_json.assert_called_once_with(changed=True)
    client.put.assert_called_once()
    put_data: dict[str, Any] = client.put.call_args[0][1]
    return put_data


def assert_write_delete(
    main_func: collections.abc.Callable[[], None], module_path: str,
    module: MagicMock, current: dict[str, Any] | None = None,
) -> MagicMock:
    """Call write main and assert resource deleted."""
    client = mock_incus_client()
    client.get.return_value = {'metadata': current or {'description': '', 'config': {}}}
    client.delete.return_value = {'type': 'sync'}
    with _write_patches(module_path, module, client):
        main_func()
    module.exit_json.assert_called_once_with(changed=True)
    client.delete.assert_called_once()
    return client


def assert_write_delete_missing(
    main_func: collections.abc.Callable[[], None], module_path: str, module: MagicMock,
) -> None:
    """Call write main and assert skip for missing resource."""
    client = mock_incus_client()
    client.get.side_effect = IncusNotFoundException('not found')
    with _write_patches(module_path, module, client):
        main_func()
    module.exit_json.assert_called_once_with(changed=False)


def assert_write_check_mode(
    main_func: collections.abc.Callable[[], None], module_path: str, module: MagicMock,
) -> None:
    """Call write main in check mode and assert no API calls."""
    client = mock_incus_client()
    client.get.side_effect = IncusNotFoundException('not found')
    with _write_patches(module_path, module, client):
        main_func()
    module.exit_json.assert_called_once_with(changed=True)
    client.post.assert_not_called()


def assert_write_fail_create(
    main_func: collections.abc.Callable[[], None], module_path: str, module: MagicMock,
) -> None:
    """Call write main and assert fail_json for missing required param."""
    module.fail_json.side_effect = SystemExit(1)
    client = mock_incus_client()
    client.get.side_effect = IncusNotFoundException('not found')
    with pytest.raises(SystemExit):
        with _write_patches(module_path, module, client):
            main_func()
    module.fail_json.assert_called_once()


def run_module_main(
    module_path: str, module: MagicMock, client: MagicMock,
    main_func: collections.abc.Callable[[], None],
) -> None:
    """Patch write module factory and client, then run main."""
    with _write_patches(module_path, module, client):
        main_func()
