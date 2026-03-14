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
      - Client certificate content for remote authentication.
      - Requires O(url) and O(client_key). Mutually exclusive with O(token) and O(client_cert_path).
    type: str
  client_key:
    description:
      - Client key content for remote authentication.
      - Requires O(url) and O(client_cert). Mutually exclusive with O(client_key_path).
    type: str
  server_cert:
    description:
      - Server certificate content for remote verification.
      - Requires O(url). Mutually exclusive with O(server_cert_path).
    type: str
  client_cert_path:
    description:
      - Path to the client certificate for remote authentication.
      - Requires O(url) and O(client_key_path). Mutually exclusive with O(token) and O(client_cert).
    type: str
  client_key_path:
    description:
      - Path to the client key for remote authentication.
      - Requires O(url) and O(client_cert_path). Mutually exclusive with O(client_key).
    type: str
  server_cert_path:
    description:
      - Path to the server certificate for remote verification.
      - Requires O(url). Mutually exclusive with O(server_cert).
    type: str
  token:
    description:
      - Token for remote authentication.
      - Requires O(url). Mutually exclusive with O(client_cert).
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

    SOURCE = r"""
options:
  source:
    description:
      - Image reference to copy from, e.g. C(images:debian/13) or C(ubuntu/24.04).
      - The C(remote:alias) format auto-resolves well-known remotes (C(images), C(ubuntu), C(ubuntu-daily)).
    type: str
  source_server:
    description:
      - URL of the image server to pull from, e.g. C(https://images.linuxcontainers.org).
      - Takes precedence over auto-resolved remotes when O(source) uses the C(remote:alias) format.
    type: str
  source_protocol:
    description:
      - Protocol used to communicate with O(source_server).
    type: str
    choices: [simplestreams, incus]
    default: simplestreams
"""

    WRITE = r"""
options:
  wait:
    description:
      - Whether to wait for async operations to complete before returning.
      - Set to C(false) for fire-and-forget behaviour.
    type: bool
    default: true
"""
