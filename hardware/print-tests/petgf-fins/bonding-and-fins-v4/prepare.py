"""Prepare two small, explicit PET-GF experiments. Manual use; no print send."""
from pathlib import Path
import hashlib
import importlib.util
import json
import math
import sys
import uuid
import xml.etree.ElementTree as ET
import zipfile

import cadquery as cq
import numpy as np
import trimesh

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
sys.path.insert(0, str(HERE.parent))
from build import block, label, FIRST, LAYER, PROFILE
sys.path.insert(0, str(ROOT / 'tools/funnel-mold-print'))
from profiles import PROD, REL, mesh_object, metadata, qn, trimmed_start_gcode

SPAN = 12.
DEPTH = 12.
TOOTH_UNDERLAP = 2.
BODY_GAP = .24
FIN_ROOF = FIRST + 66 * LAYER  # 16.04; ramps finish before this roof starts.
# Pair the roof's approximately 0.376 mm raster pitch with distinct 0.64 mm
# teeth. Actual previous-layer bead coverage is reviewed after slicing.
PAIRED_TEETH = [(.4, .8)] + [(.923 + (2*i+.5)*.376074074, .64) for i in range(14)] + [(11.6, .8)]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def model_post(x, height, foot_label=None):
    p = block(3, DEPTH, height, (x, 0, 0))
    p = p.union(block(3, DEPTH+10, FIRST+2*LAYER, (x, -9, 0)))
    if foot_label:
        p = p.union(label(foot_label, 2.25, (x+1.5, -4.5, FIRST+2*LAYER)))
    return p


def control(name, z, thickness=LAYER):
    p = model_post(0, z, name).union(model_post(15, z))
    p = p.union(block(18, DEPTH, thickness, (0, 0, z))).clean()
    return p, {'kind': 'solid_bridge', 'clear_span_mm': SPAN,
               'roof_bottom_z_mm': z, 'first_roof_z_mm': z+LAYER,
               'roof_thickness_mm': thickness, 'roof_bounds_mm': [[0,0,z],[18,DEPTH,z+thickness]],
               'bridge_axis': 'X', 'clear_interval_mm': [3,15]}


def fin(name, two=False, rotate=False):
    z = FIN_ROOF
    width = 3+SPAN+TOOTH_UNDERLAP
    roof = block(width, DEPTH, 5*LAYER, (0,0,z))
    right_x = width+BODY_GAP
    right = block(1, DEPTH, z+6*LAYER, (right_x,0,0))
    right = right.union(block(3.2, DEPTH+2, FIRST+2*LAYER, (right_x,-1,0)))
    for y,w in PAIRED_TEETH:
        right = right.union(block(TOOTH_UNDERLAP+BODY_GAP+.02,w,LAYER,
                                  (3+SPAN,y-w/2,z-LAYER)))
    # Side tines attach later roof layers; their clearance remains lateral.
    for zz in (z+2*LAYER,z+4*LAYER):
        for y in (2.,6.,10.):
            right = right.union(block(BODY_GAP+.03,.5,LAYER,(width-.01,y-.25,zz)))
    if two:
        # Replace the left post with a mirrored fin. Its tooth tips end at X3,
        # preserving exactly 12 mm of clear air between the two tip planes.
        left = right.mirror('YZ').translate((width+1,0,0))
        left = left.union(block(3.2,DEPTH+10,FIRST+2*LAYER,(-3.44,-9,0)))
        left = left.union(label(name,2.25,(-1.84,-4.5,FIRST+2*LAYER)))
        # Roof extends only to the same 2 mm overlap on the left.
        roof = block(SPAN+2*TOOTH_UNDERLAP,DEPTH,5*LAYER,(1,0,z))
    else:
        left = model_post(0,z,name)
    part=left.union(right).union(roof).clean()
    detail={'kind':'fin_bridge','two_fins':two,'clear_span_mm':SPAN,
            'roof_bottom_z_mm':z,'first_roof_z_mm':z+LAYER,
            'roof_thickness_mm':5*LAYER,'bridge_axis':'X',
            'roof_bounds_mm':[[1 if two else 0,0,z],[width,DEPTH,z+5*LAYER]],
            'clear_interval_mm':[3,15], 'tooth_underlap_mm':TOOTH_UNDERLAP,
            'body_gap_mm':BODY_GAP,'lower_teeth_per_fin':len(PAIRED_TEETH),
            'teeth_center_width_mm':PAIRED_TEETH}
    if rotate:
        part=part.rotate((0,0,0),(0,0,1),90)
        detail['bridge_axis']='Y'
        detail['rotation_degrees']=90
    return part,detail


def ramp(name, angle):
    start, reach, bottom, thick = 4.,14.,FIRST+4*LAYER,2.4
    tangent=math.tan(math.radians(angle))
    p=cq.Workplane('XZ').polyline([(start-.1,bottom-.1*tangent),
        (start+reach,bottom+reach*tangent),(start+reach,bottom+reach*tangent+thick),
        (start-.1,bottom+thick-.1*tangent)]).close().extrude(-DEPTH)
    p=p.union(block(start,DEPTH,bottom+thick))
    p=p.union(block(5,DEPTH+10,FIRST+2*LAYER,(0,-9,0)))
    p=p.union(label(name,2.25,(2.5,-4.5,FIRST+2*LAYER))).clean()
    return p,{'kind':'ramp','angle_from_bed_degrees':angle,
              'horizontal_reach_mm':reach,'underside_start_z_mm':bottom}


