"""Verify profile, printed support patterns and model separation for A–D."""
import collections
import hashlib
import io
import json
import math
from pathlib import Path
import re
import sys
import xml.etree.ElementTree as ET
import zipfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0,str(HERE.parent/'petgf-support-interface'))
from audit_gcode import TOKEN, paths, audit


def sha(data): return hashlib.sha256(data).hexdigest()


def trace(text, ceiling):
    position = [0.,0.,0.]
    absolute, e_absolute, last_e = True, False, 0.
    feature, obj, started = '', 0, False
    traces = collections.defaultdict(lambda:collections.defaultdict(lambda:collections.defaultdict(list)))
    for line in text.splitlines():
        if line.startswith('; OBJECT_ID:'): obj = int(line.split(':',1)[1])-2000
        elif line.startswith('; FEATURE:'): feature = line.split(':',1)[1].strip()
        elif line.startswith('; CHANGE_LAYER'): started = True
        code = line.split(';',1)[0].strip()
        if not code: continue
        command = code.split()[0]
        args = {k:float(v) for k,v in TOKEN.findall(code[len(command):])}
        if command == 'G90': absolute = True
        elif command == 'G91': absolute = False
        elif command == 'M82': e_absolute = True
        elif command == 'M83': e_absolute = False
        elif command == 'G92':
            for i,axis in enumerate('XYZ'):
                if axis in args: position[i] = args[axis]
            if 'E' in args: last_e = args['E']
        elif command in ('G0','G1','G2','G3'):
            start = tuple(position)
            for i,axis in enumerate('XYZ'):
                if axis in args: position[i] = args[axis] if absolute else position[i]+args[axis]
            delta = 0.
            if 'E' in args:
                delta = args['E']-last_e if e_absolute else args['E']
                last_e = args['E'] if e_absolute else last_e+args['E']
            if not (started and delta>0 and 1<=obj<=4 and ceiling-1.0<position[2]<ceiling+.5): continue
            if not (feature.startswith('Support') or feature=='Bridge'): continue
            for a,b in paths(start,tuple(position),command,args):
                if math.dist(a,b)>.001:
                    traces[obj][feature][round(position[2],5)].append([*a,*b])
    return traces


def pattern_summary(segments):
    lengths = collections.defaultdict(float)
    for x,y,u,v in segments:
        angle = round(math.degrees(math.atan2(v-y,u-x))%180,1)%180
        lengths[angle] += math.hypot(u-x,v-y)
    return {str(k):round(v,3) for k,v in sorted(lengths.items())}


