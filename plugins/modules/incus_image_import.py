#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: Roman Kuzmitskii <ansible@damex.org>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

"""
Ensure Incus image from file or URL.
"""

from __future__ import annotations

DOCUMENTATION = r"""
---
module: incus_image_import
short_description: Ensure Incus image from file or URL
author: Roman Kuzmitskii (@damex) <ansible@damex.org>
description:
  - Import and delete Incus images from local files or URLs.
  - Supports raw and qcow2 disk images for virtual machines.
  - Raw images are automatically converted to qcow2 using C(qemu-img).
  - ZIP and xz archives are automatically extracted.
  - Images are project-scoped resources identified by alias.
  - Requires C(qemu-img) on the target host for format detection and conversion.
extends_documentation_fragment:
  - damex.incus.common
  - damex.incus.common.project
  - damex.incus.common.write
options:
  alias:
    description:
      - Primary alias for the image on the local server.
      - Used to check existence and as the first alias assigned on import.
    type: str
    required: true
  aliases:
    description:
      - Additional aliases to assign to the image.
    type: list
    elements: str
  source:
    description:
      - Path to a local image file or URL to download from.
      - Supports raw and qcow2 disk images.
      - ZIP and xz archives are automatically extracted.
      - Required when O(state=present) and the image does not yet exist or O(force=true).
    type: str
  architecture:
    description:
      - Image architecture identifier.
    type: str
    default: x86_64
  properties:
    description:
      - Image properties included in the metadata.
    type: dict
    suboptions:
      os:
        description:
          - Operating system name.
        type: str
      release:
        description:
          - Operating system release or version.
        type: str
      description:
        description:
          - Human-readable image description.
        type: str
      variant:
        description:
          - Image variant.
        type: str
      serial:
        description:
          - Image serial or build identifier.
        type: str
      name:
        description:
          - Image name.
        type: str
  checksum:
    description:
      - Expected checksum of the source file for verification.
      - Verified against the downloaded or local source file before any extraction or conversion.
    type: str
  checksum_algorithm:
    description:
      - Hash algorithm used for O(checksum) verification.
    type: str
    choices: [sha256, sha512, sha384, md5]
    default: sha256
  state:
    description:
      - Desired state of the image.
    type: str
    choices: [present, absent]
    default: present
  public:
    description:
      - Make the image available to unauthenticated users.
    type: bool
    default: false
  force:
    description:
      - Delete and re-import the image even when the alias already exists.
      - Useful when the upstream source has been updated at the same URL.
    type: bool
    default: false
  timeout:
    description:
      - Timeout in seconds for downloading the source file from a URL.
      - Only applies when O(source) is a URL.
    type: int
    default: 300
"""

EXAMPLES = r"""
- name: Ensure MikroTik CHR image from URL
  damex.incus.incus_image_import:
    alias: chr/7.22
    source: https://download.mikrotik.com/routeros/7.22/chr-7.22.img.zip
    architecture: x86_64
    properties:
      os: RouterOS
      release: "7.22"
      description: MikroTik CHR 7.22

- name: Ensure MikroTik CHR image with checksum verification
  damex.incus.incus_image_import:
    alias: chr/7.22
    source: https://download.mikrotik.com/routeros/7.22/chr-7.22.img.zip
    checksum: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
    checksum_algorithm: sha256
    properties:
      os: RouterOS
      release: "7.22"
      description: MikroTik CHR 7.22

- name: Ensure image from local qcow2 file
  damex.incus.incus_image_import:
    alias: custom/1.0
    source: /tmp/custom-image.qcow2
    properties:
      os: CustomOS
      release: "1.0"
      description: Custom OS Image

- name: Ensure image with multiple aliases
  damex.incus.incus_image_import:
    alias: chr
    aliases:
      - chr/7.22
    source: https://download.mikrotik.com/routeros/7.22/chr-7.22.img.zip
    properties:
      os: RouterOS
      release: "7.22"
      description: MikroTik CHR 7.22

- name: Ensure image is re-imported from upstream
  damex.incus.incus_image_import:
    alias: chr/7.22
    source: https://download.mikrotik.com/routeros/7.22/chr-7.22.img.zip
    force: true
    properties:
      os: RouterOS
      release: "7.22"
      description: MikroTik CHR 7.22

- name: Ensure image is absent
  damex.incus.incus_image_import:
    alias: chr/7.22
    state: absent
"""

