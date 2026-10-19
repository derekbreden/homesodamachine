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
    if piece.startswith(('pump-receiver-', 'pump-return-')):
        return dict(up_axis_in_source=[0, 0, 1],
                    bed_face='Manufacturing export is already bedded in print pose',
                    source_to_print_mm=[[1, 0, 0, 0], [0, 1, 0, 0],
                                        [0, 0, 1, 0], [0, 0, 0, 1]])
    sign = -1.0 if piece == 'pump-cap' else (
        1.0 if piece == 'pump-cartridge' else e.print_up(*piece.split('-')))
    offset = -float(mesh_bounds[0][2]) if sign > 0 else float(mesh_bounds[1][2])
    return dict(up_axis_in_source=[0, 0, sign],
                bed_face='Z minus' if sign > 0 else 'Z plus',
                source_to_print_mm=[[1, 0, 0, 0], [0, sign, 0, 0],
                                    [0, 0, sign, offset], [0, 0, 0, 1]])


def dock_piece_names(dock):
    return tuple(f'{part}-{station}' for station in dock.STATIONS
                 for part in ('pump-receiver', 'pump-return',
                              'pump-receiver-keeper', 'pump-return-cradle',
                              'pump-return-cover'))


def dock_regions(box, region, wet_review):
    """Load paths from final source interfaces and posed, cut wet-key material."""
    plate = box.pack.collet_plate
    if not plate:
        return
    dock, receiver = e._dock, e._receiver
    fore = plate['fore_y']
    # The keeper's screw is offset from the receiver axis. Both its actual
    # raised bearing land and the full through-pilot belong inside this host.
    host_r = dock.LOCK_INSERT_D / 2.0 + e.wall
    for number, (x, z) in enumerate(plate['holes'], start=1):
        lock_x = x + dock.keeper_side(x) * 8.5
        lock_z = z + dock.LOCK_Z
        region('front-top', f'Dock keeper lock {number}, complete host, bearing land and wall root',
               [lock_x-host_r, lock_x+host_r, fore,
                fore+receiver.KEEPER_Y[0], lock_z-host_r,
                lock_z+dock.LOCK_INSERT_D/2.0*2**.5+e.wall])
        guide = dock.guides(fore, x, z, plate['wall_aft_y'])
        for side, shape in enumerate(guide.Solids(), start=1):
            b = shape_bounds(shape)
            b[2] = fore
            region('front-top', f'Dock keeper guide {number}/{side}, stop and wall root', b)

        # The two source-declared fixture anchors seat on integral axial lands.
        # Front hosts continue through the bulkhead. Aft hosts carry their
        # local tray foot through the plate into the appropriate flank root.
        for index, (ax, ay, az) in enumerate(dock.fixture_anchors(plate, x)):
            half = host_r
            top = az + dock.LOCK_INSERT_D/2.0*2**.5 + e.wall
            if index == 0:
                b = [ax-half, ax+half, fore, ay+dock.fits.running,
                     az-host_r, top]
            else:
                plane, sign, seats = min(plate['valve_trays'],
                                        key=lambda row: abs(row[0]-ay))
                face = plane-sign*dock.valve_tray.SEAT
                near, far = sorted((face, face-sign*dock.valve_tray.THICK))
                side = 0 if x < 0 else 1
                root_floor = dock.valve_tray.wall_root_floors(seats)[side]
                xa, xb = ((box.inner[0], ax+half) if x < 0
                          else (ax-half, box.inner[1]))
                b = [xa, xb, near-dock.fits.running, far,
                     box.splits[0]+e.fits.supported_surface,
                     max(top, root_floor+e.wall)]
            region('front-top', f'Return fixture {number}/{index+1}, insert, axial land and native host root', b)

    retention = e.pump_retention_features(box)
    for side, piece in (('moving', 'pump-cartridge'), ('fixed', 'front-top')):
        for number, shape in enumerate(retention[side]['stock'].Solids(), start=1):
            b = shape_bounds(shape)
            b[2 if side == 'moving' else 3] += -e.wall if side == 'moving' else e.wall
            region(piece, f'SB443 column {number}, rails, keyed bedding walls and host root', b)

    aft = e.pump_cartridge_aft_y(box.pack.pump_trays, plate)
    for number, shape in enumerate(e.pump_cartridge_body_stops(box), start=1):
        b = shape_bounds(shape)
        b[0] -= e.wall
        b[1] += e.wall
        b[3] += e.wall
        b[4] -= e.wall
        b[5] += e.wall
        region('front-top', f'Rigid cartridge stop {number} and wall root', b)
        region('pump-cartridge', f'Rigid stop {number} opposing bearing and cradle root',
               [b[0], b[1], aft-2*e.wall, aft, b[4], b[5]])

    stems = e.pump_stem_features(box)
    for key, piece in (('cradle_stock', 'pump-cartridge'), ('cap_stock', 'pump-cap')):
        for number, shape in enumerate(stems[key].Solids(), start=1):
            b = shape_bounds(shape)
            b[2] -= e.wall
            b[4 if piece == 'pump-cartridge' else 5] += (
                -e.wall if piece == 'pump-cartridge' else e.wall)
            region(piece, f'Stem flange capture {number}, shoulders, guard and native root', b)

    # These twelve small structural parts are exported already in print pose.
    # Their whole-object100%/six-wall recipe covers the complete throats,
    # closed tube guides, head-bearing plates, anchor arms and backing roots.
    for station in dock.STATIONS:
        for part in ('pump-receiver-keeper', 'pump-return-cradle', 'pump-return-cover'):
            name = f'{part}-{station}'
            solid = e.cq.importers.importStep(str(ENC/f'enclosure-{name}.step')).val()
            region(name, 'Complete structural part, bearings, fastener tabs and connected roots',
                   shape_bounds(solid))

    # The offline wet preparer already holds each actual key intersected with
    # the final cut wet body. Its saved native descriptors avoid rebuilding all
    # eight expensive bodies merely to recover their exact bedding transform.
    # This is a manual metadata input, not a new normal producer or gate.
    parts = wet_review['parts']
    for station in dock.STATIONS:
        for part in ('pump-receiver', 'pump-return'):
            name = f'{part}-{station}'
            record = parts[f'enclosure-{name}']
            # Slice-time identities remain in source_sha256. A current map
            # may accompany an explicit unchanged-input rebind in the review.
            bindings = record.get('current_source_sha256', record['source_sha256'])
            for path, digest in bindings.items():
                if hashlib.sha256((ROOT/path).read_bytes()).hexdigest() != digest:
                    raise ValueError(f'{name}: wet-key descriptor has a stale source: {path}')
            for key in record['key_regions']:
                region(name, f'TPU mounting key {key["index"]}, actual cut material and connected root',
                       key['bounds_print_mm'],
                       material_volume_mm3=key['volume_mm3'],
                       region_stl_sha256=key['stl_sha256'])
            if part == 'pump-receiver':
                # The separate rear-flange ears carry wall clocking loads.
                # Their full collar connection stays inside this source box.
                b = [-receiver.KEY_OUTER_X, receiver.KEY_OUTER_X,
                     receiver.REAR_COLLAR_Y[0], receiver.REAR_COLLAR_Y[1],
                     -receiver.COLLAR_OD/2, receiver.COLLAR_OD/2]
                region(name, 'Rear flange, clocking ears and their complete collar root',
                       transformed_bounds(b, record['source_to_print_mm']))


