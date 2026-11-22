"""Reproduce stationary edge statistics from the compact optical-control evidence."""
from pathlib import Path
import argparse,json
import numpy as np
def summarize(fr,base,centers):
    fr=fr/4
    out={}
    for k,site in enumerate(['right','mid']):
        rows=[];above=[];below=[];shifts=[]
        for i,y in enumerate(centers[k]):
            p0=24
            obs=fr[:,k,i,:];ref=base[k,i,:]
            row=np.arange(p0-13,p0+14)
            # Derivative centroid over a consistent physical window, before the secondary reflection.
            smooth=(obs[:,row-1]+2*obs[:,row]+obs[:,row+1])*.25
            driver=np.maximum(0,-(smooth[:,2:]-smooth[:,:-2])*.5)
            rows.append(np.sum(driver*row[None,1:-1],axis=1)/np.maximum(driver.sum(1),1e-9)+y-24)
            above.append(obs[:,p0-18:p0-8].mean(1));below.append(obs[:,p0+8:p0+18].mean(1))
            width=np.arange(p0-13,p0+15)
            # Separate common brightness and contrast from image position, comparing template slopes.
            r=ref[width];r=(r-r.mean())/(r.std()+1e-6)
            candidates=np.arange(-5.,5.01,.1)
            costs=[]
            for dx in candidates:
                a=int(np.floor(dx));d=dx-a
                v=obs[:,width+a]*(1-d)+obs[:,width+a+1]*d
                v-=v.mean(axis=1,keepdims=True);v/=np.maximum(1e-6,v.std(axis=1,keepdims=True))
                costs.append(((v-r)**2).mean(axis=1))
            shifts.append(candidates[np.argmin(costs,axis=0)])
        rr=np.median(rows,axis=0);ss=np.median(shifts,axis=0)
        out[site]={'centroid_mean_px':round(float(np.mean(rr)),3),'centroid_frame_sd_px':round(float(np.std(rr)),3),
                   'normalized_template_shift_mean_px':round(float(np.mean(ss)),3),'normalized_template_frame_sd_px':round(float(np.std(ss)),3),
                   'above_mean_y8':round(float(np.mean(above)),2),'below_mean_y8':round(float(np.mean(below)),2),
                   'early_late_centroid_px':round(float(np.mean(rr[-20:])-np.mean(rr[:20])),3),
                   'early_late_template_px':round(float(np.mean(ss[-20:])-np.mean(ss[:20])),3)}
    return out

def main():
    args=argparse.ArgumentParser(description=__doc__)
    args.add_argument('profiles',type=Path);args.add_argument('index',type=Path)
    opts=args.parse_args()
    index=json.loads(opts.index.read_text())
    with np.load(opts.profiles,allow_pickle=False) as raw:
        names={n['name']:n['key']+'_luma_x4' for n in index['windows']}
        base=np.median(raw[names['balance-4600-return']],axis=0)/4
        result={n:dict(frames=len(raw[k]),**summarize(raw[k],base,raw['center_rows'])) for n,k in names.items()}
    color_path=opts.profiles.with_name('color-samples.npz')
    if color_path.is_file():
        with np.load(color_path,allow_pickle=False) as rgb:
            for item in index['windows']:
                key=item['key']+'_rgb'
                if key in rgb:
                    result[item['name']]['lit_cup_rgb']=np.median(rgb[key],axis=(0,1)).tolist()
    print(json.dumps(result,indent=2))
if __name__=='__main__':main()
