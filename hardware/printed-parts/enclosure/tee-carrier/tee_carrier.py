"""The moving carrier behind the four pump-barb tees.

The carrier is one PET-GF part in the enclosure's world frame.  Its broad web bears on the
tees' aft side at the squeeze datum.  Two zip ties around each tee's vertical run arms pass
through the web, and an ear at either end runs in an open-top enclosure guide pocket.  Optional
spring rails receive the compression springs which push the carrier in +Y.  Step 6 adds two
compact outboard-open receivers.  Each service tab starts outside the side wall at its final Z,
slides inward through one local slot, and is retained by a short tab lock dropped from above.

`CarrierSpec` is the complete interface with the enclosure.  The default is the screened
placement in the current pack; the enclosing generator passes its own instance so that the
part does not derive a second copy of a tee, wall, coil, or cartridge datum.

Print in the assembly orientation, translated down to the bed: +Z is the build axis and the
web's Z- edge is the bed face.  When enabled, the spring rails rise from that edge, their
horizontal seats have tangent teardrop roofs, and the aft tie channels open out of a vertical
face.  The carrier, service tabs, and tab locks all print without installed support.

Run:
    tools/cad-venv/bin/python hardware/printed-parts/enclosure/tee-carrier/tee_carrier.py
    tools/cad-venv/bin/python hardware/printed-parts/enclosure/tee-carrier/tee_carrier.py selftest
"""

from __future__ import annotations

import math
import sys
from dataclasses import dataclass
from pathlib import Path

import cadquery as cq

_here = Path(__file__).resolve()
_hw = next(p for p in _here.parents if p.name == "hardware")
sys.path.insert(0, str(_hw / "scripts"))
sys.path.insert(0, str(_hw / "reference" / "tee-connector"))
from _cadq_export import export_assembly  # noqa: E402
from _material_base import M_PETGF_BLACK, one_body  # noqa: E402
import tee_connector as tee  # noqa: E402


@dataclass(frozen=True)
class CarrierSpec:
    """Every enclosure-owned station and carrier-owned section needed to draw the part.

    All coordinates are in the enclosure assembly frame.  Y is the carrier's motion axis,
    with +Y aft; Z is the print axis.  `web_fore_y` is the squeeze datum and all state offsets
    translate the complete returned body from that datum.  `tab_arm_x` retains its original
    interface name; its two values are the male-tongue tip and the flank-pad inner face.
    """

    tee_xs: tuple[float, ...]
    tee_axis_z: float
    web_x: tuple[float, float]
    web_fore_y: float
    web_z: tuple[float, float]
    spring_xs: tuple[float, float]
    spring_axis_z: float
    tab_arm_x: tuple[float, float]
    tab_outer_x: float
    tab_y: tuple[float, float]
    tab_z: tuple[float, float]

    guide_ear_outer_x: float = 98.35
    guide_ear_z: tuple[float, float] = (184.245, 196.245)

    web_t: float = 2.5
    tie_band_offsets_z: tuple[float, float] = (-12.0, 12.0)
    tie_slot_offset_x: float = 8.5
    tie_slot_x: float = 1.5
    tie_slot_z: float = 3.5
    tie_recess_depth: float = 1.2
    tie_stock_w: float = 2.5
    tie_stock_t: float = 1.0
    tie_head: tuple[float, float, float] = (5.0, 3.6, 2.8)

    spring_pad_d: float = 12.4
    spring_pad_t: float = 5.0
    spring_seat_d: float = 6.4
    spring_seat_depth: float = 2.0
    spring_roof_angle_deg: float = 45.0

    release_offset_y: float = tee.CARRIER_RELEASE_OFFSET
    connected_offset_y: float = tee.CARRIER_CONNECTED_OFFSET
    park_offset_y: float = tee.CARRIER_PARK_OFFSET
    fixed_plate_aft_y: float = 81.290
    aft_coil_fore_y: float = 116.960
    obstacle_air: float = 1.5
    exterior_x: float = 107.5
    tab_recess: float = 0.3

    lowering_cavity_half_x: float = 98.5
    tab_tongue_y_inset: float = 0.6
    tab_tongue_root_bottom_from_tab_z: float = 5.7
    tab_tongue_top_from_tab_z: float = 10.2
    tab_joint_clearance: float = 0.15
    tab_lock_center_inset: float = 1.15
    tab_lock_shaft: tuple[float, float] = (1.2, 1.0)
    tab_lock_head: tuple[float, float, float] = (2.0, 2.0, 0.7)
    tab_lock_bottom_from_tab_z: float = 7.8
    tab_lock_shaft_top_from_tab_z: float = 10.5
    tab_lock_top_from_tab_z: float = 11.0
    service_opening_top_z: float = 214.203

    bed_x: float = 325.0
    bed_y: float = 320.0
    bed_z: float = 320.0

    @property
    def web_aft_y(self) -> float:
        return self.web_fore_y + self.web_t

    @property
    def state_offsets_y(self) -> tuple[float, ...]:
        return (
            self.release_offset_y,
            0.0,
            self.connected_offset_y,
            self.park_offset_y,
        )


@dataclass(frozen=True)
class CarrierFeatures:
    """Features introduced by the three carrier steps.

    The web, tie passages, and guide/stop ears are always present.  Step 5 adds the spring
    rails and seats; Step 6 adds the fixed halves of the two separate-tab joints.
    """

    springs: bool
    tabs: bool


STEP4_FEATURES = CarrierFeatures(springs=False, tabs=False)
STEP5_FEATURES = CarrierFeatures(springs=True, tabs=False)
STEP6_FEATURES = CarrierFeatures(springs=True, tabs=True)
DEFAULT_FEATURES = STEP6_FEATURES


