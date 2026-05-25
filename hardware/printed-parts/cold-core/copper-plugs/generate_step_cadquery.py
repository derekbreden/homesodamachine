"""Copper-line plugs — four small PETG pieces that slide down into
the shared ⌀6.5 port in the outer_shell +Z wall and seal the gaps
between (and above) the four pass-throughs that share that port.

Pass-throughs that pierce the +Z outer wall through the shared port,
ordered low → high in Y:

  • lowest copper  (cold-side evaporator inlet)  at y = hole_shift_from_edge
                                                   + wall_and_floor_thickness
                                                   + below_tank_elbows_height
                                                   = 47.0 mm  (at 2 mm wall)
  • highest copper (warm-side evaporator outlet) at y = foam_shell_outer_height
                                                   − hole_shift_from_edge
                                                   − wall_and_floor_thickness
                                                   − above_tank_elbows_height
                                                   = 166.4 mm
  • water inlet                                   at y = foam_shell_outer_height
                                                   − hole_shift_from_edge
                                                   = 198.4 mm
  • PRV vent (1/4" LLDPE from prv-shroud cap)     at y = water_inlet_y
                                                   + prv_vent_offset_above_water
                                                   = 206.4 mm

The PRV vent line is unpressurized in normal operation — it carries
relief-event discharge from the prv-shroud cavity (see
`../prv-shroud/`) out to the appliance interior. Despite carrying
gas rather than water, it shares the same slot + same 1/4" OD tube
+ same ⌀6.5 slot punch as the other three pass-throughs, so it
participates in the same plug architecture.

Four plugs in the stack:
  • copper-plug-lower:  fills the Y span between the lowest-copper
                        and highest-copper pass-throughs.
  • copper-plug-middle: fills the Y span between the highest-copper
                        and water-inlet pass-throughs.
  • copper-plug-upper:  fills the Y span between the water-inlet
                        and PRV-vent pass-throughs.
  • copper-plug-top:    fills the Y span above the PRV vent, up
                        to (just below) the +Y top face of the
                        outer_shell.

Cross-section (looking along −Y; X horizontal, Z vertical) — a
true I-beam: a thin 2 mm-tall web fills the slot's X range at the
wall's Z range, sandwiched between two 1 mm-tall full-X-width
flanges that sit immediately above and below the wall:

    ████████████████████      ← top flange (full plug X, 1 mm Z;
                                  z = wall_outer .. wall_outer + 1)
         ██████████            ← web (slot X, 2 mm Z;
                                  z = wall_inner .. wall_outer)
    ████████████████████      ← bottom flange (full plug X, 1 mm Z;
                                  z = wall_inner − 1 .. wall_inner)
    ←──── 8.5 mm plug X ────→
         ←─6.5 mm slot─→

The flanges grip the +Z wall edge like a binder clip: the 2 mm Z
air gap between the top and bottom flanges (at x = ±slot_half ..
±plug_half_outer, i.e. the 1 mm of flange overhang past the web on
each side) is exactly where the wall sits when the plug is dropped
into the slot.

Built as three boxes (web + top flange + bottom flange) unioned
into a single solid. The web's top face shares a 2D 6.5 × y_height
contact patch with the top flange's bottom face at z = wall_outer
(and similarly with the bottom flange at z = wall_inner), so OCCT
merges all three into one contiguous body.

Plug ends that abut a tube have a half-circle cutout (diameter =
tube clearance, ⌀6.5) centered on x=0 in the end face and arched
into the plug body, so the plug seats gently around the tube
running through the slot below/above it. The arch is Z-tall enough
to span the full plug Z envelope (z = bottom_flange_inner ..
top_flange_outer), so the flanges don't block tubes from seating.

  • LOWER plug:  arch on BOTTOM (over lowest copper), arch on TOP
                 (under highest copper).
  • MIDDLE plug: arch on BOTTOM (over highest copper), arch on TOP
                 (under water inlet).
  • UPPER plug:  arch on BOTTOM (over water inlet), arch on TOP
                 (under PRV vent).
  • TOP plug:    arch on BOTTOM (over PRV vent), TOP stays FLAT
                 (it's the top end of the stack).
"""

