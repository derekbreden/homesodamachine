"""Production manifold derivation and bounded inner-web backing verification.

The frozen study supplies collision-free paths. Exact native subset checks carry
those paths to this carrier; positive stock, section floors and the production
interface are checked independently here. This is not printed stiffness evidence.
"""
from __future__ import annotations

import contextlib
import hashlib
import io
import json
import os
from dataclasses import asdict
from pathlib import Path
import sys

os.environ.setdefault('HSM_NO_BUILD_LOCK', '1')
import cadquery as cq

HERE=Path(__file__).resolve().parent
ROOT=next(p for p in HERE.parents if (p/'hardware/scripts').is_dir())
STUDY=HERE/'simple-carrier-study'
sys.path[:0]=[str(ROOT/'hardware/manifold-layout'), str(HERE.parent/'tee-readiness')]
import enclosure_assembly as ea
import verify_tee_integration as small

carrier=ea._carrier


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def thin_section(shape, x):
    width=.02
    native=shape.intersect(carrier._box(x-width/2,x+width/2,80,145,160,225.025).val())
    mass=native.Volume()
    inertia=cq.Shape.matrixOfInertia(native)
    return {'area_mm2':mass/width,
            'Iy_geometric_mm4':inertia[1][1]/width-mass/width*width*width/12,
            'Iz_geometric_mm4':inertia[2][2]/width-mass/width*width*width/12}


