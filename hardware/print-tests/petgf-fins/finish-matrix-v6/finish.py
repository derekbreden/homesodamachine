"""Apply named E/fan treatments and first-roof speeds to this manual experiment."""
from pathlib import Path
import hashlib
import importlib.util
import json
import math
import re
import zipfile
import xml.etree.ElementTree as ET

HERE = Path(__file__).resolve().parent
loader = importlib.util.spec_from_file_location('v4_treatments', HERE.parent/'bonding-and-fins-v4/finish.py')
v4 = importlib.util.module_from_spec(loader)
loader.loader.exec_module(v4)


def speeds(raw, spec):
    lookup = {p['identify_id']:p for p in spec['parts']}
    obj = None; feature = ''; z = None
    native_feed = None; emitted_feed = None
    out = []; changes = 0
    for line in raw.decode().splitlines(keepends=True):
        if line.startswith(';'):
            s = line[1:].strip()
            if s.startswith('Z_HEIGHT:'): z = float(s.split(':',1)[1])
            elif s.startswith('FEATURE:'): feature = s.split(':',1)[1].strip()
            elif s.startswith('OBJECT_ID:'): obj = int(s.split(':',1)[1])
            elif s.startswith('start printing object, unique label id:'): obj = int(s.rsplit(':',1)[1])
            elif s.startswith('stop printing object'): obj = None
        else:
            code = line.split(';',1)[0].strip()
            cmd = code.split()[0] if code else ''
            words = {k:float(v) for k,v in v4.WORDS.findall(code[len(cmd):])}
            if cmd in ('G0','G1','G2','G3'):
                native_feed = words.get('F', native_feed)
                desired = native_feed
                p = lookup.get(obj, {})
                if (words.get('E',0)>0 and ('X' in words or 'Y' in words)
                    and feature=='Bridge' and z is not None
                    and abs(z-p.get('first_roof_z_mm',-1))<.0001):
                    desired = p['first_bridge_speed_mm_s']*60
                if desired is not None and (desired != emitted_feed or ('F' in words and words['F'] != desired)):
                    if 'F' in words:
                        line = re.sub(r'\bF-?(?:\d*\.\d+|\d+\.?\d*)', f'F{desired:.5f}', line, count=1)
                    else:
                        body, sep, comment = line.rstrip('\r\n').partition(';')
                        line = body.rstrip()+f' F{desired:.5f}'+(' ;'+comment if sep else '')+'\n'
                    changes += 1
                emitted_feed = desired
        out.append(line)
    return ''.join(out).encode(), changes


def main():
    folder = HERE/'mark2'
    project = next(p for p in folder.glob('*.3mf') if '.gcode.' not in p.name)
    spec = json.loads(project.with_suffix('.print.json').read_text())
    source = folder/'native.gcode.3mf'
    with zipfile.ZipFile(source) as archive:
        data = {name:archive.read(name) for name in archive.namelist()}
    native = data['Metadata/plate_1.gcode']
    treated, edits = v4.transform(native, spec)
    final, feed_changes = speeds(treated, spec)
    data['Metadata/plate_1.gcode'] = final
    data['Metadata/plate_1.gcode.md5'] = hashlib.md5(final).hexdigest().encode()
    output = folder/f'{project.stem}.gcode.3mf'
    with zipfile.ZipFile(output,'w',zipfile.ZIP_DEFLATED) as archive:
        for name, body in data.items(): archive.writestr(name,body)
    report = v4.inspect(final,spec)
    meta = {e.attrib['key']:e.attrib['value'] for e in ET.fromstring(data['Metadata/slice_info.config']).find('plate').findall('metadata')}
    a, b = v4.segments(native.decode()), v4.segments(final.decode())
    assert len(a)==len(b)
    lookup = {p['identify_id']:p for p in spec['parts']}
    ideal_time_delta = 0.
    for old,new in zip(a,b):
        assert old['object']==new['object'] and old['feature']==new['feature'] and old['z']==new['z']
        assert all(abs(x-y)<1e-9 for key in ('a','b') for x,y in zip(old[key],new[key]))
        p = lookup[old['object']]
        expected = old['speed']
        if old['feature']=='Bridge' and abs(old['z']-p.get('first_roof_z_mm',-1))<.0001:
            expected = p['first_bridge_speed_mm_s']
            length = math.dist(old['a'],old['b'])
            ideal_time_delta += length/expected-length/old['speed']
        assert abs(new['speed']-expected)<.00001
    report.update(archive=output.name, archive_sha256=v4.sha(output),
        source_native_archive=source.name, source_native_sha256=v4.sha(source),
        source_gcode_sha256=hashlib.sha256(native).hexdigest(),
        gcode_sha256=hashlib.sha256(final).hexdigest(), emitted_gcode_md5=hashlib.md5(final).hexdigest(),
        treatments={**edits, 'feed_word_insertions_or_replacements':feed_changes},
        native_estimated_seconds=int(meta['prediction']), native_estimated_grams=float(meta['weight']),
        ideal_added_bridge_seconds=ideal_time_delta,
        approximate_seconds_including_speed_treatment=int(meta['prediction'])+ideal_time_delta,
        model_xyz_unchanged=True, other_model_extrusion_speeds_unchanged=True)
    ramps = [r for r in report['specimens'] if r['id'].startswith('R')]
    bridge = [r for r in report['specimens'] if not r['id'].startswith('R')]
    report['all_ramps_finish_before_first_bridge'] = max(r['maximum_nozzle_z_mm'] for r in ramps) < min(r['first_roof_nozzle_z_mm'] for r in bridge)
    (folder/'review.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({'specimens':len(spec['parts']), 'native_seconds':report['native_estimated_seconds'],
        'speed_delta_seconds':ideal_time_delta, 'grams':report['native_estimated_grams']+edits['estimated_added_grams'],
        'inset_mm':report['minimum_model_bead_edge_inset_mm'],
        'ramps_finish_first':report['all_ramps_finish_before_first_bridge'],
        'fin_landings':[{k:r[k] for k in ('id','bridge_raster_count','bridge_fill_precedes_walls',
            'maximum_endpoint_center_distance_mm','maximum_missing_terminal_025mm_mm','bridge_speed_mm_s')}
            for r in bridge if r['id'].startswith(('F','Y'))]}))


if __name__ == '__main__':
    main()