DEFAULT_SPEC = CarrierSpec(
    tee_xs=(-79.82, -20.07, 20.07, 79.82),
    tee_axis_z=190.245,
    web_x=(-94.0, 94.0),
    web_fore_y=109.718,
    web_z=(171.245, 209.245),
    spring_xs=(-49.945, 49.945),
    spring_axis_z=190.245,
    # The first X is the tongue tip; the second is the pad's inboard face.  The pad therefore
    # occupies only the 8.55 mm flank thickness while the tongue reaches into the carrier.
    tab_arm_x=(94.15, 98.65),
    tab_outer_x=107.2,
    tab_y=(109.718, 112.218),
    tab_z=(197.0, 209.0),
)


@dataclass(frozen=True)
class TieSite:
    tee_x: float
    band_z: float
    slot_xs: tuple[float, float]
    head_side: int


@dataclass(frozen=True)
class TabJointSite:
    """Installed and outboard-entry facts for one handed service-tab joint."""

    side: int
    receiver_x: tuple[float, float]
    receiver_y: tuple[float, float]
    receiver_z: tuple[float, float]
    socket_x: tuple[float, float]
    socket_y: tuple[float, float]
    socket_z: tuple[float, float]
    tongue_x: tuple[float, float]
    tongue_y: tuple[float, float]
    tongue_z: tuple[float, float]
    lock_center_xy: tuple[float, float]
    entry_shift_x: float


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

    Every head is clocked away from the machine centre.  It lies beside the tee on the fore
    side of the carrier; no head occupies the coil clearance behind the web.
    """
    return tuple(
        TieSite(
            tee_x=tee_x,
            band_z=spec.tee_axis_z + dz,
            slot_xs=(tee_x - spec.tie_slot_offset_x, tee_x + spec.tie_slot_offset_x),
            head_side=-1 if tee_x < 0.0 else 1,
        )
        for tee_x in spec.tee_xs
        for dz in spec.tie_band_offsets_z
    )


def _spring_rail(spec: CarrierSpec, x: float):
    """One bed-rooted thickening behind a spring seat.

    A semicircular crown surrounds the teardrop seat.  The rectangle below the spring axis
    carries that crown to the bed, so the extra 2.5 mm behind the web never begins as a
    horizontal ledge in the print.
    """
    radius = spec.spring_pad_d / 2.0
    stem = _box(
        x - radius,
        x + radius,
        spec.web_fore_y,
        spec.web_fore_y + spec.spring_pad_t,
        spec.web_z[0],
        spec.spring_axis_z,
    )
    crown = cq.Workplane(
        obj=cq.Solid.makeCylinder(
            radius,
            spec.spring_pad_t,
            cq.Vector(x, spec.web_fore_y, spec.spring_axis_z),
            cq.Vector(0.0, 1.0, 0.0),
        )
    )
    return stem.union(crown)


def _guide_ear_pair(spec: CarrierSpec):
    """Two fixed-section ears for the enclosure's open-top guide/stop pockets.

    Their Y faces are exactly the web faces: the pocket can therefore own both travel stops
    without introducing a second carrier datum.  The ears sit between the two tie bands in Z
    and outside the tie-head X stations, so they lower vertically into pockets without
    crossing a tie path.
    """
    z0, z1 = spec.guide_ear_z
    left = _box(
        -spec.guide_ear_outer_x,
        spec.web_x[0],
        spec.web_fore_y,
        spec.web_aft_y,
        z0,
        z1,
    )
    right = _box(
        spec.web_x[1],
        spec.guide_ear_outer_x,
        spec.web_fore_y,
        spec.web_aft_y,
        z0,
        z1,
    )
    return left.union(right)


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


def _xspan(side: int, x0: float, x1: float) -> tuple[float, float]:
    """Mirror a positive-X interval onto one handed part."""
    if side not in (-1, 1):
        raise ValueError(f"service-tab side must be -1 or +1, got {side}")
    return (x0, x1) if side > 0 else (-x1, -x0)


def tab_joint_sites(spec: CarrierSpec = DEFAULT_SPEC) -> tuple[TabJointSite, ...]:
    """The two female carrier sockets, male tab tongues, and outboard entry shifts."""
    clearance = spec.tab_joint_clearance
    tongue_inner, pad_inner = spec.tab_arm_x
    receiver_inner = min(-spec.web_x[0], spec.web_x[1]) - 0.5
    tongue_y = (
        spec.tab_y[0] + spec.tab_tongue_y_inset,
        spec.tab_y[1] - spec.tab_tongue_y_inset,
    )
    tongue_z = (
        spec.tab_z[0] + spec.tab_tongue_root_bottom_from_tab_z,
        spec.tab_z[0] + spec.tab_tongue_top_from_tab_z,
    )
    socket_y = (tongue_y[0] - clearance, tongue_y[1] + clearance)
    socket_z = (tongue_z[0] - clearance, tongue_z[1] + clearance)
    lock_y = sum(spec.tab_y) / 2.0
    entry_distance = spec.exterior_x + clearance - tongue_inner
    return tuple(
        TabJointSite(
            side=side,
            receiver_x=_xspan(side, receiver_inner, spec.guide_ear_outer_x),
            receiver_y=spec.tab_y,
            receiver_z=(spec.guide_ear_z[1], spec.web_z[1]),
            socket_x=_xspan(
                side,
                tongue_inner - clearance,
                spec.guide_ear_outer_x + clearance,
            ),
            socket_y=socket_y,
            socket_z=socket_z,
            tongue_x=_xspan(side, tongue_inner, pad_inner),
            tongue_y=tongue_y,
            tongue_z=tongue_z,
            lock_center_xy=(
                side * (pad_inner - spec.tab_lock_center_inset),
                lock_y,
            ),
            entry_shift_x=side * entry_distance,
        )
        for side in (-1, 1)
    )


def _yz_prism(
    x0: float,
    x1: float,
    points: tuple[tuple[float, float], ...],
):
    """Extrude one YZ polygon along +X."""
    return (
        cq.Workplane("YZ", origin=(x0, 0.0, 0.0))
        .polyline(points)
        .close()
        .extrude(x1 - x0)
    )


def _xz_prism(
    y0: float,
    y1: float,
    points: tuple[tuple[float, float], ...],
):
    """Extrude one XZ polygon along +Y."""
    plane = cq.Plane(origin=(0.0, y0, 0.0), xDir=(1.0, 0.0, 0.0), normal=(0.0, -1.0, 0.0))
    return cq.Workplane(plane).polyline(points).close().extrude(-(y1 - y0))


def _tab_tongue(site: TabJointSite):
    """The tab-owned tongue; its 45-degree lower face grows from the pad."""
    root_x = site.tongue_x[1] if site.side > 0 else site.tongue_x[0]
    tip_x = site.tongue_x[0] if site.side > 0 else site.tongue_x[1]
    return _xz_prism(
        site.tongue_y[0],
        site.tongue_y[1],
        (
            (root_x, site.tongue_z[0]),
            (root_x, site.tongue_z[1]),
            (tip_x, site.tongue_z[1]),
        ),
    )


def _tab_receiver_blank(spec: CarrierSpec, site: TabJointSite):
    """One ear- and web-rooted blank for an outboard-open female socket."""
    return _box(
        site.receiver_x[0],
        site.receiver_x[1],
        site.receiver_y[0],
        site.receiver_y[1],
        site.receiver_z[0],
        site.receiver_z[1],
    )


def _tab_lock_cutters(spec: CarrierSpec, site: TabJointSite):
    """The clearance bore shared by a male tab tongue and female carrier socket."""
    clearance = spec.tab_joint_clearance
    cx, cy = site.lock_center_xy
    shaft_x, shaft_y = spec.tab_lock_shaft
    head_x, head_y, head_z = spec.tab_lock_head
    lock_bottom = spec.tab_z[0] + spec.tab_lock_bottom_from_tab_z
    lock_top = spec.tab_z[0] + spec.tab_lock_top_from_tab_z
    head_bottom = lock_top - head_z
    bore = _box(
        cx - shaft_x / 2.0 - clearance,
        cx + shaft_x / 2.0 + clearance,
        cy - shaft_y / 2.0 - clearance,
        cy + shaft_y / 2.0 + clearance,
        lock_bottom,
        site.receiver_z[1] + clearance,
    )
    counterbore = _box(
        cx - head_x / 2.0 - clearance,
        cx + head_x / 2.0 + clearance,
        cy - head_y / 2.0 - clearance,
        cy + head_y / 2.0 + clearance,
        head_bottom - clearance,
        site.receiver_z[1] + clearance,
    )
    return bore, counterbore


def _tab_socket_cavity(spec: CarrierSpec, site: TabJointSite):
    """The carrier-owned female socket, open toward the enclosure exterior."""
    root_x = site.socket_x[1] if site.side > 0 else site.socket_x[0]
    tip_x = site.socket_x[0] if site.side > 0 else site.socket_x[1]
    return _xz_prism(
        site.socket_y[0],
        site.socket_y[1],
        (
            (root_x, site.socket_z[0]),
            (root_x, site.socket_z[1]),
            (tip_x, site.socket_z[1]),
        ),
    )


def _tab_joint_site(spec: CarrierSpec, side: int) -> TabJointSite:
    _xspan(side, 0.0, 1.0)
    return next(site for site in tab_joint_sites(spec) if site.side == side)


def build_service_tab(spec: CarrierSpec = DEFAULT_SPEC, side: int = 1):
    """Build one handed service pad and male tongue in installed coordinates."""
    site = _tab_joint_site(spec, side)
    pad_x = _xspan(side, spec.tab_arm_x[1], spec.tab_outer_x)
    pad = _box(
        pad_x[0],
        pad_x[1],
        spec.tab_y[0],
        spec.tab_y[1],
        spec.tab_z[0],
        spec.tab_z[1],
    )
    body = pad.union(_tab_tongue(site))
    for cutter in _tab_lock_cutters(spec, site):
        body = body.cut(cutter)
    return body


def build_tab_lock(spec: CarrierSpec = DEFAULT_SPEC, side: int = 1):
    """Build one short top-dropped tab lock in its installed enclosure coordinates."""
    site = _tab_joint_site(spec, side)
    cx, cy = site.lock_center_xy
    shaft_x, shaft_y = spec.tab_lock_shaft
    head_x, head_y, head_z = spec.tab_lock_head
    bottom = spec.tab_z[0] + spec.tab_lock_bottom_from_tab_z
    shaft_top = spec.tab_z[0] + spec.tab_lock_shaft_top_from_tab_z
    top = spec.tab_z[0] + spec.tab_lock_top_from_tab_z
    shaft = _box(
        cx - shaft_x / 2.0,
        cx + shaft_x / 2.0,
        cy - shaft_y / 2.0,
        cy + shaft_y / 2.0,
        bottom,
        shaft_top,
    )
    head = _box(
        cx - head_x / 2.0,
        cx + head_x / 2.0,
        cy - head_y / 2.0,
        cy + head_y / 2.0,
        top - head_z,
        top,
    )
    return shaft.union(head)


def build_tab(spec: CarrierSpec = DEFAULT_SPEC, side: int = 1):
    """Compatibility name for `build_service_tab`."""
    return build_service_tab(spec, side)


def build_lock_key(spec: CarrierSpec = DEFAULT_SPEC, side: int = 1):
    """Compatibility name for `build_tab_lock`."""
    return build_tab_lock(spec, side)


def _tie_cutters(spec: CarrierSpec):
    """The sixteen through slots and eight aft flush-routing channels."""
    slots = []
    recesses = []
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
                    site.band_z + spec.tie_slot_z / 2.0,
                )
            )
        recesses.append(
            _box(
                site.slot_xs[0] - spec.tie_slot_x / 2.0,
                site.slot_xs[1] + spec.tie_slot_x / 2.0,
                spec.web_aft_y - spec.tie_recess_depth,
                spec.web_aft_y + proud,
                site.band_z - spec.tie_slot_z / 2.0,
                site.band_z + spec.tie_slot_z / 2.0,
            )
        )
    return tuple(slots), tuple(recesses)


def build(
    spec: CarrierSpec = DEFAULT_SPEC,
    features: CarrierFeatures = DEFAULT_FEATURES,
):
    """Build one tee carrier at the squeeze datum with the selected step features."""
    body = _box(
        spec.web_x[0],
        spec.web_x[1],
        spec.web_fore_y,
        spec.web_aft_y,
        spec.web_z[0],
        spec.web_z[1],
    )
    body = body.union(_guide_ear_pair(spec))
    if features.springs:
        for x in spec.spring_xs:
            body = body.union(_spring_rail(spec, x))
    if features.tabs:
        for site in tab_joint_sites(spec):
            body = body.union(_tab_receiver_blank(spec, site))

    slots, recesses = _tie_cutters(spec)
    for cutter in (*slots, *recesses):
        body = body.cut(cutter)

    if features.tabs:
        for site in tab_joint_sites(spec):
            for cutter in (_tab_socket_cavity(spec, site), *_tab_lock_cutters(spec, site)):
                body = body.cut(cutter)

    if features.springs:
        seat_proud = 0.1
        for x in spec.spring_xs:
            seat = _teardrop_y(
                x,
                spec.web_fore_y - seat_proud,
                spec.spring_axis_z,
                spec.spring_seat_d,
                spec.spring_seat_depth + seat_proud,
                spec.spring_roof_angle_deg,
            )
            body = body.cut(seat)
    return body


def build_carrier(
    spec: CarrierSpec = DEFAULT_SPEC,
    features: CarrierFeatures = DEFAULT_FEATURES,
):
    """Explicit public name for the moving carrier body."""
    return build(spec, features)


def interface(spec: CarrierSpec = DEFAULT_SPEC) -> dict:
    """The placement facts the enclosure needs for guides, stops, springs, and slots."""
    tab_sites = tab_joint_sites(spec)
    lock_bottom = spec.tab_z[0] + spec.tab_lock_bottom_from_tab_z
    lock_top = spec.tab_z[0] + spec.tab_lock_top_from_tab_z
    lock_entry_bottom = max(site.receiver_z[1] for site in tab_sites)
    lock_entry_bottom += spec.tab_joint_clearance
    lock_entry_lift = lock_entry_bottom - lock_bottom
    slot_y = (
        spec.tab_y[0] + spec.release_offset_y - spec.tab_joint_clearance,
        spec.tab_y[1] + spec.park_offset_y + spec.tab_joint_clearance,
    )
    slot_z = (
        spec.tab_z[0] - spec.tab_joint_clearance,
        spec.tab_z[1] + spec.tab_joint_clearance,
    )
    return {
        "squeeze_offset_y": 0.0,
        "release_offset_y": spec.release_offset_y,
        "connected_offset_y": spec.connected_offset_y,
        "park_offset_y": spec.park_offset_y,
        "web_fore_y": spec.web_fore_y,
        "web_aft_y": spec.web_aft_y,
        "release_fore_stop_y": spec.web_fore_y + spec.release_offset_y,
        "squeeze_reference_aft_y": spec.web_aft_y,
        "park_aft_stop_y": spec.web_aft_y + spec.park_offset_y,
        "guide_ear_x": (
            (-spec.guide_ear_outer_x, spec.web_x[0]),
            (spec.web_x[1], spec.guide_ear_outer_x),
        ),
        "guide_ear_y": (spec.web_fore_y, spec.web_aft_y),
        "guide_ear_z": spec.guide_ear_z,
        "spring_seats": tuple(
            (x, spec.web_fore_y, spec.spring_axis_z) for x in spec.spring_xs
        ),
        "tab_slot_x": (
            (-spec.tab_outer_x, -spec.tab_arm_x[1]),
            (spec.tab_arm_x[1], spec.tab_outer_x),
        ),
        "tab_slot_y_sweep": (
            spec.tab_y[0] + spec.release_offset_y,
            spec.tab_y[1] + spec.park_offset_y,
        ),
        "tab_slot_z": spec.tab_z,
        "lowering_cavity_x": (
            -spec.lowering_cavity_half_x,
            spec.lowering_cavity_half_x,
        ),
        "carrier_lowering_air_x": spec.lowering_cavity_half_x - spec.guide_ear_outer_x,
        "tab_pad_x": (
            _xspan(-1, spec.tab_arm_x[1], spec.tab_outer_x),
            _xspan(1, spec.tab_arm_x[1], spec.tab_outer_x),
        ),
        "service_slot_x": (
            spec.lowering_cavity_half_x - spec.tab_joint_clearance,
            spec.exterior_x + 1.0,
        ),
        "service_slot_y": slot_y,
        "service_slot_z": slot_z,
        "service_slot_roof_z": spec.service_opening_top_z,
        "tab_joint_sites": tuple(
            {
                "side": site.side,
                "receiver_x": site.receiver_x,
                "receiver_y": site.receiver_y,
                "receiver_z": site.receiver_z,
                "socket_x": site.socket_x,
                "socket_y": site.socket_y,
                "socket_z": site.socket_z,
                "tongue_x": site.tongue_x,
                "tongue_y": site.tongue_y,
                "tongue_z": site.tongue_z,
                "lock_center_xy": site.lock_center_xy,
                "entry_shift_x": site.entry_shift_x,
            }
            for site in tab_sites
        ),
        "tab_install_path": tuple(
            {
                "side": site.side,
                "start_shift_x": site.entry_shift_x,
                "start_tab_x": tuple(
                    x + site.entry_shift_x
                    for x in _xspan(site.side, spec.tab_arm_x[0], spec.tab_outer_x)
                ),
                "insert_inward_x": -site.entry_shift_x,
                "insert_holds_y": spec.tab_y,
                "insert_holds_z": spec.tab_z,
                "entry_exterior_air_x": spec.tab_joint_clearance,
                "lock_entry_axis": (0.0, 0.0, -1.0),
                "lock_entry_lift_z": lock_entry_lift,
            }
            for site in tab_sites
        ),
        "tab_lock_z": (lock_bottom, lock_top),
        "tab_lock_entry_top_z": lock_top + lock_entry_lift,
        "service_opening_top_z": spec.service_opening_top_z,
        "tab_lock_entry_air_z": spec.service_opening_top_z - (lock_top + lock_entry_lift),
        "printed_parts": (
            "enclosure-tee-carrier",
            "enclosure-tee-carrier-tab-left",
            "enclosure-tee-carrier-tab-right",
            "enclosure-tee-carrier-tab-lock-left",
            "enclosure-tee-carrier-tab-lock-right",
        ),
        "tie_sites": tuple(
            {
                "tee_x": site.tee_x,
                "band_z": site.band_z,
                "slot_xs": site.slot_xs,
                "head_side": site.head_side,
            }
            for site in tie_sites(spec)
        ),
    }


def _spec_errors(spec: CarrierSpec) -> list[str]:
    errors = []
    if len(spec.tee_xs) != 4 or len(set(spec.tee_xs)) != 4:
        errors.append(f"carrier wants four distinct tee X stations, got {spec.tee_xs}")
    if len(spec.tie_band_offsets_z) != 2:
        errors.append(f"each tee wants two tie bands, got {spec.tie_band_offsets_z}")
    if spec.web_t <= 0.0 or spec.tie_recess_depth >= spec.web_t:
        errors.append(
            f"tie recess {spec.tie_recess_depth:g} leaves no web in {spec.web_t:g} thickness"
        )
    if spec.tie_recess_depth < spec.tie_stock_t:
        errors.append(
            f"tie recess {spec.tie_recess_depth:g} is shallower than {spec.tie_stock_t:g} stock"
        )
    if spec.tie_slot_z < spec.tie_stock_w or spec.tie_slot_x < spec.tie_stock_t:
        errors.append(
            f"tie slot {spec.tie_slot_x:g} x {spec.tie_slot_z:g} does not pass "
            f"{spec.tie_stock_t:g} x {spec.tie_stock_w:g} stock"
        )
    if spec.guide_ear_outer_x <= max(abs(x) for x in spec.web_x):
        errors.append(
            f"guide ear outer X {spec.guide_ear_outer_x:g} does not extend beyond "
            f"web {spec.web_x}"
        )
    if spec.guide_ear_outer_x >= spec.exterior_x:
        errors.append(
            f"guide ear reaches |x|={spec.guide_ear_outer_x:g}, outside enclosure "
            f"|x|={spec.exterior_x:g}"
        )
    ear_inner_x = min(-spec.web_x[0], spec.web_x[1])
    if ear_inner_x > spec.tab_arm_x[0]:
        errors.append(
            f"tab tongue begins at |x|={spec.tab_arm_x[0]:g}, inside web edge "
            f"|x|={ear_inner_x:g}"
        )
    if spec.guide_ear_z[0] >= spec.guide_ear_z[1]:
        errors.append(f"guide ear has empty Z span {spec.guide_ear_z}")
    if spec.guide_ear_z[0] < spec.web_z[0] or spec.guide_ear_z[1] > spec.web_z[1]:
        errors.append(
            f"guide ear Z span {spec.guide_ear_z} leaves web span {spec.web_z}"
        )
    half_tie_z = spec.tie_slot_z / 2.0
    for dz in spec.tie_band_offsets_z:
        tie_z = spec.tee_axis_z + dz
        if not (
            spec.guide_ear_z[1] <= tie_z - half_tie_z
            or spec.guide_ear_z[0] >= tie_z + half_tie_z
        ):
            errors.append(
                f"guide ear Z span {spec.guide_ear_z} crosses tie path at z={tie_z:g}"
            )
    if spec.guide_ear_z[1] > spec.tab_z[0]:
        errors.append(
            f"guide ear rises to z={spec.guide_ear_z[1]:g}, into tab beginning "
            f"at z={spec.tab_z[0]:g}"
        )
    ear_axis_z = sum(spec.guide_ear_z) / 2.0
    if abs(ear_axis_z - spec.tee_axis_z) > 1e-9:
        errors.append(
            f"guide ear is centred at z={ear_axis_z:g}, not tee axis "
            f"z={spec.tee_axis_z:g}"
        )
    if spec.spring_seat_depth >= spec.spring_pad_t:
        errors.append(
            f"spring seat depth {spec.spring_seat_depth:g} consumes pad {spec.spring_pad_t:g}"
        )
    if spec.spring_seat_d >= spec.spring_pad_d:
        errors.append(
            f"spring seat diameter {spec.spring_seat_d:g} leaves no wall in "
            f"pad diameter {spec.spring_pad_d:g}"
        )
    tongue_inner, pad_inner = spec.tab_arm_x
    if not (
        ear_inner_x < tongue_inner < spec.lowering_cavity_half_x < pad_inner < spec.tab_outer_x
    ):
        errors.append(
            "tab X stations are not web < tongue < cavity < pad < exterior: "
            f"{ear_inner_x:g}, {tongue_inner:g}, {spec.lowering_cavity_half_x:g}, "
            f"{pad_inner:g}, {spec.tab_outer_x:g}"
        )
    if pad_inner - spec.lowering_cavity_half_x + 1e-9 < spec.tab_joint_clearance:
        errors.append(
            f"tab pad leaves {pad_inner - spec.lowering_cavity_half_x:.3f} mm to the "
            f"flank, under {spec.tab_joint_clearance:g} slip"
        )
    if spec.tab_outer_x > spec.exterior_x - spec.tab_recess + 1e-9:
        errors.append(
            f"tab reaches x={spec.tab_outer_x:g}; recessed exterior limit is "
            f"{spec.exterior_x - spec.tab_recess:g}"
        )
    carrier_lowering_air = spec.lowering_cavity_half_x - spec.guide_ear_outer_x
    if carrier_lowering_air + 1e-9 < spec.tab_joint_clearance:
        errors.append(
            f"carrier leaves {carrier_lowering_air:.3f} mm in the lowering cavity, under "
            f"{spec.tab_joint_clearance:g} slip"
        )
    if not (
        spec.release_offset_y < 0.0 < spec.connected_offset_y < spec.park_offset_y
    ):
        errors.append(
            "carrier states are not release < squeeze < connected < park: "
            f"{spec.state_offsets_y}"
        )
    if spec.tab_y[0] + spec.release_offset_y <= spec.fixed_plate_aft_y:
        errors.append(
            f"released tab begins y={spec.tab_y[0] + spec.release_offset_y:.3f}, not aft of "
            f"fixed plate y={spec.fixed_plate_aft_y:.3f}"
        )
    parked_web_air = spec.aft_coil_fore_y - (spec.web_aft_y + spec.park_offset_y)
    if parked_web_air < spec.obstacle_air:
        errors.append(
            f"parked web leaves {parked_web_air:.3f} mm to aft coils, under "
            f"{spec.obstacle_air:g}"
        )

    if abs(spec.tab_y[0] - spec.web_fore_y) > 1e-9 or (
        abs(spec.tab_y[1] - spec.web_aft_y) > 1e-9
    ):
        errors.append(
            f"short tab Y span {spec.tab_y} is not the carrier section "
            f"{(spec.web_fore_y, spec.web_aft_y)}"
        )
    tongue_run = spec.tab_arm_x[1] - spec.tab_arm_x[0]
    tongue_rise = (
        spec.tab_tongue_top_from_tab_z - spec.tab_tongue_root_bottom_from_tab_z
    )
    if tongue_rise + 1e-9 < tongue_run:
        errors.append(
            f"tab tongue underside rises {tongue_rise:.3f} mm over {tongue_run:.3f} mm; "
            "it is shallower than 45 degrees"
        )
    if 2.0 * spec.tab_tongue_y_inset >= spec.web_t:
        errors.append(
            f"tab tongue inset {spec.tab_tongue_y_inset:g} leaves no tongue in "
            f"{spec.web_t:g} mm tab thickness"
        )

    for site in tab_joint_sites(spec):
        exterior_air = abs(site.tongue_x[0] + site.entry_shift_x) - spec.exterior_x
        if site.side < 0:
            exterior_air = abs(site.tongue_x[1] + site.entry_shift_x) - spec.exterior_x
        if exterior_air + 1e-9 < spec.tab_joint_clearance:
            errors.append(
                f"side {site.side:+d} entry starts with {exterior_air:.3f} mm exterior "
                f"air, under {spec.tab_joint_clearance:g} slip"
            )

    lock_bottom = spec.tab_z[0] + spec.tab_lock_bottom_from_tab_z
    lock_shaft_top = spec.tab_z[0] + spec.tab_lock_shaft_top_from_tab_z
    lock_top = spec.tab_z[0] + spec.tab_lock_top_from_tab_z
    lock_head_bottom = lock_top - spec.tab_lock_head[2]
    if not (lock_bottom < lock_shaft_top <= lock_top):
        errors.append(
            f"tab-lock shaft Z {lock_bottom:g}..{lock_shaft_top:g} does not end in "
            f"top z={lock_top:g}"
        )
    if lock_head_bottom >= lock_shaft_top:
        errors.append(
            f"lock head begins z={lock_head_bottom:g} above shaft z={lock_shaft_top:g}"
        )
    lock_entry_bottom = max(site.receiver_z[1] for site in tab_joint_sites(spec))
    lock_entry_bottom += spec.tab_joint_clearance
    lock_entry_lift = lock_entry_bottom - lock_bottom
    lock_entry_top = lock_top + lock_entry_lift
    lock_entry_air = spec.service_opening_top_z - lock_entry_top
    if lock_entry_air + 1e-9 < spec.tab_joint_clearance:
        errors.append(
            f"top-dropped lock leaves {lock_entry_air:.3f} mm under service gable, "
            f"under {spec.tab_joint_clearance:g} slip"
        )

    half_slot = spec.tie_slot_x / 2.0
    for site in tie_sites(spec):
        if site.band_z - spec.tie_slot_z / 2.0 < spec.web_z[0] or (
            site.band_z + spec.tie_slot_z / 2.0 > spec.web_z[1]
        ):
            errors.append(f"tie band z={site.band_z:g} leaves the web's Z span")
        for slot_x in site.slot_xs:
            if slot_x - half_slot < spec.web_x[0] or slot_x + half_slot > spec.web_x[1]:
                errors.append(f"tie slot x={slot_x:g} leaves the web's X span")

    # With each buckle beside its tee, the head's 2.8 mm radial depth stays inboard of the
    # carrier end and clear of the service tongue beginning at `tab_arm_x[0]`.
    tee_radius = 6.858
    head_radial = spec.tie_head[2]
    head_envelope = max(abs(x) + tee_radius + head_radial for x in spec.tee_xs)
    if head_envelope >= spec.tab_arm_x[0]:
        errors.append(
            f"clocked tie head reaches |x|={head_envelope:.3f}, into tab tongue at "
            f"{spec.tab_arm_x[0]:g}"
        )
    return errors


def _overlap_volume(a, b) -> float:
    return a.intersect(b).val().Volume()


def _fits_bed(bbox, spec: CarrierSpec) -> bool:
    return (
        min(bbox.xlen, bbox.ylen) <= min(spec.bed_x, spec.bed_y)
        and max(bbox.xlen, bbox.ylen) <= max(spec.bed_x, spec.bed_y)
        and bbox.zlen <= spec.bed_z
    )


def selftest(spec: CarrierSpec = DEFAULT_SPEC) -> int:
    """Carrier stages, handed parts, state motion, and the complete installation path."""
    errors = _spec_errors(spec)
    ties = tie_sites(spec)
    slots, _recesses = _tie_cutters(spec)
    if len(ties) != 8:
        errors.append(f"carrier has {len(ties)} tie sites, wants eight")
    if len(slots) != 16:
        errors.append(f"carrier has {len(slots)} through slots, wants sixteen")

    bbox = None
    carriers = {}
    for label, features in (
        ("step 4", STEP4_FEATURES),
        ("step 5", STEP5_FEATURES),
        ("step 6", STEP6_FEATURES),
    ):
        carrier = build_carrier(spec, features)
        carriers[label] = carrier
        solid = carrier.val()
        solids = solid.Solids()
        if len(solids) != 1:
            errors.append(f"{label} tee carrier is {len(solids)} solids, not one body")

        # Every nominal slot centre is air through the complete web after all booleans.
        for i, slot in enumerate(slots, 1):
            remaining = solid.intersect(slot.val()).Volume()
            if remaining > 1e-5:
                errors.append(f"{label} tie slot {i} retains {remaining:.4f} mm3 of carrier")

        bbox = solid.BoundingBox()
        cavity_air = spec.lowering_cavity_half_x - max(abs(bbox.xmin), abs(bbox.xmax))
        if cavity_air + 1e-9 < spec.tab_joint_clearance:
            errors.append(
                f"{label} leaves {cavity_air:.3f} mm in the lowering cavity, under "
                f"{spec.tab_joint_clearance:g} slip"
            )
        if not _fits_bed(bbox, spec):
            errors.append(
                f"{label} upright carrier is {bbox.xlen:.1f} x {bbox.ylen:.1f} x "
                f"{bbox.zlen:.1f}, outside {spec.bed_x:g} x {spec.bed_y:g} x "
                f"{spec.bed_z:g}"
            )

    carrier = carriers["step 6"]
    tab_volumes = []
    lock_volumes = []
    path_samples = 31
    lock_bottom = spec.tab_z[0] + spec.tab_lock_bottom_from_tab_z
    lock_entry_bottom = max(site.receiver_z[1] for site in tab_joint_sites(spec))
    lock_entry_bottom += spec.tab_joint_clearance
    lock_entry_lift = lock_entry_bottom - lock_bottom
    iface = interface(spec)

    for site in tab_joint_sites(spec):
        tab = build_service_tab(spec, site.side)
        lock = build_tab_lock(spec, site.side)
        tab_solid = tab.val()
        lock_solid = lock.val()
        tab_volumes.append(tab_solid.Volume())
        lock_volumes.append(lock_solid.Volume())
        if len(tab_solid.Solids()) != 1:
            errors.append(f"side {site.side:+d} service tab is not one solid")
        if len(lock_solid.Solids()) != 1:
            errors.append(f"side {site.side:+d} tab lock is not one solid")
        if not _fits_bed(tab_solid.BoundingBox(), spec):
            errors.append(f"side {site.side:+d} service tab does not fit the print bed")
        if not _fits_bed(lock_solid.BoundingBox(), spec):
            errors.append(f"side {site.side:+d} tab lock does not fit the print bed")

        pad_x = _xspan(site.side, spec.tab_arm_x[1], spec.tab_outer_x)
        pad = _box(
            pad_x[0],
            pad_x[1],
            spec.tab_y[0],
            spec.tab_y[1],
            spec.tab_z[0],
            spec.tab_z[1],
        )
        missing_pad = pad.val().cut(tab_solid).Volume()
        if missing_pad > 1e-5:
            errors.append(
                f"side {site.side:+d} tab is missing {missing_pad:.4f} mm3 of its pad envelope"
            )

        for other_label, other in (("carrier", carrier), ("lock", lock)):
            overlap = _overlap_volume(tab, other)
            if overlap > 1e-5:
                errors.append(
                    f"side {site.side:+d} installed tab overlaps {other_label} by "
                    f"{overlap:.4f} mm3"
                )
        lock_carrier_overlap = _overlap_volume(lock, carrier)
        if lock_carrier_overlap > 1e-5:
            errors.append(
                f"side {site.side:+d} installed lock overlaps carrier by "
                f"{lock_carrier_overlap:.4f} mm3"
            )

        tongue = _tab_tongue(site)
        receiver_bounds = _box(
            site.receiver_x[0],
            site.receiver_x[1],
            site.receiver_y[0],
            site.receiver_y[1],
            site.receiver_z[0],
            site.receiver_z[1],
        )
        tongue_inside_receiver = tongue.intersect(receiver_bounds)
        uncaptured = tongue_inside_receiver.val().cut(
            _tab_socket_cavity(spec, site).val()
        ).Volume()
        if tongue_inside_receiver.val().Volume() <= 1e-5 or uncaptured > 1e-5:
            errors.append(
                f"side {site.side:+d} tongue is not wholly inside its female socket"
            )

        start = tab.translate(cq.Vector(site.entry_shift_x, 0.0, 0.0))
        start_bbox = start.val().BoundingBox()
        entry_inner_x = start_bbox.xmin if site.side > 0 else start_bbox.xmax
        exterior_air = site.side * entry_inner_x - spec.exterior_x
        if exterior_air + 1e-9 < spec.tab_joint_clearance:
            errors.append(
                f"side {site.side:+d} tab starts with {exterior_air:.3f} mm outside the wall, "
                f"under {spec.tab_joint_clearance:g} slip"
            )

        # The representative flank is solid everywhere except the exact slot interface.  The
        # complete rigid tab must cross that wall and enter the socket without a second motion.
        slot_x = iface["service_slot_x"]
        slot_y = iface["service_slot_y"]
        slot_z = iface["service_slot_z"]
        wall_x = (
            slot_x if site.side > 0 else (-slot_x[1], -slot_x[0])
        )
        wall = _box(
            wall_x[0],
            wall_x[1],
            slot_y[0] - 5.0,
            slot_y[1] + 5.0,
            slot_z[0] - 5.0,
            slot_z[1] + 5.0,
        ).cut(
            _box(
                wall_x[0] - 0.1,
                wall_x[1] + 0.1,
                slot_y[0],
                slot_y[1],
                slot_z[0],
                slot_z[1],
            )
        )
        for i in range(path_samples):
            dx = site.entry_shift_x * (1.0 - i / (path_samples - 1))
            moved = tab.translate(cq.Vector(dx, 0.0, 0.0))
            overlap = _overlap_volume(carrier, moved) + _overlap_volume(wall, moved)
            if overlap > 1e-5:
                errors.append(
                    f"side {site.side:+d} inward-install sample {i} overlaps receiver/wall "
                    f"by {overlap:.4f} mm3"
                )
                break

        # Stage 2: drop the short rigid lock through the aligned socket and male tongue.
        for i in range(path_samples):
            dz = lock_entry_lift * (1.0 - i / (path_samples - 1))
            moved = lock.translate(cq.Vector(0.0, 0.0, dz))
            overlap = _overlap_volume(carrier, moved) + _overlap_volume(tab, moved)
            if overlap > 1e-5:
                errors.append(
                    f"side {site.side:+d} lock-drop sample {i} overlaps joint by "
                    f"{overlap:.4f} mm3"
                )
                break

        # Once locked, every named carrier state translates the three rigid pieces together.
        for state_y in spec.state_offsets_y:
            moved_carrier = carrier.translate(cq.Vector(0.0, state_y, 0.0))
            moved_tab = tab.translate(cq.Vector(0.0, state_y, 0.0))
            moved_lock = lock.translate(cq.Vector(0.0, state_y, 0.0))
            overlap = _overlap_volume(moved_carrier, moved_tab)
            overlap += _overlap_volume(moved_carrier, moved_lock)
            overlap += _overlap_volume(moved_tab, moved_lock)
            overlap += _overlap_volume(wall, moved_tab)
            overlap += _overlap_volume(wall, moved_lock)
            if overlap > 1e-5:
                errors.append(
                    f"side {site.side:+d} locked state y={state_y:g} overlaps joint/wall by "
                    f"{overlap:.4f} mm3"
                )

    if tab_volumes and max(tab_volumes) - min(tab_volumes) > 1e-5:
        errors.append(f"handed service-tab volumes differ: {tab_volumes}")
    if lock_volumes and max(lock_volumes) - min(lock_volumes) > 1e-5:
        errors.append(f"handed tab-lock volumes differ: {lock_volumes}")

    expected_sweep = (
        spec.tab_y[0] + spec.release_offset_y,
        spec.tab_y[1] + spec.park_offset_y,
    )
    if iface["tab_slot_y_sweep"] != expected_sweep:
        errors.append(
            f"tab state sweep {iface['tab_slot_y_sweep']} is not {expected_sweep}"
        )

    for error in errors:
        print(f"FAIL {error}")
    if not errors:
        assert bbox is not None
        parked_air = spec.aft_coil_fore_y - (spec.web_aft_y + spec.park_offset_y)
        print(
            "ok  enclosure-tee-carrier  "
            f"steps 4/5/6 lower through {2.0 * spec.lowering_cavity_half_x:g} mm, "
            f"two tabs enter {abs(tab_joint_sites(spec)[0].entry_shift_x):g} mm + lock, "
            f"{len(ties)} ties / {len(slots)} slots, "
            f"lock gable air {iface['tab_lock_entry_air_z']:.3f} mm, "
            f"parked coil air {parked_air:.3f} mm"
        )
    return 1 if errors else 0


def _export_printed_part(body, name: str) -> None:
    step = _here.parent / f"{name}.step"
    stl = _here.parent / f"{name}.stl"
    # The STL is written first so `_cadq_export` knows this is a bed-mesh-owned printed part
    # and does not also make a smooth `.step.mesh` beside it.
    cq.exporters.export(body, str(stl), tolerance=0.02, angularTolerance=0.15)
    print(f"-> {stl.name}")
    export_assembly(one_body(body, name, M_PETGF_BLACK), str(step))
    print(f"-> {step.name}")


def main() -> int:
    if selftest():
        return 1
    _export_printed_part(build_carrier(), "enclosure-tee-carrier")
    for side, handed in ((-1, "left"), (1, "right")):
        _export_printed_part(
            build_service_tab(side=side),
            f"enclosure-tee-carrier-tab-{handed}",
        )
        _export_printed_part(
            build_tab_lock(side=side),
            f"enclosure-tee-carrier-tab-lock-{handed}",
        )
    return 0


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "selftest":
        sys.exit(selftest())
    sys.exit(main())