def main():
    exp = json.loads((HERE/'experiment.json').read_text())
    project = ROOT/exp['project']; out = project.parent
    target = out/'petgf-interface-patterns-mark2.gcode.3mf'
    pcheck = json.loads((out/'pattern-verification.json').read_text())
    result = json.loads((out/'result.json').read_text())
    assert result['return_code']==0
    plate = result['sliced_plates'][0]
    assert not plate['warning_message'] and 45*60<plate['total_predication']<150*60
    with zipfile.ZipFile(ROOT/exp['profile']) as z:
        profile = json.loads(z.read('Metadata/project_settings.config'))
        filament = json.loads(z.read('Metadata/filament_settings_1.config'))
    assert sha((ROOT/exp['profile']).read_bytes())==exp['profile_sha256']
    with zipfile.ZipFile(project) as z:
        prepared = json.loads(z.read('Metadata/project_settings.config'))
        configs = ET.fromstring(z.read('Metadata/model_settings.config')).findall('object')
    overrides = {k:[profile.get(k),prepared.get(k)] for k in set(profile)|set(prepared) if profile.get(k)!=prepared.get(k)}
    assert overrides == {'extruder_ams_count':[['1#0|4#1','1#0|4#0'],['1#0|4#0','1#0|4#0']]}
    for cfg,spec in zip(configs,exp['specimens']):
        values={m.attrib['key']:m.attrib['value'] for m in cfg.findall('metadata') if 'key' in m.attrib}
        for key,val in spec['overrides'].items(): assert values[key]==val
    with zipfile.ZipFile(target) as z:
        raw=z.read('Metadata/plate_1.gcode'); text=raw.decode()
        assert hashlib.md5(raw).hexdigest()==z.read('Metadata/plate_1.gcode.md5').decode().lower()
        sliced=json.loads(z.read('Metadata/project_settings.config'))
        assert filament==json.loads(z.read('Metadata/filament_settings_1.config'))
        info=ET.fromstring(z.read('Metadata/slice_info.config'))
    normalization={k:[prepared.get(k),sliced.get(k)] for k in set(prepared)|set(sliced) if prepared.get(k)!=sliced.get(k)}
    assert normalization=={'filament_map_2':[None,['1']],'filament_prime_volume':[['30'],['45']]},normalization
    nozzles=[n.attrib for n in info.findall('.//nozzle')]
    assert nozzles==[{'id':'0','extruder_id':'1','nozzle_diameter':'0.4','volume_type':'Standard'}]
    trims=[s.strip() for s in text.splitlines() if s.lstrip().startswith('G29.1')]
    assert trims==['G29.1 Z0 ; clear z-trim value first','G29.1 Z0.02 ; for Textured PEI Plate']
    assert sha(raw)==pcheck['gcode_sha256'] and sha(target.read_bytes())==pcheck['bundle_sha256']
    regions=json.loads((out/'regions.json').read_text())
    measures=audit(io.StringIO(text),regions)
    with zipfile.ZipFile(out/'native.gcode.3mf') as z:
        native=z.read('Metadata/plate_1.gcode').decode()
    native_measures=audit(io.StringIO(native),regions)
    assert measures==native_measures, 'The pattern edit changed central support or model paths.'
    traced=trace(text,exp['geometry']['ceiling_z'])
    table=[]
    for i,(spec,m) in enumerate(zip(exp['specimens'],measures),1):
        roof_z=min(traced[i]['Bridge'])
        if i==4:
            assert not traced[i]['Support interface']
            top=max(traced[i]['Support'])
        else: top=max(traced[i]['Support interface'])
        gap=round(roof_z-.24-top,5)
        assert gap==.24,(spec['id'],top,roof_z,gap)
        roof_pattern=pattern_summary(traced[i]['Bridge'][roof_z])
        assert set(roof_pattern)<={'0.0','90.0'}
        assert roof_pattern['0.0']/sum(roof_pattern.values())>.98
        contact=traced[i]['Support'][top] if i==4 else traced[i]['Support interface'][top]
        orientations=pattern_summary(contact)
        if i==2: assert set(orientations)=={'0.0','90.0'}
        if i==3: assert set(orientations)=={'90.0'} and len(contact)==pcheck['c_independent_lines']
        if i==4: assert len(contact)>20
        table.append(dict(id=spec['id'],first_roof_z=roof_z,last_support_z=top,planned_gap_mm=gap,
            contact_feature='Support' if i==4 else 'Support interface',
            contact_directions_degrees_and_lengths_mm=orientations,
            roof_directions_degrees_and_lengths_mm=roof_pattern,
            interface_feature_planes=sorted(traced[i]['Support interface']),
            requested_interface_layers=spec['interface_layers'],contact_segment_count=len(contact)))
    report=dict(slicer='BambuStudio 02.08.02.61',source_profile_sha256=exp['profile_sha256'],
        project_sha256=sha(project.read_bytes()),sliced_file=str(target.relative_to(ROOT)),
        sliced_file_sha256=sha(target.read_bytes()),gcode_sha256=sha(raw),gcode_md5=hashlib.md5(raw).hexdigest(),
        settings_overrides=overrides,settings_normalizations=normalization,nozzles=nozzles,
        active_z_trim_commands=trims,estimated_seconds=plate['total_predication'],
        filament_grams_estimate=plate['filaments'][0]['total_used_g'],
        layers=int(re.search(r'; total layer number: (\d+)',text).group(1)),
        slicer_warnings=plate['warning_message'],specimens=table,
        all_central_support_and_model_paths_unchanged=True,
        single_interface_layer_note='B and C include branch-tip paths tagged Support interface one layer below the full contact sheet.',
        pattern_edit=pcheck)
    (HERE/'verification.json').write_text(json.dumps(report,indent=2)+'\n')
    (out/'traces.json').write_text(json.dumps(traced))
    print(json.dumps({k:v for k,v in report.items() if k!='pattern_edit'},indent=2))


if __name__=='__main__': main()
