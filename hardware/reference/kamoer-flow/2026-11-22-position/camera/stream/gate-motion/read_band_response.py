"""Read native optical cup-edge displacement from a compact gate-aligned band recording using NumPy."""
import argparse,csv,json
from pathlib import Path
import numpy as np
def measured(profile,ref_row,absolute_ref,centers,base_sel):
    T,N,H=profile.shape
    base=np.median(profile[base_sel],axis=0)
    # Fixed slope seeds from the focused idle geometry, refined separately in each native band.
    nominal=absolute_ref-.079*(centers-(1730 if centers.mean()>1400 else 1180))-ref_row
    lanes=np.arange(N)
    lane_center=[]
    for i,y in enumerate(nominal):
        k=int(round(y))
        ix=np.arange(k-7,k+8)
        dp=-(base[i,ix+2]-base[i,ix-2])/4
        wt=np.maximum(0,dp)
        lane_center.append(int(round(np.average(ix,weights=wt))) if np.sum(wt)>0 else k)
    ybase=np.array(lane_center)
    offsets=np.arange(-13,16)
    idx=ybase[:,None]+offsets
    ref=base[lanes[:,None],idx]
    ref=ref-ref.mean(axis=1,keepdims=True)
    ref_rms=np.sqrt(np.mean(ref**2,axis=1,keepdims=True))
    ref_norm=ref/np.maximum(ref_rms,1e-9)
    previous=0;results=[]
    ygrid=np.arange(H)
    score_error=[]
    for im in profile:
        candidates=np.arange(previous-10,previous+11,dtype=int)
        inds=idx[None,:,:]+candidates[:,None,None]
        v=im[lanes[None,:,None],np.clip(inds,0,H-1)]
        v=v-v.mean(axis=-1,keepdims=True)
        rms=np.sqrt((v*v).mean(axis=-1,keepdims=True))
        vn=v/np.maximum(rms,.01)
        sq=((vn-ref_norm)**2).mean(axis=-1)
        # A noisy flat patch should not win by correlation alone.
        sq+=np.maximum(0,.35-rms[...,0]/np.maximum(ref_rms[:,0],.1))**2
        cost=np.median(sq,axis=1)
        j=int(np.argmin(cost));previous=int(candidates[j]);d=float(previous)
        if 0<j<len(candidates)-1:
            denom=cost[j-1]-2*cost[j]+cost[j+1]
            if denom>0:d+=float(np.clip(.5*(cost[j-1]-cost[j+1])/denom,-.5,.5))
        idx2=np.clip(ybase[:,None]+previous+np.arange(-9,10)[None,:],3,H-4)
        grad=np.maximum(0,im[lanes[:,None],idx2-3]-im[lanes[:,None],idx2+3])
        centroid=(grad*idx2).sum(axis=1)/np.maximum(grad.sum(axis=1),.01)
        # The alternate is a positive darkening-gradient centroid, recomputed at the tracked edge.
        alt=float(np.median(centroid-ybase))
        bestlanes=candidates[np.argmin(sq,axis=0)]
        results.append([d,alt,float(np.sqrt(cost[j])),float(np.percentile(bestlanes,75)-np.percentile(bestlanes,25)),int(j in (0,len(candidates)-1))])
    out=np.array(results);out[:,:2]-=np.median(out[base_sel,:2],axis=0)
    return out
def read(path):
    with np.load(path,allow_pickle=False) as a:
        desc=json.loads(str(a['description']));times=a['pts_ns'];seq=a['seq'];gs=a['gates'];y0=a['y0']
        centers=a['strip_x0'][:,None]+a['band_width'][:,None]*(.5+np.arange(8)[None,:])
        raw=a['luma_x4'].astype(np.float32)/4
    z=gs[0,0];t=(times-z)/1e9;off=(gs[-1,2]-z)/1e9
    pre=(t>=-.64)&(t<-.08)
    late=(t>=off+1.4)&(t<off+2.1)
    forward=np.stack([measured(raw[:,k],y0[k],desc['pre_y'][k],centers[k],pre) for k in range(2)],axis=1)
    backward=np.stack([measured(raw[::-1,k],y0[k],desc['post_y'][k],centers[k],late[::-1])[::-1] for k in range(2)],axis=1)
    return desc,times,seq,gs,t,off,pre,forward,backward
