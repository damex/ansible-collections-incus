# -*- coding: utf-8 -*-
# Copyright: Roman Kuzmitskii <ansible@damex.org>
# SPDX-License-Identifier: GPL-3.0-or-later

"""Incus API client."""

from __future__ import annotations

import http.client
import json
import os
import socket
import ssl
import tempfile
from urllib.parse import quote, urlparse

try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False

import collections.abc
from typing import Any, NamedTuple

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.damex.incus.plugins.module_utils.common import (
    incus_common_flatten_to_config,
    incus_common_named_list_to_dict,
    incus_common_stringify_dict,
    incus_common_stringify_value,
    incus_common_strip_none,
)
from ansible_collections.damex.incus.plugins.module_utils.cloud_init import (
    CLOUD_INIT_ALL_KEYS,
    CLOUD_INIT_CONFIG_OPTIONS,
    CLOUD_INIT_USER_KEYS,
    cloud_init_data_lists_to_dicts,
)
from ansible_collections.damex.incus.plugins.module_utils.device import devices_to_api

__all__ = [
    'INCUS_INSTANCE_CONFIG_OPTIONS',
    'INCUS_COMMON_ARGUMENT_SPEC',
    'INCUS_COMMON_ARGS',
    'INCUS_COMMON_MUTUALLY_EXCLUSIVE',
    'INCUS_COMMON_REQUIRED_BY',
    'INCUS_COMMON_REQUIRED_TOGETHER',
    'INCUS_SOURCE_ARGS',
    'IncusClient',
    'IncusClientException',
    'IncusConnectionParameters',
    'IncusNotFoundException',
    'incus_build_desired',
    'incus_build_query',
    'incus_build_source',
    'incus_create_client',
    'incus_create_info_module',
    'incus_create_write_module',
    'incus_ensure_info',
    'incus_ensure_resource',
    'incus_common_flatten_to_config',
    'incus_common_named_list_to_dict',
    'incus_common_stringify_dict',
    'incus_common_stringify_value',
    'incus_common_strip_none',
    'incus_find_certificate',
    'incus_resolve_image_alias',
    'incus_run_info_module',
    'incus_run_write_module',
    'incus_stringify_instance_config',
    'incus_wait',
]

INCUS_SOCKET_PATH = '/var/lib/incus/unix.socket'

INCUS_WRITE_ARGS = {
    'wait': {'type': 'bool', 'default': True},
}


