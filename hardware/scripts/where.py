"""Where each solid in a scene stands, read off the scene's mesh payload, and a move worked out
from there.

    python3 hardware/scripts/where.py rear-port-rebuild                   # every body's box
    python3 hardware/scripts/where.py rear-port-rebuild g-ganen-pump      # that body, solid by solid
    python3 hardware/scripts/where.py rear-port-rebuild g-ganen-pump --against enclosure-back-top --reach aft
    python3 hardware/scripts/where.py rear-port-rebuild g-ganen-pump --move 0 17 0 --against 'bulkhead-*' --margin 1 --clear west
    python3 hardware/scripts/where.py selftest

A scene is a `.step.mesh` path, the STEP beside one, or a name under
`hardware/assembly/scenes/out/`. The payload is the tessellation the viewer draws, one mesh per
solid; a body of several solids names them `body/1` … `body/N` in the order it was built. Bodies
are picked by name or shell pattern, and nothing is built.

`--move` carries the picked bodies by dx dy dz. `--against` lists every pair of solids, one
carried and one it names, whose boxes come within `--margin` of each other: how far the boxes
overlap on each axis, and how far the carried one goes in each direction before the boxes stand
`--margin` apart. A box holds its solid, so boxes that far apart are solids that far apart, and
round solids part before their boxes do.

`--clear` gives, for each direction it names (all six when it names none), the least move from
there at which no carried solid comes within `--margin` of a solid `--against` names, and the
pairs that set it. `--reach` gives the farthest move from there before one does, and the pairs
that stop it: a part slid back against a wall, or down onto a shelf. Both read rays cast `--ray`
apart across the other two axes through each pair's meshes, and give the boxes' reading beside
them. A ray holds each solid from the nearest face to the farthest that cross the square of grid
round it, so `--clear` never falls short and `--reach` never runs past; each errs by a sloped
face's rise across one square, which a finer `--ray` cuts at the cost of time. West is −X, east
+X, fore −Y, aft +Y, down −Z, up +Z.

A body that wraps round others — a shell, a bracket — holds them inside its box, and inside a
ray that crosses it on both sides of them; there its faces are read where the study or
`enclosure-assembly.facts.json` states them.
"""

import argparse
import fnmatch
import hashlib
import json
import re
import signal
import struct
import sys
import tempfile
from pathlib import Path

import numpy as np

SCENES = Path(__file__).resolve().parents[2] / "hardware" / "assembly" / "scenes" / "out"
# What `_mesh_payload` puts after a body's name for each of its solids when it has several.
SOLID_INDEX = re.compile(r"/\d+$")
# Each direction's axis and sign.
DIRECTIONS = {"west": (0, -1), "east": (0, 1), "fore": (1, -1), "aft": (1, 1),
              "down": (2, -1), "up": (2, 1)}
RAY = 0.25  # mm between the rays `--clear` and `--reach` cast through a pair's meshes, unless `--ray` says


def payload(scene) -> Path:
    """The payload a scene names: a `.step.mesh` path, the STEP beside one, or a scene's name."""
    for p in (Path(scene), Path(f"{scene}.mesh"), SCENES / f"{scene}.step.mesh"):
        if p.name.endswith(".mesh") and p.is_file():
            return p
    raise SystemExit(f"where: no mesh payload for {scene}")


def read(path):
    """The payload's header, and each solid's positions and triangles as {name: (pos, idx)}."""
    raw = Path(path).read_bytes()
    n = struct.unpack("<I", raw[:4])[0]
    head = json.loads(raw[4:4 + n])
    blob = memoryview(raw)[4 + n:]
    meshes = {}
    for m in head["meshes"]:
        (po, pn), (io, im) = m["pos"], m["idx"]
        meshes[m["name"]] = (np.frombuffer(blob, "<f4", pn, po).reshape(-1, 3),
                             np.frombuffer(blob, "<u4", im, io).reshape(-1, 3))
    return head, meshes


