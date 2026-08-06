"""Doc-sync driver for hardware/printed-parts/enclosure/README.md and
the source of truth for the enclosure outer dimensions imported by the
isometric drawings.

The numbers are READ OFF THE BOX (`enclosure._dims()`), not re-derived from the
parts it is sized around: the box already computes them from the placed pack and
its own two bounds, and a second derivation here is a second machine's
dimensions in the drawings.

Run: tools/cad-venv/bin/python hardware/printed-parts/enclosure/_enclosure_dimensions.py
"""

import math as _math
import sys
from pathlib import Path

_here = Path(__file__).resolve().parent
sys.path.insert(0, str(next(p for p in _here.parents if p.name == "printed-parts") / "cadlib"))
sys.path.insert(0, str(next(p for p in _here.parents if p.name == "printed-parts") / "cold-core"))
sys.path.insert(0, str(_here / "enclosure-assembly"))
sys.path.insert(0, str(_here / "enclosure"))
sys.path.insert(0, str(next(p for p in _here.parents if (p / "tools" / "docgen").is_dir()) / "tools"))

from _cold_core_interface import (
    foam_shell_outer_height,
    outer_shell_x_length,
    outer_shell_y_length,
)
import _boxes
import _contents
import _lines
import _routing
import scorecard as _scorecard
import enclosure
from docgen import substitute_md


_OUTER = enclosure._dims().outer

# Every authored run, by id, built ONCE — four figures below read a run's length and
# building the pack's centrelines is the expensive half of importing `_lines`.
_RUNS = {r.id: r for r in _lines.build_runs()}


def _run_len(cid: str) -> float:
    """One authored run's developed length, by id.

    A run this file names and `_lines` does not build is DRIFT and not a missing key: the
    id was renamed or the segment was dropped, and the figure it feeds is describing a
    route the machine no longer takes. Say which id and what is there, so that reads as
    the rename it is rather than as a bare StopIteration out of a generator."""
    if cid not in _RUNS:
        raise KeyError(
            f"{cid} is not among the {len(_RUNS)} runs `_lines.build_runs()` returns — "
            f"this file reads a run that has been renamed or dropped, and the README "
            f"figure it feeds is stale. Have: {', '.join(sorted(_RUNS))}")
    return _RUNS[cid].length

# Zone D's ceiling — the top of the condenser standing over the shroud, which is the
# stratum's own height and the last thing under the front column's open space. Read off
# the placed block for the same reason the silhouette is read off the box.
ZONE_D_TOP = _boxes.boxed(_contents.build()["condenser+fan"][0]).zmax

# The one x every cold-core WALL penetration opens on — read off a station rather than
# typed, since the port lane is the shell's and the yaw is the pack's. Any of the seven
# answers: the lane is one bore wide, so the whole field is a single column, and the
# cap conduit that leaves by the top of that same lane stands on it too.
CORE_PORT_X = _contents.foam_shell_port("co2-in")[0][0]

# How far up the wall that column reaches, and the roof it has to stay under. Both
# bodies in Zone D span CORE_PORT_X, so height is what keeps the ports clear of them
# — and only the shroud's roof matters, because the block stands above it. The reading
# is the stations that cross this WALL; the cap conduits open on the lid overhead and
# stand in Zone B's own reckoning.
CORE_PORT_TOP = max(_contents.foam_shell_port(s)[0][2]
                    for s in _contents.foam_shell_stations()
                    if _contents.foam_shell_port(s)[1] == "y-")
SHROUD_ROOF = _boxes.boxed(_contents.build()["compressor-shroud"][0]).zmax

# The appliance's silhouette. WIDTH is the cold core's SHORT axis plus the seam
# machinery's own reach either side — the yaw (`_contents.FOAM_YAW`) is what puts
# that axis across the machine, and it is the whole point of this edition. HEIGHT is
# stated (`enclosure.appliance_height`). DEPTH follows the pack: the core's long axis
# and whatever is packed ahead of it.
APPLIANCE_W = _OUTER[1] - _OUTER[0]
APPLIANCE_D = _OUTER[3] - _OUTER[2]
APPLIANCE_H = _OUTER[5] - _OUTER[4]

