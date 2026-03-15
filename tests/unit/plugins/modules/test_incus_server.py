# -*- coding: utf-8 -*-
# Copyright: Roman Kuzmitskii <ansible@damex.org>
# SPDX-License-Identifier: GPL-3.0-or-later

"""Tests for incus_server module."""

from __future__ import annotations

from typing import Any
from unittest.mock import MagicMock, patch

from ansible_collections.damex.incus.plugins.module_utils.incus import (
    IncusClientException,
)
from ansible_collections.damex.incus.plugins.modules.incus_server import main
from ansible_collections.damex.incus.tests.unit.conftest import (
    CONNECTION_PARAMS,
)

__all__ = [
    'test_update_server_config',
    'test_skip_matching_server_config',
    'test_update_server_logging',
    'test_skip_matching_server_logging',
    'test_update_server_config_extra_keys_removed',
    'test_init_runs_preseed',
    'test_init_with_cluster',
    'test_init_preseed_failure',
    'test_init_check_mode',
    'test_server_check_mode',
    'test_server_fail_on_exception',
]

MODULE = 'ansible_collections.damex.incus.plugins.modules.incus_server'
UTILS = 'ansible_collections.damex.incus.plugins.module_utils.incus'


def _mock_module(
    config: dict[str, Any] | None = None,
    check_mode: bool = False,
    init: bool = False,
    cluster: dict[str, Any] | None = None,
) -> MagicMock:
    """Build mock module."""
    module = MagicMock()
    module.params = {
        **CONNECTION_PARAMS,
        'init': init,
        'cluster': cluster,
        'config': config or {},
    }
    module.check_mode = check_mode
    return module


def _run_main(module: MagicMock, client: MagicMock) -> None:
    """Patch module creation and client, then run main."""
    with patch(f'{MODULE}.incus_create_write_module', return_value=module), \
         patch(f'{UTILS}.incus_create_client', return_value=client), \
         patch(f'{MODULE}.incus_create_client', return_value=client, create=True):
        main()


def test_update_server_config() -> None:
    """Update server config when values differ."""
    module = _mock_module(config={'core.https_address': ':8443'})
    client = MagicMock()
    client.get.return_value = {'metadata': {'config': {}}}
    client.put.return_value = {'type': 'sync'}
    _run_main(module, client)
    module.exit_json.assert_called_once_with(changed=True)
    client.put.assert_called_once()
    put_data = client.put.call_args[0][1]
    assert put_data['config']['core.https_address'] == ':8443'


def test_skip_matching_server_config() -> None:
    """Skip update when config already matches."""
    module = _mock_module(config={'core.https_address': ':8443'})
    client = MagicMock()
    client.get.return_value = {
        'metadata': {'config': {'core.https_address': ':8443'}},
    }
    _run_main(module, client)
    module.exit_json.assert_called_once_with(changed=False)
    client.put.assert_not_called()


def test_update_server_logging() -> None:
    """Update server config with logging targets."""
    module = _mock_module(config={
        'logging': [
            {
                'name': 'loki01',
                'target.type': 'loki',
                'target.address': 'https://loki:3100',
                'target.labels': 'env=prod',
                'types': 'lifecycle,logging',
                'logging.level': 'info',
            },
        ],
    })
    client = MagicMock()
    client.get.return_value = {'metadata': {'config': {}}}
    client.put.return_value = {'type': 'sync'}
    _run_main(module, client)
    module.exit_json.assert_called_once_with(changed=True)
    put_data = client.put.call_args[0][1]
    assert put_data['config']['logging.loki01.target.type'] == 'loki'
    assert put_data['config']['logging.loki01.target.address'] == 'https://loki:3100'
    assert put_data['config']['logging.loki01.target.labels'] == 'env=prod'
    assert put_data['config']['logging.loki01.types'] == 'lifecycle,logging'
    assert put_data['config']['logging.loki01.logging.level'] == 'info'


def test_skip_matching_server_logging() -> None:
    """Skip update when logging config already matches."""
    module = _mock_module(config={
        'logging': [
            {
                'name': 'loki01',
                'target.type': 'loki',
                'target.address': 'https://loki:3100',
            },
        ],
    })
    client = MagicMock()
    client.get.return_value = {
        'metadata': {
            'config': {
                'logging.loki01.target.type': 'loki',
                'logging.loki01.target.address': 'https://loki:3100',
            },
        },
    }
    _run_main(module, client)
    module.exit_json.assert_called_once_with(changed=False)
    client.put.assert_not_called()


def test_update_server_config_extra_keys_removed() -> None:
    """Update when current config has extra keys not in desired."""
    module = _mock_module(config={'core.https_address': ':8443'})
    client = MagicMock()
    client.get.return_value = {
        'metadata': {
            'config': {
                'core.https_address': ':8443',
                'core.metrics_address': ':9090',
            },
        },
    }
    client.put.return_value = {'type': 'sync'}
    _run_main(module, client)
    module.exit_json.assert_called_once_with(changed=True)
    client.put.assert_called_once()
    put_data = client.put.call_args[0][1]
    assert 'core.metrics_address' not in put_data['config']


def test_init_runs_preseed() -> None:
    """Run preseed when init is enabled."""
    module = _mock_module(
        config={'core.https_address': ':8443'},
        init=True,
    )
    module.run_command.return_value = (0, '', '')
    client = MagicMock()
    _run_main(module, client)
    module.exit_json.assert_called_once_with(changed=True)
    module.run_command.assert_called_once()
    client.get.assert_not_called()
    client.put.assert_not_called()


def test_init_with_cluster() -> None:
    """Include cluster in preseed when provided."""
    module = _mock_module(
        config={'core.https_address': ':8443'},
        init=True,
        cluster={
            'enabled': True,
            'server_name': 'node1',
            'server_address': 'node1:8443',
        },
    )
    module.run_command.return_value = (0, '', '')
    client = MagicMock()
    _run_main(module, client)
    module.exit_json.assert_called_once_with(changed=True)
    preseed_data = module.run_command.call_args[1]['data']
    assert '"cluster"' in preseed_data
    assert '"server_name"' in preseed_data


def test_init_preseed_failure() -> None:
    """Fail when preseed command returns error."""
    module = _mock_module(
        config={'core.https_address': ':8443'},
        init=True,
    )
    module.run_command.return_value = (1, '', 'preseed error')
    client = MagicMock()
    _run_main(module, client)
    module.fail_json.assert_called_once()


def test_init_check_mode() -> None:
    """Skip preseed in check mode."""
    module = _mock_module(
        config={'core.https_address': ':8443'},
        init=True,
        check_mode=True,
    )
    client = MagicMock()
    _run_main(module, client)
    module.exit_json.assert_called_once_with(changed=True)
    module.run_command.assert_not_called()


def test_server_check_mode() -> None:
    """Skip API calls in check mode."""
    module = _mock_module(
        config={'core.https_address': ':8443'},
        check_mode=True,
    )
    client = MagicMock()
    client.get.return_value = {'metadata': {'config': {}}}
    _run_main(module, client)
    module.exit_json.assert_called_once_with(changed=True)
    client.put.assert_not_called()


def test_server_fail_on_exception() -> None:
    """Fail on client exception."""
    module = _mock_module(config={'core.https_address': ':8443'})
    client = MagicMock()
    client.get.side_effect = IncusClientException('connection refused')
    _run_main(module, client)
    module.fail_json.assert_called_once_with(msg='connection refused')
