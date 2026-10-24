"""A square-cut stock foam sleeve on the exposed vertical soda tube.

Manual study commands only. Export through the shared CAD queue. The optional
viewer overlays the sleeve on an explicitly supplied, already-issued scene.
"""
from pathlib import Path
import argparse
import base64
import copy
import gzip
import hashlib
import importlib.util
import json
import re
import numpy as np

HERE = Path(__file__).resolve().parent
PARTS = HERE / 'parts'
NAME = 'soda-rise-insulation'
XY = np.array([50., 354.3696])
Z0, Z1 = 264.5, 279.5
INSIDE_RADIUS = 3.175
OUTSIDE_RADIUS = 12.7
IDENTITY = np.eye(3).tolist()


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


def plan():
    return {
        'component': NAME,
        'stock': {'description': 'Owned CARGEN closed-cell nitrile pipe foam',
                  'source': 'hardware/ledger/purchases.md', 'asin': 'B0D2XFK337',
                  'nominal_id_mm': 2*INSIDE_RADIUS,
                  'nominal_wall_mm': OUTSIDE_RADIUS-INSIDE_RADIUS,
                  'nominal_od_mm': 2*OUTSIDE_RADIUS},
        'tube': 'soda-core-rise', 'center_xy_mm': XY.tolist(),
        'lower_z_mm': Z0, 'upper_z_mm': Z1, 'cut_length_mm': Z1-Z0,
        'installation': 'Two square end cuts; a straight longitudinal slit permits wrapping the sleeve around the tube with the pump installed. Close that slit with the existing foil tape. No shaped reliefs or extra mount.',
        'scope': 'Nominal uncompressed stock envelope. Only the middle of the exposed straight soda riser is insulated. Device bodies, fittings and tube end sections are bare. Main component and tube poses are fixed. Geometric fit does not establish thermal performance.'}


