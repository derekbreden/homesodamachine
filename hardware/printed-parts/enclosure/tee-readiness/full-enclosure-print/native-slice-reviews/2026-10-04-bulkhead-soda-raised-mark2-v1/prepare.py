"""Prepare one face-up raised SODA ring for Mark2: blue body right, white letters left.

    tools/cad-venv/bin/python prepare.py snapshot      # geometry from raised_rings.build('carb')
    tools/cad-venv/bin/python prepare.py               # corrected native slice
    tools/cad-venv/bin/python prepare.py --uncorrected # comparison slice

The geometry snapshot fixes the meshes and the commit they came from, so the
plate does not move when the ring generator does.
"""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import xml.etree.ElementTree as ET
import zipfile

import trimesh

HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p/'tools').is_dir())
TRIAL = ROOT/'hardware/printed-parts/enclosure/bulkhead-ring/face-up-trial'
sys.path.insert(0, str(ROOT/'hardware/printed-parts/faucet'))
import refresh_print_project as writer

JOB = ROOT/'.cache/prints/2026-10-04-bulkhead-soda-raised-mark2-v1'
GEOMETRY = JOB/'geometry'
STEM = 'soda-raised-face-up-z004-mark2-v1'
STATION, NAME = 'carb', 'bulkhead-ring-carb-raised'
BASE = ROOT/'hardware/printed-parts/enclosure/nameplate/nameplate-001-petgf.3mf'
PETGF = ROOT/'hardware/printed-parts/petgf.3mf'
REGISTRATION = ROOT/'hardware/printed-parts/calibration/dual-nozzle-registration/mark2-registration.json'
# Filament 1 runs in the left nozzle, filament 2 in the right; colours are the
# external spools Mark2 reports (254 left, 255 right).
COLOURS = ['#FFFFFF', '#46A8F9']
PARTS = (('body', 2), ('lettering', 1))
PLACE = (165., 125.)
NS = 'http://schemas.microsoft.com/3dmanufacturing/core/2015/02'
ET.register_namespace('', NS)
Q = lambda n: '{'+NS+'}'+n
meta = writer.metadata
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def snapshot():
    sys.path.insert(0, str(TRIAL))
    import raised_rings as trial
    ring = trial.ring
    GEOMETRY.mkdir(parents=True, exist_ok=True)
    body, word = [trial.print_pose(s) for s in trial.build(STATION)]
    bounds = body.BoundingBox()
    dy = -(bounds.ymin+bounds.ymax)/2
    parts = {}
    for shape, label in ((body, 'body'), (word, 'lettering')):
        shape = shape.translate((0, dy, 0))
        vertices, faces = shape.tessellate(.015, .05)
        mesh = trimesh.Trimesh(vertices=[v.toTuple() for v in vertices], faces=faces, process=True)
        assert mesh.is_watertight and mesh.is_winding_consistent
        path = GEOMETRY/f'soda-{label}.stl'
        mesh.export(path)
        parts[label] = {'bounds': mesh.bounds.tolist(), 'volume_mm3': float(mesh.volume),
                        'solids': len(shape.Solids()), 'stl_sha256': sha(path)}
    head = subprocess.run(['git', 'rev-parse', 'HEAD'], cwd=ROOT, capture_output=True, text=True).stdout.strip()
    sources = {}
    for path in (Path(trial.__file__), Path(ring.__file__)):
        rel = str(path.relative_to(ROOT))
        blob = subprocess.run(['git', 'show', f'HEAD:{rel}'], cwd=ROOT, capture_output=True).stdout
        sources[rel] = {'working_sha256': sha(path), 'head_sha256': hashlib.sha256(blob).hexdigest()}
        assert sources[rel]['working_sha256'] == sources[rel]['head_sha256'], rel
    flange_r = ring.FAMILIES[ring.family(STATION)].flange_footprint()/2
    _, nominal_word = trial.build(STATION)
    report = {'station': STATION, 'word': ring.STATIONS[STATION].word, 'head': head, 'sources': sources,
              'letter_rise_mm': trial.RISE, 'mounting_thickness_mm': ring.THICK,
              'flange_to_word_band_gap_mm': nominal_word.BoundingBox().zmin - flange_r, 'parts': parts}
    (GEOMETRY/'snapshot.json').write_text(json.dumps(report, indent=2)+'\n')
    return report


