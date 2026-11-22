#!/usr/bin/env python3
"""Save a contemporaneous endpoint while the shared camera stream continues uninterrupted."""
import argparse,json,pathlib,socket
p=argparse.ArgumentParser()
p.add_argument('label');p.add_argument('--seconds',type=float,default=1.0);p.add_argument('--samples',type=int,default=7);p.add_argument('--offset',type=float,default=0)
a=p.parse_args()
here=pathlib.Path(__file__).resolve().parent
port=json.loads((here/'port.json').read_text())['port']
with socket.create_connection(('127.0.0.1',port), timeout=5) as s:
    s.settimeout(60)
    s.sendall((json.dumps(vars(a)|({'op':'status'} if a.label=='status' else {}))+'\n').encode())
    response=json.loads(s.makefile('rb').readline())
if response.get('error'):raise SystemExit(response['error'])
if 'directory' in response:print(response['directory'])
else:print(json.dumps(response))
