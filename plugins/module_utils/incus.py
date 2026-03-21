# -*- coding: utf-8 -*-
# Copyright: Roman Kuzmitskii <ansible@damex.org>
# SPDX-License-Identifier: GPL-3.0-or-later

"""
Incus module framework and resource management.
"""

from __future__ import annotations

from urllib.parse import quote

try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False

import collections.abc
from typing import Any, NamedTuple

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.damex.incus.plugins.module_utils.incus_client import (
    INCUS_SOCKET_PATH,
    IncusClient,
    IncusClientException,
    IncusNotFoundException,
    incus_create_client,
)
from ansible_collections.damex.incus.plugins.module_utils.common import (
    incus_common_flatten_key_value_to_config,
    incus_common_flatten_to_config,
    incus_common_named_list_to_dict,
    incus_common_stringify_dict,
    incus_common_stringify_value,
    incus_common_strip_none,
)
from ansible_collections.damex.incus.plugins.module_utils.cloud_init import (
    CLOUD_INIT_ALL_KEYS,
    CLOUD_INIT_USER_KEYS,
    cloud_init_data_lists_to_dicts,
)
from ansible_collections.damex.incus.plugins.module_utils.device import devices_to_api
from ansible_collections.damex.incus.plugins.module_utils.incus_source import (
    INCUS_SOURCE_ARGS,
    incus_build_query,
    incus_build_source,
)

__all__ = [
    'INCUS_COMMON_ARGUMENT_SPEC',
    'INCUS_COMMON_ARGS',
    'INCUS_COMMON_MUTUALLY_EXCLUSIVE',
    'INCUS_COMMON_REQUIRED_BY',
    'INCUS_COMMON_REQUIRED_TOGETHER',
    'INCUS_SOURCE_ARGS',
    'IncusResourceOptions',
    'incus_build_desired',
    'incus_build_query',
    'incus_build_source',
    'incus_create_info_module',
    'incus_create_write_module',
    'incus_ensure_info',
    'incus_ensure_resource',
    'incus_find_certificate',
    'incus_resolve_image_alias',
    'incus_run_info_module',
    'incus_run_write_module',
    'incus_wait',
]

INCUS_WRITE_ARGS = {
    'wait': {'type': 'bool', 'default': True},
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


def incus_stringify_instance_config(config: dict[str, Any] | None) -> dict[str, str]:
    """
    Stringify config with cloud-init YAML.

    >>> incus_stringify_instance_config({'limits.cpu': 2, 'boot.autostart': True})
    {'limits.cpu': '2', 'boot.autostart': 'true'}
    """
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
    config_key_values: dict[str, str] | None = None,
) -> dict[str, Any]:
    """
    Build desired state.

    >>> incus_build_desired(module)
    {'description': '', 'config': {}}
    """
    has_devices = 'devices' in module.params and module.params['devices'] is not None
    config = module.params['config'] or {}
    list_keys: set[str] = set()
    if config_lists:
        list_keys.update(config_lists)
    if config_key_values:
        list_keys.update(config_key_values)
    if list_keys:
        config = {key: value for key, value in config.items() if key not in list_keys}
    desired: dict[str, Any] = {
        'description': module.params['description'],
        'config': incus_stringify_instance_config(config) if has_devices
        else incus_common_stringify_dict(config),
    }
    if has_devices:
        desired['devices'] = devices_to_api(module.params['devices'])
    raw_config = module.params['config'] or {}
    if config_lists:
        for key, prefix in config_lists.items():
            items = raw_config.get(key)
            if items:
                for config_key, config_value in incus_common_flatten_to_config(
                    prefix,
                    incus_common_named_list_to_dict(items),
                ).items():
                    desired['config'][config_key] = config_value
    if config_key_values:
        for key, prefix in config_key_values.items():
            items = raw_config.get(key)
            if items:
                for config_key, config_value in incus_common_flatten_key_value_to_config(
                    prefix,
                    items,
                ).items():
                    desired['config'][config_key] = config_value
    return desired


def _incus_desired_matches_current(
    desired: dict[str, Any],
    current: dict[str, Any],
) -> bool:
    """
    Check desired state matches current.

    >>> _incus_desired_matches_current(
    ...     {'description': 'test'},
    ...     {'description': 'test', 'config': {}},
    ... )
    True
    """
    for key, desired_value in desired.items():
        if key not in current:
            return False
        if current[key] != desired_value:
            return False
    return True