import math
import sys
from pathlib import Path

import cadquery as cq

_here = Path(__file__).resolve().parent
sys.path.insert(0, str(next(p for p in _here.parents if p.name == "printed-parts") / "cadlib"))
sys.path.insert(0, str(next(p for p in _here.parents if p.name == "hardware")))
sys.path.insert(
    0,
    str(next(p for p in _here.parents if (p / "tools" / "docgen").is_dir()) / "tools"),
)
sys.path.insert(0, str(_here.parent))

from world_workplane import xy_plane_z_up
from _cadq_export import export_step
from docgen import substitute_py_comments
from _cold_core_interface import (
    make_box,
    wall_and_floor_thickness,
    hole_shift_from_edge,
    below_tank_elbows_height,
    above_tank_elbows_height,
    foam_shell_outer_height,
    outer_shell_z_length,
)

# Slot width in X equals the port's ⌀[6.5 mm](SLOT_W) (matches the punch in
# cut_slot_for_copper_and_water_inlet).
slot_width_x = 6.5
slot_half_width_x = slot_width_x / 2
slot_x_range = (-slot_half_width_x, slot_half_width_x)

# Tube clearance radius at each pass-through. All three pass-throughs
# share the same ⌀[6.5 mm](SLOT_W) slot punch from cut_slot_for_copper_and_water_inlet,
# so the tube clearance circle is tangent to the slot's X edges at the
# pass-through Y.
# [3.25 mm](TUBE_CLEAR_R) — = slot_half_width_x (slot punch is ⌀[6.5 mm](SLOT_W)).
tube_clearance_radius = slot_half_width_x

# Web fills the +Z outer_shell wall's Z range exactly ([2 mm](WALL_T) thick at
# [2 mm](WALL_T) wall); the two flanges sit [1 mm](FLANGE_T) above and [1 mm](FLANGE_T) below it.
# [90.5 mm](WALL_OUTER_Z) — outer face of the +Z outer_shell wall = outer_shell_z_length / 2.
outer_wall_outer_z = outer_shell_z_length / 2
# [88.5 mm](WALL_INNER_Z) — inner face = outer face − wall_and_floor_thickness.
outer_wall_inner_z = outer_wall_outer_z - wall_and_floor_thickness
wall_z_range = (outer_wall_inner_z, outer_wall_outer_z)

# Flange dimensions.
#   flange_x_overhang_per_side: how far each flange extends in X past
#                               the slot on each side (so total plug X
#                               span = slot_width_x + 2 × overhang).
#   flange_z_thickness:         Z thickness of each flange ([1 mm](FLANGE_T) above
#                               the wall for the top flange, [1 mm](FLANGE_T) below
#                               for the bottom).
# Together these form a binder-clip cross-section that grips the wall
# edge: the [2 mm](WALL_T) gap between the two flanges (at the wall's Z range,
# outside the web's X range) is exactly where the wall slides in.
flange_x_overhang_per_side = 1.0
flange_z_thickness = 1.0

# Full plug X envelope. Flanges run the full plug X width; the web
# is narrower, sitting only in the slot's X range.
plug_half_x_outer = slot_half_width_x + flange_x_overhang_per_side
plug_x_range = (-plug_half_x_outer, plug_half_x_outer)

# Full plug Z envelope, including the two flanges.
# [87.5 mm](PLUG_Z_INNER) — bottom flange's inward face = wall inner − flange Z.
plug_z_inner = outer_wall_inner_z - flange_z_thickness
# [91.5 mm](PLUG_Z_OUTER) — top flange's outward face = wall outer + flange Z.
plug_z_outer = outer_wall_outer_z + flange_z_thickness
plug_z_range = (plug_z_inner, plug_z_outer)

