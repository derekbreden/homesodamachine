#!/usr/bin/env python3
"""Read the integral latch against the current production tee/valve interfaces.

Use Python -c to import and call main() while a production CAD build is active;
the production assembly's imports have their own manual-build entry-point lock.
Only evidence in this study folder is written. This does not install the latch
in the production carrier or qualify the full carrier assembly sequence.
"""
from __future__ import annotations
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import cadquery as cq

HERE=Path(__file__).resolve().parent
ROOT=next(p for p in HERE.parents if (p/'hardware/scripts').is_dir())


def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec)
    sys.modules[name]=module
    spec.loader.exec_module(module)
    return module


def main():
    coupon=load('integral_coupon_context',HERE/'integral_latch_coupon.py')
    region=load('integral_tee_context',ROOT/'hardware/printed-parts/enclosure/tee-readiness/verify_tee_integration.py')
    inputs=[HERE/'integral_latch_coupon.py',HERE/'check_production_context.py',
            *(ROOT/p for p in region.INPUTS)]
    def hashes():
        return {str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs}
    before=hashes()
    lift,carry,stood=region.small_placed_region()
    ea,ml,carrier=region.ea,region.ml,region.carrier
    solids={n:s for n,s,_ in stood}
    plate=ea.collet_plate_spec(carry,ea.pump_tray_stations(solids))
    spec=ea.tee_carrier_spec(carry,stood,plate)
    mismatch=carrier.placement_mismatches(spec)
    if mismatch:raise ValueError(mismatch)
    x0,y0,z0=0.,spec.web_fore_y,spec.web_z[0]
    box,union=coupon.box,coupon.union
    rows=[];issues=[]
    def read(name,a,b,expected_clear=True):
        overlap=a.intersect(b).Volume()
        passed=overlap<1e-5 if expected_clear else overlap>1e-5
        rows.append({'check':name,'overlap_mm3':overlap,'pass':passed,'expected_clear':expected_clear})
        if not passed:issues.append(name)
        return overlap
    def pose(shape,dy=0.,dx=0.):
        return shape.translate((x0+dx,y0+dy,z0))
    wall=union([coupon.flexible_wall(coupon.DEFLECTION),coupon.lip(coupon.DEFLECTION)])
    relaxed=union([coupon.flexible_wall(),coupon.lip()])
    flange=box((-spec.flange_x,spec.flange_x),spec.flange_y,spec.flange_z)
    # This flange follows the carrier, so the relative clearance is identical
    # throughout the operating travel. Test the complete free-wall family.
    for i in range(6):
        amount=coupon.DEFLECTION*i/5
        form=union([coupon.flexible_wall(amount),coupon.lip(amount)])
        read(f'wall deflection {amount:.2f} / retained carrier flange',pose(form),flange)
    relief=box(coupon.RELIEF_X,(coupon.RELIEF_FORE,6.1),coupon.RELIEF_Z)
    for x in spec.tee_xs:
        backing=box((x-spec.trough_r+.01,x+spec.trough_r-.01),
            (spec.stub_relief_y+.01,spec.web_aft_y-.01),
            (spec.trough_top_z+.01,spec.web_z[1]-.01))
        read(f'X{x:.3f} retained upper tee backing / latch relief',pose(relief),backing)
    # Include all native valves/coils and all four tees at their corresponding
    # moving state. The coupon's outer hand-grip pads are deliberately excluded.
    fixed={n:s for n,s in solids.items() if n.startswith(('valve-','coil-'))}
    tool=coupon.release_tool()
    minimum={'wall_to_fixed_mm':None,'wall_to_tee_mm':None,'release_tool_to_fixed_mm':None}
    for label,dy in (('release',spec.release_offset_y),('connected',spec.connected_offset_y),('aft_limit',spec.aft_limit_offset_y)):
        moved=pose(wall,dy)
        for name,solid in fixed.items():
            read(f'{label} fully deflected latch / {name}',moved,solid)
            distance=moved.distance(solid)
            if minimum['wall_to_fixed_mm'] is None or distance<minimum['wall_to_fixed_mm']['distance']:
                minimum['wall_to_fixed_mm']={'distance':distance,'state':label,'part':name}
            read(f'{label} rear straight release-tool lane / {name}',pose(tool,dy),solid)
            distance=pose(tool,dy).distance(solid)
            if minimum['release_tool_to_fixed_mm'] is None or distance<minimum['release_tool_to_fixed_mm']['distance']:
                minimum['release_tool_to_fixed_mm']={'distance':distance,'state':label,'part':name}
        for name in ml.CARRIER_TEES:
            solid=ea.pose_manifold(ml.carrier_tee(name,dy)).translate((0,ea.PACK_Y,lift))
            read(f'{label} fully deflected latch / {name}',moved,solid)
            read(f'{label} rear straight release-tool lane / {name}',pose(tool,dy),solid)
            distance=moved.distance(solid)
            if minimum['wall_to_tee_mm'] is None or distance<minimum['wall_to_tee_mm']['distance']:
                minimum['wall_to_tee_mm']={'distance':distance,'state':label,'part':name}
    # Preserve the proven coupon left part, but explicitly read its extra outer
    # lap material at the current independent left-half seating inset. This is
    # a production integration constraint, not a reason to alter the coupon fit.
    lap=box(coupon.v1.LAP_X,(-6.,0.),(0.,coupon.v1.HEIGHT))
    clipped=lap.intersect(box((-100,spec.joint_reach_x),(-100,100),(-100,100)))
    lap_rows=[]
    for label,dy in (('release',spec.release_offset_y),('connected',spec.connected_offset_y),('aft_limit',spec.aft_limit_offset_y)):
        for name in ml.CARRIER_TEES:
            solid=ea.pose_manifold(ml.carrier_tee(name,dy)).translate((0,ea.PACK_Y,lift))
            for stage,dx in (('seated',0.),('left_half_inset',spec.entry_shoulder_inset_x)):
                original=pose(lap,dy,dx).intersect(solid).Volume()
                trimmed=pose(clipped,dy,dx).intersect(solid).Volume()
                lap_rows.append({'state':label,'stage':stage,'tee':name,
                    'original_v1_lap_overlap_mm3':original,'production_limit_lap_overlap_mm3':trimmed})
    input_change=before!=hashes()
    if input_change:issues.append('source inputs changed during check')
    report={'scope':'Integral wall, relief and rear release lane in current tee/valve context. The whole coupon is not a replacement production carrier.',
        'checks_pass':not issues,'production_ready':False,'source_inputs_sha256':before,
        'carrier_mapping':{'x':x0,'y':y0,'z':z0,'states_y':[spec.release_offset_y,spec.connected_offset_y,spec.aft_limit_offset_y]},
        'dimensions_mm':{'relief_right_x':coupon.RELIEF_X[1],
            'inner_tee_trough_left_x':min(x for x in spec.tee_xs if x>0)-spec.trough_r,
            'wall_max_deflected_local_y':coupon.WALL_AFT+coupon.DEFLECTION,
            'flange_low_local_z':spec.flange_z[0]-z0,
            'coupon_lap_tip_x':coupon.v1.LAP_X[1],'production_lap_tip_limit_x':spec.joint_reach_x,
            'required_non_key_lap_trim_x':coupon.v1.LAP_X[1]-spec.joint_reach_x,
            'release_probe_length_mm':25.-coupon.RELIEF_FORE-.1},
        'minimum_native_distances':minimum,'readings':rows,'issues':issues,
        'original_lap_production_inset_readings':lap_rows,
        'unqualified_tee_datums':region.tee.UNQUALIFIED_DATUMS,
        'limits':['The 1.2 mm lip, spring force, release tool gesture and printed layer durability need physical qualification.',
            'Current production tee axial proxies remain explicit in the reference.',
            'Full carrier insertion, stiffness, tie access, spring capture and printed support removal require the eventual integrated carrier.']}
    (HERE/'production-context.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({'checks_pass':not issues,'checks':len(rows),'issues':issues,
        'dimensions_mm':report['dimensions_mm'],'minimum_native_distances':minimum,
        'maximum_original_lap_inset_overlap_mm3':max(r['original_v1_lap_overlap_mm3'] for r in lap_rows)},indent=2))
    return int(bool(issues))


if __name__=='__main__':
    raise SystemExit(main())
