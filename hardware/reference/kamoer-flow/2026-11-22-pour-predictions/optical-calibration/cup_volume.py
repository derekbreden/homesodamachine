#!/usr/bin/env python3
"""Read the front-wall liquid contact against each of the photographed cup's printed scales."""
import argparse
import json
from pathlib import Path

import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter1d, maximum_filter1d, minimum_filter1d, uniform_filter1d
from scipy.signal import find_peaks

CUP_ML = 236.5882365
CROP = (950, 650, 2045, 1340)
NATIVE = (2320, 1744)
# Rows only bound the search for each fixed stroke. Each exposure supplies its actual center.
SCALES = {
    'thirds': (1730, [(767, 4/3), (977, 1), (1187, 2/3)]),
    'quarters': (1220, [(691, 1.5), (836, 1.25), (991, 1), (1131, .75), (1289, .5)]),
}
# The three anchor points per face describe the approximate curvature of the near wall.
# Each face searches the full working height. These shapes do not specify a fill level.
SHAPES = {
    'thirds': [(1520, 967), (1540, 965), (1730, 951), (1930, 936), (2010, 926)],
    'quarters': [(965, 986), (1035, 988), (1220, 979), (1450, 971), (1512, 967)],
}
SITES = {
    'thirds': [*range(1520,1561,8), *range(1592, 1685, 12), *range(1714, 1823, 12), *range(1840, 1949, 12), *range(1976, 2025, 8)],
    'quarters': [*range(968, 1065, 8), *range(1078, 1147, 12), *range(1170, 1281, 14), *range(1294, 1381, 7), *range(1388, 1513, 10)],
}
# Native offsets from the traced baseline span the physical marks used for calibration.
OFFSETS = np.arange(-195, 240)


def crop(path):
    with Image.open(path) as im:
        if im.size == NATIVE:
            return im.crop(CROP)
        if im.size == (CROP[2]-CROP[0], CROP[3]-CROP[1]):
            return im.copy()
        raise ValueError(f'Unexpected source image dimensions {im.size}')


def anchor(rgb, site, prior, cups):
    rows = np.arange(prior-28, prior+29)
    centers, scores = [], []
    for x in range(site-18, site+19, 3):
        rr, gg, bb = rgb[rows-CROP[1], x-CROP[0]].T.astype(float)
        pigment = rr - np.maximum(1.27*gg, 1.13*bb)
        base = np.percentile(pigment, 18)
        weights = np.maximum(0., pigment-base)
        if weights.max() < 7:
            continue
        weights[weights < max(2.6, weights.max()*.46)] = 0.
        centers.append(np.average(rows, weights=weights))
        scores.append(weights.max())
    if len(centers) < 6 or np.median(np.abs(centers-np.median(centers))) > 3.0:
        return None
    return {'cups':float(cups), 'y':float(np.median(centers)), 'column_mad_px':float(np.median(abs(centers-np.median(centers)))), 'pigment':float(np.median(scores))}


def row_shape(side, x):
    knots = np.array(SHAPES[side]);return float(np.interp(x, knots[:,0], knots[:,1]))


def stripes(gray, rgb, side):
    y = np.arange(gray.shape[0]); strips=[]
    for x in SITES[side]:
        j=x-CROP[0]; s=slice(j-3,j+4)
        col=rgb[:,s].mean(1); r,g,b=col.T
        ink=maximum_filter1d(((r>1.48*g+8) & (r-g>14)).astype(int),5).astype(bool)
        signal=gray[:,s].mean(1) if side=='thirds' else g
        # Interpolate across red pigment when judging the liquid's longer dark plateau.
        clean=gaussian_filter1d(np.interp(y,y[~ink],signal[~ink]),1.65)
        local=uniform_filter1d(clean,7); below=uniform_filter1d(clean,18)
        base=row_shape(side,x); center=np.rint(base+OFFSETS-CROP[1]).astype(int)
        gradient=(np.roll(clean,3)-np.roll(clean,-3))/6
        a=local[center-9]; z=local[center+9]; deep=below[center+27]
        floor=np.minimum(below[center+42],below[center+68]); excess=np.maximum(0,z-floor-2)
        if side=='thirds':
            # A foreground step ends in dark bulk. Far-wall reflections often descend to a bright second shelf.
            signal_to_bulk=np.maximum(0,a-z) + .34*np.maximum(0,a-deep)
            weight=signal_to_bulk/(1+excess/4.8)
        else:
            # The left check uses native green's approach to the deep-liquid plateau, including around the red text.
            edge=np.maximum(0,gradient[center])*5
            near_bulk=np.maximum(abs(z-deep)-2,0)+.65*excess
            weight=np.sqrt(np.maximum(0,a-z)*edge)/(1+near_bulk/6.)
        # A boundary coextensive with red ink receives no direct vote on either face.
        weight[ink[center] | (gradient[center]<.14)] = 0
        if np.percentile(weight,98)<1:weight*=0
        normal=weight/max(np.percentile(weight,97),9.)
        strips.append({'x':x,'base':base,'clean':clean,'ink':ink,'weight':weight,'normal':np.minimum(1.8,normal)})
    return strips


