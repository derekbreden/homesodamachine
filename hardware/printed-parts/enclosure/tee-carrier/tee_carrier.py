"""Two PET-GF carrier halves: a 6 mm web with a top flange, station troughs for the four tees,
a full-height centre lap closed by two M3 screws from the open rear, and a return spring in
each service tab.

The four tees bear on one Y plane: the floor line of a vertical trough cut into the web's fore
face at each tee station. The web behind that line is `station_t`; everywhere else it is
`web_t`. A shelf on the web's aft face, over the inner aft coils, stiffens the span between the
two inner tees. Each service tab is a solid bar with a blind channel in its fore face; the
return spring rides in that channel and bears fore on a seat in the enclosure's flank recess.
The springs' load enters the bars and none of it crosses the web.

All geometry is in the enclosure frame: +Y aft, +Z up. Each half enters the loose enclosure
from its open rear with its spring already in the bar, lowers behind the fixed body, slides
fore to the aft stop, and seats outward into its side recess. The right half's web meets the
left half's full-height tongue on that stop; two M3 x 10 screws driven from the open rear close
the lap. The handholds finish flush with the enclosure; their retaining rims bear behind the
wall, and the fixed body's flat lands and the handholds' top and bottom faces guide Y travel.
"""

from __future__ import annotations

import math
import sys
from dataclasses import dataclass
from pathlib import Path

import cadquery as cq

_here = Path(__file__).resolve()
_hw = next(p for p in _here.parents if p.name == "hardware")
sys.path[:0] = [str(_here.parent), str(_hw / "scripts"), str(_hw / "reference" / "tee-connector"),
               str(_here.parent.parent / "enclosure")]
from _cadq_export import export_assembly
from _material_base import M_PETGF_BLACK, one_body
import _enclosure_interface as enclosure_interface
import fits
import tee_connector as tee
import tee_carrier_spring as spring


@dataclass(frozen=True)
class CarrierSpec:
    tee_xs: tuple[float, ...]
    tee_axis_z: float
    web_x: tuple[float, float]
    bearing_y: float
    web_z: tuple[float, float]
    tab_outer_x: float
    tab_z: tuple[float, float]
    # The web behind the bearing line at a tee station, and the web everywhere else.
    station_t: float = enclosure_interface.tee_carrier_station_t
    web_t: float = 6.0
    # Radial air between a tee arm and the walls of its trough.
    station_air: float = 0.5
    # The bowed stub above each tee stands this far fore of the bearing line at release, less
    # its air; the relief above the arm floors there.
    stub_relief_depth: float = 3.004166
    stub_air: float = 0.3
    # The shelf on the aft face: it reaches to the outer aft coils and stands over the inner.
    flange_x: float = 56.820
    flange_z0: float = 209.075
    flange_depth: float = 14.0
    tie_band_offsets_z: tuple[float, float] = (-12.0, 12.0)
    tie_slot_offset_x: float = tee.HALF_W + 1.64
    tie_slot_x: float = 1.5
    tie_slot_z: float = 3.5
    tie_stock_w: float = 2.5
    tie_stock_t: float = 1.0
    tie_head: tuple[float, float, float] = (5.0, 3.6, 2.8)
    # Established printed guide and loading route. Replacement spring measurements check
    # these dimensions; they do not move the fixed/moving bearing planes or guide axes.
    spring_bore_d: float = 6.57
    # The spring enters its bar sideways at this compressed length, through a window in the
    # inboard face that ends on the web's fore plane; the channel runs past it by one ring.
    spring_load_length: float = 9.61
    spring_window_air: float = 2.0 * fits.slip
    spring_ring: float = 1.1
    spring_roof_angle_deg: float = 45.0
    fixed_seat_depth: float = 2.0
    release_offset_y: float = tee.CARRIER_RELEASE_OFFSET
    connected_offset_y: float = tee.CARRIER_CONNECTED_OFFSET
    park_offset_y: float = tee.CARRIER_PARK_OFFSET
    aft_overtravel_y: float = enclosure_interface.tee_carrier_aft_overtravel
    fixed_plate_aft_y: float = 82.690
    aft_coil_fore_y: float = 119.990
    exterior_x: float = 107.5
    guide_inner_x: float = 98.5
    slide_air: float = fits.running
    finger_run: float = 16.0
    finger_air: float = 0.2
    grip_bar_t: float = 16.0
    grip_back_x: float = 91.000
    grip_back_t: float = 3.0
    grip_aft_t: float = 3.0
    grip_rail_top_z: float = 175.05
    grip_shoulder_rise: float = 6.0
    grip_rim_t: float = 3.0
    grip_wall_t: float = 3.0
    grip_overlap: float = 4.0
    grip_top_overlap: float = 3.0
    grip_edge_r: float = 2.0
    grip_root_overlap: float = 0.2
    entry_inset_x: float | None = None
    entry_staging_y: float = 38.550
    entry_lift_z: float = 70.0
    joint_lap_t: float = 6.0
    # The screw axis stands inside the coil-free band behind the web's centre; the right web
    # keeps this much beside the clearance hole, and the two webs part by the entry inset.
    joint_screw_x: float = 0.0
    joint_web_ligament: float = 1.0
    # The lower screw stands this far up the web; the upper one stands under the shelf with
    # its head and this much web between.
    joint_screw_inset_z: float = 9.0
    joint_head_shelf_air: float = 1.0
    joint_screw_length: float = 10.0
    bed_x: float = 325.0
    bed_y: float = 320.0
    bed_z: float = 320.0

    @property
    def web_aft_y(self):
        return self.bearing_y + self.station_t

    @property
    def web_fore_y(self):
        return self.web_aft_y - self.web_t

    @property
    def trough_r(self):
        return tee.HALF_W + self.station_air

    @property
    def trough_axis_y(self):
        return self.bearing_y - self.trough_r

    @property
    def stub_relief_y(self):
        return self.bearing_y - self.stub_relief_depth

    @property
    def stub_relief_z0(self):
        return self.tee_axis_z + tee.RUN_HALF - self.stub_air

    @property
    def trough_top_z(self):
        """The tee's upper run end plus axial air; the shallower tube relief continues above."""
        return self.tee_axis_z + tee.RUN_HALF + self.stub_air

    @property
    def flange_y(self):
        return self.web_aft_y, self.web_aft_y + self.flange_depth

    @property
    def flange_z(self):
        return self.flange_z0, self.web_z[1]

    @property
    def aft_limit_offset_y(self):
        return self.connected_offset_y + self.aft_overtravel_y

    @property
    def finger_y(self):
        return self.web_aft_y, self.web_aft_y + self.finger_run

    @property
    def tab_y(self):
        return self.web_aft_y - self.grip_bar_t, self.web_aft_y

    @property
    def grip_y(self):
        return self.tab_y

    @property
    def grip_z(self):
        # The upper retention rim also retreats from the supported recess roof.
        # Shorten the bar/opening together to retain the full overlap below it.
        return self.tab_z[0], self.tab_z[1] - 2 * fits.supported_surface

    @property
    def printed_grip_z(self):
        """Supported bar and aft-wall underside; the opening retains its nominal lower datum."""
        return self.grip_z[0] + fits.supported_surface, self.grip_z[1]

    @property
    def printed_rim_z(self):
        return (self.rim_z[0] + fits.supported_surface,
                self.rim_z[1] - fits.supported_surface)

    @property
    def printed_backing_z(self):
        return self.backing_z[0], self.backing_z[1] - fits.supported_surface

    @property
    def printed_root_bottom_z(self):
        return self.grip_rail_top_z + fits.supported_surface

    @property
    def aft_x(self):
        return self.grip_back_x, self.exterior_x - self.grip_wall_t - self.slide_air

    @property
    def aft_y(self):
        return self.finger_y[1], self.finger_y[1] + self.grip_aft_t

    @property
    def backing_y(self):
        return (self.tab_y[1] - self.grip_root_overlap,
                max(self.aft_y[1], self.finger_y[1] + self.park_offset_y
                    - self.release_offset_y + self.slide_air))

    @property
    def backing_z(self):
        return self.web_z[0], self.rim_z[1]

    @property
    def rim_y(self):
        margin = self.park_offset_y - self.release_offset_y + self.grip_overlap
        return self.grip_y[0] - margin, self.grip_y[1]

    @property
    def rim_z(self):
        margin = self.grip_top_overlap + self.slide_air
        return self.grip_rail_top_z + self.grip_shoulder_rise, self.tab_z[1] + margin

    @property
    def rim_x(self):
        outer = self.exterior_x - self.grip_wall_t - self.slide_air
        return outer - self.grip_rim_t, outer

    @property
    def spring_x(self):
        """The bore axis stands one backing wall and its air inboard of the bar's inboard face."""
        return self.grip_back_x + self.grip_back_t + self.slide_air + self.spring_bore_d / 2.0

    @property
    def spring_z(self):
        """The channel stands just above the tee arms' top collets, so a spring can come down
        the outer well past the seated tee and cross to the window over the arm's top."""
        return (self.tee_axis_z + tee.RUN_HALF + 2.0 * self.slide_air
                + self.spring_bore_d / 2.0)

    @property
    def spring_window_y(self):
        return self.grip_y[0], self.web_fore_y

    @property
    def spring_bore_depth(self):
        return self.spring_window_y[1] - self.grip_y[0] + self.spring_ring

    @property
    def spring_bore_floor_y(self):
        return self.grip_y[0] + self.spring_bore_depth

    @property
    def fixed_seat_mouth_y(self):
        """The flank recess's fore wall: where the rim's fore end stands at release, less air."""
        return self.rim_y[0] + self.release_offset_y - self.slide_air

    @property
    def fixed_seat_floor_y(self):
        return self.fixed_seat_mouth_y - self.fixed_seat_depth

    @property
    def joint_z(self):
        return self.web_z

    @property
    def joint_right_x0(self):
        """The right web's inboard edge: one ligament beside the screws' clearance holes."""
        return (self.joint_screw_x - enclosure_interface.screw_clear_dia / 2.0
                - self.joint_web_ligament)

    @property
    def joint_split_x(self):
        """The left web's inboard edge: the right web passes it on its inset slide."""
        return self.joint_right_x0 - self.entry_shoulder_inset_x - 2.0 * self.slide_air

    @property
    def joint_receiver_x(self):
        return self.joint_right_x0, self.joint_reach_x

    @property
    def joint_tongue_x(self):
        """The tongue runs from just outboard of the left inner tee's inboard tie slot to just
        short of the right inner tee, which the left half passes on its own inset slide."""
        inner = min(x for x in self.tee_xs if x > 0.0)
        return (-(inner - self.tie_slot_offset_x - self.tie_slot_x / 2.0 - self.slide_air),
                self.joint_reach_x)

    @property
    def joint_reach_x(self):
        inner = min(x for x in self.tee_xs if x > 0.0)
        return inner - tee.HALF_W - self.entry_shoulder_inset_x - 2.0 * self.slide_air

    @property
    def joint_screw_zs(self):
        return (self.web_z[0] + self.joint_screw_inset_z,
                self.flange_z0 - enclosure_interface.head_cbore_dia / 2.0
                - self.joint_head_shelf_air)

    @property
    def grip_root_x(self):
        return (min(self.web_x[1] - self.grip_root_overlap, self.grip_back_x),
                max(self.web_x[1], self.grip_back_x + self.grip_root_overlap))

    @property
    def state_offsets_y(self):
        return (self.release_offset_y, 0.0, self.connected_offset_y, self.park_offset_y,
                self.aft_limit_offset_y)

    @property
    def joint_face_y(self):
        return self.web_fore_y

    @property
    def joint_fore_y(self):
        return self.joint_face_y - self.joint_lap_t

    @property
    def joint_head_seat_y(self):
        return self.web_aft_y

    @property
    def entry_shift_x(self):
        if self.entry_inset_x is not None:
            return self.entry_inset_x
        # Lower the bar on the outer tee-well axis before seating it outward.
        return (self.grip_back_x + self.tab_outer_x) / 2.0 - max(self.tee_xs)

    @property
    def entry_shoulder_inset_x(self):
        return self.grip_wall_t + self.slide_air

    @property
    def capture_probe_angle(self):
        """Rotation just beyond the bar's clearance between its opposed flat guides."""
        run = self.grip_bar_t / 2.0 - self.grip_edge_r
        height = (self.printed_grip_z[1] - self.printed_grip_z[0]) / 2.0
        air = self.slide_air + fits.supported_surface
        reach = math.hypot(run, height)
        return math.degrees(math.atan2(run, height)
                            - math.acos((height + air) / reach)) + 0.1