def main(uncorrected=False):
    shot = json.loads((GEOMETRY/'snapshot.json').read_text())
    assert shot['word'] == 'SODA' and shot['letter_rise_mm'] == .48
    for label, part in shot['parts'].items():
        assert sha(GEOMETRY/f'soda-{label}.stl') == part['stl_sha256'], label
    job = JOB/'uncorrected' if uncorrected else JOB
    stem = STEM+('-uncorrected' if uncorrected else '')
    job.mkdir(parents=True, exist_ok=True)
    target = job/(stem+'-input.3mf')
    assert not target.exists(), 'Keep print archives immutable.'
    with zipfile.ZipFile(BASE) as z:
        settings = json.loads(z.read('Metadata/project_settings.config'))
        members = {n: z.read(n) for n in z.namelist() if n.startswith('Metadata/filament_settings_')}
    with zipfile.ZipFile(PETGF) as z:
        shared = json.loads(z.read('Metadata/project_settings.config'))
    registration = json.loads(REGISTRATION.read_text())
    assert registration['printer'] == 'Mark2' and registration['status'] == 'nameplate_appearance_accepted'
    # The measured correction belongs to the right nozzle, whatever spool feeds it.
    assert registration['native_extruder_offset'] == ['0x0', '0.5x-0.7']
    correction = {'X': 0., 'Y': 0.} if uncorrected else registration['white_correction_mm']
    settings['extruder_offset'] = ['0x0', f"{-correction['X']:g}x{-correction['Y']:g}"]
    settings.update({k: v for k, v in shared.items() if k.startswith(('support_', 'tree_support_'))
                     or k == 'independent_support_layer_height'})
    assert settings['filament_nozzle_map'] == ['0', '1'] and settings['filament_type'] == ['PET-CF', 'PET-CF']
    settings.update(enable_support='0', brim_type='no_brim', brim_width='0',
                    initial_layer_print_height='0.2', layer_height=shared['layer_height'],
                    flush_into_support='0', filament_colour=COLOURS, filament_multi_colour=COLOURS)
    model = ET.Element(Q('model'), unit='millimeter')
    ET.SubElement(model, Q('metadata'), name='Application').text = 'BambuStudio-02.08.02.61'
    ET.SubElement(model, Q('metadata'), name='BambuStudio:3mfVersion').text = '1'
    resources, build = ET.SubElement(model, Q('resources')), ET.SubElement(model, Q('build'))
    cfg, ranges = ET.Element('config'), ET.Element('objects')
    plate = ET.SubElement(cfg, 'plate')
    for key, value in {'plater_id': 1, 'plater_name': 'SODA raised lettering; Mark2',
                       'locked': 'false', 'bed_type': settings['curr_bed_type'], 'filament_map_mode': 'Manual',
                       'filament_maps': '1 2', 'filament_volume_maps': '0 0'}.items():
        meta(plate, key, value)
    details, children = [], []
    for oid, (label, tool) in enumerate(PARTS, 1):
        mesh = trimesh.load(GEOMETRY/f'soda-{label}.stl', process=True)
        assert mesh.is_watertight and mesh.is_winding_consistent
        obj = ET.SubElement(resources, Q('object'), id=str(oid), type='model')
        geometry = ET.SubElement(obj, Q('mesh'))
        vs, ts = ET.SubElement(geometry, Q('vertices')), ET.SubElement(geometry, Q('triangles'))
        for v in mesh.vertices:
            ET.SubElement(vs, Q('vertex'), **dict(zip('xyz', (f'{p:.8f}' for p in v))))
        for face in mesh.faces:
            ET.SubElement(ts, Q('triangle'), **dict(zip(('v1', 'v2', 'v3'), map(str, face))))
        children.append((oid, label, tool))
        details.append({'station': STATION, 'part': label, 'filament': tool,
                        'colour': COLOURS[tool-1], 'bounds': mesh.bounds.tolist()})
    oid = len(PARTS)+1
    obj = ET.SubElement(resources, Q('object'), id=str(oid), type='model')
    components = ET.SubElement(obj, Q('components'))
    config = ET.SubElement(cfg, 'object', id=str(oid))
    meta(config, 'name', NAME)
    meta(config, 'extruder', 1)
    for child, label, tool in children:
        ET.SubElement(components, Q('component'), objectid=str(child))
        part = ET.SubElement(config, 'part', id=str(child), subtype='normal_part')
        meta(part, 'name', label)
        meta(part, 'extruder', tool)
        meta(part, 'matrix', '1 0 0 0 0 1 0 0 0 0 1 0 0 0 0 1')
    ET.SubElement(build, Q('item'), objectid=str(oid), transform=f'1 0 0 0 1 0 0 0 1 {PLACE[0]} {PLACE[1]} 0', printable='1')
    instance = ET.SubElement(plate, 'model_instance')
    for k, v in {'object_id': oid, 'instance_id': 0, 'identify_id': 2901}.items():
        meta(instance, k, v)
    band_obj = ET.SubElement(ranges, 'object', id='1')
    band = ET.SubElement(band_obj, 'range', min_z='1.88', max_z='2.0')
    ET.SubElement(band, 'option', opt_key='layer_height').text = '0.12'
    members.update({
        '3D/3dmodel.model': writer.xml(model),
        'Metadata/model_settings.config': writer.xml(cfg),
        'Metadata/layer_config_ranges.xml': writer.xml(ranges),
        'Metadata/project_settings.config': json.dumps(settings, indent=2).encode(),
        '_rels/.rels': b'<?xml version="1.0"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel-1" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>',
        '[Content_Types].xml': b'<?xml version="1.0"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/><Default Extension="config" ContentType="application/octet-stream"/></Types>',
    })
    writer.archive_write(target, members)
    sources = [BASE, PETGF, REGISTRATION, Path(__file__)]
    report = {'project': str(target.relative_to(ROOT)), 'project_sha256': sha(target),
              'geometry_snapshot': shot,
              'settings_and_script_sha256': {str(p.relative_to(ROOT)): sha(p) for p in sources},
              'printer': 'Mark2', 'parts': details, 'identify_ids': {'2901': STATION},
              'orientation': 'Face up. Inboard face on the bed; 2.0 mm fitting face, letters standing to 2.48 mm.',
              'nozzles': {'left': 'filament 1, white PET-GF, external 254, lettering',
                          'right': 'filament 2, blue PET-GF, external 255, body'},
              'requested_z_trim_mm': .04, 'support_policy': 'No supports.',
              'calibration_applied': not uncorrected, 'submitted': False,
              'right_nozzle_correction_mm': correction, 'native_extruder_offset': settings['extruder_offset'],
              'correction_scope': 'Right-nozzle paths: the blue body. White lettering and nominal CAD unchanged.'}
    (job/'preparation.json').write_text(json.dumps(report, indent=2)+'\n')
    ready = job/'ready'
    ready.mkdir()
    command = ['/Applications/BambuStudio.app/Contents/MacOS/BambuStudio', '--slice', '0', '--arrange', '0', '--orient', '0',
               '--outputdir', str(ready), '--export-3mf', stem+'.gcode.3mf', str(target)]
    (job/'slice-command.json').write_text(json.dumps(command, indent=2)+'\n')
    with (ready/'bambu-cli.log').open('w') as log:
        rc = subprocess.run(command, cwd=ready, stdout=log, stderr=subprocess.STDOUT).returncode
    print('SLICE_EXIT', rc)
    return rc


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('step', nargs='?', choices=('snapshot', 'slice'), default='slice')
    parser.add_argument('--uncorrected', action='store_true')
    args = parser.parse_args()
    if args.step == 'snapshot':
        print(json.dumps(snapshot(), indent=2))
        raise SystemExit(0)
    raise SystemExit(main(args.uncorrected))
