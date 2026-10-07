"""Prepare and inspect native study slices without submitting a printer job.

Each project is bound to one exact native B-rep and a saved production recipe.
Generated projects and G-code remain disposable; compact emitted-path records
live with the study. A successful slice does not qualify strength or removal.
"""
from pathlib import Path
import argparse,hashlib,json,subprocess,sys,zipfile,re
import xml.etree.ElementTree as ET
import cadquery as cq

HERE=Path(__file__).resolve().parent
STUDY=HERE.parent
ROOT=STUDY.parents[1]
CACHE=ROOT/'.cache/pump-first-layout/slices'
sys.path.insert(0,str(ROOT/'hardware/printed-parts/faucet'))
import refresh_print_project as writer

def front_void_review(mesh,native):
    """Validate the retained sealed RC62 pocket before preparing front-top."""
    import manifold3d as md
    import numpy as np
    import trimesh
    from scipy.sparse import coo_matrix
    from scipy.sparse.csgraph import connected_components
    sys.path.insert(0,str(STUDY));import baseline
    original=baseline.read(['enclosure-front-top'])['enclosure-front-top']
    shape=cq.Shape.importBrep(str(native))
    assert shape.isValid() and len(shape.Solids())==1 and len(shape.Shells())==2
    assert len(original.Shells())==2
    cavity_shell=min(original.Shells(),key=lambda shell:shell.BoundingBox().DiagonalLength)
    box=cavity_shell.BoundingBox()
    expected=np.array([[box.xmin,box.ymin,box.zmin],[box.xmax,box.ymax,box.zmax]])
    native_shell=min(shape.Shells(),key=lambda shell:shell.BoundingBox().DiagonalLength)
    box=native_shell.BoundingBox()
    actual=np.array([[box.xmin,box.ymin,box.zmin],[box.xmax,box.ymax,box.zmax]])
    assert np.allclose(actual,expected,atol=1e-7,rtol=0)
    source_void=cq.Solid.makeSolid(cavity_shell)
    native_void=cq.Solid.makeSolid(native_shell)
    common=abs(source_void.intersect(native_void,tol=.0001).Volume(tol=1e-9))
    unchanged_void_error=abs(source_void.Volume())+abs(native_void.Volume())-2*common
    assert abs(unchanged_void_error)<1e-5
    edges=mesh.edges_unique
    graph=coo_matrix((np.ones(len(edges)),(edges[:,0],edges[:,1])),shape=(len(mesh.vertices),len(mesh.vertices)))
    count,labels=connected_components(graph,directed=False)
    components=[trimesh.Trimesh(vertices=mesh.vertices,faces=mesh.faces[np.all(labels[mesh.faces]==i,axis=1)],process=True)for i in range(count)]
    assert count==2 and all(c.is_watertight and c.is_winding_consistent for c in components)
    positive=[c for c in components if c.volume>0];negative=[c for c in components if c.volume<0]
    assert len(positive)==1 and len(negative)==1
    outer,cavity=positive[0],negative[0]
    # The circular pocket extrema need not coincide with a sampled STL vertex.
    # Bind its exact native solid first, then allow only the export tolerance.
    mesh_bounds_error=float(np.max(np.abs(cavity.bounds-expected)))
    assert mesh_bounds_error<=.06
    def manifold(part):
        result=md.Manifold(md.Mesh(vert_properties=np.asarray(part.vertices,dtype=np.float32),tri_verts=np.asarray(part.faces,dtype=np.uint32)))
        assert result.status()==md.Error.NoError
        return result
    void=cavity.copy();void.invert()
    solid,empty=manifold(outer),manifold(void)
    outside=(empty-solid).volume();assert abs(outside)<1e-5
    entire=manifold(mesh)
    assert entire.volume()>0 and np.isclose(entire.volume(),solid.volume()-empty.volume(),atol=.001,rtol=0)
    return {'positive_material_body_count':1,'connected_closed_shell_components':2,
            'enclosed_inward_cavity_count':1,'cavity_bounds_mm':cavity.bounds.tolist(),
            'native_cavity_bounds_mm':actual.tolist(),
            'native_cavity_symmetric_difference_mm3':unchanged_void_error,
            'mesh_cavity_bounds_error_mm':mesh_bounds_error,'mesh_export_tolerance_mm':.06,
            'cavity_signed_volume_mm3':cavity.volume,'cavity_outside_positive_mm3':outside,
            'baseline_sha256':baseline.prepare()['sha256'],'native_brep_sha256':sha(native),
            'scope':'One closed material exterior and the unchanged enclosed RC62 pocket from the frozen front-top. No disconnected positive material or exterior hole is accepted.'}

