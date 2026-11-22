"""Track a stationary-endpoint edge template across two live cup sightlines of the timestamped preview."""
from pathlib import Path
import csv,json,os,re,sys,time
sys.path.append('/opt/homebrew/lib/python3.13/site-packages')
import numpy as np
from PIL import Image
p=Path(__file__).resolve().parent
ref=np.asarray(Image.open(p/'windows/balance-4600-return/average.png'))[::6,::6].astype(float)
def native_rows(img,x,y):
    f=y/6
    i=np.floor(f).astype(int)
    d=f-i
    return img[i,x]*(1-d)+img[i+1,x]*d
class Track:
    def __init__(self,xs,ys):
        self.x=np.asarray(xs)
        self.y=np.asarray(ys)
        x=np.broadcast_to(self.x[None,:],(8,len(xs)))
        y=(np.arange(-3,5)[:,None]*6+np.floor(self.y/6)[None,:]*6)
        self.x=x.ravel();self.y=y.ravel()
        self.tem=native_rows(ref,self.x,self.y)
        self.n=len(xs)
        self.pos=0
        self.start=float(np.median(ys))
    def measure(self,img):
        # Comparing each sightline to its own original near-wall ramp removes the fixed meniscus slope.
        shifts=np.arange(-18,18.01,.25)+self.pos
        vals=native_rows(img,self.x,self.y+shifts[:,None])
        residuals=(vals-self.tem).reshape(len(shifts),8,self.n)
        # Remove a per-column common-mode pedestal; keep slope and contrast information.
        residuals-=np.mean(residuals,axis=1,keepdims=True)
        percol=np.mean(np.minimum(np.abs(residuals),20)**2,axis=1)
        cost=np.median(percol,axis=1)
        j=int(np.argmin(cost))
        d=float(shifts[j])
        good=bool(abs(d-self.pos)<16 and cost[j]<35)
        if good:self.pos=d
        return {'y':round(self.start+d,2),'shift_px':round(d,2),'rms_luma':round(float(np.sqrt(cost[j])),3),'ok':good}
rx=np.r_[np.arange(263,280),np.arange(288,298)]
mx=np.arange(194,215)
tracks=[Track(rx,815-.075*(6*rx-1600)),Track(mx,845-.09*(6*mx-1170))]
prev=-1
with (p/'guard-trace.csv').open('w',buffering=1) as out:
    cw=csv.writer(out);cw.writerow(['seq','pts_ns','wall_ns','right_y','right_shift','right_rms_luma','right_ok','mid_y','mid_shift','mid_rms_luma','mid_ok'])
    while True:
        try:
            data=(p/'live.pgm').read_bytes().split(b'\n',4)
            seq,pts,wall=map(int,re.findall(rb'\d+',data[1]))
            if seq==prev:time.sleep(.008);continue
            w,h=map(int,data[2].split())
            img=np.frombuffer(data[4],dtype='u1').reshape(h,w).astype(float)
            a,b=[t.measure(img) for t in tracks]
            rec=dict(seq=seq,pts_ns=pts,wall_ns=wall,right=a,mid=b)
            tmp=p/'guard.json.tmp';tmp.write_text(json.dumps(rec));tmp.replace(p/'guard.json')
            cw.writerow([seq,pts,wall,*a.values(),*b.values()]);prev=seq
        except (OSError,ValueError) as ex:
            print(ex,flush=True);time.sleep(.1)
