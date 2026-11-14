"""Paths for one sloped course, in the mounting face's own plane: a across the slope, b up it.

Every path climbs. A bead laid with its uphill neighbour already down would have the nozzle's
flat ride on that neighbour, so a course goes down in this order: the rings that have the
course's stock uphill of them, the fill, then the rings that have it downhill of them."""
import math
import numpy as np
import manifold3d as m3
import trimesh
from shapely.geometry import LineString, Polygon
from shapely.geometry.polygon import orient
from shapely.ops import linemerge, substring, unary_union

STEP = 0.35


def sections(stl, course, count):
    """The base cut parallel to its mounting face through the middle of each course."""
    base = trimesh.load(stl)
    solid = m3.Manifold(m3.Mesh(vert_properties=np.asarray(base.vertices, np.float32), tri_verts=np.asarray(base.faces, np.uint32)))
    assert solid.status() == m3.Error.NoError, "the base is not a closed solid"
    out = []
    for k in range(1, count + 1):
        loops = [np.asarray(p) for p in solid.slice((k - 0.5) * course).to_polygons() if len(p) >= 3]
        def signed(p):
            return float(np.sum(p[:, 0] * np.roll(p[:, 1], -1) - np.roll(p[:, 0], -1) * p[:, 1]))
        # CAD y runs down the slope, so b = -y; the mirror is applied after telling stock from hole
        stock = [Polygon(np.c_[p[:, 0], -p[:, 1]]) for p in loops if signed(p) > 0]
        holes = [Polygon(np.c_[p[:, 0], -p[:, 1]]) for p in loops if signed(p) < 0]
        region = unary_union(stock)
        if holes:
            region = region.difference(unary_union(holes))
        region = region.buffer(0)
        assert region.geom_type == "Polygon", f"course {k} is not one piece"
        out.append(region)
    return out


def lines_of(geometry):
    if geometry.is_empty:
        return []
    if geometry.geom_type == "LineString":
        return [geometry]
    if geometry.geom_type in ("MultiLineString", "GeometryCollection"):
        merged = linemerge([g for g in geometry.geoms if g.geom_type == "LineString"]) if geometry.geom_type == "MultiLineString" else None
        if merged is not None:
            return [merged] if merged.geom_type == "LineString" else list(merged.geoms)
        return [g for g in geometry.geoms if g.geom_type == "LineString"]
    return []


def polygons_of(geometry):
    if geometry.is_empty:
        return []
    if geometry.geom_type == "Polygon":
        return [geometry]
    return [g for g in getattr(geometry, "geoms", []) if g.geom_type == "Polygon" and not g.is_empty]


def rings_of(geometry):
    """Closed rings with the stock on the left of travel."""
    out = []
    for p in polygons_of(geometry):
        p = orient(p, 1.0)
        out.append(np.array(p.exterior.coords)[:-1])
        out.extend(np.array(r.coords)[:-1] for r in p.interiors)
    return [r for r in out if len(r) >= 3]


def resample(points, closed, step=STEP):
    pts = np.asarray(points, float)
    path = np.vstack([pts, pts[:1]]) if closed else pts
    seg = np.hypot(*np.diff(path, axis=0).T)
    total = float(seg.sum())
    count = max(4 if closed else 2, int(math.ceil(total / step)) + (0 if closed else 1))
    at = np.linspace(0.0, total, count, endpoint=not closed)
    cum = np.r_[0.0, np.cumsum(seg)]
    return np.c_[np.interp(at, cum, path[:, 0]), np.interp(at, cum, path[:, 1])], total


def climbing(points, tolerance=0.03, depth=0):
    """An open path as pieces that each climb the slope: cut at a low or high point inside it."""
    pts = np.asarray(points, float)
    if len(pts) < 2:
        return []
    b = pts[:, 1]
    lo, hi = int(np.argmin(b)), int(np.argmax(b))
    last = len(pts) - 1
    if depth < 4:
        if 0 < lo < last and b[lo] < min(b[0], b[last]) - tolerance:
            return climbing(pts[:lo + 1][::-1], tolerance, depth + 1) + climbing(pts[lo:], tolerance, depth + 1)
        if 0 < hi < last and b[hi] > max(b[0], b[last]) + tolerance:
            return climbing(pts[:hi + 1], tolerance, depth + 1) + climbing(pts[hi:][::-1], tolerance, depth + 1)
    return [pts if b[last] >= b[0] else pts[::-1]]


