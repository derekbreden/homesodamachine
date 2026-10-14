#!/usr/bin/env python3
"""Render the can routine and studio shots, then assemble the connected story."""
import argparse
import json
from pathlib import Path
import shutil
import subprocess

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--fps',type=int,default=24,help='Source cadence for product portraits')
p.add_argument('--pour-fps',type=int,default=24,help='Native cadence for moving fluid')
p.add_argument('--width',type=int,default=1920)
p.add_argument('--samples',type=int,default=32)
p.add_argument('--chunk-frames',type=int,default=32,help='Maximum source frames per Blender process;0 renders a whole shot')
p.add_argument('--shots',nargs='+',choices=['case','car','kitchen','shelf','repeat','question','hero','pour','serve'])
p.add_argument('--fresh',action='store_true')
p.add_argument('--blender',default=shutil.which('blender') or '/Applications/Blender.app/Contents/MacOS/Blender')
p.add_argument('--picture-only',action='store_true')
p.add_argument('--finish-only',action='store_true')
p.add_argument('--draft',action='store_true',help='Use the faster finishing encoder')
a=p.parse_args()
story=json.loads((HERE/'story.json').read_text())
out=HERE/'out';out.mkdir(exist_ok=True)
shots=[s for s in story['scenes'] if s['kind'] in ('studio','can')]
rates={s['id']:a.pour_fps if s['id']=='pour' else a.fps for s in shots}
frames=out/'frames'/f'story-loop-{a.fps}-{a.pour_fps}fps-{a.width}px-{a.samples}spp'
(out/'render-plan.json').write_text(json.dumps({'width':a.width,'height':round(a.width*9/16),
 'samples':a.samples,'source_fps':rates,'frames':str(frames.relative_to(HERE)),
 'delivery_fps':24,'duration':story['duration'],'max_frames_per_process':a.chunk_frames},indent=2)+'\n')

def run(command):
    print('RUN '+' '.join(map(str,command)),flush=True)
    subprocess.run(list(map(str,command)),cwd=ROOT,check=True)

if not a.finish_only:
    # Bounded Blender lifetimes keep the GPU render responsive on the render host.
    for shot,rate in rates.items():
        if a.shots and shot not in a.shots:continue
        if a.fresh and (frames/shot).exists():shutil.rmtree(frames/shot)
        scene=next(item for item in shots if item['id']==shot)
        stage=HERE/('can_stage.py' if scene['kind']=='can' else 'stage.py')
        count=1 if scene.get('hold') else round((scene['end']-scene['start'])*rate)
        chunk=a.chunk_frames if a.chunk_frames>0 else count
        for start in range(0,count,chunk):
            end=min(count,start+chunk)
            if all((frames/shot/f'{i:05d}.png').exists() for i in range(start,end)):continue
            run([a.blender,'--background','--factory-startup','--python-exit-code','1','--python',stage,'--',
                 '--shots',shot,'--fps',rate,'--width',a.width,'--samples',a.samples,'--frames-root',frames,
                 '--start-frame',start,'--end-frame',end])
if not a.picture_only:
    runtime=ROOT/'tools/video-venv/bin/python'
    run([runtime,HERE/'audio.py'])
    run([runtime,HERE/'finish.py','--fps',a.fps,'--source-fps',f'pour={a.pour_fps}','--frames',frames,
         *(['--draft'] if a.draft else [])])
