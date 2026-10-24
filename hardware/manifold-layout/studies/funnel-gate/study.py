"""Funnel V-B beside the PCB with a compact, low return to Y-B.

Isolated layout study; approved parent arrangements and production geometry are
unchanged. Run --check manually to query this candidate's exterior fit.
"""
from pathlib import Path
import argparse
import copy
import importlib.util
import json
import numpy as np
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
spec=importlib.util.spec_from_file_location('funnel_gate_parent',HERE.parent/'east-feed/study.py')
parent=importlib.util.module_from_spec(spec);spec.loader.exec_module(parent)
base=parent.base
I=np.eye(3);E=np.array([1.,0.,0.]);N=np.array([0.,1.,0.]);U=np.array([0.,0.,1.])
L=20.56239;S=19.05;H=6.0452;JG_DEPTH=15.7;NEOFIT_DEPTH=16.891
PCB_SHIFT=np.array([62.5,0.,0.])
STOCK_STEM_EXPOSED=5.3058
VB_ORIGIN=np.array([-37.7,238.61573+STOCK_STEM_EXPOSED,280.41])
VB_NATIVE_R=np.array([[0.,0.,-1.],[0.,1.,0.],[1.,0.,0.]])
VK_SOURCE_R=np.array([[1.,0.,0.],[0.,0.,-1.],[0.,1.,0.]])
VK_SOURCE_T=np.array([-4.916132605004726,11.05,48.25])
DRAIN_CORNER=np.array([0.,161.69575,280.41])
YB_MOUTH=np.array([-22.35,166.24,270.675])
YA_MOUTH=parent.DEST.copy()
RETURN_CLOCK_DEGREES=45.

def union(a,b):return np.column_stack([np.cross(a,b),a,b])
def stem_rotation(host,out):return np.column_stack([host,out,np.cross(host,out)])
def tube(points):return parent.grid_model.tube(points,3.175,2.12)
def inserted(a,axis_a,b,axis_b,depth_a=JG_DEPTH,depth_b=JG_DEPTH):
    return np.array([np.array(a)-depth_a*np.array(axis_a),a,b,np.array(b)-depth_b*np.array(axis_b)])
def gentle(a,axis_a,b,axis_b,depth_a=JG_DEPTH,depth_b=JG_DEPTH):
    a,b=np.array(a),np.array(b);length=np.linalg.norm((b-a)[:2])/3
    control=[a,a+length*np.array(axis_a),b+length*np.array(axis_b),b]
    curve,radius=parent.bezier(control)
    return np.vstack([a-depth_a*np.array(axis_a),curve,b-depth_b*np.array(axis_b)]),control,radius

def low_return(mouth,target):
    """Drop in the clear corridor, pass below V-B, then rise into Y-B.

    The three tangent-continuous spans retain square socket entries. Only the
    two outlet elbows' fold plane is clocked; the valve stays axis-aligned.
    """
    drop=np.array([mouth[0],245.,259.2]);turn=np.array([-65.,200.,259.2])
    controls=[
        [mouth,mouth-6.5*N,drop+6.5*N,drop],
        [drop,drop-20*N,turn+20*N,turn],
        [turn,turn-16*N,target-20*E,target]]
    spans=[parent.bezier(control) for control in controls]
    points=np.vstack([mouth+NEOFIT_DEPTH*N,*[curve[:-1] for curve,_ in spans],
                      target,target+NEOFIT_DEPTH*E])
    return points,controls,min(radius for _,radius in spans)

