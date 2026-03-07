# -*- coding: utf-8 -*-
# Copyright: Roman Kuzmitskii <ansible@damex.org>
# SPDX-License-Identifier: GPL-3.0-or-later

"""Tests for incus module utilities."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from ansible_collections.damex.incus.plugins.module_utils.incus import (
    IncusClient,
    IncusClientException,
    IncusNotFoundException,
    incus_build_source,
    incus_ensure_resource,
    incus_run_write_module,
    incus_stringify_config,
    incus_stringify_instance_config,
    incus_wait,
)
from ansible_collections.damex.incus.tests.unit.conftest import CONNECTION_PARAMS

__all__ = [
    'test_stringify_config_empty',
    'test_stringify_config_none',
    'test_stringify_config_string_values',
    'test_stringify_config_int_values',
    'test_stringify_config_bool_true',
    'test_stringify_config_bool_false',
    'test_stringify_config_mixed',
    'test_stringify_config_skips_none_values',
    'test_stringify_instance_config_empty',
    'test_stringify_instance_config_none',
    'test_stringify_instance_config_string_values',
    'test_stringify_instance_config_bool_values',
    'test_stringify_instance_config_skips_none_values',
    'test_stringify_instance_config_cloud_init_user_data_dict',
    'test_stringify_instance_config_cloud_init_vendor_data_dict',
    'test_stringify_instance_config_non_cloud_init_dict',
    'test_stringify_instance_config_list_value',
    'test_client_default_socket_path',
    'test_client_custom_socket_path',
    'test_client_url_parsing',
    'test_client_url_default_port',
    'test_client_headers_without_token',
    'test_client_headers_with_token',
    'test_client_wait_sync_noop',
    'test_client_wait_async',
    'test_client_request_error_response',
    'test_client_request_404_response',
    'test_client_request_success',
    'test_build_source_known_remote',
    'test_build_source_ubuntu_remote',
    'test_build_source_explicit_server',
    'test_build_source_local_alias',
    'test_build_source_unknown_remote_fails',
    'test_wait_true',
    'test_wait_false',
    'test_wait_default',
    'test_run_write_module_success_changed',
    'test_run_write_module_success_unchanged',
    'test_run_write_module_client_exception',
    'test_ensure_resource_create',
    'test_ensure_resource_no_change',
    'test_ensure_resource_update',
    'test_ensure_resource_delete_exists',
    'test_ensure_resource_delete_not_exists',
    'test_ensure_resource_check_mode_create',
    'test_ensure_resource_project_query',
    'test_ensure_resource_create_only_params',
]


def test_stringify_config_empty() -> None:
    """Return empty dict for empty input."""
    assert not incus_stringify_config({})


def test_stringify_config_none() -> None:
    """Return empty dict for None."""
    assert not incus_stringify_config(None)


def test_stringify_config_string_values() -> None:
    """Preserve string values."""
    assert incus_stringify_config({'limits.cpu': '2'}) == {'limits.cpu': '2'}


def test_stringify_config_int_values() -> None:
    """Stringify int values."""
    assert incus_stringify_config({'limits.cpu': 4}) == {'limits.cpu': '4'}


def test_stringify_config_bool_true() -> None:
    """Stringify True to 'true'."""
    assert incus_stringify_config({'boot.autostart': True}) == {'boot.autostart': 'true'}


def test_stringify_config_bool_false() -> None:
    """Stringify False to 'false'."""
    assert incus_stringify_config({'boot.autostart': False}) == {'boot.autostart': 'false'}


def test_stringify_config_mixed() -> None:
    """Stringify mixed types."""
    result = incus_stringify_config({
        'limits.cpu': 2,
        'limits.memory': '4GiB',
        'boot.autostart': True,
    })
    assert result == {
        'limits.cpu': '2',
        'limits.memory': '4GiB',
        'boot.autostart': 'true',
    }


def test_stringify_config_skips_none_values() -> None:
    """Skip None values from unset options."""
    result = incus_stringify_config({
        'limits.cpu': '2',
        'boot.autostart': None,
        'limits.memory': None,
    })
    assert result == {'limits.cpu': '2'}


def test_stringify_instance_config_empty() -> None:
    """Return empty dict for empty input."""
    assert not incus_stringify_instance_config({})


def test_stringify_instance_config_none() -> None:
    """Return empty dict for None."""
    assert not incus_stringify_instance_config(None)


def test_stringify_instance_config_string_values() -> None:
    """Preserve string values."""
    assert incus_stringify_instance_config({'limits.cpu': '2'}) == {'limits.cpu': '2'}


def test_stringify_instance_config_bool_values() -> None:
    """Stringify bool values."""
    assert incus_stringify_instance_config({'boot.autostart': True}) == {'boot.autostart': 'true'}


def test_stringify_instance_config_skips_none_values() -> None:
    """Skip None values from unset options."""
    result = incus_stringify_instance_config({
        'limits.cpu': '2',
        'boot.autostart': None,
        'security.nesting': None,
        'security.privileged': True,
    })
    assert result == {'limits.cpu': '2', 'security.privileged': 'true'}


def test_stringify_instance_config_cloud_init_user_data_dict() -> None:
    """Prefix cloud-init user-data dict."""
    config = {'cloud-init.user-data': {'packages': ['vim']}}
    result = incus_stringify_instance_config(config)
    assert result['cloud-init.user-data'].startswith('#cloud-config\n')
    assert 'packages' in result['cloud-init.user-data']


def test_stringify_instance_config_cloud_init_vendor_data_dict() -> None:
    """Prefix cloud-init vendor-data dict."""
    config = {'cloud-init.vendor-data': {'packages': ['curl']}}
    result = incus_stringify_instance_config(config)
    assert result['cloud-init.vendor-data'].startswith('#cloud-config\n')


def test_stringify_instance_config_non_cloud_init_dict() -> None:
    """Skip prefix for non-cloud-init dict."""
    config = {'cloud-init.network-config': {'version': 2}}
    result = incus_stringify_instance_config(config)
    assert not result['cloud-init.network-config'].startswith('#cloud-config')


def test_stringify_instance_config_list_value() -> None:
    """Prefix cloud-init list value."""
    config = {'cloud-init.user-data': ['item1', 'item2']}
    result = incus_stringify_instance_config(config)
    assert result['cloud-init.user-data'].startswith('#cloud-config\n')


def test_client_default_socket_path() -> None:
    """Set default socket path."""
    client = IncusClient()
    assert client.socket_path == '/var/lib/incus/unix.socket'
    assert client.url is None


def test_client_custom_socket_path() -> None:
    """Set custom socket path."""
    client = IncusClient(socket_path='/tmp/test.sock')
    assert client.socket_path == '/tmp/test.sock'


def test_client_url_parsing() -> None:
    """Parse URL host and port."""
    client = IncusClient(url='https://incus.example.com:9443')
    assert client.host == 'incus.example.com'
    assert client.port == 9443


def test_client_url_default_port() -> None:
    """Default to port 8443."""
    client = IncusClient(url='https://incus.example.com')
    assert client.port == 8443


def test_client_headers_without_token() -> None:
    """Omit Authorization without token."""
    client = IncusClient()
    mock_conn = MagicMock()
    mock_response = MagicMock()
    mock_response.read.return_value = b'{"type":"sync","metadata":{}}'
    mock_conn.getresponse.return_value = mock_response

    with patch.object(client, '_connection', return_value=mock_conn):
        client.get('/1.0')
        headers = mock_conn.request.call_args[1]['headers']
        assert headers['Content-Type'] == 'application/json'
        assert 'Authorization' not in headers


def test_client_headers_with_token() -> None:
    """Include Bearer token."""
    client = IncusClient(token='secret')
    mock_conn = MagicMock()
    mock_response = MagicMock()
    mock_response.read.return_value = b'{"type":"sync","metadata":{}}'
    mock_conn.getresponse.return_value = mock_response

    with patch.object(client, '_connection', return_value=mock_conn):
        client.get('/1.0')
        headers = mock_conn.request.call_args[1]['headers']
        assert headers['Authorization'] == 'Bearer secret'


def test_client_wait_sync_noop() -> None:
    """Skip wait for sync response."""
    client = IncusClient()
    with patch.object(client, '_request') as mock_req:
        client.wait({'type': 'sync'})
        mock_req.assert_not_called()


def test_client_wait_async() -> None:
    """Wait for async operation."""
    client = IncusClient()
    with patch.object(client, '_request') as mock_req:
        client.wait({'type': 'async', 'metadata': {'id': 'op-123'}})
        mock_req.assert_called_once_with('GET', '/1.0/operations/op-123/wait')


def test_client_request_error_response() -> None:
    """Raise IncusClientException on error."""
    client = IncusClient()
    mock_conn = MagicMock()
    mock_response = MagicMock()
    mock_response.read.return_value = b'{"type":"error","error_code":500,"error":"server error"}'
    mock_conn.getresponse.return_value = mock_response

    with patch.object(client, '_connection', return_value=mock_conn):
        with pytest.raises(IncusClientException, match='server error'):
            client.get('/1.0/test')


def test_client_request_404_response() -> None:
    """Raise IncusNotFoundException on 404."""
    client = IncusClient()
    mock_conn = MagicMock()
    mock_response = MagicMock()
    mock_response.read.return_value = b'{"type":"error","error_code":404,"error":"not found"}'
    mock_conn.getresponse.return_value = mock_response

    with patch.object(client, '_connection', return_value=mock_conn):
        with pytest.raises(IncusNotFoundException, match='not found'):
            client.get('/1.0/test')


def test_client_request_success() -> None:
    """Return parsed JSON on success."""
    client = IncusClient()
    mock_conn = MagicMock()
    mock_response = MagicMock()
    mock_response.read.return_value = b'{"type":"sync","metadata":{"name":"test"}}'
    mock_conn.getresponse.return_value = mock_response

    with patch.object(client, '_connection', return_value=mock_conn):
        result = client.get('/1.0/test')
        assert result['metadata']['name'] == 'test'


def test_build_source_known_remote() -> None:
    """Resolve known remote."""
    module = MagicMock()
    module.params = {'source': 'images:debian/13', 'source_server': None, 'source_protocol': None}
    result = incus_build_source(module)
    assert result['alias'] == 'debian/13'
    assert result['server'] == 'https://images.linuxcontainers.org'
    assert result['protocol'] == 'simplestreams'


def test_build_source_ubuntu_remote() -> None:
    """Resolve ubuntu remote."""
    module = MagicMock()
    module.params = {'source': 'ubuntu:24.04', 'source_server': None, 'source_protocol': None}
    result = incus_build_source(module)
    assert result['alias'] == '24.04'
    assert result['server'] == 'https://cloud-images.ubuntu.com/releases'


def test_build_source_explicit_server() -> None:
    """Override remote with explicit server."""
    module = MagicMock()
    module.params = {
        'source': 'images:debian/13',
        'source_server': 'https://custom.example.com',
        'source_protocol': 'lxd',
    }
    result = incus_build_source(module)
    assert result['server'] == 'https://custom.example.com'
    assert result['protocol'] == 'lxd'


def test_build_source_local_alias() -> None:
    """Omit server for local alias."""
    module = MagicMock()
    module.params = {'source': 'my-image', 'source_server': None, 'source_protocol': None}
    result = incus_build_source(module)
    assert result['alias'] == 'my-image'
    assert 'server' not in result


def test_build_source_unknown_remote_fails() -> None:
    """Fail on unknown remote."""
    module = MagicMock()
    module.params = {'source': 'unknown:image', 'source_server': None, 'source_protocol': None}
    incus_build_source(module)
    module.fail_json.assert_called_once()


def test_wait_true() -> None:
    """Call client.wait when enabled."""
    module = MagicMock()
    module.params = {'wait': True}
    client = MagicMock()
    response = {'type': 'async', 'metadata': {'id': 'op-1'}}
    incus_wait(module, client, response)
    client.wait.assert_called_once_with(response)


def test_wait_false() -> None:
    """Skip client.wait when disabled."""
    module = MagicMock()
    module.params = {'wait': False}
    client = MagicMock()
    incus_wait(module, client, {'type': 'async', 'metadata': {'id': 'op-1'}})
    client.wait.assert_not_called()


def test_wait_default() -> None:
    """Default wait to True."""
    module = MagicMock()
    module.params = {}
    client = MagicMock()
    response = {'type': 'async', 'metadata': {'id': 'op-1'}}
    incus_wait(module, client, response)
    client.wait.assert_called_once_with(response)


def test_run_write_module_success_changed() -> None:
    """Exit changed on success."""
    module = MagicMock()
    incus_run_write_module(module, lambda: True)
    module.exit_json.assert_called_once_with(changed=True)


def test_run_write_module_success_unchanged() -> None:
    """Exit unchanged on no-op."""
    module = MagicMock()
    incus_run_write_module(module, lambda: False)
    module.exit_json.assert_called_once_with(changed=False)


def test_run_write_module_client_exception() -> None:
    """Fail on client exception."""
    module = MagicMock()

    def _raise() -> bool:
        raise IncusClientException('api error')

    incus_run_write_module(module, _raise)
    module.fail_json.assert_called_once_with(msg='api error')


def _ensure_module(
    name: str = 'test', state: str = 'present',
    project: str | None = None, check_mode: bool = False,
) -> MagicMock:
    """Build mock module."""
    module = MagicMock()
    module.params = {
        **CONNECTION_PARAMS,
        'name': name,
        'state': state,
    }
    if project:
        module.params['project'] = project
    module.check_mode = check_mode
    return module


@patch('ansible_collections.damex.incus.plugins.module_utils.incus.incus_create_client')
def test_ensure_resource_create(mock_create_client: MagicMock) -> None:
    """Create missing resource."""
    client = MagicMock()
    client.get.side_effect = IncusNotFoundException('not found')
    client.post.return_value = {'type': 'sync'}
    mock_create_client.return_value = client

    module = _ensure_module()
    desired = {'description': '', 'config': {}}
    result = incus_ensure_resource(module, 'projects', desired)

    assert result is True
    client.post.assert_called_once()


@patch('ansible_collections.damex.incus.plugins.module_utils.incus.incus_create_client')
def test_ensure_resource_no_change(mock_create_client: MagicMock) -> None:
    """Skip matching resource."""
    client = MagicMock()
    client.get.return_value = {'metadata': {'description': 'desc', 'config': {'k': 'v'}}}
    mock_create_client.return_value = client

    module = _ensure_module()
    desired = {'description': 'desc', 'config': {'k': 'v'}}
    result = incus_ensure_resource(module, 'projects', desired)

    assert result is False


@patch('ansible_collections.damex.incus.plugins.module_utils.incus.incus_create_client')
def test_ensure_resource_update(mock_create_client: MagicMock) -> None:
    """Update changed resource."""
    client = MagicMock()
    client.get.return_value = {'metadata': {'description': 'old', 'config': {}}}
    client.put.return_value = {'type': 'sync'}
    mock_create_client.return_value = client

    module = _ensure_module()
    desired = {'description': 'new', 'config': {}}
    result = incus_ensure_resource(module, 'projects', desired)

    assert result is True
    client.put.assert_called_once()


@patch('ansible_collections.damex.incus.plugins.module_utils.incus.incus_create_client')
def test_ensure_resource_delete_exists(mock_create_client: MagicMock) -> None:
    """Delete existing resource."""
    client = MagicMock()
    client.get.return_value = {'metadata': {'description': '', 'config': {}}}
    client.delete.return_value = {'type': 'sync'}
    mock_create_client.return_value = client

    module = _ensure_module(state='absent')
    result = incus_ensure_resource(module, 'projects', {'description': '', 'config': {}})

    assert result is True
    client.delete.assert_called_once()


@patch('ansible_collections.damex.incus.plugins.module_utils.incus.incus_create_client')
def test_ensure_resource_delete_not_exists(mock_create_client: MagicMock) -> None:
    """Skip deleting missing resource."""
    client = MagicMock()
    client.get.side_effect = IncusNotFoundException('not found')
    mock_create_client.return_value = client

    module = _ensure_module(state='absent')
    result = incus_ensure_resource(module, 'projects', {'description': '', 'config': {}})

    assert result is False


@patch('ansible_collections.damex.incus.plugins.module_utils.incus.incus_create_client')
def test_ensure_resource_check_mode_create(mock_create_client: MagicMock) -> None:
    """Skip create in check mode."""
    client = MagicMock()
    client.get.side_effect = IncusNotFoundException('not found')
    mock_create_client.return_value = client

    module = _ensure_module(check_mode=True)
    result = incus_ensure_resource(module, 'projects', {'description': '', 'config': {}})

    assert result is True
    client.post.assert_not_called()


@patch('ansible_collections.damex.incus.plugins.module_utils.incus.incus_create_client')
def test_ensure_resource_project_query(mock_create_client: MagicMock) -> None:
    """Add project query param."""
    client = MagicMock()
    client.get.side_effect = IncusNotFoundException('not found')
    client.post.return_value = {'type': 'sync'}
    mock_create_client.return_value = client

    module = _ensure_module(project='myproject')
    desired = {'description': '', 'config': {}}
    incus_ensure_resource(module, 'networks', desired)

    client.get.assert_called_with('/1.0/networks/test?project=myproject')
    client.post.assert_called_once()
    args = client.post.call_args
    assert '?project=myproject' in args[0][0]


@patch('ansible_collections.damex.incus.plugins.module_utils.incus.incus_create_client')
def test_ensure_resource_create_only_params(mock_create_client: MagicMock) -> None:
    """Include create-only params."""
    client = MagicMock()
    client.get.side_effect = IncusNotFoundException('not found')
    client.post.return_value = {'type': 'sync'}
    mock_create_client.return_value = client

    module = _ensure_module()
    module.params['driver'] = 'zfs'
    desired = {'description': '', 'config': {}}
    incus_ensure_resource(module, 'storage-pools', desired, ['driver'])

    post_data = client.post.call_args[0][1]
    assert post_data['driver'] == 'zfs'
