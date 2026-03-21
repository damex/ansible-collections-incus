# -*- coding: utf-8 -*-
# Copyright: Roman Kuzmitskii <ansible@damex.org>
# SPDX-License-Identifier: GPL-3.0-or-later

"""
Incus API client.
"""

from __future__ import annotations

import http.client
import json
import os
import socket
import ssl
import tempfile
from typing import Any, NamedTuple
from urllib.parse import quote, urlparse

from ansible.module_utils.basic import AnsibleModule

__all__ = [
    'INCUS_SOCKET_PATH',
    'IncusClient',
    'IncusClientException',
    'IncusConnectionParameters',
    'IncusNotFoundException',
    'incus_create_client',
]

INCUS_SOCKET_PATH = '/var/lib/incus/unix.socket'


class IncusClientException(Exception):
    """
    API error.
    """


class IncusNotFoundException(IncusClientException):
    """
    Resource not found.
    """


class _UnixSocketHTTPConnection(http.client.HTTPConnection):
    """
    HTTP over Unix socket.
    """

    def __init__(self, socket_path: str) -> None:
        """
        Set socket path.

        >>> conn = _UnixSocketHTTPConnection('/run/incus/unix.socket')
        """
        super().__init__('localhost')
        self.socket_path = socket_path

    def connect(self) -> None:
        """
        Connect to socket.

        >>> conn.connect()
        """
        self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.sock.connect(self.socket_path)


class IncusConnectionParameters(NamedTuple):
    """
    Connection parameters for Incus API.

    >>> params = IncusConnectionParameters()
    >>> params.socket_path
    '/var/lib/incus/unix.socket'
    """

    socket_path: str = INCUS_SOCKET_PATH
    url: str | None = None
    client_cert: str | None = None
    client_key: str | None = None
    server_cert: str | None = None
    client_cert_path: str | None = None
    client_key_path: str | None = None
    server_cert_path: str | None = None
    token: str | None = None
    validate_certs: bool = True