def _build_create_data(
    module: AnsibleModule,
    name: str,
    desired: dict[str, Any],
    create_only_params: list[str] | None,
    *,
    require: bool = True,
) -> dict[str, Any]:
    """
    Build create payload.

    >>> _build_create_data(
    ...     module,
    ...     'web',
    ...     {'description': ''},
    ...     ['source'],
    ... )
    {'name': 'web', 'description': '', 'source': 'images:debian/13'}
    """
    data: dict[str, Any] = desired.copy()
    data['name'] = name
    for param in (create_only_params or []):
        value = module.params.get(param)
        if require and not value:
            module.fail_json(msg=f"'{param}' is required when creating")
        if value:
            data[param] = value
    return data


class IncusResourceOptions(NamedTuple):
    """
    Options for incus_ensure_resource.

    >>> opts = IncusResourceOptions(create_only_params=['source'])
    >>> opts.create_only_params
    ['source']
    """

    create_only_params: list[str] | None = None
    name_key: str = 'name'
    immutable_config_keys: frozenset[str] = frozenset()


def _incus_build_effective_desired(
    desired: dict[str, Any],
    current: dict[str, Any],
    immutable_config_keys: frozenset[str],
    global_config_keys: frozenset[str],
) -> dict[str, Any]:
    """
    Build effective desired state.

    >>> _incus_build_effective_desired(
    ...     {'config': {'limits.cpu': '2'}},
    ...     {'config': {'volatile.uuid': 'abc'}},
    ...     frozenset(),
    ...     frozenset(),
    ... )
    {'config': {'volatile.uuid': 'abc', 'limits.cpu': '2'}}
    """
    current_config = current.get('config', {})
    desired_config = desired.get('config', {})
    preserved = {
        key: value
        for key, value in current_config.items()
        if key not in desired_config
        and (key in global_config_keys
             or key.startswith('volatile.')
             or key in immutable_config_keys)
    }
    has_absent_immutable = any(
        config_key in immutable_config_keys and config_key not in current_config
        for config_key in desired_config
    )
    if not preserved and not has_absent_immutable:
        return desired
    combined_config: dict[str, Any] = {}
    for config_key, config_value in preserved.items():
        combined_config[config_key] = config_value
    for config_key, config_value in desired_config.items():
        if config_key in immutable_config_keys and config_key not in current_config:
            continue
        combined_config[config_key] = config_value
    result = desired.copy()
    result['config'] = combined_config
    return result


def _incus_check_target_creation(
    module: AnsibleModule,
    client: IncusClient,
    resource: str,
    encoded_name: str,
    project: str | None,
) -> bool:
    """
    Check target creation is allowed.

    >>> _incus_check_target_creation(
    ...     module,
    ...     client,
    ...     'instances',
    ...     'web',
    ...     'default',
    ... )
    True
    """
    try:
        global_query = incus_build_query(project, None)
        global_meta = client.get(f'/1.0/{resource}/{encoded_name}{global_query}').get('metadata') or {}
        global_status = global_meta.get('status')
        if global_status == 'Errored':
            module.fail_json(msg=f'{module.params["name"]} is in errored state, delete it first')
        return global_status in ('Pending', 'Unknown', None)
    except IncusNotFoundException:
        return True


def incus_ensure_resource(
    module: AnsibleModule,
    resource: str,
    desired: dict[str, Any],
    options: IncusResourceOptions | None = None,
) -> bool:
    """
    Ensure resource.

    >>> incus_ensure_resource(
    ...     module,
    ...     'instances',
    ...     {'description': '', 'config': {}},
    ... )
    True
    """
    opts = options or IncusResourceOptions()
    with incus_create_client(module) as client:
        encoded_name = quote(module.params['name'], safe='')
        project = module.params.get('project')
        target = module.params.get('target')
        query = incus_build_query(project, target)

        try:
            current = client.get(f'/1.0/{resource}/{encoded_name}{query}').get('metadata') or {}
            exists = True
        except IncusNotFoundException:
            current = {}
            exists = False

        if module.params['state'] == 'present':
            if not exists or current.get('status') in ('Pending', 'Unknown'):
                if target and not _incus_check_target_creation(module, client, resource, encoded_name, project):
                    return False
                create_data = _build_create_data(
                    module,
                    module.params['name'],
                    desired,
                    opts.create_only_params,
                    require=not exists,
                )
                if opts.name_key != 'name':
                    create_data[opts.name_key] = create_data.pop('name')
                if not module.check_mode:
                    incus_wait(
                        module,
                        client,
                        client.post(f'/1.0/{resource}{query}', create_data),
                    )
                return True
            if target:
                return False
            effective = _incus_build_effective_desired(desired, current, opts.immutable_config_keys, frozenset())
            changed = not _incus_desired_matches_current(effective, current)
            if changed and not module.check_mode:
                incus_wait(
                    module,
                    client,
                    client.put(f'/1.0/{resource}/{encoded_name}{query}', effective),
                )
            return changed

        if exists:
            if not module.check_mode:
                incus_wait(
                    module,
                    client,
                    client.delete(f'/1.0/{resource}/{encoded_name}{incus_build_query(project, target)}'),
                )
            return True
        return False


