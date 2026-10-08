"""Read the DATA frame against the saved production rear wall and purchased jack."""
from pathlib import Path
import hashlib
import json
import sys

HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p / 'hardware').is_dir())
for path in (ROOT / 'hardware/scripts', ROOT / 'hardware/manifold-layout',
             HERE, HERE.parent / 'enclosure'):
    sys.path.insert(0, str(path))
from _run_lock import acquire
acquire(str(Path(__file__).resolve()))
import cadquery as cq
import data_ring as data
import _data_wing_interface as fit
import enclosure as enc


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def volume(shape):
    return sum(s.Volume() for s in shape.Solids())


def main():
    paths = (Path(__file__).resolve(), Path(data.__file__), Path(fit.__file__), Path(enc.__file__),
             ROOT / 'hardware/manifold-layout/enclosure_assembly.py',
             ROOT / 'hardware/manifold-layout/enclosure-assembly.facts.json',
             HERE.parent / 'enclosure/enclosure-back-top.step',
             HERE / 'data-ring.step',
             ROOT / 'hardware/reference/riteav-keystone/riteav-keystone.step',
             ROOT / 'hardware/reference/jg-bulkhead-union/jg-bulkhead-union.step')
    paths += (Path(fit.nameplate.__file__), Path(fit.nameplate.dimensions.__file__))
    before = {str(p.relative_to(ROOT)): sha(p) for p in paths}
    facts = json.loads(paths[5].read_text())
    station = tuple(facts['constants']['KEYSTONE_STATION'])
    outer, inner = tuple(facts['box']['outer']), tuple(facts['box']['inner'])
    y_outer = outer[3]
    shift = (station[0], y_outer - fit.POCKET_DEPTH, station[1])
    wall = cq.importers.importStep(str(paths[6])).val()
    body, word = data.build_ring(), data.build_word()
    placed = body.translate(shift)
    jack = cq.importers.importStep(str(paths[8])).val().translate(shift)
    checks = {}

    def add(name, passed, **values):
        checks[name] = dict(passed=bool(passed), **values)
        print(('PASS ' if passed else 'FAIL ') + name, flush=True)

    add('frame:one-valid-solid', body.isValid() and len(body.Solids()) == 1)
    add('word:four-valid-letters', word.isValid() and len(word.Solids()) == 4)
    add('print:flat-back', abs(body.BoundingBox().ymin) < 1e-7)
    for name, a, b in (('word-frame', body, word), ('frame-wall', placed, wall),
                       ('jack-wall', jack, wall), ('jack-frame', jack, placed)):
        common = volume(a.intersect(b))
        add('clearance:' + name, common <= 1e-7, overlap_mm3=common)

    # Read the complete broad wing bearing lands in the production wall.
    lips = []
    for side in (-1, 1):
        lo, hi = sorted((side*(fit.WIDTH/2+fit.FACE_AIR+fit.ENTRY_WIDTH),
                         side*(fit.WIDTH/2+fit.PROJECTION)))
        witness = fit.box(lo, hi, fit.WING_THICK+fit.THICKNESS_AIR,
                          fit.POCKET_DEPTH, fit.CENTER_Z-fit.WING_SPAN/2, fit.CENTER_Z+fit.WING_SPAN/2).translate(shift)
        missing = volume(witness.cut(wall))
        lips.append(dict(side=side, required_volume_mm3=volume(witness),
                         missing_mm3=missing,
                         thickness_mm=fit.POCKET_DEPTH-fit.WING_THICK-fit.THICKNESS_AIR))
        add('stock:retaining-lip:' + str(side), missing <= 1e-7, **lips[-1])

    # Check the saved native frame against the continuous face and shared
    # nameplate wings, including its exact DATA/DRAIN Z envelope.
    native = cq.importers.importStep(str(paths[7])).val()
    native_body = next(s for s in native.Solids() if s.BoundingBox().ymin < 1e-6)
    expected = fit.port_chip.outline(fit.WIDTH,fit.TOP,fit.BOTTOM,fit.THICK)
    wings = [w.translate((0,0,fit.CENTER_Z)) for w in
             fit.nameplate.wings(width=fit.WIDTH,span=fit.WING_SPAN)]
    expected = expected.fuse(*wings).cut(fit.aperture(-.01,fit.THICK+.01)).cut(word)
    mismatch = volume(native_body.cut(expected))+volume(expected.cut(native_body))
    bb = native_body.BoundingBox()
    add('construction:shared-nameplate-wings-and-continuous-face', mismatch <= 1e-7,
        symmetric_difference_mm3=mismatch, face_width_mm=fit.WIDTH,
        height_mm=bb.zlen, body_and_wing_depth_mm=bb.ylen,
        wing_projection_mm=fit.PROJECTION, wing_span_mm=fit.WING_SPAN,
        outside_corner_radius_mm=fit.CORNER_R)
    pushed = placed.translate((0,fit.THICKNESS_AIR+.1,0))
    add('retention:complete-wings-meet-wall', volume(pushed.intersect(wall)) > 1,
        outward_motion_mm=fit.THICKNESS_AIR+.1,
        interference_mm3=volume(pushed.intersect(wall)))

    # Read the complete finite native surfaces behind the mesh-lint picks.
    for name, point, normal, thickness in (
        ('upper-pad-remainder', (station[0],shift[1]-fit.FLOOR_STOCK,station[1]+17.117), (0,-1,0),2.0),
        ('lower-mouth-floor', (station[0],shift[1]+fit.POCKET_DEPTH/2,
                               station[1]-fit.BOTTOM-fit.FACE_AIR-fit.SUPPORTED_AIR), (0,0,1),1.5),
    ):
        near=[]
        for index, face in enumerate(wall.Faces()):
            if face.geomType()!='PLANE' or face.normalAt().dot(cq.Vector(*normal))<.999999:
                continue
            if face.distance(cq.Vertex.makeVertex(*point))<.002:near.append((index,face))
        if len(near)!=1:raise ValueError(f'Expected one finite DATA {name} face; found {len(near)}')
        index,face=near[0]
        witness=cq.Solid.extrudeLinear(face.outerWire(),face.innerWires(),face.normalAt().multiply(-thickness))
        missing=witness.cut(wall);missing_volume=volume(missing)
        add('stock:finite-'+name,face.isValid() and witness.isValid() and missing.isValid()
            and volume(witness)>0 and abs(missing_volume)<=1e-7,
            native_face=index,face_area_mm2=face.Area(),stock_thickness_mm=thickness,
            witness_volume_mm3=volume(witness),missing_volume_mm3=missing_volume)

    drain_bounds=facts['bodies']['bulkhead-ring-drain']
    frame_bounds=facts['bodies']['data-ring']
    add('layout:DATA-and-DRAIN-identical-Z',
        abs(frame_bounds[2]-drain_bounds[2])<1e-6 and
        abs(frame_bounds[5]-drain_bounds[5])<1e-6,
        data_z_bounds_mm=[frame_bounds[2],frame_bounds[5]],
        drain_z_bounds_mm=[drain_bounds[2],drain_bounds[5]])

    # This reference envelope includes the RJ11 plug body and its lower latch.
    # It establishes the trim's approach space, not a connector insertion force.
    port_z = station[1] - 1.0
    plug = fit.box(station[0]-4.5, station[0]+4.5, shift[1]-6.2, y_outer+22,
                   port_z-3.225, port_z+3.225)
    latch = fit.box(station[0]-1.7, station[0]+1.7, shift[1], y_outer+18,
                    port_z-5.575, port_z-3.225)
    envelope = plug.fuse(latch)
    common = volume(envelope.intersect(placed))
    add('access:plug-and-latch-through-trim', common <= 1e-7, overlap_mm3=common,
        plug_width_mm=9.0, plug_height_mm=6.45, lower_latch_depth_mm=2.35)

    # Read the complete fixed receptacle independently of the decorative pocket.
    feature, cutter, catches = enc._keystone_receptacle_geometry(
        inner, outer, station, station[1]-60, station[1]+60, -1)
    receiver = feature.cut(cutter).fuse(catches)
    for name in ('bulkhead-carb', 'bulkhead-flavor-a'):
        bbox = facts['bodies'][name]
        supplier = cq.importers.importStep(str(paths[9])).val().translate(
            ((bbox[0]+bbox[3])/2, y_outer, (bbox[2]+bbox[5])/2))
        gap = receiver.distance(supplier)
        common = volume(receiver.intersect(supplier))
        add('receiver:' + name, common <= 1e-7 and gap >= 3.0-1e-6,
            overlap_mm3=common, clearance_mm=gap, required_clearance_mm=3.0)

    after = {str(p.relative_to(ROOT)): sha(p) for p in paths}
    add('provenance:inputs-unchanged', before == after)
    result = dict(passed=all(r['passed'] for r in checks.values()), checks=checks,
                  source_and_artifact_sha256=before, station_mm=station,
                  jack_show_face_y_mm=shift[1], trim_show_face_y_mm=shift[1]+fit.THICK,
                  scope='Production native fit, shared nameplate construction, complete broad wing lands, DATA/DRAIN alignment and plug approach. Printed fit, insertion force, pullout strength and endurance are unmeasured.')
    (HERE / 'fit-check.json').write_text(json.dumps(result, indent=2)+'\n')
    return 0 if result['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
