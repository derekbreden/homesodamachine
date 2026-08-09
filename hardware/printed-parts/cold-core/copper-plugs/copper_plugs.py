"""Copper-line plugs — small PETG pieces that slide down into a lane's ⌀[6.5 mm](SLOT_W)
slot in the outer_shell wall and seal the gaps between (and above) the lines crossing there.

THE SLOT IS THE COPPER'S DOING. An evaporator tail is formed off a coil that is lowered into
the cavity, so its outward leg travels DOWN the wall to its station rather than being
threaded through it, and that takes an opening running out through the shell's top face.
Everything else on the same lane then crosses inside that one opening.

THE SHELL'S FRONT WALL HAS TWO LANES AND THE REFRIGERATION BASE IS TWO BODIES — the
condenser on the PORT lane's flank, the compressor on the WEST lane's. So the evaporator's
two coppers leave by opposite lanes, each one out on the side the leg that reaches it comes
from, and each lane is one slot with its own stack. `columns` is that table.

  PORT LANE, one station, over the front port field's two reed cables:
    • [27.75 mm](EVAP_INLET_Z) evaporator inlet — the cold-side copper, reached from the
      condenser's outlet through the drier and the cap tube

  WEST LANE, low → high:
    • [19.75 mm](PRV_VENT_Z) PRV vent — 1/4" LLDPE down the lane from the prv-shroud's barrel
    • [27.75 mm](EVAP_OUTLET_Z) evaporator outlet — the warm-side copper, reached from the
      compressor's suction. It crosses at the height its opposite number does: the two
      lanes are the same strip mirrored, and one coil's two tails reach either the same way.

THE VENT CROSSES UNDER THE COPPER IT SHARES A LANE WITH, and that is the west lane's own
arithmetic rather than a preference. Reservoir B's pocket closes the standoff annulus at the
outlet tail's azimuth, so that tail falls IN the lane (`_coil.FALL_IN_LANE`) — a riser from its
wrap all the way down to its station, and a wall to anything crossing that column at any storey
above it. What is left is the storey below, one pitch down. The port lane's own copper stands
its fall outside the lane, so nothing there is a riser and its one station sits at the field's
own floor.

Not one of them crosses at the height its own fitting sits at. Each line leaves its fitting,
turns onto its lane and climbs or drops it — the cold tail drops to its station, the warm
tail drops the far lane, the PRV vent comes down off the shroud's barrel — so all of it stands
in one band low on the wall rather than spreading up it.

The PRV vent line is unpressurized in normal operation — it carries
relief-event discharge from the prv-shroud cavity (see
`../prv-shroud/`) out to the appliance interior. It takes the same 1/4" OD tube and the same
⌀[6.5 mm](SLOT_W) slot punch as the copper beside it.

Three plugs, one printed part each. A plug fills from one station up to the next, and the
last plug of a column reaches the wall's top face so nothing is left open above the stack:
  • copper-plug-lower:  WEST lane, PRV vent up to the evaporator outlet.
  • copper-plug-middle: WEST lane, the evaporator outlet up to (just below) the +Z top face
                        of the outer_shell.
  • copper-plug-top:    PORT lane, the evaporator inlet up to that same face — the whole
                        of its own column, because one line crosses that lane.

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

Every plug arches on the BOTTOM, over the line its own station carries. It arches on TOP only
where another station stands above it in the same column; the plug that closes a column stays
FLAT on top, at the wall's own top face.
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
    west_lane_mid_y,
    bound,
    state,
)

# Slot width in X equals the port's ⌀[6.5 mm](SLOT_W) punch in
# cut_lane_slots.
slot_width_x = 6.5
slot_half_width_x = slot_width_x / 2
slot_x_range = (-slot_half_width_x, slot_half_width_x)

# Tube clearance circle is tangent to the slot's ⌀[6.5 mm](SLOT_W) X edges
# at each pass-through Z.
tube_clearance_radius = slot_half_width_x  # [3.25 mm](TUBE_CLEAR_R)

# The plug is authored in the PORT FRAME — the frame every foam-shell penetration is
# authored in, where the wall a port crosses is a −Y wall, the slot runs lateral in x
# and z is the shell's own. In the shell the slot is in the −X wall, on one of its two lanes;
# `_cold_core_interface.port_to_shell` is the one transform that carries this frame
# there, and `_port_cuts.cut_lane_slots` cuts each slot through it, so a
# slot and the stack that fills it cannot land in two places. The plug's exported
# STEP stays in this frame: a printed part's frame is the one that describes it, and
# what describes a plug is the wall it plugs — one wall for both lanes, so a plug drawn
# here fits either.
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
# A LANE IS ONE COLUMN AT ONE PITCH. On the port lane the front port field
# (`_cold_core_interface.front_port_stations`) takes the bottom of it and the slot
# takes the span above; both are one bore wide, so they share one line and cannot
# overlap. A station's Z is where its line CROSSES THE WALL, not the height of the
# fitting it serves — every line turns onto its lane and climbs or drops it to get
# here — so the slot's stations sit at the field's own `front_port_pitch` rather
# than each crossing at its fitting's own height. That is what keeps every
# penetration in one low band: no station stands above [27.75 mm](EVAP_INLET_Z) on a
# wall [213.4 mm](SHELL_TOP_Z) tall, so whatever is packed against this face outside
# meets all of them in one reach instead of up the shell's full height. What a
# stack owes the field under it is the field's top, one wall of PETG, and the reach of the
# slot's own rounded bottom below the lowest plug.
slot_bottom_below_lowest_plug = 5.0     # open slot under the lowest plug's bottom arch
# The cold-side evaporator inlet on the PORT lane, and
# [27.75 mm](EVAP_OUTLET_Z) the warm-side outlet on the WEST one. Both coppers cross at this
# height: the two lanes are one strip mirrored, and each tail leaves its wrap
# (`_cold_core_interface.evap_tail_low_z` / `evap_tail_high_z`) and turns onto its own lane
# to reach it — which is why the coil's geometry and these stations are separate numbers.
evap_cross_z = (front_port_field_top_z + port_lane_wall
                + slot_width_x / 2 + slot_bottom_below_lowest_plug)
# [19.75 mm](PRV_VENT_Z) — PRV relief line, down the WEST lane from the prv-shroud's barrel,
# one pitch UNDER the copper beside it. That direction is the outlet tail's doing: it falls in
# the lane from its wrap to its own station, so the column is closed at every storey above and
# this is the only one left. The field the port lane keeps below its slot has no counterpart
# here, so the west slot's bottom simply follows this station down.
prv_vent_z = evap_cross_z - front_port_pitch

# THE TWO COLUMNS. A column is a lane, the stations crossing the wall on it in climbing
# order, and the slot bottom under the lowest of them — the straight section's low end, with
# the punch's rounded end reaching `slot_width_x / 2` further down.
Column = namedtuple("Column", ["lane_y", "stations", "slot_z_bottom"])


def _column(lane_y, stations):
    return Column(lane_y, tuple(stations),
                  stations[0][1] - slot_bottom_below_lowest_plug)


columns = {
    "port-lane": _column(port_lane_mid_y, [("evap-inlet", evap_cross_z)]),
    "west-lane": _column(west_lane_mid_y,
                         [("prv-vent", prv_vent_z), ("evap-outlet", evap_cross_z)]),
}


def station_lane(station):
    """Which lane one station crosses on: `(column name, its lane's y)`.

    A line that falls a lane and a plug that seals it read the same table, so the lane is
    looked up by the station's name rather than restated at either end."""
    for name, column in columns.items():
        if any(s == station for s, _z in column.stations):
            return (name, column.lane_y)
    raise KeyError(f"no station {station!r} — have: "
                   f"{', '.join(sorted(s for c in columns.values() for s, _z in c.stations))}")

