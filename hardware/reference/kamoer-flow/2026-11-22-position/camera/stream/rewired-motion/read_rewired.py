"""Read the independent upper-rim trajectory at native and preview sightlines after reconfiguration."""
import argparse,csv,json
from pathlib import Path
import numpy as np
def locate(samples,ys,xs,reference,ref_y,previous=None):
    # The upper lip, rising gently toward the right, is distinct from the lower wall contact.
    nominal=np.interp(xs,[1400,1500,1650,1730,1860,1980],[896,890,882,879,871,869])
    pos=np.arange(-12,14)
    base=[]
    for band,r in enumerate(reference):
        y=nominal[band];grid=np.arange(round(y)-7,round(y)+8)
        gradient=np.interp(grid-3,ref_y,r)-np.interp(grid+3,ref_y,r)
        center=grid[np.argmax(gradient)]
        base.append(center)
    base=np.asarray(base)
    raw_ref=np.array([np.interp(z+pos,ref_y,r) for z,r in zip(base,reference)])
    raw_ref-=raw_ref.mean(1,keepdims=True);raw_ref/=np.maximum(.05,raw_ref.std(1,keepdims=True))
    shifts=np.arange(-38,39,.25)
    query=base[None,:,None]+shifts[:,None,None]+pos[None,None,:]
    step=np.median(np.diff(ys));idx=(query-ys[0])/step
    floor=np.clip(np.floor(idx).astype(int),0,len(ys)-2);w=idx-floor
    lanes=np.arange(len(xs))[None,:,None];results=[]
    for frame in samples:
        match=frame[lanes,floor]*(1-w)+frame[lanes,floor+1]*w
        match-=match.mean(2,keepdims=True);match/=np.maximum(.05,match.std(2,keepdims=True))
        cost=np.mean((match-raw_ref)**2,axis=2)
        fusion=np.median(cost,axis=1)
        eligible=np.ones(len(shifts),bool) if previous is None else abs(shifts-previous)<14.
        j=np.flatnonzero(eligible)[int(np.argmin(fusion[eligible]))];d=shifts[j]
        byband=shifts[np.argmin(np.where(eligible[:,None],cost,np.inf),axis=0)]
        iqr=float(np.percentile(byband,75)-np.percentile(byband,25))
        results.append([d,float(np.sqrt(fusion[j])),iqr]);previous=d
    return np.asarray(results),base
def read(path):
    out={}
    with np.load(path,allow_pickle=False) as d:
        meta=json.loads(str(d['description']))
        for name in ['native','preview']:
            ticks=d[name+'_pts_ns']
            if not len(ticks):continue
            frames=d[name+('_luma_x4' if name=='native' else '_luma')].astype(np.float32)/(4. if name=='native' else 1.)
            q,base=locate(frames,d[name+'_y'],d[name+'_x'],d[name+'_reference'],d['reference_y'])
            t=(ticks-meta['tx_ns'])/1e9;off=(meta['done_ack_ns']-meta['tx_ns'])/1e9
            pre=(t>=-.65)&(t<-.03);rel=q[:,0]-np.median(q[pre,0])
            rec={'x':d[name+'_x'].tolist(),'reference_rim_y':base.tolist(),'median_sensor_dt_ms':1000*np.median(np.diff(t)),'initial_from_reference_px':np.median(q[pre,0]),'pulse_timing':'time relative to command transmission and controller completion',
                 'pre_frame_sd_px':np.std(rel[pre]),'at_done_px':np.interp(off,t,rel)}
            for z in [0.1,0.25,0.5,1.,2.,4.,8.]:
                sel=(t>=off+z-.09)&(t<=off+z+.09)
                if sel.any():rec[f'done_plus_{z:g}s_px']=float(np.median(rel[sel]))
            out[name]=(rec,np.column_stack([d[name+'_seq'],ticks,t,t-off,q[:,0],rel,q[:,1:]]))
    return meta,out
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('files',nargs='+',type=Path);p.add_argument('--out',type=Path,required=True);args=p.parse_args();args.out.mkdir(exist_ok=True)
    for f in args.files:
        base=args.out/f.stem
        if base.with_suffix('.json').exists():continue
        meta,sites=read(f);summary={}
        for name,(rec,data) in sites.items():
            summary[name]=rec
            np.savetxt(args.out/(f.stem+'-'+name+'.csv'),data,delimiter=',',fmt=['%d','%d','%.5f','%.5f','%.4f','%.4f','%.4f','%.4f'],header='seq,pts_ns,from_tx_s,from_done_s,offset_from_constant_reference_px,offset_from_pre_px,shape_residual,band_iqr_px',comments='')
        base.with_suffix('.json').write_text(json.dumps(dict(gate=meta,sightlines=summary),indent=2)+'\n')