def settings_for(printer):
    with zipfile.ZipFile(PROFILE) as z:
        settings=json.loads(z.read('Metadata/project_settings.config'))
        data={k:z.read(k) for k in ('[Content_Types].xml','Metadata/filament_settings_1.config')}
    trim=.18 if printer=='Mark1' else .04
    color='#000000' if printer=='Mark1' else '#161616'
    original=dict(settings)
    changes={'enable_support':'0','brim_type':'no_brim','skirt_loops':'0',
        'filament_colour':[color],'filament_multi_colour':[color],'filament_density':['1.43'],
        'filament_map_mode':'Manual','filament_map':['1'],'filament_map_2':['1'],
        'filament_nozzle_map':['0'],'filament_volume_map':['0'],
        'extruder_ams_count':['1#0|4#0','1#0|4#0'],
        'fan_min_speed':['70'],'fan_max_speed':['70'],'overhang_fan_speed':['70'],
        'full_fan_speed_layer':['4'],'close_fan_the_first_x_layers':['3'],
        'first_x_layer_fan_speed':['0'],'first_x_layer_part_fan_speed':['0'],
        'bridge_flow':'1','is_infill_first':'1',
        'printer_settings_id':f'Bambu Lab H2C 0.4 Standard +{trim:.2f} Z trim',
        'print_settings_id':f'PET-GF bridge bonding and fin landing {printer}'}
    if printer=='Mark1':
        changes['machine_start_gcode']=trimmed_start_gcode(settings['machine_start_gcode'],trim)
    settings.update(changes)
    filament=json.loads(data['Metadata/filament_settings_1.config'])
    for k,v in changes.items():
        if k in filament or k.startswith('fan_') or k in ('overhang_fan_speed','full_fan_speed_layer',
                'close_fan_the_first_x_layers','first_x_layer_fan_speed','first_x_layer_part_fan_speed'):
            filament[k]=v
    data['Metadata/project_settings.config']=json.dumps(settings,indent=2).encode()
    data['Metadata/filament_settings_1.config']=json.dumps(filament,indent=2).encode()
    return settings,data,{k:{'profile':original.get(k),'plate':v} for k,v in changes.items()
                          if original.get(k)!=v}


