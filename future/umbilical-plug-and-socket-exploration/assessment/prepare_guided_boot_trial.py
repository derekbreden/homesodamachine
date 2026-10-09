"""Prepare an unpowered blue boot-and-key trial for Mark2; never submit it."""
import hashlib
import json
import re
import subprocess
import sys
import zipfile
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
ROOT = next(p for p in BASE.parents if (p/'hardware').is_dir())
sys.path[:0] = [str(BASE), str(ROOT/'hardware/printed-parts/faucet'), str(ROOT/'hardware/scripts')]
import boot_concept as b
import refresh_print_project as writer
from enclosure_support_audit import audit, _affine_inverse, _transform_bbox

OUT = BASE/'guided-boot-trial'
WORK = ROOT/'.cache/prints/umbilical-guided-boot'
PROFILE = ROOT/'hardware/printed-parts/petgf.3mf'
SLICER = '/Applications/BambuStudio.app/Contents/MacOS/BambuStudio'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def prepare():
    WORK.mkdir(parents=True,exist_ok=True)
    (OUT/'parts').mkdir(parents=True,exist_ok=True)
    original = b.u.magnet_slots
    try:
        b.u.magnet_slots = lambda *_args: []
        body = b.plug()
    finally:
        b.u.magnet_slots = original
    parts = []
    for name,shape,angle in (('guided-boot-tactile',body,-90),('guided-tube-key',b.key(),90)):
        source = OUT/'parts'/f'{name}.stl'
        shape.exportStl(str(source),tolerance=.01,angularTolerance=.1)
        parts.append((name,source,angle))
    project = OUT/'guided-boot-mark2-z004.3mf'
    report = writer.refresh(PROFILE,project,parts=tuple(parts),offsets=((-25,0),(25,15)),
                            title='Guided boot tactile trial — blue PET-GF, no magnets',
                            z_trim=.04,plate_border=80)
    with zipfile.ZipFile(project) as archive:
        members = {n:archive.read(n) for n in archive.namelist()}
    settings = json.loads(members[writer.SETTINGS_MEMBER])
    changes = {'initial_layer_print_height':'0.2','layer_height':'0.24',
               'wall_loops':'6','sparse_infill_density':'25%','infill_wall_overlap':'15%',
               'is_infill_first':'0','wall_sequence':'inner wall/outer wall',
               'filament_colour':['#69B4F7'],'enable_support':'1','enable_arc_fitting':'0',
               'elefant_foot_compensation':'0'}
    settings.update(changes)
    members[writer.SETTINGS_MEMBER] = (json.dumps(settings,indent=2)+'\n').encode()
    writer.archive_write(project,members)
    report.update(printer_connection='Mark2',printer_name='Mark2',z_trim_mm=.04,
                  intended_material='Fiberon PET-GF15 Blue; left 0.4 mm nozzle',
                  enable_support=True,wall_loops=6,sparse_infill_percent=25,
                  settings_changes_after_refresh=changes,
                  settings_sha256=hashlib.sha256(members[writer.SETTINGS_MEMBER]).hexdigest(),
                  project_sha256=sha(project),
                  source_sha256={name:sha(BASE/name) for name in
                                 ('umbilical.py','boot_concept.py','assessment/prepare_guided_boot_trial.py')},
                  scope='Unpowered, unpressurized tactile boot and key. Filled magnet pockets. No magnetic, fluid-sealing, electrical, pressure or lifetime qualification.',
                  submitted=False)
    archive_name = project.stem+'.gcode.3mf'
    print('Slicing guided boot and key for Mark2',flush=True)
    with (WORK/'slice.log').open('w') as log:
        result = subprocess.run([SLICER,'--slice','0','--arrange','0','--orient','0',
                                 '--outputdir',str(WORK),'--export-3mf',archive_name,str(project)],
                                cwd=WORK,stdout=log,stderr=subprocess.STDOUT)
    if result.returncode:
        raise RuntimeError(f'Slicer returned {result.returncode}: {WORK / "slice.log"}')
    sliced = OUT/archive_name
    sliced.write_bytes((WORK/archive_name).read_bytes())
    with zipfile.ZipFile(sliced) as archive:
        raw = archive.read('Metadata/plate_1.gcode')
        (OUT/'native-preview.png').write_bytes(archive.read('Metadata/plate_1.png'))
    path = WORK/'plate_1.gcode'
    path.write_bytes(raw)
    gcode = raw.decode()
    beads = writer.object_toolpaths(path,WORK/'all-layer-beads.gcode',None)
    low,high = beads['extrusion_bounds_xy_mm']
    bed_low,bed_high = report['shared_printable_area_mm']
    margin = min(*(a-c for a,c in zip(low,bed_low)),*(c-a for a,c in zip(high,bed_high)))
    layers = sorted(set(float(n) for n in re.findall(r'^; Z_HEIGHT: ([\d.]+)',gcode,re.M)))
    native = {'archive':sliced.name,'archive_sha256':sha(sliced),
              'gcode_sha256':hashlib.sha256(raw).hexdigest(),
              'estimated_time':re.search(r'; total estimated time: (.+)',gcode)[1].strip(),
              'filament_g':[float(n) for n in re.search(r'; total filament weight \[g\] : ([\d.,]+)',gcode)[1].split(',')],
              'layer_count':len(layers),'first_layer_z_mm':layers[0],
              'normal_layer_height_mm':.24,
              'pause_commands':len(re.findall(r'^M400 U1',gcode,re.M)),
              'emitted_z_trim_mm':[float(n) for n in re.findall(r'^\s*G29\.1 Z([-+.\d]+)',gcode,re.M)],
              'complete_layer_bead_bounds':beads,'minimum_full_bead_bed_margin_mm':margin}
    report['native'] = native
    support = audit(path,'guided-boot-and-key',profile=project,include_unlabelled_support=True)
    # Both supports belong to the boot. Use its explicit transform; the shared
    # audit's single-part source-offset reader cannot disambiguate this plate.
    boot = report['parts'][0]
    transform = _affine_inverse(boot['build_transform'])
    transform[9:12] = [v+c for v,c in zip(transform[9:12],boot['source_center_mm'])]
    support['coordinate_frame'] = {'plate_to_cad_transform':transform,'part':boot['name']}
    for tree in support['trees']:
        x0,y0,x1,y1 = tree['bbox_xy_mm']
        tree['bbox_cad_xyz_mm'] = _transform_bbox([x0,y0,tree['base_z_mm'],x1,y1,tree['top_z_mm']],transform)
    for contact in support['interfaces']:
        x0,y0,x1,y1 = contact['bbox_xy_mm']
        contact['bbox_cad_xyz_mm'] = _transform_bbox([x0,y0,contact['first_z_mm'],x1,y1,contact['last_z_mm']],transform)
    (OUT/'support-audit.json').write_text(json.dumps(support,indent=2)+'\n')
    report['native_support_summary'] = support['summary']
    project.with_suffix('.print.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(native,indent=2),flush=True)
    print(json.dumps(support['summary'],indent=2),flush=True)


if __name__ == '__main__':
    prepare()
