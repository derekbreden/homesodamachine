"""Faucet shell — printed shroud that wraps the harvested Westbrass,
the flavor tubes, and the lever swing volume. Sits on top of
the above-counter plate. The dispense tip carries the cradle for
the faucet display (DISPLAY CRADLE section).

Frame: world +Z is height (up), world ±X is lateral (symmetric across
the X=0 plane), world -Y is forward (dispense direction — the gooseneck
arcs toward -Y, where the user's glass sits). The Westbrass's threaded shank
runs along world Z at world (X, Y) = (0, 0).

`faucet_shell.rs` cuts the two printed pieces from the faucet's numbers crate
(`../numbers/shell.rs`). This module is for the readers that still take the shell from
Python: the builders below draw the same shell in CadQuery, and its datums are the
recipe `tools/hsm/faucet-data` serves."""

from __future__ import annotations

import io
import ast
import functools
import hashlib
import math
import os
import sys
import time
from pathlib import Path

_here = Path(__file__).resolve()
sys.path.insert(
    0,
    str(next(p for p in _here.parents if p.name == "hardware") / "scripts"),
)
sys.path.insert(
    0,
    str(next(p for p in _here.parents if (p / "tools" / "docgen").is_dir()) / "tools"),
)
sys.path.insert(0, str(_here.parent.parent))  # for _faucet_interface
sys.path.insert(0, str(next(p for p in _here.parents if p.name == "printed-parts") / "cadlib"))
import cadquery as cq
import trimesh

import fits
# Manifold validation and the ledger of named geometric bounds.
import flute_skin as _flute_skin
import _stated_bounds as _bounds
import _cadq_export  # noqa: E402,F401  the CAD lock
from _materials import C_FAUCET_BLACK, linear
import _faucet_interface
import faucet_paths as _paths
import _display_snap
from _faucet_interface import (
    above_counter_gasket_thickness,
    above_counter_plate_thickness,
    flavor_tube_od,
    flavor_tube_x_offset,
    flavor_tube_hole_dia,
    pill_length_x,
    pill_width_y,
    flavor_tube_depth,
    display_housing_width,
    display_housing_length,
    display_pcb_width,
    display_pcb_length,
    display_corner_r,
    display_pcb_corner_r,
    display_total_depth,
    display_pcb_top_z,
    display_cover_slip,
    display_cover_lap,
    display_cover_over_face,
)
from world_workplane import WorldWorkplane, xy_plane_z_up, xz_plane_y_up


# ============================================================
# WORLD FRAME PRIMITIVES
# ============================================================

from _rust_data import request as _data_request


def _shell_data(fn="datums", **values):
    if fn in ("numbers", "_lever_outline"):
        library = _data_request("faucet-data", "faucet-data", {"op": "geos-library"})
        _cadq_export.note_read(library["path"])
    if fn == "variables" and "directory" in values:
        for name in ("faucet-shell-base.stl", "faucet-shell-tip.stl"):
            _cadq_export.note_read(Path(values["directory"]) / name)
    return _data_request("faucet-data", "faucet-data", {"op": "shell", "fn": fn, "slip": fits.slip, **values})


_shell_values = _shell_data()
globals().update(_shell_values["datums"])
for _record in _shell_values["bounds"]:
    _reading = _bounds.bound(_record["id"], _record["label"], _record["target"])
    for _ok, _detail in _record["readings"]:
        _reading(_ok, _detail)


def _horizontal_plane(z_offset):
    """XY plane at world Z = z_offset; coords (world_x, world_y), +Z normal."""
    return WorldWorkplane(xy_plane_z_up).workplane(offset=z_offset)


_yz_plane_x_normal = cq.Plane(
    origin=(0, 0, 0),
    xDir=(0, 1, 0),       # local +X = world +Y (depth)
    normal=(1, 0, 0),     # extrude along world +X (lateral)
)


def _vertical_plane(x_offset):
    """YZ plane at world X = x_offset; local (depth, height) = (world +Y, world +Z), +X normal."""
    return cq.Workplane(_yz_plane_x_normal).workplane(offset=x_offset)


# ZONE 1 — first; the Westbrass is a full ⌀ cylinder here


# Westbrass bore —; Westbrass OD.


# Flavor-tube pill — 1/4" OD LLDPE tubes ( OD), tangent to the
# Westbrass's +Y face (Y=+); the mounting row is F1-D-F2.
# long axis (X), short axis (Y).


# — flat -Y edge of the flavor pill
# cutout in zones 1-4, on the Westbrass-bore +Y wall at the cutout's X corners.


# SHELL OUTER


# The donor and lever envelope owns the lower arch's construction datum.


# THE PILL'S FARTHEST POINT IS ON AN END CAP AND NOT ON ITS BACK EDGE. The cutout is a slot
# with its cap circles at (±`flavor_tube_x_offset`, `flavor_tube_depth`), and the shell's outer
# is a cylinder about `shell_center` — so the corner that reaches furthest from that centre is a
# cap's own rim, `pill_width_y / 2` out from a centre standing off the axis in X as well as Y.
# Read on the +Y edge alone the reach comes back 0.32 mm short, and the wall over the cap's
# shoulder is that much thinner than the figure says.

# outer-cylinder radius.


# ZONE 2


# Body rectangle dimensions


# Cove transition fillet — matches the Westbrass's transition_fillet_r.


# cylindrical shell wall above the Westbrass cyl top before the cove.


# BASE JOINT — three hidden M3 screws clamp the plate against the shell.
# Three pedestals register the plate before the screws are tightened.


# The lateral sockets clear the rear bundle and keep two millimetres
# of continuous stock around both their socket and installed brass envelopes.


# Positive material is measured against the inserted brass envelope, not its pilot.


# ZONE 3 — arch wraps (two wings at ±X)
#
# Body arches: 1.5 mm ridges at X = ±7.75, full Y width (±15.75); profile
# in (Y, Z) is a 2 mm foot from Z=39→41 then a 3-point arc through
# (∓15.75, 41) and (0, 46).
# Plateau between the arches (X ∈ ±) is open.


# ZONE 3 — plateau fill (between the wings, Y ≥ fill_y_min).

# 3/8" LLDPE soda faucet tube, internal to the faucet — sealed in the
# Westbrass's 10.0 mm port via a printed TPU bushing (see
# ../tpu-o-ring/).

# water bore.


# 4 mm LLDPE flavor tubes, tangent to the soda faucet tube at the dispense
# point and sitting behind it (more +Y).

# neoFlo LLDPE-4 (1/4-inch OD) supplier bend radius: 1 inch.
# https://assets.freshwatersystems.com/image/upload/s--N9disqrx--/gjtidjfc0tlprqbhb4ka.pdf


# ZONE 4 — rect column above the arch (soda faucet tube + flavor pill cutouts).

# Clears the pressed-lever head corner (Y=+6.78, Z=54.024), which sits
# inside zone 5's water-circle outline (Y=+,
# R=); zone 5's bottom is above it.


# ZONE 5 — round tube wrapper above the lever, carrying the soda bore
# and flavor pill. Its wall contains both halves of the curved joint.


# Water → flavor offset along world Y; positive — flavor sits behind water.


# ZONE 6 — gooseneck wrapper around the bent tubes: zone 5's
# cross-section swept along one circular arc above the lever-swing envelope.
# Mirrors constants in `faucet-assembly`.


# SPLIT — the shell prints in two pieces at the internal
# datum. The base has the 20 mm female socket;
# the tip carries the 18 mm male land. The
# mating surfaces follow the arc and the tip swings shut about its axis.
# Fit: the plug's outer surface sits slip/2 inside the socket's cavity
# surface, all the way around the cross-section.


# Per-side overlap depth (mm of arc), socket wall (mm), and diametral
# slip (mm), mapped onto `shrink`s (inward offsets of the outer
# cross-section):
#   socket shrink = socket_wall
#   plug   shrink = socket_shrink + slip / 2


# SPLIT geometry.
#
# All `_path_*` constants below are in path-local 2D coords: local axes
# (a, b) map to world (-Y, +Z); X=0, origin at world (0, soda_faucet_tube_y,
# zone5_z_top).

# Bend-2 sub-arcs covering the last overlap_len mm of arc before the
# junction — separate arcs for the female socket and the male plug.


# Cumulative path rotations from the +Z origin tangent.


# Tangent unit-vectors in path-local (a, b).


# Path-local waypoints, working forward from the path origin.


# Bend-2 arc center.


def _bend2_point(rot: float) -> tuple:
    return _shell_data('_bend2_point', args=[rot])


# SPLIT mating-plane geometry in world coords. The plane is
# perpendicular to the gooseneck tangent at the junction.