# Zone B. The deck's floor is the foam cap's lid — the plane every module and every
# fitting up there stands on — and its ceiling is the box's own. The SeaFlo's crown is
# what the back column's Z seam has to clear, and the piece that seam leaves is what the
# bed gate measures, so both are read off the placed pack rather than restated.
_PACK = _contents.build()
DECK_TOP = _contents.foam_cap_top()
DECK_HEIGHT = enclosure._dims().inner[5] - DECK_TOP
PUMP_CROWN = _boxes.boxed(_PACK["seaflo-pump"][0]).zmax
BACK_Z_SEAM = enclosure._dims().splits[1]
# The back-bottom piece's own height, and what the bed allows it.
BACK_BOTTOM_H = _boxes.boxed(
    enclosure.build_pieces(enclosure._dims(), "enclosure")[0]["back-bottom"].val()).zlen
BED_Z = enclosure.H2C_Z

# Zone C. The manifold's source pair rides at the top of the front column: the crown its
# valves stand to, the minimum the basin overhead owes them and what the column actually leaves
# under it, the port plane its four collets share — which is also the plane the junction's two
# tees and both feeds arrive on — the band it leaves ahead of the core's face, and how far off
# a pair a divider stands. Every one is read off `_contents`' own placement or off the placed
# pack, so the prose cannot drift from the tray.
SRC_CROWN_Z = _contents.source_tray_crown_z()
SRC_HEADROOM = _contents.SOURCE_TRAY_HEADROOM
SRC_HEADROOM_LEFT = _scorecard._solid_gap(_PACK["source-tray-assembly"][0],
                                          _contents.placed_funnel())
SRC_PORT_PLANE = _contents.source_tray_port("V-A-I")[0][2]
SRC_AFT_BAND = _contents.SOURCE_TRAY_AFT_BAND
DIVIDER_REACH = _contents.divider_reach()
# The reach at which the two leans are collinear and each leg is one straight length — the
# offset over the tangent of the collet's own allowance, and the ceiling the solved reach
# sits under.
DIVIDER_STRAIGHT_REACH = ((_contents._tray.pitch - 2.0 * _contents.DIVIDER_OUTLET_X) / 2.0
                          / _math.tan(_math.radians(_contents.FLAVOR_SKEW)))
# The lean is what the bag circuit costs: the reach follows it, Y-E's forward face follows the
# reach, and the stem column follows that. So the prose that spends the pocket behind the front
# wall reads the same number the pose is built from — the collet's own allowance, which is what
# a leg leaving as one straight length leans by.
DIVIDER_LEAN = _contents.FLAVOR_SKEW
DIVIDER_LEG_STRAIGHT = _contents.DIVIDER_LEG_STRAIGHT
# The bag-A junction's own forward face. It stands ACROSS the strip between the pump row and the
# head column, so what puts this face where it is is that strip and not the lean.
BAG_TEE_FRONT_Y = _boxes.boxed(_PACK["tee-y-e"][0]).ymin
BAG_TEE_STRIP = (_boxes.boxed(_PACK["bag-a-tray-assembly"][0]).ymin
                 - _boxes.boxed(_PACK["pump-a"][0]).ymax)
# What the junction costs instead: its two tees stand a `JUNCTION_LEG_LEAD` off the collet
# plane, so their forward face is the whole of the depth the source and selects pairs spend.
JUNCTION_FRONT_Y = _boxes.boxed(_PACK["tee-y-a"][0]).ymin
WBEND = _lines.WBEND
# The pocket between the front wall and the manifold: the cavity's own front to the most
# forward thing the head column puts in the machine, measured over the column's junctions and
# every leg they carry rather than named, so the pocket follows whichever of them reaches
# furthest.
_HEAD_COLUMN = ("fluid-3", "fluid-5", "fluid-6", "fluid-7", "fluid-8",
                "fluid-14", "fluid-15", "fluid-16")
