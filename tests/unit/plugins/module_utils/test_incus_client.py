# -*- coding: utf-8 -*-
# Copyright: Roman Kuzmitskii <ansible@damex.org>
# SPDX-License-Identifier: GPL-3.0-or-later

"""Tests for IncusClient."""

from __future__ import annotations

import http.client
from unittest.mock import MagicMock, patch

import pytest

from ansible_collections.damex.incus.plugins.module_utils.incus import (
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
