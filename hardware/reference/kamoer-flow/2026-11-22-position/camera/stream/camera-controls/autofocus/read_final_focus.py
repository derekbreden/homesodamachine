"""Measure fixed-focus repeatability, autofocus, dry ink sharpness and upper-rim position at constant fill."""
from pathlib import Path
import argparse,json
import numpy as np
from PIL import Image
def box(a,x0,y0,w,h,offset):
    return a[y0-offset[1]:y0+h-offset[1],x0-offset[0]:x0+w-offset[0]]
def fit(reference,obs,center,half=14,span=18):
    t=np.arange(int(round(center))-half,int(round(center))+half+1)
    if t.min()<0 or t.max()>=len(reference):return None
    ref=reference[t];ref=ref-ref.mean()
    if np.std(ref)<.006:return None
    ref/=ref.std()
    ds=np.arange(-span,span+.001,.05);sm=np.interp(t+ds[:,None],np.arange(len(obs)),obs)
    sm-=sm.mean(1,keepdims=True);sm/=np.maximum(.0001,sm.std(1,keepdims=True))
    cost=np.mean((sm-ref)**2,axis=1);i=int(np.argmin(cost))
    if i in (0,len(ds)-1):return None
    return float(ds[i]),float(np.sqrt(cost[i]))
def redness(im):
    r,g,b=np.moveaxis(im.astype(float),2,0)
    return (r-np.maximum(g,b))/(r+g+b+18)
def ink_geometry(reference,observed,origin):
    """Locate dry printed patches in both dimensions and fit their common affine image motion."""
    half,search=22,33
    entries=[]
    for y in range(half+search,reference.shape[0]-half-search,26):
        for x in range(half+search,reference.shape[1]-half-search,28):
            tile=reference[y-half:y+half+1,x-half:x+half+1]
            if np.std(tile)<.027 or np.percentile(tile,90)<.04:continue
            region=observed[y-half-search:y+half+search+1,x-half-search:x+half+search+1]
            h,w=tile.shape;zero=tile-tile.mean()
            ft=np.fft.rfft2(region)
            cross=np.fft.irfft2(ft*np.conj(np.fft.rfft2(zero,s=region.shape,axes=(0,1))),s=region.shape,axes=(0,1))
            cross=cross[:region.shape[0]-h+1,:region.shape[1]-w+1]
            def local_sum(val):
                integ=np.pad(np.cumsum(np.cumsum(val,axis=0),axis=1),((1,0),(1,0)))
                return integ[h:,w:]-integ[:-h,w:]-integ[h:,:-w]+integ[:-h,:-w]
            variance=local_sum(region*region)-local_sum(region)**2/(w*h)
            cor=cross/np.sqrt(np.maximum(variance*np.sum(zero*zero),1e-14))
            iy,ix=np.unravel_index(np.argmax(cor),cor.shape);peak=cor[iy,ix]
            if iy in (0,cor.shape[0]-1) or ix in (0,cor.shape[1]-1) or peak<.82:continue
            def subpix(left,mid,right):
                den=2*(2*mid-left-right)
                return (right-left)/den if den>1e-8 else 0.
            dx=ix-search+subpix(cor[iy,ix-1],peak,cor[iy,ix+1])
            dy=iy-search+subpix(cor[iy-1,ix],peak,cor[iy+1,ix])
            entries.append([x+origin[0],y+origin[1],dx,dy,peak])
    if len(entries)<6:return {'matched_patches':len(entries)}
    e=np.asarray(entries);design=np.c_[np.ones(len(e)),e[:,0]-1400,e[:,1]-500];keep=np.ones(len(e),dtype=bool)
    for _ in range(6):
        if keep.sum()<6:break
        coef=np.linalg.lstsq(design[keep],e[keep,2:4],rcond=None)[0]
        err=np.linalg.norm(design@coef-e[:,2:4],axis=1)
        typical=np.median(err[keep]);dev=np.median(abs(err[keep]-typical))
        update=err<max(1.,typical+3*1.4826*dev)
        if np.array_equal(update,keep) or update.sum()<6:break
        keep=update
    e=e[keep];coef=np.linalg.lstsq(design[keep],e[:,2:4],rcond=None)[0]
    err=np.linalg.norm(design[keep]@coef-e[:,2:4],axis=1)
    return dict(matched_patches=len(entries),affine_inliers=len(e),median_correlation=float(np.median(e[:,4])),
                median_residual_px=float(np.median(err)),reference_xy_bounds=[e[:,:2].min(axis=0).tolist(),e[:,:2].max(axis=0).tolist()],
                shift_at_x1400_y500_px=coef[0].tolist(),horizontal_and_vertical_scale=(1+np.diag(coef[1:])).tolist(),
                shift_affine_coefficients_at_x1400_y500=coef.tolist())
