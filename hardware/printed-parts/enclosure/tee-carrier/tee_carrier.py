"""Two PET-GF carrier halves with closed sliding handholds and a central M3 lap joint.

The four tees bear on one Y plane and are tied twice each. Each half carries one spring seat
and one deep service tab. Two M3 x 8 screws pass through the left half's counterbores
into M3 x 4 heat-set inserts in the right half. The heads face the empty cartridge bay.

All geometry is in the enclosure frame: +Y aft, +Z up. Each half enters the loose enclosure
from its open rear, lowers through an outer tee well and seats outward into its side recess.
The handholds finish flush with the enclosure. Their retaining rims bear behind the wall;
the fixed body's flat lands and the handholds' top and bottom faces guide Y travel.
The central lap stands above the tee run ends, and each finger recess has its own closed back.
"""

from __future__ import annotations

import math
import sys
from dataclasses import dataclass
from pathlib import Path

import cadquery as cq

_here = Path(__file__).resolve()
_hw = next(p for p in _here.parents if p.name == "hardware")
sys.path[:0] = [str(_hw / "scripts"), str(_hw / "reference" / "tee-connector"),
               str(_here.parent.parent / "enclosure")]
from _cadq_export import export_assembly
from _material_base import M_PETGF_BLACK, one_body
import _enclosure_interface as enclosure_interface
import tee_connector as tee


@dataclass(frozen=True)
class CarrierSpec:
    tee_xs: tuple[float, ...]
    tee_axis_z: float
    web_x: tuple[float, float]
    web_fore_y: float
    web_z: tuple[float, float]
    spring_xs: tuple[float, float]
    spring_axis_z: float
    tab_outer_x: float
    tab_z: tuple[float, float]
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
    exterior_x: float = 107.5
    guide_inner_x: float = 98.5
    slide_air: float = 0.15
    finger_run: float = 22.0
    finger_air: float = 0.2
    grip_bar_t: float = 16.0
    grip_back_x: float = 90.295
    grip_back_t: float = 2.5
    grip_rail_outer_x: float = 103.65
    grip_rail_top_z: float = 174.95
    grip_roof_t: float = 4.0
    grip_aft_t: float = 4.0
    grip_rim_t: float = 3.0
    grip_wall_t: float = 3.0
    grip_overlap: float = 3.0
    grip_top_overlap: float = 4.0
    grip_corner_r: float = 5.0
    grip_edge_r: float = 3.0
    grip_rim_corner_r: float = 5.0
    grip_root_overlap: float = 0.2
    entry_inset_x: float | None = None
    entry_staging_y: float = 18.5
    entry_lift_z: float = 70.0
    joint_half_x: float = 9.0
    joint_root_x: float = 4.0
    joint_receiver_t: float = 6.0
    joint_lap_t: float = 6.0
    joint_head_depth: float = 3.0
    joint_screw_xs: tuple[float, float] = (-4.5, 4.5)
    joint_screw_length: float = 8.0
    bed_x: float = 325.0
    bed_y: float = 320.0
    bed_z: float = 320.0

    @property
    def web_aft_y(self):
        return self.web_fore_y + self.web_t

    @property
    def tab_y(self):
        return self.web_aft_y - self.grip_bar_t, self.web_aft_y

    @property
    def grip_y(self):
        return self.tab_y[0], self.web_aft_y + self.finger_run + self.grip_aft_t

    @property
    def grip_z(self):
        return self.web_z[0], self.tab_z[1] + self.grip_roof_t

    @property
    def rim_y(self):
        margin = self.park_offset_y - self.release_offset_y + self.grip_overlap
        return self.grip_y[0] - margin, self.grip_y[1] + margin

    @property
    def rim_z(self):
        margin = self.grip_top_overlap + self.slide_air
        return self.grip_rail_top_z, self.grip_z[1] + margin

    @property
    def rim_x(self):
        outer = self.exterior_x - self.grip_wall_t - self.slide_air
        return outer - self.grip_rim_t, outer

    @property
    def joint_z(self):
        return self.tee_axis_z + tee.RUN_HALF + self.slide_air, self.web_z[1]

    @property
    def grip_root_x(self):
        return (min(self.web_x[1] - self.grip_root_overlap, self.grip_back_x),
                max(self.web_x[1], self.grip_back_x + self.grip_root_overlap))

    @property
    def state_offsets_y(self):
        return self.release_offset_y, 0.0, self.connected_offset_y, self.park_offset_y

    @property
    def joint_face_y(self):
        return self.web_aft_y - self.joint_lap_t

    @property
    def joint_head_seat_y(self):
        return self.joint_fore_y + self.joint_head_depth

    @property
    def joint_fore_y(self):
        return self.joint_face_y - self.joint_receiver_t

    @property
    def entry_shift_x(self):
        if self.entry_inset_x is not None:
            return self.entry_inset_x
        # Lower the complete cup on the outer tee-well axis before seating it
        # outward. This follows the cup depth and keeps its floor inside the well.
        return (self.grip_back_x + self.tab_outer_x) / 2.0 - max(self.tee_xs)

    @property
    def entry_shoulder_inset_x(self):
        return self.grip_wall_t + self.slide_air


