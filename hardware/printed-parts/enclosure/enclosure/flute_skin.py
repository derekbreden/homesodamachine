"""The enclosure's fluted show surfaces, cut into the MESH a printer reads.

The corner coupon at `69459fea6` settled this texture, and settled it as a heightfield: every station
on the wall is displaced inward by `texture_depth * groove(across) * smoothstep(along / rise)`,
sampled finely enough that what comes back is the curve and not an approximation of it. That
coupon is this box's own corner at this box's own `wall` and `corner_round`, and it printed.
This is the same field on the whole box.

WHAT THE FIELD IS STRUCK ALONG IS A RAIL, and the box's outer silhouette is one of them. A
rail hands back a point and an OUTWARD NORMAL at an arc length, says how far it runs, whether
it closes on itself, over what height band it exists, and what other bodies are berthed
against the faces it runs along. Everything below reads those and nothing else — which is
why a run round the inside of a storey is the same object here as the run round the outside
of the box, and why neither of them is named in this file. `enclosure.flute_rails` is where
the box says which runs it has.

WHY IT IS NOT IN THE SOLID. The fade is what makes the texture look made rather than applied,
and the fade is a FIELD OVER THE SURFACE — how far a station stands from the nearest place the
show face ends. A boundary-representation prism can carry a fade that runs level, because a
level fade is a loft; it cannot carry one that follows an opening's rim, a pocket's edge and
the display facet's diagonal arris all at once, and every attempt to make it costs a separate
mechanism per edge and still comes out a different shape from the coupon's. Measured over the
surface, they are all one fact and there is nothing to enumerate.

HOW THE EDGE FINDS ITSELF. Nothing here is told where an opening is. The piece is asked, at
every station, whether it has material at the nominal surface — and where it does not, that is
an edge, whatever made it. A flank opening, a port chip's seat, the nameplate's pocket, the
bay's own mouth, the seam a piece simply ends on, the facet's arris: one question, one answer,
one ramp. The rail is the parameterisation, so ARC LENGTH is the across-coordinate and a flute
crosses `corner_round`'s quarter turn without knowing the corner is there. An OPEN rail's two
ends are two more edges and want no other treatment.

AND A BODY IN THE ROOM IS AN EDGE TOO. Inside a storey the piece has material at the rail in
places a drawer stands in front of, and those are not show faces: what a fitted body hides is
not a surface anyone finishes. `_shadow_mask` asks, at every station, whether a berthed body
stands between that face and the storey's own mouth — the same question `_show_mask` asks,
asked of the other bodies — and the ramp that stops the flutes at the cartridge's edge is the
ramp that stops them at an opening's rim.

AND ONE KIND OF EDGE IS NOT ONE. An opening whose two jambs both stand on ONE groove's own side
surface runs WITH the flutes and stops nothing — the groove carries on past it at full depth.
`_bridge_grooves` gives those runs back to the show face, read off the run's own two ends and
not off any list of where an opening is. The condenser's vents are the whole of it on the box as
it stands, and without it a field pierced down every groove ramps itself flat.
"""

import math
import sys
from pathlib import Path
from typing import NamedTuple

import numpy as np
import trimesh
from scipy import ndimage
from scipy.spatial import cKDTree

_here = Path(__file__).resolve()
sys.path.insert(0, str(next(p for p in _here.parents if p.name == "printed-parts") / "cadlib"))
import reeding                                                          # noqa: E402

