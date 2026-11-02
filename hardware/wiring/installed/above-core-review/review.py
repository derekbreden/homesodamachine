"""Manual current-fine electrical layout, holder and driver study.

The explicit current fine cohort replaces the native fixture/cache. This tool
never builds an appliance or writes BREP geometry and is not a build/commit gate.
"""
import argparse
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[4]
sys.path[:0]=[str(ROOT),str(ROOT/'hardware/scripts'),str(ROOT/'hardware/manifold-layout')]
from hardware.wiring.installed._fine_contacts import (
    current_fine,fine_arguments,fine_overlap,junction_geometry,source_layout,
    wire_source_reading,cap_trial_replacements)
HERE=Path(__file__).resolve().parent
TEMP=ROOT/'tmp/above-core-electrical-fixture'
OUTPUT=HERE/'native-review.json'


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    fine_arguments(parser,ROOT)
    parser.add_argument('--reuse-fixture',action='store_true',help='Reuse only the explicit hash-bound fine index')
    parser.add_argument('--compose-only',action='store_true')
    parser.add_argument('--pack-fixture',action='store_true',help='Select the bound pack/front/roof entries; build nothing')
    parser.add_argument('--refresh-selected',action='store_true',help='Require the explicit fine cohort to match current source; never mix replacement CAD')
    parser.add_argument('--contact-wires',nargs='+')
    parser.add_argument('--export-wiring',action='store_true',help='Write a fine reference index; no BREP cache')
    parser.add_argument('--cap-cup',type=Path,help='Optional exact fine cap trial model')
    parser.add_argument('--cap-lid',type=Path,help='Optional exact fine lid trial model')
    parser.add_argument('--cap-frames',type=Path,help='Explicit model SHA, qualified body and rigid 3x4 installed frame for cup/lid')
    parser.add_argument('--junctions',nargs='+',help='Bounded source junction names for holder/driver questions')
    parser.add_argument('--obstacles',nargs='+',help='Bounded qualified physical obstacle names')
    parser.add_argument('--output',type=Path,default=OUTPUT)
    args=parser.parse_args(argv)
    if args.reuse_fixture and not args.fine_index:args.fine_index=TEMP/'fine/index.json'
    context=current_fine(args);manifest=context.manifest
    caps={}
    if args.cap_cup or args.cap_lid or args.cap_frames:
        caps=cap_trial_replacements(context,args.cap_cup,args.cap_lid,args.cap_frames)
    source=wire_source_reading(context)
    names=list(context.names())
    if args.pack_fixture:
        pieces=context.facts.get('pieces',{})
        omitted={name if name.startswith('enclosure-')else'enclosure-'+name for name in pieces}
        names=[name for name in names if name.rsplit('/',1)[-1]not in omitted]
    if args.obstacles:
        wanted={context.resolve(name)[1]for name in args.obstacles}
        names=[name for name in names if name in wanted]
    routes=manifest['routes'];terminals=manifest['terminals']
    if args.contact_wires and set(args.contact_wires)-{row['id']for row in routes}:
        raise ValueError('Unknown current conductor IDs')
    body_rows={row['name']:row for row in source['bodies']}
    failures=[{'wire':route['id'],'error':'Current fine body does not match its regenerated source recipe'}
              for route in routes if not body_rows.get('wire-'+route['id'],{}).get('matches')]
    term_failures=[name for name in manifest['terminations']if not body_rows.get(name,{}).get('matches')]
    record={'scope':'Focused current authoritative fine above-core terminal/lead/housing, source holder and driver questions. Current-source numeric proof is reused when explicitly bound. No appliance/CAD build or physical wiring qualification.',
        'physical_fixture_scope':'Bound current fine pack/front/roof entries'if args.pack_fixture else'Bound current complete fine appliance',
        'physical_fixture_sha256':context.digest(context.aggregate),'cap_fixture_sha256':caps,
        'contact_review_run':not args.compose_only,'contact_wires':args.contact_wires if not args.compose_only else[],
        'connection_count':manifest['connection_count'],'fixture_names':names,
        'reference_frames':manifest['reference_frames'],'cable_passages':manifest['cable_passages'],
        'interfaces':manifest['interfaces'],'route_failures':failures,'route_intersections':[],
        'termination_failures':term_failures,'terminations':manifest['terminations'],'bundles':manifest['bundles'],
        'routes':routes,'terminals':terminals,'junction_driver_intersections':[],'holder_intersections':[],
        'fine_boolean_count':0,'review_complete':False,'selected_obstacles':names,
        'source_binding':{key:value for key,value in source.items()if key not in('bodies','source_curve_maximum_deltas_mm','source_conductor_recipe_deltas')}}
    layout=source_layout(context)
    exterior_tubes={name.rsplit('/',1)[-1]for name in names if name.rsplit('/',1)[-1].startswith('tube-')}
    external_core=(exterior_tubes|set(layout.core_equipment_names())|{'digiten-flow','soda-bend-holder',
        'soda-continuous-insulation','tube-soda-core-rise','reservoir-b-fill-lower','reservoir-b-fill-upper',
        'wago-v12','wago-gnd','wago-sensors','wago-reeds-b'})
    obstacles=[name for name in names if not name.startswith(('wire-','wiring-','terminal-'))and
               (not name.startswith('cold-core/')or name.rsplit('/',1)[-1]in external_core or
                name.rsplit('/',1)[-1]in('foam-cap-bottom','foam-cap-lid-top'))]
    if not args.compose_only:
        pairs=[];owners=[]
        for route in routes:
            if args.contact_wires and route['id']not in args.contact_wires:continue
            if any(row['wire']==route['id']for row in failures):continue
            wire=context.resolve('wire-'+route['id'],'wiring')
            own={terminals[key]['part'].rsplit('/',1)[-1]for key in(route['start'],route['end'])}
            for name in obstacles:
                if name.rsplit('/',1)[-1]in own or name in('funnel','funnel-cover','display-gasket'):continue
                target=context.resolve(name)
                if fine_overlap(context.bounds(wire),context.bounds(target)):
                    pairs.append((wire,target));owners.append((route['id'],name))
        for(wire,name),reading in zip(owners,context.commons(pairs)):
            record['fine_boolean_count']+=reading['entry_common_count'];hit=reading['raw']
            if hit['volume_mm3']>.05:record['route_intersections'].append({'wire':wire,'part':name,
                                                                          'volume_mm3':round(hit['volume_mm3'],5)})
    geometry=junction_geometry(context,args.junctions)
    record['invalid_holders']=[parent for parent,ref in geometry['holders'].items()
                               if context.aux[ref[1]].is_empty()]
    junctions=list(geometry['poses'])if not args.junctions else args.junctions
    if set(junctions)-set(geometry['poses']):raise ValueError('Unknown source junction names')
    pairs=[];owners=[]
    for name in junctions:
        body=context.resolve(name)
        for driver,tool in geometry['drivers'].items():
            if fine_overlap(context.bounds(body),context.bounds(tool)):
                pairs.append((body,tool));owners.append(('driver',name,driver))
    for parent,holder in geometry['holders'].items():
        for name in names:
            if name.startswith('enclosure-')or(name.startswith('cold-core/')and name.rsplit('/',1)[-1]not in external_core):continue
            target=context.resolve(name)
            if fine_overlap(context.bounds(holder),context.bounds(target)):
                pairs.append((holder,target));owners.append(('holder',parent,name))
        for driver,tool in geometry['drivers'].items():
            if fine_overlap(context.bounds(holder),context.bounds(tool)):
                pairs.append((holder,tool));owners.append(('driver',parent+'-holder',driver))
    for(kind,name,other),reading in zip(owners,context.commons(pairs)):
        record['fine_boolean_count']+=reading['entry_common_count'];volume=reading['raw']['volume_mm3']
        if kind=='holder'and volume>.05:record['holder_intersections'].append([name,other,round(volume,5)])
        if kind=='driver'and volume>.001:record['junction_driver_intersections'].append([name,other,volume])
    if args.export_wiring:
        index=context.export_index(TEMP/'fine/index.json');record['wiring_fine_index']=str(index)
    record['valid_wire_count']=len(routes)-len(failures)
    record['source_sha256']={str(Path(__file__).relative_to(ROOT)):context.digest(Path(__file__))}
    record['fine_binding']=context.finish();record['review_complete']=True
    record['geometrically_clear']=not any(record[key]for key in('route_failures','route_intersections',
        'termination_failures','junction_driver_intersections','holder_intersections','invalid_holders'))
    args.output.write_text(json.dumps(record,indent=2)+'\n')
    print(json.dumps({key:record[key]for key in('connection_count','valid_wire_count','route_failures',
        'termination_failures','route_intersections','junction_driver_intersections','fine_boolean_count')}),flush=True)
    return record


if __name__=='__main__':main()