top_flange_z_range = (outer_wall_outer_z, plug_z_outer)
bottom_flange_z_range = (plug_z_inner, outer_wall_inner_z)

# Pass-through Y positions (centers).
# [47 mm](LOWEST_COPPER_Y) — cold-side evaporator inlet, measured up from Y=0.
lowest_copper_y = hole_shift_from_edge + wall_and_floor_thickness + below_tank_elbows_height
# [166.4 mm](HIGHEST_COPPER_Y) — warm-side evaporator outlet, measured down from the shell top.
highest_copper_y = foam_shell_outer_height - hole_shift_from_edge - wall_and_floor_thickness - above_tank_elbows_height
# [198.4 mm](WATER_INLET_Y) — water inlet line, hole_shift_from_edge below the shell top.
water_inlet_y = foam_shell_outer_height - hole_shift_from_edge

# PRV vent sits above the water inlet by enough to give both adjacent
# plugs reasonable Y extent (~[8 mm](PRV_OFFSET) each: [198.4 mm](WATER_INLET_Y) → [206.4 mm](PRV_VENT_Y) → [213.4 mm](SHELL_TOP_Y)). The
# LLDPE coming off the prv-shroud cap takes a slight bend to land at
# this Y in the slot, same as the water-inlet tube does for its own
# elbow exit. Above_tank_elbows_height (= [30 mm](TANK_ELBOW_H)) gives ~[15 mm](TOP_ROOM) of room
# between the water inlet and the shell top — split here as [8 mm](PRV_OFFSET) + [7 mm](TOP_PLUG_H).
prv_vent_offset_above_water = 8.0
# [206.4 mm](PRV_VENT_Y) — PRV relief line, prv_vent_offset_above_water above the water inlet.
prv_vent_y = water_inlet_y + prv_vent_offset_above_water
# [7 mm](TOP_PLUG_H) — Y extent of the top plug = shell top − PRV vent Y.
top_plug_height = foam_shell_outer_height - prv_vent_y
# [15 mm](TOP_ROOM) — room between the water inlet and the shell top = PRV offset + top plug height.
top_room_above_water = prv_vent_offset_above_water + top_plug_height

# Plug end faces meet AT the tube pass-through centers. The arch
# cutout at each tube-facing end (radius = tube_clearance_radius)
# accommodates exactly HALF of the adjacent tube: each tube sits with
# its upper half seated inside the plug ABOVE it (in that plug's
# bottom arch) and its lower half seated inside the plug BELOW it
# (in that plug's top arch). Together, three plugs + three split-arch
# pairs fill the slot from lowest_copper_y to the wall top exactly —
# no linear gaps between plugs, the tube IS the gap.
#
# The upper plug's top face is flush with the wall top (y =
# foam_shell_outer_height); the upper plug has no top arch since
# nothing sits above it.
plug_y_ranges = {
    "lower": (lowest_copper_y, highest_copper_y),
    "middle": (highest_copper_y, water_inlet_y),
    "upper": (water_inlet_y, prv_vent_y),
    "top": (prv_vent_y, foam_shell_outer_height),
}

# Which plug ends get a half-circle arch cutout (sits against a tube).
# True = arch cutout, False = flat end. TOP's top is flat (top of
# the stack); every other end-against-a-tube arches around its tube.
plug_arch_ends = {
    "lower": {"bottom": True, "top": True},
    "middle": {"bottom": True, "top": True},
    "upper": {"bottom": True, "top": True},
    "top": {"bottom": True, "top": False},
}

