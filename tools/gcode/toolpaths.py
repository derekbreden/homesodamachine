"""Read the walls a Bambu Studio slice commands, one continuous run at a time.

RUN BY HAND. NOT A STEP OF THE BUILD. `seams.py`, `speeds.py` and `view.py` read slices through
this module, so the rules below are written once.

A run is one continuous extrusion path of the chosen features, on one layer of one object.
It ends at a travel, a retraction, a layer change, an object change, or a feature outside the
set. Bambu emits feed-only lines (`G1 F876`), acceleration changes (`M204`) and the switch between
"Outer wall" and "Overhang wall" in the middle of one perimeter, so none of those end a run.
The feed is modal: each move carries the last F commanded before it, whichever line set it.
Bambu also extrudes holes counter-clockwise, so a layer's exterior is its largest-area loop,
not its only counter-clockwise one. With scarf seams a loop starts low and ramps up in Z and
flow. Its first point is the seam start, and its last point is the end of the scarf overlap.
"""
from __future__ import annotations

import json
import math
import re
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

import numpy as np

WORD = re.compile(r'([A-Z])([-+]?(?:\d*\.\d+|\d+\.?\d*))')
WALLS = ('Outer wall', 'Overhang wall')


def slice_text(path: Path, plate: int = 1) -> str:
    """The G-code of a `.gcode` file, or of one plate of a sliced `.gcode.3mf`."""
    path = Path(path)
    if path.suffix == '.gcode':
        return path.read_text()
    with zipfile.ZipFile(path) as z:
        return z.read(f'Metadata/plate_{plate}.gcode').decode()


def arc(start, end, words: dict, clockwise: bool, chord: float = 0.25) -> list[tuple]:
    """Points along a G2/G3 move after its start, with Z interpolated along the sweep."""
    cx, cy = start[0] + words.get('I', 0.0), start[1] + words.get('J', 0.0)
    r = math.hypot(start[0] - cx, start[1] - cy)
    a0 = math.atan2(start[1] - cy, start[0] - cx)
    sweep = math.atan2(end[1] - cy, end[0] - cx) - a0
    if clockwise:
        sweep = sweep if sweep < -1e-9 else sweep - 2 * math.pi
    else:
        sweep = sweep if sweep > 1e-9 else sweep + 2 * math.pi
    n = max(1, math.ceil(abs(sweep) * r / chord))
    out = [(cx + r * math.cos(a0 + sweep * i / n), cy + r * math.sin(a0 + sweep * i / n),
            start[2] + (end[2] - start[2]) * i / n) for i in range(1, n + 1)]
    out[-1] = tuple(end)
    return out


def read_runs(text: str, object_id: int | None = None, features=WALLS) -> list[dict]:
    """Every continuous extrusion run of `features`, on the object `object_id` (or any).

    Each run has `pts` (N x 3, plate mm) and, per move between them, `feed` (mm/s),
    `overhang` (the move was labelled "Overhang wall") and `lines` (its G-code line).
    """
    pos = np.zeros(3)
    rel_e, abs_xyz = True, True
    z = h = None
    layer = -1
    feature, obj, feed, e_abs = '', None, 0.0, 0.0
    run, runs = None, []

    def finish():
        nonlocal run
        if run is not None and len(run['pts']) > 2:
            for key in ('pts', 'feed', 'overhang', 'lines'):
                run[key] = np.array(run[key])
            runs.append(run)
        run = None

    for n, raw in enumerate(text.splitlines(), 1):
        if raw.startswith(';'):
            s = raw[1:].strip()
            if s.startswith('Z_HEIGHT:'):
                finish(); z = float(s.split(':', 1)[1]); layer += 1
            elif s.startswith('LAYER_HEIGHT:'):
                h = float(s.split(':', 1)[1])
            elif s.startswith('FEATURE:'):
                feature = s.split(':', 1)[1].strip()
                if feature not in features:
                    finish()
            elif s.startswith('OBJECT_ID:'):
                finish(); obj = int(s.split(':', 1)[1])
            elif s.startswith('start printing object, unique label id:'):
                finish(); obj = int(s.rsplit(':', 1)[1])
            elif s.startswith('stop printing object'):
                finish(); obj = None
            continue
        code = raw.split(';', 1)[0].strip()
        if not code:
            continue
        cmd = code.split(None, 1)[0]
        if cmd in ('G90', 'G91'):
            abs_xyz = cmd == 'G90'
            continue
        if cmd in ('M82', 'M83'):
            rel_e = cmd == 'M83'
            continue
        if cmd not in ('G0', 'G1', 'G2', 'G3', 'G92'):
            continue
        words = {k: float(v) for k, v in WORD.findall(code[len(cmd):])}
        if cmd == 'G92':
            for i, k in enumerate('XYZ'):
                if k in words:
                    pos[i] = words[k]
            e_abs = words.get('E', e_abs)
            continue
        if 'F' in words:
            feed = words['F'] / 60.0
        nxt = pos.copy()
        for i, k in enumerate('XYZ'):
            if k in words:
                nxt[i] = words[k] if abs_xyz else pos[i] + words[k]
        de = 0.0
        if 'E' in words:
            de = words['E'] if rel_e else words['E'] - e_abs
            e_abs = e_abs + words['E'] if rel_e else words['E']
        moved = math.hypot(nxt[0] - pos[0], nxt[1] - pos[1]) > 1e-9
        wanted = (feature in features and z is not None
                  and (object_id is None or obj == object_id))
        if wanted and de > 0 and moved:
            if run is None:
                run = {'layer': layer, 'z': z, 'h': h, 'object': obj, 'line': n,
                       'pts': [tuple(pos)], 'feed': [], 'overhang': [], 'lines': []}
            seg = arc(pos, nxt, words, cmd == 'G2') if cmd in ('G2', 'G3') else [tuple(nxt)]
            run['pts'].extend(seg)
            run['feed'].extend([feed] * len(seg))
            run['overhang'].extend([feature == 'Overhang wall'] * len(seg))
            run['lines'].extend([n] * len(seg))
            run['end_line'] = n
        elif moved or de < 0:
            finish()
        pos = nxt
    finish()
    return runs


