"""Require solid deposition through retention features and their native roots.

These modifier boxes change infill within existing solids; they add no geometry.
They do not supply a pullout or drop strength allowable.
"""
from pathlib import Path
import hashlib
import itertools
import json
import sys

import trimesh

ROOT = next(p for p in Path(__file__).resolve().parents if (p / 'tools/docgen').is_dir())
ENC = ROOT / 'hardware/printed-parts/enclosure/enclosure'
sys.path[:0] = [str(ROOT / 'hardware/scripts'), str(ENC)]
import enclosure as e
import _box_spec
import _rust_part
import _fixed_pump_mount as fixed_mount
from materialize_pump_cartridge import _declared_box


def transformed_bounds(bounds, transform):
    points = itertools.product(*[bounds[i:i + 2] for i in (0, 2, 4)])
    moved = [[sum(transform[i][j] * p[j] for j in range(3)) + transform[i][3]
              for i in range(3)] for p in points]
    return [value for i in range(3)
            for value in (min(p[i] for p in moved), max(p[i] for p in moved))]


def print_pose(piece, mesh_bounds):
    """Source-coordinate orientation and bed datum; plate X/Y nesting is separate."""
    if piece == 'pump-retainer':
        return dict(up_axis_in_source=[0,1,0], bed_face='Y minus',
                    source_to_print_mm=[[1,0,0,0],[0,0,-1,0],
                                        [0,1,0,-float(mesh_bounds[0][1])],[0,0,0,1]])
    sign = e.PIECE_PRINT_UP[piece]
    offset = -float(mesh_bounds[0][2]) if sign > 0 else float(mesh_bounds[1][2])
    return dict(up_axis_in_source=[0, 0, sign],
                bed_face='Z minus' if sign > 0 else 'Z plus',
                source_to_print_mm=[[1, 0, 0, 0], [0, sign, 0, 0],
                                    [0, 0, sign, offset], [0, 0, 0, 1]])


def above_core_regions(box, region, receivers):
    """Complete fixed-shell hosts from the selected native interface helpers."""
    shell = e._above_core_shell
    for component, plan in shell.wall_mount_datums().items():
        for number, station in enumerate(plan['stations'], start=1):
            root, face, axis = (station[k] for k in
                               ('stock_root_world_mm', 'insert_face_world_mm', 'axis_world'))
            tip = [face[k] + axis[k]*plan.get('bearing_tip_height_mm', 0.)
                   for k in range(3)]
            radius = plan['boss_radius_mm']
            bounds = [value for k in range(3) for value in
                      (min(root[k], tip[k]) - (radius if abs(axis[k]) < 0.5 else 0.),
                       max(root[k], tip[k]) + (radius if abs(axis[k]) < 0.5 else 0.))]
            if component == 'psu':
                bounds[5] = max(bounds[5], box.outer[5])
                bearing_root = 'ceiling root and blind floor'
            else:
                bounds[0] = min(bounds[0], box.outer[0])
                bearing_root = 'west wall root'
            region('back-top', f'{component} bearing pad, insert host and {bearing_root} {number}',
                   bounds)
        if component != 'psu':
            for y in sorted({round(s['position_world_mm'][1], 6) for s in plan['stations']}):
                row = [s for s in plan['stations'] if abs(s['position_world_mm'][1]-y) < 1e-5]
                region('back-top', f'{component} connecting host bar and wall root at Y{y:g}',
                       [box.outer[0], min(s['insert_face_world_mm'][0] for s in row),
                        y-5., y+5., min(s['position_world_mm'][2] for s in row),
                        max(s['position_world_mm'][2] for s in row)])
    x, y, z = shell.layout.pose('c14-inlet')['translation_mm']
    fasteners = shell.c14_fastener_plan()
    seat = y - fasteners['flange_thickness_mm']
    depth = fasteners['boss_depth_mm']
    pitch = shell.layout.specification()['rear_wall']['dry_openings']['c14']['mount_pitch_mm']
    for side in (-1, 1):
        # The rear wall's blind boss round each screw, with its complete blind end and
        # backing carried through the supporting exterior rear wall.
        cx, radius = x + side*pitch/2, 5.
        region('back-top', f'C14 blind insert host and rear wall root {side:+g}',
               [cx-radius, cx+radius, seat-depth, max(seat, box.outer[3]),
                z-radius, z+radius])
    nameplate_path = ENC.parent/'nameplate/nameplate.numbers.json'
    mount = json.loads(nameplate_path.read_text())['snap']
    plate = json.loads((ROOT/'hardware/manifold-layout/above-core.json').read_text())['rear_identification']['nameplate']
    back = plate['face_y_mm'] - mount['thick']
    radius = mount['insert_stock_radius']
    for number, (dx, dz) in enumerate(mount['stations'], start=1):
        x, z = plate['center_x_mm'] + dx, plate['center_z_mm'] + dz
        region('back-top', f'Nameplate insert land and rear wall root {number}',
               [x-radius, x+radius,
                min(box.inner[3], back+mount['pilot_rear']-mount['floor_stock']),
                back+mount['thick'],
                z-radius, z+radius])
    if box.pack.funnel:
        for col in ('front', 'back'):
            if col in receivers:
                region(f'{col}-top', 'Funnel frame receiver, blind cap and full flank root 1',
                       receivers[col])