FRONT_POCKET_D = min(
    [_boxes.boxed(_routing.tube(r)).ymin
     for r in _lines.build_runs() if r.id in _HEAD_COLUMN]
    + [_boxes.boxed(_PACK[n][0]).ymin for n in ("tee-y-e",) + _contents.JUNCTION_TEES]
) - enclosure._dims().inner[2]
# The hopper's own fall — spout tip to the collet's plane, the drop fluid-4 is drawn down.
HOPPER_DROP = _contents.funnel_drain()[2] - SRC_PORT_PLANE
# The pairs under it, each one stack pitch down: the pitch itself, the gap it leaves over the
# coils below, the port plane each lower pair's four collets share, and the floor the bottom
# seat has left over the refrigeration stratum's roof.
STACK_PITCH = _contents.tray_stack_pitch()
STACK_GAP_TRAY = _contents.TRAY_STACK_GAP
SEL_PORT_PLANE = _contents.selects_tray_port("V-C-I")[0][2]
BAG_PORT_PLANE = _contents.bag_a_tray_port("V-E-I")[0][2]
COLUMN_FLOOR = _contents.tray_column_floor()
# The lane EAST of that column — the trays' own plate edge to the condenser's intake face, off
# the two faces `_lines` builds the bag line's climb between. It is the one corridor at the
# manifold's height that runs the machine's full depth.
TRAY_EAST_LANE = (_boxes.boxed(_PACK["condenser+fan"][0]).xmin
                  - _boxes.boxed(_PACK["bag-a-tray-assembly"][0]).xmax)
# The margin INSIDE that column, aft of it: the trays' ports reach past the plate they are
# saddled in, so every storey leaves the same band over its own plate and the band runs the
# whole height. `_lines` falls channel B's inlet down it.
COLLET_PROUD = (_boxes.boxed(_PACK["bag-a-tray-assembly"][0]).ymax
                - (_contents.bag_a_tray_pos()[1] + _contents._tray.half_y))
# The bag-A circuit's one line to the cold core's face, and the run that crosses the
# machine corridor.
BAG_LINE_LEN = _run_len("fluid-15")
LOFT_TRAY_PLANE = _contents.bag_b_tray_port("V-H-I")[0][2]
# The two lines that leave the machine, off the nozzle gates at the loft's own port plane.
NOZZLE_A_LEN = _run_len("fluid-18")
NOZZLE_B_LEN = _run_len("fluid-28")
# Reservoir B's DRAW, which is the whole of its line outside the cold core: the climb is
# in the shell's own +Y band and this is the fall off the cap conduit onto the pair.
BAG_B_LINE_LEN = _run_len("fluid-26")


def _rect_union(rects) -> float:
    """Area of a union of axis-aligned rectangles `(a0, a1, b0, b1)`, by coordinate
    compression — exact, and it does not care how the rectangles overlap."""
    if not rects:
        return 0.0
    xs = sorted({v for r in rects for v in r[:2]})
    ys = sorted({v for r in rects for v in r[2:]})
    total = 0.0
    for i in range(len(xs) - 1):
        for j in range(len(ys) - 1):
            cx, cy = (xs[i] + xs[i + 1]) / 2.0, (ys[j] + ys[j + 1]) / 2.0
            if any(r[0] <= cx <= r[1] and r[2] <= cy <= r[3] for r in rects):
                total += (xs[i + 1] - xs[i]) * (ys[j + 1] - ys[j])
    return total


def _intake_shadow():
    """`(face_mm2, shadowed_mm2)` on the condenser's INTAKE — its −X face, the one the air
    crosses the cabinet to reach. Everything upstream of that face throws a shadow on it, and
    this is the union of them: a body by its bounding box, a run by the band each of its legs
    sweeps at its own bore. The box is what `fit.slab` counts a body by; a run's box is mostly
    air, so a run is measured leg by leg instead."""
    cb = _boxes.boxed(_PACK["condenser+fan"][0])
    win = (cb.ymin, cb.ymax, cb.zmin, cb.zmax)

    def clip(a0, a1, b0, b1):
        r = (max(a0, win[0]), min(a1, win[1]), max(b0, win[2]), min(b1, win[3]))
        return r if r[1] > r[0] and r[3] > r[2] else None

    rects = []
    for name, (solid, _c) in _PACK.items():
        if name == "condenser+fan":
            continue
        b = _boxes.boxed(solid)
        if b.xmin >= cb.xmin:                          # downstream of the face
            continue
        r = clip(b.ymin, b.ymax, b.zmin, b.zmax)
        if r:
            rects.append(r)
    for run in _lines.build_runs():
        h = run.diam / 2.0
        if _boxes.boxed(_routing.tube(run)).xmin >= cb.xmin:
            continue
        for p, q in zip(run.pts, run.pts[1:]):
            r = clip(min(p[1], q[1]) - h, max(p[1], q[1]) + h,
                     min(p[2], q[2]) - h, max(p[2], q[2]) + h)
            if r:
                rects.append(r)
    face = (win[1] - win[0]) * (win[3] - win[2])
    return face, _rect_union(rects)


