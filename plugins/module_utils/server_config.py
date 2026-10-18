# Copyright: Roman Kuzmitskii <ansible@damex.org>
# SPDX-License-Identifier: GPL-3.0-or-later

"""
Incus server config argument spec options.
"""

from __future__ import annotations

from typing import Any

__all__ = [
    'INCUS_SERVER_CONFIG_OPTIONS',
    'INCUS_SERVER_LOGGING_OPTIONS',
    'incus_build_server_config_options',
]

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
    'authorization.openfga.api.token': {'type': 'str', 'no_log': True},
    'authorization.openfga.api.url': {'type': 'str'},
    'authorization.openfga.store.id': {'type': 'str'},
    'authorization.openfga.tls.identifier': {
        'type': 'str',
        'choices': [
            'fingerprint',
            'name',
        ],
    },
    'authorization.client.default': {
        'type': 'str',
        'choices': [
            'allow',
            'deny',
            'openfga',
            'scriptlet',
        ],
    },
    'authorization.client.oidc': {
        'type': 'str',
        'choices': [
            'allow',
            'deny',
            'openfga',
            'scriptlet',
        ],
    },
    'authorization.client.tls': {
        'type': 'str',
        'choices': [
            'allow',
            'deny',
            'openfga',
            'scriptlet',
        ],
    },
    'authorization.client.tls-restricted': {
        'type': 'str',
        'choices': [
            'allow',
            'deny',
            'tls',
            'openfga',
            'scriptlet',
        ],
    },
    'authorization.client.unix': {
        'type': 'str',
        'choices': [
            'allow',
            'deny',
            'openfga',
            'scriptlet',
        ],
    },
    'authorization.scriptlet': {'type': 'str'},
    'backups.compression_algorithm': {'type': 'str'},
    'instances.lxcfs.per_instance': {'type': 'bool'},
    'instances.nic.host_name': {'type': 'str'},
    'instances.placement.scriptlet': {'type': 'str'},
    'network.hwaddr_pattern': {'type': 'str'},
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
    'loki.api.ca_cert': {'type': 'str'},
    'loki.api.url': {'type': 'str'},
    'loki.auth.password': {'type': 'str', 'no_log': True},
    'loki.auth.username': {'type': 'str'},
    'loki.instance': {'type': 'str'},
    'loki.labels': {'type': 'str'},
    'loki.loglevel': {'type': 'str'},
    'loki.types': {'type': 'str'},
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


def incus_build_server_config_options() -> dict[str, Any]:
    """
    Build server config options.

    >>> incus_build_server_config_options()['logging']['type']
    'list'
    """
    config_options: dict[str, Any] = {
        'logging': {
            'type': 'list',
            'elements': 'dict',
            'options': INCUS_SERVER_LOGGING_OPTIONS,
        },
    }
    for option_key, option_value in INCUS_SERVER_CONFIG_OPTIONS.items():
        config_options[option_key] = option_value
    return config_options
