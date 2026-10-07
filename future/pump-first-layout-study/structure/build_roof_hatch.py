"""Removable rear roof article and native factory landing reservations.

The complete back-top closes on its retained Y rails with this article absent.
The supply is tightened through the aperture, then the preassembled earth fan
and discharge union land on the hatch. Parent-stock ledges and pilot recuts are
declared independently so their final joined print can be audited.
"""
from pathlib import Path
from io import BytesIO
import sys, json, hashlib, math
import cadquery as cq

HERE = Path(__file__).resolve().parent
STUDY = HERE.parent
ROOT = STUDY.parents[1]
sys.path.insert(0, str(STUDY/'pump'))
import generate as G
from evidence_binding import content_sha256,manifest_content_sha256
from audit import common as native_common
from structure import proof_sources
from structure.assemble_prints import joined as joined_material

OUT = ROOT/'.cache/pump-first-layout/structure/roof-hatch'
RECT = [-53., 389., 83., 466.3]
CARRIED = {'ground-stack', 'ground-roof-boss', 'discharge-chain',
           'discharge-chain-anchor', 'discharge-chain-lower-key',
           'discharge-chain-clip-screw-1', 'discharge-chain-clip-screw-2',
           'hose-clamp-chain-discharge', 'hose-engagement-chain-discharge'}
FASTENERS = [(-25., 413.5), (-38.5, 466.7), (58.8, 412.5), (61., 466.7)]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def box(x0, y0, z0, x1, y1, z1):
    return cq.Solid.makeBox(x1-x0, y1-y0, z1-z0, cq.Vector(x0, y0, z0))


