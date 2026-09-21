"""Read-only native carrier, loading-tool and display-cover checks on a fresh shell.

Both the Box and world-frame front-top STEP require explicit handoff digests.
This script exports no geometry and does not read the frozen study fixture.
"""
from __future__ import annotations

import argparse
import contextlib
from datetime import datetime, timezone
import hashlib
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import time

HERE=Path(__file__).resolve().parent
ROOT=next(p for p in HERE.parents if (p/'hardware/scripts').is_dir())
CARRIER=ROOT/'hardware/printed-parts/enclosure/tee-carrier'
PUSHER=ROOT/'hardware/printed-parts/fixtures/carrier-spring-pusher'
COVER=ROOT/'hardware/printed-parts/enclosure/display-cover'
TOL=1e-5


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def label(path):
    p=Path(path).resolve()
    return str(p.relative_to(ROOT)) if p.is_relative_to(ROOT) else str(p)


def source_hashes():
    result={}
    for module in tuple(sys.modules.values()):
        raw=getattr(module,'__file__',None)
        if not raw:continue
        p=Path(raw).resolve()
        if p.suffix!='.py' or not p.is_relative_to(ROOT):continue
        relative=p.relative_to(ROOT)
        if relative.parts[:2]==('tools','cad-venv'):continue
        result[str(relative)]=sha(p)
    return dict(sorted(result.items()))


def source_snapshot():
    names=subprocess.check_output(
        ['git','ls-files','--cached','--others','--exclude-standard','-z','--','*.py'],
        cwd=ROOT).decode().split('\0')
    return {name:sha(ROOT/name) for name in names if name and
            not name.startswith('tools/cad-venv/') and (ROOT/name).is_file()}