DEFAULT_SPEC = CarrierSpec(
    tee_xs=(-82.10, -22.35, 22.35, 82.10), tee_axis_z=186.174,
    web_x=(-94.0, 94.0), bearing_y=111.790, web_z=(167.174, 222.425),
    tab_outer_x=107.5, tab_z=(175.050, 226.119),
)


@dataclass(frozen=True)
class TieSite:
    tee_x: float
    band_z: float
    slot_xs: tuple[float, float]
    head_side: int


def _box(x0: float, x1: float, y0: float, y1: float, z0: float, z1: float):
    return cq.Workplane(
        obj=cq.Solid.makeBox(
            x1 - x0,
            y1 - y0,
            z1 - z0,
            cq.Vector(x0, y0, z0),
        )
    )


def tie_sites(spec: CarrierSpec) -> tuple[TieSite, ...]:
    """The eight ties and their sixteen through-slot axes.

    The heads face the open gaps between adjacent tees. The outermost slots lie behind the
    collar tangent and stop before the full handhold backing; their opening need not stand
    beyond the collar's widest X. No head occupies the coil clearance behind the web.
    """
    sites = []
    outer = max(abs(x) for x in spec.tee_xs)
    limit = spec.grip_back_x - spec.slide_air - spec.tie_slot_x / 2.0
    for tee_x in spec.tee_xs:
        side = -1 if tee_x < 0 else 1
        is_outer = abs(tee_x) == outer
        slots = [tee_x - spec.tie_slot_offset_x, tee_x + spec.tie_slot_offset_x]
        if is_outer:
            slots[0 if side < 0 else 1] = side * limit
        for dz in spec.tie_band_offsets_z:
            sites.append(TieSite(tee_x, spec.tee_axis_z + dz, tuple(slots),
                                 -side if is_outer else side))
    return tuple(sites)


def tie_head_envelopes(spec=DEFAULT_SPEC):
    """Declared 5 × 3.6 × 2.8 mm locks, beside the collar and fore of the web."""
    width, depth, height = spec.tie_head
    shapes = []
    for site in tie_sites(spec):
        x = site.tee_x + site.head_side * (tee.HALF_W + spec.slide_air + width / 2.0)
        shapes.append(_box(x - width / 2.0, x + width / 2.0,
                           spec.web_fore_y - depth, spec.web_fore_y,
                           site.band_z - height / 2.0, site.band_z + height / 2.0).val())
    return tuple(shapes)