DEFAULT_SPEC = CarrierSpec(
    tee_xs=(-79.82, -20.07, 20.07, 79.82), tee_axis_z=190.245,
    web_x=(-94.0, 94.0), web_fore_y=109.718, web_z=(171.245, 220.165),
    spring_xs=(-49.945, 49.945), spring_axis_z=190.245,
    tab_outer_x=107.5, tab_z=(177.245, 217.245),
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
    """A semicircular crown around the spring seat and a rectangle to the web's lower edge."""
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


def _xz_prism(
    y0: float,
    y1: float,
    points: tuple[tuple[float, float], ...],
):
    """Extrude one XZ polygon along +Y."""
    plane = cq.Plane(origin=(0.0, y0, 0.0), xDir=(1.0, 0.0, 0.0), normal=(0.0, -1.0, 0.0))
    return cq.Workplane(plane).polyline(points).close().extrude(-(y1 - y0))


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


def _service_tabs(spec):
    """Flush closed finger cups with broad retaining rims behind the enclosure wall.

    The fore bar thickens directly from the web. Its aft face bears the fingers' forward
    pull. The two internal rims bear against opposite wall shoulders and capture X once
    the halves are joined. The lower inboard face clears the enclosure's seam rail.
    """
    outer = spec.tab_outer_x
    body = _box(spec.grip_back_x, outer, *spec.grip_y, *spec.grip_z)
    # The outer floor is one continuous lower bearing. Its inboard underside clears the
    # enclosure's seam head along the complete grip length.
    body = body.cut(_box(spec.grip_back_x - 1.0, spec.grip_rail_outer_x,
                         spec.grip_y[0] - 1.0, spec.grip_y[1] + 1.0,
                         spec.grip_z[0] - 1.0, spec.grip_rail_top_z))
    rim = (_box(*spec.rim_x, *spec.rim_y, *spec.rim_z)
           .edges('|X').fillet(spec.grip_rim_corner_r))
    body = body.union(rim)
    pocket_y = (spec.web_aft_y, spec.web_aft_y + spec.finger_run)
    pocket = (_box(spec.grip_back_x + spec.grip_back_t, outer + 1.0,
                   *pocket_y, *spec.tab_z).edges('|X').fillet(spec.grip_corner_r))
    body = body.cut(pocket)
    edges = [edge for edge in body.val().Edges()
             if abs(edge.BoundingBox().xmin - outer) < 1e-6
             and abs(edge.BoundingBox().xmax - outer) < 1e-6
             and pocket_y[0] - 1e-6 <= edge.Center().y <= pocket_y[1] + 1e-6
             and spec.tab_z[0] - 1e-6 <= edge.Center().z <= spec.tab_z[1] + 1e-6]
    body = cq.Workplane(obj=body.val().fillet(spec.grip_edge_r, edges))
    root = _box(*spec.grip_root_x,
                *spec.tab_y, spec.grip_rail_top_z, spec.web_z[1])
    body = body.union(root)
    return body.mirror('YZ'), body


def joint_sites(spec=DEFAULT_SPEC):
    z = sum(spec.joint_z) / 2.0
    return tuple((x, spec.joint_head_seat_y, z) for x in spec.joint_screw_xs)


def _cylinder_y(diameter, y0, y1, x, z):
    return cq.Solid.makeCylinder(diameter / 2.0, y1 - y0,
                                cq.Vector(x, y0, z), cq.Vector(0.0, 1.0, 0.0))


def _carrier_blank(spec):
    body = _box(*spec.web_x, spec.web_fore_y, spec.web_aft_y, *spec.web_z)
    for x in spec.spring_xs:
        body = body.union(_spring_rail(spec, x))
    for tab in _service_tabs(spec):
        body = body.union(tab)
    slots, recesses = _tie_cutters(spec)
    for cutter in (*slots, *recesses):
        body = body.cut(cutter)
    for x in spec.spring_xs:
        body = body.cut(_teardrop_y(
            x, spec.web_fore_y - spec.slide_air, spec.spring_axis_z, spec.spring_seat_d,
            spec.spring_seat_depth + spec.slide_air, spec.spring_roof_angle_deg))
    return body


def build_half(spec=DEFAULT_SPEC, side=1):
    if side not in (-1, 1):
        raise ValueError('carrier half must be -1 or +1')
    split = -spec.joint_half_x
    bb = _carrier_blank(spec)
    span = spec.tab_outer_x + spec.slide_air
    xa, xb = (-span, split) if side < 0 else (split, span)
    bounds = bb.val().BoundingBox()
    body = bb.intersect(_box(xa, xb, bounds.ymin - 1.0, bounds.ymax + 1.0,
                            bounds.zmin - 1.0, bounds.zmax + 1.0))
    if side < 0:
        root = split - spec.joint_root_x
        body = body.union(_box(root, split, spec.joint_fore_y, spec.web_aft_y, *spec.joint_z))
        body = body.union(_box(root, spec.joint_half_x, spec.joint_fore_y,
                               spec.joint_face_y, *spec.joint_z))
    else:
        body = body.union(_box(split, spec.joint_half_x, spec.joint_face_y,
                               spec.web_aft_y, *spec.joint_z))
    for x, seat_y, z in joint_sites(spec):
        body = body.cut(_cylinder_y(enclosure_interface.screw_clear_dia,
                                    spec.joint_fore_y - 1.0, spec.web_aft_y + 1.0, x, z))
        if side < 0:
            body = body.cut(_cylinder_y(enclosure_interface.head_cbore_dia,
                                        spec.joint_fore_y - spec.slide_air, seat_y, x, z))
        else:
            body = body.cut(_cylinder_y(enclosure_interface.heatset_dia,
                                        spec.joint_face_y - spec.slide_air,
                                        spec.joint_face_y + enclosure_interface.heatset_len, x, z))
    return body


def build_carrier(spec=DEFAULT_SPEC):
    return cq.Workplane(obj=cq.Compound.makeCompound(
        [build_half(spec, side).val() for side in (-1, 1)]))


def build(spec=DEFAULT_SPEC):
    return build_carrier(spec)


def finger_probes(spec=DEFAULT_SPEC, offset_y=0.0):
    probes = []
    inner = spec.grip_back_x + spec.grip_back_t + spec.finger_air
    outer = spec.tab_outer_x + 1.0
    for side in (-1, 1):
        xa, xb = (inner, outer) if side > 0 else (-outer, -inner)
        probes.append(_box(xa, xb, spec.web_aft_y + offset_y + spec.finger_air,
                           spec.web_aft_y + offset_y + spec.finger_run - spec.finger_air,
                           spec.tab_z[0] + spec.finger_air,
                           spec.tab_z[1] - spec.finger_air)
                      .edges('|X').fillet(spec.grip_corner_r).val())
    return tuple(probes)


def insertion_envelopes(spec=DEFAULT_SPEC, side=1):
    """Rectangular bounds enclosing each half's web, joint, spring seat, root, cup and rim.

    The assembly reads every segment of the inside-out route against the fixed body and
    seated tees. Separate cup-floor bounds retain the real seam-rail relief.
    """
    split = -spec.joint_half_x
    web_x = (spec.web_x[0], split) if side < 0 else (split, spec.web_x[1])
    rows = [('web', web_x, (spec.web_fore_y, spec.web_aft_y), spec.web_z)]
    radius = spec.spring_pad_d / 2.0
    x = spec.spring_xs[0 if side < 0 else 1]
    rows.append(('spring seat', (x - radius, x + radius),
                 (spec.web_fore_y, spec.web_fore_y + spec.spring_pad_t),
                 (spec.web_z[0], spec.spring_axis_z + radius)))
    if side < 0:
        rows.extend((
            ('joint root', (split - spec.joint_root_x, split),
             (spec.joint_fore_y, spec.web_aft_y), spec.joint_z),
            ('joint tongue', (split - spec.joint_root_x, spec.joint_half_x),
             (spec.joint_fore_y, spec.joint_face_y), spec.joint_z)))
    else:
        rows.append(('joint', (split, spec.joint_half_x),
                     (spec.joint_face_y, spec.web_aft_y), spec.joint_z))

    def handed(xs):
        return xs if side > 0 else (-xs[1], -xs[0])

    rows.extend((
        ('grip root', handed(spec.grip_root_x), spec.tab_y,
         (spec.grip_rail_top_z, spec.web_z[1])),
        ('cup', handed((spec.grip_back_x, spec.tab_outer_x)),
         spec.grip_y, (spec.grip_rail_top_z, spec.grip_z[1])),
        ('cup floor', handed((spec.grip_rail_outer_x, spec.tab_outer_x)),
         spec.grip_y, (spec.grip_z[0], spec.grip_rail_top_z)),
        ('rim', handed(spec.rim_x),
         spec.rim_y, spec.rim_z)))
    return tuple((name, _box(*xs, *ys, *zs).val()) for name, xs, ys, zs in rows)


def insertion_poses(spec=DEFAULT_SPEC, side=1, entry_y=None, rear_y=210.0):
    """Axis-aligned poses taking a complete half from the rear to its internal shoulder."""
    if entry_y is None:
        entry_y = spec.release_offset_y if side < 0 else spec.park_offset_y
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


def insertion_sweeps(spec=DEFAULT_SPEC, side=1, entry_y=None, rear_y=210.0):
    """Complete rectangular sweeps enclosing the whole half on every straight path segment."""
    poses = insertion_poses(spec, side, entry_y, rear_y)
    for (_before, start), (stage, end) in zip(poses, poses[1:]):
        if sum(abs(a - b) > 1e-8 for a, b in zip(start, end)) != 1:
            raise ValueError(f'{stage} must be a single-axis insertion segment')
        for name, shape in insertion_envelopes(spec, side):
            bb = shape.BoundingBox()
            spans = [(getattr(bb, axis + 'min') + min(a, b),
                      getattr(bb, axis + 'max') + max(a, b))
                     for axis, a, b in zip('xyz', start, end)]
            yield stage, name, _box(*spans[0], *spans[1], *spans[2]).val()


def interface(spec=DEFAULT_SPEC):
    slot_y = (spec.grip_y[0] + spec.release_offset_y,
              spec.grip_y[1] + spec.park_offset_y)
    slot_z = (spec.grip_z[0] - spec.slide_air, spec.grip_z[1] + spec.slide_air)
    return {
        'squeeze_offset_y': 0.0,
        'release_offset_y': spec.release_offset_y,
        'connected_offset_y': spec.connected_offset_y,
        'park_offset_y': spec.park_offset_y,
        'web_fore_y': spec.web_fore_y,
        'web_aft_y': spec.web_aft_y,
        'web_x': spec.web_x,
        'web_z': spec.web_z,
        'joint_z': spec.joint_z,
        'joint_work_fore_y': spec.joint_fore_y + spec.release_offset_y - spec.slide_air,
        'release_fore_stop_y': slot_y[0],
        'squeeze_reference_aft_y': spec.web_aft_y,
        'park_aft_stop_y': slot_y[1],
        'guide_body_y': spec.grip_y,
        'guide_body_z': spec.grip_z,
        'guide_bearing_length': spec.grip_y[1] - spec.grip_y[0],
        'guide_slide_air': spec.slide_air,
        'grip_bar_t': spec.grip_bar_t,
        'grip_pocket_depth': spec.tab_outer_x - spec.grip_back_x - spec.grip_back_t,
        'grip_back_x': spec.grip_back_x,
        'grip_back_t': spec.grip_back_t,
        'grip_rail_outer_x': spec.grip_rail_outer_x,
        'grip_rail_top_z': spec.grip_rail_top_z,
        'grip_rim_y': spec.rim_y,
        'grip_rim_z': spec.rim_z,
        'grip_rim_t': spec.grip_rim_t,
        'grip_rim_x': spec.rim_x,
        'grip_wall_t': spec.grip_wall_t,
        'grip_overlap': spec.grip_overlap,
        'grip_outer_x': spec.tab_outer_x,
        'grip_projection': spec.tab_outer_x - spec.exterior_x,
        'spring_seats': tuple((x, spec.web_fore_y, spec.spring_axis_z) for x in spec.spring_xs),
        'tab_slot_y_sweep': (spec.tab_y[0] + spec.release_offset_y,
                              spec.web_aft_y + spec.park_offset_y),
        'tab_slot_z': spec.tab_z,
        'tab_pad_x': ((-spec.tab_outer_x, -spec.grip_back_x - spec.grip_back_t),
                     (spec.grip_back_x + spec.grip_back_t, spec.tab_outer_x)),
        'service_slot_x': (spec.exterior_x - spec.grip_wall_t, spec.exterior_x + 1.0),
        'service_slot_y': slot_y,
        'service_slot_z': slot_z,
        'half_entry_shift_x': spec.entry_shift_x,
        'half_install_order': (-1, 1),
        'half_entry_offsets_y': (spec.release_offset_y, spec.park_offset_y),
        'half_entry_staging_y': spec.entry_staging_y,
        'half_entry_lift_z': spec.entry_lift_z,
        'half_entry_shoulder_inset_x': spec.entry_shoulder_inset_x,
        'joint_sites': joint_sites(spec),
        'joint_face_y': spec.joint_face_y,
        'joint_fore_y': spec.joint_fore_y,
        'joint_screw_length': spec.joint_screw_length,
        'joint_insert_length': enclosure_interface.heatset_len,
        'joint_count': len(joint_sites(spec)),
        'finger_run': spec.finger_run,
        'printed_parts': ('enclosure-tee-carrier-left', 'enclosure-tee-carrier-right'),
        'tie_sites': tuple({'tee_x': site.tee_x, 'band_z': site.band_z,
                            'slot_xs': site.slot_xs, 'head_side': site.head_side}
                           for site in tie_sites(spec)),
    }


def selftest(spec=DEFAULT_SPEC):
    errors = []
    halves = {side: build_half(spec, side).val() for side in (-1, 1)}
    for side, solid in halves.items():
        bb = solid.BoundingBox()
        if len(solid.Solids()) != 1 or not solid.isValid():
            errors.append(f'half {side:+d} is not one valid solid')
        if bb.xlen > spec.bed_x or bb.ylen > spec.bed_y or bb.zlen > spec.bed_z:
            errors.append(f'half {side:+d} exceeds the print bed')
        if max(abs(bb.xmin), abs(bb.xmax)) > spec.exterior_x + 1e-6:
            errors.append(f'half {side:+d} projects beyond the enclosure width')
        shifted = solid.translate((-side * spec.entry_shift_x, 0.0, 0.0)).BoundingBox()
        if max(abs(shifted.xmin), abs(shifted.xmax)) > spec.exterior_x - spec.slide_air:
            errors.append(f'half {side:+d} does not start inside the enclosure width')
        slots, _ = _tie_cutters(spec)
        for slot in slots:
            if solid.intersect(slot.val()).Volume() > 1e-5:
                errors.append(f'half {side:+d} obstructs a tee tie slot')
    if halves[-1].intersect(halves[1]).Volume() > 1e-5:
        errors.append('the two assembled halves overlap')
    contact = halves[-1].intersect(halves[1].translate((0.0, -0.001, 0.0))).Volume()
    if contact < 0.1:
        errors.append('the lap has no mating bearing face')
    screw_tip_y = spec.joint_head_seat_y + spec.joint_screw_length
    if not (spec.joint_face_y + enclosure_interface.heatset_len <= screw_tip_y < spec.web_aft_y):
        errors.append('joint screw does not engage the full insert with aft backing')
    if spec.joint_lap_t <= enclosure_interface.heatset_len:
        errors.append('the receiver has no material behind the insert')
    left_release = halves[-1].translate((0.0, spec.release_offset_y, 0.0))
    for stage, name, sweep in insertion_sweeps(spec, 1):
        if sweep.intersect(left_release).Volume() > 1e-5:
            errors.append(f'right half {name} crosses the left half during {stage}')
    for i in range(31):
        dy = spec.park_offset_y + (spec.release_offset_y - spec.park_offset_y) * i / 30
        if halves[1].translate((0, dy, 0)).intersect(left_release).Volume() > 1e-5:
            errors.append('right half crosses left half while the lap closes')
            break
    complete = build_carrier(spec).val()
    data = interface(spec)
    for dy in spec.state_offsets_y:
        for finger in finger_probes(spec, dy):
            if finger.intersect(complete.translate((0, dy, 0))).Volume() > 1e-5:
                errors.append(f'carrier obstructs finger contact at y={dy:g}')
        overlap = min(data['service_slot_y'][0] - spec.rim_y[0] - dy,
                      spec.rim_y[1] + dy - data['service_slot_y'][1],
                      spec.rim_z[1] - data['service_slot_z'][1])
        if overlap < spec.grip_overlap - 1e-6:
            errors.append(f'grip rim overlaps its opening by only {overlap:g} mm')
    # The finger recess ends on continuous back material; its front bar reaches the web.
    for side, shape in halves.items():
        xa, xb = sorted((side * (spec.grip_back_x + 0.1),
                         side * (spec.grip_back_x + spec.grip_back_t - 0.1)))
        backing = _box(xa, xb, spec.web_aft_y, spec.web_aft_y + spec.finger_run,
                       *spec.tab_z).val()
        if backing.cut(shape).Volume() > 1e-5:
            errors.append(f'half {side:+d} has an opening through its finger-pocket back')
    for error in errors:
        print('FAIL', error)
    if not errors:
        print(f'ok enclosure-tee-carrier: two valid halves, closed grips, '
              f'flush faces and inside-out entry, two M3 x '
              f'{spec.joint_screw_length:g} lap screws, eight unobstructed tie paths')
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
    values = {
        'GRIP_BAR_T': spec.grip_bar_t, 'FINGER_RUN': spec.finger_run,
        'FINGER_HEIGHT': spec.tab_z[1] - spec.tab_z[0],
        'FINGER_DEPTH': spec.tab_outer_x - spec.grip_back_x - spec.grip_back_t,
        'GRIP_CORNER_R': spec.grip_corner_r, 'GRIP_EDGE_R': spec.grip_edge_r,
        'GRIP_RIM_CORNER_R': spec.grip_rim_corner_r,
        'GRIP_PROJECTION': spec.tab_outer_x - spec.exterior_x,
        'GRIP_WIDTH': 2 * spec.tab_outer_x, 'GRIP_OVERLAP': spec.grip_overlap,
        'GRIP_BACK_T': spec.grip_back_t, 'GUIDE_LENGTH': spec.grip_y[1] - spec.grip_y[0],
        'GUIDE_AIR': spec.slide_air, 'ENTRY_FROM_PARK': spec.park_offset_y - spec.connected_offset_y,
        'RIM_BED_GAP': spec.rim_z[0] - spec.web_z[0],
    }
    substitute_md(_here.parent / 'README.md', {key: f'{value:.6g} mm' for key, value in values.items()})


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
