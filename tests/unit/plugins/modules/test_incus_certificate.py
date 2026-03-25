# -*- coding: utf-8 -*-
# Copyright: Roman Kuzmitskii <ansible@damex.org>
# SPDX-License-Identifier: GPL-3.0-or-later

"""Tests for incus_certificate module."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from ansible_collections.damex.incus.plugins.modules.incus_certificate import main
from ansible_collections.damex.incus.tests.unit.conftest import (
    CONNECTION_PARAMS,
    assert_exit_changed,
    assert_write_update,
    mock_incus_client,
    run_module_main,
)

__all__ = [
    'test_create_certificate',
    'test_create_missing_pem',
    'test_skip_matching_certificate',
    'test_update_restricted',
    'test_update_projects',
    'test_delete_existing_certificate',
    'test_delete_missing_certificate',
    'test_check_mode_create_certificate',
    'test_check_mode_update_certificate',
    'test_check_mode_delete_certificate',
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
    module.params = CONNECTION_PARAMS.copy()
    module.params['name'] = 'ansible'
    module.params['state'] = state
    module.params['certificate'] = certificate
    module.params['type'] = 'client'
    module.params['restricted'] = False
    module.params['projects'] = []
    module.check_mode = check_mode
    return module


def test_create_certificate() -> None:
    """Add new certificate to trust store."""
    module = _mock_module()
    client = mock_incus_client()
    client.get.return_value = {'metadata': []}
    client.post.return_value = {'type': 'sync'}
    run_module_main(MODULE, module, client, main)
    assert_exit_changed(module, True)
    assert client.post.call_count == 1
    payload = client.post.call_args[0][1]
    assert payload['name'] == 'ansible'
    assert payload['certificate'] == 'PEM_DATA'


def test_create_missing_pem() -> None:
    """Fail when certificate PEM missing on create."""
    module = _mock_module(certificate=None)
    module.fail_json.side_effect = SystemExit(1)
    client = mock_incus_client()
    client.get.return_value = {'metadata': []}
    with pytest.raises(SystemExit):
        run_module_main(MODULE, module, client, main)
    module.fail_json.assert_called_once()


def test_skip_matching_certificate() -> None:
    """Skip when certificate already matches."""
    module = _mock_module()
    client = mock_incus_client()
    client.get.return_value = {'metadata': [EXISTING_CERT]}
    run_module_main(MODULE, module, client, main)
    assert_exit_changed(module, False)


def test_update_restricted() -> None:
    """Update certificate restricted flag."""
    module = _mock_module()
    module.params['restricted'] = True
    module.params['projects'] = ['default']
    put_data = assert_write_update(main, MODULE, module, [{'metadata': [EXISTING_CERT]}])
    assert put_data['restricted'] is True
    assert put_data['projects'] == ['default']


def test_update_projects() -> None:
    """Update certificate project list."""
    module = _mock_module()
    module.params['projects'] = ['staging']
    current = EXISTING_CERT.copy()
    current['projects'] = ['default']
    assert_write_update(main, MODULE, module, [{'metadata': [current]}])


def test_delete_existing_certificate() -> None:
    """Delete existing certificate."""
    module = _mock_module(state='absent')
    client = mock_incus_client()
    client.get.return_value = {'metadata': [EXISTING_CERT]}
    client.delete.return_value = {'type': 'sync'}
    run_module_main(MODULE, module, client, main)
    assert_exit_changed(module, True)
    assert client.delete.call_count == 1
    assert client.delete.call_args[0][0] == '/1.0/certificates/abc123'


def test_delete_missing_certificate() -> None:
    """Skip delete for missing certificate."""
    module = _mock_module(state='absent')
    client = mock_incus_client()
    client.get.return_value = {'metadata': []}
    run_module_main(MODULE, module, client, main)
    assert_exit_changed(module, False)


def test_check_mode_create_certificate() -> None:
    """Skip API calls in check mode for create."""
    module = _mock_module(check_mode=True)
    client = mock_incus_client()
    client.get.return_value = {'metadata': []}
    run_module_main(MODULE, module, client, main)
    assert_exit_changed(module, True)
    client.post.assert_not_called()


def test_check_mode_update_certificate() -> None:
    """Skip API calls in check mode for update."""
    module = _mock_module(check_mode=True)
    module.params['restricted'] = True
    module.params['projects'] = ['default']
    client = mock_incus_client()
    client.get.return_value = {'metadata': [EXISTING_CERT]}
    run_module_main(MODULE, module, client, main)
    assert_exit_changed(module, True)
    client.put.assert_not_called()


def test_check_mode_delete_certificate() -> None:
    """Skip API calls in check mode for delete."""
    module = _mock_module(state='absent', check_mode=True)
    client = mock_incus_client()
    client.get.return_value = {'metadata': [EXISTING_CERT]}
    run_module_main(MODULE, module, client, main)
    assert_exit_changed(module, True)
    client.delete.assert_not_called()
