"""Retain timestamped front-wall pixel strips and compare their motion with the two photographed volume sightlines."""
import argparse
import bisect
import json
from pathlib import Path
import numpy as np

SITES=('x990','x1986')
COLUMNS=np.asarray([984,990,996,1980,1986,1992])


def pack(camera):
    table=json.loads((camera/'evidence/appliance-timeline.json').read_text())
    output=camera/'evidence/front-wall'
    output.mkdir(exist_ok=True)
    source=sorted((camera/'front-preview').glob('[0-9]*.npz'))
    starts=[]
    for path in source:
        with np.load(path) as f:starts.append(int(f['pts_ns'][0]))
    catalog={}
    for pour in table['pours']:
        trial=pour['trial']
        if not trial:continue
        label=pour['event_label'];dest=output/(label+'.npz')
        if dest.is_file():
            catalog[label]=dest.name
            continue
        t0=pour['start_ack_ns']-700_000_000;t1=pour['done_ack_ns']+3_100_000_000
        frames=[];clock=[];sequences=[]
        for path in source[max(0,bisect.bisect_right(starts,t0)-1):bisect.bisect_right(starts,t1)]:
            with np.load(path) as f:
                times=f['pts_ns'];take=(times>=t0)&(times<=t1)
                if not take.any():continue
                cols=np.searchsorted(f['sensor_x'],COLUMNS)
                if not np.array_equal(f['sensor_x'][cols],COLUMNS):raise ValueError('Missing front-wall column')
                full_rows=f['sensor_y'];ykeep=(full_rows>=708)&(full_rows<=1200);rows=full_rows[ykeep]
                frames.append(f['luma'][take][:,ykeep,:][:,:,cols]);clock.append(times[take]);sequences.append(f['seq'][take])
        if not clock or clock[0][0]>t0+200_000_000 or clock[-1][-1]<t1-200_000_000:
            catalog[label]=None
            continue
        temporary=dest.with_suffix('.partial')
        with temporary.open('wb') as target:
            np.savez_compressed(target,luma=np.concatenate(frames),pts_ns=np.concatenate(clock),seq=np.concatenate(sequences),
                                sensor_y=rows,sensor_x=COLUMNS,pour_label=np.asarray(label))
        temporary.replace(dest);catalog[label]=dest.name
    (output/'index.json').write_text(json.dumps(catalog,indent=2)+'\n')
    print(sum(bool(v) for v in catalog.values()),'front-wall recordings for',len(catalog),'scored pours')



def track(image,rows,pilot,ts,start):
    intensity=image.mean(axis=2)
    smooth=.15*np.roll(intensity,1,axis=1)+.70*intensity+.15*np.roll(intensity,-1,axis=1)
    gradient=np.roll(smooth,1,axis=1)-np.roll(smooth,-1,axis=1)
    below=np.stack([np.roll(smooth,-k,axis=1) for k in range(3,10)])
    floor=np.quantile(smooth,.07,axis=1)
    contrast=gradient.clip(0)/(1+(np.ptp(below,axis=0)/5)**1.2)
    contrast/=1+((below.mean(axis=0)-floor[:,None]-1).clip(0)/7)**1.2
    candidates=np.flatnonzero((abs(rows-pilot)<=140)&(np.arange(len(rows))>=2)&(np.arange(len(rows))<len(rows)-9))
    heights=rows[candidates];steps=(heights[:,None]-heights[None,:])/6
    dynamic=-((heights-pilot)/5)**2
    backlinks=[]
    for i,tick in enumerate(ts):
        dt=np.clip((tick-ts[i-1])*1e-9,.06,.5) if i else .1
        transitions=-.9*(steps*.1/dt)**2
        transitions[abs(steps)>3*dt/.1]=-1e10
        competing=dynamic[:,None]+transitions
        parent=competing.argmax(axis=0)
        dynamic=competing[parent,np.arange(len(candidates))]+np.log1p(contrast[i,candidates])
        if tick<start-80_000_000:
            dynamic-=((heights-pilot)/8)**2
        backlinks.append(parent)
    choice=int(dynamic.argmax());selected=np.empty(len(ts),dtype=int)
    for i in range(len(ts)-1,-1,-1):
        selected[i]=candidates[choice];choice=backlinks[i][choice]
    vicinity=selected[:,None]+np.arange(-1,2)[None,:]
    weights=gradient[np.arange(len(ts))[:,None],vicinity]
    weights=np.maximum(weights-.2*weights.max(axis=1,keepdims=True),.001)
    position=(weights*rows[vicinity]).sum(axis=1)/weights.sum(axis=1)
    return position,contrast[np.arange(len(ts)),selected]