def edge_pieces(geometry, taper=1.2, step=STEP):
    """The rings of `geometry` as climbing pieces with a flow for every point.

    Returns (first, last): `first` holds the pieces with the stock uphill of them, `last` those
    with it downhill. Where two pieces meet, each runs on past the joint with its flow fading
    out as the other's fades in, so a joint is a lap and not a butt."""
    first, last = [], []
    for ring in rings_of(geometry):
        pts, total = resample(ring, True, step)
        n = len(pts)
        if total < 1.5:
            continue
        nxt = np.roll(pts, -1, axis=0)
        ta = nxt[:, 0] - pts[:, 0]
        side = np.where(ta > 1e-9, 1, np.where(ta < -1e-9, -1, 0))
        for i in range(n):                      # a segment straight up or down takes its predecessor's side
            if side[i] == 0:
                side[i] = side[i - 1] if side[i - 1] != 0 else 1
        # runs of one side, as [start vertex, vertex count]; short runs join the run before them
        cuts = [i for i in range(n) if side[i] != side[i - 1]]
        if not cuts:
            cuts = [0]
        runs = []
        for j, c in enumerate(cuts):
            end = cuts[(j + 1) % len(cuts)]
            count = (end - c) % n or n
            runs.append([c, count, int(side[c])])
        seglen = total / n
        merged = []
        for run in runs:
            if merged and run[1] * seglen < 0.8:
                merged[-1][1] += run[1]
            else:
                merged.append(run)
        if len(merged) > 1 and merged[0][1] * seglen < 0.8:
            merged[-1][1] += merged[0][1]
            merged = merged[1:]
        # cut vertices: the run boundaries, and a low or high point inside a run
        joints = []
        for c, count, s in merged:
            idx = [(c + i) % n for i in range(count + 1)]
            b = pts[idx, 1]
            inner = [idx[0]]
            def split(lo_i, hi_i, depth=0):
                seg = b[lo_i:hi_i + 1]
                if hi_i - lo_i < 3 or depth > 3:
                    return
                kmin, kmax = lo_i + int(np.argmin(seg)), lo_i + int(np.argmax(seg))
                if lo_i < kmin < hi_i and b[kmin] < min(b[lo_i], b[hi_i]) - 0.03:
                    split(lo_i, kmin, depth + 1); inner.append(idx[kmin]); split(kmin, hi_i, depth + 1)
                elif lo_i < kmax < hi_i and b[kmax] > max(b[lo_i], b[hi_i]) + 0.03:
                    split(lo_i, kmax, depth + 1); inner.append(idx[kmax]); split(kmax, hi_i, depth + 1)
            split(0, count)
            for v in inner:
                joints.append((v, s))
        if len(joints) < 2:
            joints = [(0, 1), (n // 2, -1)]
        doubled = LineString(np.vstack([pts, pts, pts, pts[:1]]))
        for j, (v, s) in enumerate(joints):
            v2 = joints[(j + 1) % len(joints)][0]
            sa, sb = v * seglen, v2 * seglen
            if sb <= sa:
                sb += total
            length = sb - sa
            if length < 0.4:
                continue
            fade = min(taper, 0.3 * length)
            piece = substring(doubled, total + sa - fade, total + sb + fade)
            p, plen = resample(np.array(piece.coords), False, step)
            at = np.linspace(0.0, plen, len(p))
            flows = np.clip(np.minimum(at / (2 * fade), (plen - at) / (2 * fade)), 0.0, 1.0)
            core = p[(at >= fade) & (at <= plen - fade)]
            if len(core) >= 2 and core[-1, 1] < core[0, 1]:
                p, flows = p[::-1], flows[::-1]
            (first if s > 0 else last).append((p, flows))
    return first, last


def narrow_pieces(region, width, pitch, fill, step=STEP):
    """Rings for the strips of `region` too narrow for the fill, lowest first."""
    inside = region.buffer(-(width - 0.02))
    rest = inside if fill.is_empty else inside.difference(fill.buffer(pitch * 0.55))
    rest = rest.buffer(-0.06).buffer(0.06)
    if rest.is_empty:
        return []
    reach = rest.buffer(pitch * 0.5)
    out = []
    for level in range(1, 9):
        ring_stock = region.buffer(-(width / 2.0 + level * pitch))
        if ring_stock.is_empty:
            break
        for ring in rings_of(ring_stock):
            loop = LineString(np.vstack([ring, ring[:1]]))
            for piece in lines_of(loop.intersection(reach)):
                if piece.length < 0.8:
                    continue
                p, _ = resample(np.array(piece.coords), False, step)
                for part in climbing(p):
                    if len(part) >= 2 and LineString(part).length >= 0.6:
                        out.append((part, np.ones(len(part))))
    out.sort(key=lambda item: float(item[0][:, 1].mean()))
    return out


def hatch(region, angle, pitch, phase=0.5, shortest=0.6):
    """Rows of straight lines across `region` at `angle` degrees from the a axis. Each line is
    ((a, b), (a, b)), climbing where it can. The rows never run down the slope."""
    d = (math.cos(math.radians(angle)), math.sin(math.radians(angle)))
    nrm = (-d[1], d[0])
    if region.is_empty:
        return []
    minx, miny, maxx, maxy = region.bounds
    offsets = [x * nrm[0] + y * nrm[1] for x in (minx, maxx) for y in (miny, maxy)]
    k0, k1 = math.floor(min(offsets) / pitch) - 1, math.ceil(max(offsets) / pitch) + 1
    reach = 300.0
    rows = []
    for k in range(k0, k1 + 1):
        o = (k + phase) * pitch
        p0 = (o * nrm[0] - reach * d[0], o * nrm[1] - reach * d[1])
        p1 = (o * nrm[0] + reach * d[0], o * nrm[1] + reach * d[1])
        pieces = []
        for g in lines_of(region.intersection(LineString([p0, p1]))):
            if g.length >= shortest:
                c = list(g.coords)
                a, b = c[0], c[-1]
                if (b[0] - a[0]) * d[0] + (b[1] - a[1]) * d[1] < 0:
                    a, b = b, a
                pieces.append((a, b))
        pieces.sort(key=lambda s: s[0][0] * d[0] + s[0][1] * d[1])
        if pieces:
            rows.append(pieces)
    if nrm[1] < -1e-9:
        rows.reverse()
    return rows


def level_order(rows, start=None):
    """Level lines in an order that lays every line after the lines just downhill of it, taking
    the nearest such line each time, so a strip beside an opening is finished before crossing."""
    items = []
    for r, pieces in enumerate(rows):
        for a, b in pieces:
            lo, hi = (a, b) if a[0] <= b[0] else (b, a)
            items.append({"row": r, "lo": lo, "hi": hi, "needs": [], "done": False})
    by_row = {}
    for it in items:
        by_row.setdefault(it["row"], []).append(it)
    for it in items:
        for below in by_row.get(it["row"] - 1, []):
            if below["lo"][0] < it["hi"][0] + 0.3 and below["hi"][0] > it["lo"][0] - 0.3:
                it["needs"].append(below)
    out = []
    pos = start
    remaining = len(items)
    while remaining:
        best = None
        for it in items:
            if it["done"] or any(not q["done"] for q in it["needs"]):
                continue
            for a, b in ((it["lo"], it["hi"]), (it["hi"], it["lo"])):
                cost = it["row"] * 1e-3 + (0.0 if pos is None else math.dist(pos, a))
                if best is None or cost < best[0]:
                    best = (cost, it, a, b)
        _, it, a, b = best
        it["done"] = True
        remaining -= 1
        out.append((a, b))
        pos = b
    return out
