"""Copper-line plugs — three small PETG pieces that slide down into
the shared ⌀[6.5 mm](SLOT_W) port in the outer_shell wall and seal the gaps
between (and above) the three pass-throughs that share that port.

Pass-throughs that pierce that wall through the shared port,
ordered low → high in Z:

  • lowest copper  (cold-side evaporator inlet)  at z = the front port field's
                                                   top, one wall of PETG, and
                                                   the slot's own bottom reach
  • highest copper (warm-side evaporator outlet) at z = one front_port_pitch up
  • PRV vent (1/4" LLDPE from prv-shroud cap)     at z = one more

Not one of the three crosses at the height its own fitting sits at. The cold tail
climbs the port lane to reach the slot; the warm tail and the line off the
prv-shroud's cap drop it. So the three continue the front port field's column at the
field's own pitch instead of spreading up the wall, and every penetration the shell's
−X face has stands in one band low on it.

The PRV vent line is unpressurized in normal operation — it carries
relief-event discharge from the prv-shroud cavity (see
`../prv-shroud/`) out to the appliance interior. It shares the same
slot + same 1/4" OD tube + same ⌀[6.5 mm](SLOT_W) slot punch as the other two
pass-throughs.

Three plugs in the stack:
  • copper-plug-lower:  fills the Z span between the lowest-copper
                        and highest-copper pass-throughs.
  • copper-plug-middle: fills the Z span between the highest-copper
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
sys.path.insert(0, str(next(p for p in _here.parents if p.name == "hardware") / "scripts"))
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
    foam_shell_outer_height,
    outer_shell_x_length,
    front_port_axis,
    front_port_field_top_z,
    front_port_pitch,
    front_wall_x,
    port_lane_mid_y,
    port_lane_wall,
)

# Slot width in X equals the port's ⌀[6.5 mm](SLOT_W) punch in
# cut_slot_for_copper_and_prv_vent.
slot_width_x = 6.5
slot_half_width_x = slot_width_x / 2
slot_x_range = (-slot_half_width_x, slot_half_width_x)

# Tube clearance circle is tangent to the slot's ⌀[6.5 mm](SLOT_W) X edges
# at each pass-through Z.
tube_clearance_radius = slot_half_width_x  # [3.25 mm](TUBE_CLEAR_R)

# The plug is authored in the PORT FRAME — the frame every foam-shell penetration is
# authored in, where the wall a port crosses is a −Y wall, the slot runs lateral in x
# and z is the shell's own. In the shell the slot is in the −X wall, on the port lane;
# `_cold_core_interface.port_to_shell` is the one transform that carries this frame
# there, and `_port_cuts.cut_slot_for_copper_and_prv_vent` cuts the slot through it, so the
# slot and the stack that fills it cannot land in two places. The plug's exported
# STEP stays in this frame: a printed part's frame is the one that describes it, and
# what describes a plug is the wall it plugs.
# Web fills the wall's Y range exactly ([2 mm](CPLUG_WALL_T) thick at
# [2 mm](CPLUG_WALL_T) wall); the two flanges sit [1 mm](FLANGE_T) outboard and [1 mm](FLANGE_T) inboard of it.
# [-141.5 mm](WALL_OUTER_Y) — outer face of the wall (the shell's −X face, toward the user).
outer_wall_outer_y = -outer_shell_x_length / 2
# [-139.5 mm](WALL_INNER_Y) — inner (cavity-side) face of the −Y outer_shell wall.
outer_wall_inner_y = outer_wall_outer_y + wall_and_floor_thickness
wall_y_range = (outer_wall_inner_y, outer_wall_outer_y)

# The [2 mm](CPLUG_WALL_T) gap between the two flanges, at the wall's Y range
# and outside the web's X range, is where the −Y wall seats.
flange_x_overhang_per_side = 1.0
flange_y_thickness = 1.0

# Flanges run the full plug X width; the web sits only in the slot's X range.
plug_half_x_outer = slot_half_width_x + flange_x_overhang_per_side
plug_x_range = (-plug_half_x_outer, plug_half_x_outer)

# [-138.5 mm](PLUG_Y_INNER) — inner (cavity-side) flange's inward face.
plug_y_inner = outer_wall_inner_y + flange_y_thickness
# [-142.5 mm](PLUG_Y_OUTER) — outer flange's outward face.
plug_y_outer = outer_wall_outer_y - flange_y_thickness
plug_y_range = (plug_y_outer, plug_y_inner)

top_flange_y_range = (outer_wall_outer_y, plug_y_outer)
bottom_flange_y_range = (plug_y_inner, outer_wall_inner_y)

# Pass-through Z positions (centers).
# The lane is ONE COLUMN AT ONE PITCH. The front port field
# (`_cold_core_interface.front_port_stations`) takes the bottom of it and the slot
# takes the span above; both are one bore wide, so they share one line and cannot
# overlap. A station's Z is where its line CROSSES THE WALL, not the height of the
# fitting it serves — every line turns onto the lane and climbs or drops it to get
# here — so the slot's three continue the field at its own `front_port_pitch` rather
# than each crossing at its fitting's own height. That is what keeps all eight
# penetrations in one low band: the stack tops out at [67.75 mm](PRV_VENT_Z) on a
# wall [213.4 mm](SHELL_TOP_Z) tall, so whatever is packed against this face outside
# meets every port in one reach instead of up the shell's full height. What the
# stack owes the field is the field's top, one wall of PETG, and the reach of the
# slot's own rounded bottom below the lowest plug.
# [51.75 mm](LOWEST_COPPER_Z) — cold-side evaporator inlet, where it crosses the wall.
slot_bottom_below_lowest_plug = 5.0     # open slot under the lowest plug's bottom arch
lowest_copper_z = (front_port_field_top_z + port_lane_wall
                   + slot_width_x / 2 + slot_bottom_below_lowest_plug)
# The slot's own bottom — the straight section's low end, with the punch's rounded
# end reaching slot_width_x/2 further down.
slot_z_bottom = lowest_copper_z - slot_bottom_below_lowest_plug
# [59.75 mm](HIGHEST_COPPER_Z) — warm-side evaporator outlet. The coil's warm tail
# leaves its top wrap at `_cold_core_interface.evap_tail_high_z` and DROPS the lane
# to cross here — the mirror of the cold tail's climb, and the reason the coil's own
# geometry and this station are two numbers rather than one.
highest_copper_z = lowest_copper_z + front_port_pitch
# [67.75 mm](PRV_VENT_Z) — PRV relief line, down the lane from the prv-shroud cap.
prv_vent_z = highest_copper_z + front_port_pitch
# [145.7 mm](TOP_PLUG_H) — Z extent of the top plug, and it is most of the wall: the
# slot runs out through the shell's top face so the stack can be dropped in from
# above, so the plug over the highest line has to fill everything above it.
top_plug_height = foam_shell_outer_height - prv_vent_z

# Plug end faces meet AT the tube pass-through centers. The arch
# cutout at each tube-facing end (radius = tube_clearance_radius)
# holds exactly HALF of the adjacent tube: the plug ABOVE a tube seats
# its upper half (in that plug's bottom arch), the plug BELOW seats its
# lower half (in that plug's top arch). The plugs tile the slot from
# lowest_copper_z to the wall top with no linear gaps — the tube IS the gap.
PlugSpec = namedtuple("PlugSpec", ["z_range", "arch_bottom", "arch_top"])

plug_specs = {
    "lower": PlugSpec((lowest_copper_z, highest_copper_z), arch_bottom=True, arch_top=True),
    "middle": PlugSpec((highest_copper_z, prv_vent_z), arch_bottom=True, arch_top=True),
    "top": PlugSpec((prv_vent_z, foam_shell_outer_height), arch_bottom=True, arch_top=False),
}


def slot_station(name):
    """The line crossing the wall UNDER one plug, in the SHELL'S OWN frame:
    `(position, outward axis)`.

    A plug's bottom face IS a pass-through centre — the arch there holds the upper half of
    that tube and the plug below holds its lower half — so the three stations are the three
    plugs' own low ends, and a plug resized carries its line with it. They stand on the same
    lane the field's five do, and continue that column at its own pitch."""
    return ((front_wall_x, port_lane_mid_y, plug_specs[name].z_range[0]), front_port_axis)


