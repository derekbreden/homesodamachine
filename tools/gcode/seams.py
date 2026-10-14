#!/usr/bin/env python3
"""Where the main exterior seam sits, over the part's whole height.

RUN BY HAND. NOT A STEP OF THE BUILD.

    tools/cad-venv/bin/python tools/gcode/seams.py SLICE.gcode.3mf PRINT.json --part industrial-shell-base
    tools/cad-venv/bin/python tools/gcode/seams.py SLICE.gcode.3mf PRINT.json --part shell-base \
        --project PROJECT.3mf --csv seams.csv --json seams.json

PRINT.json is the `*.print.json` the part's preparer wrote; it gives the part's identify ID and
its pose on the plate. For each layer's exterior loop the seam is the loop's first point (the
scarf start). Its target is where the loop crosses the part's CAD X = 0 plane, on the side
farthest along --toward (a CAD direction; the default 0,1,0 is the rear). The seam is reported
as its CAD X, which is the lateral offset from that plane, and as arc length along the loop from
the target, so a contour whose centre moves between layers is measured against itself.

There is no height window. Every layer is read, the profile prints every 10 mm band of print Z,
and every run of layers past --tolerance is listed with its G-code line. Layers are numbered
from 1, as Bambu Studio's layer slider numbers them. With --project the distance from each target
to the project's seam-enforcer paint is added.
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import toolpaths as tp  # noqa: E402


def measure(slice_path: Path, placement: tp.Placement, project: Path | None = None,
            toward=(0.0, 1.0, 0.0), runs: list[dict] | None = None) -> list[dict]:
    """One row per layer: the exterior loop's seam start against its target on CAD X = 0."""
    if runs is None:
        text = tp.slice_text(slice_path)
        runs = tp.read_runs(text, tp.object_in(text, placement.identify_id))
    loops = tp.exterior_loops(runs)
    toward = np.asarray(toward, float)
    enforcers = tp.enforcer_triangles(project, placement) if project else None
    if enforcers is not None:
        import trimesh
        verts = enforcers.reshape(-1, 3)
        paint = trimesh.Trimesh(vertices=verts, faces=np.arange(len(verts)).reshape(-1, 3), process=False)
    rows = []
    for lp in loops:
        r, lap = lp['run'], lp['lap']
        cad = placement.to_cad(lap)
        s = tp.arc_length(lap[:, :2])
        perimeter = s[-1] + float(np.linalg.norm(lap[-1, :2] - lap[0, :2]))
        # crossings of CAD X = 0, interpolated along the closed lap
        x = np.r_[cad[:, 0], cad[0, 0]]
        pts = np.vstack([lap, lap[:1]])
        arc_pos = np.r_[s, perimeter]
        crossings = []
        for i in np.flatnonzero((x[:-1] * x[1:] <= 0) & (x[:-1] != x[1:])):
            f = x[i] / (x[i] - x[i + 1])
            crossings.append((pts[i] + f * (pts[i + 1] - pts[i]), arc_pos[i] + f * (arc_pos[i + 1] - arc_pos[i])))
        if crossings:
            target, s_t = max(crossings, key=lambda c: placement.to_cad(c[0]) @ toward)
        else:
            i = int(np.argmax(cad @ toward))
            target, s_t = lap[i], s[i]
        offset = (-s_t) % perimeter
        if offset > perimeter / 2:
            offset -= perimeter
        start = r['pts'][0]
        row = {'layer': r['layer'] + 1, 'print_z': r['z'], 'layer_h': r['h'], 'gcode_line': r['line'],
               'closed': lp['closed'], 'perimeter_mm': perimeter,
               'lateral_mm': float(placement.to_cad(start)[0]), 'arc_from_target_mm': float(offset),
               'start_plate': start, 'end_plate': r['pts'][-1], 'target_plate': target,
               'start_normal': tp.start_normal(r['pts']),
               'start_cad': placement.to_cad(start), 'target_cad': placement.to_cad(target),
               'centroid_plate': lp['centroid']}
        if enforcers is not None:
            q = np.array([[target[0], target[1], r['z'] - (r['h'] or 0.2) / 2]])
            row['enforcer_mm'] = float(trimesh.proximity.closest_point(paint, q)[1][0])
        rows.append(row)
    return rows


