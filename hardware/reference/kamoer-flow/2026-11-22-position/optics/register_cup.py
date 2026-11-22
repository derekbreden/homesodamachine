#!/usr/bin/env python3
"""Register liquid-row targets to the front ink in the contemporaneous color sample."""
import argparse
import json
from pathlib import Path

import numpy as np
from PIL import Image

HERE=Path(__file__).resolve().parent
# For each sightline the three references are upper graduations always above the liquid.
ROWS={'left':(1180,[412,554,684],[979,1123]),'right':(1730,[328,542,756],[964,1175])}
HALF=19
LIMIT=44
LEGACY_LIMIT=13
SPINES={'left':[(460,1243),(506,1248),(602,1263),(642,1269),(735,1280)],
        'right':[(407,1537),(477,1542),(604,1551),(663,1556),(704,1558)]}


def tile_rectangles(limit=LIMIT):
    padding=HALF+limit
    boxes=[]
    for x,dry,lower in ROWS.values():
        for y in dry+lower:boxes.append((x-27,y-padding,x+28,y+padding+1))
    for rows in SPINES.values():
        for y,x in rows:boxes.append((x-padding,y-3,x+padding+1,y+4))
    return boxes


def pack_color(source, destination):
    image=Image.open(source).convert('RGB')
    if image.size!=(2320,1744):raise ValueError('color tiles require the full upright source')
    boxes=tile_rectangles();width=max(r-l for l,_,r,_ in boxes)
    atlas=Image.new('RGB',(width,sum(b-t for _,t,_,b in boxes)))
    off=0
    for l,t,r,b in boxes:
        atlas.paste(image.crop((l,t,r,b)),(0,off))
        off+=b-t
    atlas.save(destination,format='PNG',compress_level=7)
    return atlas.size


def rgb_image(path):
    im=Image.open(path)
    if im.size==(2320,1744):return np.asarray(im),LIMIT
    for radius in (LIMIT,LEGACY_LIMIT):
        boxes=tile_rectangles(radius)
        shape=(max(r-l for l,_,r,_ in boxes),sum(b-t for _,t,_,b in boxes))
        if im.size==shape:break
    else:
        raise ValueError(f'unrecognized ink image size {im.size}')
    pixels=np.asarray(im.convert('RGB'))
    full=np.zeros((1744,2320,3),dtype=np.uint8)
    off=0
    for l,t,r,b in boxes:
        full[t:b,l:r]=pixels[off:off+b-t,:r-l]
        off+=b-t
    return full,radius


def signature(rgb,x,y,axis,limit=LIMIT):
    # Chroma rejects invisible grayscale texture seen through the side of the cup.
    if axis=='y': area=rgb[y-HALF-limit:y+HALF+limit+1,x-3:x+4].astype(float)
    else: area=rgb[y-3:y+4,x-HALF-limit:x+HALF+limit+1].astype(float).transpose(1,0,2)
    r,g,b=np.moveaxis(area,2,0)
    return np.mean((r-np.maximum(g,b))/(r+g+b+18),axis=1)


def templates_from_color(image):
    info=[];data=[]
    for side,(x,refs,check) in ROWS.items():
        for role,rows in [('dry',refs),('lower_check',check)]:
            for row in rows:
                for off in [-24,-12,0,12,24]:
                    xx=x+off
                    prof=signature(image,xx,row,'y')
                    info.append((side,role,xx,row,'y'));data.append(prof[LIMIT:-LIMIT])
    for side,yx in SPINES.items():
        for y,x in yx:
            prof=signature(image,x,y,'x')
            info.append((side,'spine',x,y,'x'));data.append(prof[LIMIT:-LIMIT])
    return info,np.array(data)


def correlation(profile,ref):
    windows=np.lib.stride_tricks.sliding_window_view(profile,len(ref))
    centered=windows-windows.mean(1,keepdims=True)
    target=ref-ref.mean()
    strength=np.linalg.norm(target)
    if strength<.10:return None
    return centered@target/np.maximum(np.linalg.norm(centered,axis=1)*strength,1e-9)


