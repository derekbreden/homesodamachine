"""Prepare face-up rings using Mark2's accepted nameplate appearance correction."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import xml.etree.ElementTree as ET
import zipfile

import trimesh
import raised_rings as trial

HERE, ROOT = trial.HERE, trial.ROOT
sys.path.insert(0, str(ROOT/'hardware/printed-parts/faucet'))
import refresh_print_project as writer

JOB = ROOT/'.cache/prints/2026-09-30-bulkhead-raised-mark2-v2'
STEM = 'tap-flavor-raised-face-up-z004-mark2-v2'
BASE = HERE.parents[1]/'nameplate/nameplate-001-petgf.3mf'
PETGF = ROOT/'hardware/printed-parts/petgf.3mf'
REGISTRATION = ROOT/'hardware/printed-parts/calibration/dual-nozzle-registration/mark2-registration.json'
ACCEPTANCE = ROOT/'hardware/printed-parts/enclosure/tee-readiness/full-enclosure-print/native-slice-reviews/2026-09-29-nameplate-y030-receiver-mark2-v7/physical-result.json'
NS = 'http://schemas.microsoft.com/3dmanufacturing/core/2015/02'
ET.register_namespace('', NS)
Q = lambda n: '{'+NS+'}'+n
meta = writer.metadata
PLATE = (('water', 2, 1, (115., 125.)), ('flavor-a', 1, 2, (165., 125.)), ('flavor-b', 1, 2, (215., 125.)))


def main(uncorrected=False):
    job = JOB/'uncorrected' if uncorrected else JOB
    stem = STEM+('-uncorrected' if uncorrected else '')
    job.mkdir(parents=True, exist_ok=True)
    target = job/(stem+'-input.3mf')
    assert not target.exists(), 'Keep trial archives immutable.'
    with zipfile.ZipFile(BASE) as z:
        settings = json.loads(z.read('Metadata/project_settings.config'))
        members = {n:z.read(n) for n in z.namelist() if n.startswith('Metadata/filament_settings_')}
    with zipfile.ZipFile(PETGF) as z:
        shared = json.loads(z.read('Metadata/project_settings.config'))
    registration = json.loads(REGISTRATION.read_text())
    assert registration['printer']=='Mark2' and registration['status']=='nameplate_appearance_accepted'
    assert json.loads(ACCEPTANCE.read_text())['fit_accepted_for_now']
    correction = {'X':0., 'Y':0.} if uncorrected else registration['white_correction_mm']
    settings['extruder_offset'] = ['0x0',f"{-correction['X']:g}x{-correction['Y']:g}"]
    settings.update({k:v for k,v in shared.items() if k.startswith(('support_', 'tree_support_'))
                     or k=='independent_support_layer_height'})
    assert settings['filament_nozzle_map'] == ['0', '1']
    settings.update(enable_support='0', brim_type='no_brim', brim_width='0',
                    initial_layer_print_height='0.2', layer_height=shared['layer_height'],
                    flush_into_support='0')
    model = ET.Element(Q('model'), unit='millimeter')
    ET.SubElement(model, Q('metadata'), name='Application').text = 'BambuStudio-02.08.02.61'
    ET.SubElement(model, Q('metadata'), name='BambuStudio:3mfVersion').text = '1'
    resources, build = ET.SubElement(model, Q('resources')), ET.SubElement(model, Q('build'))
    cfg, ranges = ET.Element('config'), ET.Element('objects')
    plate = ET.SubElement(cfg, 'plate')
    for key, value in {'plater_id':1, 'plater_name':'TAP and FLAVOR raised lettering; Mark2',
                       'locked':'false', 'bed_type':settings['curr_bed_type'], 'filament_map_mode':'Manual',
                       'filament_maps':'1 2', 'filament_volume_maps':'0 0'}.items():
        meta(plate, key, value)
    next_id, details = 1, []
    for order, (station, body_tool, word_tool, (bx, by)) in enumerate(PLATE, 1):
        body, word = [trial.print_pose(s) for s in trial.build(station)]
        bounds = body.BoundingBox()
        dy = -(bounds.ymin+bounds.ymax)/2
        children = []
        for shape, label, tool in ((body, 'body', body_tool), (word, 'lettering', word_tool)):
            shape = shape.translate((0, dy, 0))
            vertices, faces = shape.tessellate(.015, .05)
            mesh = trimesh.Trimesh(vertices=[v.toTuple() for v in vertices], faces=faces, process=True)
            assert mesh.is_watertight and mesh.is_winding_consistent
            obj = ET.SubElement(resources, Q('object'), id=str(next_id), type='model')
            geometry = ET.SubElement(obj, Q('mesh'))
            vs, ts = ET.SubElement(geometry, Q('vertices')), ET.SubElement(geometry, Q('triangles'))
            for v in mesh.vertices:
                ET.SubElement(vs, Q('vertex'), **dict(zip('xyz', (f'{p:.8f}' for p in v))))
            for face in mesh.faces:
                ET.SubElement(ts, Q('triangle'), **dict(zip(('v1', 'v2', 'v3'), map(str, face))))
            children.append((next_id, label, tool))
            details.append({'station':station, 'part':label, 'filament':tool, 'bounds':mesh.bounds.tolist()})
            next_id += 1
        oid = next_id
        next_id += 1
        obj = ET.SubElement(resources, Q('object'), id=str(oid), type='model')
        components = ET.SubElement(obj, Q('components'))
        config = ET.SubElement(cfg, 'object', id=str(oid))
        meta(config, 'name', trial.name(station))
        meta(config, 'extruder', 1)
        for child, label, tool in children:
            ET.SubElement(components, Q('component'), objectid=str(child))
            part = ET.SubElement(config, 'part', id=str(child), subtype='normal_part')
            meta(part, 'name', label)
            meta(part, 'extruder', tool)
            meta(part, 'matrix', '1 0 0 0 0 1 0 0 0 0 1 0 0 0 0 1')
        ET.SubElement(build, Q('item'), objectid=str(oid), transform=f'1 0 0 0 1 0 0 0 1 {bx} {by} 0', printable='1')
        instance = ET.SubElement(plate, 'model_instance')
        for k, v in {'object_id':oid, 'instance_id':0, 'identify_id':2900+order}.items():
            meta(instance, k, v)
        band_obj = ET.SubElement(ranges, 'object', id=str(order))
        band = ET.SubElement(band_obj, 'range', min_z='1.88', max_z='2.0')
        ET.SubElement(band, 'option', opt_key='layer_height').text = '0.12'
    members.update({
        '3D/3dmodel.model':writer.xml(model),
        'Metadata/model_settings.config':writer.xml(cfg),
        'Metadata/layer_config_ranges.xml':writer.xml(ranges),
        'Metadata/project_settings.config':json.dumps(settings, indent=2).encode(),
        '_rels/.rels':b'<?xml version="1.0"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel-1" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>',
        '[Content_Types].xml':b'<?xml version="1.0"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/><Default Extension="config" ContentType="application/octet-stream"/></Types>',
    })
    writer.archive_write(target, members)
    geometry = json.loads((HERE/'geometry-check.json').read_text())
    sources = [ROOT/p for p in geometry['source_sha256']] + [BASE, PETGF, REGISTRATION, ACCEPTANCE,
               ROOT/registration['appearance_record'], HERE/'geometry-check.json', Path(__file__)]
    report = {'project':str(target.relative_to(ROOT)), 'project_sha256':hashlib.sha256(target.read_bytes()).hexdigest(),
              'source_geometry_and_settings_sha256':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sources},
              'printer':'Mark2', 'parts':details, 'identify_ids':{'2901':'water', '2902':'flavor-a', '2903':'flavor-b'},
              'orientation':'Face up. Existing fitting seat on the bed, lettering above Z=2.0 mm.',
              'requested_z_trim_mm':.04, 'support_policy':'No supports.',
              'calibration_applied':not uncorrected, 'submitted':False,
              'white_correction_mm':correction, 'native_extruder_offset':settings['extruder_offset'],
              'correction_scope':'White nozzle paths, including the TAP body and both FLAVOR words. Nominal CAD unchanged.'}
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
    parser=argparse.ArgumentParser();parser.add_argument('--uncorrected',action='store_true')
    raise SystemExit(main(parser.parse_args().uncorrected))