def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def review_mesh(path):
    """Remove zero-area facets and exact opposing internal facet pairs.

    OCC can emit both sides of coincident internal partition faces. These
    pairs cancel in signed volume and are not the exterior print surface.
    This review moves no vertices, fills no holes and rejects other defects.
    """
    import numpy as np
    import trimesh
    mesh=trimesh.load(path,force='mesh')
    before=len(mesh.faces);volume=mesh.volume
    keep=mesh.nondegenerate_faces(height=1e-8).copy()
    degenerate=int((~keep).sum());opposed=0
    _,groups,counts=np.unique(np.sort(mesh.faces,axis=1),axis=0,return_inverse=True,return_counts=True)
    for group in np.where(counts>1)[0]:
        indices=np.where(groups==group)[0]
        if len(indices)==2 and float(np.dot(mesh.face_normals[indices[0]],mesh.face_normals[indices[1]]))<-.999999:
            keep[indices]=False;opposed+=2
    mesh.update_faces(keep);mesh.remove_unreferenced_vertices()
    delta=abs(mesh.volume-volume)
    if delta>max(1e-6,abs(volume)*1e-10):raise ValueError('Surface review changes occupied mesh volume: '+str(path))
    if not mesh.is_volume:raise ValueError('Native mesh has an unresolved exterior defect: '+str(path))
    if not keep.all():mesh.export(path)
    return {'input_faces':before,'output_faces':len(mesh.faces),
            'zero_area_facets_removed':degenerate,'opposing_internal_facets_removed':opposed,
            'vertex_displacement_mm':0.,'signed_volume_change_mm3':delta,
            'closed_oriented_volume':mesh.is_volume}

def selected_parts():
    funnel=json.loads((STUDY/'funnel/candidate.json').read_text())
    tooling=json.loads((STUDY/f"funnel/candidate-aft-{funnel['aft_extension_mm']:g}-tooling.json").read_text())
    rows={
        'funnel-frame':(funnel['parts']['funnel-frame'],0,'petgf'),
        'funnel-cover':(funnel['parts']['funnel-cover'],180,'petgf'),
        'funnel-mold-cavity':(tooling['artifact_parts']['cavity'],0,'mold'),
        'funnel-mold-core':(tooling['artifact_parts']['core'],180,'mold')}
    assembly=STUDY/'structure/print-parts.json'
    if assembly.exists():
        for name,record in json.loads(assembly.read_text())['parts'].items():
            rows[name]=(record,record['rotation_x_deg'],'petgf')
    return rows