def route():
    photo=parent.route();fixed=np.array(photo['turn_outlet_mm'])
    va1=fixed-(H+STOCK_STEM_EXPOSED)*N;va1mouth=va1+S*E
    va2=np.array([83.,va1[1],va1[2]]);va2in=va2-L*E;va2out=va2-L*N
    va3=np.array([83.,YA_MOUTH[1],YA_MOUTH[2]+H]);va3in=va3+L*N;va3out=va3-L*E
    ya=YA_MOUTH+H*U;yasocket=ya+S*E
    vb_i=VB_NATIVE_R@np.array([0.,-29.75,11.05])+VB_ORIGIN
    vb_o=VB_NATIVE_R@np.array([0.,29.75,11.05])+VB_ORIGIN
    d1=DRAIN_CORNER+(L+H+STOCK_STEM_EXPOSED)*N;d1mouth=d1-S*E
    d2=np.array([vb_i[0],d1[1],d1[2]]);d2in=d2+L*E;d2out=d2+L*N
    angle=np.radians(RETURN_CLOCK_DEGREES);fold=np.cos(angle)*E-np.sin(angle)*U
    vb1=vb_o+H*N;vb2=vb1+(S+H)*fold;vb2mouth=vb2-S*N
    yb=YB_MOUTH+H*U;ybmouth=yb-S*E
    va_fore,va_control,va_radius=gentle(va2out,-N,va3in,N)
    vb_fore,vb_control,vb_radius=low_return(vb2mouth,ybmouth)
    tubes={
        'va-east-jumper':inserted(va1mouth,E,va2in,-E,NEOFIT_DEPTH,JG_DEPTH),
        'va-east-fore-run':va_fore,
        'va-ya-west-link':inserted(va3out,-E,yasocket,E,JG_DEPTH,NEOFIT_DEPTH),
        'drain-vb-west-link':inserted(d1mouth,-E,d2in,E,NEOFIT_DEPTH,JG_DEPTH),
        'drain-vb-inlet-link':inserted(d2out,N,vb_i,-N,JG_DEPTH,12.7),
        'vb-south-return':vb_fore}
    joints={
        'va-after-head-stem':{'geometry':'stem-elbow','corner':va1,'rotation':stem_rotation(-N,E)},
        'va-east-perimeter-turn':{'geometry':'jg-turn-elbow','corner':va2,'rotation':union(-E,-N)},
        'va-front-perimeter-turn':{'geometry':'jg-turn-elbow','corner':va3,'rotation':union(N,-E)},
        'ya-stem-elbow':{'geometry':'ya-stem-elbow','corner':ya,'rotation':stem_rotation(U,E)},
        'drain-outlet-stem':{'geometry':'stem-elbow','corner':d1,'rotation':stem_rotation(N,-E)},
        'vb-inlet-turn':{'geometry':'jg-turn-elbow','corner':d2,'rotation':union(E,N)},
        'vb-outlet-stem':{'geometry':'stem-elbow-trimmed','corner':vb1,'rotation':stem_rotation(N,fold)},
        'vb-return-stem':{'geometry':'elbow-elbow','corner':vb2,'rotation':stem_rotation(fold,-N)},
        'yb-stem-elbow':{'geometry':'gas-stem-elbow','corner':yb,'rotation':stem_rotation(U,-E)}}
    return {'tubes':{k:v.tolist() for k,v in tubes.items()},'joints':{k:{'geometry':v['geometry'],'corner':v['corner'].tolist(),'rotation':v['rotation'].tolist()} for k,v in joints.items()},
        'vb_native_origin_mm':VB_ORIGIN.tolist(),'vb_native_rotation':VB_NATIVE_R.tolist(),
        'vb_inlet_mm':vb_i.tolist(),'vb_outlet_mm':vb_o.tolist(),
        'drain_union_corner_mm':DRAIN_CORNER.tolist(),'ya_mouth_mm':YA_MOUTH.tolist(),'yb_mouth_mm':YB_MOUTH.tolist(),
        'va_fore_control_mm':np.array(va_control).tolist(),'va_fore_minimum_radius_mm':va_radius,
        'vb_return_control_mm':np.array(vb_control).tolist(),'vb_return_minimum_radius_mm':vb_radius,
        'pcb_translation_from_parent_mm':PCB_SHIFT.tolist(),
        'return_fold_direction':'east and down; final outlet fore',
        'return_fold_clock_degrees':RETURN_CLOCK_DEGREES,
        'hardware_scope':'Main bodies remain square to X/Y/Z; two trimmed outlet stems are clocked together 45 degrees to pass the return below V-B; Y-B socket points west',
        'insertions_mm':{'JG_socket':JG_DEPTH,'NeoFit_socket':NEOFIT_DEPTH,'Beduan_socket':12.7,'YA_YB_tee':15.7},
        'stock_stem_exposure_mm':STOCK_STEM_EXPOSED,
        'insertion_scope':'Family-based layout assumptions; two stock stems retain5.3058mm exposure to clear adjacent hardware and the existing drain cradle; other stems seat shoulder-flush'}

def library():
    g=parent.library();d=route()
    for name,points in d['tubes'].items():g[name]=tube(points)
    return g

