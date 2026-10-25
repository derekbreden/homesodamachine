"""Manual bare-frame lift review and static drain-snap/fastener interfaces.

Run through tmp/takeover/cadq. --shells adds both exported production upper shells;
without it the record covers the exported frame and authored ledges. With shells,
nominal J10 tool columns are checked with the frame and its cradled drain removed. All lift poses
remove the cradle, elbow, stub and connected tubing. No snap-deflection or
connected-plumbing motion is modeled.
This script is not called by a generator, build or hook.
"""

import argparse
import hashlib
import json
from pathlib import Path
import sys

import cadquery as cq
import manifold3d as mf
import numpy as np
import trimesh

HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p / 'hardware/scripts').is_dir())
FUNNEL = HERE.parent
ENC = ROOT / 'hardware/printed-parts/enclosure/enclosure'
sys.path[:0] = [str(FUNNEL), str(ENC), str(ROOT / 'hardware/scripts')]
import funnel_frame as ff
import enclosure as enc


def j10_driver_columns(roof_z):
    """Nominal Ø3.3 mm tools above the actual KF301 screw stations."""
    pcb_path = ROOT / 'hardware/printed-parts/electronics/pcba-tray'
    sys.path[:0] = [str(ROOT / 'hardware/manifold-layout'), str(pcb_path)]
    import above_core
    import pcba_tray
    connector_map = ROOT / 'hardware/wiring/installed/connector-map.json'
    connector = json.loads(connector_map.read_text())['connectors']['J10']
    columns = {}
    for pin in connector['pins']:
        x, y = pin['xy_mm']
        point = above_core.point(above_core.pose('pcba'),
            (x-pcba_tray._centre[0], y-pcba_tray._centre[1],
             pcba_tray._thickness+connector['component_glb_bounds_mm'][5]))
        columns[pin['label']] = cq.Solid.makeCylinder(
            1.65, roof_z-point[2], cq.Vector(*point))
    return columns, [Path(above_core.__file__), Path(pcba_tray.__file__),
                     ROOT / 'hardware/manifold-layout/above-core.json', connector_map]


