"""Prepare fresh flush-frame PET-GF jobs and the open fit-comparison plate.

Sources and reviewed archives are never replaced. This prepares/slices only;
printer launch and the shared-circuit interval belong to the sending session.
"""
from pathlib import Path
import argparse
import copy
import hashlib
import json
import math
import re
import shutil
import subprocess
import sys
import uuid
import xml.etree.ElementTree as ET
import zipfile

import numpy as np
import trimesh

HERE = Path(__file__).resolve().parent
ENC = HERE.parent
ROOT = next(p for p in HERE.parents if (p / 'tools').is_dir())
sys.path[:0] = [str(ROOT / 'hardware/printed-parts/faucet'), str(ENC)]
import refresh_print_project as writer

JOBS = {
    'front-top': ('H2C', .18, ENC / 'enclosure-front-top.stl',
                  '2026-10-04-enclosure-front-top-flush-frame-h2c-v18'),
    'funnel-frame': ('Mark2', .04, ROOT / 'hardware/printed-parts/zone-c/funnel/funnel-frame.stl',
                     '2026-10-04-funnel-frame-flush-roof-mark2-v2'),
}
PROFILE = ROOT / 'hardware/printed-parts/petgf.3mf'
STUDIO = '/Applications/BambuStudio.app/Contents/MacOS/BambuStudio'
sha = lambda path: hashlib.sha256(Path(path).read_bytes()).hexdigest()


def add_solid_hosts(members, model, config, part, center, bounds):
    """Apply each current declared full-host box inside the native solid bounds."""
    record = ENC / 'heat-set-review/print-regions.json'
    spec = json.loads(record.read_text())
    assert spec['native_artifact_sha256'][part]['.stl'] == sha(ENC / f'enclosure-{part}.stl')
    components = model.find(f'.//{writer.qn("components")}')
    obj = config.find('object')
    relations = ET.fromstring(members['3D/_rels/3dmodel.model.rels'])
    rows = []
    for index, item in enumerate(spec['pieces'][part], 3):
        row = copy.deepcopy(item)
        clipped = np.array(row['machine_bounds_mm']).reshape(3, 2)
        clipped[:, 0] = np.maximum(clipped[:, 0], bounds[0]+.001)
        clipped[:, 1] = np.minimum(clipped[:, 1], bounds[1]-.001)
        assert (clipped[:, 1] > clipped[:, 0]).all(), row
        row['applied_machine_bounds_mm'] = clipped.flatten().tolist()
        rows.append(row)
        mesh = trimesh.creation.box(extents=clipped[:, 1]-clipped[:, 0])
        mesh.apply_translation(clipped.mean(axis=1)-center)
        member = f'3D/Objects/solid-host-{index}.model'
        ident = str(uuid.uuid5(uuid.NAMESPACE_URL, f'{sha(record)}:{part}:{index}'))
        document = ET.Element(writer.qn('model'), unit='millimeter')
        resources = ET.SubElement(document, writer.qn('resources'))
        solid = ET.SubElement(resources, writer.qn('object'), id=str(index), type='model')
        shaped = ET.SubElement(solid, writer.qn('mesh'))
        vertices = ET.SubElement(shaped, writer.qn('vertices'))
        for point in mesh.vertices:
            ET.SubElement(vertices, writer.qn('vertex'), **dict(zip('xyz', (f'{v:.9f}' for v in point))))
        triangles = ET.SubElement(shaped, writer.qn('triangles'))
        for face in mesh.faces:
            ET.SubElement(triangles, writer.qn('triangle'), **dict(zip(('v1', 'v2', 'v3'), map(str, face))))
        ET.SubElement(document, writer.qn('build'))
        members[member] = writer.xml(document)
        ET.SubElement(components, writer.qn('component'), objectid=str(index), transform='1 0 0 0 1 0 0 0 1 0 0 0',
                      **{f'{{{writer.PROD}}}path': '/'+member, f'{{{writer.PROD}}}UUID': ident})
        element = ET.SubElement(obj, 'part', id=str(index), subtype='modifier_part', uuid=ident)
        for key, value in {'name': row['name'], 'matrix': '1 0 0 0 0 1 0 0 0 0 1 0 0 0 0 1',
                           'sparse_infill_density': '100%', 'sparse_infill_pattern': 'zig-zag'}.items():
            writer.metadata(element, key, value)
        ET.SubElement(element, 'mesh_stat', face_count='12', edges_fixed='0', degenerate_facets='0',
                      facets_removed='0', facets_reversed='0', backwards_edges='0')
        ET.SubElement(relations, f'{{{writer.REL}}}Relationship', Target='/'+member, Id=f'solid-host-{index}',
                      Type='http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel')
    count = obj.find('metadata[@face_count]')
    count.set('face_count', str(int(count.get('face_count'))+12*len(rows)))
    members['3D/_rels/3dmodel.model.rels'] = writer.xml(relations).replace(b'ns0:', b'').replace(b'xmlns:ns0=', b'xmlns=')
    return rows, sha(record)


