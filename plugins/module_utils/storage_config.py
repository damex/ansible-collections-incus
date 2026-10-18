# Copyright: Roman Kuzmitskii <ansible@damex.org>
# SPDX-License-Identifier: GPL-3.0-or-later

"""
Incus storage pool config argument spec options.
"""

from __future__ import annotations

__all__ = [
    'INCUS_STORAGE_CONFIG_OPTIONS',
]

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
