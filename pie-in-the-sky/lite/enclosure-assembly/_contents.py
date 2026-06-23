"""Lite Edition enclosure contents — every internal subsystem packed, in the
Kitchen-edition frame so the same split-half enclosure wraps them.

Coordinate frame: +X right, +Y back, +Z up. Origin at the lower-front-left
corner; floor on Z=0. The -Y face is the FRONT (the user side, carrying the
display facet); +Y is the cabinet BACK.

The reservoir-pockets box plays the Kitchen cold core's role — the one heavy
volume that cannot move, seated on the floor at the BACK, its bag-load doorway
facing the cabinet LEFT (-X) and its two bag-spout exit holes on the +X face. It
sits hard against the left corner braces, opening a strip on its +X side. The
cabinet is NARROW in X and DEEP in Y; the rest sits in the front zone ahead of
the reservoir, with a tall thin column of electronics and rear-panel ports in
that +X strip:

  * Front, on the floor:  the two flavor pump ASSEMBLIES (Kamoer pump + 90 deg
    outlet elbows), laid on their sides, motor cylinders pointing -X into the
    bag-circuit tray's air gaps (lower motor in the floor band beneath the bag,
    upper motor in the bag's mid gap), heads at +X on the short-tray front.
  * Back-right:  the two SHORT trays (bib-gate, nozzle-gate) STACKED into one
    footprint, turned a quarter-turn (shallow in Y), backs on the split. Each tray
    is linear (tees one end, elbows the other); nozzle is flipped end-for-end, the
    small ELBOW ends interleaved (overlap STACK_OVERLAP in Z), the bulky tees at the
    outer ends.
  * Back-left:  the source-select tray stood vertical and turned a quarter-turn,
    its long footprint side along the back wall (wide in X, shallow in Y), back face
    on the split.
  * Left column:  the bag-circuit tray stood vertical, narrow in X, in the strip
    left of the pump motors, back on the source-select front, raised off the floor.
  * Front-right, high:  the hopper funnel (added in the assembly, derived from the
    enclosure) — a narrow-X, deep-Y slot over the short trays.
  * Front-right corner:  the power tray (Mean Well PSU + Wago distribution + ground
    stack, no relay) stood vertical, its -X face on the pump-head +X face, front
    ahead of the bag.
  * Right of the reservoir (the +X strip):  the logic tray stood vertical at the
    strip front, and behind it on the back wall the rear-panel cluster — the
    faucet-inlet stub (turned so its two carb-water bulkheads stack in Z), the two
    umbilical flavor bulkheads, and the C14 mains inlet. The three rear-panel
    parts mount THROUGH the back wall: bodies inboard, ports proud out the back.

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
LOGIC_STEP = _repo / "pie-in-the-sky" / "lite" / "printed-parts" / "electronics" / "logic-tray" / "logic-assembly.step"
# Rear-panel hardware, mounted THROUGH the back wall: the carb-water pass-through
# stub, the two umbilical flavor bulkheads, and the C14 mains inlet.
STUB_STEP = _repo / "pie-in-the-sky" / "lite" / "printed-parts" / "faucet-inlet-stub" / "faucet-inlet-stub.step"
BULKHEAD_STEP = _hw / "reference" / "jg-bulkhead-union" / "jg-bulkhead-union.step"
C14_STEP = _hw / "reference" / "iec-c14-inlet" / "iec-c14-inlet.step"

# --- Packing parameters (free design choices, not measured geometry) ------
# Inset off the -X wall so the floor content clears the bottom corner pods.
X_INSET = 3.0
# The reservoir is inset off the -X wall, just clear of the back-half corner
# braces (full-depth in the ±X corners). Slid hard left like this it opens a
# strip on its +X side — between it and the power tray — for the rear-panel
# cluster (faucet-inlet stub, umbilical bulkheads, C14) and the logic tray.
RES_X_INSET = 15.0
# The four corner cross-pin bosses tuck into the ±X/±Z corners and run in Y
# across the seam. Floor content against a side wall would foul the bottom pods,
# so it is lifted clear of them — the Kitchen `FOAM_LIFT` idiom.
FLOOR_LIFT = 14.0
# Front-zone Y stations. The reservoir is the fixed back anchor (RES_FRONT_Y); the
# split rides just in front of it; the back trays hang off the split. The pumps lie
# at the front on the floor, motors pointing -X into the bag-circuit tray's air gaps.
PUMP_HEAD_X = 164.0        # the pump heads' +X face
PUMP_UPPER_ZMIN = 93.0     # upper pump zmin (its motor in the bag tray's ~z100-150 air gap)
PUMP_TO_STACK_GAP = 1.0    # pump heads to the back-row (bib/nozzle) front (Y)
RES_FRONT_Y = 180.0        # split datum: back trays hang off it, seam rides on it
RES_Y_PULL = 7.0           # reservoir front pulled forward of the datum (-Y); held back
                           # just enough to clear source-select's back fitting at the -X inset
BAG_SOURCE_GAP = 1.0       # bag-circuit back to the source-select front (Y)
BAG_Z_LIFT = 5.0           # bag-circuit raised this far above the floor lift
# The short trays (bib, nozzle) STACK into one footprint at the back-right, turned a
# quarter-turn (rot +90 about Z, shallow in Y), backs on the split. Each tray is
# linear — tees at one end, ELBOWS at the other. bib stands elbows-up (rot +90 about
# Y); nozzle is flipped end-for-end (rot -90 about Y), elbows down onto bib's, the
# small ELBOW ends interleaved, the bulky tees at the outer ends.
SHORT_X_MAX = 178.5        # short-tray stack right edge
SRC_X_INSET = 12.0         # source-select inset off the -X wall
STACK_OVERLAP = 32.0       # nozzle drops this far into bib (Z); elbow ends interleave
RES_TO_SPLIT_GAP = 1.0     # reservoir front behind the split (Y)
POWER_AHEAD_OF_BAG = 2.0   # power-tray front ahead of the bag-circuit front (Y)
# The +X strip, right of the reservoir. The logic tray stands vertical at the
# strip front; the three rear-panel parts seat on the back wall behind it.
PANEL_X_GAP = 1.0          # gap from the reservoir's +X face to the strip contents
BULKHEAD_X = 186.0         # the two umbilical flavor bulkheads, centered here in X
BULKHEAD_ZA = 215.0        # lower flavor bulkhead, center height
BULKHEAD_ZB = 245.0        # upper flavor bulkhead, center height
C14_Z = 150.0              # mains inlet, center height (mid-strip, between stub and bulkheads)

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
LOGIC_COLOR = cq.Color(0.30, 0.45, 0.58)      # teal control tray
PANEL_COLOR = cq.Color(0.55, 0.57, 0.60)      # gray panel hardware (stub + bulkheads)
C14_COLOR = cq.Color(0.22, 0.22, 0.25)        # black mains inlet


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

    # The reservoir is the fixed back anchor; the split rides just in front of it,
    # and the back trays hang off the split (pushed back against the reservoir).
    res_front = RES_FRONT_Y
    split_front = res_front - RES_TO_SPLIT_GAP

    # --- Back-right: bib-gate + nozzle-gate STACKED into one footprint, turned a
    # quarter-turn (rot +90 about Z), backs on the split. bib elbows-up; nozzle
    # flipped end-for-end (rot -90 about Y), its elbow end down onto bib's — the small
    # ELBOW ends interleaved (overlap STACK_OVERLAP in Z), the bulky tees at the
    # outer ends.
    bib = _place(_rot(_rot(_load(TRAY_STEPS["bib-gate"]), (0, 1, 0), 90.0), (0, 0, 1), 90.0),
                 xmax=SHORT_X_MAX, ymax=split_front, zmin=FLOOR_LIFT)
    bibb = bib.BoundingBox()
    noz = _place(_rot(_rot(_load(TRAY_STEPS["nozzle-gate"]), (0, 1, 0), -90.0), (0, 0, 1), 90.0),
                 xmax=SHORT_X_MAX, ymax=split_front, zmin=bibb.zmax - STACK_OVERLAP)
    placed["bib-gate"] = (bib, COLORS["bib-gate"])
    placed["nozzle-gate"] = (noz, COLORS["nozzle-gate"])
    stack_front = min(bibb.ymin, noz.BoundingBox().ymin)   # back-row front

    # --- Back-left: source-select stood vertical and turned a quarter-turn (rot +90
    # about Y, then -90 about Z), its long footprint side along the back wall (wide in
    # X, shallow in Y), back face on the split.
    src = _place(_rot(_rot(_load(TRAY_STEPS["source-select"]), (0, 1, 0), 90.0), (0, 0, 1), -90.0),
                 xmin=SRC_X_INSET, ymax=split_front, zmin=FLOOR_LIFT)
    placed["source-select"] = (src, COLORS["source-select"])

    # --- Left column: bag-circuit stood vertical (rot +90 about Y), narrow in X in
    # the strip left of the pump motors, back BAG_SOURCE_GAP off the source-select
    # front, raised FLOOR_LIFT + BAG_Z_LIFT off the floor.
    bag = _place(_rot(_load(TRAY_STEPS["bag-circuit"]), (0, 1, 0), 90.0),
                 xmin=X_INSET, ymax=src.BoundingBox().ymin - BAG_SOURCE_GAP,
                 zmin=FLOOR_LIFT + BAG_Z_LIFT)
    placed["bag-circuit"] = (bag, COLORS["bag-circuit"])

    # --- Front, on the floor: the two pump ASSEMBLIES (with elbows), laid on their
    # sides, motor CYLINDERS pointing -X into the bag-circuit tray's air gaps, heads
    # at +X. Lower pump on the floor (zmin 0); upper at PUMP_UPPER_ZMIN. Heads
    # PUMP_TO_STACK_GAP off the back-row front. (Orientation: rot +90 Z, then +90 Y to
    # lay the motor along X, then 180 Z to point it -X, head at +X.)
    pump_neg_x = _rot(_rot(_rot(_load(PUMP_STEP), (0, 0, 1), 90.0), (0, 1, 0), 90.0), (0, 0, 1), 180.0)
    pump_back = stack_front - PUMP_TO_STACK_GAP
    pump_lo = _place(pump_neg_x, xmax=PUMP_HEAD_X, ymax=pump_back, zmin=0.0)
    pump_up = _place(pump_neg_x, xmax=PUMP_HEAD_X, ymax=pump_back, zmin=PUMP_UPPER_ZMIN)
    placed["pump-lower"] = (pump_lo, PUMP_COLORS["pump-lower"])
    placed["pump-upper"] = (pump_up, PUMP_COLORS["pump-upper"])

    # --- Reservoir-pockets, doorway facing the cabinet left. Rotate 180 about Z:
    # local +X doorway -> world -X (left); local -X spout exits -> world +X (right).
    # Pulled RES_Y_PULL forward of the datum, its front crossing the seam as an
    # insert; the box back wall follows its (now shallower) back.
    res = _place(_rot(_load(RES_STEP), (0, 0, 1), 180.0),
                 xmin=RES_X_INSET, ymin=res_front - RES_Y_PULL, zmin=0.0)
    placed["reservoir-pockets"] = (res, RES_COLOR)

    # --- Power tray in the front-right corner: stood vertical (rot -90 about Y), its
    # -X face on the pump-head +X face, front POWER_AHEAD_OF_BAG ahead of the
    # bag-circuit front.
    power = _place(_rot(_load(POWER_STEP), (0, 1, 0), -90.0),
                   xmin=PUMP_HEAD_X, ymin=bag.BoundingBox().ymin - POWER_AHEAD_OF_BAG, zmin=FLOOR_LIFT)
    placed["power-tray"] = (power, POWER_COLOR)

    # --- Right of the reservoir: the +X strip it opened. The logic tray is
    # interior — stood vertical (its long axis up Z) at the strip front, just
    # behind the short-tray backs, off the floor pods. The three rear-panel parts
    # mount THROUGH the back wall: each seats its Y=0 face on the reservoir's back
    # (the box's inner +Y wall), body reaching -Y inward, proud end out the back
    # for the Lillium hose / C13 cord / umbilical tubes. They are sized out of the
    # enclosure (enclosure._PANEL_ZONE); only their inboard bodies need to clear.
    back_wall = res.BoundingBox().ymax
    strip_x = res.BoundingBox().xmax + PANEL_X_GAP

    def _on_panel(step, xc, zc):
        """Seat a panel part's Y=0 face on the back wall, centered at (xc, zc)."""
        s = _load(step).translate((0.0, back_wall, 0.0))
        b = s.BoundingBox()
        return s.translate((xc - (b.xmin + b.xmax) / 2.0, 0.0, zc - (b.zmin + b.zmax) / 2.0))

    logic = _place(_rot(_load(LOGIC_STEP), (0, 1, 0), 90.0),
                   xmin=strip_x, ymin=split_front + 1.0, zmin=FLOOR_LIFT)
    placed["logic-assembly"] = (logic, LOGIC_COLOR)

    # Faucet-inlet stub, rot +90 about Y so its two carb-water bulkheads stack in
    # Z (not side-by-side in X) to fit the narrow strip; the flow-meter chain
    # reaches -Y inward, low in the strip.
    stub = _place(_rot(_load(STUB_STEP), (0, 1, 0), 90.0).translate((0.0, back_wall, 0.0)),
                  xmin=strip_x, zmin=FLOOR_LIFT)
    placed["faucet-inlet-stub"] = (stub, PANEL_COLOR)

    # The two umbilical flavor bulkheads, stacked high above the stub. (The
    # carb-water umbilical port is the stub's own OUT bulkhead, not a third here.)
    placed["umbilical-bulkhead-a"] = (_on_panel(BULKHEAD_STEP, BULKHEAD_X, BULKHEAD_ZA), PANEL_COLOR)
    placed["umbilical-bulkhead-b"] = (_on_panel(BULKHEAD_STEP, BULKHEAD_X, BULKHEAD_ZB), PANEL_COLOR)

    # C14 mains inlet, mid-strip, its +X edge flush to the power-tray's +X line.
    c14 = _place(_on_panel(C14_STEP, 0.0, C14_Z), xmax=power.BoundingBox().xmax)
    placed["iec-c14-inlet"] = (c14, C14_COLOR)

    return placed
