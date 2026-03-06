# -*- coding: utf-8 -*-
# Copyright: Roman Kuzmitskii <ansible@damex.org>
# SPDX-License-Identifier: GPL-3.0-or-later

"""Incus API client."""

from __future__ import annotations

import http.client
import json
import socket
import ssl
from urllib.parse import urlparse

try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False

import collections.abc
from typing import Any

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.damex.incus.plugins.module_utils.device import devices_to_api

__all__ = [
    'INCUS_COMMON_ARGUMENT_SPEC',
    'IncusClient',
    'IncusClientException',
    'IncusNotFoundException',
    'incus_build_desired',
    'incus_create_client',
    'incus_ensure_resource',
    'incus_create_info_module',
    'incus_create_write_module',
    'incus_wait',
    'incus_ensure_global_info',
    'incus_run_info_module',
    'incus_ensure_project_info',
    'incus_run_write_module',
]

_CLOUD_INIT_USER_KEYS = frozenset({'cloud-init.user-data', 'cloud-init.vendor-data'})

INCUS_SOCKET_PATH = '/var/lib/incus/unix.socket'

INCUS_WRITE_ARGS = {
    'wait': {'type': 'bool', 'default': True},
}

INCUS_COMMON_ARGUMENT_SPEC = {
    'name': {'type': 'str', 'required': True},
    'state': {'type': 'str', 'default': 'present', 'choices': ['present', 'absent']},
}

INCUS_COMMON_ARGS = {
    'socket_path': {'type': 'str', 'default': INCUS_SOCKET_PATH},
    'url': {'type': 'str'},
    'client_cert': {'type': 'path'},
    'client_key': {'type': 'path', 'no_log': True},
    'server_cert': {'type': 'path'},
    'token': {'type': 'str', 'no_log': True},
    'validate_certs': {'type': 'bool', 'default': True},
}

INCUS_COMMON_MUTUALLY_EXCLUSIVE = [
    ['token', 'client_cert'],
]

INCUS_COMMON_REQUIRED_TOGETHER = [
    ['client_cert', 'client_key'],
]

INCUS_COMMON_REQUIRED_BY = {
    'client_cert': 'url',
    'client_key': 'url',
    'server_cert': 'url',
    'token': 'url',
}


class IncusClientException(Exception):
    """API error."""


class IncusNotFoundException(IncusClientException):
    """Resource not found."""


class _UnixSocketHTTPConnection(http.client.HTTPConnection):
    """HTTP over Unix socket."""

    def __init__(self, socket_path: str) -> None:
        """Set socket path."""
        super().__init__('localhost')
        self.socket_path = socket_path

    def connect(self) -> None:
        """Connect to socket."""
        self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.sock.connect(self.socket_path)


class IncusClient:  # pylint: disable=too-many-instance-attributes
    """Incus API client."""

    def __init__(  # pylint: disable=too-many-arguments,too-many-positional-arguments
        self, socket_path: str | None = None, url: str | None = None,
        client_cert: str | None = None, client_key: str | None = None,
        server_cert: str | None = None, token: str | None = None,
        validate_certs: bool = True,
    ) -> None:
        """Set connection params."""
        self.socket_path = socket_path or INCUS_SOCKET_PATH
        self.url = url
        self.client_cert = client_cert
        self.client_key = client_key
        self.server_cert = server_cert
        self.token = token
        self.validate_certs = validate_certs
        self.host: str | None = None
        self.port: int = 8443

        if url:
            parsed = urlparse(url)
            self.host = parsed.hostname
            self.port = parsed.port or 8443

    def _connection(self) -> http.client.HTTPConnection:
        """Get connection."""
        if self.url:
            context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
            if not self.validate_certs:
                context.check_hostname = False
                context.verify_mode = ssl.CERT_NONE
            if self.server_cert:
                context.load_verify_locations(self.server_cert)
            if self.client_cert and self.client_key:
                context.load_cert_chain(self.client_cert, self.client_key)
            if self.host is None:
                raise IncusClientException('URL provided but hostname could not be parsed')
            return http.client.HTTPSConnection(self.host, self.port, context=context)
        return _UnixSocketHTTPConnection(self.socket_path)

    def _headers(self) -> dict[str, str]:
        """Build headers."""
        headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
        if self.token:
            headers['Authorization'] = f'Bearer {self.token}'
        return headers

    def _request(self, method: str, path: str, data: dict[str, Any] | None = None) -> dict[str, Any]:
        """Send request."""
        conn = self._connection()
        try:
            body = json.dumps(data) if data is not None else None
            conn.request(method, path, body=body, headers=self._headers())
            response = conn.getresponse()
            content: dict[str, Any] = json.loads(response.read().decode('utf-8'))
        except Exception as e:
            raise IncusClientException(str(e)) from e
        finally:
            conn.close()

        if content.get('type') == 'error':
            if content.get('error_code') == 404:
                raise IncusNotFoundException(content.get('error', 'not found'))
            raise IncusClientException(content.get('error', 'unknown error'))

        return content

    def get(self, path: str) -> dict[str, Any]:
        """GET request."""
        return self._request('GET', path)

    def post(self, path: str, data: dict[str, Any] | None = None) -> dict[str, Any]:
        """POST request."""
        return self._request('POST', path, data)

    def put(self, path: str, data: dict[str, Any]) -> dict[str, Any]:
        """PUT request."""
        return self._request('PUT', path, data)

    def patch(self, path: str, data: dict[str, Any]) -> dict[str, Any]:
        """PATCH request."""
        return self._request('PATCH', path, data)

    def delete(self, path: str) -> dict[str, Any]:
        """DELETE request."""
        return self._request('DELETE', path)

    def wait(self, response: dict[str, Any]) -> None:
        """Wait for operation."""
        if response.get('type') == 'async':
            op_id = response['metadata']['id']
            self._request('GET', f'/1.0/operations/{op_id}/wait')


