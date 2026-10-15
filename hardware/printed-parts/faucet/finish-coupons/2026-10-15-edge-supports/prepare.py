"""Prepare one edge-support candidate per printer; no printer-control commands."""
from pathlib import Path
import argparse
import importlib.util
import json
import math
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
sys.path[:0] = [str(FAUCET), str(FAUCET / 'industrial'), str(FAUCET / 'faucet-shell')]
import refresh_print_project as writer
import prepare_print_project as industrial
import faucet_shell as shell


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


foot = load_module('edge_foot', HERE.parent / '2026-10-14-foot-fins-current-angle/prepare.py')
coarse = load_module('edge_coarse', HERE.parent / 'coarse-start-v1/prepare.py')
SOURCE = FAUCET / 'industrial/faucet-industrial-petgf.3mf'
WORK = ROOT / '.cache/printer-control/faucet-edge-supports-20261015'


def save(path, value):
    path.write_text(json.dumps(value, indent=2) + '\n')


def recipe(settings):
    changes = {}
    for key in ('fan_min_speed', 'fan_max_speed', 'overhang_fan_speed'):
        old = settings[key]
        settings[key] = ['70'] * len(old)
        changes[key] = dict(source=old, candidate=settings[key])
    for key in ('bridge_speed', 'filament_bridge_speed'):
        old = settings[key]
        settings[key] = ['15'] * len(old)
        changes[key] = dict(source=old, candidate=settings[key])
    for prefix in ('', 'filament_'):
        for kind in ('1_4', '2_4', '3_4', '4_4', 'totally'):
            key = f'{prefix}overhang_{kind}_speed'
            old = settings[key]
            settings[key] = [str(min(float(v), 15)) if float(v) > 0 else '15' for v in old]
            changes[key] = dict(source=old, candidate=settings[key])
    old = settings['bridge_flow']
    settings['bridge_flow'] = '1.25'
    changes['bridge_flow'] = dict(source=old, candidate='1.25')
    return changes


def pose(row):
    t = np.array(row['build_transform'])
    return t[:9].reshape(3, 3).T, t[9:], np.array(row['source_center_mm'])


def to_cad(mesh, row):
    rotation, translation, center = pose(row)
    mesh.vertices = (mesh.vertices - translation) @ rotation + center
    return mesh


def arc_strip(row, angles, inner, outer, bottom, top):
    """Vertical-sided curved strip; bottom/top are offsets from the tilted CAD Z0 plane."""
    rotation, translation, center = pose(row)
    vertices = []
    for a in angles:
        points = np.array([[r * math.cos(a), r * math.sin(a), 0] for r in (inner, outer)])
        points = (points - center) @ rotation.T + translation
        for offset in (bottom, top):
            for p in points:
                q = p.copy()
                q[2] = 0 if offset is None else p[2] + offset
                vertices.append(q)
    faces = []
    for j in range(len(angles) - 1):
        a, b = 4 * j, 4 * (j + 1)
        for q in ((a, b, b+1, a+1), (a+2, a+3, b+3, b+2),
                  (a, a+2, b+2, b), (a+1, b+1, b+3, a+3)):
            faces.extend(((q[0], q[1], q[2]), (q[0], q[2], q[3])))
    for q in ((0, 1, 3, 2), (4*(len(angles)-1), 4*(len(angles)-1)+2,
                              4*(len(angles)-1)+3, 4*(len(angles)-1)+1)):
        faces.extend(((q[0], q[1], q[2]), (q[0], q[2], q[3])))
    mesh = trimesh.Trimesh(vertices=vertices, faces=faces, process=True)
    mesh.fix_normals()
    assert mesh.is_watertight and mesh.is_volume
    return mesh