def write_regions(box, _bounds, box_path):
    pieces = {name: [] for name in e.PIECE_COLORS}
    mesh_bounds = {
        name: trimesh.load_mesh(ENC/f'enclosure-{name}.stl', process=False).bounds
        for name in pieces
    }
    def region(piece, name, bounds, **evidence):
        pieces[piece].append(dict(name=name, machine_bounds_mm=bounds,
                                 sparse_infill_density='100%', sparse_infill_pattern='zig-zag',
                                 **evidence))
    # The knuckles' and receivers' bounds from the pieces' construction plan.
    cut = json.loads(_rust_part.run('enclosure-quadrants', 'enclosure-region-bounds', '--box', box_path))
    for knuckle in cut['knuckles']:
        sx, (x0, x1, y0, y1, z0, z1) = knuckle['sx'], knuckle['bounds']
        # Carry the modifier through the supporting exterior wall, not
        # just the projecting block that the knuckle recipe returns.
        xa = min(x0, box.outer[0]) if sx > 0 else x0
        xb = max(x1, box.outer[1]) if sx < 0 else x1
        region(knuckle['piece'], f"Y seam knuckle and its wall root {sx:+g}/{knuckle['z0']:g}",
               [xa, xb, y0, y1, z0, z1])
    for col, y0, y1 in (('front',box.outer[2],box.y_joint),('back',box.y_joint,box.outer[3])):
        for sx in (-1,1):
            xa,xb=sorted((sx*90.0,sx*107.5))
            for level in ('top','bottom'):
                region(f'{col}-{level}',f'Z rail, end stop and wall root {sx:+g}',
                       [xa,xb,y0,y1,e.z_seam-e.wall,e.z_seam+e.z_rise+e.wall])
    for y,z,tip,*_ in box.pack.east_bosses:
        name=('front' if y<=box.y_joint else 'back')+('-top' if z>e.z_seam else '-bottom')
        root=e.piece_root_faces(box.inner,*name.split('-'))[1]
        radius=e.mount_boss_dia/2.0
        region(name,f'Electronics host and wall root {y:g}/{z:g}',
               [min(tip,root),box.outer[1],y-radius,y+radius,
                z-radius-abs(root-tip),z+radius])
    for x,y,tip,_dia in box.pack.floor_bosses:
        radius=e.floor_heatset_dia/2.0+2.6
        region('front-bottom' if y<=box.y_joint else 'back-bottom',f'Compressor post and floor {x:g}/{y:g}',
               [x-radius,x+radius,y-radius,y+radius,box.outer[4],tip])
    for x,y,tip in box.pack.cond_mount[-1]:
        region('front-bottom',f'Condenser host and supporting finger {x:g}/{y:g}',
               [x-5,x+5,y-5,y+5,box.outer[4],tip])
    retainer_low, retainer_high = mesh_bounds['pump-retainer']
    mount = fixed_mount.datums(e, box)
    snap = fixed_mount.snap_datums(e, box)
    root_inner_x = snap['carrier_inner_x']-e.wall
    for side, sign in (('west', -1), ('east', 1)):
        # The printed, relaxed wing bounds include its outward tip spread.
        # Carry the whole hook and flexure one wall into the filled upper root
        # and the inboard carrier; the flex clearance remains empty.
        xa, xb = ((float(retainer_low[0]), -root_inner_x) if sign < 0
                  else (root_inner_x, float(retainer_high[0])))
        region('pump-retainer', f'Pump snap {side} full-Y hook, wing and upper root',
               [xa, xb, mount['y0'], mount['y1'], snap['floor_z'], snap['root_z']+e.wall])
        # The complete bearing band continues through the exterior flank.
        # The centre screwdriver port and its roof retain their native shape.
        xa, xb = sorted((sign*snap['receiver_inner_x'], sign*snap['receiver_outer_x']))
        region('front-top', f'Pump snap {side} receiver floor and full flank root',
               [xa, xb, snap['receiver_y0'], snap['receiver_y1'],
                snap['receiver_z0'], snap['receiver_z1']])
    above_core_regions(box, region, cut['receivers'])
    display_mount_path = ENC.parent/'display-cover/mount-dimensions.json'
    display_mount = json.loads(display_mount_path.read_text())
    display_placement_path = ROOT/'hardware/manifold-layout/machine-export-physical.numbers.json'
    display_placement = json.loads(display_placement_path.read_text())['spec']
    display_frame = next(row['transform'] for row in display_placement['instances']
                         if row.get('name') == 'display-cover')
    thick = display_mount['cover_mm'][2]
    rear = -thick-display_mount['pilot_depth_mm']-display_mount['required_backing_mm']
    for number, (x, y) in enumerate(display_mount['stations_local_xy_mm'], start=1):
        bounds = transformed_bounds([x-6.,x+6.,y-6.,y+6.,rear,-thick],display_frame)
        region('front-top',f'Display side insert and continuous housing root {number}',bounds)
    poses = {}
    for name, rows in pieces.items():
        bounds = mesh_bounds[name]
        poses[name] = print_pose(name, bounds)
        for row in rows:
            clipped = [value for axis in range(3) for value in (
                max(row['machine_bounds_mm'][2*axis], float(bounds[0][axis])),
                min(row['machine_bounds_mm'][2*axis+1], float(bounds[1][axis])))]
            row['applied_source_bounds_mm'] = clipped
            row['print_bounds_mm'] = transformed_bounds(
                clipped, poses[name]['source_to_print_mm'])
    paths=[Path(__file__),ENC/'enclosure.py',ENC/'_enclosure_interface.py',
           Path(fixed_mount.__file__),box_path,
           Path(e._above_core_shell.__file__),
           Path(e._above_core_shell.layout.__file__),
           ROOT/'hardware/manifold-layout/above-core.json',
           ENC.parent/'nameplate/nameplate.numbers.json',
           ENC.parent/'nameplate/snap_dimensions.rs',
           ROOT/'hardware/reference/meanwell-irm90/meanwell_irm90.py',
           ROOT/'hardware/reference/teyleten-relay/teyleten_relay.py',
           ENC/'quadrants/funnel.rs',
           ENC/'quadrants/ystacks.rs',
           Path(__file__).with_name('region_bounds.rs'),
           Path(e._dock.__file__),
           Path(e._dock.plumbing.__file__),
           ROOT/'hardware/printed-parts/petgf.3mf',display_mount_path,display_placement_path]
    report=dict(scope='Local 100% infill modifiers in existing native material; complete insert hosts, blind caps, pump snap wings and receivers, roots and seam load paths. No load capacity or lifetime qualification.',
                use='Manual print-preparation specification only. Modifier boxes intersect existing material and add no geometry. applied_source_bounds_mm clips each requested box to the model bounds before its prescribed print transform; plate X/Y nesting is separate. Bind a fresh native project and emitted paths to these hashes before production printing; this is not a build gate or a sliced-print result.',
                coordinate_frames={name: 'Source STEP/STL coordinates in the appliance frame' for name in pieces},
                print_poses=poses,
                part_process_overrides={},
                source_sha256={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths},
                native_artifact_sha256={name:{suffix:hashlib.sha256((ENC/f'enclosure-{name}{suffix}').read_bytes()).hexdigest()
                                             for suffix in ('.step','.stl')} for name in pieces},pieces=pieces)
    (Path(__file__).parent/'print-regions.json').write_text(json.dumps(report,indent=2)+'\n')


def main():
    write_regions(*_declared_box(_box_spec, e))


if __name__=='__main__':
    main()