def stats(desc,t,off,base,q,back):
    sgn=1 if desc['head']=='A' else -1
    def subsection(mask):
        return np.median(q[mask,:,0],axis=0)
    settled=(t>=off+1)&(t<off+2)
    final=subsection(settled)
    base_sd=q[base,:,0].std(axis=0)
    late=(t>=off+1.4)&(t<off+2.1)
    back_start=np.median(back[base,:,0],axis=0)
    back_settled=np.median(back[settled,:,0],axis=0)-back_start
    early=q[:,:,0]
    back_from_start=back[:,:,0]-back_start
    def bat(z):
        return np.array([np.interp(z,t,back[:,k,0]) for k in range(2)])
    gaps=np.diff(t)
    def agree(z):
        return np.array([np.interp(z,t,early[:,k]-back_from_start[:,k]) for k in range(2)])
    def waves(series):
        v=t[(t>=off+.48)&(t<=off+2.1)]-off
        y=series[(t>=off+.48)&(t<=off+2.1)]
        slow=np.column_stack((np.ones(len(v)),v))
        residual=y-slow@np.linalg.lstsq(slow,y,rcond=None)[0]
        sigma=np.mean(residual**2)
        results=[]
        for f in np.arange(1.5,7.01,.05):
            m=np.column_stack((slow,np.sin(2*np.pi*f*v),np.cos(2*np.pi*f*v)))
            pars=np.linalg.lstsq(m,y,rcond=None)[0]
            error=np.sum((y-m@pars)**2)/max(np.sum(residual**2),1e-9)
            results.append((error,f,np.hypot(pars[2],pars[3])))
        err,hz,amp=min(results)
        return dict(fit_hz=round(float(hz),2),amplitude_px=round(float(amp),3),r2_above_linear=round(float(1-err),3),detrended_sd_px=round(float(np.sqrt(sigma)),3))
    def at(z):
        return np.array([np.interp(z,t,q[:,k,0]) for k in range(2)])
    signs=sgn*q[:,:,0]
    good=np.min(signs-np.maximum(.65,base_sd*3),axis=1)>0
    i=[j for j in range(1,len(t)-1) if t[j]>=0 and good[j] and good[j+1]]
    return dict(label=desc['label'],head=desc['head'],on_ms=desc['on_ms'],count=desc['count'],pause_ms=desc['pause_ms'],
                frame_interval_ms=float(np.median(gaps)*1000),frames=len(t),largest_frame_gap_ms=1000*np.max(gaps),
                start_ack_from_tx_ms=None, late_reference='median 1.4–2.1 s after last DONE acknowledgement',
                late_minus_off_px=(-bat(off)).tolist(),late_minus_250ms_after_off_px=(-bat(off+.25)).tolist(),
                late_minus_500ms_after_off_px=(-bat(off+.5)).tolist(),
                late_minus_1000ms_after_off_px=(-bat(off+1)).tolist(),back_settled_from_start=back_settled.tolist(),
                two_direction_difference_100ms=agree(.1).tolist(),two_direction_difference_at_off=agree(off).tolist(),
                late_oscillation=[waves(back[:,k,0]) for k in range(2)],
                first_clear_ms=round(1000*t[i[0]]) if i else None,
                base_sd_px=base_sd.tolist(),at_100ms=at(.1).tolist(),at_200ms=at(.2).tolist(),at_off=at(off).tolist(),
                at_off_plus_100ms=at(off+.1).tolist(),at_off_plus_250ms=at(off+.25).tolist(),
                settled=final.tolist(),settled_alt=np.median(q[settled,:,1],axis=0).tolist(),endpoint=desc['settled_endpoint_delta'],
                settled_vs_endpoint_px=(final-np.array(desc['settled_endpoint_delta'])).tolist(),
                settled_template_residual=np.median(q[settled,:,2],axis=0).tolist(),
                peak_to_peak_400ms=(np.ptp(q[(t>=off)&(t<off+.4),:,0],axis=0)).tolist(),
                endpoint_band_iqr=np.median(q[settled,:,3],axis=0).tolist())
def main():
    a=argparse.ArgumentParser(description=__doc__);a.add_argument('files',nargs='+',type=Path)
    a.add_argument('--out',type=Path)
    opts=a.parse_args()
    if opts.out:opts.out.mkdir(exist_ok=True)
    for f in opts.files:
        desc,times,seq,gs,t,off,pre,results,back=read(f)
        summary=stats(desc,t,off,pre,results,back)
        summary['start_ack_from_tx_ms']=((gs[:,1]-gs[:,0])/1e6).tolist()
        summary['individual_gate_times_from_first_tx_s']=((gs[:,:3]-gs[0,0])/1e9).tolist()
        if opts.out:
            out=opts.out/(f.stem+'.csv')
            with out.open('w',newline='') as z:
                b=csv.writer(z);b.writerow(['seq','pts_ns','from_first_tx_s','from_final_done_ack_s',*[s+'_'+n for s in ['right','mid'] for n in ['from_pre_px','pre_centroid_px','pre_normalized_residual','pre_lane_iqr_px','pre_search_bound','from_late_px','late_centroid_px','late_normalized_residual','late_lane_iqr_px','late_search_bound']]])
                for i in range(len(t)):
                    b.writerow([seq[i],times[i],round(t[i],5),round(t[i]-off,5),*[round(float(z),5) for z in np.concatenate([results[i],back[i]],axis=1).ravel()]])
            (opts.out/(f.stem+'.json')).write_text(json.dumps(summary,indent=2)+'\n')
        print(json.dumps(summary))
if __name__=='__main__':main()