# PRINTING — the base beds on its foot (Z=0) with the -Y edge lifted
#, keeping the long straight neck close to vertical.
# The tip beds on the joint end with the crown lifted and its build
# direction at the angular midpoint of the sweep it carries.


# Tilt off the bed face. The foot is square to the path at rotation 0
# and the joint face to the path at the junction.


# ZONE 3 OUTER ARCH — single circular arc from the wing bottom
# (zone3_z_bottom at the -Y end) up to zone4_z_top at Y=fill_y_min,
# tangent-horizontal at the high end. Center is directly below the high end.


# Angular midpoint of the arc, between the high end (fill_y_min) and the
# low end (shell_rect_y_min, the -Y front/user edge of the rect column).


# ZONE 4.5 — block capping the lever swing volume from above, reaching
# up to Z=gn_bend1_z_start ≈.

# Round gooseneck section at world X=0.


# Zone 4.5 Y extents — back edge follows the rect column; front edge
# matched-margin from zone 5.


# Top sits 3 mm above zone 4's top on the back side (lid sits flat on
# zone 4 top). The front bottom follows the back-arch curve down to
# ≈ Z=.


# Mid-point of the bottom arch sub-arc, between zone45_front_y end
# and fill_y_min end.


# Joinery and retention: see ASSEMBLY.md.


# ============================================================
# GEOMETRY BUILDERS
# ============================================================


def soda_faucet_tube_cyl(z_bottom: float, z_height: float) -> cq.Workplane:
    """Soda-faucet-tube bore cylinder (R = soda_faucet_hole_diameter/2 at (0, soda_faucet_tube_y)) over the Z range."""
    return (
        _horizontal_plane(z_bottom)
        .moveTo((0.0, soda_faucet_tube_y))
        .circle(soda_faucet_hole_diameter / 2.0)
        .extrude(z_height)
    ).unwrap()


def westbrass_bore_cyl(z_bottom: float, z_height: float) -> cq.Workplane:
    """Westbrass bore cylinder (R = westbrass_bore_diameter/2 at origin) over the Z range."""
    return (
        _horizontal_plane(z_bottom)
        .moveTo((westbrass_bore_x, westbrass_bore_y))
        .circle(westbrass_bore_diameter / 2.0)
        .extrude(z_height)
    ).unwrap()


def _flavor_pill_flat_y_minus(z_bottom: float, z_height: float) -> cq.Workplane:
    """Flavor pill cutout (pill_length_x × pill_width_y, X long axis) at
    flavor_pill_center, -Y side flattened to flavor_pill_y_minus_edge."""
    pill = (
        _horizontal_plane(z_bottom)
        .moveTo(flavor_pill_center)
        .slot2D(pill_length_x, pill_width_y, angle=0)
        .extrude(z_height)
    ).unwrap()
    pill_center_y = flavor_pill_center[1]
    fill_width = pill_center_y - flavor_pill_y_minus_edge
    fill_rect = (
        _horizontal_plane(z_bottom)
        .moveTo((flavor_pill_center[0], pill_center_y - fill_width / 2.0))
        .rect(pill_length_x, fill_width)
        .extrude(z_height)
    ).unwrap()
    return pill.union(fill_rect)


def build_zone1_inner_cut() -> cq.Workplane:
    """Body bore + flavor-tube pill."""
    westbrass_bore = westbrass_bore_cyl(zone1_z_bottom, zone2_bore_z_bottom - zone1_z_bottom)
    pill = _flavor_pill_flat_y_minus(zone1_z_bottom, zone1_height)
    return westbrass_bore.union(pill)


def build_base_pod_holes() -> cq.Workplane:
    """Three pedestal sockets, each with an insert pilot opening through its roof."""
    cuts = []
    for center in base_pod_centers:
        socket = (_horizontal_plane(base_pod_z_bottom).moveTo(center)
                  .circle(base_pod_hole_dia / 2.0).extrude(base_pod_hole_depth).unwrap())
        insert = (_horizontal_plane(base_insert_bottom_z).moveTo(center)
                  .circle(base_pod_insert_dia / 2.0).extrude(base_pod_insert_depth).unwrap())
        cuts.append(socket.val().fuse(insert.val()))
    return cq.Workplane(obj=cq.Compound.makeCompound(cuts))


def build_foot_outline(z_bottom: float, z_height: float) -> cq.Workplane:
    """Shared oval perimeter of the shell, above-counter plate and gasket."""
    return (cq.Workplane("XY").workplane(offset=z_bottom)
            .center(0.0, foot_center_y).ellipse(foot_width / 2.0, foot_depth / 2.0)
            .extrude(z_height))


# The lower shell's oval sections, (z, width, depth, centre y), lofted up onto the round neck at
# lower_neck_z; the neck's land stands on to neck_land_overrun past the zone-5 seam.


def build_lower_outer() -> cq.Workplane:
    """Continuous oval lower shell, terminating on the round gooseneck section."""
    wires = [cq.Workplane("XY").workplane(offset=z).center(0.0, cy)
             .ellipse(width / 2.0, depth / 2.0).val()
             for z, width, depth, cy in lower_outer_sections]
    neck = _tube_shell_outer_sketch()._faces.Faces()[0].outerWire()
    wires.append(neck.translate((0.0, soda_faucet_tube_y, lower_neck_z)))
    loft = cq.Solid.makeLoft(wires, ruled=False)
    neck_land = cq.Solid.extrudeLinear(
        wires[-1], [], cq.Vector(0.0, 0.0, zone5_z_top + neck_land_overrun - lower_neck_z))
    return cq.Workplane(obj=loft.fuse(neck_land)).clean()


# The flat ribbon shares the rear mounting channel with the F1-D-F2 row.


def _lower_signal_stations():
    return _shell_data('_lower_signal_stations', args=[])


def _lower_signal_profile(z, x, y, width, depth, rounded, angle=0.0):
    wp = cq.Workplane("XY").workplane(offset=z).center(x, y)
    wire = (wp.slot2D(width, depth) if rounded else wp.rect(width, depth)).val()
    return wire.rotate((x, y, z), (x, y, z + 1.0), angle)


def _lower_signal_profiles(width, depth, rounded, bottom_z, turn_clearance=0.0):
    return _shell_data('_lower_signal_profiles', args=[width, depth, rounded, bottom_z, turn_clearance])


def _lower_signal_wires(width, depth, rounded, bottom_z, turn_clearance=0.0):
    return [_lower_signal_profile(*profile) for profile in
            _lower_signal_profiles(width, depth, rounded, bottom_z, turn_clearance)]


def _lower_signal_solid(width, depth, rounded, bottom_z, turn_clearance=0.0):
    solid = cq.Solid.makeLoft(
        _lower_signal_wires(width, depth, rounded, bottom_z, turn_clearance), ruled=True)
    if not solid.isValid() or len(solid.Solids()) != 1:
        raise ValueError("the complete lower ribbon or clearance lane must be one valid solid")
    return cq.Workplane(obj=solid)


# The measured flat ribbon through the complete mount stack: its section, and its foot.


def build_lower_signal_ribbon() -> cq.Workplane:
    """Measured flat ribbon envelope through the complete mount stack."""
    return _lower_signal_solid(*lower_signal_ribbon)


# The flat cable lane's foot, in the mounting stack below the counter; the bundle opening's
# straight lands start bundle_land_below under zone 3's floor and stand bundle_land_above over
# the loft's top.


def _lower_opening_heights():
    return _shell_data('_lower_opening_heights', args=[])


def _lower_opening_circles(z):
    return _shell_data('_lower_opening_circles', args=[z])


def build_lower_signal_lane() -> cq.Workplane:
    """Flat rear cable passage and one open tube/cable transition.

    Tangent hulls around the complete rounded clearances join the mounting
    channel to the neck. The opening has no thin stock between adjoining
    tube and cable passages.
    """
    lane = _lower_signal_solid(signal_lane_width, signal_lane_depth, True, signal_lane_bottom_z)
    heights = _lower_opening_heights()
    wires = []
    for z in heights:
        sketch = cq.Sketch()
        for x, y, r in _lower_opening_circles(z):
            sketch = sketch.arc((x, y), r, 0.0, 360.0)
        wires.append(sketch.hull().clean()._faces.Faces()[0].outerWire()
                     .translate((0.0, 0.0, z)))
    transition = cq.Solid.makeLoft(wires, ruled=False)
    # Exact straight lands meet the donor and neck profiles. Extending a
    # spline loft through these constant runs can introduce tiny ripples at
    # coincident bore faces, so their circular/planar boundaries stay analytic.
    z0 = heights[0]
    bottom = zone3_z_bottom-bundle_land_below
    lower = cq.Solid.extrudeLinear(
        wires[0].translate((0.0, 0.0, bottom-z0)), [], cq.Vector(0, 0, z0-bottom))
    upper = cq.Solid.extrudeLinear(wires[-1], [], cq.Vector(0, 0, bundle_land_above))
    opening = lower.fuse(transition, upper, tol=1e-6).clean()
    joined = lane.val().fuse(opening,tol=1e-6)
    if not joined.isValid() or len(joined.Solids()) != 1:
        raise ValueError("the common lower bundle opening must be one valid native solid")
    return cq.Workplane(obj=joined)


