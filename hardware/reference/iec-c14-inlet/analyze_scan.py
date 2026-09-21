"""Reproduce the C14 inlet's scan measurements from the archived MINI 2 captures.

Reads the three fused clouds named in the archive's `capture-manifest.json`, puts
each in a table frame off its marker plane, builds a part frame from the part's
own faces, registers passes 2 and 3 onto pass 1, removes each pass's buried
ear, and measures the features `iec_c14_inlet.py` carries. Writes
`scan-measurements.json` beside this file. No source cloud is rewritten.

    tools/cad-venv/bin/python hardware/reference/iec-c14-inlet/analyze_scan.py
    tools/cad-venv/bin/python hardware/reference/iec-c14-inlet/analyze_scan.py --selftest
"""
from pathlib import Path
import argparse
import hashlib
import json
import sys

import numpy as np
from scipy import ndimage
from scipy.optimize import least_squares
from scipy.spatial import cKDTree
from scipy.spatial.transform import Rotation

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / 'g-ganen-pump'))
from scan_tools import cylinder, load_cloud, plane, stats, unit  # noqa: E402
from register_scan import refine, voxel_sample, compare  # noqa: E402

ARCHIVE = Path.home() / 'Documents/3D Scans/2026-09-21-iec-c14-inlet'


# --- frames -----------------------------------------------------------------------------------

def table_frame(points, normals):
    """z = 0 on the turntable marker plane, +z toward the scanner, origin under the part; the
    normals turn with the points."""
    c = points.mean(0)
    _, _, vt = np.linalg.svd(points - c, full_matrices=False)
    n0 = unit(vt[-1])
    d = points - c
    h = d @ n0
    r = np.linalg.norm(d - np.outer(h, n0), axis=1)
    ring = points[(r > 40) & (np.abs(h) < 8)]
    c_t, n_t, _ = plane(ring)
    ring = ring[np.abs((ring - c_t) @ n_t) < 1.0]
    c_t, n_t, st = plane(ring)
    if (-c_t) @ n_t < 0:
        n_t = -n_t
    ex = unit(np.cross(n_t, [1, 0, 0]) if abs(n_t[0]) < 0.9 else np.cross(n_t, [0, 1, 0]))
    ey = np.cross(n_t, ex)
    R = np.vstack([ex, ey, n_t])
    q = (points - c_t) @ R.T
    tall = q[q[:, 2] > 5.0]
    q[:, 0] -= np.median(tall[:, 0])
    q[:, 1] -= np.median(tall[:, 1])
    return q, normals @ R.T, {'marker_plane_rms_mm': st['rms'], 'marker_points': int(len(ring))}


def axes_from_normals(n, cone_deg=8.0, refine_deg=12.0):
    """The three dominant, mutually orthogonal face-normal families."""
    k = 600
    i = np.arange(k) + 0.5
    phi = np.arccos(1 - 2 * i / k)
    theta = np.pi * (1 + 5 ** 0.5) * i
    dirs = np.column_stack([np.cos(theta) * np.sin(phi), np.sin(theta) * np.sin(phi), np.cos(phi)])
    dirs = dirs[dirs[:, 2] >= 0]
    c = np.cos(np.radians(cone_deg))
    counts = np.zeros(len(dirs), int)
    for s in range(0, len(n), 100000):
        counts += (np.abs(n[s:s + 100000] @ dirs.T) > c).sum(0)

    def tighten(a):
        for _ in range(4):
            sel = np.abs(n @ a) > np.cos(np.radians(refine_deg))
            a = unit((n[sel] * np.sign(n[sel] @ a)[:, None]).mean(0))
        return a
    order = np.argsort(counts)[::-1]
    a = tighten(dirs[order[0]])
    b = next(tighten(dirs[j]) for j in order if abs(dirs[j] @ a) < 0.15)
    b = unit(b - (b @ a) * a)
    cc = tighten(np.cross(a, b))
    cc = unit(cc - (cc @ a) * a - (cc @ b) * b)
    return [a, b, cc]


