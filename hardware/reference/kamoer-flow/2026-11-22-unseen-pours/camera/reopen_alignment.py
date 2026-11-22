"""Compare dry cup references and the same local liquid contacts with the previous fixed-camera photographs."""
import argparse
import json
from pathlib import Path
import numpy as np
from PIL import Image

MARKS=((1180,412),(1180,554),(1180,684),(1730,328),(1730,542),(1730,756))
FRONTS=((990,989),(1450,894),(1986,931),(1986,862))
def refine(left,middle,right):
    den=2*(2*middle-left-right)
    return float(np.clip((right-left)/den,-.5,.5)) if den>1e-10 else 0.
def measure(a,b):
    outcome={'dry_print':{},'liquid_features':{}}
    for x,y in MARKS:
        template=a[y-13:y+14,x-26:x+27];ref=template-template.mean();rn=np.linalg.norm(ref)
        if rn<5:continue
        q=np.zeros((13,13))
        for i,dy in enumerate(range(-6,7)):
            for j,dx in enumerate(range(-6,7)):
                obs=b[y+dy-13:y+dy+14,x+dx-26:x+dx+27];zz=obs-obs.mean()
                q[i,j]=np.sum(zz*ref)/max(.001,np.linalg.norm(zz)*rn)
        i,j=np.unravel_index(q.argmax(),q.shape);dx=float(j-6);dy=float(i-6)
        if 0<i<12:dy+=refine(*q[i-1:i+2,j])
        if 0<j<12:dx+=refine(*q[i,j-1:j+2])
        patch=b[y+i-6-13:y+i-6+14,x+j-6-26:x+j-6+27];moved=np.std(patch)
        outcome['dry_print'][f'{x},{y}']={'dx_px':dx,'dy_px':dy,'correlation':float(q[i,j]),'contrast_ratio':float(moved/np.std(template)),
              'vertical_feature_gradient_ratio':float(np.sqrt(np.mean(np.diff(patch,axis=0)**2))/np.sqrt(np.mean(np.diff(template,axis=0)**2))),
              'mean_luma_difference':float(patch.mean()-template.mean())}
    for x,y in FRONTS:
        p=a[:,x-4:x+5].mean(1);r=b[:,x-4:x+5].mean(1);rows=y+np.arange(-18,19);shifts=np.arange(-12,12.001,.05)
        corrs=[np.corrcoef(p[rows],np.interp(rows+d,np.arange(len(r)),r))[0,1] for d in shifts]
        i=int(np.argmax(corrs));outcome['liquid_features'][f'{x},{y}']={'dy_px':round(float(shifts[i]),2),'correlation':float(corrs[i])}
    return outcome
def read(path):return np.asarray(Image.open(path).convert('L'),dtype=np.float32)
if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('before',type=Path);ap.add_argument('after',type=Path);ap.add_argument('--out',type=Path,required=True);v=ap.parse_args()
    v.out.write_text(json.dumps(measure(read(v.before),read(v.after)),indent=2)+'\n')
