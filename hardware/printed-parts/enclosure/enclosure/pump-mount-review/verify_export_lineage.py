"""Manual lightweight viewer-source and shown pump-fastener identity reading."""
from pathlib import Path
import argparse
import hashlib
import json
import struct

HERE=Path(__file__).resolve().parent
ROOT=next(path for path in HERE.parents if (path/'hardware/scripts').is_dir())


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def payload(path):
    with path.open('rb') as source:
        size=struct.unpack('<I',source.read(4))[0]
        return json.loads(source.read(size))


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--reading',type=Path,default=HERE/'native-review.json')
    parser.add_argument('--extraction',type=Path,default=HERE/'final-native-extraction.json')
    args=parser.parse_args()
    prior_sha=sha(args.reading)
    reading=json.loads(args.reading.read_text())
    extraction=json.loads(args.extraction.read_text())
    agreement=reading['current_hardware_agreements'][-1]
    if agreement['final_subset_sha256']!=extraction['subset']['sha256']:
        raise RuntimeError('Named-body agreement uses another extracted subset')
    aggregate=ROOT/'hardware/manifold-layout/enclosure-assembly.step'
    top=HERE.parent/'enclosure-front-top.step'
    viewer_rows=[]
    for step in (aggregate,top):
        viewer=step.with_suffix(step.suffix+'.mesh')
        header=payload(viewer)
        identity=sha(step)
        if header['src']!=identity:
            raise RuntimeError(f'Viewer names another native export: {viewer}')
        viewer_rows.append(dict(step=str(step.relative_to(ROOT)),native_sha256=identity,
            viewer=str(viewer.relative_to(ROOT)),viewer_sha256=sha(viewer),viewer_source_sha256=header['src']))
    if extraction['source']['sha256']!=viewer_rows[0]['native_sha256']:
        raise RuntimeError('Extraction and viewer bind different full-appliance exports')
    expected={f'pump-retainer-{label}-{kind}' for label in ('left','centre','right')
              for kind in ('screw','insert')}
    aggregate_names={mesh['name'] for mesh in payload(aggregate.with_suffix('.step.mesh'))['meshes']}
    if not expected<=aggregate_names:
        raise RuntimeError('Full-appliance viewer omits pump-retainer hardware')
    glb=ROOT/'hardware/assembly/scenes/glb/pump-mount.glb'
    with glb.open('rb') as source:
        source.seek(12)
        size,kind=struct.unpack('<II',source.read(8))
        if kind!=0x4E4F534A:raise RuntimeError('GLB JSON chunk is absent')
        scene=json.loads(source.read(size))
    nodes={node['name']:node for node in scene['nodes'] if 'name'in node}
    common_matrix=nodes['enclosure-front-top'].get('matrix')
    fasteners={label:station for label,station in zip(('left','centre','right'),reading['fasteners'])}
    rows=[]
    for name in sorted(expected):
        node=nodes[name]
        accessor=scene['accessors'][scene['meshes'][node['mesh']]['primitives'][0]['attributes']['POSITION']]
        low,high=accessor['min'],accessor['max']
        station=fasteners[name.split('-')[2]]
        kind=name.rsplit('-',1)[1]
        wanted_z=(station['insert_mouth_z'],station['insert_top_z']) if kind=='insert' else (
            station['retainer_bottom_z'],station['screw_tip_z'])
        error=max(abs((low[0]+high[0])/2.-station['x']),
            abs((low[1]+high[1])/2.-station['y']),abs(low[2]-wanted_z[0]),abs(high[2]-wanted_z[1]))
        if error>1e-4 or node.get('matrix')!=common_matrix:
            raise RuntimeError(f'Installation mesh hardware station differs: {name}, error={error}')
        rows.append(dict(name=name,native_mesh_bounds_mm=[low,high],maximum_station_error_mm=error))
    result=dict(scope='Exact native/viewer source headers and frozen actual-appliance extraction '
        'agree. The full-appliance viewer contains six pump-retainer fasteners; the installation '
        'GLB shows all six at their recorded native stations under the same view transform '
        'as front-top. This checks visual identity and placement, not physical assembly.',
        verification_source_sha256=sha(Path(__file__)),prior_reading_sha256=prior_sha,
        extraction=dict(path=str(args.extraction.relative_to(ROOT)),sha256=sha(args.extraction)),
        viewers=viewer_rows,installation_glb=dict(path=str(glb.relative_to(ROOT)),sha256=sha(glb)),
        installation_hardware=rows,status='pass')
    previous=reading.get('current_export_lineage')
    if previous is not None:
        reading.setdefault('prior_export_lineages',[]).append(previous)
    reading['current_export_lineage']=result
    args.reading.write_text(json.dumps(reading,indent=2)+'\n')
    print(json.dumps(result,indent=2))


if __name__=='__main__':main()