def prepare_policy(project,preparation,name):
    """Retain the production roof transitions, without changing bearings."""
    bands=[];painted=0
    if name not in ['enclosure-front-top','enclosure-back-top']:return bands,painted
    with zipfile.ZipFile(project) as z:members={n:z.read(n) for n in z.namelist()}
    settings=json.loads(members[writer.SETTINGS_MEMBER])
    settings.update(support_filament='1',support_interface_filament='1',flush_into_support='0')
    if name=='enclosure-back-top':settings['elefant_foot_compensation']='0'
    members[writer.SETTINGS_MEMBER]=(json.dumps(settings,indent=2)+'\n').encode()
    ranges=ET.Element('objects');obj=ET.SubElement(ranges,'object',id='1')
    if name=='enclosure-front-top':
        bands=[{'min_z':187.,'max_z':195.,'layer_height':.08,
                'reason':'Retained complete inward/top visible roof rounds.'}]
    else:
        bands=[{'min_z':0.,'max_z':9.4,'layer_height':.24,'wall_loops':6,
                'reason':'Retained additive expanding roof-side transition.'}]
    for band in bands:
        row=ET.SubElement(obj,'range',min_z=f"{band['min_z']:.4f}",max_z=f"{band['max_z']:.4f}")
        for key in ['layer_height','wall_loops']:
            if key in band:ET.SubElement(row,'option',opt_key=key).text=str(band[key])
    members['Metadata/layer_config_ranges.xml']=ET.tostring(ranges,encoding='utf-8',xml_declaration=True)
    # Exact triangles of the retained outside roof-side show transition are
    # blocked. Interior flat hardware seats retain the shared tree supports.
    import numpy as np
    member=preparation['parts'][0]['member'];raw=members[member]
    vp=rb'<vertex x="([^"]+)" y="([^"]+)" z="([^"]+)"\s*/>'
    tp=rb'<triangle v1="(\d+)" v2="(\d+)" v3="(\d+)"\s*/>'
    vertices=np.fromiter((float(v) for m in re.finditer(vp,raw) for v in m.groups()),dtype=float).reshape(-1,3)
    faces=np.fromiter((int(v) for m in re.finditer(tp,raw) for v in m.groups()),dtype=int).reshape(-1,3)
    cad=vertices+preparation['parts'][0]['source_center_mm'];tri=cad[faces]
    selected=((tri[:,:,0].max(axis=1)<=-100)|(tri[:,:,0].min(axis=1)>=100))&(tri[:,:,2].min(axis=1)>=345.69)
    assert selected.any();painted=int(selected.sum());flags=iter(selected)
    def paint(m):return m.group(0).replace(b'/>',b'paint_supports="8" />') if next(flags) else m.group(0)
    members[member]=re.sub(tp,paint,raw)
    assert members[member].replace(b'paint_supports="8" ',b'')==raw
    writer.archive_write(project,members)
    return bands,painted

def paths(gcode):
    # Bounds include half of the emitted bead width, including short support
    # bodies. Startup purge and travel are excluded from model-path readings.
    import re,math
    xyz={'X':0.,'Y':0.,'Z':0.,'E':0.};relative_e=True;feature='';width=.42
    counts={};bounds={};layers=set();heights=[]
    words=re.compile(r'([XYZE])([-+]?(?:\d*\.\d+|\d+))')
    for line in gcode.splitlines():
        if line.startswith('; FEATURE:'):feature=line.split(':',1)[1].strip()
        if line.startswith('; LINE_WIDTH:'):width=float(line.split(':',1)[1])
        if line.startswith('; Z_HEIGHT:'):layers.add(float(line.split(':',1)[1]))
        if line.startswith('; LAYER_HEIGHT:'):heights.append(float(line.split(':',1)[1]))
        command=line.split(';',1)[0].strip()
        if command=='M83':relative_e=True
        if command=='M82':relative_e=False
        fields={a:float(v) for a,v in words.findall(command)}
        if command.startswith('G92'):
            xyz.update(fields);continue
        if not command.startswith(('G0 ','G1 ')):continue
        end={k:fields.get(k,xyz[k]) for k in xyz}
        deposited=fields.get('E',0)>0 if relative_e else end['E']>xyz['E']+1e-8
        if deposited and feature and math.hypot(end['X']-xyz['X'],end['Y']-xyz['Y'])>1e-7:
            lo=[min(xyz['X'],end['X'])-width/2,min(xyz['Y'],end['Y'])-width/2,end['Z']]
            hi=[max(xyz['X'],end['X'])+width/2,max(xyz['Y'],end['Y'])+width/2,end['Z']]
            if feature not in bounds:bounds[feature]=[lo,hi]
            else:
                bounds[feature]=[[min(a,b) for a,b in zip(bounds[feature][0],lo)],
                                 [max(a,b) for a,b in zip(bounds[feature][1],hi)]]
            counts[feature]=counts.get(feature,0)+1
        xyz.update({k:v for k,v in fields.items() if k!='E' or not relative_e})
    return {'extrusion_segments_by_feature':counts,'deposited_bead_bounds_mm':bounds,
            'model_layer_count':len(layers),'layer_heights_mm':sorted(set(heights))}

