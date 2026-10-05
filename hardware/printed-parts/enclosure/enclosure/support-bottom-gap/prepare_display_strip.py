"""Prepare one immutable native strip-enforcer revision from frozen v18.

Only the retained display-strip underside's support paint changes. The source
mesh, show-surface blockers, bands, poses, modifiers and pause remain bound.
Printer control is outside this preparation.
"""
from pathlib import Path
import argparse
import copy
import hashlib
import json
import re
import shutil
import xml.etree.ElementTree as ET
import zipfile

import numpy as np

import prepare_prints as common

HERE = Path(__file__).resolve().parent
ROOT = common.ROOT
BASE = ROOT / '.cache/prints/2026-10-04-enclosure-front-top-flush-frame-h2c-v18'
BASE_PROJECT = BASE / '2026-10-04-enclosure-front-top-flush-frame-h2c-v18-input.3mf'
BASE_SHA = '5723afde9b1ed915f5150d8659dbf128bb61a9e9debc76502940c0960793fe3b'
FROZEN_STL_SHA = 'cc2cfd8a490b52439d957aa082b0e4369c5602076740494298b3a954f0ba36ba'
FACE = (-96.878444663164, 93.158492076719, 96.878444663167, 95.208492076719)
FACE_Z = 349.25
CORE = {'c': 'http://schemas.microsoft.com/3dmanufacturing/core/2015/02'}
sha = common.sha


def prepare(revision):
    assert revision >= 19
    assert sha(BASE_PROJECT) == BASE_SHA
    report = copy.deepcopy(json.loads((BASE / 'preparation.json').read_text()))
    part, = report['parts']
    assert part['stl_sha256'] == FROZEN_STL_SHA
    assert sha(ROOT / part['source']) == FROZEN_STL_SHA
    for path, digest in report['source_sha256'].items():
        assert sha(ROOT / path) == digest, path
    stem = f'2026-10-04-enclosure-front-top-display-strip-h2c-v{revision}'
    directory = ROOT / '.cache/prints' / stem
    assert not directory.exists(), f'Use a new revision: {directory}'
    directory.mkdir()
    project = directory / (stem+'-input.3mf')
    with zipfile.ZipFile(BASE_PROJECT) as archive:
        members = {name: archive.read(name) for name in archive.namelist()}
    original_hashes = {name: hashlib.sha256(payload).hexdigest() for name, payload in members.items()}
    member = part['member']
    original = members[member]
    geometry = ET.fromstring(original)
    vertices = np.array([[float(p.get(axis)) for axis in 'xyz']
                         for p in geometry.findall('.//c:vertex', CORE)])
    vertices += np.array(part['source_center_mm'])
    selected = []; area = 0.; existing_blockers = 0
    faces = geometry.findall('.//c:triangle', CORE)
    for index, element in enumerate(faces):
        existing_blockers += element.get('paint_supports') == '8'
        points = vertices[[int(element.get(key)) for key in ('v1', 'v2', 'v3')]]
        if np.max(np.abs(points[:, 2]-FACE_Z)) > .002:
            continue
        if points[:, 0].min() < FACE[0]-.002 or points[:, 0].max() > FACE[2]+.002 \
                or points[:, 1].min() < FACE[1]-.002 or points[:, 1].max() > FACE[3]+.002:
            continue
        normal = np.cross(points[1]-points[0], points[2]-points[0])
        magnitude = np.linalg.norm(normal)
        if magnitude < 1e-9 or normal[2]/magnitude > -.99:
            continue
        assert element.get('paint_supports') is None, (index, element.attrib)
        selected.append(index); area += magnitude/2
    assert len(selected) == 68 and abs(area-391.35523) < .01, (len(selected), area)
    # Bambu's leaf state is stored in the upper two nibble bits: enforcer=1
    # serializes as 4; blocker=2 serializes as 8. Preserve every other byte.
    chosen = set(selected); index = 0
    def paint(match):
        nonlocal index
        current = index; index += 1
        if current not in chosen:
            return match.group(0)
        assert b'paint_supports=' not in match.group(0)
        return re.sub(rb'\s*/>$', b' paint_supports="4" />', match.group(0))
    members[member] = re.sub(rb'<(?:\w+:)?triangle\b[^>]*/>', paint, original)
    assert index == len(faces), (index, len(faces))
    assert members[member].count(b'paint_supports="8"') == original.count(b'paint_supports="8"')
    changed = [name for name, payload in members.items()
               if hashlib.sha256(payload).hexdigest() != original_hashes[name]]
    assert changed == [member], changed
    common.writer.archive_write(project, members)
    sources = [BASE_PROJECT, BASE / 'preparation.json', Path(__file__), HERE / 'prepare_prints.py']
    frozen = directory / 'inputs'; frozen.mkdir()
    for index, source in enumerate(sources):
        shutil.copyfile(source, frozen / f'{index:02d}-{source.name}')
    report['source_sha256'].update({str(path.relative_to(ROOT)): sha(path) for path in sources})
    report['project'] = str(project.relative_to(ROOT))
    report['project_sha256'] = sha(project)
    report.update(revision=revision, stem=stem, baseline_project=str(BASE_PROJECT.relative_to(ROOT)),
                  baseline_project_sha256=BASE_SHA, baseline_preparation_sha256=sha(BASE / 'preparation.json'),
                  changed_project_members=changed,
                  unchanged_project_member_sha256={name: digest for name, digest in original_hashes.items() if name not in changed},
                  display_strip_support_enforcer=dict(
                      native_face_z_mm=FACE_Z, machine_xy_bounds_mm=list(FACE),
                      painted_triangle_indices=selected, painted_triangle_count=len(selected),
                      painted_area_mm2=float(area), native_paint_value='4',
                      existing_blocker_count_retained=existing_blockers,
                      scope='Only the downward display-strip underside. No vertices, triangle indices or other facet attributes change.',
                      serialization_source='https://github.com/bambulab/BambuStudio/blob/v02.08.02.61/src/libslic3r/TriangleSelector.cpp'),
                  geometry_exports_changed=False, source_pose_bands_settings_modifiers_and_pause_unchanged=True,
                  submitted=False, launch_state='awaiting_full_bead_backing_and_support_access_review')
    report['support_painted_facets']['display_strip_enforcer'] = len(selected)
    (directory / 'preparation.json').write_text(json.dumps(report, indent=2)+'\n')
    return directory, project, report


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--revision', type=int, default=19)
    parser.add_argument('--slice', action='store_true')
    args = parser.parse_args()
    directory, project, report = prepare(args.revision)
    if args.slice:
        common.slice_prepared(directory, project, report)
    else:
        print(str(project.relative_to(ROOT)))