def fit_edge(samples, site):
    xyz=np.array([(s['x'],s['y'],s['contrast']) for s in samples]); x,y=xyz[:,:2].T
    # Use native cup curvature, then allow an additional tilt and offset at this fill level.
    bases=np.array([s['base'] for s in samples]);corr=y-bases
    keep=np.ones(len(x),dtype=bool)
    for _ in range(5):
        coef=np.polyfit(x[keep]-site,corr[keep],1)
        residual=corr-np.polyval(coef,x-site); mad=np.median(abs(residual[keep]-np.median(residual[keep])))
        update=abs(residual-np.median(residual[keep]))<max(2.8,3.3*mad)
        if update.sum()<4 or np.array_equal(keep,update):break
        keep=update
    coef=np.polyfit(x[keep]-site,corr[keep],1);residual=corr-np.polyval(coef,x-site)
    return coef,keep,residual


def face(gray,rgb,side,detail):
    site, priors=SCALES[side]; marks=[m for y,c in priors if (m:=anchor(rgb,site,y,c)) is not None]
    ss=stripes(gray,rgb,side); slopes=np.arange(-.055,.056,.01)
    shoulders=[]
    for strip in ss:
        if side=='thirds' and strip['x']<1976 or side=='quarters' and strip['x']>1065:continue
        v=strip['clean']; center=np.rint(strip['base']+OFFSETS-CROP[1]).astype(int)
        floor=np.percentile(v[190:600],10)
        spread=(maximum_filter1d(v,47)-minimum_filter1d(v,47))[center+39]
        level=uniform_filter1d(v,41)[center+41]
        smooth_bulk=strip['normal'] / (1+(spread/3)**1.2) / (1+(np.maximum(0,level-floor-2)/5)**1.2)
        shoulders.append(maximum_filter1d(smooth_bulk/max(smooth_bulk.max(),.025),9))
    shoulder=np.mean(shoulders,axis=0); pilot=int(np.argmax(shoulder))
    radius=14+abs(OFFSETS[pilot])*.13
    allowed=abs(OFFSETS-OFFSETS[pilot])<=radius
    trial=[]
    for slope in slopes:
        curves=np.array([np.roll(maximum_filter1d(s['normal'],9),-round((s['x']-site)*slope)) for s in ss]);
        trial.append(np.mean(curves,axis=0)*.6 + np.percentile(curves,50,axis=0)*.4)
    trial=np.array(trial);vector=trial.max(0); best=int(np.argmax(np.where(allowed,vector,-1))); tilt=slopes[np.argmax(trial[:,best])]
    other=abs(np.arange(len(vector))-pilot)>23; second_idx=int(np.argmax(np.where(other,shoulder,-1)))
    local=[]
    for s in ss:
        near=np.flatnonzero(abs(OFFSETS-(OFFSETS[best]+(s['x']-site)*tilt))<=9)
        k=near[np.argmax(s['weight'][near])];row=round(s['base']+OFFSETS[k])-CROP[1];v=s['clean']
        light=float(np.median(v[row-15:row-5]));dark=float(np.median(v[row+5:row+15])); contrast=light-dark
        if s['weight'][k]<3.8 or contrast<5 or s['ink'][row]:continue
        thresholds=[dark+f*contrast for f in (.35,.5,.65)];cross=[]
        for threshold in thresholds:
            idx=np.arange(row-10,row+11);hits=idx[(v[idx]>=threshold)&(v[idx+1]<threshold)]
            if not len(hits):break
            i=hits[np.argmin(abs(hits-row))];cross.append(i+(v[i]-threshold)/(v[i]-v[i+1])+CROP[1])
        if len(cross)!=3:continue
        cy=round(cross[1])-CROP[1]
        # A crossing calculated on or immediately beside an interpolated red stroke is artificial.
        if np.any(s['ink'][cy-5:cy+6]) or np.any(s['ink'][row-3:row+4]):continue
        local.append({'x':s['x'],'y':cross[1],'base':s['base'],'contrast':contrast,'edge_width_px':cross[0]-cross[2]})
    out={'ok':False,'x':site,'marks':marks,'signal':float(vector[best]),'runner_up_ratio':float(shoulder[second_idx]/max(.01,shoulder[pilot])),'other_candidate_y':float(row_shape(side,site)+OFFSETS[second_idx]),'shoulder_contrast_consensus':float(shoulder[pilot]),'shoulder_seed_offset':int(OFFSETS[pilot])}
    flags=[]
    if len(local)<5:
        out.update(flags=['few visible contacts'],patches=len(local));return out
    coef,keep,residual=fit_edge(local,site); keep_x=np.array([s['x'] for s in local])[keep]; y=float(row_shape(side,site)+coef[1]); med=float(np.median(abs(residual[keep])))
    bracket=next(((a,b) for a,b in zip(marks,marks[1:]) if a['y']<=y<=b['y']),None)
    if not bracket:flags.append('outside observed graduation bracket')
    if len(keep_x)<7 or np.ptp(keep_x)<130 or not keep_x.min()<=site<=keep_x.max():flags.append('inadequate clear strips on both sides of the printed column')
    if med>3.7 or abs(coef[0])>.07:flags.append('inconsistent contact shape')
    if shoulder[pilot]<.35 or vector[best]<.20 or out['runner_up_ratio']>.91:flags.append('another near-wall candidate is plausible')
    if bracket:
        a,b=bracket; fraction=(y-a['y'])/(b['y']-a['y']); vol=(a['cups']+fraction*(b['cups']-a['cups']))*CUP_ML
        out.update(nominal_ml=float(vol),bracket_cups=[b['cups'],a['cups']])
    out.update(ok=not flags,flags=flags,y=y,patches=len(keep_x),span=[int(keep_x.min()),int(keep_x.max())],slope_correction=float(coef[0]),residual_mad_px=med,edge_width_px=float(np.median([s['edge_width_px'] for s,k in zip(local,keep) if k])))
    if detail:out['contacts']=[{k:v for k,v in s.items() if k!='base'}|{'used':bool(accept)} for s,accept in zip(local,keep)]
    return out


