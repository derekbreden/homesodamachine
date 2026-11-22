"""Reproduce upper-rim direction and dry-tube silhouette movement from compact rewire qualification captures."""
import argparse,json
import numpy as np
from pathlib import Path
def rimshift(a,b,grid,y):
    ii=np.arange(round(y)-12,round(y)+14)
    r=np.interp(ii,grid,a);r=(r-r.mean())/max(.01,r.std())
    choices=np.arange(-45,45.01,.1)
    ans=np.interp(ii+choices[:,None],grid,b);ans-=ans.mean(1,keepdims=True);ans/=np.maximum(.01,ans.std(1,keepdims=True))
    cost=np.mean((ans-r)**2,axis=1);j=int(np.argmin(cost))
    return choices[j],np.sqrt(cost[j])
def tube(pre,post,rows,start_x,which):
    track=[]
    rough=930+.43*rows if which=='diagonal' else 1400+.42*rows-.00030*rows*rows
    for y,a,b,target in zip(rows,pre,post,rough):
        xx=np.arange(round(target)-35,round(target)+36)-start_x
        peak=.5*(np.mean(a[xx[:,None]+np.arange(-40,-24)],axis=1)+np.mean(a[xx[:,None]+np.arange(24,40)],axis=1))-np.mean(a[xx[:,None]+np.arange(-10,11)],axis=1)
        ctr=int(xx[np.argmax(peak)])
        if max(peak)<9:continue
        ii=np.arange(ctr-32,ctr+33);r=a[ii];r=(r-r.mean())/max(.01,r.std())
        choices=np.arange(-100,131);v=b[ii+choices[:,None]];v-=v.mean(1,keepdims=True);v/=np.maximum(.01,v.std(1,keepdims=True))
        cost=np.mean((r-v)**2,axis=1);j=int(np.argmin(cost))
        if j in (0,len(choices)-1) or cost[j]>.4:continue
        af,bf,cf=cost[j-1:j+2];curv=af-2*bf+cf
        dx=float(choices[j])+(.5*(af-cf)/curv if curv>0 else 0.)
        track.append((y,dx))
    tr=np.array(track)
    return {'dry_rows':len(tr),'median_dx':float(np.median(tr[:,1])),'median_dx_at_rows_245_to_329':float(np.median(tr[(tr[:,0]>=245)&(tr[:,0]<335),1]))}
def read(path):
    with np.load(path,allow_pickle=False) as d:
        meta=json.loads(str(d['description']));x=d['rim_x'];y=d['rim_y']
        prior=d['reference_rim_sum']/9;pre=d['pre_rim_sum']/9;post=d['post_rim_sum']/9
        selected=np.interp(x,[1400,1500,1650,1730,1860,1980],[896,890,882,879,871,869])
        allrows=[]
        for r,a,b,guess in zip(prior,pre,post,selected):
            ys=np.arange(round(guess)-7,round(guess)+8);g=(np.interp(ys-3,y,r)-np.interp(ys+3,y,r))/6
            seed=ys[np.argmax(g)]
            loc,score=rimshift(r,a,y,seed)
            delta,err=rimshift(a,b,y,seed+loc)
            allrows.append((seed+loc,delta,err))
        q=np.array(allrows)
        seg={}
        for key,pick in [('inner_clear',x<1550),('intermediate',((x>1550)&(x<1800))),('outer_clear',x>1800)]:
            z=q[pick]
            seg[key]={'x_center':float(np.median(x[pick])),'bands':int(np.sum(pick)),'start_upper_rim_y':float(np.median(z[:,0])),'delta_y':float(np.median(z[:,1])),'quantiles_15_85_px':np.percentile(z[:,1],[15,85]).tolist(),'median_normalized_residual':float(np.median(z[:,2]))}
        tubes={k:tube(d['pre_dry_sum']/5,d['post_dry_sum']/5,d['dry_y'],int(d['dry_x0']),k) for k in ['diagonal','upright']}
    return dict(label=meta['label'],rim=seg,tubes=tubes)
if __name__=='__main__':
    a=argparse.ArgumentParser(description=__doc__);a.add_argument('files',nargs='+',type=Path);a.add_argument('--out',type=Path)
    args=a.parse_args();r=[read(f) for f in args.files];text=json.dumps(r,indent=2)+'\n'
    if args.out:args.out.write_text(text)
    else:print(text,end='')
