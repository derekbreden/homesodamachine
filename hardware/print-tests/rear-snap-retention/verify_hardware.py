"""Measure each sample's rigid hardware clearance and the neighboring rear caps."""
from pathlib import Path
import json
import sys

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
sys.path[:0]=[str(ROOT/'hardware/scripts'),str(ROOT/'hardware/printed-parts/cadlib'),
             str(ROOT/'hardware/printed-parts/cold-core'),str(ROOT/'hardware/manifold-layout')]
import cadquery as cq
import above_core_parts as refs
import above_core
import _above_core_mounts as mounts
import rear_plumbing


def main():
    objects=refs.components()
    shapes=rear_plumbing.seats()
    names={'asse':('bulkhead-water','gagira-coupling','asse1022-assembly','jg-pi4512f6s','jg-pp061208w','asse-drain-adapter'),
      'pisco':('co2-inlet','gas-regulator','gas-check'),
      'regulator':('flow-regulator',),'meter':('digiten-flow',),'pump':('g-ganen-pump',)}
    report={'rigid_object_intersections_mm3':{},'cap_neighbors_mm3':{},'scope':'Static native fit checks, not physical qualification.'}
    for family,items in names.items():
        seat=mounts.pump_cradle() if family=='pump' else shapes[family+'-seat']
        cap=mounts.pump_snap_cap() if family=='pump' else shapes[family+'-snap-cap']
        rows={}
        for name in items:
            obj=objects[name][0]
            rows[name]={'seat':seat.intersect(obj).Volume(),'cap':cap.intersect(obj).Volume()}
        report['rigid_object_intersections_mm3'][family]=rows
    caps={name:shapes[name+'-snap-cap'] for name in ('asse','pisco','regulator','meter')}
    for i,(name,a) in enumerate(caps.items()):
        for other,b in list(caps.items())[i+1:]:
            report['cap_neighbors_mm3'][name+'/'+other]=a.intersect(b).Volume()
    (HERE/'hardware-check.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2),flush=True)


if __name__=='__main__':main()
