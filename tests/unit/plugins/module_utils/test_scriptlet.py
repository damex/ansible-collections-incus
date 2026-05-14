# Copyright: Roman Kuzmitskii <ansible@damex.org>
# SPDX-License-Identifier: GPL-3.0-or-later

"""
Tests for Starlark scriptlet validation utilities.
"""

from __future__ import annotations

from ansible_collections.damex.incus.plugins.module_utils.scriptlet import (
    incus_scriptlet_validate,
)

__all__ = [
    'test_valid_placement_scriptlet',
    'test_valid_authorization_scriptlet',
    'test_syntax_error_caught',
    'test_missing_placement_function',
    'test_missing_authorization_function',
    'test_unknown_key_skips_function_check',
    'test_multiline_scriptlet',
]


def test_valid_placement_scriptlet() -> None:
    """Accept valid placement scriptlet."""
    scriptlet_content = (
        "def instance_placement(request, candidate_members):\n"
        "    set_target(candidate_members[0].server_name)\n"
    )
    assert incus_scriptlet_validate(
        "instances.placement.scriptlet",
        scriptlet_content,
    ) is None


def test_valid_authorization_scriptlet() -> None:
    """Accept valid authorization scriptlet."""
    scriptlet_content = (
        "def authorize(details):\n"
        "    return True\n"
    )
    assert incus_scriptlet_validate(
        "authorization.scriptlet",
        scriptlet_content,
    ) is None


def test_syntax_error_caught() -> None:
    """Catch syntax error with line number."""
    result = incus_scriptlet_validate(
        "instances.placement.scriptlet",
        "def (",
    )
    assert result is not None
    assert "line 1" in result


def test_missing_placement_function() -> None:
    """Catch missing instance_placement function."""
    scriptlet_content = (
        "def some_other_function():\n"
        "    pass\n"
    )
    result = incus_scriptlet_validate(
        "instances.placement.scriptlet",
        scriptlet_content,
    )
    assert result is not None
    assert "instance_placement" in result


def test_missing_authorization_function() -> None:
    """Catch missing authorize function."""
    scriptlet_content = (
        "def some_other_function():\n"
        "    pass\n"
    )
    result = incus_scriptlet_validate(
        "authorization.scriptlet",
        scriptlet_content,
    )
    assert result is not None
    assert "authorize" in result


def test_unknown_key_skips_function_check() -> None:
    """Skip function check for unknown config keys."""
    scriptlet_content = (
        "def whatever():\n"
        "    pass\n"
    )
    assert incus_scriptlet_validate(
        "some.other.key",
        scriptlet_content,
    ) is None


def test_multiline_scriptlet() -> None:
    """Accept complex multiline scriptlet."""
    scriptlet_content = (
        "def instance_placement(request, candidate_members):\n"
        "    cfg = request.expanded_config\n"
        "    for member in candidate_members:\n"
        "        instances = get_instances(location=member.server_name)\n"
        "        if not instances:\n"
        "            set_target(member.server_name)\n"
        "            return\n"
    )
    assert incus_scriptlet_validate(
        "instances.placement.scriptlet",
        scriptlet_content,
    ) is None
