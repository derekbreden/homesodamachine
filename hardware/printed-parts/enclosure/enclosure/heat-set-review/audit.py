from pathlib import Path
import hashlib
import json
import sys

import cadquery as cq
from datetime import datetime, timezone

ROOT = next(p for p in Path(__file__).resolve().parents if (p / 'tools/docgen').is_dir())
ENC = ROOT / 'hardware/printed-parts/enclosure/enclosure'
sys.path[:0] = [str(ROOT / 'hardware/scripts'), str(ENC)]
import enclosure as e
import _box_spec
import _fixed_pump_mount as fixed_mount
from materialize_pump_cartridge import _declared_box

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

source_paths = (ENC / 'enclosure.py', ENC / '_enclosure_interface.py',
                Path(fixed_mount.__file__), _box_spec.ARTIFACT)
input_paths = (*source_paths, *(ENC / f'enclosure-{name}.step' for name in e.PIECE_COLORS))
input_hashes = {str(p.relative_to(ROOT)): sha(p) for p in input_paths}
box, bounds, box_path = _declared_box(_box_spec, e)
station_rows = []

def add(piece, family, seat, into, pilot, length, depth, minimum, supported=False):
    station_rows.append(dict(piece=piece, family=family, seat_mm=seat, into=into,
        pilot_mm=pilot, insert_length_mm=length, pocket_depth_mm=depth,
        minimum_wall_mm=minimum, supported=supported))

for xi, sx in ((box.inner[0], 1.0), (box.inner[1], -1.0)):
    bores = e._y_stack_bores(xi, sx, box.y_joint, box.inner)
    for rod, _seat, tip, length, piece, z0, z1 in e.y_stack_rods(box.inner):
        ax, ay = e.y_stack_axis(xi, sx, box.y_joint, rod)
        # Both pilots open on the top of their knuckles; read each far end from the cutter
        # that actually makes the pocket.
        bore = bores[2 if rod == 'lower' else 5].BoundingBox()
        mouth, into, blind = z1, -1.0, bore.zmin
        depth = into * (blind - mouth)
        add(piece, 'Y-seam stack', (ax, ay, mouth), (0, 0, into), e.floor_heatset_dia,
            e.floor_heatset_depth, depth, 2.6)
        tolerance = e.y_stack_screw_length_tolerance
        if rod == 'lower':
            # Driven up into the insert from its deep end; the tip stands past the open top.
            engaged = min(tip - tolerance, z1) - z0
            station_rows[-1].update(
                screw_length_mm=length, screw_length_tolerance_mm=tolerance,
                printed_clearance_diameter_mm=e.y_stack_clearance_dia,
                through_passage_mm=e.y_stack_clearance_dia,
                nominal_thread_engagement_mm=min(tip, z1) - z0,
                minimum_thread_engagement_mm=engaged,
                nominal_tip_past_open_mouth_mm=tip - z1,
                maximum_tip_past_open_mouth_mm=tip + tolerance - z1)
            station_rows[-1]['screw_reach_pass'] = engaged >= e.floor_heatset_depth - 1e-9
            continue
        reach = into * (tip - mouth)
        tip_clearance = depth - reach
        station_rows[-1].update(
            screw_length_mm=length, screw_length_tolerance_mm=tolerance,
            printed_clearance_diameter_mm=e.y_stack_clearance_dia,
            nominal_thread_reach_mm=reach, minimum_thread_reach_mm=reach-tolerance,
            nominal_thread_engagement_mm=min(reach, e.floor_heatset_depth),
            minimum_thread_engagement_mm=min(reach-tolerance, e.floor_heatset_depth),
            nominal_blind_tip_clearance_mm=tip_clearance,
            minimum_blind_tip_clearance_mm=tip_clearance-tolerance)
        station_rows[-1]['screw_reach_pass'] = (
            reach-tolerance >= e.floor_heatset_depth
            and tip_clearance-tolerance >= 0.5)
for station in box.pack.east_bosses:
    sy,sz,tip=station[:3]
    piece=('front' if sy<=box.y_joint else 'back')+('-top' if sz>e.z_seam else '-bottom')
    col,level=piece.split('-')
    root=e.piece_root_faces(box.inner,col,level)[1]
    setback=e.east_boss_insert_setback(station)
    seat=(tip if root-tip >= e.east_boss_min_stand-e.stated_bound_tol else root)+setback
    add(piece,'electronics', (seat,sy,sz),(1,0,0),e.heatset_dia,e.heatset_len,
        e.east_boss_bore_end(sy,tip+setback,box.outer)-seat,1.6,True)
    if setback:
        station_rows[-1].update(entry_setback_mm=setback,mounting_face_x_mm=tip,
                               screw_length_mm=8.0,pcb_thickness_mm=1.6,
                               nominal_thread_reach_mm=8.0-1.6-setback,
                               nominal_blind_tip_clearance_mm=station_rows[-1]['pocket_depth_mm']-(8.0-1.6-setback))
