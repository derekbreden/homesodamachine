"""Cap-sense sleeve — printed clamshell that wraps a 1/4" OD LLDPE
tube and seats two copper-foil ring electrodes against the tube wall.
Pairs with an MPR121 capacitive touch controller on the existing I2C
bus to sense liquid presence inside the tube (segment 4, hopper feed
in the manifold; can also live on the BiB-feed segments). The MPR121
reads capacitance between the two foil rings; water in the tube
(~80 dielectric) gives a much larger reading than air (~1).

Two-piece clamshell, split at y=0 along the tube axis. Same pattern
as ../touch-flo-shell/ tube halves: each half has its cut face on the
build plate, so each half prints support-free with the tube axis
lying horizontal. Joined by friction-fit dowel pins at the cut plane.

Asymmetric features:
  - +y half: foil grooves (180° arcs on the inner bore) and wire
             exit slots (radial through-wall, +x side, one per
             groove) — the functional half. Receives dowel HOLES.
  - -y half: plain inner bore — the structural cap. Carries
             integrated dowel PINS that protrude into the +y half.

The foil rings install on +y before assembly; -y stays a plain print
with no fiddly inner features. The 180° foil strips still produce a
field spanning the whole tube interior — a full 360° ring isn't
needed for sensing.

Print orientation: each STEP exports in part coordinates with the cut
face at y=0. In the slicer, rotate -90° about world x to set the cut
face on the build plate; tube axis then runs along the print's y
axis, foil grooves face up. No supports — the inner bore's top half
bridges naturally at this OD.
"""

import sys
from pathlib import Path

import cadquery as cq

sys.path.insert(
    0,
    str(next(p for p in Path(__file__).resolve().parents if p.name == "hardware")),
)
from _cadq_export import export_step


# 1/4" OD LLDPE flavor tube; slip-fit bore.
tube_od = 6.35
bore_clearance = 0.05
bore_radius = (tube_od + 2 * bore_clearance) / 2

wall_thickness = 3.0
outer_radius = bore_radius + wall_thickness

# Minimum length: 8 mm of grooves (3 + 2 gap + 3) + ~4.5 mm of end
# zone per side (1 mm rim margin + 2 mm dowel diameter + 1.5 mm
# dowel-to-groove clearance). 17 mm hits this with no extra.
sleeve_length = 17.0
sleeve_z_range = (0.0, sleeve_length)

# Two foil-ring grooves on the inner bore, 5 mm apart axially.
# Groove depth = one layer at 0.1 mm layer height — foil tape
# (~0.05 mm thick) sits in the groove with ~0.05 mm of adhesive
# room. At coarser layer heights the groove resolves marginally;
# fall back to sticking the foil flush against the un-grooved bore.
groove_depth = 0.1
groove_outer_radius = bore_radius + groove_depth
groove_width_z = 3.0
groove_centers_z = (6.0, 11.0)

# Radial through-wall wire exits, one per groove, on the +x side of
# the +y half only. Sized in y for the wire to bend from
# circumferential (in the groove) to radial (out of the slot)
# without stressing the solder joint; padded in z so the wire's
# entry/exit edges don't sit at the groove's z corner.
slot_width_y = 2.0
slot_z_padding = 0.5

# Dowel pins at the y=0 cut plane: -y half carries integrated dowels
# that protrude into matching holes on +y. Same cylinder geometry
# defines pin and hole, so the friction fit is tuned by trial.
dowel_radius = 1.0
dowel_length = 2.5
dowel_x_offset = (bore_radius + outer_radius) / 2  # mid-wall
dowel_z_inset_from_ends = 2.0
dowel_z_positions = (dowel_z_inset_from_ends, sleeve_length - dowel_z_inset_from_ends)
dowel_bearing_y_sign = -1

eps = 0.01


def annular_extrude(r_outer, r_inner, z_range):
    """Hollow cylinder, axis = z. Concentric circles on the same
    workplane extrude as an annulus via CadQuery's even-odd fill rule."""
    z_min, z_max = z_range
    return (
        cq.Workplane("XY")
        .workplane(offset=z_min)
        .circle(r_outer).circle(r_inner)
        .extrude(z_max - z_min)
    )


def build_full_sleeve():
    """Plain hollow cylinder, tube axis = z."""
    return annular_extrude(outer_radius, bore_radius, sleeve_z_range)


