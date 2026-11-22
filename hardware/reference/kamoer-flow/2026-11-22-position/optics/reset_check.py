#!/usr/bin/env python3
"""Measure short post-reset motion against a photographed contact without assuming which electrical head fills the cup."""
import argparse
import json
from pathlib import Path

import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter1d

import independent
import register_cup

HERE=Path(__file__).resolve().parent
REFERENCE=HERE/"post-reset"
GROUPS={"left_clear":(980,[(958,986),(966,986),(974,987),(982,988),(990,989),(998,990),(1006,989)]),
        "center":(1450,[(1424,973),(1432,972),(1440,971),(1448,970),(1456,970),(1464,970),(1472,970)]),
        "right":(1730,[(1706,954),(1714,953),(1722,953),(1730,952),(1738,952),(1746,951),(1754,950)]),
        "outer_right":(1990,[(1976,935),(1984,933),(1992,931),(2000,928),(2008,927)])}
RANGE=20
HALF=12


def luma(path):
    return np.asarray(independent.crop_frame(path).convert("L"))


def sensor_profile(image,x):
    j=x-independent.CROP[0]
    return gaussian_filter1d(image[:,j-3:j+4].mean(1),1.35)


def create(window,dest):
    dest.mkdir(parents=True,exist_ok=True)
    register_cup.build(window/"color.png",dest/"dry-ink.npz")
    gray=luma(window/"average.png"); rgb=np.asarray(independent.crop_frame(window/"color.png").convert("RGB"))
    info={"source":window.name,"ml_per_cup":independent.CUP_ML,"groups":{},"marks":{}}
    template=[];coords=[]
    for name,(site,stations) in GROUPS.items():
        rows=[];xs=[]
        for x,y in stations:
            v=sensor_profile(gray,x);j=y-independent.CROP[1]
            p=v[j-5:j+6];idx=np.arange(j-5,j+6);g=np.maximum(0,-np.gradient(v)[idx]);cy=float(np.average(idx,weights=g))+independent.CROP[1]
            template.append(v[j-HALF:j+HALF+1]);coords.append([name,x,y,cy]);rows.append(cy);xs.append(x)
        fit=np.polyfit(np.array(xs)-site,rows,1)
        info["groups"][name]={"x":site,"y":float(fit[1]),"slope_dy_dx":float(fit[0])}
    for name,(x,mark) in independent.STATIONS.items():
        # Both printed columns physically shifted between configurations.
        rough=[(prior+11,cups) for prior,cups in mark]
        info["marks"][name]=independent.anchor_rows(rgb,x,rough)
    np.savez_compressed(dest/"level.npz",coordinates=np.array(coords),profiles=np.array(template))
    (dest/"cup.json").write_text(json.dumps(info,indent=2)+"\n")


def read(path,source=REFERENCE,color=None):
    d=path if path.is_dir() else path.parent
    gray=luma(path/"average.png" if path.is_dir() else path)
    if color is None and path.is_dir():color=d/"color.png"
    cfg=json.loads((source/"cup.json").read_text())
    with np.load(source/"level.npz") as ref:
        points=ref["coordinates"];templates=ref["profiles"]
    groups={k:[] for k in GROUPS}
    for (name,sx,sy,baseline),template in zip(points,templates):
        x,y=int(float(sx)),int(float(sy));cy=float(baseline)
        v=sensor_profile(gray,x);j=y-independent.CROP[1]
        radius=32 if name=="outer_right" else RANGE
        segment=v[j-HALF-radius:j+HALF+radius+1]
        ss=np.lib.stride_tricks.sliding_window_view(segment,len(template))
        ss=ss-ss.mean(1,keepdims=True);t=template-template.mean()
        c=(ss@t)/np.maximum(1e-8,np.linalg.norm(ss,axis=1)*np.linalg.norm(t))
        i=int(np.argmax(c))
        if 0<i<len(c)-1 and c[i]>=.87:
            a,b,e=c[i-1:i+2];div=a-2*b+e;sub=.5*(a-e)/div if div<-.000001 else 0.
            groups[name].append((x,cy,i-radius+float(np.clip(sub,-.5,.5)),float(c[i])))
    out={}
    for name,samples in groups.items():
        if len(samples)<3:
            out[name]={"ok":False,"patches":len(samples)};continue
        arr=np.array(samples);move=arr[:,2];dy=float(np.median(move))
        out[name]={"ok":bool(np.median(abs(move-dy))<=2.5),"x":cfg["groups"][name]["x"],"raw_row":cfg["groups"][name]["y"]+dy,
                   "delta_from_reference_px":dy,"patch_mad_px":float(np.median(abs(move-dy))),
                   "median_correlation":float(np.median(arr[:,3])),"patches":len(samples)}
    if out["right"].get("ok"):
        row=out["right"]["raw_row"];marks=cfg["marks"]
        left=None
        if out["left_clear"].get("ok") and out["center"].get("ok"):
            left=float(np.interp(1180,[out["left_clear"]["x"],out["center"]["x"]],[out["left_clear"]["raw_row"],out["center"]["raw_row"]]))
        left_for_ink=left if left is not None else 980.0
        corrected=register_cup.form(color,row,left_for_ink,source/"dry-ink.npz") if color is not None else None
        if corrected:
            out["right"]["cup_row"]=corrected["right"]["cup_y"];out["dry_ink"]=corrected
        if left is not None:
            lr=np.array(marks["left"]);ly=corrected["left"]["cup_y"] if corrected else left
            out["projected_left"]={"x":1180,"raw_row":left,"cup_row":ly,"nominal_ml":float(np.interp(ly,lr[:,0],lr[:,1])*independent.CUP_ML),
                                   "basis":"Straight-line interpolation between two clear contacts across a printed stroke."}
        rr=np.array(marks["right"])
        out["right"]["nominal_ml"]=float(np.interp(out["right"].get("cup_row",row),rr[:,0],rr[:,1])*independent.CUP_ML)
    return out


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument("window",type=Path);p.add_argument("--reference",type=Path,default=REFERENCE)
    p.add_argument("--calibrate",action="store_true");p.add_argument("--color",type=Path);a=p.parse_args()
    if a.calibrate:create(a.window,a.reference)
    else:print(json.dumps(read(a.window,a.reference,a.color)))


if __name__=="__main__":main()