# How finely the field is sampled ACROSS the flutes. The corner coupon at `69459fea6` used 0.3 mm on the
# same groove and printed clean; a 4 mm groove read at this step carries its arc to about 28
# microns, a fifteenth of the 0.42 mm bead that draws it and well under what the machine can
# repeat. IT IS NOT FREE: the mesh is what a slicer reads, so a step finer than the show
# surface can use is paid on every export for nothing.
grid_across = 0.4
# And ALONG them. The field is constant along a flute except where it ramps, so rows that say
# nothing new are dropped after the field is built rather than never taken — the ramp is what
# needs the resolution and the ramp is 5 mm of a 358 mm wall.
grid_along = 0.25
# How far outboard the cutter stands before it turns inward. It is air out there; what this
# buys is a boolean that never has to decide about two surfaces lying on each other.
cut_margin = 0.4
# HOW FAR THE CUTTER'S CAPS STAND CLEAR OF ANY FACE. On a rail that runs the piece's own
# height they land PAST its top and bottom faces; on one that runs a storey they land INSIDE
# that storey's floor and ceiling. Either way the cap is in air by this much, because a cap
# that lands a fraction of a micron off a face leaves the boolean a sliver to resolve, and
# what it resolves it into is degenerate triangles, duplicate faces and edges carrying four
# and six faces apiece. A slicer reads that as non-manifold and refuses the part, and it
# refuses it while `is_watertight` still says yes.
cut_overrun = 1.0
# How far the cutter's own surface may stand off the rail where stations are dropped. A corner
# keeps its stations at this; the flats collapse to their two ends regardless, because there the
# chord and the rail are the same line.
plan_tol = 0.01
# A station counts as show face when the piece's own material reaches this close to the rail.
# Bigger than the mesh's own deviation, far smaller than the shallowest recess that is not
# meant to be fluted (a port chip's seat is 2.0 mm).
face_tol = 0.25


class Rail(NamedTuple):
    """One run the field is struck along.

    `at(s)` hands back the run's point and OUTWARD normal at arc length `s`, measured in the
    FIELD'S OWN coordinate — `start` is where the walk begins in it, so a run whose datum is
    its middle says so by starting at minus half its length, and `reeding.groove` is read at
    the same `s` on every rail the box has.

    `closed` says whether the two ends are the same station. `band` is the height the run
    exists over, or None for the whole piece. `berthed` are the bodies fitted into the room
    it runs round, and `mouth` is the plan direction that room opens on — the two together
    are what `_shadow_mask` reads."""
    at: object
    length: float
    start: float = 0.0
    closed: bool = True
    band: object = None
    berthed: tuple = ()
    mouth: tuple = (0.0, -1.0)


def _rail_frames(rail):
    """Every across-station on one rail: (arc length, point, outward normal).

    A CLOSED rail stops one step short of its own start, because that station is already
    drawn; an OPEN one carries both its ends, because they are two edges."""
    steps = max(int(round(rail.length / grid_across)), 3)
    if rail.closed:
        s = rail.start + np.arange(steps) * (rail.length / steps)
    else:
        s = rail.start + np.linspace(0.0, rail.length, steps + 1)
    point = np.empty((len(s), 2))
    normal = np.empty((len(s), 2))
    for i, si in enumerate(s):
        (px, py), (nx, ny) = rail.at(float(si))
        point[i] = (px, py)
        normal[i] = (nx, ny)
    return s, point, normal


def _field_rows(mesh, band):
    """The heights the field is read at — the piece's own span, or the band a storey's run
    exists over, held `cut_overrun` clear of whichever ends it."""
    lo, hi = mesh.bounds[0][2], mesh.bounds[1][2]
    if band is not None:
        lo, hi = max(lo, band[0] + cut_overrun), min(hi, band[1] - cut_overrun)
        return np.arange(lo, hi + grid_along / 2.0, grid_along)
    # OFF THE PIECE'S OWN FACES BY A MARGIN THAT MEANS SOMETHING. A level cut taken ON the top
    # or bottom face is degenerate, so the field's first and last rows stand clear of both.
    return np.arange(lo + grid_along, hi - grid_along / 2.0, grid_along)


def _outline(segments, step):
    """A level cut's outline, RESAMPLED to `step` — the raw segments a plane makes with the
    mesh, walked. Asking how far a station stands from the outline means asking about the
    LINE; a wall 200 mm long is one segment and its two ends say nothing about the middle."""
    if segments is None or len(segments) == 0:
        return np.empty((0, 2))
    a = segments[:, 0, :2]
    b = segments[:, 1, :2]
    span = np.hypot(*(b - a).T)
    counts = np.maximum((span / step).astype(int), 1)
    runs = []
    for start, end, count in zip(a, b, counts):
        t = np.linspace(0.0, 1.0, count, endpoint=False)[:, None]
        runs.append(start + (end - start) * t)
    runs.append(b)
    return np.vstack(runs)