INCUS_INSTANCE_CONFIG_OPTIONS: dict[str, Any] = {
    'limits.cpu': {'type': 'str'},
    'limits.memory': {'type': 'str'},
    'limits.processes': {'type': 'int'},
    'limits.cpu.priority': {'type': 'int'},
    'limits.cpu.allowance': {'type': 'str'},
    'limits.cpu.nodes': {'type': 'str'},
    'limits.disk.priority': {'type': 'int'},
    'limits.network.priority': {'type': 'int'},
    'limits.hugepages.1GB': {'type': 'str'},
    'limits.hugepages.1MB': {'type': 'str'},
    'limits.hugepages.2MB': {'type': 'str'},
    'limits.hugepages.64KB': {'type': 'str'},
    'limits.memory.enforce': {'type': 'str'},
    'limits.memory.hotplug': {'type': 'str'},
    'limits.memory.hugepages': {'type': 'bool'},
    'limits.memory.oom_priority': {'type': 'int'},
    'limits.memory.swap': {'type': 'str'},
    'limits.memory.swap.priority': {'type': 'int'},
    'boot.autostart': {'type': 'bool'},
    'boot.autostart.delay': {'type': 'int'},
    'boot.autostart.priority': {'type': 'int'},
    'boot.autorestart': {'type': 'bool'},
    'boot.host_shutdown_action': {'type': 'str'},
    'boot.host_shutdown_timeout': {'type': 'int'},
    'boot.stop.priority': {'type': 'int'},
    'security.privileged': {'type': 'bool'},
    'security.nesting': {'type': 'bool'},
    'security.agent.metrics': {'type': 'bool'},
    'security.bpffs.delegate_attachs': {'type': 'str'},
    'security.bpffs.delegate_cmds': {'type': 'str'},
    'security.bpffs.delegate_maps': {'type': 'str'},
    'security.bpffs.delegate_progs': {'type': 'str'},
    'security.bpffs.path': {'type': 'str'},
    'security.csm': {'type': 'bool'},
    'security.guestapi': {'type': 'bool'},
    'security.guestapi.images': {'type': 'bool'},
    'security.idmap.base': {'type': 'int'},
    'security.idmap.isolated': {'type': 'bool'},
    'security.idmap.size': {'type': 'int'},
    'security.iommu': {'type': 'bool'},
    'security.protection.delete': {'type': 'bool'},
    'security.protection.shift': {'type': 'bool'},
    'security.secureboot': {'type': 'bool'},
    'security.sev': {'type': 'bool'},
    'security.sev.policy.es': {'type': 'bool'},
    'security.sev.session.data': {'type': 'str'},
    'security.sev.session.dh': {'type': 'str'},
    'security.syscalls.allow': {'type': 'str'},
    'security.syscalls.deny': {'type': 'str'},
    'security.syscalls.deny_compat': {'type': 'bool'},
    'security.syscalls.deny_default': {'type': 'bool'},
    'security.syscalls.intercept.bpf': {'type': 'bool'},
    'security.syscalls.intercept.bpf.devices': {'type': 'bool'},
    'security.syscalls.intercept.mknod': {'type': 'bool'},
    'security.syscalls.intercept.mount': {'type': 'bool'},
    'security.syscalls.intercept.mount.allowed': {'type': 'str'},
    'security.syscalls.intercept.mount.fuse': {'type': 'str'},
    'security.syscalls.intercept.mount.shift': {'type': 'bool'},
    'security.syscalls.intercept.sched_setscheduler': {'type': 'bool'},
    'security.syscalls.intercept.setxattr': {'type': 'bool'},
    'security.syscalls.intercept.sysinfo': {'type': 'bool'},
    'migration.stateful': {'type': 'bool'},
    'migration.incremental.memory': {'type': 'bool'},
    'migration.incremental.memory.goal': {'type': 'int'},
    'migration.incremental.memory.iterations': {'type': 'int'},
    'snapshots.expiry': {'type': 'str'},
    'snapshots.expiry.manual': {'type': 'str'},
    'snapshots.pattern': {'type': 'str'},
    'snapshots.schedule': {'type': 'str'},
    'snapshots.schedule.stopped': {'type': 'bool'},
    'nvidia.driver.capabilities': {'type': 'str'},
    'nvidia.require.cuda': {'type': 'str'},
    'nvidia.require.driver': {'type': 'str'},
    'nvidia.runtime': {'type': 'bool'},
    'raw.apparmor': {'type': 'str'},
    'raw.idmap': {'type': 'str'},
    'raw.lxc': {'type': 'str'},
    'raw.qemu': {'type': 'str'},
    'raw.qemu.conf': {'type': 'str'},
    'raw.qemu.qmp.early': {'type': 'str'},
    'raw.qemu.qmp.pre-start': {'type': 'str'},
    'raw.qemu.qmp.post-start': {'type': 'str'},
    'raw.qemu.scriptlet': {'type': 'str'},
    'raw.seccomp': {'type': 'str'},
    'agent.nic_config': {'type': 'bool'},
    'cluster.evacuate': {'type': 'str', 'choices': [
        'auto', 'live-migrate', 'migrate', 'stop', 'stateful-stop', 'force-stop',
    ]},
    'linux.kernel_modules': {'type': 'str'},
    'oci.cwd': {'type': 'str'},
    'oci.entrypoint': {'type': 'str'},
    'oci.gid': {'type': 'str'},
    'oci.uid': {'type': 'str'},
    **CLOUD_INIT_CONFIG_OPTIONS,
}

INCUS_COMMON_ARGUMENT_SPEC = {
    'name': {'type': 'str', 'required': True},
    'state': {
        'type': 'str',
        'default': 'present',
        'choices': [
            'present',
            'absent',
        ],
    },
}

INCUS_COMMON_ARGS = {
    'socket_path': {'type': 'str', 'default': INCUS_SOCKET_PATH},
    'url': {'type': 'str'},
    'client_cert': {'type': 'str'},
    'client_key': {'type': 'str', 'no_log': True},
    'server_cert': {'type': 'str'},
    'client_cert_path': {'type': 'str'},
    'client_key_path': {'type': 'str', 'no_log': True},
    'server_cert_path': {'type': 'str'},
    'token': {'type': 'str', 'no_log': True},
    'validate_certs': {'type': 'bool', 'default': True},
}

