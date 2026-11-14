"""Assemble each plug-ramp alternative against the same exact five-part reference."""

import argparse
from collections import Counter
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

STAGE = Path(__file__).with_name('archived_sequence.py')
ARCHIVED_SEQUENCER_SHA256 = '0ff0f30d03dcc58b20e141f3f4507e98679adc6598897660e3e4fe798d8e5a72'
REFERENCE_SHA256 = 'de1ed31c0a8f690d415cd1701c0404ab0e97b6cc46ce39342d143c5a3ab50d02'
REFERENCE_RINGS = 13


def source():
    if checksum(STAGE) != ARCHIVED_SEQUENCER_SHA256:
        raise ValueError('The sequencer must match the archived f5dee3210 stage')
    spec = importlib.util.spec_from_file_location('archived_sequence', STAGE)
    recipe = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = recipe
    spec.loader.exec_module(recipe)
    return recipe


def checksum(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument('reference', type=Path)
    cli.add_argument('--candidate', nargs=2, type=Path, action='append', required=True,
                     metavar=('TIP_TAPE', 'OUTPUT_PLATE'))
    args = cli.parse_args()
    reference_sha = checksum(args.reference)
    if reference_sha != REFERENCE_SHA256:
        raise ValueError('The reference must match the exact prior dispense-face review archive')
    maker = source()
    reference_lines = maker.lines(args.reference)
    startup, reference, footer = maker.read_reference(reference_lines)
    cover = [band for band in reference if band.obj == maker.COVER]
    retained = [band for band in reference if band.obj not in (maker.TIP, maker.COVER)]
    ring_count = sum(band.phase == 'mounting plate counterbore supports' for band in retained)
    if not cover or ring_count != REFERENCE_RINGS:
        raise ValueError('The previous plate is missing its cover or ring groups')
    for tip_path, output in args.candidate:
        tip_sha = checksum(tip_path)
        declared = json.loads(tip_path.with_suffix('.json').read_text())
        if declared['tip_tape_sha256'] != tip_sha:
            raise ValueError(f'The mapped tip tape and its receipt differ: {tip_path}')
        tip = maker.read_custom(maker.lines(tip_path))
        schedule = list(maker.interleave(reference, {maker.TIP: tip, maker.COVER: cover}))
        if Counter(map(id, schedule)) != Counter(map(id, tip + cover + retained)):
            raise ValueError('Missing or repeated plate group')
        startup_window, box = maker.leveling(startup, reference_lines, schedule)
        result = maker.emit(output, startup_window, schedule, footer)
        result['source_gcode_sha256'] = {'reference_for_all_non_tip_parts': reference_sha,
                                        'tip_model': tip_sha}
        result['stock_leveling_window_xy_mm'] = box
        result['retained_ring_count'] = ring_count
        result['archived_sequencer_sha256'] = ARCHIVED_SEQUENCER_SHA256
        output.with_suffix('.json').write_text(json.dumps(result, indent=2)+'\n')
        print(json.dumps({'plate': output.name, 'groups': len(result['groups']),
                          'plate_sha256': result['sequenced_gcode_sha256'], 'tip_sha256': tip_sha,
                          'counts_by_phase': result['counts_by_phase']}), flush=True)


if __name__ == '__main__':
    main()