# How far the donor's cutters reach past its bore across Y, so their ends meet no face of it.


def _rect_cove_cyl(
    center_x: float, center_y: float,
    rect_x_width: float, rect_y_width: float,
    z_bottom: float, z_top: float,
    clip_cyl: cq.Workplane,
) -> cq.Workplane:
    """Rect column with cove-filleted ±X faces, clipped to a cylinder
    (mirrors the Westbrass's build_transition_cove)."""
    z_height = z_top - z_bottom
    rect_x_half = rect_x_width / 2.0
    ext_y = rect_y_width / 2.0 + bore_overrun

    rect = (
        _horizontal_plane(z_bottom)
        .moveTo((center_x, center_y))
        .rect(rect_x_width, rect_y_width)
        .extrude(z_height)
    ).unwrap()

    def filler(x_sign: int) -> cq.Workplane:
        flat_x = center_x + x_sign * rect_x_half
        blk_cx = flat_x + x_sign * (cove_r / 2.0)
        return (
            _horizontal_plane(z_bottom)
            .moveTo((blk_cx, center_y))
            .rect(cove_r, 2.0 * ext_y)
            .extrude(cove_r)
        ).unwrap()

    def cove_cutter(x_sign: int) -> cq.Workplane:
        flat_x = center_x + x_sign * rect_x_half
        cove_cx = flat_x + x_sign * cove_r
        cove_cz = z_bottom + cove_r
        # Cylinder axis along world Y.
        return (
            WorldWorkplane(xz_plane_y_up)
            .workplane(offset=center_y - ext_y)
            .moveTo((cove_cx, cove_cz))
            .circle(cove_r)
            .extrude(2.0 * ext_y)
            .unwrap()
        )

    return (
        rect
        .union(filler(+1))
        .union(filler(-1))
        .cut(cove_cutter(+1))
        .cut(cove_cutter(-1))
        .intersect(clip_cyl)
    )


def build_zone2_inner_cut() -> cq.Workplane:
    """Zone 2 inner — Westbrass cross-section (rect + cove + cyl clip) at
    bore_clearance per side, plus the flavor-tube pill through."""
    bore_zone2_height = zone2_z_top - zone2_bore_z_bottom
    bore = _rect_cove_cyl(
        westbrass_bore_x, westbrass_bore_y,
        westbrass_bore_rect_short_x, westbrass_bore_rect_long_y,
        zone2_bore_z_bottom, zone2_z_top,
        westbrass_bore_cyl(zone2_bore_z_bottom, bore_zone2_height),
    )
    pill = _flavor_pill_flat_y_minus(zone2_z_bottom, zone2_height)
    return bore.union(pill)


def build_zone3_inner_cut() -> cq.Workplane:
    """Donor arch clearance joined to the tube opening behind the lever."""
    bore_y_oversize = westbrass_bore_diameter / 2.0 + bore_overrun

    def bore(x_bottom: float, x_height: float) -> cq.Workplane:
        return (
            _vertical_plane(x_bottom)
            .moveTo(+bore_y_oversize, zone3_z_bottom)
            .lineTo(-bore_y_oversize, zone3_z_bottom)
            .lineTo(-bore_y_oversize, shell_arch_bore_z_foot_top)
            .threePointArc((0, shell_arch_bore_z_peak),
                           (+bore_y_oversize, shell_arch_bore_z_foot_top))
            .lineTo(+bore_y_oversize, zone3_z_bottom)
            .wire()
            .extrude(x_height)
        )

    bore_thickness = shell_arch_bore_outer_x - shell_arch_bore_inner_x
    bores = bore(+shell_arch_bore_inner_x, +bore_thickness).union(
        bore(-shell_arch_bore_outer_x, +bore_thickness)
    )
    # Keep the donor's arch roof while opening the rear central span into the
    # tube passage. The lever corridor ahead of fill_y_min remains unchanged.
    # No independent divider stands between the arch clearance and the tubes.
    rear_window = cq.Solid.makeBox(
        2.0 * shell_arch_bore_inner_x,
        bore_y_oversize - fill_y_min,
        shell_arch_bore_z_peak - zone3_z_bottom,
        cq.Vector(-shell_arch_bore_inner_x, fill_y_min, zone3_z_bottom))
    rear_join = bore(-shell_arch_bore_inner_x, 2.0 * shell_arch_bore_inner_x).intersect(
        cq.Workplane(obj=rear_window))
    bores = bores.union(rear_join)
    return bores.intersect(westbrass_bore_cyl(zone3_z_bottom, shell_arch_bore_z_peak - zone3_z_bottom))


def build_lower_soda_inner_cut() -> cq.Workplane:
    """Straight soda-tube passage from the donor outlet into the swept neck."""
    return soda_faucet_tube_cyl(zone3_z_bottom, zone5_z_top + 0.5 - zone3_z_bottom)


@functools.lru_cache(maxsize=None)
def _tube_envelope(kind, diameter, bottom_z=-6.2, sign=1):
    wire = _paths.path_wire(kind, bottom_z, sign)
    start = wire.Edges()[0].startPoint()
    plane = cq.Plane(origin=start, xDir=(1,0,0), normal=(0,0,1))
    return cq.Workplane(plane).circle(diameter/2).sweep(cq.Workplane(obj=wire), transition="round")


def build_flavor_transition_inner_cut():
    return _tube_envelope("flavor", flavor_tube_hole_dia, zone3_z_bottom-0.5, 1).union(
           _tube_envelope("flavor", flavor_tube_hole_dia, zone3_z_bottom-0.5, -1))


def build_flavor_entry_relief():
    """Taper each lower bore mouth before its curved return begins."""
    z0, z1 = zone3_z_bottom - 0.5, _paths.LOWER_START_Z
    if z1 <= z0:
        raise ValueError("The flavor bore entry must precede the lower return")
    cutters = []
    for sign in (1, -1):
        origin = _paths.lower_point(z0, "flavor", sign)
        end = _paths.lower_point(z1, "flavor", sign)
        if math.dist(origin[:2], end[:2]) > 1e-7:
            raise ValueError("The flavor bore entry must remain vertical")
        cutters.append(cq.Solid.makeCone(
            flavor_tube_hole_dia / 2.0 + 0.05,
            flavor_tube_hole_dia / 2.0,
            z1 - z0, cq.Vector(*origin), cq.Vector(0, 0, 1)))
    return cq.Workplane(obj=cq.Compound.makeCompound(cutters))


def _ribbon_section(point, tangent, width, clearance):
    plane=cq.Plane(origin=point,xDir=(1,0,0),normal=tangent)
    wp=cq.Workplane(plane)
    return (wp.slot2D(signal_lane_width,signal_lane_depth) if clearance
            else wp.rect(width,signal_ribbon_max_depth)).val()


def _ribbon_lower_frame(z):
    dz=0.001
    a=_paths.lower_point(z-dz,"ribbon")
    b=_paths.lower_point(z+dz,"ribbon")
    tangent=tuple((v-u)/(2*dz) for u,v in zip(a,b))
    return _paths.lower_point(z,"ribbon"),tangent,signal_ribbon_max_width


def _ribbon_arc_frame(s):
    point=_paths.tube_arc_point(s,"ribbon")
    ds=0.001
    a=_paths.tube_arc_point(s-ds,"ribbon")
    b=_paths.tube_arc_point(s+ds,"ribbon")
    tangent=tuple((v-u)/(2*ds) for u,v in zip(a,b))
    return point,tangent,_paths.positions(s)[4]


def _ribbon_transition(frame_fn,start,end,clearance,section=_ribbon_section):
    # Ruled sections only cover the short quintic offsets. A 0.3 mm pitch
    # keeps their chord error below the print surface tolerance.
    count=max(2,math.ceil((end-start)/0.3))
    return "loft",[section(*frame_fn(start+(end-start)*i/count),clearance)
                   for i in range(count+1)]


