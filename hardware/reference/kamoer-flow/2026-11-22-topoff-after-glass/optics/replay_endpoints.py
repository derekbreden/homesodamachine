"""Replay archived endpoint pixels (this record's, or Codex's) through the frozen reader on the NumPy filters and compare with the journal."""
import json, sys, glob
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(HERE / 'shim'), str(HERE)]; sys.path.append('/opt/homebrew/lib/python3.13/site-packages')
import numpy as np
from cup_volume import CROP
from read_levels import measure_gray

def canvas_from(npz):
    with np.load(npz) as z:
        x, y, pix = z['sensor_x'], z['sensor_y'], z['native_luma']
        avg = np.rint(np.mean(pix, axis=0, dtype=np.float32)).astype(np.uint8).T
    l, top, r, b = CROP
    c = np.zeros((b - top, r - l), np.uint8)
    c[np.ix_(y - top, x - l)] = avg
    return c

if __name__ == '__main__':
    rec = Path(sys.argv[1])
    logged = {}
    for f in glob.glob(str(rec / 'logs/*.jsonl')):
        for s in open(f):
            r = json.loads(s)
            if r['event'] == 'image':
                logged[r['label']] = r['readings']
    worst = 0; n = 0
    for npz in sorted(glob.glob(str(rec / 'camera/endpoints/*.npz'))):
        lab = Path(npz).stem
        if lab not in logged: continue
        got = measure_gray(canvas_from(npz))
        for k in got:
            a, b = got[k]['row'], logged[lab][k]['row']
            worst = max(worst, abs(a - b)); n += 1
    print('compared', n, 'sightline readings; worst row difference', worst)