def incus_find_certificate(
    client: IncusClient,
    name: str,
) -> dict[str, Any] | None:
    """
    Find certificate by name.

    >>> incus_find_certificate(
    ...     client,
    ...     'my-cert',
    ... )
    {'name': 'my-cert', 'type': 'client', 'fingerprint': 'abc123...'}
    """
    query = incus_build_query(recursion=1)
    certificates = client.get(f'/1.0/certificates{query}').get('metadata') or []
    for certificate in certificates:
        if certificate.get('name') == name:
            result: dict[str, Any] = certificate
            return result
    return None


def incus_resolve_image_alias(
    client: IncusClient,
    alias: str,
    query: str,
) -> str | None:
    """
    Resolve image alias to fingerprint.

    >>> incus_resolve_image_alias(
    ...     client,
    ...     'debian/13',
    ...     '?project=default',
    ... )
    'abc123def456...'
    """
    encoded_alias = quote(alias, safe='')
    try:
        alias_meta = client.get(f'/1.0/images/aliases/{encoded_alias}{query}').get('metadata') or {}
        fingerprint: str | None = alias_meta.get('target')
        return fingerprint
    except IncusNotFoundException:
        return None


def incus_run_write_module(
    module: AnsibleModule,
    impl: collections.abc.Callable[[], bool],
) -> None:
    """
    Execute write module.

    >>> incus_run_write_module(
    ...     module,
    ...     impl,
    ... )
    """
    try:
        module.exit_json(changed=impl())
    except IncusClientException as exc:
        module.fail_json(msg=str(exc))


def incus_run_info_module(
    module: AnsibleModule,
    resource: str,
    return_key: str,
) -> None:
    """
    Execute info module.

    >>> incus_run_info_module(
    ...     module,
    ...     'instances',
    ...     'instances',
    ... )
    """
    name = module.params.get('name')
    project = module.params.get('project')
    result: list[Any] = []

    try:
        with incus_create_client(module) as client:
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


def incus_ensure_info(
    resource: str,
    return_key: str,
    *,
    project_scoped: bool = False,
) -> None:
    """
    Execute info module.

    >>> incus_ensure_info(
    ...     'instances',
    ...     'instances',
    ... )
    """
    args: dict[str, Any] = {'name': {'type': 'str'}}
    if project_scoped:
        args['project'] = {'type': 'str', 'default': 'default'}
    module = incus_create_info_module(args)
    incus_run_info_module(module, resource, return_key)


def incus_create_info_module(argument_spec: dict[str, Any]) -> AnsibleModule:
    """
    Create info module.

    >>> incus_create_info_module({'name': {'type': 'str'}})
    <AnsibleModule ...>
    """
    full_spec = argument_spec.copy()
    for spec_key, spec_value in INCUS_COMMON_ARGS.items():
        full_spec[spec_key] = spec_value
    return AnsibleModule(
        argument_spec=full_spec,
        supports_check_mode=True,
        mutually_exclusive=INCUS_COMMON_MUTUALLY_EXCLUSIVE,
        required_together=INCUS_COMMON_REQUIRED_TOGETHER,
        required_by=INCUS_COMMON_REQUIRED_BY,
    )


def incus_create_write_module(
    argument_spec: dict[str, Any],
    *,
    require_yaml: bool = False,
) -> AnsibleModule:
    """
    Create write module.

    >>> incus_create_write_module({'name': {'type': 'str', 'required': True}})
    <AnsibleModule ...>
    """
    full_spec = argument_spec.copy()
    for spec_key, spec_value in INCUS_COMMON_ARGS.items():
        full_spec[spec_key] = spec_value
    for spec_key, spec_value in INCUS_WRITE_ARGS.items():
        full_spec[spec_key] = spec_value
    module = AnsibleModule(
        argument_spec=full_spec,
        supports_check_mode=True,
        mutually_exclusive=INCUS_COMMON_MUTUALLY_EXCLUSIVE,
        required_together=INCUS_COMMON_REQUIRED_TOGETHER,
        required_by=INCUS_COMMON_REQUIRED_BY,
    )
    if require_yaml and not HAS_YAML:
        module.fail_json(msg='PyYAML is required for this module')
    return module


def incus_wait(
    module: AnsibleModule,
    client: IncusClient,
    response: dict[str, Any],
) -> dict[str, Any] | None:
    """
    Wait for operation.

    >>> incus_wait(
    ...     module,
    ...     client,
    ...     {'type': 'sync', 'metadata': {}},
    ... )
    """
    if module.params.get('wait', True):
        return client.wait(response)
    return None