def _ribbon_straight(z0,z1,clearance,section=_ribbon_section):
    point,_,width=_ribbon_lower_frame(z0)
    return "extrude",section(point,(0,0,1),width,clearance),(0,0,z1-z0)


def _ribbon_constant_arc(s0,s1,n,width,clearance,section=_ribbon_section):
    a=_paths.JOINT_ANGLE+s0/_paths.WATER_RADIUS
    b=_paths.JOINT_ANGLE+s1/_paths.WATER_RADIUS
    start,mid,end=[_paths.arc_point(t,n=n) for t in (a,(a+b)/2,b)]
    return "sweep",section(start,(0,-math.sin(a),math.cos(a)),width,clearance),(start,mid,end)


def _ribbon_spans(clearance=False,bottom_z=38.8,section=_ribbon_section):
    """The cable's spans up the neck, bottom first, as what each is cut from: `("extrude",
    section, rise)` for a straight run, `("loft", sections)` for an offset transition, ruled,
    and `("sweep", section, arc points)` for a constant arc."""
    end_angle=_path_total_rot-math.asin(
        (display_ribbon_join_s-gn_tip_straight_len)/(gn_bend1_r+signal_lane_center_n))
    end_s=(end_angle-_paths.JOINT_ANGLE)*_paths.WATER_RADIUS
    arc_start_s=-_paths.JOINT_ANGLE*_paths.WATER_RADIUS
    parts=[_ribbon_straight(bottom_z,_paths.LOWER_START_Z,clearance,section),
           _ribbon_transition(_ribbon_lower_frame,_paths.LOWER_START_Z,_paths.LOWER_END_Z,clearance,section),
           _ribbon_straight(_paths.LOWER_END_Z,_paths.ARC_START_Z,clearance,section),
           _ribbon_constant_arc(arc_start_s,_paths.CONVERGE_START_S,
                                _paths.TIGHT_RIBBON_N,signal_ribbon_max_width,clearance,section)]
    parts.extend([
        _ribbon_transition(_ribbon_arc_frame,_paths.CONVERGE_START_S,
                           _paths.CONVERGE_START_S+_paths.RIBBON_CONVERGE_LENGTH,clearance,section),
        _ribbon_constant_arc(_paths.CONVERGE_START_S+_paths.RIBBON_CONVERGE_LENGTH,
                             end_s,_paths.FACE_RIBBON_N,signal_ribbon_max_width,clearance,section)])
    return parts


def _ribbon_span_solid(span):
    if span[0]=="extrude":
        return cq.Solid.extrudeLinear(span[1],[],cq.Vector(*span[2]))
    if span[0]=="loft":
        return cq.Solid.makeLoft(span[1],ruled=True)
    edge=cq.Edge.makeThreePointArc(*(cq.Vector(*p) for p in span[2]))
    return cq.Solid.sweep(span[1],[],cq.Wire.assembleEdges([edge]),makeSolid=True,isFrenet=False)


def _ribbon_span_solids(clearance=False,bottom_z=38.8):
    return [_ribbon_span_solid(span) for span in _ribbon_spans(clearance,bottom_z)]


@functools.lru_cache(maxsize=None)
def _ribbon_envelope(clearance=False,bottom_z=38.8):
    parts=_ribbon_span_solids(clearance,bottom_z)
    if not all(p.isValid() and len(p.Solids())==1 for p in parts):
        raise ValueError("each cable/lane transition must be one valid native solid")
    result=parts[0].fuse(*parts[1:],tol=1e-5).clean()
    if not result.isValid() or len(result.Solids())!=1:
        raise ValueError("the cable/lane spans must join as one valid native solid")
    return cq.Workplane(obj=result)


def build_signal_transition_inner_cut():
    return _ribbon_envelope(True)


def build_signal_transition_ribbon():
    return _ribbon_envelope(False)


def _arc_from_tangent(start, tangent, radius, theta_rad, ccw):
    """(mid, end, end_tangent) for a 2D arc from `start` along `tangent`, sweeping `theta_rad` at `radius`."""
    sign = +1 if ccw else -1
    if ccw:
        perp = (-tangent[1], tangent[0])
    else:
        perp = (tangent[1], -tangent[0])
    center = (start[0] + radius * perp[0], start[1] + radius * perp[1])
    rad = (start[0] - center[0], start[1] - center[1])

    def _rot(v, a):
        c, s = math.cos(a), math.sin(a)
        return (v[0] * c - v[1] * s, v[0] * s + v[1] * c)

    rad_mid = _rot(rad, sign * theta_rad / 2.0)
    rad_end = _rot(rad, sign * theta_rad)

    mid = (center[0] + rad_mid[0], center[1] + rad_mid[1])
    end = (center[0] + rad_end[0], center[1] + rad_end[1])
    end_tangent = _rot(tangent, sign * theta_rad)
    return mid, end, end_tangent


# Gooseneck path plane (Y-Z, X=0). Local (a, b) ↔ world (-Y, +Z);
# bending CW from the +Z tangent bends toward -Y (toward the user).
_path_plane = cq.Plane(
    origin=(0, 0, 0),
    xDir=(0, -1, 0),    # local +X = world -Y (forward, toward user)
    normal=(-1, 0, 0),  # local +Y = world +Z (normal × xDir = +Z)
)


# Gooseneck sweep profile plane: normal = +Z, local (X, Y) = world (X, Y).
_profile_plane = cq.Plane(
    origin=(0, 0, 0),
    xDir=(1, 0, 0),
    normal=(0, 0, 1),
)


def _gooseneck_path_at_origin(tip_length: float | None = None,
                             *, bend_sweep_rad: float | None = None) -> cq.Workplane:
    """Gooseneck path in path-local (a, b): vertical lift, circular arc,
    tip straight. Origin (s=0) lands in world at
    (0, soda_faucet_tube_y, zone5_z_top)."""
    z_lift = gn_bend1_z_start - zone5_z_top
    tip_length = gn_tip_straight_len if tip_length is None else tip_length
    bend_sweep_rad = _path_total_rot if bend_sweep_rad is None else bend_sweep_rad

    p_bottom = (0.0, 0.0)
    p_bend_start = (0.0, z_lift)

    arc_mid, arc_end, tip_tangent = _arc_from_tangent(
        p_bend_start, (0.0, 1.0), gn_bend1_r, bend_sweep_rad, ccw=False
    )
    tip_end = (arc_end[0] + tip_length * tip_tangent[0],
               arc_end[1] + tip_length * tip_tangent[1])

    path = (
        cq.Workplane(_path_plane)
        .moveTo(*p_bottom)
        .lineTo(*p_bend_start)
        .threePointArc(arc_mid, arc_end)
    )
    if tip_length > 1e-8:
        path = path.lineTo(*tip_end)
    return path.wire()


def _tube_shell_outer_sketch() -> cq.Sketch:
    """Circular neck enclosing the soda, flavor-pair and signal-cable passages."""
    return cq.Sketch().push([(0.0, tube_shell_center_y)]).circle(tube_shell_outer_r)


def _tube_shell_inner_circles(*, include_signal=True, station=0.0):
    return _shell_data("_tube_shell_inner_circles", include_signal=include_signal, station=station)


def _tube_shell_inner_sketch(*, include_signal=True, station=0.0):
    """One smooth bundle opening, with the flavors in a shared capsule.

    Tangent hull faces remove the thin dividers between tube and ribbon
    clearances. The complete rounded profiles, rather than their centres,
    define this opening; no bore-intersection cusp is retained as stock.
    """
    sketch = cq.Sketch()
    for x, y, r in _tube_shell_inner_circles(include_signal=include_signal, station=station):
        sketch = sketch.arc((x, y), r, 0.0, 360.0)
    return sketch.hull().clean()


def _sweep_along_gooseneck(sketch: cq.Sketch) -> cq.Workplane:
    """`sketch` swept along the gooseneck path, placed at the zone-5 seam
    (0, soda_faucet_tube_y, zone5_z_top)."""
    profile = cq.Workplane(_profile_plane).placeSketch(sketch)
    swept = profile.sweep(_gooseneck_path_at_origin(), transition="right")
    return swept.translate((0, soda_faucet_tube_y, zone5_z_top))


def build_display_neck_reference(shrink: float = 0.0) -> cq.Workplane:
    """Constant circular head profile used by its cover, lips and grooves."""
    sketch = cq.Sketch().push([(0.0, tube_shell_center_y)]).circle(
        display_neck_outer_r - shrink)
    return _sweep_along_gooseneck(sketch)


def build_zone6_outer() -> cq.Workplane:
    """Uniform circular stem, bend and dispense tip."""
    return _sweep_along_gooseneck(_tube_shell_outer_sketch())