def _teardrop_y(
    x: float,
    y0: float,
    z: float,
    diameter: float,
    length: float,
    angle_deg: float,
):
    """A +Y round passage with a tangent, support-free roof for a +Z print.

    The spring still sees the complete circular lower and side profile.  Above the circle,
    two tangent roof faces meet at `angle_deg`, replacing the circle's down-facing crown.
    """
    radius = diameter / 2.0
    angle = math.radians(angle_deg)
    tangent_x = radius * math.sin(angle)
    tangent_z = radius * math.cos(angle)
    peak_z = radius / math.cos(angle)

    circle = cq.Workplane(
        obj=cq.Solid.makeCylinder(
            radius,
            length,
            cq.Vector(x, y0, z),
            cq.Vector(0.0, 1.0, 0.0),
        )
    )
    # This plane's local Y is world +Z and its normal is world -Y.  Extruding a negative
    # distance therefore sends the triangular roof along world +Y with the round passage.
    plane = cq.Plane(origin=(0.0, y0, 0.0), xDir=(1.0, 0.0, 0.0), normal=(0.0, -1.0, 0.0))
    roof = (
        cq.Workplane(plane)
        .polyline(
            (
                (x - tangent_x, z + tangent_z),
                (x + tangent_x, z + tangent_z),
                (x, z + peak_z),
            )
        )
        .close()
        .extrude(-length)
    )
    return circle.union(roof)


def _tie_cutters(spec: CarrierSpec):
    """Sixteen through slots, with the station web between each pair carrying its tie."""
    slots = []
    proud = 0.1
    for site in tie_sites(spec):
        for slot_x in site.slot_xs:
            slots.append(
                _box(
                    slot_x - spec.tie_slot_x / 2.0,
                    slot_x + spec.tie_slot_x / 2.0,
                    spec.web_fore_y - proud,
                    spec.web_aft_y + proud,
                    site.band_z - spec.tie_slot_z / 2.0,
                    site.band_z + spec.tie_slot_z / 2.0 + fits.supported_surface,
                )
            )
    return tuple(slots)


def tie_back_envelopes(spec=DEFAULT_SPEC):
    """The eight straps crossing the full aft face between their through slots."""
    return tuple(_box(
        site.slot_xs[0] - spec.tie_stock_t / 2.0,
        site.slot_xs[1] + spec.tie_stock_t / 2.0,
        spec.web_aft_y, spec.web_aft_y + spec.tie_stock_t,
        site.band_z - spec.tie_stock_w / 2.0,
        site.band_z + spec.tie_stock_w / 2.0).val() for site in tie_sites(spec))


def _station_cutters(spec: CarrierSpec):
    """One vertical trough and one stub relief per tee station, cut into the web's fore face.

    The trough is the arm's own radius plus air about the arm's run axis, floored on the
    bearing line. The relief above the arm's top collet is a flat-floored box of the trough's
    width, standing off the bowed stub's aft face; the web behind it keeps more than the
    station thickness.
    """
    cutters = []
    for x in spec.tee_xs:
        cutters.append(cq.Workplane(obj=cq.Solid.makeCylinder(
            spec.trough_r, spec.trough_top_z - (spec.web_z[0] - 1.0),
            cq.Vector(x, spec.trough_axis_y, spec.web_z[0] - 1.0), cq.Vector(0.0, 0.0, 1.0))))
        cutters.append(_box(x - spec.trough_r, x + spec.trough_r,
                            spec.web_fore_y - 1.0, spec.stub_relief_y,
                            spec.stub_relief_z0, spec.web_z[1] + 1.0))
    return tuple(cutters)


def _service_tabs(spec):
    """Solid pull bars and backed finger spaces with fore shoulders, upper stop tongues and a
    blind spring bore in each bar's fore face."""
    body = _box(spec.grip_back_x, spec.tab_outer_x, *spec.grip_y, *spec.printed_grip_z)
    outer_edges = [edge for edge in body.val().Edges()
                   if abs(edge.Center().x - spec.tab_outer_x) < 1e-6
                   and edge.BoundingBox().zlen > spec.printed_grip_z[1] - spec.printed_grip_z[0] - 1e-6]
    body = cq.Workplane(obj=body.val().fillet(spec.grip_edge_r, outer_edges))
    body = body.union(_box(*spec.rim_x, *spec.rim_y, *spec.printed_rim_z))
    root = _box(*spec.grip_root_x, *spec.tab_y,
                spec.printed_root_bottom_z, spec.web_z[1])
    body = body.union(root)
    body = body.union(_box(spec.grip_back_x, spec.grip_back_x + spec.grip_back_t,
                           *spec.backing_y, *spec.printed_backing_z))
    body = body.union(_box(*spec.aft_x, *spec.aft_y, *spec.printed_grip_z))
    body = body.cut(_teardrop_y(
        spec.spring_x, spec.grip_y[0] - spec.slide_air, spec.spring_z, spec.spring_bore_d,
        spec.spring_bore_depth + spec.slide_air, spec.spring_roof_angle_deg))
    body = body.cut(_loading_window(spec))
    return body.mirror('YZ'), body


def _loading_window(spec):
    """The window in the bar's inboard face into the spring channel: the channel's inboard
    half over the loading length, its roof a plane at the channel roof's own angle rising
    inboard from the spring's crown on the channel axis. The whole round spring passes under
    it on its way to the axis."""
    radius = spec.spring_bore_d / 2.0
    angle = math.radians(spec.spring_roof_angle_deg)
    inboard_x = spec.grip_back_x - 1.0
    y0, y1 = spec.spring_window_y[0] - spec.slide_air, spec.spring_window_y[1]
    crown_z = spec.spring_z + radius
    plane = cq.Plane(origin=(0.0, y0, 0.0), xDir=(1.0, 0.0, 0.0), normal=(0.0, -1.0, 0.0))
    return (cq.Workplane(plane)
            .polyline(((inboard_x, spec.spring_z - radius), (spec.spring_x, spec.spring_z - radius),
                       (spec.spring_x, crown_z),
                       (inboard_x, crown_z + (spec.spring_x - inboard_x) * math.tan(angle))))
            .close().extrude(-(y1 - y0)))


PLACEMENT_FIELDS = (
    'tee_xs', 'tee_axis_z', 'web_x', 'bearing_y', 'web_z', 'tab_outer_x', 'tab_z',
    'station_t', 'web_t', 'station_air', 'stub_relief_depth', 'stub_air', 'flange_x',
    'flange_z0', 'flange_depth', 'grip_back_x', 'grip_rail_top_z', 'exterior_x',
    'guide_inner_x', 'release_offset_y', 'connected_offset_y', 'park_offset_y',
    'aft_overtravel_y', 'fixed_plate_aft_y', 'aft_coil_fore_y', 'entry_staging_y')


def placement_mismatches(spec, base=None, tol=0.01):
    """The fields on which `spec` and the printed default part differ by more than `tol`.

    The appliance reads the carrier it derives; the printer gets the default. They are the
    same part only while these agree; the assembly refuses a derived spec that has moved off
    the printed one."""
    base = DEFAULT_SPEC if base is None else base
    out = []
    for name in PLACEMENT_FIELDS:
        a, b = getattr(spec, name), getattr(base, name)
        a = a if isinstance(a, tuple) else (a,)
        b = b if isinstance(b, tuple) else (b,)
        if len(a) != len(b) or any(abs(x - y) > tol for x, y in zip(a, b)):
            out.append((name, getattr(spec, name), getattr(base, name)))
    return out


