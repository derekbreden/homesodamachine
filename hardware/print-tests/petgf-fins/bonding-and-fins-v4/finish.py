"""Apply named local fan/first-bridge extrusion treatments, then read the paths."""
from pathlib import Path
import hashlib
import json
import math
import re
import sys
import zipfile
import xml.etree.ElementTree as ET

import numpy as np
from shapely.geometry import LineString, Point
from shapely.ops import unary_union

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent))
from review import segments
sys.path.insert(0,str(HERE.parents[3]/'tools'))
from bambu_print_archive import package

WORDS=re.compile(r'([A-Z])\s*(-?(?:\d*\.\d+|\d+\.?\d*))')


def transform(raw, spec):
    lookup={p['identify_id']:p for p in spec['parts']}
    obj=None;feature='';z=None;fan=0.;relative=True;out=[];changed={};fan_changes=0;extra_e=0.
    for rawline in raw.decode().splitlines(keepends=True):
        line=rawline
        if line.startswith(';'):
            s=line[1:].strip()
            if s.startswith('Z_HEIGHT:'):z=float(s.split(':',1)[1])
            elif s.startswith('FEATURE:'):feature=s.split(':',1)[1].strip()
            elif s.startswith('OBJECT_ID:'):obj=int(s.split(':',1)[1])
            elif s.startswith('start printing object, unique label id:'):obj=int(s.rsplit(':',1)[1])
            elif s.startswith('stop printing object'):obj=None
        else:
            code=line.split(';',1)[0].strip()
            cmd=code.split()[0] if code else ''
            words={k:float(v) for k,v in WORDS.findall(code[len(cmd):])}
            if cmd=='M106' and words.get('P',1)==1:fan=words.get('S',255)
            elif cmd in ('M83','M82'):relative=cmd=='M83'
            if cmd in ('G1','G2','G3') and words.get('E',0)>0 and ('X' in words or 'Y' in words) and obj in lookup and z is not None:
                part=lookup[obj]
                desired=0 if z<=.68001 else part['fan_percent']*2.55
                if abs(fan-desired)>.01:
                    out.append(f'; diagnostic part cooling {part["id"]}\nM106 P1 S{desired:.5f}\n')
                    fan=desired;fan_changes+=1
                multiplier=part.get('bridge_extrusion_multiplier',1.)
                if feature=='Bridge' and abs(z-part.get('first_roof_z_mm',-1))<.0001:
                    if not relative:raise ValueError('Relative E is required for this local treatment')
                    if multiplier!=1:
                        value=words['E']*multiplier
                        line=re.sub(r'\bE-?(?:\d*\.\d+|\d+\.?\d*)',f'E{value:.7f}',line,count=1)
                        extra_e+=value-words['E']
                    changed[part['id']]=changed.get(part['id'],0)+1
        out.append(line)
    return ''.join(out).encode(),{'first_roof_bridge_fill_commands':changed,
        'fan_insertions':fan_changes,'added_filament_mm':extra_e,
        'estimated_added_grams':extra_e*math.pi*(1.75/2)**2*1.43/1000}


def footprint(paths):
    return unary_union([LineString([p['a'][:2],p['b'][:2]]).buffer(p['width']/2) for p in paths])


def local(p,part):
    tr=np.array(part['plate_translation_mm'])
    q={**p,'a':p['a']-tr,'b':p['b']-tr}
    if part.get('bridge_axis')=='Y':
        for k in ('a','b'):q[k]=np.array([q[k][1],-q[k][0],q[k][2]])
    return q


