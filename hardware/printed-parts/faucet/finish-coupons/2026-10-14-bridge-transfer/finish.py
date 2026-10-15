"""Apply local fan/feed treatment and inspect the submitted paths, by hand."""
from collections import Counter
from pathlib import Path
import hashlib
import json
import re
import sys
from zipfile import ZipFile

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p/'tools/bambu_print.py').exists())
sys.path[:0] = [str(ROOT/'hardware/print-tests/petgf-fins'), str(ROOT/'tools'),
                str(ROOT/'hardware/printed-parts/faucet')]
from review import segments
from bambu_print_archive import package
import refresh_print_project as writer

WORD = re.compile(r'([A-Z])([-+]?(?:\d*\.\d+|\d+\.?\d*))')
MODEL = {'Bridge', 'Outer wall', 'Overhang wall', 'Inner wall', 'Internal solid infill',
         'Sparse infill', 'Top surface', 'Bottom surface', 'Gap infill'}


def transform(text, candidate):
    obj, feature, z = None, '', None
    native_fan = emitted_fan = native_feed = emitted_feed = 0.0
    relative = True
    out, counts = [], Counter()
    for raw in text.splitlines(keepends=True):
        if raw.startswith(';'):
            s = raw[1:].strip()
            if s.startswith('Z_HEIGHT:'): z = float(s.split(':', 1)[1])
            elif s.startswith('FEATURE:'): feature = s.split(':', 1)[1].strip()
            elif s.startswith('OBJECT_ID:'): obj = int(s.split(':', 1)[1])
            elif s.startswith('start printing object, unique label id:'): obj = int(s.rsplit(':', 1)[1])
            elif s.startswith('stop printing object'): obj = None
            out.append(raw)
            continue
        code = raw.split(';', 1)[0].strip()
        cmd = code.split(None, 1)[0] if code else ''
        words = {k:float(v) for k,v in WORD.findall(code[len(cmd):])}
        if cmd in ('M83', 'M82'): relative = cmd == 'M83'
        if cmd == 'M106' and words.get('P', 1) == 1:
            native_fan = emitted_fan = words.get('S', 255)
        if cmd in ('G0', 'G1', 'G2', 'G3'):
            native_feed = words.get('F', native_feed)
            if not relative:
                raise ValueError('This experiment requires the reviewed native relative-E mode')
            extrusion = words.get('E', 0)>0 and ('X' in words or 'Y' in words)
            treated = obj == candidate and feature in MODEL and z is not None and z>0.68001
            if extrusion:
                desired_fan = 178.5 if treated else native_fan
                if abs(desired_fan-emitted_fan)>0.001:
                    out.append(f'; faucet comparison: {"B model cooling" if treated else "restore native cooling"}\nM106 P1 S{desired_fan:.5f}\n')
                    emitted_fan = desired_fan
                    counts['fan_commands'] += 1
            desired_feed = min(native_feed, 900.0) if treated and extrusion and feature=='Bridge' else native_feed
            # Preserve every native movement/E word; only F can change on a move.
            if 'F' in words or abs(desired_feed-emitted_feed)>0.001:
                if 'F' in words:
                    raw = re.sub(r'\bF[-+]?(?:\d*\.\d+|\d+\.?\d*)', f'F{desired_feed:.3f}', raw, count=1)
                else:
                    raw = raw.rstrip('\r\n')+f' F{desired_feed:.3f}\n'
                emitted_feed = desired_feed
            if treated and extrusion:
                counts[feature] += 1
        out.append(raw)
    return ''.join(out), dict(counts)


def movement_signature(text):
    result = []
    for line in text.splitlines():
        code = line.split(';', 1)[0].strip()
        cmd = code.split(None, 1)[0] if code else ''
        if cmd in ('G0', 'G1', 'G2', 'G3'):
            result.append((cmd, tuple((k,v) for k,v in WORD.findall(code[len(cmd):]) if k!='F')))
    return result


