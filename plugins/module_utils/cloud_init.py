# -*- coding: utf-8 -*-
# Copyright: Roman Kuzmitskii <ansible@damex.org>
# SPDX-License-Identifier: GPL-3.0-or-later

"""Cloud-init option definitions and transforms."""

from __future__ import annotations

from typing import Any, NamedTuple

from ansible_collections.damex.incus.plugins.module_utils.common import incus_common_named_list_to_dict

__all__ = [
    'CLOUD_INIT_ALL_KEYS',
    'CLOUD_INIT_CONFIG_OPTIONS',
    'CLOUD_INIT_DATA_OPTIONS',
    'CLOUD_INIT_USER_KEYS',
    'CloudInitInterfaceTypeOptions',
    'cloud_init_data_lists_to_dicts',
    'cloud_init_interface_options',
    'cloud_init_named_list_to_scalar_dict',
]

CLOUD_INIT_USER_KEYS = frozenset({'cloud-init.user-data', 'cloud-init.vendor-data'})

CLOUD_INIT_ALL_KEYS = frozenset({
    'cloud-init.network-config',
    'cloud-init.user-data',
    'cloud-init.vendor-data',
})

CLOUD_INIT_NAMED_DICT_KEYS = frozenset({
    'bonds',
    'bridges',
    'disk_setup',
    'ethernets',
    'sources',
    'vlans',
})

CLOUD_INIT_NAMED_SCALAR_DICT_KEYS = frozenset({
    'debconf_selections',
    'headers',
})


class CloudInitInterfaceTypeOptions(NamedTuple):
    """Type-specific options for a cloud-init network interface."""

    match: dict[str, Any] | None = None
    interfaces: dict[str, Any] | None = None
    parameters: dict[str, Any] | None = None
    id: dict[str, Any] | None = None
    link: dict[str, Any] | None = None


def cloud_init_interface_options(
    type_options: CloudInitInterfaceTypeOptions | None = None,
) -> dict[str, Any]:
    """
    Build cloud-init network interface options.

    >>> cloud_init_interface_options()['dhcp4']
    {'type': 'bool'}
    """
    opts: dict[str, Any] = {
        'name': {'type': 'str', 'required': True},
        'dhcp4': {'type': 'bool'},
        'dhcp6': {'type': 'bool'},
        'addresses': {'type': 'list', 'elements': 'str'},
        'gateway4': {'type': 'str'},
        'gateway6': {'type': 'str'},
        'mtu': {'type': 'int'},
        'optional': {'type': 'bool'},
        'set-name': {'type': 'str'},
        'accept-ra': {'type': 'bool'},
        'routes': {
            'type': 'list',
            'elements': 'dict',
            'options': {
                'to': {'type': 'str'},
                'via': {'type': 'str'},
                'metric': {'type': 'int'},
                'table': {'type': 'int'},
                'scope': {'type': 'str'},
            },
        },
        'nameservers': {'type': 'dict', 'options': {
            'addresses': {'type': 'list', 'elements': 'str'},
            'search': {'type': 'list', 'elements': 'str'},
        }},
    }
    if type_options:
        opts.update({key: value for key, value in type_options._asdict().items() if value is not None})
    return opts