def joint_sites(spec=DEFAULT_SPEC):
    """The two lap screws: driven from the open rear, heads on the right web's aft face."""
    return tuple((spec.joint_screw_x, spec.joint_head_seat_y, z) for z in spec.joint_screw_zs)


def spring_stations(spec=DEFAULT_SPEC):
    """Each bar's bore axis and floor, and the fixed seat's floor it bears against."""
    return tuple({'x': side * spec.spring_x, 'z': spec.spring_z,
                  'bore_floor_y': spec.spring_bore_floor_y,
                  'seat_floor_y': spec.fixed_seat_floor_y,
                  'seat_mouth_y': spec.fixed_seat_mouth_y}
                 for side in (-1, 1))


def _cylinder_y(diameter, y0, y1, x, z):
    """Horizontal passage with its supported crown raised by the bridge allowance."""
    passage = cq.Solid.makeCylinder(diameter / 2.0, y1 - y0,
                                    cq.Vector(x, y0, z), cq.Vector(0.0, 1.0, 0.0))
    return passage.fuse(passage.translate((0.0, 0.0, fits.supported_surface)))


def _carrier_blank(spec):
    body = _box(*spec.web_x, spec.web_fore_y, spec.web_aft_y, *spec.web_z)
    body = body.union(_box(-spec.flange_x, spec.flange_x, *spec.flange_y, *spec.flange_z))
    for tab in _service_tabs(spec):
        body = body.union(tab)
    for cutter in _tie_cutters(spec):
        body = body.cut(cutter)
    for cutter in _station_cutters(spec):
        body = body.cut(cutter)
    return body


def build_half(spec=DEFAULT_SPEC, side=1):
    if side not in (-1, 1):
        raise ValueError('carrier half must be -1 or +1')
    split = spec.joint_split_x
    bb = _carrier_blank(spec)
    span = spec.tab_outer_x + spec.slide_air
    xa, xb = (-span, split) if side < 0 else (spec.joint_right_x0, span)
    bounds = bb.val().BoundingBox()
    body = bb.intersect(_box(xa, xb, bounds.ymin - 1.0, bounds.ymax + 1.0,
                            bounds.zmin - 1.0, bounds.zmax + 1.0))
    if side < 0:
        body = body.union(_box(*spec.joint_tongue_x,
                               spec.joint_fore_y, spec.joint_face_y, *spec.joint_z))
    for x, _seat_y, z in joint_sites(spec):
        if side < 0:
            body = body.cut(_cylinder_y(enclosure_interface.heatset_dia,
                                        spec.joint_face_y - enclosure_interface.heatset_len,
                                        spec.joint_face_y + spec.slide_air, x, z))
        else:
            body = body.cut(_cylinder_y(enclosure_interface.screw_clear_dia,
                                        spec.web_fore_y - 1.0, spec.web_aft_y + 1.0, x, z))
    return body


def build_carrier(spec=DEFAULT_SPEC):
    return cq.Workplane(obj=cq.Compound.makeCompound(
        [build_half(spec, side).val() for side in (-1, 1)]))


def build(spec=DEFAULT_SPEC):
    return build_carrier(spec)


def finger_probes(spec=DEFAULT_SPEC, offset_y=0.0, *, opening_aft_y=None):
    """Finger room beside the actual printed grip, including its supported-face relief."""
    probes = []
    inner = spec.grip_back_x + spec.grip_back_t + spec.finger_air
    outer = spec.tab_outer_x + 1.0
    z0, z1 = spec.printed_grip_z
    aft = spec.finger_y[1] + offset_y
    if opening_aft_y is not None:
        aft = min(aft, opening_aft_y)
    for side in (-1, 1):
        xa, xb = (inner, outer) if side > 0 else (-outer, -inner)
        probes.append(_box(xa, xb, spec.finger_y[0] + offset_y + spec.finger_air,
                           aft - spec.finger_air,
                           z0 + spec.finger_air,
                           z1 - spec.finger_air).val())
    return tuple(probes)


def arm_probes(spec=DEFAULT_SPEC):
    """Each tee arm at the bearing line: a run-axis cylinder of the tee's own radius."""
    return tuple(cq.Solid.makeCylinder(
        tee.HALF_W, 2.0 * tee.RUN_HALF,
        cq.Vector(x, spec.bearing_y - tee.HALF_W, spec.tee_axis_z - tee.RUN_HALF),
        cq.Vector(0.0, 0.0, 1.0)) for x in spec.tee_xs)


def spring_envelope(spec=DEFAULT_SPEC, side=1, *, tip_y, xz_air=0.0):
    """The spring in its bar, from its fore tip at `tip_y` to the channel's floor."""
    x = side * spec.spring_x
    r = spec.spring_bore_d / 2.0 + xz_air
    return _box(x - r, x + r, tip_y, spec.spring_bore_floor_y,
                spec.spring_z - r, spec.spring_z + r).val()


def insertion_envelopes(spec=DEFAULT_SPEC, side=1, *, xz_air=0.0):
    """Rectangular bounds enclosing each half's web, flange, tongue, root and grip walls.

    The assembly reads every segment of the inside-out route against the fixed body and
    seated tees. The bar's flat underside clears the seam rail across its full depth.
    """
    split = spec.joint_split_x
    web_x = ((spec.web_x[0], split) if side < 0
             else (spec.joint_right_x0, spec.web_x[1]))
    rows = [('web', web_x, (spec.web_fore_y, spec.web_aft_y), spec.web_z)]
    flange_x = ((-spec.flange_x, split) if side < 0
                else (spec.joint_right_x0, spec.flange_x))
    rows.append(('flange', flange_x, spec.flange_y, spec.flange_z))
    if side < 0:
        rows.append(('joint tongue', spec.joint_tongue_x,
                     (spec.joint_fore_y, spec.joint_face_y), spec.joint_z))

    def handed(xs):
        return xs if side > 0 else (-xs[1], -xs[0])

    rows.extend((
        ('grip root', handed(spec.grip_root_x), spec.tab_y,
         (spec.grip_rail_top_z, spec.web_z[1])),
        ('bar', handed((spec.grip_back_x, spec.tab_outer_x)),
         spec.grip_y, spec.grip_z),
        ('grip back', handed((spec.grip_back_x, spec.grip_back_x + spec.grip_back_t)),
         spec.backing_y, spec.backing_z),
        ('grip aft wall', handed(spec.aft_x), spec.aft_y, spec.grip_z),
        ('rim', handed(spec.rim_x),
         spec.rim_y, spec.rim_z)))
    return tuple((name, _box(xs[0] - xz_air, xs[1] + xz_air, *ys,
                             zs[0] - xz_air, zs[1] + xz_air).val())
                 for name, xs, ys, zs in rows)


def insertion_poses(spec=DEFAULT_SPEC, side=1, entry_y=None, rear_y=210.0):
    """Axis-aligned poses taking a complete half from the rear to its internal shoulder."""
    if entry_y is None:
        entry_y = spec.aft_limit_offset_y
    inset = -side * spec.entry_shift_x
    shoulder = -side * spec.entry_shoulder_inset_x
    return (
        ('open rear', (inset, rear_y, spec.entry_lift_z)),
        ('above outer well', (inset, spec.entry_staging_y, spec.entry_lift_z)),
        ('lowered behind tees', (inset, spec.entry_staging_y, 0.0)),
        ('behind wall shoulder', (shoulder, spec.entry_staging_y, 0.0)),
        ('aligned with opening', (shoulder, entry_y, 0.0)),
        ('seated outward', (0.0, entry_y, 0.0)),
    )