for x,y,tip,dia in box.pack.floor_bosses:
    add('front-bottom' if y<=box.y_joint else 'back-bottom','compressor',
        (x,y,tip),(0,0,-1),e.floor_heatset_dia,e.floor_heatset_depth,
        e.floor_heatset_depth+e.mount_bore_relief,2.6)
for x,y,tip in box.pack.cond_mount[-1]:
    add('front-bottom','condenser',(x,y,tip),(0,0,-1),e.heatset_dia,
        e.heatset_long_len,e.cond_bore_depth,1.6)
for fastener in fixed_mount.fasteners(e, box):
    mouth = fastener['insert_mouth_z']
    add('front-top', 'pump retainer', (fastener['x'], fastener['y'], mouth),
        (0, 0, 1), e.heatset_dia, e.heatset_long_len,
        fastener['insert_top_z']+e.mount_bore_relief-mouth, 1.6)
    station_rows[-1].update(
        through_passage_mm=e.screw_clear_dia,
        screw_length_mm=fastener['screw_length_mm'],
        nominal_thread_reach_mm=fastener['screw_tip_z']-mouth,
        nominal_thread_engagement_mm=e.heatset_long_len,
        nominal_blind_tip_clearance_mm=fastener['pilot_end_z']-fastener['screw_tip_z'],
        screw_reach_pass=(fastener['screw_tip_z'] >= fastener['insert_top_z']
                          and fastener['pilot_end_z']-fastener['screw_tip_z'] >= 0.5),
        tip_passage_depth_mm=fastener['pilot_end_z']-mouth)
fore=box.outer[3]-e.socket_cap-e.c14_tunnel_len
for x,z in box.pack.c14:
    add('back-top','C14',(x,fore,z),(0,1,0),e.heatset_dia,e.heatset_len,
        e.heatset_depth,1.6,True)

shapes={}
for piece in sorted(e.PIECE_COLORS):
    path=ENC/f'enclosure-{piece}.step'
    shapes[piece]=cq.importers.importStep(str(path)).val()
    print(f'read {piece}',flush=True)

def cylinder(row,radius,length):
    origin=cq.Vector(*row['seat_mm']) + cq.Vector(*row['into'])*0.02
    shape=cq.Solid.makeCylinder(radius,length-0.04,origin,cq.Vector(*row['into']))
    if row['supported']:
        shape=shape.fuse(shape.translate((0,0,e.PIECE_PRINT_UP[row['piece']]*e.fits.supported_surface)))
    return shape

tol=1e-5
for row in station_rows:
    shape=shapes[row['piece']]
    radius=row['pilot_mm']/2
    body=cylinder(row,radius,row['insert_length_mm'])
    probe=cylinder(row,radius,row['pocket_depth_mm'])
    row['blocked_pocket_mm3']=abs(probe.intersect(shape).Volume())
    row['blind_relief_mm']=row['pocket_depth_mm']-row['insert_length_mm']
    def missing(wall):
        return abs(cylinder(row,radius+wall,row['insert_length_mm']).cut(body).cut(shape).Volume())
    minimum=row['minimum_wall_mm']
    row['missing_required_stock_mm3']=None if minimum is None else missing(minimum)
    lo,hi=0.0,3.5
    for _ in range(10):
        mid=(lo+hi)/2
        if missing(mid)<=tol: lo=mid
        else: hi=mid
    row['minimum_full_depth_wall_mm_interval']=[round(lo,5),round(hi,5)]
    row['stock_rule_pass']=None if minimum is None else row['missing_required_stock_mm3']<=tol
    row['stock_rule']='ruthex RX table minimum wall from recommended pilot'
    row['manufacturer_wall_pass']=row['stock_rule_pass']
    # This is an independent supplier constraint, not an equality between two CAD constants.
    expected_pilot = 6.4 if row['family'] in ('compressor', 'Y-seam stack') else 4.0
    row['manufacturer_pilot_mm'] = expected_pilot
    row['manufacturer_pilot_pass'] = None if expected_pilot is None else abs(row['pilot_mm'] - expected_pilot) < 1e-6
    row['blind_relief_pass']=row['blind_relief_mm']>=1-1e-6
    row['pocket_clear_pass']=row['blocked_pocket_mm3']<=tol
    print(json.dumps({k:row[k] for k in ('piece','family','seat_mm','minimum_full_depth_wall_mm_interval',
        'stock_rule_pass','blind_relief_mm','pocket_clear_pass')}),flush=True)

