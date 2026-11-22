"""Verify the delivered camera hashes, native replay, controller receipts, endpoint clocks and restored hardware controls."""
import argparse
import csv
import gzip
import hashlib
import json
import re
from pathlib import Path


def read(path):
    return json.loads(path.read_text())


def registers(path):
    return {key:int(val) for key,val in re.findall(r'^\s+([a-z_]+)\s+(-?\d+)',path.read_text(),re.M)}


def verify(folder):
    manifest=read(folder/'sha256.json')
    actual={str(p.relative_to(folder)):p for p in folder.rglob('*') if p.is_file() and p.name!='sha256.json'}
    if set(manifest)!=set(actual):
        raise ValueError(f'File-list mismatch: {set(manifest)^set(actual)}')
    for key,path in actual.items():
        if hashlib.sha256(path.read_bytes()).hexdigest()!=manifest[key]:raise ValueError(f'Hash mismatch for {key}')
    index=read(folder/'gate-index.json');timeline=read(folder/'appliance-timeline.json');replay=read(folder/'native-replay-check.json')
    files={r['file'] for r in index['groups']}
    if set(replay['groups'])!=files:raise ValueError('Indexed and replayed sets of native recordings differ.')
    if index['unarchived_command_times_ns'] or index['acknowledged_commands_seen']!=index['archived_commands']:
        raise ValueError('A physical receipt has no native recording.')
    if len(timeline['direct'])!=index['direct_gate_count'] or len(timeline['pours'])!=index['metered_pour_count']:
        raise ValueError('The timeline and the gate archive have different counts.')
    if replay['covered_receipts']!=index['acknowledged_commands_seen']:
        raise ValueError('The native replay did not bracket every receipt.')
    for file,r in replay['groups'].items():
        if r['sha256']!=manifest['gate-profiles/'+file]:raise ValueError(f'Native replay hash mismatch for {file}.')
    max_diff=max(d for r in replay['groups'].values() for d in r['max_abs_replay_difference_px'].values())
    reference=folder/'reference';initial=registers(reference/'original-uvc.txt')
    restored=registers(reference/'restored-uvc.txt');closed=registers(reference/'restored-after-close-uvc.txt')
    wet=registers(reference/'wet-end-uvc.txt');fixed=registers(reference/'frozen-uvc.txt')
    if not(initial==restored==closed) or wet!=fixed:raise ValueError('Restored or wet controls disagree.')
    with gzip.open(folder/'frames.csv.gz','rt') as f:
        points={int(r['seq']):int(r['pts_ns']) for r in csv.DictReader(f)}
    windows=0;photos=0
    with gzip.open(folder/'endpoint-times.jsonl.gz','rt') as f:
        for line in f:
            r=json.loads(line)
            for seq,pts in zip(r['native_seq'],r['native_pts_ns']):
                if points.get(seq)!=pts:raise ValueError(f'Missing luma endpoint clock for {r["label"]}')
                photos+=1
            if points.get(r['color_seq'])!=r['color_pts_ns'] or points.get(r['mid_seq'])!=r['mid_pts_ns']:
                raise ValueError(f'Missing color or midpoint clock for {r["label"]}')
            windows+=1
    cadence=read(reference/'cadence.json');closure=read(reference/'closure.json')
    if cadence['native_frames']!=len(points) or closure['native_last_sequence']!=max(points):
        raise ValueError('Native frame journal and closure clocks differ.')
    return {'manifest_sha256':hashlib.sha256((folder/'sha256.json').read_bytes()).hexdigest(),'files_including_manifest':len(actual)+1,
            'bytes_including_manifest':sum(f.stat().st_size for f in actual.values())+(folder/'sha256.json').stat().st_size,
            'native_frames':len(points),'native_gate_sample_rows':replay['sample_rows_across_groups'],'native_groups':len(files),
            'replayed_receipts':replay['covered_receipts'],'max_replay_difference_px':max_diff,
            'verified_native_endpoint_windows':windows,'contributing_luma_frames':photos,'verified_uvc_registers':len(initial)}


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('folder',type=Path);p.add_argument('--out',type=Path)
    args=p.parse_args();text=json.dumps(verify(args.folder),indent=2)+'\n'
    if args.out:args.out.write_text(text)
    print(text,end='')
