"""Assemble a self-contained compact optical record for the unseen pours and their final return."""
import argparse
import csv
import gzip
import hashlib
import json
import os
from pathlib import Path

from PIL import Image

from archive_endpoints import capture
from endpoint_receipts import summarize
import register_cup
from replay_sights import HERE

def link(src,dst):
    dst.parent.mkdir(parents=True,exist_ok=True)
    if dst.exists() and os.path.samefile(src,dst):return
    if dst.exists():dst.unlink()
    os.link(src,dst)

def materialize(root,final):
    out=root/'evidence';readings=capture(root)
    src=out/'capture-source';ref=out/'reference';ref.mkdir(exist_ok=True)
    for name in ('camera.swift','feed.py','endpoint.py','controls.py','close_capture.py','archive_endpoints.py','endpoint_receipts.py','package_camera.py'):
        link(root/name,src/name)
    for name in ('replay_sights.py','reopen_alignment.py','register_cup.py','trial_clock.py','window_repeatability.py','verify_evidence.py'):
        link(root/name,out/name)
    for name in ('read_levels.py','cup_volume.py','mark_crossings.py','mark_crossings_v2.py','mark_crossings_v3.py','geometry-used.json'):
        link(root/'optical-source'/name,out/'optical-source'/name)
    for name in ('clock.json','source-revision.txt','original-uvc.txt','frozen-uvc.txt','control-events.jsonl','events.jsonl','reopen-alignment.json',
                 'reopen-printed.json','source-equivalence.json','reopen-geometry.json','readiness-repeat.json','idle-repeat-alignment.json'):
        if (root/name).is_file():link(root/name,ref/name)
    for name in ('frozen-uvc.txt','home-final-settled-full.png','home-final-settled-ink.png'):
        link(root/'previous'/name,ref/('previous-'+name))
    link(root/'windows/station-idle/average.png',ref/'station-idle-average.png')
    link(root/'reopened-ink.png',ref/'station-idle-ink.png')
    link(root/'previous/final-ink-templates.npz',ref/'previous-final-ink-templates.npz')
    if not final:return
    for name in ('wet-end-uvc.txt','restored-uvc.txt','restored-after-close-uvc.txt','closure.json'):
        link(root/name,ref/name)
    # Two-column camera times support exact endpoint and appliance receipt reconciliation.
    with (root/'frames.csv').open() as source, (ref/'native-clock.csv.gz').open('wb') as output:
        with gzip.GzipFile(filename='native-clock.csv',fileobj=output,mode='wb',compresslevel=7,mtime=0) as zipped:
            zipped.write(b'seq,pts_ns\n')
            for row in csv.DictReader(source):zipped.write((row['seq']+','+row['pts_ns']+'\n').encode())
    from window_repeatability import run
    records=summarize(root,root.parent/'work');(out/'receipts.json').write_text(json.dumps(records,indent=2)+'\n')
    (out/'window-repeatability.json').write_text(json.dumps(run(out/'endpoints',records),indent=2)+'\n')
    from trial_clock import assess
    trials=assess(out)
    (out/'trial-clocks.json').write_text(json.dumps(trials,indent=2)+'\n')
    examples=out/'photographed-programs';examples.mkdir(exist_ok=True)
    picked={};box=(950,780,2045,1150)
    for trial in trials['completed']:
        name=trial['scenario']
        if name in picked:continue
        entry={'label':trial['label'],'head':trial['head'],'native_crop_ltrb':box}
        for field in ('start_window','finish_window'):
            label=trial[field];target=examples/(label+'.png')
            with Image.open(root/'windows'/label/'average.png') as image:image.crop(box).save(target,compress_level=7)
            entry[field]={'label':label,'picture':target.name,'mid_pts_ns':readings[label]['mid_pts_ns']}
        picked[name]=entry
    (examples/'index.json').write_text(json.dumps(picked,indent=2)+'\n')
    chosen=[]
    for journal in records.values():
        last_image=None
        for ev in journal['records']:
            r=ev['record']
            if r.get('event')=='image':last_image=r['label']
            if r.get('event') in ('station_return','station_position'):
                label=r.get('last_window') or last_image
                if label in readings:chosen.append(label)
    for label in ['station-idle','camera-readiness-repeat',*chosen]:
        w=root/'windows'/label
        if not w.exists():continue
        link(w/'average.png',ref/(label+'-average.png'))
        if not (ref/(label+'-ink.png')).is_file():register_cup.pack_color(w/'color.png',ref/(label+'-ink.png'))
    (ref/'return-windows.json').write_text(json.dumps(chosen,indent=2)+'\n')
    checksums={str(f.relative_to(out)):hashlib.sha256(f.read_bytes()).hexdigest() for f in sorted(out.rglob('*'))
               if f.is_file() and f.name!='sha256.json' and '__pycache__' not in f.parts}
    (out/'sha256.json').write_text(json.dumps(checksums,indent=2)+'\n')

if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--final',action='store_true');v=ap.parse_args();materialize(HERE,v.final)
