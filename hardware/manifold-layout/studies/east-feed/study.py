"""Under-head V-A feed, centered PCB and native push-connect water regulators.

Isolated arrangement using frozen references. Local electrical connections
participate in the manual fit query; harness drawings are omitted.
"""
from pathlib import Path
import argparse
import copy
import importlib.util
import json
import numpy as np

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]

def module(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

parent=module('east_feed_parent',HERE.parent/'wall-supported/study.py')
base=parent.base
grid_model=module('east_feed_mesh',HERE.parent/'co2-grid/study.py')
yzmsz=module('east_feed_yzmsz',ROOT/'hardware/reference/yzmsz-water-regulator/model.py')
frizzlife=module('east_feed_frizzlife',ROOT/'hardware/reference/frizzlife-prv01/model.py')
I=np.eye(3)
PCB_R=np.array([[0,1,0],[0,0,-1],[-1,0,0]])
PCB_T=[-323.9839324951172,521.5948832211246,353.25]
DEST=np.array([22.35,166.24,270.675])
REG_OUT=np.array([-57.35410112876839,296.3397605281867,334.3760478805363])
TEE_MOUTH=np.array([17.145898871231594,296.3397605281867,334.3760478805363])
REG_R=np.diag([-1.,1.,-1.])
REGULATORS={
    'yzmsz':{'geometry':'yzmsz-water-regulator','length':67.,'insertion':15.,
        'label':'YZMSZ · fixed 0.3 MPa / 43.5 psi · native push-connects · estimated 67 × Ø27 mm'},
    'frizzlife':{'geometry':'frizzlife-prv01','length':66.802,'insertion':15.7,
        'label':'Frizzlife PRV01 · 50–60 psi · native push-connects · published 66.8 × Ø26.7 mm'}}

def bezier(control):
    p=np.array(control,float);t=np.linspace(0.,1.,65)[:,None]
    points=(1-t)**3*p[0]+3*(1-t)**2*t*p[1]+3*(1-t)*t*t*p[2]+t**3*p[3]
    d=3*((1-t)**2*(p[1]-p[0])+2*(1-t)*t*(p[2]-p[1])+t*t*(p[3]-p[2]))
    dd=6*((1-t)*(p[2]-2*p[1]+p[0])+t*(p[3]-2*p[2]+p[1]))
    curvature=np.linalg.norm(np.cross(d,dd),axis=1)/np.linalg.norm(d,axis=1)**3
    return points,float(1/curvature.max())

def route():
    source_corner=np.array([-76.40410112876839,296.3397605281867,262.7856478805363])
    mouth=source_corner+[19.05,0.,0.]
    ya_corner=DEST+[0.,0.,6.0452]
    # Flat on the core beneath the head, as demonstrated on the received pump.
    # The small aft offset puts the collet behind the rigid lower switch block.
    corner=np.array([33.1317,309.1355,261.6])
    west=np.array([-1.,0.,0.]);onward=np.array([0.,-1.,0.])
    pickup=corner+20.56239*west;departure=corner+20.56239*onward
    ya_socket=ya_corner-19.05*onward
    turn_r=np.column_stack([np.cross(west,onward),west,onward])
    ya_r=np.column_stack([[0.,0.,1.],-onward,np.cross([0.,0.,1.],-onward)])
    under_controls=[mouth,mouth+[23.,0.,0.],pickup+23*west,pickup]
    onward_handle=(departure[1]-ya_socket[1])/3
    onward_controls=[departure,departure+onward_handle*onward,
                     ya_socket-onward_handle*onward,ya_socket]
    under_curve,under_radius=bezier(under_controls)
    onward_curve,onward_radius=bezier(onward_controls)
    under=np.vstack([mouth-[16.891,0.,0.],under_curve,pickup-15.7*west])
    direct=np.vstack([departure-15.7*onward,onward_curve,ya_socket+16.891*onward])
    tube_low=float(grid_model.tube(under,3.175,2.12)[0][:,2].min())
    return {'source_elbow_corner_mm':source_corner.tolist(),'elbow_socket_mm':mouth.tolist(),
        'under_head_bezier_control_points_mm':np.array(under_controls).tolist(),
        'onward_bezier_control_points_mm':np.array(onward_controls).tolist(),
        'minimum_centerline_radius_mm':min(under_radius,onward_radius),
        'under_head_minimum_radius_mm':under_radius,'onward_minimum_radius_mm':onward_radius,
        'under_head_centerline_mm':under.tolist(),'onward_centerline_mm':direct.tolist(),
        'turn_corner_mm':corner.tolist(),'turn_inlet_mm':pickup.tolist(),'turn_outlet_mm':departure.tolist(),
        'turn_rotation':turn_r.tolist(),'ya_elbow_corner_mm':ya_corner.tolist(),
        'turn_location':'Flat beneath pump head; inlet west (-X), outlet fore (-Y)',
        'turn_inlet_clock_degrees':0.,
        'ya_socket_mm':ya_socket.tolist(),'ya_elbow_rotation':ya_r.tolist(),
        'onward_exposed_length_mm':float(np.linalg.norm(np.diff(onward_curve,axis=0),axis=1).sum()),
        'onward_rise_mm':float(ya_socket[2]-departure[2]),
        'destination_mm':DEST.tolist(),'destination_outward_axis':[0.,0.,1.],
        'tube_od_mm':6.35,'tube_id_mm':4.24,'tube_lowest_z_mm':tube_low,
        'cold_core_top_z_mm':253.4,'nominal_core_gap_mm':tube_low-253.4,
        'nominal_insertions_mm':{'source_socket':16.891,'JG_turn':15.7,'YA_elbow_socket':16.891,'YA_stem':15.7},
        'insertion_scope':'JG turn insertion is a family-based layout estimate; its scan does not establish an internal stop'}

def library():
    import trimesh
    g=parent.library();g.update(yzmsz.library());g.update(frizzlife.library());d=route()
    g['va-under-head']=grid_model.tube(d['under_head_centerline_mm'],3.175,2.12)
    g['va-to-ya']=grid_model.tube(d['onward_centerline_mm'],3.175,2.12)
    fitting=trimesh.load(ROOT/'hardware/reference/jg-pp0308e-elbow/jg-pp0308e-elbow.stl',process=False)
    g['jg-turn-elbow']=np.asarray(fitting.vertices),np.asarray(fitting.faces,dtype=np.int32)
    # Full 15.7 mm host engagement behind the shoulder, entirely inside Y-A.
    g['ya-stem-elbow']=g['gas-stem-elbow']
    v,f=g['forward-tee-y-b'];g['tee-ya-target']=v*np.array([-1.,1.,1.]),f[:,::-1].copy()
    for key,row in REGULATORS.items():
        inlet=REG_OUT+[row['length'],0.,0.]
        g['clean-water-link-'+key]=grid_model.tube([TEE_MOUTH+[16.891,0.,0.],inlet-[row['insertion'],0.,0.]],3.175,2.12)
    with np.load(HERE/'parts/east-feed-ceiling.npz') as data:g['ceiling']=data['v'],data['f']
    with np.load(HERE/'parts/pump-under-head.npz') as data:g['pump-under-head']=data['v'],data['f']
    return g

def pose(g,regulator='yzmsz'):
    scene=parent.pose(g);d=route();selected=REGULATORS[regulator]
    pump_frame=json.loads((HERE/'parts/pump-under-head-source.json').read_text())['native_to_world']
    for m in scene['instances']:
        if m['name']=='pump':m.update(geometry='pump-under-head',rotation=pump_frame['rotation'],translation=pump_frame['translation_mm'])
        if m['name']=='va-outlet-elbow':m.update(rotation=PCB_R.tolist(),label='V-A outlet · stem elbow points east (+X)')
        if m['name']=='va-flavor':m.update(geometry='va-under-head',rotation=I.tolist(),translation=[0.,0.,0.],label='V-A water tube · under pump head · into elbow between pump and V-K')
        if m['name']=='pcba' or m.get('connection_owner')=='pcba':
            m.update(rotation=PCB_R.tolist(),translation=PCB_T)
            if m['name']=='pcba':m['label']='Main PCB · centered between V-A support and core front · long dimension across X'
        if m['name']=='reg':m.update(geometry=selected['geometry'],rotation=REG_R.tolist(),translation=(REG_OUT+[selected['length'],0.,0.]).tolist(),role='wet',label=selected['label'])
        if m['name']=='tee-regulator-tube':m.update(geometry='clean-water-link-'+regulator,rotation=I.tolist(),translation=[0.,0.,0.],label=f"Straight clean-water feed · {74.5-selected['length']:.1f} mm exposed · direct push-connects")
        if m['name']=='ceiling':m['label']='Study ceiling · 9 mm ordinary stock · 6 mm over inline water regulator'
        if m['role']=='wire':m['display_suppressed']=True
    scene['instances'].extend([
        base.instance('va-east-turn','jg-turn-elbow',d['turn_corner_mm'],d['turn_rotation'],role='wet',kind='elbow',label='Purchased scanned JG PP0308E · flat beneath pump head · west inlet and fore outlet'),
        base.instance('va-ya-straight','va-to-ya',role='flavor',kind='tube',label='Direct 1/4-inch tube to Y-A · gentle rise · square socket entries'),
        base.instance('ya-stem-elbow','ya-stem-elbow',d['ya_elbow_corner_mm'],d['ya_elbow_rotation'],role='stem',kind='elbow',label='Y-A · trimmed NeoFit stem elbow · socket faces aft (+Y)'),
        base.instance('tee-ya-target','tee-ya-target',kind='component',role='wet',context=True,label='Y-A · shared-source tee for flavor manifold · upper port1')])
    for mate in scene['mates']:
        if {mate['a'],mate['b']}=={'va-outlet-elbow','va-flavor'}:mate['point']=d['elbow_socket_mm']
        if {mate['a'],mate['b']}=={'tee-regulator-tube','reg'}:mate['point']=(REG_OUT+[selected['length'],0.,0.]).tolist()
    scene['mates'].extend([{'a':a,'b':b,'connection':label} for a,b,label in (
        ('va-flavor','va-east-turn','Tube inside JG socket; nominal15.7mm insertion'),
        ('va-east-turn','va-ya-straight','Tube inside JG socket; nominal15.7mm insertion'),
        ('va-ya-straight','ya-stem-elbow','Tube inside NeoFit socket; nominal16.891mm insertion'),
        ('ya-stem-elbow','tee-ya-target','Stem trimmed to15.7mm host depth; shoulder flush'))])
    scene.update(id='east-feed',title='Under-head V-A feed and centered PCB',regulator=regulator)
    scene['layout'].update(pcb_orientation='Flat, components up; long dimension across X and J10 entry facing east',
        pcb_footprint_mm={'xmin':-88.,'xmax':2.8160552978515625,'ymin':195.39487101389335,'ymax':268.1948893244402},
        pcb_centering={'core_front_y_mm':182.2999998,'va_support_front_y_mm':281.2897605281867,'equal_end_gap_mm':13.0948712138933,'west_edge_to_ideal_wall_mm':10.5,'west_J11_housing_to_wall_mm':18.96593322753906},
        pcb_lead_dressing='Local connector and wire envelopes checked quietly; harness drawings omitted',
        flavor_mouth_world_mm=d['elbow_socket_mm'],flavor_handoff_direction_world=[1.,0.,0.],
        va_destination='Y-A port1, the flavor manifold shared-source tee; clean-water supply',va_route=d,
        route_context='V-B and reservoir routes deferred; Y-A retains its actual destination datum',
        regulator_selection=selected['label'],regulator_exposed_inlet_tube_mm=74.5-selected['length'],
        regulator_outlet_world_mm=REG_OUT.tolist(),regulator_inlet_world_mm=(REG_OUT+[selected['length'],0.,0.]).tolist())
    return scene

def comparison(g):
    old=copy.deepcopy(next(m for m in parent.pose(g)['instances'] if m['name']=='reg'))
    inlet=np.array([2.1458988712315943,296.3397605281867,334.3760478805363]);q=REG_R
    old.update(name='comparison-yetaha',translation=(q@np.array(old['translation'])-q@inlet+[0.,90.,0.]).tolist(),rotation=(q@np.array(old['rotation'])).tolist(),role='current-regulator',label='Yetaha reference · 59.5mm mouths · 63mm fork span · 53mm height')
    return {'id':'regulator-comparison','instances':[old,
        base.instance('comparison-frizzlife','frizzlife-prv01',[0.,35.,0.],role='wet',label=REGULATORS['frizzlife']['label']),
        base.instance('comparison-yzmsz','yzmsz-water-regulator',[0.,-12.,0.],role='wet',label=REGULATORS['yzmsz']['label'])],
        'scope':'Free-space comparison; both ordered inline choices have native push-connects'}

def check(scene,g):
    result=parent.check(scene,g);meshes=base.world_meshes(scene,g)
    moving=['pcba',*[m['name'] for m in scene['instances'] if m.get('connection_owner')=='pcba']]
    v=np.vstack([meshes[n][0] for n in moving]);result['connected_pcb_bounds_mm']=[v.min(0).tolist(),v.max(0).tolist()]
    result['connected_pcb_to_ideal_west_wall_mm']=float(v[:,0].min()+98.5)
    import fcl
    def obj(mesh):
        v,f=mesh;b=fcl.BVHModel();b.beginModel(len(v),len(f));b.addSubModel(v,f.astype(np.int32));b.endModel();return fcl.CollisionObject(b)
    objects={n:obj(meshes[n]) for n in ('va-flavor','va-ya-straight','va-east-turn','lower-pump-elbow','pump','vk','pcba','funnel-frame','reg','ceiling')}
    result['tube_gaps_mm']={a+'_to_'+b:float(fcl.distance(objects[a],objects[b],fcl.DistanceRequest(),fcl.DistanceResult())) for a,b in (
        ('va-flavor','pump'),('va-flavor','pcba'),('va-east-turn','pump'),('va-east-turn','vk'),('va-east-turn','lower-pump-elbow'),('va-ya-straight','pcba'),('va-ya-straight','funnel-frame'),('reg','ceiling'))}
    result['under_head_tube_to_plain_core_mm']=float(meshes['va-flavor'][0][:,2].min()-253.4)
    result['scope']='Flat under-head elbow, direct Y-A tube, centered PCB/local connections and native push-connect regulator against the selected arrangement'
    return result

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--check',action='store_true');args=parser.parse_args()
    g=library();scene=pose(g);alternative=pose(g,'frizzlife')
    if args.check:scene['metrics']=check(scene,g);alternative['metrics']=check(alternative,g)
    (HERE/'study.json').write_text(json.dumps(scene,indent=2)+'\n')
    (HERE/'alternative.json').write_text(json.dumps(alternative,indent=2)+'\n')
    (HERE/'route.json').write_text(json.dumps(route(),indent=2)+'\n')
    datums=parent.connections.world_datums(scene['instances'])
    datums['service']={'scope':'Local envelopes only; harness drawings omitted','J10':'Wire entry east; long vertical driver service requires funnel/frame removal'}
    (HERE/'connection-datums.json').write_text(json.dumps(datums,indent=2)+'\n')
    comp=comparison(g);visible=copy.deepcopy(scene);visible['instances']=[m for m in visible['instances'] if not m.get('display_suppressed') and not m.get('render_only')]
    for key in ('layout','metrics','mates'):visible.pop(key,None)
    overrides={key:[m for m in pose(g,key)['instances'] if m['name'] in ('reg','tee-regulator-tube')] for key in REGULATORS}
    used={m['geometry'] for s in (visible,comp) for m in s['instances']}|{m['geometry'] for ms in overrides.values() for m in ms}
    packed={n:base.pack(*g[n],10000 if n in ('va-under-head','va-to-ya') else 12000 if n.startswith('connection-') else 5200 if n in ('pump','pump-under-head') else 3000) for n in sorted(used)}
    out=HERE/'out';out.mkdir(exist_ok=True)
    (out/'viewer-data.json').write_text(json.dumps({'geometries':packed,'variants':[visible],'comparison':comp,'regulator_overrides':overrides,'grid':parent.parent.grid()},separators=(',',':')))
    print(json.dumps({'selected':scene.get('metrics',{}),'frizzlife':alternative.get('metrics',{})},indent=2))

if __name__=='__main__':main()
