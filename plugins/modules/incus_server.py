#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: Roman Kuzmitskii <ansible@damex.org>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

"""Ensure Incus server configuration."""

from __future__ import annotations

DOCUMENTATION = r"""
---
module: incus_server
short_description: Ensure Incus server configuration
author: Roman Kuzmitskii (@damex) <ansible@damex.org>
description:
  - Ensures Incus server configuration via the Incus REST API.
  - When init is enabled, bootstraps the server using preseed.
  - Supports logging targets (Loki, syslog, webhook) as a validated list
    inside config that gets flattened to logging.NAME.* keys.
extends_documentation_fragment:
  - damex.incus.common
  - damex.incus.common.write
options:
  init:
    description:
      - Whether to initialize the server using preseed.
      - Always applies the preseed when enabled.
    type: bool
    default: false
  cluster:
    description:
      - Cluster configuration for preseed initialization.
      - Only used when init is enabled.
    type: dict
    suboptions:
      enabled:
        description:
          - Whether clustering is enabled.
        type: bool
      server_name:
        description:
          - Name of the cluster member.
        type: str
      server_address:
        description:
          - Address of the cluster member.
        type: str
      cluster_address:
        description:
          - Address of an existing cluster member to join.
        type: str
      cluster_certificate:
        description:
          - Expected cluster certificate in X509 PEM format.
        type: str
      cluster_token:
        description:
          - Token for joining an existing cluster.
        type: str
      member_config:
        description:
          - Member-specific configuration overrides for joining.
        type: list
        elements: dict
        suboptions:
          entity:
            description:
              - Type of entity being configured.
            type: str
            required: true
          name:
            description:
              - Name of the entity.
            type: str
            required: true
          key:
            description:
              - Configuration key to set.
            type: str
            required: true
          value:
            description:
              - Value for the configuration key.
            type: str
  config:
    description:
      - Server configuration key-value pairs.
      - Logging targets can be specified as a list under the logging key
        and will be automatically flattened to logging.NAME.* config keys.
    type: dict
    default: {}
    suboptions:
      logging:
        description:
          - List of logging targets.
          - Each target is flattened to logging.NAME.* config keys.
        type: list
        elements: dict
        suboptions:
          name:
            description:
              - Name of the logging target.
            type: str
            required: true
          target.type:
            description:
              - Type of logging target.
            type: str
            required: true
            choices:
              - loki
              - syslog
              - webhook
          target.address:
            description:
              - Address of the logging target.
            type: str
            required: true
          target.username:
            description:
              - Username for authentication.
            type: str
          target.password:
            description:
              - Password for authentication.
            type: str
          target.ca_cert:
            description:
              - CA certificate for the server.
            type: str
          target.facility:
            description:
              - Syslog facility for the log message.
            type: str
          target.labels:
            description:
              - Labels for a Loki log entry.
            type: str
          target.instance:
            description:
              - Name to use as the instance field in Loki events.
            type: str
          target.retry:
            description:
              - Number of delivery retries.
            type: int
          types:
            description:
              - Events to send to the logger.
            type: str
          lifecycle.types:
            description:
              - Lifecycle event types to send.
            type: str
          lifecycle.projects:
            description:
              - Projects to send lifecycle events for.
            type: str
          logging.level:
            description:
              - Minimum log level to send to the logger.
            type: str
"""

EXAMPLES = r"""
- name: Ensure server is initialized
  damex.incus.incus_server:
    init: true
    config:
      core.https_address: :8443

- name: Ensure server is initialized with cluster
  damex.incus.incus_server:
    init: true
    config:
      core.https_address: :8443
    cluster:
      enabled: true
      server_name: node1
      server_address: node1:8443

- name: Ensure server configuration
  damex.incus.incus_server:
    config:
      core.https_address: :8443

- name: Ensure server with Loki logging
  damex.incus.incus_server:
    config:
      core.https_address: :8443
      logging:
        - name: loki01
          target.type: loki
          target.address: https://loki.example.com:3100
          target.labels: env=prod
          types: lifecycle,logging
          logging.level: info

- name: Ensure server with syslog logging
  damex.incus.incus_server:
    config:
      logging:
        - name: syslog01
          target.type: syslog
          target.address: tcp://syslog.example.com:514
          target.facility: daemon
          types: lifecycle,logging
"""