def base_arcs(members, model, config, rel, row):
    rotation, translation, center = pose(row)
    records = []
    pid = 2200
    # The front/lever-facing pole is CAD -Y, so its arc is centred at -90 degrees.
    # Eight 41-degree arcs leave 4-degree release gaps away from that midpoint.
    for angle in range(-90, 270, 45):
        samples = np.radians(np.linspace(angle-20.5, angle+20.5, 165))
        p = np.array([[29.55*math.cos(a), 29.55*math.sin(a), 0] for a in samples])
        z = ((p-center) @ rotation.T + translation)[:, 2] - .24
        valid = z >= .20
        groups = np.split(np.flatnonzero(valid), np.flatnonzero(np.diff(np.flatnonzero(valid)) > 1)+1)
        for group in groups:
            if len(group) < 3:
                continue
            angles = samples[group]
            if 29.1 * float(angles[-1]-angles[0]) < 2:
                continue
            wall = arc_strip(row, angles, 28.65, 29.55, None, -.24)
            name = f'rim-arc-{pid}'
            foot.component(members, model, config, rel, row, to_cad(wall.copy(), row), pid, name)
            # Block only this wall's narrow contact strip, leaving the annulus interior
            # and all release gaps to Bambu's automatic support decisions.
            blocker = arc_strip(row, angles, 28.45, 29.95, -.85, .85)
            foot.component(members, model, config, rel, row, to_cad(blocker, row), pid+100,
                           name+'-contact-blocker', subtype='support_blocker')
            records.append(dict(component_id=pid, blocker_component_id=pid+100,
                cad_angle_interval_degrees=np.degrees(angles[[0, -1]]).tolist(),
                cad_radius_interval_mm=[28.65, 29.55], nominal_wall_width_mm=.90,
                requested_vertical_gap_mm=.24, world_bounds_mm=wall.bounds.tolist(),
                blocker_radius_interval_mm=[28.45, 29.95]))
            pid += 1
    return records


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('kind', choices=('base', 'tip'))
    ap.add_argument('--slice', action='store_true')
    args = ap.parse_args()
    base = args.kind == 'base'
    printer, trim, colour = ('Mark2', .04, '#161616') if base else ('Mark1', .18, '#000000')
    folder = HERE / f'{args.kind}-{printer.lower()}'
    if (folder / 'launch.json').exists():
        raise ValueError('Preserve the accepted print; use another candidate directory')
    folder.mkdir(parents=True, exist_ok=True)
    work = WORK / args.kind
    work.mkdir(parents=True, exist_ok=True)
    stem = ('2026-10-15-faucet-base-segmented-rim-arcs-tree-current15-bridge125-fan70-z004-mark2'
            if base else '2026-10-15-faucet-tip-lip-trees-eight-fins-current105-bridge125-fan70-z018-mark1')
    part = (HERE.parent / '2026-10-14-foot-fins-current-angle/foot-section.stl' if base else
            HERE.parent / '2026-10-14-bridge-transfer/tip-section.stl')
    parent_path = (HERE.parent / '2026-10-14-foot-fins-current-angle/stock-vs-tree/mark2/preparation.json'
                   if base else HERE.parent / '2026-10-15-tip-fins/mark2/preparation.json')
    parent = json.loads(parent_path.read_text())
    assert writer.digest(part.read_bytes()) == parent['parts'][0]['stl_sha256']
    name = 'Base: segmented rim arcs and automatic trees' if base else 'Tip: retained fins and seam-side lip trees'
    project = folder / f'{stem}.3mf'
    report = writer.refresh(SOURCE, project, parts=((name, part, -15 if base else -105),),
                            offsets=((0, 0),), title=name, z_trim=trim, plate_border=80)
    with ZipFile(project) as z, ZipFile(SOURCE) as source:
        members = {n: z.read(n) for n in z.namelist()}
        source_config = ET.fromstring(source.read('Metadata/model_settings.config'))
        parent_object = next(o for o in source_config.findall('object') if
            o.find("metadata[@key='name']").get('value') == ('industrial-shell-base' if base else 'faucet-shell-tip'))
    settings = json.loads(members[writer.SETTINGS_MEMBER])
    changes = recipe(settings)
    settings['filament_colour'] = [colour]
    members[writer.SETTINGS_MEMBER] = (json.dumps(settings, indent=2)+'\n').encode()
    config = ET.fromstring(members['Metadata/model_settings.config'])
    model = ET.fromstring(members['3D/3dmodel.model'])
    rel = ET.fromstring(members['3D/_rels/3dmodel.model.rels'])
    row = report['parts'][0]
    cfg = config.find(f"object[@id='{row['object_id']}']")
    for m in parent_object.findall('metadata'):
        if m.get('key') and m.get('key') not in ('name', 'extruder', 'bridge_flow'):
            writer.metadata(cfg, m.get('key'), m.get('value'))
    writer.metadata(cfg, 'bridge_flow', '1.25')
    if base:
        region = trimesh.creation.box(extents=[61, 61, 14.02])
        region.apply_translation([0, 0, 7])
        coarse.add_foot_modifier(members, model, config, rel, row, region, 0)
        arcs = base_arcs(members, model, config, rel, row)
        report['rim_arcs'] = arcs
        support_scope = 'Segmented curved walls under the visible outer rim only. Narrow support-blocker volumes follow their contact strips; Tree(auto)/Default serves the rest of the annulus and all other geometry. No blanket bottom-face blocker.'
        support_reason = 'Derek identifies the visible edge as the fin task and requests interrupted circumferential arcs with trees elsewhere. The front arc is continuous beneath the lever-facing midpoint; release gaps lie to its sides. Straight/radial fins have an inferior physical rim result to trees.'
    else:
        mesh = trimesh.load(part, force='mesh', process=True)
        point = np.array([0, shell.split_junction_y, shell.split_junction_z])
        normal = np.array(shell.split_normal)
        plane = (np.max(abs((mesh.triangles-point) @ normal), axis=1) < .02) & (mesh.face_normals @ (-normal) > .999)
        rotation, translation, center = pose(row)
        placed = (mesh.triangles_center-center) @ rotation.T + translation
        # The rear seam reaches the low starting pole. Select a broad patch there,
        # preserving the fin-only treatment on the opposite, physically good side.
        targeted = plane & (placed[:, 2] < 21) & (abs(mesh.triangles_center[:, 0]) < 8)
        child = ET.fromstring(members[row['member']])
        triangles = child.find('.//' + writer.qn('triangles'))
        assert len(triangles) == len(plane)
        for tri, blocked, enforced in zip(triangles, plane, targeted):
            if blocked:
                tri.set('paint_supports', '4' if enforced else '8')
        members[row['member']] = writer.xml(child)
        # Retain the submitted fin geometry from the committed editable project;
        # reproduction does not depend on transient upstream-engine output.
        retained_project = ROOT / parent['project']
        assert writer.digest(retained_project.read_bytes()) == parent['project_sha256']
        with ZipFile(retained_project) as retained:
            fin_doc = ET.fromstring(retained.read('3D/Objects/tip-joint-fin-walls.model'))
        fin_mesh = fin_doc.find('.//' + writer.qn('mesh'))
        vertices = np.array([[float(v.get(k)) for k in 'xyz'] for v in fin_mesh.find(writer.qn('vertices'))])
        faces = [[int(f.get(k)) for k in ('v1', 'v2', 'v3')] for f in fin_mesh.find(writer.qn('triangles'))]
        support = trimesh.Trimesh(vertices=vertices+np.array(parent['parts'][0]['source_center_mm']),
                                 faces=faces, process=False)
        foot.component(members, model, config, rel, row, support, 2000, 'retained-tip-eight-fins')
        report.update(retained_fin_count=8, joint_plane=dict(point=point.tolist(), normal=normal.tolist()),
            enforced_lip_faces=int(targeted.sum()), enforced_lip_area_mm2=float(mesh.area_faces[targeted].sum()),
            enforced_facet_bounds_cad_mm=[mesh.triangles[targeted].reshape(-1, 3).min(axis=0).tolist(),
                                        mesh.triangles[targeted].reshape(-1, 3).max(axis=0).tolist()],
            retained_fin_source=str((HERE.parent/'2026-10-15-tip-fins/mark2/layout-engine.json').relative_to(ROOT)))
        support_scope = 'The eight existing plain fin walls and joint-plane blockers are retained on the good side. The seam-side low starting lip patch is support-enforced instead of blocked, allowing Tree(auto)/Default to reach it. Other automatic supports retain their saved settings and 0.45 mm top gap.'
        support_reason = 'Derek reports the opposite rim side remains rough while the fin/cooling-recipe underside is the best observed. The native prior slice leaves 4.19 mm without lower bead overlap at the seam-side low lip. Add local tree contacts without changing the successful opposite-side treatment.'
    members['Metadata/model_settings.config'] = writer.xml(config)
    members['3D/3dmodel.model'] = writer.xml(model)
    members['3D/_rels/3dmodel.model.rels'] = writer.xml(rel).replace(b'ns0:', b'').replace(b'xmlns:ns0=', b'xmlns=')
    paint = industrial.enforce_rear_seam(members, report, dict(part=name, half_width_mm=.25 if base else 0,
        **({} if base else dict(surface='curved_outer_arc'))))
    writer.archive_write(project, members)
    report.update(project=str(project.relative_to(ROOT)), project_sha256=writer.digest(project.read_bytes()),
        settings_sha256=writer.digest(members[writer.SETTINGS_MEMBER]), settings_preserved_byte_for_byte=False,
        printer=printer, requested_z_trim_mm=trim, recipe_changes=changes, rear_seam_paint=paint,
        specimen_count=1, repeat_control=False, support_scope=support_scope, support_reason=support_reason,
        parent_preparation=str(parent_path.relative_to(ROOT)), parent_project_sha256=parent['project_sha256'],
        material_treatment='Native bridge flow1.25,70% fan after3off bedlayers including floating vertical shell/supports;Bridge15mm/s,overhang limits<=15 preserving existing10mm/s. No post-slice edits.',
        candidate_status='Prepared; printer submission pending.',
        authorization_quote='Both printers are available and its my bed time. Print as you see fit.')
    save(folder / 'preparation.json', report)
    save(project.with_suffix('.print.json'), report)
    if not args.slice:
        print(project, flush=True)
        return
    native = work / 'native'
    native.mkdir(exist_ok=True)
    command = ['/Applications/BambuStudio.app/Contents/MacOS/BambuStudio', '--slice', '0', '--arrange', '0',
               '--orient', '0', '--outputdir', str(native), '--export-3mf', 'native.gcode.3mf', str(project)]
    save(folder / 'slice-command.json', dict(argv=command))
    with (native / 'slice.log').open('w') as log:
        result = subprocess.run(command, cwd=native, stdout=log, stderr=subprocess.STDOUT,
                                env=dict(os.environ, OMP_NUM_THREADS='1', OPENBLAS_NUM_THREADS='1'))
    if result.returncode:
        raise RuntimeError(f'Native slice failed ({result.returncode}); see {native / "slice.log"}')
    sliced = json.loads((native / 'result.json').read_text())
    assert sliced.get('return_code') == 0, sliced
    (folder / f'{stem}.gcode.3mf').write_bytes((native / 'native.gcode.3mf').read_bytes())
    save(folder / 'slice-result.json', sliced)
    print(json.dumps(sliced['sliced_plates']), flush=True)


if __name__ == '__main__':
    main()
