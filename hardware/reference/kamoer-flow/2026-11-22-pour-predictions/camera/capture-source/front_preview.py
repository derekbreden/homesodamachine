"""Preserve the photographed front contact at three sites from the timestamped live luma preview."""
import json
import re
import signal
import time
from pathlib import Path

import numpy as np

HERE=Path(__file__).resolve().parent
COLUMNS=np.r_[np.arange(156,177),np.arange(237,252),np.arange(325,344)]
ROWS=np.arange(105,202)
active=True
def stop(*args):
    global active
    active=False
def save(folder,frames,times,seqs):
    if not frames:return
    dst=folder/('%010d.npz'%seqs[0]);tmp=dst.with_suffix('.partial')
    with tmp.open('wb') as f:
        np.savez_compressed(f,luma=np.asarray(frames),pts_ns=times,seq=seqs,sensor_x=COLUMNS*6,sensor_y=ROWS*6)
    tmp.replace(dst);frames.clear();times.clear();seqs.clear()
def main():
    signal.signal(signal.SIGTERM,stop)
    folder=HERE/'front-preview';folder.mkdir(exist_ok=True)
    frames=[];times=[];seqs=[];last=-1
    try:
        while active and (HERE/'port.json').exists():
            raw=(HERE/'live.pgm').read_bytes().split(b'\n',4)
            seq,pts,wall=map(int,re.findall(rb'\d+',raw[1]))
            if seq==last:
                time.sleep(.012);continue
            w,h=map(int,raw[2].split());im=np.frombuffer(raw[4],dtype='u1').reshape(h,w)
            frames.append(im[ROWS[:,None],COLUMNS]);times.append(pts);seqs.append(seq);last=seq
            if len(frames)>=64:save(folder,frames,times,seqs)
    finally:save(folder,frames,times,seqs)
if __name__=='__main__':main()