RETURN = r"""
"""

import json
from typing import Any

from ansible_collections.damex.incus.plugins.module_utils.incus import (
    incus_create_client,
    incus_create_write_module,
    incus_run_write_module,
)
from ansible_collections.damex.incus.plugins.module_utils.common import (
    incus_common_flatten_to_config,
    incus_common_named_list_to_dict,
    incus_common_stringify_dict,
)

__all__ = ['DOCUMENTATION', 'EXAMPLES', 'RETURN', 'main']

INCUS_SERVER_CONFIG_OPTIONS: dict[str, Any] = {
    'core.bgp_address': {'type': 'str'},
    'core.bgp_asn': {'type': 'str'},
    'core.bgp_routerid': {'type': 'str'},
    'core.debug_address': {'type': 'str'},
    'core.dns_address': {'type': 'str'},
    'core.https_address': {'type': 'str'},
    'core.https_allowed_credentials': {'type': 'bool'},
    'core.https_allowed_headers': {'type': 'str'},
    'core.https_allowed_methods': {'type': 'str'},
    'core.https_allowed_origin': {'type': 'str'},
    'core.https_trusted_proxy': {'type': 'str'},
    'core.metrics_address': {'type': 'str'},
    'core.metrics_authentication': {'type': 'bool'},
    'core.proxy_http': {'type': 'str'},
    'core.proxy_https': {'type': 'str'},
    'core.proxy_ignore_hosts': {'type': 'str'},
    'core.remote_token_expiry': {'type': 'str'},
    'core.shutdown_timeout': {'type': 'int'},
    'core.storage_buckets_address': {'type': 'str'},
    'core.syslog_socket': {'type': 'bool'},
    'core.trust_ca_certificates': {'type': 'bool'},
    'acme.agree_tos': {'type': 'bool'},
    'acme.ca_url': {'type': 'str'},
    'acme.challenge': {
        'type': 'str',
        'choices': [
            'HTTP-01',
            'DNS-01',
        ],
    },
    'acme.domain': {'type': 'str'},
    'acme.email': {'type': 'str'},
    'acme.http.port': {'type': 'str'},
    'acme.provider': {'type': 'str'},
    'acme.provider.environment': {'type': 'str'},
    'acme.provider.resolvers': {'type': 'str'},
    'cluster.healing_threshold': {'type': 'int'},
    'cluster.https_address': {'type': 'str'},
    'cluster.images_minimal_replica': {'type': 'int'},
    'cluster.join_token_expiry': {'type': 'str'},
    'cluster.max_standby': {'type': 'int'},
    'cluster.max_voters': {'type': 'int'},
    'cluster.offline_threshold': {'type': 'int'},
    'cluster.rebalance.batch': {'type': 'int'},
    'cluster.rebalance.cooldown': {'type': 'str'},
    'cluster.rebalance.interval': {'type': 'int'},
    'cluster.rebalance.threshold': {'type': 'int'},
    'images.auto_update_cached': {'type': 'bool'},
    'images.auto_update_interval': {'type': 'int'},
    'images.compression_algorithm': {'type': 'str'},
    'images.default_architecture': {'type': 'str'},
    'images.remote_cache_expiry': {'type': 'int'},
    'oidc.audience': {'type': 'str'},
    'oidc.claim': {'type': 'str'},
    'oidc.client.id': {'type': 'str'},
    'oidc.issuer': {'type': 'str'},
    'oidc.scopes': {'type': 'str'},
    'openfga.api.token': {'type': 'str'},
    'openfga.api.url': {'type': 'str'},
    'openfga.store.id': {'type': 'str'},
    'authorization.scriptlet': {'type': 'str'},
    'backups.compression_algorithm': {'type': 'str'},
    'instances.lxcfs.per_instance': {'type': 'bool'},
    'instances.nic.host_name': {'type': 'str'},
    'instances.placement.scriptlet': {'type': 'str'},
    'network.ovn.ca_cert': {'type': 'str'},
    'network.ovn.client_cert': {'type': 'str'},
    'network.ovn.client_key': {'type': 'str'},
    'network.ovn.integration_bridge': {'type': 'str'},
    'network.ovn.northbound_connection': {'type': 'str'},
    'network.ovs.connection': {'type': 'str'},
    'storage.backups_volume': {'type': 'str'},
    'storage.images_volume': {'type': 'str'},
    'storage.linstor.ca_cert': {'type': 'str'},
    'storage.linstor.client_cert': {'type': 'str'},
    'storage.linstor.client_key': {'type': 'str'},
    'storage.linstor.controller_connection': {'type': 'str'},
    'storage.linstor.satellite.name': {'type': 'str'},
    'storage.logs_volume': {'type': 'str'},
}