def _level(mesh, z):
    """One horizontal cut through a mesh, as raw segments."""
    return trimesh.intersections.mesh_plane(
        mesh, plane_normal=np.array([0.0, 0.0, 1.0]),
        plane_origin=np.array([0.0, 0.0, float(z)]))


def _show_mask(mesh, point, rows):
    """Where the piece has material AT the nominal surface — the show face, and nothing else.

    Read by SECTION rather than by asking about points one at a time: one horizontal cut gives
    the piece's whole outline at that height, and a station is show face when the outline runs
    within `face_tol` of the rail there. An opening has no outline on the rail; a pocket's has
    moved inboard; a piece that has simply ended has none at all."""
    mask = np.zeros((len(point), len(rows)), dtype=bool)
    for j, z in enumerate(rows):
        pts = _outline(_level(mesh, z), face_tol / 2.0)
        if len(pts) < 3:
            continue
        near = cKDTree(pts).query(point, distance_upper_bound=face_tol)[0]
        mask[:, j] = np.isfinite(near)
    return mask


def _shadow_mask(bodies, point, rows, mouth):
    """Where a body berthed in the room stands between the face and the room's own mouth.

    THE SAME QUESTION `_show_mask` ASKS, ASKED OF THE OTHER BODIES. A level cut gives each
    body its whole outline at that height; a station stands in shadow when that outline
    reaches the station's own across-coordinate at any depth NEARER THE MOUTH than the station
    is. A drawer fitted into a bay hides the wall behind it and nothing else — the post beside
    it, which the drawer never passes, is not in its shadow at any height.

    Read in the room's own two directions rather than the box's: `mouth` is out, and across is
    the perpendicular of it, so nothing here knows which way the machine faces."""
    out = np.array(mouth, dtype=float)
    out /= np.hypot(*out)
    across = np.array([-out[1], out[0]])
    qu = point @ across
    qv = point @ out
    shadow = np.zeros((len(point), len(rows)), dtype=bool)
    for body in bodies:
        lo, hi = body.bounds[0][2], body.bounds[1][2]
        corner = np.array([(x, y) for x in body.bounds[:, 0] for y in body.bounds[:, 1]])
        if ((corner @ out).max() <= qv.min()
                or (corner @ across).max() <= qu.min()
                or (corner @ across).min() >= qu.max()):
            continue
        for j, z in enumerate(rows):
            if not lo <= z <= hi:
                continue
            segments = _level(body, z)
            if segments is None or len(segments) == 0:
                continue
            a = segments[:, 0, :2]
            b = segments[:, 1, :2]
            au, bu = a @ across, b @ across
            av, bv = a @ out, b @ out
            run, rise = (bu - au)[None, :], (bv - av)[None, :]
            for lo_i in range(0, len(qu), 512):
                q = slice(lo_i, min(lo_i + 512, len(qu)))
                straddle = (au[None, :] > qu[q, None]) != (bu[None, :] > qu[q, None])
                t = np.zeros(straddle.shape)
                np.divide(qu[q, None] - au[None, :], run, out=t, where=straddle)
                v = av[None, :] + t * rise
                shadow[q, j] |= (straddle & (v > qv[q, None])).any(axis=1)
    return shadow


