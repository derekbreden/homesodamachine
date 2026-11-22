"""Measure the effect of fixed white-balance temperature on the stationary cup edge."""
from pathlib import Path
import json,subprocess,sys,time
p=Path(__file__).resolve().parent
repo=p.parents[3]
uvc=str(repo/'tools/panelcam-uvc/uvc.js')
node=subprocess.Popen(['node',uvc,'serve'],stdin=subprocess.PIPE,stdout=subprocess.PIPE,text=True,bufsize=1)
data=(p/'control-events.jsonl').open('a',buffering=1)
def record(ev):
    ev.update(mono_ns=time.monotonic_ns(),wall_ns=time.time_ns())
    data.write(json.dumps(ev)+'\n')
def setv(k,v):
    start=time.monotonic_ns()
    print(f'set {k} {v}',file=node.stdin,flush=True)
    got=node.stdout.readline().strip()
    record(dict(op='set',start_ns=start,control=k,asked=v,readback=got))
    if int(got)!=v: raise RuntimeError((k,v,got))
def endwindow(label):
    record(dict(op='start_window',label=label))
    subprocess.run([sys.executable,str(p/'endpoint.py'),label,'--seconds','0.9','--samples','9'],check=True)
    record(dict(op='end_window',label=label))
for k,v in [('auto_focus',0),('auto_exposure_mode',1),('absolute_exposure_time',275),('gain',12),('white_balance_temperature_auto',0),('white_balance_temperature',4600),('sharpness',3),('absolute_focus',380)]:
    setv(k,v)
time.sleep(.65)
setv('absolute_focus',500)
time.sleep(1.4)
endwindow('balance-4600-before')
for temp,label in [(3000,'low'),(6500,'high'),(4600,'return')]:
    setv('white_balance_temperature',temp)
    time.sleep(1.1)
    endwindow('balance-'+str(temp)+'-'+label)
record(dict(op='frozen_for_wet_runs'))
(p/'frozen-uvc.txt').write_bytes(subprocess.check_output(['node',uvc,'show']))
print('frozen',flush=True)
node.stdin.write('quit\n');node.stdin.flush();node.wait(timeout=2)