# Razor-edge mitigation for the web at each arched plug end. The
# arch's half-disc (radius = tube_clearance_radius) is tangent to the
# web's outer X edge at (x = ±slot_half_width_x, y = at_y). For Y just
# inside the plug from the arch center, the web survives as a sliver
# of width (slot_half_width_x − sqrt(R² − (y−at_y)²)). That sliver
# narrows to zero at y = at_y, which is a razor-thin edge that FDM
# printers can't resolve.
#
# Solution: don't print web where its sliver is thinner than
# `min_printable_thickness` mm. The web's Y range is inset from each
# arched plug end by `web_arch_buffer`, the Y distance at which the
# arch's X reach has narrowed enough for the web's outer-X sliver to
# be exactly `min_printable_thickness` wide. At the inset Y the web
# starts abruptly with two strips of width `min_printable_thickness`
# at x = ±(slot_half_width_x − min_printable_thickness) .. ±slot_half_width_x;
# both strips grow toward full ±slot_half_width_x width as Y moves
# further from the arch center. Flanges are unchanged — their
# flange_z_thickness-thick × flange_x_overhang_per_side-wide tabs at
# x = ±slot_half_width_x .. ±plug_half_x_outer were already at the
# print-resolution limit at the arch tangent and don't get thinner.
min_printable_thickness = 1.0
# [2.34521 mm](WEB_BUFFER) — Y inset from arched plug end where the web outer-X sliver reaches min_printable_thickness.
web_arch_buffer = math.sqrt(
    tube_clearance_radius ** 2
    - (slot_half_width_x - min_printable_thickness) ** 2
)

# Volume cross-check tolerance for the analytical-vs-OCCT comparison.
volume_check_tolerance = 0.01


def build_plug(name, y_bottom, y_top):
    """Single solid plug with the I-beam cross-section described in
    the module docstring, extending y_bottom..y_top in Y. Half-
    circle cutouts (radius = tube_clearance_radius) at the ends that
    sit against a tube; the cutouts span the full Z envelope so they
    pass through both flanges and the web."""
    plug_y_range = (y_bottom, y_top)
    arches = plug_arch_ends[name]

    # Web and top flange share the same Y range, inset from each arched
    # plug end by `web_arch_buffer`. Two reasons combine:
    #   • Web razor edge — see razor-edge note above.
    #   • Top-flange hanging tab — the plug prints XY-face-down so the
    #     top flange is in the last layers, sitting flange_z_thickness
    #     above the bottom flange across an air gap. At each arched
    #     end the top flange's tab regions plus the inner razor strips
    #     (between arch cut and flange edge) all print mangled.
    # Both fixes collapse to: skip web + top flange in the buffer band
    # at each arched end. Bottom flange keeps its full Y range — those
    # tabs print fine because they're on the print bed.
    web_y_range = (
        y_bottom + (web_arch_buffer if arches["bottom"] else 0),
        y_top - (web_arch_buffer if arches["top"] else 0),
    )

    web = make_box(slot_x_range, web_y_range, wall_z_range)
    top_flange = make_box(plug_x_range, web_y_range, top_flange_z_range)
    bottom_flange = make_box(plug_x_range, plug_y_range, bottom_flange_z_range)
    plug = web.union(top_flange).union(bottom_flange)

    # Arch cutter: cylinder centered on the plug's end Y face, spanning
    # the full plug Z envelope so it pierces through both flanges and
    # the web. Only the half inside the plug body removes material —
    # the other half is air outside the end face.
    def arch_cutter(at_y):
        z_min, z_max = plug_z_range
        return (
            cq.Workplane(xy_plane_z_up)
            .workplane(offset=z_min)
            .moveTo(0, at_y)
            .circle(tube_clearance_radius)
            .extrude(z_max - z_min)
        )

    if arches["bottom"]:
        plug = plug.cut(arch_cutter(y_bottom))
    if arches["top"]:
        plug = plug.cut(arch_cutter(y_top))

    return plug