def bed_overlap(gcode):
    """Measure the real XY deposited areas of the first two model layers."""
    from shapely.geometry import LineString
    from shapely.ops import unary_union
    import math
    xyz={'X':0.,'Y':0.,'Z':0.,'E':0.};relative_e=True;feature='';width=.42;z=None
    words=re.compile(r'([XYZE])([-+]?(?:\d*\.\d+|\d+))');layers={}
    for line in gcode.splitlines():
        if line.startswith('; FEATURE:'):feature=line.split(':',1)[1].strip()
        if line.startswith('; LINE_WIDTH:'):width=float(line.split(':',1)[1])
        if line.startswith('; Z_HEIGHT:'):z=float(line.split(':',1)[1])
        command=line.split(';',1)[0].strip()
        if command=='M83':relative_e=True
        if command=='M82':relative_e=False
        fields={a:float(v) for a,v in words.findall(command)}
        if command.startswith('G92'):xyz.update(fields);continue
        if not command.startswith(('G0 ','G1 ')):continue
        end={k:fields.get(k,xyz[k]) for k in xyz}
        deposited=fields.get('E',0)>0 if relative_e else end['E']>xyz['E']+1e-8
        model=feature in ['Outer wall','Inner wall','Bottom surface','Internal solid infill','Top surface','Sparse infill','Bridge','Internal Bridge']
        if deposited and model and z is not None and math.hypot(end['X']-xyz['X'],end['Y']-xyz['Y'])>1e-7:
            if z not in layers and len(layers)>=2:break
            layers.setdefault(z,[]).append(LineString([(xyz['X'],xyz['Y']),(end['X'],end['Y'])]).buffer(width/2,cap_style=1))
        xyz.update({k:v for k,v in fields.items() if k!='E' or not relative_e})
    assert len(layers)==2,'Two model layers required'
    heights=sorted(layers);first,second=[unary_union(layers[h]) for h in heights]
    overlap=first.intersection(second).area
    return {'model_z_mm':heights,'first_deposited_area_mm2':first.area,
            'second_deposited_area_mm2':second.area,'overlapping_deposited_area_mm2':overlap,
            'second_deposited_area_on_first_percent':100*overlap/second.area,
            'scope':'XY bead-width union of actual straight model extrusion paths. Does not qualify adhesion or supported higher layers.'}