def incus_create_client(module: AnsibleModule) -> IncusClient:
    """Create client."""
    return IncusClient(
        socket_path=module.params.get('socket_path'),
        url=module.params.get('url'),
        client_cert=module.params.get('client_cert'),
        client_key=module.params.get('client_key'),
        server_cert=module.params.get('server_cert'),
        token=module.params.get('token'),
        validate_certs=module.params.get('validate_certs', True),
    )


def incus_stringify_config(config: dict[str, Any] | None) -> dict[str, str]:
    """Stringify config."""
    result = {}
    for k, v in (config or {}).items():
        if isinstance(v, bool):
            result[k] = str(v).lower()
        else:
            result[k] = str(v)
    return result


def incus_stringify_instance_config(config: dict[str, Any] | None) -> dict[str, str]:
    """Stringify config with cloud-init YAML."""
    result = {}
    for k, v in (config or {}).items():
        if isinstance(v, (dict, list)):
            prefix = '#cloud-config\n' if k in _CLOUD_INIT_USER_KEYS else ''
            result[k] = prefix + yaml.dump(v, default_flow_style=False)
        elif isinstance(v, bool):
            result[k] = str(v).lower()
        else:
            result[k] = str(v)
    return result


def incus_build_desired(module: AnsibleModule) -> dict[str, Any]:
    """Build desired state."""
    has_devices = 'devices' in module.params and module.params['devices'] is not None
    desired: dict[str, Any] = {
        'description': module.params['description'],
        'config': incus_stringify_instance_config(module.params['config']) if has_devices
        else incus_stringify_config(module.params['config']),
    }
    if has_devices:
        desired['devices'] = devices_to_api(module.params['devices'])
    return desired


def incus_ensure_resource(
    module: AnsibleModule, resource: str, desired: dict[str, Any],
    create_only_params: list[str] | None = None,
) -> bool:
    """Ensure resource."""
    client = incus_create_client(module)
    name = module.params['name']
    project = module.params.get('project')
    query = f'?project={project}' if project else ''

    try:
        current = client.get(f'/1.0/{resource}/{name}{query}').get('metadata') or {}
        exists = True
    except IncusNotFoundException:
        current = {}
        exists = False

    if module.params['state'] == 'present':
        if not exists:
            create_data: dict[str, Any] = {'name': name, **desired}
            for param in (create_only_params or []):
                value = module.params.get(param)
                if not value:
                    module.fail_json(msg=f"'{param}' is required when creating")
                create_data[param] = value
            if not module.check_mode:
                incus_wait(module, client, client.post(f'/1.0/{resource}{query}', create_data))
            return True
        if (current.get('description', '') == desired['description']
                and current.get('config', {}) == desired['config']):
            return False
        if not module.check_mode:
            incus_wait(module, client, client.put(f'/1.0/{resource}/{name}{query}', desired))
        return True

    if exists:
        if not module.check_mode:
            incus_wait(module, client, client.delete(f'/1.0/{resource}/{name}{query}'))
        return True
    return False


def incus_run_write_module(module: AnsibleModule, impl: collections.abc.Callable[[], bool]) -> None:
    """Execute write module."""
    try:
        module.exit_json(changed=impl())
    except IncusClientException as exc:
        module.fail_json(msg=str(exc))


def incus_run_info_module(module: AnsibleModule, resource: str, return_key: str) -> None:
    """Run common info module logic. project param optional."""
    name = module.params.get('name')
    project = module.params.get('project')
    result: list[Any] = []

    try:
        client = incus_create_client(module)

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



def incus_ensure_project_info(resource: str, return_key: str) -> None:
    """Create and run a project-scoped info module."""
    module = incus_create_info_module({'name': {'type': 'str'}, 'project': {'type': 'str', 'default': 'default'}})
    incus_run_info_module(module, resource, return_key)


def incus_ensure_global_info(resource: str, return_key: str) -> None:
    """Create and run a global (non-project-scoped) info module."""
    module = incus_create_info_module({'name': {'type': 'str'}})
    incus_run_info_module(module, resource, return_key)


def incus_create_info_module(argument_spec: dict[str, Any]) -> AnsibleModule:
    """Create AnsibleModule with common args merged in for info modules."""
    argument_spec.update(INCUS_COMMON_ARGS)
    return AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
        mutually_exclusive=INCUS_COMMON_MUTUALLY_EXCLUSIVE,
        required_together=INCUS_COMMON_REQUIRED_TOGETHER,
        required_by=INCUS_COMMON_REQUIRED_BY,
    )


def incus_create_write_module(
    argument_spec: dict[str, Any], *, require_yaml: bool = False,
) -> AnsibleModule:
    """Create AnsibleModule with common and write args merged in."""
    argument_spec.update(INCUS_COMMON_ARGS)
    argument_spec.update(INCUS_WRITE_ARGS)
    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
        mutually_exclusive=INCUS_COMMON_MUTUALLY_EXCLUSIVE,
        required_together=INCUS_COMMON_REQUIRED_TOGETHER,
        required_by=INCUS_COMMON_REQUIRED_BY,
    )
    if require_yaml and not HAS_YAML:
        module.fail_json(msg='PyYAML is required for this module')
    return module


def incus_wait(module: AnsibleModule, client: IncusClient, response: dict[str, Any]) -> None:
    """Wait for an async operation only if the wait param is true."""
    if module.params.get('wait', True):
        client.wait(response)
