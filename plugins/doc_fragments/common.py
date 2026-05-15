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
      - Incus Unix socket path for local connections.
    type: str
    default: /var/lib/incus/unix.socket
  url:
    description:
      - Remote Incus server URL (e.g. https://host:8443).
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
      - Client certificate path for remote authentication.
      - Requires O(url) and O(client_key_path). Mutually exclusive with O(token) and O(client_cert).
    type: str
  client_key_path:
    description:
      - Client key path for remote authentication.
      - Requires O(url) and O(client_cert_path). Mutually exclusive with O(client_key).
    type: str
  server_cert_path:
    description:
      - Server certificate path for remote verification.
      - Requires O(url). Mutually exclusive with O(server_cert).
    type: str
  token:
    description:
      - Token for remote authentication.
      - Requires O(url). Mutually exclusive with O(client_cert).
    type: str
  validate_certs:
    description:
      - Server TLS certificate validation.
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
      - Image reference to copy from, e.g. C(images:debian/13), C(ubuntu/24.04), or C(docker:library/nginx).
      - C(remote:alias) format auto-resolves well-known remotes (C(images), C(ubuntu), C(ubuntu-daily), C(docker)).
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
    choices: [simplestreams, incus, oci]
    default: simplestreams
"""

    WRITE = r"""
options:
  wait:
    description:
      - Async operation completion wait.
      - Set to C(false) for fire-and-forget behaviour.
    type: bool
    default: true
"""

    WRITE_RETURN = r"""
changed:
  description: Resource state change indicator.
  type: bool
  returned: always
changed_keys:
  description: Configuration keys that changed.
  type: list
  elements: str
  returned: always
restart_required:
  description: Indicator that the Incus daemon must be restarted for changes to take effect.
  type: bool
  returned: always
diff:
  description: Before and after state for diff mode.
  type: dict
  returned: changed
  contains:
    before:
      description: State before the change.
      type: dict
    after:
      description: State after the change.
      type: dict
"""
