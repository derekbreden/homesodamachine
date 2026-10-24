"""West PCB and a visible V-B seat wall on the east cold-core roof.

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
PCB_R=np.array([[0.,0.,1.],[0.,1.,0.],[-1.,0.,0.]])
PCB_T=np.array([-336.3999938964844,-49.597079979949626,353.25])
DRAIN_STEM_EXPOSED=3.3058
MOUNT_PLAN=json.loads((HERE/'mount-plan.json').read_text())
VB_ORIGIN=np.array(MOUNT_PLAN['vb_native_origin_mm'],float)
VB_NATIVE_R=np.array(MOUNT_PLAN['vb_native_rotation'],float)
VK_SOURCE_R=np.array([[1.,0.,0.],[0.,0.,-1.],[0.,1.,0.]])
VK_SOURCE_T=np.array([-4.916132605004726,11.05,48.25])
DRAIN_CORNER=np.array([0.,161.69575,280.41])
YB_MOUTH=np.array([-22.35,166.24,270.675])
YA_MOUTH=parent.DEST.copy()


def union(a,b):return np.column_stack([np.cross(a,b),a,b])
def stem_rotation(host,out):return np.column_stack([host,out,np.cross(host,out)])
def tube(points):return parent.grid_model.tube(points,3.175,2.12)
def inserted(a,axis_a,b,axis_b,depth_a=JG_DEPTH,depth_b=JG_DEPTH):
    return np.array([np.array(a)-depth_a*np.array(axis_a),a,b,np.array(b)-depth_b*np.array(axis_b)])
def route():
    angle=np.radians(7.5)
    yaout=np.sin(angle)*E-np.cos(angle)*N
    ybout=-np.sin(angle)*E-np.cos(angle)*N
    ya=YA_MOUTH+H*U;yb=YB_MOUTH+H*U
    yasocket=ya+S*yaout;ybsocket=yb+S*ybout
    # A concealed tube joins Y-A's stem elbow to a union; the next stem
    # returns aft under the drain cradle without crossing the PCB.
    inner=ya+(S+L)*yaout
    fold=np.cos(np.radians(30))*(-np.cos(angle)*E-np.sin(angle)*N)-.5*U
    outer=inner+(L+H)*fold;va_socket=outer-S*yaout
    start=np.array(parent.route()['turn_outlet_mm'])
    va_control=[start,start-40*N,va_socket-40*yaout,va_socket]
    va_curve,va_radius=parent.bezier(va_control)
    va_points=np.vstack([start+JG_DEPTH*N,va_curve,va_socket+NEOFIT_DEPTH*yaout])
    vb_i=VB_NATIVE_R@np.array([0.,-29.75,11.05])+VB_ORIGIN
    vb_o=VB_NATIVE_R@np.array([0.,29.75,11.05])+VB_ORIGIN
    drain=DRAIN_CORNER+(L+H+DRAIN_STEM_EXPOSED)*N
    inlet=np.array([vb_i[0],drain[1],drain[2]])
    # Nested stem elbows reverse the outlet along the west side of V-B's
    # seat wall. Only their fold plane is clocked; the valve stays square.
    vb_fold=-np.cos(np.radians(20))*E+np.sin(np.radians(20))*U
    outlet=vb_o+H*N;return_corner=outlet+(S+H)*vb_fold
    return_socket=return_corner-S*N
    return_u=np.array([return_socket[0],149.,return_socket[2]])
    vb_control=[return_u,return_u-40*N,ybsocket+40*ybout,ybsocket]
    vb_curve,vb_radius=parent.bezier(vb_control)
    vb_points=np.vstack([return_socket+NEOFIT_DEPTH*N,return_socket,
                         return_u,vb_curve[1:],ybsocket-NEOFIT_DEPTH*ybout])
    tubes={
        'va-fore-feed':va_points,
        'ya-concealed-link':inserted(yasocket,yaout,inner-L*yaout,-yaout,NEOFIT_DEPTH,JG_DEPTH),
        'drain-vb-east-link':inserted(drain+S*E,E,inlet-L*E,-E,NEOFIT_DEPTH,JG_DEPTH),
        'drain-vb-inlet-link':inserted(inlet+L*N,N,vb_i,-N,JG_DEPTH,12.7),
        'vb-yb-link':vb_points}
    joints={
        'ya-stem-elbow':{'geometry':'gas-stem-elbow','corner':ya,'rotation':stem_rotation(U,yaout)},
        'ya-fold-inner':{'geometry':'jg-turn-elbow','corner':inner,'rotation':union(-yaout,fold)},
        'ya-fold-return':{'geometry':'gas-stem-elbow','corner':outer,'rotation':stem_rotation(fold,-yaout)},
        'drain-outlet-stem':{'geometry':'drain-stem-elbow','corner':drain,'rotation':stem_rotation(N,E)},
        'vb-inlet-turn':{'geometry':'jg-turn-elbow','corner':inlet,'rotation':union(-E,N)},
        'vb-outlet-stem':{'geometry':'stem-elbow-trimmed','corner':outlet,'rotation':stem_rotation(N,vb_fold)},
        'vb-outlet-return':{'geometry':'elbow-elbow','corner':return_corner,'rotation':stem_rotation(vb_fold,-N)},
        'yb-stem-elbow':{'geometry':'gas-stem-elbow','corner':yb,'rotation':stem_rotation(U,ybout)}}
    exposed_b=float(np.linalg.norm((inlet-L*E)-(drain+S*E)))+float(np.linalg.norm(np.diff(vb_points[1:-1],axis=0),axis=1).sum())
    return {'tubes':{k:v.tolist() for k,v in tubes.items()},
        'joints':{k:{'geometry':v['geometry'],'corner':v['corner'].tolist(),'rotation':v['rotation'].tolist()} for k,v in joints.items()},
        'vb_native_origin_mm':VB_ORIGIN.tolist(),'vb_native_rotation':VB_NATIVE_R.tolist(),
        'vb_inlet_mm':vb_i.tolist(),'vb_outlet_mm':vb_o.tolist(),
        'drain_union_corner_mm':DRAIN_CORNER.tolist(),'ya_mouth_mm':YA_MOUTH.tolist(),'yb_mouth_mm':YB_MOUTH.tolist(),
        'va_fore_control_mm':np.array(va_control).tolist(),'va_fore_minimum_radius_mm':va_radius,
        'vb_return_control_mm':np.array(vb_control).tolist(),'vb_return_minimum_radius_mm':vb_radius,
        'vb_return_socket_mm':return_socket.tolist(),'vb_return_fold_degrees':20.,
        'vb_exposed_tube_length_mm':exposed_b,
        'pcb_native_rotation':PCB_R.tolist(),'pcb_native_translation_mm':PCB_T.tolist(),
        'hardware_scope':'V-A and the upstream group stay fixed. V-B and its core-roof wall remain square. Its nested outlet fold clocks west/up20degrees. Y-A and Y-B stem elbows clock7.5degrees outward from fore; the Y-A fold drops30degrees.',
        'insertions_mm':{'JG_socket':JG_DEPTH,'NeoFit_socket':NEOFIT_DEPTH,'Beduan_socket':12.7,'YA_YB_tee':15.7},
        'drain_stem_exposure_mm':DRAIN_STEM_EXPOSED,
        'drain_stem_length_mm':JG_DEPTH+DRAIN_STEM_EXPOSED,
        'insertion_scope':'Family-based layout estimates. Drain outlet stem retains3.3058mm exposure for the cradle; other stems seat shoulder-flush.'}

def library():
    g=parent.library()
    v,f=g['stem-elbow-trimmed'];v=v.copy();mask=v[:,0]<-H
    v[mask,0]=-H+(v[mask,0]+H)*(JG_DEPTH+DRAIN_STEM_EXPOSED)/12.7
    g['drain-stem-elbow']=v,f
    for name,points in route()['tubes'].items():g[name]=tube(points)
    with np.load(HERE/'parts/vb-core-support.npz') as mesh:
        g['vb-core-support']=mesh['v'],mesh['f']
    return g


def pose(g):
    scene=parent.pose(g);d=route()
    for item in scene['instances']:
        if item['name']=='pcba' or item.get('connection_owner')=='pcba':
            item.update(rotation=PCB_R.tolist(),translation=PCB_T.tolist())
            if item['name']=='pcba':item['label']='Main PCB · west · long dimension fore–aft · JSTs open above'
        if item['name']=='va-ya-straight':
            item.update(geometry='va-fore-feed',label='V-A feed · east of PCB · gentle direct fore run below the drain')
        if item['name']=='ya-stem-elbow':
            j=d['joints']['ya-stem-elbow'];item.update(translation=j['corner'],rotation=j['rotation'],label='Y-A · fore-facing stem elbow · clocked7.5degrees east')
    vb_r=VB_NATIVE_R@VK_SOURCE_R.T;vb_t=VB_ORIGIN-vb_r@VK_SOURCE_T
    scene['instances'].extend([
        base.instance('vb','vk',vb_t,vb_r,role='wet',kind='component',label='V-B · east of PCB · head east · flow aft · cold-core roof'),
        base.instance('vb-core-support','vb-core-support',role='support',kind='component',label='V-B socket wall · rooted in the cold-core roof · back-bottom'),
        base.instance('tee-yb-target','forward-tee-y-b',role='wet',kind='component',context=True,label='Y-B · funnel-source tee · fixed production position'),
        base.instance('funnel-drain-union','jg-turn-elbow',DRAIN_CORNER,I,role='wet',kind='elbow',label='Funnel drain · scanned JG union elbow · aft outlet'),
        base.instance('funnel-drain-stub','forward-funnel-drain-stub',role='wet',kind='tube',context=True,label='Funnel drain stub · existing production position'),
        base.instance('funnel-drain-cradle','forward-elbow-cradle',role='support',kind='component',context=True,label='Funnel drain elbow cradle · existing production position')])
    labels={
        'ya-fold-inner':'Y-A · union elbow · concealed tube at inlet',
        'ya-fold-return':'Y-A · stem elbow returns aft below drain cradle',
        'vb-outlet-stem':'V-B outlet · stem elbow folds west and up20degrees',
        'vb-outlet-return':'V-B outlet · nested stem elbow returns fore beside the seat wall',
        'yb-stem-elbow':'Y-B · fore-facing stem elbow · clocked7.5degrees west'}
    for name,j in d['joints'].items():
        if name=='ya-stem-elbow':continue
        scene['instances'].append(base.instance(name,j['geometry'],j['corner'],j['rotation'],role='stem' if j['geometry']!='jg-turn-elbow' else 'wet',kind='elbow',label=labels.get(name,name.replace('-',' '))))
    for name in d['tubes']:
        if name=='va-fore-feed':continue
        scene['instances'].append(base.instance(name,name,role='flavor',kind='tube',label=name.replace('-',' ')))
    superseded={frozenset(('va-ya-straight','ya-stem-elbow'))}
    scene['mates']=[item for item in scene['mates'] if frozenset((item['a'],item['b'])) not in superseded]
    pairs=[('va-ya-straight','ya-fold-return'),('ya-fold-return','ya-fold-inner'),('ya-fold-inner','ya-concealed-link'),('ya-concealed-link','ya-stem-elbow'),
        ('funnel-drain-union','funnel-drain-stub'),('funnel-drain-union','funnel-drain-cradle'),('funnel-drain-cradle','funnel-drain-stub'),('funnel-drain-stub','funnel'),
        ('funnel-drain-union','drain-outlet-stem'),('drain-outlet-stem','drain-vb-east-link'),('drain-vb-east-link','vb-inlet-turn'),('vb-inlet-turn','drain-vb-inlet-link'),('drain-vb-inlet-link','vb'),
        ('vb','vb-outlet-stem'),('vb-outlet-stem','vb-outlet-return'),('vb-outlet-return','vb-yb-link'),('vb-yb-link','yb-stem-elbow'),('yb-stem-elbow','tee-yb-target')]
    scene['mates'].extend({'a':a,'b':b,'connection':'Intended seated fitting, tube insertion or existing drain support'} for a,b in pairs)
    scene['mates'].append({'a':'vb','b':'vb-core-support','connection':'Four existing posts seat in shared V69 blind sockets'})
    scene.update(id='funnel-gate',title='West PCB and V-B on the east cold-core roof')
    scene['layout'].update(funnel_gate=d,
        pcb_footprint_mm={'xmin':-83.,'xmax':-10.1999817,'ymin':186.3868525,'ymax':277.2029078},
        pcb_orientation='Flat, long dimension fore–aft; all JST mating housings open above',
        route_context='V-A and upstream group fixed; V-B on the core roof east of the PCB; Y-A/Y-B and funnel drain retain production datums',
        pending_structure='Native V-B wall roots in the cold-core roof; production fusion and installed retention remain to qualify. PCB retention is to design.',
        pcb_local_lead_dressing='Ordinary edge-directed local estimates carried with the PCB')
    return scene

def check(scene,g):
    result=parent.check(scene,g);meshes=base.world_meshes(scene,g)
    import fcl
    def obj(mesh):
        v,f=mesh;m=fcl.BVHModel();m.beginModel(len(v),len(f));m.addSubModel(v,f.astype(np.int32));m.endModel();return fcl.CollisionObject(m)
    names=['vb','pcba','pump','funnel-frame','funnel','left-wall','right-wall','drain-outlet-stem','vb-inlet-turn','vb-outlet-stem','vb-outlet-return','vb-yb-link','vb-core-support','ya-fold-inner','ya-fold-return','ya-stem-elbow','yb-stem-elbow','va-ya-straight','funnel-drain-cradle']
    objects={n:obj(meshes[n]) for n in names if n in meshes}
    pairs=[('vb','pcba'),('vb','funnel-frame'),('vb','funnel'),
        ('vb-core-support','funnel'),('vb-core-support','pcba'),('vb-core-support','funnel-frame'),
        ('vb-outlet-return','pump'),('vb-outlet-return','vb-core-support'),('vb-outlet-stem','right-wall'),
        ('drain-outlet-stem','funnel-drain-cradle'),
        ('vb-yb-link','ya-fold-inner'),('vb-yb-link','ya-stem-elbow'),
        ('vb-yb-link','funnel-drain-cradle'),('vb-yb-link','funnel-frame'),
        ('vb-yb-link','va-ya-straight'),('vb-yb-link','pcba'),
        ('ya-fold-return','funnel-drain-cradle'),('ya-stem-elbow','funnel-drain-cradle'),
        ('yb-stem-elbow','funnel-drain-cradle'),('va-ya-straight','pcba'),('va-ya-straight','funnel-drain-cradle')]
    result['funnel_gate_gaps_mm']={a+'_to_'+b:float(fcl.distance(objects[a],objects[b],fcl.DistanceRequest(),fcl.DistanceResult())) for a,b in pairs}
    result['vb_bounds_mm']=[meshes['vb'][0].min(0).tolist(),meshes['vb'][0].max(0).tolist()]
    result['vb_wall_bounds_mm']=[meshes['vb-core-support'][0].min(0).tolist(),meshes['vb-core-support'][0].max(0).tolist()]
    result['vb_body_to_plain_core_mm']=float(meshes['vb'][0][:,2].min()-253.4)
    result['funnel_route_minimum_radii_mm']={'va':route()['va_fore_minimum_radius_mm'],'vb':route()['vb_return_minimum_radius_mm']}
    result['vb_exposed_tube_length_mm']=route()['vb_exposed_tube_length_mm']
    result['pcb_bounds_mm']=[meshes['pcba'][0].min(0).tolist(),meshes['pcba'][0].max(0).tolist()]
    result['scope']='Manual exterior fit query of the selected core-roof V-B/west-PCB arrangement, native V-B wall and local installed electrical connections; intended seated connections excluded'
    return result

def service_check(scene,g):
    """Query JST withdrawal and 30 mm of vertical space above each housing."""
    import fcl
    import trimesh
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
        terminal='terminal-'+name.removeprefix('probe-').removesuffix('-pull')
        v=base.world_meshes({'instances':[item for item in scene['instances'] if item['name']==terminal]},g)[terminal][0]
        lo,hi=v.min(0),v.max(0)
        column=trimesh.creation.box(extents=[hi[0]-lo[0],hi[1]-lo[1],30.])
        column.apply_translation([(lo[0]+hi[0])/2,(lo[1]+hi[1])/2,hi[2]+15.])
        c=obj((np.array(column.vertices),np.array(column.faces)));headroom=[]
        for other in physical:
            if other=='ceiling':continue
            if fcl.collide(c,objects[other],fcl.CollisionRequest(),fcl.CollisionResult()):headroom.append(other)
        rows.append({'probe':name,'blocked_with_funnel_assembly_installed':hits,
            'vertical_headroom_30mm_obstructions':headroom,
            'blocked_after_front_top_removed':[n for n in hits if n not in front_top]})
    return {'scope':'Nominal 6 mm axial JST withdrawal and 30 mm vertical columns above housing outlines, with roof removed. Does not model fingers or complete harness manipulation.',
        'service_order':'JST withdrawal is evaluated with the funnel/frame installed; only the roof is removed for vertical headroom',
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