def _bridge_grooves(mask, s, closed):
    """Background runs lying INSIDE ONE GROOVE, given back to the show face.

    THE FADE IS FOR AN EDGE THAT CROSSES A FLUTE. `_show_mask` asks only whether the piece has
    material at the nominal surface, which is the right question for an opening's rim, a
    pocket's edge and a seam alike — and it is the wrong answer for an opening whose two jambs
    both stand on ONE groove's own side surface. Such a rim runs WITH the flutes and stops
    nothing: the groove carries on past it at full depth, the box's own rule that a rim running
    with the flutes is not one of them.

    THE CONDENSER'S VENTS ARE THAT, all of it. A slot narrower than the groove is struck down
    the groove's own floor down EVERY groove of a field (`enclosure._flank_vents`). Left as
    background each one reads as an edge, every station on the wall then stands within a
    millimetre of one, and the ramp takes the whole vent — grooves, mullions and all — down to a
    flat panel with holes in it. Nothing about the vent is named here: what is read is the RUN's
    own two ends, which is what the rule is about.

    The ends are carried half a grid step outward, because the edge itself lies between the last
    station that has material and the first that has none."""
    out = mask.copy()
    half = reeding.flute_width / 2.0
    span = float(s[-1] + (s[1] - s[0]) - s[0])
    for j in range(mask.shape[1]):
        col = mask[:, j]
        idx = np.flatnonzero(~col)
        if len(idx) == 0 or len(idx) == len(col):
            continue
        groups = np.split(idx, np.flatnonzero(np.diff(idx) > 1) + 1)
        if closed and len(groups) > 1 and groups[0][0] == 0 and groups[-1][-1] == len(col) - 1:
            groups[0] = np.concatenate([groups[-1], groups[0]])
            groups.pop()
        for g in groups:
            a = float(s[g[0]]) - grid_across / 2.0
            b = float(s[g[-1]]) + grid_across / 2.0
            if g[0] > g[-1]:
                b += span
            centre = round(a / flute_pitch) * flute_pitch
            if abs(a - centre) <= half and abs(b - centre) <= half:
                out[g, j] = True
    return out


def _depth_field(s, mask, closed):
    """The inward displacement at every station — the coupon's own expression, with the ramp
    driven by how far the station stands from the nearest edge of the show face.

    A CLOSED RAIL WRAPS ACROSS AND AN OPEN ONE DOES NOT, and both halves of that have to be
    said out loud or the box comes out wrong in a different way each time. A closed run's arc
    length is a loop, so the field is tripled in that axis and the middle taken back —
    otherwise the two ends of the arc length would each read as an edge and the box would fade
    to nothing down a seam that is not there. An open run's two ends ARE edges, and get a
    column of background to measure to, the same as the two ends of the HEIGHT: the bed, the
    seam a piece ends on, the ceiling, a storey's own floor, all of them real edges — and a
    distance transform does NOT treat an array's own boundary as background, so left alone it
    measures from there to the nearest opening halfway up the wall and reports no edge at
    all."""
    wide = np.vstack([mask, mask, mask]) if closed else mask
    pad = np.pad(wide, ((0, 0) if closed else (1, 1), (1, 1)), constant_values=False)
    far = ndimage.distance_transform_edt(pad, sampling=(grid_across, grid_along))
    far = far[len(mask):2 * len(mask), 1:-1] if closed else far[1:-1, 1:-1]
    along = np.clip(far / flute_rise, 0.0, 1.0)
    fade = along * along * (3.0 - 2.0 * along)
    across = reeding.groove(s, flute_pitch, reeding.flute_width)[:, None]
    return flute_depth * across * fade * mask


def _thin(depth, rows, s, point, normal):
    """Drop the stations that say nothing new.

    The field is CONSTANT ALONG A FLUTE except where it ramps, and a ramp is 5 mm of a 358 mm
    wall — so most rows repeat the one above them exactly, and a mesh drawn through all of them
    is ten million triangles of saying the same thing. Across, the same is true of every stretch
    of a rail this piece does not carry: the depth is zero the whole height and two columns
    describe it as well as four hundred.

    A row or column is kept when it differs from the last one kept. Nothing is interpolated
    away: every station where the field actually moves is still drawn.

    AND A COLUMN CARRIES THE RAIL AS WELL AS THE FIELD, which is the trap. Dropping a station
    because the DEPTH there is unchanged leaves the cutter's own surface running straight from
    the last kept station to the next — a chord across the rail. Down a flat wall that chord IS
    the rail and costs nothing. Across a corner, or across the long stretch of perimeter a piece
    does not carry, it cuts the corner off and the cutter runs through the INSIDE of the box,
    slicing whatever it meets: a seam lip, an underwall, a boss. Every edge that leaves is one
    four faces share, a slicer refuses the file, and nothing measured in memory can see it.

    So a column is kept when the depth moves OR when dropping it would pull the cutter's surface
    off the rail by more than `plan_tol`. The flats still collapse to their two ends, because
    there a chord and the rail are the same line."""
    tol = 0.01
    keep_rows = [0]
    for j in range(1, depth.shape[1]):
        if np.abs(depth[:, j] - depth[:, keep_rows[-1]]).max() > tol:
            if j - 1 != keep_rows[-1]:
                keep_rows.append(j - 1)
            keep_rows.append(j)
    if keep_rows[-1] != depth.shape[1] - 1:
        keep_rows.append(depth.shape[1] - 1)
    keep_cols = [0]
    for i in range(1, depth.shape[0]):
        moved = np.abs(depth[i] - depth[keep_cols[-1]]).max() > tol
        if not moved and _chord_error(point, keep_cols[-1], i) <= plan_tol:
            continue
        if i - 1 != keep_cols[-1]:
            keep_cols.append(i - 1)
        keep_cols.append(i)
    keep_cols.append(depth.shape[0] - 1)
    rows_i = np.array(keep_rows)
    cols_i = np.array(sorted(set(keep_cols)))
    return (depth[np.ix_(cols_i, rows_i)], np.asarray(rows)[rows_i],
            point[cols_i], normal[cols_i])