def main(printer):
    folder = HERE/printer.lower()
    if (folder/'launch.json').exists(): raise ValueError('Preserve the submitted files')
    spec = json.loads((folder/'preparation.json').read_text())
    native = folder/'native.gcode.3mf'
    with ZipFile(native) as z: data = {n:z.read(n) for n in z.namelist()}
    raw = data['Metadata/plate_1.gcode']
    if hashlib.md5(raw).hexdigest() != data['Metadata/plate_1.gcode.md5'].decode().strip().lower():
        raise ValueError('Native G-code checksum mismatch')
    text, edits = transform(raw.decode(), spec['specimens'][1]['identify_id'])
    if movement_signature(raw.decode()) != movement_signature(text):
        raise ValueError('The local treatment changed native movement or extrusion')
    final = text.encode()
    data['Metadata/plate_1.gcode'] = final
    data['Metadata/plate_1.gcode.md5'] = hashlib.md5(final).hexdigest().encode()
    output = (ROOT/spec['project']).with_suffix('.gcode.3mf')
    writer.archive_write(output, data)
    paths = segments(text)
    before = segments(raw.decode())
    rows = []
    for row in spec['specimens']:
        own = [p for p in paths if p['object']==row['identify_id'] and p['feature'] in MODEL]
        native_own = [p for p in before if p['object']==row['identify_id'] and p['feature'] in MODEL]
        if len(own)!=len(native_own): raise ValueError('Model path count changed')
        after_bed = [p for p in own if p['z']>0.68001]
        if row['treatment'] and any(abs(p['fan']-178.5)>0.001 for p in after_bed):
            raise ValueError('Candidate model cooling does not match the treatment')
        if not row['treatment'] and any(a['fan']!=b['fan'] or a['speed']!=b['speed'] for a,b in zip(own,native_own)):
            raise ValueError('Reference fan/feed changed')
        rows.append(dict(id=row['id'], native_bridge_flow=row['native_bridge_flow'],
            model_z_range_mm=[min(p['z'] for p in own), max(p['z'] for p in own)],
            model_fan_after_three_layers_percent=sorted({round(p['fan']/2.55,3) for p in after_bed}),
            bridge_speed_mm_s=sorted({p['speed'] for p in after_bed if p['feature']=='Bridge'}),
            bridge_z_mm=sorted({p['z'] for p in own if p['feature']=='Bridge'}),
            model_features=sorted({p['feature'] for p in own})))
    # Read all deposited model/support/brim moves, including arc extrema and width padding.
    coordinates = np.array([q for p in paths for q in (p['a'][:2], p['b'][:2])])
    padding = max(p['width'] for p in paths)/2+0.1
    low, high = coordinates.min(axis=0)-padding, coordinates.max(axis=0)+padding
    usable = np.array(spec['shared_printable_area_mm'])
    inset = float(min(*(low-usable[0]), *(usable[1]-high)))
    if inset < 80: raise ValueError(f'Beads enter the 80 mm border: {inset}')
    expected_trim = 0.16 if printer=='Mark1' else 0.02
    trims = [float(v) for v in re.findall(r'^\s*G29\.1 Z([-+.\d]+)', text, re.M)]
    if trims != [0.0, expected_trim]: raise ValueError(f'Unexpected Z trim: {trims}')
    if re.search(r'^\s*G39(?:\s|;|$)', text, re.M): raise ValueError('Unexpected probing cycle')
    support_before = [p for p in before if p['feature'].startswith('Support')]
    support_after = [p for p in paths if p['feature'].startswith('Support')]
    if len(support_before)!=len(support_after) or any(a['fan']!=b['fan'] or a['speed']!=b['speed'] for a,b in zip(support_before,support_after)):
        raise ValueError('Support cooling or speed changed')
    report = dict(source_native_sha256=writer.digest(native.read_bytes()),
        submitted_archive=str(output.relative_to(ROOT)), submitted_sha256=writer.digest(output.read_bytes()),
        native_xyz_arc_and_extrusion_words_preserved=True, native_support_fan_and_feed_preserved=True,
        source_gcode_sha256=writer.digest(raw), submitted_gcode_sha256=writer.digest(final),
        full_bead_envelope_mm=[low.tolist(), high.tolist()], minimum_edge_clearance_mm=inset,
        trim_commands_mm=trims, local_treatments=edits, specimens=rows,
        physical_result='Pending; no finish or removal result is established by this path review.')
    (folder/'review.json').write_text(json.dumps(report, indent=2)+'\n')
    print_only = output.with_name(output.name.removesuffix('.gcode.3mf')+'-print-only.gcode.3mf')
    packaging = package(output, print_only)
    (folder/'packaging.json').write_text(json.dumps(packaging, indent=2)+'\n')
    print(json.dumps(report), flush=True)


if __name__=='__main__': main(sys.argv[1])
