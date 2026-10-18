# Copyright: Roman Kuzmitskii <ansible@damex.org>
# SPDX-License-Identifier: GPL-3.0-or-later

"""Tests for Incus config secret discovery and registration."""

from __future__ import annotations

from typing import Any
from unittest.mock import patch

from ansible_collections.damex.incus.plugins.module_utils.incus import incus_stringify_instance_config
from ansible_collections.damex.incus.plugins.module_utils.instance_config import INCUS_INSTANCE_CONFIG_OPTIONS
from ansible_collections.damex.incus.plugins.module_utils.secret import (
    incus_secret_collect_config,
    incus_secret_register_configs,
)

__all__ = [
    'test_collect_config_flat_no_log',
    'test_collect_config_skips_no_log_false',
    'test_collect_config_skips_unknown_key',
    'test_collect_config_list_prefix',
    'test_collect_config_list_dotted_field',
    'test_collect_config_list_dotted_name',
    'test_collect_config_list_skips_other_prefix',
    'test_collect_config_cloud_init_secrets',
    'test_collect_config_cloud_init_folded_value',
    'test_collect_config_cloud_init_quoted_value',
    'test_collect_config_cloud_init_complex_key',
    'test_collect_config_cloud_init_without_secrets',
    'test_collect_config_cloud_init_invalid_yaml',
    'test_collect_config_cloud_init_not_mapping',
    'test_collect_config_cloud_init_without_yaml',
    'test_register_configs_registers_collected',
    'test_register_configs_registers_all_configs_once',
]

SECRET_UTILS: str = 'ansible_collections.damex.incus.plugins.module_utils.secret'

SERVER_OPTIONS: dict[str, Any] = {
    'loki.auth.password': {'type': 'str', 'no_log': True},
    'loki.api.url': {'type': 'str'},
    'core.remote_token_expiry': {'type': 'str', 'no_log': False},
    'logging': {
        'type': 'list',
        'elements': 'dict',
        'options': {
            'name': {'type': 'str', 'required': True},
            'target.address': {'type': 'str'},
            'target.password': {'type': 'str', 'no_log': True},
        },
    },
}

NETWORK_OPTIONS: dict[str, Any] = {
    'bgp_peers': {
        'type': 'list',
        'elements': 'dict',
        'options': {
            'name': {'type': 'str', 'required': True},
            'asn': {'type': 'int'},
            'password': {'type': 'str', 'no_log': True},
        },
    },
}


def _mask(document: str, secrets: set[str]) -> str:
    """Replace secrets in document, longest first."""
    masked = document
    for secret in sorted(secrets, key=len, reverse=True):
        masked = masked.replace(secret, '$REDACTED$')
    return masked


def test_collect_config_flat_no_log() -> None:
    """Collect flat no_log config value."""
    config = {'loki.auth.password': 'lokipass', 'loki.api.url': 'http://loki'}
    assert incus_secret_collect_config(config, SERVER_OPTIONS) == {'lokipass'}


def test_collect_config_skips_no_log_false() -> None:
    """Skip config value marked no_log false."""
    config = {'core.remote_token_expiry': '1d'}
    assert not incus_secret_collect_config(config, SERVER_OPTIONS)


def test_collect_config_skips_unknown_key() -> None:
    """Skip config key missing from spec."""
    config = {'user.note': 'visible'}
    assert not incus_secret_collect_config(config, SERVER_OPTIONS)


def test_collect_config_list_prefix() -> None:
    """Collect no_log field from flattened list keys."""
    config = {
        'bgp.peers.router.asn': '64601',
        'bgp.peers.router.password': 'bgppass',
        'bgp.peers.backup.password': 'backuppass',
    }
    result = incus_secret_collect_config(config, NETWORK_OPTIONS, {'bgp_peers': 'bgp.peers'})
    assert result == {'bgppass', 'backuppass'}


def test_collect_config_list_dotted_field() -> None:
    """Collect no_log dotted field from flattened list keys."""
    config = {
        'logging.remote.target.address': 'loki.example.com',
        'logging.remote.target.password': 'targetpass',
    }
    result = incus_secret_collect_config(config, SERVER_OPTIONS, {'logging': 'logging'})
    assert result == {'targetpass'}


def test_collect_config_list_dotted_name() -> None:
    """Collect no_log field when item name contains dots."""
    config = {'bgp.peers.edge.router.password': 'edgepass', 'bgp.peers.edge.router.asn': '64601'}
    result = incus_secret_collect_config(config, NETWORK_OPTIONS, {'bgp_peers': 'bgp.peers'})
    assert result == {'edgepass'}


def test_collect_config_list_skips_other_prefix() -> None:
    """Skip keys outside list prefix."""
    config = {'tunnel.site.password': 'notsecret'}
    assert not incus_secret_collect_config(config, NETWORK_OPTIONS, {'bgp_peers': 'bgp.peers'})


