"""Confirm the liquid boundary at a second position when fixed cup print wins a broad search."""
from copy import deepcopy

from prospective_reader import read


def read_endpoint(image, config):
    first=read(image,config)
    first['reader']='broad'
    if first['ok'] or not first['sightlines']['right']['ok']:
        return first
    adjusted=deepcopy(config)
    right=first['right_y']
    adjusted['sightlines']['left']['row_search']=[int(right+30),int(right+65)]
    constrained=read(image,adjusted)
    constrained['reader']='left_geometry_check'
    constrained['unconstrained_left_y']=first['left_y']
    if not constrained['ok']:
        left=smooth_left(image,right,config)
        if left:
            constrained['sightlines']['left']=left
            constrained['left_y']=left['row']
            rv=constrained['sightlines']['right']['nominal_ml']
            constrained['ok']=abs(rv-left['nominal_ml']-config['reference_right_minus_left_ml'])<8
            constrained['nominal_ml']=round((rv+left['nominal_ml'])/2,3)
            constrained['side_difference_ml']=round(abs(rv-left['nominal_ml']),3)
            constrained['reader']='left_gradient_between_strokes'
    return constrained

def smooth_left(image, right, config):
    """Locate the falling edge between the two neighboring fixed strokes at the left sightline."""
    import numpy as np
    from scipy.ndimage import gaussian_filter1d
    spec=config['sightlines']['left']
    data=[]
    for x in (1156,1168,1180,1192,1204,1216):
        row=image[:,x-4:x+5].mean(axis=1)
        grad=-gaussian_filter1d(row,2,order=1)
        lo,hi=round(right+34),round(right+60)
        peak=lo+np.argmax(grad[lo:hi+1])
        if peak<lo+2 or peak>hi-2 or grad[peak]<.38:continue
        j=np.arange(peak-5,peak+6)
        y=np.average(j,weights=np.maximum(grad[j],0))
        data.append((x,y,grad[peak]))
    if len(data)<4:return None
    x,y,g=np.array(data).T
    slope=np.median([(y[j]-y[i])/(x[j]-x[i]) for j in range(len(y)) for i in range(j)])
    centered=y-(x-spec['x'])*slope
    pos=float(np.median(centered))
    if abs(slope)>.4 or np.median(abs(centered-pos))>3:return None
    mark_y,mark_v=np.array(spec['marks']).T
    return dict(ok=True,row=round(pos,4),alternative_row=round(float(np.median(y)),4),nominal_ml=round(float(np.interp(pos,mark_y,mark_v))*236.5882365,4),columns_used=len(y),median_gradient=round(float(np.median(g)),3))