def zones(rows: list[dict], tolerance: float) -> list[dict]:
    """Runs of consecutive layers whose seam is more than `tolerance` off the plane."""
    out, cur = [], []
    for row in rows + [None]:
        if row is not None and abs(row['lateral_mm']) > tolerance:
            cur.append(row)
            continue
        if cur:
            peak = max(cur, key=lambda r: abs(r['lateral_mm']))
            out.append({'layers': [cur[0]['layer'], cur[-1]['layer']],
                        'print_z_mm': [cur[0]['print_z'], cur[-1]['print_z']],
                        'cad_z_mm': [round(float(cur[0]['target_cad'][2]), 2), round(float(cur[-1]['target_cad'][2]), 2)],
                        'peak_lateral_mm': round(peak['lateral_mm'], 3), 'peak_print_z_mm': peak['print_z'],
                        'peak_gcode_line': peak['gcode_line']})
            cur = []
    return out


def profile(rows: list[dict], band: float = 10.0) -> list[dict]:
    out = {}
    for row in rows:
        out.setdefault(int(row['print_z'] // band), []).append(row)
    return [{'print_z_mm': [k * band, (k + 1) * band], 'layers': len(v),
             'mean_lateral_mm': round(float(np.mean([r['lateral_mm'] for r in v])), 3),
             'max_abs_lateral_mm': round(float(max(abs(r['lateral_mm']) for r in v)), 3)}
            for k, v in sorted(out.items())]


def main(argv=None) -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument('slice', type=Path)
    ap.add_argument('print_json', type=Path)
    ap.add_argument('--part', required=True, help='substring of the part name in PRINT.json')
    ap.add_argument('--project', type=Path, help='editable .3mf whose seam paint to measure against')
    ap.add_argument('--toward', default='0,1,0', help='CAD direction of the intended side (default rear)')
    ap.add_argument('--tolerance', type=float, default=1.0, help='mm off the plane that counts as a zone')
    ap.add_argument('--csv', type=Path)
    ap.add_argument('--json', type=Path)
    a = ap.parse_args(argv)

    placement = tp.Placement(a.print_json, a.part)
    rows = measure(a.slice, placement, a.project, [float(v) for v in a.toward.split(',')])
    summary = {'slice': str(a.slice), 'part': placement.name, 'layers': len(rows),
               'open_loops': sum(not r['closed'] for r in rows), 'tolerance_mm': a.tolerance,
               'max_abs_lateral_mm': round(max(abs(r['lateral_mm']) for r in rows), 3),
               'zones': zones(rows, a.tolerance), 'profile': profile(rows)}
    print(f"{placement.name}: {len(rows)} layers, {summary['open_loops']} open, "
          f"largest offset {summary['max_abs_lateral_mm']} mm")
    print(f"{'print Z band':>14} {'layers':>6} {'mean':>7} {'max |off|':>9}")
    for b in summary['profile']:
        print(f"{b['print_z_mm'][0]:6.0f}-{b['print_z_mm'][1]:<6.0f} {b['layers']:6d} "
              f"{b['mean_lateral_mm']:7.2f} {b['max_abs_lateral_mm']:9.2f}")
    for z in summary['zones']:
        print(f"over {a.tolerance} mm: layers {z['layers'][0]}-{z['layers'][1]}, print Z "
              f"{z['print_z_mm'][0]}-{z['print_z_mm'][1]}, CAD Z {z['cad_z_mm'][0]}-{z['cad_z_mm'][1]}, "
              f"peak {z['peak_lateral_mm']} mm at print Z {z['peak_print_z_mm']} (G-code line {z['peak_gcode_line']})")
    if a.json:
        a.json.write_text(json.dumps(summary, indent=1) + '\n')
    if a.csv:
        with a.csv.open('w', newline='') as f:
            w = csv.writer(f)
            w.writerow(['layer', 'print_z', 'layer_h', 'gcode_line', 'closed', 'perimeter_mm', 'lateral_mm',
                        'arc_from_target_mm', 'start_cad_x', 'start_cad_y', 'start_cad_z',
                        'target_cad_y', 'target_cad_z', 'enforcer_mm'])
            for r in rows:
                w.writerow([r['layer'], r['print_z'], r['layer_h'], r['gcode_line'], int(r['closed']),
                            round(r['perimeter_mm'], 3), round(r['lateral_mm'], 3), round(r['arc_from_target_mm'], 3),
                            *np.round(r['start_cad'], 3), round(float(r['target_cad'][1]), 3),
                            round(float(r['target_cad'][2]), 3),
                            '' if 'enforcer_mm' not in r else round(r['enforcer_mm'], 3)])


if __name__ == '__main__':
    main()