def main():
    ml=ea.ml
    sources=[Path(__file__), HERE/'tee_carrier.py', HERE/'_simple_carrier.py',
             HERE/'_carrier_motion.py', Path(ea.__file__), Path(ml.__file__),
             Path(small.__file__), Path(ml.vlv.__file__)]
    before={str(p.relative_to(ROOT)):sha(p) for p in sources}
    frozen=json.loads((STUDY/'artifact-manifest.json').read_text())
    required=['left-concept.step','right-concept.step','right-structural-body.step',
              'section-stock-checks.json','inputs/placed-neighbors/manifest.json']
    for name in required:
        if sha(STUDY/name)!=frozen['files'][name]['sha256']:
            raise ValueError('Frozen study input changed: '+name)
    rows=[]
    def check(label,value,maximum=1e-5):
        value=float(value)
        row={'check':label,'value':value,'maximum':float(maximum),'pass':value<=maximum}
        rows.append(row)
        if not row['pass']:raise ValueError(f'{label}: {value} > {maximum}')

    # These are the same complete manifold producers and carrier state choices
    # used by build_pack, without unrelated refrigeration/enclosure construction.
    datum=ea.posed_manifold(ml.CARRIER_RELEASE)
    squeeze=ea.posed_manifold(ml.CARRIER_SQUEEZE)
    posed=ea.posed_manifold(ml.CARRIER_STATES[ea.CARRIER_ASSEMBLY_STATE])
    lift=(ea.PACK_CROWN+ea._enc._interface.manifold_rise-ml.CARRIER_DROP
          -min(ea.box(s).zmin for n,s,c in datum if n in ('tube-fluid-17','tube-fluid-27')))
    carry=ea.manifold_carry(lift)
    stood=[(n,s.translate((0,ea.PACK_Y,lift)),c) for n,s,c in posed]
    squeezed=[(n,s.translate((0,ea.PACK_Y,lift)),c) for n,s,c in squeeze]
    solids={n:s for n,s,c in squeezed}
    trays=ea.pump_tray_stations({n:s for n,s,c in stood})
    plate=ea.collet_plate_spec(carry,trays)
    spec=ea.tee_carrier_spec(carry,squeezed,plate)
    mismatches=carrier.placement_mismatches(spec)
    if mismatches:raise ValueError(f'Production-derived carrier mismatch: {mismatches}')
    interface=ea.tee_carrier_interface(spec,plate,squeezed)
    print(json.dumps({'phase':'actual_producer_derivation_pass','side_web_z0':spec.side_web_z0,
                      'side_web_added_y':spec.side_web_added_y,'mismatches':mismatches}),flush=True)

    small_lift,_small_carry,small_stood=small.small_placed_region()
    check('actual / small placed-region lift',abs(lift-small_lift),1e-6)
    small_solids={n:s for n,s,c in small_stood}
    neighbors=json.loads((STUDY/'inputs/placed-neighbors/manifest.json').read_text())
    projection=[]
    entry=-(ea._vtray.grip()+spec.slide_air)
    for name in ('coil-v-c','coil-v-d'):
        native=solids[name]
        source_row=neighbors['bodies'][name]
        path=STUDY/'inputs/placed-neighbors'/source_row['brep']
        if sha(path)!=source_row['sha256']:raise ValueError('Frozen coil changed')
        reference=cq.Shape.importBrep(str(path))
        for label,other in (('small placed-region',small_solids[name]),('frozen fixture',reference)):
            check(name+' '+label+' missing mm3',native.cut(other).Volume())
            check(name+' '+label+' extra mm3',other.cut(native).Volume())
        b=native.BoundingBox()
        rear=spec.web_aft_y+spec.side_web_added_y-entry+spec.slide_air
        feature=native.intersect(carrier._box(b.xmin-1,b.xmax+1,b.ymin-1,rear,b.zmin-1,b.zmax+1).val())
        top=feature.BoundingBox().zmax
        air=spec.side_web_z0-top
        check(name+' projection lacks required entry air',spec.slide_air-air,1e-6)
        projection.append({'component':name,'entry_offset_y_mm':entry,
            'backing_depth_mm':spec.side_web_added_y,'projection_rear_y_mm':rear,
            'projection_top_z_mm':top,'backing_floor_z_mm':spec.side_web_z0,
            'air_above_forward_projection_mm':air,'required_air_mm':spec.slide_air,
            'projection_formula':'web_aft_y + side_web_added_y - valve_entry_y + slide_air'})

    parts=carrier.assembly_parts(spec)
    y=spec.web_aft_y
    cutter=carrier._box(-spec.flange_x,-13,y+.90,y+.95,spec.side_web_z0,spec.flange_z[0]).val().fuse(
        carrier._box(15,spec.flange_x,y+.90,y+.95,spec.side_web_z0,spec.flange_z[0]).val())
    delta=[]
    for name,filename in (('left','left-concept.step'),('right','right-concept.step'),
                          ('right_structural','right-structural-body.step')):
        old=cq.importers.importStep(str(STUDY/filename)).val()
        new=parts[name]
        removed=old.cut(new)
        check(name+' is not a subset of frozen body',new.cut(old).Volume())
        check(name+' removal outside declared 0.05 backing strip',removed.cut(cutter).Volume())
        expected=old.cut(cutter)
        check(name+' bounded cutter mismatch extra',new.cut(expected).Volume())
        check(name+' bounded cutter mismatch missing',expected.cut(new).Volume())
        check(name+' native solid count',abs(len(new.Solids())-1),0)
        if not new.isValid():raise ValueError(name+' is not valid')
        delta.append({'part':name,'frozen_volume_mm3':old.Volume(),'current_volume_mm3':new.Volume(),
                      'removed_volume_mm3':removed.Volume(),'added_volume_mm3':new.cut(old).Volume()})
    # The changed stock ends below the shelf; joint, guide, spring cup, trough
    # bearing and handhold roots retain the frozen native stock and contacts.
    joint_zone=carrier._box(-13,15,80,145,160,250).val()
    check('backing cutter crosses centre-joint region',cutter.intersect(joint_zone).Volume())
    for x in spec.tee_xs:
        shape=parts['left' if x<0 else 'right']
        stock=carrier._box(x-spec.trough_r+.01,x+spec.trough_r-.01,
            spec.stub_relief_y+.01,spec.web_aft_y-.01,spec.trough_top_z+.01,spec.web_z[1]-.01).val()
        check(f'X{x:g} retained complete upper backing',stock.cut(shape).Volume())
    old_sections=json.loads((STUDY/'section-stock-checks.json').read_text())
    beam=cq.Compound.makeCompound([parts['left'],parts['right_structural']])
    sections=[{'x_mm':r['x_mm'],'current':thin_section(beam,r['x_mm']),
               'screwed_reference':r['screwed_reference']} for r in old_sections['rows']]
    minima={k:min(({'x_mm':r['x_mm'],'value':r['current'][k]} for r in sections),key=lambda r:r['value'])
            for k in ('area_mm2','Iy_geometric_mm4','Iz_geometric_mm4')}
    reference_minima=old_sections['sampled_minima']['screwed_reference']
    ratios={}
    for k in ('Iy_geometric_mm4','Iz_geometric_mm4'):
        check(k+' sampled floor below frozen reference',reference_minima[k]['value']-minima[k]['value'],0)
        ratios[k]={'sampled_minimum_ratio':minima[k]['value']/reference_minima[k]['value'],
                   'least_local_ratio':min(r['current'][k]/r['screwed_reference'][k] for r in sections)}
    out=io.StringIO()
    with contextlib.redirect_stdout(out):result=carrier.selftest(spec)
    check('production carrier selftest exit code',result,0)
    after={str(p.relative_to(ROOT)):sha(p) for p in sources}
    if after!=before:raise ValueError('Relevant sources changed during verification')
    report={'status':'bounded_backing_and_actual_producer_verified','source_sha256':after,
        'frozen_study_manifest_sha256':sha(STUDY/'artifact-manifest.json'),
        'scope':'Actual production manifold derivation, exact carrier subset, changed-region bounds, local positive stock/contacts and native sections. Full current Box and enclosure generation remain separate.',
        'frozen_study_projection_limitation':'The frozen check_valve_entry.py projection used literal 0.90 mm while its carrier used 0.95 mm. Its collision sweeps remain valid. Its stated 0.25 mm projection air does not qualify that frozen thicker backing.',
        'current_projection_basis':'Live spec.side_web_added_y is used in the same projection as tee_carrier_spec; 0.25 mm required air is unchanged.',
        'placement_spec':asdict(spec),'interface':interface,'projection':projection,
        'native_delta':delta,'checks':rows,'all_checks_pass':all(r['pass'] for r in rows),
        'sections':sections,'sampled_minima':minima,'reference_sampled_minima':reference_minima,
        'section_moment_ratios':ratios,
        'section_limit':'Geometric sections only; sampled minima do not establish uniform local improvement, joint transfer or assembled stiffness. Flexible retaining wall excluded.',
        'motion_carry_forward':'Current halves are exact subsets of frozen collision-free halves. Identical placement, interface, joint, guide and cup stock carry the frozen noninterference results; native positive stock/contact and section checks are independent.',
        'selftest':{'exit_code':result,'output':out.getvalue()},
        'physical_trial':'Complete enclosure assembly tests actual spring feel, both-end retention, handling and full-width rigidity.'}
    (HERE/'entry-backing-check.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({'status':report['status'],'checks':len(rows),'projection':projection,
                      'native_delta':delta,'sampled_minima':minima,'section_moment_ratios':ratios},indent=2),flush=True)


if __name__=='__main__':main()
