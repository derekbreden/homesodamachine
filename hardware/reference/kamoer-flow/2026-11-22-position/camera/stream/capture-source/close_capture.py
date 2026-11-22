"""Close this experiment's camera processes and verify register restoration with the stream stopped."""
from pathlib import Path
import ast,datetime,json,os,re,signal,subprocess,time
p=Path(__file__).resolve().parent;port=json.loads((p/'port.json').read_text())
procs=subprocess.check_output(['ps','-ax','-o','pid=,command='],text=True)
names=['guard.py','storage_watch.py','tube_watch.py','rim_watch.py','feed.py','nativecamera'];own={}
for l in procs.splitlines():
    z=l.strip().split(None,1)
    if len(z)!=2:continue
    for n in names:
        if z[1].endswith('pump-prediction-20261122/camera/'+n):own[n]=int(z[0])
assert own['feed.py']==port['pid'] and 'nativecamera' in own
for n in names[:5]:
    if n in own:os.kill(own[n],signal.SIGTERM)
def remaining():
    txt=subprocess.check_output(['ps','-ax','-o','pid=,command='],text=True)
    return [int(l.strip().split(None,1)[0]) for l in txt.splitlines() if any(l.endswith('pump-prediction-20261122/camera/'+n) for n in names)]
for _ in range(30):
    if not remaining():break
    time.sleep(.1)
left=remaining()
if left:raise RuntimeError(f'capture processes still active {left}')
uvc=p.parents[3]/'tools/panelcam-uvc/uvc.js'
after=subprocess.check_output(['node',str(uvc),'show'],text=True)
(p/'restored-after-close-uvc.txt').write_text(after)
parse=lambda txt:{m[1]:int(m[2]) for m in re.finditer(r'^\s+([a-z_]+)\s+(-?\d+)',txt,re.M)}
original=parse((p/'original-uvc.txt').read_text());restored=parse(after)
diff={k:[v,restored.get(k)] for k,v in original.items() if v!=restored.get(k)}
after_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='milliseconds')
closure={'utc':after_utc,'closed_processes':sorted(own),'remaining_capture_processes':left,'hardware_after_stop':restored,'register_differences':diff,'registered_controls_compared':len(original),'last_frame':json.loads((p/'live.json').read_text()),'scratch_storage_before_stop':json.loads((p/'storage.json').read_text())}
(p/'closure.json').write_text(json.dumps(closure,indent=2)+'\n')
(p/'port.json').unlink()
print('Stopped',sorted(own),'remaining',left,'register differences',diff)