def mesh_solid(shape):
    vertices, faces = shape.tessellate(0.015, 0.08)
    mesh = trimesh.Trimesh(np.asarray([v.toTuple() for v in vertices]),
                           np.asarray(faces), process=True)
    solid = mf.Manifold(mf.Mesh(np.asarray(mesh.vertices, np.float32),
                                np.asarray(mesh.faces, np.uint32)))
    if solid.status() != mf.Error.NoError:
        raise ValueError(f'invalid motion mesh: {solid.status()}')
    return solid


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--shells', action='store_true')
    parser.add_argument('--output', type=Path, default=HERE / 'native-review.json')
    args = parser.parse_args()
    inner, outer = ff.DEFAULT_INNER, (-107.5, 107.5, 0.0, 472.0, 0.0, 355.0)
    centre, seat, joint = (0.0, ff.center_y), 349.0, 200.0
    source_frame = ff.build(inner, joint, centre, seat)
    frame_path = FUNNEL / 'funnel-frame.step'
    frame = cq.importers.importStep(str(frame_path)).val().translate(
        (centre[0], centre[1], ff.datums(seat)[0]))
    frame_difference = (source_frame.cut(frame).Volume() +
                        frame.cut(source_frame).Volume())
    receivers = {}
    for col in ('front', 'back'):
        receivers[col] = ff.receivers(inner, outer, joint, centre, seat, col).cut(
            ff.shell_screw_cuts(inner, centre, seat, col, joint)).clean()
    fixed = {f'{n} ledges': s for n, s in receivers.items()}
    files = [Path(ff.__file__), Path(ff.funnel.__file__), Path(ff.elbow_cradle.__file__),
             Path(enc.__file__), ENC / '_enclosure_interface.py',
             FUNNEL / 'funnel.step', frame_path,
             FUNNEL / 'elbow-cradle.step', Path(__file__)]
    checks = []

    def check(label, passed, **values):
        row = dict(check=label, passed=bool(passed), **values)
        checks.append(row)
        print(json.dumps(row), flush=True)

    for name, shape in {'frame': frame, **fixed}.items():
        metrics = {'solids': len(shape.Solids()), 'volume_mm3': shape.Volume()}
        if name == 'frame':metrics['exported_source_difference_mm3'] = frame_difference
        check(name + ' valid stock', shape.isValid() and len(shape.Solids()) >= 1
              and (name != 'frame' or frame_difference < .001), **metrics)
    if args.shells:
        for col in ('front', 'back'):
            path = ENC / f'enclosure-{col}-top.step'
            fixed[f'production {col}-top'] = cq.importers.importStep(str(path)).val()
            files.append(path)
        columns, inputs = j10_driver_columns(outer[5])
        files.extend(inputs)
        for name, column in columns.items():
            contacts = {col: column.intersect(fixed[f'production {col}-top']).Volume()
                        for col in ('front', 'back')}
            bounds = column.BoundingBox()
            check('J10 roof tool passage / ' + name,
                  max(contacts.values()) < .001,
                  driver_diameter_mm=3.3, shell_overlap_mm3=contacts,
                  roof_world_z_mm=outer[5], axis_world=[0., 0., 1.],
                  driver_base_world_mm=[(bounds.xmin+bounds.xmax)/2.,
                                        (bounds.ymin+bounds.ymax)/2., bounds.zmin],
                  shell_gap_mm={col: column.distance(fixed[f'production {col}-top'])
                                for col in ('front', 'back')},
                  tool_basis='Nominal screwdriver cylinder; purchased tool fit and hand access unqualified.',
                  closure_prerequisite='Frame and its cradled drain removed.')

    frame_mesh = mesh_solid(frame)
    lifts = sorted(set([0.0, .1, .25, .5, 1, 2, 3, 6, 9, 12, 12.25,
                        15, 20, 30, 40, 50, 55.1, 56.0, 60.0]))
    for name, shape in fixed.items():
        other = mesh_solid(shape)
        poses = [dict(lift_mm=z,
                      overlap_mm3=(frame_mesh.translate((0, 0, z)) ^ other).volume())
                 for z in lifts]
        maximum = max(row['overlap_mm3'] for row in poses)
        check('vertical motion / ' + name, maximum < .1,
              maximum_overlap_mm3=maximum, poses=poses)

    # The complete brim's 3 mm bearing annulus, including square front corners.
    brim = ff.funnel.brim_plan(0.0, seat - ff.web, seat, *centre)
    collar = ff.funnel._rounded_box(ff.funnel.collar_w + .6,
        ff.funnel.collar_d + .6, ff.funnel.collar_corner_r + .3,
        seat - ff.web - 1, seat + 1, *centre)
    bearing = brim.cut(collar)
    missing = bearing.cut(frame).Volume()
    check('complete silicone brim bearing', missing < .001,
          missing_volume_mm3=missing, bearing_thickness_mm=ff.web)
    silicone = cq.importers.importStep(str(FUNNEL / 'funnel.step')).val().translate(
        (*centre, seat))
    for name, shape in {'frame': frame, **receivers}.items():
        overlap = silicone.intersect(shape).Volume()
        check('silicone / ' + name, overlap < .001, overlap_mm3=overlap)

    # Exported cradle is printed on its bottom; place its own local joint datum.
    drain = ff.drain_seat_datums(centre, seat)
    cradle = ff.elbow_cradle.build().translate(
        (drain['x'], drain['y'], ff.datums(seat)[0] - ff.elbow_cradle.CATCH_GAP))
    overlap = cradle.intersect(frame).Volume()
    check('released cradle / frame static fit', overlap < .001, overlap_mm3=overlap)

    # The original lower web has only its drain hole and two wing slots.
    half, gap = ff.funnel.plug_width / 2, (ff.socket_width - ff.funnel.plug_width) / 2
    place = cq.Vector(drain['x'], drain['y'], drain['floor_z'])
    plate = ff.elbow_cradle.plug_outline(half, gap, 0., ff.web).translate(place)
    for cutter in ff.elbow_cradle.web_cuts():
        plate = plate.cut(cutter.translate(place))
    missing_web = plate.cut(frame).Volume()
    check('complete original snap web', missing_web < .001,
          thickness_mm=ff.web, missing_volume_mm3=missing_web)
    above = ff.elbow_cradle.plug_outline(half, gap, ff.web + .01,
                                        seat - drain['floor_z']).translate(place)
    socket_stock = frame.intersect(above).Volume()
    check('clear original plug socket', socket_stock < .001,
          socket_depth_mm=ff.socket_depth, unintended_stock_mm3=socket_stock)

    # The complete selected screw-head footprint continues through the frame
    # grip; the shell pilot has its own full wall and blind-backing witnesses.
    rows = ff.fastener_datums(inner, joint, centre, seat)
    for row in rows:
        shortest = row['head_seat_z'] - (ff.SCREW_LENGTH - ff.SCREW_LENGTH_ALLOWANCE)
        longest = row['head_seat_z'] - (ff.SCREW_LENGTH + ff.SCREW_LENGTH_ALLOWANCE)
        minimum_thread = row['insert_top_z'] - shortest
        minimum_tip_air = longest - row['bore_bottom_z']
        head_diameter = enc.head_cbore_dia - 2 * enc.fits.slip
        grip = row['head_seat_z'] - row['ledge_z']
        bearing_cylinder = cq.Solid.makeCylinder(head_diameter / 2,
            grip, cq.Vector(row['x'], row['y'], row['ledge_z']))
        shank = cq.Solid.makeCylinder(enc.screw_clear_dia / 2, grip + .02,
            cq.Vector(row['x'], row['y'], row['ledge_z'] - .01))
        land = bearing_cylinder.cut(shank)
        missing_land = land.cut(frame).Volume()
        radius = row['host_radius_mm']
        pilot_height = row['insert_top_z'] - row['bore_bottom_z']
        host = cq.Solid.makeCylinder(radius, pilot_height,
            cq.Vector(row['x'], row['y'], row['bore_bottom_z']))
        pilot = cq.Solid.makeCylinder(enc.heatset_dia / 2, pilot_height + .02,
            cq.Vector(row['x'], row['y'], row['bore_bottom_z'] - .01))
        annulus = host.cut(pilot)
        backing = cq.Solid.makeCylinder(radius,
            row['bore_bottom_z'] - row['host_bottom_z'],
            cq.Vector(row['x'], row['y'], row['host_bottom_z']))
        hosts = {'authored receiver': receivers[row['col']]}
        if args.shells:
            hosts['production shell'] = fixed[f'production {row["col"]}-top']
        missing_pilot = {name: annulus.cut(shape).Volume() for name, shape in hosts.items()}
        missing_backing = {name: backing.cut(shape).Volume() for name, shape in hosts.items()}
        check('screw / ' + row['name'],
              minimum_thread >= enc.heatset_long_len - 1e-6 and
              minimum_tip_air >= .5 and missing_land < .001 and
              radius - enc.heatset_dia / 2 >= enc.wall - 1e-6 and
              max(missing_pilot.values()) < .001 and max(missing_backing.values()) < .001,
              **row, minimum_thread_reach_mm=minimum_thread,
              minimum_blind_tip_air_mm=minimum_tip_air,
              pilot_radial_stock_mm=radius - enc.heatset_dia / 2,
              pilot_wall_missing_volume_mm3=missing_pilot,
              blind_backing_missing_volume_mm3=missing_backing,
              screw_head_bearing_diameter_mm=head_diameter,
              complete_frame_grip_mm=grip,
              missing_frame_bearing_volume_mm3=missing_land)

    result = dict(passed=all(row['passed'] for row in checks),
        scope=('Sampled exported bare-frame vertical motion through exported upper shells and authored '
               'ledges; drain cradle, elbow, stub and connected tubing removed from all lift poses. '
               'Nominal J10 tool passages through both upper shells are checked with the '
               'frame and its cradled drain removed.'
               if args.shells else
               'Exported bare frame and authored ledges only; drain cradle, elbow, stub and tubing removed '
               'from all lift poses. Production shells and the populated assembly are outside this record.'),
        drain_attachment='Cradle snaps into the removable frame original 3 mm web.',
        removal_prerequisite='The plug, stub, elbow and cradle travel with the frame; disconnect the V-B feed '
                             'before frame withdrawal. This review does not model that disconnection, snap '
                             'deflection or connected-tube motion.',
        evidence_limit='Native and tessellated geometry; no printed fit, support removal, force, '
                       'water exclusion, stiffness or lifetime result.',
        source_sha256={str(p.resolve().relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
                       for p in files}, checks=checks)
    args.output.write_text(json.dumps(result, indent=2) + '\n')
    if not result['passed']:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
