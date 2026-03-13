# -*- coding: utf-8 -*-
# Copyright: Roman Kuzmitskii <ansible@damex.org>
# SPDX-License-Identifier: GPL-3.0-or-later

"""Incus API client."""

from __future__ import annotations

import http.client
import json
import socket
import ssl
from urllib.parse import quote, urlparse

try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False

import collections.abc
from typing import Any, NamedTuple

from ansible.module_utils.basic import AnsibleModule
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
    'incus_ensure_global_info',
    'incus_ensure_project_info',
    'incus_ensure_resource',
    'incus_find_certificate',
    'incus_resolve_image_alias',
    'incus_run_info_module',
    'incus_run_write_module',
    'incus_stringify_config',
    'incus_stringify_instance_config',
    'incus_wait',
]

_CLOUD_INIT_USER_KEYS = frozenset({'cloud-init.user-data', 'cloud-init.vendor-data'})

INCUS_SOCKET_PATH = '/var/lib/incus/unix.socket'

INCUS_WRITE_ARGS = {
    'wait': {'type': 'bool', 'default': True},
}


def _cloud_init_interface_options(**extra: Any) -> dict[str, Any]:
    """Build cloud-init network interface options."""
    opts: dict[str, Any] = {
        'name': {'type': 'str', 'required': True},
        'dhcp4': {'type': 'bool'},
        'addresses': {'type': 'list', 'elements': 'str'},
        'routes': {
            'type': 'list',
            'elements': 'dict',
            'options': {
                'to': {'type': 'str'},
                'via': {'type': 'str'},
            },
        },
        'nameservers': {'type': 'dict', 'options': {
            'addresses': {'type': 'list', 'elements': 'str'},
        }},
    }
    opts.update(extra)
    return opts