def frame_rules(members, report, bands, source):
    """Keep only the complete additive roof-side transition at six walls."""
    sys.path.insert(0, str(ROOT / 'hardware/printed-parts/zone-c/funnel'))
    import funnel_frame as frame
    if frame.roof_datums()['side_reach'] <= 1e-9:
        report['support_painted_facets'] = dict(additive_roof_side_expansion=0)
        return
    root = ET.SubElement(bands, 'object', id='1')
    span = ET.SubElement(root, 'range', min_z='34.0000', max_z='46.3000')
    ET.SubElement(span, 'option', opt_key='layer_height').text = '0.24'
    ET.SubElement(span, 'option', opt_key='wall_loops').text = '6'
    report['layer_ranges_mm'].append(dict(min_z=34., max_z=46.3, layer_height=.24, wall_loops=6,
                                          object=report['parts'][0]['name'],
                                          reason='Complete additive expanding roof-side transition, print Z34.1..46.1.'))
    item = report['parts'][0]
    mesh = trimesh.load_mesh(source, process=True)
    geometry = ET.fromstring(members[item['member']])
    triangles = geometry.find(f'.//{writer.qn("triangles")}')
    count = 0
    for element, points, normal in zip(triangles, mesh.triangles, mesh.face_normals):
        side = (np.abs(points[:, 0]) >= 98.249).all() and points[:, 2].min() >= 34.099 \
            and points[:, 2].max() <= 46.101 and normal[2] < -.001
        if side:
            element.set('paint_supports', '8'); count += 1
    assert count > 0, 'The declared additive roof-side expansion was not found.'
    members[item['member']] = writer.xml(geometry)
    report['support_painted_facets'] = dict(additive_roof_side_expansion=count)


