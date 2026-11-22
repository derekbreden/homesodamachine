"""Finish the native stream and its private recorders, then verify the original hardware settings."""
import csv
import datetime
import json
import os
import signal
import subprocess
import time
from pathlib import Path

import numpy as np
from controls import parse,show

HERE=Path(__file__).resolve().parent
def process(pid):
    return subprocess.run(['ps','-p',str(pid),'-o','command='],text=True,capture_output=True).stdout.strip()
def stop(pid,suffix):
    command=process(pid)
    if not command:return
    if not command.endswith(suffix):raise RuntimeError(f'Process does not belong to this camera: {pid}')
    os.kill(pid,signal.SIGTERM)
def wait_empty(pid,suffix):
    end=time.monotonic()+15
    while time.monotonic()<end and process(pid).endswith(suffix):time.sleep(.1)
    if process(pid).endswith(suffix):raise RuntimeError(f'Camera process remains: {pid}')
def last_sequence(name):
    with (HERE/name).open('rb') as f:
        f.seek(max(0,f.seek(0,2)-800));lines=f.read().splitlines();return int(lines[-1].split(b',',1)[0])
def close():
    original=parse((HERE/'original-uvc.txt').read_text())
    if parse((HERE/'restored-uvc.txt').read_text())!=original:raise ValueError('Starting controls have not been restored')
    feed=json.loads((HERE/'port.json').read_text())['pid'];suffix=str(HERE/'feed.py')
    if not process(feed).endswith(suffix):raise ValueError('Unexpected capture owner')
    kids=subprocess.check_output(['pgrep','-P',str(feed)],text=True).split()
    helpers=[int(k) for k in kids if process(int(k)).endswith(str(HERE/'nativecamera'))]
    if len(helpers)!=1:raise RuntimeError('Unexpected native capture process')
    owned={}
    for pidfile,script in [('steward.pid','steward.py'),('front_preview.pid','front_preview.py'),('rim-measure.pid','rim_measure.py'),('upper-contact.pid','upper_contact.py')]:
        pid=int((HERE/pidfile).read_text());end=str(HERE/script)+(' record' if script=='rim_measure.py' else '')
        owned[script]=(pid,end)
    for k in ('steward.py','front_preview.py'):stop(*owned[k]);wait_empty(*owned[k])
    stop(feed,suffix);wait_empty(feed,suffix);wait_empty(helpers[0],str(HERE/'nativecamera'))
    last=last_sequence('frames.csv');deadline=time.monotonic()+20
    names=['upper-rim.csv','direct-inner-contact.csv']
    while time.monotonic()<deadline and min(last_sequence(n) for n in names)<last:time.sleep(.3)
    final={n:last_sequence(n) for n in names}
    if any(s!=last for s in final.values()):raise RuntimeError(f'Final camera traces lag native frame {last}: {final}')
    for k in ('rim_measure.py','upper_contact.py'):stop(*owned[k]);wait_empty(*owned[k])
    after=show('restored-after-close-uvc.txt');diff={k:[v,after.get(k)] for k,v in original.items() if after.get(k)!=v}
    clock=np.genfromtxt(HERE/'frames.csv',delimiter=',',names=True,dtype=None,encoding=None)
    pts=clock['pts_ns'];delta=np.diff(pts)/1e6
    cadence={'native_frames':len(pts),'fps':float((len(pts)-1)*1e9/(pts[-1]-pts[0])),
             'first_pts_ns':int(pts[0]),'last_pts_ns':int(pts[-1]),
             'interval_ms_percentiles':dict(zip(['min','median','p95','p99','max'],np.percentile(delta,[0,50,95,99,100]).tolist())),
             'callback_delay_ms_percentiles':dict(zip(['median','p95','p99'],np.percentile((clock['host_ns']-pts)/1e6,[50,95,99]).tolist())),
             'gaps_over_55_ms':[[int(clock['seq'][i]),int(clock['seq'][i+1]),round(float(delta[i]),3)] for i in np.flatnonzero(delta>55)]}
    (HERE/'cadence.json').write_text(json.dumps(cadence,indent=2)+'\n')
    result={'closed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'verified_controls':len(original),'original_register_differences':diff,
            'native_last_sequence':last,'last_sequence_by_native_tracker':final,'closed_processes':[suffix,str(HERE/'nativecamera'),*[s for _,s in owned.values()]],
            'camera_budget_last_sample':json.loads((HERE/'storage.json').read_text())}
    (HERE/'closure.json').write_text(json.dumps(result,indent=2)+'\n');(HERE/'port.json').unlink()
    if diff:raise RuntimeError(diff)
    print(json.dumps(result))
if __name__=='__main__':close()