RETURN = r"""
"""

import hashlib
import json
import os
import lzma
import shutil
import tarfile
import tempfile
import time
import zipfile
from typing import Any
from urllib.parse import quote
from ansible.module_utils.urls import open_url

try:
    import yaml
except ImportError:
    pass

from ansible_collections.damex.incus.plugins.module_utils.incus import (
    IncusClient,
    incus_build_query,
    incus_create_client,
    incus_create_write_module,
    incus_resolve_image_alias,
    incus_run_write_module,
    incus_wait,
)

__all__ = ['DOCUMENTATION', 'EXAMPLES', 'RETURN', 'main']


def _incus_image_import_download_source(module: Any, source: str, temp_directory: str, timeout: int) -> str:
    """
    Download source to temporary directory.

    >>> _incus_image_import_download_source(module, '/tmp/image.img', '/tmp/work', 30)
    '/tmp/image.img'
    """
    if source.startswith(('http://', 'https://')):
        download_path = os.path.join(temp_directory, os.path.basename(source))
        try:
            with open_url(source, timeout=timeout) as response:
                with open(download_path, 'wb') as fh:
                    shutil.copyfileobj(response, fh)
        except OSError as exc:
            module.fail_json(msg=f"Failed downloading source: {exc}")
        return download_path
    if not os.path.isfile(source):
        module.fail_json(msg=f"Source file not found: {source}")
    return source


def _incus_image_import_verify_checksum(
    module: Any, file_path: str, expected_checksum: str, algorithm: str,
) -> None:
    """
    Verify file checksum.

    >>> _incus_image_import_verify_checksum(module, '/tmp/image.img', 'abc123', 'sha256')
    """
    file_hash = hashlib.new(algorithm)
    with open(file_path, 'rb') as fh:
        while True:
            chunk = fh.read(65536)
            if not chunk:
                break
            file_hash.update(chunk)
    actual_checksum = file_hash.hexdigest()
    if actual_checksum != expected_checksum:
        module.fail_json(
            msg=f"Checksum mismatch: expected {expected_checksum}, got {actual_checksum}",
        )


def _incus_image_import_extract_zip(module: Any, file_path: str, temp_directory: str) -> str:
    """
    Extract first file from ZIP archive.

    >>> _incus_image_import_extract_zip(module, '/tmp/image.zip', '/tmp/work')
    '/tmp/work/image.img'
    """
    try:
        with zipfile.ZipFile(file_path, 'r') as zf:
            names = zf.namelist()
            if not names:
                module.fail_json(msg="ZIP archive is empty")
            zf.extract(names[0], temp_directory)
            return os.path.join(temp_directory, names[0])
    except zipfile.BadZipFile as exc:
        module.fail_json(msg=f"Invalid ZIP archive: {exc}")
    return file_path


def _incus_image_import_is_xz(file_path: str) -> bool:
    """
    Detect xz compressed file.

    >>> _incus_image_import_is_xz('/tmp/image.img.xz')
    True
    """
    try:
        with lzma.open(file_path, 'rb') as fh:
            fh.read(1)
        return True
    except lzma.LZMAError:
        return False


def _incus_image_import_extract_xz(module: Any, file_path: str, temp_directory: str) -> str:
    """
    Decompress xz compressed file.

    >>> _incus_image_import_extract_xz(module, '/tmp/image.img.xz', '/tmp/work')
    '/tmp/work/image.img'
    """
    output_path = os.path.join(temp_directory, os.path.basename(file_path).removesuffix('.xz'))
    try:
        with lzma.open(file_path, 'rb') as xz_file:
            with open(output_path, 'wb') as out_file:
                shutil.copyfileobj(xz_file, out_file)
    except lzma.LZMAError as exc:
        module.fail_json(msg=f"Failed decompressing xz archive: {exc}")
    return output_path


