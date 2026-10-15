"""Prepare one tip with a sacrificial bed anchor; no printer-control commands."""
from pathlib import Path
import argparse
import copy
import importlib.util
import json
import os
import subprocess
import sys
import xml.etree.ElementTree as ET
from zipfile import ZipFile

import numpy as np
import trimesh

HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p / 'tools/bambu_print.py').exists())
FAUCET = HERE.parents[1]
sys.path.insert(0, str(FAUCET))
import refresh_print_project as writer

loader = importlib.util.spec_from_file_location('anchor_component', HERE.parent / '2026-10-14-foot-fins-current-angle/prepare.py')
helper = importlib.util.module_from_spec(loader)
loader.loader.exec_module(helper)
PARENT = HERE.parent / '2026-10-15-edge-supports/tip-mark1/preparation.json'
FOLDER = HERE / 'mark1'
STEM = '2026-10-15-faucet-tip-root-anchor-eight-fins-lip-trees-current105-bridge125-fan70-z018-mark1'
WORK = ROOT / '.cache/printer-control/faucet-tip-root-anchor-20261015'


def save(path, value):
    path.write_text(json.dumps(value, indent=2) + '\n')


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--slice', action='store_true')
    args = ap.parse_args()
    if (FOLDER / 'launch.json').exists():
        raise ValueError('Preserve the submitted candidate')
    FOLDER.mkdir(parents=True, exist_ok=True)
    parent = json.loads(PARENT.read_text())
    source = ROOT / parent['project']
    assert writer.digest(source.read_bytes()) == '2840400b8c6a0c70398dc2c08c41d697845c32bd026ddeddc343f0ea5deb9abe'
    with ZipFile(source) as z:
        members = {n: z.read(n) for n in z.namelist()}
    report = copy.deepcopy(parent)
    for key in ('submitted', 'launch_record', 'printer_task_id', 'submitted_gcode_sha256', 'authorization_quote'):
        report.pop(key, None)
    row = report['parts'][0]
    t = np.array(row['build_transform'])
    rotation, translation = t[:9].reshape(3, 3).T, t[9:]
    center = np.array(row['source_center_mm'])
    # Broad two-course bed pad, with a narrower third-course contact strip.
    # It intentionally joins the non-show terminal end of the male plug.
    # A support air gap would leave the low starting island unsecured.
    pad = trimesh.creation.cylinder(radius=1, height=.44, sections=96)
    pad.vertices *= [5, 4, 1]
    pad.apply_translation([162.5, 153.15, .22])
    neck = trimesh.creation.box(extents=[8, 1.2, .24])
    neck.apply_translation([162.5, 153.15, .56])
    anchor = trimesh.util.concatenate([pad, neck])
    bounds = anchor.bounds.tolist()
    anchor.vertices = (anchor.vertices - translation) @ rotation + center
    assert anchor.is_watertight
    model = ET.fromstring(members['3D/3dmodel.model'])
    config = ET.fromstring(members['Metadata/model_settings.config'])
    rel = ET.fromstring(members['3D/_rels/3dmodel.model.rels'])
    helper.component(members, model, config, rel, row, anchor, 2400, 'plug-root-breakaway-foot')
    name = 'Tip: bed-anchored plug, retained fins and lip trees'
    row['name'] = name
    report['rear_seam_paint']['part'] = name
    writer.metadata(config.find(f"object[@id='{row['object_id']}']"), 'name', name)
    writer.metadata(config.find('plate'), 'plater_name', name)
    model.find(f"{writer.qn('metadata')}[@name='Title']").text = name
    members['Metadata/model_settings.config'] = writer.xml(config)
    members['3D/3dmodel.model'] = writer.xml(model)
    members['3D/_rels/3dmodel.model.rels'] = writer.xml(rel).replace(b'ns0:', b'').replace(b'xmlns:ns0=', b'xmlns=')
    project = FOLDER / f'{STEM}.3mf'
    writer.archive_write(project, members)
    report.update(project=str(project.relative_to(ROOT)), project_sha256=writer.digest(project.read_bytes()),
        parent_preparation=str(PARENT.relative_to(ROOT)), parent_project_sha256=parent['project_sha256'],
        settings_source=parent['project'], settings_source_sha256=parent['project_sha256'],
        settings_preserved_byte_for_byte=True, recipe_changes={}, submitted=False,
        candidate_status='Prepared; not submitted. Current photos show the failed article and debris on Mark1.',
        root_anchor=dict(component_id=2400, member='3D/Objects/plug-root-breakaway-foot.model',
            build_center_xy_mm=[162.5, 153.15], build_bounds_mm=bounds,
            elliptical_pad_diameters_mm=[10, 8], pad_height_mm=.44,
            upper_contact_strip_mm=[8, 1.2, .24], total_height_mm=.68,
            requested_air_gap_mm=0, nominal_pad_area_mm2=float(np.pi*5*4),
            removal='Peel or clip the sacrificial foot from the non-show male-plug terminal end. Preserve the plug wall and mating profile; physical removal and fit are not yet established.'),
        retained_geometry=dict(part_member=row['member'], part_member_sha256=writer.digest(members[row['member']]),
            fin_member='3D/Objects/retained-tip-eight-fins.model',
            fin_member_sha256=writer.digest(members['3D/Objects/retained-tip-eight-fins.model']),
            part_and_eight_fins_preserved_byte_for_byte=True, pose_preserved=True,
            seam_and_support_facet_paint_preserved=True),
        support_scope='One directly bonded sacrificial bed foot under the lowest male-plug start only. Retain the eight fins, seam-side lip tree enforcers and Tree(auto)/Default everywhere else. The foot is a local print aid, not a production geometry change.',
        support_reason='The failed Mark1 native slice has no model bead under the plug on the 0.20 mm bed course. Its first plug bead is at Z0.44, with zero lower-bead overlap. Derek reports that the male insertion section fell over and points to its detached curved section. Direct bed anchorage addresses this start independently of overhang angle.',
        authorization_quotes=["So I'm thinking something needs to be under that, where my finger is pointing here in these photos.",
            "And I don't want you to keep wasting my time printing the same control over and over again. Please just print what you think will work best, no repeat control."])
    save(FOLDER / 'preparation.json', report)
    save(project.with_suffix('.print.json'), report)
    if not args.slice:
        print(project)
        return
    native = WORK / 'native'
    native.mkdir(parents=True, exist_ok=True)
    argv = ['/Applications/BambuStudio.app/Contents/MacOS/BambuStudio', '--slice', '0', '--arrange', '0',
        '--orient', '0', '--outputdir', str(native), '--export-3mf', 'native.gcode.3mf', str(project)]
    save(FOLDER / 'slice-command.json', dict(argv=argv))
    with (native / 'slice.log').open('w') as log:
        result = subprocess.run(argv, cwd=native, stdout=log, stderr=subprocess.STDOUT,
            env=dict(os.environ, OMP_NUM_THREADS='1', OPENBLAS_NUM_THREADS='1'))
    if result.returncode:
        raise RuntimeError(f'Native slice failed; see {native / "slice.log"}')
    sliced = json.loads((native / 'result.json').read_text())
    assert sliced['return_code'] == 0
    (FOLDER / f'{STEM}.gcode.3mf').write_bytes((native / 'native.gcode.3mf').read_bytes())
    save(FOLDER / 'slice-result.json', sliced)
    print(json.dumps(sliced['sliced_plates']))


if __name__ == '__main__':
    main()
