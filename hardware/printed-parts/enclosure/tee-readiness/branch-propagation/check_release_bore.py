#!/usr/bin/env python3
"""Bounded source-geometry check of the circular tube passage and flat release face.

No native full front-top or production slice is qualified by this check.
"""
import hashlib
import json
import math
import os
from pathlib import Path
import sys

os.environ['HSM_NO_BUILD_LOCK']='1'
HERE=Path(__file__).resolve().parent
ROOT=next(p for p in HERE.parents if (p/'hardware/scripts').is_dir())
sys.path[:0]=[str(HERE.parent),str(ROOT/'hardware/printed-parts/enclosure/enclosure')]
import verify_tee_integration as region


def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    before={str(p.relative_to(ROOT)):sha(p) for p in [
        ROOT/'hardware/reference/tee-connector/tee_connector.py',
        ROOT/'hardware/reference/jg-pp0208e-tee/branch-operating-measurements.json',
        ROOT/'hardware/manifold-layout/manifold_layout.py',
        ROOT/'hardware/manifold-layout/enclosure_assembly.py',
        ROOT/'hardware/printed-parts/enclosure/enclosure/enclosure.py',
        ROOT/'hardware/printed-parts/enclosure/tee-carrier/tee_carrier.py',
        ROOT/'hardware/reference/kamoer-kphm400/kamoer-kphm400.step',Path(__file__)]}
    ml,ea,enc,tee=region.ml,region.ea,region.enc,region.tee
    ml._tee_solid=tee.build()
    lift,carry,stood=region.small_placed_region()
    trays=ea.pump_tray_stations({n:s for n,s,_c in stood})
    plate=ea.collet_plate_spec(carry,trays)
    spec=ea.tee_carrier_spec(carry,stood,plate)
    if region.carrier.placement_mismatches(spec):raise ValueError('Carrier datums are not synchronized')
    interface=ea.tee_carrier_interface(spec,plate,stood)
    inner=(*enc.interior_x(),enc.front_plane_y,enc.rear_plane_y)
    wall=enc._tee_wall(inner,0,plate,(0,0,plate['z1']))
    rows=[]
    def check(name,value,limit=1e-6):
        rows.append({'check':name,'value':float(value),'maximum':limit,'pass':value<=limit})
        if value>limit:raise ValueError(f'{name}: {value} exceeds {limit}')
    for x,z in plate['holes']:
        annulus=enc._ycyl(5.0,x,z,plate['aft_y']-.10,plate['aft_y']-.01).cut(
            enc._ycyl(plate['hole_d']/2+.01,x,z,plate['aft_y']-.11,plate['aft_y']))
        check(f'X{x:g} R4.26..5.0 release annulus missing stock',annulus.cut(wall).Volume())
        bore=enc._ycyl(plate['hole_d']/2-.001,x,z,plate['fore_y']-.1,plate['aft_y']+.1)
        check(f'X{x:g} complete axial opening obstructed',bore.intersect(wall).Volume())
        tube=enc._ycyl(tee.TUBE_D/2,x,z,plate['fore_y']-.1,plate['aft_y']+.1)
        check(f'X{x:g} tube passage obstructed',tube.intersect(wall).Volume())
    pressed=tee.depress_branch(ml._tee_solid,tee.BRANCH_COLLET_TRAVEL)
    fixed=enc._ybox(-20,20,tee.CAP_NEAR,tee.BRANCH_FIXED_END,-25,25)
    check('fixed collar and reduced barrel removed by release',ml._tee_solid.intersect(fixed).cut(pressed).Volume())
    check('nominal pressed branch face error',abs(pressed.BoundingBox().ymax-tee.BRANCH_PRESSED_REACH))
    check('source tee validity',0 if ml._tee_solid.isValid() and len(ml._tee_solid.Solids())==1 else 1)
    aft=enc.pump_cartridge_aft_y(trays,plate)
    for name,digest in before.items():
        if sha(ROOT/name)!=digest:raise ValueError('Input changed during check: '+name)
    report={'status':'pass','scope':__doc__,'inputs_sha256':before,'checks':rows,
            'source_tee_used_in_memory':True,'current_native_front_top_checked':False,
            'current_production_slice_checked':False,'physical_release_qualified':False,
            'plate':plate,'pump_trays':trays,'spring_stations':region.carrier.spring_stations(spec),
            'cartridge_aft_y':aft,'plate_running_air_mm':enc.bay_back_y(plate)-aft,
            'bore_diameter_mm':plate['hole_d'],'tube_radial_air_mm':(plate['hole_d']-tee.TUBE_D)/2,
            'annular_probe_radii_mm':[plate['hole_d']/2+.01,5.0],
            'annular_probe_area_mm2':math.pi*(5**2-(plate['hole_d']/2+.01)**2),
            'annular_probe_qualification':'Proves plate stock at a declared radius; R5.0 is not a caliper-qualified minimum terminal-ring radius.',
            'print_up':[0,0,enc.PIECE_PRINT_UP['front-top']],
            'bore_axis':[0,1,0],'release_neck_length_mm':plate['aft_y']-plate['fore_y'],
            'support_access':'The 3.175 mm cylindrical neck is open axially into the empty pump bay and the larger aft journal. Crown supports require removal before tees/cartridge installation. Final generated support bodies and complete front-top surroundings require the refreshed production slice.'}
    (HERE/'release-bore-check.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({'status':'pass','checks':len(rows),'tube_radial_air_mm':report['tube_radial_air_mm'],'annular_probe_area_mm2':report['annular_probe_area_mm2'],'plate_running_air_mm':report['plate_running_air_mm']},indent=2))


if __name__=='__main__':main()
