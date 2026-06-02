"""Copper-line plugs — four small PETG pieces that slide down into
the shared ⌀6.5 port in the outer_shell +Y wall and seal the gaps
between (and above) the four pass-throughs that share that port.

Pass-throughs that pierce the +Y outer wall through the shared port,
ordered low → high in Z:

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

# Slot width in X equals the port's ⌀[6.5 mm](SLOT_W) punch in
# cut_slot_for_copper_and_water_inlet.
slot_width_x = 6.5
slot_half_width_x = slot_width_x / 2
slot_x_range = (-slot_half_width_x, slot_half_width_x)

# Tube clearance circle is tangent to the slot's ⌀[6.5 mm](SLOT_W) X edges
# at each pass-through Z.
tube_clearance_radius = slot_half_width_x  # [3.25 mm](TUBE_CLEAR_R)

# Web fills the +Y outer_shell wall's Y range exactly ([2 mm](WALL_T) thick at
# [2 mm](WALL_T) wall); the two flanges sit [1 mm](FLANGE_T) above and [1 mm](FLANGE_T) below it.
# [90.5 mm](WALL_OUTER_Y) — outer face of the +Y outer_shell wall.
outer_wall_outer_y = outer_shell_y_length / 2
# [88.5 mm](WALL_INNER_Y) — inner face of the +Y outer_shell wall.
outer_wall_inner_y = outer_wall_outer_y - wall_and_floor_thickness
wall_y_range = (outer_wall_inner_y, outer_wall_outer_y)

# The [2 mm](WALL_T) gap between the two flanges, at the wall's Y range
# and outside the web's X range, is where the +Y wall seats.
flange_x_overhang_per_side = 1.0
flange_y_thickness = 1.0

# Flanges run the full plug X width; the web sits only in the slot's X range.
plug_half_x_outer = slot_half_width_x + flange_x_overhang_per_side
plug_x_range = (-plug_half_x_outer, plug_half_x_outer)

# [87.5 mm](PLUG_Y_INNER) — bottom flange's inward face.
plug_y_inner = outer_wall_inner_y - flange_y_thickness
# [91.5 mm](PLUG_Y_OUTER) — top flange's outward face.
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

# PRV vent above the water inlet: [198.4 mm](WATER_INLET_Z) → [206.4 mm](PRV_VENT_Z) → [213.4 mm](SHELL_TOP_Z).
# The LLDPE off the prv-shroud cap bends to land at this Z in the slot.
# [15 mm](TOP_ROOM) of room between the water inlet and the shell top
# ([30 mm](TANK_ELBOW_H) above_tank_elbows_height), as [8 mm](PRV_OFFSET) + [7 mm](TOP_PLUG_H).
prv_vent_offset_above_water = 8.0
# [206.4 mm](PRV_VENT_Z) — PRV relief line.
prv_vent_z = water_inlet_z + prv_vent_offset_above_water
# [7 mm](TOP_PLUG_H) — Z extent of the top plug.
top_plug_height = foam_shell_outer_height - prv_vent_z
# [15 mm](TOP_ROOM) — room between the water inlet and the shell top.
top_room_above_water = prv_vent_offset_above_water + top_plug_height

# Plug end faces meet AT the tube pass-through centers. The arch
# cutout at each tube-facing end (radius = tube_clearance_radius)
# holds exactly HALF of the adjacent tube: the plug ABOVE a tube seats
# its upper half (in that plug's bottom arch), the plug BELOW seats its
# lower half (in that plug's top arch). The plugs tile the slot from
# lowest_copper_z to the wall top with no linear gaps — the tube IS the gap.
PlugSpec = namedtuple("PlugSpec", ["z_range", "arch_bottom", "arch_top"])

plug_specs = {
    "lower": PlugSpec((lowest_copper_z, highest_copper_z), arch_bottom=True, arch_top=True),
    "middle": PlugSpec((highest_copper_z, water_inlet_z), arch_bottom=True, arch_top=True),
    "upper": PlugSpec((water_inlet_z, prv_vent_z), arch_bottom=True, arch_top=True),
    "top": PlugSpec((prv_vent_z, foam_shell_outer_height), arch_bottom=True, arch_top=False),
}

# The arch's half-disc (radius = tube_clearance_radius) is tangent to
# the web's outer X edge at (x = ±slot_half_width_x, z = at_z), so the
# web's outer-X sliver narrows to zero at z = at_z. The web is inset
# from each arched end by web_arch_buffer so that sliver is never
# thinner than min_printable_thickness.
min_printable_thickness = 1.0
# [2.35 mm](WEB_BUFFER) — Z inset where the web's outer-X sliver reaches min_printable_thickness.
web_arch_buffer = math.sqrt(
    tube_clearance_radius ** 2
    - (slot_half_width_x - min_printable_thickness) ** 2
)

volume_check_tolerance = 0.01  # [0.01 mm³](VOL_TOL)


def build_plug(spec):
    """Single I-beam plug over spec.z_range, with full-Y-envelope arch
    cutouts at the ends marked arch_bottom / arch_top."""
    z_bottom, z_top = spec.z_range

    # Web and top flange are inset by web_arch_buffer at each arched end;
    # the bottom flange spans the full z_range.
    web_z_range = (
        z_bottom + (web_arch_buffer if spec.arch_bottom else 0),
        z_top - (web_arch_buffer if spec.arch_top else 0),
    )

    web = make_box(slot_x_range, wall_y_range, web_z_range)
    top_flange = make_box(plug_x_range, top_flange_y_range, web_z_range)
    bottom_flange = make_box(plug_x_range, bottom_flange_y_range, spec.z_range)
    plug = web.union(top_flange).union(bottom_flange)

    # Full-plug-Y cylinder (radius tube_clearance_radius) centered on the
    # plug's end Z face at x=0.
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
    """Closed-form volume of the plug: three boxes minus the arch cutouts."""
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
    buffer_cap_area = b * math.sqrt(r ** 2 - b ** 2) + r ** 2 * math.asin(b / r)
    inset_in_arch_area = half_disc_area - buffer_cap_area
    vol_arch_per_end = (
        flange_y_thickness * half_disc_area
        + flange_y_thickness * inset_in_arch_area
        + web_y_thickness * inset_in_arch_area
    )
    vol_arch_total = n_arches * vol_arch_per_end

    return vol_web + vol_top_flange + vol_bot_flange - vol_arch_total


def main():
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

    variables = {
        "SLOT_W": f"{slot_width_x:.4g} mm",
        "FLANGE_T": f"{flange_y_thickness:.4g} mm",
        "PRV_OFFSET": f"{prv_vent_offset_above_water:.4g} mm",
        "VOL_TOL": f"{volume_check_tolerance:.4g} mm³",
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
            "SLOT_W": 2,
            "FLANGE_T": 2,
            "PRV_OFFSET": 1,
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