def planar_peaks(p, m, axis, thresh=0.95, width=0.05, min_count=300):
    planar = np.abs(m[:, axis]) > thresh
    x = p[planar, axis]
    hist, edges = np.histogram(x, bins=np.arange(x.min(), x.max() + width, width))
    peaks = [(edges[i], hist[i]) for i in range(1, len(hist) - 1)
             if hist[i] > min_count and hist[i] >= hist[i - 1] and hist[i] >= hist[i + 1]]
    merged = []
    for e, h in peaks:
        if merged and e - merged[-1][0] < 0.4:
            if h > merged[-1][1]:
                merged[-1] = (e, h)
        else:
            merged.append((e, h))
    others = [i for i in range(3) if i != axis]
    out = []
    for e, h in merged:
        sel = planar & (np.abs(p[:, axis] - e) < 0.15)
        lo, hi = np.percentile(p[sel][:, others], [1, 99], axis=0)
        out.append({'pos': float(e), 'n': int(sel.sum()), 'sign': int(np.sign(m[sel, axis].mean())),
                    'ext': [float(hi[0] - lo[0]), float(hi[1] - lo[1])]})
    return out


def part_frame(q, n):
    """Y = mating axis (+ toward the rim), X along the flange, Z up; origin on the ear front face,
    between the long flats, centred on the housing's X faces where both were seen."""
    part = (q[:, 2] > 0.6) & (np.hypot(q[:, 0], q[:, 1]) < 45)
    q, n = q[part], n[part]
    axes = axes_from_normals(n)
    best = None
    for iy in range(3):
        y = axes[iy]
        rest = [a for i, a in enumerate(axes) if i != iy]
        x = rest[int(np.argmax([np.ptp(q @ a) for a in rest]))]
        y = unit(y - (y @ x) * x)
        R = np.vstack([x, y, np.cross(x, y)])
        p, m = q @ R.T, n @ R.T
        wide = [k for k in planar_peaks(p, m, 1) if k['ext'][0] > 30]
        for a in wide:
            for b in wide:
                if 1.2 < b['pos'] - a['pos'] < 3.5 and a['sign'] != b['sign']:
                    score = a['n'] + b['n']
                    if best is None or score > best[0]:
                        best = (score, a, b, R)
    if best is None:
        raise ValueError('no flange pair found on any axis')
    _, a, b, R = best
    p, m = q @ R.T, n @ R.T
    if (p[:, 1] < a['pos'] - 1).sum() > (p[:, 1] > b['pos'] + 1).sum():
        front = b['pos']
    else:
        R = np.vstack([R[0], -R[1], -R[2]])
        p, m = q @ R.T, n @ R.T
        front = -a['pos']
    sel = (np.abs(p[:, 1] - front) < 0.25) & (m[:, 1] > 0.95)
    c_f, n_f, st = plane(p[sel])
    n_f = n_f if n_f[1] > 0 else -n_f
    xv = unit(np.array([1.0, 0, 0]) - (np.array([1.0, 0, 0]) @ n_f) * n_f)
    R2 = np.vstack([xv, n_f, np.cross(xv, n_f)])
    p, m, R = (p - c_f) @ R2.T, m @ R2.T, R2 @ R
    edge = (p[:, 1] > -3.5) & (p[:, 1] < 0.3) & (np.abs(m[:, 2]) > 0.95) & (np.abs(p[:, 0]) < 9)
    top, bot = p[edge & (p[:, 2] > 5), 2], p[edge & (p[:, 2] < -5), 2]
    z0 = (np.median(top) + np.median(bot)) / 2.0 if len(top) > 200 and len(bot) > 200 else 0.0
    wall = (p[:, 1] > -14.0) & (p[:, 1] < -5.0) & (np.abs(m[:, 0]) > 0.95) & (np.abs(p[:, 2] - z0) < 6)
    xp, xm = p[wall & (p[:, 0] > 5), 0], p[wall & (p[:, 0] < -5), 0]
    x0 = (np.median(xp) + np.median(xm)) / 2.0 if len(xp) > 200 and len(xm) > 200 else 0.0
    p[:, 0] -= x0
    p[:, 2] -= z0
    return p, m, {'front_face_rms_mm': st['rms'], 'front_face_points': int(sel.sum())}