# Clear insertion access, supported whole knurl, and closed stock after each pilot.
for row in station_rows:
    shape=shapes[row['piece']]
    into=cq.Vector(*row['into']);seat=cq.Vector(*row['seat_mm'])
    cap_start=seat+into*(row['pocket_depth_mm']+0.02)
    cap_probe=cq.Solid.makeCylinder(row['pilot_mm']/2.0,0.25,cap_start,into)
    if row.get('through_passage_mm'):
        # The screw enters this insert from the pocket's far end: the stock past the pilot is
        # the shoulder round its clearance passage.
        cap_probe=cap_probe.cut(cq.Solid.makeCylinder(row['through_passage_mm']/2.0,0.25,cap_start,into))
    row['missing_closed_blind_stock_mm3']=cap_probe.cut(shape).Volume()
    row['closed_blind_pass']=row['missing_closed_blind_stock_mm3']<=tol
    if row.get('entry_setback_mm'):
        mouth=seat-into*(row['entry_setback_mm']-0.02)
        entry=cq.Solid.makeCylinder(4.6/2.0,row['entry_setback_mm']-0.04,mouth,into)
        row['blocked_whole_knurl_entry_mm3']=entry.intersect(shape).Volume()
        row['insertion_access_pass']=row['blocked_whole_knurl_entry_mm3']<=tol
        row['screw_reach_pass']=row['nominal_thread_reach_mm']>=row['insert_length_mm'] and row['nominal_blind_tip_clearance_mm']>=0.5

# Every finished knuckle of both corner stacks, whole in its carrying piece.
seam=[]
lower, upper = e.y_stack(box.inner)
for xi, sx in ((box.inner[0], 1.0), (box.inner[1], -1.0)):
    bores = e._y_stack_bores(xi, sx, box.y_joint, box.inner)
    for rows, depth in ((lower, e.y_stack_low_depth), (upper, e.y_stack_high_depth)):
        ax, ay = e.y_stack_axis(xi, sx, box.y_joint, "lower" if rows is lower else "upper")
        for who, z0, z1, gap_below, gap_above in rows:
            knuckle = e._y_knuckle(box.inner, box.outer, xi, sx, box.y_joint, who, z0, z1, depth)
            for cutter in bores:
                knuckle = knuckle.cut(cutter)
            y_side, z_side = who.split('-')
            if z_side == 'bottom':
                knuckle = e._finish_handholds(knuckle, box.inner)
            knuckle = e._seam_fit_reliefs(knuckle, box, y_side, z_side)
            seam.append(dict(side='west' if sx>0 else 'east', piece=who, z_mm=[z0, z1],
                             rod_axis_mm=[ax, ay], bearing_length_mm=z1-z0,
                             gaps_mm=[gap_below, gap_above],
                             ligament_fore_and_aft_mm=e.lip_len/2.0-e.y_stack_clearance_dia/2.0,
                             missing_knuckle_stock_mm3=knuckle.cut(shapes[who]).Volume()))

final_hashes = {str(p.relative_to(ROOT)): sha(p) for p in input_paths}
inputs_unchanged = final_hashes == input_hashes
report={'generated_utc':datetime.now(timezone.utc).isoformat(),'scope':'Full installed insert envelopes in retained native STEP solids; supported-face clearance is included. No printed fit, pullout, torque, transport or drop qualification.',
    'source_sha256':{str(p.relative_to(ROOT)): input_hashes[str(p.relative_to(ROOT))] for p in source_paths},
    'native_step_sha256':{name: input_hashes[str((ENC/f'enclosure-{name}.step').relative_to(ROOT))] for name in shapes},
    'inputs_unchanged': inputs_unchanged,
    'stations':station_rows,'seam_stations':seam,
    'sources':{'ruthex':'https://www.igo3d.com/mediafiles/Sonstiges/Ruthex/ruthex_Datenblatt_RX-Serie.pdf',
    'spirol':'https://www.spirol.com/resources/white-papers/how-to-select-a-threaded-insert-for-your-3d-printed-assembly/'},
    'status':'pass' if inputs_unchanged and all(r['stock_rule_pass'] and r['blind_relief_pass'] and r['pocket_clear_pass'] and r['closed_blind_pass'] and r.get('insertion_access_pass',True) and r.get('screw_reach_pass',True) and r['manufacturer_pilot_pass'] is not False for r in station_rows) and all(r['missing_knuckle_stock_mm3']<=tol for r in seam) else 'fail'}
(Path(__file__).parent/'geometry-check.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'stations':len(station_rows),'failed_known_wall':sum(r['stock_rule_pass'] is False for r in station_rows),
    'failed_depth':sum(not r['blind_relief_pass'] for r in station_rows),'blocked':sum(not r['pocket_clear_pass'] for r in station_rows)}),flush=True)