INTAKE_FACE, INTAKE_SHADOW = _intake_shadow()

# The pump lane's own width — the two tees' columns, which are the two rims they were
# pushed onto, so this is the lane and not a pick.
PUMP_LANE_W = (_contents.pump_row_tee_pos("tee-y-c")[0]
               - _contents.pump_row_tee_pos("tee-y-d")[0])
# What the loft's west lane holds, end to end: the bag-B pair's forward face to the
# nozzle-B gate's aft one. The funnel's real skirt bounds the front of it and the two lanes
# the nozzle runs turn on bound the back.
_LOFT_LANE_PLATES = ("bag-b-tray-assembly", "vk-tray-assembly", "nozzle-b-tray-assembly")
_LOFT_LANE_Y = [(_boxes.boxed(_contents.build()[n][0]).ymin,
                 _boxes.boxed(_contents.build()[n][0]).ymax) for n in _LOFT_LANE_PLATES]
LOFT_LANE_LEN = max(hi for _lo, hi in _LOFT_LANE_Y) - min(lo for lo, _hi in _LOFT_LANE_Y)
# What of that lane is PLATE rather than bay, and what the bays between them leave. Read off
# every stand standing in it, so the three figures close on each other and none is typed —
# a plate that joins the lane or leaves it moves all three.
LOFT_TRAY_LEN = sum(hi - lo for lo, hi in _LOFT_LANE_Y)
LOFT_LANE_BAYS = LOFT_LANE_LEN - LOFT_TRAY_LEN
assert LOFT_LANE_BAYS >= 0.0, (
    f"the loft's west lane is {LOFT_LANE_LEN:.2f} mm end to end and the stands in it come to "
    f"{LOFT_TRAY_LEN:.2f} — so two of {', '.join(_LOFT_LANE_PLATES)} overlap in Y, and one of "
    f"them is no longer a stand on this lane")
# How far INSIDE the loft trays' east face Y-F's own column stands. The fitting is aloft of
# the stand rather than off its flank, so this reads as a plan inset off that face and not as
# a standoff from it — `_lines.LOFT_TEE_STANDOFF` is the other half, the air under the tee.
LOFT_TEE_INSET = ((_contents.bag_b_tray_pos()[0] + _contents._tray.half_x)
                  - _contents.aft_lane_x())
# What the bag-B pair actually has ahead of it — the funnel's REAL surface, not its box,
# which is the first of the levers that would open that lane.
BAG_B_FUNNEL = _scorecard._solid_gap(_contents.build()["bag-b-tray-assembly"][0],
                                     _contents.placed_funnel())
# The routed axis, read off the same scorecard the assembly prints rather than kept by hand.
# Both counts are named, because a percentage in prose is always read back as a count and
# the count is the half that goes stale silently.
ROUTED_N = len(_lines.routed_ids())
CONNECTIONS_N = len(_scorecard.load_connections())
ROUTED_PCT = 100.0 * ROUTED_N / CONNECTIONS_N