# --- registration -----------------------------------------------------------------------------

def not_putty(p):
    x, y, _z = p.T
    return ~(((np.abs(x) > 15) & ((y > 2.3) | (y < -4.0))) | (np.abs(x) > 26.5) | (y > 2.3) | (y < -26))


def coarse_x(fixed, moving):
    bins = np.arange(-40, 40, 0.1)
    sel_f = (fixed[:, 1] > -15) & (fixed[:, 1] < -5) & (np.abs(fixed[:, 2]) < 7)
    sel_m = (moving[:, 1] > -15) & (moving[:, 1] < -5) & (np.abs(moving[:, 2]) < 7)
    hf, _ = np.histogram(fixed[sel_f, 0], bins)
    hm, _ = np.histogram(moving[sel_m, 0], bins)
    hf, hm = hf / hf.max(), hm / hm.max()
    return max(range(-150, 151), key=lambda s: np.dot(hf, np.roll(hm, s))) * 0.1


def putty_side(p):
    return int(np.sign((p[:, 0] > 26).sum() - (p[:, 0] < -26).sum()))


def earth_tab_z(p):
    tb = p[(p[:, 1] < -19) & (np.abs(p[:, 0]) < 2.5) & (np.abs(p[:, 2]) < 8)]
    return float(np.median(tb[:, 2])) if len(tb) else None


def register(fixed_p, fixed_n, mv_p, mv_n, want_putty_side, init=None):
    """Passes 2 and 3 onto pass 1. The 180-degree turn about Y scores alike, so the buried ear
    and the earth tab (below the line pair) pick the candidate."""
    keep = not_putty(fixed_p)
    fixed, fn = voxel_sample(fixed_p[keep], fixed_n[keep], 0.3)
    best = None
    for flip in (False, True):
        F = np.eye(4)
        if flip:
            F[0, 0] = F[2, 2] = -1
        T0 = (init @ F) if init is not None else F
        mv = mv_p @ T0[:3, :3].T + T0[:3, 3]
        mn = mv_n @ T0[:3, :3].T
        if init is None:
            D = np.eye(4)
            D[0, 3] = coarse_x(fixed_p[keep], mv[not_putty(mv)])
            mv = mv + D[:3, 3]
            T0 = D @ T0
        km = not_putty(mv)
        m_s, n_s = voxel_sample(mv[km], mn[km], 0.3)
        try:
            T, _ = refine(fixed, fn, m_s, n_s, max_distance=1.0)
        except ValueError:
            continue
        Tt = T @ T0
        moved = mv_p @ Tt[:3, :3].T + Tt[:3, 3]
        cmp_ = compare(m_s @ T[:3, :3].T + T[:3, 3], n_s @ T[:3, :3].T, fixed, fn)
        ez = earth_tab_z(moved)
        if putty_side(moved) == want_putty_side and ez is not None and ez < 0:
            if best is None or cmp_['overlap_within_0_75mm_fraction'] > best[0]:
                best = (cmp_['overlap_within_0_75mm_fraction'], Tt, cmp_)
    if best is None:
        raise ValueError('no candidate put the buried ear where the pose says and the earth tab below')
    return best[1], best[2]


# --- measurements -----------------------------------------------------------------------------

def circle_fit(pts2, c0):
    def res(c):
        return np.hypot(pts2[:, 0] - c[0], pts2[:, 1] - c[1]) - c[2]
    f = least_squares(res, c0, loss='soft_l1', f_scale=0.1)
    return f.x, stats(res(f.x))


def wall_median(pts, nrm, axis, sign, other_lim):
    m = (nrm[:, axis] * sign > 0.9) & (np.abs(pts[:, 2 - axis]) < other_lim)
    return float(np.median(pts[m, axis])) if m.sum() > 30 else None


