"""Photograph the cup through PanelCamShot (the app holding the camera grant) and keep only the sightline columns the frozen reader uses."""
import glob
import json
import os
import re
import shutil
import subprocess
import sys
import threading
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(HERE.parent / 'optics' / 'shim'), str(HERE.parent / 'optics')]
sys.path.append('/opt/homebrew/lib/python3.13/site-packages')
from cup_volume import CROP  # noqa: E402
from read_levels import measure_gray  # noqa: E402

REPO = '/Users/derekbredensteiner/Developer/homesodamachine'
APP = f'{REPO}/tools/panelcam-shot/PanelCamShot.app'
UVC = f'{REPO}/tools/panelcam-uvc/uvc.js'
NODE = shutil.which('node')
W, H = 2320, 1744
# The 45 native columns Codex's endpoints keep: both sightlines and the x990 reader's neighbour lanes.
SENSOR_X = np.array([*range(968, 977), *range(986, 995), *range(1014, 1023), *range(1032, 1041), *range(1982, 1991)])
SENSOR_Y = np.arange(650, 1340)
FREEZE = [('auto_focus', 0), ('auto_exposure_mode', 1), ('absolute_exposure_time', 275), ('gain', 12),
          ('white_balance_temperature_auto', 0), ('white_balance_temperature', 4600), ('sharpness', 3),
          ('absolute_focus', 380)]
FROZEN = dict(FREEZE, absolute_focus=500)
RESTORE = [('auto_exposure_mode', 8), ('gain', 0), ('white_balance_temperature_auto', 1), ('absolute_focus', 650)]


def uvc_set(k, v):
    out = subprocess.run([NODE, UVC, 'set', k, str(v)], capture_output=True, text=True)
    return (out.stdout + out.stderr).strip()


def uvc_show():
    text = subprocess.run([NODE, UVC, 'show'], capture_output=True, text=True).stdout
    return {m[1]: int(m[2]) for m in re.finditer(r'^\s+([a-z_]+)\s+(-?\d+)', text, re.M)}


