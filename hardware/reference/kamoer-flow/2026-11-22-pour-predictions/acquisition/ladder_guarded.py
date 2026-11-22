"""Continue the marked-level sweep with neighboring liquid edges checking a locally obscured strip."""
import argparse
import json
import time

import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter1d

from board import Board,Journal
from lab import HERE,WINDOWS,exposure,live


def local_edge(gray,x,hint,radius):
    v=gaussian_filter1d(gray[:,x-4:x+5].mean(axis=1),2.3)
    rows=np.arange(round(hint)-radius,round(hint)+radius+1)
    fall=v[rows-5]-v[rows+6]
    i=int(np.argmax(fall));y=rows[i];k=np.arange(y-3,y+4)
    weights=np.maximum(-np.gradient(v)[k],1e-5)
    return {'row':float(np.average(k,weights=weights)),'contrast':float(fall[i]),'on_edge':i<2 or i>len(rows)-3}


def observe(name,hints,j,radius):
    path=exposure(name,.55)
    with Image.open(path/'average.png') as f:gray=np.asarray(f)
    rr={x:local_edge(gray,x,hint,radius) for x,hint in hints.items()}
    main=rr[990]
    # Center the local search on the photographed motion of nearby glass lanes.
    shifts=[rr[x]['row']-hints[x] for x in (972,1018,1036)
            if rr[x]['contrast']>=7 and not rr[x]['on_edge']]
    if len(shifts)<2:
        raise ValueError(('neighboring contacts unresolved',name,rr))
    neighbor_shift=float(np.median(shifts))
    agreeing=[delta for delta in shifts if abs(delta-neighbor_shift)<4.5]
    expected=hints[990]+neighbor_shift
    if len(agreeing)<2:
        raise ValueError(('neighboring contacts disagree',name,rr))
    if main['on_edge'] or main['contrast']<7 or abs(main['row']-expected)>5.5:
        local=local_edge(gray,990,expected,6)
        if not local['on_edge'] and local['contrast']>=7 and abs(local['row']-expected)<5.5:
            main=local
        else:
            main={'row':expected,'contrast':local['contrast'],'on_edge':False,
                  'source':'neighbor-movement only; no direct x990 measurement','x990_raw':local}
        rr[990]=main
    j.append('ladder_image',label=name,lanes=rr)
    if not 760<main['row']<1160:
        raise ValueError(('outside photographed sweep',name,rr))
    return rr


def dwell(label,points,j):
    began=time.monotonic()
    for seconds in [5,20,40,65]:
        time.sleep(max(0,began+seconds-time.monotonic()))
        obs=observe(f'{label}-hold{seconds}',{x:v['row'] for x,v in points.items()},j,12)
        j.append('hold',label=label,window=f'{label}-hold{seconds}',elapsed_s=time.monotonic()-began,main_row=obs[990]['row'])
    return obs


def sweep(board,j,tag,legs,start_hints):
    points=observe(tag+'-entry',start_hints,j,13)
    for leg,target in legs:
        inside_held=False
        for i in range(110):
            y=points[990]['row'];gap=target-y
            if abs(gap)<2.6:break
            direction=1 if gap>0 else -1
            head='A' if gap>0 else 'B'
            distance_to_anchor=min(abs(y-c) for c in (848,985,1005,1130))
            desired=min(abs(gap),4.2 if distance_to_anchor<25 else 12.5)
            if 1097<y<1126 or 815<y<870:
                desired=min(desired,2.6)
            ms=round(max(65,min(600,desired/(27 if head=='A' else 24)*1000)))
            label=f'{tag}-{leg}-{i:02d}'
            live()
            receipt=board.gate(head,ms)
            j.append('ladder_gate',label=label,leg=leg,target_y=target,head=head,width_ms=ms,**receipt)
            time.sleep(2.6)
            previous=points
            points=observe(label,{x:v['row']+direction*desired for x,v in previous.items()},j,14)
            shift=points[990]['row']-y
            agreement=[x for x in (972,1018,1036) if not points[x]['on_edge'] and points[x]['contrast']>6 and
                       abs((points[x]['row']-previous[x]['row'])-shift)<max(5,abs(shift)*.52)]
            j.append('ladder_step',label=label,leg=leg,head=head,operating_y=points[990]['row'],
                     independent_agreement=agreement,step_px=shift)
            print(label,head,ms,round(points[990]['row'],2),'Δ',round(shift,2),'others',agreement,flush=True)
            if shift*direction<.35 or abs(shift)>max(8,1.8*desired+3) or not agreement:
                raise RuntimeError(('uncertain step',label,shift,agreement))
            if leg in ('down-low','up-high') and not inside_held:
                interior = 1092 if leg=='down-low' else 875
                if (y-interior)*(points[990]['row']-interior)<=0:
                    points=dwell(tag+'-'+leg+'-inside',points,j)
                    inside_held=True
        else:raise RuntimeError(('target not reached',leg))
        j.append('leg_end',leg=leg,measured_y=points[990]['row'],target_y=target)
        if leg in ('down-low','up-high'):points=dwell(tag+'-'+leg,points,j)


if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('tag');ap.add_argument('legs',nargs='+');ap.add_argument('--hint',type=float,default=990)
    a=ap.parse_args();goal=[(s.split('=')[0],float(s.split('=')[1])) for s in a.legs]
    if any(not 798<=x<=1170 for _,x in goal):raise ValueError(goal)
    j=Journal(HERE/'graduations.jsonl');b=Board('/dev/cu.usbserial-120',j)
    try:sweep(b,j,a.tag,goal,{990:a.hint,972:a.hint-5,1018:a.hint+3,1036:a.hint+8})
    except BaseException as e:j.append('halt',error=repr(e));raise
    finally:
        b.close();j.append('closed')