def read(window,detail=False):
    p=Path(window); gray=np.asarray(crop(p/'average.png').convert('L'));rgb=np.asarray(crop(p/'color.png').convert('RGB'))
    right=face(gray,rgb,'thirds',detail);left=face(gray,rgb,'quarters',detail)
    flags=[side for side,f in [('right thirds',right),('left quarters',left)] if not f['ok']]
    out={'window':p.name,'primary':right,'held_out':left};
    if 'nominal_ml' in right and 'nominal_ml' in left:
        a=right['nominal_ml'];b=left['nominal_ml'];out['nominal_ml']=a;out['crosscheck_ml']=b;out['difference_ml']=a-b
        if abs(a-b)>10:flags.append('printed scales differ by more than the acceptance allowance')
    out.update(ok=not flags,flags=flags);return out


def pack(source,dest):
    dest.mkdir(parents=True,exist_ok=True)
    for f in ('average.png','color.png'):crop(source/f).save(dest/f,compress_level=4)
    for f in ('window.json','color.json'):
        if (source/f).is_file():(dest/f).write_bytes((source/f).read_bytes())


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('window',type=Path);p.add_argument('--before',type=Path);p.add_argument('--detail',action='store_true');p.add_argument('--pack',type=Path);p.add_argument('--out',type=Path);a=p.parse_args()
    if a.pack:pack(a.window,a.pack);return
    after=read(a.window,a.detail)
    if a.before:
        before=read(a.before,a.detail);o={'ok':before['ok'] and after['ok'],'before':before,'after':after}
        for key,field in [('primary','nominal_change_ml'),('held_out','crosscheck_change_ml')]:
            if 'nominal_ml' in before[key] and 'nominal_ml' in after[key]:o[field]=after[key]['nominal_ml']-before[key]['nominal_ml']
    else:o=after
    data=json.dumps(o,indent=2,allow_nan=False)+'\n'
    if a.out:a.out.write_text(data)
    else:print(data,end='')


if __name__=='__main__':main()