CLOUD_INIT_DATA_OPTIONS: dict[str, Any] = {
    'bootcmd': {'type': 'list', 'elements': 'raw'},
    'users': {
        'type': 'list',
        'elements': 'dict',
        'options': {
            'name': {'type': 'str', 'required': True},
            'groups': {'type': 'raw'},
            'shell': {'type': 'str'},
            'sudo': {'type': 'raw'},
            'ssh_authorized_keys': {'type': 'list', 'elements': 'str', 'no_log': False},
            'ssh_import_id': {'type': 'list', 'elements': 'str', 'no_log': False},
            'ssh_redirect_user': {'type': 'bool'},
            'lock_passwd': {'type': 'bool'},
            'passwd': {'type': 'str', 'no_log': True},
            'plain_text_passwd': {'type': 'str', 'no_log': True},
            'hashed_passwd': {'type': 'str', 'no_log': True},
            'gecos': {'type': 'str'},
            'homedir': {'type': 'str'},
            'primary_group': {'type': 'str'},
            'no_create_home': {'type': 'bool'},
            'no_user_group': {'type': 'bool'},
            'no_log_init': {'type': 'bool'},
            'create_groups': {'type': 'bool'},
            'expiredate': {'type': 'str'},
            'inactive': {'type': 'str'},
            'system': {'type': 'bool'},
            'uid': {'type': 'int'},
            'snapuser': {'type': 'str'},
            'doas': {'type': 'list', 'elements': 'str'},
            'selinux_user': {'type': 'str'},
        },
    },
    'groups': {'type': 'list', 'elements': 'raw'},
    'user': {'type': 'str'},
    'password': {'type': 'str', 'no_log': True},
    'ssh_pwauth': {'type': 'bool'},
    'ssh_authorized_keys': {'type': 'list', 'elements': 'str', 'no_log': False},
    'ssh_deletekeys': {'type': 'bool'},
    'ssh_genkeytypes': {'type': 'list', 'elements': 'str', 'no_log': False},
    'ssh_keys': {
        'type': 'dict',
        'no_log': False,
        'options': {
            'ed25519_private': {'type': 'str', 'no_log': True},
            'ed25519_public': {'type': 'str'},
            'ed25519_certificate': {'type': 'str'},
            'rsa_private': {'type': 'str', 'no_log': True},
            'rsa_public': {'type': 'str'},
            'rsa_certificate': {'type': 'str'},
            'ecdsa_private': {'type': 'str', 'no_log': True},
            'ecdsa_public': {'type': 'str'},
            'ecdsa_certificate': {'type': 'str'},
        },
    },
    'ssh_publish_hostkeys': {
        'type': 'dict',
        'no_log': False,
        'options': {
            'enabled': {'type': 'bool'},
            'blacklist': {'type': 'list', 'elements': 'str'},
        },
    },
    'ssh_quiet_keygen': {'type': 'bool'},
    'allow_public_ssh_keys': {'type': 'bool'},
    'disable_root': {'type': 'bool'},
    'disable_root_opts': {'type': 'str'},
    'chpasswd': {
        'type': 'dict',
        'no_log': False,
        'options': {
            'expire': {'type': 'bool'},
            'users': {
                'type': 'list',
                'elements': 'dict',
                'options': {
                    'name': {'type': 'str', 'required': True},
                    'password': {'type': 'str', 'no_log': True},
                    'type': {
                        'type': 'str',
                        'choices': [
                            'text',
                            'hash',
                            'RANDOM',
                        ],
                    },
                },
            },
        },
    },
    'timezone': {'type': 'str'},
    'locale': {'type': 'str'},
    'locale_configfile': {'type': 'str'},
    'hostname': {'type': 'str'},
    'fqdn': {'type': 'str'},
    'prefer_fqdn_over_hostname': {'type': 'bool'},
    'manage_etc_hosts': {'type': 'bool'},
    'package_update': {'type': 'bool'},
    'package_upgrade': {'type': 'bool'},
    'package_reboot_if_required': {'type': 'bool'},
    'packages': {'type': 'list', 'elements': 'str'},
    'apt': {
        'type': 'dict',
        'options': {
            'sources_list': {'type': 'str'},
            'preserve_sources_list': {'type': 'bool'},
            'disable_suites': {'type': 'list', 'elements': 'str'},
            'primary': {'type': 'list', 'elements': 'raw'},
            'security': {'type': 'list', 'elements': 'raw'},
            'sources': {
                'type': 'list',
                'elements': 'dict',
                'options': {
                    'name': {'type': 'str', 'required': True},
                    'source': {'type': 'str'},
                    'keyid': {'type': 'str', 'no_log': False},
                    'key': {'type': 'str', 'no_log': False},
                    'keyserver': {'type': 'str'},
                    'filename': {'type': 'str'},
                    'append': {'type': 'bool'},
                },
            },
            'conf': {'type': 'str'},
            'proxy': {'type': 'str'},
            'http_proxy': {'type': 'str'},
            'ftp_proxy': {'type': 'str'},
            'https_proxy': {'type': 'str'},
            'add_apt_repo_match': {'type': 'str'},
            'debconf_selections': {
                'type': 'list',
                'elements': 'dict',
                'options': {
                    'name': {'type': 'str', 'required': True},
                    'selection': {'type': 'str', 'required': True},
                },
            },
        },
    },
    'snap': {'type': 'dict', 'options': {
        'commands': {'type': 'list', 'elements': 'raw'},
    }},
    'growpart': {
        'type': 'dict',
        'options': {
            'mode': {
                'type': 'str',
                'choices': [
                    'auto',
                    'growpart',
                    'gpart',
                    'off',
                ],
            },
            'devices': {'type': 'list', 'elements': 'str'},
            'ignore_growroot_disabled': {'type': 'bool'},
        },
    },
    'disk_setup': {
        'type': 'list',
        'elements': 'dict',
        'options': {
            'name': {'type': 'str', 'required': True},
            'table_type': {
                'type': 'str',
                'choices': [
                    'mbr',
                    'gpt',
                ],
            },
            'layout': {'type': 'raw'},
            'overwrite': {'type': 'bool'},
        },
    },
    'fs_setup': {
        'type': 'list',
        'elements': 'dict',
        'options': {
            'label': {'type': 'str'},
            'filesystem': {'type': 'str'},
            'device': {'type': 'str'},
            'partition': {'type': 'raw'},
            'overwrite': {'type': 'bool'},
            'replace_fs': {'type': 'bool'},
            'extra_opts': {'type': 'list', 'elements': 'str'},
            'cmd': {'type': 'raw'},
        },
    },
    'mounts': {'type': 'list', 'elements': 'raw'},
    'mount_default_fields': {'type': 'list', 'elements': 'raw'},
    'swap': {
        'type': 'dict',
        'options': {
            'filename': {'type': 'str'},
            'size': {'type': 'raw'},
            'maxsize': {'type': 'raw'},
        },
    },
    'ntp': {
        'type': 'dict',
        'options': {
            'enabled': {'type': 'bool'},
            'servers': {'type': 'list', 'elements': 'str'},
            'pools': {'type': 'list', 'elements': 'str'},
            'peers': {'type': 'list', 'elements': 'str'},
            'allow': {'type': 'list', 'elements': 'str'},
            'ntp_client': {'type': 'str'},
            'config': {
                'type': 'dict',
                'options': {
                    'confpath': {'type': 'str'},
                    'check_exe': {'type': 'str'},
                    'packages': {'type': 'list', 'elements': 'str'},
                    'service_name': {'type': 'str'},
                    'template': {'type': 'str'},
                },
            },
        },
    },
    'ca_certs': {
        'type': 'dict',
        'options': {
            'trusted': {'type': 'list', 'elements': 'str'},
            'remove_defaults': {'type': 'bool'},
        },
    },
    'resolv_conf': {
        'type': 'dict',
        'options': {
            'nameservers': {'type': 'list', 'elements': 'str'},
            'searchdomains': {'type': 'list', 'elements': 'str'},
            'domain': {'type': 'str'},
            'sortlist': {'type': 'list', 'elements': 'str'},
            'options': {
                'type': 'dict',
                'options': {
                    'ndots': {'type': 'int'},
                    'timeout': {'type': 'int'},
                    'attempts': {'type': 'int'},
                    'rotate': {'type': 'bool'},
                    'no-check-names': {'type': 'bool'},
                    'inet6': {'type': 'bool'},
                    'edns0': {'type': 'bool'},
                    'single-request': {'type': 'bool'},
                    'single-request-reopen': {'type': 'bool'},
                    'no-tld-query': {'type': 'bool'},
                    'use-vc': {'type': 'bool'},
                    'trust-ad': {'type': 'bool'},
                    'no-reload': {'type': 'bool'},
                },
            },
        },
    },
    'manage_resolv_conf': {'type': 'bool'},
    'power_state': {
        'type': 'dict',
        'options': {
            'mode': {
                'type': 'str',
                'choices': [
                    'reboot',
                    'poweroff',
                    'halt',
                ],
            },
            'delay': {'type': 'str'},
            'timeout': {'type': 'int'},
            'condition': {'type': 'raw'},
        },
    },
    'write_files': {
        'type': 'list',
        'elements': 'dict',
        'options': {
            'path': {'type': 'str', 'required': True},
            'content': {'type': 'str'},
            'source': {
                'type': 'dict',
                'options': {
                    'uri': {'type': 'str', 'required': True},
                    'headers': {
                        'type': 'list',
                        'elements': 'dict',
                        'options': {
                            'name': {'type': 'str', 'required': True},
                            'value': {'type': 'str', 'required': True},
                        },
                    },
                },
            },
            'owner': {'type': 'str'},
            'permissions': {'type': 'str'},
            'encoding': {
                'type': 'str',
                'choices': [
                    'b64',
                    'base64',
                    'gz',
                    'gzip',
                    'gz+b64',
                    'gzip+b64',
                    'gz+base64',
                    'gzip+base64',
                    'text/plain',
                ],
            },
            'append': {'type': 'bool'},
            'defer': {'type': 'bool'},
        },
    },
    'runcmd': {'type': 'list', 'elements': 'raw'},
    'final_message': {'type': 'str'},
    'phone_home': {
        'type': 'dict',
        'options': {
            'url': {'type': 'str', 'required': True},
            'post': {'type': 'list', 'elements': 'str'},
            'tries': {'type': 'int'},
        },
    },
}


