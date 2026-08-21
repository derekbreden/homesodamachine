"""The enclosure's fluted show surface, cut into the MESH a printer reads.

`../texture-corner/` settled this texture, and it settled it as a heightfield: every station
on the wall is displaced inward by `texture_depth * groove(across) * smoothstep(along / rise)`,
sampled finely enough that what comes back is the curve and not an approximation of it. That
coupon is this box's own corner at this box's own `wall` and `corner_round`, and it printed.
This is the same field on the whole box.

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
one ramp. `enclosure.plan_at` is the parameterisation, so ARC LENGTH is the across-coordinate
and a flute crosses `corner_round`'s quarter turn without knowing the corner is there.
"""

import math
import sys
from pathlib import Path

import numpy as np
import trimesh
from scipy import ndimage
from scipy.spatial import cKDTree

_here = Path(__file__).resolve()
sys.path.insert(0, str(next(p for p in _here.parents if p.name == "printed-parts") / "cadlib"))
import reeding                                                          # noqa: E402

# How finely the field is sampled ACROSS the flutes. `../texture-corner/` used 0.3 mm on the
# same groove and printed clean; a 4 mm groove read at this step carries its arc to about 28
# microns, a fifteenth of the 0.42 mm bead that draws it and well under what the machine can
# repeat. IT IS NOT FREE: the mesh is what the release bundle carries and what a deploy fetches,
# so a step finer than the show surface can use is paid on every deploy for nothing.
grid_across = 0.4
# And ALONG them. The field is constant along a flute except where it ramps, so rows that say
# nothing new are dropped after the field is built rather than never taken — the ramp is what
# needs the resolution and the ramp is 5 mm of a 358 mm wall.
grid_along = 0.25
# How far outboard the cutter stands before it turns inward. It is air out there; what this
# buys is a boolean that never has to decide about two surfaces lying on each other.
cut_margin = 0.4
# How far the cutter runs PAST the piece at each end. It has to clear the piece's own top and
# bottom faces outright: a cap that lands a fraction of a micron off one of them leaves the
# boolean a sliver to resolve, and what it resolves it into is degenerate triangles, duplicate
# faces and edges carrying four and six faces apiece. A slicer reads that as non-manifold and
# refuses the part, and it refuses it while `is_watertight` still says yes.
cut_overrun = 1.0
# How far the cutter's own surface may stand off the plan where stations are dropped. A corner
# keeps its stations at this; the flats collapse to their two ends regardless, because there the
# chord and the plan are the same line.
plan_tol = 0.01
# A station counts as show face when the piece's own material reaches this close to the plan.
# Bigger than the mesh's own deviation, far smaller than the shallowest recess that is not
# meant to be fluted (a port chip's seat is 2.0 mm).
face_tol = 0.25


def _plan_frames(plan_at, perimeter, outer):
    """Every across-station on the box's plan: (arc length, point, outward normal)."""
    count = int(round(perimeter / grid_across))
    s = np.arange(count) * (perimeter / count)
    point = np.empty((count, 2))
    normal = np.empty((count, 2))
    for i, si in enumerate(s):
        (px, py), (nx, ny) = plan_at(float(si), outer)
        point[i] = (px, py)
        normal[i] = (nx, ny)
    return s, point, normal


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


def _show_mask(mesh, point, normal, rows):
    """Where the piece has material AT the nominal surface — the show face, and nothing else.

    Read by SECTION rather than by asking about points one at a time: one horizontal cut gives
    the piece's whole outline at that height, and a station is show face when the outline runs
    within `face_tol` of the plan there. An opening has no outline on the plan; a pocket's has
    moved inboard; a piece that has simply ended has none at all."""
    mask = np.zeros((len(point), len(rows)), dtype=bool)
    for j, z in enumerate(rows):
        segments = trimesh.intersections.mesh_plane(
            mesh, plane_normal=np.array([0.0, 0.0, 1.0]),
            plane_origin=np.array([0.0, 0.0, float(z)]))
        pts = _outline(segments, face_tol / 2.0)
        if len(pts) < 3:
            continue
        near = cKDTree(pts).query(point, distance_upper_bound=face_tol)[0]
        mask[:, j] = np.isfinite(near)
    return mask


def _depth_field(s, mask):
    """The inward displacement at every station — the coupon's own expression, with the ramp
    driven by how far the station stands from the nearest edge of the show face.

    ACROSS WRAPS AND ALONG DOES NOT, and both halves of that have to be said out loud or the
    box comes out wrong in a different way each time. The perimeter is a closed loop, so the
    field is tripled in that axis and the middle taken back — otherwise the two ends of the arc
    length would each read as an edge and the box would fade to nothing down a seam that is not
    there. The two ends of the HEIGHT are the opposite case: the bed, the seam a piece ends on,
    the ceiling, all of them real edges — and a distance transform does NOT treat an array's own
    boundary as background, so left alone it measures from there to the nearest opening halfway
    up the wall and reports no edge at all. They are given a row of background to measure to."""
    wide = np.vstack([mask, mask, mask])
    pad = np.pad(wide, ((0, 0), (1, 1)), constant_values=False)
    far = ndimage.distance_transform_edt(pad, sampling=(grid_across, grid_along))
    far = far[len(mask):2 * len(mask), 1:-1]
    along = np.clip(far / flute_rise, 0.0, 1.0)
    fade = along * along * (3.0 - 2.0 * along)
    across = reeding.groove(s, flute_pitch, reeding.flute_width)[:, None]
    return flute_depth * across * fade * mask


