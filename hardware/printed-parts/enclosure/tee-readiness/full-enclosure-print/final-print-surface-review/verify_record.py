"""Verify retained lint evidence and optional live artifact bindings; no writes."""
from pathlib import Path
import argparse
import hashlib
import json
import math
import re

HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p / 'hardware/cad-artifacts.json').is_file())


def sha(path):
    result = hashlib.sha256()
    with path.open('rb') as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b''):
            result.update(chunk)
    return result.hexdigest()


def answers(text):
    entries = []
    for block in re.split(r'(?=^\[)', text, flags=re.M):
        kind = re.match(r'\[([^]]+)\]', block)
        if kind:
            entries.extend((kind.group(1), tuple(map(float, point))) for point in
                           re.findall(r'^click: x=([^ ]+) y=([^ ]+) z=([^\s]+)', block, re.M))
    return entries


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--current-inputs', action='store_true')
    args = parser.parse_args()
    manifest = json.loads((HERE / 'manifest.json').read_text())
    for name, data in manifest['files'].items():
        path = HERE / name
        assert path.stat().st_size == data['bytes'], f'Wrong retained size: {name}'
        assert sha(path) == data['sha256'], f'Changed retained evidence: {name}'
    record = json.loads((HERE / 'record.json').read_text())
    current = json.loads((ROOT / 'hardware/cad-artifacts.json').read_text()) if args.current_inputs else None
    total = 0
    for part in record['parts']:
        raw_path = HERE / part['measurement_report']
        assert sha(raw_path) == part['measurement_report_sha256']
        raw = json.loads(raw_path.read_text())
        assert 'lint pass failed:' not in raw['errors'], part['part']
        findings = [f for rows in raw['open'].values() for f in rows]
        findings += [row['finding'] for row in raw['answered']]
        if part.get('retained_answers'):
            answer_path = HERE / part['retained_answers']
            assert sha(answer_path) == part['answers_sha256']
            entries = answers(answer_path.read_text())
        else:
            entries = []
        for finding in findings:
            point, = [tuple(map(float, match)) for match in re.findall(
                r'click: x=([^ ]+) y=([^ ]+) z=([^\s]+)', '\n'.join(finding['pick']))]
            assert any(kind == finding['class'] and math.dist(point, anchor) <= .002
                       for kind, anchor in entries), (part['part'], finding['pick'])
        assert len(findings) == part['answered'] and part['unanswered'] == 0
        total += len(findings)
        if current is not None:
            assert sha(ROOT / part['mesh']) == part['mesh_sha256'], part['mesh']
            for name, digest in part['published_member_sha256'].items():
                assert sha(ROOT / name) == digest, f'Changed artifact: {name}'
                assert current['solids'].get(name) == digest, f'Unpublished artifact: {name}'
            if part.get('answers_source'):
                assert sha(ROOT / part['answers_source']) == part['answers_sha256'], part['answers_source']
    assert len(record['parts']) == 8 and total == 328
    print(json.dumps({'status': 'pass', 'parts': 8, 'answered': total, 'unanswered': 0,
                      'packaged_files_verified': len(manifest['files']),
                      'current_artifact_members_verified': args.current_inputs,
                      'print_or_support_release': False}, indent=2))


if __name__ == '__main__':
    main()