def write_plate(printer, groups, *, destination=None, stem=None):
    trim='018' if printer=='Mark1' else '004'
    stem=stem or f'2026-10-14-v4-{"bonding" if printer=="Mark1" else "fins-ramps"}-petgf-left04-z{trim}-{printer.lower()}'
    folder=(destination or HERE)/printer.lower();(folder/'parts').mkdir(parents=True,exist_ok=True)
    settings,data,edits=settings_for(printer)
    model=ET.Element(qn('model'),unit='millimeter',requiredextensions='p',
        **{'xmlns:BambuStudio':'http://schemas.bambulab.com/package/2021'})
    for k,v in (('Application','BambuStudio-02.08.02.61'),('BambuStudio:3mfVersion','1'),('Title',stem)):
        ET.SubElement(model,qn('metadata'),name=k).text=v
    resources=ET.SubElement(model,qn('resources'))
    build=ET.SubElement(model,qn('build'),**{f'{{{PROD}}}UUID':str(uuid.uuid4())})
    config=ET.Element('config');plate=ET.SubElement(config,'plate')
    for k,v in {'plater_id':1,'plater_name':stem,'locked':'false','filament_map_mode':'Manual',
                'filament_maps':'1','filament_volume_maps':'0','bed_type':'Textured PEI Plate'}.items():metadata(plate,k,v)
    rels=ET.Element(f'{{{REL}}}Relationships');records=[]
    for cy,items in groups:
        mesh_items=[]
        for name,shape,detail in items:
            path=folder/'parts'/f'{name}.stl'
            cq.exporters.export(shape,str(path),tolerance=.015,angularTolerance=.12)
            mesh=trimesh.load(path,force='mesh',process=True)
            mesh_items.append((name,shape,detail,path,mesh))
        cursor=162.5-(sum(m.extents[0] for *_,m in mesh_items)+4*(len(mesh_items)-1))/2
        for name,shape,detail,path,mesh in mesh_items:
            center=mesh.bounds.mean(axis=0);cx=cursor+mesh.extents[0]/2
            trans=np.array([cx,cy,center[2]])-center;n=len(records)+1;pid,oid=str(2*n-1),str(2*n)
            subpath=f'/3D/Objects/object_{n}.model';sub=ET.Element(qn('model'),unit='millimeter')
            mesh_object(ET.SubElement(sub,qn('resources')),pid,mesh,center)
            data[subpath.lstrip('/')]=ET.tostring(sub,encoding='UTF-8',xml_declaration=True)
            obj=ET.SubElement(resources,qn('object'),id=oid,type='model',**{f'{{{PROD}}}UUID':str(uuid.uuid4())})
            ET.SubElement(ET.SubElement(obj,qn('components')),qn('component'),objectid=pid,
                transform='1 0 0 0 1 0 0 0 1 0 0 0',**{f'{{{PROD}}}path':subpath,f'{{{PROD}}}UUID':str(uuid.uuid4())})
            ET.SubElement(build,qn('item'),objectid=oid,printable='1',
                transform=f'1 0 0 0 1 0 0 0 1 {cx:.9f} {cy:.9f} {center[2]:.9f}')
            ET.SubElement(rels,f'{{{REL}}}Relationship',Target=subpath,Id=f'rel-{n}',Type='http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel')
            cfg=ET.SubElement(config,'object',id=oid)
            for k,v in {'name':name,'extruder':1,'is_infill_first':1,
                        'bridge_angle':90 if detail.get('bridge_axis')=='Y' else 180,
                        'thick_bridges':int(detail.get('thick_bridges',False))}.items():metadata(cfg,k,v)
            ET.SubElement(cfg,'metadata',face_count=str(len(mesh.faces)))
            part=ET.SubElement(cfg,'part',id=pid,subtype='normal_part')
            for k,v in {'name':path.name,'matrix':'1 0 0 0 0 1 0 0 0 0 1 0 0 0 0 1',
                'source_file':path.name,'source_object_id':0,'source_volume_id':0,
                'source_offset_x':center[0],'source_offset_y':center[1],'source_offset_z':center[2]}.items():metadata(part,k,v)
            inst=ET.SubElement(plate,'model_instance')
            for k,v in {'object_id':oid,'instance_id':0,'identify_id':7100+n}.items():metadata(inst,k,v)
            records.append({'id':name,'identify_id':7100+n,'object_id':int(oid),
                'plate_translation_mm':trans.tolist(),'plate_bounds_mm':(mesh.bounds+trans).tolist(),
                'mesh':str(path.relative_to(folder)),'mesh_sha256':sha(path),
                'cad_valid':shape.val().isValid(),'mesh_watertight':bool(mesh.is_watertight),
                'mesh_bodies':mesh.body_count,**detail})
            cursor+=mesh.extents[0]+4
    package=ET.Element(f'{{{REL}}}Relationships')
    ET.SubElement(package,f'{{{REL}}}Relationship',Target='/3D/3dmodel.model',Id='rel-1',Type='http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel')
    for path,element in (('3D/3dmodel.model',model),('Metadata/model_settings.config',config),
                        ('3D/_rels/3dmodel.model.rels',rels),('_rels/.rels',package)):
        data[path]=ET.tostring(element,encoding='UTF-8',xml_declaration=True).replace(b'ns0:',b'').replace(b'xmlns:ns0=',b'xmlns=')
    project=folder/f'{stem}.3mf'
    with zipfile.ZipFile(project,'w',zipfile.ZIP_DEFLATED) as z:
        for k,v in data.items():z.writestr(k,v)
    report={'project':project.name,'printer':printer,'material':'Polymaker Fiberon PET-GF15',
        'source_profile':str(PROFILE.relative_to(ROOT)),'source_profile_sha256':sha(PROFILE),
        'project_sha256':sha(project),'settings_edits':edits,'requested_z_trim_mm':.18 if printer=='Mark1' else .04,
        'expected_emitted_z_trim_mm':.16 if printer=='Mark1' else .02,'parts':records,'submitted':False}
    (folder/f'{stem}.print.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({'project':str(project),'parts':len(records),'invalid':[p['id'] for p in records if not p['cad_valid'] or not p['mesh_watertight'] or p['mesh_bodies']!=1]}),flush=True)


def main():
    which=sys.argv[1] if len(sys.argv)>1 else 'both'
    if which in ('Mark1','both'):
        groups=[]
        for thick,cy,prefix in ((False,140,'N'),(True,166,'T')):
            items=[]
            for flow in (100,125,150):
                name=f'{prefix}{flow}';shape,d=control(name,FIRST+22*LAYER)
                d.update(thick_bridges=thick,bridge_extrusion_multiplier=flow/100,fan_percent=70)
                items.append((name,shape,d))
            groups.append((cy,items))
        write_plate('Mark1',groups)
    if which in ('Mark2','both'):
        groups=[]
        for fan,cy in ((70,127),(100,155)):
            items=[]
            for angle in (30,35,40):
                name=f'{angle}F{fan}';shape,d=ramp(name,angle);d['fan_percent']=fan
                items.append((name,shape,d))
            groups.append((cy,items))
        items=[]
        p,d=control('C12',FIN_ROOF,5*LAYER);d.update(fan_percent=70,bridge_extrusion_multiplier=1.5)
        items.append(('C12',p,d))
        for name,two,rotate in (('F12',True,False),('Y12',True,True)):
            p,d=fin(name,two,rotate);d.update(fan_percent=70,bridge_extrusion_multiplier=1.5)
            items.append((name,p,d))
        groups.append((185,items))
        write_plate('Mark2',groups)


if __name__=='__main__':main()