def object_in(text: str, identify_id: int | None) -> int | None:
    """`identify_id` when the slice marks that object, else None (read every object)."""
    if identify_id is None:
        return None
    known = f'OBJECT_ID: {identify_id}' in text or f'unique label id: {identify_id}' in text
    return identify_id if known else None


def start_normal(pts: np.ndarray) -> np.ndarray:
    """Unit outward normal at a counter-clockwise loop's first point, in the plate's XY plane."""
    far = np.flatnonzero(np.linalg.norm(pts[:, :2] - pts[0, :2], axis=1) > 0.3)
    t = pts[far[0], :2] - pts[0, :2] if len(far) else np.array([1.0, 0.0])
    t = t / np.linalg.norm(t)
    return np.array([t[1], -t[0], 0.0])


def polygon(xy: np.ndarray) -> tuple[float, np.ndarray]:
    """Signed area (counter-clockwise positive) and centroid of a closed polyline."""
    x, y = xy[:, 0], xy[:, 1]
    cross = x * np.roll(y, -1) - np.roll(x, -1) * y
    area = 0.5 * cross.sum()
    if abs(area) < 1e-12:
        return 0.0, xy.mean(axis=0)
    return float(area), np.array([((x + np.roll(x, -1)) * cross).sum() / (6 * area),
                                  ((y + np.roll(y, -1)) * cross).sum() / (6 * area)])


def first_lap(pts: np.ndarray, tol: float = 0.6) -> int | None:
    """Index where a run first returns to its start: the scarf overlap begins after it."""
    d = np.linalg.norm(pts[:, :2] - pts[0, :2], axis=1)
    away = np.flatnonzero(d > 2 * tol)
    if not len(away):
        return None
    back = np.flatnonzero((np.arange(len(d)) > away[0]) & (d < tol))
    return int(back[0]) if len(back) else None


def exterior_loops(runs: list[dict]) -> list[dict]:
    """Each layer's largest closed counter-clockwise loop, in layer order, with its first lap."""
    best = {}
    for r in runs:
        cut = first_lap(r['pts'])
        lap = r['pts'][: cut + 1] if cut is not None else r['pts']
        area, centroid = polygon(lap[:, :2])
        key = (r['object'], r['layer'])
        if area > 0 and (key not in best or area > best[key]['area']):
            best[key] = {'run': r, 'lap': lap, 'closed': cut is not None, 'area': area, 'centroid': centroid}
    return [best[k] for k in sorted(best, key=lambda k: (str(k[0]), k[1]))]


def arc_length(xy: np.ndarray) -> np.ndarray:
    return np.concatenate([[0.0], np.cumsum(np.linalg.norm(np.diff(xy, axis=0), axis=1))])


class Placement:
    """One part's pose on the plate, from the `*.print.json` its preparer wrote.

    plate = (cad - source_center) @ M + plate_translation, with M the 3 x 3 of build_transform.
    """

    def __init__(self, print_json: Path, part: str):
        report = json.loads(Path(print_json).read_text())
        row = next(p for p in report['parts'] if part in p['name'])
        self.name = row['name']
        self.identify_id = row.get('identify_id')
        self.m = np.array(row['build_transform'][:9]).reshape(3, 3)
        self.t = np.array(row['plate_translation_mm'])
        self.center = np.array(row['source_center_mm'])

    def to_cad(self, p):
        return (np.asarray(p) - self.t) @ self.m.T + self.center

    def to_plate(self, cad):
        return (np.asarray(cad) - self.center) @ self.m + self.t


def enforcer_triangles(project: Path, placement: Placement) -> np.ndarray | None:
    """Seam-enforcer facets (`paint_seam="4"`) of a project's meshes, as plate triangles."""
    tris = []
    with zipfile.ZipFile(project) as z:
        for name in z.namelist():
            if not (name.startswith('3D/Objects/') and name.endswith('.model')):
                continue
            root = ET.fromstring(z.read(name))
            ns = root.tag.split('}')[0].strip('{')
            for mesh in root.iter(f'{{{ns}}}mesh'):
                verts = np.array([[float(v.get(k)) for k in 'xyz'] for v in mesh.iter(f'{{{ns}}}vertex')])
                for t in mesh.iter(f'{{{ns}}}triangle'):
                    if t.get('paint_seam') == '4':
                        tris.append(verts[[int(t.get('v1')), int(t.get('v2')), int(t.get('v3'))]])
    return np.array(tris) @ placement.m + placement.t if tris else None
