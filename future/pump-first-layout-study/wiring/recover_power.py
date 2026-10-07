"""Recover route recipes from the received analytic conductor surfaces.

The saved native conductor and clearance files remain unchanged. Complete
circle sections supply a nonbranching centreline, and each arc supplies its
original virtual corner. The recovered recipe must reproduce every received
lateral section, surface area and the complete conductor volume.
"""
from pathlib import Path
import hashlib,json,math,sys
import cadquery as cq
from OCP.BRepAdaptor import BRepAdaptor_Surface

HERE=Path(__file__).resolve().parent
STUDY=HERE.parent;ROOT=STUDY.parents[1]
sys.path[:0]=[str(HERE),str(STUDY)]
from native_harness import sweep,bounds

JOBS={
 'AC1-H':('C14-H','wago-h:1','line','C14 to AC distribution'),
 'AC1-N':('C14-N','wago-n:1','neutral','C14 to AC distribution'),
 'AC1-G':('C14-PE','wago-g:1','earth','C14 to AC distribution'),
 'AC2-H':('wago-h:2','PSU-L','line','AC distribution to ClassII PSU'),
 'AC2-N':('wago-n:2','PSU-N','neutral','AC distribution to ClassII PSU'),
 'AC3-H':('wago-h:3','R1-COM','line','Unswitched line to relay1 COM'),
 'AC4-H':('R1-NO','COMP-H','switched-line','Relay1 NO to compressor SJOOW hot'),
 'AC5-N':('wago-n:3','COMP-N','neutral','AC neutral to compressor SJOOW'),
 'PE-feed':('wago-g:2','PE-feed','earth','AC earth distribution to bonded ring fan'),
 'AC6-G':('PE-compressor','COMP-G','earth','Ring fan to compressor SJOOW earth'),
 'DC1-V12':('PSU-V12','wago-v12:1','positive','PSU DC output to distribution'),
 'DC1-GND':('PSU-GND','wago-gnd:1','return','PSU DC output to distribution'),
 'DC2-V12':('wago-v12:2','R2-COM','positive','12V distribution to relay2 COM'),
 'DC3-V12':('R2-NO','MOTOR-+','switched-positive','Relay2 NO to motor pigtail reserve'),
 'DC3-GND':('wago-gnd:2','MOTOR-−','return','DC return to motor pigtail reserve'),
 'DC4-V12':('wago-v12:3','J10-V12','positive','12V distribution to J10'),
 'DC4-GND':('wago-gnd:3','J10-GND','return','12V distribution to J10'),
 'PE-carbonator':('PE-carbonator','LOWER-carbonator','earth','Ring fan to lower metalwork boundary reserve'),
 'PE-under-counter':('PE-under-counter','LOWER-under-counter','earth','Ring fan to lower metalwork boundary reserve'),
}

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def analytic_sections(shape,diameter):
    result=[]
    for face in shape.Faces():
        kind=face.geomType()
        if kind=='PLANE':continue
        if kind not in ['CYLINDER','TORUS']:raise ValueError('Nonanalytic conductor surface '+kind)
        points=[]
        for edge in face.Edges():
            if edge.geomType()!='CIRCLE' or abs(edge.radius()-diameter/2)>1e-6:continue
            p=edge._geomAdaptor().Circle().Location();point=cq.Vector(p.X(),p.Y(),p.Z())
            if not any((point-q).Length<1e-6 for q in points):points.append(point)
        if len(points)!=2:raise ValueError('Incomplete analytic circular section')
        a,b=points
        item={'kind':kind,'a':a,'b':b,'area':face.Area()}
        if kind=='TORUS':
            torus=BRepAdaptor_Surface(face.wrapped).Torus();p=torus.Location()
            item.update(centre=cq.Vector(p.X(),p.Y(),p.Z()),radius=torus.MajorRadius())
        result.append(item)
    return result

