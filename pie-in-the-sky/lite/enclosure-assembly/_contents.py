"""Lite Edition enclosure contents — every internal subsystem packed, in the
Kitchen-edition frame so the same split-half enclosure wraps them.

Coordinate frame: +X right, +Y back, +Z up. Origin at the lower-front-left
corner; floor on Z=0. The -Y face is the FRONT (the user side, carrying the
display facet); +Y is the cabinet BACK.

The reservoir-pockets box plays the Kitchen cold core's role — the one heavy
volume that cannot move, seated on the floor at the BACK, its single fully-open
wall (the bag-load doorway) facing the cabinet back (+Y) and its two bag-spout
exit holes on the forward (-Y) face. The cabinet is deliberately NARROW in X and
DEEP in Y: nothing stands beside the reservoir except the one part thin enough to
share its +X depth band — the power tray. Everything else packs into the FRONT
zone, ahead of the reservoir:

  * Back band (against the split):  the two LONG-axis trays stood vertical, side
    by side — source-select and bag-circuit — long axis up Z, footprints ~63 mm
    wide so two fit across the narrow box. They sit behind the pump stack.
  * Front-left:  the two flavor pump ASSEMBLIES (Kamoer pump + 90 deg outlet
    elbows), stacked one above the other (turned a quarter-turn so the elbow span
    runs in X, the shallower 72 mm depth in Y), a single narrow footprint.
  * Back-right:  the two SHORT trays (bib-gate, nozzle-gate) STACKED into one
    footprint, pushed back with their backs on the split. Each tray is linear
    (tees one end, elbows the other); nozzle is flipped end-for-end so the small
    ELBOW ends meet and interleave while the bulky tees ride the outer ends — one
    footprint instead of two trays nose-to-tail, opening a void at the right-FRONT.
  * Front-right, high:  the hopper funnel (added in the assembly, derived from the
    enclosure) — a narrow-X, deep-Y slot dropping over the short trays.
  * +X back band:  the power tray (Mean Well PSU + Wago distribution + ground
    stack, no relay) stood vertical beside the reservoir, its 40.5 mm depth all it
    costs in X.

The display and the hopper funnel are NOT placed here — like the Kitchen, the
enclosure sizes itself from these contents, then the display facet and the funnel
are derived from the enclosure and seated in `enclosure_assembly.py`.

The groups never overlap (verified by real solid intersection in
`enclosure.py`'s report). Inter-tray links are tubing (the topology "Tube
Segments" tables); valve and Tee branches point +Z (up) or out the open tray
ends.
"""

from pathlib import Path

import cadquery as cq

_here = Path(__file__).resolve()
_repo = next(p for p in _here.parents if (p / "hardware" / "scripts" / "_cadq_export.py").is_file())
_hw = _repo / "hardware"
_VM = _hw / "printed-parts" / "valve-manifold"

# --- Source STEPs ---------------------------------------------------------
TRAY_STEPS = {
    "source-select": _VM / "source-select-tray" / "source-select-assembly.step",
    "bag-circuit":   _VM / "bag-circuit-tray"   / "bag-circuit-assembly.step",
    "bib-gate":      _VM / "bib-gate-tray"      / "bib-gate-assembly.step",
    "nozzle-gate":   _VM / "nozzle-gate-tray"   / "nozzle-gate-assembly.step",
}
# The flavor pumps as full ASSEMBLIES — the Kamoer KPHM400 with its 90 deg outlet
# elbows — not the bare pump body (the elbows set the real envelope).
PUMP_STEP = _hw / "reference" / "kamoer-kphm400" / "pump-assembly.step"
RES_STEP = _repo / "pie-in-the-sky" / "lite" / "printed-parts" / "reservoir-pockets" / "reservoir-pockets.step"
POWER_STEP = _repo / "pie-in-the-sky" / "lite" / "printed-parts" / "electronics" / "power-tray" / "power-assembly.step"

