# -*- coding: utf-8 -*-
# Copyright: Roman Kuzmitskii <ansible@damex.org>
# SPDX-License-Identifier: GPL-3.0-or-later

"""Tests for incus_certificate module."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from ansible_collections.damex.incus.plugins.modules.incus_certificate import main
from ansible_collections.damex.incus.tests.unit.conftest import CONNECTION_PARAMS, run_module_main

__all__ = [
    'test_create_certificate',
    'test_create_missing_pem',
    'test_skip_matching_certificate',
    'test_update_restricted',
    'test_update_projects',
    'test_delete_existing_certificate',
    'test_delete_missing_certificate',
    'test_check_mode_create_certificate',
]

MODULE = 'ansible_collections.damex.incus.plugins.modules.incus_certificate'

EXISTING_CERT = {
    'fingerprint': 'abc123',
    'name': 'ansible',
    'type': 'client',
    'restricted': False,
    'projects': [],
}


def _mock_module(state: str = 'present', check_mode: bool = False,
                 certificate: str | None = 'PEM_DATA') -> MagicMock:
    """Build mock module."""
    module = MagicMock()
    module.params = {
        **CONNECTION_PARAMS,
        'name': 'ansible',
        'state': state,
        'certificate': certificate,
        'type': 'client',
        'restricted': False,
        'projects': [],
    }
    module.check_mode = check_mode
    return module


def test_create_certificate() -> None:
    """Add new certificate to trust store."""
    module = _mock_module()
    client = MagicMock()
    client.get.return_value = {'metadata': []}
    client.post.return_value = {'type': 'sync'}
    run_module_main(MODULE, module, client, main)
    module.exit_json.assert_called_once_with(changed=True)
    assert client.post.call_count == 1
    payload = client.post.call_args[0][1]
    assert payload['name'] == 'ansible'
    assert payload['certificate'] == 'PEM_DATA'


def test_create_missing_pem() -> None:
    """Fail when certificate PEM missing on create."""
    module = _mock_module(certificate=None)
    module.fail_json.side_effect = SystemExit(1)
    client = MagicMock()
    client.get.return_value = {'metadata': []}
    with pytest.raises(SystemExit):
        run_module_main(MODULE, module, client, main)
    module.fail_json.assert_called_once()


def test_skip_matching_certificate() -> None:
    """Skip when certificate already matches."""
    module = _mock_module()
    client = MagicMock()
    client.get.return_value = {'metadata': [EXISTING_CERT]}
    run_module_main(MODULE, module, client, main)
    module.exit_json.assert_called_once_with(changed=False)


def test_update_restricted() -> None:
    """Update certificate restricted flag."""
    module = _mock_module()
    module.params['restricted'] = True
    module.params['projects'] = ['default']
    client = MagicMock()
    client.get.return_value = {'metadata': [EXISTING_CERT]}
    client.put.return_value = {'type': 'sync'}
    run_module_main(MODULE, module, client, main)
    module.exit_json.assert_called_once_with(changed=True)
    client.put.assert_called_once()
    put_data = client.put.call_args[0][1]
    assert put_data['restricted'] is True
    assert put_data['projects'] == ['default']


def test_update_projects() -> None:
    """Update certificate project list."""
    module = _mock_module()
    module.params['projects'] = ['staging']
    current = {**EXISTING_CERT, 'projects': ['default']}
    client = MagicMock()
    client.get.return_value = {'metadata': [current]}
    client.put.return_value = {'type': 'sync'}
    run_module_main(MODULE, module, client, main)
    module.exit_json.assert_called_once_with(changed=True)


def test_delete_existing_certificate() -> None:
    """Delete existing certificate."""
    module = _mock_module(state='absent')
    client = MagicMock()
    client.get.return_value = {'metadata': [EXISTING_CERT]}
    client.delete.return_value = {'type': 'sync'}
    run_module_main(MODULE, module, client, main)
    module.exit_json.assert_called_once_with(changed=True)
    assert client.delete.call_count == 1
    assert client.delete.call_args[0][0] == '/1.0/certificates/abc123'


def test_delete_missing_certificate() -> None:
    """Skip delete for missing certificate."""
    module = _mock_module(state='absent')
    client = MagicMock()
    client.get.return_value = {'metadata': []}
    run_module_main(MODULE, module, client, main)
    module.exit_json.assert_called_once_with(changed=False)


def test_check_mode_create_certificate() -> None:
    """Skip API calls in check mode."""
    module = _mock_module(check_mode=True)
    client = MagicMock()
    client.get.return_value = {'metadata': []}
    run_module_main(MODULE, module, client, main)
    module.exit_json.assert_called_once_with(changed=True)
    client.post.assert_not_called()
