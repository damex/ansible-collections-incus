# -*- coding: utf-8 -*-
# Copyright: Roman Kuzmitskii <ansible@damex.org>
# SPDX-License-Identifier: GPL-3.0-or-later

"""Tests for IncusClient."""

from __future__ import annotations

import collections.abc
import http.client
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from ansible_collections.damex.incus.plugins.module_utils.incus_client import (
    IncusClient,
    IncusClientException,
    IncusConnectionParameters,
    IncusNotFoundException,
)

__all__ = [
    'test_client_default_socket_path',
    'test_client_custom_socket_path',
    'test_client_url_parsing',
    'test_client_url_default_port',
    'test_client_headers_without_token',
    'test_client_headers_with_token',
    'test_client_wait_sync_noop',
    'test_client_wait_async',
    'test_client_wait_async_encodes_operation_id',
    'test_client_wait_async_failure',
    'test_client_wait_async_success',
    'test_client_request_error_response',
    'test_client_request_404_response',
    'test_client_request_success',
    'test_client_retry_on_stale_connection',
    'test_client_retry_fails_with_exception',
    'test_client_retry_fails_with_client_exception',
    'test_client_no_retry_on_non_socket_error',
    'test_client_request_serializes_json',
    'test_client_request_none_body',
    'test_client_post_sends_data',
    'test_client_post_without_data',
    'test_client_put_sends_data',
    'test_client_patch_sends_data',
    'test_client_delete_sends_no_data',
    'test_client_post_file_sends_binary',
    'test_client_post_file_public_header',
    'test_client_post_file_token_header',
    'test_client_context_manager_closes',
    'test_client_close_removes_temp_files',
]


def test_client_default_socket_path() -> None:
    """Set default socket path."""
    client = IncusClient()
    assert client.parameters.socket_path == '/var/lib/incus/unix.socket'
    assert client.parameters.url is None


def test_client_custom_socket_path() -> None:
    """Set custom socket path."""
    client = IncusClient(IncusConnectionParameters(socket_path='/tmp/test.sock'))
    assert client.parameters.socket_path == '/tmp/test.sock'


def test_client_url_parsing() -> None:
    """Parse URL host and port."""
    client = IncusClient(IncusConnectionParameters(url='https://incus.example.com:9443'))
    assert client.host == 'incus.example.com'
    assert client.port == 9443


def test_client_url_default_port() -> None:
    """Default to port 8443."""
    client = IncusClient(IncusConnectionParameters(url='https://incus.example.com'))
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
    client = IncusClient(IncusConnectionParameters(token='secret'))
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


def test_client_wait_async_encodes_operation_id() -> None:
    """Encode special characters in operation id."""
    client = IncusClient()
    with patch.object(client, '_request') as mock_req:
        client.wait({'type': 'async', 'metadata': {'id': 'op/special&id'}})
        mock_req.assert_called_once_with('GET', '/1.0/operations/op%2Fspecial%26id/wait')


def test_client_wait_async_failure() -> None:
    """Raise on failed async operation."""
    client = IncusClient()
    response = {'type': 'async', 'metadata': {'id': 'op-fail'}}
    wait_result = {'metadata': {'status': 'Failure', 'err': 'image not found'}}
    with patch.object(client, '_request', return_value=wait_result):
        with pytest.raises(IncusClientException, match='image not found'):
            client.wait(response)


def test_client_wait_async_success() -> None:
    """Complete without error on successful operation."""
    client = IncusClient()
    response = {'type': 'async', 'metadata': {'id': 'op-ok'}}
    wait_result = {'metadata': {'status': 'Success'}}
    with patch.object(client, '_request', return_value=wait_result):
        client.wait(response)


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


def test_client_retry_on_stale_connection() -> None:
    """Retry once on stale connection and succeed."""
    client = IncusClient()

    with patch.object(client, '_send', side_effect=[OSError('connection reset'), {'type': 'sync', 'metadata': {}}]), \
         patch.object(client, '_close') as mock_close:
        result = client.get('/1.0/test')
        assert result['type'] == 'sync'
        mock_close.assert_called_once()


def test_client_retry_fails_with_exception() -> None:
    """Raise IncusClientException when retry also fails."""
    client = IncusClient()

    errors = [http.client.HTTPException('broken pipe'), ValueError('retry failed')]
    with patch.object(client, '_send', side_effect=errors), \
         patch.object(client, '_close'), \
         pytest.raises(IncusClientException, match='retry failed'):
        client.get('/1.0/test')


def test_client_retry_fails_with_client_exception() -> None:
    """Re-raise IncusClientException from retry directly."""
    client = IncusClient()

    with patch.object(client, '_send', side_effect=[OSError('reset'), IncusNotFoundException('not found')]), \
         patch.object(client, '_close'), \
         pytest.raises(IncusNotFoundException, match='not found'):
        client.get('/1.0/test')


def test_client_no_retry_on_non_socket_error() -> None:
    """Raise IncusClientException without retry for non-socket errors."""
    client = IncusClient()

    with patch.object(client, '_send', side_effect=ValueError('bad data')), \
         patch.object(client, '_close') as mock_close, \
         pytest.raises(IncusClientException, match='bad data'):
        client.get('/1.0/test')
    mock_close.assert_called_once()