def pose(g):
    scene=parent.pose(g);d=route();rows={m['name']:m for m in scene['instances']}
    for m in scene['instances']:
        if m['name']=='pcba' or m.get('connection_owner')=='pcba':
            m['translation']=(np.array(m['translation'])+PCB_SHIFT).tolist()
        if m['name'] in ('local-lead-J3','local-lead-J4','local-lead-J11'):
            m['geometry']='connection-'+m['name'].removeprefix('local-lead-')+'-wire-inward'
            m['label']=m['name']+' · same-radius local lead dressed inward over PCB'
        if m['name']=='va-ya-straight':m.update(geometry='va-east-fore-run',label='V-A water feed · fore along east perimeter · gentle rise')
        if m['name']=='ya-stem-elbow':
            joint=d['joints']['ya-stem-elbow'];m.update(translation=joint['corner'],rotation=joint['rotation'],label='Y-A · stem elbow socket points east')
    vb_r=VB_NATIVE_R@VK_SOURCE_R.T;vb_t=VB_ORIGIN-vb_r@VK_SOURCE_T
    scene['instances'].extend([
        base.instance('vb','vk',vb_t,vb_r,role='wet',kind='component',label='V-B funnel gate · on its side west of PCB · head west · flow aft'),
        base.instance('tee-yb-target','forward-tee-y-b',role='wet',kind='component',context=True,label='Y-B · funnel-source tee · fixed production position'),
        base.instance('funnel-drain-union','jg-turn-elbow',DRAIN_CORNER,I,role='wet',kind='elbow',label='Funnel drain · scanned JG union elbow · aft outlet'),
        base.instance('funnel-drain-stub','forward-funnel-drain-stub',role='wet',kind='tube',context=True,label='Funnel drain stub · existing production position'),
        base.instance('funnel-drain-cradle','forward-elbow-cradle',role='support',kind='component',context=True,label='Funnel drain elbow cradle · existing production position')])
    for name,j in d['joints'].items():
        if name=='ya-stem-elbow':continue
        scene['instances'].append(base.instance(name,j['geometry'],j['corner'],j['rotation'],role='stem' if j['geometry']!='jg-turn-elbow' else 'wet',kind='elbow',label=name.replace('-',' ')))
    for name in d['tubes']:
        if name=='va-east-fore-run':continue
        scene['instances'].append(base.instance(name,name,role='flavor',kind='tube',label=name.replace('-',' ')))
    superseded={frozenset(('va-east-turn','va-ya-straight')),frozenset(('va-ya-straight','ya-stem-elbow'))}
    scene['mates']=[m for m in scene['mates'] if frozenset((m['a'],m['b'])) not in superseded]
    pairs=[('va-east-turn','va-after-head-stem'),('va-after-head-stem','va-east-jumper'),('va-east-jumper','va-east-perimeter-turn'),('va-east-perimeter-turn','va-ya-straight'),('va-ya-straight','va-front-perimeter-turn'),('va-front-perimeter-turn','va-ya-west-link'),('va-ya-west-link','ya-stem-elbow'),
        ('funnel-drain-union','funnel-drain-stub'),('funnel-drain-union','funnel-drain-cradle'),('funnel-drain-cradle','funnel-drain-stub'),('funnel-drain-stub','funnel'),
        ('funnel-drain-union','drain-outlet-stem'),('drain-outlet-stem','drain-vb-west-link'),('drain-vb-west-link','vb-inlet-turn'),('vb-inlet-turn','drain-vb-inlet-link'),('drain-vb-inlet-link','vb'),
        ('vb','vb-outlet-stem'),('vb-outlet-stem','vb-return-stem'),('vb-return-stem','vb-south-return'),('vb-south-return','yb-stem-elbow'),('yb-stem-elbow','tee-yb-target')]
    scene['mates'].extend({'a':a,'b':b,'connection':'Intended seated fitting, tube insertion or existing drain support'} for a,b in pairs)
    scene.update(id='funnel-gate',title='Funnel gate beside the PCB')
    scene['layout'].update(funnel_gate=d,pcb_footprint_mm={k:v+(PCB_SHIFT[0] if k[0]=='x' else PCB_SHIFT[1]) for k,v in scene['layout']['pcb_footprint_mm'].items()},
        route_context='Y-A and Y-B retain production port datums; funnel drain, stub and cradle are production context; V-B is the new side-mounted valve',
        pending_structure='V-B and its drain/Y-B route belong to the funnel-frame assembly; frame bracket and shifted PCB retention are to design',
        pcb_local_lead_dressing='J3, J4 and J11 use the existing inward local lead estimates; plug housings,3mm exit and4mm bend radius remain fixed')
    return scene

