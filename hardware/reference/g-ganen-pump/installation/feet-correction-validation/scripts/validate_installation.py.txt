"""Bounded native G Ganen installation check; no production artifact is overwritten.

The cap frame comes from the retained foam assembly. The candidate gate cruise is
explicit and is rechecked by the eventual complete production assembly build.
"""
from pathlib import Path
from argparse import ArgumentParser
import hashlib
import json
import math
import sys
import time
import cadquery as cq

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
sys.path.insert(0, str(ROOT/'hardware/manifold-layout'))
sys.path.insert(0, str(ROOT/'hardware/printed-parts/cold-core/foam-cap'))
import enclosure_assembly as ea
import foam_cap as cap
import g_ganen_installation as pump


def bounds(shape):
    b=shape.BoundingBox()
    return [[b.xmin,b.ymin,b.zmin],[b.xmax,b.ymax,b.zmax]]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(*, include_hoses=True, output=HERE/'native-installation-check.json'):
    started=time.monotonic()
    inputs=[Path(ea.__file__), Path(ea._lines.__file__), Path(ea._cci.__file__),
            HERE/'g_ganen_installation.py', HERE/'validate_installation.py',
            Path(pump.stock_foot.__file__),
            pump.envelope.NATIVE, pump.envelope.HERE/'native-validation.json',
            pump.REFERENCE/'reference-parameters.json', Path(ea.FOAM_STEP),
            Path(cap.__file__)]
    before={str(p.relative_to(ROOT)):sha(p) for p in inputs}
    facts_path=ROOT/'hardware/manifold-layout/enclosure-assembly.facts.json'
    facts=json.loads(facts_path.read_text())
    bb=facts['bodies']['bulkhead-flavor-a']
    gate=(bb[2]+bb[5])/2
    f0,_=ea.build_foam(0.)
    foam,fc=ea.build_foam(ea._enc.rear_plane_y-ea._enc.rear_seam_clear-ea.box(f0).ylen)
    shape,carry=ea.build_water_pump(foam,gate)
    core_y_shift=ea.box(foam).ymax-facts['bodies']['foam-assembly'][4]
    print('placed pump',bounds(shape),flush=True)
    su,sc=ea.build_suction_chain(fc)
    di,dc=ea.build_discharge_chain(fc)
    vk,vc=ea.build_vk(sc)
    placed={'g-ganen-pump':shape,'suction-chain':su,'discharge-chain':di,'vk-solenoid':vk,'foam-assembly':foam}
    carries={'g-ganen-pump':carry,'suction-chain':sc,'discharge-chain':dc,'vk-solenoid':vc,'foam-assembly':fc}
    F=ea._lines.frames(placed,carries)
    checks=[]
    def check(label,value,limit,relation='<='):
        good=value<=limit if relation=='<=' else value>=limit
        checks.append({'check':label,'value':value,'limit':limit,'relation':relation,'pass':good})
        print(label,value,'PASS' if good else 'FAIL',flush=True)
    mount_rows=ea.pump_mount_rows(fc,carry)
    for i,(got,want) in enumerate(mount_rows):check(f'cap mount axis {i}',math.dist(got,want),ea.MOUNT_TOL)
    check('bearing datum on cap',abs(pump.placed_bearing_z(carry)-ea.cap_face(foam)),1e-7)
    check('rear rigid face has declared core-rear clearance',
          abs(ea.box(foam).ymax-pump.rigid_shape().moved(carry.where).BoundingBox().ymax-pump.REAR_CLEARANCE),1e-6)
    check('flavor gate unchanged',abs(ea.flavor_storey(gate,carry)-gate),1e-7)
    check('flow local discharge maps enclosure -X',carry(pump.discharge())[1][0],-.999)
    for name,s in [('suction-chain',su),('discharge-chain',di),('vk-solenoid',vk)]:
        b=ea.box(s);wanted=list(facts['bodies'][name])
        wanted[1]+=core_y_shift;wanted[4]+=core_y_shift
        got=[b.xmin,b.ymin,b.zmin,b.xmax,b.ymax,b.zmax]
        check(name+' cap-relative placed bounds',max(abs(x-y) for x,y in zip(got,wanted)),1e-5)
        check(name+' pump clearance',s.distance(shape),1.,'>=')
    # Four instances of the same purchased foot, with their rail clips engaged.
    foot_rows=[]
    for row in pump.mount_stations():
        foot=pump.build_parts()[row['id']+'_observed_rubber_slider_envelope']
        b=foot.BoundingBox()
        start, end = row['rail_engagement_x_mm']
        check(row['id']+' complete clip above rail start',start,pump.RAIL_X[0],'>=')
        check(row['id']+' complete clip below rail end',end,pump.RAIL_X[1])
        at_end = abs(start-pump.RAIL_X[0]) if row['id'].startswith('head_') else abs(end-pump.RAIL_X[1])
        check(row['id']+' clip at selected outer rail end',at_end,1e-7)
        check(row['id']+' shared pad thickness',abs(row['pad_thickness_mm']-7.),1e-7)
        p=carry((row['station_mm'],(0,0,1)))[0]
        z0=pump.placed_bearing_z(carry)+min(t['over_washer_min_mm'] for t in row['observed_pad_top_mm'])+pump.WASHER_T
        tool=cq.Solid.makeCylinder(pump.WASHER_OD/2,45.,cq.Vector(p[0],p[1],z0))
        gap=tool.distance(pump.rigid_shape().moved(carry.where))
        check(row['id']+' washer and straight driver corridor to rigid pump',gap,.5,'>=')
        foot_rows.append({**row,'selected_native_bounds_mm':bounds(foot),'tool_rigid_gap_mm':gap})
    routes=[]
    hose_solids=[]
    ea._routing.BLOCKED.clear()
    for fn in ((ea._lines._water_7,ea._lines._water_6) if include_hoses else ()):
        r=fn(F);tube=ea._routing.tube(r)
        check(r.id+' native invalid',int(not tube.isValid()),0)
        check(r.id+' smallest seated bend radius',min(r.radii.values()),ea._lines.HOSE_BEND,'>=')
        # At the connected tip the hose meets its own fitting. A volume check
        # distinguishes that intended end-plane contact from a route entering
        # the molded port or any other measured pump component.
        tb=tube.BoundingBox()
        overlap=[]
        for name,part in pump.build_parts().items():
            part=part.moved(carry.where)
            pb=part.BoundingBox()
            boxes_meet=all(getattr(tb,axis+'min')<=getattr(pb,axis+'max') and
                           getattr(pb,axis+'min')<=getattr(tb,axis+'max') for axis in 'xyz')
            overlap.append((name,part.intersect(tube).Volume() if boxes_meet else 0.))
        peak=max(overlap,key=lambda x:x[1])
        check(r.id+' maximum native pump-component overlap',peak[1],1e-6)
        others={'vk-solenoid':vk, 'opposite chain':di if r.id=='water-7' else su}
        distances={n:tube.distance(s) for n,s in others.items()}
        for n,d in distances.items():check(r.id+' to '+n,d,1.,'>=')
        routes.append({'id':r.id,'waypoints_mm':r.pts,'radii_mm':r.radii,
                       'minimum_requested_radius_mm':ea._lines.HOSE_BEND,
                       'native_valid':tube.isValid(),'distance_mm':distances,
                       'pump_component_overlap_mm3':dict(overlap)})
        hose_solids.append((r.id,tube))
    blocked=list(ea._routing.BLOCKED)
    if include_hoses:check('hose route blockers',len(blocked),0)
    # Build the actual printed cap and lid, without calling their exporting main.
    cup=cap.add_deck_mounts(cap.build_foam_cap()).val()
    lid=cap.add_side_anchors(cap.add_chain_anchors(cap.add_cradles(
        cap.cut_deck_mounts_lid(cap.build_foam_cap_lid()),cap.lid_total_height),
        cap.lid_total_height),cap.lid_total_height).val()
    check('cap cup native invalid',int(not cup.isValid()),0)
    check('cap lid native invalid',int(not lid.isValid()),0)
    check('cap cup solid count',abs(len(cup.Solids())-1),0)
    check('cap lid solid count',abs(len(lid.Solids())-1),0)
    cup_world=ea._foam._spin(cup).translate((0,0,ea._foam.cap_face_z-cap.lid_total_height-cap.top_cap_height)).moved(fc.where)
    lid_world=ea._foam._spin(lid).translate((0,0,ea._foam.cap_face_z-cap.lid_total_height)).moved(fc.where)
    check('rigid pump to printed lid',pump.rigid_shape().moved(carry.where).distance(lid_world),1.,'>=')
    for name,tube in hose_solids:
        check(name+' printed lid clearance',tube.distance(lid_world),1.,'>=')
    screw_rows=[]
    for row in pump.mount_stations():
        p=carry((row['station_mm'],(0,0,1)))[0]
        pad_min=min(t['over_washer_min_mm'] for t in row['observed_pad_top_mm'])
        pad_max=max(t['over_washer_max_mm'] for t in row['observed_pad_top_mm'])
        low=pump.placed_bearing_z(carry)+pad_min+pump.WASHER_T-pump.SCREW_LENGTH
        high=pump.placed_bearing_z(carry)+pad_max+pump.WASHER_T
        shank=cq.Solid.makeCylinder(pump.SCREW_D/2,high-low,cq.Vector(p[0],p[1],low))
        for name,s in [('cup',cup_world),('lid',lid_world)]:
            check(row['id']+' M3 shank envelope printed '+name+' overlap',s.intersect(shank).Volume(),1e-6)
        reach_min=pump.SCREW_LENGTH-pad_max-pump.WASHER_T-cap.lid_total_height
        reach_max=pump.SCREW_LENGTH-pad_min-pump.WASHER_T-cap.lid_total_height
        check(row['id']+' nominal full insert engagement',reach_min,ea._cci.deck_mount_insert_length,'>=')
        screw_rows.append({'id':row['id'],'free_pad_stack_mm':[pad_min,pad_max],
                           'insert_reach_mm':[reach_min,reach_max],
                           'physical_loaded_stack_qualified':False})
    floor=cap.deck_boss_z_top('g-ganen-pump')-ea._cci.deck_mount_bore_depth
    check('blind bore remaining floor',floor,ea._cci.wall_and_floor_thickness,'>=')
    # Independent occupied-column stock against non-pump cup features.
    plain=cap.build_foam_cap().val()
    expected=len(pump.mount_stations())*math.pi*(ea._cci.deck_mount_boss_radius**2*(cap.deck_boss_z_top('g-ganen-pump')-ea._cci.wall_and_floor_thickness)-ea._cci.deck_mount_bore_radius**2*ea._cci.deck_mount_bore_depth)
    check('added four columns exact volume vs clear stock',abs((cup.Volume()-plain.Volume())-expected),1e-4)
    after={str(p.relative_to(ROOT)):sha(p) for p in inputs}
    if before!=after:raise RuntimeError('Installation inputs changed during native validation')
    out={'schema':'g-ganen-installation/1','inputs':before,
         'gate_fixture':{'source':str(facts_path.relative_to(ROOT)),'sha256':sha(facts_path),'z_mm':gate,
                         'qualification':'retained baseline gate; complete candidate assembly still required'},
         'local_to_world':{'z_rotation_degrees':pump.YAW,'origin_mm':carry(pump.bearing_datum())[0]},
         'core_translation_from_retained_facts_y_mm':core_y_shift,
         'installed_bounds_mm':bounds(shape),'suction':carry(pump.suction()),'discharge':carry(pump.discharge()),
         'selected_feet':foot_rows,'printed_cap_stations_mm':ea._cci.deck_mount_xy('g-ganen-pump'),
         'mount_rows':mount_rows,'screw_stacks':screw_rows,'washer_od_mm':pump.WASHER_OD,'washer_t_mm':pump.WASHER_T,
         'bore_depth_mm':ea._cci.deck_mount_bore_depth,'remaining_floor_mm':floor,
         'routes':routes,'routes_checked':include_hoses,'route_blockers':blocked,
         'checks':checks,'all_pass':all(r['pass'] for r in checks),
         'physical_checks_open':['Actual M3 passes all four complete slots','Selected washer seats flat and clears rubber upstand','Loaded rubber compression and screw engagement','Hose insertion and clamp retention'],
         'elapsed_seconds':time.monotonic()-started}
    output.write_text(json.dumps(out,indent=2)+'\n')
    print('All pass:',out['all_pass'],'seconds',out['elapsed_seconds'],flush=True)
    if not out['all_pass']:raise SystemExit(1)

if __name__=='__main__':
    parser=ArgumentParser(description=__doc__)
    parser.add_argument('--skip-hoses',action='store_true',
                        help='Check mounts and neighbors; hose qualification is a separate current route check')
    parser.add_argument('--output',type=Path,default=HERE/'native-installation-check.json')
    args=parser.parse_args()
    run(include_hoses=not args.skip_hoses,output=args.output)