def insertion_sweeps(spec=DEFAULT_SPEC, side=1, entry_y=None, rear_y=210.0, *, xz_air=0.0):
    """Complete rectangular sweeps enclosing the whole half on every straight path segment.
    The springs are not yet in the bars."""
    poses = insertion_poses(spec, side, entry_y, rear_y)
    for (_before, start), (stage, end) in zip(poses, poses[1:]):
        if sum(abs(a - b) > 1e-8 for a, b in zip(start, end)) != 1:
            raise ValueError(f'{stage} must be a single-axis insertion segment')
        for name, shape in insertion_envelopes(spec, side, xz_air=xz_air):
            bb = shape.BoundingBox()
            spans = [(getattr(bb, axis + 'min') + min(a, b),
                      getattr(bb, axis + 'max') + max(a, b))
                     for axis, a, b in zip('xyz', start, end)]
            yield stage, name, _box(*spans[0], *spans[1], *spans[2]).val()


def interface(spec=DEFAULT_SPEC):
    slot_y = (spec.grip_y[0] + spec.release_offset_y,
              spec.finger_y[1] + spec.park_offset_y)
    slot_z = (spec.grip_z[0] - spec.slide_air, spec.grip_z[1] + spec.slide_air)
    return {
        'squeeze_offset_y': 0.0,
        'release_offset_y': spec.release_offset_y,
        'connected_offset_y': spec.connected_offset_y,
        'park_offset_y': spec.park_offset_y,
        'aft_limit_offset_y': spec.aft_limit_offset_y,
        'bearing_y': spec.bearing_y,
        'station_t': spec.station_t,
        'web_t': spec.web_t,
        'web_fore_y': spec.web_fore_y,
        'web_aft_y': spec.web_aft_y,
        'web_x': spec.web_x,
        'web_z': spec.web_z,
        'station_trough_r': spec.trough_r,
        'station_trough_axis_y': spec.trough_axis_y,
        'station_trough_top_z': spec.trough_top_z,
        'stub_relief_y': spec.stub_relief_y,
        'stub_relief_z0': spec.stub_relief_z0,
        'flange_x': spec.flange_x,
        'flange_y': spec.flange_y,
        'flange_z': spec.flange_z,
        'joint_z': spec.joint_z,
        'joint_work_fore_y': spec.joint_fore_y + spec.release_offset_y - spec.slide_air,
        'release_fore_stop_y': slot_y[0],
        'squeeze_reference_aft_y': spec.web_aft_y,
        'nominal_tongue_aft_y': spec.rim_y[1] + spec.connected_offset_y,
        'guide_body_y': spec.grip_y,
        'guide_body_z': spec.grip_z,
        'printed_guide_body_z': spec.printed_grip_z,
        'printed_grip_rim_z': spec.printed_rim_z,
        'printed_grip_back_z': spec.printed_backing_z,
        'printed_joint_z': spec.joint_z,
        'supported_surface_air': fits.supported_surface,
        'guide_bearing_length': spec.grip_y[1] - spec.grip_y[0],
        'guide_slide_air': spec.slide_air,
        'grip_bar_t': spec.grip_bar_t,
        'grip_pocket_depth': spec.tab_outer_x - spec.grip_back_x - spec.grip_back_t,
        'grip_back_x': spec.grip_back_x,
        'grip_back_t': spec.grip_back_t,
        'grip_back_y': spec.backing_y,
        'grip_back_z': spec.backing_z,
        'grip_aft_t': spec.grip_aft_t,
        'grip_aft_x': spec.aft_x,
        'grip_aft_y': spec.aft_y,
        'grip_rail_top_z': spec.grip_rail_top_z,
        'grip_rim_y': spec.rim_y,
        'grip_rim_z': spec.rim_z,
        'grip_rim_t': spec.grip_rim_t,
        'grip_rim_x': spec.rim_x,
        'grip_wall_t': spec.grip_wall_t,
        'grip_overlap': spec.grip_overlap,
        'grip_outer_x': spec.tab_outer_x,
        'grip_projection': spec.tab_outer_x - spec.exterior_x,
        'spring_seats': tuple((side * spec.spring_x, spec.spring_bore_floor_y, spec.spring_z)
                              for side in (-1, 1)),
        'spring_stations': spring_stations(spec),
        'spring_bore_d': spec.spring_bore_d,
        'spring_bore_depth': spec.spring_bore_depth,
        'spring_bore_mouth_y': spec.grip_y[0],
        'fixed_seat_depth': spec.fixed_seat_depth,
        'fixed_seat_mouth_y': spec.fixed_seat_mouth_y,
        'fixed_seat_floor_y': spec.fixed_seat_floor_y,
        'tab_slot_y_sweep': (spec.tab_y[0] + spec.release_offset_y,
                              spec.tab_y[1] + spec.park_offset_y),
        'tab_slot_z': spec.tab_z,
        'tab_pad_x': ((-spec.tab_outer_x, -spec.grip_back_x - spec.grip_back_t),
                     (spec.grip_back_x + spec.grip_back_t, spec.tab_outer_x)),
        'service_slot_x': (spec.exterior_x - spec.grip_wall_t, spec.exterior_x + 1.0),
        'service_slot_y': slot_y,
        'service_slot_z': slot_z,
        'half_entry_shift_x': spec.entry_shift_x,
        'half_install_order': (-1, 1),
        'half_entry_offsets_y': (spec.aft_limit_offset_y, spec.aft_limit_offset_y),
        'half_entry_staging_y': spec.entry_staging_y,
        'half_entry_lift_z': spec.entry_lift_z,
        'half_entry_shoulder_inset_x': spec.entry_shoulder_inset_x,
        'joint_sites': joint_sites(spec),
        'joint_reach_x': spec.joint_reach_x,
        'joint_receiver_x': spec.joint_receiver_x,
        'joint_tongue_x': spec.joint_tongue_x,
        'joint_split_x': spec.joint_split_x,
        'joint_screw_x': spec.joint_screw_x,
        'joint_screw_zs': spec.joint_screw_zs,
        'joint_face_y': spec.joint_face_y,
        'joint_fore_y': spec.joint_fore_y,
        'joint_head_seat_y': spec.joint_head_seat_y,
        'joint_screw_length': spec.joint_screw_length,
        'joint_insert_length': enclosure_interface.heatset_len,
        'joint_count': len(joint_sites(spec)),
        'finger_run': spec.finger_run,
        'finger_y': spec.finger_y,
        'spring_load_length': spec.spring_load_length,
        'spring_window_y': spec.spring_window_y,
        'spring_window_x': (spec.grip_back_x, spec.spring_x),
        'printed_parts': ('enclosure-tee-carrier-left', 'enclosure-tee-carrier-right'),
        'tie_sites': tuple({'tee_x': site.tee_x, 'band_z': site.band_z,
                            'slot_xs': site.slot_xs, 'head_side': site.head_side}
                           for site in tie_sites(spec)),
    }