def _analytical_volume(name, y_bottom, y_top):
    """Closed-form volume of the plug from its three boxes minus the
    arch cutouts. Used as a cross-check on the OCCT boolean result —
    if they don't agree to within 0.01 mm^3, the union dropped or
    duplicated material somewhere.

    The web, top flange, and bottom flange occupy disjoint Z bands
    (web at wall_inner..wall_outer, top flange at wall_outer..
    wall_outer+1, bottom flange at wall_inner-1..wall_inner), so no
    overlap term is needed — their volumes simply add.

    Bottom-flange Y range = plug Y range (full y_height).
    Web AND top-flange Y range are both inset by `web_arch_buffer`
    at each arched end (razor + hanging-tab fix).

    Arch cutout per arched end: a Z-axis cylinder of radius
    tube_clearance_radius centered at (x=0, y=at_y).  The cut volume
    splits across the three Z bands:
      • Bottom flange (full Y range): half-disc × flange_z_thickness
      • Web AND top flange (Y range only past the buffer):
        (half-disc − buffer cap) × Z-thickness-of-that-band,
        where the buffer cap is the area of the half-disc from
        y=at_y to y=at_y+web_arch_buffer.
    """
    y_height = y_top - y_bottom
    plug_full_x = plug_x_range[1] - plug_x_range[0]
    slot_full_x = slot_x_range[1] - slot_x_range[0]
    web_z_thickness = wall_z_range[1] - wall_z_range[0]

    arches = plug_arch_ends[name]
    n_arches = sum(1 for v in arches.values() if v)

    web_y_height = y_height - n_arches * web_arch_buffer
    vol_web = slot_full_x * web_z_thickness * web_y_height
    vol_top_flange = plug_full_x * flange_z_thickness * web_y_height
    vol_bot_flange = plug_full_x * flange_z_thickness * y_height

    r = tube_clearance_radius
    b = web_arch_buffer
    half_disc_area = 0.5 * math.pi * r ** 2
    # Area of the half-disc from y=0 to y=b (the "buffer cap" near
    # the diameter — where the web AND top flange are both absent
    # in the new design).
    buffer_cap_area = b * math.sqrt(r ** 2 - b ** 2) + r ** 2 * math.asin(b / r)
    inset_in_arch_area = half_disc_area - buffer_cap_area
    vol_arch_per_end = (
        flange_z_thickness * half_disc_area  # bottom flange (full Y)
        + flange_z_thickness * inset_in_arch_area  # top flange (inset Y)
        + web_z_thickness * inset_in_arch_area  # web (inset Y)
    )
    vol_arch_total = n_arches * vol_arch_per_end

    return vol_web + vol_top_flange + vol_bot_flange - vol_arch_total