def _incus_image_import_detect_format(module: Any, qemu_img_path: str, file_path: str) -> str:
    """
    Detect image format using qemu-img.

    >>> _incus_image_import_detect_format(module, '/usr/bin/qemu-img', '/tmp/image.img')
    'raw'
    """
    rc, stdout, stderr = module.run_command([qemu_img_path, 'info', '--output=json', file_path])
    if rc:
        module.fail_json(msg=f"Failed detecting image format: {stderr}")
    try:
        info = json.loads(stdout)
        image_format: str = info.get('format', 'raw')
        return image_format
    except (ValueError, KeyError) as exc:
        module.fail_json(msg=f"Failed parsing qemu-img output: {exc}")
    return 'raw'


def _incus_image_import_convert_to_qcow2(
    module: Any, qemu_img_path: str, file_path: str, temp_directory: str,
) -> str:
    """
    Convert image to qcow2 format.

    >>> _incus_image_import_convert_to_qcow2(module, '/usr/bin/qemu-img', '/tmp/image.img', '/tmp/work')
    '/tmp/work/rootfs.img'
    """
    qcow2_path = os.path.join(temp_directory, 'rootfs.img')
    rc, _stdout, stderr = module.run_command([
        qemu_img_path, 'convert', '-f', 'raw', '-O', 'qcow2', file_path, qcow2_path,
    ])
    if rc:
        module.fail_json(msg=f"Failed converting image to qcow2: {stderr}")
    return qcow2_path


def _incus_image_import_build_metadata(architecture: str, properties: dict[str, str] | None) -> str:
    """
    Build metadata.yaml content.

    >>> _incus_image_import_build_metadata('x86_64', {'os': 'debian', 'release': 'bookworm'})
    'architecture: x86_64\\ncreation_date: ...\\nproperties:\\n  os: debian\\n  release: bookworm\\n'
    """
    metadata: dict[str, Any] = {
        'architecture': architecture,
        'creation_date': int(time.time()),
    }
    clean_properties = {
        property_key: property_value
        for property_key, property_value in (properties or {}).items()
        if property_value is not None
    }
    if clean_properties:
        metadata['properties'] = clean_properties
    return yaml.dump(metadata, default_flow_style=False)


def _incus_image_import_build_tarball(
    module: Any, image_path: str, architecture: str,
    properties: dict[str, str] | None, temp_directory: str,
) -> str:
    """
    Build image tarball with metadata.

    >>> _incus_image_import_build_tarball(module, '/tmp/work/rootfs.img', 'x86_64', None, '/tmp/work')
    '/tmp/work/image.tar.gz'
    """
    metadata_path = os.path.join(temp_directory, 'metadata.yaml')
    with open(metadata_path, 'w', encoding='utf-8') as fh:
        fh.write(_incus_image_import_build_metadata(architecture, properties))
    tarball_path = os.path.join(temp_directory, 'image.tar.gz')
    try:
        with tarfile.open(tarball_path, 'w:gz') as tar:
            tar.add(metadata_path, arcname='metadata.yaml')
            tar.add(image_path, arcname='rootfs.img')
    except OSError as exc:
        module.fail_json(msg=f"Failed creating image tarball: {exc}")
    return tarball_path


def _incus_image_import_prepare(
    module: Any, source: str, architecture: str,
    properties: dict[str, str] | None, temp_directory: str,
) -> str:
    """
    Prepare image tarball from source.

    >>> _incus_image_import_prepare(module, '/tmp/image.img', 'x86_64', None, '/tmp/work')
    '/tmp/work/image.tar.gz'
    """
    qemu_img_path = module.get_bin_path('qemu-img')
    if not qemu_img_path:
        module.fail_json(msg="qemu-img is required but not found on the target host")
    file_path = _incus_image_import_download_source(module, source, temp_directory, module.params['timeout'])
    expected_checksum = module.params.get('checksum')
    if expected_checksum:
        _incus_image_import_verify_checksum(
            module, file_path, expected_checksum, module.params['checksum_algorithm'],
        )
    if zipfile.is_zipfile(file_path):
        file_path = _incus_image_import_extract_zip(module, file_path, temp_directory)
    if _incus_image_import_is_xz(file_path):
        file_path = _incus_image_import_extract_xz(module, file_path, temp_directory)
    image_format = _incus_image_import_detect_format(module, qemu_img_path, file_path)
    if image_format != 'qcow2':
        file_path = _incus_image_import_convert_to_qcow2(module, qemu_img_path, file_path, temp_directory)
    return _incus_image_import_build_tarball(
        module, file_path, architecture, properties, temp_directory,
    )