@functools.lru_cache(maxsize=None)
def build_zone6_inner_cut():
    """Lower flavor return into the smooth shared gooseneck opening."""
    return build_flavor_transition_inner_cut().intersect(_lower_neck_halfspace())


def _lower_neck_halfspace():
    return cq.Workplane(obj=cq.Solid.makeBox(
        400.0,400.0,500.0,cq.Vector(-200.0,-200.0,zone5_z_top+0.5-500.0)))


def _ribbon_end_station():
    return _shell_data('_ribbon_end_station', args=[])


def _bundle_stations(s0, s1):
    return _shell_data('_bundle_stations', args=[s0, s1])


def _bundle_opening_loft(s0, s1, *, include_signal):
    """Smooth opening around the complete tube and optional ribbon profiles."""
    wires = []
    for station in _bundle_stations(s0, s1):
        origin, xdir, tangent = _paths.station_plane(station)
        plane = cq.Plane(origin=origin, xDir=xdir, normal=tangent)
        section = _tube_shell_inner_sketch(include_signal=include_signal,station=station)
        wires.append(section._faces.Faces()[0].outerWire().transformShape(plane.rG))
    return cq.Workplane(obj=cq.Solid.makeLoft(wires, ruled=False))


# How far below the cable's exit the beverage outlets start, inside the shared passage.


@functools.lru_cache(maxsize=None)
def build_beverage_interstice_cut():
    """Smooth flavor capsule and soda opening beyond the display-ribbon exit."""
    end = _paths.CONVERGE_START_S + _paths.CONVERGE_LENGTH
    profile = _tube_shell_inner_sketch(include_signal=False,station=end)
    return _sweep_along_gooseneck(profile).intersect(
        _station_halfspace(_ribbon_end_station()-beverage_lead, 0.0, 1))


def build_upstream_interstice_cut():
    """Open the ribbon lane into the shared smooth bundle passage."""
    end = _paths.CONVERGE_START_S + _paths.CONVERGE_LENGTH
    ribbon_end_s = _ribbon_end_station()
    profile = _tube_shell_inner_sketch()
    lower = _sweep_along_gooseneck(profile).intersect(
        _station_halfspace(_paths.CONVERGE_START_S, 0.0, -1))
    upper = _bundle_opening_loft(_paths.CONVERGE_START_S,end,include_signal=True)
    outlet = (_sweep_along_gooseneck(_tube_shell_inner_sketch(station=end))
              .intersect(_station_halfspace(end,0.0,1))
              .intersect(_station_halfspace(ribbon_end_s,0.0,-1)))
    return lower.union(upper, clean=False, tol=1e-6).union(outlet, clean=False, tol=1e-6)


def drain_return_point(angle=None):
    return _paths.tube_arc_point(_paths.DRAIN_CUT_S,"drain")


def drain_exit_angle():
    return split_junction_rot+_paths.DRAIN_CUT_S/gn_bend1_r


def build_drain_neck_path(bottom_z=-6.2, *, cutter=False):
    return cq.Workplane(obj=_paths.path_wire("drain",bottom_z))


def build_drain_neck(diameter=None,bottom_z=-6.2,*,cutter=False):
    diameter=_faucet_interface.drain_tube_hole_dia if diameter is None else diameter
    return _tube_envelope("drain",diameter,bottom_z)


def build_signal_neck_inner_cut():
    """Lower flat ribbon return into the shared smooth neck opening."""
    return _ribbon_envelope(True).intersect(_lower_neck_halfspace())


def build_signal_neck_ribbon():
    return _ribbon_envelope(False)


def _round_cavity_segment(s0,s1,radius=_paths.CAVITY_RADIUS):
    a=split_junction_rot+s0/gn_bend1_r
    b=split_junction_rot+s1/gn_bend1_r
    start,mid,end=[_paths.arc_point(t,n=tube_shell_center_y) for t in (a,(a+b)/2,b)]
    edge=cq.Edge.makeThreePointArc(cq.Vector(*start),cq.Vector(*mid),cq.Vector(*end))
    plane=cq.Plane(origin=start,xDir=(1,0,0),normal=(0,-math.sin(a),math.cos(a)))
    return cq.Workplane(plane).circle(radius).sweep(cq.Workplane(obj=cq.Wire.assembleEdges([edge])))


def _gland_plane(s,z):
    midpoint=s+_paths.GLAND_MID_SHIFT_S
    origin,xdir,tangent=_paths.station_plane(midpoint,center_n=tube_shell_center_y)
    origin=tuple(p+(z-_paths.GLAND_BODY_MID_Z)*t for p,t in zip(origin,tangent))
    return origin,xdir,tangent


def _gland_world(local,s):
    origin,xdir,tangent=_gland_plane(s,0)
    plane=cq.Plane(origin=origin,xDir=xdir,normal=tangent)
    return cq.Workplane(obj=local.val().transformShape(plane.rG))


def _gland_halfspace(s,z,sign):
    origin,_,tangent=_gland_plane(s,z)
    return _split_plane_halfspace(origin,tangent,sign)


@functools.lru_cache(maxsize=None)
def build_vent_cavity():
    """Retained round-pocket geometry for the archived insertion-tool reader.

    This cavity is not subtracted from the current faucet shell.
    """
    rounded=_round_cavity_segment(-0.01,_paths.CONVERGE_START_S+_paths.CONVERGE_LENGTH)
    us,ds=_paths.DRIP_POCKET_ENTRY_S,_paths.DRIP_POCKET_EXIT_S
    thickness=_paths.DRIP_GUIDE_WALL_THICKNESS
    dry_in=rounded.intersect(_drip_guide_halfspace(us,0,-1))
    pocket=(rounded.intersect(_drip_guide_halfspace(us,thickness,1))
                   .intersect(_drip_guide_halfspace(ds,0,-1)))
    dry_out=rounded.intersect(_drip_guide_halfspace(ds,thickness,1))
    return dry_in.union(pocket).union(dry_out)


def _station_halfspace(station,offset,sign):
    origin,_,tangent=_paths.station_plane(station,center_n=tube_shell_center_y)
    origin=tuple(p+offset*t for p,t in zip(origin,tangent))
    return _split_plane_halfspace(origin,tangent,sign)


def _drip_guide_halfspace(station,offset,sign):
    return _station_halfspace(station,offset,sign)


# How far behind the drain's square-cut mouth its relief starts.


def build_drain_terminal_relief():
    """Local open space beyond the square-cut drain mouth."""
    end = _paths.tube_arc_point(_paths.DRAIN_CUT_S, "drain")
    _, xdir, tangent = _paths.station_plane(_paths.DRAIN_CUT_S)
    plane = cq.Plane(origin=end, xDir=xdir, normal=tangent)
    return (cq.Workplane(plane).workplane(offset=-drain_relief_lead)
            .circle(_faucet_interface.drain_tube_hole_dia / 2.0)
            .extrude(_paths.DRIP_END_CLEARANCE_MM + drain_relief_lead))


# How far inside the curved soda-clearance wall the vent outlet starts, so it opens across the
# complete 4 mm hole. A shallow flat start leaves thin crescents beside that curvature.


def _vent_outlet_frame():
    return _shell_data('_vent_outlet_frame', args=[])


@functools.lru_cache(maxsize=None)
def build_vent_outlet():
    """Round underside hole opening into the common tube-passage clearance."""
    origin, normal, inner_offset = _vent_outlet_frame()
    plane=cq.Plane(origin=origin,xDir=(1,0,0),normal=normal)
    return (cq.Workplane(plane).workplane(offset=inner_offset)
            .circle(_paths.DRIP_HOLE_DIAMETER/2)
            .extrude(tube_shell_outer_r + wall_thickness_min))


def _tube_shell_outer_shrunk_sketch(shrink: float) -> cq.Sketch:
    """_tube_shell_outer_sketch offset inward by `shrink` mm (centers fixed)."""
    return cq.Sketch().push([(0.0, tube_shell_center_y)]).circle(tube_shell_outer_r - shrink)


def _build_zone6_outer_shrunk(shrink: float) -> cq.Workplane:
    """Gooseneck outer with the cross-section offset inward by `shrink`."""
    return _sweep_along_gooseneck(_tube_shell_outer_shrunk_sketch(shrink))


def _split_plane_halfspace(origin: tuple, normal: tuple, sign: int,
                           extent: float = 600.0) -> cq.Workplane:
    """Solid filling one side of a plane: sign +1 = +normal side, -1 = −normal side."""
    plane = cq.Plane(
        origin=cq.Vector(*origin),
        xDir=cq.Vector(1, 0, 0),  # world X lies in the plane (normal is in YZ)
        normal=cq.Vector(*normal),
    )
    return cq.Workplane(plane).rect(2.0 * extent, 2.0 * extent).extrude(sign * extent)


