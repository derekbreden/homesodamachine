#!/usr/bin/env python3
"""Continuously record timestamped cup-band profiles and serve full-field camera observations."""
import collections, csv, datetime, io, json, os, pathlib, re, signal, socketserver, struct, subprocess, sys, threading, time, traceback
sys.path.append('/opt/homebrew/lib/python3.13/site-packages')
import numpy as np
from PIL import Image
HERE=pathlib.Path(__file__).resolve().parent
ROOT=HERE.parents[3]
HELPER=HERE/'nativecamera'
END=HERE/'windows'
PROFILES=HERE/'profiles'
for p in (END,PROFILES):p.mkdir(exist_ok=True)
def atom_json(path,obj):
    temp=path.with_suffix('.json.tmp')
    temp.write_text(json.dumps(obj,indent=2)+'\n')
    temp.replace(path)
def put_png(path,img):
    temp=path.with_suffix('.png.tmp')
    Image.fromarray(img).save(temp,format='PNG',compress_level=2)
    temp.replace(path)
def utc(ns):return datetime.datetime.fromtimestamp(ns/1e9,datetime.timezone.utc).isoformat(timespec='milliseconds')
ring=collections.deque(maxlen=72)
cond=threading.Condition()
latest=None
color=None
running=True
last_error=None
def write_images(d,frames):
    avg=np.zeros(frames[0][1].shape,np.float32)
    for _,frame in frames:avg+=frame
    avg=np.rint(avg/len(frames)).astype('u1')
    mid=frames[len(frames)//2]
    put_png(d/'average.png',avg)
    put_png(d/'native.png',mid[1])
    with cond: c=color
    if c:
        save_color(d/'color.png',c[1],c[2])
        atom_json(d/'color.json',c[0])
    sm=Image.fromarray(avg).resize((1160,872),Image.Resampling.BOX)
    sm.save(d/'overview.png',compress_level=2)
    return mid[0]
class Request(socketserver.StreamRequestHandler):
    def handle(self):
        try:
            req=json.loads(self.rfile.readline())
            if req.get('op')=='status':
                with cond:reply={'up':bool(latest),'last':latest,'frames_in_ring':len(ring),'error':last_error}
            else:
                label=req['label']
                if not re.fullmatch('[a-zA-Z0-9][a-zA-Z0-9_.-]{0,99}',label):raise ValueError('invalid label')
                t=float(req.get('seconds',1))
                if not 0<=t<=30: raise ValueError('window duration must be 0–30 seconds')
                n=int(req.get('samples',7))
                if not 1<=n<=60:raise ValueError('sample count must be 1–60')
                start=time.monotonic_ns() + int(float(req.get('offset',0))*1e9)
                targets=np.linspace(start,start+int(t*1e9),n,dtype='int64') if t else [start]
                frames=[]
                d=END/label
                d.mkdir()
                for target in targets:
                    with cond:
                        if not cond.wait_for(lambda:ring and ring[-1][0]['pts_ns']>=target or last_error, timeout=8+max(0,(target-time.monotonic_ns())/1e9)): raise TimeoutError('frame unavailable')
                        if last_error:raise RuntimeError(last_error)
                        if target<ring[0][0]['pts_ns']-100000000:raise ValueError('window start has left native ring')
                        frames.append(min(ring,key=lambda pair:abs(pair[0]['pts_ns']-target)))
                mid=write_images(d,frames)
                reply={'label':label,'target_start_ns':start,'target_end_ns':int(targets[-1]),'mid':mid,'frames':[v[0] for v in frames],'directory':str(d),'source':'upright 2320x1744 gray8; average is rounded mean of listed frames; native is middle listed frame'}
                atom_json(d/'window.json',reply)
            self.wfile.write((json.dumps(reply)+'\n').encode())
        except Exception as ex:
            self.wfile.write((json.dumps({'error':str(ex)})+'\n').encode())
class S(socketserver.ThreadingTCPServer):allow_reuse_address=True;daemon_threads=True
server=S(('127.0.0.1',0),Request)
atom_json(HERE/'port.json',{'port':server.server_address[1],'pid':os.getpid()})
threading.Thread(target=server.serve_forever,daemon=True).start()
def save_color(path,y,uv):
    w,h=2320,1744
    yy=Image.fromarray(y).point([max(0,min(255,round((i-16)*255/219))) for i in range(256)])
    chroma=np.frombuffer(uv,dtype='u1').reshape(h//2,w//2,2)[::-1,::-1]
    cb=Image.fromarray(chroma[:,:,0]).resize((w,h),Image.Resampling.BILINEAR)
    cr=Image.fromarray(chroma[:,:,1]).resize((w,h),Image.Resampling.BILINEAR)
    im=Image.merge('YCbCr',(yy,cb,cr)).convert('RGB')
    im.save(path,compress_level=2)
def overview():
    prior=time.monotonic()-2
    while running:
        if time.monotonic()-prior<2:
            time.sleep(.1);continue
        with cond:
            if not ring:
                cond.wait(.3);continue
            rec,frame=ring[-1]
        im=Image.fromarray(frame).resize((1160,872),Image.Resampling.BOX)
        im.save(HERE/'latest.tmp',format='PNG',compress_level=2)
        (HERE/'latest.tmp').replace(HERE/'latest.png')
        with cond: c=color
        if c and not (HERE/'first-color.png').exists():
            save_color(HERE/'first-color.png',c[1],c[2])
            atom_json(HERE/'first-color.json',c[0])
        if not (HERE/'first.png').exists():
            put_png(HERE/'first.png',frame)
            atom_json(HERE/'first.json',rec)
        atom_json(HERE/'latest.json',rec);prior=time.monotonic()
threading.Thread(target=overview,daemon=True).start()
def read_exact(pipe,n):
    b=pipe.read(n)
    if len(b)!=n:raise EOFError(f'stream closed, expected {n}, read {len(b)}')
    return b
def stopped(*args):
    global running
    running=False
    cap.terminate()
with (HERE/'helper.stderr').open('ab') as log:
    cap=subprocess.Popen([str(HELPER)],stdout=subprocess.PIPE,stderr=log,bufsize=4*1024*1024)
signal.signal(signal.SIGTERM,stopped)
signal.signal(signal.SIGINT,stopped)
clock_pair=(time.monotonic_ns(),time.time_ns())
atom_json(HERE/'clock.json',{'monotonic_ns':clock_pair[0],'wall_ns':clock_pair[1],'utc':utc(clock_pair[1])})
table=(HERE/'frames.csv').open('w',buffering=1)
cw=csv.writer(table);cw.writerow(['seq','pts_ns','host_ns','wall_ns','mean_right','mean_mid','mean_print','right_y','right_gradient','mid_y','mid_gradient'])
slices=[(int(x*2320/4656),int(y*2320/4656)) for x,y in [(3200,3560),(2276,2588),(2700,2970)]]
profiles=[];profile_times=[];profile_seq=[];block=None
def saveblock():
    if not profiles:return
    # Eight vertical sightlines per optical region retain independent registration.
    out=PROFILES/('%010d.npz'%profile_seq[0])
    np.savez_compressed(out, profiles=np.array(profiles),pts_ns=np.array(profile_times),seq=np.array(profile_seq),slices=slices,y0=450,y1=1290)
    profiles.clear();profile_times.clear();profile_seq.clear()
try:
    while running:
        magic,hlen,plen=struct.unpack('<4sII',read_exact(cap.stdout,12))
        if magic!=b'GPO1':raise ValueError('bad GPO1 header')
        h=json.loads(read_exact(cap.stdout,hlen)); data=read_exact(cap.stdout,plen)
        if h['type']!='frame':
            with (HERE/'events.jsonl').open('a') as q:q.write(json.dumps(h)+'\n')
            if h['type']=='error':raise RuntimeError(h)
            continue
        nw=h['height']*h['width']
        frame=np.frombuffer(data,dtype='u1',count=nw).reshape(h['height'],h['width'])[::-1,::-1]
        wall=h['pts_ns']-clock_pair[0]+clock_pair[1]
        rec={k:h[k] for k in ('seq','pts_ns','host_ns','width','height')}
        rec.update(wall_ns=wall,utc=utc(wall))
        with cond:
            if h['codec']=='nv12':color=(rec,frame,data[nw:])
            ring.append((rec,frame));latest=rec;cond.notify_all()
        # Compute only the image bands. Each cell is the measured mean luma of adjoining native columns.
        bands=[]
        for x0,x1 in slices:
            unit=(x1-x0)//8
            bands.append(frame[450:1290,x0:x0+8*unit].reshape(840,8,unit).mean(axis=2,dtype=np.float32).T)
        profile=np.rint(np.stack(bands)*4).astype('u2')
        profiles.append(profile);profile_times.append(h['pts_ns']);profile_seq.append(h['seq'])
        estimates=[]
        for b in bands[:2]:
            rows=b[:,260:540].mean(axis=0)
            smooth=np.convolve(rows,np.ones(5)/5,'same')
            g=-np.gradient(smooth)
            g[:10]=0;g[-10:]=0
            peak=int(np.argmax(g));idx=np.arange(max(0,peak-9),min(len(g),peak+10))
            wt=g[idx].clip(0);ed=float(710+np.average(idx,weights=wt)) if wt.sum()>0 else None
            estimates.append([round(ed,3) if ed else None,round(float(g[peak]),3)])
        rec.update(right_y=estimates[0][0],right_gradient=estimates[0][1],mid_y=estimates[1][0],mid_gradient=estimates[1][1])
        atom_json(HERE/'live.json',rec)
        if h['seq']%3==0:
            # PGM comments carry source timestamps with the pixels in a single atomic file.
            thumb=frame[::6,::6].copy()
            hh,ww=thumb.shape
            pp=HERE/'live.pgm.tmp'
            pp.write_bytes(('P5\n# seq=%d pts_ns=%d wall_ns=%d\n%d %d\n255\n'%(h['seq'],h['pts_ns'],wall,ww,hh)).encode()+thumb.tobytes())
            pp.replace(HERE/'live.pgm')
        cw.writerow([h['seq'],h['pts_ns'],h['host_ns'],wall,*[round(float(v.mean()),3) for v in bands],*estimates[0],*estimates[1]])
        if len(profiles)>=125:saveblock()
except Exception as exc:
    last_error=repr(exc)
    if running:traceback.print_exc()
finally:
    saveblock()
    running=False
    cap.terminate()
    table.close()
