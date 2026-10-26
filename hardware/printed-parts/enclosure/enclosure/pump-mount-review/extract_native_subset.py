"""Extract selected named AP214 assembly subtrees without materializing other BReps."""
from array import array
from pathlib import Path
import argparse
import hashlib
import json
import re

RECORD=re.compile(rb'#(\d+)\s*=\s*(.*?);',re.S)
STRING=re.compile(rb"'((?:[^']|'')*)'")
REFERENCE=re.compile(rb'#(\d+)')
STRUCTURE={b'PRODUCT',b'PRODUCT_DEFINITION_FORMATION',b'PRODUCT_DEFINITION',
    b'PRODUCT_DEFINITION_SHAPE',b'SHAPE_DEFINITION_REPRESENTATION',
    b'NEXT_ASSEMBLY_USAGE_OCCURRENCE',b'CONTEXT_DEPENDENT_SHAPE_REPRESENTATION',
    b'PRODUCT_RELATED_PRODUCT_CATEGORY'}


def refs(value):
    return [int(v) for v in REFERENCE.findall(STRING.sub(b"''",value))]


def base(name):
    return re.sub(r'/\d+$','',name)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('source',type=Path)
    p.add_argument('cache_index',type=Path)
    p.add_argument('--out',type=Path,required=True)
    p.add_argument('--report',type=Path,required=True)
    args=p.parse_args()
    source_sha=sha(args.source)
    wanted=set(json.loads(args.cache_index.read_text())['bodies'])
    data=args.source.read_bytes()
    starts,ends=array('Q',[0]),array('Q',[0])
    structural={}
    first=None
    count=0
    for match in RECORD.finditer(data):
        count+=1
        entity=int(match[1])
        if first is None:first=match.start()
        while len(starts)<=entity:
            starts.append(0);ends.append(0)
        starts[entity]=match.start();ends[entity]=match.end()
        body=match[2]
        kind=body.partition(b'(')[0].strip()
        if kind in STRUCTURE:structural[entity]=(kind,body,refs(body))
    products={i:STRING.search(body)[1].replace(b"''",b"'").decode()
              for i,(kind,body,_r) in structural.items() if kind==b'PRODUCT'}
    forms={i:r[-1] for i,(kind,_b,r) in structural.items()
           if kind==b'PRODUCT_DEFINITION_FORMATION'}
    definitions={i:products[forms[r[0]]] for i,(kind,_b,r) in structural.items()
                 if kind==b'PRODUCT_DEFINITION'}
    arcs={}
    for i,(kind,body,r) in structural.items():
        if kind!=b'NEXT_ASSEMBLY_USAGE_OCCURRENCE':continue
        values=[v.replace(b"''",b"'").decode() for v in STRING.findall(body)]
        arcs[i]=dict(parent=r[-2],child=r[-1],name=values[1] or definitions[r[-1]])
    selected_arcs={i for i,arc in arcs.items() if base(arc['name']) in wanted}
    selected_defs={arc[key] for i,arc in arcs.items() if i in selected_arcs
                   for key in ('parent','child')}
    changed=True
    while changed:
        added={i for i,arc in arcs.items() if arc['child'] in selected_defs}-selected_arcs
        selected_arcs.update(added)
        more={arcs[i]['parent'] for i in added}-selected_defs
        selected_defs.update(more)
        changed=bool(added or more)
    pds={i for i,(kind,_b,r) in structural.items()
         if kind==b'PRODUCT_DEFINITION_SHAPE' and r[-1] in selected_defs|selected_arcs}
    chosen=set(selected_defs)|selected_arcs|pds
    for i,(kind,_b,r) in structural.items():
        if kind==b'SHAPE_DEFINITION_REPRESENTATION' and r[0] in pds:chosen.add(i)
        if kind==b'CONTEXT_DEPENDENT_SHAPE_REPRESENTATION' and r[-1] in pds:chosen.add(i)
    queue=list(chosen)
    while queue:
        entity=queue.pop()
        if entity>=len(starts) or ends[entity]==0:raise RuntimeError(f'Unknown STEP reference #{entity}')
        for dependency in refs(data[starts[entity]:ends[entity]].partition(b'=')[2]):
            if dependency not in chosen:
                chosen.add(dependency);queue.append(dependency)
    found={base(arc['name']) for i,arc in arcs.items() if i in selected_arcs
           and base(arc['name']) in wanted}
    if found!=wanted:raise RuntimeError(f'Named products absent: {sorted(wanted-found)}')
    args.out.write_bytes(data[:first]+b'\n'.join(data[starts[i]:ends[i]] for i in sorted(chosen))
                         +b'\nENDSEC;\nEND-ISO-10303-21;\n')
    if sha(args.source)!=source_sha:raise RuntimeError('Aggregate changed during extraction')
    result=dict(scope='Manual AP214 record-closure extraction. Selected native geometry and '
        'ancestor assembly placements retain their original STEP records and IDs; unselected '
        'products and presentation styles are omitted. Import only the small subset for '
        'native named-body/placement agreement before treating extraction as qualified.',
        source=dict(path=str(args.source.resolve()),sha256=source_sha),
        subset=dict(path=str(args.out.resolve()),sha256=sha(args.out)),
        verification_source_sha256=sha(Path(__file__)),
        cache_index_sha256=sha(args.cache_index),wanted_names=sorted(wanted),
        input_entity_count=count,retained_entity_count=len(chosen),
        chosen_assembly_arc_count=len(selected_arcs))
    args.report.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))


if __name__=='__main__':main()