def export():
    import cadquery as cq
    shape = (cq.Workplane('XY').workplane(offset=Z0)
             .center(*XY).circle(OUTSIDE_RADIUS).circle(INSIDE_RADIUS)
             .extrude(Z1-Z0).val())
    PARTS.mkdir(exist_ok=True)
    path = PARTS/(NAME+'.step')
    cq.exporters.export(shape, str(path))
    verts, faces = shape.tessellate(.025, .08)
    verts = np.array([v.toTuple() for v in verts])
    faces = np.array(faces, dtype=np.int32)
    np.savez_compressed(PARTS/(NAME+'.npz'), v=verts, f=faces)
    record = {**plan(), 'valid': shape.isValid(), 'solids': len(shape.Solids()),
              'bounds_mm': [verts.min(0).tolist(), verts.max(0).tolist()],
              'volume_mm3': shape.Volume(),
              'producer_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              'step_sha256': hashlib.sha256(path.read_bytes()).hexdigest()}
    (PARTS/(NAME+'.json')).write_text(json.dumps(record, indent=2)+'\n')
    print(json.dumps(record), flush=True)


def display_mesh():
    """Analytic annulus display sampling; no CAD worker is needed."""
    tube = load('soda_insulation_tube_mesh', HERE.parent/'co2-grid/study.py').tube
    v, f = tube([[*XY,Z0],[*XY,Z1]], OUTSIDE_RADIUS, INSIDE_RADIUS, sections=192)
    PARTS.mkdir(exist_ok=True)
    np.savez_compressed(PARTS/(NAME+'.npz'), v=v, f=f)
    print(json.dumps({'mesh': str(PARTS/(NAME+'.npz')), 'vertices':len(v), 'triangles':len(f)}))


def check():
    import fcl
    study = load('soda_insulation_study', HERE/'study.py')
    library = study.library()
    scene = study.pose(library)
    world = study.base.world_meshes(scene, library)
    with np.load(PARTS/(NAME+'.npz')) as mesh:
        sleeve_mesh = mesh['v'], mesh['f']
    def obj(mesh):
        v, f = mesh
        model=fcl.BVHModel(); model.beginModel(len(v),len(f))
        model.addSubModel(v, f.astype(np.int32)); model.endModel()
        return fcl.CollisionObject(model)
    sleeve = obj(sleeve_mesh)
    gaps = {}; hits = []
    for name, mesh in world.items():
        if name in ('soda-core-rise', NAME):
            continue  # Intended foam/tube bore contact.
        other = obj(mesh)
        gaps[name] = float(fcl.distance(sleeve, other, fcl.DistanceRequest(), fcl.DistanceResult()))
        if fcl.collide(sleeve, other, fcl.CollisionRequest(), fcl.CollisionResult()):
            hits.append(name)
    soda = study.soda_route.route()
    tube0 = np.array(soda['upstream_handoff']['core_carb_water_out_mm'])
    tube1 = np.array(soda['tubes']['soda-core-rise'][-2])
    record = {**plan(), 'exposed_tube_length_mm': float(tube1[2]-tube0[2]),
              'bare_lower_length_mm': float(Z0-tube0[2]),
              'bare_upper_length_mm': float(tube1[2]-Z1),
              'hard_contact_parts': hits,
              'nearest_parts_mm': sorted(gaps.items(), key=lambda row: row[1])[:12],
              'clearance_to_plain_core_roof_mm': float(Z0-tube0[2]),
              'passed': bool(not hits and Z0>=tube0[2] and Z1<=tube1[2]),
              'query_scope': 'Full native sleeve display mesh against the isolated arrangement exterior meshes; intended sleeve/tube bore contact excluded. Production mounts and complete wiring are separate.'}
    (HERE/'tube-insulation-review.json').write_text(json.dumps(record, indent=2)+'\n')
    print(json.dumps(record), flush=True)


def viewer(baseline, output):
    packer = load('soda_insulation_viewer', HERE/'viewer.py')
    source = baseline.read_text()
    encoded = re.search(r'<script id="qa-data"[^>]*>(.*?)</script>', source, re.S).group(1)
    data = json.loads(gzip.decompress(base64.b85decode(encoded)))
    # The issued camera, walls and every existing instance/mesh remain frozen.
    old_instances = copy.deepcopy(data['scene']['instances'])
    for part in data['scene']['instances']:
        part['latest_change'] = False
    with np.load(PARTS/(NAME+'.npz')) as mesh:
        v, f = mesh['v'], mesh['f']
    study = load('soda_insulation_mesh_packer', HERE/'study.py')
    new = study.base.pack(v, f, 12000)
    data['geometries'][NAME] = packer.compact_meshes({'geometries': {NAME: new}})['geometries'][NAME]
    data['scene']['instances'].append({
        'name': NAME, 'geometry': NAME, 'rotation': IDENTITY, 'translation': [0.,0.,0.],
        'role': 'insulation', 'kind': 'component', 'latest_change': True,
        'label': 'Soda riser · 15 mm square-cut stock foam sleeve · 9.525 mm nominal wall',
        'assembly': {'quadrant': 'back-bottom', 'status': 'located',
                     'basis': 'Wraps the core-mounted vertical soda tube. Main component and tube poses are fixed.'}})
    template = (HERE/'viewer.html').read_text()
    theme_path = HERE.parents[3]/'tools/viz/inline-mobile/assets/theme.js'
    template = template.replace('// INLINE_MOBILE_THEME', theme_path.read_text())
    template = template.replace('id="quadrant-arrangement"', 'id="tube-insulation-arrangement"')
    template = template.replace('#quadrant-arrangement', '#tube-insulation-arrangement')
    template = template.replace("getElementById('quadrant-arrangement')", "getElementById('tube-insulation-arrangement')")
    template = template.replace('quadrant-arrangement-v1', 'tube-insulation-arrangement-v1')
    template = template.replace('<option value="quadrant" selected>', '<option value="quadrant">')
    template = template.replace('<option value="changes">', '<option value="changes" selected>')
    template = template.replace("function build(){", "function build(){\n  pin('15 mm foam sleeve',[50,354.3696,272]);")
    template = template.replace("pin('Core soda',[50,354.3696,253.4]);", '')
    template = template.replace("'gas-check':2,electronics:5", "'gas-check':2,insulation:2,electronics:5")
    template = template.replace("{label:'Electronics',token:'viz-series-5'}]", "{label:'Electronics',token:'viz-series-5'},{label:'Insulation',token:'viz-series-2'}]")
    template = re.sub(r'(<div id="qa-stage" role="img" aria-label=")[^"]*(")',
        r'\1Rotatable clean above-core arrangement with a 15 mm square-cut stock foam sleeve on the vertical soda tube. Existing components, walls and tube routes retain their displayed positions. Device bodies and tube ends remain bare. Latest changes highlights only the sleeve.\2', template)
    packed = base64.b85encode(gzip.compress(json.dumps(data,separators=(',',':')).encode(),9,mtime=0)).decode()
    template = template.replace('<!-- ARRANGEMENT_DATA -->', '<script id="qa-data" type="application/octet-stream">'+packed+'</script>')
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(template)
    assert [{k:v for k,v in p.items() if k!='latest_change'} for p in data['scene']['instances'][:-1]] == [{k:v for k,v in p.items() if k!='latest_change'} for p in old_instances]
    print(json.dumps({'output': str(output), 'bytes': len(template.encode()),
                      'existing_parts_unchanged': len(old_instances), 'added_parts': [NAME]}))


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--export',action='store_true')
    parser.add_argument('--mesh',action='store_true')
    parser.add_argument('--check',action='store_true')
    parser.add_argument('--baseline',type=Path)
    parser.add_argument('--viewer',type=Path)
    args=parser.parse_args()
    if args.export: export()
    if args.mesh: display_mesh()
    if args.check: check()
    if args.viewer:
        if not args.baseline: parser.error('--viewer requires the issued --baseline fragment')
        viewer(args.baseline,args.viewer)


if __name__=='__main__':
    main()