def main(names):
    allparts=selected_parts(); records=[]
    for name in names or allparts:
        rec,angle,recipe=allparts[name]
        source=ROOT/rec['brep'];digest=sha(source)
        policy_digest=sha(__file__)
        directory=CACHE/(name+'-'+digest[:12]+'-'+policy_digest[:8]);directory.mkdir(parents=True,exist_ok=True)
        mesh=directory/(name+'.stl')
        if not mesh.exists():cq.exporters.export(cq.Shape.importBrep(str(source)),str(mesh),tolerance=.06,angularTolerance=.1)
        surface_review=review_mesh(mesh)
        profile=ROOT/('hardware/printed-parts/petgf.3mf' if recipe=='petgf' else 'hardware/printed-parts/zone-c/funnel-mold/funnel-mold.3mf')
        project=directory/(name+'-input.3mf')
        refresh=writer.refresh;void_validation=None
        if name=='enclosure-front-top':
            # Same process-local predicate specialization as the production
            # enclosure support-bottom-gap preparer; shared writer stays intact.
            import inspect
            original=inspect.getsource(writer.refresh);predicate='mesh.body_count != 1'
            assert original.count(predicate)==1
            def accepted_front(mesh,source_path):
                nonlocal void_validation
                void_validation=front_void_review(mesh,source)
                return True
            scoped=original.replace(predicate,'not accepted_front(mesh, source_path)')
            namespace=dict(writer.refresh.__globals__);namespace['accepted_front']=accepted_front
            exec(compile(scoped,str(Path(__file__)),'exec'),namespace);refresh=namespace['refresh']
        preparation=refresh(profile,project,parts=((name,mesh,angle),),offsets=((0.,0.),),
                            title=name+' native study review',plate_border=15.)
        if void_validation:
            preparation['closed_cavity_validation']=void_validation
            preparation['parts'][0].update(positive_material_body_count=1,connected_closed_shell_components=2)
        bands,painted=prepare_policy(project,preparation,name)
        ready=directory/'slice';ready.mkdir(exist_ok=True)
        archive=ready/(name+'.gcode.3mf')
        command=['/Applications/BambuStudio.app/Contents/MacOS/BambuStudio','--slice','0','--arrange','0','--orient','0',
                 '--outputdir',str(ready),'--export-3mf',archive.name,str(project)]
        if not archive.exists():
            with (ready/'slice.log').open('w') as log:
                proc=subprocess.run(command,stdout=log,stderr=subprocess.STDOUT,cwd=ready)
            if proc.returncode:raise RuntimeError(f'{name} native slicer exit{proc.returncode}; see{ready}/slice.log')
        result=json.loads((ready/'result.json').read_text())
        assert result['return_code']==0
        with zipfile.ZipFile(archive) as z:
            assert z.testzip() is None
            raw=z.read('Metadata/plate_1.gcode')
            assert hashlib.md5(raw).hexdigest()==z.read('Metadata/plate_1.gcode.md5').decode().strip().lower()
            settings=json.loads(z.read(writer.SETTINGS_MEMBER))
            preview=HERE/(name+'-slice.png');preview.write_bytes(z.read('Metadata/plate_1.png'))
        native={'part':name,'brep':str(source.relative_to(ROOT)),'brep_sha256':digest,
                'stl_sha256':sha(mesh),'project_sha256':sha(project),'archive_sha256':sha(archive),
                'gcode_sha256':hashlib.sha256(raw).hexdigest(),'recipe':str(profile.relative_to(ROOT)),
                'recipe_sha256':sha(profile),'rotation_x_deg':angle,'slice_return_code':result['return_code'],
                'review_source_sha256':policy_digest,'layer_ranges_mm':bands,'show_transition_blocked_triangles':painted,
                'mesh_surface_review':surface_review,
                'closed_cavity_validation':void_validation,
                'warnings':[p['warning_message'] for p in result['sliced_plates'] if p['warning_message']],
                'embedded_native_mesh':preparation['parts'][0],
                'selected_recipe':{k:settings.get(k) for k in ['layer_height','initial_layer_print_height','wall_loops',
                'sparse_infill_pattern','sparse_infill_density','support_type','support_style','support_top_z_distance',
                'support_bottom_z_distance','support_object_xy_distance']},**paths(raw.decode()),
                'first_second_model_layer_overlap':bed_overlap(raw.decode()),
                'scope':'Native slice and emitted deposition. No printer submission. Physical fit, support-removal effort, load capacity and life remain unqualified.'}
        (HERE/(name+'-slice.json')).write_text(json.dumps(native,indent=2)+'\n')
        records.append({'part':name,'slice':native['slice_return_code'],'warnings':native['warnings'],
                        'layers':native['model_layer_count']})
        print(json.dumps(records[-1]),flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('names',nargs='*');main(p.parse_args().names)
