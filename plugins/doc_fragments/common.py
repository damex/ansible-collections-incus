# -*- coding: utf-8 -*-
# Copyright: Roman Kuzmitskii <ansible@damex.org>
# SPDX-License-Identifier: GPL-3.0-or-later

"""Common documentation fragment for Incus modules."""

from __future__ import annotations

__all__ = ['ModuleDocFragment']


class ModuleDocFragment:  # pylint: disable=too-few-public-methods
    """Common connection options."""

    DOCUMENTATION = r"""
options:
  socket_path:
    description:
      - Path to the Incus Unix socket for local connections.
    type: str
    default: /var/lib/incus/unix.socket
  url:
    description:
      - URL of the remote Incus server (e.g. https://host:8443).
      - If specified, connects via HTTPS instead of Unix socket.
    type: str
  client_cert:
    description:
      - Path to the client certificate for remote authentication.
    type: path
  client_key:
    description:
      - Path to the client key for remote authentication.
    type: path
  server_cert:
    description:
      - Path to the server certificate for remote verification.
    type: path
  token:
    description:
      - Token for remote authentication.
    type: str
  validate_certs:
    description:
      - Whether to validate the server TLS certificate.
    type: bool
    default: true
"""

    PROJECT = r"""
options:
  project:
    description:
      - Incus project to query.
    type: str
    default: default
"""