def selftest(spec=DEFAULT_SPEC):
    errors = []
    halves = {side: build_half(spec, side).val() for side in (-1, 1)}
    for index, (site, head) in enumerate(zip(tie_sites(spec), tie_head_envelopes(spec)), 1):
        collar_air = cq.Solid.makeCylinder(
            tee.HALF_W + spec.slide_air, 2.0 * tee.RUN_HALF,
            cq.Vector(site.tee_x, spec.bearing_y - tee.HALF_W,
                      spec.tee_axis_z - tee.RUN_HALF), cq.Vector(0, 0, 1))
        if head.intersect(collar_air).Volume() > 1e-5:
            errors.append(f'tie {index} lock loses collar running clearance')
        for slot_x in site.slot_xs:
            slot = _box(slot_x-spec.tie_slot_x/2, slot_x+spec.tie_slot_x/2,
                        spec.web_fore_y-.1, spec.web_aft_y+.1,
                        site.band_z-spec.tie_slot_z/2,
                        site.band_z+spec.tie_slot_z/2+fits.supported_surface).val()
            if slot.intersect(collar_air).Volume() > 1e-5:
                errors.append(f'tie {index} slot loses collar running clearance')
        for side, half in halves.items():
            if head.intersect(half).Volume() > 1e-5:
                errors.append(f'tie {index} lock crosses carrier half {side:+d}')
    for side, solid in halves.items():
        bb = solid.BoundingBox()
        if len(solid.Solids()) != 1 or not solid.isValid():
            errors.append(f'half {side:+d} is not one valid solid')
        if bb.xlen > spec.bed_x or bb.ylen > spec.bed_y or bb.zlen > spec.bed_z:
            errors.append(f'half {side:+d} exceeds the print bed')
        if max(abs(bb.xmin), abs(bb.xmax)) > spec.exterior_x + 1e-6:
            errors.append(f'half {side:+d} projects beyond the enclosure width')
        show = [face for face in solid.Faces()
                if face.geomType() == 'PLANE'
                and abs(face.Center().x - side * spec.tab_outer_x) < 1e-6
                and face.normalAt().x * side > 0.999]
        if len(show) != 1 or show[0].innerWires():
            errors.append(f'half {side:+d} has no continuous flush bar face')
        elif abs(show[0].BoundingBox().zmin - spec.printed_grip_z[0]) > 1e-6:
            errors.append(f'half {side:+d} has material below the flat bar underside')
        xa, xb = sorted((side * (spec.grip_back_x + 0.1),
                         side * (spec.web_x[1] - 0.1)))
        root = _box(xa, xb, spec.web_fore_y + 0.1, spec.web_aft_y - 0.1,
                    spec.printed_root_bottom_z + 0.1, spec.web_z[1] - 0.1).val()
        if root.cut(solid).Volume() > 1e-5:
            errors.append(f'half {side:+d} lacks a solid bar root across the full web thickness')
        shifted = solid.translate((-side * spec.entry_shift_x, 0.0, 0.0)).BoundingBox()
        if max(abs(shifted.xmin), abs(shifted.xmax)) > spec.exterior_x - spec.slide_air:
            errors.append(f'half {side:+d} does not start inside the enclosure width')
        for slot in _tie_cutters(spec):
            if solid.intersect(slot.val()).Volume() > 1e-5:
                errors.append(f'half {side:+d} obstructs a tee tie slot')
        for site in tie_sites(spec):
            if (site.tee_x > 0) != (side > 0):
                continue
            backing = _box(
                site.slot_xs[0] + spec.tie_slot_x / 2.0,
                site.slot_xs[1] - spec.tie_slot_x / 2.0,
                spec.bearing_y, spec.web_aft_y,
                site.band_z - spec.tie_slot_z / 2.0,
                site.band_z + spec.tie_slot_z / 2.0).val()
            if backing.cut(solid).Volume() > 1e-5:
                errors.append(f'half {side:+d} has reduced tie backing at X{site.tee_x:g} Z{site.band_z:g}')
        for x, arm in zip(spec.tee_xs, arm_probes(spec)):
            if (x > 0) != (side > 0):
                continue
            if arm.intersect(solid).Volume() > 1e-5:
                errors.append(f'half {side:+d} crosses the tee arm at X{x:g}')
            beside = cq.Solid.makeCylinder(
                spec.trough_r - 0.01, 2.0 * tee.RUN_HALF,
                cq.Vector(x, spec.trough_axis_y, spec.tee_axis_z - tee.RUN_HALF),
                cq.Vector(0.0, 0.0, 1.0))
            if beside.intersect(solid).Volume() > 1e-5:
                errors.append(f'half {side:+d} leaves less than {spec.station_air:g} mm about the arm at X{x:g}')
            bearing = _box(x - 0.5, x + 0.5, spec.bearing_y + 0.01, spec.web_aft_y,
                           max(spec.web_z[0], spec.tee_axis_z - tee.RUN_HALF) + 0.5,
                           min(spec.web_z[1], spec.tee_axis_z + tee.RUN_HALF) - 0.5).val()
            if bearing.cut(solid).Volume() > 1e-5:
                errors.append(f'half {side:+d} lacks its station web behind the bearing line at X{x:g}')
            stub = _box(x - spec.trough_r + 0.001, x + spec.trough_r - 0.001,
                        spec.web_fore_y - 1.0, spec.stub_relief_y - 0.001,
                        spec.stub_relief_z0 + 0.001, spec.web_z[1]).val()
            if stub.intersect(solid).Volume() > 1e-5:
                errors.append(f'half {side:+d} stands inside the stub relief at X{x:g}')
            # The tube's air alone cannot establish a reinforced section. This positive
            # stock probe rejects a trough cut that continues above the tee through the
            # material the shallower relief is meant to retain.
            upper_backing = _box(
                x - spec.trough_r + 0.01, x + spec.trough_r - 0.01,
                spec.stub_relief_y + 0.01, spec.web_aft_y - 0.01,
                spec.trough_top_z + 0.01, spec.web_z[1] - 0.01).val()
            if upper_backing.cut(solid).Volume() > 1e-5:
                errors.append(f'half {side:+d} lacks retained upper backing at X{x:g}')
        flange = _box(*sorted((side * (spec.flange_x - 0.5), side * (abs(spec.joint_right_x0) + 0.5))),
                      spec.flange_y[0] + 0.1, spec.flange_y[1] - 0.1,
                      spec.flange_z[0] + 0.1, spec.flange_z[1] - 0.1).val()
        if side > 0 and flange.cut(solid).Volume() > 1e-5:
            errors.append(f'half {side:+d} lacks its full aft flange')
        beyond = _box(*sorted((side * spec.flange_x, side * spec.exterior_x)),
                      spec.web_aft_y + 0.001, spec.flange_y[1] + 1.0,
                      spec.flange_z[0], spec.flange_z[1]).val()
        beyond = beyond.cut(_box(*sorted((side * (spec.grip_back_x - 0.001), side * spec.exterior_x)),
                                 spec.web_aft_y - 1.0, spec.flange_y[1] + 2.0,
                                 spec.web_z[0], spec.web_z[1] + 1.0).val())
        if beyond.intersect(solid).Volume() > 1e-5:
            errors.append(f'half {side:+d} carries its flange past the outer aft coils')
        below = _box(*sorted((side * (abs(spec.joint_right_x0) + 0.5), side * (spec.grip_back_x - 0.001))),
                     spec.web_aft_y + 0.001, spec.flange_y[1] + 1.0,
                     spec.web_z[0], spec.flange_z[0] - 0.001).val()
        if below.intersect(solid).Volume() > 1e-5:
            errors.append(f'half {side:+d} stands aft of the web under the inner aft coils')
        bore = _box(side * spec.spring_x - 0.5, side * spec.spring_x + 0.5,
                    spec.grip_y[0] - 0.5, spec.spring_bore_floor_y - 0.001,
                    spec.spring_z - 0.5, spec.spring_z + 0.5).val()
        if bore.intersect(solid).Volume() > 1e-5:
            errors.append(f'half {side:+d} lacks its {spec.spring_bore_depth:g} mm spring bore')
        floor = _box(side * spec.spring_x - 0.5, side * spec.spring_x + 0.5,
                     spec.spring_bore_floor_y + 0.001, spec.grip_y[1] - 0.001,
                     spec.spring_z - 0.5, spec.spring_z + 0.5).val()
        if floor.cut(solid).Volume() > 1e-5:
            errors.append(f'half {side:+d} has no bar behind its spring bore')
    aft = spec.aft_limit_offset_y
    if halves[-1].intersect(halves[1]).Volume() > 1e-5:
        errors.append('the two assembled halves overlap')
    contact = halves[-1].intersect(halves[1].translate((0.0, -0.001, 0.0))).Volume()
    if contact < 0.1:
        errors.append('the lap has no mating bearing face')
    lap = _box(spec.joint_right_x0 + 0.5, spec.joint_reach_x - 0.5,
               spec.joint_face_y - 0.5, spec.joint_face_y + 0.5,
               spec.web_z[0] + 0.5, spec.web_z[1] - 0.5).val()
    for x, _seat_y, z in joint_sites(spec):
        lap = lap.cut(cq.Solid.makeCylinder(
            enclosure_interface.head_cbore_dia / 2.0, 2.0,
            cq.Vector(x, spec.joint_face_y - 1.0, z), cq.Vector(0.0, 1.0, 0.0)))
    if lap.cut(halves[-1]).cut(halves[1]).Volume() > 1e-5:
        errors.append('the lap is not closed over the full web height')
    screw_tip_y = spec.joint_head_seat_y - spec.joint_screw_length
    insert_end_y = spec.joint_face_y - enclosure_interface.heatset_len
    if not (spec.joint_fore_y < screw_tip_y <= insert_end_y + 1e-9):
        errors.append('joint screw does not engage the full insert with fore backing')
    if spec.joint_lap_t <= enclosure_interface.heatset_len:
        errors.append('the tongue has no material behind the insert')
    left_parked = halves[-1].translate((0.0, aft, 0.0))
    for stage, name, sweep in insertion_sweeps(spec, 1):
        if sweep.intersect(left_parked).Volume() > 1e-5:
            errors.append(f'right half {name} crosses the left half during {stage}')
    complete = build_carrier(spec).val()
    data = interface(spec)
    for dy in spec.state_offsets_y:
        for finger in finger_probes(spec, dy):
            if finger.intersect(complete.translate((0, dy, 0))).Volume() > 1e-5:
                errors.append(f'carrier obstructs finger contact at y={dy:g}')
        fore_overlap = data['service_slot_y'][0] - spec.rim_y[0] - dy
        top_overlap = (spec.printed_rim_z[1]
                       - (data['service_slot_z'][1] + fits.supported_surface))
        if fore_overlap < spec.grip_overlap - aft - 1e-6 or top_overlap < spec.grip_top_overlap - 1e-6:
            errors.append(f'grip retention overlap is only {fore_overlap:g}/{top_overlap:g} mm')
    for side, shape in halves.items():
        xa, xb = sorted((side * (spec.grip_back_x + spec.grip_back_t + spec.finger_air),
                         side * (spec.exterior_x + 1.0)))
        passage = _box(xa, xb, spec.finger_y[0] + spec.finger_air, spec.finger_y[1],
                       spec.grip_z[0] - 1.0, spec.rim_z[1] + 1.0).val()
        if passage.intersect(shape).Volume() > 1e-5:
            errors.append(f'half {side:+d} obstructs its open vertical finger passage')
        xa, xb = sorted((side * spec.grip_back_x,
                         side * (spec.grip_back_x + spec.grip_back_t)))
        backing = _box(xa, xb, *spec.backing_y, *spec.printed_backing_z).val()
        if backing.cut(shape).Volume() > 1e-5:
            errors.append(f'half {side:+d} lacks its full finger-pocket backing')
        xa, xb = sorted((side * spec.aft_x[0], side * spec.aft_x[1]))
        aft_wall = _box(xa, xb, *spec.aft_y, *spec.printed_grip_z).val()
        if spec.grip_aft_t < 3.0 or aft_wall.cut(shape).Volume() > 1e-5:
            errors.append(f'half {side:+d} lacks a continuous 3 mm aft wall')
        for dy in spec.state_offsets_y:
            if spec.backing_y[1] + dy < data['service_slot_y'][1] + spec.slide_air - 1e-6:
                errors.append(f'half {side:+d} exposes the enclosure behind its finger space')
    if spec.web_fore_y - spec.tie_head[1] - spec.slide_air < data['joint_work_fore_y']:
        errors.append('the tie heads stand fore of the lap work face')
    if spec.web_aft_y - spec.stub_relief_y < spec.station_t:
        errors.append('the stub relief leaves less than the station web')
    if spec.spring_ring < 1.0:
        errors.append('the spring channel keeps less than 1 mm of ring behind its window')
    try:
        spring.fit_facts(
            {str(offset): spec.spring_bore_floor_y + offset - spec.fixed_seat_floor_y
             for offset in spec.state_offsets_y},
            bore_diameter=spec.spring_bore_d, loading_length=spec.spring_load_length,
            required_radial_air=spec.slide_air)
    except ValueError as exc:
        errors.append(str(exc))
    if (spec.spring_window_y[1] - spec.spring_window_y[0]
            < spec.spring_load_length + spec.spring_window_air):
        errors.append('the loading window is shorter than the compressed spring and its air')
    for side, solid in halves.items():
        loaded = _box(*sorted((side * (spec.grip_back_x - 0.5), side * spec.spring_x)),
                      spec.spring_window_y[0] + 0.01, spec.spring_window_y[1] - 0.01,
                      spec.spring_z - spec.spring_bore_d / 2.0 + 0.01,
                      spec.spring_z + spec.spring_bore_d / 2.0 - 0.01).val()
        if loaded.intersect(solid).Volume() > 1e-5:
            errors.append(f'half {side:+d} has no open loading window into its spring channel')
        ring = _box(*sorted((side * (spec.grip_back_x + 0.5), side * (spec.spring_x - spec.spring_bore_d / 2.0 - 0.5))),
                    spec.spring_window_y[1] + 0.01, spec.spring_bore_floor_y - 0.01,
                    spec.spring_z - 0.5, spec.spring_z + 0.5).val()
        if ring.cut(solid).Volume() > 1e-5:
            errors.append(f'half {side:+d} has no ring behind its loading window')
    for error in errors:
        print('FAIL', error)
    if not errors:
        print(f'ok enclosure-tee-carrier: two valid halves, {spec.web_t:g} mm web with '
              f'{spec.station_t:g} mm stations and an aft flange, backed grips carrying their '
              f'springs, a full-height lap on two M3 x {spec.joint_screw_length:g} screws from '
              f'the rear, eight unobstructed tie paths')
    return int(bool(errors))


