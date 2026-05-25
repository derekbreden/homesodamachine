"""Cap-sense sleeve — printed clamshell that wraps a 1/4" OD LLDPE
flavor tube and seats two copper-foil ring electrodes against the
tube wall. See README.md for the sensing principle, clamshell split
rationale, and print orientation."""

import sys
from pathlib import Path

import cadquery as cq

_here = Path(__file__).resolve()
sys.path.insert(
    0,
    str(next(p for p in _here.parents if p.name == "hardware")),
)
sys.path.insert(
    0,
    str(next(p for p in _here.parents if (p / "tools" / "docgen").is_dir()) / "tools"),
)
from _cadq_export import export_step
from docgen import substitute_md, substitute_py_comments


# Tube and bore.
tube_od = 6.35              # 1/4" OD LLDPE flavor tube — [6.35 mm](TUBE_OD)
bore_clearance = 0.05       # radial slip-fit clearance per side
# [3.225 mm](BORE_R) inner bore radius = (tube_od + 2 × bore_clearance) / 2.
bore_radius = (tube_od + 2 * bore_clearance) / 2

wall_thickness = 3.0        # [3 mm](WALL_T) wall — solid clamshell shell around the bore
# [6.225 mm](OUTER_R) sleeve outer radius = bore_radius + wall_thickness.
outer_radius = bore_radius + wall_thickness

# Sleeve axial length budget:
#   2 × [3 mm](GROOVE_W) grooves + [2 mm](GROOVE_GAP) gap = [8 mm](GROOVES_TOTAL_Z) of groove zone,
#   plus ~[4.5 mm](END_ZONE_Z) end zone per side ([1 mm](RIM_MARGIN) rim margin +
#   [2 mm](DOWEL_D) dowel diameter + [1.5 mm](DOWEL_TO_GROOVE) dowel-to-groove clearance).
# [17 mm](SLEEVE_L) hits this with no extra.
sleeve_length = 17.0
sleeve_z_range = (0.0, sleeve_length)

# Two foil-ring grooves on the inner bore, centers [5 mm](GROOVE_PITCH)
# apart axially. Groove depth = one layer at [0.1 mm](LAYER_H) layer
# height — foil tape (~[0.05 mm](FOIL_T) thick) sits in the groove
# with ~[0.05 mm](FOIL_ADHESIVE_ROOM) of adhesive room. At coarser
# layer heights the groove resolves marginally; fall back to sticking
# the foil flush against the un-grooved bore.
groove_depth = 0.1
# [3.325 mm](GROOVE_OUTER_R) groove outer radius = bore_radius + groove_depth.
groove_outer_radius = bore_radius + groove_depth
groove_width_z = 3.0
groove_centers_z = (6.0, 11.0)

# Radial through-wall wire exits, one per groove, on the +x side of
# the +y half only. Sized in y ([2 mm](SLOT_W_Y)) for the wire to
# bend from circumferential (in the groove) to radial (out of the
# slot) without stressing the solder joint; padded in z by
# [0.5 mm](SLOT_Z_PAD) per side so the wire's entry/exit edges don't
# sit at the groove's z corner.
slot_width_y = 2.0
slot_z_padding = 0.5