# --- Packing parameters (free design choices, not measured geometry) ------
# Inset off the -X wall so the floor content clears the bottom corner pods.
X_INSET = 3.0
# The reservoir gets its own slightly larger inset so its full-height -X wall
# clears the back-half corner braces (which run the full depth in the ±X corners,
# reaching a hair inboard of the inner wall).
RES_X_INSET = 6.0
# The four corner cross-pin bosses tuck into the ±X/±Z corners and run in Y
# across the seam. Floor content against a side wall would foul the bottom pods,
# so it is lifted clear of them — the Kitchen `FOAM_LIFT` idiom.
FLOOR_LIFT = 14.0
# Front-zone Y stations. The two pump assemblies stack at the very front; the two
# long trays (source-select, bag-circuit) stand just behind them, their backs on
# the split. Gaps keep the real solids clear.
PUMP_FRONT_Y = 5.0         # pump stack front face
PUMP_TO_TRAY_GAP = 2.5     # gap from the pump stack back to the vertical trays (Y)
STACK_GAP = 2.0            # vertical gap between stacked parts (Z)
TRAY_GAP_X = 3.0           # gap between side-by-side vertical trays (X)
# The short trays (bib, nozzle) STACK into one footprint at the back-right (backs
# on the split), so the void opens at the right-front. Each tray is linear —
# tees at one end, ELBOWS at the other. bib stands elbows-up (rot +90 about Y);
# nozzle is flipped end-for-end (rot -90 about Y) so its elbows point DOWN onto
# bib's, so the small ELBOW ends interleave and the bulky tees sit at the outer
# (top/bottom) ends, clear of each other.
SHORT_X = 135.0            # short-tray / funnel column left edge (clear of bag-circuit)
STACK_OVERLAP = 34.0      # nozzle drops this far into bib — clean elbow-to-elbow interleave
# Reservoir seats behind the front zone; the split falls in the gap between them.
RES_TO_SPLIT_GAP = 8.0     # reservoir front face behind the deepest front tray
# Gap from the reservoir's real +X wall to the power tray beside it.
POWER_GAP_X = 2.0

# --- Colors ---------------------------------------------------------------
RES_COLOR = cq.Color(0.60, 0.80, 1.00, 0.28)
COLORS = {
    "source-select": cq.Color(0.45, 0.70, 0.45),  # green
    "bag-circuit":   cq.Color(0.90, 0.66, 0.32),  # amber
    "bib-gate":      cq.Color(0.62, 0.47, 0.82),  # violet
    "nozzle-gate":   cq.Color(0.84, 0.42, 0.42),  # red
}
PUMP_COLORS = {
    "pump-lower": cq.Color(0.38, 0.40, 0.44),     # dark slate
    "pump-upper": cq.Color(0.56, 0.58, 0.62),     # light slate
}
POWER_COLOR = cq.Color(0.85, 0.78, 0.62)      # PETG tan tray


def _load(path):
    return cq.importers.importStep(str(path)).val()


def _rot(shape, axis, deg):
    return shape.rotate((0, 0, 0), axis, deg)


def _box(dx, dy, dz):
    return cq.Workplane("XY").box(dx, dy, dz, centered=False).val()


def _place(shape, *, xmax=None, xmin=None, ymin=None, ymax=None, zmin=None, zmax=None):
    """Translate so the requested bounding-box references land on targets.
    Unset axes are left where they are."""
    bb = shape.BoundingBox()
    dx = (xmax - bb.xmax) if xmax is not None else (xmin - bb.xmin) if xmin is not None else 0.0
    dy = (ymax - bb.ymax) if ymax is not None else (ymin - bb.ymin) if ymin is not None else 0.0
    dz = (zmax - bb.zmax) if zmax is not None else (zmin - bb.zmin) if zmin is not None else 0.0
    return shape.translate((dx, dy, dz))


