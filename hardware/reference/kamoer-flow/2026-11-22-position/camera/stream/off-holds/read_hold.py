"""Replay the wet edge and dry printed marks during an unpowered hold using native luma profiles."""
import argparse,json
from pathlib import Path
import numpy as np
def offset(src,obs):
    # Evaluate all trial shifts on exact native rows, then refine the best integer cost subpixel.
    src=src.astype(float);obs=obs.astype(float);H=src.shape[-1]
    rad=13;ds=np.arange(-5,6);ii=np.arange(H//2-rad,H//2+rad+1)
    ref=src[...,ii]
    contrast=ref.std(axis=-1)
    norm=(ref-ref.mean(axis=-1,keepdims=True))/np.maximum(.005,contrast[...,None])
    v=obs[...,ii[None,:]+ds[:,None]]
    v-=v.mean(axis=-1,keepdims=True);v/=np.maximum(.005,v.std(axis=-1,keepdims=True))
    costs=np.mean((v-norm[...,None,:])**2,axis=-1)
    j=np.argmin(costs,axis=-1);jm=np.maximum(0,j-1);jp=np.minimum(len(ds)-1,j+1)
    def at(idx):return np.take_along_axis(costs,idx[...,None],axis=-1)[...,0]
    a,b,c=at(jm),at(j),at(jp);curv=a-2*b+c
    # Search interpolated native luma near the integer match. Identical profiles register at exactly zero.
    base=ds[j]
    f=np.arange(-.65,.651,.025)
    dd=base[...,None]+f
    floor=np.floor(dd).astype(int)
    w=(dd-floor)[...,None]
    target_indices=ii+floor[...,None]
    v0=np.take_along_axis(obs[...,None,:],target_indices,axis=-1)
    v1=np.take_along_axis(obs[...,None,:],target_indices+1,axis=-1)
    vals=v0*(1-w)+v1*w
    vals-=vals.mean(axis=-1,keepdims=True)
    vals/=np.maximum(.005,vals.std(axis=-1,keepdims=True))
    resids=np.mean((vals-norm[...,None,:])**2,axis=-1)
    jj=np.argmin(resids,axis=-1)
    z=np.take_along_axis(dd,jj[...,None],axis=-1)[...,0]
    z[(j==0)|(j==len(ds)-1)|(contrast<.75)]=np.nan
    return z,contrast,np.sqrt(b)
def read(path):
    with np.load(path,allow_pickle=False) as d:
        info=json.loads(str(d['details']));ix=d['window']
        contact=d['luma_x4']/4;marks=d['dry_x4']/4;tm=d['pts_ns']
        a0=np.mean(contact[ix==0],axis=0);m0=np.mean(marks[ix==0],axis=0)
        out=[]
        for i,z in enumerate(info['windows_from_done_s']):
            co=contact[ix==i];mk=marks[ix==i]
            e,contrast,resid=offset(a0,co.mean(axis=0));dry,dry_amplitude,dry_resid=offset(m0,mk.mean(axis=0))
            # These bands fall within the calibrated front graduation strokes at each sightline.
            mid=[np.array([5,6,7]),np.array([1,2,3])]
            markshift=np.array([np.nanmedian(dry[k][:,mid[k]],axis=1) for k in range(2)])
            ink=np.array([np.interp(info['reference_rows'][k],info['mark_centers_y'][k],markshift[k]) for k in range(2)])
            # Keep per-mark estimates to inspect vertical translation and tilt separately.
            fr=[offset(a0,v)[0] for v in co]
            es=np.nanmedian(e,axis=1)
            out.append(dict(from_done_s=round((np.mean(tm[ix==i])-info['done_ns'])/1e9,3),frames=len(co),
               raw_shift_px=es.tolist(),native_lane_iqr_px=(np.nanpercentile(e,75,axis=1)-np.nanpercentile(e,25,axis=1)).tolist(),
               frame_sd_px=np.nanstd(np.nanmedian(fr,axis=2),axis=0).tolist(),dry_mark_shifts_px=markshift.tolist(),
               dry_relative_shift_px=(es-ink).tolist(),dry_point_contrast_y8=[dry_amplitude[k][:,mid[k]].tolist() for k in range(2)],
               template_residual=np.median(resid,axis=1).tolist()))
    return dict(label=info['label'],head=info['head'],gate_ms=info['gate_ms'],unpowered_s=info['unpowered_s'],windows=out)
if __name__=='__main__':
 a=argparse.ArgumentParser(description=__doc__);a.add_argument('files',type=Path,nargs='+');a.add_argument('--out',type=Path)
 q=a.parse_args();res={f.stem:read(f) for f in q.files}
 if q.out:q.out.write_text(json.dumps(res,indent=2)+'\n')
 else:print(json.dumps(res,indent=2))
