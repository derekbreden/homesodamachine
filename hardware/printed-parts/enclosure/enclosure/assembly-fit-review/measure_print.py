"""Manual October 2026 C14 article measurements; not a build or commit check.

Run with tools/cad-venv/bin/python from the repository root. Measures the
October 10 project's main mesh and the current print STL in the machine frame.
"""
from pathlib import Path
import hashlib
import json
import struct
import zipfile
import xml.etree.ElementTree as ET
import numpy as np

ROOT = Path(__file__).resolve().parents[5]
HERE = Path(__file__).resolve().parent
ARTICLE = ROOT / 'hardware/printed-parts/drain-readiness/prints/2026-10-10-current-back-top-bridge50-mark1/2026-10-10-current-back-top-tree-bridge50-black-z018-mark1.3mf'
CURRENT = ROOT / 'hardware/printed-parts/enclosure/enclosure/enclosure-back-top.stl'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def article_mesh():
    ns = {'m': 'http://schemas.microsoft.com/3dmanufacturing/core/2015/02'}
    candidates = []
    with zipfile.ZipFile(ARTICLE) as archive:
        for name in archive.namelist():
            if not name.endswith('.model'):
                continue
            for mesh in ET.fromstring(archive.read(name)).findall('.//m:mesh', ns):
                vertices = np.array([[float(v.attrib[k]) for k in 'xyz']
                                     for v in mesh.find('m:vertices', ns)])
                faces = np.array([[int(t.attrib[k]) for k in ('v1', 'v2', 'v3')]
                                  for t in mesh.find('m:triangles', ns)])
                candidates.append((len(faces), name, vertices[faces]))
    _, name, triangles = max(candidates, key=lambda row: row[0])
    # The source object's axes are CAD axes, before the plate's printing pose.
    # Register the fixed outside planes, independently of the pocket being measured.
    lo, hi = triangles.reshape(-1, 3).min(0), triangles.reshape(-1, 3).max(0)
    offset = np.array([-(lo[0] + hi[0])/2, 471.3-hi[1], 355.0-hi[2]])
    return triangles + offset, {'member': name, 'offset_mm': offset.tolist(),
                                'raw_bounds_mm': [lo.tolist(), hi.tolist()]}


def stl_mesh():
    data = CURRENT.read_bytes()
    n = struct.unpack('<I', data[80:84])[0]
    record = np.dtype([('n', '<f4', 3), ('v', '<f4', (3,3)), ('a', '<u2')])
    return np.frombuffer(data, record, count=n, offset=84)['v'].astype(float)


def first_hit(triangles, origin, direction):
    v0, v1, v2 = triangles[:,0], triangles[:,1], triangles[:,2]
    e1, e2 = v1-v0, v2-v0
    p = np.cross(direction, e2)
    det = (e1*p).sum(1)
    valid = np.abs(det)>1e-12
    e1,e2,v0,p,det = (a[valid] for a in (e1,e2,v0,p,det))
    s = np.array(origin)-v0
    u = (s*p).sum(1)/det
    q = np.cross(s,e1)
    v = (q*np.array(direction)).sum(1)/det
    t = (e2*q).sum(1)/det
    hit = t[(u>=-1e-9)&(v>=-1e-9)&(u+v<=1+1e-9)&(t>1e-7)]
    return float(hit.min()) if len(hit) else None


def widths(triangles, y):
    origin = (66.9, y, 336.2105808375568)
    cardinal = [first_hit(triangles,origin,d) for d in
                ((1,0,0),(-1,0,0),(0,0,1),(0,0,-1))]
    return {'x_mm': cardinal[0]+cardinal[1], 'z_mm': cardinal[2]+cardinal[3],
            'half_spans_xplus_xminus_zplus_zminus_mm': cardinal}


def main():
    article, registration = article_mesh()
    current = stl_mesh()
    result = {'scope': 'Mesh dimensions at two C14 sections; excludes deposited bead error and hand fit.',
              'article': {'path': str(ARTICLE.relative_to(ROOT)), 'sha256': digest(ARTICLE),
                          'registration': registration,
                          'pocket_at_y460': widths(article,460),
                          'cord_bore_at_y469': widths(article,469)},
              'current': {'path': str(CURRENT.relative_to(ROOT)), 'sha256': digest(CURRENT),
                          'pocket_at_y460': widths(current,460),
                          'cord_bore_at_y469': widths(current,469)}}
    (HERE/'printed-c14-measurements.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))

if __name__ == '__main__':
    main()
