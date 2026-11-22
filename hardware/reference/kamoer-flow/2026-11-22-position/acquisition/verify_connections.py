"""Test each current motor channel's actual liquid direction from the same visible cup edge."""
from pathlib import Path
import json,sys,socket,time,numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter1d
from board import Board,Journal
HERE=Path(__file__).parent.resolve()
CAM=HERE.parent/'camera'
SITES=[(1450,971),(1730,952),(1980,935)]
def capture(label):
    info=json.loads((CAM/'port.json').read_text())
    with socket.create_connection(('127.0.0.1',info['port']),timeout=10) as sock:
        sock.sendall((json.dumps(dict(label=label,samples=11,seconds=.6))+'\n').encode())
        response=json.loads(sock.makefile('rb').readline())
    if 'error' in response:raise RuntimeError(response['error'])
    p=Path(response['directory'])
    meta=response['mid']
    if time.monotonic_ns()-meta['pts_ns']>2_000_000_000:raise ValueError('old camera sample')
    return np.asarray(Image.open(p/'average.png')).astype(np.float32),dict(label=label,seq=meta['seq'],pts_ns=meta['pts_ns'])
def measure(before,after,positions,spec):
    out=[]
    for (x,_),y in zip(spec,positions):
        readings=[]
        for dx in [-10,-5,0,5,10]:
            xx=x+dx
            p=gaussian_filter1d(before[:,xx-3:xx+4].mean(axis=1),1.5)
            q=gaussian_filter1d(after[:,xx-3:xx+4].mean(axis=1),1.5)
            idx=round(y)+np.arange(-12,13)
            ref=p[idx];ref=ref-ref.mean()
            scores=[];shifts=np.arange(-36,37)
            for k in shifts:
                pt=q[idx+k];pt=pt-pt.mean();scores.append(float(np.dot(ref,pt)/(np.linalg.norm(ref)*np.linalg.norm(pt)+1e-6)))
            i=int(np.argmax(scores))
            if i in (0,len(scores)-1) or scores[i]<.85 or np.ptp(p[idx])<7:continue
            a,b,c=scores[i-1:i+2];curv=a-2*b+c
            frac=float(np.clip(.5*(a-c)/curv,-.5,.5)) if curv<-.00001 else 0
            readings.append((float(shifts[i]+frac),scores[i]))
        if len(readings)>=3:
            out.append(dict(x=x,start_y=y,shift=float(np.median(np.array(readings)[:,0])),score=float(np.median(np.array(readings)[:,1])),columns=len(readings)))
    if len(out)<2:raise ValueError('Insufficient visible edges: '+str(out))
    return out
def run(tag,order,initial):
    j=Journal(HERE/(tag+'.jsonl'));b=Board('/dev/cu.usbserial-120',j)
    base=initial or [float(y) for x,y in SITES]
    try:
        for i,head in enumerate(order):
            label=f'{tag}-{i:02d}-{head}'
            pre,pinfo=capture(label+'-pre')
            j.append('verification_pre',label=label,head=head,sites=SITES,positions=base,pre=pinfo)
            if head!='idle':
                # Both directions leave the measured starting level well inside the cup.
                if not 820<base[1]<1035:raise RuntimeError('Outside checked liquid band')
                if time.monotonic_ns()-pinfo['pts_ns']>2_000_000_000:raise RuntimeError('Stale live frame')
                ack=b.gate(head,600)
                j.append('gate',label=label,gate_index=1,**ack)
            time.sleep(2.6)
            post,pout=capture(label+'-post')
            read=measure(pre,post,base,SITES)
            moves=np.array([d['shift'] for d in read])
            j.append('verification_observation',label=label,head=head,readings=read,post=pout,median_shift_px=float(np.median(moves)))
            print(label,[(a['x'],round(a['shift'],2),round(a['score'],3)) for a in read],flush=True)
            if head=='idle':
                if np.max(abs(moves))>2.:raise ValueError('Changing starting level')
            else:
                pos=sum(moves>3);neg=sum(moves<-3)
                if max(pos,neg)<2 or np.ptp(moves)>11:raise ValueError('Disagreement at the liquid edges: '+str(moves))
                move=float(np.median(moves))
                base=[y+next((q['shift'] for q in read if q['x']==x),move) for (x,_),y in zip(SITES,base)]
    finally:
        b.close();j.append('session_end')
if __name__=='__main__':
    run(sys.argv[1],sys.argv[2].split(','),([float(v) for v in sys.argv[3].split(',')] if len(sys.argv)>3 else None))
