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

  * Right-front void:  the two flavor pump ASSEMBLIES (Kamoer pump + 90 deg outlet
    elbows), laid on their sides with the motor cylinders pointing at the -X wall,
    heads stacked at the void's bottom-right corner. The thin motors reach left
    across the front-left, where only the narrow bag-circuit tray sits.
  * Back-right:  the two SHORT trays (bib-gate, nozzle-gate) STACKED into one
    footprint, their front against the pump backs. Each tray is linear (tees one
    end, elbows the other); nozzle is flipped end-for-end so the small ELBOW ends
    meet and interleave while the bulky tees ride the outer ends. The stack's back
    face sets the split plane.
  * Back-left:  the source-select tray stood vertical and turned a quarter-turn so
    its long footprint side lies along the back wall — wide in X, shallow in Y —
    back face on the split, against the reservoir.
  * Front-left:  the bag-circuit tray stood vertical, narrow in X, dropped into the
    strip left of the pump motors with its front flush to the pump fronts.
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
# Front-zone Y stations. The pumps sit in the right-front void; the bib/nozzle
# stack sits with its front against the pump backs, and the stack's depth sets the
# split plane (the reservoir seats behind that).
PUMP_FRONT_Y = 25.0        # pump front face — also the box front edge (the frontmost content)
PUMP_HEAD_X = 200.0        # the pump heads' +X face (the void's bottom-right corner)
STACK_TO_PUMP_GAP = 1.0    # gap from the pump backs to the short-tray stack front (Y)
STACK_GAP = 2.0            # vertical gap between stacked parts (Z)
# The short trays (bib, nozzle) STACK into one footprint at the back-right, front
# against the pump backs. Each tray is linear — tees at one end, ELBOWS at the
# other. bib stands elbows-up (rot +90 about Y); nozzle is flipped end-for-end
# (rot -90 about Y) so its elbows point DOWN onto bib's, so the small ELBOW ends
# interleave and the bulky tees sit at the outer (top/bottom) ends, clear of each
# other.
SHORT_X = 135.0            # short-tray / funnel column left edge (clear of source-select)
# The source-select tray stands full height; its top-left corner would foul the
# enclosure's rounded top -X/+Z edge (12 mm print-anti-warp round), so it is held
# off the -X wall by that radius. The lower bag-circuit, which never reaches the
# round, still sits hard against the wall at X_INSET.
SRC_X_INSET = 12.0
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

    # --- Right-front void: the two pump ASSEMBLIES (with elbows), laid on their
    # sides so the motor CYLINDERS point at the -X wall — bulky heads at +X, thin
    # motors reaching left. Heads stacked at the void's bottom-right corner; the
    # motors reach left across the (now vacated) front-left, where nothing else
    # sits, so they stay clear. (Orientation: rot +90 Z, then +90 Y to lay the
    # motor along X, then 180 Z to point it -X with the head at +X.)
    pump_neg_x = _rot(_rot(_rot(_load(PUMP_STEP), (0, 0, 1), 90.0), (0, 1, 0), 90.0), (0, 0, 1), 180.0)
    pump_lo = _place(pump_neg_x, xmax=PUMP_HEAD_X, ymin=PUMP_FRONT_Y, zmin=FLOOR_LIFT)
    pb = pump_lo.BoundingBox()
    pump_up = _place(pump_neg_x, xmax=PUMP_HEAD_X, ymin=PUMP_FRONT_Y, zmin=pb.zmax + STACK_GAP)
    placed["pump-lower"] = (pump_lo, PUMP_COLORS["pump-lower"])
    placed["pump-upper"] = (pump_up, PUMP_COLORS["pump-upper"])

    # --- Back-right: bib-gate + nozzle-gate STACKED into one footprint, their
    # front against the pump backs; the stack's back face sets the split plane (and
    # the reservoir seats behind it). bib stands elbows-up; nozzle is flipped
    # end-for-end (rot -90 about Y) so its elbow end points DOWN onto bib's — the
    # small ELBOW ends interleave (overlap STACK_OVERLAP in Z), the bulky tees ride
    # the outer ends clear of each other, and the tower clears the funnel floor.
    bib = _place(_rot(_load(TRAY_STEPS["bib-gate"]), (0, 1, 0), 90.0),
                 xmin=SHORT_X, ymin=pb.ymax + STACK_TO_PUMP_GAP, zmin=FLOOR_LIFT)
    bibb = bib.BoundingBox()
    split_front = bibb.ymax           # the front zone's back face (the split rides here)
    noz = _place(_rot(_load(TRAY_STEPS["nozzle-gate"]), (0, 1, 0), -90.0),
                 xmin=SHORT_X, ymax=split_front, zmin=bibb.zmax - STACK_OVERLAP)
    placed["bib-gate"] = (bib, COLORS["bib-gate"])
    placed["nozzle-gate"] = (noz, COLORS["nozzle-gate"])

    # --- Back-left: source-select stood vertical and turned a quarter-turn (rot
    # +90 about Y to stand it up, then -90 about Z) so its long footprint side runs
    # along the back wall — wide in X, shallow in Y — with its back face on the
    # split, against the reservoir.
    src = _place(_rot(_rot(_load(TRAY_STEPS["source-select"]), (0, 1, 0), 90.0), (0, 0, 1), -90.0),
                 xmin=SRC_X_INSET, ymax=split_front, zmin=FLOOR_LIFT)
    placed["source-select"] = (src, COLORS["source-select"])

    # --- Front-left void: bag-circuit stood vertical (rot +90 about Y), narrow in
    # X so it drops into the strip left of the pump motors, its front flush with the
    # pump fronts (the box front edge).
    bag = _place(_rot(_load(TRAY_STEPS["bag-circuit"]), (0, 1, 0), 90.0),
                 xmin=X_INSET, ymin=PUMP_FRONT_Y, zmin=FLOOR_LIFT)
    placed["bag-circuit"] = (bag, COLORS["bag-circuit"])

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
