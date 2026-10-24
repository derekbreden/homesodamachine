"""Package the complete quadrant arrangement plus its empty access-panel zone."""
from pathlib import Path
import argparse
import base64
import gzip
import importlib.util
import json

import numpy as np

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('access_selected_study', HERE / 'study.py')
parent = importlib.util.module_from_spec(spec)
spec.loader.exec_module(parent)


def packed_mesh(path):
    with np.load(path) as mesh:
        positions = np.rint(mesh['v'] * 50).astype('<i2')
        triangles = mesh['f'].astype('<u4')
    return {'vc': len(positions), 'ic': int(triangles.size),
            'data': base64.b64encode(gzip.compress(positions.tobytes() + triangles.tobytes(), 9, mtime=0)).decode()}


def compact_meshes(data):
    """Lossless coordinate deltas and narrow indices; retain every vertex/face."""
    for mesh in data['geometries'].values():
        if mesh.get('alias'):continue
        raw=gzip.decompress(base64.b64decode(mesh['data']));offset=mesh['vc']*6
        positions=np.frombuffer(raw[:offset],dtype='<i2').reshape(-1,3).astype(np.int32)
        indices=np.frombuffer(raw[offset:],dtype='<u4')
        delta=np.diff(positions,axis=0,prepend=np.zeros((1,3),np.int32)).T
        if delta.min()>=-32768 and delta.max()<=32767:
            vertices=delta.astype('<i2').tobytes();mesh['position_encoding']='axis-delta'
        else:vertices=raw[:offset]
        mesh['index_bytes']=2 if indices.max()<65536 else 4
        triangles=indices.astype('<u2' if mesh['index_bytes']==2 else '<u4').tobytes()
        mesh['data']=base64.b64encode(gzip.compress(vertices+triangles,9,mtime=0)).decode()
    return data


def payload():
    geometry = parent.library()
    source = parent.parent.viewer_data(parent.pose(geometry), geometry)
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
        part['assembly'] = part.get('assembly') or dict(assignment.get(part.get('connection_owner', part['name']),
            {'quadrant': None, 'status': 'undecided', 'basis': 'Attachment is not assigned'}))
        if part['name'] in handoffs:
            part['assembly']['handoffs'] = handoffs[part['name']]
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


def detail_payload():
    plan=json.loads((HERE/'panel-plan.json').read_text());x,y=plan['fasteners']['centres_xy_mm'][2]
    roles={'section-frame':('support','Fixed boss · 3 mm blind floor'),
           'section-panel':('closure','9 mm panel · Ø6.2 × 3.2 mm counterbore'),
           'section-screw':('hardware-screw','M3 × 12 screw · 1.3 mm tip reserve'),
           'section-insert':('hardware-insert','RX-M3×5.7 heatset · full nominal engagement')}
    instances=[{'name':name,'geometry':name,'role':role,'label':label,
        'rotation':[[1,0,0],[0,1,0],[0,0,1]],'translation':[0,0,0],
        'assembly':{'quadrant':'electronics-access' if name in ('section-panel','section-screw') else 'back-top',
                    'status':'modelled','basis':label}}
        for name,(role,label) in roles.items()]
    return {'detail':True,'scene':{'instances':instances},'access_panel':plan,
        'detail_bounds':[[x-12,y,334.5],[x+12,y+12,356]],
        'quadrants':[{'id':'back-top','label':'Boss','series':3},{'id':'electronics-access','label':'Panel','series':5}],
        'geometries':{name:packed_mesh(HERE/'parts'/(name+'.npz')) for name in roles}}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('output', type=Path)
    parser.add_argument('--detail',action='store_true')
    args = parser.parse_args()
    data = compact_meshes(detail_payload() if args.detail else payload())
    packed = gzip.compress(json.dumps(data, separators=(',', ':')).encode(), 9, mtime=0)
    text = (HERE / 'viewer.html').read_text().replace('<!-- ARRANGEMENT_DATA -->',
        '<script id="qa-data" type="application/octet-stream">' + base64.b64encode(packed).decode() + '</script>')
    if args.detail:text=text.replace('electronics-access-arrangement','electronics-access-fastener-detail')
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(text)
    print(json.dumps({'output': str(args.output), 'bytes': len(text.encode()),
                      'arrangement_parts': len(data['scene']['instances']),
                      'equipment_carried_by_panel': []}))


if __name__ == '__main__':
    main()
