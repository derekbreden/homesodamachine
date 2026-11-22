"""Verify the manifest, raw endpoint clocks, native pixel averages and both optical readings in a clean archive."""
import argparse
import csv
import gzip
import hashlib
import json
import re
from pathlib import Path

import numpy as np
from replay_sights import check

def sha(data):return hashlib.sha256(data).hexdigest()
def controls(path):
    return dict(re.findall(r'^\s+([a-z_]+)\s+(-?\d+)',path.read_text(),re.M))
def verify(folder):
    manifest=json.loads((folder/'sha256.json').read_text())
    files={str(f.relative_to(folder)):f for f in folder.rglob('*') if f.is_file() and f.name!='sha256.json' and '__pycache__' not in f.parts}
    if set(files)!=set(manifest):raise ValueError('File inventory differs from manifest.')
    for name,path in files.items():
        if sha(path.read_bytes())!=manifest[name]:raise ValueError(f'Hash mismatch for {name}.')
    ref=folder/'reference';orig=controls(ref/'original-uvc.txt')
    if not (orig==controls(ref/'restored-uvc.txt')==controls(ref/'restored-after-close-uvc.txt')):raise ValueError('Camera restoration differs.')
    if not (controls(ref/'frozen-uvc.txt')==controls(ref/'wet-end-uvc.txt')==controls(ref/'previous-frozen-uvc.txt')):raise ValueError('Wet camera controls differ.')
    with gzip.open(ref/'native-clock.csv.gz','rt') as f:
        clocks={int(r['seq']):int(r['pts_ns']) for r in csv.DictReader(f)}
    readings=json.loads((folder/'windows.json').read_text());count=0
    for key,win in readings.items():
        path=folder/'endpoints'/win['source'];reconstructed=check(path)
        if reconstructed['geometry']!=win['absolute_ml']:raise ValueError(f'Different volume at {key}.')
        if any(clocks.get(s)!=p for s,p in zip(reconstructed['seq'],reconstructed['pts_ns'])):raise ValueError(f'Camera clock differs at {key}.')
        if clocks.get(win['mid_seq'])!=win['mid_pts_ns'] or clocks.get(win['color_seq'])!=win['color_pts_ns']:raise ValueError(f'Window clocks differ at {key}.')
        with np.load(path) as z:
            pixels=z['native_luma'];avg=np.rint(pixels.mean(axis=0,dtype=np.float32)).astype(np.uint8)
            if sha(pixels.tobytes())!=win['source_pixel_sha256'] or sha(avg.tobytes())!=win['averaged_pixel_sha256']:raise ValueError(f'Pixel set differs for {key}.')
            count+=len(pixels)
    receipt_index=json.loads((folder/'receipts.json').read_text())
    trials=0;journal_images=0
    for journal in receipt_index.values():
        for event in journal['records']:
            row=event['record'];kind=row.get('event')
            if kind=='image':
                window=readings[row['label']]
                if window['absolute_ml']!=row['readings'] or window['mid_pts_ns']!=row['mid']['pts_ns']:
                    raise ValueError(f'Camera replay differs from the official journaled reading for {row["label"]}.')
                journal_images+=1
            if kind=='trial':
                start=readings[row['start']]['absolute_ml'];finish=readings[row['finish']]['absolute_ml']
                if start!=row['pre'] or finish!=row['post']:raise ValueError(f'Trial endpoint differs for {row["label"]}.')
                sign=1 if row['head']=='B' else -1
                for site in start:
                    a=start[site]['ml'];b=finish[site]['ml'];estimate=sign*(b-a) if a is not None and b is not None else None
                    if estimate!=row['dose_ml'][site]:raise ValueError(f'Dose differs for {row["label"]} at {site}.')
                trials+=1
    from trial_clock import assess
    timing=assess(folder)
    if timing!=json.loads((folder/'trial-clocks.json').read_text()):raise ValueError('Reconstructed motor and endpoint brackets differ.')
    for name,counts in timing['raw_receipts_by_journal'].items():
        if counts['direct_writes']!=counts['direct_received_completions'] or counts['meter_received_openings']!=counts['parsed_openings'] or counts['meter_received_closures']!=counts['parsed_closures']:
            raise ValueError(f'Physical transmit and receive counts disagree for {name}.')
    return {'direct_motor_receipts':timing['transmitted_direct_positioning_count'],'replayed_trial_doses_both_sightlines':trials,'journaled_images_verified':journal_images,'manifest_sha256':sha((folder/'sha256.json').read_bytes()),'files_including_manifest':len(files)+1,
            'bytes_including_manifest':sum(f.stat().st_size for f in files.values())+(folder/'sha256.json').stat().st_size,
            'native_frames':len(clocks),'replayed_windows':len(readings),'replayed_source_frames_across_windows':count,'verified_uvc_registers':len(orig)}

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('folder',type=Path);p.add_argument('--out',type=Path)
    a=p.parse_args();obj=verify(a.folder);txt=json.dumps(obj,indent=2)+'\n'
    if a.out:a.out.write_text(txt)
    print(txt,end='')
