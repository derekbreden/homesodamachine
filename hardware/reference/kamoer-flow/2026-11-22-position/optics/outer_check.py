"""Locate the optical contact in flanking left-side pixels held out of the live reader."""
import numpy as np
from scipy.ndimage import gaussian_filter1d

from independent import CROP

# The source's visible falling edge locates each shoulder of the operating window.
PATCHES=[(1014,990),(1019,990),(1024,990),(1029,990),(1034,990),(1039,990)]


def read(gray):
    result=[]
    for x,y in PATCHES:
        ix=x-CROP[0]
        v=gaussian_filter1d(gray[:,ix-2:ix+3].mean(1),1.6)
        ys=np.arange(y-19,y+20)-CROP[1]
        # The integrated local change avoids locking on a single bright JPEG or sensor sample.
        first=np.median(v[ys[:,None]+np.arange(-9,-3)],axis=1)
        last=np.median(v[ys[:,None]+np.arange(4,10)],axis=1)
        score=first-last
        j=ys[int(np.argmax(score))]
        before=np.median(v[j-8:j-3]);after=np.median(v[j+4:j+9]);threshold=(before+after)/2
        k=np.arange(j-5,j+6);crossings=k[(v[k]>=threshold)&(v[k+1]<threshold)]
        if before-after<6 or len(crossings)==0:continue
        i=crossings[np.argmin(abs(crossings-j))]
        crossing=i+(v[i]-threshold)/(v[i]-v[i+1])+CROP[1]
        result.append([x,float(crossing)])
    return result


def displacement(gray,baseline):
    base=dict(read(baseline));now=dict(read(gray))
    shifts=[[x,now[x]-base[x]] for x in sorted(base.keys()&now.keys())]
    if len(shifts)<4:return {'ok':False,'patches':len(shifts)}
    ds=np.array([v for _,v in shifts]);median=float(np.median(ds));mad=float(np.median(abs(ds-median)))
    return {'ok':bool(mad<=2.5),'shoulder_delta_px':median,'mad_px':mad,'patches':len(shifts),'samples':shifts}