def prepare(part, bottom_gap=.3, xy_gap=.5):
    printer, trim, source, stem = JOBS[part]
    directory = ROOT / '.cache/prints' / stem
    project = directory / (stem+'-input.3mf')
    assert not project.exists(), f'Use a new revision; existing projects are immutable: {project}'
    directory.mkdir(parents=True, exist_ok=True)
    frozen = directory / 'inputs'
    frozen.mkdir()
    sources = [source, source.with_suffix('.step'), PROFILE, Path(__file__),
               ENC / 'enclosure.py', ENC / '_cartridge_retention.py',
               ROOT / 'hardware/printed-parts/zone-c/funnel/funnel_frame.py']
    if part == 'front-top':
        sources.extend([ENC / 'heat-set-review/print-regions.json', ENC / 'magnet-retention/geometry-check.json'])
    for index, path in enumerate(sources):
        shutil.copyfile(path, frozen / f'{index:02d}-{path.name}')
    name = 'enclosure-front-top' if part == 'front-top' else part
    report = writer.refresh(PROFILE, project, parts=((name, source, 0.),), offsets=((0., 0.),),
                            title=f'{name}: flush roof and bounded support XY gap; {printer}',
                            z_trim=trim, plate_border=15.)
    with zipfile.ZipFile(project) as archive:
        members = {n: archive.read(n) for n in archive.namelist()}
    settings = json.loads(members[writer.SETTINGS_MEMBER])
    overrides = {'support_bottom_z_distance': f'{bottom_gap:g}', 'support_object_xy_distance': f'{xy_gap:g}',
                 'extruder_ams_count': ['1#0|4#0', '1#0|4#0'],
                 'support_filament': '1', 'support_interface_filament': '1', 'flush_into_support': '0',
                 'filament_colour': ['#000000' if printer == 'H2C' else '#161616']}
    if part == 'funnel-frame':
        overrides.update(elefant_foot_compensation='0', brim_type='no_brim', brim_width='0')
    report['intentional_overrides'] = {k: {'from': settings.get(k), 'to': v} for k, v in overrides.items()}
    settings.update(overrides)
    members[writer.SETTINGS_MEMBER] = (json.dumps(settings, indent=2)+'\n').encode()
    bands = ET.Element('objects')
    report['layer_ranges_mm'] = []
    report['support_painted_facets'] = {}
    report['pause'] = None
    if part == 'funnel-frame':
        frame_rules(members, report, bands, source)
    if part == 'front-top':
        root = ET.SubElement(bands, 'object', id='1')
        span = ET.SubElement(root, 'range', min_z='187.0000', max_z='195.0000')
        ET.SubElement(span, 'option', opt_key='layer_height').text = '0.08'
        report['layer_ranges_mm'].append(dict(min_z=187., max_z=195., layer_height=.08,
                                              reason='Retained complete inward/top roof-side show rounds.'))
        model = ET.fromstring(members['3D/3dmodel.model'])
        config = ET.fromstring(members['Metadata/model_settings.config'])
        item = report['parts'][0]
        mesh = trimesh.load_mesh(source, process=True)
        center = np.array(item['source_center_mm'])
        geometry = ET.fromstring(members[item['member']])
        triangles = geometry.find(f'.//{writer.qn("triangles")}')
        roof_count = pocket_count = 0
        pocket = json.loads((ENC / 'magnet-retention/geometry-check.json').read_text())['pieces']['front-top']
        px, pz = pocket['axis_xz_mm']; ymin, ymax = pocket['pocket_y_mm']; radius = pocket['pocket_radius_mm']
        for element, points, normal in zip(triangles, mesh.triangles, mesh.face_normals):
            roof_side = (points[:, 2] >= 345.69).all() and ((points[:, 0] <= -100).all() or (points[:, 0] >= 100).all())
            pocket_roof = np.max(np.abs(points[:, 2]-pocket['roof_z_mm'])) < .001 and normal[2] < -.99 \
                and (points[:, 0] >= px-radius-.001).all() and (points[:, 0] <= px+radius+.001).all() \
                and (points[:, 1] >= ymin-.001).all() and (points[:, 1] <= ymax+.001).all()
            if roof_side or pocket_roof:
                element.set('paint_supports', '8')
                roof_count += int(roof_side); pocket_count += int(pocket_roof)
        assert roof_count > 0 and pocket_count == 2, (roof_count, pocket_count)
        report['support_painted_facets'] = dict(exterior_roof_side=roof_count, RC62_roof=pocket_count)
        members[item['member']] = writer.xml(geometry)
        hosts, digest = add_solid_hosts(members, model, config, 'front-top', center, mesh.bounds)
        members['3D/3dmodel.model'] = writer.xml(model)
        members['Metadata/model_settings.config'] = writer.xml(config)
        report.update(solid_host_regions=hosts, solid_host_region_record_sha256=digest)
        roof_height = pocket['roof_z_mm'] - mesh.bounds[0, 2]
        pause_height = .2 + math.ceil((roof_height+.24/2-.2)/.24)*.24
        pauses = ET.Element('custom_gcodes_per_layer'); plate = ET.SubElement(pauses, 'plate')
        ET.SubElement(plate, 'plate_info', id='1')
        ET.SubElement(plate, 'layer', top_z=f'{pause_height:.6f}', type='1', extruder='1', color='',
                      extra='Insert one labeled attracting RC62 upright; fully below both rims. Keep tube passages and toolhead clear. Resume only after separate authorization.', gcode='M400 U1')
        ET.SubElement(plate, 'mode', value='SingleExtruder')
        members['Metadata/custom_gcode_per_layer.xml'] = writer.xml(pauses)
        report['pause'] = dict(requested_top_z_mm=pause_height, pocket_roof_height_mm=roof_height,
                               pocket_geometry_unchanged=True, pocket_fit_qualified=False)
    members['Metadata/layer_config_ranges.xml'] = writer.xml(bands)
    writer.archive_write(project, members)
    report.update(project=str(project.relative_to(ROOT)), project_sha256=sha(project),
                  settings_sha256=hashlib.sha256(members[writer.SETTINGS_MEMBER]).hexdigest(),
                  printer=printer, requested_z_trim_mm=trim, expected_textured_trim_mm=trim-.02,
                  source_step_sha256=sha(source.with_suffix('.step')), source_stl_sha256=sha(source),
                  source_profile_sha256=sha(PROFILE), support_bottom_z_distance_mm=bottom_gap,
                  support_object_xy_distance_mm=xy_gap, support_top_z_distance_mm=float(settings['support_top_z_distance']),
                  source_sha256={str(path.relative_to(ROOT)): sha(path) for path in sources},
                  production_print_pose_retained=True, submitted=False)
    (directory / 'preparation.json').write_text(json.dumps(report, indent=2)+'\n')
    return directory, project, report


