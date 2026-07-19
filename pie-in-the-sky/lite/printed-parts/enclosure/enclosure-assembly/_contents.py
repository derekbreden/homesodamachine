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
  * Back-right:  the SHORT tray (nozzle-gate), turned a quarter-turn (shallow in
    Y), back on the split. The tray is linear — tees one end, elbows the other —
    and stands elbows-up on the floor lift.
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
    strip front, and behind it on the back wall a vertical column of rear-panel
    ports — bottom to top: the faucet-inlet stub's two carb-water bulkheads
    (turned so they stack in Z), the two umbilical flavor bulkheads, then the C14
    mains inlet alone at the TOP, above every water port. The three rear-panel
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
PUMP_TO_STACK_GAP = 1.0    # pump heads to the back-row (nozzle-gate) front (Y)
RES_FRONT_Y = 180.0        # split datum: back trays hang off it, seam rides on it
RES_Y_PULL = 7.0           # reservoir front pulled forward of the datum (-Y); held back
                           # just enough to clear source-select's back fitting at the -X inset
BAG_SOURCE_GAP = 1.0       # bag-circuit back to the source-select front (Y)
BAG_Z_LIFT = 5.0           # bag-circuit raised this far above the floor lift
# The short tray (nozzle-gate) sits at the back-right, turned a quarter-turn
# (rot +90 about Z, shallow in Y), back on the split. It is linear — tees at one
# end, ELBOWS at the other — and stands elbows-up (rot +90 about Y) on the floor
# lift, sharing the back band with source-select. Its X is set off source-select's
# +X face, not off a fixed right edge: at the floor lift the two trays sit in the
# same Z band, so the gap to source-select is the binding constraint and the open
# strip is on the right.
SHORT_TO_SRC_GAP = 1.0     # nozzle-gate left face to the source-select right face (X)
SRC_X_INSET = 12.0         # source-select inset off the -X wall
RES_TO_SPLIT_GAP = 1.0     # reservoir front behind the split (Y)
POWER_AHEAD_OF_BAG = 2.0   # power-tray front ahead of the bag-circuit front (Y)
# The +X strip, right of the reservoir. The logic tray stands vertical at the
# strip front; the three rear-panel parts seat on the back wall behind it, their
# ports aligned in one vertical column at PANEL_PORT_X. Up the column: the
# carb-water stub (low), the two umbilical flavor bulkheads, then the C14 mains
# inlet alone at the TOP — mains kept above every water/carb port, so condensate
# off the cold lines and any leak (both run downward) stay clear of it.
PANEL_X_GAP = 1.0          # gap from the reservoir's +X face to the logic tray
PANEL_PORT_X = 189.0       # rear-panel ports aligned on this vertical line
BULKHEAD_ZA = 150.0        # lower umbilical flavor bulkhead, center height
BULKHEAD_ZB = 185.0        # upper umbilical flavor bulkhead, center height
C14_Z = 258.0              # mains inlet, high in the strip — above all water ports
STUB_HALF_PITCH = 49.56    # stub bulkhead offset from its center (faucet_inlet_stub.bulkhead_x)
# Panel parts seat on the back wall's OUTER face, so their barrels pass through the
# wall (body/flange proud outside, retained by the wall). enclosure.py cuts the
# matching holes (back_wall_ports), sized to clear the modeled hardware.
PANEL_WALL = 3.0           # enclosure wall thickness (== enclosure.wall)
BULKHEAD_HOLE_D = 18.0     # clears the jg-bulkhead-union panel barrel (Ø17.14)
C14_HOLE_CLEAR = 0.5       # C14 cutout clearance per side around its body cross-section
C14_LIP_DEPTH = 4.5        # bezel-lip depth behind the C14 flange; seat the lip on the
                           # wall's outer face so the 20.5 body (not the 22.5 lip) is in the hole