# Plug end faces meet AT the tube pass-through centers. The arch
# cutout at each tube-facing end (radius = tube_clearance_radius)
# holds exactly HALF of the adjacent tube: the plug ABOVE a tube seats
# its upper half (in that plug's bottom arch), the plug BELOW seats its
# lower half (in that plug's top arch). The plugs tile their column from
# its lowest station to the wall top with no linear gaps — the tube IS the gap.
PlugSpec = namedtuple("PlugSpec", ["z_range", "arch_bottom", "arch_top", "column", "station"])

# Which printed part fills which span. The three names are the three STEPs, and each is one
# span of one column: `lower` and `middle` tile the west lane, `top` is the whole of the
# port lane's own stack.
PLUG_ORDER = (("lower", "west-lane", 0), ("middle", "west-lane", 1), ("top", "port-lane", 0))

plug_specs = {}
for _plug, _col, _i in PLUG_ORDER:
    _spec = columns[_col]
    _edges = [z for _n, z in _spec.stations] + [foam_shell_outer_height]
    plug_specs[_plug] = PlugSpec((_edges[_i], _edges[_i + 1]),
                                 arch_bottom=True, arch_top=_i + 1 < len(_spec.stations),
                                 column=_col, station=_spec.stations[_i][0])
state(
    "plug-per-station", "Every station is one plug's bottom face and every plug is one station's",
    f"{sum(len(c.stations) for c in columns.values())} plugs",
    len(plug_specs) == sum(len(c.stations) for c in columns.values()),
    "every station in every column is one plug's bottom face, and every plug is one station's "
    f"— {len(plug_specs)} plugs against "
    f"{sum(len(c.stations) for c in columns.values())} stations")