def _export_printed_part(body, name, spec=DEFAULT_SPEC):
    import enclosure as enclosure
    import _box_spec
    import trimesh
    from flute_payload import cut

    step = _here.parent / f'{name}.step'
    stl = _here.parent / f'{name}.stl'
    box, _bounds = _box_spec.read(enclosure.Box, enclosure.Bound,
                                  (enclosure.Pack, enclosure.PortField, enclosure.Nameplate))
    # Strike the show face on the enclosure's field at the connected resting pose.
    # The skin cuts inward; the opening, rounded hand contact and internal guides
    # retain their surfaces. Travel moves the finished grooves with the carrier.
    mesh = enclosure._piece_mesh(body.val())
    mesh.apply_translation((0.0, spec.connected_offset_y, 0.0))
    mesh = enclosure._flute_skin.flute(
        mesh, enclosure.flute_rails(box)[:1], enclosure.flute_pitch(box.outer),
        enclosure.flute_depth, enclosure.flute_rise)
    mesh.apply_translation((0.0, -spec.connected_offset_y, 0.0))
    mesh.export(str(stl))
    printed = trimesh.load_mesh(str(stl))
    if not printed.is_watertight or enclosure._flute_skin.non_manifold_edges(printed):
        raise ValueError(f'{name} fluted print is not a closed manifold mesh')
    export_assembly(one_body(body, name, M_PETGF_BLACK), str(step))
    cut(step, stl)
    print(f'-> {name}.step / .stl')