def check(scene,g):
    result=parent.check(scene,g);meshes=base.world_meshes(scene,g)
    import fcl
    def obj(mesh):
        v,f=mesh;m=fcl.BVHModel();m.beginModel(len(v),len(f));m.addSubModel(v,f.astype(np.int32));m.endModel();return fcl.CollisionObject(m)
    names=['vb','pcba','funnel-frame','funnel','left-wall','right-wall','drain-outlet-stem','vb-inlet-turn','vb-south-return','va-east-perimeter-turn','vk','lower-valve-elbow','funnel-drain-cradle']
    objects={n:obj(meshes[n]) for n in names if n in meshes}
    pairs=[('vb','pcba'),('vb','funnel-frame'),('vb','left-wall'),('vb-inlet-turn','pcba'),('vb-south-return','vb'),('vb-south-return','pcba'),('va-east-perimeter-turn','vk'),('va-east-perimeter-turn','lower-valve-elbow'),('funnel-drain-cradle','pcba')]
    result['funnel_gate_gaps_mm']={a+'_to_'+b:float(fcl.distance(objects[a],objects[b],fcl.DistanceRequest(),fcl.DistanceResult())) for a,b in pairs}
    result['vb_bounds_mm']=[meshes['vb'][0].min(0).tolist(),meshes['vb'][0].max(0).tolist()]
    result['funnel_route_minimum_radii_mm']={'va':route()['va_fore_minimum_radius_mm'],'vb':route()['vb_return_minimum_radius_mm']}
    result['scope']='Manual exterior fit query: entire selected arrangement, current local PCB connections, added funnel gate and actual drain/Y-B context; intended seats excluded'
    return result

def service_check(scene,g):
    """Ask about the existing nominal 6 mm JST removal sweeps, not finger reach."""
    import fcl
    connections=parent.parent.connections
    probes=[m for m in connections.instances(scene['instances'],probes=True,owners={'pcba'})
            if m.get('kind')=='probe' and m['name'].endswith('-pull')]
    physical={m['name']:m for m in scene['instances'] if not m.get('render_only')
              and m.get('role')!='wire' and m['name']!='pcba' and m.get('connection_owner')!='pcba'}
    all_meshes=base.world_meshes({'instances':list(physical.values())+probes},g)
    def obj(mesh):
        v,f=mesh;b=fcl.BVHModel();b.beginModel(len(v),len(f));b.addSubModel(v,f.astype(np.int32));b.endModel()
        return fcl.CollisionObject(b)
    objects={n:obj(mesh) for n,mesh in all_meshes.items()}
    ownership=json.loads((HERE/'assembly-ownership.json').read_text())
    front_top={n for group in ownership['groups'] if group['quadrant']=='front-top' for n in group['names']}
    rows=[]
    for probe in probes:
        name=probe['name'];a=all_meshes[name][0];hits=[]
        for other in physical:
            b=all_meshes[other][0]
            if np.any(np.minimum(a.max(0),b.max(0))-np.maximum(a.min(0),b.min(0))<.001):continue
            if fcl.collide(objects[name],objects[other],fcl.CollisionRequest(),fcl.CollisionResult()):hits.append(other)
        rows.append({'probe':name,'blocked_with_funnel_assembly_installed':hits,
            'blocked_after_front_top_removed':[n for n in hits if n not in front_top]})
    return {'scope':'Nominal 6 mm axial JST housing withdrawal only. Does not model finger reach or complete harness manipulation.',
        'service_order':'Remove the front-top funnel assembly before unplugging the main PCB',
        'headers':rows}

def viewer_data(scene,g):return parent.viewer_data(scene,g)
def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--check',action='store_true');args=parser.parse_args()
    g=library();scene=pose(g)
    if args.check:
        scene['metrics']=check(scene,g)
        scene['metrics']['pcb_jst_service']=service_check(scene,g)
        scene['metrics']['flexible_lead_conflicts']=[pair for pair in scene['metrics']['unrelated_interferences'] if any(n.startswith('local-lead-') for n in pair)]
        scene['metrics']['hard_interferences']=[pair for pair in scene['metrics']['unrelated_interferences'] if not any(n.startswith('local-lead-') for n in pair)]
        (HERE/'fit-report.json').write_text(json.dumps(scene['metrics'],indent=2)+'\n')
    (HERE/'route.json').write_text(json.dumps(route(),indent=2)+'\n');(HERE/'study.json').write_text(json.dumps(scene,indent=2)+'\n')
    out=HERE/'out';out.mkdir(exist_ok=True);(out/'viewer-data.json').write_text(json.dumps(viewer_data(scene,g),separators=(',',':')))
    print(json.dumps(scene.get('metrics',{}),indent=2))
if __name__=='__main__':main()
