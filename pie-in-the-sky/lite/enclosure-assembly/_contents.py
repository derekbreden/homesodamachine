"""Lite Edition enclosure contents — every internal subsystem packed, in the
Kitchen-edition frame so the same split-half enclosure wraps them.

Coordinate frame: +X right, +Y back, +Z up. Origin at the lower-front-left
corner; floor on Z=0. The -Y face is the FRONT (the user side, carrying the
display facet); +Y is the cabinet BACK.

The reservoir-pockets box plays the Kitchen cold core's role — the one heavy
volume that cannot move, seated on the floor at the BACK, its single fully-open
wall (the bag-load doorway) facing the cabinet back (+Y) and its two bag-spout
exit holes on the forward (-Y) face. Everything else fills the voids that
placement leaves, mirroring the Kitchen zone map:

  * Zone A (back-bottom):  reservoir-pockets, on the floor, rotated +90 deg
    about Z so its doorway faces +Y (back) and its spout exits face -Y (front).
    It is the full-height anchor, flush to the -X (left) wall.
  * Zone C (front-top):    the hopper opening + funnel (added in the assembly,
    derived from the enclosure) and, below it, the two flavor pumps standing on
    the floor under the opening.
  * Zone D (front-bottom): the two short valve trays (bib-gate, nozzle-gate)
    stacked flat against the front-left corner, under the display facet, with
    bag-circuit laid flat across the top of the front zone above the pump tops.
  * Zone B (back, right channel): source-select stood vertical in the column to
    the +X of the reservoir (under the hopper), and the electronics shelf in the
    dead strip between the reservoir's +X wall and that column.

The trays keep their native stack pitch where stacked. The display and the
hopper funnel are NOT placed here — like the Kitchen, the enclosure sizes itself
from these contents, then the display facet and the funnel are derived from the
enclosure and seated in `enclosure_assembly.py`.

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
PUMP_STEP = _hw / "reference" / "kamoer-kphm400" / "kamoer-kphm400.step"
RES_STEP = _repo / "pie-in-the-sky" / "lite" / "printed-parts" / "reservoir-pockets" / "reservoir-pockets.step"

# --- Packing parameters (free design choices, not measured geometry) ------
# Reservoir -Y (front) face Y. Seated just behind where the split-plane cross-pin
# bosses and telescoping lip land (the enclosure derives y_joint from the display
# facet), mirroring the Kitchen `boss_to_coldcore` clear gap so the box never
# fouls the seam hardware.
RES_FRONT_Y = 100.0
# Shared right edge: pump-2 and the vertical source-select column both flush to
# it, so the box's +X wall lands one wall outboard of this.
RIGHT_X = 261.0
# Native valve-tray stack pitch (a tray floor lands on the walls below).
TRAY_PITCH = 63.0
# bag-circuit lies flat across the front-zone top; its underside sits just clear
# of the pump tops rather than stacking at the native pitch (which would foul
# them).
BAG_TOP_Z = 128.0
PUMP_FRONT_Y = 8.0         # pump -Y face (leaves the barb face clear of the front wall)
PUMP_GAP = 2.0             # gap between the two side-by-side pumps
ELEC_GAP = 2.0             # gap from the reservoir +X wall to the electronics shelf
# Electronics shelf — consolidated stand-in for the Lite's undesigned 12 V /
# logic / driver stack (ESP32, MCP23017, ULN2803A, L298N, 12 V supply). A solid
# placeholder, like the Kitchen's condenser/SeaFlo boxes, sized to the real
# board clusters packed into the dead +X channel beside the reservoir.
ELEC_DIMS = (32.0, 150.0, 72.0)   # X (into the strip) x Y (depth) x Z (height)

# --- Colors ---------------------------------------------------------------
RES_COLOR = cq.Color(0.60, 0.80, 1.00, 0.28)
COLORS = {
    "source-select": cq.Color(0.45, 0.70, 0.45),  # green
    "bag-circuit":   cq.Color(0.90, 0.66, 0.32),  # amber
    "bib-gate":      cq.Color(0.62, 0.47, 0.82),  # violet
    "nozzle-gate":   cq.Color(0.84, 0.42, 0.42),  # red
}
PUMP_COLORS = {
    "pump-1": cq.Color(0.38, 0.40, 0.44),     # dark slate
    "pump-2": cq.Color(0.56, 0.58, 0.62),     # light slate
}
ELEC_COLOR = cq.Color(0.30, 0.55, 0.45)       # teal placeholder


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

    # --- Zone A: reservoir-pockets, back-bottom, doorway facing the cabinet
    # back. Rotate +90 deg about Z: local +X doorway -> world +Y (back); local
    # -X spout exits -> world -Y (front). Flush to the -X wall, on the floor.
    res = _place(_rot(_load(RES_STEP), (0, 0, 1), 90.0), xmin=0.0, ymin=RES_FRONT_Y, zmin=0.0)
    placed["reservoir-pockets"] = (res, RES_COLOR)

    # --- Zone D: the two short trays stacked flat against the front-left
    # corner (native orientation, long axis along X), under the display facet.
    bib = _place(_load(TRAY_STEPS["bib-gate"]), xmin=0.0, ymin=0.0, zmin=0.0)
    noz = _place(_load(TRAY_STEPS["nozzle-gate"]), xmin=0.0, ymin=0.0, zmin=TRAY_PITCH)
    placed["bib-gate"] = (bib, COLORS["bib-gate"])
    placed["nozzle-gate"] = (noz, COLORS["nozzle-gate"])

    # bag-circuit lies flat across the front-zone top, spanning the width above
    # the pump tops (native orientation; elbows up into the open air below the
    # facet/hopper).
    bag = _place(_load(TRAY_STEPS["bag-circuit"]), xmin=0.0, ymin=0.0, zmin=BAG_TOP_Z)
    placed["bag-circuit"] = (bag, COLORS["bag-circuit"])

    # --- Zone C floor: two bare Kamoer pumps standing tall on the floor in the
    # front-right, side by side along X, under the hopper opening. Barbs face
    # -Y (front) into the open front air.
    pump2 = _place(_load(PUMP_STEP), xmax=RIGHT_X, ymin=PUMP_FRONT_Y, zmin=0.0)
    pump1 = _place(_load(PUMP_STEP), xmax=pump2.BoundingBox().xmin - PUMP_GAP, ymin=PUMP_FRONT_Y, zmin=0.0)
    placed["pump-1"] = (pump1, PUMP_COLORS["pump-1"])
    placed["pump-2"] = (pump2, PUMP_COLORS["pump-2"])

    # --- Zone B: source-select stood vertical (rotate +90 about Y so its long
    # axis runs up Z; footprint 63 x 93), flush to the +X column, under the
    # hopper, front-aligned with the reservoir so its V-B port sits below the
    # funnel spout.
    src = _place(_rot(_load(TRAY_STEPS["source-select"]), (0, 1, 0), 90.0),
                 xmax=RIGHT_X, ymin=RES_FRONT_Y, zmin=0.0)
    placed["source-select"] = (src, COLORS["source-select"])

    # --- Zone B: electronics shelf in the dead strip between the reservoir's
    # +X wall and the source-select column.
    elec = _place(_box(*ELEC_DIMS),
                  xmin=res.BoundingBox().xmax + ELEC_GAP, ymin=RES_FRONT_Y, zmin=0.0)
    placed["electronics"] = (elec, ELEC_COLOR)

    return placed
