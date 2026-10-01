"""Read immutable scan evidence and select elbow material in a rigid mm frame."""
from pathlib import Path
import gzip
import hashlib
import json
import numpy as np

HERE = Path(__file__).resolve().parent
ARCHIVE = Path.home() / 'Documents/3D Scans/2026-10-01-elbow'
SOURCE_SHA = 'b6f935b34965c9d3b7fe997052517add4517bf4d3b656d8643e25c18282fcdfe'


def read_cloud():
    raw = gzip.decompress((HERE / 'source-cloud.ply.gz').read_bytes())
    assert hashlib.sha256(raw).hexdigest() == SOURCE_SHA, 'Input scan digest mismatch'
    end = raw.index(b'end_header\n') + len(b'end_header\n')
    header = raw[:end].decode('ascii')
    properties = [line for line in header.splitlines() if line.startswith('property ')]
    assert properties == [f'property float {name}' for name in ('x','y','z','nx','ny','nz')]
    count = int(next(line.split()[-1] for line in header.splitlines() if line.startswith('element vertex ')))
    assert len(raw)-end == 24*count
    a = np.frombuffer(raw, dtype='<f4', offset=end).reshape(count, 6).astype(float)
    assert np.isfinite(a).all()
    return a[:, :3], a[:, 3:]


def rigid(points, transform):
    transform = np.asarray(transform)
    rotation = transform[:3, :3]
    assert np.allclose(rotation.T @ rotation, np.eye(3), atol=1e-8)
    assert abs(np.linalg.det(rotation)-1) < 1e-8
    assert np.allclose(transform[3], [0,0,0,1])
    return points @ rotation.T + transform[:3, 3]


def observations():
    evidence = json.loads((HERE/'scan-measurements.json').read_text())
    selection = json.loads((HERE/'scan-selection.json').read_text())
    p,n = read_cloud()
    table = ((p-np.array(selection['table_origin_native'])) @ np.array(selection['table_basis_rows']).T)
    T = np.array(evidence['native_to_reference'])
    return rigid(p,T), n@T[:3,:3].T, table[:,2]


def material_mask(p, height):
    """Inspected fixture exclusion, independent of model distances."""
    core = ((abs(p[:,0])<5.2)&(p[:,1]>-5.1)&(p[:,2]>-5.1)
            &(p[:,1]<7.3)&(p[:,2]<7.3))
    y = (p[:,1]>=6.6)&(p[:,1]<21.2)&(np.hypot(p[:,0],p[:,2])<8.7)
    z = (p[:,2]>=6.6)&(p[:,2]<21.2)&(np.hypot(p[:,0],p[:,1])<8.6)
    return (core|y|z)&(height>17.2)


def stats(v):
    v=np.asarray(v)
    return {'n':len(v), 'mean':float(np.mean(v)), 'median':float(np.median(v)),
            'rms':float(np.sqrt(np.mean(v*v))), 'p05':float(np.quantile(v,.05)),
            'p95':float(np.quantile(v,.95)), 'abs_p95':float(np.quantile(abs(v),.95)),
            'min':float(v.min()), 'max':float(v.max())}