def inspect(raw,spec):
    paths=segments(raw.decode());rows=[]
    lo=np.full(2,np.inf);hi=np.full(2,-np.inf)
    for p in paths:
        xy=np.asarray([p['a'][:2],p['b'][:2]])
        lo=np.minimum(lo,xy.min(axis=0)-p['width']/2);hi=np.maximum(hi,xy.max(axis=0)+p['width']/2)
    for part in spec['parts']:
        own=[local(p,part) for p in paths if p['object']==part['identify_id']]
        row={'id':part['id'],'maximum_nozzle_z_mm':max(p['z'] for p in own),
             'fan_percent_on_model_after_first_three_layers':sorted({round(p['fan']/2.55,3) for p in own if p['z']>.68001})}
        if 'first_roof_z_mm' in part:
            bottom=part['roof_bottom_z_mm'];first=part['first_roof_z_mm'];bounds=part['roof_bounds_mm']
            previous=[p for p in own if abs(p['z']-bottom)<.0001]
            below=footprint(previous)
            roof=[p for p in own if abs(p['z']-first)<.0001 and bounds[0][0]-.01<=(p['a'][0]+p['b'][0])/2<=bounds[1][0]+.01
                  and -.01<=(p['a'][1]+p['b'][1])/2<=12.01]
            raster=[p for p in roof if p['feature']=='Bridge' and abs(p['a'][1]-p['b'][1])<.005
                    and min(p['a'][0],p['b'][0])<3.1 and max(p['a'][0],p['b'][0])>14.9]
            first_fill=min((p['line'] for p in raster),default=None)
            wall=[p for p in roof if p['feature'].endswith('wall')]
            wall_first=min((p['line'] for p in wall),default=None)
            both=[];terminals=[]
            for p in raster:
                ends=sorted([p['a'][:2],p['b'][:2]],key=lambda a:a[0])
                both.append([Point(end).distance(below) for end in ends])
                probes=[LineString([ends[0],ends[0]+np.array([.25,0])]),
                        LineString([ends[1]-np.array([.25,0]),ends[1]])]
                terminals.append([probe.difference(below).length for probe in probes])
            ys=sorted({round((p['a'][1]+p['b'][1])/2,5) for p in raster})
            row.update(first_roof_nozzle_z_mm=first,first_roof_features_in_order=list(dict.fromkeys(p['feature'] for p in roof)),
                first_roof_extrusion_line=roof[0]['line'] if roof else None,
                first_main_bridge_line=first_fill,first_roof_wall_line=wall_first,
                bridge_fill_precedes_walls=(first_fill is not None and wall_first is not None and first_fill<wall_first),
                bridge_raster_count=len(raster),raster_y_mm=ys,
                raster_pitch_mm=sorted({round(b-a,5) for a,b in zip(ys,ys[1:])}),
                nozzle_extrusion_height_mm=sorted({p['height'] for p in raster}),
                bridge_speed_mm_s=sorted({p['speed'] for p in raster}),
                bridge_end_center_distances_to_previous_beads_mm=both,
                maximum_endpoint_center_distance_mm=max((d for pair in both for d in pair),default=None),
                maximum_missing_terminal_025mm_mm=max((d for pair in terminals for d in pair),default=None),
                bridge_rasters_with_both_end_centers_on_previous_beads=sum(max(pair)<.001 for pair in both))
        rows.append(row)
    return {'model_bead_bounds_mm':[lo.tolist(),hi.tolist()],
        'minimum_model_bead_edge_inset_mm':min(lo[0],lo[1],325-hi[0],320-hi[1]),
        'support_extrusion_segments':sum(p['feature'].startswith('Support') for p in paths),
        'trim_commands':re.findall(r'^\s*G29\.1[^\n]*',raw.decode(),re.M),
        'specimens':rows,'limits':'Commanded paths and nominal previous-bead coverage; physical formation, fusion, release and finish remain unmeasured.'}


def main():
    folder=HERE/sys.argv[1].lower()
    project=next(p for p in folder.glob('*.3mf') if '.gcode.' not in p.name)
    stem=project.stem;spec=json.loads((folder/f'{stem}.print.json').read_text())
    source=folder/'native.gcode.3mf'
    with zipfile.ZipFile(source) as z:data={k:z.read(k) for k in z.namelist()}
    raw=data['Metadata/plate_1.gcode'];final,edits=transform(raw,spec)
    data['Metadata/plate_1.gcode']=final
    data['Metadata/plate_1.gcode.md5']=hashlib.md5(final).hexdigest().encode()
    output=folder/f'{stem}.gcode.3mf'
    with zipfile.ZipFile(output,'w',zipfile.ZIP_DEFLATED) as z:
        for k,v in data.items():z.writestr(k,v)
    report=inspect(final,spec)
    plate=ET.fromstring(data['Metadata/slice_info.config']).find('plate')
    meta={p.attrib['key']:p.attrib['value'] for p in plate.findall('metadata')}
    report.update(source_native_archive=source.name,source_native_sha256=sha(source),
        source_gcode_sha256=hashlib.sha256(raw).hexdigest(),archive=output.name,archive_sha256=sha(output),
        gcode_sha256=hashlib.sha256(final).hexdigest(),treatments=edits,
        estimated_seconds=int(meta['prediction']),native_estimated_grams=float(meta['weight']),
        emitted_gcode_md5=hashlib.md5(final).hexdigest())
    (folder/'review.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({'printer':spec['printer'],'seconds':report['estimated_seconds'],'grams':report['native_estimated_grams'],
        'inset_mm':report['minimum_model_bead_edge_inset_mm'],'trim':report['trim_commands'],
        'rows':[{k:r[k] for k in ('id','fan_percent_on_model_after_first_three_layers','bridge_raster_count',
            'bridge_fill_precedes_walls','maximum_endpoint_center_distance_mm','maximum_missing_terminal_025mm_mm') if k in r} for r in report['specimens']]}))


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


if __name__=='__main__':main()