# --- Colors ---------------------------------------------------------------
RES_COLOR = cq.Color(0.60, 0.80, 1.00, 0.28)
COLORS = {
    "source-select": cq.Color(0.45, 0.70, 0.45),  # green
    "bag-circuit":   cq.Color(0.90, 0.66, 0.32),  # amber
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

    # --- Back-left: source-select stood vertical and turned a quarter-turn (rot +90
    # about Y, then -90 about Z), its long footprint side along the back wall (wide in
    # X, shallow in Y), back face on the split. It is placed FIRST: sharing the back
    # band's floor lift, it is what the nozzle-gate tray's X stands off.
    src = _place(_rot(_rot(_load(TRAY_STEPS["source-select"]), (0, 1, 0), 90.0), (0, 0, 1), -90.0),
                 xmin=SRC_X_INSET, ymax=split_front, zmin=FLOOR_LIFT)
    placed["source-select"] = (src, COLORS["source-select"])

    # --- Back-right: the nozzle-gate tray, turned a quarter-turn (rot +90 about Z),
    # back on the split, standing elbows-up (rot +90 about Y) on the floor lift, its
    # left face SHORT_TO_SRC_GAP off source-select's right.
    noz = _place(_rot(_rot(_load(TRAY_STEPS["nozzle-gate"]), (0, 1, 0), 90.0), (0, 0, 1), 90.0),
                 xmin=src.BoundingBox().xmax + SHORT_TO_SRC_GAP, ymax=split_front, zmin=FLOOR_LIFT)
    placed["nozzle-gate"] = (noz, COLORS["nozzle-gate"])
    stack_front = noz.BoundingBox().ymin                   # back-row front

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
    # interior — stood vertical (long axis up Z) at the strip front, just behind
    # the short-tray backs, off the floor pods. It tucks under the +X wall the
    # power tray already sets, so it does not push that wall out (enclosure.py
    # excludes it from the +X size; verified to clear the wall and braces).
    res_bb = res.BoundingBox()

    logic = _place(_rot(_load(LOGIC_STEP), (0, 1, 0), 90.0),
                   xmin=res_bb.xmax + PANEL_X_GAP, ymin=split_front + 1.0, zmin=FLOOR_LIFT)
    placed["logic-assembly"] = (logic, LOGIC_COLOR)

    # The three rear-panel parts mount THROUGH the back wall: each seats its Y=0
    # face on the wall's OUTER face, so the barrel passes through the wall (port
    # proud outside for the Lillium hose / C13 cord / umbilical, retained by the
    # wall; far end reaching -Y inboard). Their ports align on one vertical column
    # at PANEL_PORT_X; enclosure.py cuts the matching holes and sizes the box from
    # interior content only (enclosure._PANEL_ZONE).
    panel_seat = res_bb.ymax + PANEL_WALL          # back wall OUTER face

    def _on_panel(step, xc, zc):
        """Seat a panel part's Y=0 face on the wall's outer face, port at (xc, zc)."""
        s = _load(step).translate((0.0, panel_seat, 0.0))
        b = s.BoundingBox()
        return s.translate((xc - (b.xmin + b.xmax) / 2.0, 0.0, zc - (b.zmin + b.zmax) / 2.0))

    # Faucet-inlet stub, rot +90 about Y so its two carb-water bulkheads stack in
    # Z (not side-by-side in X) to fit the narrow strip; lifted off the floor,
    # inline flow-meter chain reaching -Y inboard. Centered in X on the bulkhead
    # axis — the rotated origin (X=0) — NOT the bbox: the meter's wire boss sticks
    # off to one side, so the bbox center sits off the barrels the holes register on.
    stub = _rot(_load(STUB_STEP), (0, 1, 0), 90.0).translate((0.0, panel_seat, 0.0))
    sb = stub.BoundingBox()
    stub = stub.translate((PANEL_PORT_X, 0.0, FLOOR_LIFT - sb.zmin))
    placed["faucet-inlet-stub"] = (stub, PANEL_COLOR)

    # The two umbilical flavor bulkheads, up the column above the stub. (The
    # carb-water umbilical port is the stub's own OUT bulkhead, not a third here.)
    placed["umbilical-bulkhead-a"] = (_on_panel(BULKHEAD_STEP, PANEL_PORT_X, BULKHEAD_ZA), PANEL_COLOR)
    placed["umbilical-bulkhead-b"] = (_on_panel(BULKHEAD_STEP, PANEL_PORT_X, BULKHEAD_ZB), PANEL_COLOR)

    # C14 mains inlet, mid column between the stub and the bulkheads. Seated out by
    # the bezel-lip depth so the snap-in body (not the lip) passes through the hole.
    placed["iec-c14-inlet"] = (
        _on_panel(C14_STEP, PANEL_PORT_X, C14_Z).translate((0.0, C14_LIP_DEPTH, 0.0)),
        C14_COLOR,
    )

    return placed


def back_wall_ports():
    """Through-holes the rear panel needs for the panel-mounted parts, derived
    from their placed positions: (kind, x, z, *size) in world coords — kind
    'round' (a diameter) or 'rect' (x, z size). enclosure.py cuts these through
    the back wall. The faucet-inlet stub contributes its two carb-water bulkheads
    (±STUB_HALF_PITCH about the column axis); the C14 and the two umbilical
    bulkheads are one port each."""
    placed = build()
    # Stub holes register on the bulkhead axis (PANEL_PORT_X, the column), not the
    # stub bbox center — the meter's wire boss offsets the bbox off the barrels.
    s = placed["faucet-inlet-stub"][0].BoundingBox()
    scz = (s.zmin + s.zmax) / 2.0
    holes = [
        ("round", PANEL_PORT_X, scz - STUB_HALF_PITCH, BULKHEAD_HOLE_D),
        ("round", PANEL_PORT_X, scz + STUB_HALF_PITCH, BULKHEAD_HOLE_D),
    ]
    for key in ("umbilical-bulkhead-a", "umbilical-bulkhead-b"):
        b = placed[key][0].BoundingBox()
        holes.append(("round", (b.xmin + b.xmax) / 2.0, (b.zmin + b.zmax) / 2.0, BULKHEAD_HOLE_D))
    # C14: cut to its actual cross-section where it passes through the wall. Its
    # earth-key makes the bezel taller than the body, so the full-bbox center sits
    # above the body center — slicing at the wall finds the true body footprint.
    wall_y0 = placed["reservoir-pockets"][0].BoundingBox().ymax
    slab = cq.Solid.makeBox(1000.0, PANEL_WALL, 1000.0, cq.Vector(-500.0, wall_y0, -500.0))
    cs = placed["iec-c14-inlet"][0].intersect(slab).BoundingBox()
    holes.append(("rect", (cs.xmin + cs.xmax) / 2.0, (cs.zmin + cs.zmax) / 2.0,
                  cs.xlen + 2.0 * C14_HOLE_CLEAR, cs.zlen + 2.0 * C14_HOLE_CLEAR))
    return holes
