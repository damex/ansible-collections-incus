# Copyright: Roman Kuzmitskii <ansible@damex.org>
# SPDX-License-Identifier: GPL-3.0-or-later

"""
Starlark scriptlet validation utilities.
"""

from __future__ import annotations

import ast

__all__ = [
    'INCUS_SCRIPTLET_FUNCTIONS',
    'incus_scriptlet_validate',
]

INCUS_SCRIPTLET_FUNCTIONS: dict[str, str] = {
    'instances.placement.scriptlet': 'instance_placement',
    'authorization.scriptlet': 'authorize',
}


def incus_scriptlet_validate(
    config_key: str,
    scriptlet_content: str,
) -> str | None:
    """
    Validate Starlark scriptlet syntax.

    >>> incus_scriptlet_validate(
    ...     'instances.placement.scriptlet',
    ...     'def instance_placement(request, candidate_members):\\n    return',
    ... )

    >>> incus_scriptlet_validate(
    ...     'instances.placement.scriptlet',
    ...     'def (',
    ... )
    'line 1: invalid syntax'
    """
    try:
        ast.parse(scriptlet_content)
    except SyntaxError as parse_error:
        return f"line {parse_error.lineno}: {parse_error.msg}"

    required_function = INCUS_SCRIPTLET_FUNCTIONS.get(config_key)
    if required_function and f"def {required_function}(" not in scriptlet_content:
        return f"missing required function {required_function}"

    return None
