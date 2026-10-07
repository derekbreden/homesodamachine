"""Bind scene content independently of another check's provenance metadata.

Native part records, ports, routes, cutters, ownership and assembly parameters
remain in the digest. Only top-level results and input/provenance digests are
excluded. Producers take this snapshot when reading a manifest, alongside its
raw-file hash and the hashes of every imported native shape.
"""
import hashlib
import json
from pathlib import Path

RESULT_FIELDS = {
    'checks', 'failures', 'pass', 'pass_result', 'all_checks_pass',
    'geometry_pass', 'source_drift', 'manifest_drift', 'publication_status',
    'native_inputs', 'hardware_only', 'static_pair_checks',
}


def content_sha256(manifest):
    content = {key: value for key, value in manifest.items()
               if key not in RESULT_FIELDS and not key.endswith('sha256')
               and key != 'source_inputs'}
    data = json.dumps(content, sort_keys=True, separators=(',', ':')).encode()
    return hashlib.sha256(data).hexdigest()


def manifest_content_sha256(path):
    return content_sha256(json.loads(Path(path).read_text()))