def datum_differences(expected, actual, path='interface'):
    if isinstance(expected,dict):
        if not isinstance(actual,dict):return [path+' is not a dictionary']
        return [issue for key,value in expected.items()
                for issue in ([path+'.'+key+' is absent'] if key not in actual else
                              datum_differences(value,actual[key],path+'.'+key))]
    if isinstance(expected,(tuple,list)):
        if not isinstance(actual,(tuple,list)) or len(expected)!=len(actual):
            return [path+' sequence differs']
        return [issue for i,(a,b) in enumerate(zip(expected,actual))
                for issue in datum_differences(a,b,f'{path}[{i}]')]
    if isinstance(expected,(float,int)) and not isinstance(expected,bool):
        if isinstance(actual,(float,int)) and abs(expected-actual)<=1e-6:return []
    elif expected==actual:return []
    return [f'{path}: printed {expected!r}, Box {actual!r}']


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--box',type=Path,default=ROOT/'hardware/manifold-layout/enclosure-box.json')
    parser.add_argument('--box-sha256',required=True)
    parser.add_argument('--front-top',type=Path,required=True,
                        help='Canonical complete native front-top in enclosure world coordinates')
    parser.add_argument('--front-top-sha256',required=True)
    parser.add_argument('--left',type=Path,default=CARRIER/'enclosure-tee-carrier-left.step')
    parser.add_argument('--right',type=Path,default=CARRIER/'enclosure-tee-carrier-right.step')
    parser.add_argument('--pusher',type=Path,default=PUSHER/'carrier-spring-pusher.step')
    parser.add_argument('--display-cover',type=Path,default=COVER/'display-cover.step')
    parser.add_argument('--output',type=Path,default=HERE/'current-front-top-check.json')
    args=parser.parse_args()
    for path,digest in ((args.box,args.box_sha256),(args.front_top,args.front_top_sha256)):
        if sha(path)!=digest:raise ValueError('Handoff digest mismatch: '+label(path))

    snapshot=source_snapshot()
    os.environ.setdefault('HSM_NO_BUILD_LOCK','1')
    sys.path[:0]=[str(ROOT/'hardware/manifold-layout'),str(CARRIER),str(PUSHER)]
    import cadquery as cq
    import enclosure_assembly as ea
    import _box_spec
    import _carrier_motion as motion
    import carrier_spring_pusher as pusher
    enc,carrier,ml,cover=ea._enc,ea._carrier,ea.ml,ea._cover
    from _simple_carrier import box as block,bounds

    source_before=source_hashes()
    paths=[args.box,args.front_top,args.left,args.right,args.pusher,args.display_cover,
           PUSHER/'geometry-check.json',args.left.with_suffix('.stl'),
           args.right.with_suffix('.stl'),args.pusher.with_suffix('.stl'),
           args.display_cover.with_suffix('.stl')]
    inputs={label(p):sha(p) for p in paths}
    report={'status':'running','created_at_utc':datetime.now(timezone.utc).isoformat(),
        'scope':'Fresh complete native front-top, canonical carrier halves, canonical loading tool and machine display cover. Loose front-top loading has bare tees present and valves absent. Full appliance neighbor/support checks remain separate.',
        'command':sys.argv,'input_sha256':inputs,'source_sha256':source_before,
        'checks':[],'sweeps':[],'failures':[],'print_released':False,
        'physical_trial_is_preprint_gate':False}
    started=time.perf_counter()
    def save():
        args.output.parent.mkdir(parents=True,exist_ok=True)
        temp=args.output.with_suffix('.tmp')
        temp.write_text(json.dumps(report,indent=2)+'\n')
        temp.replace(args.output)
    def check(name,value,*,positive=False,maximum=TOL):
        value=float(value);passed=value>TOL if positive else value<=maximum
        report['checks'].append({'check':name,'value':value,
            'condition':f'>{TOL}' if positive else f'<={maximum}','pass':passed})
        if not passed:report['failures'].append(name)
    def sweep(name,shape,start,end,obstacle):
        tick=time.perf_counter()
        row={'check':name,**motion.swept_overlap(shape,start,end,obstacle)}
        row['elapsed_seconds']=time.perf_counter()-tick
        report['sweeps'].append(row)
        if max(row['initial_overlap_mm3'],row['max_prism_overlap_mm3'])>TOL:
            report['failures'].append(name+' has a native or unresolved conservative overlap')
        save()
        print(f'{name}: {max(row["initial_overlap_mm3"],row["max_prism_overlap_mm3"]):.6g} mm3; {row["elapsed_seconds"]:.1f} s',flush=True)
    def native(path):
        shape=cq.importers.importStep(str(path)).val()
        if not shape.isValid() or len(shape.Solids())!=1:
            raise ValueError(label(path)+' is not one valid native solid')
        return shape
    def equal(name,a,b):
        check(name+' extra native stock mm3',a.cut(b).Volume())
        check(name+' missing native stock mm3',b.cut(a).Volume())
    def ycyl(x,z,d,y0,y1):
        return cq.Solid.makeCylinder(d/2,y1-y0,cq.Vector(x,y0,z),cq.Vector(0,1,0))
    try:
        box,_bounds=_box_spec.read(enc.Box,enc.Bound,(enc.Pack,enc.PortField,enc.Nameplate),path=args.box)
        interface=box.pack.tee_carrier
        if not interface:raise ValueError('The handed-off Box has no carrier interface')
        spec=carrier.DEFAULT_SPEC
        mismatch=datum_differences(carrier.interface(spec),interface)
        if mismatch:raise ValueError('Box / printed carrier mismatch: '+'; '.join(mismatch))
        wall=native(args.front_top)
        halves={-1:native(args.left),1:native(args.right)}
        tool_native=native(args.pusher)
        parts=carrier.assembly_parts(spec)
        equal('canonical left / source',halves[-1],parts['left'])
        equal('canonical right / source',halves[1],parts['right'])
        equal('canonical pusher / source',tool_native,pusher.build())
        if abs(spec.spring_load_length-pusher.HELD_SPRING_LENGTH)>1e-8:
            raise ValueError('Carrier and canonical pusher held lengths differ')
        evidence=json.loads((PUSHER/'geometry-check.json').read_text())
        for path,digest in evidence['artifacts'].items():
            if sha(ROOT/path)!=digest:raise ValueError('Canonical pusher export changed: '+path)
        # The complete half STEP is the authority; source decomposition supplies
        # only its separately moving flexible wall, after exact equality above.
        parts={**parts,'left':halves[-1],'right':halves[1]}
        report['box_interface']=interface
        report['native_front_top']={'volume_mm3':wall.Volume(),'bounds':bounds(wall),
                                    'valid':True,'solids':1}
        joint=motion.joint_checks(spec,parts)
        report['joint']=joint
        if not joint['clear']:report['failures'].append('canonical inter-half joint motion')

        lift=spec.tee_axis_z-ml.branch_port(sorted(ml.CARRIER_TEES)[0])[0][1]
        def tee_pose(name,dy):
            return ea.pose_manifold(ml.carrier_tee(name,dy)).translate((0,ea.PACK_Y,lift))
        tees=[(ml.body_name(n),tee_pose(n,spec.release_offset_y)) for n in sorted(ml.CARRIER_TEES)]
        for name,shape in tees:
            check(name+' outside conservative tee envelope',shape.cut(motion.tee_envelope(shape)).Volume())
        obstacles=wall.fuse(*(s for _,s in tees)).clean()
        aft=spec.aft_limit_offset_y
        spring_d=interface['spring_clearance_d']+2*spec.slide_air
        def installed_tool(side):
            s=next(s for s in interface['spring_stations'] if s['x']*side>0)
            tip=s['bore_floor_y']-pusher.HELD_SPRING_LENGTH
            shape=tool_native
            if side<0:shape=shape.rotate((0,0,0),(0,0,1),180)
            return shape.rotate((0,0,0),(1,0,0),-90).translate((s['x'],tip-pusher.THICKNESS,s['z']))

        print('Fresh input identities, Box datums, canonical native equality and joint checked',flush=True)
        report['canonical_pusher']={'quantity':1,'thickness_mm':pusher.THICKNESS,
            'tongue_width_mm':pusher.TONGUE_WIDTH,'lift_clearances':[],
            'reuse':'Seat and release left spring; withdraw tool; reuse it for right.'}
        for side,key in ((-1,'left'),(1,'right_structural')):
            body=parts[key]
            station=next(s for s in interface['spring_stations'] if s['x']*side>0)
            tool=installed_tool(side)
            equal(f'half {side:+} canonical pusher pose',tool,pusher.installed(interface,side))
            tip=station['bore_floor_y']-spec.spring_load_length
            held_spring=ycyl(station['x'],station['z'],spring_d,tip,station['bore_floor_y'])
            check(f'half {side:+} held spring / moving cup',held_spring.intersect(halves[side]).Volume())
            check(f'half {side:+} canonical pusher / moving cup',tool.intersect(halves[side]).Volume())
            held=tool.fuse(held_spring)
            poses=[pose for _name,pose in carrier.insertion_poses(spec,side)]
            blockers=obstacles
            if side>0:blockers=blockers.fuse(halves[-1].translate((0,aft,0)))
            for i,(start,end) in enumerate(zip(poses,poses[1:]),1):
                sweep(f'half {side:+} structural insertion {i}',body,start,end,wall)
                sweep(f'half {side:+} canonical held tool/spring insertion {i}',held,start,end,blockers)
                for name,tee in tees:
                    check(f'half {side:+} insertion {i} / {name} continuous envelope',
                          body.intersect(motion.tee_sweep(tee,start,end)).Volume())
            withdraw=spec.spring_x-max(spec.tee_xs)
            path=[(0,aft,0),(-side*withdraw,aft,0),(-side*withdraw,aft,spec.entry_lift_z)]
            blockers=blockers.fuse(halves[side].translate((0,aft,0)))
            for i,(start,end) in enumerate(zip(path,path[1:]),1):
                sweep(f'half {side:+} canonical pusher removal {i}',tool,start,end,blockers)
            b=tool.translate(path[1]).BoundingBox()
            lift_box=block((b.xmin,b.xmax),(b.ymin,b.ymax),(b.zmin,b.zmax+spec.entry_lift_z))
            check(f'half {side:+} conservative pusher lift box',lift_box.intersect(blockers).Volume())
            report['canonical_pusher']['lift_clearances'].append(
                {'side':side,'conservative_native_gap_mm':lift_box.distance(blockers)})
            print(f'Half {side:+}: complete native placement and canonical pusher withdrawal checked',flush=True)

        left=interface['spring_stations'][0]
        released=ycyl(left['x'],left['z'],spring_d,left['seat_floor_y'],left['bore_floor_y']+aft)
        right_with_tool=halves[1].fuse(installed_tool(1))
        poses=[pose for _name,pose in carrier.insertion_poses(spec,1)]
        for i,(start,end) in enumerate(zip(poses,poses[1:]),1):
            sweep(f'right half/tool / released left spring {i}',right_with_tool,start,end,released)
        flex=parts['retention_wall'].fuse(parts['retention_lip'])
        for i,(start,end) in enumerate(zip(poses,poses[1:]),1):
            sweep(f'nominal retaining-wall insertion {i}',flex,start,end,wall)
        b=flex.BoundingBox()
        deflection_box=block((b.xmin-spec.entry_shoulder_inset_x,b.xmax),
                            (b.ymin+aft,b.ymax+aft+4.3),(b.zmin,b.zmax))
        check('complete final retaining-wall deflection envelope',deflection_box.intersect(wall).Volume())

        # Actual native closed cups and their full floors, without adding any
        # in-memory cup extensions to the handed-off finished wall.
        for s,cup in zip(interface['spring_stations'],enc._tee_carrier_fixed_cups(interface)):
            cup=cup.val() if hasattr(cup,'val') else cup
            check(f'X{s["x"]:g} complete integral fixed cup stock',cup.cut(wall).Volume())
            floor=ycyl(s['x'],s['z'],6,s['seat_floor_y']-.15,s['seat_floor_y']-.02)
            check(f'X{s["x"]:g} fixed spring floor stock',floor.cut(wall).Volume())
            bore=ycyl(s['x'],s['z'],spec.spring_bore_d-.02,s['seat_floor_y']+.01,
                       s['seat_floor_y']+spec.fixed_seat_depth-.01)
            check(f'X{s["x"]:g} complete fixed cup bore',bore.intersect(wall).Volume())
        carrier_whole=cq.Compound.makeCompound(list(halves.values()))
        guide_walls=[]
        for side in (-1,1):
            xa,xb=sorted((side*spec.guide_inner_x,side*spec.exterior_x))
            guide_walls.append(wall.intersect(block((xa,xb),
                (spec.rim_y[0]+spec.release_offset_y-1,spec.rim_y[1]+aft+1),
                (min(spec.rim_z[0],spec.grip_z[0])-1,spec.rim_z[1]+1))))
            xa,xb=sorted((side*spec.rim_x[0],side*spec.rim_x[1]))
            top=spec.rim_z[0]-spec.slide_air
            stock=block((xa,xb),(spec.rim_y[0]+spec.park_offset_y,
                spec.tab_y[0]+spec.release_offset_y-spec.slide_air),(top-enc.wall,top))
            check(f'half {side:+} full fore-guide stock',stock.cut(wall).Volume())
            xa,xb=sorted((side*(spec.exterior_x-spec.grip_wall_t),side*spec.exterior_x))
            lip=block((xa,xb),(spec.rim_y[0]+spec.park_offset_y,
                spec.tab_y[0]+spec.release_offset_y-spec.slide_air),(spec.grip_rail_top_z,spec.grip_z[1]))
            check(f'half {side:+} full fore retaining-lip stock',lip.cut(wall).Volume())
            sweep(f'half {side:+} complete working travel',halves[side],
                  (0,spec.release_offset_y,0),(0,aft,0),wall)
        guides=cq.Compound.makeCompound(guide_walls)
        report['guide_probe_angle_deg']=spec.capture_probe_angle
        for state,dy in (('release',spec.release_offset_y),('connected',spec.connected_offset_y),('aft_limit',aft)):
            posed=carrier_whole.translate((0,dy,0))
            check(state+' carrier / completed wall',posed.intersect(wall).Volume())
            for s in interface['spring_stations']:
                spring=ycyl(s['x'],s['z'],spring_d,s['seat_floor_y'],s['bore_floor_y']+dy)
                check(f'{state} X{s["x"]:g} spring / actual cups',spring.intersect(wall.fuse(posed)).Volume())
            for name in sorted(ml.CARRIER_TEES):
                tee=tee_pose(name,dy)
                check(f'{state} {name} / completed wall',tee.intersect(wall).Volume())
                check(f'{state} {name} / canonical carrier',tee.intersect(posed).Volume())
            for sense,z in ((-1,spec.web_z[0]-spec.slide_air),
                             (1,spec.web_z[1]+spec.slide_air+carrier.fits.supported_surface)):
                zs=sorted((z,z+sense*.001))
                strip=block(spec.web_x,(spec.web_fore_y+dy,spec.web_aft_y+dy),zs)
                check(f'{state} web bearing {sense:+}',strip.intersect(wall).Volume(),positive=True)
            center=(0,(spec.grip_y[0]+spec.grip_y[1])/2+dy,(spec.grip_z[0]+spec.grip_z[1])/2)
            for axis in (0,2):
                for sign in (-1,1):
                    delta=[0,0,0];delta[axis]=sign*(spec.slide_air+(carrier.fits.supported_surface if axis==2 else 0)+.001)
                    check(f'{state} guide translation {"XYZ"[axis]}{sign:+}',
                          posed.translate(delta).intersect(guides).Volume(),positive=True)
            for axis in range(3):
                tip=list(center);tip[axis]+=1
                for sign in (-1,1):
                    check(f'{state} guide rotation {"XYZ"[axis]}{sign:+}',
                        posed.rotate(center,tip,sign*spec.capture_probe_angle).intersect(guides).Volume(),positive=True)
        for side,half in halves.items():
            for state,dy in (('release',spec.release_offset_y-.001),('aft_limit',aft+.001)):
                check(f'half {side:+} {state} stop at 0.001 overshoot',
                      half.translate((0,dy,0)).intersect(wall).Volume(),positive=True)
        print('Native cup stock, complete working travel and positive guide contacts checked',flush=True)

        # The printed cover is relaxed. Production assembly explicitly seats its
        # broad skirts elastically; relaxed-hook interference is not a seated fit.
        cover_native=native(args.display_cover)
        equal('canonical display cover / relaxed source',cover_native,cover.build_display_cover().val())
        captured=io.StringIO()
        with contextlib.redirect_stdout(captured):cover_exit=cover.selftest()
        check('display-cover existing selftest exit',cover_exit,maximum=0)
        seated,_carry=ea.build_display_cover(box)
        check('seated display cover / completed front-top',seated.intersect(wall).Volume())
        plane=enc.display_plane(box.outer)
        def display_pose(shape):return shape.moved(cq.Location(plane))
        engagement=[]
        for side in (-1,1):
            pocket=display_pose(cover.retention.pocket(side))
            check(f'display skirt {side:+} complete declared approach/pocket',pocket.intersect(wall).Volume())
            skirt=cover.retention.skirt(side,seated=True)
            pulled=display_pose(skirt.translate((0,0,cover.retention.ROOF_AIR+.001)))
            volume=pulled.intersect(wall).Volume()
            check(f'display skirt {side:+} shoulder retaining contact',volume,positive=True)
            engagement.append({'side':side,'pull_out_mm':cover.retention.ROOF_AIR+.001,
                               'native_contact_mm3':volume})
        report['display_cover']={'existing_selftest_output':captured.getvalue(),
            'seated_pose':'enclosure_assembly.build_display_cover(Box)',
            'shoulder_contacts':engagement,
            'scope':'Canonical relaxed export equality, existing glass/seated-pocket gate, actual seated-wall clearance, complete declared pocket/approach cavity and positive retaining shoulders.',
            'snap_insertion_force_or_deformation_qualified':False,
            'limitation':'The production gate has no full elastic snap-entry model. This current-shell interface check does not measure hand force, skirt strain or fatigue; the user reports prior physical display fit acceptance.'}
        after=source_hashes()
        changed=[path for path,digest in after.items() if snapshot.get(path)!=digest]
        if changed:
            raise ValueError('Loaded source changed or was absent from the initial snapshot: '+', '.join(changed))
        report['source_sha256']=after
        report['source_drift']=[]
        for path,digest in inputs.items():
            if sha(ROOT/path if not Path(path).is_absolute() else path)!=digest:
                raise ValueError('Input artifact changed during native check: '+path)
        report['elapsed_seconds']=time.perf_counter()-started
        report['all_native_checks_pass']=not report['failures']
        report['status']='current_front_top_native_pass' if not report['failures'] else 'current_front_top_native_findings'
        report['limitations']=[
            'Planar translation prisms are native sweeps; curved-face boxes enclose the motion. Any positive enclosing-box result is unresolved, not automatically a proven collision.',
            'Guide/contact probes are geometric constraints, not stiffness or free-body angular play.',
            'Actual spring deformation, both-end retention, force, tool handling and full-width rigidity are complete-enclosure physical trial outcomes.',
            'This loose-wall audit omits installed valves during half loading. The combined appliance checks qualify final surrounding hardware and lower-shell closure.',
            'Current slice identity, material, support toolpaths and removal access are separate release checks.']
        save()
        print(json.dumps({'status':report['status'],'checks':len(report['checks']),
                          'sweeps':len(report['sweeps']),'failures':report['failures'],
                          'elapsed_seconds':report['elapsed_seconds']},indent=2),flush=True)
        return 0 if not report['failures'] else 1
    except Exception as exc:
        report['status']='verification_error';report['error']=repr(exc)
        report['elapsed_seconds']=time.perf_counter()-started
        save()
        raise


if __name__=='__main__':raise SystemExit(main())
