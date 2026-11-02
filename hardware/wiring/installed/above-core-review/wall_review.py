"""Manual current-fine wiring check against the two installed valve supports.

Support material is cropped from the bound back-top by its source-defined stock.
No native geometry, BREP fixture, appliance or wiring generation runs.
"""
import argparse
import hashlib
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[4]
sys.path[:0]=[str(ROOT),str(ROOT/'hardware/scripts'),str(ROOT/'hardware/manifold-layout')]
from hardware.wiring.installed._fine_contacts import (
    current_fine,fine_arguments,fine_overlap,valve_wall_geometry)

HERE=Path(__file__).resolve().parent


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    fine_arguments(parser,ROOT)
    parser.add_argument('--bodies',nargs='+',help='Explicit wiring names for a bounded question')
    parser.add_argument('--output',type=Path,default=HERE/'wall-review.json')
    args=parser.parse_args(argv)
    context=current_fine(args)
    walls,datums=valve_wall_geometry(context)
    names=list(context.names('wiring'))
    if args.bodies:
        names=[context.resolve(name,'wiring')[1]for name in args.bodies]
    invalid=[name for name,ref in walls.items()if context.aux[ref[1]].is_empty()]
    record={'scope':'Actual current f64 wire/termination/jacket entries against actual back-top material inside both current source-defined valve support stocks. Source sockets/channels and later cuts remain actual bound material; bounds only prune. No physical qualification.',
        'body_count':len(names),'walls':{},'intersections':[],'errors':[],
        'fixture_aggregate_sha256':context.digest(context.aggregate),'source_sha256':{},
        'invalid_walls':invalid,'review_complete':False,'fine_boolean_count':0}
    pairs=[];owners=[]
    for wall,ref in walls.items():
        record['walls'][wall]={'bounds_mm':context.bounds(ref),'valid':wall not in invalid,
                               'stock_datums':datums[wall],'candidate_count':0}
        if wall in invalid:continue
        for name in names:
            body=context.resolve(name,'wiring')
            if fine_overlap(context.bounds(body),context.bounds(ref)):
                pairs.append((body,ref));owners.append((name,wall))
                record['walls'][wall]['candidate_count']+=1
    for(name,wall),reading in zip(owners,context.commons(pairs)):
        record['fine_boolean_count']+=reading['entry_common_count']
        hit=reading['raw']
        if hit['volume_mm3']>.01:
            record['intersections'].append({'body':name,'wall':wall,'volume_mm3':hit['volume_mm3'],
                                           'bounds_mm':hit['min']+hit['max']})
    record['source_sha256']={str(Path(__file__).relative_to(ROOT)):context.digest(Path(__file__))}
    record['fine_binding']=context.finish()
    record['review_complete']=True
    record['geometrically_clear']=not record['intersections']and not invalid
    args.output.write_text(json.dumps(record,indent=2)+'\n')
    print(json.dumps({key:record[key]for key in('body_count','fine_boolean_count','geometrically_clear')}),flush=True)
    return record


if __name__=='__main__':main()
