# -*- coding: utf-8 -*-
# Copyright: Roman Kuzmitskii <ansible@damex.org>
# SPDX-License-Identifier: GPL-3.0-or-later

"""Incus REST API client."""

from __future__ import annotations

import http.client
import json
import socket
import ssl
from urllib.parse import urlparse

__all__ = [
    'INCUS_COMMON_ARGS',
    'IncusClientException',
    'IncusNotFoundException',
    'IncusClient',
    'incus_client_from_module',
    'run_info_module',
]

INCUS_SOCKET_PATH = '/var/lib/incus/unix.socket'

INCUS_COMMON_ARGS = {
    'socket_path': {'type': 'str', 'default': INCUS_SOCKET_PATH},
    'url': {'type': 'str'},
    'client_cert': {'type': 'path'},
    'client_key': {'type': 'path', 'no_log': True},
    'server_cert': {'type': 'path'},
    'token': {'type': 'str', 'no_log': True},
    'validate_certs': {'type': 'bool', 'default': True},
}


class IncusClientException(Exception):
    """API error."""


class IncusNotFoundException(IncusClientException):
    """Resource not found (404)."""


class _UnixSocketHTTPConnection(http.client.HTTPConnection):
    """HTTP over Unix socket."""

    def __init__(self, socket_path):
        """Set socket path."""
        super().__init__('localhost')
        self.socket_path = socket_path

    def connect(self):
        """Connect to socket."""
        self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.sock.connect(self.socket_path)


class IncusClient:  # pylint: disable=too-many-instance-attributes
    """Incus REST API client."""

    def __init__(  # pylint: disable=too-many-arguments,too-many-positional-arguments
        self, socket_path=None, url=None, client_cert=None, client_key=None,
        server_cert=None, token=None, validate_certs=True,
    ):
        """Store connection params."""
        self.socket_path = socket_path or INCUS_SOCKET_PATH
        self.url = url
        self.client_cert = client_cert
        self.client_key = client_key
        self.server_cert = server_cert
        self.token = token
        self.validate_certs = validate_certs

        if url:
            parsed = urlparse(url)
            self.host = parsed.hostname
            self.port = parsed.port or 8443

    def _connection(self):
        """Return HTTP or HTTPS connection."""
        if self.url:
            context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
            if not self.validate_certs:
                context.check_hostname = False
                context.verify_mode = ssl.CERT_NONE
            if self.server_cert:
                context.load_verify_locations(self.server_cert)
            if self.client_cert and self.client_key:
                context.load_cert_chain(self.client_cert, self.client_key)
            return http.client.HTTPSConnection(self.host, self.port, context=context)
        return _UnixSocketHTTPConnection(self.socket_path)

    def _headers(self):
        """Build request headers."""
        headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
        if self.token:
            headers['Authorization'] = f'Bearer {self.token}'
        return headers

    def _request(self, method, path, data=None):
        """Send request, return parsed response."""
        conn = self._connection()
        try:
            body = json.dumps(data) if data is not None else None
            conn.request(method, path, body=body, headers=self._headers())
            response = conn.getresponse()
            content = json.loads(response.read().decode('utf-8'))
        except Exception as e:
            raise IncusClientException(str(e)) from e
        finally:
            conn.close()

        if content.get('type') == 'error':
            if content.get('error_code') == 404:
                raise IncusNotFoundException(content.get('error', 'not found'))
            raise IncusClientException(content.get('error', 'unknown error'))

        return content

    def get(self, path):
        """GET request."""
        return self._request('GET', path)

    def post(self, path, data=None):
        """POST request."""
        return self._request('POST', path, data)

    def put(self, path, data):
        """PUT request."""
        return self._request('PUT', path, data)

    def patch(self, path, data):
        """PATCH request."""
        return self._request('PATCH', path, data)

    def delete(self, path):
        """DELETE request."""
        return self._request('DELETE', path)


def incus_client_from_module(module):
    """Build client from module params."""
    return IncusClient(
        socket_path=module.params.get('socket_path'),
        url=module.params.get('url'),
        client_cert=module.params.get('client_cert'),
        client_key=module.params.get('client_key'),
        server_cert=module.params.get('server_cert'),
        token=module.params.get('token'),
        validate_certs=module.params.get('validate_certs'),
    )


def run_info_module(module, resource, return_key):
    """Run common info module logic. project param optional."""
    name = module.params.get('name')
    project = module.params.get('project')

    try:
        client = incus_client_from_module(module)

        if name:
            path = f'/1.0/{resource}/{name}' + (f'?project={project}' if project else '')
            try:
                response = client.get(path)
                metadata = response.get('metadata')
                result = [metadata] if metadata else []
            except IncusNotFoundException:
                result = []
        else:
            query = f'?project={project}&recursion=1' if project else '?recursion=1'
            response = client.get(f'/1.0/{resource}{query}')
            result = response.get('metadata') or []

    except IncusClientException as e:
        module.fail_json(msg=str(e))

    module.exit_json(**{return_key: result})
