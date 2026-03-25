# -*- coding: utf-8 -*-
# Copyright: Roman Kuzmitskii <ansible@damex.org>
# SPDX-License-Identifier: GPL-3.0-or-later

"""Tests for source and query helpers."""

from __future__ import annotations

from unittest.mock import MagicMock

from ansible_collections.damex.incus.plugins.module_utils.incus_source import (
    incus_build_query,
    incus_build_source,
)

__all__ = [
    'test_build_query_empty',
    'test_build_query_project_only',
    'test_build_query_target_only',
    'test_build_query_recursion_only',
    'test_build_query_all_parameters',
    'test_build_query_project_url_encoded',
    'test_build_query_target_url_encoded',
    'test_build_source_plain_alias',
    'test_build_source_images_remote',
    'test_build_source_ubuntu_remote',
    'test_build_source_ubuntu_daily_remote',
    'test_build_source_docker_remote',
    'test_build_source_explicit_server',
    'test_build_source_explicit_server_overrides_remote',
    'test_build_source_unknown_remote_fails',
]


def test_build_query_empty():
    """Verify empty string when no parameters provided."""
    assert incus_build_query() == ''


def test_build_query_project_only():
    """Verify query with project parameter."""
    assert incus_build_query(project='default') == '?project=default'


def test_build_query_target_only():
    """Verify query with target parameter."""
    assert incus_build_query(target='node01') == '?target=node01'


def test_build_query_recursion_only():
    """Verify query with recursion parameter."""
    assert incus_build_query(recursion=1) == '?recursion=1'


def test_build_query_all_parameters():
    """Verify query with all parameters combined."""
    result = incus_build_query(
        project='myproject',
        target='node01',
        recursion=1,
    )
    assert result == '?project=myproject&target=node01&recursion=1'


def test_build_query_project_url_encoded():
    """Verify project name with special characters is URL-encoded."""
    result = incus_build_query(project='my project/test')
    assert result == '?project=my%20project%2Ftest'


def test_build_query_target_url_encoded():
    """Verify target name with special characters is URL-encoded."""
    result = incus_build_query(target='node/01')
    assert result == '?target=node%2F01'


def test_build_source_plain_alias():
    """Verify plain alias without remote prefix."""
    module = MagicMock()
    module.params = {
        'source': 'debian/13',
        'source_server': None,
        'source_protocol': 'simplestreams',
    }
    result = incus_build_source(module)
    assert result == {'type': 'image', 'alias': 'debian/13'}


def test_build_source_images_remote():
    """Verify images: remote resolves to linuxcontainers.org."""
    module = MagicMock()
    module.params = {
        'source': 'images:debian/13',
        'source_server': None,
        'source_protocol': 'simplestreams',
    }
    result = incus_build_source(module)
    assert result == {
        'type': 'image',
        'alias': 'debian/13',
        'server': 'https://images.linuxcontainers.org',
        'protocol': 'simplestreams',
    }


def test_build_source_ubuntu_remote():
    """Verify ubuntu: remote resolves to cloud-images releases."""
    module = MagicMock()
    module.params = {
        'source': 'ubuntu:24.04',
        'source_server': None,
        'source_protocol': 'simplestreams',
    }
    result = incus_build_source(module)
    assert result == {
        'type': 'image',
        'alias': '24.04',
        'server': 'https://cloud-images.ubuntu.com/releases',
        'protocol': 'simplestreams',
    }


def test_build_source_ubuntu_daily_remote():
    """Verify ubuntu-daily: remote resolves to cloud-images daily."""
    module = MagicMock()
    module.params = {
        'source': 'ubuntu-daily:24.04',
        'source_server': None,
        'source_protocol': 'simplestreams',
    }
    result = incus_build_source(module)
    assert result == {
        'type': 'image',
        'alias': '24.04',
        'server': 'https://cloud-images.ubuntu.com/daily',
        'protocol': 'simplestreams',
    }


def test_build_source_docker_remote():
    """Verify docker: remote resolves to docker.io with oci protocol."""
    module = MagicMock()
    module.params = {
        'source': 'docker:nginx',
        'source_server': None,
        'source_protocol': 'simplestreams',
    }
    result = incus_build_source(module)
    assert result == {
        'type': 'image',
        'alias': 'nginx',
        'server': 'https://docker.io',
        'protocol': 'oci',
    }


def test_build_source_explicit_server():
    """Verify explicit server used when no remote prefix."""
    module = MagicMock()
    module.params = {
        'source': 'myimage',
        'source_server': 'https://custom.example.com',
        'source_protocol': 'incus',
    }
    result = incus_build_source(module)
    assert result == {
        'type': 'image',
        'alias': 'myimage',
        'server': 'https://custom.example.com',
        'protocol': 'incus',
    }


def test_build_source_explicit_server_overrides_remote():
    """Verify explicit server prevents remote resolution."""
    module = MagicMock()
    module.params = {
        'source': 'images:debian/13',
        'source_server': 'https://override.example.com',
        'source_protocol': 'incus',
    }
    result = incus_build_source(module)
    assert result == {
        'type': 'image',
        'alias': 'images:debian/13',
        'server': 'https://override.example.com',
        'protocol': 'incus',
    }


def test_build_source_unknown_remote_fails():
    """Verify unknown remote prefix triggers fail_json."""
    module = MagicMock()
    module.params = {
        'source': 'unknown:debian/13',
        'source_server': None,
        'source_protocol': 'simplestreams',
    }
    incus_build_source(module)
    module.fail_json.assert_called_once()