def build_half_space(y_sign):
    """Halfspace box for splitting at y=0. y_sign = +1 keeps y >= 0;
    y_sign = -1 keeps y <= 0."""
    big = 500.0
    y_min = 0.0 if y_sign > 0 else -big
    box = cq.Solid.makeBox(
        2 * big, big, 2 * big,
        pnt=cq.Vector(-big, y_min, -big),
    )
    return cq.Workplane("XY").newObject([box])


def cut_foil_grooves(sleeve):
    """Cut full annular grooves into the bore wall. The cutter is the
    full ring on the pre-split sleeve; +y/-y separation happens later
    via half-space intersection. Cutting the full ring rather than a
    half-ring intersected at y=0 avoids the kernel leaving a paper-
    thin face at the cut plane from coplanar boolean residue."""
    for z_center in groove_centers_z:
        z_range = (z_center - groove_width_z / 2, z_center + groove_width_z / 2)
        sleeve = sleeve.cut(annular_extrude(groove_outer_radius, bore_radius, z_range))
    return sleeve


def cut_wire_exit_slots_pos_y(sleeve):
    """Radial slots through the +x side of the +y half, one per foil
    groove. The slot's y range starts at -eps so the cutter crosses
    y=0 by eps — when the +y half is split off, the slot opens cleanly
    through the cut face with no paper-thin lid at y=0."""
    slot_y_range = (-eps, slot_width_y)
    slot_x_range = (-eps, outer_radius + eps)
    slot_width_x = slot_x_range[1] - slot_x_range[0]
    slot_height_y = slot_y_range[1] - slot_y_range[0]
    slot_height_z = groove_width_z + 2 * slot_z_padding
    slot_center_xy = (sum(slot_x_range) / 2, sum(slot_y_range) / 2)
    for z_center in groove_centers_z:
        slot_z_min = z_center - slot_height_z / 2
        slot = (
            cq.Workplane("XY")
            .workplane(offset=slot_z_min)
            .moveTo(*slot_center_xy)
            .rect(slot_width_x, slot_height_y)
            .extrude(slot_height_z)
        )
        sleeve = sleeve.cut(slot)
    return sleeve


def build_dowel_features(y_sign):
    """Dowel cylinders at the y=0 cut plane, four per half (one near
    each end on each x side). The bearing half UNIONs them in as
    integrated dowels; the other half CUTs them as matching holes.
    Bearing dowel protrudes dowel_length past y=0; matching hole is
    slightly longer (dowel_length + 2*eps) so dowels never bottom
    out before the cut faces seat."""
    is_bearing = (y_sign == dowel_bearing_y_sign)
    # Cylinder always grows from the bearing-half side across y=0;
    # only its length differs (hole gets +eps extra to clear seating).
    direction = -dowel_bearing_y_sign
    y_start = -eps * direction
    cyl_length = dowel_length + eps if is_bearing else dowel_length + 2 * eps

    cylinders = [
        cq.Solid.makeCylinder(
            dowel_radius, cyl_length,
            pnt=cq.Vector(x_sign * dowel_x_offset, y_start, z),
            dir=cq.Vector(0, float(direction), 0),
        )
        for x_sign in (-1, +1)
        for z in dowel_z_positions
    ]
    return cq.Workplane("XY").newObject(cylinders)


def build_pos_y_half():
    """+y half — foil grooves + wire exit slots, dowel HOLES at cut plane."""
    sleeve = build_full_sleeve()
    sleeve = cut_foil_grooves(sleeve)
    sleeve = cut_wire_exit_slots_pos_y(sleeve)
    half = sleeve.intersect(build_half_space(+1), clean=False)
    return half.cut(build_dowel_features(+1), clean=False)


def build_neg_y_half():
    """-y half — same foil grooves as +y (so the assembled bore has
    continuous full-ring grooves), no wire exit slots. Bearing half —
    integrated dowel PINS at the cut plane."""
    sleeve = build_full_sleeve()
    sleeve = cut_foil_grooves(sleeve)
    half = sleeve.intersect(build_half_space(-1), clean=False)
    return half.union(build_dowel_features(-1), clean=False)


def main():
    pos_y = build_pos_y_half()
    neg_y = build_neg_y_half()

    here = Path(__file__).resolve().parent
    export_step(pos_y, str(here / "cap-sense-sleeve-pos-y.step"))
    export_step(neg_y, str(here / "cap-sense-sleeve-neg-y.step"))
    print("-> cap-sense-sleeve-pos-y.step  (+y functional half: grooves, wire slots, dowel HOLES)")
    print("-> cap-sense-sleeve-neg-y.step  (-y structural half: grooves, no slots, dowel PINS)")


if __name__ == "__main__":
    main()
