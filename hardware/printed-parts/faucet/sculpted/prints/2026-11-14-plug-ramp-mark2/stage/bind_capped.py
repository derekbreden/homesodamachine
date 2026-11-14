"""Bind capped tape to identical geometric-group metadata and immutable source."""

import argparse
import json
from pathlib import Path
import shutil

from merge import checksum


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('uncapped', type=Path)
    parser.add_argument('capped', type=Path)
    parser.add_argument('output', type=Path)
    parser.add_argument('--clamp-receipt', type=Path)
    a = parser.parse_args()
    geometry = json.loads(a.uncapped.with_suffix('.json').read_text())
    source_sha = checksum(a.uncapped)
    if source_sha != geometry['sequenced_gcode_sha256']:
        raise ValueError('Original tape and course geometry do not match')
    capped_sha = checksum(a.capped)
    if source_sha == capped_sha:
        raise ValueError('Capped and uncapped inputs are identical')
    if a.clamp_receipt:
        verify = a.clamp_receipt.read_text()
        if source_sha not in verify or capped_sha not in verify:
            raise ValueError('Clamp receipt does not cover this tape pair')
        geometry['mapped_speed_cap_receipt_sha256'] = checksum(a.clamp_receipt)
    geometry['pre_cap_gcode_sha256'] = source_sha
    geometry['sequenced_gcode_sha256'] = capped_sha
    if a.capped != a.output:
        shutil.copyfile(a.capped, a.output)
        if capped_sha != checksum(a.output):
            raise ValueError('Cloned output differs from the capped source')
    with a.output.open('rb') as stream:
        emitted_group_count = sum(line == b'; CHANGE_LAYER\n' for line in stream)
    if emitted_group_count != len(geometry['groups']):
        raise ValueError('The feed clamp changed course group boundaries')
    a.output.with_suffix('.json').write_text(json.dumps(geometry, indent=2)+'\n')
    print(capped_sha)


if __name__ == '__main__':
    main()
