"""Check the existing window covers against current CAD and front-top posts."""
from pathlib import Path
import hashlib, json, math, sys
import cadquery as cq
import numpy as np
import trimesh

ROOT = next(p for p in Path(__file__).resolve().parents if (p/'hardware/printed-parts/petgf.3mf').is_file())
JOB = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT/'hardware/printed-parts/enclosure/tee-carrier'))
import tee_carrier as tc
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
diff = lambda a,b: abs(a.cut(b).Volume()) + abs(b.cut(a).Volume())
spec = tc._spec()
parts = tc.covers(spec)
pointer = json.loads((ROOT/'hardware/cad-artifacts.json').read_text())['solids']
front_path = ROOT/'hardware/printed-parts/enclosure/enclosure/enclosure-front-top.step'
print('Reading current front-top STEP', flush=True)
front = cq.importers.importStep(str(front_path)).val()
records = []
for name, generated in parts.items():
    print('Checking', name, flush=True)
    source = ROOT/'hardware/printed-parts/enclosure/tee-carrier'/f'{name}.step'
    solid = cq.importers.importStep(str(source)).val()
    assert solid.isValid() and len(solid.Solids()) == 1
    equivalent = diff(solid, generated.val())
    assert equivalent < 1e-5, (name, equivalent)
    for p in (source, source.with_suffix('.stl'), source.with_suffix('.step.mesh')):
        assert sha(p) == pointer[str(p.relative_to(ROOT))], p
    mesh = trimesh.load_mesh(source.with_suffix('.stl'))
    assert mesh.is_watertight and mesh.is_winding_consistent and mesh.body_count == 1
    bb = solid.BoundingBox()
    bbox = np.array([[bb.xmin,bb.ymin,bb.zmin],[bb.xmax,bb.ymax,bb.zmax]])
    assert np.max(np.abs(mesh.bounds-bbox)) < .0001
    assert abs(mesh.volume-solid.Volume()) < .03
    # Crop to the complete insertion lane, then probe the retained post geometry.
    crop = cq.Solid.makeBox(bb.xlen+2,bb.ylen+2,bb.zlen+47,
                            cq.Vector(bb.xmin-1,bb.ymin-1,bb.zmin-1))
    nearby = front.intersect(crop)
    tongue_bottom = spec.slot_z[0] + tc.fits.clearance(at_floor=True)
    release_lift = float(math.ceil(spec.roof_z - tongue_bottom + tc.fits.slip))
    lane = []
    for lift in (0.,5.,15.,release_lift):
        volume = abs(nearby.intersect(solid.translate((0,0,lift))).Volume())
        assert volume < 1e-5, (name,lift,volume)
        lane.append({'lift_above_seat_mm':lift,'front_top_intersection_mm3':volume})
    # The top faces swept through the release stroke cover the continuous lane.
    sweep = solid
    for face in solid.Faces():
        if face.normalAt().z > .999:
            sweep = sweep.fuse(cq.Solid.extrudeLinear(face,cq.Vector(0,0,release_lift)))
    swept_intersection = abs(nearby.intersect(sweep).Volume())
    assert swept_intersection < 1e-5, (name,swept_intersection)
    records.append({'name':name,'step_sha256':sha(source),
                    'stl_sha256':sha(source.with_suffix('.stl')),
                    'source_to_step_symmetric_difference_mm3':equivalent,
                    'watertight_single_body':True,'stl_triangles':len(mesh.faces),
                    'cad_bounds_mm':bbox.tolist(),'front_top_insertion_probes':lane,
                    'release_lift_mm':release_lift,
                    'tongue_above_post_at_release_mm':tongue_bottom+release_lift-spec.roof_z,
                    'continuous_release_sweep_front_top_intersection_mm3':swept_intersection})
display_check = json.loads((ROOT/'.cache/prints/2026-09-24-display-cover-mark2-v5/geometry-check.json').read_text())
assert display_check['pass'] and display_check['bezel_window_thickness_and_outer_perimeter_unchanged']
for suffix in ('step','stl','step.mesh'):
    p = ROOT/'hardware/printed-parts/enclosure/display-cover'/('display-cover.'+suffix)
    assert sha(p) == pointer[str(p.relative_to(ROOT))]
result = {'pass':True,'parts':records,'front_top_step_sha256':sha(front_path),
          'display_cover_check':display_check,
          'window_cover_geometry_changed':False,
          'cover_to_seated_carrier_y_clearance_mm':spec.cover_y[0]-spec.plate_y[1],
          'post_width_mm':tc.POST_W,'slot_width_mm':tc.SLOT_W,
          'tongue_thickness_mm':tc.SLOT_W-tc.fits.slip,
          'tongue_floor_clearance_mm':tc.fits.clearance(at_floor=True),
          'assembly_order':'Lower covers onto front-top posts after V-G and V-J and before V-F and V-I.',
          'limitation':'CAD insertion probes do not measure printed fit or retention force.'}
(JOB/'geometry-check.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2),flush=True)
