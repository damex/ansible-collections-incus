#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: Roman Kuzmitskii <ansible@damex.org>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

"""Ensure Incus storage."""

from __future__ import annotations

DOCUMENTATION = r"""
---
module: incus_storage
short_description: Ensure Incus storage
author: Roman Kuzmitskii (@damex) <ansible@damex.org>
description:
  - Create, update, and delete Incus storage pools via the Incus REST API.
  - Storage pools are global resources, not project-scoped.
  - The storage driver is set on creation and cannot be changed afterwards.
extends_documentation_fragment: [damex.incus.common, damex.incus.common.write]
options:
  name:
    description:
      - Name of the storage pool.
    type: str
    required: true
  driver:
    description:
      - Storage driver.
      - Required when creating a new storage pool.
      - Ignored on update — driver cannot be changed after creation.
    type: str
    choices: [dir, btrfs, lvm, zfs, ceph, cephfs, cephobject, linstor, truenas]
  description:
    description:
      - Storage pool description.
    type: str
    default: ''
  target:
    description:
      - Cluster member to target for pending storage pool creation.
    type: str
  state:
    description:
      - Desired state of the storage pool.
    type: str
    choices: [present, absent]
    default: present
  config:
    description:
      - Storage pool configuration key-value pairs.
      - Boolean values are converted to lowercase strings.
    type: dict
    default: {}
    suboptions:
      source:
        description:
          - Path or device to use as storage source.
        type: str
      source.wipe:
        description:
          - Wipe the source device before use.
        type: bool
      size:
        description:
          - Size of the storage pool.
        type: str
      rsync.bwlimit:
        description:
          - Upper limit on the bandwidth for rsync.
        type: str
      rsync.compression:
        description:
          - Whether to use compression for rsync.
        type: bool
      btrfs.mount_options:
        description:
          - Mount options for the Btrfs filesystem.
        type: str
      lvm.metadata_size:
        description:
          - Size of the LVM metadata volume.
        type: str
      lvm.thinpool_metadata_size:
        description:
          - Size of the LVM thin pool metadata volume.
        type: str
      lvm.thinpool_name:
        description:
          - Name of the LVM thin pool.
        type: str
      lvm.use_thinpool:
        description:
          - Whether to use an LVM thin pool.
        type: bool
      lvm.vg.force_reuse:
        description:
          - Force reuse of an existing LVM volume group.
        type: bool
      lvm.vg_name:
        description:
          - Name of the LVM volume group.
        type: str
      zfs.clone_copy:
        description:
          - Whether to use ZFS lightweight clones.
        type: bool
      zfs.export:
        description:
          - Whether to export the ZFS pool on removal.
        type: bool
      zfs.pool_name:
        description:
          - Name of the ZFS pool.
        type: str
      zfs.blocksize:
        description:
          - Block size for the ZFS pool.
        type: str
      ceph.cluster_name:
        description:
          - Name of the Ceph cluster.
        type: str
      ceph.osd.data_pool_name:
        description:
          - Name of the Ceph OSD data pool.
        type: str
      ceph.osd.pg_name:
        description:
          - Name of the Ceph OSD placement group.
        type: str
      ceph.osd.pool_name:
        description:
          - Name of the Ceph OSD pool.
        type: str
      ceph.rbd.clone_copy:
        description:
          - Whether to use RBD lightweight clones.
        type: bool
      ceph.rbd.du:
        description:
          - Whether to use RBD disk usage tracking.
        type: bool
      ceph.rbd.features:
        description:
          - RBD image features to enable.
        type: str
      ceph.user.name:
        description:
          - Ceph user name.
        type: str
      cephfs.cluster_name:
        description:
          - Name of the CephFS cluster.
        type: str
      cephfs.create_missing:
        description:
          - Create missing CephFS pools.
        type: bool
      cephfs.data_pool:
        description:
          - Name of the CephFS data pool.
        type: str
      cephfs.fscache:
        description:
          - Whether to enable fscache for CephFS.
        type: bool
      cephfs.meta_pool:
        description:
          - Name of the CephFS metadata pool.
        type: str
      cephfs.osd_pg_num:
        description:
          - Number of placement groups for CephFS OSD pools.
        type: str
      cephfs.path:
        description:
          - CephFS path to mount.
        type: str
      cephfs.user.name:
        description:
          - CephFS user name.
        type: str
      cephobject.bucket_name_prefix:
        description:
          - Prefix for Ceph object store bucket names.
        type: str
      cephobject.cluster_name:
        description:
          - Name of the Ceph object store cluster.
        type: str
      cephobject.radosgw.endpoint:
        description:
          - URL of the RADOS Gateway endpoint.
        type: str
      cephobject.radosgw.endpoint_cert_file:
        description:
          - Path to the RADOS Gateway endpoint certificate.
        type: str
      cephobject.user.name:
        description:
          - Ceph object store user name.
        type: str
      linstor.resource_group.name:
        description:
          - Name of the LINSTOR resource group.
        type: str
      linstor.resource_group.place_count:
        description:
          - Number of replicas in the LINSTOR resource group.
        type: int
      linstor.resource_group.storage_pool:
        description:
          - LINSTOR storage pool for the resource group.
        type: str
      linstor.volume.prefix:
        description:
          - Prefix for LINSTOR volume names.
        type: str
      drbd.auto_add_quorum_tiebreaker:
        description:
          - Whether to automatically add a DRBD quorum tiebreaker.
        type: bool
      drbd.auto_diskful:
        description:
          - Automatic diskful mode for DRBD.
        type: str
      drbd.on_no_quorum:
        description:
          - Action to take when DRBD has no quorum.
        type: str
      truenas.allow_insecure:
        description:
          - Allow insecure connections to TrueNAS.
        type: bool
      truenas.api_key:
        description:
          - API key for TrueNAS authentication.
        type: str
      truenas.clone_copy:
        description:
          - Whether to use TrueNAS lightweight clones.
        type: bool
      truenas.config:
        description:
          - Path to the TrueNAS configuration file.
        type: str
      truenas.dataset:
        description:
          - Name of the TrueNAS dataset.
        type: str
      truenas.force_reuse:
        description:
          - Force reuse of an existing TrueNAS dataset.
        type: bool
      truenas.host:
        description:
          - Hostname or IP of the TrueNAS server.
        type: str
      truenas.initiator:
        description:
          - iSCSI initiator name for TrueNAS.
        type: str
      truenas.portal:
        description:
          - iSCSI portal ID for TrueNAS.
        type: str
"""