def stale(path, head) -> bool:
    """Whether the STEP beside the payload has been rewritten since the payload was cut from it."""
    step = Path(str(path)[:-len(".mesh")])
    if "src" not in head or not step.is_file():
        return False
    h = hashlib.sha256()
    with open(step, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest() != head["src"]


def body(name) -> str:
    return SOLID_INDEX.sub("", name)


def pick(names, patterns) -> list:
    """The solids of every body a pattern names."""
    picked = []
    for p in patterns:
        hit = [n for n in names if fnmatch.fnmatchcase(body(n), p)]
        if not hit:
            raise SystemExit(f"where: no body is named {p}")
        picked += [n for n in hit if n not in picked]
    return picked


def near(a, b, margin, axes=range(3)) -> bool:
    """Whether two boxes come within `margin` of each other on every one of `axes`."""
    return all(a[0][i] < b[1][i] + margin and a[1][i] > b[0][i] - margin for i in axes)


def parting(a, b, margin) -> dict:
    """How far box `a` goes in each direction before it stands `margin` off box `b`."""
    return {d: (a[1][k] - b[0][k] if sign < 0 else b[1][k] - a[0][k]) + margin
            for d, (k, sign) in DIRECTIONS.items()}


def _spans(alo, ahi, blo, bhi, sign, margin):
    """The open interval of moves along one axis that leaves `a` within `margin` of `b`, from the
    two's extents on that axis."""
    if sign > 0:
        return blo - margin - ahi, bhi + margin - alo
    return alo - bhi - margin, ahi - blo + margin


def _first_free(lo, hi):
    """The least move at or past zero inside none of the open intervals (lo, hi), and the
    intervals that end there."""
    lo, hi = np.asarray(lo, float), np.asarray(hi, float)
    live = np.flatnonzero(hi > 0)
    if not len(live):
        return 0.0, []
    order = live[np.argsort(lo[live], kind="stable")]
    reach = np.maximum.accumulate(np.concatenate([[0.0], hi[order]]))
    free = np.flatnonzero(lo[order] >= reach[:-1])
    s = float(reach[free[0]] if len(free) else reach[-1])
    return s, ([int(x) for x in np.flatnonzero(hi == s)] if s > 0 else [])


def box_spans(carried, against, direction, margin):
    """The open intervals of moves in `direction` that leave a box in `carried` within `margin` of
    a box in `against`, and the pair each belongs to. A pair within the margin across the other
    two axes rules out one interval; any other pair rules out none."""
    k, sign = DIRECTIONS[direction]
    rest = [i for i in range(3) if i != k]
    whose = [(a, b) for a in carried for b in against if near(carried[a], against[b], margin, rest)]
    spans = [_spans(carried[a][0][k], carried[a][1][k], against[b][0][k], against[b][1][k], sign, margin)
             for a, b in whose]
    return whose, np.array([lo for lo, _ in spans]), np.array([hi for _, hi in spans])


def _cells(tri, k, origin, shape, ray):
    """The least and greatest depth along axis `k` the triangles reach over each cell of a grid
    laid `ray` apart across the other two axes from `origin`; inf and -inf where none does.

    A triangle reaches a cell its shadow meets, to the depths its plane takes across the cell,
    held within the triangle's own. A triangle edge-on to the rays casts no shadow; the solid's
    faces either side of it reach the cells it stands over."""
    i, j = (a for a in range(3) if a != k)
    lo, hi = np.full(shape, np.inf), np.full(shape, -np.inf)
    p, d = tri[:, :, [i, j]] - np.asarray(origin), tri[:, :, k]
    c0 = np.maximum(np.floor(p.min(1) / ray).astype(int), 0)
    c1 = np.minimum(np.floor(p.max(1) / ray).astype(int), np.array(shape) - 1)
    n = np.maximum(c1 - c0 + 1, 0)
    count = n[:, 0] * n[:, 1]
    t = np.repeat(np.arange(len(tri)), count)
    if not len(t):
        return lo, hi
    off = np.arange(len(t)) - np.repeat(np.cumsum(count) - count, count)
    ci, cj = c0[t, 0] + off // n[t, 1], c0[t, 1] + off % n[t, 1]
    pt, dt = p[t], d[t]
    # The shadow meets the cell unless one of its edges has the whole cell beyond it.
    corners = np.stack([np.stack([ci + a, cj + b], -1) for a in (0, 1) for b in (0, 1)], 1) * ray
    meets = np.ones(len(t), bool)
    for e in range(3):
        a, b, c = pt[:, e], pt[:, (e + 1) % 3], pt[:, (e + 2) % 3]
        normal = np.stack([a[:, 1] - b[:, 1], b[:, 0] - a[:, 0]], -1)
        side = np.sign(np.einsum("ij,ij->i", normal, c - a))
        meets &= (side == 0) | ((np.einsum("ikj,ij->ik", corners - a[:, None], normal)
                                 * side[:, None]).max(1) >= 0)
    e1, e2 = pt[:, 1] - pt[:, 0], pt[:, 2] - pt[:, 0]
    det = e1[:, 0] * e2[:, 1] - e1[:, 1] * e2[:, 0]
    meets &= np.abs(det) > 1e-12
    det = np.where(meets, det, 1.0)
    gi = ((dt[:, 1] - dt[:, 0]) * e2[:, 1] - (dt[:, 2] - dt[:, 0]) * e1[:, 1]) / det
    gj = (e1[:, 0] * (dt[:, 2] - dt[:, 0]) - e2[:, 0] * (dt[:, 1] - dt[:, 0])) / det
    at = (dt[:, 0] + gi * ((ci + 0.5) * ray - pt[:, 0, 0]) + gj * ((cj + 0.5) * ray - pt[:, 0, 1]))
    half = (np.abs(gi) + np.abs(gj)) * ray / 2
    dmin, dmax = dt.min(1), dt.max(1)
    near_, far_ = np.clip(at - half, dmin, dmax), np.clip(at + half, dmin, dmax)
    np.minimum.at(lo, (ci[meets], cj[meets]), near_[meets])
    np.maximum.at(hi, (ci[meets], cj[meets]), far_[meets])
    return lo, hi


def _grow(lo, hi, margin, ray):
    """Each cell's depths carried out to every point within `margin` of the surface: from each
    cell that comes within `margin` across the grid, by what is left of it along the ray."""
    r = int(np.ceil(margin / ray))
    plo, phi = np.pad(lo, r, constant_values=np.inf), np.pad(hi, r, constant_values=-np.inf)
    out_lo, out_hi = np.full(lo.shape, np.inf), np.full(hi.shape, -np.inf)
    for di in range(-r, r + 1):
        for dj in range(-r, r + 1):
            across = (max(0, abs(di) - 1) ** 2 + max(0, abs(dj) - 1) ** 2) * ray ** 2
            if across > margin ** 2:
                continue
            along = np.sqrt(margin ** 2 - across)
            window = (slice(r + di, r + di + lo.shape[0]), slice(r + dj, r + dj + lo.shape[1]))
            out_lo, out_hi = np.minimum(out_lo, plo[window] - along), np.maximum(out_hi, phi[window] + along)
    return out_lo, out_hi


def _ray_spans(ta, tb, k, sign, margin, ray):
    """The open intervals of moves along axis `k` that leave mesh `a` within `margin` of mesh `b`
    on some ray across the other two axes."""
    i, j = (x for x in range(3) if x != k)
    pa, pb = ta.reshape(-1, 3), tb.reshape(-1, 3)
    pad = (int(np.ceil(margin / ray)) + 1) * ray
    lo = [max(pa[:, x].min(), pb[:, x].min() - margin) - pad for x in (i, j)]
    hi = [min(pa[:, x].max(), pb[:, x].max() + margin) + pad for x in (i, j)]
    if lo[0] > hi[0] or lo[1] > hi[1]:
        return np.empty(0), np.empty(0)
    shape = tuple(int(np.ceil((h - l) / ray)) + 1 for l, h in zip(lo, hi))
    alo, ahi = _cells(ta, k, lo, shape, ray)
    blo, bhi = _grow(*_cells(tb, k, lo, shape, ray), margin, ray)
    both = np.isfinite(alo) & np.isfinite(blo)
    s_lo, s_hi = _spans(alo, ahi, blo, bhi, sign, 0.0)
    return s_lo[both], s_hi[both]


def ray_spans(triangles, carried, against, direction, margin, ray=RAY):
    """`box_spans` read off rays cast `ray` apart through the meshes of the pairs whose boxes rule
    anything out: an interval for each ray that crosses both."""
    k, sign = DIRECTIONS[direction]
    rest = [i for i in range(3) if i != k]
    whose, los, his = [], [np.empty(0)], [np.empty(0)]
    for a in carried:
        for b in against:
            if near(carried[a], against[b], margin, rest):
                lo, hi = _ray_spans(triangles(a), triangles(b), k, sign, margin, ray)
                los.append(lo), his.append(hi)
                whose += [(a, b)] * len(lo)
    return whose, np.concatenate(los), np.concatenate(his)


def clear(spans):
    """The least move at or past zero inside none of the intervals, and the pairs that set it."""
    whose, lo, hi = spans
    s, ends = _first_free(lo, hi)
    return s, list(dict.fromkeys(whose[i] for i in ends))


def reach(spans):
    """The farthest move from zero that enters none of the intervals, and the pairs that set it:
    inf when none lies ahead, and 0 when one holds zero already."""
    whose, lo, hi = spans
    ahead = np.flatnonzero(hi > 0)
    if not len(ahead):
        return np.inf, []
    s = max(float(lo[ahead].min()), 0.0)
    return s, list(dict.fromkeys(whose[i] for i in ahead[lo[ahead] <= s]))


def _span(box) -> str:
    lo, hi = box
    return "  ".join(f"{axis} {lo[i]:.2f}..{hi[i]:.2f}" for i, axis in enumerate("XYZ"))


def _size(box) -> str:
    return " x ".join(f"{d:.2f}" for d in box[1] - box[0])


def _bodies(boxes) -> dict:
    """{body: (its solids' names, the box round them all)}."""
    out = {}
    for n in boxes:
        out.setdefault(body(n), []).append(n)
    return {b: (names, (np.min([boxes[n][0] for n in names], 0), np.max([boxes[n][1] for n in names], 0)))
            for b, names in out.items()}


def main(argv) -> int:
    ap = argparse.ArgumentParser(prog="where", description=__doc__.splitlines()[0])
    ap.add_argument("scene", help="a .step.mesh path, the STEP beside one, or a scene's name")
    ap.add_argument("bodies", nargs="*", metavar="BODY", help="body names or shell patterns")
    ap.add_argument("--move", nargs=3, type=float, metavar=("DX", "DY", "DZ"), default=(0.0, 0.0, 0.0))
    ap.add_argument("--against", nargs="+", metavar="BODY", help="body names or shell patterns")
    ap.add_argument("--margin", type=float, default=0.0)
    for flag in ("--clear", "--reach"):
        ap.add_argument(flag, nargs="*", choices=list(DIRECTIONS), metavar="DIR",
                        help="west east fore aft down up; all six when none is named")
    ap.add_argument("--ray", type=float, default=RAY, help=f"mm between the rays (default {RAY:g})")
    a = ap.parse_args(argv)
    if (a.clear is not None or a.reach is not None) and not a.against:
        ap.error("--clear and --reach need --against")

    path = payload(a.scene)
    head, meshes = read(path)
    boxes = {n: (p.min(0).astype(float), p.max(0).astype(float)) for n, (p, _) in meshes.items()}
    if stale(path, head):
        print(f"note: {path.name[:-len('.mesh')]} has been rewritten since this payload was cut from it")
    if not a.bodies:
        groups = _bodies(boxes)
        print(f"{path.name}: {len(boxes)} solids in {len(groups)} bodies")
        for b in sorted(groups):
            names, box = groups[b]
            print(f"{b:28} {len(names):3d}  {_span(box)}  {_size(box)}")
        return 0

    move = np.array(a.move)
    carried = {n: (boxes[n][0] + move, boxes[n][1] + move) for n in pick(boxes, a.bodies)}
    if any(move):
        print("moved " + " ".join(f"{axis} {d:+.2f}" for axis, d in zip("XYZ", move)))
    for b, (names, box) in sorted(_bodies(carried).items()):
        print(f"{b:28} {len(names):3d}  {_span(box)}  {_size(box)}")
        if not a.against and len(names) > 1:
            for n in names:
                print(f"  {n:24} {_span(carried[n])}  {_size(carried[n])}")
    if not a.against:
        return 0

    against = {n: boxes[n] for n in pick(boxes, a.against) if n not in carried}
    pairs = [(m, n) for m in carried for n in against if near(carried[m], against[n], a.margin)]
    print(f"\nboxes within {a.margin:g} mm, how far they overlap, and the move in each direction "
          f"that stands them {a.margin:g} mm apart:")
    if not pairs:
        print("  none")
    for m in dict.fromkeys(m for m, _ in pairs):
        print(f"{m:24} {_span(carried[m])}  {_size(carried[m])}")
        for _, n in (p for p in pairs if p[0] == m):
            o = np.minimum(carried[m][1], against[n][1]) - np.maximum(carried[m][0], against[n][0])
            print(f"  {n:22} overlap " + " ".join(f"{axis} {v:.2f}" for axis, v in zip("XYZ", o))
                  + "   " + " ".join(f"{d} {v:.2f}" for d, v in parting(carried[m], against[n], a.margin).items()))
    cache = {}

    def triangles(n):
        if n not in cache:
            pos, idx = meshes[n]
            cache[n] = pos[idx].astype(float) + (move if n in carried else 0.0)
        return cache[n]

    for dirs, choose, what, none in (
            (a.clear, clear, f"least move from there with every pair {a.margin:g} mm apart", "nothing in the way"),
            (a.reach, reach, f"farthest move from there before a pair comes within {a.margin:g} mm", "nothing ahead")):
        if dirs is None:
            continue
        print(f"\n{what}, by rays {a.ray:g} mm apart through the meshes [by boxes]:")
        for d in dirs or DIRECTIONS:
            s, setters = choose(ray_spans(triangles, carried, against, d, a.margin, a.ray))
            print(f"  {d:5} {s:7.2f} [{choose(box_spans(carried, against, d, a.margin))[0]:7.2f}]   "
                  + ("; ".join(f"{m} against {n}" for m, n in setters) or none))
    return 0


def _cuboid(lo, hi):
    """A box's eight corners and twelve triangles."""
    pos = [(x, y, z) for x in (lo[0], hi[0]) for y in (lo[1], hi[1]) for z in (lo[2], hi[2])]
    idx = [(0, 1, 3), (0, 3, 2), (4, 6, 7), (4, 7, 5), (0, 4, 5), (0, 5, 1),
           (2, 3, 7), (2, 7, 6), (0, 2, 6), (0, 6, 4), (1, 5, 7), (1, 7, 3)]
    return pos, idx


def _write(path, solids, src=None):
    """A payload laid out the way `_mesh_payload.write` lays one out, from {name: (pos, idx)}."""
    entries, blob = [], bytearray()
    for name, (pos, idx) in solids.items():
        e = {"name": name, "color": None}
        for key, fmt, arr in (("pos", "f", [c for p in pos for c in p]), ("nrm", "f", []),
                              ("idx", "I", [i for t in idx for i in t]), ("fac", "I", [])):
            e[key] = [len(blob), len(arr)]
            blob += struct.pack(f"<{len(arr)}{fmt}", *arr)
        entries.append(e)
    header = {"v": 3, "meshes": entries}
    if src is not None:
        header["src"] = src
    head = json.dumps(header, separators=(",", ":")).encode()
    head += b" " * (-(len(head) + 4) % 4)
    Path(path).write_bytes(struct.pack("<I", len(head)) + head + bytes(blob))


def selftest():
    """Boxes read back, bodies grouped, the STEP's digest, and the parting and least moves, by
    boxes and by rays, against arithmetic."""
    def check(what, got, want, tol=1e-4):
        got = np.round(np.asarray(got, float), 4).tolist()
        if not np.allclose(got, np.asarray(want, float), atol=tol):
            raise AssertionError(f"{what}: {got} rather than {want}")
        return f"{what}: {got}"

    # A wedge along Y whose sloped face runs from (1, 0) to (3, 2) in XZ.
    wedge = ([(1, 0, 0), (3, 0, 0), (3, 0, 2), (1, 1, 0), (3, 1, 0), (3, 1, 2)],
             [(0, 1, 2), (3, 4, 5), (0, 1, 4), (0, 4, 3), (1, 2, 5), (1, 5, 4), (0, 2, 5), (0, 5, 3)])
    with tempfile.TemporaryDirectory() as d:
        step = Path(d) / "scene.step"
        step.write_bytes(b"scene")
        _write(f"{step}.mesh", {
            "block": _cuboid((0, 0, 0), (2, 2, 2)),
            "post": _cuboid((3, 0.5, -1), (5, 1.5, 5)),
            "post-far": _cuboid((5.2, 0, 0), (7, 2, 2)),
            "aside": _cuboid((3, 10, 0), (5, 11, 2)),
            "cold-core/coil/1": _cuboid((0, 0, 10), (1, 1, 11)),
            "cold-core/coil/2": _cuboid((2, 0, 10), (3, 1, 11)),
            "tile": _cuboid((2, 0, 1.5), (3, 1, 2)),
            "tab": _cuboid((1, 0, 1.5), (1.5, 1, 2)),
            "wedge": wedge,
        }, src=hashlib.sha256(b"scene").hexdigest())
        head, meshes = read(f"{step}.mesh")
        boxes = {n: (p.min(0).astype(float), p.max(0).astype(float)) for n, (p, _) in meshes.items()}
        yield check("post-far's box reads back", np.concatenate(boxes["post-far"]), (5.2, 0, 0, 7, 2, 2))
        if sorted(_bodies(boxes))[:3] != ["aside", "block", "cold-core/coil"]:
            raise AssertionError(f"bodies grouped as {sorted(_bodies(boxes))}")
        if pick(boxes, ["cold-core/*"]) != ["cold-core/coil/1", "cold-core/coil/2"]:
            raise AssertionError("a body with a slash in its name lost its solids")
        yield "a body's solids group under its name, slash and all"
        if stale(f"{step}.mesh", head):
            raise AssertionError("a payload reads as stale beside the STEP it was cut from")
        step.write_bytes(b"scene, cut again")
        if not stale(f"{step}.mesh", head):
            raise AssertionError("a payload reads as current beside a rewritten STEP")
        yield "a rewritten STEP is noticed"

    def triangles(n, move=(0.0, 0.0, 0.0)):
        pos, idx = meshes[n]
        return pos[idx].astype(float) + np.array(move)

    # The block carried 2 east stands 1 into the post on X, 1 on Y and 2 on Z.
    carried = {"block": (np.array((2., 0, 0)), np.array((4., 2, 2)))}
    against = {n: boxes[n] for n in ("post", "post-far", "aside")}
    yield check("block against post, 0.5 apart", list(parting(carried["block"], boxes["post"], 0.5).values()),
                (1.5, 3.5, 2.0, 2.0, 3.5, 5.5))
    # East, the block clears the post at 3.5 and stands in post-far there; past post-far is 5.5.
    # The aside post is 8 mm off across Y and rules nothing out.
    s, setters = clear(box_spans(carried, against, "east", 0.5))
    if setters != [("block", "post-far")]:
        raise AssertionError(f"east was set by {setters}")
    yield check("least east by boxes, past both posts", s, 5.5)
    yield check("least west by boxes, off the post", clear(box_spans(carried, against, "west", 0.5))[0], 1.5)
    touching = {"block": (np.array((1., 0, 0)), np.array((3., 2, 2)))}
    yield check("least west from touching, margin 0", clear(box_spans(touching, against, "west", 0.0))[0], 0.0)
    # Boxes are their solids, so rays read what the boxes read, to within a ray's margin.
    rays = clear(ray_spans(lambda n: triangles(n, (2, 0, 0) if n == "block" else (0, 0, 0)),
                           carried, against, "east", 0.5))
    yield check("least east by rays, cuboids", rays[0], 5.5)
    # The tile stands in the wedge's box and against its slope. West, the boxes part at
    # 3 - 1 = 2; the tile's east face meets the slope's foot at height 1.5 at x 2.5, so it is
    # clear 0.5 west, to within one ray across the slope.
    tile, wedge_box = {"tile": boxes["tile"]}, {"wedge": boxes["wedge"]}
    yield check("least west by boxes, tile against wedge", clear(box_spans(tile, wedge_box, "west", 0.0))[0], 2.0)
    yield check("least west by rays, tile against wedge",
                clear(ray_spans(triangles, tile, wedge_box, "west", 0.0))[0], 0.5, tol=RAY)
    # Two cubes side by side on X, 0.3 apart across both Y and Z, so their nearest edges are
    # 0.42 apart. Half a millimetre off one another, east past the other is 1 + √(0.5² − 0.3² − 0.3²)
    # = 1.26 exactly and 1.5 by boxes; the rays read between, by what a ray's width rounds off.
    pair = {"near": _cuboid((3, 0, 0), (4, 1, 1)), "far": _cuboid((3, 1.3, 1.3), (4, 2.3, 2.3))}
    corner = {n: (np.min(pos, 0).astype(float), np.max(pos, 0).astype(float)) for n, (pos, _) in pair.items()}
    by_rays = clear(ray_spans(lambda n: np.array(pair[n][0], float)[np.array(pair[n][1])],
                              {"near": corner["near"]}, {"far": corner["far"]}, "east", 0.5))[0]
    if not 1 + np.sqrt(0.25 - 0.18) <= by_rays < clear(box_spans({"near": corner["near"]}, {"far": corner["far"]}, "east", 0.5))[0]:
        raise AssertionError(f"a corner-to-corner approach read {by_rays:.3f} by rays")
    yield f"a corner-to-corner approach reads {by_rays:.3f} by rays, between 1.265 exactly and 1.5 by boxes"
    # The block, 1 short of the post and 0.5 off it, reaches it at 0.5 east; west lies open.
    block = {"block": boxes["block"]}
    yield check("reach east by boxes, block to post", reach(box_spans(block, against, "east", 0.5))[0], 0.5)
    yield check("reach east by rays, block to post", reach(ray_spans(triangles, block, against, "east", 0.5))[0], 0.5)
    yield check("reach west, nothing ahead", reach(box_spans(block, against, "west", 0.5))[0], np.inf)
    # The tab stands inside the wedge's box, its east edge 1 over the slope: by boxes it goes
    # nowhere down, and the rays read the slope short by its rise across one ray.
    tab = {"tab": boxes["tab"]}
    yield check("reach down by boxes, tab over wedge", reach(box_spans(tab, wedge_box, "down", 0.0))[0], 0.0)
    by_rays = reach(ray_spans(triangles, tab, wedge_box, "down", 0.0))[0]
    if not 1 - RAY - 1e-6 <= by_rays <= 1 + 1e-6:
        raise AssertionError(f"the tab reached {by_rays:.3f} down by rays")
    yield f"the tab reaches {by_rays:.3f} down by rays, short of 1 by a ray across the slope at most"


if __name__ == "__main__":
    signal.signal(signal.SIGPIPE, signal.SIG_DFL)  # piped into head, stop quietly
    if sys.argv[1:] == ["selftest"]:
        for line in selftest():
            print(" ", line)
        print("where selftest OK")
    else:
        sys.exit(main(sys.argv[1:]))