def slot_station(name):
    """The line crossing the wall UNDER one plug, in the SHELL'S OWN frame:
    `(position, outward axis)`.

    A plug's bottom face IS a pass-through centre — the arch there holds the upper half of
    that tube and the plug below holds its lower half — so the stations are the plugs' own
    low ends, and a plug resized carries its line with it. `name` is either the plug's or
    the station's; a column of one has both names for one point."""
    spec = plug_specs[name] if name in plug_specs else plug_specs[_by_station(name)]
    return ((front_wall_x, columns[spec.column].lane_y, spec.z_range[0]), front_port_axis)


def _by_station(station):
    for plug, spec in plug_specs.items():
        if spec.station == station:
            return plug
    raise KeyError(f"no station {station!r} — have: "
                   f"{', '.join(sorted(s.station for s in plug_specs.values()))}")


def slot_stations() -> dict:
    """Every station either lane's slot carries, under the LINE that crosses there. The two
    evaporator coppers are the two the refrigeration base picks up on the other side of the
    plane it shares with this wall."""
    return {spec.station: slot_station(plug) for plug, spec in plug_specs.items()}

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

# A plug between two stations one `front_port_pitch` apart is the pitch's own wall: the two
# arches eat a bore's radius out of each end of its span, and what stands between them is the
# PETG a bore on the lane would have left either side of it. Below `min_printable_thickness`
# the wall between two lines stops being printable, so the shortest plug in either stack is
# where a column tightened too far shows up.
_plug_web = bound(
    "plug-web", "Every plug leaves a printable wall standing between its arches",
    f"{min_printable_thickness:g} mm of web")
for _plug, _spec in plug_specs.items():
    _web = (_spec.z_range[1] - _spec.z_range[0]
            - tube_clearance_radius * (2 if _spec.arch_top else 1))
    _plug_web(
        _web >= min_printable_thickness - 1e-9,
        f"plug {_plug} spans {_spec.z_range[1] - _spec.z_range[0]:g} mm and leaves {_web:g} mm "
        f"standing between its arches, under the {min_printable_thickness:g} mm a wall takes")


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
            f"{spec.column} {spec.station:12} "
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
        "EVAP_INLET_Z": f"{evap_cross_z:.4g} mm",
        "EVAP_OUTLET_Z": f"{evap_cross_z:.4g} mm",
        "PRV_VENT_Z": f"{prv_vent_z:.4g} mm",
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
            "EVAP_INLET_Z": 2,
            "EVAP_OUTLET_Z": 2,
            "PRV_VENT_Z": 2,
            "WEB_BUFFER": 1,
            "CPLUG_WALL_T": 3,
            "SHELL_TOP_Z": 1,
        },
    )
    print(f"-> {Path(__file__).name} (self)")


if __name__ == "__main__":
    main()