CLOUD_INIT_CONFIG_OPTIONS: dict[str, Any] = {
    'cloud-init.network-config': {
        'type': 'dict',
        'options': {
            'version': {'type': 'int'},
            'renderer': {'type': 'str'},
            'ethernets': {
                'type': 'list',
                'elements': 'dict',
                'options': cloud_init_interface_options(
                    CloudInitInterfaceTypeOptions(
                        match={'type': 'dict', 'options': {
                            'name': {'type': 'str'},
                            'macaddress': {'type': 'str'},
                            'driver': {'type': 'str'},
                        }},
                    ),
                ),
            },
            'bonds': {
                'type': 'list',
                'elements': 'dict',
                'options': cloud_init_interface_options(
                    CloudInitInterfaceTypeOptions(
                        interfaces={'type': 'list', 'elements': 'str'},
                        parameters={
                            'type': 'dict',
                            'options': {
                                'mode': {'type': 'str'},
                                'mii-monitor-interval': {'type': 'int'},
                            },
                        },
                    ),
                ),
            },
            'bridges': {
                'type': 'list',
                'elements': 'dict',
                'options': cloud_init_interface_options(
                    CloudInitInterfaceTypeOptions(
                        interfaces={'type': 'list', 'elements': 'str'},
                        parameters={
                            'type': 'dict',
                            'options': {
                                'stp': {'type': 'bool'},
                                'forward-delay': {'type': 'int'},
                            },
                        },
                    ),
                ),
            },
            'vlans': {
                'type': 'list',
                'elements': 'dict',
                'options': cloud_init_interface_options(
                    CloudInitInterfaceTypeOptions(
                        id={'type': 'int', 'required': True},
                        link={'type': 'str', 'required': True},
                    ),
                ),
            },
        },
    },
    'cloud-init.user-data': {'type': 'dict', 'options': CLOUD_INIT_DATA_OPTIONS},
    'cloud-init.vendor-data': {'type': 'dict', 'options': CLOUD_INIT_DATA_OPTIONS},
}


def cloud_init_named_list_to_scalar_dict(items: list[dict[str, Any]]) -> dict[str, Any]:
    """Transform list of name/value pairs to dict."""
    return {item['name']: item.get('value', item.get('selection', '')) for item in items}


def cloud_init_data_lists_to_dicts(data: Any) -> Any:
    """Transform cloud-init named lists to dict format."""
    match data:
        case dict():
            result: dict[str, Any] = {}
            for key, value in data.items():
                if key in CLOUD_INIT_NAMED_DICT_KEYS and isinstance(value, list):
                    result[key] = incus_common_named_list_to_dict(value)
                elif key in CLOUD_INIT_NAMED_SCALAR_DICT_KEYS and isinstance(value, list):
                    result[key] = cloud_init_named_list_to_scalar_dict(value)
                else:
                    result[key] = cloud_init_data_lists_to_dicts(value)
            return result
        case list():
            return [cloud_init_data_lists_to_dicts(item) for item in data]
        case _:
            return data