def _thin(depth, rows, s, point, normal):
    """Drop the stations that say nothing new.

    The field is CONSTANT ALONG A FLUTE except where it ramps, and a ramp is 5 mm of a 358 mm
    wall — so most rows repeat the one above them exactly, and a mesh drawn through all of them
    is ten million triangles of saying the same thing. Across, the same is true of every stretch
    of perimeter this piece does not carry: the depth is zero the whole height and two columns
    describe it as well as four hundred.

    A row or column is kept when it differs from the last one kept. Nothing is interpolated
    away: every station where the field actually moves is still drawn.

    AND A COLUMN CARRIES THE PLAN AS WELL AS THE FIELD, which is the trap. Dropping a station
    because the DEPTH there is unchanged leaves the cutter's own surface running straight from
    the last kept station to the next — a chord across the plan. Down a flat wall that chord IS
    the plan and costs nothing. Across a corner, or across the long stretch of perimeter a piece
    does not carry, it cuts the corner off and the cutter runs through the INSIDE of the box,
    slicing whatever it meets: a seam lip, an underwall, a boss. Every edge that leaves is one
    four faces share, a slicer refuses the file, and nothing measured in memory can see it.

    So a column is kept when the depth moves OR when dropping it would pull the cutter's surface
    off the plan by more than `plan_tol`. The flats still collapse to their two ends, because
    there a chord and the plan are the same line."""
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
    rows_i = np.array(keep_rows)
    cols_i = np.array(sorted(set(keep_cols)))
    return (depth[np.ix_(cols_i, rows_i)], np.asarray(rows)[rows_i],
            point[cols_i], normal[cols_i])


def _chord_error(point, first, last):
    """How far the plan wanders off the straight line between two stations — what dropping
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


def _cutter(point, normal, rows, depth):
    """The volume between the nominal surface and the fluted one, as one closed mesh — the
    across-axis wraps, so it is a tube, capped at the two heights."""
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

    i, j = np.meshgrid(np.arange(count), np.arange(height - 1), indexing="ij")
    i, j = i.ravel(), j.ravel()
    nxt = ((i + 1) % count) * height + j
    cur = i * height + j
    faces = [quads(cur, cur + 1, nxt + 1, nxt),
             quads(base + cur, base + nxt, base + nxt + 1, base + cur + 1)]
    k = np.arange(count)
    lo, hi = k * height, k * height + height - 1
    lon, hin = ((k + 1) % count) * height, ((k + 1) % count) * height + height - 1
    faces.append(quads(lo, lon, base + lon, base + lo))
    faces.append(quads(hi, base + hi, base + hin, hin))
    mesh = trimesh.Trimesh(vertices=vertices, faces=np.concatenate(faces), process=True)
    if mesh.volume < 0:
        mesh.invert()
    return mesh


def flute(mesh, outer, plan_at, perimeter, pitch, depth_mm, rise_mm):
    """`mesh` with the box's flutes cut into whatever of the show face it carries."""
    global flute_pitch, flute_depth, flute_rise
    flute_pitch, flute_depth, flute_rise = pitch, depth_mm, rise_mm
    lo, hi = mesh.bounds[0][2], mesh.bounds[1][2]
    # OFF THE PIECE'S OWN FACES BY A MARGIN THAT MEANS SOMETHING. A level cut taken ON the top
    # or bottom face is degenerate, so the field's first and last rows stand clear of both.
    rows = np.arange(lo + grid_along, hi - grid_along / 2.0, grid_along)
    if len(rows) < 4:
        return mesh
    s, point, normal = _plan_frames(plan_at, perimeter, outer)
    mask = _show_mask(mesh, point, normal, rows)
    if not mask.any():
        return mesh
    depth = _depth_field(s, mask)
    if depth.max() <= 0.0:
        return mesh
    depth, rows, point, normal = _thin(depth, rows, s, point, normal)
    # AND THE CUTTER IS CAPPED IN AIR, past both ends of the piece. The field is already nothing
    # at the piece's own edges, so these two rows take the same nothing further out and give the
    # boolean two caps that lie on no face of anything.
    rows = np.concatenate([[rows[0] - cut_overrun], rows, [rows[-1] + cut_overrun]])
    depth = np.hstack([depth[:, :1] * 0.0, depth, depth[:, -1:] * 0.0])
    # `check_volume=False` because trimesh's own gate is stricter than the engine's. A piece
    # tessellates to a surface where a handful of edges out of twenty-odd thousand carry four
    # faces rather than two — the solid touching itself along a line, which is a fact about the
    # solid and not about this mesh — and trimesh refuses the whole boolean for it. Manifold
    # takes it, repairs it, and hands back a watertight result; the caller checks that.
    cut = trimesh.boolean.difference(
        [mesh, _cutter(point, normal, rows, depth)], engine="manifold", check_volume=False)
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
