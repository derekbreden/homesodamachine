"""Retain timestamped upper-cup images to distinguish geometric tube motion during electrical qualification."""
from pathlib import Path
import csv,json,re,time
import numpy as np
p=Path(__file__).resolve().parent;dst=p/'tube-frames';dst.mkdir(exist_ok=True)
buf=[];times=[];seqs=[];last=-1
while True:
    v=(p/'live.pgm').read_bytes().split(b'\n',4);seq,pts,wall=map(int,re.findall(rb'\d+',v[1]))
    if seq==last:time.sleep(.009);continue
    w,h=map(int,v[2].split());img=np.frombuffer(v[4],dtype='u1').reshape(h,w)
    buf.append(img[0:155,120:300].copy());times.append(pts);seqs.append(seq);last=seq
    if len(buf)==30:
        target=dst/('%010d.npz'%seqs[0]);tmp=target.with_suffix('.partial.npz')
        np.savez_compressed(tmp,images=buf,pts_ns=times,seq=seqs,x0=120,y0=0,sample_spacing=6)
        tmp.replace(target);buf=[];times=[];seqs=[]