class IncusClient:
    """
    Incus API client.
    """

    def __init__(self, parameters: IncusConnectionParameters | None = None) -> None:
        """
        Set connection parameters.

        >>> client = IncusClient()
        """
        self.parameters = parameters or IncusConnectionParameters()
        self.host: str | None = None
        self.port: int = 8443
        self._conn: http.client.HTTPConnection | None = None
        self._temp_files: list[str] = []

        if self.parameters.url:
            parsed = urlparse(self.parameters.url)
            self.host = parsed.hostname
            self.port = parsed.port or 8443

    def _write_temp_file(self, content: str) -> str:
        """
        Write content to temporary file.

        >>> client._write_temp_file('cert content')
        '/tmp/tmpXXXXXX.pem'
        """
        with tempfile.NamedTemporaryFile(mode='w', suffix='.pem', delete=False) as temp_file:
            temp_file.write(content)
            self._temp_files.append(temp_file.name)
            return temp_file.name

    def _build_ssl_context(self) -> ssl.SSLContext:
        """
        Build SSL context.

        >>> client._build_ssl_context()
        <ssl.SSLContext object>
        """
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        if not self.parameters.validate_certs:
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
        if self.parameters.server_cert:
            context.load_verify_locations(cadata=self.parameters.server_cert)
        elif self.parameters.server_cert_path:
            context.load_verify_locations(self.parameters.server_cert_path)
        if self.parameters.client_cert and self.parameters.client_key:
            context.load_cert_chain(
                self._write_temp_file(self.parameters.client_cert),
                self._write_temp_file(self.parameters.client_key),
            )
        elif self.parameters.client_cert_path and self.parameters.client_key_path:
            context.load_cert_chain(
                self.parameters.client_cert_path,
                self.parameters.client_key_path,
            )
        return context

    def _connect(self) -> http.client.HTTPConnection:
        """
        Create connection.

        >>> client._connect()
        <_UnixSocketHTTPConnection object>
        """
        if self.parameters.url:
            context = self._build_ssl_context()
            if self.host is None:
                raise IncusClientException('URL provided but hostname could not be parsed')
            return http.client.HTTPSConnection(self.host, self.port, context=context)
        return _UnixSocketHTTPConnection(self.parameters.socket_path)

    def _connection(self) -> http.client.HTTPConnection:
        """
        Get connection.

        >>> client._connection()
        <_UnixSocketHTTPConnection object>
        """
        if self._conn is None:
            self._conn = self._connect()
        return self._conn

    def _close(self) -> None:
        """
        Close connection.

        >>> client._close()
        """
        if self._conn is not None:
            self._conn.close()
            self._conn = None

    def close(self) -> None:
        """
        Close connection and clean up temporary files.

        >>> client.close()
        """
        self._close()
        for temp_path in self._temp_files:
            try:
                os.unlink(temp_path)
            except OSError:
                pass
        self._temp_files.clear()

    def __enter__(self) -> IncusClient:
        """
        Enter context.

        >>> with IncusClient() as client:
        ...     pass
        """
        return self

    def __exit__(
        self,
        exception_type: type[BaseException] | None,
        exception_value: BaseException | None,
        exception_traceback: object,
    ) -> None:
        """
        Exit context and clean up.

        >>> client.__exit__(None, None, None)
        """
        self.close()

    def _headers(self) -> dict[str, str]:
        """
        Build headers.

        >>> client._headers()
        {'Content-Type': 'application/json', 'Accept': 'application/json'}
        """
        headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
        if self.parameters.token:
            headers['Authorization'] = f'Bearer {self.parameters.token}'
        return headers

    def _send(
        self,
        method: str,
        path: str,
        body: str | bytes | None,
        headers: dict[str, str],
    ) -> dict[str, Any]:
        """
        Execute request.

        >>> client._send('GET', '/1.0', None, {})
        {'type': 'sync', 'status': 'Success', 'metadata': {...}}
        """
        conn = self._connection()
        conn.request(method, path, body=body, headers=headers)
        response = conn.getresponse()
        result: dict[str, Any] = json.loads(response.read().decode('utf-8'))
        return result

    def _execute(
        self,
        method: str,
        path: str,
        body: str | bytes | None,
        headers: dict[str, str],
    ) -> dict[str, Any]:
        """
        Execute request with retry.

        >>> client._execute('GET', '/1.0', None, {})
        {'type': 'sync', 'status': 'Success', 'metadata': {...}}
        """
        try:
            content = self._send(method, path, body, headers)
        except IncusClientException:
            self._close()
            raise
        except (OSError, http.client.HTTPException):
            self._close()
            try:
                content = self._send(method, path, body, headers)
            except IncusClientException:
                self._close()
                raise
            except Exception as e:
                self._close()
                raise IncusClientException(str(e)) from e
        except Exception as e:
            self._close()
            raise IncusClientException(str(e)) from e

        if content.get('type') == 'error':
            if content.get('error_code') == 404:
                raise IncusNotFoundException(content.get('error', 'not found'))
            raise IncusClientException(content.get('error', 'unknown error'))

        return content

    def _request(
        self,
        method: str,
        path: str,
        data: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Send JSON request.

        >>> client._request('GET', '/1.0')
        {'type': 'sync', 'status': 'Success', 'metadata': {...}}
        """
        body = json.dumps(data) if data is not None else None
        return self._execute(method, path, body, self._headers())

    def get(self, path: str) -> dict[str, Any]:
        """
        GET request.

        >>> client.get('/1.0/instances/web')
        {'type': 'sync', 'metadata': {'name': 'web', 'status': 'Running', ...}}
        """
        return self._request('GET', path)

    def post(
        self,
        path: str,
        data: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        POST request.

        >>> client.post('/1.0/instances', {'name': 'web', 'type': 'container'})
        {'type': 'async', 'metadata': {'id': '...', 'status': 'Running'}}
        """
        return self._request('POST', path, data)

    def put(
        self,
        path: str,
        data: dict[str, Any],
    ) -> dict[str, Any]:
        """
        PUT request.

        >>> client.put('/1.0/instances/web', {'description': 'updated'})
        {'type': 'async', 'metadata': {'id': '...', 'status': 'Running'}}
        """
        return self._request('PUT', path, data)

    def patch(
        self,
        path: str,
        data: dict[str, Any],
    ) -> dict[str, Any]:
        """
        PATCH request.

        >>> client.patch('/1.0/instances/web', {'description': 'updated'})
        {'type': 'async', 'metadata': {'id': '...', 'status': 'Running'}}
        """
        return self._request('PATCH', path, data)

    def delete(self, path: str) -> dict[str, Any]:
        """
        DELETE request.

        >>> client.delete('/1.0/instances/web')
        {'type': 'async', 'metadata': {'id': '...', 'status': 'Running'}}
        """
        return self._request('DELETE', path)

    def post_file(
        self,
        path: str,
        file_path: str,
        public: bool = False,
    ) -> dict[str, Any]:
        """
        POST file.

        >>> client.post_file('/1.0/images', '/tmp/image.tar.gz')
        {'type': 'async', 'metadata': {'id': '...', 'status': 'Running'}}
        """
        with open(file_path, 'rb') as fh:
            body = fh.read()
        headers = {
            'Content-Type': 'application/octet-stream',
            'Accept': 'application/json',
            'X-Incus-filename': os.path.basename(file_path),
        }
        if public:
            headers['X-Incus-public'] = '1'
        if self.parameters.token:
            headers['Authorization'] = f'Bearer {self.parameters.token}'
        return self._execute('POST', path, body, headers)

    def wait(self, response: dict[str, Any]) -> dict[str, Any] | None:
        """
        Wait for operation.

        >>> client.wait({'type': 'async', 'metadata': {'id': 'op-id'}})
        {'status': 'Success', 'metadata': {...}}
        """
        if response.get('type') == 'async':
            encoded_op_id = quote(response['metadata']['id'], safe='')
            result = self._request('GET', f'/1.0/operations/{encoded_op_id}/wait')
            metadata = result.get('metadata') or {}
            if metadata.get('status') == 'Failure':
                raise IncusClientException(metadata.get('err', 'operation failed'))
            return metadata
        return None


def incus_create_client(module: AnsibleModule) -> IncusClient:
    """
    Create client.

    >>> client = incus_create_client(module)
    >>> client.get('/1.0')
    {'type': 'sync', 'metadata': {...}}
    """
    return IncusClient(IncusConnectionParameters(
        socket_path=module.params.get('socket_path') or INCUS_SOCKET_PATH,
        url=module.params.get('url'),
        client_cert=module.params.get('client_cert'),
        client_key=module.params.get('client_key'),
        server_cert=module.params.get('server_cert'),
        client_cert_path=module.params.get('client_cert_path'),
        client_key_path=module.params.get('client_key_path'),
        server_cert_path=module.params.get('server_cert_path'),
        token=module.params.get('token'),
        validate_certs=module.params.get('validate_certs', True),
    ))