_CLOUD_INIT_DATA_OPTIONS = {
    'bootcmd': {'type': 'list', 'elements': 'raw'},
    'user': {'type': 'str'},
    'password': {'type': 'str', 'no_log': True},
    'ssh_pwauth': {'type': 'bool'},
    'ssh_authorized_keys': {'type': 'list', 'elements': 'str'},
    'chpasswd': {
        'type': 'dict',
        'no_log': False,
        'options': {
            'expire': {'type': 'bool'},
        },
    },
    'package_upgrade': {'type': 'bool'},
    'packages': {'type': 'list', 'elements': 'str'},
    'power_state': {'type': 'dict', 'options': {
        'mode': {
            'type': 'str',
            'choices': [
                'reboot',
                'poweroff',
                'halt',
            ],
        },
    }},
    'write_files': {
        'type': 'list',
        'elements': 'dict',
        'options': {
            'path': {'type': 'str', 'required': True},
            'content': {'type': 'str'},
            'owner': {'type': 'str'},
            'permissions': {'type': 'str'},
        },
    },
    'runcmd': {'type': 'list', 'elements': 'raw'},
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
    'cloud-init.network-config': {
        'type': 'dict',
        'options': {
            'version': {'type': 'int'},
            'renderer': {'type': 'str'},
            'ethernets': {
                'type': 'list',
                'elements': 'dict',
                'options': _cloud_init_interface_options(
                    match={'type': 'dict', 'options': {
                        'name': {'type': 'str'},
                        'macaddress': {'type': 'str'},
                        'driver': {'type': 'str'},
                    }},
                ),
            },
            'bonds': {
                'type': 'list',
                'elements': 'dict',
                'options': _cloud_init_interface_options(
                    interfaces={'type': 'list', 'elements': 'str'},
                    parameters={
                        'type': 'dict',
                        'options': {
                            'mode': {'type': 'str'},
                            'mii-monitor-interval': {'type': 'int'},
                        },
                    },
                ),
            },
            'bridges': {
                'type': 'list',
                'elements': 'dict',
                'options': _cloud_init_interface_options(
                    interfaces={'type': 'list', 'elements': 'str'},
                    parameters={
                        'type': 'dict',
                        'options': {
                            'stp': {'type': 'bool'},
                            'forward-delay': {'type': 'int'},
                        },
                    },
                ),
            },
            'vlans': {
                'type': 'list',
                'elements': 'dict',
                'options': _cloud_init_interface_options(
                    id={'type': 'int', 'required': True},
                    link={'type': 'str', 'required': True},
                ),
            },
        },
    },
    'cloud-init.user-data': {'type': 'dict', 'options': _CLOUD_INIT_DATA_OPTIONS},
    'cloud-init.vendor-data': {'type': 'dict', 'options': _CLOUD_INIT_DATA_OPTIONS},
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


class IncusConnectionParameters(NamedTuple):
    """Connection parameters for Incus API."""

    socket_path: str = INCUS_SOCKET_PATH
    url: str | None = None
    client_cert: str | None = None
    client_key: str | None = None
    server_cert: str | None = None
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

        if self.parameters.url:
            parsed = urlparse(self.parameters.url)
            self.host = parsed.hostname
            self.port = parsed.port or 8443

    def _connect(self) -> http.client.HTTPConnection:
        """Create connection."""
        if self.parameters.url:
            context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
            if not self.parameters.validate_certs:
                context.check_hostname = False
                context.verify_mode = ssl.CERT_NONE
            if self.parameters.server_cert:
                context.load_verify_locations(self.parameters.server_cert)
            if self.parameters.client_cert and self.parameters.client_key:
                context.load_cert_chain(self.parameters.client_cert, self.parameters.client_key)
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

    def _headers(self) -> dict[str, str]:
        """Build headers."""
        headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
        if self.parameters.token:
            headers['Authorization'] = f'Bearer {self.parameters.token}'
        return headers

    def _send(self, method: str, path: str, body: str | None) -> dict[str, Any]:
        """Execute request."""
        conn = self._connection()
        conn.request(method, path, body=body, headers=self._headers())
        response = conn.getresponse()
        result: dict[str, Any] = json.loads(response.read().decode('utf-8'))
        return result

    def _request(self, method: str, path: str, data: dict[str, Any] | None = None) -> dict[str, Any]:
        """Send request."""
        body = json.dumps(data) if data is not None else None
        try:
            content = self._send(method, path, body)
        except IncusClientException:
            self._close()
            raise
        except (OSError, http.client.HTTPException):
            self._close()
            try:
                content = self._send(method, path, body)
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
            encoded_op_id = quote(response['metadata']['id'], safe='')
            result = self._request('GET', f'/1.0/operations/{encoded_op_id}/wait')
            metadata = result.get('metadata') or {}
            if metadata.get('status') == 'Failure':
                raise IncusClientException(metadata.get('err', 'operation failed'))


def incus_create_client(module: AnsibleModule) -> IncusClient:
    """Create client."""
    return IncusClient(IncusConnectionParameters(
        socket_path=module.params.get('socket_path') or INCUS_SOCKET_PATH,
        url=module.params.get('url'),
        client_cert=module.params.get('client_cert'),
        client_key=module.params.get('client_key'),
        server_cert=module.params.get('server_cert'),
        token=module.params.get('token'),
        validate_certs=module.params.get('validate_certs', True),
    ))


def incus_stringify_config(config: dict[str, Any] | None) -> dict[str, str]:
    """Stringify config."""
    result = {}
    for k, v in (config or {}).items():
        if v is None:
            continue
        if isinstance(v, bool):
            result[k] = str(v).lower()
        else:
            result[k] = str(v)
    return result


def _strip_none(data: Any) -> Any:
    """Strip None values recursively."""
    if isinstance(data, dict):
        return {key: _strip_none(value) for key, value in data.items() if value is not None}
    if isinstance(data, list):
        return [_strip_none(item) for item in data if item is not None]
    return data


_CLOUD_INIT_NETWORK_INTERFACE_KEYS = frozenset({'ethernets', 'bonds', 'bridges', 'vlans'})


def _cloud_init_network_config_to_netplan(config: dict[str, Any]) -> dict[str, Any]:
    """Transform cloud-init network config from list to netplan dict format."""
    result: dict[str, Any] = {}
    for key, value in config.items():
        if key in _CLOUD_INIT_NETWORK_INTERFACE_KEYS and isinstance(value, list):
            result[key] = {
                interface['name']: {
                    option: option_value
                    for option, option_value in interface.items()
                    if option != 'name'
                }
                for interface in value
            }
        else:
            result[key] = value
    return result


def incus_stringify_instance_config(config: dict[str, Any] | None) -> dict[str, str]:
    """Stringify config with cloud-init YAML."""
    result = {}
    for key, value in (config or {}).items():
        if value is None:
            continue
        if isinstance(value, (dict, list)):
            cleaned = _strip_none(value)
            if key == 'cloud-init.network-config' and isinstance(cleaned, dict):
                cleaned = _cloud_init_network_config_to_netplan(cleaned)
            prefix = '#cloud-config\n' if key in _CLOUD_INIT_USER_KEYS else ''
            result[key] = prefix + yaml.dump(cleaned, default_flow_style=False)
        elif isinstance(value, bool):
            result[key] = str(value).lower()
        else:
            result[key] = str(value)
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


INCUS_KNOWN_REMOTES = {
    'images': ('https://images.linuxcontainers.org', 'simplestreams'),
    'ubuntu': ('https://cloud-images.ubuntu.com/releases', 'simplestreams'),
    'ubuntu-daily': ('https://cloud-images.ubuntu.com/daily', 'simplestreams'),
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
        if not exists or (not target and current.get('status') == 'Pending'):
            create_data = _build_create_data(module, name, desired, create_only_params, require=not exists)
            if not module.check_mode:
                incus_wait(module, client, client.post(f'/1.0/{resource}{target_query}', create_data))
            return True
        if target:
            return False
        if all(k in current and current[k] == v for k, v in desired.items()):
            return False
        if not module.check_mode:
            incus_wait(module, client, client.put(f'/1.0/{resource}/{encoded_name}{base_query}', desired))
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


def incus_ensure_project_info(resource: str, return_key: str) -> None:
    """Execute project-scoped info."""
    module = incus_create_info_module({'name': {'type': 'str'}, 'project': {'type': 'str', 'default': 'default'}})
    incus_run_info_module(module, resource, return_key)


def incus_ensure_global_info(resource: str, return_key: str) -> None:
    """Execute global info."""
    module = incus_create_info_module({'name': {'type': 'str'}})
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


def incus_wait(module: AnsibleModule, client: IncusClient, response: dict[str, Any]) -> None:
    """Wait for operation."""
    if module.params.get('wait', True):
        client.wait(response)
