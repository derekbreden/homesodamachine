"""Hold one board's render mutex until its parent's stdin pipe closes."""
import fcntl
import hashlib
import json
import os
import select
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'hardware/scripts'))
import _run_slots

if _run_slots.current() is None:
    raise SystemExit('board mutex requires a verified parent run lease')
key = sys.argv[1]
path = _run_slots.directory() / ('board.' + hashlib.sha256(key.encode()).hexdigest()[:16] + '.lock')
fd = os.open(path, os.O_RDWR | os.O_CREAT, 0o600)
try:
    while True:
        try:
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            break
        except BlockingIOError:
            if select.select([sys.stdin], [], [], 0.1)[0] and not sys.stdin.buffer.read(1):
                raise SystemExit(0)          # a cancelled waiter must not keep its parent's lease
    print(json.dumps({'ready': True}), flush=True)
    sys.stdin.buffer.read()                  # EOF on parent exit, including a crash
finally:
    os.close(fd)