INCUS_COMMON_MUTUALLY_EXCLUSIVE = [
    ['token', 'client_cert'],
    ['token', 'client_cert_path'],
    ['client_cert', 'client_cert_path'],
    ['client_key', 'client_key_path'],
    ['server_cert', 'server_cert_path'],
]

INCUS_COMMON_REQUIRED_TOGETHER = [
    ['client_cert', 'client_key'],
    ['client_cert_path', 'client_key_path'],
]

INCUS_COMMON_REQUIRED_BY = {
    'client_cert': 'url',
    'client_key': 'url',
    'server_cert': 'url',
    'client_cert_path': 'url',
    'client_key_path': 'url',
    'server_cert_path': 'url',
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


class IncusConnectionParameters(NamedTuple):
    """Connection parameters for Incus API."""

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
    """Incus API client."""

    def __init__(self, parameters: IncusConnectionParameters | None = None) -> None:
        """Set connection parameters."""
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
        """Write content to temporary file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.pem', delete=False) as temp_file:
            temp_file.write(content)
            self._temp_files.append(temp_file.name)
            return temp_file.name

    def _build_ssl_context(self) -> ssl.SSLContext:
        """Build SSL context."""
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
        """Create connection."""
        if self.parameters.url:
            context = self._build_ssl_context()
            if self.host is None:
                raise IncusClientException('URL provided but hostname could not be parsed')
            return http.client.HTTPSConnection(self.host, self.port, context=context)
        return _UnixSocketHTTPConnection(self.parameters.socket_path)

    def _connection(self) -> http.client.HTTPConnection:
        """Get connection."""
        if self._conn is None:
            self._conn = self._connect()
        return self._conn

    def _close(self) -> None:
        """Close connection."""
        if self._conn is not None:
            self._conn.close()
            self._conn = None

    def close(self) -> None:
        """Close connection and clean up temporary files."""
        self._close()
        for temp_path in self._temp_files:
            try:
                os.unlink(temp_path)
            except OSError:
                pass
        self._temp_files.clear()

    def _headers(self) -> dict[str, str]:
        """Build headers."""
        headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
        if self.parameters.token:
            headers['Authorization'] = f'Bearer {self.parameters.token}'
        return headers

    def _send(self, method: str, path: str, body: str | bytes | None, headers: dict[str, str]) -> dict[str, Any]:
        """Execute request."""
        conn = self._connection()
        conn.request(method, path, body=body, headers=headers)
        response = conn.getresponse()
        result: dict[str, Any] = json.loads(response.read().decode('utf-8'))
        return result

    def _execute(self, method: str, path: str, body: str | bytes | None, headers: dict[str, str]) -> dict[str, Any]:
        """Execute request with retry."""
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

    def _request(self, method: str, path: str, data: dict[str, Any] | None = None) -> dict[str, Any]:
        """Send JSON request."""
        body = json.dumps(data) if data is not None else None
        return self._execute(method, path, body, self._headers())

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

    def post_file(self, path: str, file_path: str, public: bool = False) -> dict[str, Any]:
        """POST file."""
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
        """Wait for operation."""
        if response.get('type') == 'async':
            encoded_op_id = quote(response['metadata']['id'], safe='')
            result = self._request('GET', f'/1.0/operations/{encoded_op_id}/wait')
            metadata = result.get('metadata') or {}
            if metadata.get('status') == 'Failure':
                raise IncusClientException(metadata.get('err', 'operation failed'))
            return metadata
        return None


def incus_create_client(module: AnsibleModule) -> IncusClient:
    """Create client."""
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


def incus_stringify_instance_config(config: dict[str, Any] | None) -> dict[str, str]:
    """Stringify config with cloud-init YAML."""
    result = {}
    for key, value in (config or {}).items():
        if value is None:
            continue
        if isinstance(value, (dict, list)):
            cleaned = incus_common_strip_none(value)
            if isinstance(cleaned, dict) and key in CLOUD_INIT_ALL_KEYS:
                cleaned = cloud_init_data_lists_to_dicts(cleaned)
            prefix = '#cloud-config\n' if key in CLOUD_INIT_USER_KEYS else ''
            result[key] = prefix + yaml.dump(cleaned, default_flow_style=False)
        else:
            result[key] = incus_common_stringify_value(value)
    return result


def incus_build_desired(
    module: AnsibleModule,
    config_lists: dict[str, str] | None = None,
) -> dict[str, Any]:
    """Build desired state."""
    has_devices = 'devices' in module.params and module.params['devices'] is not None
    config = module.params['config'] or {}
    if config_lists:
        config = {key: value for key, value in config.items() if key not in config_lists}
    desired: dict[str, Any] = {
        'description': module.params['description'],
        'config': incus_stringify_instance_config(config) if has_devices
        else incus_common_stringify_dict(config),
    }
    if has_devices:
        desired['devices'] = devices_to_api(module.params['devices'])
    if config_lists:
        raw_config = module.params['config'] or {}
        for key, prefix in config_lists.items():
            items = raw_config.get(key)
            if items:
                desired['config'].update(
                    incus_common_flatten_to_config(prefix, incus_common_named_list_to_dict(items)),
                )
    return desired


INCUS_KNOWN_REMOTES = {
    'images': ('https://images.linuxcontainers.org', 'simplestreams'),
    'ubuntu': ('https://cloud-images.ubuntu.com/releases', 'simplestreams'),
    'ubuntu-daily': ('https://cloud-images.ubuntu.com/daily', 'simplestreams'),
    'docker': ('https://docker.io', 'oci'),
}

INCUS_SOURCE_ARGS = {
    'source': {'type': 'str'},
    'source_server': {'type': 'str'},
    'source_protocol': {
        'type': 'str',
        'default': 'simplestreams',
        'choices': [
            'simplestreams',
            'incus',
            'oci',
        ],
    },
}


def incus_build_source(module: AnsibleModule) -> dict[str, Any]:
    """Build image source."""
    raw = module.params['source']
    server = module.params.get('source_server')
    protocol = module.params.get('source_protocol') or 'simplestreams'

    alias = raw
    if ':' in raw:
        remote, alias = raw.split(':', 1)
        if not server:
            if remote not in INCUS_KNOWN_REMOTES:
                module.fail_json(msg=f"Unknown remote '{remote}'. Set source_server explicitly.")
            server, protocol = INCUS_KNOWN_REMOTES[remote]

    source = {'type': 'image', 'alias': alias}
    if server:
        source['server'] = server
        source['protocol'] = protocol
    return source


def incus_build_query(
    project: str | None = None, target: str | None = None, recursion: int | None = None,
) -> str:
    """Build query string."""
    params = []
    if project:
        params.append(f'project={quote(project, safe="")}')
    if target:
        params.append(f'target={quote(target, safe="")}')
    if recursion is not None:
        params.append(f'recursion={recursion}')
    return f'?{"&".join(params)}' if params else ''


def _build_create_data(
    module: AnsibleModule, name: str, desired: dict[str, Any],
    create_only_params: list[str] | None, *, require: bool = True,
) -> dict[str, Any]:
    """Build create payload with create-only params."""
    data: dict[str, Any] = {'name': name, **desired}
    for param in (create_only_params or []):
        value = module.params.get(param)
        if require and not value:
            module.fail_json(msg=f"'{param}' is required when creating")
        if value:
            data[param] = value
    return data


def incus_ensure_resource(
    module: AnsibleModule, resource: str, desired: dict[str, Any],
    create_only_params: list[str] | None = None,
    name_key: str = 'name',
) -> bool:
    """Ensure resource."""
    client = incus_create_client(module)
    name = module.params['name']
    encoded_name = quote(name, safe='')
    project = module.params.get('project')
    target = module.params.get('target')
    base_query = incus_build_query(project, None)
    target_query = incus_build_query(project, target)

    try:
        current = client.get(f'/1.0/{resource}/{encoded_name}{target_query}').get('metadata') or {}
        exists = True
    except IncusNotFoundException:
        current = {}
        exists = False

    if module.params['state'] == 'present':
        if not exists or current.get('status') in ('Pending', 'Unknown'):
            create_data = _build_create_data(module, name, desired, create_only_params, require=not exists)
            if name_key != 'name':
                create_data[name_key] = create_data.pop('name')
            if not module.check_mode:
                incus_wait(module, client, client.post(f'/1.0/{resource}{target_query}', create_data))
            return True
        if all(k in current and current[k] == v for k, v in desired.items()):
            return False
        update_query = target_query if target else base_query
        if not module.check_mode:
            incus_wait(module, client, client.put(f'/1.0/{resource}/{encoded_name}{update_query}', desired))
        return True

    if exists:
        if not module.check_mode:
            incus_wait(module, client, client.delete(f'/1.0/{resource}/{encoded_name}{base_query}'))
        return True
    return False


def incus_find_certificate(client: IncusClient, name: str) -> dict[str, Any] | None:
    """Find certificate by name."""
    query = incus_build_query(recursion=1)
    certificates = client.get(f'/1.0/certificates{query}').get('metadata') or []
    for certificate in certificates:
        if certificate.get('name') == name:
            result: dict[str, Any] = certificate
            return result
    return None


def incus_resolve_image_alias(client: IncusClient, alias: str, query: str) -> str | None:
    """Resolve image alias to fingerprint."""
    encoded_alias = quote(alias, safe='')
    try:
        alias_meta = client.get(f'/1.0/images/aliases/{encoded_alias}{query}').get('metadata') or {}
        fingerprint: str | None = alias_meta.get('target')
        return fingerprint
    except IncusNotFoundException:
        return None


def incus_run_write_module(module: AnsibleModule, impl: collections.abc.Callable[[], bool]) -> None:
    """Execute write module."""
    try:
        module.exit_json(changed=impl())
    except IncusClientException as exc:
        module.fail_json(msg=str(exc))


def incus_run_info_module(module: AnsibleModule, resource: str, return_key: str) -> None:
    """Execute info module."""
    name = module.params.get('name')
    project = module.params.get('project')
    result: list[Any] = []

    try:
        client = incus_create_client(module)

        if name:
            encoded_name = quote(name, safe='')
            query = incus_build_query(project=project)
            path = f'/1.0/{resource}/{encoded_name}{query}'
            try:
                response = client.get(path)
                metadata = response.get('metadata')
                result = [metadata] if metadata else []
            except IncusNotFoundException:
                result = []
        else:
            query = incus_build_query(project=project, recursion=1)
            response = client.get(f'/1.0/{resource}{query}')
            result = response.get('metadata') or []

    except IncusClientException as e:
        module.fail_json(msg=str(e))

    module.exit_json(**{return_key: result})


def incus_ensure_info(resource: str, return_key: str, *, project_scoped: bool = False) -> None:
    """Execute info module."""
    args: dict[str, Any] = {'name': {'type': 'str'}}
    if project_scoped:
        args['project'] = {'type': 'str', 'default': 'default'}
    module = incus_create_info_module(args)
    incus_run_info_module(module, resource, return_key)


def incus_create_info_module(argument_spec: dict[str, Any]) -> AnsibleModule:
    """Create info module."""
    return AnsibleModule(
        argument_spec={**argument_spec, **INCUS_COMMON_ARGS},
        supports_check_mode=True,
        mutually_exclusive=INCUS_COMMON_MUTUALLY_EXCLUSIVE,
        required_together=INCUS_COMMON_REQUIRED_TOGETHER,
        required_by=INCUS_COMMON_REQUIRED_BY,
    )


def incus_create_write_module(
    argument_spec: dict[str, Any], *, require_yaml: bool = False,
) -> AnsibleModule:
    """Create write module."""
    module = AnsibleModule(
        argument_spec={**argument_spec, **INCUS_COMMON_ARGS, **INCUS_WRITE_ARGS},
        supports_check_mode=True,
        mutually_exclusive=INCUS_COMMON_MUTUALLY_EXCLUSIVE,
        required_together=INCUS_COMMON_REQUIRED_TOGETHER,
        required_by=INCUS_COMMON_REQUIRED_BY,
    )
    if require_yaml and not HAS_YAML:
        module.fail_json(msg='PyYAML is required for this module')
    return module


def incus_wait(module: AnsibleModule, client: IncusClient, response: dict[str, Any]) -> dict[str, Any] | None:
    """Wait for operation."""
    if module.params.get('wait', True):
        return client.wait(response)
    return None
