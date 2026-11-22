"""Compare dry printed-cup motion with the simultaneously photographed liquid during representative metered pours."""
import argparse
import bisect
import json
import sys
from pathlib import Path

import numpy as np
from read_pour_timings import wave

def read_recording(path):
    with np.load(path) as z:
        values=z['dry_luma_x4'].astype(float)*.25;reference=z['dry_reference'];pts=z['pts_ns']
        meta=json.loads(str(z['metadata']))
    shifts=np.arange(-6,7);offsets=np.arange(-8,9);center=17
    results={}
    for j,side in enumerate(('printed_thirds','printed_quarters')):
        patches=[]
        for k in range(values.shape[2]):
            ref=reference[j,k,center+offsets];ref=ref-ref.mean();rnorm=np.linalg.norm(ref)
            if rnorm<5:continue
            samples=values[:,j,k,:,][:,center+shifts[:,None]+offsets[None,:]]
            samples-=samples.mean(axis=2,keepdims=True)
            corr=np.sum(samples*ref[None,None,:],axis=2)/np.maximum(rnorm*np.linalg.norm(samples,axis=2),.001)
            patches.append(corr)
        if len(patches)<2:continue
        fusion=np.median(patches,axis=0);idx=np.argmax(fusion,axis=1);row=np.arange(len(idx));j0=np.clip(idx,1,len(shifts)-2)
        left=fusion[row,j0-1];mid=fusion[row,j0];right=fusion[row,j0+1]
        off=np.clip((right-left)/np.maximum(2*(2*mid-left-right),1e-6),-.5,.5)
        delta=shifts[idx]+off
        estimate=wave({'pts_ns':pts,side+'_shift_px':delta},side,meta['last_modeled_motor_off_ns'])
        during=(pts>=meta['start_ack_ns'])&(pts<=meta['done_ack_ns']+0.5e9)
        results[side]={'patches':len(patches),'median_shape_correlation_during':float(np.median(mid[during])),
                       'movement_10_to_90_px':float(np.percentile(delta[during],90)-np.percentile(delta[during],10)),
                       'post_motor_harmonic':estimate}
    return results

def pack(root):
    sys.path.append('/opt/homebrew/lib/python3.13/site-packages')
    from PIL import Image
    from timing_window import Source
    source=Source(root);timeline=json.loads((root/'evidence/appliance-timeline.json').read_text())
    image=np.asarray(Image.open(root/'windows/station-idle/average.png'),dtype=float)
    with np.load(source.files[0]) as z:sites=z['slices']
    boxes=[];reference=[]
    for j,(lanes,priors) in enumerate([([5,6],[551,765]),([1,2],[553,691])]):
        unit=(sites[j,1]-sites[j,0])//8;ba=[];ref=[]
        for y in priors:
            for lane in lanes:
                x=sites[j,0]+lane*unit;raw=image[:,x:x+unit].mean(axis=1)
                area=np.arange(y-12,y+13);at=int(area[np.argmax(abs(raw[area-2]-raw[area+2]))])
                ba.append([int(j),lane,int(x),int(x+unit),at]);ref.append(raw[at-17:at+18])
        boxes.append(ba);reference.append(ref)
    dest=root/'evidence/dry-waves';dest.mkdir(exist_ok=True);summary=dest/'results.json'
    results=json.loads(summary.read_text()) if summary.is_file() else {}
    for r in timeline['pours']:
        pred=r['prediction']
        original=(pred.get('phase')=='validation' and pred.get('block')==1 and pred.get('scenario') in ('full_glass','partial_glass','same_open_time','release_reopen'))
        reserved=(r['journal']=='fresh.jsonl' and pred.get('block')==1 and pred.get('scenario') in ('near_full_glass','short_richer_pour'))
        if not r['trial'] or not (original or reserved or r['journal']=='fill.jsonl'):continue
        path=dest/(r['event_label']+'.npz')
        if path.is_file() and path.stem in results:continue
        if not path.exists():
            begin=r['start_ack_ns']-700_000_000;end=r['done_ack_ns']+3_100_000_000
            lo=max(0,bisect.bisect_left(source.pts,begin)-1);hi=min(len(source.pts)-1,bisect.bisect_right(source.pts,end))
            fs=source.files[max(0,bisect.bisect_right(source.first_seq,source.clock[lo][1])-1):bisect.bisect_right(source.first_seq,source.clock[hi][1])]
            dy=[];ts=[];seq=[]
            for f in fs:
                with np.load(f) as z:
                    ticks=z['pts_ns'];keep=(ticks>=begin)&(ticks<=end)
                    if not keep.any():continue
                    samples=z['profiles'][keep];cols=[]
                    for site in boxes:
                        bounds=[samples[:,j,lane,at-17-450:at+18-450] for j,lane,_,_,at in site];cols.append(np.stack(bounds,axis=1))
                    dy.append(np.stack(cols,axis=1));ts.append(ticks[keep]);seq.append(z['seq'][keep])
            if not ts or ts[0][0]>begin+200e6 or ts[-1][-1]<end-200e6:continue
            meta={'head':r['head'],'program':pred['scenario'],'start_ack_ns':r['start_ack_ns'],'done_ack_ns':r['done_ack_ns'],
                  'last_modeled_motor_off_ns':r['start_ack_ns']+sum(r['predicted_switches_ms'][-1])*1_000_000,'label':r['event_label']}
            np.savez_compressed(path,dry_luma_x4=np.concatenate(dy),dry_reference=np.array(reference),sensor_boxes=np.array(boxes),
                                pts_ns=np.concatenate(ts),seq=np.concatenate(seq),metadata=np.asarray(json.dumps(meta)))
        results[path.stem]=read_recording(path)
    temp=dest/'results.partial';temp.write_text(json.dumps(results,indent=2)+'\n');temp.replace(summary)
    return results

if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('recordings',nargs='*',type=Path);ap.add_argument('--pack-camera',type=Path);ap.add_argument('--out',type=Path)
    a=ap.parse_args();r=pack(a.pack_camera) if a.pack_camera else {f.stem:read_recording(f) for f in a.recordings}
    txt=json.dumps(r,indent=2)+'\n'
    if a.out:a.out.write_text(txt)
    elif not a.pack_camera:print(txt,end='')