def recover(shape,start,end,diameter=3.2,radius=3.4):
    sections=analytic_sections(shape,diameter)
    nodes=[];incident={}
    def node(point):
        for index,other in enumerate(nodes):
            if (point-other).Length<1e-6:return index
        nodes.append(point);return len(nodes)-1
    for index,item in enumerate(sections):
        item['nodes']=(node(item['a']),node(item['b']))
        for n in item['nodes']:incident.setdefault(n,[]).append(index)
    if any(len(edges)>2 for edges in incident.values()):raise ValueError('Received centreline branches')
    first=node(cq.Vector(*start));last=node(cq.Vector(*end))
    if first not in incident or last not in incident or len(incident[first])!=1 or len(incident[last])!=1:
        raise ValueError('Current endpoint does not match a received open section')
    at=first;visited=set();points=[list(start)];length=0.;ordered=[]
    while at!=last:
        choices=[i for i in incident[at]if i not in visited]
        if len(choices)!=1:raise ValueError('Received centreline is not one continuous open route')
        index=choices[0];visited.add(index);item=sections[index]
        next_node=next(n for n in item['nodes']if n!=at)
        a,b=nodes[at],nodes[next_node]
        if item['kind']=='CYLINDER':edge=cq.Edge.makeLine(a,b)
        else:
            c=item['centre'];r=item['radius']
            if abs(r-radius)>1e-6:raise ValueError('Received arc radius differs from route standard')
            mid=c+((a-c)+(b-c)).normalized()*r
            edge=cq.Edge.makeThreePointArc(a,mid,b)
            theta=edge.Length()/r
            if theta>=math.pi-1e-6:raise ValueError('Cannot recover a semicircular virtual corner')
            corner=a+edge.tangentAt(0).normalized()*(r*math.tan(theta/2))
            points.append(list(corner.toTuple()))
        length+=edge.Length();ordered.append(index);at=next_node
    if len(visited)!=len(sections):raise ValueError('Disconnected received conductor sections')
    points.append(list(end));authored,_=sweep(points,diameter,radius)
    remaining=analytic_sections(authored,diameter)
    matched=[]
    for item in sections:
        choices=[]
        for index,other in enumerate(remaining):
            if other['kind']!=item['kind']:continue
            direct=max((item['a']-other['a']).Length,(item['b']-other['b']).Length)
            reverse=max((item['a']-other['b']).Length,(item['b']-other['a']).Length)
            if min(direct,reverse)>1e-6:continue
            if abs(item['area']-other['area'])>max(.0001,item['area']*1e-6):continue
            if item['kind']=='TORUS' and ((item['centre']-other['centre']).Length>1e-6 or abs(item['radius']-other['radius'])>1e-6):continue
            choices.append(index)
        if len(choices)!=1:raise ValueError('Recovered recipe differs from a received lateral section')
        matched.append(remaining.pop(choices[0]))
    if remaining:raise ValueError('Recovered recipe adds lateral sections')
    volume_error=abs(authored.Volume(tol=1e-9)-shape.Volume(tol=1e-9))
    if volume_error>.001:raise ValueError('Recovered complete conductor volume differs')
    return points,length,{'pass':True,'received_lateral_members':len(sections),
        'matched_lateral_members':len(matched),'maximum_section_position_tolerance_mm':1e-6,
        'complete_length_mm':length,'reconstructed_volume_difference_mm3':volume_error,
        'scope':'Current open endpoints and every received cylinder/torus circle section, area and arc centre/radius match the reconstructed recipe. This restores metadata; independent physical-member clearance is required before publication.'}

def main():
    path=HERE/'power-candidate.json';power=json.loads(path.read_text());restored={}
    received_manifest_sha=sha(path)
    for name,(a,b,color,topology) in JOBS.items():
        if name in power['power_routes']:continue
        key='wire-'+name;native=ROOT/'.cache/pump-first-layout/wiring/power'/(key+'.brep')
        cutter=native.with_name(key+'-clearance.brep')
        shape=cq.Shape.importBrep(str(native));points,length,proof=recover(shape,power['ports'][a]['point'],power['ports'][b]['point'])
        power['parts'][key]={'brep':str(native.relative_to(ROOT)),'sha256':sha(native),'bounds':bounds(shape),
            'role':'wiring','color_role':color,'detail':topology+'; nominal Ø3.2 conductor exterior, exact R3.4 arcs.'}
        power['clearance_cutters'][key]={'brep':str(cutter.relative_to(ROOT)),'sha256':sha(cutter)}
        power['power_routes'][name]={'points_mm':points,'radius_mm':3.4,'diameter_mm':3.2,'length_mm':length,
            'from':power['ports'][a],'to':power['ports'][b],'search_states':None,'native_interferences':[],
            'topology':topology,'from_key':a,'to_key':b,'received_native_recovery':proof}
        for end in [a,b]:power['intended_contacts'].append([key,power['ports'][end]['owner']])
        restored[name]={'received_conductor_sha256':sha(native),'received_cutter_sha256':sha(cutter),**proof}
        print('Recovered analytic route',name,len(points),length,flush=True)
    power['expected_route_count']=19;power['pass']=False
    power['failures']=[{'check':'independent physical-member gate pending after native recipe recovery'}]
    path.write_text(json.dumps(power,indent=2)+'\n')
    report={'pass':len(power['power_routes'])==19,'received_manifest_sha256':received_manifest_sha,
        'source_inputs':{str(Path(__file__).relative_to(ROOT)):sha(Path(__file__))},'restored_routes':restored,
        'route_count':len(power['power_routes']),'published_manifest_sha256':sha(path)}
    (HERE/'power-recovery-check.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({'restored':len(restored),'routes':len(power['power_routes']),'pass':report['pass']}),flush=True)

if __name__=='__main__':main()
