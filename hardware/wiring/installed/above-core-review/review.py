"""Manual native electrical-layout review; not part of a build or commit gate.

Run through tmp/takeover/cadq. The optional --reuse-fixture flag only reuses the
explicit temporary native fixture from the preceding run; no published model
or aggregate export is changed.
"""
import argparse
from dataclasses import asdict
import hashlib
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[4]
sys.path[:0]=[str(ROOT),str(ROOT/'hardware/scripts'),str(ROOT/'hardware/manifold-layout')]
import cadquery as cq
from hardware.wiring.installed import build
from hardware.wiring.installed.terminals import Attachments,bounds
from hardware.wiring.installed.connections import connections,interfaces
from hardware.wiring.installed.routes import routed
from hardware.wiring.installed.model import STOCK,shape
from hardware.wiring.installed.terminations import add_terminations
from hardware.wiring.installed.bundles import add_jackets

TEMP=ROOT/'tmp/above-core-electrical-fixture'
OUTPUT=Path(__file__).with_name('native-review.json')


def overlapping(a,b,tol=1e-5):
    aa,ab=bounds(a);ba,bb=bounds(b)
    return all(ab[i]>ba[i]+tol and bb[i]>aa[i]+tol for i in range(3))


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--reuse-fixture',action='store_true')
    parser.add_argument('--compose-only',action='store_true')
    parser.add_argument('--pack-fixture',action='store_true')
    parser.add_argument('--refresh-selected',action='store_true')
    parser.add_argument('--aggregate',type=Path)
    parser.add_argument('--contact-wires',nargs='+')
    parser.add_argument('--export-wiring',action='store_true')
    parser.add_argument('--cap-cup',type=Path)
    parser.add_argument('--cap-lid',type=Path)
    args=parser.parse_args()
    import enclosure_assembly as ea
    TEMP.mkdir(parents=True,exist_ok=True)
    index=TEMP/'index.json'
    if args.aggregate:
        from _cadq_export import import_assembly
        scene=import_assembly(str(args.aggregate))
        fixture={'scope':'materialized production assembly '+str(args.aggregate)}
    elif args.reuse_fixture:
        fixture=json.loads(index.read_text())
        scene={n:(cq.Shape.importBrep(str(TEMP/file)),None)
               for n,file in fixture['parts'].items()}
    else:
        print('Build the native physical fixture',flush=True)
        attach=build.attach
        build.attach=lambda *args:None
        try:
            if args.pack_fixture:
                assembly,pack,box=ea.machine()
                assembly.box,assembly.pack=box,pack
                assembly.add(ea.build_display(box),name='display')
                cover,_=ea.build_display_cover(box)
                assembly.add(cover,name='display-cover')
                for name,entry in zip(('pump-contact-male','pump-contact-female'),ea.build_pump_contacts(box)):
                    assembly.add(entry[0],name=name)
                centre=ea.funnel_centre(box);seat=ea._enc.funnel_seat_z(box.outer)
                assembly.add(ea._funnel_frame.build(box.inner,box.y_joint,centre,seat),name='funnel-frame')
                for name,solid,_colour,_carry in ea.build_drain_joint(box):
                    assembly.add(solid,name=name)
                assembly.add(ea._enc._above_core_shell.access_panel(),name='electronics-access-panel')
                for name,solid in ea._dock.parts(box.pack.collet_plate).items():
                    assembly.add(solid,name=name)
            else:
                assembly=ea.build_enclosure_assembly()
        finally:
            build.attach=attach
        scene={n:(s,c) for n,s,c in ea.ml.placed_leaves(assembly)}
        files={}
        for i,(name,(solid,_color)) in enumerate(scene.items()):
            file=f'{i}.brep';solid.exportBrep(str(TEMP/file));files[name]=file
        fixture={'scope':'pack, fixed front hardware and roof interfaces' if args.pack_fixture else 'complete native appliance',
                 'parts':files}
        index.write_text(json.dumps(fixture,indent=2)+'\n')
        from _facts import _route_facts
        logical,native=_route_facts(assembly)
        (TEMP/'logical-routes.json').write_text(json.dumps({'runs':logical,'native_runs':native},indent=2)+'\n')
    if args.refresh_selected:
        import above_core_parts,above_core_wiring,above_core_routes
        for name,(solid,color,_carry) in {**above_core_parts.components(),
                                         **above_core_parts.core_components(),
                                         **above_core_wiring.components()}.items():
            target='cold-core/'+name if 'cold-core/'+name in scene else name
            scene[target]=(solid,color)
            if target!=name:scene.pop(name,None)
        scene['funnel-frame']=(ea._funnel_frame.build(),None)
    if args.cap_cup and args.cap_lid:
        import above_core
        location=above_core.frame_location(above_core.cap_lid_pose())
        cup=cq.Shape.importBrep(str(args.cap_cup)).translate((0.,0.,-ea._foam.top_cap_height)).moved(location)
        lid=cq.Shape.importBrep(str(args.cap_lid)).moved(location)
        scene['cold-core/foam-cap-top']=(cup,None)
        scene['cold-core/foam-cap-lid-top']=(lid,None)
    print('Resolve actual terminal frames and complete electrical graph',flush=True)
    at=Attachments(scene,ea);at.resolve()
    graph=connections();routes=routed(graph,at)
    records={'scope':'Focused native above-core junction, terminal-frame, lead and housing review; no physical wiring qualification.',
             'physical_fixture_scope':fixture['scope'],
             'physical_fixture_sha256':(hashlib.sha256(args.aggregate.read_bytes()).hexdigest()
                                        if args.aggregate else None),
             'cap_fixture_sha256':{str(path):hashlib.sha256(path.read_bytes()).hexdigest()
                                   for path in (args.cap_cup,args.cap_lid) if path},
             'contact_review_run':not args.compose_only,
             'contact_wires':args.contact_wires if not args.compose_only else [],
             'connection_count':len(graph),'fixture_names':sorted(scene),
             'reference_frames':at.frame_checks,'cable_passages':at.passages,
             'interfaces':interfaces(at.terminals,graph),'route_failures':[],
             'route_intersections':[],'termination_failures':[]}
    wires=cq.Assembly(name='review-wiring')
    wire_shapes={}
    for route in routes:
        try:
            solid=shape(route,STOCK[route.connection.stock]['od_mm'])
            if not solid.isValid() or solid.Volume()<=0:
                raise ValueError('Invalid or empty insulated conductor')
            wire_shapes[route.connection.id]=solid
            wires.add(solid,name='wire-'+route.connection.id)
        except Exception as error:
            records['route_failures'].append({'wire':route.connection.id,'error':str(error)})
    print(f'{len(wire_shapes)}/{len(graph)} complete insulated conductors are valid',flush=True)
    print('Route failures',records['route_failures'],flush=True)
    try:
        records['terminations']=add_terminations(wires,at,graph,routes)
        records['bundles']=add_jackets(wires,at)
    except Exception as error:
        records['termination_failures'].append(str(error))
    records['routes']=[r.record() for r in routes]
    records['terminals']={k:asdict(v) for k,v in at.terminals.items()}
    if args.export_wiring:
        folder=TEMP/'wiring';folder.mkdir(exist_ok=True)
        files={}
        for i,(name,solid,_color) in enumerate(ea.ml.placed_leaves(wires)):
            file=f'{i}.brep';solid.exportBrep(str(folder/file));files[name]=file
        (folder/'index.json').write_text(json.dumps({'parts':files},indent=2)+'\n')
        records['wiring_brep_index']=str((folder/'index.json').relative_to(ROOT))
    records['review_complete']=False
    OUTPUT.write_text(json.dumps(records,indent=2)+'\n')
    import above_core
    # Qualified core tenants include every native exterior tube as well as the
    # purchased equipment. Closed wet internals remain outside this question.
    exterior_tubes=frozenset(n.rsplit('/',1)[-1] for n in scene
                              if n.rsplit('/',1)[-1].startswith('tube-'))
    external_core=(exterior_tubes | above_core.core_equipment_names() |
                   frozenset(('digiten-flow','soda-inlet-stem','tube-soda-core-rise',
                              'reservoir-b-fill-lower','reservoir-b-fill-upper',
                              'wago-v12','wago-gnd','wago-sensors','wago-reeds-b',
                              'ground-stack')))
    if not args.compose_only:
        print('Check routed leads against native equipment, cap, tubes and roof interfaces',flush=True)
        # Foam fill and intact core-shell solids represent material around
        # existing internal harness channels; this question concerns relocated
        # external runs and their cap crossings, not requalification of them.
        obstacles={n:s for n,(s,_c) in scene.items()
                   if not n.startswith(('wire-','wiring-','terminal-')) and
                   (not n.startswith('cold-core/') or
                    n.rsplit('/',1)[-1] in external_core or
                    n in ('cold-core/foam-cap-top','cold-core/foam-cap-lid-top'))}
        for route in routes:
            if args.contact_wires and route.connection.id not in args.contact_wires:continue
            solid=wire_shapes.get(route.connection.id)
            if solid is None:continue
            own={at.terminals[k].part.rsplit('/',1)[-1]
                 for k in (route.connection.start,route.connection.end)}
            for name,body in obstacles.items():
                if name.rsplit('/',1)[-1] in own or name in ('funnel','funnel-cover','display-gasket'):
                    continue
                if not overlapping(solid,body):continue
                volume=solid.intersect(body).Volume()
                if volume>.05:
                    records['route_intersections'].append({'wire':route.connection.id,'part':name,
                                                          'volume_mm3':round(volume,5)})
    import above_core_wiring as junctions
    columns=junctions.driver_columns()
    records['junction_driver_intersections']=[]
    for name,(body,_color,_carry) in junctions.components().items():
        for driver,tool in columns.items():
            if overlapping(body,tool):
                v=body.intersect(tool).Volume()
                if v>.001:records['junction_driver_intersections'].append([name,driver,v])
    records['holder_intersections']=[]
    for parent in ('cold-core','front-top','back-top'):
        features=(junctions.cap_features() if parent=='cold-core' else junctions.shell_features(parent))
        holder=features['add'].cut(features['cut'])
        for name,(body,_color) in scene.items():
            if name.startswith('enclosure-') or (name.startswith('cold-core/') and
                                                name.rsplit('/',1)[-1] not in external_core):
                continue
            if not overlapping(holder,body):continue
            volume=holder.intersect(body).Volume()
            if volume>.05:
                records['holder_intersections'].append([parent,name,round(volume,5)])
        for driver,tool in columns.items():
            if overlapping(holder,tool):
                volume=holder.intersect(tool).Volume()
                if volume>.001:records['junction_driver_intersections'].append([parent+'-holder',driver,volume])
    records['valid_wire_count']=len(wire_shapes)
    records['review_complete']=True
    records['source_sha256']={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest()
                             for p in [ROOT/'hardware/manifold-layout/above-core.json',
                                       ROOT/'hardware/manifold-layout/above_core_wiring.py',
                                       *[ROOT/'hardware/wiring/installed'/n for n in
                                         ('terminals.py','routes.py','route-overrides.json','bundles.py','bundle-routes.json','terminations.py','connections.py')]]}
    OUTPUT.write_text(json.dumps(records,indent=2)+'\n')
    for key in ('connection_count','valid_wire_count','route_failures','termination_failures',
                'route_intersections','junction_driver_intersections'):
        print(key,records[key],flush=True)


if __name__=='__main__':main()
