#!/usr/bin/env python3
"""Build a 3D page of the walls a slice commands, the way Bambu Studio's slice preview shows them.

RUN BY HAND. NOT A STEP OF THE BUILD. The page follows the Artifact page contract and the
tools/viz conventions. Look at it with `node tools/viz/shot.mjs PAGE.html PAGE.png`, then
publish it with the Artifact tool. Pages belong in a scratchpad, never the tree.

Seams: one part's outer walls, with each layer's seam start as a dot coloured by its offset from
the part's CAD X = 0 plane, the seam-enforcer paint when --project is given, and the seams of
other slices of the same part as optional overlays.

    tools/cad-venv/bin/python tools/gcode/view.py seams SLICE.gcode.3mf PRINT.json --part shell-base \
        --project PROJECT.3mf --compare "Oct 13 print=OTHER.gcode.3mf:OTHER.print.json" \
        --frame-z 0-100 --title "Base seam toolpaths" --out PAGE.html

Speed: the outer walls of one or more slices, side by side under one camera, coloured by the
speed each move commands. --mark-layers with --at tags each panel with the speed `speeds.py`
reads at that place.

    tools/cad-venv/bin/python tools/gcode/view.py speed "Original=A.gcode.3mf" "Outer 10=B.gcode.3mf" \
        --mark-layers 26-33 --at leftmost --view left --title "Elbow lip speeds" --out PAGE.html
"""
from __future__ import annotations

import argparse
import base64
import html
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import seams  # noqa: E402
import speeds  # noqa: E402
import toolpaths as tp  # noqa: E402

PAGE_LIMIT = 16_000_000  # the Artifact page limit


def b64(a) -> str:
    return base64.b64encode(np.ascontiguousarray(a).tobytes()).decode()


def walls(runs: list[dict], origin: np.ndarray, with_speed: bool = False) -> dict:
    """Runs as int16 hundredths of a millimetre from `origin`, ready for the page's ribbons."""
    pts = np.concatenate([r['pts'] for r in runs])
    if np.abs(pts - origin).max() > 327:
        raise SystemExit('the toolpaths span more than 654 mm; nothing here draws that')
    out = {'paths': b64(np.round((pts - origin) * 100).astype(np.int16)),
           'offsets': b64(np.cumsum([0] + [len(r['pts']) for r in runs]).astype(np.uint32)),
           'heights': b64(np.array([round((r['h'] or 0.2) * 100) for r in runs], dtype=np.uint8)),
           'runs': len(runs), 'points': int(len(pts))}
    if with_speed:  # a point carries the speed of the move leaving it; the last takes the move ending there
        out['speeds'] = b64(np.round(np.concatenate([np.r_[r['feed'], r['feed'][-1]] for r in runs]) * 100)
                            .astype(np.uint16))
    return out


def seam_dots(rows: list[dict], placement: tp.Placement, main: tp.Placement, origin) -> np.ndarray:
    """Seam starts nudged 0.5 mm outside the wall, carried into `main`'s plate frame."""
    starts = np.array([r['start_plate'] + 0.5 * r['start_normal'] for r in rows])
    return main.to_plate(placement.to_cad(starts)) - origin


def fill(template: str, title: str, lede: str, data: dict, out: Path) -> None:
    page = (HERE / template).read_text()
    payload = json.dumps(data, separators=(',', ':'))
    if '</' in payload:
        raise SystemExit('page data would close its script tag')
    page = (page.replace('{{TITLE}}', html.escape(title)).replace('{{LEDE}}', html.escape(lede))
            .replace('/*DATA*/', payload))
    if len(page.encode()) > PAGE_LIMIT:
        raise SystemExit(f'{len(page.encode()) / 1e6:.1f} MB is past the 16 MB Artifact limit')
    out.write_text(page)
    print(f'{out}  {len(page.encode()) / 1e6:.1f} MB')