def sync_readme(spec=DEFAULT_SPEC):
    """Dimensions of the printed handholds and their guide interface."""
    sys.path.insert(0, str(_hw.parent / 'tools'))
    from docgen import substitute_md
    data = interface(spec)
    values = {
        'WEB_T': spec.web_t,
        'STATION_T': spec.station_t,
        'STATION_AIR': spec.station_air,
        'TROUGH_D': 2.0 * spec.trough_r,
        'TROUGH_DEPTH': spec.bearing_y - spec.web_fore_y,
        'TROUGH_TOP_Z': spec.trough_top_z,
        'STUB_RELIEF_WEB': spec.web_aft_y - spec.stub_relief_y,
        'STUB_RELIEF_DEPTH': spec.stub_relief_y - spec.web_fore_y,
        'STUB_AIR': spec.stub_air,
        'FLANGE_DEPTH': spec.flange_depth,
        'FLANGE_HEIGHT': spec.flange_z[1] - spec.flange_z[0],
        'FLANGE_REACH': 2.0 * spec.flange_x,
        'WEB_HEIGHT': spec.web_z[1] - spec.web_z[0],
        'WEB_WIDTH': spec.web_x[1] - spec.web_x[0],
        'LAP_T': spec.joint_lap_t,
        'SPLIT_X': spec.joint_split_x,
        'SCREW_X': spec.joint_screw_x,
        'INSERT_BACKING': spec.joint_lap_t - enclosure_interface.heatset_len,
        'SPRING_LOAD_ABOVE_COMPRESSED': (spec.spring_load_length
                                        - spring.COMPRESSED_LENGTH_UPPER_ESTIMATE),
        'LAP_WIDTH': spec.joint_reach_x - spec.joint_right_x0,
        'TONGUE_WIDTH': spec.joint_tongue_x[1] - spec.joint_tongue_x[0],
        'TONGUE_ROOT': spec.joint_split_x - spec.joint_tongue_x[0],
        'WEB_GAP': spec.joint_right_x0 - spec.joint_split_x,
        'LAP_STACK': spec.web_aft_y - spec.joint_fore_y,
        'SCREW_LENGTH': spec.joint_screw_length,
        'SCREW_SPACING': spec.joint_screw_zs[1] - spec.joint_screw_zs[0],
        'INSERT_LENGTH': enclosure_interface.heatset_len,
        'SPRING_BORE_D': spec.spring_bore_d,
        'SPRING_BORE_DEPTH': spec.spring_bore_depth,
        'SPRING_BAR_WALL': spec.grip_y[1] - spec.spring_bore_floor_y,
        'SPRING_X': spec.spring_x,
        'SPRING_Z': spec.spring_z,
        'FIXED_SEAT_DEPTH': spec.fixed_seat_depth,
        'SPRING_LENGTH_RELEASE': spec.spring_bore_floor_y + spec.release_offset_y - spec.fixed_seat_floor_y,
        'SPRING_LENGTH_CONNECTED': spec.spring_bore_floor_y + spec.connected_offset_y - spec.fixed_seat_floor_y,
        'SPRING_LENGTH_LIMIT': spec.spring_bore_floor_y + spec.aft_limit_offset_y - spec.fixed_seat_floor_y,
        'SPRING_LOAD_LENGTH': spec.spring_load_length,
        'SPRING_WINDOW_LENGTH': spec.spring_window_y[1] - spec.spring_window_y[0],
        'SPRING_RING': spec.spring_ring,
        'SPRING_COMPRESSED_ESTIMATE': spring.COMPRESSED_LENGTH_UPPER_ESTIMATE,
        'SPRING_OD': spring.OUTSIDE_DIAMETER,
        'SPRING_FREE': spring.FREE_LENGTH,
        'GRIP_BAR_T': spec.grip_bar_t, 'FINGER_RUN': spec.finger_run,
        'FINGER_HEIGHT': spec.printed_grip_z[1] - spec.printed_grip_z[0],
        'FINGER_DEPTH': spec.tab_outer_x - spec.grip_back_x - spec.grip_back_t,
        'GRIP_BACK_T': spec.grip_back_t,
        'GRIP_AFT_T': spec.grip_aft_t,
        'GRIP_AFT_INSET': spec.exterior_x - spec.aft_x[1],
        'OPENING_HEIGHT': (spec.grip_z[1] - spec.grip_z[0] + 2.0 * spec.slide_air
                           + fits.supported_surface),
        'GRIP_EDGE_R': spec.grip_edge_r,
        'GRIP_PROJECTION': spec.tab_outer_x - spec.exterior_x,
        'GRIP_WIDTH': 2 * spec.tab_outer_x, 'GRIP_OVERLAP': spec.grip_overlap,
        'GRIP_TOP_OVERLAP': (spec.printed_rim_z[1]
                             - data['service_slot_z'][1]
                             - fits.supported_surface),
        'GRIP_HEIGHT': spec.printed_grip_z[1] - spec.printed_grip_z[0],
        'GUIDE_LENGTH': spec.grip_y[1] - spec.grip_y[0],
        'OPENING_RUN': spec.grip_bar_t + spec.finger_run + spec.park_offset_y - spec.release_offset_y,
        'GUIDE_AIR': spec.slide_air,
        'SUPPORTED_GUIDE_AIR': spec.slide_air + fits.supported_surface,
        'SUPPORT_AIR': fits.supported_surface,
        'TIE_SLOT_HEIGHT': spec.tie_slot_z + fits.supported_surface,
        'CAPTURE_PROBE_SHIFT': spec.slide_air + 0.001,
        'CAPTURE_PROBE_SHIFT_Z': spec.slide_air + fits.supported_surface + 0.001,
        'GUIDE_TRAVEL': spec.aft_limit_offset_y - spec.release_offset_y,
        'AFT_OVERTRAVEL': spec.aft_overtravel_y,
        'FINGER_RUN_AT_LIMIT': spec.finger_run - spec.aft_overtravel_y,
        'FORE_OVERLAP_AT_LIMIT': spec.grip_overlap - spec.aft_overtravel_y,
        'AFT_COLLET_GAP': tee.CARRIER_AFT_COLLET_GAP,
        'RIM_BED_GAP': spec.printed_rim_z[0] - spec.web_z[0],
    }
    figures = {key: f'{value:.6g} mm' for key, value in values.items()}
    figures['CAPTURE_PROBE_ANGLE'] = f'{spec.capture_probe_angle:.3g}°'
    substitute_md(_here.parent / 'README.md', figures)


def main():
    if selftest():
        return 1
    for side, name in ((-1, 'left'), (1, 'right')):
        _export_printed_part(build_half(side=side), f'enclosure-tee-carrier-{name}')
    sync_readme()
    return 0


if __name__ == '__main__':
    if sys.argv[1:] == ['selftest']:
        if selftest():
            sys.exit(1)
    elif main():
        sys.exit(1)
