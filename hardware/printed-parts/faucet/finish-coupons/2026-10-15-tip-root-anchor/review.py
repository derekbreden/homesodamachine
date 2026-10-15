"""Manually inspect the plug's native starting courses, not only its rim."""
from pathlib import Path
import hashlib
import json
import re
import sys
from zipfile import ZipFile

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from shapely.geometry import LineString, box
from shapely.ops import unary_union

HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p / 'tools/bambu_print.py').exists())
sys.path[:0] = [str(ROOT / 'hardware/print-tests/petgf-fins'), str(ROOT / 'tools')]
from review import segments
from bambu_print_archive import package

FOLDER = HERE / 'mark1'
PRIOR = HERE.parent / '2026-10-15-edge-supports/tip-mark1'


def save(path, value):
    path.write_text(json.dumps(value, indent=2) + '\n')


def read(folder):
    prep = json.loads((folder / 'preparation.json').read_text())
    archive = ROOT / prep['project'].replace('.3mf', '.gcode.3mf')
    with ZipFile(archive) as z:
        raw = z.read('Metadata/plate_1.gcode')
        md5 = z.read('Metadata/plate_1.gcode.md5').decode().strip().lower()
        settings = z.read('Metadata/project_settings.config')
    assert hashlib.md5(raw).hexdigest() == md5
    return prep, archive, raw, settings, segments(raw.decode())


def footprint(paths):
    return unary_union([LineString([p['a'][:2], p['b'][:2]]).buffer(p['width']/2, quad_segs=8) for p in paths])


def root(paths, z):
    return [p for p in paths if abs(p['z']-z) < 1e-5 and not p['feature'].startswith('Support')
        and p['feature'] != 'Brim' and 156.5 < (p['a'][0]+p['b'][0])/2 < 168.5
        and 148 < (p['a'][1]+p['b'][1])/2 < 158]


