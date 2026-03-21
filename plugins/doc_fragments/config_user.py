# -*- coding: utf-8 -*-
# Copyright: Roman Kuzmitskii <ansible@damex.org>
# SPDX-License-Identifier: GPL-3.0-or-later

"""User-defined configuration documentation fragment."""

from __future__ import annotations

__all__ = ['ModuleDocFragment']


class ModuleDocFragment:  # pylint: disable=too-few-public-methods
    """User-defined configuration options."""

    DOCUMENTATION = r"""
options:
  config:
    description:
      - User-defined configuration entries.
      - Each entry is flattened to a C(user.<name>) config key.
    type: list
    elements: dict
    suboptions:
      name:
        description:
          - Configuration key name (without the user. prefix).
        type: str
        required: true
      value:
        description:
          - Configuration value.
        type: str
        required: true
"""