def _sweep_segment_in_path_local(
    start_yz: tuple,
    tangent_yz: tuple,
    path_workplane: cq.Workplane,
    sketch: cq.Sketch,
) -> cq.Workplane:
    """`sketch` swept along `path_workplane`, profile perpendicular to
    `tangent_yz` at `start_yz` (path-local 2D on _path_plane), placed at
    world (0, soda_faucet_tube_y, zone5_z_top)."""
    # tangent in world (X, Y, Z) — path-local (a, b) → world (-a, b)
    normal = (0.0, -tangent_yz[0], tangent_yz[1])
    xdir = (1.0, 0.0, 0.0)
    plane = cq.Plane(
        origin=cq.Vector(0.0, -start_yz[0], start_yz[1]),
        xDir=cq.Vector(*xdir),
        normal=cq.Vector(*normal),
    )
    profile = cq.Workplane(plane).placeSketch(sketch)
    swept = profile.sweep(path_workplane, transition="right")
    return swept.translate((0, soda_faucet_tube_y, zone5_z_top))


def _bend_overlap_subarc(start_yz: tuple, mid_yz: tuple) -> cq.Workplane:
    """Bend-2 sub-arc from `start_yz` through `mid_yz` to `_path_junction`, path-local (a, b)."""
    return (
        cq.Workplane(_path_plane)
        .moveTo(*start_yz)
        .threePointArc(mid_yz, _path_junction)
        .wire()
    )


def _build_bend_overlap(sketch: cq.Sketch, *, side: str) -> cq.Workplane:
    """`sketch` swept along the split_<side>_overlap_len mm of bend 2
    below the junction. `side` "socket" (longer) or "plug" (shorter)."""
    if side == "socket":
        start_yz, mid_yz, tan_start = _path_socket_start, _path_socket_mid, _tan_at_socket_start
    elif side == "plug":
        start_yz, mid_yz, tan_start = _path_plug_start, _path_plug_mid, _tan_at_plug_start
    else:
        raise ValueError(f"side must be 'socket' or 'plug', got {side!r}")
    return _sweep_segment_in_path_local(
        start_yz, tan_start, _bend_overlap_subarc(start_yz, mid_yz), sketch,
    )


# ============================================================
# DISPLAY CRADLE — pocket + collar on the dispense tip
# ============================================================
# Tip frame: s runs up-gooseneck from the tube exit, n points out through
# the display face, and x is world X. The headerless vendor components,
# corrected to the caliper PCB height, clear the real tubes by 1.80064 mm.
# Four small feet pads support the display; the space over the tubes is open.
# The vendor USB-C shell extends beyond the PCB and housing's lower end.
# Bounds use the device's centred XY / feet-Z frame.


# Retain the neck's snap datums while the display and bezel move outward.


# Rear lower edge: s = s0 + ds_dn * n.


# Factory assembly: place the display in the open cover, approach from the
# outlet at S=-slide, translate along S while lifted, then seat along -N.
# A 9.5 mm factory lift clears the complete relaxed cover from the round neck
# by 0.566 mm throughout the axial approach, before normal seating.


# Viewed from the glass, the cable termination is in the southwest corner.


def _tip_frame_data():
    return _shell_data('_tip_frame_data', args=[])


def _tip_frame():
    """(tube exit, up-gooseneck tangent, outward display normal)."""
    return tuple(cq.Vector(*point) for point in _tip_frame_data())


def _cradle_prism(half_x: float, s0: float, s1: float, n0: float, n1: float,
                  corner_r: float = 0.0) -> cq.Workplane:
    tip_end, _, n_hat = _tip_frame()
    plane = cq.Plane(origin=tip_end, xDir=cq.Vector(1, 0, 0), normal=n_hat)
    sketch = cq.Sketch().push([(0.0, (s0 + s1) / 2.0)]).rect(2.0 * half_x, s1 - s0)
    if corner_r > 0.0:
        sketch = sketch.reset().vertices().fillet(corner_r)
    return cq.Workplane(plane).workplane(offset=n0).placeSketch(sketch).extrude(n1 - n0)


def _display_world(native: cq.Workplane) -> cq.Workplane:
    """Place a native (x, s, n) solid in the assembled faucet frame."""
    tip_end, _, n_hat = _tip_frame()
    plane = cq.Plane(origin=tip_end, xDir=(1.0, 0.0, 0.0), normal=n_hat)
    return cq.Workplane(obj=native.val().transformShape(plane.rG))


def _display_outline_wire(width: float, length: float, radius: float,
                          n: float, *, center_s: float = _display_cover_center_s) -> cq.Wire:
    """Matched eight-edge rounded outline for the shallow display shroud."""
    h, r = width / 2.0, radius
    a = center_s - length / 2.0
    b = center_s + length / 2.0
    q = r / math.sqrt(2.0)
    return (cq.Workplane("XY").workplane(offset=n)
            .moveTo(-h + r, a).lineTo(h - r, a)
            .threePointArc((h - r + q, a + r - q), (h, a + r))
            .lineTo(h, b - r)
            .threePointArc((h - r + q, b - r + q), (h - r, b))
            .lineTo(-h + r, b)
            .threePointArc((-h + r - q, b - r + q), (-h, b - r))
            .lineTo(-h, a + r)
            .threePointArc((-h + r - q, a + r - q), (-h + r, a))
            .close().val())


def build_display_outer_envelope() -> cq.Workplane:
    """Tapered rounded display shroud."""
    rows = (
        (display_cover_skirt_width, display_cover_skirt_length,
         display_cover_skirt_r, display_cover_bottom_n),
        (display_cover_skirt_width, display_cover_skirt_length,
         display_cover_skirt_r, display_cover_shoulder_n),
        (display_cover_face_width, display_cover_face_length,
         display_cover_face_r, display_cover_top_n),
    )
    loft = _display_world(cq.Workplane(obj=cq.Solid.makeLoft(
        [_display_outline_wire(*row) for row in rows], ruled=False)))
    return loft.intersect(_cradle_prism(
        30.0, display_head_s_min, display_head_s_max + 1.0, -30.0, 40.0))


# The display's clearance under the bezel: its (width, length, corner radius, n) rows about the
# housing's centre, and the prism (half x, s0, s1, n0, n1) that stands its rear wall upright.


def build_display_cover_inner_envelope() -> cq.Workplane:
    """Display clearance below the bezel with a vertical rear wall."""
    loft = _display_world(cq.Workplane(obj=cq.Solid.makeLoft(
        [_display_outline_wire(*row, center_s=_display_housing_center_s)
         for row in display_cover_inner_rows], ruled=False)))
    return loft.intersect(_cradle_prism(*display_cover_inner_clamp))


def build_display_neck_clearance() -> cq.Workplane:
    """The shroud's open lip follows the round neck without a square shoe."""
    return build_display_neck_reference(-display_cover_slip)


def build_display_feet_pads() -> cq.Workplane:
    """Four bearing pads with their inner walls flush to the open channel."""
    solids = []
    h = display_foot_pad_width / 2.0
    for x, s in display_foot_centers:
        outer_x = abs(x) + h
        inner_x = min(abs(x) - h, display_channel_half_width)
        solids.append(_cradle_prism(
            (outer_x - inner_x) / 2.0, s - h, s + h,
            display_feet_n - display_foot_pad_depth,
            display_feet_n).translate((math.copysign((outer_x + inner_x) / 2.0, x), 0.0, 0.0)).val())
    return cq.Workplane(obj=cq.Compound.makeCompound(solids))


def build_display_cover_lips() -> cq.Workplane:
    """Broad lips with relieved inner corners and flat bearing lands."""
    band = _cradle_prism(display_cover_skirt_width / 2.0 + 1.0,
                         display_clip_s_bottom, display_clip_s_top,
                         display_clip_bottom_n, display_clip_top_n)
    inner = build_display_neck_reference(display_neck_outer_r - display_clip_lip_radius)
    lips = build_display_outer_envelope().intersect(band).cut(inner)
    return relieve_display_lip_inner_edges(lips)


