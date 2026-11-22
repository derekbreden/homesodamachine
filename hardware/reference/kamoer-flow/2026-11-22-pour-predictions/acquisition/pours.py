"""Issue bounded meter inputs to the appliance and pair every resulting pour with settled cup images."""
import importlib
import json
import math
import os
import re
import sys
import time
from pathlib import Path

import numpy as np
from board import Board, Journal
from lab import CAMERA, HERE, OPTICS, RECORD, WINDOWS, exposure, live, scan

sys.path.insert(0,str(RECORD/'analysis'))
import cup_volume

DESIGN=json.loads((RECORD/'preregistration.json').read_text())
ORIGINAL=HERE/'original-settings.json'
REF=WINDOWS/'station-idle'
REF_ML=246.17
REF_CLEAR=scan(REF)[1][1]
USB='/dev/cu.usbserial-120'


def await_line(board,pattern,timeout):
    deadline=time.monotonic()+timeout
    while time.monotonic()<deadline:
        line=board.line()
        if m:=re.search(pattern,line):return m
        if re.search(r'refused|could not be opened|gas alarm|unknown:',line,re.I):raise RuntimeError(line)
    raise TimeoutError(pattern)


def read_settings(board):
    board.send('status')
    flavor=await_line(board,r'flavor\s+([AB])\s',2)[1]
    ratio=await_line(board,r'ratio\s+A 1:(\d+), B 1:(\d+)',2)
    await_line(board,r'valves\s+all closed',2)
    await_line(board,r'volume\s+',2)
    return {'flavor':flavor,'A':int(ratio[1]),'B':int(ratio[2])}


def configure(board,previous,head,ratio):
    if previous[head]!=ratio:
        board.send(f'ratio {head.lower()} {ratio}')
        found=await_line(board,r'ratio A 1:(\d+), B 1:(\d+)',2)
        values={'A':int(found[1]),'B':int(found[2])}
        if values[head]!=ratio:raise RuntimeError(('ratio selection',head,values))
        previous.update(values)
    if previous['flavor']!=head:
        board.send(f'flavor {head.lower()}')
        await_line(board,rf'flavor {head} \(',2)
        previous['flavor']=head


def restore(board):
    if not ORIGINAL.is_file():return
    original=json.loads(ORIGINAL.read_text())
    current=read_settings(board)
    for h in ('A','B'):
        if current[h]!=original[h]: configure(board,current,h,original[h])
    configure(board,current,original['flavor'],original[original['flavor']])
    restored=read_settings(board)
    if restored!=original:raise RuntimeError(('settings restore failed',restored,original))
    board.events.append('original_settings_restored',settings=restored)


def window(label,journal):
    w=exposure(label)
    lanes=scan(w)
    # A separate live reference marks the working band; the dose score uses the printed scales.
    clear=lanes[1]
    if clear[2]<7 or abs(clear[1]-REF_CLEAR)>98:
        raise RuntimeError(('uncertain clear glass contact',label,clear))
    operating=REF_ML-(clear[1]-REF_CLEAR)*.42
    optic=cup_volume.read(w)
    journal.append('image',label=label,operating_ml=operating,clear=clear,optics=optic)
    if not (209<=operating<=281):raise RuntimeError(('outside guarded band',label,operating))
    return {'label':label,'operating_ml':operating,'optics':optic}


def arrange(board,journal,label,target,max_steps=4):
    at=window(label+'-entry',journal)
    for i in range(max_steps):
        error=target-at['operating_ml']
        if abs(error)<=1.25:break
        ch='B' if error>0 else 'A'
        ms=round(min(1.25,max(.04,abs(error)/(10 if ch=='B' else 11.5)))*1000)
        before=at['operating_ml']
        receipt=board.gate(ch,ms)
        journal.append('position_gate',label=label,head=ch,ms=ms,**receipt)
        time.sleep(2.25)
        at=window(f'{label}-set{i+1}',journal)
        motion=(at['operating_ml']-before)*(1 if ch=='B' else -1)
        if ms>=240 and (motion<.45 or motion>ms*.025+2):
            raise RuntimeError(('positioning moved unexpectedly',label,ms,motion))
    if abs(target-at['operating_ml'])>3:
        raise RuntimeError(('start position outside matched band',label,target,at['operating_ml']))
    return at


def check_stream_until(board,deadline):
    while True:
        remaining=deadline-time.monotonic()
        if remaining<=0:return
        live()
        # Keep the raw board output for the entire waveform. A tty prompt may have no newline.
        if board.port.in_waiting:
            line=board.line()
            if re.search(r'gas alarm|the pump would not start|could not be opened|refused|valves closed',line,re.I):
                raise RuntimeError(('early controller closure',line))
        time.sleep(min(.025,remaining))