def prepare_combined():
    """One frame aft, open magnet coupons mid-plate and upright valve panels fore."""
    frame = JOBS['funnel-frame'][2]
    magnets = ENC / 'magnet-retention/fit-coupons'
    valves = ROOT / 'hardware/printed-parts/fixtures/valve-socket-fit/tighter-trial-v2'
    magnet_manifest = json.loads((magnets / 'geometry.json').read_text())
    valve_manifest = json.loads((valves / 'geometry.json').read_text())
    assert len(magnet_manifest['samples']) == 17 and len(valve_manifest['samples']) == 5
    assert not magnet_manifest['pause'] and not valve_manifest['insertion_pause']
    rows = [('funnel-frame', frame, 0.)]
    frame_mesh = trimesh.load_mesh(frame, process=True)
    frame_height_y = float(np.ptp(frame_mesh.bounds[:, 1]))
    centres = [(162.5, 304.5-frame_height_y/2)]
    valve_height_y = 16.2
    first_magnet_y = 15.5 + valve_height_y + 10. + 14.775/2
    for index, sample in enumerate(magnet_manifest['samples']):
        source = magnets / sample['stl']
        assert sha(source) == sample['stl_sha256']
        rows.append((sample['name'], source, 0.))
        row, col = divmod(index, 5)
        count = 5 if row < 3 else 2
        centres.append((162.5+(col-(count-1)/2)*34., first_magnet_y+row*25.))
    for index, sample in enumerate(valve_manifest['samples']):
        source = valves / sample['stl']
        assert sha(source) == sample['stl_sha256']
        rows.append((sample['name'], source, 0.))
        centres.append((162.5+(index-2)*54., 15.5+valve_height_y/2))
    stem = '2026-10-04-rc62-valve-frame-fit-mark2-v2'
    directory = ROOT / '.cache/prints' / stem
    project = directory / (stem+'-input.3mf')
    assert not project.exists(), f'Use a new revision; existing projects are immutable: {project}'
    directory.mkdir(parents=True, exist_ok=True)
    frozen = directory / 'inputs'; frozen.mkdir()
    sources = [PROFILE, Path(__file__), frame, frame.with_suffix('.step'),
               ROOT / 'hardware/printed-parts/zone-c/funnel/funnel_frame.py',
               ROOT / 'hardware/printed-parts/zone-c/funnel/flush-roof-review/geometry-check.json',
               magnets / 'geometry.json', valves / 'geometry.json',
               valves / 'generate.py', magnets / 'generate.py']
    for _, source, _ in rows[1:]: sources.extend([source, source.with_suffix('.step')])
    source_hashes = {str(path.relative_to(ROOT)): sha(path) for path in sources}
    for index, path in enumerate(sources): shutil.copyfile(path, frozen / f'{index:02d}-{path.name}')
    report = writer.refresh(PROFILE, project, parts=tuple(rows),
                            offsets=tuple((x-162.5, y-160.) for x, y in centres),
                            title='Flush funnel frame, seventeen RC62 pockets and five valve sockets; Mark2',
                            z_trim=.04, plate_border=15.)
    with zipfile.ZipFile(project) as archive:
        members = {n: archive.read(n) for n in archive.namelist()}
    settings = json.loads(members[writer.SETTINGS_MEMBER])
    overrides = dict(extruder_ams_count=['1#0|4#0', '1#0|4#0'], support_filament='1',
                     support_interface_filament='1', flush_into_support='0',
                     filament_colour=['#161616'], elefant_foot_compensation='0',
                     brim_type='no_brim', brim_width='0')
    report['intentional_overrides'] = {k: {'from': settings.get(k), 'to': v} for k, v in overrides.items()}
    settings.update(overrides)
    members[writer.SETTINGS_MEMBER] = (json.dumps(settings, indent=2)+'\n').encode()
    config = ET.fromstring(members['Metadata/model_settings.config'])
    for obj, part in zip(config.findall('object'), report['parts']):
        if part['name'] != 'funnel-frame':
            writer.metadata(obj, 'enable_support', '0')
            part['supports_enabled'] = False
        else: part['supports_enabled'] = True
    members['Metadata/model_settings.config'] = writer.xml(config)
    report['layer_ranges_mm'] = []; report['support_painted_facets'] = {}; report['pause'] = None
    bands = ET.Element('objects'); frame_rules(members, report, bands, frame)
    members['Metadata/layer_config_ranges.xml'] = writer.xml(bands)
    separations = []
    for index, a in enumerate(report['parts']):
        for b in report['parts'][:index]:
            aa, bb = np.array(a['plate_bounds_mm']), np.array(b['plate_bounds_mm'])
            axis_gap = np.maximum(np.maximum(aa[0, :2]-bb[1, :2], bb[0, :2]-aa[1, :2]), 0.)
            gap = float(np.linalg.norm(axis_gap))
            assert gap >= 8., (a['name'], b['name'], gap)
            separations.append(dict(parts=[a['name'], b['name']], native_bounding_box_gap_mm=gap))
    writer.archive_write(project, members)
    for source, expected in source_hashes.items(): assert sha(ROOT / source) == expected, source
    report.update(project=str(project.relative_to(ROOT)), project_sha256=sha(project),
                  settings_sha256=hashlib.sha256(members[writer.SETTINGS_MEMBER]).hexdigest(),
                  printer='Mark2', requested_z_trim_mm=.04, expected_textured_trim_mm=.02,
                  source_sha256=source_hashes, source_profile_sha256=sha(PROFILE),
                  support_bottom_z_distance_mm=float(settings['support_bottom_z_distance']),
                  support_object_xy_distance_mm=float(settings['support_object_xy_distance']),
                  support_top_z_distance_mm=float(settings['support_top_z_distance']),
                  support_policy='Production trees only on the frame; support-free fit samples have support disabled per object.',
                  object_separations=separations, production_print_pose_retained=True,
                  fit_sample_quantity=22, frame_quantity=1, submitted=False,
                  physical_fit_retention_and_surface_qualified=False)
    (directory / 'preparation.json').write_text(json.dumps(report, indent=2)+'\n')
    return directory, project, report