EXAMPLES = r"""
- name: Create dir storage pool
  damex.incus.incus_storage:
    name: default
    driver: dir

- name: Create ZFS storage pool
  damex.incus.incus_storage:
    name: tank
    driver: zfs
    config:
      zfs.pool_name: tank

- name: Remove storage pool
  damex.incus.incus_storage:
    name: default
    state: absent
"""

RETURN = r"""
"""

from ansible_collections.damex.incus.plugins.module_utils.incus import (
    INCUS_COMMON_ARGUMENT_SPEC,
    incus_build_desired,
    incus_create_write_module,
    incus_ensure_resource,
    incus_run_write_module,
)

__all__ = ['DOCUMENTATION', 'EXAMPLES', 'RETURN', 'main']

INCUS_STORAGE_CONFIG_OPTIONS = {
    'source': {'type': 'str'},
    'source.wipe': {'type': 'bool'},
    'size': {'type': 'str'},
    'rsync.bwlimit': {'type': 'str'},
    'rsync.compression': {'type': 'bool'},
    'btrfs.mount_options': {'type': 'str'},
    'lvm.metadata_size': {'type': 'str'},
    'lvm.thinpool_metadata_size': {'type': 'str'},
    'lvm.thinpool_name': {'type': 'str'},
    'lvm.use_thinpool': {'type': 'bool'},
    'lvm.vg.force_reuse': {'type': 'bool'},
    'lvm.vg_name': {'type': 'str'},
    'zfs.clone_copy': {'type': 'bool'},
    'zfs.export': {'type': 'bool'},
    'zfs.pool_name': {'type': 'str'},
    'zfs.blocksize': {'type': 'str'},
    'ceph.cluster_name': {'type': 'str'},
    'ceph.osd.data_pool_name': {'type': 'str'},
    'ceph.osd.pg_name': {'type': 'str'},
    'ceph.osd.pool_name': {'type': 'str'},
    'ceph.rbd.clone_copy': {'type': 'bool'},
    'ceph.rbd.du': {'type': 'bool'},
    'ceph.rbd.features': {'type': 'str'},
    'ceph.user.name': {'type': 'str'},
    'cephfs.cluster_name': {'type': 'str'},
    'cephfs.create_missing': {'type': 'bool'},
    'cephfs.data_pool': {'type': 'str'},
    'cephfs.fscache': {'type': 'bool'},
    'cephfs.meta_pool': {'type': 'str'},
    'cephfs.osd_pg_num': {'type': 'str'},
    'cephfs.path': {'type': 'str'},
    'cephfs.user.name': {'type': 'str'},
    'cephobject.bucket_name_prefix': {'type': 'str'},
    'cephobject.cluster_name': {'type': 'str'},
    'cephobject.radosgw.endpoint': {'type': 'str'},
    'cephobject.radosgw.endpoint_cert_file': {'type': 'str'},
    'cephobject.user.name': {'type': 'str'},
    'linstor.resource_group.name': {'type': 'str'},
    'linstor.resource_group.place_count': {'type': 'int'},
    'linstor.resource_group.storage_pool': {'type': 'str'},
    'linstor.volume.prefix': {'type': 'str'},
    'drbd.auto_add_quorum_tiebreaker': {'type': 'bool'},
    'drbd.auto_diskful': {'type': 'str'},
    'drbd.on_no_quorum': {'type': 'str'},
    'truenas.allow_insecure': {'type': 'bool'},
    'truenas.api_key': {'type': 'str', 'no_log': True},
    'truenas.clone_copy': {'type': 'bool'},
    'truenas.config': {'type': 'str'},
    'truenas.dataset': {'type': 'str'},
    'truenas.force_reuse': {'type': 'bool'},
    'truenas.host': {'type': 'str'},
    'truenas.initiator': {'type': 'str'},
    'truenas.portal': {'type': 'str'},
}


def main() -> None:
    """Run module."""
    module = incus_create_write_module({
        **INCUS_COMMON_ARGUMENT_SPEC,
        'target': {'type': 'str'},
        'driver': {
            'type': 'str',
            'choices': [
                'dir', 'btrfs', 'lvm', 'zfs', 'ceph', 'cephfs', 'cephobject', 'linstor', 'truenas',
            ],
        },
        'config': {'type': 'dict', 'default': {}, 'options': INCUS_STORAGE_CONFIG_OPTIONS},
        'description': {'type': 'str', 'default': ''},
    })
    desired = incus_build_desired(module)
    incus_run_write_module(module, lambda: incus_ensure_resource(module, 'storage-pools', desired, ['driver']))


if __name__ == '__main__':
    main()