def test_collect_config_cloud_init_secrets() -> None:
    """Collect cloud-init no_log values and rendered document."""
    config = incus_stringify_instance_config({
        'cloud-init.user-data': {
            'password': 'defaultpass',
            'users': [
                {
                    'name': 'admin',
                    'passwd': 'hashpass',
                    'plain_text_passwd': 'plainpass',
                    'hashed_passwd': 'hashedpass',
                },
            ],
            'chpasswd': {'users': [{'name': 'root', 'password': 'rootpass'}]},
            'hostname': 'visible',
        },
    })
    result = incus_secret_collect_config(config, INCUS_INSTANCE_CONFIG_OPTIONS)
    assert result == {
        'defaultpass',
        'hashpass',
        'plainpass',
        'hashedpass',
        'rootpass',
    }


def test_collect_config_cloud_init_folded_value() -> None:
    """Mask multi-line secret folded by YAML and keep rest of document."""
    private_key = '-----BEGIN OPENSSH PRIVATE KEY-----\nKEYLINEONE\nKEYLINETWO\n-----END OPENSSH PRIVATE KEY-----\n'
    config = incus_stringify_instance_config({
        'cloud-init.vendor-data': {'ssh_keys': {'ed25519_private': private_key}, 'hostname': 'web'},
    })
    rendered = config['cloud-init.vendor-data']
    result = incus_secret_collect_config(config, INCUS_INSTANCE_CONFIG_OPTIONS)
    assert private_key not in rendered
    assert rendered not in result
    masked = _mask(rendered, result)
    assert 'KEYLINEONE' not in masked
    assert 'hostname: web' in masked


def test_collect_config_cloud_init_quoted_value() -> None:
    """Mask secret quoted by YAML and keep rest of document."""
    config = incus_stringify_instance_config({
        'cloud-init.user-data': {'users': [{'name': 'admin', 'passwd': "it's: secret"}]},
    })
    rendered = config['cloud-init.user-data']
    masked = _mask(rendered, incus_secret_collect_config(config, INCUS_INSTANCE_CONFIG_OPTIONS))
    assert 'secret' not in masked
    assert 'name: admin' in masked


def test_collect_config_cloud_init_complex_key() -> None:
    """Skip non-scalar mapping key."""
    config = {'cloud-init.user-data': '#cloud-config\n? [a, b]\n: value\npassword: pass\n'}
    assert incus_secret_collect_config(config, INCUS_INSTANCE_CONFIG_OPTIONS) == {'pass'}


def test_collect_config_cloud_init_without_secrets() -> None:
    """Skip rendered document without no_log values."""
    config = incus_stringify_instance_config({
        'cloud-init.user-data': {'hostname': 'web', 'packages': ['nginx']},
    })
    assert not incus_secret_collect_config(config, INCUS_INSTANCE_CONFIG_OPTIONS)


def test_collect_config_cloud_init_invalid_yaml() -> None:
    """Collect whole value when YAML is invalid."""
    config = {'cloud-init.user-data': '#cloud-config\npassword: [unclosed\n'}
    assert incus_secret_collect_config(config, INCUS_INSTANCE_CONFIG_OPTIONS) == {
        '#cloud-config\npassword: [unclosed\n',
    }


def test_collect_config_cloud_init_not_mapping() -> None:
    """Skip cloud-init value that is not a mapping."""
    config = {'cloud-init.user-data': '#!/bin/sh\necho ready\n'}
    assert not incus_secret_collect_config(config, INCUS_INSTANCE_CONFIG_OPTIONS)


def test_collect_config_cloud_init_without_yaml() -> None:
    """Collect whole value when PyYAML is missing."""
    config = {'cloud-init.user-data': '#cloud-config\nhostname: web\n'}
    with patch(f'{SECRET_UTILS}.HAS_YAML', False):
        result = incus_secret_collect_config(config, INCUS_INSTANCE_CONFIG_OPTIONS)
    assert result == {'#cloud-config\nhostname: web\n'}


def test_register_configs_registers_collected() -> None:
    """Register collected values."""
    with patch(f'{SECRET_UTILS}.register_secrets') as mock_register_secrets:
        incus_secret_register_configs([{'loki.auth.password': 'lokipass'}], SERVER_OPTIONS)
    mock_register_secrets.assert_called_once_with({'lokipass'})


def test_register_configs_registers_all_configs_once() -> None:
    """Register values from every config in one call."""
    with patch(f'{SECRET_UTILS}.register_secrets') as mock_register_secrets:
        incus_secret_register_configs(
            [{'loki.auth.password': 'oldpass'}, {'loki.auth.password': 'newpass'}],
            SERVER_OPTIONS,
        )
    mock_register_secrets.assert_called_once_with({'oldpass', 'newpass'})
