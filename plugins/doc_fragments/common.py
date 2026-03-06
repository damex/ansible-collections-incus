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
      - Requires O(url) and O(client_key). Mutually exclusive with O(token).
    type: path
  client_key:
    description:
      - Path to the client key for remote authentication.
      - Requires O(url) and O(client_cert).
    type: path
  server_cert:
    description:
      - Path to the server certificate for remote verification.
      - Requires O(url).
    type: path
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

    DEVICES = r"""
options:
  devices:
    description:
      - Devices as a list.
      - Each item must include a C(name) field used as the device key in the Incus API.
      - Boolean values are converted to lowercase strings.
    type: list
    elements: dict
    default: []
    suboptions:
      name:
        description: Device name used as the key in the Incus API.
        type: str
        required: true
      type:
        description: Device type.
        type: str
        choices: [disk, nic]
        required: true
      path:
        description: Filesystem mount path inside the instance (disk only).
        type: str
      pool:
        description: Incus storage pool backing the disk device (disk only).
        type: str
      source:
        description: Host path or device to pass through (disk only).
        type: str
      size:
        description: Maximum size of the disk device, e.g. C(20GiB) (disk only).
        type: str
      readonly:
        description: Expose the disk as read-only inside the instance (disk only).
        type: bool
      network:
        description: Managed Incus network to attach the NIC to (nic only).
        type: str
      nictype:
        description: NIC device sub-type, e.g. C(bridged) (nic only).
        type: str
      parent:
        description: Host bridge or interface to attach the NIC to (nic only).
        type: str
      hwaddr:
        description: Override the NIC MAC address (nic only).
        type: str
      mtu:
        description: Override the NIC MTU (nic only).
        type: str
      ipv4.address:
        description: Static IPv4 address to assign to the NIC (nic only).
        type: str
      ipv4.routes:
        description: Comma-separated IPv4 routes to add on the host for this NIC (nic only).
        type: str
      ipv6.address:
        description: Static IPv6 address to assign to the NIC (nic only).
        type: str
      ipv6.routes:
        description: Comma-separated IPv6 routes to add on host for this NIC (nic only).
        type: str
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
    choices: [simplestreams, lxd]
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