def slot_stations() -> dict:
    """All three the slot carries, under the plugs whose low ends they are."""
    return {name: slot_station(name) for name in plug_specs}

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
    web_y_thickness = abs(wall_y_range[1] - wall_y_range[0])

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
        "VOL_TOL": f"{volume_check_tolerance:.4g} mm³",
        "TUBE_CLEAR_R": f"{tube_clearance_radius:.4g} mm",
        "WALL_OUTER_Y": f"{outer_wall_outer_y:.4g} mm",
        "WALL_INNER_Y": f"{outer_wall_inner_y:.4g} mm",
        "PLUG_Y_INNER": f"{plug_y_inner:.4g} mm",
        "PLUG_Y_OUTER": f"{plug_y_outer:.4g} mm",
        "LOWEST_COPPER_Z": f"{lowest_copper_z:.4g} mm",
        "HIGHEST_COPPER_Z": f"{highest_copper_z:.4g} mm",
        "PRV_VENT_Z": f"{prv_vent_z:.4g} mm",
        "TOP_PLUG_H": f"{top_plug_height:.4g} mm",
        "WEB_BUFFER": f"{web_arch_buffer:.2f} mm",
        # External references (read-only constants from _cold_core_interface).
        "CPLUG_WALL_T": f"{wall_and_floor_thickness:.4g} mm",
        "SHELL_TOP_Z": f"{foam_shell_outer_height:.4g} mm",
    }
    substitute_py_comments(
        Path(__file__),
        variables=variables,
        expected_counts={
            "SLOT_W": 4,
            "FLANGE_T": 2,
            "VOL_TOL": 1,
            "TUBE_CLEAR_R": 1,
            "WALL_OUTER_Y": 1,
            "WALL_INNER_Y": 1,
            "PLUG_Y_INNER": 1,
            "PLUG_Y_OUTER": 1,
            "LOWEST_COPPER_Z": 1,
            "HIGHEST_COPPER_Z": 1,
            "PRV_VENT_Z": 2,
            "TOP_PLUG_H": 1,
            "WEB_BUFFER": 1,
            "CPLUG_WALL_T": 3,
            "SHELL_TOP_Z": 1,
        },
    )
    print(f"-> {Path(__file__).name} (self)")


if __name__ == "__main__":
    main()
