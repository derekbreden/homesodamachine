"""Write the single-camera arrangement viewer with assembly highlight modes.

Run study.py first. This command only packages frozen viewer meshes and explicit
assembly ownership; it does not rebuild CAD or introduce an automatic check.
"""
from pathlib import Path
import argparse
import base64
import copy
import gzip
import hashlib
import json
import struct

HERE = Path(__file__).resolve().parent


def geometry_signature(part, geometries):
    mesh = geometries[part['geometry']]
    while 'alias' in mesh:
        mesh = geometries[mesh['alias']]
    pose = [[round(float(value), 7) for value in row] for row in part['rotation']]
    translation = [round(float(value), 7) for value in part['translation']]
    digest = hashlib.sha256(gzip.decompress(base64.b64decode(mesh['data'])))
    digest.update(json.dumps([mesh['vc'], mesh['ic'], pose, translation],
        separators=(',', ':')).encode())
    return digest.hexdigest()


def payload():
    source = json.loads((HERE / 'out/viewer-data.json').read_text())
    scene = copy.deepcopy(source['variants'][0])
    ownership = json.loads((HERE / 'assembly-ownership.json').read_text())
    assignment = {name: {key: group[key] for key in ('quadrant', 'status', 'basis')}
                  for group in ownership['groups'] for name in group['names']}
    handoffs = {}
    for link in ownership['boundary_handoffs']:
        for name in (link['carried_part'], link['other_part']):
            handoffs.setdefault(name, []).append(link['note'])
    old = json.loads((HERE / 'highlight-baseline.json').read_text())['parts']
    for part in scene['instances']:
        part['assembly'] = copy.deepcopy(assignment.get(part.get('connection_owner', part['name']),
            {'quadrant': None, 'status': 'undecided', 'basis': 'Attachment is not assigned'}))
        if part['name'] in handoffs:
            part['assembly']['handoffs'] = handoffs[part['name']]
        part['latest_change'] = old.get(part['name']) != geometry_signature(part, source['geometries'])
    used = {part['geometry'] for part in scene['instances']}
    geometries = source['geometries']
    for name in list(used):
        target = geometries[name]
        while target.get('alias'):
            used.add(target['alias'])
            target = geometries[target['alias']]
    return {'scene': scene, 'quadrants': ownership['quadrants'],
            'geometries': {name: geometries[name] for name in sorted(used)}}


def compact_meshes(data):
    """Lossless display-mesh encoding; retain every coordinate and triangle."""
    for mesh in data['geometries'].values():
        if mesh.get('alias'):
            continue
        raw = gzip.decompress(base64.b64decode(mesh['data']))
        offset = mesh['vc'] * 6
        positions = [row[0] for row in struct.iter_unpack('<h', raw[:offset])]
        delta = [positions[i] - (positions[i - 3] if i >= 3 else 0)
                 for axis in range(3) for i in range(axis, len(positions), 3)]
        vertices = raw[:offset]
        if min(delta) >= -32768 and max(delta) <= 32767:
            vertices = struct.pack(f'<{len(delta)}h', *delta)
            mesh['position_encoding'] = 'axis-delta'
        indices = [row[0] for row in struct.iter_unpack('<I', raw[offset:])]
        mesh['index_bytes'] = 2 if max(indices) < 65536 else 4
        triangles = (struct.pack(f'<{len(indices)}H', *indices)
                     if mesh['index_bytes'] == 2 else raw[offset:])
        mesh['data'] = base64.b64encode(gzip.compress(vertices + triangles, 9, mtime=0)).decode()
    return data


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    data = compact_meshes(payload())
    packed = gzip.compress(json.dumps(data, separators=(',', ':')).encode(),
                           compresslevel=9, mtime=0)
    text = (HERE / 'viewer.html').read_text().replace('<!-- ARRANGEMENT_DATA -->',
        '<script id="qa-data" type="application/octet-stream">' +
        base64.b85encode(packed).decode() + '</script>')
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(text)
    print(json.dumps({'output': str(args.output), 'bytes': len(text.encode()),
                      'displayed_parts': len(data['scene']['instances']),
                      'unassigned': [part['name'] for part in data['scene']['instances']
                                     if not part['assembly']['quadrant']]}))


if __name__ == '__main__':
    main()