def main(ground_pose=None,report_path=None):
    sources=proof_sources.snapshot(__file__,G.__file__,HERE/'check_hatch_hose.py',
                                  HERE/'check_ground_make_up.py',HERE/'probe_psu_tools.py',
                                  HERE/'assemble_prints.py')
    material_joins=[]
    controller_finish_checks=[]
    def join_stock(left,right,owner,name):
        components=right.Solids()
        if len(components)>1:
            result=left
            for index,solid in enumerate(components):
                result=joined_material(result,solid,owner,name+'/solid-'+str(index))
            missing=[]
            for operand in [left,right]:
                missing.append(sum(abs(solid.copy(mesh=False).cut(result.copy(mesh=False),tol=.0001).Volume(tol=1e-9))
                                   for solid in operand.Solids()))
            outside=result.copy(mesh=False)
            for operand in [left,right]:
                for solid in operand.Solids():
                    if not outside.Solids():break
                    outside=outside.cut(solid.copy(mesh=False),tol=.0001)
            excess=abs(outside.Volume(tol=1e-9)) if outside.Solids() else 0.
            volumes=[left.Volume(tol=1e-9),right.Volume(tol=1e-9)]
            volume=result.Volume(tol=1e-9)
            if not result.isValid() or not result.Solids() or max(missing)>=.001 or excess>=.001 or not max(volumes)-.001<=volume<=sum(volumes)+.001:
                raise ValueError('Sequential physical join lost or added material: '+name)
            row={'method':'Separate occupied-solid unions with witnessed contained-solid no-ops',
                 'right_solid_count':len(components),'operand_missing_mm3':missing,
                 'outside_operands_mm3':excess}
        else:
            result=joined_material(left,right,owner,name)
            row={'method':'Guarded shared material union, including witnessed containment no-op'}
        material_joins.append({'owner':owner,'member':name,
                               'operand_volume_mm3':[left.Volume(tol=1e-9),right.Volume(tol=1e-9)],
                               'result_volume_mm3':result.Volume(tol=1e-9),'pass':True,**row})
        return result
    OUT.mkdir(parents=True, exist_ok=True)
    prepared_structure=json.loads((HERE/'candidate.json').read_text())
    if 'enclosure-back-top' not in prepared_structure.get('parts',{}):
        raise RuntimeError('Regenerate structure/build_shell.py before the hatch: a prepared current back-top source is required')
    index = G.baseline.prepare()
    records = {n: {'brep': str((G.baseline.CACHE/r['file']).relative_to(ROOT))}
               for n, r in index['parts'].items()}
    manifests, manifest_contents, removed, current = {}, {}, set(), set()
    paths = [STUDY/f/'candidate.json' for f in ['funnel', 'pump', 'routing', 'structure', 'mounts']]
    paths += [STUDY/'wiring'/f for f in ['controls-candidate.json', 'power-candidate.json',
                                       'control-reserves.json','control-fanouts-check.json']]
    paths += [STUDY/'pump/fluid24-candidate.json',STUDY/'mounts/fluid-candidate.json',
              STUDY/'routing/co2-candidate.json',STUDY/'mounts/body-candidate.json',
              STUDY/'mounts/water5-hosts.json',STUDY/'routing/tube-hosts.json']
    for p in paths:
        if not p.exists():
            continue
        m = json.loads(p.read_text())
        manifests[str(p.relative_to(ROOT))] = sha(p)
        manifest_contents[str(p.relative_to(ROOT))]=content_sha256(m)
        records.update(m.get('parts', {}))
        current.update(m.get('parts', {}))
        removed.update(m.get('replacement_names', []))
    front_handling_path=STUDY/'wiring/front-loom-handling.json'
    front_handling=json.loads(front_handling_path.read_text())
    manifests[str(front_handling_path.relative_to(ROOT))]=sha(front_handling_path)
    manifest_contents[str(front_handling_path.relative_to(ROOT))]=content_sha256(front_handling)
    records = {n: r for n, r in records.items() if n not in removed or n in current}
    shapes, inputs = {}, {}
    for n, r in records.items():
        p = ROOT/r['brep']
        shapes[n] = cq.Shape.importBrep(str(p))
        inputs[n] = {'brep': r['brep'], 'sha256': sha(p)}
    roof = shapes['enclosure-back-top']
    structure = json.loads((HERE/'candidate.json').read_text())
    if ground_pose is not None:
        datum,clock=ground_pose
        gm=next(m for m in structure['mounts']if m['owner']=='ground-stack')
        old=tuple(gm['mouth']);axis=tuple(cq.Vector(*old)+cq.Vector(0,0,1))
        shapes['ground-stack']=shapes['ground-stack'].rotate(old,axis,clock-gm.get('clock_degrees',0)).translate(tuple(datum[i]-old[i]for i in range(3)))
        shapes['ground-roof-boss']=shapes['ground-roof-boss'].translate(tuple(datum[i]-old[i]for i in range(3)))
        b=G.bounds(shapes['ground-roof-boss'])
        if b[5]<355:
            shapes['ground-roof-boss']=join_stock(shapes['ground-roof-boss'],
                cq.Solid.makeCylinder(4,355-b[5]+.01,cq.Vector(datum[0],datum[1],b[5]-.01)),
                'ground-roof-boss','roof-root-extension')
        gm.update(mouth=list(datum),clock_degrees=clock,root_cover=355-datum[2]-gm['pilot_depth'])
    pcba_mounts = [m for m in structure['mounts'] if m['owner']=='pcba']
    rear = [m for m in pcba_mounts if m['mouth'][1]>400]
    controller_pilots={}
    for index,m in enumerate(pcba_mounts,1):
        key='controller-'+str(index)
        record=structure['pilot_cutters'][key]
        path=ROOT/record['brep'];raw=path.read_bytes();digest=hashlib.sha256(raw).hexdigest()
        if digest!=record['sha256']:
            raise ValueError('Controller finishing pilot changed: '+key)
        controller_pilots[key]=cq.Shape.importBrep(BytesIO(raw))
        inputs['finishing-pilot:'+key]={'brep':record['brep'],'sha256':digest}
    # Preserve the complete native C14 receiver and three millimetres of its
    # parent roof stock. The resulting hatch has an explicit left-side step.
    cb = G.bounds(shapes['c14-inlet'])
    wb = G.bounds(shapes['west-junction-platform'])
    # The measured meter seats remain fixed to the roof. Their upper webs
    # reach351.01 and retain positive stock in the exterior roof. A four-mm
    # plan notch leaves one-mm air even at the three-mm grown lap edge;
    # it avoids an underside relief that would breach the three-mm skin.
    meter_root_notches=[G.bounds(shapes[n]) for n in ['meter-roof-seat-1','meter-roof-seat-2']]
    def plan(z0, z1, grow=0.):
        s = box(RECT[0]-grow, RECT[1]-grow, z0,
                RECT[2]+grow, RECT[3]+grow, z1)
        for m in [m for m in structure['mounts'] if m['owner']=='psu' and m['mouth'][1]<430]:
            x, y, _ = m['mouth']
            radius = 2.5/math.sqrt(3)+1.+grow
            if radius>0:
                s = s.fuse(cq.Solid.makeCylinder(radius, z1-z0, cq.Vector(x, y, z0)))
        for m in rear:
            x, y, _ = m['mouth']
            radius=5. if x>0 else 12.
            s = s.cut(cq.Solid.makeCylinder(radius-grow, z1-z0, cq.Vector(x, y, z0)))
            if x>0 and 2.5-grow>0:
                s=s.cut(box(x-2.5+grow,RECT[1]-3.+grow,z0,
                            x+2.5-grow,y-grow,z1))
        s = s.cut(box(-120., cb[1]-3.+grow, z0,
                      cb[3]+4.-grow, cb[4]+3.-grow, z1))
        s=s.cut(box(wb[0]+grow, 300., z0,
                    wb[3]-grow, wb[4]+1.-grow, z1))
        for b in meter_root_notches:
            s=s.cut(box(b[0]-4.+grow,b[1]-4.+grow,z0,
                        b[3]+4.-grow,b[4]+4.-grow,z1))
        return s
    islands = [{'centre_xy_mm': m['mouth'][:2], 'radius_mm': 5. if m['mouth'][0]>0 else 12.} for m in rear]
    selector = plan(343., 356.)
    hatch = roof.intersect(plan(343., 356., -.15))
    fixed_roof = roof.cut(selector)
    for n in ['ground-roof-boss', 'discharge-chain-anchor']:
        hatch = join_stock(hatch,shapes[n],'rear-roof-hatch',n)
        fixed_roof = fixed_roof.cut(shapes[n])
    # A4mm upper lap supports the4mm hatch rim. The printed ledge is interrupted
    # at each insert station so a recessed head clamps a full3mm hatch web.
    ledge = plan(347., 351., 3.).cut(plan(347., 351., -4.))
    roots = plan(347., 355., 3.).cut(plan(347., 355.))
    pb = G.bounds(shapes['pcba'])
    controller_reserve = box(pb[0]-1., pb[1]-1., 330., pb[3]+1., pb[4]+1., 356.)
    ledge = ledge.cut(controller_reserve)
    roots = roots.cut(controller_reserve)
    rebate = plan(343., 351.).cut(plan(343., 351., -4.15))
    for x, y in FASTENERS:
        local = cq.Solid.makeCylinder(5., 30., cq.Vector(x, y, 330.))
        ledge = ledge.cut(local)
        roots = roots.cut(local)
        rebate = rebate.cut(local)
    for n in CARRIED:
        if n not in shapes:
            continue
        b = G.bounds(shapes[n])
        sweep_reserve = box(b[0]-1., b[1]-1., 330., b[3]+1., b[4]+1., 374.)
        ledge = ledge.cut(sweep_reserve)
        roots = roots.cut(sweep_reserve)
    # The supply tool sweeps remain clear through the open aperture.
    for m in [m for m in structure['mounts'] if m['owner']=='psu']:
        x, y, _ = m['mouth']
        clear = cq.Solid.makeCylinder(2.5/math.sqrt(3)+1., 60., cq.Vector(x, y, 300.))
        ledge = ledge.cut(clear)
        roots = roots.cut(clear)
    hatch = hatch.cut(rebate)
    fixed_roof = join_stock(fixed_roof,ledge,'enclosure-back-top','hatch-lap-ledge')
    fixed_roof = join_stock(fixed_roof,roots,'enclosure-back-top','hatch-lap-roots')
    station_parts, pilot_records, screws = {}, {}, {}
    for m in rear:
        x,y,_=m['mouth']
        if x>0:
            bridge=box(x-2.5,RECT[1]-3.,351.,x+2.5,y,355.)
            key='controller-'+str(pcba_mounts.index(m)+1)
            bridge=bridge.cut(controller_pilots[key],tol=0)
            if not bridge.isValid() or len(bridge.Solids())!=1:
                raise ValueError('Controller rear bridge finishing failed')
            fixed_roof=join_stock(fixed_roof,bridge,'enclosure-back-top','hatch-controller-rear-bridge')
            station_parts['hatch-controller-rear-bridge']=bridge
            screw=shapes['controller-screw-'+str(pcba_mounts.index(m)+1)]
            volume=native_common(bridge,screw)
            controller_finish_checks.append({'part':'hatch-controller-rear-bridge',
                'tool':key,'tool_record':structure['pilot_cutters'][key],
                'print_owner':'enclosure-back-top','screw_common_mm3':volume,
                'valid':bridge.isValid(),'solids':len(bridge.Solids()),
                'pass':volume<.001})
    for i, (x, y) in enumerate(FASTENERS, 1):
        boss = cq.Solid.makeCylinder(4., 9.5, cq.Vector(x, y, 339.))
        pilot = cq.Solid.makeCylinder(2., 6.5, cq.Vector(x, y, 348.5), cq.Vector(0, 0, -1))
        beam = None
        if i==1:
            # The controller's preserved west island roots this strip. Its
            # outside X edge clears the populated board by one millimetre.
            beam = box(x-4., y, 345.5, x+4., 420.65, 348.5)
        elif i==3:
            beam = box(x-4., RECT[1]-10.8, 345.5, x+4., y, 348.5)
        tab = box(x-4., y-4., 348.5, x+4., y+4., 355.)
        tab_clear = box(x-4.15, y-4.15, 348.5, x+4.15, y+4.15, 356.)
        fixed_roof = fixed_roof.cut(tab_clear)
        hatch = join_stock(hatch,tab,'rear-roof-hatch','hatch-head-tab-'+str(i))
        # Base posts reach their mating plane through a local underside rebate.
        pocket = cq.Solid.makeCylinder(4.15, 18.5, cq.Vector(x, y, 330.))
        if beam is not None:
            bb = G.bounds(beam)
            pocket = pocket.fuse(box(bb[0]-.15, bb[1]-.15, 330., bb[3]+.15, bb[4]+.15, 348.5))
        hatch = hatch.cut(pocket)
        boss = boss.cut(pilot)
        fixed_roof = join_stock(fixed_roof,boss,'enclosure-back-top','hatch-roof-boss-'+str(i))
        station_parts['hatch-roof-boss-'+str(i)] = boss
        if beam is not None:
            beam = beam.cut(pilot)
            fixed_roof = join_stock(fixed_roof,beam,'enclosure-back-top','hatch-roof-beam-'+str(i))
            station_parts['hatch-roof-beam-'+str(i)] = beam
        if i==3:
            web = box(x-4., RECT[1]-10.8, 345.5, x+4., RECT[1]-7.8, 355.)
            fixed_roof = join_stock(fixed_roof,web,'enclosure-back-top','hatch-roof-web-3')
            station_parts['hatch-roof-web-3'] = web
        if i==1:
            web = box(x-4., 417.65, 345.5, x+5., 420.65, 355.)
            fixed_roof = join_stock(fixed_roof,web,'enclosure-back-top','hatch-roof-web-1')
            station_parts['hatch-roof-web-1'] = web
        pilot_records['hatch-pilot-'+str(i)] = pilot
        hatch = hatch.cut(cq.Solid.makeCylinder(1.65, 7., cq.Vector(x, y, 348.)))
        hatch = hatch.cut(cq.Solid.makeCylinder(2.9, 4., cq.Vector(x, y, 351.5)))
        screw = join_stock(cq.Solid.makeCylinder(1.5,8.,cq.Vector(x,y,343.5)),
            cq.Solid.makeCylinder(2.75,3.,cq.Vector(x,y,351.5)),
            'hatch-screw-'+str(i),'head-to-shank')
        # Nominal purchased socket reservation for the actual2.5AF tool.
        rr = 2.5/math.sqrt(3)
        pts = [cq.Vector(x+rr*math.cos(k*math.pi/3), y+rr*math.sin(k*math.pi/3), 352.7) for k in range(6)]
        socket = cq.Solid.extrudeLinear(cq.Wire.makePolygon(pts+[pts[0]]), [], cq.Vector(0, 0, 2.))
        screws['hatch-screw-'+str(i)] = screw.cut(socket)
    # The silicone is cast and factory bonded after torque. Its top groove
    # crosses the actual joint; no unknown compression ratio is assumed.
    def sealed_plan(grow):
        s = plan(354.2, 355., grow-.075)
        for x, y in FASTENERS:
            s = s.fuse(box(x-4.+.075-grow, y-4.+.075-grow, 354.2,
                          x+4.-.075+grow, y+4.-.075+grow, 355.))
        return s
    seam_seal = sealed_plan(.6).cut(sealed_plan(-.6)).clean()
    hatch = hatch.cut(seam_seal)
    fixed_roof = fixed_roof.cut(seam_seal)
    finished_controller_bosses={}
    for index,m in enumerate(pcba_mounts,1):
        name='controller-roof-boss-'+str(index)
        before=native_common(shapes[name],seam_seal)
        if before<.001:
            continue
        inputs['source:'+name]=dict(inputs[name])
        boss=shapes[name].cut(seam_seal,tol=0)
        if not boss.isValid() or len(boss.Solids())!=1:
            raise ValueError('Controller boss seam finishing failed: '+name)
        x,y,z=m['mouth'];depth=m['pilot_depth']
        pilot=controller_pilots['controller-'+str(index)]
        annulus=cq.Solid.makeCylinder(3.6,depth,cq.Vector(x,y,z)).cut(pilot,tol=0)
        cap=cq.Solid.makeCylinder(2.,m['end_cover'],cq.Vector(x,y,z+depth))
        annulus_missing=annulus.Volume(tol=1e-9)-native_common(boss,annulus)
        cap_missing=cap.Volume(tol=1e-9)-native_common(boss,cap)
        volume=native_common(boss,seam_seal)
        controller_finish_checks.append({'part':name,'tool':'hatch-seam-groove-roof',
            'print_owner':'enclosure-back-top','before_common_mm3':before,
            'seam_common_mm3':volume,'pilot_annulus_mm':1.6,
            'pilot_annulus_missing_mm3':annulus_missing,
            'end_cover_mm':m['end_cover'],'end_cap_missing_mm3':cap_missing,
            'valid':boss.isValid(),'solids':len(boss.Solids()),
            'pass':volume<.001 and abs(annulus_missing)<.001 and abs(cap_missing)<.001})
        shapes[name]=boss
        finished_controller_bosses[name]=boss
    hatch_pilots = {}
    gm = next(m for m in structure['mounts'] if m['owner']=='ground-stack')
    hatch_pilots['hatch-ground-pilot'] = cq.Solid.makeCylinder(
        2., gm['pilot_depth'], cq.Vector(*gm['mouth']), cq.Vector(*gm['axis']))
    pump_manifest = json.loads((STUDY/'pump/candidate.json').read_text())
    retainer = pump_manifest['poses']['discharge-chain-retainer']
    for i, (x, y) in enumerate(retainer['screw_axes_xy_mm'], 1):
        hatch_pilots['hatch-discharge-pilot-'+str(i)] = cq.Solid.makeCylinder(
            2., retainer['pilot_depth_mm'], cq.Vector(x, y, G.DISCH_TIP[2]))
    for pilot in hatch_pilots.values():
        hatch = hatch.cut(pilot)
    for pilot in pilot_records.values():
        fixed_roof = fixed_roof.cut(pilot)
    import check_hatch_hose as HH
    target=pump_manifest['routes']['water-6']['developed_length_mm']
    pos,axis=G.point(G.P.discharge(),G.loc(shift=G.PUMP_ORIGIN))
    family_cutters=[]
    family_poses=[]
    for lift in range(14,-1,-1):
        wire,riser,angle=HH.solve(lift,target)
        if lift in [14,7,0]:
            cutter=cq.Solid.sweep(cq.Wire.makeCircle(8.55,cq.Vector(*pos),cq.Vector(*axis)),
                                  [],wire,makeSolid=True,isFrenet=True)
            family_cutters.append(cutter.intersect(box(-120.,390.,330.,100.,480.,380.)))
        family_poses.append({'hatch_lift_z_mm':lift,'plane_degrees':angle,
                             'length_mm':wire.Length(),'minimum_radius_mm':15.9})
    # Apply these tools sequentially. Their overlapping compound is an
    # inspection article, not a valid Boolean cutting tool. The full15-pose
    # hose audit below independently verifies coverage between cut stations.
    removed=[fixed_roof.intersect(c) for c in family_cutters]
    removed_bounds=G.bounds(cq.Compound.makeCompound(removed)) if any(s.Volume()>1e-6 for s in removed) else None
    if removed_bounds is not None and removed_bounds[5]>352.+1e-5:
        raise ValueError('Hatch hose pocket would leave less than3mm exterior roof stock')
    for cutter in family_cutters:
        fixed_roof=fixed_roof.cut(cutter)
    hatch=hatch.cut(family_cutters[-1])
    for cutter in family_cutters:
        ledge=ledge.cut(cutter)
        roots=roots.cut(cutter)
        station_parts={n:s.cut(cutter) for n,s in station_parts.items()}
    # Interrupt the local lap at the water5 exit. A complete pocket to351
    # removes the thin residual strip that a round cutter alone would leave.
    # Four millimetres of exterior roof remains; the seal groove leaves3.2.
    water5_lap=box(77.5,449.325,343.,87.5,457.675,351.)
    hatch=hatch.cut(water5_lap)
    fixed_roof=fixed_roof.cut(water5_lap)
    ledge=ledge.cut(water5_lap);roots=roots.cut(water5_lap)
    station_parts={n:s.cut(water5_lap)for n,s in station_parts.items()}
    # The final ASSE-to-tee route passes the fore hatch framing. Its exact
    #1mm-air native cutter is applied to every fixed and removable article.
    # The fore screw station is west of this channel; its full pilot wall
    # and closed cap are independently checked below.
    routing_manifest=json.loads((STUDY/'routing/candidate.json').read_text())
    water2_record=routing_manifest['clearance_cutters']['tube-water-2']
    water2_cutter=cq.Shape.importBrep(str(ROOT/water2_record['brep']))
    water2_roof=water2_cutter.intersect(box(-120.,300.,330.,120.,480.,352.))
    hatch=hatch.cut(water2_roof);fixed_roof=fixed_roof.cut(water2_roof)
    ledge=ledge.cut(water2_roof);roots=roots.cut(water2_roof)
    station_parts={n:s.cut(water2_roof)for n,s in station_parts.items()}
    # Native bought-component envelopes get1mm air beneath the removable
    # article. The carried worm housing needs its own pocket in addition to
    # the seated braid sweep; neither housing nor clamp clock changes.
    hatch_neighbor_cutters={}
    for name in ['carb-foam-carb-2','hose-clamp-chain-discharge']:
        b=G.bounds(shapes[name]);cut_top=b[5]+1.
        if cut_top>352.+1e-5:raise ValueError('Hatch neighbor relief would breach3mm roof stock')
        cutter=box(b[0]-1.,b[1]-1.,343.,b[3]+1.,b[4]+1.,cut_top)
        hatch=hatch.cut(cutter)
        hatch_neighbor_cutters[name]=cutter
    # The fore junction is completed after the hatch seats, before the front
    # article closes. A nominal hook enters this channel and opens the final
    # G2 working volume; its insertion, roll and staged withdrawal are audited.
    g2_channel=box(-53.15,322.,343.,-32.35,327.65,352.).fuse(
        box(-45.8,326.7,343.,-41.1,345.3,352.))
    fixed_roof=fixed_roof.cut(g2_channel)
    # All four precrimped ground tails can pass the fixed lap while the hatch
    # lands. Their exact nominal handling curves reserve one millimetre of
    # radial air and remove only lap stock below351, preserving the upper4mm.
    import check_ground_make_up as GW
    tail_cutters=[]
    tail_names=[]
    power=json.loads((STUDY/'wiring/power-candidate.json').read_text())
    for index,label in enumerate(GW.POWER_ROUTE_KEYS):
        length=power['power_routes'][label]['length_mm']
        for lift in [14.,10.,22.5]:
            wire,start,_,_=GW.wire_at(index,lift,length,gm['mouth'],gm.get('clock_degrees',0.))
            _,axis=GW.port(index,gm['mouth'],gm.get('clock_degrees',0.))
            cutter=cq.Solid.sweep(cq.Wire.makeCircle(2.6,start,axis),[],wire,
                                  makeSolid=True,isFrenet=True).intersect(
                                      box(40.,400.,343.,75.,445.,351.))
            tail_cutters.append(cutter);tail_names.append(label+'-'+str(lift))
    # Coincident clipped sweeps are retained as inspection records. Apply one
    # conservative rectangular clearance to the physical lap instead of
    # Boolean-cutting the repeated overlapping cylindrical faces.
    tail_lap_working=box(64.,415.5,343.,69.,438.3,351.)
    # The under-counter ring turns east past the controller's aft island.
    # Protect the completeØ4 pilot plus1.6mm surrounding stock while opening
    # the local fixed lap below351. The upper4mm and3.2mm seam backing remain.
    rear_controller=next(m for m in rear if m['mouth'][0]>0)
    px,py,_=rear_controller['mouth']
    controller_guard=cq.Solid.makeCylinder(3.6,8.,cq.Vector(px,py,343.))
    under_tail_working=box(52.2,416.6,343.,60.,421.4,351.).cut(controller_guard)
    tail_lap_working=tail_lap_working.fuse(under_tail_working)
    fixed_roof=fixed_roof.cut(tail_lap_working)
    ledge=ledge.cut(tail_lap_working);roots=roots.cut(tail_lap_working)
    station_parts={n:s.cut(tail_lap_working)for n,s in station_parts.items()}
    # The two printed mating articles share contact faces, never occupied
    # nominal stock. Remove the exact residual from all declared parent roots.
    nominal_joint_common=G.overlap(fixed_roof,hatch)
    fixed_roof=fixed_roof.cut(hatch)
    ledge=ledge.cut(hatch);roots=roots.cut(hatch)
    station_parts={n:s.cut(hatch)for n,s in station_parts.items()}
    # The controller island and fore insert tab meet at a reentrant corner.
    # Remove its unused underside nibs explicitly; their roof remains4mm
    # thick and the complete1.6mm controller pilot surround is west ofX53.9.
    controller_corner=box(54.79,416.99,346.99,55.55,419.,351.)
    fixed_roof=fixed_roof.cut(controller_corner)
    ledge=ledge.cut(controller_corner);roots=roots.cut(controller_corner)
    station_parts={n:s.cut(controller_corner)for n,s in station_parts.items()}
    # Retain the raw exact Boolean faces. Global simplify/clean can invalidate
    # the existing spline-backed receiver edges without changing occupancy.
    native_heal=None
    discarded_slivers = []
    if len(fixed_roof.Solids())>1:
        solids = sorted(fixed_roof.Solids(), key=lambda s:s.Volume(), reverse=True)
        if any(s.Volume()>=.001 for s in solids[1:]):
            print('Disconnected fixed-roof solids',[(s.Volume(),G.bounds(s)) for s in solids],flush=True)
            raise ValueError('A declared hatch support is disconnected from the fixed roof')
        discarded_slivers = [{'volume_mm3': s.Volume(), 'bounds_mm': G.bounds(s)} for s in solids[1:]]
        fixed_roof = solids[0]
    parts = {}

    def save(name, shape, role, detail):
        p = OUT/(name+'.brep')
        shape.exportBrep(str(p))
        parts[name] = {'brep': str(p.relative_to(ROOT)), 'sha256': sha(p),
                       'role': role, 'detail': detail, 'bounds_mm': G.bounds(shape),
                       'valid': shape.isValid(), 'solids': len(shape.Solids())}
        return shape

    if ground_pose is not None:
        for n in ['ground-stack','ground-roof-boss']:
            save(n,shapes[n],'structure','Native source transformed by the declared provisional ground datum and clock; pilot and stack dimensions retained.')
            inputs[n]={'brep':parts[n]['brep'],'sha256':parts[n]['sha256']}

    for name,boss in finished_controller_bosses.items():
        save(name,boss,'structure',
             'Original controller insert boss with the exact finished hatch seam groove; complete1.6mm pilot surround and3mm blind end cover retained.')
        inputs[name]={'brep':parts[name]['brep'],'sha256':parts[name]['sha256']}

    save('rear-roof-hatch', hatch, 'structure',
         'Exact native roof article carrying the ground boss and discharge anchor; controller and C14 roof islands retained.')
    save('enclosure-back-top', fixed_roof, 'structure',
         'Retained back-top with a vertical hatch aperture and fixed controller, WAGO and C14 stock.')
    selector_path = OUT/'roof-hatch-selector.brep'
    selector.exportBrep(str(selector_path))
    family_records={}
    for lift,cutter in zip([14,7,0],family_cutters):
        path=OUT/('hatch-hose-clearance-z-'+str(lift)+'.brep')
        cutter.exportBrep(str(path))
        family_records['hatch-hose-family-roof-'+str(lift)]={
            'brep':str(path.relative_to(ROOT)),'sha256':sha(path),'print_owner':'enclosure-back-top'}
    seated_path=OUT/'hatch-seated-hose-clearance.brep'
    family_cutters[-1].exportBrep(str(seated_path))
    water5_lap_path=OUT/'water5-lap-relief.brep';water5_lap.exportBrep(str(water5_lap_path))
    water2_path=OUT/'water2-hatch-relief.brep';water2_roof.exportBrep(str(water2_path))
    controller_corner_path=OUT/'controller-island-corner-clearance.brep';controller_corner.exportBrep(str(controller_corner_path))
    g2_channel_path=OUT/'g2-fore-tool-channel.brep';g2_channel.exportBrep(str(g2_channel_path))
    tail_records={};tail_inspection_records={}
    tail_working_path=OUT/'ground-tail-lap-working-channel.brep'
    tail_lap_working.exportBrep(str(tail_working_path))
    tail_records['ground-tail-lap-working-channel']={'brep':str(tail_working_path.relative_to(ROOT)),
        'sha256':sha(tail_working_path),'print_owner':'enclosure-back-top',
        'maximum_cut_z_mm':351.,'minimum_upper_stock_mm':4.,
        'method':'Conservative rectangular clearance covering the four temporary ground-tail families, independent of coincident clipped sweep faces.'}
    for label,cutter in zip(tail_names,tail_cutters):
        p=OUT/('ground-tail-lap-'+label+'.brep');cutter.exportBrep(str(p))
        tail_inspection_records['ground-tail-lap-'+label]={'brep':str(p.relative_to(ROOT)),
            'sha256':sha(p),'inspection_only':True,'radial_air_mm':1.,
            'maximum_cut_z_mm':351.,'minimum_upper_stock_mm':4.}
    neighbor_records={}
    for name,cutter in hatch_neighbor_cutters.items():
        p=OUT/(name+'-hatch-clearance.brep');cutter.exportBrep(str(p))
        neighbor_records[name+'-hatch-clearance']={'brep':str(p.relative_to(ROOT)),
            'sha256':sha(p),'print_owner':'rear-roof-hatch','air_mm':1.,
            'minimum_exterior_roof_stock_mm':355.-G.bounds(cutter)[5]}
    save('hatch-lap-ledge', join_stock(ledge,roots,'hatch-lap-ledge','parent-stock-roots').cut(seam_seal), 'structure', '4mm lap and parent-stock roots, clear of controller and all supply tool approaches.')
    save('hatch-seam-silicone', seam_seal, 'structure', 'Factory-cast bonded silicone in1.2mm×0.8mm top seam groove; minimum underlying hatch rim3.2mm.')
    for n, s in station_parts.items():
        save(n, s.cut(seam_seal), 'structure', 'Ø8 insert station or3mm support web rooted in the fixed roof.')
    for n, s in screws.items():
        save(n, s, 'structure', 'Recessed M3×8 cap screw with nominal2.5AF socket; maximum appliance height355.')
    for i, (x, y) in enumerate(FASTENERS, 1):
        cap = cq.Solid.makeCylinder(2.9, .5, cq.Vector(x, y, 354.5))
        rr = 2.5/math.sqrt(3)
        pts = [cq.Vector(x+rr*math.cos(k*math.pi/3), y+rr*math.sin(k*math.pi/3), 352.7) for k in range(6)]
        cap = join_stock(cap,cq.Solid.extrudeLinear(cq.Wire.makePolygon(pts+[pts[0]]), [], cq.Vector(0, 0, 1.8)),
                         'hatch-screw-silicone-cap-'+str(i),'socket-fill')
        save('hatch-screw-silicone-cap-'+str(i), cap, 'structure', 'Flush factory cast cap and socket fill after screw torque, using the funnel casting silicone.')
    pilots = {}
    for n, s in pilot_records.items():
        p = OUT/(n+'.brep')
        s.exportBrep(str(p))
        pilots[n] = {'brep': str(p.relative_to(ROOT)), 'sha256': sha(p), 'print_owner': 'enclosure-back-top'}
    for n, s in hatch_pilots.items():
        p = OUT/(n+'.brep')
        s.exportBrep(str(p))
        pilots[n] = {'brep': str(p.relative_to(ROOT)), 'sha256': sha(p), 'print_owner': 'rear-roof-hatch'}
    print('hatch native', hatch.isValid(), len(hatch.Solids()),
          'fixed roof', fixed_roof.isValid(), len(fixed_roof.Solids()), flush=True)
    absent = {'enclosure-front-top', 'funnel', 'funnel-frame', 'funnel-cover',
              'asse-drip-pan', 'moisture-plate', 'display', 'display-cover', 'display-gasket'}
    deferred = {n for n in shapes if n.startswith(('wire-', 'control-', 'loom-', 'harness-'))}
    deferred |= {'tube-water-2', 'tube-water-3', 'tube-water-5', 'tube-water-6',
                 'tube-water-supply-link', 'tube-co2-0', 'tube-co2-1', 'tube-carb-1',
                 'tube-fluid-1', 'tube-fluid-2', 'tube-fluid-14', 'tube-fluid-18', 'tube-fluid-28'}
    moving = {n: shapes[n] for n in CARRIED}
    moving['rear-roof-hatch'] = hatch
    carried_internal_checks=[]
    for name in sorted(CARRIED-{'ground-roof-boss','discharge-chain-anchor'}):
        common=G.overlap(shapes[name],hatch)
        gap=shapes[name].distance(hatch)
        row={'carried':name,'other_carried':'rear-roof-hatch','common_mm3':common,
             'gap_mm':gap,'pass':common<.001}
        carried_internal_checks.append(row)
        print('hatch internal',name,row,flush=True)
    fixed = {n: s for n, s in shapes.items() if n not in CARRIED|absent|deferred}
    fixed['enclosure-back-top'] = fixed_roof
    boxes = {n: G.bounds(s) for n, s in fixed.items()}
    rigid_poses, rigid_blockers = [], []
    for z in [22.5,18.,14., 12., 6., 3., 1., .25, 0.]:
        rows = []
        for n, source in moving.items():
            s = source.translate((0, 0, z))
            b = G.bounds(s)
            for other, t in fixed.items():
                v = boxes[other]
                if not all(b[i]<=v[i+3] and v[i]<=b[i+3] for i in range(3)):
                    continue
                gap = s.distance(t)
                if gap>1e-6:
                    continue
                common = G.overlap(s, t)
                if common>.01:
                    row = {'hatch_z_mm': z, 'carried': n, 'fixed': other, 'common_mm3': common}
                    rows.append(row)
                    rigid_blockers.append(row)
        rigid_poses.append({'hatch_z_mm': z, 'pass': not rows, 'blockers': rows})
        print('hatch Z', z, 'blockers', rows, flush=True)
    # Conservative whole nominal key: long entering leg vertical, short handle
    # above the appliance. This moves through the open hatch before it is fitted.
    import probe_psu_tools as K
    K.SHORT, K.LONG = 160., 32.
    tool_poses = []
    tool_fixed = {**fixed}
    for i, m in enumerate([m for m in structure['mounts'] if m['owner']=='psu'], 1):
        x, y, _ = m['mouth']
        tip = (x, y, G.bounds(shapes['supply-screw-'+str(i)])[5]-1.7)
        key, _, _ = K.key(tip, (1, 0, 0))
        for travel in [0., 1.8, 10., 30., 60.]:
            tool = key.translate((0, 0, travel))
            b = G.bounds(tool)
            bad = []
            for n, s in tool_fixed.items():
                if n=='supply-screw-'+str(i):
                    continue
                v = boxes[n]
                if not all(b[j]<=v[j+3] and v[j]<=b[j+3] for j in range(3)):
                    continue
                common = G.overlap(tool, s)
                if common>.01:
                    bad.append({'other': n, 'common_mm3': common})
            path = OUT/('supply-tool-'+str(i)+'-'+str(travel)+'.brep')
            tool.exportBrep(str(path))
            tool_poses.append({'station': i, 'withdraw_z_mm': travel,
                               'brep': str(path.relative_to(ROOT)), 'pass': not bad, 'blockers': bad})
            print('hatch tool', i, travel, bad, flush=True)
    fastener_checks = []
    for i, (x, y) in enumerate(FASTENERS, 1):
        boss = station_parts['hatch-roof-boss-'+str(i)]
        bad = []
        b = G.bounds(boss)
        for n, s in {**fixed, **moving}.items():
            if n in ['enclosure-back-top', 'rear-roof-hatch']:
                continue
            v = G.bounds(s)
            if not all(b[j]<=v[j+3] and v[j]<=b[j+3] for j in range(3)):
                continue
            common = G.overlap(boss, s)
            if common>.01:
                bad.append({'other': n, 'common_mm3': common})
        surround=cq.Solid.makeCylinder(3.6,9.5,cq.Vector(x,y,339.)).cut(
            cq.Solid.makeCylinder(2.,6.5,cq.Vector(x,y,342.)))
        missing=surround.cut(boss).Volume()
        fastener_checks.append({'station': i, 'xy_mm': [x, y], 'pass': not bad and missing<.001,
                               'blockers': bad,'full_1_6mm_pilot_surround_and_3mm_cap_missing_mm3':missing})
        print('hatch boss', i, bad, flush=True)
    rail_checks=[]
    # A continuous3×3mm coupon joins each fore insert node to its roof web.
    # It avoids the pilot and proves that the route relief did not sever the
    # load path even when the support remains a nominal single solid.
    for i,root_y in [(1,417.65),(3,RECT[1]-10.8)]:
        x,y=FASTENERS[i-1]
        if i==1:
            coupon=box(x+2.,root_y,345.5,x+5.,root_y+3.,348.5)
            support=station_parts['hatch-roof-web-1']
            ends=[root_y,root_y+3.]
        else:
            coupon=box(x-4.,root_y,345.5,x-1.,y-4.,348.5)
            support=station_parts['hatch-roof-beam-'+str(i)]
            ends=[root_y,y-4.]
        missing=coupon.cut(support).Volume()
        rail_checks.append({'station':i,'continuous_stock_mm':[3.,3.],
                            'root_to_node_y_mm':ends,
                            'missing_mm3':missing,'pass':missing<.001})
    meter_notch_checks=[]
    for name in ['meter-roof-seat-1','meter-roof-seat-2']:
        host=shapes[name]
        hatch_gap=hatch.distance(host);lap_gap=ledge.distance(host)
        meter_notch_checks.append({'fixed_root':name,'hatch_air_mm':hatch_gap,
                                   'lap_air_mm':lap_gap,
                                   'pass':hatch_gap>=1.-1e-6 and lap_gap>=1.-1e-6})
    hatch_tool_poses=[]
    for i,(x,y) in enumerate(FASTENERS,1):
        tool,_,_=K.key((x,y,352.8),(1,0,0))
        for travel in [0.,1.8,10.,30.,60.]:
            t=tool.translate((0,0,travel))
            b=G.bounds(t)
            bad=[]
            for n,s in {**fixed,**moving,**screws}.items():
                if n=='hatch-screw-'+str(i):
                    continue
                v=G.bounds(s)
                if not all(b[j]<=v[j+3] and v[j]<=b[j+3] for j in range(3)):
                    continue
                common=G.overlap(t,s)
                if common>.01:
                    bad.append({'other':n,'common_mm3':common})
            path=OUT/('hatch-tool-'+str(i)+'-'+str(travel)+'.brep')
            t.exportBrep(str(path))
            hatch_tool_poses.append({'station':i,'withdraw_z_mm':travel,
                                     'brep':str(path.relative_to(ROOT)),
                                     'pass':not bad,'blockers':bad})
            print('hatch screw tool',i,travel,bad,flush=True)
    report = {'parts': parts, 'selector': {'brep': str(selector_path.relative_to(ROOT)), 'sha256': sha(selector_path)},
              'rectangle_xy_mm': RECT, 'controller_islands': islands,
              'fixed_meter_root_notches':{'method':'Four-mm native seat bounding-footprint notch through the hatch plan; the three-mm grown lap stays one-mm clear. The complete fixed351.01mm roof roots retain their endpoint.',
                                         'fixed_seat_bounds_mm':meter_root_notches,
                                         'notch_plan_air_mm':4.,'grown_lap_air_mm':1.,
                                         'checks':meter_notch_checks},
              'c14_keepout_xy_mm': [-120., cb[1]-3., cb[3]+4., cb[4]+3.],
              'wago_keepout_end_y_mm': wb[4]+1.,
              'carried_names': sorted(CARRIED), 'rigid_poses': rigid_poses,
              'carried_internal_checks':carried_internal_checks,
              'tool_poses': tool_poses, 'fastener_reservations': fastener_checks,
              'continuous_support_stock':rail_checks,
              'ground_tail_inspection_cutters':tail_inspection_records,
              'hatch_tool_poses':hatch_tool_poses,
              'mounts': [{'owner': 'rear-roof-hatch', 'index': i, 'mouth': [x, y, 348.5],
                          'axis': [0, 0, -1], 'pilot_depth': 6.5, 'insert_length': 4.,
                          'root_cover': 3., 'screw_length': 8., 'head_bearing_z': 351.5,
                          'head_top_z': 354.5, 'actual_engagement': 5., 'tip_reserve': 1.5}
                         for i, (x, y) in enumerate(FASTENERS, 1)],
              'native_inputs': inputs, 'manifest_sha256': manifests,
              'manifest_content_sha256':manifest_contents,
              'source_inputs':sources,
              'material_join_checks':{'method':'Guarded native joins preserve each full operand, bound result volume by operand volumes, and independently reject missing operand material or result material outside both operands. Temporary selectors and inspection cutters are not physical joins.',
                                      'maximum_missing_or_added_material_mm3':.001,
                                      'checks':material_joins},
              'controller_finish_checks':controller_finish_checks,
              'pass': not rigid_blockers and all(r['pass'] for r in tool_poses+fastener_checks+hatch_tool_poses+rail_checks+meter_notch_checks+carried_internal_checks)
                      and hatch.isValid() and len(hatch.Solids())==1
                      and fixed_roof.isValid() and len(fixed_roof.Solids())==1
                      and all(row['pass'] for row in controller_finish_checks),
              'replacement_names': ['enclosure-back-top',*finished_controller_bosses], 'pilot_cutters': pilots,
              'root_owner_overrides': {'ground-roof-boss': 'rear-roof-hatch', 'discharge-chain-anchor': 'rear-roof-hatch'},
              'pilot_owner_overrides': {'ground': 'rear-roof-hatch'},
              'shell_fuse_part_names': ['hatch-lap-ledge', *station_parts],
              'clearance_cutters': {
                  'hatch-seam-groove-roof': {**parts['hatch-seam-silicone'], 'print_owner': 'enclosure-back-top'},
                  'hatch-seam-groove-article': {**parts['hatch-seam-silicone'], 'print_owner': 'rear-roof-hatch'},
                  **family_records,
                  **tail_records,
                  **neighbor_records,
                  'water2-hatch-relief':{'brep':str(water2_path.relative_to(ROOT)),
                                          'sha256':sha(water2_path),'print_owner':'enclosure-back-top',
                                          'native_route_source':water2_record,
                                          'minimum_exterior_roof_stock_mm':355.-G.bounds(water2_roof)[5]},
                  'water2-hatch-article-relief':{'brep':str(water2_path.relative_to(ROOT)),
                                          'sha256':sha(water2_path),'print_owner':'rear-roof-hatch',
                                          'native_route_source':water2_record,
                                          'minimum_exterior_roof_stock_mm':355.-G.bounds(water2_roof)[5]},
                  'controller-island-corner':{'brep':str(controller_corner_path.relative_to(ROOT)),
                                          'sha256':sha(controller_corner_path),'print_owner':'enclosure-back-top',
                                          'minimum_exterior_roof_stock_mm':4.},
                  'water5-lap-relief':{'brep':str(water5_lap_path.relative_to(ROOT)),
                                       'sha256':sha(water5_lap_path),'print_owner':'enclosure-back-top'},
                  'g2-fore-tool-channel':{'brep':str(g2_channel_path.relative_to(ROOT)),
                                           'sha256':sha(g2_channel_path),'print_owner':'enclosure-back-top',
                                           'minimum_exterior_roof_stock_mm':3.},
                  'hatch-hose-seated-article': {'brep':str(seated_path.relative_to(ROOT)),
                                               'sha256':sha(seated_path),'print_owner':'rear-roof-hatch'}},
              'hose_handling_pocket': {'sampled_poses':family_poses,'hose_air_mm':1.,
                                       'removed_fixed_roof_bounds_mm':removed_bounds,
                                       'minimum_remaining_exterior_roof_stock_mm':355.-removed_bounds[5] if removed_bounds else None},
              'discarded_boolean_slivers': discarded_slivers,
              'native_topology_heal':native_heal,
              'removed_nominal_joint_overlap_mm3':nominal_joint_common,
              'final_nominal_joint_overlap_mm3':G.overlap(fixed_roof,hatch),
              'ground_pose_override':{'datum_mm':ground_pose[0],'clock_degrees':ground_pose[1]}if ground_pose else None,
              'standalone_print_parts': {'rear-roof-hatch': {'source_part': 'rear-roof-hatch', 'rotation_x_deg': 180,
                                         'fuse_part_names': ['ground-roof-boss', 'discharge-chain-anchor']}},
              'joint': {'ordinary_stock_mm': 3., 'slip_per_side_mm': .15, 'lap_z_mm': [347., 351.],
                         'hatch_rim_z_mm': [351., 355.], 'head_web_mm': 3.,
                         'seal_groove_mm': [1.2, .8], 'minimum_stock_below_groove_mm': 3.2,
                         'seal_method': 'Cast and permanently bond the continuous top groove and four flush head/socket caps after hatch torque, using the existing funnel silicone. Surface bonding and leak retention require physical qualification.'},
              'factory_access': {
                  'g2_tool_report': 'future/pump-first-layout-study/structure/g2-factory-tool-probe.json',
                  'ground_tail_report': 'future/pump-first-layout-study/structure/ground-make-up-check.json',
                  'braid_report': 'future/pump-first-layout-study/structure/hatch-hose-check.json',
                  'front_loom_handling_report': 'future/pump-first-layout-study/wiring/front-loom-handling.json',
                  'sequence': [
                      'Precrimp the four ground rings to their final cut lengths and torque the complete fan on the removed hatch; retain free opposite ends. Preassemble the discharge union, key and clamp on that article.',
                      'Slide the populated back-top 237.5 mm onto its empty back-bottom, then bring the assembled back column over the core from fully aft. Keep the hatch, ASSE, purchased VK and front-top/frame absent, the supply supported in its declared loose fixture and cross-boundary tubes and wires free. Fasten the supply through the open hatch with the native vertical key reservation; install the separately held ASSE and bolted carrier afterward.',
                      'Engage the fixed pump barb with the hatch raised14mm, then land it through the separately checked constant-length R15.9 hose family. Dress the four free wire tails through their individual native landing reservations.',
                      'Make up WAGO-G2 before other looms occupy its access channel, using the native staged hook approach and34mm straight normal wire insertion. Terminate the other free ends and dress the installed routes.',
                      'Torque the four hatch screws and install the pan. Keep the display and J9 absent; carry the complete constant-length parked J13 contact lead with the prepared front-top/frame through the independently checked102.2mm late closure path in front-loom-handling.json.',
                      'Keep the hatch seated and silicone funnel absent. Release and manually dress the free J13 board end through the open funnel/display apertures and make its existing XH termination; install the display and J9 afterward. Final dressing, connector insertion and workholding remain unqualified manual processes. Inspect the completed connections, then permanently bond the cast hatch seam/head caps and fit the silicone funnel and cover.'
                  ],
                  'scope': 'Rigid roof/hatch and tool poses, the sampled constant-cut-length braid family, and sampled free-ended ground tails have separate native reports. Flexible compliance, wire dressing, crimping, applied torque, workholding and seal retention remain physical qualifications.'
              },
              'scope': 'Exact hatch split, carried rigid +Z landing and open-aperture PSU tool reservations. Final ledges, root connection, screw passage and sealing joint are separately regenerated and checked.',
              'qualification_limits': ['Hatch joint sealing, insert retention, applied torque and factory workholding are physical properties.',
                  'Installed flexible wires/tubes remain free while the back-top Y rails close. The braided discharge loop gets a separate constant-length hatch +Z family.']}
    report['geometry_pass']=report['pass']
    report['native_validity']={'hatch':{'valid':hatch.isValid(),'solids':len(hatch.Solids())},
                               'fixed_roof':{'valid':fixed_roof.isValid(),'solids':len(fixed_roof.Solids())}}
    drift = [n for n, r in inputs.items() if sha(ROOT/r['brep']) != r['sha256']]+proof_sources.changed(sources)
    report['source_drift'] = drift
    report['manifest_drift']=[n for n,h in manifest_contents.items()if manifest_content_sha256(ROOT/n)!=h]
    report['pass'] = report['pass'] and not drift and not report['manifest_drift']
    (Path(report_path)if report_path else HERE/'roof-hatch.json').write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps({'pass': report['pass'], 'rigid_blockers': len(rigid_blockers)}), flush=True)


if __name__=='__main__':
    main()
