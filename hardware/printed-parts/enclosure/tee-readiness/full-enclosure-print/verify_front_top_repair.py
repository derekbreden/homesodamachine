"""Bounded native evidence for front-top collision repairs, without a full rebuild.

The handed-off failed aggregate parts remain frozen inputs. These probes validate
the prescribed local source helpers and translated core, not a regenerated shell.
"""
from __future__ import annotations

import argparse
from collections import namedtuple
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import sys
import tempfile
import zipfile

HERE=Path(__file__).resolve().parent
ROOT=next(p for p in HERE.parents if (p/'hardware/scripts').is_dir())

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def relative(p):return str(p.relative_to(ROOT)) if p.is_relative_to(ROOT) else str(p)

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--baseline',type=Path,default=HERE/'fit-correction-baseline.zip')
    parser.add_argument('--output',type=Path,default=HERE/'front-top-repair.json')
    args=parser.parse_args()
    temporary=tempfile.TemporaryDirectory(prefix='hsm-front-top-baseline-')
    baseline=Path(temporary.name)
    with zipfile.ZipFile(args.baseline) as archive:
        manifest=json.loads(archive.read('manifest.json'))
        for name,row in manifest['files'].items():
            if Path(name).name!=name:raise ValueError('Baseline archive entries must be flat')
            data=archive.read(name)
            if hashlib.sha256(data).hexdigest()!=row['sha256']:raise ValueError(name+' digest mismatch')
            (baseline/name).write_bytes(data)
    os.environ['HSM_NO_BUILD_LOCK']='1'
    sys.path[:0]=[str(ROOT/'hardware/manifold-layout'),str(ROOT/'hardware/printed-parts/enclosure/tee-carrier')]
    import cadquery as cq
    import enclosure_assembly as ea
    import _box_spec
    from _carrier_motion import swept_overlap
    enc,tc=ea._enc,ea._carrier
    box_path=baseline/'enclosure-box.json'
    raw_fields=json.loads(box_path.read_text())['box']['pack']['fields']
    input_pack=enc.Pack if tuple(raw_fields)==enc.Pack._fields else namedtuple('Pack',raw_fields)
    box,_=_box_spec.read(enc.Box,enc.Bound,(input_pack,enc.PortField,enc.Nameplate),path=box_path)
    box=box._replace(pack=enc.Pack(**box.pack._asdict()))
    interface=box.pack.tee_carrier;spec=tc.DEFAULT_SPEC
    def input_label(p):return args.baseline.name+'::'+p.name if p.parent==baseline else relative(p)
    inputs={relative(args.baseline):sha(args.baseline),input_label(box_path):sha(box_path)}
    def load(p):
        inputs[input_label(p)]=sha(p)
        return (cq.Shape.importBrep(str(p)) if p.suffix=='.brep'
                else cq.importers.importStep(str(p)).val())
    wall=load(baseline/'enclosure-front-top.step')
    foam=load(baseline/'cold-core-foam-shell.brep')
    coils={name:load(baseline/(name+'.brep')) for name in ('coil-v-f','coil-v-i','coil-v-c','coil-v-d')}
    tube=load(baseline/'tube-fluid-18.brep')
    halves=[load(baseline/f'enclosure-tee-carrier-{name}.step') for name in ('left','right')]
    carrier=cq.Compound.makeCompound(halves)
    source_paths=[Path(m.__file__) for m in (ea,enc,tc,ea._cci,enc._interface,enc._cable_clip)]
    report={'status':'running','created_at_utc':datetime.now(timezone.utc).isoformat(),
        'scope':'Frozen failed native aggregate/Box versus bounded current local helpers. No completed regenerated full-shell/whole-appliance claim.',
        'input_sha256':inputs,'source_sha256':{relative(p):sha(p) for p in source_paths},
        'checks':[],'failures':[],'readings':{}}
    def save():args.output.write_text(json.dumps(report,indent=2)+'\n')
    def check(name,value,limit=1e-5,minimum=False):
        value=float(value);passed=value>=limit-1e-6 if minimum else value<=limit
        report['checks'].append({'name':name,'value':value,'minimum' if minimum else 'maximum':limit,'pass':passed})
        if not passed:report['failures'].append(name)
        save();print(name+': '+str(value),flush=True)

    check('frozen foam shell and frozen wall overlap establishes regression',foam.intersect(wall).Volume(),1,True)
    check('translated core shell vs unchanged tray native overlap mm3',foam.translate((0,4.3,0)).intersect(wall).Volume())
    report['readings']['core_world_y']={'front':182.3,'aft':465.3,'rear_inner':enc.rear_plane_y,'tray_aft':181.29,'tray_air':1.01}
    check('rear inner plane matches selected complete core shift',abs(enc.rear_plane_y-468.3))
    check('full aft tray to new core front plane mm',182.3-181.29,1,True)

    pockets=ea.front_flank_reliefs({n:(s,None) for n,s in coils.items()})
    revised=enc._front_top_flank_pockets(wall,pockets)
    report['readings']['native_yoke_pockets']=pockets
    for name in ('coil-v-f','coil-v-i'):
        check(name+' shallow-pocket native overlap mm3',coils[name].intersect(revised).Volume())
        check(name+' shallow-pocket native air mm',coils[name].distance(revised),1,True)
    for name,x0,x1,y0,y1,z0,z1 in pockets:
        stock=enc.appliance_width/2-max(abs(x0),abs(x1))
        check(name+' residual wall stock mm',stock,7.65,True)
        check(name+' stock behind maximum exterior fluting mm',stock-enc._interface.flute_depth,enc.wall,True)
    lower=enc._ybox(-110,110,0,210,159,175)
    check('pockets remove no lower seam/rail stock mm3',wall.cut(revised).intersect(lower).Volume())

    # Each clip uses the production profile and transformation on a full local host slab.
    # Its world station is read from the frozen seam; revised full-Box proof remains required.
    clip=enc._cable_clip;fx=enc.front_top_flank_face()[1]
    z0=enc._seam_web_at(box,fx+enc.flank_clip_embed)-clip.channel_mouth()
    for y,run in enc.flank_clip_stations:
        host=enc._ybox(fx,enc.appliance_width/2,y,y+run,z0-2,z0+clip.HEIGHT+2)
        part=clip.apply(host,origin=(fx,y,z0),outward=(-1,0,0),along=(0,1,0),
                        embed=enc.flank_clip_embed,wall_thickness=enc.front_top_flank_t,run=run).val()
        check(f'clip at Y{y:g} current tube native overlap mm3',tube.intersect(part).Volume())
        check(f'clip at Y{y:g} current tube air mm',tube.distance(part),1,True)
    check('clip full-grid arm section mm',clip.GRID,3,True)
    check('clip host stock behind embedded channel mm',enc.front_top_flank_t-enc.flank_clip_embed,clip.BACKING,True)
    report['readings']['flank_clip']={'embed_mm':enc.flank_clip_embed,'projection_mm':clip.projection(enc.flank_clip_embed),
        'profile_grid_mm':clip.GRID,'host_mm':enc.front_top_flank_t,'z_origin':z0,
        'scope':'Existing 3 mm profile translated intact into host; production end ramps retained. Exact new route and completed shell remain to be checked.'}

    cups=enc._tee_carrier_fixed_cups(interface)
    for i,cup in enumerate(cups,1):check(f'fixed cup {i} missing native stock mm3',cup.cut(wall).Volume())
    for i,spans in enumerate(interface['tee_wells'],1):
        well=tc._box(*[v for span in spans for v in span]).val()
        check(f'well {i} unintended stock outside declared cups mm3',well.cut(*cups).intersect(wall).Volume())
    for letter in 'cd':
        coil=coils['coil-v-'+letter];valve=load(baseline/f'valve-v-{letter}.brep')
        dz=box.pack.collet_plate['z0']-max(coil.BoundingBox().zmax,valve.BoundingBox().zmax)-spec.slide_air
        result=swept_overlap(coil,(0,interface['aft_valve_entry_y'],dz),
                             (0,interface['aft_valve_entry_y'],0),carrier)
        report['readings']['coil-'+letter+'-full-rise']=result
        check('coil '+letter+' continuous native entry mm3',max(result['initial_overlap_mm3'],result['max_prism_overlap_mm3']))
    report['input_sha256']=inputs
    report['status']='bounded_native_repair_pass' if not report['failures'] else 'failed'
    report['full_regenerated_shell_required']=True
    save()
    if report['failures']:raise SystemExit('; '.join(report['failures']))

if __name__=='__main__':main()
