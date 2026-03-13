# -*- coding: utf-8 -*-
# Copyright: Roman Kuzmitskii <ansible@damex.org>
# SPDX-License-Identifier: GPL-3.0-or-later

"""Tests for incus module utilities."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from ansible_collections.damex.incus.plugins.module_utils.incus import (
    IncusClientException,
    IncusNotFoundException,
    incus_build_desired,
    incus_build_query,
    incus_build_source,
    incus_find_certificate,
    incus_resolve_image_alias,
    incus_run_info_module,
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
    'test_stringify_instance_config_cloud_init_users_list',
    'test_stringify_instance_config_cloud_init_ssh_keys',
    'test_stringify_instance_config_cloud_init_nested_dicts',
    'test_stringify_instance_config_cloud_init_freeform_dict',
    'test_stringify_instance_config_cloud_init_mounts',
    'test_stringify_instance_config_network_dhcp6',
    'test_stringify_instance_config_network_gateway_mtu',
    'test_stringify_instance_config_network_routes_metric',
    'test_stringify_instance_config_network_nameservers_search',
    'test_stringify_instance_config_network_set_name',
    'test_build_source_known_remote',
    'test_build_source_ubuntu_remote',
    'test_build_source_explicit_server',
    'test_build_source_local_alias',
    'test_build_source_unknown_remote_fails',
    'test_build_query_no_params',
    'test_build_query_project_only',
    'test_build_query_target_only',
    'test_build_query_project_and_target',
    'test_build_query_encodes_project',
    'test_build_query_encodes_target',
    'test_build_query_recursion_only',
    'test_build_query_project_and_recursion',
    'test_build_desired_without_devices',
    'test_build_desired_with_devices',
    'test_build_desired_devices_none',
    'test_wait_true',
    'test_wait_false',
    'test_wait_default',
    'test_run_write_module_success_changed',
    'test_run_write_module_success_unchanged',
    'test_run_write_module_client_exception',
    'test_run_info_module_single_resource',
    'test_run_info_module_not_found',
    'test_run_info_module_list_all',
    'test_run_info_module_project_query',
    'test_run_info_module_client_exception',
    'test_run_info_module_encodes_name',
    'test_run_info_module_encodes_project',
    'test_find_certificate_found',
    'test_find_certificate_not_found',
    'test_find_certificate_empty_list',
    'test_resolve_image_alias_found',
    'test_resolve_image_alias_not_found',
    'test_resolve_image_alias_encodes_name',
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


def test_stringify_instance_config_cloud_init_users_list() -> None:
    """Serialize users list to YAML."""
    config = {'cloud-init.user-data': {
        'users': [
            {'name': 'deploy', 'groups': 'sudo', 'shell': '/bin/bash'},
        ],
    }}
    result = incus_stringify_instance_config(config)
    assert 'users:' in result['cloud-init.user-data']
    assert 'deploy' in result['cloud-init.user-data']
    assert 'sudo' in result['cloud-init.user-data']


def test_stringify_instance_config_cloud_init_ssh_keys() -> None:
    """Serialize ssh_keys dict to YAML."""
    config = {'cloud-init.user-data': {
        'ssh_keys': {
            'ed25519_private': 'PRIVATE_KEY',
            'ed25519_public': 'PUBLIC_KEY',
        },
    }}
    result = incus_stringify_instance_config(config)
    assert 'PRIVATE_KEY' in result['cloud-init.user-data']
    assert 'PUBLIC_KEY' in result['cloud-init.user-data']


def test_stringify_instance_config_cloud_init_nested_dicts() -> None:
    """Serialize nested cloud-init dicts to YAML."""
    config = {'cloud-init.user-data': {
        'apt': {'proxy': 'http://proxy:3128'},
        'ntp': {'enabled': True, 'servers': ['ntp.example.com']},
        'growpart': {'mode': 'auto', 'devices': ['/']},
    }}
    result = incus_stringify_instance_config(config)
    assert 'proxy: http://proxy:3128' in result['cloud-init.user-data']
    assert 'ntp.example.com' in result['cloud-init.user-data']
    assert "mode: auto" in result['cloud-init.user-data']


def test_stringify_instance_config_cloud_init_freeform_dict() -> None:
    """Serialize free-form disk_setup dict to YAML."""
    config = {'cloud-init.user-data': {
        'disk_setup': {'/dev/vdb': {'table_type': 'gpt', 'layout': True}},
    }}
    result = incus_stringify_instance_config(config)
    assert '/dev/vdb' in result['cloud-init.user-data']
    assert 'table_type: gpt' in result['cloud-init.user-data']


def test_stringify_instance_config_cloud_init_mounts() -> None:
    """Serialize mounts as list of lists."""
    config = {'cloud-init.user-data': {
        'mounts': [['/dev/vdb1', '/data', 'ext4', 'defaults', '0', '2']],
    }}
    result = incus_stringify_instance_config(config)
    assert '/dev/vdb1' in result['cloud-init.user-data']
    assert '/data' in result['cloud-init.user-data']


def test_stringify_instance_config_network_dhcp6() -> None:
    """Serialize network config with DHCPv6."""
    config = {'cloud-init.network-config': {
        'version': 2,
        'ethernets': [{'name': 'eth0', 'dhcp4': True, 'dhcp6': True}],
    }}
    result = incus_stringify_instance_config(config)
    assert 'dhcp6: true' in result['cloud-init.network-config']


def test_stringify_instance_config_network_gateway_mtu() -> None:
    """Serialize network config with gateway and MTU."""
    config = {'cloud-init.network-config': {
        'version': 2,
        'ethernets': [{
            'name': 'eth0',
            'addresses': ['10.0.0.2/24'],
            'gateway4': '10.0.0.1',
            'mtu': 9000,
        }],
    }}
    result = incus_stringify_instance_config(config)
    assert 'gateway4: 10.0.0.1' in result['cloud-init.network-config']
    assert 'mtu: 9000' in result['cloud-init.network-config']


def test_stringify_instance_config_network_routes_metric() -> None:
    """Serialize network routes with metric."""
    config = {'cloud-init.network-config': {
        'version': 2,
        'ethernets': [{
            'name': 'eth0',
            'routes': [{'to': '0.0.0.0/0', 'via': '10.0.0.1', 'metric': 100}],
        }],
    }}
    result = incus_stringify_instance_config(config)
    assert 'metric: 100' in result['cloud-init.network-config']


def test_stringify_instance_config_network_nameservers_search() -> None:
    """Serialize nameservers with search domains."""
    config = {'cloud-init.network-config': {
        'version': 2,
        'ethernets': [{
            'name': 'eth0',
            'nameservers': {
                'addresses': ['8.8.8.8'],
                'search': ['example.com'],
            },
        }],
    }}
    result = incus_stringify_instance_config(config)
    assert 'example.com' in result['cloud-init.network-config']


def test_stringify_instance_config_network_set_name() -> None:
    """Serialize set-name on ethernet interfaces."""
    config = {'cloud-init.network-config': {
        'version': 2,
        'ethernets': [{
            'name': 'id0',
            'match': {'macaddress': '00:11:22:33:44:55'},
            'set-name': 'lan0',
        }],
    }}
    result = incus_stringify_instance_config(config)
    assert 'set-name: lan0' in result['cloud-init.network-config']


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
    module.fail_json.side_effect = SystemExit(1)
    module.params = {'source': 'unknown:image', 'source_server': None, 'source_protocol': None}
    with pytest.raises(SystemExit):
        incus_build_source(module)
    module.fail_json.assert_called_once()


def test_build_query_no_params() -> None:
    """Return empty string without params."""
    assert not incus_build_query(None, None)


def test_build_query_project_only() -> None:
    """Return project query."""
    assert incus_build_query('myproject', None) == '?project=myproject'


def test_build_query_target_only() -> None:
    """Return target query."""
    assert incus_build_query(None, 'node1') == '?target=node1'


def test_build_query_project_and_target() -> None:
    """Return combined query."""
    assert incus_build_query('myproject', 'node1') == '?project=myproject&target=node1'


def test_build_query_encodes_project() -> None:
    """Encode special characters in project name."""
    assert incus_build_query(project='my project&x') == '?project=my%20project%26x'


def test_build_query_encodes_target() -> None:
    """Encode special characters in target name."""
    assert incus_build_query(target='node/1') == '?target=node%2F1'


def test_build_query_recursion_only() -> None:
    """Return recursion query."""
    assert incus_build_query(recursion=1) == '?recursion=1'


def test_build_query_project_and_recursion() -> None:
    """Return project and recursion query."""
    assert incus_build_query(project='default', recursion=1) == '?project=default&recursion=1'


def test_build_desired_without_devices() -> None:
    """Build desired with config only."""
    module = MagicMock()
    module.params = {'description': 'test pool', 'config': {'size': 10}}
    result = incus_build_desired(module)
    assert result == {'description': 'test pool', 'config': {'size': '10'}}
    assert 'devices' not in result


def test_build_desired_with_devices() -> None:
    """Build desired with devices and instance config."""
    module = MagicMock()
    module.params = {
        'description': 'test profile',
        'config': {'boot.autostart': True},
        'devices': [{'name': 'root', 'type': 'disk', 'pool': 'local', 'path': '/'}],
    }
    result = incus_build_desired(module)
    assert result['description'] == 'test profile'
    assert result['config'] == {'boot.autostart': 'true'}
    assert result['devices'] == {'root': {'type': 'disk', 'pool': 'local', 'path': '/'}}


def test_build_desired_devices_none() -> None:
    """Treat devices=None as no devices."""
    module = MagicMock()
    module.params = {'description': '', 'config': {'size': 5}, 'devices': None}
    result = incus_build_desired(module)
    assert result == {'description': '', 'config': {'size': '5'}}
    assert 'devices' not in result


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


def _info_module(name: str | None = None, project: str | None = None) -> MagicMock:
    """Build mock info module."""
    module = MagicMock()
    module.params = {**CONNECTION_PARAMS, 'name': name, 'project': project}
    return module


@patch('ansible_collections.damex.incus.plugins.module_utils.incus.incus_create_client')
def test_run_info_module_single_resource(mock_create_client: MagicMock) -> None:
    """Return single resource as list."""
    client = MagicMock()
    client.get.return_value = {'metadata': {'name': 'pool1', 'driver': 'zfs'}}
    mock_create_client.return_value = client

    module = _info_module(name='pool1')
    incus_run_info_module(module, 'storage-pools', 'storage_pools')

    module.exit_json.assert_called_once_with(storage_pools=[{'name': 'pool1', 'driver': 'zfs'}])


@patch('ansible_collections.damex.incus.plugins.module_utils.incus.incus_create_client')
def test_run_info_module_not_found(mock_create_client: MagicMock) -> None:
    """Return empty list when resource not found."""
    client = MagicMock()
    client.get.side_effect = IncusNotFoundException('not found')
    mock_create_client.return_value = client

    module = _info_module(name='missing')
    incus_run_info_module(module, 'storage-pools', 'storage_pools')

    module.exit_json.assert_called_once_with(storage_pools=[])


@patch('ansible_collections.damex.incus.plugins.module_utils.incus.incus_create_client')
def test_run_info_module_list_all(mock_create_client: MagicMock) -> None:
    """Return all resources."""
    client = MagicMock()
    items = [{'name': 'a'}, {'name': 'b'}]
    client.get.return_value = {'metadata': items}
    mock_create_client.return_value = client

    module = _info_module()
    incus_run_info_module(module, 'networks', 'networks')

    module.exit_json.assert_called_once_with(networks=items)
    assert '?recursion=1' in client.get.call_args[0][0]


@patch('ansible_collections.damex.incus.plugins.module_utils.incus.incus_create_client')
def test_run_info_module_project_query(mock_create_client: MagicMock) -> None:
    """Include project in query."""
    client = MagicMock()
    client.get.return_value = {'metadata': []}
    mock_create_client.return_value = client

    module = _info_module(project='myproject')
    incus_run_info_module(module, 'networks', 'networks')

    path = client.get.call_args[0][0]
    assert '?project=myproject' in path
    assert 'recursion=1' in path


@patch('ansible_collections.damex.incus.plugins.module_utils.incus.incus_create_client')
def test_run_info_module_encodes_name(mock_create_client: MagicMock) -> None:
    """Encode special characters in resource name."""
    client = MagicMock()
    client.get.return_value = {'metadata': {'name': 'pool/special'}}
    mock_create_client.return_value = client

    module = _info_module(name='pool/special')
    incus_run_info_module(module, 'storage-pools', 'storage_pools')

    path = client.get.call_args[0][0]
    assert '/1.0/storage-pools/pool%2Fspecial' in path


@patch('ansible_collections.damex.incus.plugins.module_utils.incus.incus_create_client')
def test_run_info_module_encodes_project(mock_create_client: MagicMock) -> None:
    """Encode special characters in project query param."""
    client = MagicMock()
    client.get.return_value = {'metadata': []}
    mock_create_client.return_value = client

    module = _info_module(project='my project')
    incus_run_info_module(module, 'networks', 'networks')

    path = client.get.call_args[0][0]
    assert 'project=my%20project' in path


@patch('ansible_collections.damex.incus.plugins.module_utils.incus.incus_create_client')
def test_run_info_module_client_exception(mock_create_client: MagicMock) -> None:
    """Fail on client exception."""
    client = MagicMock()
    client.get.side_effect = IncusClientException('connection refused')
    mock_create_client.return_value = client

    module = _info_module(name='test')
    module.fail_json.side_effect = SystemExit(1)
    with pytest.raises(SystemExit):
        incus_run_info_module(module, 'storage-pools', 'storage_pools')
    module.fail_json.assert_called_once_with(msg='connection refused')


def test_find_certificate_found() -> None:
    """Return certificate matching name."""
    client = MagicMock()
    client.get.return_value = {
        'metadata': [
            {'name': 'other', 'fingerprint': 'aaa'},
            {'name': 'ansible', 'fingerprint': 'bbb'},
        ],
    }
    result = incus_find_certificate(client, 'ansible')
    assert result is not None
    assert result['fingerprint'] == 'bbb'


def test_find_certificate_not_found() -> None:
    """Return None when no certificate matches."""
    client = MagicMock()
    client.get.return_value = {
        'metadata': [{'name': 'other', 'fingerprint': 'aaa'}],
    }
    result = incus_find_certificate(client, 'missing')
    assert result is None


def test_find_certificate_empty_list() -> None:
    """Return None when certificate list is empty."""
    client = MagicMock()
    client.get.return_value = {'metadata': []}
    result = incus_find_certificate(client, 'ansible')
    assert result is None


def test_resolve_image_alias_found() -> None:
    """Return fingerprint for existing alias."""
    client = MagicMock()
    client.get.return_value = {'metadata': {'target': 'abc123'}}
    result = incus_resolve_image_alias(client, 'debian/12', '?project=default')
    assert result == 'abc123'


def test_resolve_image_alias_not_found() -> None:
    """Return None when alias does not exist."""
    client = MagicMock()
    client.get.side_effect = IncusNotFoundException('not found')
    result = incus_resolve_image_alias(client, 'missing', '?project=default')
    assert result is None


def test_resolve_image_alias_encodes_name() -> None:
    """Encode special characters in alias name."""
    client = MagicMock()
    client.get.return_value = {'metadata': {'target': 'def456'}}
    incus_resolve_image_alias(client, 'ubuntu/24.04', '?project=default')
    path = client.get.call_args[0][0]
    assert '/1.0/images/aliases/ubuntu%2F24.04?project=default' == path