def hole(P, N, SRC, srcs, guess):
    x, y, z = P.T
    g = np.array(guess, float)
    cyl = None
    for _ in range(3):
        r = np.hypot(x - g[0], z - g[1])
        hw = np.isin(SRC, srcs) & (y > -3.0) & (y < -0.3) & (np.abs(N[:, 1]) < 0.4) & (r > 1.2) & (r < 2.1)
        if hw.sum() < 60:
            return {'n_wall': int(hw.sum())}
        cyl = cylinder(P[hw], [0, 1, 0], 1.62)
        g = np.array([cyl['axis_point'][0], cyl['axis_point'][2]])
    return {'n_wall': int(hw.sum()), 'axis_xz': g.tolist(), 'radius': cyl['radius_mm'],
            'abs_p95': cyl['untrimmed_residual_mm']['abs_p95']}


def measure(P, N, SRC, clean):
    x, y, z = P.T
    nx, ny, nz = N.T
    out = {}
    front = (np.abs(y) < 0.3) & (ny > 0.95) & (np.abs(x) < 24) & (np.abs(z) < 11)
    back = (np.abs(y + 3.3) < 0.5) & (ny < -0.95) & (np.abs(x) < 24) & (np.abs(z) < 11) & ((np.abs(x) > 13.5) | (np.abs(z) > 9.3))
    c, _, st = plane(P[front])
    out['front_face'] = {'y': float(c[1]), 'rms': st['rms'], 'n': int(front.sum())}
    c, _, st = plane(P[back])
    out['back_face'] = {'y': float(c[1]), 'rms': st['rms'], 'n': int(back.sum())}
    out['flange_thickness'] = -out['back_face']['y'] + out['front_face']['y']
    edge = (y > -2.9) & (y < -0.4) & (np.abs(ny) < 0.3) & (np.abs(z) < 12)
    flats = {}
    for sgn, name in ((1, 'top'), (-1, 'bot')):
        m = edge & (np.abs(x) < 8) & (nz * sgn > 0.98) & (z * sgn > 9)
        flats[name] = float(np.median(P[m, 2]))
    out['long_flats_z'] = flats
    out['flange_height'] = flats['top'] - flats['bot']
    out['ears'] = {}
    out['screw_holes'] = {}
    for side in (-1, 1):
        cl = clean[side]
        m = edge & cl & (x * side > 21.0) & (x * side < 25.6) & (np.abs(z) < 5.5)
        cc, st = circle_fit(P[m][:, [0, 2]], [20.0 * side, 0.0, 5.0])
        out['ears'][side] = {'n': int(m.sum()), 'centre_xz': [float(cc[0]), float(cc[1])], 'radius': float(cc[2]), 'abs_p95': st['abs_p95']}
        out['screw_holes'][side] = hole(P, N, SRC, [k for k in (1, 2, 3) if clean[side][SRC == k].all()] or [1, 2, 3], [20.3 * side, 0.0])
        m = edge & cl & (x * side > 12.0) & (x * side < 18.5) & (z > 4.5)
        if m.sum() > 100:
            A = np.column_stack([P[m, 0], np.ones(m.sum())])
            coef, *_ = np.linalg.lstsq(A, P[m, 2], rcond=None)
            out['ears'][side]['taper_deg'] = float(abs(np.degrees(np.arctan(coef[0]))))
            out['ears'][side]['taper_meets_flat_x'] = float((flats['top'] - coef[1]) / coef[0])
    a, b = out['screw_holes'][-1], out['screw_holes'][1]
    if 'axis_xz' in a and 'axis_xz' in b:
        out['screw_pitch'] = float(np.hypot(b['axis_xz'][0] - a['axis_xz'][0], b['axis_xz'][1] - a['axis_xz'][1]))
        out['screw_midpoint_xz'] = [(a['axis_xz'][0] + b['axis_xz'][0]) / 2, (a['axis_xz'][1] + b['axis_xz'][1]) / 2]
    rim_face = (y > 0.6) & (y < 3.0) & (ny > 0.95) & (np.abs(x) < 17) & (np.abs(z) < 11.5)
    c, _, st = plane(P[rim_face])
    out['rim_face'] = {'y': float(c[1]), 'rms': st['rms'], 'n': int(rim_face.sum())}
    rim = (y > 0.3) & (y < 1.55) & (np.abs(ny) < 0.35) & (np.abs(x) < 17.5) & (np.abs(z) < 12)
    Rm, nR = P[rim], N[rim]
    out['rim_outer'] = {'x-': wall_median(Rm[Rm[:, 0] < -10], nR[Rm[:, 0] < -10], 0, -1, 7), 'x+': wall_median(Rm[Rm[:, 0] > 10], nR[Rm[:, 0] > 10], 0, 1, 7),
                        'z-': wall_median(Rm[Rm[:, 2] < -9.5], nR[Rm[:, 2] < -9.5], 2, -1, 12), 'z+': wall_median(Rm[Rm[:, 2] > 9.5], nR[Rm[:, 2] > 9.5], 2, 1, 12)}
    mouth = (y > -2.5) & (y < 1.55) & (np.abs(ny) < 0.35) & (np.abs(x) < 14) & (np.abs(z) < 9)
    Mo, nM = P[mouth], N[mouth]
    out['mouth'] = {'x-': wall_median(Mo[Mo[:, 0] < -10], nM[Mo[:, 0] < -10], 0, 1, 6), 'x+': wall_median(Mo[Mo[:, 0] > 10], nM[Mo[:, 0] > 10], 0, -1, 6),
                    'z-': wall_median(Mo[Mo[:, 2] < -6.5], nM[Mo[:, 2] < -6.5], 2, 1, 8), 'z+': wall_median(Mo[Mo[:, 2] > 6.5], nM[Mo[:, 2] > 6.5], 2, -1, 8)}
    q = P[mouth]
    ang = np.degrees(np.arctan2(q[:, 2], q[:, 0]))
    r = np.hypot(q[:, 0], q[:, 2])
    out['mouth_lower_chamfer_u'] = {s: float(np.median(r[(ang > a - 3) & (ang < a + 3)])) for s, a in (('-x-z', -135.0), ('+x-z', -45.0))}
    inside = (np.abs(x) < 11) & (np.abs(z) < 6.5) & (ny > 0.9) & (y < -3)
    h, e = np.histogram(y[inside], bins=np.arange(-16, -3, 0.1))
    out['cavity_floor_y'] = float(e[np.argmax(h)])
    band = (y > -15.5) & (y < -4.5) & (np.abs(ny) < 0.25)
    B, nB = P[band], N[band]
    out['body_faces'] = {'x-': wall_median(B, nB, 0, -1, 6), 'x+': wall_median(B, nB, 0, 1, 6), 'z-': wall_median(B, nB, 2, -1, 8), 'z+': wall_median(B, nB, 2, 1, 8)}
    for name, sx in (('x+z-', 1), ('x-z-', -1)):
        m = band & (nx * sx > 0.5) & (nz < -0.5) & (x * sx > 6) & (z < -3)
        q = P[m]
        out.setdefault('body_lower_chamfers', {})[name] = {'n': int(m.sum()), 'u_median': float(np.median((q[:, 0] * sx - q[:, 2]) / np.sqrt(2)))}
    end = (y > -17.5) & (y < -16.4) & (ny < -0.95) & (np.abs(x) < 14) & (np.abs(z) < 10)
    c, _, st = plane(P[end])
    out['body_end_face'] = {'y': float(c[1]), 'rms': st['rms']}
    block = (y > -18.7) & (y < -17.6) & (ny < -0.95) & (np.abs(x) < 14) & (np.abs(z) < 10)
    c, _, st = plane(P[block])
    out['tab_boss_face'] = {'y': float(c[1]), 'rms': st['rms']}
    tab = (y < -18.8) & (y > -25.3) & (np.abs(x) < 11) & (np.abs(z) < 8)
    ij = np.floor(P[tab][:, [0, 2]] / 0.5).astype(int)
    ij -= ij.min(0)
    occ = np.zeros(ij.max(0) + 3, bool)
    occ[ij[:, 0] + 1, ij[:, 1] + 1] = True
    lab, k = ndimage.label(occ, structure=np.ones((3, 3)))
    labels = lab[ij[:, 0] + 1, ij[:, 1] + 1]
    out['tabs'] = sorted([{'n': int((labels == i).sum()), 'centre_xz': [float(np.median(P[tab][labels == i, 0])), float(np.median(P[tab][labels == i, 2]))],
                           'y_tip': float(np.percentile(P[tab][labels == i, 1], 1))} for i in range(1, k + 1) if (labels == i).sum() > 1000],
                         key=lambda t: t['centre_xz'][0])
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument('--archive', type=Path, default=ARCHIVE)
    ap.add_argument('--selftest', action='store_true')
    args = ap.parse_args()
    if args.selftest:
        rng = np.random.default_rng(0)
        pts = rng.normal(size=(500, 3)) * [30, 30, 0.02]
        cloud = np.vstack([pts + [0, 0, 200], rng.normal(size=(200, 3)) * 2 + [0, 0, 190]])
        q, _, info = table_frame(cloud, np.tile([0.0, 0.0, -1.0], (len(cloud), 1)))
        assert info['marker_plane_rms_mm'] < 0.1
        print('table frame recovered on a synthetic marker plane')
        return 0
    manifest = json.loads((args.archive / 'capture-manifest.json').read_text())
    frames, clouds = {}, {}
    for entry in manifest['passes']:
        pts, nrm, meta = load_cloud(entry['cloud'], entry['sha256'])
        q, qn, tinfo = table_frame(pts, nrm)
        p, m, pinfo = part_frame(q, qn)
        clouds[entry['name']] = (p, m)
        frames[entry['name']] = {'table': tinfo, 'part': pinfo, 'sha256': meta['sha256']}
    p1, n1 = clouds['pass-01']
    want = {'pass-02': -putty_side(p1), 'pass-03': -putty_side(p1)}
    T = {}
    T['pass-03'], q3 = register(p1, n1, *clouds['pass-03'], want['pass-03'])
    T['pass-02'], q2 = register(p1, n1, *clouds['pass-02'], want['pass-02'], init=T['pass-03'])
    parts, srcs = [p1], [np.full(len(p1), 1)]
    norms = [n1]
    for i, name in ((2, 'pass-02'), (3, 'pass-03')):
        p, m = clouds[name]
        Tt = T[name]
        parts.append(p @ Tt[:3, :3].T + Tt[:3, 3])
        norms.append(m @ Tt[:3, :3].T)
        srcs.append(np.full(len(p), i))
    P, N, SRC = np.vstack(parts), np.vstack(norms), np.concatenate(srcs)
    side = {k: putty_side(P[SRC == k]) for k in (1, 2, 3)}
    clean = {s: np.isin(SRC, [k for k in (1, 2, 3) if side[k] != s]) for s in (-1, 1)}
    buried = np.zeros(len(P), bool)
    for k in (1, 2, 3):
        buried |= (SRC == k) & (P[:, 0] * side[k] > 14.5)
    keep = ~buried & (np.abs(P[:, 0]) <= 25.3) & (P[:, 1] > -25.4) & (P[:, 1] < 2.2)
    measured = measure(P[keep], N[keep], SRC[keep], {s: clean[s][keep] for s in (-1, 1)})
    report = {'archive': str(args.archive), 'frames': frames, 'registration': {'pass-02': q2, 'pass-03': q3, 'putty_side_by_pass': side},
              'transforms_to_pass1': {k: v.tolist() for k, v in T.items()}, 'retained_points': int(keep.sum()), 'measurements_mm': measured,
              'source_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    (HERE / 'scan-measurements.json').write_text(json.dumps(report, indent=1) + '\n')
    print(json.dumps(measured, indent=1))
    return 0


if __name__ == '__main__':
    sys.exit(main())
