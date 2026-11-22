"""Compare fixed and autofocus on the stationary cup, then return the USB registers to their original state."""
from pathlib import Path
import csv,json,os,re,subprocess,sys,time
p=Path(__file__).resolve().parent
uvc=str(p.parents[3]/'tools/panelcam-uvc/uvc.js')
records=(p/'restore-events.jsonl').open('a',buffering=1)
def event(op,**fields):
    records.write(json.dumps(dict(op=op,mono_ns=time.monotonic_ns(),wall_ns=time.time_ns(),**fields))+'\n')
def show(name):
    v=subprocess.run(['node',uvc,'show'],capture_output=True,text=True,check=True).stdout
    (p/name).write_text(v);event('readback',file=name);return v
def set_reg(k,v):
    a=time.monotonic_ns()
    got=subprocess.run(['node',uvc,'set',k,str(v)],capture_output=True,text=True,check=True).stdout.strip()
    event('set',control=k,asked=v,readback=got,start_ns=a)
    if int(got)!=v:raise RuntimeError((k,v,got))
def capture(label):
    event('window_requested',label=label)
    subprocess.run([sys.executable,str(p/'endpoint.py'),label,'--seconds','.85','--samples','11'],check=True)
    event('window_recorded',label=label)
def run():
    show('wet-end-uvc.txt')
    try:
        capture('final-focus-fixed')
        set_reg('auto_focus',1)
        time.sleep(1.)
        show('af-early-uvc.txt')
        capture('final-focus-auto-early')
        time.sleep(1.8)
        show('af-late-uvc.txt')
        capture('final-focus-auto-late')
        set_reg('auto_focus',0)
        set_reg('absolute_focus',380)
        time.sleep(.65)
        set_reg('absolute_focus',500)
        time.sleep(1.4)
        show('af-return-uvc.txt')
        capture('final-focus-fixed-return')
    finally:
        # The pre-session baseline includes automatic exposure and white balance. Write their saved
        # manual registers first, then restore the original automatic-mode flags.
        set_reg('auto_focus',0);set_reg('absolute_focus',650)
        set_reg('auto_exposure_mode',1);set_reg('absolute_exposure_time',275);set_reg('gain',0)
        set_reg('white_balance_temperature_auto',0);set_reg('white_balance_temperature',4600)
        set_reg('sharpness',3);set_reg('white_balance_temperature_auto',1);set_reg('auto_exposure_mode',8)
        time.sleep(.6);show('restored-uvc.txt')
    parse=lambda txt:{m[1]:int(m[2]) for m in re.finditer(r'^\s+([a-z_]+)\s+(-?\d+)',txt,re.M)}
    old=parse((p/'original-uvc.txt').read_text());new=parse((p/'restored-uvc.txt').read_text())
    changes={k:[v,new.get(k)] for k,v in old.items() if new.get(k)!=v}
    event('compare',original=old,restored=new,differences=changes)
    print('UVC differences:',changes)
if __name__=='__main__':run()
