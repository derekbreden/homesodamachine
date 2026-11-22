"""Test short bounded transfers against a contemporaneous image while qualifying the camera volume band."""
import sys,time
from board import Board,Journal
from lab import HERE,exposure,scan,live
label=sys.argv[1]
head=sys.argv[2]
ms=int(sys.argv[3])
assert head in ('A','B','idle') and 0<=ms<=1250
j=Journal(HERE/'qualifications.jsonl')
b=Board('/dev/cu.usbserial-120',j)
try:
    pre=exposure(label+'-pre')
    s=scan(pre)
    print('before',s,flush=True)
    j.append('before',label=label,window=pre.name,lanes=s)
    if min(x[2] for x in s[:3])<5: raise ValueError('front edge is unreadable')
    live()
    if head!='idle':
        j.append('qualification_gate',label=label,head=head,**b.gate(head,ms))
    time.sleep(2.5)
    post=exposure(label+'-post')
    t=scan(post)
    print('after',t,flush=True); print('delta',[round(y[1]-x[1],2) for x,y in zip(s,t)],flush=True)
    j.append('after',label=label,window=post.name,lanes=t)
finally:
    b.close()
    j.append('closed')
