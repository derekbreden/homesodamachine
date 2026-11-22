"""Stop this run's camera and verify the original UVC settings after both capture processes have exited."""
import csv
import datetime
import json
import os
import signal
import subprocess
import time
from pathlib import Path

import numpy as np
from controls import show,parse

ROOT=Path(__file__).resolve().parent
def process(pid):
    return subprocess.run(['ps','-p',str(pid),'-o','command='],capture_output=True,text=True).stdout.strip()

def wait(pid,ending):
    start=time.monotonic()
    while time.monotonic()-start<15 and process(pid).endswith(ending):time.sleep(.1)
    if process(pid).endswith(ending):raise RuntimeError(f'Camera process {pid} has not stopped.')

def close():
    original=parse((ROOT/'original-uvc.txt').read_text());restored=parse((ROOT/'restored-uvc.txt').read_text())
    if original!=restored:raise ValueError('The control readback must already match the original.')
    f=json.loads((ROOT/'port.json').read_text())['pid'];feeder=str(ROOT/'feed.py');helper=str(ROOT/'nativecamera')
    if not process(f).endswith(feeder):raise RuntimeError('Unknown camera process.')
    children=[int(k) for k in subprocess.check_output(['pgrep','-P',str(f)],text=True).split()]
    owned=[c for c in children if process(c).endswith(helper)]
    if len(owned)!=1:raise RuntimeError('The native capture owner could not be verified.')
    os.kill(f,signal.SIGTERM);wait(f,feeder);wait(owned[0],helper)
    current=show('restored-after-close-uvc.txt')
    if current!=original:raise ValueError('The after-close UVC readback differs.')
    with (ROOT/'frames.csv').open() as f:
        frame_clock=np.asarray([(int(r['seq']),int(r['pts_ns']),int(r['host_ns'])) for r in csv.DictReader(f)],dtype=np.int64)
    seq,pts,callback=frame_clock.T;dt=np.diff(pts)*1e-6
    summary={'closed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'controls_restored':len(current),
             'control_differences':{},'capture_processes_closed':[feeder,helper],'native_frames':len(seq),'first_and_last_seq':[int(seq[0]),int(seq[-1])],
             'first_and_last_pts_ns':[int(pts[0]),int(pts[-1])],'monotonic_sequence':bool(np.all(np.diff(seq)==1) and np.all(np.diff(pts)>0)),
             'native_fps':float((len(pts)-1)*1e9/(pts[-1]-pts[0])),'native_interval_ms':dict(zip(('min','median','p95','p99','max'),np.percentile(dt,[0,50,95,99,100]).tolist())),
             'callback_delay_ms':dict(zip(('median','p95','p99'),np.percentile((callback-pts)*1e-6,[50,95,99]).tolist())),
             'gaps_over_55ms':int((dt>55).sum())}
    (ROOT/'closure.json').write_text(json.dumps(summary,indent=2)+'\n');(ROOT/'port.json').unlink()
    print(json.dumps(summary))
if __name__=='__main__':close()
