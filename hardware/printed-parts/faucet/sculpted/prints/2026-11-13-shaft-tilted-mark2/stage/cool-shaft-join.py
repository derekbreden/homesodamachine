"""Apply the existing PET-GF foundation stage to the shaft's bridge stitch and recovery courses."""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
import os
from pathlib import Path
import re
import subprocess
from tempfile import TemporaryDirectory
from zipfile import ZipFile

SETTINGS = ('filament_settings_id', 'overhang_fan_speed', 'filament_bridge_speed', 'bridge_speed')
LAYER = re.compile(rb'^; CHANGE_LAYER\n; Z_HEIGHT: ([\d.]+)\n', re.M)
STITCH = b'; HSM_BRIDGE_STITCH: shaft join bridge stitch\n'
UPPER = b'; HSM_PHASE: native level upper base\n'
CALIBRATION = Path('tools/hsm/shared-data/catalog/scalars.json')
COOLING = Path('tools/hsm/target/release/petgf-cooling')
FEED_WORD = re.compile(rb' F[-\d.]+(?=\s|$)')
DECIMAL_FEED = re.compile(rb' F([-\d.]+)(?=\s|$)')


def motion_without_feed(data):
    return [FEED_WORD.sub(b'', line) for line in data.splitlines()
            if line.startswith((b'G0 ', b'G1 ', b'G2 ', b'G3 ')) and not line.startswith(b'G1 F')]


def normalize_feed(data):
    return DECIMAL_FEED.sub(lambda match: b' F' + f'{float(match[1]):g}'.encode(), data)


def local_window(raw, depth):
    if raw.count(STITCH) != 1:
        raise ValueError('Expected one shaft bridge stitch marker')
    marker = raw.index(STITCH)
    layers = list(LAYER.finditer(raw))
    stitch_index = max(index for index, m in enumerate(layers) if m.start() < marker)
    stitch = layers[stitch_index]
    stitch_z = float(stitch[1])
    end_index = next(i for i in range(stitch_index + 1, len(layers))
                     if float(layers[i][1]) > stitch_z + depth + 1e-6)
    next_layer = layers[end_index]
    first_native = layers[stitch_index + 1].start()
    end = next_layer.start()
    for i in range(stitch_index + 1, end_index):
        band = raw[layers[i].start():layers[i+1].start()]
        if UPPER not in band or b'; OBJECT_ID: 1901\n' not in band:
            raise ValueError('The recovery window must contain only original upper base courses')
    return stitch.start(), end, first_native, [float(m[1]) for m in layers[stitch_index:end_index]]


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('source', type=Path)
    p.add_argument('project', type=Path)
    p.add_argument('output', type=Path)
    p.add_argument('--cooling-program', type=Path, default=COOLING)
    p.add_argument('--catalog', type=Path, default=CALIBRATION)
    a = p.parse_args()
    raw = a.source.read_bytes()
    schedule = json.loads(a.source.with_suffix('.json').read_text())
    before_hash = sha256(raw).hexdigest()
    if schedule['sequenced_gcode_sha256'] != before_hash:
        raise ValueError('Uncooled schedule and G-code differ')
    depth = json.loads(a.catalog.read_text())['petgf_cooling']['FOUNDATION']['height_mm']
    start, end, first_native, levels = local_window(raw, depth)
    original = raw[start:end]
    with ZipFile(a.project) as project:
        settings = json.loads(project.read('Metadata/project_settings.config'))
    env = {**os.environ, **{'SLIC3R_'+name.upper():json.dumps(settings[name]) for name in SETTINGS}}
    with TemporaryDirectory(dir=a.output.parent) as tmp:
        window = Path(tmp) / 'shaft-bridge-window.gcode'
        window.write_bytes(original)
        subprocess.run([a.cooling_program.resolve(), window], env=env, check=True)
        report = json.loads(Path(str(window)+'.cooling.json').read_text())
        if not report['changed']:
            raise ValueError('Canonical cooling did not find any covered recovery roads')
        marker, modified = window.read_bytes().split(b'\n', 1)
        tail = b'; HSM bridge-foundation result: '
        if marker != b'; HSM bridge-foundation cooling' or modified.count(tail) != 1:
            raise ValueError('Unrecognized canonical foundation stage output')
        modified = modified.split(tail, 1)[0]
    native_marker = original[first_native-start:].split(b'; HSM_PHASE_TRAVEL:', 1)[0]
    if modified.count(native_marker) != 1:
        raise ValueError('Canonical stage changed the first upper layer marker')
    modified_native_start = modified.index(native_marker)
    first_group_prefix = original[:first_native-start]
    if normalize_feed(modified[:modified_native_start]) != normalize_feed(first_group_prefix):
        raise ValueError('Canonical stage changed the stitch seed course')
    # The cooling tool may reformat feed words even when the value is unchanged.
    modified = first_group_prefix + modified[modified_native_start:]
    if motion_without_feed(original) != motion_without_feed(modified):
        raise ValueError('Foundation cooling changed motion geometry or extrusion')
    combined = raw[:start] + modified + raw[end:]
    a.output.write_bytes(combined)
    report.update({
        'source_sha256': before_hash,
        'output_sha256': sha256(combined).hexdigest(),
        'source_project_sha256': sha256(a.project.read_bytes()).hexdigest(),
        'stitch_and_recovery_z_mm': levels,
        'start_line': raw[:start].count(b'\n')+1,
        'last_source_line': raw[:end].count(b'\n'),
        'scope_geometry_and_extrusion_verified': True,
        'outside_scope_bytes_retained': True,
    })
    a.output.with_suffix('.recovery.json').write_text(json.dumps(report, indent=2)+'\n')
    schedule['sequenced_gcode_sha256'] = report['output_sha256']
    schedule['pre_recovery_gcode_sha256'] = report['source_sha256']
    schedule['shaft_join_recovery'] = report
    a.output.with_suffix('.json').write_text(json.dumps(schedule, indent=2)+'\n')


if __name__ == '__main__':
    main()