def main():
    variables = {
        "FOAM_SHELL_X": f"{outer_shell_x_length:.4g}",
        "FOAM_SHELL_Y": f"{outer_shell_y_length:.4g}",
        "FOAM_SHELL_Z": f"{foam_shell_outer_height:.4g}",
        "APPLIANCE_WIDTH": f"{APPLIANCE_W:.4g} mm",
        "APPLIANCE_DEPTH": f"{APPLIANCE_D:.4g} mm",
        "APPLIANCE_HEIGHT": f"{APPLIANCE_H:.4g} mm",
        "ZONE_D_TOP": f"{ZONE_D_TOP:.4g}",
        "CONDENSER_LANE": f"{_contents.CONDENSER_LANE:.4g}",
        "CONDENSER_ACROSS": f"{_contents.CONDENSER_AIRFLOW:.4g}",
        "CONDENSER_STANDING": f"{_contents.CONDENSER_FACE_B:.4g}",
        "STACK_GAP": f"{_contents.STACK_GAP:.4g}",
        # The core's port column, and what it clears. The free length is the pack's
        # own standoff and not a separate measurement — the whole column crosses
        # below the shroud's roof, so every port opens into the machine corridor and
        # casting each bore forward returns exactly this.
        "CORE_PORT_X": f"{CORE_PORT_X:.4g}",
        "CORE_PORT_TOP": f"{CORE_PORT_TOP:.4g}",
        "SHROUD_ROOF": f"{SHROUD_ROOF:.4g}",
        "CORE_PORT_FREE": f"{_contents.MACHINE_CORRIDOR:.4g}",
        # Zone B — the band the quarter turn bought, and the one number it costs.
        "DECK_TOP": f"{DECK_TOP:.4g}",
        "DECK_HEIGHT": f"{DECK_HEIGHT:.4g}",
        "PUMP_CROWN": f"{PUMP_CROWN:.4g}",
        "BACK_Z_SEAM": f"{BACK_Z_SEAM:.4g}",
        "BACK_BOTTOM_H": f"{BACK_BOTTOM_H:.4g}",
        "BED_Z": f"{BED_Z:.4g}",
        "PORT_ROW_Z": f"{_contents.port_row_z():.4g}",
        # Zone C — the manifold's source pair at the top of the front column.
        "SRC_CROWN_Z": f"{SRC_CROWN_Z:.4g}",
        "SRC_HEADROOM": f"{SRC_HEADROOM:.4g}",
        "SRC_HEADROOM_LEFT": f"{SRC_HEADROOM_LEFT:.4g}",
        "SRC_PORT_PLANE": f"{SRC_PORT_PLANE:.4g}",
        "SRC_AFT_BAND": f"{SRC_AFT_BAND:.4g}",
        "DIVIDER_REACH": f"{DIVIDER_REACH:.4g}",
        "DIVIDER_STRAIGHT_REACH": f"{DIVIDER_STRAIGHT_REACH:.4g}",
        "DIVIDER_LEAN": f"{DIVIDER_LEAN:.4g}",
        "DIVIDER_LEG_STRAIGHT": f"{DIVIDER_LEG_STRAIGHT:.4g}",
        "BAG_TEE_FRONT_Y": f"{BAG_TEE_FRONT_Y:.4g}",
        "BAG_TEE_STRIP": f"{BAG_TEE_STRIP:.4g}",
        "JUNCTION_FRONT_Y": f"{JUNCTION_FRONT_Y:.4g}",
        "WBEND": f"{WBEND:.4g}",
        "FRONT_POCKET_D": f"{FRONT_POCKET_D:.4g}",
        "HOPPER_DROP": f"{HOPPER_DROP:.4g}",
        "STACK_PITCH": f"{STACK_PITCH:.4g}",
        "STACK_GAP_TRAY": f"{STACK_GAP_TRAY:.4g}",
        "SEL_PORT_PLANE": f"{SEL_PORT_PLANE:.4g}",
        "BAG_PORT_PLANE": f"{BAG_PORT_PLANE:.4g}",
        "COLUMN_FLOOR": f"{COLUMN_FLOOR:.4g}",
        "TRAY_EAST_LANE": f"{TRAY_EAST_LANE:.4g}",
        "COLLET_PROUD": f"{COLLET_PROUD:.4g}",
        "BAG_LINE_LEN": f"{BAG_LINE_LEN:.4g}",
        "BAG_B_LINE_LEN": f"{BAG_B_LINE_LEN:.4g}",
        "LOFT_TRAY_PLANE": f"{LOFT_TRAY_PLANE:.4g}",
        "NOZZLE_A_LEN": f"{NOZZLE_A_LEN:.4g}",
        "NOZZLE_B_LEN": f"{NOZZLE_B_LEN:.4g}",
        # The pump lane, the loft's over-packed west lane, and what the scorecard scores.
        "PUMP_LANE_W": f"{PUMP_LANE_W:.4g}",
        "LOFT_TRAY_BAY_MM": f"{_contents.AFT_TRAY_BAY:.4g}",
        "LOFT_TEE_INSET": f"{LOFT_TEE_INSET:.4g}",
        "LOFT_LANE_LEN": f"{LOFT_LANE_LEN:.4g}",
        "LOFT_TRAY_LEN": f"{LOFT_TRAY_LEN:.4g}",
        "LOFT_LANE_BAYS": f"{LOFT_LANE_BAYS:.4g}",
        "BAG_B_FUNNEL": f"{BAG_B_FUNNEL:.4g}",
        "ROUTED_PCT": f"{ROUTED_PCT:.2g}",
        "ROUTED_N": f"{ROUTED_N:d}",
        "CONNECTIONS_N": f"{CONNECTIONS_N:d}",
        "INTAKE_FACE_W": f"{_contents.CONDENSER_FACE_A:.4g}",
        "INTAKE_FACE_H": f"{_contents.CONDENSER_FACE_B:.4g}",
        "INTAKE_SHADOW_PCT": f"{100.0 * INTAKE_SHADOW / INTAKE_FACE:.3g}",
        "INTAKE_OPEN_PCT": f"{100.0 * (INTAKE_FACE - INTAKE_SHADOW) / INTAKE_FACE:.3g}",
    }

    substitute_md(
        _here / "README.md",
        variables=variables,
        expected_counts={
            "FOAM_SHELL_X": 1,
            "FOAM_SHELL_Y": 1,
            "FOAM_SHELL_Z": 1,
            "APPLIANCE_WIDTH": 1,
            "APPLIANCE_DEPTH": 1,
            "APPLIANCE_HEIGHT": 1,
            "ZONE_D_TOP": 1,
            "CONDENSER_LANE": 1,
            "CONDENSER_ACROSS": 1,
            "CONDENSER_STANDING": 1,
            "STACK_GAP": 1,
            "CORE_PORT_X": 1,
            "CORE_PORT_TOP": 1,
            "SHROUD_ROOF": 1,
            "CORE_PORT_FREE": 1,
            "DECK_TOP": 1,
            "DECK_HEIGHT": 1,
            "PUMP_CROWN": 1,
            "BACK_Z_SEAM": 1,
            "BACK_BOTTOM_H": 1,
            "BED_Z": 1,
            "PORT_ROW_Z": 2,     # the deck paragraph and the loft lane's aft bound
            "SRC_CROWN_Z": 1,
            "SRC_HEADROOM": 1,
            "SRC_HEADROOM_LEFT": 1,
            "SRC_PORT_PLANE": 1,
            "SRC_AFT_BAND": 2,       # the band both trays' aft collets stand in
            "DIVIDER_REACH": 5,   # Y-A ahead of the source pair, Y-H off bag B's west face twice, the junctions' own paragraph, and the loft-vs-column reading
            "DIVIDER_STRAIGHT_REACH": 1,  # the reach a leg with no corner in it would want
            "DIVIDER_LEAN": 1,       # the lean a leg leaves its collet at
            "DIVIDER_LEG_STRAIGHT": 1,  # the straight that has to survive both a leg's arcs
            "BAG_TEE_FRONT_Y": 2,    # where the bag-A junction's face lands: in that pair's
                                     #   own paragraph, and again in the junctions one, which
                                     #   lists all three forward faces together
            "BAG_TEE_STRIP": 1,      # and the strip it stands across
            "JUNCTION_FRONT_Y": 1,   # and where the source/selects junction's lands
            "FRONT_POCKET_D": 1,     # what the head column leaves between the wall and itself
            "HOPPER_DROP": 1,
            "STACK_PITCH": 1,
            "STACK_GAP_TRAY": 1,
            "SEL_PORT_PLANE": 1,
            "BAG_PORT_PLANE": 1,
            "COLUMN_FLOOR": 1,
            "TRAY_EAST_LANE": 1,
            "COLLET_PROUD": 1,
            "BAG_LINE_LEN": 1,
            "BAG_B_LINE_LEN": 1,
            "LOFT_TRAY_PLANE": 1,
            "NOZZLE_A_LEN": 1,
            "NOZZLE_B_LEN": 1,
            "PUMP_LANE_W": 1,
            "LOFT_TRAY_BAY_MM": 2,   # the bay in the loft paragraph and again in Constraints
            "LOFT_TEE_INSET": 1,
            "LOFT_LANE_LEN": 1,
            "LOFT_TRAY_LEN": 1,
            "LOFT_LANE_BAYS": 1,
            "BAG_B_FUNNEL": 1,
            "ROUTED_PCT": 1,
            "ROUTED_N": 1,
            "CONNECTIONS_N": 1,
            "INTAKE_FACE_W": 1,
            "INTAKE_FACE_H": 1,
            "INTAKE_SHADOW_PCT": 1,
            "INTAKE_OPEN_PCT": 1,
        },
    )
    print("-> README.md")


if __name__ == "__main__":
    main()