def peak(curve,limit,center):
    if limit==LEGACY_LIMIT or abs(center)<=4:
        low,high=-LEGACY_LIMIT,LEGACY_LIMIT
    else:
        low,high=max(-limit,center-11),min(limit,center+11)
    index=limit+low+int(np.argmax(curve[limit+low:limit+high+1]))
    if index in (limit+low,limit+high) or curve[index]<.91:return None
    a,b,c=curve[index-1:index+2]
    divisor=a-2*b+c
    delta=.5*(a-c)/divisor if divisor<-.000001 else 0.
    return index-limit+float(np.clip(delta,-.5,.5)),float(curve[index])


def form(color_path,raw_right=850.,raw_left=895.,reference=HERE/'dry-ink.npz',detail=False):
    image,limit=rgb_image(color_path)
    with np.load(reference) as r:info=r['locations'];templates=r['profiles']
    curves=[]
    for (side,role,xx,yy,axis),ref in zip(info,templates):
        x,y=int(xx),int(yy)
        curve=correlation(signature(image,x,y,axis,limit),ref)
        if curve is not None:curves.append((side,role,x,y,curve))
    centers={}
    for side in ROWS:
        for role in ['dry','spine']:
            votes=[row[-1] for row in curves if row[0]==side and row[1]==role]
            centers[side,role]=int(np.argmax(np.median(votes,axis=0)))-limit if votes else 0
    obs=[]
    for side,role,x,y,curve in curves:
        coarse=centers[side,'spine' if role=='spine' else 'dry']
        z=peak(curve,limit,coarse)
        if z is not None:obs.append((side,role,x,y,*z))
    stations={}
    for side,row in [('left',raw_left),('right',raw_right)]:
        grouped={}
        for role in ['dry','lower_check','spine']:
            grouped[role]={}
            for yy in sorted({q[3] for q in obs if q[0]==side and q[1]==role}):
                values=[q[4] for q in obs if q[0]==side and q[1]==role and q[3]==yy]
                if len(values)>=(1 if role=='spine' else 3):grouped[role][yy]=float(np.median(values))
        dry=grouped['dry'];ys=np.array(list(dry));ds=np.array(list(dry.values()))
        if len(ds)<3:raise ValueError(f'{side}: too few dry-front strokes')
        coef=np.polyfit(ys,ds,1);dy=float(np.polyval(coef,row))
        resid=float(np.max(np.abs(ds-np.polyval(coef,ys))))
        lower=grouped['lower_check']
        lower_error={k:float(v-np.polyval(coef,k)) for k,v in lower.items()}
        sp=grouped['spine'];dx=float(np.median(list(sp.values()))) if sp else None
        stations[side]={'raw_y':row,'cup_y':row-dy,'dy':dy,'spine_dx':dx,
                        'dry_fit_max_residual_px':resid,'lower_minus_dry_prediction_px':lower_error}
        if detail:stations[side]['observed_shifts_px']=grouped
    return stations


def build(path,out):
    w,v=templates_from_color(rgb_image(path)[0])
    np.savez_compressed(out,locations=np.array(w),profiles=v)


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('image',type=Path);p.add_argument('--right',type=float,default=850);p.add_argument('--left',type=float,default=895)
    p.add_argument('--pack',type=Path,help='write the lossless RGB tiles used by registration')
    p.add_argument('--reference',type=Path,default=HERE/'dry-ink.npz');p.add_argument('--make-reference',action='store_true');p.add_argument('--detail',action='store_true')
    a=p.parse_args();image=a.image/'color.png' if a.image.is_dir() else a.image
    if a.pack:pack_color(image,a.pack)
    elif a.make_reference:build(image,a.reference)
    else:print(json.dumps(form(image,a.right,a.left,a.reference,a.detail)))


if __name__=='__main__':main()