def _chord_error(point, first, last):
    """How far the rail wanders off the straight line between two stations — what dropping
    every station between them would cost the cutter's own surface."""
    if last - first < 2:
        return 0.0
    a, b = point[first], point[last]
    run = b - a
    span = float(np.hypot(*run))
    off = point[first + 1:last] - a
    if span < 1e-12:
        return float(np.hypot(*off.T).max())
    return float(np.abs(off[:, 0] * run[1] - off[:, 1] * run[0]).max() / span)


def _cutter(point, normal, rows, depth, closed):
    """The volume between the nominal surface and the fluted one, as one closed mesh — a tube
    where the rail wraps and a slab where it does not, capped at the two heights either way."""
    count, height = depth.shape
    out = np.empty((count, height, 3))
    inn = np.empty((count, height, 3))
    z = np.asarray(rows, dtype=float)
    for i in range(count):
        out[i, :, :2] = point[i] + normal[i] * cut_margin
        inn[i, :, :2] = point[i][None, :] - normal[i][None, :] * depth[i][:, None]
        out[i, :, 2] = z
        inn[i, :, 2] = z
    vertices = np.vstack([out.reshape(-1, 3), inn.reshape(-1, 3)])
    base = count * height

    def quads(a, b, c, d):
        return np.concatenate([np.stack([a, b, c], -1), np.stack([a, c, d], -1)]).reshape(-1, 3)

    rung = np.arange(count if closed else count - 1)
    i, j = np.meshgrid(rung, np.arange(height - 1), indexing="ij")
    i, j = i.ravel(), j.ravel()
    nxt = ((i + 1) % count) * height + j
    cur = i * height + j
    faces = [quads(cur, cur + 1, nxt + 1, nxt),
             quads(base + cur, base + nxt, base + nxt + 1, base + cur + 1)]
    k = rung
    lo, hi = k * height, k * height + height - 1
    lon, hin = ((k + 1) % count) * height, ((k + 1) % count) * height + height - 1
    faces.append(quads(lo, lon, base + lon, base + lo))
    faces.append(quads(hi, base + hi, base + hin, hin))
    if not closed:
        # AND AN OPEN RUN IS SHUT AT ITS TWO ENDS, on the same two surfaces the rest of it
        # runs between — so what the boolean is handed is a slab and not a sheet.
        end = np.arange(height - 1)
        faces.append(quads(end, base + end, base + end + 1, end + 1))
        far = (count - 1) * height + end
        faces.append(quads(far, far + 1, base + far + 1, base + far))
    mesh = trimesh.Trimesh(vertices=vertices, faces=np.concatenate(faces), process=True)
    if mesh.volume < 0:
        mesh.invert()
    return mesh


