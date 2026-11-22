"""Apply the established camera settings and restore the measured starting controls after the last pour."""
import argparse
import json
import re
import subprocess
import time
from pathlib import Path

here = Path(__file__).resolve().parent
uvc = here.parents[3] / 'tools/panelcam-uvc/uvc.js'
def show(name):
    value = subprocess.check_output(['node', str(uvc), 'show'], text=True)
    (here / name).write_text(value)
    return parse(value)

def parse(text):
    return {m[1]:int(m[2]) for m in re.finditer(r'^\s+([a-z_]+)\s+(-?\d+)', text, re.M)}

def write(key, value):
    start = time.monotonic_ns()
    got = int(subprocess.check_output(['node', str(uvc), 'set', key, str(value)], text=True))
    with (here / 'control-events.jsonl').open('a') as log:
        log.write(json.dumps(dict(start_ns=start, done_ns=time.monotonic_ns(), control=key, requested=value, readback=got))+'\n')
    if got != value:
        raise RuntimeError((key, value, got))

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action',choices=['freeze','restore'])
    action=parser.parse_args().action
    original=parse((here/'original-uvc.txt').read_text())
    if action=='freeze':
        values=[('auto_focus',0),('auto_exposure_mode',1),('absolute_exposure_time',275),('gain',12),('white_balance_temperature_auto',0),('white_balance_temperature',4600),('sharpness',3),('absolute_focus',380)]
        for key,value in values:write(key,value)
        time.sleep(.65)
        write('absolute_focus',500)
        time.sleep(1.5)
        frozen=show('frozen-uvc.txt')
        expected=dict(values,absolute_focus=500)
        assert all(frozen[k]==v for k,v in expected.items())
    else:
        for key,value in [('auto_focus',0),('auto_exposure_mode',1),('white_balance_temperature_auto',0)]:write(key,value)
        for key in ('absolute_focus','absolute_exposure_time','gain','white_balance_temperature','sharpness','white_balance_temperature_auto','auto_exposure_mode','auto_focus'):
            write(key,original[key])
        time.sleep(.75)
        restored=show('restored-uvc.txt')
        if restored!=original:raise RuntimeError({k:(v,restored.get(k)) for k,v in original.items() if v!=restored.get(k)})

if __name__=='__main__':main()
