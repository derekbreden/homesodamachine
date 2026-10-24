"""Complete access-panel arrangement, preserving the parent equipment layout."""
from pathlib import Path
import importlib.util
import json

import numpy as np

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('fastened_access_parent',HERE.parent/'funnel-gate/study.py')
parent=importlib.util.module_from_spec(spec);spec.loader.exec_module(parent)
base=parent.base


def plan():return json.loads((HERE/'panel-plan.json').read_text())


def library():
    geometry=parent.library()
    for path in (HERE/'parts').glob('*.npz'):
        if path.stem.startswith('section-'):continue
        with np.load(path) as mesh:geometry[path.stem]=mesh['v'],mesh['f']
    return geometry


def assembly(owner,basis):
    return {'quadrant':owner,'status':'modelled','basis':basis}


def pose(geometry):
    scene=parent.pose(geometry);p=plan();f=p['fasteners']
    shift=np.array(p['c14']['translation_from_parent_mm'])
    for part in scene['instances']:
        part['latest_change']=part['name'] in ('ceiling','back-wall','c14-inlet')
        if part['name']=='ceiling':
            part.update(geometry='access-fixed-ceiling',label='Fixed ceiling · four discrete heatset bosses',
                assembly=assembly('back-top','Integral corner bosses support the panel; no perimeter rim'))
        elif part['name']=='back-wall':
            part.update(geometry='access-back-wall',label='Rear wall · C14 pocket and screw holes follow the balanced inlet pose')
        if part['name']=='c14-inlet' or part.get('connection_owner')=='c14-inlet':
            part['translation']=(np.array(part['translation'])+shift).tolist()
            part['latest_change']=True
            if part['name']=='c14-inlet':part['label']='C14 inlet · balanced corner gaps · 2.75 mm inward and 3 mm lower'
    scene['instances'].append(base.instance('electronics-access-panel','electronics-access-panel',
        role='closure',kind='component',latest_change=True,moves_with_panel=True,
        label='Empty access panel · four recessed screws and a 6 × 2 mm pry notch',
        assembly=assembly('electronics-access','Plain last-on closure; no equipment, wire or tube is attached')))
    for index,(x,y) in enumerate(f['centres_xy_mm']):
        screw_name=f'access-screw-{index}';insert_name=f'access-insert-{index}'
        scene['instances'].extend([
            base.instance(screw_name,'panel-screw-m3x12',[x,y,f['counterbore_floor_z_mm']],
                role='hardware-screw',kind='hardware',latest_change=True,moves_with_panel=True,
                label='M3 × 12 socket screw · Ø6.2 mm counterbore · head 0.2 mm below top',
                assembly=assembly('electronics-access','Unscrew before lifting the empty panel')),
            base.instance(insert_name,'panel-insert-rx-m3x5p7',[x,y,f['bearing_z_mm']],
                role='hardware-insert',kind='hardware',latest_change=True,
                label='RX-M3×5.7 heatset · full nominal engagement · blind Ø4 × 7.5 mm pilot',
                assembly=assembly('back-top','Heatset remains in the fixed corner boss')),
            base.instance(f'access-boss-highlight-{index}','panel-boss',[x,y,0],
                role='support',kind='display',render_only=True,latest_change=True,
                label='Integral 18 × 12 mm boss · 3 mm stock below the blind pilot',
                assembly=assembly('back-top','Display overlay of the integral boss; not a separate printed part'))])
        scene['mates'].extend([
            {'a':screw_name,'b':insert_name,'connection':'M3 thread engagement'},
            {'a':screw_name,'b':'electronics-access-panel','connection':'Counterbore bearing face'},
            {'a':insert_name,'b':'ceiling','connection':'Heatset press envelope in its integral boss'}])
    scene['mates'].append({'a':'electronics-access-panel','b':'ceiling','connection':'Four discrete boss top bearings at Z346'})
    scene.update(id='electronics-access',title='Empty access panel on four heatset bosses')
    return scene