def build():
    placed = {}

    # --- Front-left: the two pump ASSEMBLIES (with elbows), stacked. Turned a
    # quarter-turn about Z so the elbow span (89.5 mm) runs in X and the shallower
    # 71.7 mm depth runs in Y, keeping the front zone short.
    pump_lo = _place(_rot(_load(PUMP_STEP), (0, 0, 1), 90.0),
                     xmin=X_INSET, ymin=PUMP_FRONT_Y, zmin=FLOOR_LIFT)
    pb = pump_lo.BoundingBox()
    pump_up = _place(_rot(_load(PUMP_STEP), (0, 0, 1), 90.0),
                     xmin=X_INSET, ymin=PUMP_FRONT_Y, zmin=pb.zmax + STACK_GAP)
    placed["pump-lower"] = (pump_lo, PUMP_COLORS["pump-lower"])
    placed["pump-upper"] = (pump_up, PUMP_COLORS["pump-upper"])

    # --- Back band: source-select + bag-circuit stood vertical (rotate +90 about
    # Y so their long axis runs up Z), side by side behind the pump stack, their
    # back faces on the split line. source-select is the deeper of the two and
    # sets the front-zone depth.
    tray_front = pb.ymax + PUMP_TO_TRAY_GAP
    src = _place(_rot(_load(TRAY_STEPS["source-select"]), (0, 1, 0), 90.0),
                 xmin=X_INSET, ymin=tray_front, zmin=FLOOR_LIFT)
    placed["source-select"] = (src, COLORS["source-select"])
    sb = src.BoundingBox()
    split_front = sb.ymax            # the front zone's back face (the split rides here)
    bag = _place(_rot(_load(TRAY_STEPS["bag-circuit"]), (0, 1, 0), 90.0),
                 xmin=sb.xmax + TRAY_GAP_X, ymax=split_front, zmin=FLOOR_LIFT)
    placed["bag-circuit"] = (bag, COLORS["bag-circuit"])

    # --- Back-right: bib-gate + nozzle-gate STACKED into one footprint, pushed to
    # the back (their backs on the split, touching the reservoir side) so the void
    # opens at the right-FRONT. bib stands elbows-up; nozzle is flipped end-for-end
    # (rot -90 about Y) so its elbow end points DOWN onto bib's — the small ELBOW
    # ends interleave (overlap STACK_OVERLAP in Z), the bulky tees ride the outer
    # ends clear of each other, and the tower clears the funnel floor.
    bib = _place(_rot(_load(TRAY_STEPS["bib-gate"]), (0, 1, 0), 90.0),
                 xmin=SHORT_X, ymax=split_front, zmin=FLOOR_LIFT)
    bibb = bib.BoundingBox()
    noz = _place(_rot(_load(TRAY_STEPS["nozzle-gate"]), (0, 1, 0), -90.0),
                 xmin=SHORT_X, ymax=split_front, zmin=bibb.zmax - STACK_OVERLAP)
    placed["bib-gate"] = (bib, COLORS["bib-gate"])
    placed["nozzle-gate"] = (noz, COLORS["nozzle-gate"])

    # --- Reservoir-pockets, back, doorway facing the cabinet back. Rotate +90
    # about Z: local +X doorway -> world +Y (back); local -X spout exits -> world
    # -Y (front). Seated behind the front zone, the split falling in the gap.
    res_front = split_front + RES_TO_SPLIT_GAP
    res = _place(_rot(_load(RES_STEP), (0, 0, 1), 90.0),
                 xmin=RES_X_INSET, ymin=res_front, zmin=0.0)
    placed["reservoir-pockets"] = (res, RES_COLOR)

    # --- Power tray stood vertical beside the reservoir on +X: rotate -90 about Y
    # so its 134 mm length runs up Z, costing only its 40.5 mm depth in X. Butted
    # to the reservoir's real +X wall (the bbox +X is a high rod-end boss).
    rb = res.BoundingBox()
    res_wall = res.intersect(_box(rb.xlen + 20, rb.ylen + 20, 250)
                             .translate((rb.xmin - 10, rb.ymin - 10, 0))).BoundingBox().xmax
    power = _place(_rot(_load(POWER_STEP), (0, 1, 0), -90.0),
                   xmin=res_wall + POWER_GAP_X, ymin=res_front, zmin=FLOOR_LIFT)
    placed["power-tray"] = (power, POWER_COLOR)

    return placed
