# -*- coding: utf-8 -*-
# Copyright: Roman Kuzmitskii <ansible@damex.org>
# SPDX-License-Identifier: GPL-3.0-or-later
# pylint: disable=too-many-lines

"""Instance configuration documentation fragment."""

from __future__ import annotations

__all__ = ['ModuleDocFragment']


class ModuleDocFragment:  # pylint: disable=too-few-public-methods
    """Instance configuration options."""

    DOCUMENTATION = r"""
options:
  config:
    description:
      - Configuration key-value pairs.
      - Boolean values are converted to lowercase strings.
      - Dict values for C(cloud-init.*) keys are serialized to YAML.
    type: dict
    default: {}
    suboptions:
      limits.cpu:
        description:
          - Number or range of CPUs to expose.
        type: str
      limits.memory:
        description:
          - Percentage of host memory or fixed value in bytes.
        type: str
      limits.processes:
        description:
          - Maximum number of processes in the instance.
        type: int
      limits.cpu.priority:
        description:
          - CPU scheduling priority compared to other instances.
        type: int
      limits.cpu.allowance:
        description:
          - CPU time allowance as a percentage or fixed duration.
        type: str
      limits.cpu.nodes:
        description:
          - NUMA nodes to restrict the instance to.
        type: str
      limits.disk.priority:
        description:
          - I/O request priority when under load (0-10).
        type: int
      limits.network.priority:
        description:
          - Network I/O priority compared to other instances.
        type: int
      limits.hugepages.1GB:
        description:
          - Limit for 1GB huge pages.
        type: str
      limits.hugepages.1MB:
        description:
          - Limit for 1MB huge pages.
        type: str
      limits.hugepages.2MB:
        description:
          - Limit for 2MB huge pages.
        type: str
      limits.hugepages.64KB:
        description:
          - Limit for 64KB huge pages.
        type: str
      limits.memory.enforce:
        description:
          - Memory limit enforcement mode.
        type: str
      limits.memory.hotplug:
        description:
          - Memory hotplug.
        type: str
      limits.memory.hugepages:
        description:
          - Huge page memory backing.
        type: bool
      limits.memory.oom_priority:
        description:
          - OOM killer priority for the instance.
        type: int
      limits.memory.swap:
        description:
          - Swap encouragement or discouragement.
        type: str
      limits.memory.swap.priority:
        description:
          - Swap priority compared to other instances.
        type: int
      boot.autostart:
        description:
          - Instance autostart on daemon startup.
        type: bool
      boot.autostart.delay:
        description:
          - Seconds to wait after the instance started.
        type: int
      boot.autostart.priority:
        description:
          - Instance startup priority (higher starts first).
        type: int
      boot.autorestart:
        description:
          - Auto-restart after crash.
        type: bool
      boot.host_shutdown_action:
        description:
          - Action to take on host shutdown.
        type: str
      boot.host_shutdown_timeout:
        description:
          - Seconds to wait for instance to stop on host shutdown.
        type: int
      boot.stop.priority:
        description:
          - Instance shutdown priority (higher stops first).
        type: int
      security.privileged:
        description:
          - Privileged mode.
        type: bool
      security.nesting:
        description:
          - Incus nesting support.
        type: bool
      security.agent.metrics:
        description:
          - Incus-agent metrics exposure.
        type: bool
      security.bpffs.delegate_attachs:
        description:
          - Delegated BPF attach types.
        type: str
      security.bpffs.delegate_cmds:
        description:
          - Delegated BPF commands.
        type: str
      security.bpffs.delegate_maps:
        description:
          - Delegated BPF map types.
        type: str
      security.bpffs.delegate_progs:
        description:
          - Delegated BPF program types.
        type: str
      security.bpffs.path:
        description:
          - BPFFS mount path in the instance.
        type: str
      security.csm:
        description:
          - Compatibility Support Module.
        type: bool
      security.guestapi:
        description:
          - Guest API.
        type: bool
      security.guestapi.images:
        description:
          - Guest API image access.
        type: bool
      security.idmap.base:
        description:
          - Base host UID/GID for the ID map.
        type: int
      security.idmap.isolated:
        description:
          - Unique ID map isolation.
        type: bool
      security.idmap.size:
        description:
          - Size of the ID map range.
        type: int
      security.iommu:
        description:
          - IOMMU.
        type: bool
      security.protection.delete:
        description:
          - Deletion protection.
        type: bool
      security.protection.shift:
        description:
          - UID/GID shift protection.
        type: bool
      security.secureboot:
        description:
          - UEFI Secure Boot.
        type: bool
      security.sev:
        description:
          - AMD SEV encryption.
        type: bool
      security.sev.policy.es:
        description:
          - SEV-ES.
        type: bool
      security.sev.session.data:
        description:
          - SEV session data blob.
        type: str
      security.sev.session.dh:
        description:
          - SEV Diffie-Hellman key.
        type: str
      security.syscalls.allow:
        description:
          - Allowed syscalls whitelist.
        type: str
      security.syscalls.deny:
        description:
          - Denied syscalls blacklist.
        type: str
      security.syscalls.deny_compat:
        description:
          - Compat syscall blocking on amd64.
        type: bool
      security.syscalls.deny_default:
        description:
          - Default syscall deny list.
        type: bool
      security.syscalls.intercept.bpf:
        description:
          - BPF syscall interception.
        type: bool
      security.syscalls.intercept.bpf.devices:
        description:
          - Device-type BPF program allowance.
        type: bool
      security.syscalls.intercept.mknod:
        description:
          - Mknod syscall interception.
        type: bool
      security.syscalls.intercept.mount:
        description:
          - Mount syscall interception.
        type: bool
      security.syscalls.intercept.mount.allowed:
        description:
          - Filesystems allowed for intercepted mounts.
        type: str
      security.syscalls.intercept.mount.fuse:
        description:
          - FUSE mounts to redirect intercepted mounts to.
        type: str
      security.syscalls.intercept.mount.shift:
        description:
          - ID-mapped mount shifting for intercepted mounts.
        type: bool
      security.syscalls.intercept.sched_setscheduler:
        description:
          - Sched_setscheduler syscall interception.
        type: bool
      security.syscalls.intercept.setxattr:
        description:
          - Setxattr syscall interception.
        type: bool
      security.syscalls.intercept.sysinfo:
        description:
          - Sysinfo syscall interception.
        type: bool
      migration.stateful:
        description:
          - Allow stateful stop/start and snapshots.
        type: bool
      migration.incremental.memory:
        description:
          - Incremental memory transfer.
        type: bool
      migration.incremental.memory.goal:
        description:
          - Target percentage of dirty memory for completion.
        type: int
      migration.incremental.memory.iterations:
        description:
          - Maximum number of memory transfer iterations.
        type: int
      snapshots.expiry:
        description:
          - Automatic expiry time for snapshots.
        type: str
      snapshots.expiry.manual:
        description:
          - Expiry time for manually created snapshots.
        type: str
      snapshots.pattern:
        description:
          - Pongo2 template for snapshot names.
        type: str
      snapshots.schedule:
        description:
          - Cron expression for automatic snapshots.
        type: str
      snapshots.schedule.stopped:
        description:
          - Stopped instance snapshots.
        type: bool
      nvidia.driver.capabilities:
        description:
          - NVIDIA driver capabilities to expose.
        type: str
      nvidia.require.cuda:
        description:
          - Required CUDA version.
        type: str
      nvidia.require.driver:
        description:
          - Required NVIDIA driver version.
        type: str
      nvidia.runtime:
        description:
          - Pass NVIDIA runtime libraries into the container.
        type: bool
      raw.apparmor:
        description:
          - Raw AppArmor profile entries.
        type: str
      raw.idmap:
        description:
          - Raw ID map configuration.
        type: str
      raw.lxc:
        description:
          - Raw LXC configuration to append.
        type: str
      raw.qemu:
        description:
          - Raw QEMU command-line arguments.
        type: str
      raw.qemu.conf:
        description:
          - Raw QEMU configuration overrides.
        type: str
      raw.qemu.qmp.early:
        description:
          - Raw QMP commands before instance start.
        type: str
      raw.qemu.qmp.pre-start:
        description:
          - Raw QMP commands just before instance start.
        type: str
      raw.qemu.qmp.post-start:
        description:
          - Raw QMP commands after instance start.
        type: str
      raw.qemu.scriptlet:
        description:
          - Raw QEMU scriptlet.
        type: str
      raw.seccomp:
        description:
          - Raw Seccomp configuration.
        type: str
      agent.nic_config:
        description:
          - Use instance NIC names and MTU for default interfaces.
        type: bool
      cluster.evacuate:
        description:
          - Evacuation behavior during cluster evacuation.
        type: str
        choices: [auto, live-migrate, migrate, stop, stateful-stop, force-stop]
      linux.kernel_modules:
        description:
          - Comma-separated kernel modules to load.
        type: str
      oci.cwd:
        description:
          - Working directory for the OCI container.
        type: str
      oci.entrypoint:
        description:
          - Entrypoint for the OCI container.
        type: str
      oci.gid:
        description:
          - GID to run the OCI container as.
        type: str
      oci.uid:
        description:
          - UID to run the OCI container as.
        type: str
      environment_variables:
        description:
          - Environment variables to set in the instance.
          - Each entry is flattened to an C(environment.NAME) config key.
        type: list
        elements: dict
        suboptions:
          name:
            description:
              - Environment variable name.
            type: str
            required: true
          value:
            description:
              - Environment variable value.
            type: str
            required: true
      cloud-init.network-config:
        description:
          - Cloud-init network configuration.
        type: dict
        suboptions:
          version:
            description:
              - Network config format version.
            type: int
          renderer:
            description:
              - Network renderer to use.
            type: str
          ethernets:
            description:
              - Ethernet interface configurations.
            type: list
            elements: dict
            suboptions:
              name:
                description:
                  - Interface name.
                type: str
                required: true
              dhcp4:
                description:
                  - DHCPv4.
                type: bool
              dhcp6:
                description:
                  - DHCPv6.
                type: bool
              addresses:
                description:
                  - Static addresses in CIDR notation.
                type: list
                elements: str
              gateway4:
                description:
                  - Default IPv4 gateway address.
                type: str
              gateway6:
                description:
                  - Default IPv6 gateway address.
                type: str
              mtu:
                description:
                  - Maximum transmission unit for the interface.
                type: int
              optional:
                description:
                  - Optional boot interface.
                type: bool
              set-name:
                description:
                  - Rename the interface to this name.
                type: str
              accept-ra:
                description:
                  - IPv6 Router Advertisement acceptance.
                type: bool
              match:
                description:
                  - Match rules for the interface.
                type: dict
                suboptions:
                  name:
                    description:
                      - Interface name to match.
                    type: str
                  macaddress:
                    description:
                      - MAC address to match.
                    type: str
                  driver:
                    description:
                      - Kernel driver name to match.
                    type: str
              routes:
                description:
                  - Static routes for the interface.
                type: list
                elements: dict
                suboptions:
                  to:
                    description:
                      - Route destination in CIDR notation.
                    type: str
                  via:
                    description:
                      - Gateway address for the route.
                    type: str
                  metric:
                    description:
                      - Route metric.
                    type: int
                  table:
                    description:
                      - Routing table ID.
                    type: int
                  scope:
                    description:
                      - Route scope.
                    type: str
              nameservers:
                description:
                  - DNS server configuration.
                type: dict
                suboptions:
                  addresses:
                    description:
                      - DNS server addresses.
                    type: list
                    elements: str
                  search:
                    description:
                      - DNS search domains.
                    type: list
                    elements: str
          bonds:
            description:
              - Bond interface configurations.
            type: list
            elements: dict
            suboptions:
              name:
                description:
                  - Bond name.
                type: str
                required: true
              dhcp4:
                description:
                  - DHCPv4.
                type: bool
              dhcp6:
                description:
                  - DHCPv6.
                type: bool
              addresses:
                description:
                  - Static addresses in CIDR notation.
                type: list
                elements: str
              gateway4:
                description:
                  - Default IPv4 gateway address.
                type: str
              gateway6:
                description:
                  - Default IPv6 gateway address.
                type: str
              mtu:
                description:
                  - Maximum transmission unit for the interface.
                type: int
              optional:
                description:
                  - Optional boot interface.
                type: bool
              set-name:
                description:
                  - Rename the interface to this name.
                type: str
              accept-ra:
                description:
                  - IPv6 Router Advertisement acceptance.
                type: bool
              interfaces:
                description:
                  - Member interfaces for the bond.
                type: list
                elements: str
              parameters:
                description:
                  - Bond parameters.
                type: dict
                suboptions:
                  mode:
                    description:
                      - Bonding mode.
                    type: str
                  mii-monitor-interval:
                    description:
                      - MII monitoring interval in milliseconds.
                    type: int
              routes:
                description:
                  - Static routes for the bond.
                type: list
                elements: dict
                suboptions:
                  to:
                    description:
                      - Route destination in CIDR notation.
                    type: str
                  via:
                    description:
                      - Gateway address for the route.
                    type: str
                  metric:
                    description:
                      - Route metric.
                    type: int
                  table:
                    description:
                      - Routing table ID.
                    type: int
                  scope:
                    description:
                      - Route scope.
                    type: str
              nameservers:
                description:
                  - DNS server configuration.
                type: dict
                suboptions:
                  addresses:
                    description:
                      - DNS server addresses.
                    type: list
                    elements: str
                  search:
                    description:
                      - DNS search domains.
                    type: list
                    elements: str
          bridges:
            description:
              - Bridge interface configurations.
            type: list
            elements: dict
            suboptions:
              name:
                description:
                  - Bridge name.
                type: str
                required: true
              dhcp4:
                description:
                  - DHCPv4.
                type: bool
              dhcp6:
                description:
                  - DHCPv6.
                type: bool
              addresses:
                description:
                  - Static addresses in CIDR notation.
                type: list
                elements: str
              gateway4:
                description:
                  - Default IPv4 gateway address.
                type: str
              gateway6:
                description:
                  - Default IPv6 gateway address.
                type: str
              mtu:
                description:
                  - Maximum transmission unit for the interface.
                type: int
              optional:
                description:
                  - Optional boot interface.
                type: bool
              set-name:
                description:
                  - Rename the interface to this name.
                type: str
              accept-ra:
                description:
                  - IPv6 Router Advertisement acceptance.
                type: bool
              interfaces:
                description:
                  - Member interfaces for the bridge.
                type: list
                elements: str
              parameters:
                description:
                  - Bridge parameters.
                type: dict
                suboptions:
                  stp:
                    description:
                      - Spanning Tree Protocol.
                    type: bool
                  forward-delay:
                    description:
                      - Forwarding delay in seconds.
                    type: int
              routes:
                description:
                  - Static routes for the bridge.
                type: list
                elements: dict
                suboptions:
                  to:
                    description:
                      - Route destination in CIDR notation.
                    type: str
                  via:
                    description:
                      - Gateway address for the route.
                    type: str
                  metric:
                    description:
                      - Route metric.
                    type: int
                  table:
                    description:
                      - Routing table ID.
                    type: int
                  scope:
                    description:
                      - Route scope.
                    type: str
              nameservers:
                description:
                  - DNS server configuration.
                type: dict
                suboptions:
                  addresses:
                    description:
                      - DNS server addresses.
                    type: list
                    elements: str
                  search:
                    description:
                      - DNS search domains.
                    type: list
                    elements: str
          vlans:
            description:
              - VLAN interface configurations.
            type: list
            elements: dict
            suboptions:
              name:
                description:
                  - VLAN interface name.
                type: str
                required: true
              id:
                description:
                  - VLAN ID.
                type: int
                required: true
              link:
                description:
                  - Parent interface for the VLAN.
                type: str
                required: true
              dhcp4:
                description:
                  - DHCPv4.
                type: bool
              dhcp6:
                description:
                  - DHCPv6.
                type: bool
              addresses:
                description:
                  - Static addresses in CIDR notation.
                type: list
                elements: str
              gateway4:
                description:
                  - Default IPv4 gateway address.
                type: str
              gateway6:
                description:
                  - Default IPv6 gateway address.
                type: str
              mtu:
                description:
                  - Maximum transmission unit for the interface.
                type: int
              optional:
                description:
                  - Optional boot interface.
                type: bool
              set-name:
                description:
                  - Rename the interface to this name.
                type: str
              accept-ra:
                description:
                  - IPv6 Router Advertisement acceptance.
                type: bool
              routes:
                description:
                  - Static routes for the VLAN.
                type: list
                elements: dict
                suboptions:
                  to:
                    description:
                      - Route destination in CIDR notation.
                    type: str
                  via:
                    description:
                      - Gateway address for the route.
                    type: str
                  metric:
                    description:
                      - Route metric.
                    type: int
                  table:
                    description:
                      - Routing table ID.
                    type: int
                  scope:
                    description:
                      - Route scope.
                    type: str
              nameservers:
                description:
                  - DNS server configuration.
                type: dict
                suboptions:
                  addresses:
                    description:
                      - DNS server addresses.
                    type: list
                    elements: str
                  search:
                    description:
                      - DNS search domains.
                    type: list
                    elements: str
      cloud-init.user-data:
        description:
          - Cloud-init user data configuration.
        type: dict
        suboptions:
          bootcmd:
            description:
              - Commands to run early in the boot process.
            type: list
            elements: raw
          users:
            description:
              - Users to create.
            type: list
            elements: dict
            suboptions:
              name:
                description:
                  - User name.
                type: str
                required: true
              groups:
                description:
                  - Groups to add the user to.
                type: raw
              shell:
                description:
                  - Login shell for the user.
                type: str
              sudo:
                description:
                  - Sudo rule for the user.
                type: raw
              ssh_authorized_keys:
                description:
                  - SSH public keys to add to the user.
                type: list
                elements: str
              ssh_import_id:
                description:
                  - SSH IDs to import public keys from.
                type: list
                elements: str
              ssh_redirect_user:
                description:
                  - SSH login redirection to default user.
                type: bool
              lock_passwd:
                description:
                  - User password lock.
                type: bool
              passwd:
                description:
                  - Hashed password for the user.
                type: str
              plain_text_passwd:
                description:
                  - Plain text password for the user.
                type: str
              hashed_passwd:
                description:
                  - Pre-hashed password for the user.
                type: str
              gecos:
                description:
                  - GECOS field for the user.
                type: str
              homedir:
                description:
                  - Home directory path.
                type: str
              primary_group:
                description:
                  - Primary group for the user.
                type: str
              no_create_home:
                description:
                  - Home directory creation skip.
                type: bool
              no_user_group:
                description:
                  - User group creation skip.
                type: bool
              no_log_init:
                description:
                  - User initialization log skip.
                type: bool
              create_groups:
                description:
                  - User group creation.
                type: bool
              expiredate:
                description:
                  - Account expiration date in YYYY-MM-DD format.
                type: str
              inactive:
                description:
                  - Days after password expires until account is disabled.
                type: str
              system:
                description:
                  - System user.
                type: bool
              uid:
                description:
                  - Numeric user ID.
                type: int
              snapuser:
                description:
                  - Email for Snappy user creation.
                type: str
              doas:
                description:
                  - Doas rules for the user.
                type: list
                elements: str
              selinux_user:
                description:
                  - SELinux user for login mapping.
                type: str
          groups:
            description:
              - Groups to create.
            type: list
            elements: raw
          user:
            description:
              - Default user name.
            type: str
          password:
            description:
              - Password for the default user.
            type: str
          ssh_pwauth:
            description:
              - SSH password authentication.
            type: bool
          ssh_authorized_keys:
            description:
              - SSH public keys to add to the default user.
            type: list
            elements: str
          ssh_deletekeys:
            description:
              - Default SSH host key deletion.
            type: bool
          ssh_genkeytypes:
            description:
              - SSH key types to generate.
            type: list
            elements: str
          ssh_keys:
            description:
              - Pre-generated SSH host keys.
            type: dict
            suboptions:
              ed25519_private:
                description:
                  - Ed25519 private host key.
                type: str
              ed25519_public:
                description:
                  - Ed25519 public host key.
                type: str
              ed25519_certificate:
                description:
                  - Ed25519 host certificate.
                type: str
              rsa_private:
                description:
                  - RSA private host key.
                type: str
              rsa_public:
                description:
                  - RSA public host key.
                type: str
              rsa_certificate:
                description:
                  - RSA host certificate.
                type: str
              ecdsa_private:
                description:
                  - ECDSA private host key.
                type: str
              ecdsa_public:
                description:
                  - ECDSA public host key.
                type: str
              ecdsa_certificate:
                description:
                  - ECDSA host certificate.
                type: str
          ssh_publish_hostkeys:
            description:
              - SSH host key publishing configuration.
            type: dict
            suboptions:
              enabled:
                description:
                  - Host key publishing.
                type: bool
              blacklist:
                description:
                  - Key types to exclude from publishing.
                type: list
                elements: str
          ssh_quiet_keygen:
            description:
              - SSH key generation output suppression.
            type: bool
          allow_public_ssh_keys:
            description:
              - Public SSH key allowance.
            type: bool
          disable_root:
            description:
              - Root login.
            type: bool
          disable_root_opts:
            description:
              - SSH options applied when root login is disabled.
            type: str
          chpasswd:
            description:
              - Password change settings.
            type: dict
            suboptions:
              expire:
                description:
                  - Password expiry on first login.
                type: bool
              users:
                description:
                  - User password entries.
                type: list
                elements: dict
                suboptions:
                  name:
                    description:
                      - User name.
                    type: str
                    required: true
                  password:
                    description:
                      - Password for the user.
                    type: str
                  type:
                    description:
                      - Password type.
                    type: str
                    choices: [text, hash, RANDOM]
          timezone:
            description:
              - System timezone.
            type: str
          locale:
            description:
              - System locale.
            type: str
          locale_configfile:
            description:
              - Locale configuration file path.
            type: str
          hostname:
            description:
              - System hostname.
            type: str
          fqdn:
            description:
              - Fully qualified domain name.
            type: str
          prefer_fqdn_over_hostname:
            description:
              - FQDN preference over short hostname.
            type: bool
          manage_etc_hosts:
            description:
              - /etc/hosts management.
            type: bool
          package_update:
            description:
              - First-boot package list update.
            type: bool
          package_upgrade:
            description:
              - First-boot package upgrade.
            type: bool
          package_reboot_if_required:
            description:
              - Post-upgrade reboot.
            type: bool
          packages:
            description:
              - Packages to install on first boot.
            type: list
            elements: str
          apt:
            description:
              - APT package manager configuration.
            type: dict
            suboptions:
              sources_list:
                description:
                  - Custom sources.list content.
                type: str
              preserve_sources_list:
                description:
                  - Existing sources.list preservation.
                type: bool
              disable_suites:
                description:
                  - APT suites to disable.
                type: list
                elements: str
              primary:
                description:
                  - Primary mirror configuration.
                type: list
                elements: raw
              security:
                description:
                  - Security mirror configuration.
                type: list
                elements: raw
              sources:
                description:
                  - Additional APT source definitions.
                type: list
                elements: dict
                suboptions:
                  name:
                    description:
                      - Source entry identifier and filename.
                    type: str
                    required: true
                  source:
                    description:
                      - Sources.list entry.
                    type: str
                  keyid:
                    description:
                      - GPG key ID to import.
                    type: str
                  key:
                    description:
                      - Raw GPG key.
                    type: str
                  keyserver:
                    description:
                      - Alternate keyserver to pull key from.
                    type: str
                  filename:
                    description:
                      - Name of the source list file.
                    type: str
                  append:
                    description:
                      - Source file append mode.
                    type: bool
              conf:
                description:
                  - APT configuration to write.
                type: str
              proxy:
                description:
                  - APT proxy URL.
                type: str
              http_proxy:
                description:
                  - HTTP proxy URL for APT.
                type: str
              ftp_proxy:
                description:
                  - FTP proxy URL for APT.
                type: str
              https_proxy:
                description:
                  - HTTPS proxy URL for APT.
                type: str
              add_apt_repo_match:
                description:
                  - Regex for matching add-apt-repository entries.
                type: str
              debconf_selections:
                description:
                  - Debconf preseed selections.
                type: list
                elements: dict
                suboptions:
                  name:
                    description:
                      - Selection set identifier.
                    type: str
                    required: true
                  selection:
                    description:
                      - Debconf selection lines.
                    type: str
                    required: true
          snap:
            description:
              - Snap package manager configuration.
            type: dict
            suboptions:
              commands:
                description:
                  - Snap commands to execute.
                type: list
                elements: raw
          growpart:
            description:
              - Partition growing configuration.
            type: dict
            suboptions:
              mode:
                description:
                  - Growpart mode.
                type: str
                choices: [auto, growpart, gpart, "off"]
              devices:
                description:
                  - Devices to grow.
                type: list
                elements: str
              ignore_growroot_disabled:
                description:
                  - Growroot disabled marker bypass.
                type: bool
          disk_setup:
            description:
              - Disk partitioning configuration.
            type: list
            elements: dict
            suboptions:
              name:
                description:
                  - Device path.
                type: str
                required: true
              table_type:
                description:
                  - Partition table type.
                type: str
                choices: [mbr, gpt]
              layout:
                description:
                  - Partition layout specification.
                type: raw
              overwrite:
                description:
                  - Existing partition table overwrite.
                type: bool
          fs_setup:
            description:
              - Filesystem creation configuration.
            type: list
            elements: dict
            suboptions:
              label:
                description:
                  - Filesystem label.
                type: str
              filesystem:
                description:
                  - Filesystem type.
                type: str
              device:
                description:
                  - Device path.
                type: str
              partition:
                description:
                  - Partition specification.
                type: raw
              overwrite:
                description:
                  - Existing filesystem overwrite.
                type: bool
              replace_fs:
                description:
                  - Existing filesystem replacement.
                type: bool
              extra_opts:
                description:
                  - Extra options for mkfs.
                type: list
                elements: str
              cmd:
                description:
                  - Custom mkfs command.
                type: raw
          mounts:
            description:
              - Mount point definitions.
            type: list
            elements: raw
          mount_default_fields:
            description:
              - Default values for mount entries with fewer than six fields.
            type: list
            elements: raw
          swap:
            description:
              - Swap configuration.
            type: dict
            suboptions:
              filename:
                description:
                  - Swap file path.
                type: str
              size:
                description:
                  - Swap size in bytes or C(auto).
                type: raw
              maxsize:
                description:
                  - Maximum swap size in bytes.
                type: raw
          ntp:
            description:
              - NTP client configuration.
            type: dict
            suboptions:
              enabled:
                description:
                  - NTP.
                type: bool
              servers:
                description:
                  - NTP servers.
                type: list
                elements: str
              pools:
                description:
                  - NTP pools.
                type: list
                elements: str
              peers:
                description:
                  - NTP peer nodes.
                type: list
                elements: str
              allow:
                description:
                  - Allowed NTP network ranges.
                type: list
                elements: str
              ntp_client:
                description:
                  - NTP client to use.
                type: str
              config:
                description:
                  - NTP client-specific configuration.
                type: dict
                suboptions:
                  confpath:
                    description:
                      - NTP client configuration file path.
                    type: str
                  check_exe:
                    description:
                      - Executable name for the NTP client.
                    type: str
                  packages:
                    description:
                      - Packages needed for the NTP client.
                    type: list
                    elements: str
                  service_name:
                    description:
                      - Service name for the NTP client.
                    type: str
                  template:
                    description:
                      - Jinja template for NTP client configuration.
                    type: str
          ca_certs:
            description:
              - CA certificate configuration.
            type: dict
            suboptions:
              trusted:
                description:
                  - Trusted CA certificates in PEM format.
                type: list
                elements: str
              remove_defaults:
                description:
                  - Default CA certificate removal.
                type: bool
          resolv_conf:
            description:
              - DNS resolver configuration.
            type: dict
            suboptions:
              nameservers:
                description:
                  - DNS server addresses.
                type: list
                elements: str
              searchdomains:
                description:
                  - DNS search domains.
                type: list
                elements: str
              domain:
                description:
                  - Default DNS domain.
                type: str
              sortlist:
                description:
                  - DNS sort list.
                type: list
                elements: str
              options:
                description:
                  - Resolver options for /etc/resolv.conf.
                type: dict
                suboptions:
                  ndots:
                    description:
                      - Minimum dots in a name before absolute query.
                    type: int
                  timeout:
                    description:
                      - Resolver query timeout in seconds.
                    type: int
                  attempts:
                    description:
                      - Number of resolver query attempts.
                    type: int
                  rotate:
                    description:
                      - Nameserver rotation.
                    type: bool
                  no-check-names:
                    description:
                      - Name checking disabling.
                    type: bool
                  inet6:
                    description:
                      - IPv6 address preference.
                    type: bool
                  edns0:
                    description:
                      - EDNS0 extensions.
                    type: bool
                  single-request:
                    description:
                      - Sequential A and AAAA queries.
                    type: bool
                  single-request-reopen:
                    description:
                      - Socket reopen for sequential queries.
                    type: bool
                  no-tld-query:
                    description:
                      - Top-level domain query disabling.
                    type: bool
                  use-vc:
                    description:
                      - TCP DNS queries.
                    type: bool
                  trust-ad:
                    description:
                      - Resolver AD flag trust.
                    type: bool
                  no-reload:
                    description:
                      - Automatic config reload disabling.
                    type: bool
          manage_resolv_conf:
            description:
              - /etc/resolv.conf management.
            type: bool
          power_state:
            description:
              - Power state change after cloud-init completes.
            type: dict
            suboptions:
              mode:
                description:
                  - Power state action to take.
                type: str
                choices: [reboot, poweroff, halt]
              delay:
                description:
                  - Delay before power action.
                type: str
              timeout:
                description:
                  - Timeout in seconds for power action.
                type: int
              condition:
                description:
                  - Condition to check before power action.
                type: raw
          write_files:
            description:
              - Files to create on first boot.
            type: list
            elements: dict
            suboptions:
              path:
                description:
                  - Absolute path of the file to create.
                type: str
                required: true
              content:
                description:
                  - Content to write to the file.
                type: str
              source:
                description:
                  - URL source for file content.
                type: dict
                suboptions:
                  uri:
                    description:
                      - URL to fetch content from.
                    type: str
                    required: true
                  headers:
                    description:
                      - HTTP headers for the request.
                    type: list
                    elements: dict
                    suboptions:
                      name:
                        description:
                          - Header name.
                        type: str
                        required: true
                      value:
                        description:
                          - Header value.
                        type: str
                        required: true
              owner:
                description:
                  - Owner and group of the file.
                type: str
              permissions:
                description:
                  - File permissions in octal notation.
                type: str
              encoding:
                description:
                  - Content encoding.
                type: str
                choices: [b64, base64, gz, gzip, gz+b64, gzip+b64, gz+base64, gzip+base64, text/plain]
              append:
                description:
                  - File append mode.
                type: bool
              defer:
                description:
                  - Deferred writing until final stage.
                type: bool
          runcmd:
            description:
              - Commands to run after cloud-init completes.
            type: list
            elements: raw
          final_message:
            description:
              - Message to display when cloud-init completes.
            type: str
          phone_home:
            description:
              - Phone home configuration.
            type: dict
            suboptions:
              url:
                description:
                  - URL to POST instance data to.
                type: str
                required: true
              post:
                description:
                  - Data fields to POST.
                type: list
                elements: str
              tries:
                description:
                  - Number of attempts.
                type: int
      cloud-init.vendor-data:
        description:
          - Cloud-init vendor data configuration.
        type: dict
        suboptions:
          bootcmd:
            description:
              - Commands to run early in the boot process.
            type: list
            elements: raw
          users:
            description:
              - Users to create.
            type: list
            elements: dict
            suboptions:
              name:
                description:
                  - User name.
                type: str
                required: true
              groups:
                description:
                  - Groups to add the user to.
                type: raw
              shell:
                description:
                  - Login shell for the user.
                type: str
              sudo:
                description:
                  - Sudo rule for the user.
                type: raw
              ssh_authorized_keys:
                description:
                  - SSH public keys to add to the user.
                type: list
                elements: str
              ssh_import_id:
                description:
                  - SSH IDs to import public keys from.
                type: list
                elements: str
              ssh_redirect_user:
                description:
                  - SSH login redirection to default user.
                type: bool
              lock_passwd:
                description:
                  - User password lock.
                type: bool
              passwd:
                description:
                  - Hashed password for the user.
                type: str
              plain_text_passwd:
                description:
                  - Plain text password for the user.
                type: str
              hashed_passwd:
                description:
                  - Pre-hashed password for the user.
                type: str
              gecos:
                description:
                  - GECOS field for the user.
                type: str
              homedir:
                description:
                  - Home directory path.
                type: str
              primary_group:
                description:
                  - Primary group for the user.
                type: str
              no_create_home:
                description:
                  - Home directory creation skip.
                type: bool
              no_user_group:
                description:
                  - User group creation skip.
                type: bool
              no_log_init:
                description:
                  - User initialization log skip.
                type: bool
              create_groups:
                description:
                  - User group creation.
                type: bool
              expiredate:
                description:
                  - Account expiration date in YYYY-MM-DD format.
                type: str
              inactive:
                description:
                  - Days after password expires until account is disabled.
                type: str
              system:
                description:
                  - System user.
                type: bool
              uid:
                description:
                  - Numeric user ID.
                type: int
              snapuser:
                description:
                  - Email for Snappy user creation.
                type: str
              doas:
                description:
                  - Doas rules for the user.
                type: list
                elements: str
              selinux_user:
                description:
                  - SELinux user for login mapping.
                type: str
          groups:
            description:
              - Groups to create.
            type: list
            elements: raw
          user:
            description:
              - Default user name.
            type: str
          password:
            description:
              - Password for the default user.
            type: str
          ssh_pwauth:
            description:
              - SSH password authentication.
            type: bool
          ssh_authorized_keys:
            description:
              - SSH public keys to add to the default user.
            type: list
            elements: str
          ssh_deletekeys:
            description:
              - Default SSH host key deletion.
            type: bool
          ssh_genkeytypes:
            description:
              - SSH key types to generate.
            type: list
            elements: str
          ssh_keys:
            description:
              - Pre-generated SSH host keys.
            type: dict
            suboptions:
              ed25519_private:
                description:
                  - Ed25519 private host key.
                type: str
              ed25519_public:
                description:
                  - Ed25519 public host key.
                type: str
              ed25519_certificate:
                description:
                  - Ed25519 host certificate.
                type: str
              rsa_private:
                description:
                  - RSA private host key.
                type: str
              rsa_public:
                description:
                  - RSA public host key.
                type: str
              rsa_certificate:
                description:
                  - RSA host certificate.
                type: str
              ecdsa_private:
                description:
                  - ECDSA private host key.
                type: str
              ecdsa_public:
                description:
                  - ECDSA public host key.
                type: str
              ecdsa_certificate:
                description:
                  - ECDSA host certificate.
                type: str
          ssh_publish_hostkeys:
            description:
              - SSH host key publishing configuration.
            type: dict
            suboptions:
              enabled:
                description:
                  - Host key publishing.
                type: bool
              blacklist:
                description:
                  - Key types to exclude from publishing.
                type: list
                elements: str
          ssh_quiet_keygen:
            description:
              - SSH key generation output suppression.
            type: bool
          allow_public_ssh_keys:
            description:
              - Public SSH key allowance.
            type: bool
          disable_root:
            description:
              - Root login.
            type: bool
          disable_root_opts:
            description:
              - SSH options applied when root login is disabled.
            type: str
          chpasswd:
            description:
              - Password change settings.
            type: dict
            suboptions:
              expire:
                description:
                  - Password expiry on first login.
                type: bool
              users:
                description:
                  - User password entries.
                type: list
                elements: dict
                suboptions:
                  name:
                    description:
                      - User name.
                    type: str
                    required: true
                  password:
                    description:
                      - Password for the user.
                    type: str
                  type:
                    description:
                      - Password type.
                    type: str
                    choices: [text, hash, RANDOM]
          timezone:
            description:
              - System timezone.
            type: str
          locale:
            description:
              - System locale.
            type: str
          locale_configfile:
            description:
              - Locale configuration file path.
            type: str
          hostname:
            description:
              - System hostname.
            type: str
          fqdn:
            description:
              - Fully qualified domain name.
            type: str
          prefer_fqdn_over_hostname:
            description:
              - FQDN preference over short hostname.
            type: bool
          manage_etc_hosts:
            description:
              - /etc/hosts management.
            type: bool
          package_update:
            description:
              - First-boot package list update.
            type: bool
          package_upgrade:
            description:
              - First-boot package upgrade.
            type: bool
          package_reboot_if_required:
            description:
              - Post-upgrade reboot.
            type: bool
          packages:
            description:
              - Packages to install on first boot.
            type: list
            elements: str
          apt:
            description:
              - APT package manager configuration.
            type: dict
            suboptions:
              sources_list:
                description:
                  - Custom sources.list content.
                type: str
              preserve_sources_list:
                description:
                  - Existing sources.list preservation.
                type: bool
              disable_suites:
                description:
                  - APT suites to disable.
                type: list
                elements: str
              primary:
                description:
                  - Primary mirror configuration.
                type: list
                elements: raw
              security:
                description:
                  - Security mirror configuration.
                type: list
                elements: raw
              sources:
                description:
                  - Additional APT source definitions.
                type: list
                elements: dict
                suboptions:
                  name:
                    description:
                      - Source entry identifier and filename.
                    type: str
                    required: true
                  source:
                    description:
                      - Sources.list entry.
                    type: str
                  keyid:
                    description:
                      - GPG key ID to import.
                    type: str
                  key:
                    description:
                      - Raw GPG key.
                    type: str
                  keyserver:
                    description:
                      - Alternate keyserver to pull key from.
                    type: str
                  filename:
                    description:
                      - Name of the source list file.
                    type: str
                  append:
                    description:
                      - Source file append mode.
                    type: bool
              conf:
                description:
                  - APT configuration to write.
                type: str
              proxy:
                description:
                  - APT proxy URL.
                type: str
              http_proxy:
                description:
                  - HTTP proxy URL for APT.
                type: str
              ftp_proxy:
                description:
                  - FTP proxy URL for APT.
                type: str
              https_proxy:
                description:
                  - HTTPS proxy URL for APT.
                type: str
              add_apt_repo_match:
                description:
                  - Regex for matching add-apt-repository entries.
                type: str
              debconf_selections:
                description:
                  - Debconf preseed selections.
                type: list
                elements: dict
                suboptions:
                  name:
                    description:
                      - Selection set identifier.
                    type: str
                    required: true
                  selection:
                    description:
                      - Debconf selection lines.
                    type: str
                    required: true
          snap:
            description:
              - Snap package manager configuration.
            type: dict
            suboptions:
              commands:
                description:
                  - Snap commands to execute.
                type: list
                elements: raw
          growpart:
            description:
              - Partition growing configuration.
            type: dict
            suboptions:
              mode:
                description:
                  - Growpart mode.
                type: str
                choices: [auto, growpart, gpart, "off"]
              devices:
                description:
                  - Devices to grow.
                type: list
                elements: str
              ignore_growroot_disabled:
                description:
                  - Growroot disabled marker bypass.
                type: bool
          disk_setup:
            description:
              - Disk partitioning configuration.
            type: list
            elements: dict
            suboptions:
              name:
                description:
                  - Device path.
                type: str
                required: true
              table_type:
                description:
                  - Partition table type.
                type: str
                choices: [mbr, gpt]
              layout:
                description:
                  - Partition layout specification.
                type: raw
              overwrite:
                description:
                  - Existing partition table overwrite.
                type: bool
          fs_setup:
            description:
              - Filesystem creation configuration.
            type: list
            elements: dict
            suboptions:
              label:
                description:
                  - Filesystem label.
                type: str
              filesystem:
                description:
                  - Filesystem type.
                type: str
              device:
                description:
                  - Device path.
                type: str
              partition:
                description:
                  - Partition specification.
                type: raw
              overwrite:
                description:
                  - Existing filesystem overwrite.
                type: bool
              replace_fs:
                description:
                  - Existing filesystem replacement.
                type: bool
              extra_opts:
                description:
                  - Extra options for mkfs.
                type: list
                elements: str
              cmd:
                description:
                  - Custom mkfs command.
                type: raw
          mounts:
            description:
              - Mount point definitions.
            type: list
            elements: raw
          mount_default_fields:
            description:
              - Default values for mount entries with fewer than six fields.
            type: list
            elements: raw
          swap:
            description:
              - Swap configuration.
            type: dict
            suboptions:
              filename:
                description:
                  - Swap file path.
                type: str
              size:
                description:
                  - Swap size in bytes or C(auto).
                type: raw
              maxsize:
                description:
                  - Maximum swap size in bytes.
                type: raw
          ntp:
            description:
              - NTP client configuration.
            type: dict
            suboptions:
              enabled:
                description:
                  - NTP.
                type: bool
              servers:
                description:
                  - NTP servers.
                type: list
                elements: str
              pools:
                description:
                  - NTP pools.
                type: list
                elements: str
              peers:
                description:
                  - NTP peer nodes.
                type: list
                elements: str
              allow:
                description:
                  - Allowed NTP network ranges.
                type: list
                elements: str
              ntp_client:
                description:
                  - NTP client to use.
                type: str
              config:
                description:
                  - NTP client-specific configuration.
                type: dict
                suboptions:
                  confpath:
                    description:
                      - NTP client configuration file path.
                    type: str
                  check_exe:
                    description:
                      - Executable name for the NTP client.
                    type: str
                  packages:
                    description:
                      - Packages needed for the NTP client.
                    type: list
                    elements: str
                  service_name:
                    description:
                      - Service name for the NTP client.
                    type: str
                  template:
                    description:
                      - Jinja template for NTP client configuration.
                    type: str
          ca_certs:
            description:
              - CA certificate configuration.
            type: dict
            suboptions:
              trusted:
                description:
                  - Trusted CA certificates in PEM format.
                type: list
                elements: str
              remove_defaults:
                description:
                  - Default CA certificate removal.
                type: bool
          resolv_conf:
            description:
              - DNS resolver configuration.
            type: dict
            suboptions:
              nameservers:
                description:
                  - DNS server addresses.
                type: list
                elements: str
              searchdomains:
                description:
                  - DNS search domains.
                type: list
                elements: str
              domain:
                description:
                  - Default DNS domain.
                type: str
              sortlist:
                description:
                  - DNS sort list.
                type: list
                elements: str
              options:
                description:
                  - Resolver options for /etc/resolv.conf.
                type: dict
                suboptions:
                  ndots:
                    description:
                      - Minimum dots in a name before absolute query.
                    type: int
                  timeout:
                    description:
                      - Resolver query timeout in seconds.
                    type: int
                  attempts:
                    description:
                      - Number of resolver query attempts.
                    type: int
                  rotate:
                    description:
                      - Nameserver rotation.
                    type: bool
                  no-check-names:
                    description:
                      - Name checking disabling.
                    type: bool
                  inet6:
                    description:
                      - IPv6 address preference.
                    type: bool
                  edns0:
                    description:
                      - EDNS0 extensions.
                    type: bool
                  single-request:
                    description:
                      - Sequential A and AAAA queries.
                    type: bool
                  single-request-reopen:
                    description:
                      - Socket reopen for sequential queries.
                    type: bool
                  no-tld-query:
                    description:
                      - Top-level domain query disabling.
                    type: bool
                  use-vc:
                    description:
                      - TCP DNS queries.
                    type: bool
                  trust-ad:
                    description:
                      - Resolver AD flag trust.
                    type: bool
                  no-reload:
                    description:
                      - Automatic config reload disabling.
                    type: bool
          manage_resolv_conf:
            description:
              - /etc/resolv.conf management.
            type: bool
          power_state:
            description:
              - Power state change after cloud-init completes.
            type: dict
            suboptions:
              mode:
                description:
                  - Power state action to take.
                type: str
                choices: [reboot, poweroff, halt]
              delay:
                description:
                  - Delay before power action.
                type: str
              timeout:
                description:
                  - Timeout in seconds for power action.
                type: int
              condition:
                description:
                  - Condition to check before power action.
                type: raw
          write_files:
            description:
              - Files to create on first boot.
            type: list
            elements: dict
            suboptions:
              path:
                description:
                  - Absolute path of the file to create.
                type: str
                required: true
              content:
                description:
                  - Content to write to the file.
                type: str
              source:
                description:
                  - URL source for file content.
                type: dict
                suboptions:
                  uri:
                    description:
                      - URL to fetch content from.
                    type: str
                    required: true
                  headers:
                    description:
                      - HTTP headers for the request.
                    type: list
                    elements: dict
                    suboptions:
                      name:
                        description:
                          - Header name.
                        type: str
                        required: true
                      value:
                        description:
                          - Header value.
                        type: str
                        required: true
              owner:
                description:
                  - Owner and group of the file.
                type: str
              permissions:
                description:
                  - File permissions in octal notation.
                type: str
              encoding:
                description:
                  - Content encoding.
                type: str
                choices: [b64, base64, gz, gzip, gz+b64, gzip+b64, gz+base64, gzip+base64, text/plain]
              append:
                description:
                  - File append mode.
                type: bool
              defer:
                description:
                  - Deferred writing until final stage.
                type: bool
          runcmd:
            description:
              - Commands to run after cloud-init completes.
            type: list
            elements: raw
          final_message:
            description:
              - Message to display when cloud-init completes.
            type: str
          phone_home:
            description:
              - Phone home configuration.
            type: dict
            suboptions:
              url:
                description:
                  - URL to POST instance data to.
                type: str
                required: true
              post:
                description:
                  - Data fields to POST.
                type: list
                elements: str
              tries:
                description:
                  - Number of attempts.
                type: int
"""
