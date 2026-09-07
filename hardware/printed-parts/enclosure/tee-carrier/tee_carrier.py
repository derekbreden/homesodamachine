"""Two PET-GF carrier halves with integral service tabs and a central M3 lap joint.

The four tees bear on one Y plane and are tied twice each. Each half carries one spring seat,
guide ear and exterior service tab. Two M3 x 8 screws pass through the right half's counterbores
into M3 x 4 heat-set inserts in the left half. The heads face aft, into the gap between coils.

All geometry is in the enclosure frame: +Y aft, +Z up. Both halves print upright on their
web's lower edge. Assembly is right half down and outward at release, right half to park,
left half down and outward at release, then right half forward to close the lap.
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
    exterior_x: float = 107.5
    tab_recess: float = 0.3
    lowering_cavity_half_x: float = 98.5
    slide_air: float = 0.15
    finger_run: float = 18.0
    finger_air: float = 0.2
    joint_half_x: float = 6.0
    joint_root_x: float = 4.0
    joint_receiver_t: float = 5.0
    joint_lap_t: float = 3.0
    joint_head_depth: float = 3.0
    joint_screw_offsets_z: tuple[float, float] = (-10.0, 10.0)
    joint_screw_length: float = 8.0
    bed_x: float = 325.0
    bed_y: float = 320.0
    bed_z: float = 320.0

    @property
    def web_aft_y(self):
        return self.web_fore_y + self.web_t

    @property
    def tab_y(self):
        return self.web_fore_y, self.web_aft_y

    @property
    def state_offsets_y(self):
        return self.release_offset_y, 0.0, self.connected_offset_y, self.park_offset_y

    @property
    def joint_face_y(self):
        return self.joint_head_seat_y - self.joint_lap_t

    @property
    def joint_head_seat_y(self):
        return self.web_aft_y - self.joint_head_depth

    @property
    def joint_fore_y(self):
        return self.joint_face_y - self.joint_receiver_t

    @property
    def entry_shift_x(self):
        return self.tab_outer_x - self.lowering_cavity_half_x + self.slide_air


DEFAULT_SPEC = CarrierSpec(
    tee_xs=(-79.82, -20.07, 20.07, 79.82), tee_axis_z=190.245,
    web_x=(-94.0, 94.0), web_fore_y=109.718, web_z=(171.245, 209.245),
    spring_xs=(-49.945, 49.945), spring_axis_z=190.245,
    tab_outer_x=107.2, tab_z=(197.0, 217.0),
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
    parts = []
    for side in (-1, 1):
        root = side * spec.web_x[1]
        tip = side * spec.tab_outer_x
        xa, xb = sorted((root, tip))
        pad = _box(xa, xb, *spec.tab_y, *spec.tab_z)
        lower = spec.tab_z[0] - (spec.tab_outer_x - spec.web_x[1])
        ramp = _xz_prism(*spec.tab_y, (
            (root, lower), (tip, spec.tab_z[0]), (root, spec.tab_z[0])))
        parts.append(pad.union(ramp))
    return parts


def joint_sites(spec=DEFAULT_SPEC):
    return tuple((0.0, spec.joint_head_seat_y, spec.tee_axis_z + dz)
                 for dz in spec.joint_screw_offsets_z)


def _cylinder_y(diameter, y0, y1, x, z):
    return cq.Solid.makeCylinder(diameter / 2.0, y1 - y0,
                                cq.Vector(x, y0, z), cq.Vector(0.0, 1.0, 0.0))


def _carrier_blank(spec):
    body = _box(*spec.web_x, spec.web_fore_y, spec.web_aft_y, *spec.web_z)
    body = body.union(_guide_ear_pair(spec))
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
    body = bb.intersect(_box(xa, xb, spec.joint_fore_y - 1.0,
                            spec.web_aft_y + spec.spring_pad_t, spec.web_z[0] - 1.0,
                            spec.tab_z[1] + 1.0))
    if side < 0:
        root = split - spec.joint_root_x
        body = body.union(_box(root, split, spec.joint_fore_y, spec.web_aft_y, *spec.web_z))
        body = body.union(_box(root, spec.joint_half_x, spec.joint_fore_y,
                               spec.joint_face_y, *spec.web_z))
    else:
        body = body.union(_box(split, spec.joint_half_x, spec.joint_face_y,
                               spec.web_aft_y, *spec.web_z))
    for x, seat_y, z in joint_sites(spec):
        body = body.cut(_cylinder_y(enclosure_interface.screw_clear_dia,
                                    spec.joint_fore_y - 1.0, spec.web_aft_y + 1.0, x, z))
        if side > 0:
            body = body.cut(_cylinder_y(enclosure_interface.head_cbore_dia,
                                        seat_y, spec.web_aft_y + spec.slide_air, x, z))
        else:
            body = body.cut(_cylinder_y(enclosure_interface.heatset_dia,
                                        spec.joint_face_y - enclosure_interface.heatset_len,
                                        spec.joint_face_y + spec.slide_air, x, z))
    return body


def build_carrier(spec=DEFAULT_SPEC):
    return cq.Workplane(obj=cq.Compound.makeCompound(
        [build_half(spec, side).val() for side in (-1, 1)]))


def build(spec=DEFAULT_SPEC):
    return build_carrier(spec)


def finger_probes(spec=DEFAULT_SPEC, offset_y=0.0):
    probes = []
    inner = spec.lowering_cavity_half_x + spec.slide_air + spec.finger_air
    outer = spec.exterior_x + 1.0
    for side in (-1, 1):
        xa, xb = (inner, outer) if side > 0 else (-outer, -inner)
        probes.append(_box(xa, xb, spec.web_aft_y + offset_y + spec.finger_air,
                           spec.web_aft_y + offset_y + spec.finger_run,
                           spec.tab_z[0] + spec.finger_air,
                           spec.tab_z[1] - spec.finger_air).val())
    return tuple(probes)


def interface(spec=DEFAULT_SPEC):
    slot_y = (spec.web_fore_y + spec.release_offset_y - spec.slide_air,
              spec.web_aft_y + spec.park_offset_y + spec.finger_run + spec.slide_air)
    ramp_z = spec.tab_z[0] - (spec.tab_outer_x - spec.guide_ear_outer_x)
    slot_z = (ramp_z - spec.slide_air, spec.tab_z[1] + spec.slide_air)
    return {
        'squeeze_offset_y': 0.0,
        'release_offset_y': spec.release_offset_y,
        'connected_offset_y': spec.connected_offset_y,
        'park_offset_y': spec.park_offset_y,
        'web_fore_y': spec.web_fore_y,
        'web_aft_y': spec.web_aft_y,
        'release_fore_stop_y': spec.web_fore_y + spec.release_offset_y,
        'squeeze_reference_aft_y': spec.web_aft_y,
        'park_aft_stop_y': spec.web_aft_y + spec.park_offset_y,
        'guide_ear_x': ((-spec.guide_ear_outer_x, spec.web_x[0]),
                        (spec.web_x[1], spec.guide_ear_outer_x)),
        'guide_ear_y': spec.tab_y,
        'guide_ear_z': spec.guide_ear_z,
        'spring_seats': tuple((x, spec.web_fore_y, spec.spring_axis_z) for x in spec.spring_xs),
        'tab_slot_y_sweep': (spec.web_fore_y + spec.release_offset_y,
                              spec.web_aft_y + spec.park_offset_y),
        'tab_slot_z': spec.tab_z,
        'tab_pad_x': ((-spec.tab_outer_x, -spec.lowering_cavity_half_x - spec.slide_air),
                     (spec.lowering_cavity_half_x + spec.slide_air, spec.tab_outer_x)),
        'service_slot_x': (spec.guide_ear_outer_x, spec.exterior_x + 1.0),
        'service_slot_y': slot_y,
        'service_slot_z': slot_z,
        'service_slot_roof_z': slot_z[1] + (slot_y[1] - slot_y[0]) / 2.0,
        'lowering_cavity_x': (-spec.lowering_cavity_half_x, spec.lowering_cavity_half_x),
        'carrier_lowering_air_x': spec.slide_air,
        'half_entry_shift_x': spec.entry_shift_x,
        'half_install_order': (1, -1),
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
        shifted = solid.translate((-side * spec.entry_shift_x, 0.0, 0.0)).BoundingBox()
        air = spec.lowering_cavity_half_x - max(abs(shifted.xmin), abs(shifted.xmax))
        if air < spec.slide_air - 1e-6:
            errors.append(f'half {side:+d} leaves {air:g} mm in its lowering position')
        slots, _ = _tie_cutters(spec)
        for slot in slots:
            if solid.intersect(slot.val()).Volume() > 1e-5:
                errors.append(f'half {side:+d} obstructs a tee tie slot')
    if halves[-1].intersect(halves[1]).Volume() > 1e-5:
        errors.append('the two assembled halves overlap')
    contact = halves[-1].intersect(halves[1].translate((0.0, -0.001, 0.0))).Volume()
    if contact < 0.1:
        errors.append('the lap has no mating bearing face')
    if abs(spec.joint_head_seat_y - spec.joint_screw_length - spec.joint_fore_y) > 1e-6:
        errors.append('joint screw does not finish flush with the carrier fore face')
    if spec.joint_receiver_t <= enclosure_interface.heatset_len:
        errors.append('the receiver has no material behind the insert')
    right_park = halves[1].translate((0.0, spec.park_offset_y, 0.0))
    left_release = halves[-1].translate((0.0, spec.release_offset_y, 0.0))
    for i in range(31):
        left = left_release.translate((spec.entry_shift_x * (1.0 - i / 30), 0, 0))
        if left.intersect(right_park).Volume() > 1e-5:
            errors.append('left half crosses parked right half during outward entry')
            break
    for i in range(31):
        dy = spec.park_offset_y + (spec.release_offset_y - spec.park_offset_y) * i / 30
        if halves[1].translate((0, dy, 0)).intersect(left_release).Volume() > 1e-5:
            errors.append('right half crosses left half while the lap closes')
            break
    complete = build_carrier(spec).val()
    for dy in spec.state_offsets_y:
        for finger in finger_probes(spec, dy):
            if finger.intersect(complete.translate((0, dy, 0))).Volume() > 1e-5:
                errors.append(f'carrier obstructs finger contact at y={dy:g}')
    for error in errors:
        print('FAIL', error)
    if not errors:
        print(f'ok enclosure-tee-carrier: two valid halves, integral grips, '
              f'{spec.entry_shift_x:g} mm outward entry, two M3 x '
              f'{spec.joint_screw_length:g} lap screws, eight unobstructed tie paths')
    return int(bool(errors))


def _export_printed_part(body, name):
    from flute_payload import cut

    step = _here.parent / f'{name}.step'
    stl = _here.parent / f'{name}.stl'
    cq.exporters.export(body, str(stl), tolerance=0.02, angularTolerance=0.15)
    export_assembly(one_body(body, name, M_PETGF_BLACK), str(step))
    cut(step, stl)
    print(f'-> {name}.step / .stl')


def main():
    if selftest():
        return 1
    for side, name in ((-1, 'left'), (1, 'right')):
        _export_printed_part(build_half(side=side), f'enclosure-tee-carrier-{name}')
    return 0


if __name__ == '__main__':
    if sys.argv[1:] == ['selftest']:
        if selftest():
            sys.exit(1)
    elif main():
        sys.exit(1)
