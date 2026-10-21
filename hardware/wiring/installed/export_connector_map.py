"""Snapshot the fabricated board's connector pins for the installed CAD model.

Run explicitly after exporting the PCB. The full circuit JSON is a local PCB
intermediate; the small tracked map is the reproducible CAD input.
"""
import hashlib
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'hardware/manifold-layout'),str(ROOT/'hardware/scripts')]


def main():
    import enclosure_assembly as ea
    source=ROOT/'hardware/pcb/pcba/out/pcba.circuit.json'
    data=json.loads(source.read_text())
    components={r['source_component_id']:r for r in data if r.get('type')=='source_component'}
    ports={r['source_port_id']:r for r in data if r.get('type')=='source_port'}
    cad=[r for r in data if r.get('type')=='cad_component' and r.get('model_step_url')]
    boxes=ea._pcba._glb_component_boxes()
    result={}
    for row in data:
        if row.get('type')!='pcb_port':continue
        pin=ports.get(row.get('source_port_id'))
        if not pin:continue
        component=components[pin['source_component_id']];name=component['name']
        if name not in {'J1','J2','J3','J4','J5','J6','J7','J8','J9','J10','J11','J13'}:continue
        entry=result.setdefault(name,{'part':component.get('manufacturer_part_number'),'pins':[]})
        entry['pins'].append({'number':pin['pin_number'],'label':pin['name'],'xy_mm':[row['x'],row['y']]})
        if name=='J10':
            index=next(i for i,r in enumerate(cad) if r.get('source_component_id')==pin['source_component_id'])
            entry['component_glb_bounds_mm']=boxes[index]
    for entry in result.values():entry['pins'].sort(key=lambda r:r['number'])
    paths=[source,ROOT/'hardware/pcb/pcba/out/pcba.glb',ROOT/'hardware/pcb/pcba/pcba.tsx',ROOT/'hardware/pcb/pcba/parts.tsx']
    output={'schema':1,'units':'mm','scope':'Physical pad positions and logical pin identities from the fabricated board export; no PCB routing run is required by enclosure CAD.',
            'source_sha256':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths},
            'connectors':dict(sorted(result.items()))}
    target=Path(__file__).with_name('connector-map.json');target.write_text(json.dumps(output,indent=2)+'\n')
    print(len(result),'connectors,',sum(len(v['pins']) for v in result.values()),'physical pins')


if __name__=='__main__':main()