INCUS_SERVER_LOGGING_OPTIONS = {
    'name': {
        'type': 'str',
        'required': True,
    },
    'target.type': {
        'type': 'str',
        'required': True,
        'choices': [
            'loki',
            'syslog',
            'webhook',
        ],
    },
    'target.address': {
        'type': 'str',
        'required': True,
    },
    'target.username': {'type': 'str'},
    'target.password': {
        'type': 'str',
        'no_log': True,
    },
    'target.ca_cert': {'type': 'str'},
    'target.facility': {'type': 'str'},
    'target.labels': {'type': 'str'},
    'target.instance': {'type': 'str'},
    'target.retry': {'type': 'int'},
    'types': {'type': 'str'},
    'lifecycle.types': {'type': 'str'},
    'lifecycle.projects': {'type': 'str'},
    'logging.level': {'type': 'str'},
}


def _build_desired_config(config: dict[str, Any]) -> dict[str, str]:
    """Build desired config with flattened logging."""
    logging_items = config.get('logging')
    flat_config = {key: value for key, value in config.items() if key != 'logging'}
    desired = incus_common_stringify_dict(flat_config)
    if logging_items:
        desired.update(
            incus_common_flatten_to_config(
                'logging',
                incus_common_named_list_to_dict(logging_items),
            ),
        )
    return desired


def _preseed_init(module: Any, desired_config: dict[str, str]) -> bool:
    """Initialize server with preseed."""
    if module.check_mode:
        return True
    preseed: dict[str, Any] = {'config': desired_config}
    cluster = module.params.get('cluster')
    if cluster:
        preseed['cluster'] = cluster
    rc, _stdout, stderr = module.run_command(
        ['incus', 'admin', 'init', '--preseed'],
        data=json.dumps(preseed),
    )
    if rc:
        module.fail_json(msg=f'Preseed initialization failed: {stderr}')
    return True


def _ensure_server_config(module: Any, desired_config: dict[str, str]) -> bool:
    """Ensure server config matches desired state."""
    if module.params.get('init'):
        return _preseed_init(module, desired_config)
    client = incus_create_client(module)
    current = client.get('/1.0').get('metadata', {}).get('config', {})
    if current == desired_config:
        return False
    if not module.check_mode:
        client.put('/1.0', {'config': desired_config})
    return True


def main() -> None:
    """Run module."""
    module = incus_create_write_module({
        'init': {'type': 'bool', 'default': False},
        'cluster': {'type': 'dict'},
        'config': {
            'type': 'dict',
            'default': {},
            'options': {
                **INCUS_SERVER_CONFIG_OPTIONS,
                'logging': {
                    'type': 'list',
                    'elements': 'dict',
                    'options': INCUS_SERVER_LOGGING_OPTIONS,
                },
            },
        },
    })
    desired_config = _build_desired_config(module.params['config'] or {})
    incus_run_write_module(module, lambda: _ensure_server_config(module, desired_config))


if __name__ == '__main__':
    main()