def pour(board,head,settings):
    stages=settings['meter']
    hp,hold=stages[0]
    board.send(f'flow {hp} {math.ceil((hold+200)/1000)}')
    first=await_line(board,rf'pour {head} at 1:(\d+): valves (.*?) open, pump {head} bursting (\d+) on / (\d+) off',1.8)
    if int(first[1])!=settings['ratio']:raise RuntimeError(('wrong ratio',first.group()))
    began=time.monotonic()
    board.events.append('board_pour_start',head=head,ratio=int(first[1]),first_on=int(first[3]),first_off=int(first[4]),valves=first[2],first_receipt_clock=began)
    boundary=began
    for i,(pulses,ms) in enumerate(stages):
        if i:
            board.send(f'flow {pulses} {math.ceil((ms+200)/1000)}')
        boundary+=ms/1000
        check_stream_until(board,boundary)
    board.send('flow 0 0')
    done=await_line(board,rf'pour {head}: flow stopped after (\d+) ms, (\d+) bursts? — valves closed',4.0)
    stamp=time.monotonic()
    board.events.append('board_pour_end',head=head,elapsed_ms=int(done[1]),bursts=int(done[2]),receipt_clock=stamp)
    return int(done[2]),int(done[1]),stamp


def measure_one(board,journal,phase,idx,trial,config,frozen,tag):
    head,name,block=trial['head'],trial['scenario'],trial['block']
    s=DESIGN['scenarios'][name]
    label=f'{tag}-{idx:03d}-{head.lower()}-{name.replace("_","-")}'
    prior=s['old_middle_ruler_rate_prediction_ml'][head]
    pred=frozen['forecasts'][name][head] if frozen else None
    signal=pred if pred is not None else prior
    offset=DESIGN['epochs']['validation_offset_ml'][block-1] if phase=='validation' else [0.,3.,-3.][block-1]
    target=REF_ML+offset+(1 if head=='A' else -1)*signal/2
    place=arrange(board,journal,label,target)
    before=place['optics']
    configure(board,config,head,s['ratio'])
    # The working reference and sign bound the entire uninterrupted transfer well inside both vessels.
    limit=s['ideal_on_s']*18+3
    edge=place['operating_ml']+(-1 if head=='A' else 1)*limit
    if not 193<=edge<=304:raise RuntimeError(('prospective band check',label,edge))
    journal.append('prediction',phase=phase,index=idx,block=block,label=label,scenario=name,head=head,pre=place['label'],
                   forecast_ml=pred,prior_ml=prior,ideal_bursts=s['ideal_bursts'],target_start_ml=target,start_operating_ml=place['operating_ml'])
    burst,elapsed,done=pour(board,head,s)
    time.sleep(max(0,done+2.9-time.monotonic()))
    after=window(label+'-post',journal)
    sign=1 if head=='B' else -1
    b,a=before,after['optics']
    def difference(face):
        one,two=b[face],a[face]
        if one.get('ok') and two.get('ok') and 'nominal_ml' in one and 'nominal_ml' in two:
            return sign*(two['nominal_ml']-one['nominal_ml'])
        return None
    d1,d2=difference('primary'),difference('held_out')
    moving=sign*(after['operating_ml']-place['operating_ml'])
    journal.append('trial',phase=phase,index=idx,block=block,scenario=name,head=head,label=label,pre=place['label'],post=after['label'],
                   start_ml=b['primary'].get('nominal_ml'),finish_ml=a['primary'].get('nominal_ml'),primary_ml=d1,heldout_ml=d2,
                   forecast_ml=pred,burst_count=burst,expected_bursts=s['ideal_bursts'],elapsed_ms=elapsed,operating_change_ml=moving,
                   optical_flags=[before['flags'],after['optics']['flags']])
    print(phase,idx,head,name,'forecast',None if pred is None else round(pred,2),'measured',None if d1 is None else round(d1,2),None if d2 is None else round(d2,2),'clear',round(moving,2),'bursts',burst,flush=True)
    if moving<max(0.4,.3*signal) or moving>2*signal+2:
        raise RuntimeError(('unexpected direction or transfer on independent working strip',label,moving,signal))


def run(phase,start,end,tag):
    raw=HERE/('train.jsonl' if phase=='training' else 'validation.jsonl')
    journal=Journal(raw)
    frozen=json.loads((RECORD/'frozen-model.json').read_text()) if phase=='validation' else None
    done_ids={z['index'] for z in map(json.loads,raw.read_text().splitlines()) if z['event']=='trial'}
    board=Board(USB,journal)
    try:
        config=read_settings(board)
        if not ORIGINAL.exists():ORIGINAL.write_text(json.dumps(config,indent=2)+'\n')
        journal.append('session',phase=phase,tag=tag,settings=config)
        for i,trial in enumerate(DESIGN['orders'][phase]):
            if i in done_ids or not start<=i<=end:continue
            measure_one(board,journal,phase,i,trial,config,frozen,tag)
    except BaseException as exc:
        journal.append('halt',error=repr(exc))
        board.send('flow 0 0');board.send('stop');time.sleep(.6)
        raise
    finally:
        try:
            board.status()
            restore(board)
        finally:
            board.close()
            journal.append('closed',phase=phase)


if __name__=='__main__':
    run(sys.argv[1],int(sys.argv[2]),int(sys.argv[3]),sys.argv[4])