def run(folder):
    index=json.loads((folder/'index.json').read_text());ink_rect=index['rectangles_ltrb']['ink'];rim_rect=index['rectangles_ltrb']['rim']
    baseline=redness(np.asarray(Image.open(folder/'final-focus-fixed-ink.png')))
    baseline_rim=np.asarray(Image.open(folder/'final-focus-fixed-rim.png')).astype(float)
    old=np.asarray(Image.open(folder/'starting-rim-reference.png')).astype(float)
    regions=[(1005,373,200,90),(1470,283,330,76),(1040,513,185,88),(1520,511,248,94),(1055,625,202,98)]
    x_sets=[np.arange(1400,1501,10),np.arange(1860,1981,10)]
    allstats={}
    for label in index['stages']:
        ink=redness(np.asarray(Image.open(folder/(label+'-ink.png'))));rim=np.asarray(Image.open(folder/(label+'-rim.png'))).astype(float)
        features=[];shifts=[];ink_q=[]
        for x,y,w,h in regions:
            ref=box(baseline,x,y,w,h,ink_rect);obs=box(ink,x,y,w,h,ink_rect)
            # Normalized central-difference energy is a sharpness measure on fixed dry ink regions.
            dx=(obs[1:-1,2:]-obs[1:-1,:-2])*.5;dy=(obs[2:,1:-1]-obs[:-2,1:-1])*.5
            score=float(np.sqrt(np.mean(dx*dx+dy*dy))/max(.00001,obs.std()))
            features.append(score)
            for cx in np.arange(22,w-22,12):
                a=ref[:,cx-3:cx+4].mean(1);b=obs[:,cx-3:cx+4].mean(1);yy=16+int(np.argmax(a[16:-16]))
                z=fit(a,b,yy,12,13)
                if z and z[1]<.65:shifts.append(z[0]);ink_q.append(z[1])
        rims=[]
        for xx in x_sets:
            zs=[]
            for x in xx:
                j=x-rim_rect[0];ref=old[:,j-4:j+5].mean(axis=1);start=baseline_rim[:,j-4:j+5].mean(axis=1);a=rim[:,j-4:j+5].mean(axis=1)
                center=np.interp(x,[1400,1500,1860,1980],[896,890,871,869])-rim_rect[1];ys=np.arange(round(center)-7,round(center)+8)
                seed=ys[np.argmax(ref[ys-3]-ref[ys+3])]
                init=fit(ref,start,seed,12,34)
                if not init:continue
                z=fit(start,a,seed+init[0],12,35)
                if z is not None:zs.append(z)
            q=np.array(zs)
            rims.append(dict(x_station=int(np.median(xx)),valid_bands=len(q),shift_px=float(np.median(q[:,0])) if len(q) else None,
                             quantiles_15_85_px=np.percentile(q[:,0],[15,85]).tolist() if len(q) else [],
                             normalized_rms=float(np.median(q[:,1])) if len(q) else None))
        allstats[label]=dict(dry_ink_sharpness_per_region=features,dry_ink_sharpness_median=float(np.median(features)),
             dry_mark_shift_px=float(np.median(shifts)),dry_mark_shift_quantiles_15_85_px=np.percentile(shifts,[15,85]).tolist(),dry_marks_count=len(shifts),
             dry_ink_affine=ink_geometry(baseline,ink,ink_rect[:2]),upper_rim=rims)
    return allstats
if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('folder',type=Path);ap.add_argument('--out',type=Path);v=ap.parse_args()
    txt=json.dumps(run(v.folder),indent=2)+'\n'
    if v.out:v.out.write_text(txt)
    else:print(txt,end='')
