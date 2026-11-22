"""Acquire settled photographs and track the liquid between them during the physical trials."""
import json
import re
import socket
import time
from pathlib import Path

import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter1d

HERE=Path(__file__).resolve().parent
CAMERA=HERE.parent/'camera'
OPTICS=HERE.parent/'optics'
RECORD=HERE.parents[3]/'hardware/reference/kamoer-flow/2026-11-22-pour-predictions'
WINDOWS=CAMERA/'windows'
# Each lane follows the front-wall edge in clear glass on the upright full-field photograph.
LANES=[(972,986),(990,989),(1018,991),(1036,990),(1450,971),(1986,932)]


def live():
    raw=(CAMERA/'live.pgm').read_bytes().split(b'\n',4)
    seq,pts,_=map(int,re.findall(rb'\d+',raw[1]))
    age=(time.monotonic_ns()-pts)/1e9
    if raw[0]!=b'P5' or not 0<=age<.7:raise RuntimeError(('stale live preview',seq,age))
    return seq


def exposure(label, seconds=.45):
    live()
    req={'label':label,'seconds':seconds,'samples':9}
    with socket.create_connection(('127.0.0.1',json.loads((CAMERA/'port.json').read_text())['port']),timeout=6) as sock:
        sock.settimeout(10)
        sock.sendall((json.dumps(req)+'\n').encode())
        res=json.loads(sock.makefile('rb').readline())
    if res.get('error'):raise RuntimeError(res['error'])
    if time.monotonic_ns()-res['mid']['pts_ns']>2_600_000_000:raise RuntimeError('stale settled photograph')
    return Path(res['directory'])


def scan(window):
    with Image.open(window/'average.png') as f:
        a=np.asarray(f.convert('L'))
    out=[]
    for x,y in LANES:
        v=gaussian_filter1d(a[:,x-4:x+5].mean(axis=1),2.3)
        lo,hi=y-110,y+122
        j=np.arange(lo,hi)
        g=v[j-5]-v[j+6]
        i=j[int(np.argmax(g))]
        local=np.arange(i-3,i+4)
        center=np.average(local,weights=np.maximum(-np.gradient(v)[local],1e-5))
        out.append([x,round(float(center),3),round(float(g.max()),2)])
    return out


def clock_sleep(t):
    time.sleep(max(0,t-time.monotonic()))