def relieve_display_lip_inner_edges(lips: cq.Workplane) -> cq.Workplane:
    """Chamfer the root's top and bottom corners, retaining flat outer lands."""
    origin, _, normal = _tip_frame()
    inner_edges = []
    for face in lips.val().Faces():
        if face.geomType() not in ("CYLINDER", "TORUS"):
            continue
        for edge in face.Edges():
            stations = [(vertex.Center() - origin).dot(normal) for vertex in edge.Vertices()]
            if any(stations and all(abs(n - plane) < 1e-6 for n in stations)
                   and abs((edge.Center() - origin).dot(normal) - plane) < 1e-6
                   for plane in (display_clip_bottom_n, display_clip_top_n)):
                if not any(edge.isSame(existing) for existing in inner_edges):
                    inner_edges.append(edge)
    if not inner_edges:
        raise ValueError("display lips have no inner N-plane corners")
    return cq.Workplane(obj=lips.val().chamfer(
        _display_snap.LIP_INNER_EDGE_RELIEF, None, inner_edges))


# How far past the neck each groove's band reaches across X; how far the device opening stands
# over the cover's top; how far the open channel rises into the device opening.


def build_display_retention_grooves() -> cq.Workplane:
    """Side grooves with preload roots, flat floors and retaining shoulders."""
    band = _cradle_prism(display_neck_outer_r + display_groove_reach,
                         display_clip_s_bottom - _display_snap.END_SLIP,
                         display_clip_s_top + _display_snap.END_SLIP,
                         display_clip_bottom_n,
                         display_clip_top_n + _display_snap.BEARING_SLIP)
    core = build_display_neck_reference(display_neck_outer_r - display_clip_groove_radius)
    return band.cut(core)


def _display_cavity() -> cq.Workplane:
    # Keep the open underside and ribbon route at their fixed neck datum.
    # Only the four existing bearing pads extend to the raised display seat.
    device_opening = _cradle_prism(
        display_neck_outer_r + wall_thickness_min, dispense_face_thickness, display_s_top,
        display_seat_reference_n, display_cover_top_n + display_pocket_overrun,
    ).cut(build_display_feet_pads())
    open_channel = _cradle_prism(
        display_channel_half_width, dispense_face_thickness, display_s_top,
        0.0, display_seat_reference_n + display_channel_overlap)
    return device_opening.union(open_channel)


def build_display_usb_keepout() -> cq.Workplane:
    """Conservative connector envelope from the vendor STEP, without fit clearance."""
    low, high = display_usb_reference_bounds
    return _cradle_prism(
        (high[0] - low[0]) / 2.0,
        _display_housing_center_s + low[1], _display_housing_center_s + high[1],
        display_floor_n + low[2], display_floor_n + high[2],
    ).translate(((low[0] + high[0]) / 2.0, 0.0, 0.0))


def _display_ribbon_frames(width: float, depth: float, top_n: float):
    return _shell_data('_display_ribbon_frames', args=[width, depth, top_n])


def _display_ribbon_sections(width: float, depth: float, top_n: float):
    wires = []
    for section in _display_ribbon_frames(width, depth, top_n):
        plane = cq.Plane(origin=section["origin"], xDir=section["xdir"], normal=section["normal"])
        wires.append(cq.Workplane(plane).rect(*section["rect"]).val())
    return wires


def _display_ribbon_sweep(width: float, depth: float, top_n: float) -> cq.Workplane:
    return cq.Workplane(obj=cq.Solid.makeLoft(_display_ribbon_sections(width, depth, top_n),
                                              ruled=True))


# The cable's top: the factory wire fan-out beside the PCB, short of its measured underside.


def build_display_ribbon_transition() -> cq.Workplane:
    """Maximum SIG-6 envelope up to the factory wire fan-out beside the PCB."""
    return _display_ribbon_sweep(signal_ribbon_max_width, signal_ribbon_max_depth,
                                 display_ribbon_top_n)


def build_lever_overhead_clearance() -> cq.Workplane:
    """Circular overhead relief above the lever's resting top."""
    front_y = fill_y_min - math.sqrt(
        back_arch_r ** 2 - (lever_rest_top_z - back_arch_center_z) ** 2)
    front_angle = math.atan2(lever_rest_top_z - back_arch_center_z,
                             front_y - fill_y_min)
    rear_z = back_arch_center_z + math.sqrt(
        back_arch_r ** 2 - (lever_clearance_y_back - fill_y_min) ** 2)
    rear_angle = math.atan2(rear_z - back_arch_center_z,
                            lever_clearance_y_back - fill_y_min)
    mid_angle = (front_angle + rear_angle) / 2.0
    mid = (fill_y_min + back_arch_r * math.cos(mid_angle),
           back_arch_center_z + back_arch_r * math.sin(mid_angle))
    return (_vertical_plane(-lever_clearance_x_half)
            .moveTo(front_y, lever_rest_top_z)
            .threePointArc(mid, (lever_clearance_y_back, rear_z))
            .lineTo(lever_clearance_y_back, lever_rest_top_z)
            .lineTo(front_y, lever_rest_top_z).wire()
            .extrude(2.0 * lever_clearance_x_half))


def build_lever_front_clearance() -> cq.Workplane:
    """Open central span ahead of the rounded neck cap, above the resting lever."""
    opening = cq.Solid.makeBox(
        2.0 * lever_clearance_x_half, fill_y_min - lever_insertion_front_y,
        zone5_z_top - lever_rest_top_z,
        cq.Vector(-lever_clearance_x_half, lever_insertion_front_y, lever_rest_top_z))
    cap = cq.Solid.makeCylinder(
        shell_outer_r, zone5_z_top - lever_rest_top_z,
        cq.Vector(0.0, zone45_front_y + shell_outer_r, lever_rest_top_z))
    # The straight lower entry stays open up to the neck shoulder. Leaving a
    # rounded cap below that shoulder creates a thin strip against the water
    # bore; the lever has no bearing or retention surface in this upper span.
    lower_entry = cq.Solid.makeBox(
        2.0 * lever_clearance_x_half, fill_y_min - lever_insertion_front_y,
        zone5_z_bottom - lever_rest_top_z,
        cq.Vector(-lever_clearance_x_half, lever_insertion_front_y, lever_rest_top_z))
    return cq.Workplane(obj=opening.cut(cap).fuse(lower_entry))


def _lever_outline():
    return _shell_data('_lever_outline', args=[])


def build_lever_clearance() -> cq.Workplane:
    """Lever travel, overhead relief and straight front insertion corridor."""
    x_half = lever_clearance_x_half
    return (_vertical_plane(-x_half).polyline(_lever_outline()).close()
            .extrude(2.0 * x_half)
            .union(build_lever_overhead_clearance())
            .union(build_lever_front_clearance()))


def _tube_shell_outer_section(z_bottom: float, z_height: float) -> cq.Workplane:
    """Circular tube-shell cross-section extruded vertically over the Z range."""
    return (
        _horizontal_plane(z_bottom)
        .moveTo((0.0, soda_faucet_tube_y + tube_shell_center_y))
        .circle(tube_shell_outer_r)
        .extrude(z_height)
    ).unwrap()


def _tube_shell_inner_section(z_bottom: float, z_height: float) -> cq.Workplane:
    """The complete tube and ribbon passage extruded vertically."""
    return (cq.Workplane(_profile_plane).workplane(offset=z_bottom)
            .placeSketch(_tube_shell_inner_sketch()).extrude(z_height)
            .translate((0.0, soda_faucet_tube_y, 0.0)))


# ============================================================
# PUBLIC SHELL BUILDERS
# ============================================================

