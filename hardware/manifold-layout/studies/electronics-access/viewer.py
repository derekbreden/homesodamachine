"""Package the complete quadrant arrangement plus its empty access-panel zone."""
from pathlib import Path
import argparse
import base64
import gzip
import importlib.util
import json

import numpy as np

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('access_parent_study', HERE.parent / 'funnel-gate/study.py')
parent = importlib.util.module_from_spec(spec)
spec.loader.exec_module(parent)


def packed_mesh(path):
    with np.load(path) as mesh:
        positions = np.rint(mesh['v'] * 50).astype('<i2')
        triangles = mesh['f'].astype('<u4')
    return {'vc': len(positions), 'ic': int(triangles.size),
            'data': base64.b64encode(gzip.compress(positions.tobytes() + triangles.tobytes(), 9, mtime=0)).decode()}


def payload():
    geometry = parent.library()
    source = parent.viewer_data(parent.pose(geometry), geometry)
    ownership = json.loads((HERE.parent / 'funnel-gate/assembly-ownership.json').read_text())
    data = {'scene': source['variants'][0], 'geometries': source['geometries'],
            'quadrants': ownership['quadrants']}
    assignment = {name: {key: group[key] for key in ('quadrant', 'status', 'basis')}
                  for group in ownership['groups'] for name in group['names']}
    handoffs = {}
    for link in ownership['boundary_handoffs']:
        for name in (link['carried_part'], link['other_part']):
            handoffs.setdefault(name, []).append(link['note'])
    plan = json.loads((HERE / 'panel-plan.json').read_text())
    data['quadrants'].append({'id': 'electronics-access', 'label': 'Empty access panel', 'series': 5})
    for part in data['scene']['instances']:
        part['assembly'] = dict(assignment.get(part.get('connection_owner', part['name']),
            {'quadrant': None, 'status': 'undecided', 'basis': 'Attachment is not assigned'}))
        if part['name'] in handoffs:
            part['assembly']['handoffs'] = handoffs[part['name']]
        part['latest_change'] = part['name'] == 'ceiling'
        if part['name'] == 'ceiling':
            part.update(geometry='access-fixed-ceiling', label='Fixed ceiling · electronics access opening')
            part['assembly'] = {'quadrant': 'back-top', 'status': 'proposed',
                                'basis': 'Ceiling and perimeter bearing seat remain with back-top'}
    data['scene']['instances'].append({
        'name': 'electronics-access-panel', 'geometry': 'electronics-access-panel',
        'rotation': [[1, 0, 0], [0, 1, 0], [0, 0, 1]], 'translation': [0, 0, 0],
        'kind': 'component', 'role': 'closure', 'latest_change': True,
        'label': 'Electronics access panel · installed last',
        'assembly': {'quadrant': 'electronics-access', 'status': 'proposed',
                     'basis': 'Plain closure only; no equipment, wire or tube is attached. Retention detail remains to design.'}})
    for name in ('access-fixed-ceiling', 'electronics-access-panel'):
        data['geometries'][name] = packed_mesh(HERE / 'parts' / (name + '.npz'))
    used = {part['geometry'] for part in data['scene']['instances']}
    for name in list(used):
        mesh = data['geometries'][name]
        while mesh.get('alias'):
            used.add(mesh['alias'])
            mesh = data['geometries'][mesh['alias']]
    data['geometries'] = {name: data['geometries'][name] for name in sorted(used)}
    data['access_panel'] = plan
    data['scene'].update(id='electronics-access', title='Empty last-on electronics access panel')
    return data


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    data = payload()
    packed = gzip.compress(json.dumps(data, separators=(',', ':')).encode(), 9, mtime=0)
    text = (HERE / 'viewer.html').read_text().replace('<!-- ARRANGEMENT_DATA -->',
        '<script id="qa-data" type="application/octet-stream">' + base64.b64encode(packed).decode() + '</script>')
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(text)
    print(json.dumps({'output': str(args.output), 'bytes': len(text.encode()),
                      'arrangement_parts': len(data['scene']['instances']),
                      'equipment_carried_by_panel': []}))


if __name__ == '__main__':
    main()
