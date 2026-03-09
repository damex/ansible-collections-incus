# damex.incus

[![](https://github.com/damex/ansible-collections-incus/workflows/linting/badge.svg)](https://github.com/damex/ansible-collections-incus/actions)
[![](https://github.com/damex/ansible-collections-incus/workflows/documentation/badge.svg)](https://incus.ansible.damex.org)

Ansible collection for [Incus](https://linuxcontainers.org/incus/).

## Modules

| Module | Description |
|--------|-------------|
| `incus_certificate` | Ensure Incus certificate |
| `incus_certificate_info` | Ensure Incus certificate information is gathered |
| `incus_cluster_info` | Ensure Incus cluster information is gathered |
| `incus_image` | Ensure Incus image |
| `incus_image_info` | Ensure Incus image information is gathered |
| `incus_instance` | Ensure Incus instance |
| `incus_instance_info` | Ensure Incus instance information is gathered |
| `incus_network` | Ensure Incus network |
| `incus_network_info` | Ensure Incus network information is gathered |
| `incus_profile` | Ensure Incus profile |
| `incus_profile_info` | Ensure Incus profile information is gathered |
| `incus_project` | Ensure Incus project |
| `incus_project_info` | Ensure Incus project information is gathered |
| `incus_server_info` | Ensure Incus server information is gathered |
| `incus_storage` | Ensure Incus storage |
| `incus_storage_info` | Ensure Incus storage information is gathered |

## Roles

| Role | Description |
|------|-------------|
| `incus` | Ensure Incus |
| `incus_certificates` | Ensure Incus certificates |
| `incus_client` | Ensure Incus client |
| `incus_cluster` | Ensure Incus cluster |
| `incus_images` | Ensure Incus images |
| `incus_instances` | Ensure Incus instances |
| `incus_networks` | Ensure Incus networks |
| `incus_profiles` | Ensure Incus profiles |
| `incus_projects` | Ensure Incus projects |
| `incus_repository` | Ensure Incus repository |
| `incus_server` | Ensure Incus server |
| `incus_storages` | Ensure Incus storages |

## Requirements

- Ansible core >= 2.19.0
- Debian or Fedora or Red Hat Enterprise Linux derivatives

## Installation

```
ansible-galaxy collection install damex.incus
```

Or via `requirements.yml`:

```yaml
collections:
  - name: damex.incus
    version: 1.7.4
```

```
ansible-galaxy collection install -r requirements.yml
```

## Documentation

Automatically generated documentation is available at [incus.ansible.damex.org](https://incus.ansible.damex.org).

## Issues

Bug reports and feature requests are welcome at [GitHub Issues](https://github.com/damex/ansible-collections-incus/issues).
