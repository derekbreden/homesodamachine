"""Require solid deposition through complete fastener hosts and their native roots.

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
from materialize_pump_cartridge import _declared_box


def shape_bounds(shape):
    b = shape.BoundingBox()
    return [b.xmin, b.xmax, b.ymin, b.ymax, b.zmin, b.zmax]


def transformed_bounds(bounds, transform):
    points = itertools.product(*[bounds[i:i + 2] for i in (0, 2, 4)])
    moved = [[sum(transform[i][j] * p[j] for j in range(3)) + transform[i][3]
              for i in range(3)] for p in points]
    return [value for i in range(3)
            for value in (min(p[i] for p in moved), max(p[i] for p in moved))]


def print_pose(piece, mesh_bounds):
    """Source-coordinate orientation and bed datum; plate X/Y nesting is separate."""
    sign = -1.0 if piece == 'pump-cap' else (
        1.0 if piece == 'pump-cartridge' else e.print_up(*piece.split('-')))
    offset = -float(mesh_bounds[0][2]) if sign > 0 else float(mesh_bounds[1][2])
    return dict(up_axis_in_source=[0, 0, sign],
                bed_face='Z minus' if sign > 0 else 'Z plus',
                source_to_print_mm=[[1, 0, 0, 0], [0, sign, 0, 0],
                                    [0, 0, sign, offset], [0, 0, 0, 1]])


def dock_regions(box, region):
    """Load paths from final source interfaces."""
    plate = box.pack.collet_plate
    if not plate:
        return
    retention = e.pump_retention_features(box)
    for side, piece in (('moving', 'pump-cartridge'), ('fixed', 'front-top')):
        for number, shape in enumerate(retention[side]['cutter'].Solids(), start=1):
            b = shape_bounds(shape)
            b[0] -= e.wall
            b[1] += e.wall
            b[4] -= e.wall
            b[5] += e.wall
            b[2 if side == 'moving' else 3] += -e.wall if side == 'moving' else e.wall
            region(piece, f'SB443 column {number}: rail slot walls, roof over the blocks and root', b)


def above_core_regions(box, region):
    """Complete fixed-shell hosts from the selected native interface helpers."""
    shell = e._above_core_shell
    for number, shape in enumerate(shell.access_bosses(), start=1):
        region('back-top', f'Electronics closure host, blind cap and roof root {number}',
               shape_bounds(shape))
    bosses, _holes = shell.relay_bosses()
    for number, shape in enumerate(bosses, start=1):
        bounds = shape_bounds(shape)
        bounds[0] = min(bounds[0], box.outer[0])
        region('back-top', f'Relay insert host and complete west wall root {number}',
               bounds)
    x, y, z = shell.layout.pose('c14-inlet')['translation_mm']
    fasteners = shell.c14_fastener_plan()
    seat = y - fasteners['flange_thickness_mm']
    depth = fasteners['boss_depth_mm']
    pitch = shell.layout.specification()['rear_wall']['dry_openings']['c14']['mount_pitch_mm']
    for side in (-1, 1):
        # Use the same native cylinder as rear_geometry(); carry its complete
        # blind end and backing through the supporting exterior rear wall.
        host = shell.ycylinder(5., x + side*pitch/2, z, seat-depth, seat)
        bounds = shape_bounds(host)
        bounds[3] = max(bounds[3], box.outer[3])
        region('back-top', f'C14 blind insert host and rear wall root {side:+g}', bounds)
    if box.pack.funnel:
        frame = e._funnel_frame_part
        for col in ('front', 'back'):
            receivers = frame.receivers(box.inner, box.outer, box.y_joint,
                                        box.pack.funnel, e.funnel_seat_z(box.outer), col)
            if receivers is not None:
                for number, shape in enumerate(receivers.Solids(), start=1):
                    region(f'{col}-top',
                           f'Funnel frame receiver, blind cap and full flank root {number}',
                           shape_bounds(shape))


def main():
    box, _bounds, box_path = _declared_box(_box_spec, e)
    pieces = {name: [] for name in e.PIECE_COLORS}
    def region(piece, name, bounds, **evidence):
        pieces[piece].append(dict(name=name, machine_bounds_mm=bounds,
                                 sparse_infill_density='100%', sparse_infill_pattern='zig-zag',
                                 **evidence))
    lower, upper = e.y_stack(box.inner)
    for xi, sx in ((box.inner[0], 1.0), (box.inner[1], -1.0)):
        for rows, depth in ((lower, e.y_stack_low_depth), (upper, e.y_stack_high_depth)):
            for who, z0, z1, _g0, _g1 in rows:
                b = e._y_knuckle(box.inner, box.outer, xi, sx, box.y_joint, who, z0, z1,
                                depth).BoundingBox()
                # Carry the modifier through the supporting exterior wall, not
                # just the projecting block that the knuckle helper returns.
                xa = min(b.xmin, box.outer[0]) if sx > 0 else b.xmin
                xb = max(b.xmax, box.outer[1]) if sx < 0 else b.xmax
                region(who, f'Y seam knuckle and its wall root {sx:+g}/{z0:g}',
                       [xa, xb, b.ymin, b.ymax, b.zmin, b.zmax])
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
    split=e.cap_split_z(box.pack.pump_trays)
    lane = min(abs(cx) for cx, _cy, _cz in box.pack.pump_trays) - e._tray.boss_half - e.cap_boss_air
    for y in e.cap_screw_ys(box.inner,box.pack.collet_plate):
        region('pump-cartridge',f'Clamp insert and complete spine root {y:g}',
               [-lane,lane,y-5,y+5,e.bay_floor_z(box.pack.pump_trays)[1],split])
    x,z=e.pump_contact_station(box)
    host_x = max(e._pogo.EAR_L/2.0+e.fits.slip,
                 max(abs(ex) for ex in e._pogo.ear_xs())+e.pogo_insert_entry_dia/2.0)+e.wall
    host_z = e._pogo.BODY_W/2.0+e.fits.slip+e.fits.supported_surface+e.wall
    fixed_face, moving_face = e.pump_contact_faces(box)
    for name,face,sgn in (('front-top',fixed_face,1), ('pump-cap',moving_face,-1)):
        back=face+sgn*(e._pogo.ear_back()+e.pogo_heatset_setback+
                       e.pogo_heatset_len+e.pogo_heatset_relief+e.wall)
        ya,yc=sorted((face,back))
        bounds = [x-host_x,x+host_x,ya,yc,z-host_z,z+host_z]
        region(name,'Both pogo insert hosts, loading passages and blind caps',
               bounds)
    dock_regions(box, region)
    above_core_regions(box, region)
    poses = {}
    for name, rows in pieces.items():
        mesh = trimesh.load_mesh(ENC/f'enclosure-{name}.stl', process=False)
        poses[name] = print_pose(name, mesh.bounds)
        for row in rows:
            clipped = [value for axis in range(3) for value in (
                max(row['machine_bounds_mm'][2*axis], float(mesh.bounds[0][axis])),
                min(row['machine_bounds_mm'][2*axis+1], float(mesh.bounds[1][axis])))]
            row['applied_source_bounds_mm'] = clipped
            row['print_bounds_mm'] = transformed_bounds(
                clipped, poses[name]['source_to_print_mm'])
    paths=[Path(__file__),ENC/'enclosure.py',ENC/'_enclosure_interface.py',box_path,
           Path(e._above_core_shell.__file__),
           Path(e._above_core_shell.layout.__file__),
           ROOT/'hardware/manifold-layout/above-core.json',
           ROOT/'hardware/reference/teyleten-relay/teyleten_relay.py',
           Path(e._funnel_frame_part.__file__),
           Path(e._funnel_frame_part.funnel.__file__),
           Path(e._dock.__file__),
           Path(e._retention.__file__),
           Path(e._dock.plumbing.__file__),
           ROOT/'hardware/printed-parts/petgf.3mf']
    report=dict(scope='Local 100% infill modifiers in existing native material; complete insert hosts, blind caps, roots and seam load paths. No load capacity or lifetime qualification.',
                use='Manual print-preparation specification only. Modifier boxes intersect existing material and add no geometry. applied_source_bounds_mm clips each requested box to the model bounds before its prescribed print transform; plate X/Y nesting is separate. Bind a fresh native project and emitted paths to these hashes before production printing; this is not a build gate or a sliced-print result.',
                coordinate_frames={name: 'Source STEP/STL coordinates in the appliance frame' for name in pieces},
                print_poses=poses,
                part_process_overrides={},
                source_sha256={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths},
                native_artifact_sha256={name:{suffix:hashlib.sha256((ENC/f'enclosure-{name}{suffix}').read_bytes()).hexdigest()
                                             for suffix in ('.step','.stl')} for name in pieces},pieces=pieces)
    (Path(__file__).parent/'print-regions.json').write_text(json.dumps(report,indent=2)+'\n')


if __name__=='__main__':
    main()