def main():
    # Sanity report per plug: count of solids must be 1 (OCCT merged
    # web + 2 flanges into a single contiguous body — no floating
    # flanges); bounding box must match the I-beam X and Z envelope;
    # analytical volume (closed-form from the three boxes minus arch
    # cutouts) must match the OCCT-computed volume to within [0.01 mm³](VOL_TOL).
    for name, (y_bottom, y_top) in plug_y_ranges.items():
        plug = build_plug(name, y_bottom, y_top)
        out = _here / f"copper-plug-{name}.step"
        export_step(plug, str(out))

        solids = plug.solids().vals()
        assert len(solids) == 1, f"plug {name}: expected 1 solid, got {len(solids)}"
        bb = solids[0].BoundingBox()
        vol = solids[0].Volume()
        vol_analytical = _analytical_volume(name, y_bottom, y_top)
        vol_diff = vol - vol_analytical
        print(
            f"-> copper-plug-{name}.step  "
            f"y {y_bottom:.2f} -> {y_top:.2f} (h {y_top - y_bottom:.2f} mm)  "
            f"bbox X[{bb.xmin:6.2f}..{bb.xmax:6.2f}] "
            f"Y[{bb.ymin:6.2f}..{bb.ymax:6.2f}] "
            f"Z[{bb.zmin:6.2f}..{bb.zmax:6.2f}]  "
            f"vol {vol:.3f} mm^3  "
            f"analytical {vol_analytical:.3f} mm^3  "
            f"diff {vol_diff:+.4f} mm^3"
        )
        assert abs(bb.xmin - plug_x_range[0]) < 1e-6 and abs(bb.xmax - plug_x_range[1]) < 1e-6, (
            f"plug {name}: X bbox {bb.xmin:.4f}..{bb.xmax:.4f} expected "
            f"{plug_x_range[0]:.4f}..{plug_x_range[1]:.4f}"
        )
        assert abs(bb.zmin - plug_z_range[0]) < 1e-6 and abs(bb.zmax - plug_z_range[1]) < 1e-6, (
            f"plug {name}: Z bbox {bb.zmin:.4f}..{bb.zmax:.4f} expected "
            f"{plug_z_range[0]:.4f}..{plug_z_range[1]:.4f}"
        )
        assert abs(vol_diff) < volume_check_tolerance, (
            f"plug {name}: OCCT volume {vol:.4f} differs from analytical "
            f"{vol_analytical:.4f} by {vol_diff:+.4f} mm^3 "
            f"(> {volume_check_tolerance} tolerance)"
        )

    # Short names scoped to this part. Units live inside the value so
    # the script controls them — change a unit in source and every
    # dynamic-comment marker follows.
    variables = {
        # Local design choices.
        "SLOT_W": f"{slot_width_x:g} mm",
        "FLANGE_T": f"{flange_z_thickness:g} mm",
        "PRV_OFFSET": f"{prv_vent_offset_above_water:g} mm",
        "VOL_TOL": f"{volume_check_tolerance:g} mm³",
        # Derived dimensions.
        "TUBE_CLEAR_R": f"{tube_clearance_radius:g} mm",
        "WALL_OUTER_Z": f"{outer_wall_outer_z:g} mm",
        "WALL_INNER_Z": f"{outer_wall_inner_z:g} mm",
        "PLUG_Z_INNER": f"{plug_z_inner:g} mm",
        "PLUG_Z_OUTER": f"{plug_z_outer:g} mm",
        "LOWEST_COPPER_Y": f"{lowest_copper_y:g} mm",
        "HIGHEST_COPPER_Y": f"{highest_copper_y:g} mm",
        "WATER_INLET_Y": f"{water_inlet_y:g} mm",
        "PRV_VENT_Y": f"{prv_vent_y:g} mm",
        "TOP_PLUG_H": f"{top_plug_height:g} mm",
        "TOP_ROOM": f"{top_room_above_water:g} mm",
        "WEB_BUFFER": f"{web_arch_buffer:g} mm",
        # External references (read-only constants from _cold_core_interface).
        "WALL_T": f"{wall_and_floor_thickness:g} mm",
        "TANK_ELBOW_H": f"{above_tank_elbows_height:g} mm",
        "SHELL_TOP_Y": f"{foam_shell_outer_height:g} mm",
    }
    substitute_py_comments(
        Path(__file__),
        variables=variables,
        expected_counts={
            "SLOT_W": 3,
            "FLANGE_T": 4,
            "PRV_OFFSET": 2,
            "VOL_TOL": 1,
            "TUBE_CLEAR_R": 1,
            "WALL_OUTER_Z": 1,
            "WALL_INNER_Z": 1,
            "PLUG_Z_INNER": 1,
            "PLUG_Z_OUTER": 1,
            "LOWEST_COPPER_Y": 1,
            "HIGHEST_COPPER_Y": 1,
            "WATER_INLET_Y": 2,
            "PRV_VENT_Y": 2,
            "TOP_PLUG_H": 2,
            "TOP_ROOM": 2,
            "WEB_BUFFER": 1,
            "WALL_T": 3,
            "TANK_ELBOW_H": 1,
            "SHELL_TOP_Y": 1,
        },
    )
    print("-> generate_step_cadquery.py (self)")


if __name__ == "__main__":
    main()
