"""Assemble self-contained camera source, photographed examples and timing records for the completed pour trials."""
import argparse
import bisect
import csv
import gzip
import hashlib
import json
import os
import shutil
import sys
from pathlib import Path

import numpy as np
sys.path.append('/opt/homebrew/lib/python3.13/site-packages')
from PIL import Image
from timing_window import HERE
import register_cup

def link(source,dest):
    dest.parent.mkdir(parents=True,exist_ok=True)
    if dest.exists() and os.path.samefile(source,dest):return
    if dest.exists():dest.unlink()
    os.link(source,dest)

def compact_photo(window,out,label):
    ref=HERE/'windows'/window
    color=json.loads((ref/'color.json').read_text());timing=json.loads((ref/'window.json').read_text())
    gray=out/(label+'-cup.png');ink=out/(label+'-ink.png')
    box=(920,658,2040,1240)
    if not gray.is_file():
        with Image.open(ref/'average.png') as image:image.crop(box).save(gray,compress_level=3)
    if not ink.is_file():register_cup.pack_color(ref/'color.png',ink)
    return {'window':window,'average':gray.name,'rgb_ink_tiles':ink.name,'luma_upright_crop_ltrb':box,
            'luma_mid_pts_ns':timing['mid']['pts_ns'],'contributing_pts_ns':[r['pts_ns'] for r in timing['frames']],
            'color_pts_ns':color['pts_ns'],'color_seq':color['seq']}

