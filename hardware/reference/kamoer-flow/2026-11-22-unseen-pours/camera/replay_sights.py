"""Reconstruct the two photographed volume sightlines from native pre- and post-pour pixels."""
import argparse
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE/'optical-source'))
from cup_volume import CROP
from mark_crossings_v3 import clear_lane
from read_levels import measure_gray as read_gray

def replay(path):
    with np.load(path) as z:
        x=z['sensor_x'];y=z['sensor_y'];seq=z['seq'];t=z['pts_ns']
        pix=z['native_luma'];avg=np.rint(np.mean(pix,axis=0,dtype=np.float32)).astype(np.uint8).T
    l,top,r,b=CROP;canvas=np.zeros((b-top,r-l),dtype=np.uint8)
    canvas[np.ix_(y-top,x-l)]=avg
    return canvas,x,y,seq,t

def from_photo(path):
    with Image.open(path) as im:return np.asarray(im.crop(CROP).convert('L'))

def check(path,photo=None):
    gray,x,y,seq,t=replay(path)
    result={'geometry':read_gray(gray),'seq':seq.tolist(),'pts_ns':t.tolist()}
    if photo:
        original=from_photo(photo)
        if not np.array_equal(gray[np.ix_(y-CROP[1],x-CROP[0])],original[np.ix_(y-CROP[1],x-CROP[0])]):
            raise RuntimeError(f'Reconstructed native endpoint pixels differ from full average in {path}.')
        if read_gray(original)!=result['geometry']:raise RuntimeError(f'Full-frame geometry differs for {path}.')
        result['exact_full_photo_agreement']=True
    return result

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('recording',type=Path);p.add_argument('--average',type=Path);p.add_argument('--out',type=Path)
    a=p.parse_args();result=check(a.recording,a.average);text=json.dumps(result,indent=2)+'\n'
    if a.out:a.out.write_text(text)
    print(text,end='')