def _native_cache_path():
    """Bind the expensive Boolean body to its executable CAD inputs."""
    import vent_seals
    import world_workplane
    import OCP
    drivers = (Path(__file__), Path(_paths.__file__), Path(_faucet_interface.__file__),
               Path(vent_seals.__file__), Path(_display_snap.__file__),
               Path(fits.__file__), Path(world_workplane.__file__))
    digest = hashlib.sha256()
    digest.update(f"{cq.__version__}:{OCP.__version__}".encode())
    for path in drivers:
        tree = ast.parse(path.read_text())
        # Docgen refreshes prose during export without changing the CAD.
        for node in ast.walk(tree):
            if isinstance(node, (ast.Module, ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                if node.body and isinstance(node.body[0], ast.Expr) and isinstance(node.body[0].value, ast.Constant) and isinstance(node.body[0].value.value, str):
                    node.body = node.body[1:]
        digest.update(path.name.encode())
        digest.update(ast.dump(tree, include_attributes=False).encode())
    root = next(p for p in _here.parents if (p / "tools" / "docgen").is_dir())
    return root / ".cache" / "native-faucet" / digest.hexdigest() / "full.brep"


def _cad_progress(message):
    if os.environ.get("HSM_CAD_PROGRESS") == "1":
        print(message, flush=True)


def _keep_brep(shape, path):
    """Write `shape` to `path` when the disk allows it. A sandboxed build step cannot write
    outside its declared outputs, and the body it built is the same whether or not it is kept."""
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        temporary = path.with_name(f"{path.stem}.{os.getpid()}{path.suffix}")
        shape.exportBrep(str(temporary))
        temporary.replace(path)
    except OSError:
        pass


def build_shell() -> cq.Workplane:
    """Complete unsplit reference body; the accessible curved joint defines its two prints."""
    cached = _native_cache_path()
    if cached.is_file() and os.environ.get("HSM_CAD_REFRESH") != "1":
        try:
            native = cq.Shape.importBrep(str(cached))
            if native.isValid() and len(native.Solids()) == 1:
                _cad_progress(f"Shell: source-bound native cache {cached.parent.name[:12]}")
                return cq.Workplane(obj=native)
        except Exception:
            pass
    started = time.monotonic()
    _cad_progress("Shell: outer stock")
    outer_parts = [
        build_lower_outer().val(),
        build_zone6_outer().val(),
        build_display_feet_pads().val(),
    ]
    outer = cq.Workplane(obj=outer_parts[0].fuse(*outer_parts[1:]))
    _cad_progress(f"Shell: outer valid={outer.val().isValid()}, solids={len(outer.val().Solids())}")
    cutters = (
        ("donor lower bore", build_zone1_inner_cut),
        ("mounting screws", build_base_pod_holes),
        ("donor shoulder", build_zone2_inner_cut),
        ("donor upper bores", build_zone3_inner_cut),
        ("drain mouth clearance", build_drain_terminal_relief),
        ("underside fault outlet", build_vent_outlet),
        ("lever motion", build_lever_clearance),
        ("display pocket", _display_cavity),
        ("display retention", build_display_retention_grooves),
        ("lower common bundle opening", build_lower_signal_lane),
        ("shared smooth upper passage", build_upstream_interstice_cut),
        ("smooth beverage outlets", build_beverage_interstice_cut),
    )
    part = outer.val()
    for name, builder in cutters:
        _cad_progress(f"Shell: construct {name} ({time.monotonic()-started:.1f}s)")
        cutter = builder().val()
        _cad_progress(f"Shell: cut {name} ({time.monotonic()-started:.1f}s)")
        part = part.cut(cutter, tol=1e-5)
        _cad_progress(f"Shell: after {name}: valid={part.isValid()}, solids={len(part.Solids())}")
        if not part.isValid():
            diagnostic = cached.with_name("invalid-" + name.replace(" ", "-") + ".brep")
            _keep_brep(part, diagnostic)
            raise ValueError(f"shell cut {name!r} produced an invalid native body; "
                             f"diagnostic={diagnostic}")
    # Keep the exact spline/straight transition boundaries from the native
    # cuts. Same-domain face merging is unnecessary for the printed surface.
    if not part.isValid() or len(part.Solids()) != 1:
        _keep_brep(part, cached.with_name("invalid-full.brep"))
        raise ValueError(f"shell Boolean body: valid={part.isValid()}, "
                         f"solid volumes={[s.Volume() for s in part.Solids()]}; "
                         f"diagnostic={cached.with_name('invalid-full.brep')}")
    _keep_brep(part, cached)
    _cad_progress(f"Shell: native body complete ({time.monotonic()-started:.1f}s)")
    return cq.Workplane(obj=part)


def build_shell_base(full_shell=None):
    """Base carries the open female socket at the midpoint of the bend."""
    full=full_shell if full_shell is not None else build_shell()
    below=_split_plane_halfspace(
        (0.0,split_junction_y,split_junction_z),split_normal,-1)
    socket=_build_bend_overlap(
        _tube_shell_outer_shrunk_sketch(split_socket_shrink),side="socket")
    base=full.intersect(below, clean=False).cut(socket, clean=False)
    base=base.val()
    if not base.isValid() or len(base.Solids()) != 1:
        raise ValueError("The relieved faucet base must be one valid solid")
    return cq.Workplane(obj=base)


def build_shell_tip(full_shell=None):
    """Tip carries the arc-guided male plug, smooth passages and display pocket."""
    full=full_shell if full_shell is not None else build_shell()
    above=_split_plane_halfspace((0,split_junction_y,split_junction_z),split_normal,1)
    plug_outer=_build_bend_overlap(
        _tube_shell_outer_shrunk_sketch(split_plug_shrink),side="plug")
    plug=full.val().intersect(plug_outer.val(),tol=1e-6)
    joined=full.val().intersect(above.val()).fuse(plug,tol=1e-6)
    # Heal microscopic Boolean seam faces below the 0.005 mm print-mesh
    # deflection, so the close-fitting passages survive STEP round-tripping.
    from OCP.ShapeFix import ShapeFix_FixSmallFace
    healer = ShapeFix_FixSmallFace()
    healer.Init(joined.wrapped)
    healer.SetPrecision(0.001)
    healer.SetMaxTolerance(0.001)
    healer.Perform()
    joined = cq.Shape.cast(healer.FixShape())
    return cq.Workplane(obj=joined)


def print_height(stl: Path, build_rot: float) -> float:
    _cadq_export.note_read(stl)
    return _shell_data("print_height", path=str(stl), args=[build_rot])


# Absolute millimetre deflection and angular deflection of the printable surface.


def piece_mesh(solid) -> trimesh.Trimesh:
    """Absolute-tolerance print mesh, on a copy without cached triangulation."""
    import numpy as np
    from OCP.BRep import BRep_Tool
    from OCP.BRepMesh import BRepMesh_IncrementalMesh
    from OCP.TopAbs import TopAbs_REVERSED
    from OCP.TopLoc import TopLoc_Location

    solid = solid.val() if hasattr(solid, "val") else solid
    meshed = solid.copy(mesh=False)
    triangulator = BRepMesh_IncrementalMesh(
        meshed.wrapped, piece_mesh_tol, False, piece_mesh_angle, False)
    if not triangulator.IsDone():
        raise ValueError("the absolute-tolerance print triangulation did not finish")
    points, tris = [], []
    for face in meshed.Faces():
        location = TopLoc_Location()
        poly = BRep_Tool.Triangulation_s(face.wrapped, location)
        if poly is None or poly.NbTriangles() == 0:
            raise ValueError("a printable face has no triangulation")
        offset = len(points)
        transform = location.Transformation()
        for i in range(1, poly.NbNodes()+1):
            point = poly.Node(i).Transformed(transform)
            points.append((point.X(), point.Y(), point.Z()))
        for i in range(1, poly.NbTriangles()+1):
            a, b, c = poly.Triangle(i).Get()
            if face.wrapped.Orientation() == TopAbs_REVERSED:
                b, c = c, b
            tris.append((offset+a-1, offset+b-1, offset+c-1))
    # Binary STL stores float32 vertices. Weld in that same precision so
    # sub-micron Boolean slivers cannot collapse into duplicate STL sheets.
    mesh = trimesh.Trimesh(vertices=np.asarray(points, dtype=np.float32),
                           faces=tris, process=True)
    mesh.merge_vertices()
    mesh.update_faces(mesh.area_faces > 0.0)
    # Boolean tangencies can tessellate microscopic internal sheets twice,
    # with opposite normals. Cancel only those exact opposing triangle pairs;
    # they enclose no stock and have no printable surface.
    _, inverse, counts = np.unique(
        np.sort(mesh.faces, axis=1), axis=0, return_inverse=True, return_counts=True)
    keep = np.ones(len(mesh.faces), dtype=bool)
    for group in np.flatnonzero(counts == 2):
        faces = np.flatnonzero(inverse == group)
        if (max(mesh.area_faces[faces]) < 1e-5 and
                np.dot(*mesh.face_normals[faces]) < -0.999999):
            keep[faces] = False
    mesh.update_faces(keep)
    mesh.remove_unreferenced_vertices()
    return mesh


def write_bed_file(solid, path):
    """The printed surface, checked as serialized STL before replacing the bed file."""
    path = Path(path)
    mesh = piece_mesh(solid)
    data = mesh.export(file_type="stl")
    written = trimesh.load_mesh(io.BytesIO(data), file_type="stl")
    loose = _flute_skin.non_manifold_edges(written)
    print(f"-> {path.name}  ({len(mesh.faces)} facets, "
          f"{'watertight' if written.is_watertight else 'NOT WATERTIGHT'})")
    if loose or not written.is_watertight:
        raise ValueError(
            f"{path.name}: a slicer refuses this — {loose} non-manifold edge(s), "
            f"watertight={written.is_watertight}, over {len(written.faces)} facets")
    path.write_bytes(data)
    return mesh


def lower_bundle_numbers():
    return _shell_data("lower_bundle_numbers")
