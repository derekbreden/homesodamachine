"""
Cap-sense sleeve — printed clamshell that wraps a 1/4" OD LLDPE tube
and seats two copper-foil ring electrodes against the tube wall. Pairs
with an MPR121 capacitive touch controller on the existing I2C bus to
sense liquid presence inside the tube (segment 4, hopper feed in the
manifold; can also live on the BiB-feed segments). The MPR121 reads
the capacitance between the two foil rings; water in the tube (~80
dielectric) gives a much larger reading than air (~1).

FIRST PASS — geometry sketch for review, not a finalized print. The
constants here are starting points; expect them to move after a build.

══════════════════════════════════════════════════════════════
TWO-PIECE CLAMSHELL — split at Y=0 plane (along the tube axis)
══════════════════════════════════════════════════════════════

Same pattern as ../touch-flo-shell/ tube halves: each half has its cut
face on the build plate, so each half prints support-free with the tube
axis lying horizontal across the bed. Joined by friction-fit dowel pins
at the cut plane.

Asymmetric features:
  - +Y half  : foil grooves (180° arcs on the inner bore) and wire
               exit slots (radial through-wall, +X side, one per
               groove) — the FUNCTIONAL half. Receives dowel HOLES.
  - -Y half  : plain inner bore — the structural CAP. Carries integrated
               dowel PINS that protrude into the +Y half.

Why asymmetric:
  - The foil rings are installed on one half before assembly. Putting
    grooves only on +Y means -Y is a plain print with no fiddly
    inner features.
  - Wire exit on one side keeps wire routing clean.
  - The foil ring strips are 180° arcs on +Y; the field still spans
    the whole tube interior, so a complete 360° ring isn't needed
    for sensing.

Print orientation (slicer):
  - Each STEP is exported in part coordinates with the cut face at Y=0.
  - In the slicer, rotate -90° about world X to set the cut face on
    the build plate. After rotation: tube axis runs along the print's
    Y axis, the foil grooves face up.
  - No supports required. The inner bore's top half bridges naturally
    (same situation as the touch-flo-shell tube halves at this OD).

══════════════════════════════════════════════════════════════
INSTALLATION FLOW (for reference; not encoded in this script)
══════════════════════════════════════════════════════════════

  1. Cut two foil-tape strips, each ~10 mm long (≈ half the bore
     circumference at the groove). Bend into a half-ring shape.
  2. Solder one wire to each strip. Conductive adhesive on the tape
     means the solder joint can sit anywhere on the strip.
  3. Stick each strip into one of the two grooves on the +Y half.
     Wires exit through the matching wire-exit slots.
  4. Slip the LLDPE tube into the +Y half's bore.
  5. Press the -Y half on. Dowel pins engage the +Y half's holes.

Regenerate:  tools/cad-venv/bin/python generate_step_cadquery.py
"""

import sys
from pathlib import Path

import cadquery as cq

sys.path.insert(
    0,
    str(next(p for p in Path(__file__).resolve().parents if p.name == "hardware")),
)
from _cadq_export import export_step


# ═══════════════════════════════════════════════════════
# CONSTANTS
# ═══════════════════════════════════════════════════════

# ─── Tube and bore ───
TUBE_OD            = 6.35     # 1/4" OD LLDPE flavor tube
BORE_CLEARANCE     = 0.05     # per side, slip fit
BORE_DIAMETER      = TUBE_OD + 2 * BORE_CLEARANCE
BORE_RADIUS        = BORE_DIAMETER / 2

# ─── Sleeve outer dimensions ───
WALL_THICKNESS     = 3.0
OUTER_RADIUS       = BORE_RADIUS + WALL_THICKNESS
# Minimum length: 8 mm of grooves (3 + 2 gap + 3) + ~4.5 mm of end zone
# per side (1 mm rim margin + 2 mm dowel diameter + 1.5 mm dowel-to-
# groove clearance). 17 mm hits this with no extra. Bump up if a
# specific install needs more grip surface or strain-relief features.
SLEEVE_LENGTH      = 17.0