class Stream:
    """One open camera stream: controls frozen after the lens parks, frames reduced to sightline columns as they land."""

    def __init__(self, work, tag, seconds, every=2, journal=None):
        self.dir = Path(work) / 'dump' / tag
        shutil.rmtree(self.dir, ignore_errors=True)
        self.dir.mkdir(parents=True)
        self.tag, self.journal, self.seconds = tag, journal, seconds
        self.frames = []  # (counter, wall_s, cols uint8 (45, 690), patch_mean)
        self.lock = threading.Condition()
        self.done = False
        self.error = None
        self.want_full = None
        args = ['open', '-W', APP, '--args', '--out', str(self.dir / 'best.png'), '--match', '16MP',
                '--format', f'{W}x{H}:420v', '--dwell', str(seconds), '--max', str(seconds + 5),
                '--dump', str(self.dir), '--dump-max', str(int(seconds * 30 / every) + 20),
                '--dump-every', str(every), '--score', '200:200:100:100']
        self.t0 = time.time()
        self.proc = subprocess.Popen(args)
        self.collector = threading.Thread(target=self._collect, daemon=True)
        self.collector.start()
        self.ready_at = None
        self.controls = self._freeze()

    def log(self, event, **kw):
        if self.journal:
            self.journal.append(event, stream=self.tag, **kw)

    def _freeze(self):
        deadline = time.time() + 12
        while not self.frames and time.time() < deadline:
            time.sleep(.02)
        if not self.frames:
            raise RuntimeError(('camera stream produced no frames', self.tag))
        first = self.frames[0][1]
        time.sleep(max(0, max(self.t0 + 1.3, first + .8) - time.time()))
        marks = []
        for k, v in FREEZE:
            ta = time.time()
            marks.append((round(ta - self.t0, 3), k, v, uvc_set(k, v)))
        time.sleep(.65)
        marks.append((round(time.time() - self.t0, 3), 'absolute_focus', 500, uvc_set('absolute_focus', 500)))
        time.sleep(1.5)
        readback = uvc_show()
        self.ready_at = time.time()
        bad = {k: (v, readback.get(k)) for k, v in FROZEN.items() if readback.get(k) != v}
        self.log('camera_frozen', first_frame_s=round(first - self.t0, 3), ready_s=round(self.ready_at - self.t0, 3),
                 writes=marks, readback={k: readback.get(k) for k in FROZEN}, mismatched=bad)
        if bad:
            raise RuntimeError(('camera controls did not take', bad))
        return readback

    def _collect(self):
        seen = set()
        try:
            while True:
                alive = self.proc.poll() is None
                files = sorted(glob.glob(str(self.dir / '*_p0_s*.raw')))
                for p in files:
                    m = re.search(r'/(\d+)_\w+_(\d+)x(\d+)_[0-9.]+_p0_s(\d+)\.raw$', p)
                    n, w, h, stride = (int(g) for g in m.groups())
                    stem = p[:p.rindex('_p0_')]
                    p1 = glob.glob(stem + '_p1_*.raw')
                    later = any(int(re.search(r'/(\d+)_', q).group(1)) > n for q in files)
                    if n in seen or not (p1 or later or not alive):
                        continue
                    if os.path.getsize(p) != stride * h:
                        if alive:
                            continue
                    wall = os.stat(p).st_mtime
                    a = np.fromfile(p, dtype=np.uint8, count=stride * h).reshape(h, stride)[:, :w][::-1, ::-1]
                    cols = np.ascontiguousarray(a[SENSOR_Y[0]:SENSOR_Y[-1] + 1][:, SENSOR_X].T)
                    patch = float(a[300:400, 1100:1300].mean())
                    if self.want_full and self.ready_at and wall > self.ready_at:
                        np.save(self.want_full, np.ascontiguousarray(a[CROP[1]:CROP[3], CROP[0]:CROP[2]]))
                        self.want_full = None
                    for q in [p, *p1, stem + '.png']:
                        try:
                            os.remove(q)
                        except FileNotFoundError:
                            pass
                    seen.add(n)
                    with self.lock:
                        self.frames.append((n, wall, cols, patch))
                        self.lock.notify_all()
                if not alive and not glob.glob(str(self.dir / '*_p0_s*.raw')):
                    break
                time.sleep(.015)
        except Exception as exc:  # surfaced to the caller on the next photograph
            self.error = repr(exc)
        finally:
            for q in glob.glob(str(self.dir / '*.raw')):
                os.remove(q)
            with self.lock:
                self.done = True
                self.lock.notify_all()

    def alive(self):
        return self.proc.poll() is None and not self.done

    def live(self):
        if self.error:
            raise RuntimeError(self.error)
        if not self.frames or time.time() - self.frames[-1][1] > .9:
            raise RuntimeError(('camera stream is stale', self.tag))

    def window(self, n=9):
        """The next n frames that land after this call."""
        start = time.time()
        with self.lock:
            ok = self.lock.wait_for(lambda: self.error or self.done or
                                    sum(1 for f in self.frames if f[1] >= start) >= n, timeout=6)
        got = [f for f in self.frames if f[1] >= start][:n]
        if self.error or len(got) < n:
            raise RuntimeError(('camera window unavailable', self.tag, self.error, len(got)))
        return got

    def close(self):
        self.proc.wait()
        self.collector.join(timeout=10)


def canvas(stack):
    avg = np.rint(np.mean(stack, axis=0, dtype=np.float32)).astype(np.uint8).T  # (690, 45)
    left, top, right, bottom = CROP
    c = np.zeros((bottom - top, right - left), np.uint8)
    c[np.ix_(SENSOR_Y - top, SENSOR_X - left)] = avg
    return c


def photograph(stream, label, endpoints, n=9):
    frames = stream.window(n)
    stack = np.stack([f[2] for f in frames])
    readings = measure_gray(canvas(stack))
    seq = np.array([f[0] for f in frames])
    wall = np.array([f[1] for f in frames])
    Path(endpoints).mkdir(parents=True, exist_ok=True)
    with open(Path(endpoints) / f'{label}.npz', 'wb') as out:
        np.savez_compressed(out, native_luma=stack, sensor_x=SENSOR_X, sensor_y=SENSOR_Y, seq=seq, wall_s=wall)
    info = dict(label=label, readings=readings, stream=stream.tag, wall_mid=float(np.median(wall)),
                span_s=round(float(wall[-1] - wall[0]), 3), patch_luma=round(float(np.mean([f[3] for f in frames])), 2))
    if stream.journal:
        stream.journal.append('image', **info)
    return info
