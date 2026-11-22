"""Request timestamped settled cup photographs from the live camera and reject stale frames."""
import json
import re
import socket
import time
from pathlib import Path


def live(camera):
    with (camera/'live.pgm').open('rb') as stream:
        if stream.readline().strip() != b'P5':
            raise ValueError('Invalid preview format')
        seq, stamp, _ = map(int, re.findall(rb'\d+', stream.readline()))
    if not 0 <= time.monotonic_ns()-stamp < 700_000_000:
        raise ValueError('Camera preview is stale')
    return seq


def exposure(camera, label):
    live(camera)
    request = dict(label=label, seconds=.45, samples=9)
    port = json.loads((camera/'port.json').read_text())['port']
    with socket.create_connection(('127.0.0.1', port), timeout=6) as sock:
        sock.settimeout(10)
        sock.sendall((json.dumps(request)+'\n').encode())
        response = json.loads(sock.makefile('rb').readline())
    if response.get('error') or time.monotonic_ns()-response['mid']['pts_ns'] > 2_600_000_000:
        raise RuntimeError(('Camera snapshot failed', response))
    return Path(response['directory'])
