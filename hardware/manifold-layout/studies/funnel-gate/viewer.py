"""Write the single-camera arrangement viewer with assembly highlight modes.

Run study.py first. This command only packages frozen viewer meshes and explicit
assembly ownership; it does not rebuild CAD or introduce an automatic check.
"""
from pathlib import Path
import argparse
import base64
import copy
import gzip
import json

HERE = Path(__file__).resolve().parent


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
    previous = json.loads((HERE.parent / 'east-feed/study.json').read_text())
    old = {part['name']: part for part in previous['instances']}
    for part in scene['instances']:
        part['assembly'] = copy.deepcopy(assignment.get(part.get('connection_owner', part['name']),
            {'quadrant': None, 'status': 'undecided', 'basis': 'Attachment is not assigned'}))
        if part['name'] in handoffs:
            part['assembly']['handoffs'] = handoffs[part['name']]
        former = old.get(part['name'])
        part['latest_change'] = former is None or any(
            part.get(key) != former.get(key) for key in ('geometry', 'rotation', 'translation'))
    used = {part['geometry'] for part in scene['instances']}
    geometries = source['geometries']
    for name in list(used):
        target = geometries[name]
        while target.get('alias'):
            used.add(target['alias'])
            target = geometries[target['alias']]
    return {'scene': scene, 'quadrants': ownership['quadrants'],
            'geometries': {name: geometries[name] for name in sorted(used)}}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    data = payload()
    packed = gzip.compress(json.dumps(data, separators=(',', ':')).encode(),
                           compresslevel=9, mtime=0)
    text = (HERE / 'viewer.html').read_text().replace('<!-- ARRANGEMENT_DATA -->',
        '<script id="qa-data" type="application/octet-stream">' +
        base64.b64encode(packed).decode() + '</script>')
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(text)
    print(json.dumps({'output': str(args.output), 'bytes': len(text.encode()),
                      'displayed_parts': len(data['scene']['instances']),
                      'unassigned': [part['name'] for part in data['scene']['instances']
                                     if not part['assembly']['quadrant']]}))


if __name__ == '__main__':
    main()