# Dowel pins at the y=0 cut plane: -y half carries integrated dowels
# that protrude into matching holes on +y. Same cylinder geometry
# defines pin and hole — [1 mm](DOWEL_R) radius, [2.5 mm](DOWEL_L)
# length protruding past the cut plane — so the friction fit is tuned
# by trial. Each half ends carry a dowel inset [2 mm](DOWEL_Z_INSET)
# from the rim.
dowel_radius = 1.0
dowel_length = 2.5
# [4.725 mm](DOWEL_X) dowel X offset = mid-wall, (bore_radius + outer_radius) / 2.
dowel_x_offset = (bore_radius + outer_radius) / 2
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
    growth_y_sign = -dowel_bearing_y_sign
    y_start = -eps * growth_y_sign
    cyl_length = dowel_length + eps if is_bearing else dowel_length + 2 * eps

    cylinders = [
        cq.Solid.makeCylinder(
            dowel_radius, cyl_length,
            pnt=cq.Vector(x_sign * dowel_x_offset, y_start, z),
            dir=cq.Vector(0, float(growth_y_sign), 0),
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

    # Derived auxiliary values referenced by the comments and README.
    # End-zone breakdown per side: rim margin + dowel diameter + dowel-to-groove clearance.
    grooves_total_z = 2 * groove_width_z + (groove_centers_z[1] - groove_centers_z[0] - groove_width_z)
    end_zone_z = (sleeve_length - grooves_total_z) / 2
    rim_margin = dowel_z_inset_from_ends - dowel_radius
    dowel_to_groove = (groove_centers_z[0] - groove_width_z / 2) - (dowel_z_inset_from_ends + dowel_radius)
    groove_pitch = groove_centers_z[1] - groove_centers_z[0]
    groove_gap = groove_pitch - groove_width_z

    variables = {
        # Tube and bore.
        "TUBE_OD": f"{tube_od:g} mm",
        "BORE_R": f"{bore_radius:g} mm",
        "WALL_T": f"{wall_thickness:g} mm",
        "OUTER_R": f"{outer_radius:g} mm",
        # Sleeve length and end-zone budget.
        "SLEEVE_L": f"{sleeve_length:g} mm",
        "GROOVES_TOTAL_Z": f"{grooves_total_z:g} mm",
        "END_ZONE_Z": f"{end_zone_z:g} mm",
        "RIM_MARGIN": f"{rim_margin:g} mm",
        "DOWEL_TO_GROOVE": f"{dowel_to_groove:g} mm",
        # Grooves and foil.
        "GROOVE_W": f"{groove_width_z:g} mm",
        "GROOVE_GAP": f"{groove_gap:g} mm",
        "GROOVE_PITCH": f"{groove_pitch:g} mm",
        "LAYER_H": f"{groove_depth:g} mm",
        "FOIL_T": "0.05 mm",
        "FOIL_ADHESIVE_ROOM": "0.05 mm",
        "GROOVE_OUTER_R": f"{groove_outer_radius:g} mm",
        # Wire exit slots.
        "SLOT_W_Y": f"{slot_width_y:g} mm",
        "SLOT_Z_PAD": f"{slot_z_padding:g} mm",
        # Dowels.
        "DOWEL_R": f"{dowel_radius:g} mm",
        "DOWEL_D": f"{2 * dowel_radius:g} mm",
        "DOWEL_L": f"{dowel_length:g} mm",
        "DOWEL_X": f"{dowel_x_offset:g} mm",
        "DOWEL_Z_INSET": f"{dowel_z_inset_from_ends:g} mm",
    }

    substitute_py_comments(
        Path(__file__),
        variables=variables,
        expected_counts={
            "TUBE_OD": 1,
            "BORE_R": 1,
            "WALL_T": 1,
            "OUTER_R": 1,
            "SLEEVE_L": 1,
            "GROOVES_TOTAL_Z": 1,
            "END_ZONE_Z": 1,
            "RIM_MARGIN": 1,
            "DOWEL_TO_GROOVE": 1,
            "GROOVE_W": 1,
            "GROOVE_GAP": 1,
            "GROOVE_PITCH": 1,
            "LAYER_H": 1,
            "FOIL_T": 1,
            "FOIL_ADHESIVE_ROOM": 1,
            "GROOVE_OUTER_R": 1,
            "SLOT_W_Y": 1,
            "SLOT_Z_PAD": 1,
            "DOWEL_R": 1,
            "DOWEL_D": 1,
            "DOWEL_L": 1,
            "DOWEL_X": 1,
            "DOWEL_Z_INSET": 1,
        },
    )
    print(f"-> {Path(__file__).name}")

    substitute_md(
        here / "README.md",
        variables=variables,
        expected_counts={
            "TUBE_OD": 2,
            "BORE_R": 1,
            "WALL_T": 1,
            "OUTER_R": 1,
            "SLEEVE_L": 2,
            "GROOVES_TOTAL_Z": 2,
            "END_ZONE_Z": 3,
            "RIM_MARGIN": 1,
            "DOWEL_TO_GROOVE": 1,
            "DOWEL_D": 1,
            "GROOVE_W": 3,
            "GROOVE_GAP": 2,
            "GROOVE_PITCH": 1,
            "LAYER_H": 1,
            "FOIL_T": 1,
            "FOIL_ADHESIVE_ROOM": 1,
            "GROOVE_OUTER_R": 1,
            "SLOT_W_Y": 1,
            "SLOT_Z_PAD": 1,
            "DOWEL_R": 1,
            "DOWEL_L": 1,
            "DOWEL_X": 1,
            "DOWEL_Z_INSET": 1,
        },
    )
    print("-> README.md")


if __name__ == "__main__":
    main()