# ─── Foil grooves on inner bore (+Y half only, 180° arcs) ───
# Two circumferential grooves, 5 mm center-to-center, seat copper foil
# ring electrodes. Groove depth is one layer at 0.1 mm layer height —
# foil tape (~0.05 mm thick) sits in the groove with ~0.05 mm of
# adhesive room. Print at 0.1 mm layer height for the groove to
# resolve cleanly; at coarser layer heights the groove will be
# marginal — fall back to sticking the foil flush against the
# un-grooved bore surface.
GROOVE_DEPTH       = 0.1
GROOVE_BORE_RADIUS = BORE_RADIUS + GROOVE_DEPTH
GROOVE_WIDTH_Z     = 3.0
GROOVE_CENTERS_Z   = (6.0, 11.0)    # 5 mm apart axially, sleeve symmetric

# ─── Wire exit slots (+Y half only, +X side) ───
# Radial through-wall slots, one per groove. Axially aligned with the
# groove plus a small Z padding so the wire can bend from circumferen-
# tial (in the groove) to radial (out of the slot) without sharp
# stress on the solder joint. Slot is offset in +Y by EPS so it lives
# entirely in the +Y half — the -Y half ends up with no slot.
SLOT_WIDTH_Y       = 2.0      # circumferential extent at the outer surface
SLOT_Z_PADDING     = 0.5      # extra Z margin top/bottom of groove

# ─── Dowel pins at the Y=0 cut plane ───
# Same convention as touch-flo-shell. The bearing half (-Y, by sign
# below) carries integrated dowels that protrude across the cut plane
# into the +Y half, which has matching holes. Same cylinder geometry
# is used to UNION the pin and CUT the hole, so friction fit is tuned
# by trial-and-error from one set of dimensions.
DOWEL_R                    = 1.0
DOWEL_LEN                  = 2.5
DOWEL_BEARING_HALF_Y_SIGN  = -1
DOWEL_X_OFFSET             = (BORE_RADIUS + OUTER_RADIUS) / 2   # mid-wall
DOWEL_Z_POSITIONS          = (2.0, SLEEVE_LENGTH - 2.0)         # 2 mm from each end

EPS = 0.01


# ═══════════════════════════════════════════════════════
# GEOMETRY HELPERS
# ═══════════════════════════════════════════════════════


def build_full_sleeve():
    """Plain hollow cylinder: tube axis = Z, length SLEEVE_LENGTH."""
    outer = (
        cq.Workplane("XY")
        .circle(OUTER_RADIUS)
        .extrude(SLEEVE_LENGTH)
    )
    bore = (
        cq.Workplane("XY")
        .circle(BORE_RADIUS)
        .extrude(SLEEVE_LENGTH)
    )
    return outer.cut(bore)


def build_split_box(y_sign):
    """Halfspace box. y_sign = +1: keep Y >= 0. y_sign = -1: keep Y <= 0."""
    big = 500.0
    if y_sign > 0:
        box = cq.Solid.makeBox(
            2 * big, big, 2 * big,
            pnt=cq.Vector(-big, 0.0, -big),
        )
    else:
        box = cq.Solid.makeBox(
            2 * big, big, 2 * big,
            pnt=cq.Vector(-big, -big, -big),
        )
    return cq.Workplane("XY").newObject([box])


def cut_foil_grooves(sleeve):
    """Cut FULL annular grooves into the bore wall. We don't pre-clip to
    the +Y half here: the cutter is the full ring, applied to the full
    pre-split sleeve. The +Y/-Y separation happens later in the build
    functions via half-space intersection. Cutting the full ring rather
    than a half-ring intersected at Y=0 avoids the kernel leaving a
    paper-thin face at the cut plane from coplanar boolean residue."""
    for z_center in GROOVE_CENTERS_Z:
        z_bottom = z_center - GROOVE_WIDTH_Z / 2
        outer = (
            cq.Workplane("XY")
            .workplane(offset=z_bottom)
            .circle(GROOVE_BORE_RADIUS)
            .extrude(GROOVE_WIDTH_Z)
        )
        inner = (
            cq.Workplane("XY")
            .workplane(offset=z_bottom)
            .circle(BORE_RADIUS)
            .extrude(GROOVE_WIDTH_Z)
        )
        annular = outer.cut(inner)
        sleeve = sleeve.cut(annular)
    return sleeve


