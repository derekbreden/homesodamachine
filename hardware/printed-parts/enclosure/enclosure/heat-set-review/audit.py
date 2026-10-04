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
from materialize_pump_cartridge import _declared_box

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

source_paths = (ENC / 'enclosure.py', ENC / '_enclosure_interface.py', _box_spec.ARTIFACT)
input_paths = (*source_paths, *(ENC / f'enclosure-{name}.step' for name in e.PIECE_COLORS))
input_hashes = {str(p.relative_to(ROOT)): sha(p) for p in input_paths}
box, bounds, box_path = _declared_box(_box_spec, e)
station_rows = []

def add(piece, family, seat, into, pilot, length, depth, minimum, supported=False):
    station_rows.append(dict(piece=piece, family=family, seat_mm=seat, into=into,
        pilot_mm=pilot, insert_length_mm=length, pocket_depth_mm=depth,
        minimum_wall_mm=minimum, supported=supported))

for xi, xe, sx, z in box.y_bosses:
    _, tip, end, _ = e._boss_x(xe,sx)
    add('front-top' if z>e.z_seam else 'front-bottom','Y seam',
        (tip,e._y_boss(box.y_joint),z),(sx,0,0),e.heatset_dia,e.heatset_len,
        abs(end-tip),1.6,True)
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
cap_split=e.cap_split_z(box.pack.pump_trays)
sets=e._cap_screws(box)[1]
for y,cutter in zip(e.cap_screw_ys(box.inner,box.pack.collet_plate),sets):
    add('pump-cartridge','pump clamp',(0,y,cap_split),(0,0,-1),e.heatset_dia,
        e.cap_heatset_len,cap_split-cutter.BoundingBox().zmin,1.6)
fore=box.outer[3]-e.socket_cap-e.c14_tunnel_len
for x,z in box.pack.c14:
    add('back-top','C14',(x,fore,z),(0,1,0),e.heatset_dia,e.heatset_len,
        e.heatset_depth,1.6,True)
x,z=e.pump_contact_station(box)
for piece,face,sgn in (('front-top',e.bay_back_y(box.pack.collet_plate),1),
    ('pump-cap',e.pump_cartridge_aft_y(box.pack.pump_trays,box.pack.collet_plate),-1)):
    for ex in e._pogo.ear_xs():
        add(piece,'pogo',(x+ex,face+sgn*(e._pogo.ear_back()+e.pogo_heatset_setback),z),(0,sgn,0),
            e.pogo_heatset_dia,e.pogo_heatset_len,e.pogo_heatset_len+e.pogo_heatset_relief,(1.5*2.3-e.pogo_heatset_dia)/2.0,True)

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
    row['stock_rule']='SPIROL general FDM boss ≥1.5× knurl OD; ZWMSSLL publishes no host-wall minimum' if row['family']=='pogo' else 'ruthex RX table minimum wall from recommended pilot'
    row['manufacturer_wall_pass']=row['stock_rule_pass'] if row['family']!='pogo' else None
    # This is an independent supplier constraint, not an equality between two CAD constants.
    expected_pilot = None if row['family'] == 'pogo' else (6.4 if row['family'] == 'compressor' else 4.0)
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
    row['missing_closed_blind_stock_mm3']=cap_probe.cut(shape).Volume()
    row['closed_blind_pass']=row['missing_closed_blind_stock_mm3']<=tol
    if row['family']=='pogo':
        mouth=seat-into*(e.pogo_heatset_setback-0.02)
        entry=cq.Solid.makeCylinder(2.3/2.0,e.pogo_heatset_setback-0.04,mouth,into)
        row['blocked_whole_knurl_entry_mm3']=entry.intersect(shape).Volume()
        row['insertion_access_pass']=row['blocked_whole_knurl_entry_mm3']<=tol
    elif row.get('entry_setback_mm'):
        mouth=seat-into*(row['entry_setback_mm']-0.02)
        entry=cq.Solid.makeCylinder(4.6/2.0,row['entry_setback_mm']-0.04,mouth,into)
        row['blocked_whole_knurl_entry_mm3']=entry.intersect(shape).Volume()
        row['insertion_access_pass']=row['blocked_whole_knurl_entry_mm3']<=tol
        row['screw_reach_pass']=row['nominal_thread_reach_mm']>=row['insert_length_mm'] and row['nominal_blind_tip_clearance_mm']>=0.5

seam=[]
for xi,xe,sx,z in box.y_bosses:
    seat,tip,blind,cap=e._boss_x(xe,sx)
    y=e._y_boss(box.y_joint)
    back=shapes['back-top' if z>e.z_seam else 'back-bottom']
    xa,xb=sorted((seat,tip))
    strip=e._ybox(xa,xb,box.y_joint,y-e.screw_clear_dia/2.0,
                  z-e.screw_clear_dia/2.0,z+e.screw_clear_dia/2.0)
    seam.append(dict(side='west' if sx>0 else 'east',xyz_mm=[xe,y,z],
                     fore_edge_ligament_mm=y-box.y_joint-e.screw_clear_dia/2.0,
                     shank_mm=abs(tip-seat),
                     projected_strip_area_mm2=(y-box.y_joint-e.screw_clear_dia/2.0)*abs(tip-seat),
                     missing_strip_stock_mm3=strip.cut(back).Volume(),
                     screw_tip_clearance_mm=abs(blind-seat)-e.screw_len,
                     insert_blind_relief_mm=abs(blind-tip)-e.heatset_len,
                     inboard_cap_mm=abs(cap-blind)))

final_hashes = {str(p.relative_to(ROOT)): sha(p) for p in input_paths}
inputs_unchanged = final_hashes == input_hashes
report={'generated_utc':datetime.now(timezone.utc).isoformat(),'scope':'Full installed insert envelopes in retained native STEP solids; supported-face clearance is included. No printed fit, pullout, torque, transport or drop qualification.',
    'source_sha256':{str(p.relative_to(ROOT)): input_hashes[str(p.relative_to(ROOT))] for p in source_paths},
    'native_step_sha256':{name: input_hashes[str((ENC/f'enclosure-{name}.step').relative_to(ROOT))] for name in shapes},
    'inputs_unchanged': inputs_unchanged,
    'stations':station_rows,'seam_stations':seam,
    'sources':{'ruthex':'https://www.igo3d.com/mediafiles/Sonstiges/Ruthex/ruthex_Datenblatt_RX-Serie.pdf',
    'spirol':'https://www.spirol.com/resources/white-papers/how-to-select-a-threaded-insert-for-your-3d-printed-assembly/'},
    'status':'pass' if inputs_unchanged and all(r['stock_rule_pass'] and r['blind_relief_pass'] and r['pocket_clear_pass'] and r['closed_blind_pass'] and r.get('insertion_access_pass',True) and r.get('screw_reach_pass',True) and r['manufacturer_pilot_pass'] is not False for r in station_rows) and all(r['missing_strip_stock_mm3']<=tol and r['screw_tip_clearance_mm']>=0.5-1e-6 for r in seam) else 'fail'}
(Path(__file__).parent/'geometry-check.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'stations':len(station_rows),'failed_known_wall':sum(r['stock_rule_pass'] is False for r in station_rows),
    'failed_depth':sum(not r['blind_relief_pass'] for r in station_rows),'blocked':sum(not r['pocket_clear_pass'] for r in station_rows)}),flush=True)
