"""Copper-line plugs — four small PETG pieces that slide down into
the shared ⌀6.5 port in the outer_shell +Y wall and seal the gaps
between (and above) the four pass-throughs that share that port.

Pass-throughs that pierce the +Y outer wall through the shared port,
ordered low → high in Z (see the lowest_copper_z / highest_copper_z /
water_inlet_z / prv_vent_z module constants for the live values):

  • lowest copper  (cold-side evaporator inlet)  at z = hole_shift_from_edge
                                                   + wall_and_floor_thickness
                                                   + below_tank_elbows_height
  • highest copper (warm-side evaporator outlet) at z = foam_shell_outer_height
                                                   − hole_shift_from_edge
                                                   − wall_and_floor_thickness
                                                   − above_tank_elbows_height
  • water inlet                                   at z = foam_shell_outer_height
                                                   − hole_shift_from_edge
  • PRV vent (1/4" LLDPE from prv-shroud cap)     at z = water_inlet_z
                                                   + prv_vent_offset_above_water

The PRV vent line is unpressurized in normal operation — it carries
relief-event discharge from the prv-shroud cavity (see
`../prv-shroud/`) out to the appliance interior. It shares the same
slot + same 1/4" OD tube + same ⌀6.5 slot punch as the other three
pass-throughs.

Four plugs in the stack:
  • copper-plug-lower:  fills the Z span between the lowest-copper
                        and highest-copper pass-throughs.
  • copper-plug-middle: fills the Z span between the highest-copper
                        and water-inlet pass-throughs.
  • copper-plug-upper:  fills the Z span between the water-inlet
                        and PRV-vent pass-throughs.
  • copper-plug-top:    fills the Z span above the PRV vent, up
                        to (just below) the +Z top face of the
                        outer_shell.

Cross-section (looking along −Z; X horizontal, Y vertical) — a
true I-beam: a thin web fills the slot's X range at the wall's Y
range, sandwiched between two full-plug-X-width flanges that sit
immediately above and below the wall:

    ████████████████████      ← top flange (above wall_outer)
         ██████████            ← web (in the wall's Y range, slot's X range)
    ████████████████████      ← bottom flange (below wall_inner)
    ←──── plug X ────→
         ←─ slot ─→

The wall sits in the air gap between the two flanges (at
x = ±slot_half_width_x .. ±plug_half_x_outer, the flange overhang
past the web on each side) when the plug is dropped into the slot.

Built as three boxes (web + top flange + bottom flange) unioned
into a single solid. The web's top face shares a 2D contact patch
with the top flange's bottom face at y = wall_outer (and similarly
with the bottom flange at y = wall_inner), so OCCT merges all three
into one contiguous body.

Plug ends that abut a tube have a half-circle cutout (radius =
tube_clearance_radius) centered on x=0 in the end face and arched
into the plug body, so the plug seats gently around the tube
running through the slot below/above it. The arch is Y-tall enough
to span the full plug Y envelope (y = bottom_flange_inner ..
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
from collections import namedtuple
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

from world_workplane import xz_plane_y_up, WorldWorkplane
from _cadq_export import export_step
from docgen import substitute_py_comments
from _cold_core_interface import (
    make_box,
    wall_and_floor_thickness,
    hole_shift_from_edge,
    below_tank_elbows_height,
    above_tank_elbows_height,
    foam_shell_outer_height,
    outer_shell_y_length,
)

# Slot width in X equals the port's ⌀[6.5 mm](SLOT_W) (matches the punch in
# cut_slot_for_copper_and_water_inlet).
slot_width_x = 6.5
slot_half_width_x = slot_width_x / 2
slot_x_range = (-slot_half_width_x, slot_half_width_x)

# Tube clearance radius at each pass-through. All three pass-throughs
# share the same ⌀[6.5 mm](SLOT_W) slot punch from cut_slot_for_copper_and_water_inlet,
# so the tube clearance circle is tangent to the slot's X edges at the
# pass-through Z.
# [3.25 mm](TUBE_CLEAR_R) — = slot_half_width_x (slot punch is ⌀[6.5 mm](SLOT_W)).
tube_clearance_radius = slot_half_width_x

# Web fills the +Y outer_shell wall's Y range exactly ([2 mm](WALL_T) thick at
# [2 mm](WALL_T) wall); the two flanges sit [1 mm](FLANGE_T) above and [1 mm](FLANGE_T) below it.
# [90.5 mm](WALL_OUTER_Y) — outer face of the +Y outer_shell wall = outer_shell_y_length / 2.
outer_wall_outer_y = outer_shell_y_length / 2
# [88.5 mm](WALL_INNER_Y) — inner face = outer face − wall_and_floor_thickness.
outer_wall_inner_y = outer_wall_outer_y - wall_and_floor_thickness
wall_y_range = (outer_wall_inner_y, outer_wall_outer_y)

# Flange dimensions.
#   flange_x_overhang_per_side: how far each flange extends in X past
#                               the slot on each side (so total plug X
#                               span = slot_width_x + 2 × overhang).
#   flange_y_thickness:         Y thickness of each flange ([1 mm](FLANGE_T) above
#                               the wall for the top flange, [1 mm](FLANGE_T) below
#                               for the bottom).
# Together these form a binder-clip cross-section that grips the wall
# edge: the [2 mm](WALL_T) gap between the two flanges (at the wall's Y range,
# outside the web's X range) is exactly where the wall slides in.
flange_x_overhang_per_side = 1.0
flange_y_thickness = 1.0

# Full plug X envelope. Flanges run the full plug X width; the web
# is narrower, sitting only in the slot's X range.
plug_half_x_outer = slot_half_width_x + flange_x_overhang_per_side
plug_x_range = (-plug_half_x_outer, plug_half_x_outer)

# Full plug Y envelope, including the two flanges.
# [87.5 mm](PLUG_Y_INNER) — bottom flange's inward face = wall inner − flange Y.
plug_y_inner = outer_wall_inner_y - flange_y_thickness
# [91.5 mm](PLUG_Y_OUTER) — top flange's outward face = wall outer + flange Y.
plug_y_outer = outer_wall_outer_y + flange_y_thickness
plug_y_range = (plug_y_inner, plug_y_outer)

top_flange_y_range = (outer_wall_outer_y, plug_y_outer)
bottom_flange_y_range = (plug_y_inner, outer_wall_inner_y)

# Pass-through Z positions (centers).
# [47 mm](LOWEST_COPPER_Z) — cold-side evaporator inlet, measured up from Z=0.
lowest_copper_z = hole_shift_from_edge + wall_and_floor_thickness + below_tank_elbows_height
# [166.4 mm](HIGHEST_COPPER_Z) — warm-side evaporator outlet, measured down from the shell top.
highest_copper_z = foam_shell_outer_height - hole_shift_from_edge - wall_and_floor_thickness - above_tank_elbows_height
# [198.4 mm](WATER_INLET_Z) — water inlet line, hole_shift_from_edge below the shell top.
water_inlet_z = foam_shell_outer_height - hole_shift_from_edge

# PRV vent sits above the water inlet by enough to give both adjacent
# plugs reasonable Z extent (~[8 mm](PRV_OFFSET) each: [198.4 mm](WATER_INLET_Z) → [206.4 mm](PRV_VENT_Z) → [213.4 mm](SHELL_TOP_Z)). The
# LLDPE coming off the prv-shroud cap takes a slight bend to land at
# this Z in the slot, same as the water-inlet tube does for its own
# elbow exit. Above_tank_elbows_height (= [30 mm](TANK_ELBOW_H)) gives ~[15 mm](TOP_ROOM) of room
# between the water inlet and the shell top — split here as [8 mm](PRV_OFFSET) + [7 mm](TOP_PLUG_H).
prv_vent_offset_above_water = 8.0
# [206.4 mm](PRV_VENT_Z) — PRV relief line, prv_vent_offset_above_water above the water inlet.
prv_vent_z = water_inlet_z + prv_vent_offset_above_water
# [7 mm](TOP_PLUG_H) — Z extent of the top plug = shell top − PRV vent Z.
top_plug_height = foam_shell_outer_height - prv_vent_z
# [15 mm](TOP_ROOM) — room between the water inlet and the shell top = PRV offset + top plug height.
top_room_above_water = prv_vent_offset_above_water + top_plug_height

# Plug end faces meet AT the tube pass-through centers. The arch
# cutout at each tube-facing end (radius = tube_clearance_radius)
# accommodates exactly HALF of the adjacent tube: each tube sits with
# its upper half seated inside the plug ABOVE it (in that plug's
# bottom arch) and its lower half seated inside the plug BELOW it
# (in that plug's top arch). Together, three plugs + three split-arch
# pairs fill the slot from lowest_copper_z to the wall top exactly —
# no linear gaps between plugs, the tube IS the gap.
#
# The upper plug's top face is flush with the wall top (z =
# foam_shell_outer_height); the upper plug has no top arch since
# nothing sits above it.
#
# Each PlugSpec records both the Z span the plug fills AND whether each
# Z end has an arch cutout (sitting against a tube) or a flat end (top
# of the stack).  Unified so adding a new plug forces specifying both
# attributes — no risk of one dict gaining a key the other forgets.
PlugSpec = namedtuple("PlugSpec", ["z_range", "arch_bottom", "arch_top"])

plug_specs = {
    "lower": PlugSpec((lowest_copper_z, highest_copper_z), arch_bottom=True, arch_top=True),
    "middle": PlugSpec((highest_copper_z, water_inlet_z), arch_bottom=True, arch_top=True),
    "upper": PlugSpec((water_inlet_z, prv_vent_z), arch_bottom=True, arch_top=True),
    "top": PlugSpec((prv_vent_z, foam_shell_outer_height), arch_bottom=True, arch_top=False),
}

# Razor-edge mitigation for the web at each arched plug end. The
# arch's half-disc (radius = tube_clearance_radius) is tangent to the
# web's outer X edge at (x = ±slot_half_width_x, z = at_z). For Z just
# inside the plug from the arch center, the web survives as a sliver
# of width (slot_half_width_x − sqrt(R² − (z−at_z)²)). That sliver
# narrows to zero at z = at_z, which is a razor-thin edge that FDM
# printers can't resolve.
#
# Solution: don't print web where its sliver is thinner than
# `min_printable_thickness` mm. The web's Z range is inset from each
# arched plug end by `web_arch_buffer`, the Z distance at which the
# arch's X reach has narrowed enough for the web's outer-X sliver to
# be exactly `min_printable_thickness` wide. At the inset Z the web
# starts abruptly with two strips of width `min_printable_thickness`
# at x = ±(slot_half_width_x − min_printable_thickness) .. ±slot_half_width_x;
# both strips grow toward full ±slot_half_width_x width as Z moves
# further from the arch center. Flanges are unchanged — their
# flange_y_thickness-thick × flange_x_overhang_per_side-wide tabs at
# x = ±slot_half_width_x .. ±plug_half_x_outer were already at the
# print-resolution limit at the arch tangent and don't get thinner.
min_printable_thickness = 1.0
# [2.35 mm](WEB_BUFFER) — Z inset from arched plug end where the web outer-X sliver reaches min_printable_thickness.
web_arch_buffer = math.sqrt(
    tube_clearance_radius ** 2
    - (slot_half_width_x - min_printable_thickness) ** 2
)

# Volume cross-check tolerance for the analytical-vs-OCCT comparison.
volume_check_tolerance = 0.01


def build_plug(spec):
    """Single solid plug with the I-beam cross-section described in
    the module docstring, extending spec.z_range in Z. Half-circle
    cutouts (radius = tube_clearance_radius) at the ends marked
    arch_bottom / arch_top; the cutouts span the full Y envelope so
    they pass through both flanges and the web."""
    z_bottom, z_top = spec.z_range

    # Web and top flange share the same Z range, inset from each arched
    # plug end by `web_arch_buffer`. Two reasons combine:
    #   • Web razor edge — see razor-edge note above.
    #   • Top-flange hanging tab — the plug prints XZ-face-down so the
    #     top flange is in the last layers, sitting flange_y_thickness
    #     above the bottom flange across an air gap. At each arched
    #     end the top flange's tab regions plus the inner razor strips
    #     (between arch cut and flange edge) all print mangled.
    # Both fixes collapse to: skip web + top flange in the buffer band
    # at each arched end. Bottom flange keeps its full Z range — those
    # tabs print fine because they're on the print bed.
    web_z_range = (
        z_bottom + (web_arch_buffer if spec.arch_bottom else 0),
        z_top - (web_arch_buffer if spec.arch_top else 0),
    )

    web = make_box(slot_x_range, wall_y_range, web_z_range)
    top_flange = make_box(plug_x_range, top_flange_y_range, web_z_range)
    bottom_flange = make_box(plug_x_range, bottom_flange_y_range, spec.z_range)
    plug = web.union(top_flange).union(bottom_flange)

    # Arch cutter: cylinder centered on the plug's end Z face, spanning
    # the full plug Y envelope so it pierces through both flanges and
    # the web. Only the half inside the plug body removes material —
    # the other half is air outside the end face.
    def arch_cutter(at_z):
        y_min, y_max = plug_y_range
        return (
            WorldWorkplane(xz_plane_y_up)
            .workplane(offset=y_min)
            .moveTo((0, at_z))
            .circle(tube_clearance_radius)
            .extrude(y_max - y_min)
            .unwrap()
        )

    if spec.arch_bottom:
        plug = plug.cut(arch_cutter(z_bottom))
    if spec.arch_top:
        plug = plug.cut(arch_cutter(z_top))

    return plug


def _analytical_volume(spec):
    """Closed-form volume of the plug from its three boxes minus the
    arch cutouts. Used as a cross-check on the OCCT boolean result —
    if they don't agree to within 0.01 mm^3, the union dropped or
    duplicated material somewhere.

    The web, top flange, and bottom flange occupy disjoint Y bands
    (web at wall_inner..wall_outer, top flange at wall_outer..
    wall_outer+1, bottom flange at wall_inner-1..wall_inner), so no
    overlap term is needed — their volumes simply add.

    Bottom-flange Z range = plug Z range (full z_height).
    Web AND top-flange Z range are both inset by `web_arch_buffer`
    at each arched end (razor + hanging-tab fix).

    Arch cutout per arched end: a Y-axis cylinder of radius
    tube_clearance_radius centered at (x=0, z=at_z).  The cut volume
    splits across the three Y bands:
      • Bottom flange (full Z range): half-disc × flange_y_thickness
      • Web AND top flange (Z range only past the buffer):
        (half-disc − buffer cap) × Y-thickness-of-that-band,
        where the buffer cap is the area of the half-disc from
        z=at_z to z=at_z+web_arch_buffer.
    """
    z_bottom, z_top = spec.z_range
    z_height = z_top - z_bottom
    plug_full_x = plug_x_range[1] - plug_x_range[0]
    slot_full_x = slot_x_range[1] - slot_x_range[0]
    web_y_thickness = wall_y_range[1] - wall_y_range[0]

    n_arches = sum([spec.arch_bottom, spec.arch_top])

    web_z_height = z_height - n_arches * web_arch_buffer
    vol_web = slot_full_x * web_y_thickness * web_z_height
    vol_top_flange = plug_full_x * flange_y_thickness * web_z_height
    vol_bot_flange = plug_full_x * flange_y_thickness * z_height

    r = tube_clearance_radius
    b = web_arch_buffer
    half_disc_area = 0.5 * math.pi * r ** 2
    # Area of the half-disc from z=0 to z=b (the "buffer cap" near
    # the diameter — where the web AND top flange are both absent
    # in the new design).
    buffer_cap_area = b * math.sqrt(r ** 2 - b ** 2) + r ** 2 * math.asin(b / r)
    inset_in_arch_area = half_disc_area - buffer_cap_area
    vol_arch_per_end = (
        flange_y_thickness * half_disc_area  # bottom flange (full Z)
        + flange_y_thickness * inset_in_arch_area  # top flange (inset Z)
        + web_y_thickness * inset_in_arch_area  # web (inset Z)
    )
    vol_arch_total = n_arches * vol_arch_per_end

    return vol_web + vol_top_flange + vol_bot_flange - vol_arch_total


def main():
    # Sanity report per plug: count of solids must be 1 (OCCT merged
    # web + 2 flanges into a single contiguous body — no floating
    # flanges); bounding box must match the I-beam X and Y envelope;
    # analytical volume (closed-form from the three boxes minus arch
    # cutouts) must match the OCCT-computed volume to within [0.01 mm³](VOL_TOL).
    for name, spec in plug_specs.items():
        plug = build_plug(spec)
        out = _here / f"copper-plug-{name}.step"
        export_step(plug, str(out))

        solids = plug.solids().vals()
        assert len(solids) == 1, f"plug {name}: expected 1 solid, got {len(solids)}"
        bb = solids[0].BoundingBox()
        vol = solids[0].Volume()
        vol_analytical = _analytical_volume(spec)
        vol_diff = vol - vol_analytical
        z_bottom, z_top = spec.z_range
        print(
            f"-> copper-plug-{name}.step  "
            f"z {z_bottom:.2f} -> {z_top:.2f} (h {z_top - z_bottom:.2f} mm)  "
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
        assert abs(bb.ymin - plug_y_range[0]) < 1e-6 and abs(bb.ymax - plug_y_range[1]) < 1e-6, (
            f"plug {name}: Y bbox {bb.ymin:.4f}..{bb.ymax:.4f} expected "
            f"{plug_y_range[0]:.4f}..{plug_y_range[1]:.4f}"
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
        "SLOT_W": f"{slot_width_x:.4g} mm",
        "FLANGE_T": f"{flange_y_thickness:.4g} mm",
        "PRV_OFFSET": f"{prv_vent_offset_above_water:.4g} mm",
        "VOL_TOL": f"{volume_check_tolerance:.4g} mm³",
        # Derived dimensions.
        "TUBE_CLEAR_R": f"{tube_clearance_radius:.4g} mm",
        "WALL_OUTER_Y": f"{outer_wall_outer_y:.4g} mm",
        "WALL_INNER_Y": f"{outer_wall_inner_y:.4g} mm",
        "PLUG_Y_INNER": f"{plug_y_inner:.4g} mm",
        "PLUG_Y_OUTER": f"{plug_y_outer:.4g} mm",
        "LOWEST_COPPER_Z": f"{lowest_copper_z:.4g} mm",
        "HIGHEST_COPPER_Z": f"{highest_copper_z:.4g} mm",
        "WATER_INLET_Z": f"{water_inlet_z:.4g} mm",
        "PRV_VENT_Z": f"{prv_vent_z:.4g} mm",
        "TOP_PLUG_H": f"{top_plug_height:.4g} mm",
        "TOP_ROOM": f"{top_room_above_water:.4g} mm",
        "WEB_BUFFER": f"{web_arch_buffer:.2f} mm",
        # External references (read-only constants from _cold_core_interface).
        "WALL_T": f"{wall_and_floor_thickness:.4g} mm",
        "TANK_ELBOW_H": f"{above_tank_elbows_height:.4g} mm",
        "SHELL_TOP_Z": f"{foam_shell_outer_height:.4g} mm",
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
            "WALL_OUTER_Y": 1,
            "WALL_INNER_Y": 1,
            "PLUG_Y_INNER": 1,
            "PLUG_Y_OUTER": 1,
            "LOWEST_COPPER_Z": 1,
            "HIGHEST_COPPER_Z": 1,
            "WATER_INLET_Z": 2,
            "PRV_VENT_Z": 2,
            "TOP_PLUG_H": 2,
            "TOP_ROOM": 2,
            "WEB_BUFFER": 1,
            "WALL_T": 3,
            "TANK_ELBOW_H": 1,
            "SHELL_TOP_Z": 1,
        },
    )
    print(f"-> {Path(__file__).name} (self)")


if __name__ == "__main__":
    main()