def build_seams(a) -> None:
    main = tp.Placement(a.print_json, a.part)
    text = tp.slice_text(a.slice)
    runs = tp.read_runs(text, tp.object_in(text, main.identify_id))
    pts = np.concatenate([r['pts'] for r in runs])
    origin = np.array([main.t[0], (pts[:, 1].min() + pts[:, 1].max()) / 2, 0.0])
    rows = seams.measure(a.slice, main, a.project, runs=runs)
    dots = seam_dots(rows, main, main, origin)
    lateral = np.array([r['lateral_mm'] for r in rows], dtype=np.float32)
    peaks = []
    for z in seams.zones(rows, 1.0):
        i = next(i for i, r in enumerate(rows) if r['print_z'] == z['peak_print_z_mm'])
        peaks.append({'at': dots[i].round(3).tolist(), 'lateral': z['peak_lateral_mm'],
                      'from_z': z['print_z_mm'][0], 'to_z': z['print_z_mm'][1], 'z': z['peak_print_z_mm']})
    toward = np.array([0.0, 1.0, 0.0]) @ main.m  # the rear, in plate directions
    data = {'source': str(a.slice), 'walls': walls(runs, origin), 'layers': len(rows),
            'seams': {'dots': b64(dots.astype(np.float32)), 'lateral': b64(lateral)},
            'rear': b64((np.array([r['target_plate'] for r in rows]) - origin + 0.35 * np.r_[toward[:2], 0])
                        .astype(np.float32)),
            'peaks': peaks, 'view_azimuth': float(np.degrees(np.arctan2(toward[1], toward[0]))),
            'frame_z': [float(v) for v in a.frame_z.split('-')] if a.frame_z else None, 'compare': []}
    if a.project:
        paint = tp.enforcer_triangles(a.project, main)
        if paint is not None:
            data['enforcers'] = b64((paint.reshape(-1, 3) - origin).astype(np.float32))
            data['enforcer_triangles'] = int(len(paint))
    palette = ['#ff7ad9', '#7fe3ff', '#c7f464', '#ffd166']
    for k, spec in enumerate(a.compare or []):
        label, _, paths = spec.partition('=')
        other_slice, _, other_json = paths.partition(':')
        other = tp.Placement(Path(other_json), a.part)
        rows_c = seams.measure(Path(other_slice), other)
        dots_c = seam_dots(rows_c, other, main, origin)
        data['compare'].append({'label': label, 'color': palette[k % len(palette)],
                                'dots': b64(dots_c.astype(np.float32)),
                                'max_abs_lateral': round(max(abs(r['lateral_mm']) for r in rows_c), 2)})
    lede = a.lede or (f'Every outer wall of {main.name} in {a.slice.name}, drawn from the G-code. Each dot is '
                      'where a layer\'s outer loop starts, which is where the seam is. Dots are coloured by '
                      'their distance from the part\'s centerline.')
    fill('seam-page.html', a.title, lede, data, a.out)


def build_speed(a) -> None:
    panels, origin = [], None
    for k, spec in enumerate(a.slices):
        label, _, path = spec.rpartition('=') if '=' in spec else ('', '', spec)
        path = Path(path)
        runs = tp.read_runs(tp.slice_text(path), a.object)
        if origin is None:
            pts = np.concatenate([r['pts'] for r in runs])
            origin = np.array([(pts[:, 0].min() + pts[:, 0].max()) / 2, (pts[:, 1].min() + pts[:, 1].max()) / 2, 0.0])
        panel = {'letter': chr(65 + k), 'name': label or path.name, 'source': str(path), **walls(runs, origin, True)}
        if a.mark_layers:
            rows = speeds.probe(path, a.at, speeds.layer_range(a.mark_layers), a.object)
            mid = rows[len(rows) // 2]
            panel['mark'] = {'at': (np.array(mid['point_plate']) - origin).round(3).tolist(),
                             'layers': [rows[0]['layer'], rows[-1]['layer']], 'place': a.at,
                             'speeds': [r['arriving_mm_s'] for r in rows]}
        panels.append(panel)
    lede = a.lede or ('Outer walls coloured by the speed each move commands; feed-only lines carry the '
                      'speed forward.')
    fill('speed-page.html', a.title, lede, {'panels': panels, 'view': a.view, 'elevation': a.elevation,
                                            'scale_mm_s': [float(v) for v in a.scale.split('-')]}, a.out)


def main(argv=None) -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest='mode', required=True)
    s = sub.add_parser('seams')
    s.add_argument('slice', type=Path)
    s.add_argument('print_json', type=Path)
    s.add_argument('--part', required=True)
    s.add_argument('--project', type=Path)
    s.add_argument('--compare', action='append', help='"label=SLICE:PRINT.json" of the same part')
    s.add_argument('--frame-z', help='print Z band the rear view opens on, e.g. 0-100')
    v = sub.add_parser('speed')
    v.add_argument('slices', nargs='+', help='"label=SLICE.gcode.3mf", one panel each')
    v.add_argument('--object', type=int)
    v.add_argument('--mark-layers', help='first-last layer to tag, numbered from 1')
    v.add_argument('--at', default='leftmost', help='place to tag, as speeds.py --at')
    v.add_argument('--view', default='iso', choices=['left', 'right', 'front', 'back', 'iso'])
    v.add_argument('--elevation', type=float, default=None)
    v.add_argument('--scale', default='10-30', help='mm/s at the pale and hot ends of the colour ramp')
    for p in (s, v):
        p.add_argument('--title', required=True, help='two to four words')
        p.add_argument('--lede', help='one or two sentences under the title')
        p.add_argument('--out', type=Path, required=True)
    a = ap.parse_args(argv)
    build_seams(a) if a.mode == 'seams' else build_speed(a)


if __name__ == '__main__':
    main()
