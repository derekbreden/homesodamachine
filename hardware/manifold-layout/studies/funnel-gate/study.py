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

def module(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    result=importlib.util.module_from_spec(spec);spec.loader.exec_module(result);return result

b_plumbing=module('funnel_gate_b_plumbing',HERE/'b_plumbing.py')
soda_route=module('funnel_gate_soda_route',HERE/'soda_route.py')
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
DRAIN_CORNER=b_plumbing.DRAIN_CORNER.copy()
DRAIN_SHIFT=DRAIN_CORNER-np.array([0.,161.69575,280.41])
YB_MOUTH=np.array([-22.35,166.24,270.675])
YA_MOUTH=parent.DEST.copy()
FLOW_R=soda_route.METER_R
FLOW_T=soda_route.METER_T


def union(a,b):return np.column_stack([np.cross(a,b),a,b])
def stem_rotation(host,out):return np.column_stack([host,out,np.cross(host,out)])
def tube(points):return parent.grid_model.tube(points,3.175,2.12)
def inserted(a,axis_a,b,axis_b,depth_a=JG_DEPTH,depth_b=JG_DEPTH):
    return np.array([np.array(a)-depth_a*np.array(axis_a),a,b,np.array(b)-depth_b*np.array(axis_b)])
def route():
    angle=np.radians(7.5)
    yaout=np.sin(angle)*E+np.cos(angle)*N
    ya=YA_MOUTH+H*U;yasocket=ya+S*yaout
    # Keep the fore feed below the B inlet and west of V-B's seat wall.
    # The two tangent spans dress one continuous tube into Y-A's single elbow.
    start=np.array(parent.route()['turn_outlet_mm'])
    low=np.array([24.,235.,start[2]])
    va_control1=[start,start-20*N,low+20*N,low]
    va_control2=[low,low-17*N,yasocket+17*yaout,yasocket]
    va_curve1,va_radius1=parent.bezier(va_control1)
    va_curve2,va_radius2=parent.bezier(va_control2)
    va_radius=min(va_radius1,va_radius2)
    va_points=np.vstack([start+JG_DEPTH*N,va_curve1,va_curve2[1:],yasocket-NEOFIT_DEPTH*yaout])
    b=b_plumbing.route(VB_ORIGIN,DRAIN_STEM_EXPOSED)
    soda=soda_route.route()
    tubes={'va-fore-feed':va_points.tolist(),**b['tubes'],**soda['tubes']}
    joints={'ya-stem-elbow':{'geometry':'gas-stem-elbow','corner':ya.tolist(),
                             'rotation':stem_rotation(U,yaout).tolist()},
            **b['joints'],**soda['joints']}
    exposed_b=sum(b['metrics'][key] for key in
                  ('inlet_exposed_length_mm','cross_exposed_length_mm','return_exposed_length_mm'))
    return {'tubes':tubes,'joints':joints,'mates':b['mates']+soda['mates'],
        'vb_native_origin_mm':VB_ORIGIN.tolist(),'vb_native_rotation':VB_NATIVE_R.tolist(),
        'vb_inlet_mm':b['vb_inlet_mm'],'vb_outlet_mm':b['vb_outlet_mm'],
        'drain_union_corner_mm':DRAIN_CORNER.tolist(),'ya_mouth_mm':YA_MOUTH.tolist(),'yb_mouth_mm':YB_MOUTH.tolist(),
        'va_fore_controls_mm':[np.array(va_control1).tolist(),np.array(va_control2).tolist()],
        'va_fore_minimum_radius_mm':va_radius,'vb_return_minimum_radius_mm':b['metrics']['return_minimum_radius_mm'],
        'vb_exposed_tube_length_mm':exposed_b,'b_plumbing':b['metrics'],'soda_route':soda,
        'pcb_native_rotation':PCB_R.tolist(),'pcb_native_translation_mm':PCB_T.tolist(),
        'hardware_scope':'V-A stays low; V-B feeds Y-B through an aft-side stair over the PCB. The valve inlet uses a directly seated stem elbow. The aft edge-on meter has no exposed outlet tube and a direct-down inlet to a proposed aft core guide.',
        'insertions_mm':{'JG_socket':JG_DEPTH,'NeoFit_socket':NEOFIT_DEPTH,'Beduan_socket':12.7,'YA_YB_tee':15.7},
        'drain_stem_exposure_mm':DRAIN_STEM_EXPOSED,
        'drain_stem_length_mm':JG_DEPTH+DRAIN_STEM_EXPOSED,
        'insertion_scope':'Family-based layout estimates. Drain outlet stem retains 3.3058 mm exposure for the cradle; other stems seat shoulder-flush.'}

def library():
    g=parent.library()
    v,f=g['stem-elbow-trimmed'];v=v.copy();mask=v[:,0]<-H
    v[mask,0]=-H+(v[mask,0]+H)*(JG_DEPTH+DRAIN_STEM_EXPOSED)/12.7
    g['drain-stem-elbow']=v,f
    v,f=g['elbow-elbow'];v=v.copy();mask=v[:,0]<-H
    v[mask,0]=-H+(v[mask,0]+H)*(NEOFIT_DEPTH+soda_route.REAR_STEM_EXPOSED)/NEOFIT_DEPTH
    g['soda-rear-stem-elbow']=v,f
    for name,points in route()['tubes'].items():g[name]=tube(points)
    with np.load(HERE/'parts/vb-core-support.npz') as mesh:
        g['vb-core-support']=mesh['v'],mesh['f']
    with np.load(HERE/'parts/digiten-flow.npz') as mesh:
        g['digiten-flow']=mesh['v'],mesh['f']
    with np.load(HERE/'parts/pcb-j11-dressed-lead.npz') as mesh:
        g['pcb-j11-dressed-lead']=mesh['v'],mesh['f']
    with np.load(HERE/'parts/pcb-j3-dressed-lead.npz') as mesh:
        g['pcb-j3-dressed-lead']=mesh['v'],mesh['f']
    for suffix in ('','-frame','-cover','-ceiling','-left-wall','-right-wall'):
        key='expanded-funnel'+suffix
        with np.load(HERE/'parts'/(key+'.npz')) as mesh:g[key]=mesh['v'],mesh['f']
    return g


def pose(g):
    scene=parent.pose(g);d=route()
    replacements={'funnel':'expanded-funnel','funnel-frame':'expanded-funnel-frame',
        'ceiling':'expanded-funnel-ceiling','left-wall':'expanded-funnel-left-wall','right-wall':'expanded-funnel-right-wall'}
    obsolete={'bulkhead-carb-departure'}
    scene['instances']=[item for item in scene['instances'] if item['name'] not in obsolete]
    scene['mates']=[mate for mate in scene['mates'] if mate['a'] not in obsolete and mate['b'] not in obsolete]
    for item in scene['instances']:
        if item['name'] in replacements:
            item.update(geometry=replacements[item['name']],rotation=I.tolist(),translation=[0.,0.,0.])
        if item['name']=='soda-stem-elbow':
            joint=d['joints'][item['name']];item.update(geometry=joint['geometry'],rotation=joint['rotation'],translation=joint['corner'])
        if item['name']=='local-lead-J11':
            item.update(geometry='pcb-j11-dressed-lead',label='J11 · conductors dress aft with a low R4 bend')
        if item['name']=='local-lead-J3':
            item.update(geometry='pcb-j3-dressed-lead',label='J3 · local conductor exits dress aft')
        if item['name']=='pcba' or item.get('connection_owner')=='pcba':
            item.update(rotation=PCB_R.tolist(),translation=PCB_T.tolist())
            if item['name']=='pcba':item['label']='Main PCB · west · long dimension fore–aft · connect before funnel/frame'
        if item['name']=='va-ya-straight':
            item.update(geometry='va-fore-feed',label='V-A feed · east of PCB · gentle direct fore run below the drain')
        if item['name']=='ya-stem-elbow':
            j=d['joints']['ya-stem-elbow'];item.update(translation=j['corner'],rotation=j['rotation'],label='Y-A · single aft-facing stem elbow · clocked 7.5 degrees east')
    vb_r=VB_NATIVE_R@VK_SOURCE_R.T;vb_t=VB_ORIGIN-vb_r@VK_SOURCE_T
    scene['instances'].extend([
        base.instance('vb','vk',vb_t,vb_r,role='wet',kind='component',label='V-B · east of PCB · head east · flow aft · cold-core roof'),
        base.instance('digiten-flow','digiten-flow',FLOW_T,FLOW_R,role='wet',kind='component',label='DIGITEN flow meter · aft between pump and CO2 · ports fore–aft · outlet collets meet'),
        base.instance('vb-core-support','vb-core-support',role='support',kind='component',label='V-B socket wall · rooted in the cold-core roof · back-bottom'),
        base.instance('tee-yb-target','forward-tee-y-b',role='wet',kind='component',context=True,label='Y-B · funnel-source tee · fixed production position'),
        base.instance('funnel-drain-union','jg-turn-elbow',DRAIN_CORNER,I,role='wet',kind='elbow',label='Funnel drain · scanned JG union elbow · aft outlet'),
        base.instance('funnel-drain-stub','forward-funnel-drain-stub',DRAIN_SHIFT,role='wet',kind='tube',context=True,label='Funnel drain stub · centered on the funnel mouth'),
        base.instance('funnel-drain-cradle','forward-elbow-cradle',DRAIN_SHIFT,role='support',kind='component',context=True,label='Funnel drain elbow cradle · snaps into the removable funnel frame')])
    labels={
        'drain-outlet-stem':'B feed · drain stem elbow · level east outlet',
        'vb-inlet-turn':'B feed · stem elbow seated directly in V-B · level west pickup',
        'vb-outlet-stem':'V-B outlet · stem elbow points west and up 8 degrees',
        'vb-outlet-return':'B return · two-socket elbow turns the cross-PCB tube toward Y-B',
        'yb-stem-elbow':'Y-B · aft-facing stem elbow · clocked 7.5 degrees west',
        'soda-inlet-stem':'Core soda · inlet stem turns directly down aft of the pump elbow',
        'soda-outlet-return-stem':'Soda outlet · fore-facing stem · 2.4048 mm exposed for CO2 clearance · collet meets meter'}
    for name,j in d['joints'].items():
        if name in ('ya-stem-elbow','soda-stem-elbow'):continue
        scene['instances'].append(base.instance(name,j['geometry'],j['corner'],j['rotation'],role='stem' if j['geometry']!='jg-turn-elbow' else 'wet',kind='elbow',label=labels.get(name,name.replace('-',' '))))
    for name in d['tubes']:
        if name=='va-fore-feed':continue
        scene['instances'].append(base.instance(name,name,role='carbonator' if name.startswith('soda-') else 'flavor',kind='tube',label=name.replace('-',' ')))
    pairs=[('funnel-drain-union','funnel-drain-stub'),('funnel-drain-union','funnel-drain-cradle'),
        ('funnel-drain-cradle','funnel-drain-stub'),('funnel-drain-stub','funnel'),
        ('funnel','funnel-drain-cradle'),
        ('funnel-frame','funnel-drain-cradle'),*d['mates']]
    scene['mates'].extend({'a':a,'b':b,'connection':'Intended seated fitting, tube insertion or existing drain support'} for a,b in pairs)
    scene['mates'].append({'a':'vb','b':'vb-core-support','connection':'Four existing posts seat in shared V69 blind sockets'})
    scene.update(id='funnel-gate',title='West PCB and V-B on the east cold-core roof')
    scene['layout'].update(funnel_gate=d,
        flow_meter={'native_origin_mm':FLOW_T.tolist(),'native_rotation':FLOW_R.tolist(),'attachment':'Proposed core-mounted support aft between the pump and CO2 path; retention detail is to design','scope':'Direct-down inlet to proposed aft core guide and concealed outlet join shown; internal core integration, pigtail and retention remain separate'},
        funnel_expansion={'aft_extension_mm':35.,
            'capacity_to_mouth_ml':json.loads((HERE/'funnel-expansion.json').read_text())['capacity_to_mouth_ml'],
            'outlet_fore_of_mouth_center_mm':0.,'receipt':'funnel-expansion.json'},
        pcb_footprint_mm={'xmin':-83.,'xmax':-10.1999817,'ymin':186.3868525,'ymax':277.2029078},
        pcb_orientation='Flat, long dimension fore–aft; funnel/frame drops in after electrical connections',
        route_context='V-A, upstream group and Y-A/Y-B fixed; centered funnel outlet at Y179.19575; V-B on the core roof east of the PCB',
        pending_structure='Native V-B wall roots in the cold-core roof; production fusion and installed retention remain to qualify. PCB retention is to design.',
        pcb_local_lead_dressing='J11 dresses aft with a 1 mm straight exit and R4 bend; other local estimates carry with the PCB')
    return scene

def check(scene,g):
    result=parent.check(scene,g);meshes=base.world_meshes(scene,g)
    import fcl
    def obj(mesh):
        v,f=mesh;m=fcl.BVHModel();m.beginModel(len(v),len(f));m.addSubModel(v,f.astype(np.int32));m.endModel();return fcl.CollisionObject(m)
    names=['vb','pcba','pump','funnel-frame','funnel','left-wall','right-wall','drain-outlet-stem','drain-vb-east-link','vb-yb-cross','soda-meter-bulkhead','vb-inlet-turn','vb-outlet-stem','vb-outlet-return','vb-yb-link','vb-core-support','ya-stem-elbow','yb-stem-elbow','va-ya-straight','funnel-drain-cradle','local-lead-J3','digiten-flow','asse','psu','ceiling']
    names+=['vk','gas-check','gas-regulator','gas-core-drop','pump-inlet-tpu','lower-pump-elbow',*soda_route.route()['joints'],*soda_route.route()['tubes']]
    objects={n:obj(meshes[n]) for n in names if n in meshes}
    pairs=[('vb','pcba'),('vb','funnel-frame'),('vb','funnel'),
        ('vb-core-support','funnel'),('vb-core-support','pcba'),('vb-core-support','funnel-frame'),
        ('vb-outlet-return','pump'),('vb-outlet-return','vb-core-support'),('vb-outlet-stem','right-wall'),
        ('drain-outlet-stem','funnel-drain-cradle'),
        ('drain-vb-east-link','vb-yb-link'),('drain-outlet-stem','ya-stem-elbow'),
        ('va-ya-straight','vb-inlet-turn'),('va-ya-straight','drain-vb-east-link'),
        ('vb-yb-link','ya-stem-elbow'),
        ('vb-yb-link','funnel-drain-cradle'),('vb-yb-link','funnel-frame'),
        ('vb-yb-link','va-ya-straight'),('vb-yb-link','pcba'),
        ('ya-stem-elbow','funnel-drain-cradle'),
        ('yb-stem-elbow','funnel-drain-cradle'),('va-ya-straight','pcba'),('va-ya-straight','funnel-drain-cradle'),
        ('drain-outlet-stem','local-lead-J3'),('vb-yb-link','local-lead-J3'),
        ('digiten-flow','pump'),('digiten-flow','asse'),('digiten-flow','psu'),('digiten-flow','ceiling'),
        ('soda-meter-bulkhead','pump'),('vb-yb-cross','pcba'),('vb-yb-cross','funnel-frame'),
        ('digiten-flow','gas-check'),('digiten-flow','gas-regulator'),('digiten-flow','gas-core-drop'),
        ('soda-inlet-stem','vk'),('soda-inlet-stem','right-wall'),('soda-inlet-stem','pump'),
        ('soda-core-rise','vk'),('soda-core-rise','pump'),('soda-core-rise','right-wall'),
        ('soda-core-rise','pump-inlet-tpu'),('soda-core-rise','lower-pump-elbow'),
        ('soda-outlet-return-stem','gas-regulator'),('soda-outlet-return-stem','pump')]
    result['funnel_gate_gaps_mm']={a+'_to_'+b:float(fcl.distance(objects[a],objects[b],fcl.DistanceRequest(),fcl.DistanceResult())) for a,b in pairs}
    result['vb_bounds_mm']=[meshes['vb'][0].min(0).tolist(),meshes['vb'][0].max(0).tolist()]
    result['vb_wall_bounds_mm']=[meshes['vb-core-support'][0].min(0).tolist(),meshes['vb-core-support'][0].max(0).tolist()]
    result['vb_body_to_plain_core_mm']=float(meshes['vb'][0][:,2].min()-253.4)
    result['funnel_route_minimum_radii_mm']={'va':route()['va_fore_minimum_radius_mm'],'vb':route()['vb_return_minimum_radius_mm']}
    result['vb_exposed_tube_length_mm']=route()['vb_exposed_tube_length_mm']
    result['pcb_bounds_mm']=[meshes['pcba'][0].min(0).tolist(),meshes['pcba'][0].max(0).tolist()]
    result['flow_meter_bounds_mm']=[meshes['digiten-flow'][0].min(0).tolist(),meshes['digiten-flow'][0].max(0).tolist()]
    result['flow_meter_ports_mm']={'inlet':soda_route.route()['meter_inlet_mm'],'outlet':soda_route.route()['meter_outlet_mm']}
    result['b_plumbing']=route()['b_plumbing']
    result['soda_outlet_route']=soda_route.route()['metrics']
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
    removable_funnel={'funnel','funnel-frame'}
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
            'blocked_after_funnel_frame_removed':[n for n in hits if n not in removable_funnel],
            'vertical_headroom_30mm_after_funnel_frame_removed':[n for n in headroom if n not in removable_funnel],
            'blocked_after_front_top_removed':[n for n in hits if n not in front_top]})
    return {'scope':'Nominal 6 mm axial JST withdrawal and 30 mm vertical columns above housing outlines, with roof removed. Does not model fingers or complete harness manipulation.',
        'service_order':'Complete electrical connections before the funnel/frame drops in. Report both installed and removed states; plumbing may remain above the PCB.',
        'headers':rows}

def viewer_data(scene,g):
    data=parent.viewer_data(scene,g)
    # The native assets and fit query retain full meshes; this is the inline
    # viewer's surface sampling for the expanded printed parts.
    for name in data['geometries']:
        if name.startswith('expanded-funnel'):
            data['geometries'][name]=base.pack(*g[name],2200)
        elif name=='soda-rear-stem-elbow':
            data['geometries'][name]=base.pack(*g[name],1200)
    return data
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
