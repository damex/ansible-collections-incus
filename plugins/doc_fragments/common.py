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
    choices: [simplestreams, incus]
    default: simplestreams
"""

    INSTANCE_CONFIG = r"""
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
          - Whether to enable memory hotplug.
        type: str
      limits.memory.hugepages:
        description:
          - Whether to back instance memory with huge pages.
        type: bool
      limits.memory.oom_priority:
        description:
          - OOM killer priority for the instance.
        type: int
      limits.memory.swap:
        description:
          - Whether to encourage or discourage swapping.
        type: str
      limits.memory.swap.priority:
        description:
          - Swap priority compared to other instances.
        type: int
      boot.autostart:
        description:
          - Whether to start the instance on daemon startup.
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
          - Whether to restart the instance after a crash.
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
          - Whether to run the instance in privileged mode.
        type: bool
      security.nesting:
        description:
          - Allow running Incus inside the instance.
        type: bool
      security.agent.metrics:
        description:
          - Whether the incus-agent exposes metrics.
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
          - Path to the BPFFS mount in the instance.
        type: str
      security.csm:
        description:
          - Whether to enable Compatibility Support Module.
        type: bool
      security.guestapi:
        description:
          - Whether to enable the guest API.
        type: bool
      security.guestapi.images:
        description:
          - Whether to allow image access via the guest API.
        type: bool
      security.idmap.base:
        description:
          - Base host UID/GID for the ID map.
        type: int
      security.idmap.isolated:
        description:
          - Whether to use a unique ID map for the instance.
        type: bool
      security.idmap.size:
        description:
          - Size of the ID map range.
        type: int
      security.iommu:
        description:
          - Whether to enable IOMMU for the instance.
        type: bool
      security.protection.delete:
        description:
          - Whether to prevent deletion of the instance.
        type: bool
      security.protection.shift:
        description:
          - Whether to prevent UID/GID shifting.
        type: bool
      security.secureboot:
        description:
          - Whether to enable UEFI Secure Boot.
        type: bool
      security.sev:
        description:
          - Whether to enable AMD SEV encryption.
        type: bool
      security.sev.policy.es:
        description:
          - Whether to enable SEV-ES for the instance.
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
          - Whether to block compat syscalls on amd64.
        type: bool
      security.syscalls.deny_default:
        description:
          - Whether to enable default syscall deny list.
        type: bool
      security.syscalls.intercept.bpf:
        description:
          - Whether to intercept bpf syscalls.
        type: bool
      security.syscalls.intercept.bpf.devices:
        description:
          - Whether to allow device-type BPF programs.
        type: bool
      security.syscalls.intercept.mknod:
        description:
          - Whether to intercept mknod syscalls.
        type: bool
      security.syscalls.intercept.mount:
        description:
          - Whether to intercept mount syscalls.
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
          - Whether to use ID-mapped mounts for intercepted mounts.
        type: bool
      security.syscalls.intercept.sched_setscheduler:
        description:
          - Whether to intercept sched_setscheduler syscalls.
        type: bool
      security.syscalls.intercept.setxattr:
        description:
          - Whether to intercept setxattr syscalls.
        type: bool
      security.syscalls.intercept.sysinfo:
        description:
          - Whether to intercept sysinfo syscalls.
        type: bool
      migration.stateful:
        description:
          - Allow stateful stop/start and snapshots.
        type: bool
      migration.incremental.memory:
        description:
          - Whether to use incremental memory transfer.
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
          - Whether to snapshot stopped instances.
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
                  - Whether to enable DHCPv4.
                type: bool
              addresses:
                description:
                  - Static addresses in CIDR notation.
                type: list
                elements: str
              match:
                description:
                  - Match rules for the interface.
                type: dict
                suboptions:
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
              nameservers:
                description:
                  - DNS server configuration.
                type: dict
                suboptions:
                  addresses:
                    description:
                      - List of DNS server addresses.
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
                  - Whether to enable DHCPv4.
                type: bool
              addresses:
                description:
                  - Static addresses in CIDR notation.
                type: list
                elements: str
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
              nameservers:
                description:
                  - DNS server configuration.
                type: dict
                suboptions:
                  addresses:
                    description:
                      - List of DNS server addresses.
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
                  - Whether to enable DHCPv4.
                type: bool
              addresses:
                description:
                  - Static addresses in CIDR notation.
                type: list
                elements: str
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
                      - Whether to enable Spanning Tree Protocol.
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
              nameservers:
                description:
                  - DNS server configuration.
                type: dict
                suboptions:
                  addresses:
                    description:
                      - List of DNS server addresses.
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
                  - Whether to enable DHCPv4.
                type: bool
              addresses:
                description:
                  - Static addresses in CIDR notation.
                type: list
                elements: str
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
              nameservers:
                description:
                  - DNS server configuration.
                type: dict
                suboptions:
                  addresses:
                    description:
                      - List of DNS server addresses.
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
              - Whether to enable SSH password authentication.
            type: bool
          chpasswd:
            description:
              - Password change settings.
            type: dict
            suboptions:
              expire:
                description:
                  - Whether the password expires on first login.
                type: bool
          package_upgrade:
            description:
              - Whether to upgrade packages on first boot.
            type: bool
          packages:
            description:
              - Packages to install on first boot.
            type: list
            elements: str
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
              owner:
                description:
                  - Owner and group of the file.
                type: str
              permissions:
                description:
                  - File permissions in octal notation.
                type: str
          runcmd:
            description:
              - Commands to run after cloud-init completes.
            type: list
            elements: raw
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
              - Whether to enable SSH password authentication.
            type: bool
          chpasswd:
            description:
              - Password change settings.
            type: dict
            suboptions:
              expire:
                description:
                  - Whether the password expires on first login.
                type: bool
          package_upgrade:
            description:
              - Whether to upgrade packages on first boot.
            type: bool
          packages:
            description:
              - Packages to install on first boot.
            type: list
            elements: str
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
              owner:
                description:
                  - Owner and group of the file.
                type: str
              permissions:
                description:
                  - File permissions in octal notation.
                type: str
          runcmd:
            description:
              - Commands to run after cloud-init completes.
            type: list
            elements: raw
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
