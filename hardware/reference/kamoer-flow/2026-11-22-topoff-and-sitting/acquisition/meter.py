"""Apply the specified meter history to the live appliance and record the controller acknowledgements."""
import math
import re
import time
from stream import live


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


def check_stream_until(board,deadline,camera):
    while True:
        remaining=deadline-time.monotonic()
        if remaining<=0:return
        live(camera)
        # Keep the raw board output for the entire waveform. A tty prompt may have no newline.
        if board.port.in_waiting:
            line=board.line()
            if re.search(r'gas alarm|the pump would not start|could not be opened|refused|valves closed',line,re.I):
                raise RuntimeError(('early controller closure',line))
        time.sleep(min(.008,remaining))


def pour(board,head,settings,camera):
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
        check_stream_until(board,boundary,camera)
    board.send('flow 0 0')
    done=await_line(board,rf'pour {head}: flow stopped after (\d+) ms, (\d+) bursts? — valves closed',4.0)
    stamp=time.monotonic()
    board.events.append('board_pour_end',head=head,elapsed_ms=int(done[1]),bursts=int(done[2]),receipt_clock=stamp)
    return {'bursts':int(done[2]), 'elapsed_ms':int(done[1]), 'end_clock':stamp,
            'first_on':int(first[3]), 'first_off':int(first[4]), 'valves':first[2]}