def _capture_execute() -> tuple[dict[str, Any], collections.abc.Callable[..., dict[str, Any]]]:
    """
    Build capture dict and side_effect for _execute calls.

    >>> _capture_execute()
    """
    captured: dict[str, Any] = {}

    def side_effect(
        method: str,
        path: str,
        body: str | bytes | None,
        headers: dict[str, str],
    ) -> dict[str, Any]:
        """Capture execute arguments."""
        captured['method'] = method
        captured['path'] = path
        captured['body'] = body
        captured['headers'] = headers
        return {'type': 'sync'}

    return captured, side_effect


def test_client_request_serializes_json() -> None:
    """Verify _request serializes data dict as JSON string."""
    client = IncusClient()
    captured, side_effect = _capture_execute()
    with patch.object(client, '_execute', side_effect=side_effect):
        client._request('POST', '/1.0/test', {'name': 'web'})
        assert captured['body'] == '{"name": "web"}'


def test_client_request_none_body() -> None:
    """Verify _request sends None body when no data provided."""
    client = IncusClient()
    captured, side_effect = _capture_execute()
    with patch.object(client, '_execute', side_effect=side_effect):
        client._request('GET', '/1.0/test')
        assert captured['body'] is None


def test_client_post_sends_data() -> None:
    """Verify POST delegates with correct method and data."""
    client = IncusClient()
    with patch.object(client, '_request', return_value={'type': 'sync'}) as mock_request:
        client.post('/1.0/instances', {'name': 'web'})
        mock_request.assert_called_once_with('POST', '/1.0/instances', {'name': 'web'})


def test_client_post_without_data() -> None:
    """Verify POST with no data sends None."""
    client = IncusClient()
    with patch.object(client, '_request', return_value={'type': 'sync'}) as mock_request:
        client.post('/1.0/instances')
        mock_request.assert_called_once_with('POST', '/1.0/instances', None)


def test_client_put_sends_data() -> None:
    """Verify PUT delegates with correct method and data."""
    client = IncusClient()
    with patch.object(client, '_request', return_value={'type': 'sync'}) as mock_request:
        client.put('/1.0/instances/web', {'description': 'updated'})
        mock_request.assert_called_once_with('PUT', '/1.0/instances/web', {'description': 'updated'})


def test_client_patch_sends_data() -> None:
    """Verify PATCH delegates with correct method and data."""
    client = IncusClient()
    with patch.object(client, '_request', return_value={'type': 'sync'}) as mock_request:
        client.patch('/1.0/instances/web', {'description': 'patched'})
        mock_request.assert_called_once_with('PATCH', '/1.0/instances/web', {'description': 'patched'})


def test_client_delete_sends_no_data() -> None:
    """Verify DELETE delegates with no data."""
    client = IncusClient()
    with patch.object(client, '_request', return_value={'type': 'sync'}) as mock_request:
        client.delete('/1.0/instances/web')
        mock_request.assert_called_once_with('DELETE', '/1.0/instances/web')


def test_client_post_file_sends_binary() -> None:
    """Verify post_file reads file and sends as octet-stream."""
    client = IncusClient()
    file_content = b'fake image data'
    captured, side_effect = _capture_execute()
    with patch('builtins.open', return_value=MagicMock(
        __enter__=MagicMock(return_value=MagicMock(read=MagicMock(return_value=file_content))),
        __exit__=MagicMock(return_value=False),
    )):
        with patch.object(client, '_execute', side_effect=side_effect):
            client.post_file('/1.0/images', '/tmp/image.tar.gz')
            assert captured['method'] == 'POST'
            assert captured['path'] == '/1.0/images'
            assert captured['body'] == file_content
            assert captured['headers']['Content-Type'] == 'application/octet-stream'
            assert captured['headers']['X-Incus-filename'] == 'image.tar.gz'
            assert 'X-Incus-public' not in captured['headers']


def test_client_post_file_public_header() -> None:
    """Verify post_file adds public header when requested."""
    client = IncusClient()
    captured, side_effect = _capture_execute()
    with patch('builtins.open', return_value=MagicMock(
        __enter__=MagicMock(return_value=MagicMock(read=MagicMock(return_value=b'data'))),
        __exit__=MagicMock(return_value=False),
    )):
        with patch.object(client, '_execute', side_effect=side_effect):
            client.post_file('/1.0/images', '/tmp/image.tar.gz', public=True)
            assert captured['headers']['X-Incus-public'] == '1'


def test_client_post_file_token_header() -> None:
    """Verify post_file includes Bearer token."""
    client = IncusClient(IncusConnectionParameters(token='secret'))
    captured, side_effect = _capture_execute()
    with patch('builtins.open', return_value=MagicMock(
        __enter__=MagicMock(return_value=MagicMock(read=MagicMock(return_value=b'data'))),
        __exit__=MagicMock(return_value=False),
    )):
        with patch.object(client, '_execute', side_effect=side_effect):
            client.post_file('/1.0/images', '/tmp/image.tar.gz')
            assert captured['headers']['Authorization'] == 'Bearer secret'


def test_client_context_manager_closes() -> None:
    """Verify context manager calls close on exit."""
    client = IncusClient()
    with patch.object(client, 'close') as mock_close:
        with client:
            pass
        mock_close.assert_called_once()


def test_client_close_removes_temp_files() -> None:
    """Verify close removes temporary files."""
    client = IncusClient()
    temp_files = ['/tmp/fake1.pem', '/tmp/fake2.pem']
    setattr(client, '_temp_files', temp_files)
    with patch.object(client, '_close'), \
         patch('os.unlink') as mock_unlink:
        client.close()
        assert mock_unlink.call_count == 2
    assert not getattr(client, '_temp_files')