def main():
    old_spec, old_archive, old_raw, old_settings, old = read(PRIOR)
    spec, archive, raw, settings_raw, paths = read(FOLDER)
    settings = json.loads(settings_raw)
    assert old_settings == settings_raw, 'The material and machine recipe is unchanged'
    with ZipFile(ROOT / old_spec['project']) as a, ZipFile(ROOT / spec['project']) as b:
        for member in (spec['parts'][0]['member'], '3D/Objects/retained-tip-eight-fins.model'):
            assert a.read(member) == b.read(member), member
    assert spec['parts'][0]['build_transform'] == old_spec['parts'][0]['build_transform']
    assert [float(v) for v in re.findall(r'^\s*G29\.1 Z([-+.\d]+)', raw.decode(), re.M)] == [0, .16]
    assert settings['support_type'] == 'tree(auto)' and settings['support_style'] == 'default'
    assert settings['bridge_flow'] == '1.25'
    assert all(p['fan'] == 0 for p in paths if p['z'] <= .68001)
    assert all(abs(p['fan'] - 178.5) < .001 for p in paths if p['z'] > .68001)
    assert all(abs(p['speed'] - 15) < .001 for p in paths if p['feature'] == 'Bridge' and p['z'] > .68001)
    assert all(p['speed'] <= 15.001 for p in paths if p['feature'] == 'Overhang wall')
    low = np.full(2, np.inf)
    high = -low
    for p in paths:
        xy = np.array([p['a'][:2], p['b'][:2]])
        low = np.minimum(low, xy.min(axis=0)-p['width']/2)
        high = np.maximum(high, xy.max(axis=0)+p['width']/2)
    inset = float(min(*low, 325-high[0], 320-high[1]))
    assert inset >= 80
    assert not root(old, .2)
    first = root(old, .44)
    assert first
    old_first = footprint(first)
    old_lower = footprint([p for p in old if p['z'] < .44-.001])
    assert old_first.intersection(old_lower).area == 0
    bed_root = footprint(root(paths, .2))
    assert bed_root.area > 45
    old_root_bearing = min(1., old_first.intersection(bed_root).area / old_first.area)
    assert old_root_bearing > .95
    courses = []
    for z in (.2, .44, .68, .92, 1.16):
        group = root(paths, z)
        own = footprint(group)
        assert group
        if z > .2:
            previous = footprint(root(paths, round(z-.24, 5)))
            overlap = own.intersection(previous).area
            assert overlap > 1, 'Every root starting course has a direct bond to the preceding course'
        else:
            overlap = None
        courses.append(dict(nozzle_z_mm=z, native_segments=len(group), footprint_area_mm2=own.area,
            footprint_bounds_xy_mm=list(own.bounds), previous_root_course_overlap_area_mm2=overlap,
            features=sorted({p['feature'] for p in group})))
    report = dict(archive=str(archive.relative_to(ROOT)), archive_sha256=hashlib.sha256(archive.read_bytes()).hexdigest(),
        gcode_sha256=hashlib.sha256(raw).hexdigest(), embedded_md5_matches=True,
        reference_failed_job='1341173963', reference_gcode_sha256=hashlib.sha256(old_raw).hexdigest(),
        reference_first_plug_course=dict(nozzle_z_mm=.44, first_gcode_line=first[0]['line'],
            native_segments=len(first), footprint_area_mm2=old_first.area,
            footprint_bounds_xy_mm=list(old_first.bounds), model_root_segments_at_bed_course=0,
            lower_bead_overlap_area_mm2=0, nearest_lower_bead_footprint_distance_mm=old_first.distance(old_lower)),
        corrected_root_bed_course_nozzle_z_mm=.2, corrected_root_bed_bead_area_mm2=bed_root.area,
        corrected_bed_course_overlap_fraction_of_reference_first_root_footprint=old_root_bearing,
        corrected_root_courses=courses, starting_root_courses_directly_joined=True,
        retained_settings_byte_for_byte=True, retained_part_and_fin_members_byte_for_byte=True,
        angle_x_degrees=-105, requested_trim_mm=.18, emitted_trim_mm=.16,
        bridge_flow=1.25, fan_first_three_bed_courses_percent=0, fan_later_percent=70,
        bridge_speed_mm_s=sorted({p['speed'] for p in paths if p['feature']=='Bridge'}),
        overhang_wall_speed_mm_s=sorted({p['speed'] for p in paths if p['feature']=='Overhang wall'}),
        native_support_segments=sum(p['feature'].startswith('Support') for p in paths),
        full_native_bead_bounds_xy_mm=[low.tolist(), high.tolist()], minimum_edge_clearance_mm=inset,
        layer_count=len({p['z'] for p in paths}), specimen_count=1, repeat_control=False, submitted=False,
        limits='Native bead envelopes locate commanded contact. The direct root foot removes the observed missing starting-course bearing; it does not establish physical adhesion, force capacity, removal quality or joint fit. Photos do not establish the initiating motion or its time.')
    save(FOLDER / 'anchor-review.json', report)
    fig, axs = plt.subplots(2, 4, figsize=(15, 8), layout='constrained')
    for row, dataset in enumerate((old, paths)):
        for col, z in enumerate((.2, .44, .68, .92)):
            ax = axs[row, col]
            for p in dataset:
                if abs(p['z']-z) > 1e-5:
                    continue
                color = '#16856b' if p['feature'].startswith('Support') else '#b84530' if row == 0 else '#2263b3'
                ax.plot([p['a'][0], p['b'][0]], [p['a'][1], p['b'][1]], color=color, lw=.8)
            ax.set(xlim=(151, 174), ylim=(146, 160), aspect='equal',
                xlabel='Printer X (mm)', title=f'{"Failed" if row == 0 else "With root foot"}: Z{z:.2f}')
            if col == 0:
                ax.set_ylabel('Printer Y (mm)')
            if row == 0 and col == 0:
                ax.annotate('No plug bead here', xy=(162.5,153.15), xytext=(154,157.5),
                    arrowprops=dict(arrowstyle='->'), fontsize=10)
    fig.suptitle('Male plug start: native model / foot beads; green = automatic supports')
    fig.savefig(FOLDER / 'root-contact.png', dpi=150)
    plt.close(fig)
    print_only = archive.with_name(archive.name.removesuffix('.gcode.3mf')+'-print-only.gcode.3mf')
    assert not print_only.exists(), 'Preserve the packaged review'
    save(FOLDER / 'packaging.json', package(archive, print_only))
    print(json.dumps({k:v for k,v in report.items() if k != 'corrected_root_courses'}, indent=2))


if __name__ == '__main__':
    main()
