#!/usr/bin/env python3
"""Bounded native front-top release-bearing, support-access and working-state checks.

This checks the emitted shell fixture and current carrier at three named stations.
It does not sweep the complete insertion path or qualify support bodies from a slice.
"""
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p/'hardware/scripts').is_dir())
INTEGRATION = ROOT/'hardware/printed-parts/enclosure/tee-readiness/tee-integration.json'


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    fixture = json.loads((HERE/'fixture.json').read_text())
    integration = json.loads(INTEGRATION.read_text())
    inputs = {**fixture['source_sha256'], **fixture['input_sha256'],
              **integration['inputs_sha256'], fixture['step']: fixture['step_sha256'],
              str(INTEGRATION.relative_to(ROOT)): sha(INTEGRATION),
              str(Path(__file__).relative_to(ROOT)): sha(__file__)}
    for path,digest in inputs.items():
        if sha(ROOT/path) != digest:
            raise ValueError('Input changed before native interface checks: '+path)
    os.environ['HSM_NO_BUILD_LOCK'] = '1'
    sys.path[:0] = [str(ROOT/'hardware/printed-parts/enclosure/enclosure'),
                    str(ROOT/'hardware/printed-parts/enclosure/tee-carrier')]
    import cadquery as cq
    import enclosure as enc
    import tee_carrier as carrier
    wall = cq.importers.importStep(str(ROOT/fixture['step'])).val()
    plate = integration['collet_plate']
    spec = carrier.DEFAULT_SPEC
    rows = []

    def reading(label,amount,limit=1e-5):
        passed = amount <= limit
        rows.append({'check':label,'volume_mm3':amount,'maximum_mm3':limit,'pass':passed})
        print(('PASS ' if passed else 'FAIL ')+label+f': {amount:.8g} mm3',flush=True)
        if not passed:
            raise ValueError(label)

    for x,z in plate['holes']:
        annulus = enc._ycyl(5.0,x,z,plate['aft_y']-.10,plate['aft_y']-.01).cut(
            enc._ycyl(plate['hole_d']/2+.01,x,z,plate['aft_y']-.11,plate['aft_y']))
        reading(f'X{x:g} full annulus R4.26..5.0 retains native stock',annulus.cut(wall).Volume())
        corridor = enc._ycyl(plate['hole_d']/2-.01,x,z,enc.front_plane_y-1,plate['aft_y']+.01)
        reading(f'X{x:g} circular bore has a straight open fore extraction lane',
                corridor.intersect(wall).Volume())
    halves = {label:cq.importers.importStep(str(ROOT/
        f'hardware/printed-parts/enclosure/tee-carrier/enclosure-tee-carrier-{label}.step')).val()
        for label in ('left','right')}
    for state,dy in (('release',spec.release_offset_y),('connected',spec.connected_offset_y),
                     ('aft_limit',spec.aft_limit_offset_y)):
        for label,shape in halves.items():
            moved = shape.translate((0,dy,0))
            b = moved.BoundingBox()
            region = enc._ybox(b.xmin-.01,b.xmax+.01,b.ymin-.01,b.ymax+.01,b.zmin-.01,b.zmax+.01)
            local_wall = wall.intersect(region)
            reading(f'{state} {label} native carrier / actual front-top',moved.intersect(local_wall).Volume())
        for index,head in enumerate(carrier.tie_head_envelopes(spec),1):
            reading(f'{state} tie lock {index} / actual front-top',
                    head.translate((0,dy,0)).intersect(wall).Volume())
    for path,digest in inputs.items():
        if sha(ROOT/path) != digest:
            raise ValueError('Input changed during native interface checks: '+path)
    record = {
        'status':'pass','created_at_utc':datetime.now(timezone.utc).isoformat(),
        'input_sha256':inputs,'checks':rows,'checks_pass':True,
        'assembly_current':False,'production_enclosure_released':False,
        'scope':'Emitted current measured-branch front-top, three discrete carrier working stations, release annulus and empty-bay access. SeaFlo-sized Box baseline.',
        'release_bearing':{'bore_diameter_mm':plate['hole_d'],
            'native_annular_probe_radii_mm':[plate['hole_d']/2+.01,5.0],
            'minimum_physical_terminal_ring_radius_qualified':False},
        'support_access':{'print_up':'+Z','bore_axis':'Y',
            'neck_length_mm':plate['aft_y']-plate['fore_y'],
            'open_fore_corridor_diameter_mm':plate['hole_d']-.02,
            'removal_state':'Empty cartridge bay before pump/cartridge or tee installation.',
            'actual_support_bodies_reviewed':False,'physical_cleanup_tested':False,
            'limit':'The native straight lane is clear. A production slice must still show each connected support body and any branches can leave that lane.'},
        'complete_insertion_sweep_checked':False,'continuous_motion_sweep_checked':False,
        'remaining':['G Ganen integration and final carrier structure are separate.',
                     'Physical ring bearing, spring capture and assembled stiffness are unqualified.',
                     'Current production slice and support-body removal review are pending.']}
    (HERE/'native-interface-check.json').write_text(json.dumps(record,indent=2)+'\n')
    print(f'PASS {len(rows)} bounded native interface checks',flush=True)


if __name__=='__main__':main()