def slice_prepared(directory, project, report):
    """Slice one immutable source project and retain its exact native result."""
    ready = directory / 'ready'; ready.mkdir()
    archive = ready / (directory.name+'.gcode.3mf')
    command = [STUDIO, '--slice', '0', '--arrange', '0', '--orient', '0', '--outputdir', str(ready),
               '--export-3mf', archive.name, str(project)]
    (directory / 'slice-command.json').write_text(json.dumps(command, indent=2)+'\n')
    with (ready / 'slice.log').open('w') as log:
        subprocess.run(command, cwd=ready, stdout=log, stderr=subprocess.STDOUT, check=True)
    result = json.loads((ready / 'result.json').read_text())
    assert result['return_code'] == 0, result
    plate, = result['sliced_plates']
    assert len(plate['objects']) == len(report['parts']) and not plate['warning_message'], plate
    with zipfile.ZipFile(archive) as az:
        assert az.testzip() is None
        data = az.read('Metadata/plate_1.gcode')
        assert hashlib.md5(data).hexdigest() == az.read('Metadata/plate_1.gcode.md5').decode().strip().lower()
        (ready / 'plate_1.gcode').write_bytes(data)
        (directory / 'preview.png').write_bytes(az.read('Metadata/plate_1.png'))
    for source, expected in report['source_sha256'].items(): assert sha(ROOT / source) == expected, source
    assert sha(project) == report['project_sha256']
    native = dict(status='native_slice_awaiting_emitted_review', printer=report['printer'],
                  part=report['parts'][0]['name'], quantity=len(report['parts']),
                  archive=str(archive.relative_to(ROOT)), archive_sha256=sha(archive),
                  project=str(project.relative_to(ROOT)), project_sha256=sha(project),
                  gcode_sha256=hashlib.sha256(data).hexdigest(), estimated_seconds=plate['total_predication'],
                  parts=[{k: p[k] for k in ('name', 'source', 'stl_sha256', 'identify_id')} for p in report['parts']],
                  production_print_pose_retained=True, submitted=False,
                  physical_fit_retention_and_surface_qualified=False)
    (directory / 'native-slice.json').write_text(json.dumps(native, indent=2)+'\n')
    print(str(archive.relative_to(ROOT)), flush=True)
    return native


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('part', choices=[*JOBS, 'combined-trials'])
    parser.add_argument('--slice', action='store_true')
    parser.add_argument('--bottom-gap', type=float, default=.3)
    parser.add_argument('--xy-gap', type=float, default=.5)
    args = parser.parse_args()
    directory, project, report = prepare_combined() if args.part == 'combined-trials' else prepare(args.part, args.bottom_gap, args.xy_gap)
    if args.slice:
        slice_prepared(directory, project, report)
    else:
        print(str(project.relative_to(ROOT)))
