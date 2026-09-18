"""Exact Industrial cover fit, stock, loading and sampled seating readings.

Run with tools/cad-venv/bin/python. The report lives beside the cover source;
transient meshes and phase readings use a temporary directory.
"""
from pathlib import Path
import ast
import inspect
import json
import sys
import tempfile
import types
ROOT = next((parent for parent in Path(__file__).resolve().parents if (parent / 'tools' / 'cad-venv').is_dir()))
for directory in (ROOT / 'hardware/scripts', ROOT / 'hardware/faucet-layout', Path(__file__).resolve().parent):
    sys.path.insert(0, str(directory))
import cadquery as cq
import industrial_display_cover as industrial
import faucet_assembly as assembly
import check_faucet_geometry as check

def run(out):
    OUT = out
    f = industrial.shell
    source_paths = (Path(__file__).resolve(), Path(check.__file__), Path(assembly.__file__), Path(industrial.__file__), Path(f.__file__), ROOT / 'hardware/printed-parts/faucet/_faucet_interface.py', ROOT / 'hardware/printed-parts/faucet/_display_snap.py', ROOT / 'hardware/reference/touch-flo-faucet/display-reference/component-envelopes.json', ROOT / 'hardware/printed-parts/cadlib/fits.py', ROOT / 'hardware/printed-parts/cadlib/world_workplane.py')
    before = check.hashes(source_paths)
    read = check.Reading()
    seated = industrial.build_seated_display_cover().val()
    free = industrial.build_display_cover().val()
    origin, along, normal = f._tip_frame()
    frame = cq.Location(cq.Plane(origin=origin, xDir=(1, 0, 0), normal=normal))
    parts = {name: cq.importers.importStep(str(check.SHELL / f'faucet-shell-{key}.step')).val() for name, key in [('shell_base', 'base'), ('shell_tip', 'tip')]}
    parts['display_cover'] = seated
    body = assembly.build_display_body().val()
    screen = assembly.build_display_screen().val()
    ribbon = assembly.build_display_ribbon()
    tubes = {'soda-tube': assembly.build_soda_faucet_tube(), 'flavor-a': assembly.build_flavor_tube(1), 'flavor-b': assembly.build_flavor_tube(-1)}
    fp = types.SimpleNamespace(**vars(f))
    fp.build_display_outer_envelope = industrial.build_plate_outer
    fp.build_display_cover_lips = industrial.build_display_cover_lips
    fp.display_head_s_max = industrial.display_head_s_max
    for name, part in [('seated', seated), ('relaxed', free)]:
        read.add(f'solid:cover-{name}', part.isValid() and len(part.Solids()) == 1, valid=part.isValid(), solids=len(part.Solids()), volume_mm3=part.Volume())
        for key, hardware in [('display', body), ('glass', screen), ('ribbon', ribbon), *tubes.items()]:
            check.clearance_reading(read, f'clearance:{name}-{key}', part, hardware, 0.1 if key in ('display', 'ribbon') else 0.0)
    print('Static Industrial solids and hardware readings complete', flush=True)
    source = inspect.getsource(check.display_retention_reading)
    assert source.count('if face.geomType() != "PLANE"]') == 1
    source = source.replace('if face.geomType() != "PLANE"]', 'if face.geomType() == "PLANE" and abs(face.normalAt().x) > 0.999999]')
    source = source.replace('radial_stock >= 1.0-DISTANCE_TOLERANCE', 'radial_stock >= f.wall_thickness_min-DISTANCE_TOLERANCE')
    source = source.replace('required_radial_stock_mm=1.0', 'required_radial_stock_mm=f.wall_thickness_min')
    source = source.replace('complete curved-side separation', 'complete separation from the planar exterior flanks')
    tree = ast.parse(source)

    class Stations(ast.NodeTransformer):

        def visit_Assign(self, node):
            if any((isinstance(target, ast.Name) and target.id == 'lifts' for target in node.targets)):
                node.value = ast.parse('[0.0, 0.10, 0.15, 0.16, 0.35, 1.0, 3.0, 5.0, f.display_cartridge_lift_n]', mode='eval').body
            return self.generic_visit(node)
    namespace = dict(vars(check))
    exec(compile(ast.fix_missing_locations(Stations().visit(tree)), str(__file__), 'exec'), namespace)
    namespace['display_retention_reading'](read, fp, parts, body, screen, ribbon, tubes, free, industrial)
    (OUT / 'after-retention.json').write_text(json.dumps(read.rows, indent=2) + '\n')
    check.display_loading_reading(read, fp, industrial, body, screen, free)
    check.display_cartridge_axial_reading(read, fp, parts, seated, free, body, screen, tubes)
    check.display_rear_closure_reading(read, fp, parts['shell_tip'], seated, body)
    stock = []
    for name, part in [('seated', seated), ('relaxed', free)]:
        native = part.moved(frame.inverse)
        for side in (-1, 1):
            for s in (0.1, 1.0, 2.1, 5.0, 10.0, 15.0, 25.0, 35.0, 40.0, 47.0, 48.0, 49.65):
                for n in (3.31, 3.75, 6.29, 6.46, 8.0, 10.1, 15.45, 18.0, 20.54, 21.0):
                    shift = industrial.preload_inward_at(n) if name == 'relaxed' else 0.0
                    x = side * (industrial.DIMENSIONS.width / 2 - shift)
                    slope = side * f._display_snap.X_PRELOAD / (industrial.bezel_n_bottom - f.display_clip_top_n) if name == 'relaxed' and n < industrial.bezel_n_bottom else 0.0
                    inward = cq.Vector(-side, 0.0, side * slope).normalized()
                    start = cq.Vector(x, s, n) + inward.multiply(check.DISTANCE_TOLERANCE)
                    spans = check.line_intervals(native, start.toTuple(), inward.toTuple(), 5.0)
                    thickness = spans[0][1] + check.DISTANCE_TOLERANCE if spans and spans[0][0] < 0.001 else 0.0
                    stock.append({'shape': name, 'side': side, 's_mm': s, 'n_mm': n, 'normal_stock_mm': check.clean_number(thickness)})
    minimum = min((x['normal_stock_mm'] for x in stock))
    read.add('wall:industrial-flanks', minimum >= 1.0 - check.DISTANCE_TOLERANCE, minimum_sampled_normal_stock_mm=minimum, required_mm=1.0, samples=stock, method='exact B-rep chords normal to the complete rectangular flank faces and their affine relaxed images', scope='480 named flank sections; the bezel and end walls have separate complete witnesses')
    local_seated = seated.moved(frame.inverse)
    local_free = free.moved(frame.inverse)
    upper = cq.Solid.makeBox(100.0, 150.0, 50.0, cq.Vector(-50.0, -50.0, industrial.bezel_n_bottom))
    bezel = local_seated.intersect(upper)
    delta = check.outside_material_volume(bezel, local_free) + check.outside_material_volume(local_free.intersect(upper), bezel)
    read.add('shape:industrial-bezel', delta <= check.VOLUME_TOLERANCE and industrial.bezel_thickness >= 1.0 - check.DISTANCE_TOLERANCE, unchanged_bezel_symmetric_difference_mm3=check.clean_number(delta), bezel_thickness_mm=industrial.bezel_thickness, window_mm=[industrial.window_x, industrial.window_s], show_face_count=industrial.show_face(cq.Workplane(obj=free))[0])
    ends = []
    for name, native in [('seated', local_seated), ('relaxed', local_free)]:
        for end, outer_s, inner_s in [('front', 0.0, industrial.DIMENSIONS.front_wall), ('rear', industrial.DIMENSIONS.length, industrial.DIMENSIONS.length - industrial.DIMENSIONS.rear_wall)]:
            planes = []
            for s in (outer_s, inner_s):
                matches = [face for face in native.Faces() if face.geomType() == 'PLANE' and abs(abs(face.normalAt().y) - 1.0) < 1e-06 and (abs(face.Center().y - s) < 1e-06)]
                planes.append(cq.Compound.makeCompound(matches))
            gap = planes[0].distance(planes[1])
            ends.append({'shape': name, 'end': end, 'surface_gap_mm': check.clean_number(gap), 'required_mm': abs(outer_s - inner_s)})
    read.add('wall:industrial-end-walls', all((row['surface_gap_mm'] >= row['required_mm'] - check.DISTANCE_TOLERANCE for row in ends)), samples=ends, method='complete parallel outer/inner end-face distances on both actual solids; X preforming preserves every S coordinate', scope='the remaining front and rear slabs and their neck-opening rims; no cuff')
    import trimesh
    stl = OUT / 'industrial-display-cover.stl'
    mesh = f.piece_mesh(cq.Workplane(obj=free))
    mesh.export(stl)
    loaded = trimesh.load_mesh(stl, process=True)
    read.add('mesh:industrial-cover', loaded.is_watertight and loaded.is_winding_consistent and (len(loaded.split()) == 1), triangles=len(loaded.faces), watertight=loaded.is_watertight, consistent_winding=loaded.is_winding_consistent, bodies=len(loaded.split()), sha256=check.digest(stl), tolerance_mm=0.005, tolerance_is_relative=False, angular_tolerance_rad=0.05)
    assert before == check.hashes(source_paths), 'Source changed during readings'
    report = {'passed': all((row['passed'] for row in read.rows.values())), 'geometry_source_sha256': before, 'checks': read.rows, 'dimensions': vars(industrial.DIMENSIONS), 'reference_artifact_sha256': {str(check.SHELL / f'faucet-shell-{name}.step'): check.digest(check.SHELL / f'faucet-shell-{name}.step') for name in ('base', 'tip')}, 'validation_script_sha256': check.digest(Path(__file__)), 'scope': 'Industrial cover only against the shared exact tip, device and tubing. Nine explicit normal stations measure geometric outward demand; whole-volume loading and axial cylinder bounds cover their complete strokes. The shared lower base is outside the display motion region. Material behavior, insertion force and retention require the complete Industrial print trial.'}
    (OUT / 'display-cover-check.json').write_text(json.dumps(report, indent=2) + '\n')
    if report['passed']:
        target = ROOT / 'hardware/printed-parts/faucet/industrial/display-cover-check.json'
        target.write_text(json.dumps(report, indent=2) + '\n')
    print('Industrial cover', report['passed'], len(read.rows), 'readings', flush=True)
    print('Failures', [key for key, row in read.rows.items() if not row['passed']], flush=True)
    return int(not report['passed'])
if __name__ == '__main__':
    with tempfile.TemporaryDirectory(prefix='industrial-display-cover-') as temporary:
        sys.exit(run(Path(temporary)))