def _incus_image_import_create_aliases(
    client: IncusClient, fingerprint: str, alias: str,
    aliases: list[str] | None, query: str,
) -> None:
    """
    Create image aliases.

    >>> _incus_image_import_create_aliases(client, 'abc123', 'debian/13', None, '?project=default')
    """
    all_aliases = [alias] + (aliases or [])
    for name in all_aliases:
        client.post(f'/1.0/images/aliases{query}', {
            'name': name,
            'target': fingerprint,
        })


def main() -> None:
    """
    Run module.

    >>> main()
    """
    module = incus_create_write_module({
        'alias': {'type': 'str', 'required': True},
        'aliases': {
            'type': 'list',
            'elements': 'str',
        },
        'state': {
            'type': 'str',
            'default': 'present',
            'choices': [
                'present',
                'absent',
            ],
        },
        'project': {'type': 'str', 'default': 'default'},
        'source': {'type': 'str'},
        'checksum': {'type': 'str'},
        'checksum_algorithm': {
            'type': 'str',
            'default': 'sha256',
            'choices': [
                'sha256',
                'sha512',
                'sha384',
                'md5',
            ],
        },
        'architecture': {'type': 'str', 'default': 'x86_64'},
        'properties': {
            'type': 'dict',
            'options': {
                'os': {'type': 'str'},
                'release': {'type': 'str'},
                'description': {'type': 'str'},
                'variant': {'type': 'str'},
                'serial': {'type': 'str'},
                'name': {'type': 'str'},
            },
        },
        'public': {'type': 'bool', 'default': False},
        'force': {'type': 'bool', 'default': False},
        'timeout': {'type': 'int', 'default': 300},
    }, require_yaml=True)

    def _ensure_image() -> bool:
        client = incus_create_client(module)
        alias = module.params['alias']
        project = module.params['project']
        query = incus_build_query(project=project)

        if module.params['state'] == 'present':
            fingerprint = incus_resolve_image_alias(client, alias, query)
            if fingerprint and not module.params['force']:
                return False
            if fingerprint and module.params['force']:
                if not module.check_mode:
                    encoded_fingerprint = quote(fingerprint, safe='')
                    incus_wait(module, client, client.delete(f'/1.0/images/{encoded_fingerprint}{query}'))
            if not module.params['source']:
                module.fail_json(msg="'source' is required when creating an image")
            if module.check_mode:
                return True
            temp_directory = tempfile.mkdtemp()
            try:
                tarball_path = _incus_image_import_prepare(
                    module, module.params['source'], module.params['architecture'],
                    module.params.get('properties'), temp_directory,
                )
                response = client.post_file(
                    f'/1.0/images{query}', tarball_path, module.params['public'],
                )
                metadata = client.wait(response)
                if metadata:
                    fingerprint = (metadata.get('metadata') or {}).get('fingerprint', '')
                else:
                    fingerprint = (response.get('metadata') or {}).get('fingerprint', '')
                if not fingerprint:
                    module.fail_json(msg="Failed to retrieve image fingerprint after upload")
                _incus_image_import_create_aliases(
                    client, fingerprint, alias, module.params.get('aliases'), query,
                )
            finally:
                shutil.rmtree(temp_directory, ignore_errors=True)
            return True

        fingerprint = incus_resolve_image_alias(client, alias, query)
        if not fingerprint:
            return False
        if not module.check_mode:
            encoded_fingerprint = quote(fingerprint, safe='')
            incus_wait(module, client, client.delete(f'/1.0/images/{encoded_fingerprint}{query}'))
        return True

    incus_run_write_module(module, _ensure_image)


if __name__ == '__main__':
    main()