def _rail_cutter(mesh, rail):
    """One rail's cutter, or None where this piece carries none of that run."""
    s, point, normal = _rail_frames(rail)
    reach = cut_margin + flute_depth + face_tol
    lo, hi = mesh.bounds
    if (point[:, 0].min() - reach > hi[0] or point[:, 0].max() + reach < lo[0]
            or point[:, 1].min() - reach > hi[1] or point[:, 1].max() + reach < lo[1]):
        return None
    rows = _field_rows(mesh, rail.band)
    if len(rows) < 4:
        return None
    mask = _show_mask(mesh, point, rows)
    if not mask.any():
        return None
    if rail.berthed:
        mask &= ~_shadow_mask(rail.berthed, point, rows, rail.mouth)
    mask = _bridge_grooves(mask, s, rail.closed)
    if not mask.any():
        return None
    depth = _depth_field(s, mask, rail.closed)
    if depth.max() <= 0.0:
        return None
    depth, rows, point, normal = _thin(depth, rows, s, point, normal)
    if rail.band is None:
        # THE CUTTER IS CAPPED IN AIR, past both ends of the piece. The field is already nothing
        # at the piece's own edges, so these two rows take the same nothing further out and give
        # the boolean two caps that lie on no face of anything.
        rows = np.concatenate([[rows[0] - cut_overrun], rows, [rows[-1] + cut_overrun]])
        depth = np.hstack([depth[:, :1] * 0.0, depth, depth[:, -1:] * 0.0])
    return _cutter(point, normal, rows, depth, rail.closed)


def flute(mesh, rails, pitch, depth_mm, rise_mm):
    """`mesh` with the box's flutes cut into whatever of its rails this piece carries."""
    global flute_pitch, flute_depth, flute_rise
    flute_pitch, flute_depth, flute_rise = pitch, depth_mm, rise_mm
    cutters = [c for c in (_rail_cutter(mesh, rail) for rail in rails) if c is not None]
    if not cutters:
        return mesh
    # ONE DIFFERENCE FOR ALL OF THEM. Every rail's field is read off the SAME surface — the
    # piece as it stands — so a run round the inside of a storey asks about a wall the run
    # round the outside has not yet grooved, and the two answers are struck together.
    # `check_volume=False` because trimesh's own gate is stricter than the engine's. A piece
    # tessellates to a surface where a handful of edges out of twenty-odd thousand carry four
    # faces rather than two — the solid touching itself along a line, which is a fact about the
    # solid and not about this mesh — and trimesh refuses the whole boolean for it. Manifold
    # takes it, repairs it, and hands back a watertight result; the caller checks that.
    cut = trimesh.boolean.difference([mesh] + cutters, engine="manifold", check_volume=False)
    # ONE MORE PASS THROUGH THE ENGINE, ON THE POSITIONS THE FILE WILL HOLD. A difference hands
    # back a result whose own invariants hold in double precision, and the exporter then rounds
    # it to float32 and makes coincidences the engine never saw. Quantising first and unioning
    # after is what puts the engine's answer and the file's contents in the same space.
    return trimesh.boolean.union([as_written(cut)], engine="manifold", check_volume=False)


def non_manifold_edges(mesh) -> int:
    """Edges the mesh gives to more than two faces — WHAT A SLICER ACTUALLY REFUSES.

    TWO THINGS ABOUT THIS READING, and getting either wrong makes it agree with you instead of
    with the machine.

    `is_watertight` IS THE EASIER QUESTION. A mesh can pass it while a slicer rejects the file,
    because winding can close over an edge that four faces share.

    AND IT MUST BE READ ON A MESH MERGED BY POSITION. An STL carries every triangle's own
    vertices, so on the soup almost no edge is shared and the count is near zero BY
    CONSTRUCTION — it cannot find the fault it exists to find. A slicer merges on import; so
    does `trimesh.load` unless told not to. Read it anywhere else and it will pass a file that
    is refused at the bed."""
    merged = mesh.copy()
    merged.merge_vertices()
    _u, counts = np.unique(merged.edges_sorted, axis=0, return_counts=True)
    return int((counts > 2).sum())


def as_written(mesh):
    """`mesh` with its vertices moved to the positions an STL will actually store.

    AN STL IS SINGLE PRECISION. Two vertices a double can tell apart land on the same float32,
    and the file then holds a coincidence the solid never had — an edge four faces share,
    invisible in memory and refused at the bed. Quantising BEFORE the last boolean lets the
    engine resolve that coincidence properly instead of the exporter creating it afterwards."""
    out = mesh.copy()
    out.vertices = out.vertices.astype(np.float32).astype(np.float64)
    out.merge_vertices()
    return out