def main():
    box, _bounds, box_path = _declared_box(_box_spec, e)
    wet_path = ENC.parent/'pump-dock/print-preparation/2026-10-18-asymmetric-wet-siraya85a-mark1/native-review.json'
    wet_review = json.loads(wet_path.read_text())
    pieces = {name: [] for name in (*e.PIECE_COLORS, *dock_piece_names(e._dock))}
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
    fore=box.outer[3]-e.socket_cap-e.c14_tunnel_len
    for x,z in box.pack.c14:
        region('back-top',f'C14 host and wall {x:g}',
               [x-5,x+5,fore,box.outer[3],z-5,z+5])
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
        if name == 'front-top':
            pad = shape_bounds(e._pump_contact_fixed_stock(box))
            bounds = [value for axis in range(3) for value in (
                min(bounds[2*axis], pad[2*axis]),
                max(bounds[2*axis+1], pad[2*axis+1]))]
        region(name,'Both pogo insert hosts, loading passages and blind caps',
               bounds)
    dock_regions(box, region, wet_review)
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
           Path(e._dock.__file__),Path(e._receiver.__file__),
           Path(e._retention.__file__),Path(e._stems.__file__),
           Path(e._dock.returned.__file__),Path(e._dock.plumbing.__file__),
           ROOT/'hardware/printed-parts/petgf.3mf',wet_path]
    report=dict(scope='Local 100% infill modifiers in existing native material; complete insert hosts, blind caps, roots and seam load paths. No load capacity or lifetime qualification.',
                use='Manual print-preparation specification only. Modifier boxes intersect existing material and add no geometry. applied_source_bounds_mm clips each requested box to the model bounds before its prescribed print transform; plate X/Y nesting is separate. Bind a fresh native project and emitted paths to these hashes before production printing; this is not a build gate or a sliced-print result.',
                coordinate_frames={name: ('Canonical manufacturing STEP/STL, already bedded in print pose'
                                         if name.startswith(('pump-receiver-', 'pump-return-'))
                                         else 'Source STEP/STL coordinates in the appliance frame') for name in pieces},
                print_poses=poses,
                part_process_overrides={name: dict(wall_loops='6', sparse_infill_density='100%',
                    sparse_infill_pattern='zig-zag',
                    purpose='The complete rigid keeper/cradle/cover section carries the head bearings, closed tube guide and fastener load paths. Whole-object solid deposition includes every named interface.')
                    for name in pieces if name.startswith(('pump-receiver-keeper-', 'pump-return-cradle-', 'pump-return-cover-'))},
                source_sha256={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths},
                native_artifact_sha256={name:{suffix:hashlib.sha256((ENC/f'enclosure-{name}{suffix}').read_bytes()).hexdigest()
                                             for suffix in ('.step','.stl')} for name in pieces},pieces=pieces)
    (Path(__file__).parent/'print-regions.json').write_text(json.dumps(report,indent=2)+'\n')


if __name__=='__main__':
    main()