def score(timeline,folder):
    output=[]
    for p in timeline['pours']:
        tt=p.get('trial') or {}
        if not tt.get('pre_cup') or not tt.get('post_cup'):continue
        f=folder/(p['event_label']+'.npz')
        if not f.is_file():continue
        with np.load(f) as z:
            ts=z['pts_ns'];rows=z['sensor_y'];image=z['luma']
        beginning=p['start_ack_ns'];end=p['done_ack_ns']
        last_zero=[m['transmitted_ns'] for m in p['meter_stages'] if not m['pulses']][-1]
        def window(t,lo,hi):
            return (ts>=t+lo*1e9)&(ts<t+hi*1e9)
        intervals={'pre':window(beginning,-.58,-.08),'release':window(last_zero,-.20,.04),
                   'closure':window(end,-.17,.17),'settled':window(end,2.35,3.10)}
        record={'label':p['event_label'],'head':p['head'],'journal':p['journal'],'scenario':p['prediction'].get('scenario'),
                'level':p['prediction'].get('level') or tt.get('level'),'block':p['prediction'].get('block'),
                'frames':len(ts),'median_interval_ms':float(np.median(np.diff(ts))*1e-6),'maximum_interval_ms':float(np.max(np.diff(ts))*1e-6),
                'sample_counts':{k:int(v.sum()) for k,v in intervals.items()},'sites':{}}
        if all(np.any(m) for m in intervals.values()):
            for i,site in enumerate(SITES):
                photo_start=tt['pre_cup'][site]['row'];photo_finish=tt['post_cup'][site]['row']
                delta,quality=track(image[:,:,i*3:i*3+3],rows,photo_start,ts,beginning)
                signed=1 if p['head']=='A' else -1
                shifts={k:signed*float(np.median(delta[m])-np.median(delta[intervals['pre']])) for k,m in intervals.items()}
                official=signed*(photo_finish-photo_start)
                record['sites'][site]={'signed_native_photo_endpoint_px':official,'signed_front_wall_px':shifts,
                    'settled_minus_photo_px':shifts['settled']-official,'release_to_closure_px':shifts['closure']-shifts['release'],
                    'median_local_edge_score':float(np.median(quality)),'minimum_local_edge_score':float(np.min(quality))}
        output.append(record)
    return {'method':'Front-wall native luma is sampled at three upright columns about each volume sightline with a six-row sensor pitch. The pre-pour photographed contact seeds a continuous sequence of downward intensity transitions into uniformly dark liquid. The path scores all frames using their time spacing, direction-independent smoothness and local contrast. The post-pour photograph supplies only the separate endpoint error. Positions, including fractional estimates, are in native sensor pixels. Camera stamps determine the measured phase windows.','trials':output}


if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__);sub=ap.add_subparsers(dest='action',required=True)
    collect=sub.add_parser('pack');collect.add_argument('camera',type=Path)
    run=sub.add_parser('score');run.add_argument('timeline',type=Path);run.add_argument('recordings',type=Path);run.add_argument('--out',type=Path,required=True)
    v=ap.parse_args()
    if v.action=='pack':pack(v.camera)
    else:v.out.write_text(json.dumps(score(json.loads(v.timeline.read_text()),v.recordings),indent=2,allow_nan=False)+'\n')
