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
      core.bgp_address:
        description:
          - Address to bind the BGP server to.
        type: str
      core.bgp_asn:
        description:
          - BGP Autonomous System Number for the local server.
        type: str
      core.bgp_routerid:
        description:
          - BGP router ID for the local server.
        type: str
      core.debug_address:
        description:
          - Address to bind the pprof debug server to.
        type: str
      core.dns_address:
        description:
          - Address to bind the authoritative DNS server to.
        type: str
      core.https_address:
        description:
          - Address to bind the remote API to.
        type: str
      core.https_allowed_credentials:
        description:
          - Whether to set Access-Control-Allow-Credentials.
        type: bool
      core.https_allowed_headers:
        description:
          - Access-Control-Allow-Headers header value.
        type: str
      core.https_allowed_methods:
        description:
          - Access-Control-Allow-Methods header value.
        type: str
      core.https_allowed_origin:
        description:
          - Access-Control-Allow-Origin header value.
        type: str
      core.https_trusted_proxy:
        description:
          - Comma-separated list of trusted proxy IP addresses.
        type: str
      core.metrics_address:
        description:
          - Address to bind the metrics server to.
        type: str
      core.metrics_authentication:
        description:
          - Whether to enforce authentication on the metrics endpoint.
        type: bool
      core.proxy_http:
        description:
          - HTTP proxy to use.
        type: str
      core.proxy_https:
        description:
          - HTTPS proxy to use.
        type: str
      core.proxy_ignore_hosts:
        description:
          - Hosts that do not need the proxy.
        type: str
      core.remote_token_expiry:
        description:
          - Expiry time for remote add join tokens.
        type: str
      core.shutdown_timeout:
        description:
          - Number of minutes to wait for running operations to complete before shutdown.
        type: int
      core.storage_buckets_address:
        description:
          - Address to bind the storage buckets API to.
        type: str
      core.syslog_socket:
        description:
          - Whether to enable the syslog socket listener.
        type: bool
      core.trust_ca_certificates:
        description:
          - Whether to trust CA-signed client certificates.
        type: bool
      acme.agree_tos:
        description:
          - Agree to ACME terms of service.
        type: bool
      acme.ca_url:
        description:
          - URL to the ACME CA directory.
        type: str
      acme.challenge:
        description:
          - ACME challenge type to use.
        type: str
        choices:
          - HTTP-01
          - DNS-01
      acme.domain:
        description:
          - Domain for which to issue the certificate.
        type: str
      acme.email:
        description:
          - Email address for the account registration.
        type: str
      acme.http.port:
        description:
          - Port to use for HTTP-01 challenge listener.
        type: str
      acme.provider:
        description:
          - DNS provider for DNS-01 challenge.
        type: str
      acme.provider.environment:
        description:
          - Environment variables for the DNS provider.
        type: str
      acme.provider.resolvers:
        description:
          - DNS resolvers for the DNS-01 challenge.
        type: str
      cluster.healing_threshold:
        description:
          - Threshold after which an offline cluster member is evacuated.
        type: int
      cluster.https_address:
        description:
          - Address to bind for intra-cluster communication.
        type: str
      cluster.images_minimal_replica:
        description:
          - Minimum number of cluster members that keep a copy of an image.
        type: int
      cluster.join_token_expiry:
        description:
          - Expiry time for cluster join tokens.
        type: str
      cluster.max_standby:
        description:
          - Maximum number of standby database members.
        type: int
      cluster.max_voters:
        description:
          - Maximum number of voting database members.
        type: int
      cluster.offline_threshold:
        description:
          - Seconds after which an unresponsive member is considered offline.
        type: int
      cluster.rebalance.batch:
        description:
          - Number of instances to move per rebalance batch.
        type: int
      cluster.rebalance.cooldown:
        description:
          - Cooldown period between rebalance batches.
        type: str
      cluster.rebalance.interval:
        description:
          - Interval in seconds between rebalance checks.
        type: int
      cluster.rebalance.threshold:
        description:
          - Percentage threshold to trigger instance rebalancing.
        type: int
      images.auto_update_cached:
        description:
          - Whether to auto-update cached images.
        type: bool
      images.auto_update_interval:
        description:
          - Interval in hours between image auto-update checks.
        type: int
      images.compression_algorithm:
        description:
          - Compression algorithm to use for images.
        type: str
      images.default_architecture:
        description:
          - Default architecture to use in mixed-architecture clusters.
        type: str
      images.remote_cache_expiry:
        description:
          - Number of days after which an unused cached remote image is removed.
        type: int
      oidc.audience:
        description:
          - Expected audience value for the OIDC provider.
        type: str
      oidc.claim:
        description:
          - OIDC claim to use as the username.
        type: str
      oidc.client.id:
        description:
          - OIDC client ID for the Incus server.
        type: str
      oidc.issuer:
        description:
          - Issuer URL for the OIDC provider.
        type: str
      oidc.scopes:
        description:
          - Comma-separated list of OIDC scopes to request.
        type: str
      openfga.api.token:
        description:
          - API token for the OpenFGA server.
        type: str
      openfga.api.url:
        description:
          - URL of the OpenFGA server.
        type: str
      openfga.store.id:
        description:
          - OpenFGA store ID.
        type: str
      authorization.scriptlet:
        description:
          - Starlark scriptlet for custom authorization logic.
        type: str
      backups.compression_algorithm:
        description:
          - Compression algorithm to use for backups.
        type: str
      instances.lxcfs.per_instance:
        description:
          - Whether to use a per-instance LXCFS process.
        type: bool
      instances.nic.host_name:
        description:
          - How to set the host name for a NIC.
        type: str
      instances.placement.scriptlet:
        description:
          - Starlark scriptlet for custom instance placement.
        type: str
      network.ovn.ca_cert:
        description:
          - CA certificate for the OVN northbound connection.
        type: str
      network.ovn.client_cert:
        description:
          - Client certificate for the OVN northbound connection.
        type: str
      network.ovn.client_key:
        description:
          - Client key for the OVN northbound connection.
        type: str
      network.ovn.integration_bridge:
        description:
          - Name of the OVS integration bridge to use.
        type: str
      network.ovn.northbound_connection:
        description:
          - OVN northbound database connection string.
        type: str
      network.ovs.connection:
        description:
          - OVS database connection string.
        type: str
      storage.backups_volume:
        description:
          - Volume to use for storing backup tarballs.
        type: str
      storage.images_volume:
        description:
          - Volume to use for storing image tarballs.
        type: str
      storage.linstor.ca_cert:
        description:
          - CA certificate for the LINSTOR controller connection.
        type: str
      storage.linstor.client_cert:
        description:
          - Client certificate for the LINSTOR controller connection.
        type: str
      storage.linstor.client_key:
        description:
          - Client key for the LINSTOR controller connection.
        type: str
      storage.linstor.controller_connection:
        description:
          - LINSTOR controller connection string.
        type: str
      storage.linstor.satellite.name:
        description:
          - LINSTOR satellite node name for this server.
        type: str
      storage.logs_volume:
        description:
          - Volume to use for storing log files.
        type: str
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
    'core.remote_token_expiry': {'type': 'str', 'no_log': False},
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
    'cluster.join_token_expiry': {'type': 'str', 'no_log': False},
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
    'openfga.api.token': {'type': 'str', 'no_log': True},
    'openfga.api.url': {'type': 'str'},
    'openfga.store.id': {'type': 'str'},
    'authorization.scriptlet': {'type': 'str'},
    'backups.compression_algorithm': {'type': 'str'},
    'instances.lxcfs.per_instance': {'type': 'bool'},
    'instances.nic.host_name': {'type': 'str'},
    'instances.placement.scriptlet': {'type': 'str'},
    'network.ovn.ca_cert': {'type': 'str'},
    'network.ovn.client_cert': {'type': 'str'},
    'network.ovn.client_key': {'type': 'str', 'no_log': True},
    'network.ovn.integration_bridge': {'type': 'str'},
    'network.ovn.northbound_connection': {'type': 'str'},
    'network.ovs.connection': {'type': 'str'},
    'storage.backups_volume': {'type': 'str'},
    'storage.images_volume': {'type': 'str'},
    'storage.linstor.ca_cert': {'type': 'str'},
    'storage.linstor.client_cert': {'type': 'str'},
    'storage.linstor.client_key': {'type': 'str', 'no_log': True},
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
        for config_key, config_value in incus_common_flatten_to_config(
            'logging',
            incus_common_named_list_to_dict(logging_items),
        ).items():
            desired[config_key] = config_value
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