def assemble(final):
    out=HERE/'evidence';sources=out/'capture-source';replay=out/'replay';ref=out/'reference'
    for item in ('acquisition.md','camera.swift','feed.py','endpoint.py','controls.py','close_camera.py','front_preview.py','refresh_results.py','pack_camera_evidence.py','repack_native.py','archive_gates.py','timing_window.py','native_profiles.py','steward.py','timeline.py','stationary_evidence.py','pack_hold_ink.py','collect_holds.py'):
        link(HERE/item,sources/item)
    for item in ('native_profiles.py','rim_measure.py','upper_contact.py','read_pour_timings.py','freeze_rim.py','score_optics.py','score_fill_timing.py','read_hold.py','read_hold_ink.py','hold_variation.py','dry_waves.py','sampling_coverage.py','register_cup.py','replay_native.py','front_wall.py','front_holds.py','inspect_hold_feature.py','return_contacts.py','score_front_wall.py','audit_native.py','check_receipts.py','verify_camera_archive.py','plot_pour_phases.py'):
        link(HERE/item,replay/item)
    for item in ('rim-reference.npz','upper-contact-reference.npz','original-uvc.txt','frozen-uvc.txt','clock.json','control-events.jsonl','events.jsonl'):
        link(HERE/item,ref/item)
    home=HERE/'windows/station-idle'
    for name in ('average.png','color.png','window.json','color.json'):
        link(home/name,ref/('station-idle-'+name))
    examples=out/'examples';examples.mkdir(exist_ok=True);pictures=[]
    trace_files=sorted(f for f in (HERE/'front-preview').glob('*.npz') if f.stem.isdigit())
    front_starts=[]
    for f in trace_files:
        with np.load(f) as z:front_starts.append(int(z['pts_ns'][0]))
    for p in json.loads((out/'appliance-timeline.json').read_text())['pours']:
        req=p['prediction'];trial=p['trial']
        if not trial or req.get('block')!=1:continue
        original=(req.get('phase')=='validation' and req.get('scenario') in ('full_glass','partial_glass','same_open_time','release_reopen'))
        reserved=(p['journal']=='fresh.jsonl' and req.get('scenario') in ('near_full_glass','short_richer_pour'))
        if not (original or reserved or p['journal']=='fill.jsonl'):continue
        for edge in ('pre','post'):
            result=compact_photo(trial[edge],examples,p['event_label']+'-'+edge)
            pictures.append(dict(pour=p['event_label'],phase=edge,**result))
        dst=examples/(p['event_label']+'-front-preview.npz')
        first=p['start_ack_ns']-700_000_000;last=p['done_ack_ns']+3_100_000_000
        if not dst.is_file():
            tiles=[];times=[];seqs=[]
            for f in trace_files[max(0,bisect.bisect_right(front_starts,first)-1):bisect.bisect_right(front_starts,last)]:
                with np.load(f) as z:
                    sel=(z['pts_ns']>=first)&(z['pts_ns']<=last)
                    if sel.any():
                        tiles.append(z['luma'][sel]);times.append(z['pts_ns'][sel]);seqs.append(z['seq'][sel]);xx=z['sensor_x'];yy=z['sensor_y']
            if times and times[0][0]<first+200_000_000 and times[-1][-1]>last-200_000_000:
                np.savez_compressed(dst,luma=np.concatenate(tiles),pts_ns=np.concatenate(times),seq=np.concatenate(seqs),sensor_x=xx,sensor_y=yy)
    (examples/'index.json').write_text(json.dumps(pictures,indent=2)+'\n')
    if not final:return
    rest=[]
    for home_window in sorted((HERE/'windows').glob('home*settled*')):
        if (home_window/'average.png').exists() and (home_window/'color.json').exists():
            row=compact_photo(home_window.name,ref,home_window.name)
            if home_window.name=='home-final-settled':
                link(home_window/'average.png',ref/'home-final-settled-full.png')
                row['full_native_luma']='home-final-settled-full.png'
            rest.append(row)
    (ref/'home-endpoints.json').write_text(json.dumps(rest,indent=2)+'\n')
    with (out/'endpoint-times.jsonl.gz').open('wb') as target:
        with gzip.GzipFile(fileobj=target,filename='endpoint-times.jsonl',mode='wb',compresslevel=6,mtime=0) as gz:
            for f in sorted((HERE/'windows').glob('*/window.json')):
                w=json.loads(f.read_text());c=json.loads((f.parent/'color.json').read_text())
                obj={'label':w['label'],'mid_pts_ns':w['mid']['pts_ns'],'mid_seq':w['mid']['seq'],'requested_ns':[w['target_start_ns'],w['target_end_ns']],
                     'native_pts_ns':[r['pts_ns'] for r in w['frames']],'native_seq':[r['seq'] for r in w['frames']],'color_pts_ns':c['pts_ns'],'color_seq':c['seq']}
                gz.write((json.dumps(obj)+'\n').encode())
    for name in ('upper-rim.csv','direct-inner-contact.csv','frames.csv'):
        raw=HERE/name;dest=out/(name+'.gz');tmp=out/(name+'.partial')
        with raw.open('rb') as handle,tmp.open('wb') as compressed:
            with gzip.GzipFile(fileobj=compressed,filename=name,mode='wb',compresslevel=6,mtime=0) as gz:shutil.copyfileobj(handle,gz)
        tmp.replace(dest)
    for name in ('wet-end-uvc.txt','restored-uvc.txt','restored-after-close-uvc.txt','closure.json','cadence.json'):
        if (HERE/name).exists():link(HERE/name,ref/name)
    # A checkpoint can move to another group when later journal rows arrive.
    index=json.loads((out/'gate-index.json').read_text());kept={g['file'] for g in index['groups']}
    for old in (out/'gate-profiles').glob('*.npz'):
        if old.name not in kept:
            dest=HERE/'superseded-gate-profiles'/old.name;dest.parent.mkdir(exist_ok=True);old.replace(dest)
    artifacts={str(f.relative_to(out)):hashlib.sha256(f.read_bytes()).hexdigest() for f in sorted(out.rglob('*'))
               if f.is_file() and f.name!='sha256.json' and '__pycache__' not in f.parts}
    (out/'sha256.json').write_text(json.dumps(artifacts,indent=2)+'\n')
    print(len(artifacts),'hashed files')

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--final',action='store_true')
    assemble(p.parse_args().final)