def cut_wire_exit_slots_pos_y(sleeve):
    """Cut radial slots through the +X side of the +Y half, one per foil
    groove. The slot's Y range extends from -EPS to SLOT_WIDTH_Y so the
    cutter crosses the eventual cut plane (Y=0) by EPS — when the +Y
    half is split off, the slot opens cleanly through the cut face,
    leaving no paper-thin lid at Y=0."""
    slot_y_lo = -EPS
    slot_y_hi = SLOT_WIDTH_Y
    for z_center in GROOVE_CENTERS_Z:
        z_height = GROOVE_WIDTH_Z + 2 * SLOT_Z_PADDING
        z_bottom = z_center - z_height / 2
        slot = (
            cq.Workplane("XY")
            .workplane(offset=z_bottom)
            .moveTo(OUTER_RADIUS / 2, (slot_y_lo + slot_y_hi) / 2)
            .rect(OUTER_RADIUS + 2 * EPS, slot_y_hi - slot_y_lo)
            .extrude(z_height)
        )
        sleeve = sleeve.cut(slot)
    return sleeve


def build_dowel_features(y_sign):
    """Dowel cylinders at the Y=0 cut plane, four per half (one near each
    end on each X side). The bearing half UNIONs them in as integrated
    dowels; the other half CUTs them as matching holes. Both halves use
    the same cylinder geometry — friction fit will be tuned by trial."""
    direction_sign = -DOWEL_BEARING_HALF_Y_SIGN   # +1 if -Y bears dowels
    is_bearing = (y_sign == DOWEL_BEARING_HALF_Y_SIGN)
    if is_bearing:
        # Dowel: from EPS inside the bearing half to DOWEL_LEN past the
        # cut plane (so the protruding length is DOWEL_LEN).
        y_start = -EPS * direction_sign
        length = DOWEL_LEN + EPS
    else:
        # Matching hole: slightly longer (DOWEL_LEN + 2*EPS) so the
        # dowel never bottoms out before the cut faces seat.
        y_start = -EPS * direction_sign
        length = DOWEL_LEN + 2 * EPS

    result = None
    for x_sign in (-1, +1):
        for z in DOWEL_Z_POSITIONS:
            cyl = cq.Solid.makeCylinder(
                DOWEL_R, length,
                pnt=cq.Vector(x_sign * DOWEL_X_OFFSET, y_start, z),
                dir=cq.Vector(0, float(direction_sign), 0),
            )
            wp = cq.Workplane("XY").newObject([cyl])
            result = wp if result is None else result.union(wp)
    return result


def build_pos_y_half():
    """+Y half — foil grooves + wire exit slots, with dowel HOLES at cut plane."""
    sleeve = build_full_sleeve()
    sleeve = cut_foil_grooves(sleeve)
    sleeve = cut_wire_exit_slots_pos_y(sleeve)
    half = sleeve.intersect(build_split_box(+1), clean=False)
    half = half.cut(build_dowel_features(+1), clean=False)
    return half


def build_neg_y_half():
    """-Y half — has the same foil grooves as the +Y half (so the
    assembled bore has continuous full-ring grooves), but no wire exit
    slots. Bearing half — gets integrated dowel PINS at the cut plane."""
    sleeve = build_full_sleeve()
    sleeve = cut_foil_grooves(sleeve)
    half = sleeve.intersect(build_split_box(-1), clean=False)
    half = half.union(build_dowel_features(-1), clean=False)
    return half


# ═══════════════════════════════════════════════════════
# BUILD AND EXPORT
# ═══════════════════════════════════════════════════════


def main():
    pos_y = build_pos_y_half()
    neg_y = build_neg_y_half()

    here = Path(__file__).resolve().parent
    export_step(pos_y, str(here / "cap-sense-sleeve-pos-y.step"))
    export_step(neg_y, str(here / "cap-sense-sleeve-neg-y.step"))
    print("-> cap-sense-sleeve-pos-y.step  (+Y functional half: grooves, wire slots, dowel HOLES)")
    print("-> cap-sense-sleeve-neg-y.step  (-Y structural half: grooves, no slots, dowel PINS)")


if __name__ == "__main__":
    main()
