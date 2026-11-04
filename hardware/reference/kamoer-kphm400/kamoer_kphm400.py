"""Reference mock: Kamoer KPHM400-SW3B25 peristaltic pump, sub-categorized.

A coarse keep-out approximation of the pump as it sits inside the case,
sectioned into functional sub-bodies (head, rotor housing, motor body).
Envelopes combine catalog dimensions with cartridge fit measurements — see
`off-the-shelf-parts/kamoer-kphm400/extracted-results/geometry-description.md`.

The model is authored in the PUMP-CASE WORLD FRAME: origin at the base-plate
bore-opening face, the head datum centered at (cx, cy), and the pump's depth
axis along world +Z (head front at -Z, motor at +Z). Width and height lie in X
and Y. The rear boss and motor share their measured axis one millimetre toward
-Y from that head datum; consumers locating the head and rear stack therefore
read the two datums separately.

The head and rotor profile are derived live from `pump_case`:
- The head is the datasheet head block clipped to the skirt + lower-extension
  inner cavity, so it fills that cavity and stops at every wall.
- The rotor housing takes the octagon-bore profile (ledges and all) from the
  base plane to the tower-bore start, on the rear stack's offset axis.

The motor is the part's own can, not the hole it turns in. The three bodies end
at `pump_len` off the fitted head's front face, and the tower bore the motor
sits inside does not size it. A consumer reading this module's STEP gets the pump.

The pump's two outlet barbs sit on the body's +Y face (`body_y_face`) at the
arch-notch positions and reach out toward the case wall (`y_face`); this model
draws no tubing — `barb(i)` is each as a station in the pump's own frame, for
whatever seats the pump and attaches downstream.


The reference STEP and payloads are declared in `frozen-asset.json`.
Native builder functions remain available to current composition callers.
The native pump body retains its live authored `pump_case` dimensions and cavity.
"""

from __future__ import annotations

import sys
from pathlib import Path
from functools import cache as _reference_cache

_REFERENCE_DIR = Path(__file__).resolve().parent
STEP_PATH = _REFERENCE_DIR / 'kamoer-kphm400.step'
PAYLOAD_PATH = _REFERENCE_DIR / 'kamoer-kphm400.step.mesh'
FINE_PAYLOAD_PATH = _REFERENCE_DIR / 'kamoer-kphm400.step.mesh'
ASSET_MANIFEST_PATH = _REFERENCE_DIR / "frozen-asset.json"

def main():
    print(f"Frozen STEP: {STEP_PATH}")
    print(f"Display payload: {PAYLOAD_PATH}")
    print(f"Fine payload: {FINE_PAYLOAD_PATH}")


if __name__ == "__main__":
    main()
    raise SystemExit(0)


_here = Path(__file__).resolve()
_hw = next(p for p in _here.parents if p.name == "hardware")
for _p in (_hw / "scripts", _hw / "printed-parts" / "cadlib", _hw / "printed-parts" / "enclosure" / "pump-tray"):
    sys.path.insert(0, str(_p))
import pump_case as pc


# --- Case-interior anchors (derived live from pump_case) --------------------

_reference_hardware = next(p for p in Path(__file__).resolve().parents if p.name == 'hardware')
import sys as _reference_sys
_reference_sys.path.insert(0, str(_reference_hardware / 'reference'))
from _reference_data import data as _reference_data
_reference_values = _reference_data('kamoer_kphm400', inputs={'pc': {name: getattr(pc, name) for name in ('bore_bottom_z', 'center_x', 'center_y', 'pos_y_face_y', 'skirt_bottom_z')}})
globals().update({name: _reference_values[name] for name in ('cx', 'cy', 'rear_axis_y_shift', 'rear_axis_y', 'base_plane_z', 'octagon_top_z', 'outlet_above_skirt_bottom', 'arch_plane_z', 'y_face', 'tube_casing_w', 'shaft_w', 'outlet_span_x', 'barb_pitch', 'outlet_open_span_x', 'arch_xs', 'skirt_depth', 'head_front_below_skirt', 'skirt_support_air', 'skirt_y', 'skirt_y_max', 'skirt_y_plus_air', 'skirt_upper_band', 'skirt_body_y', 'skirt_support_xy_air', 'skirt_support_y_minus', 'skirt_support_y_plus', 'skirt_body_y_max', 'skirt_body_y_min', 'head_w', 'head_depth', 'motor_dia', 'motor_reach', 'pump_len', 'body_y_face', 'bracket_w', 'bracket_t', 'bracket_z', 'outlet_relief', 'outlet_relief_top_z', 'outlet_relief_run', 'head_front_z', 'motor_end_z')})

# THE REAR STACK IS NOT CONCENTRIC WITH THE HEAD DATUM. The fitted octagon and motor-can
# readings put their common axis one millimetre toward Y- while the head, barbs and lower
# seating faces remain on the case datum. This is part geometry, not assembly clearance: the
# boss and can both take it, and anything seating the head must not silently take it too.
# Outlet-port X positions on the +Y face — where the pump's two built-in tube casings cross the
# wall. The two 12.75 mm casings span 72.50 mm outside-to-outside, putting their axes 59.75 mm
# apart — approximately the measured 60 mm centre pitch. Their 13 mm holder shafts leave
# 0.125 mm per side and span 72.75 mm outside-to-outside.
# Outermost rigid front-cover rim below the measured underside bearing plane. This envelope
# is independent of the coarse case-clipped head solid and excludes spray fixtures/tubing.
# The skirt's measured Y span and +Y holder clearance. Its +Y face is 30.11 mm from the pump
# axis; the cartridge opens 0.30 mm beyond it and carries only 3 mm of upper band behind that.
# The lower head body between the two skirt overhangs, measured along Y in the pump frame.
# Its holder room is 54.3 mm: 54 mm of body plus 0.15 mm per face. Place that room so the
# case-profile land is 5 mm on Y- and the remaining rectangular land is 3.482 mm on Y+.

# --- Reference dimensions and fitted axial datums -------------------------
# The rigid molded skirt carries the clamp load between its head-facing underside and the
# motor-facing outer rim. Its observed thickness is 8 mm; no additional plate stands above
# the rear flange datum. The compatibility names below describe that flange footprint.
# scan-review.md and scan-measurements.json retain the independent bearing-strip observations.
# THE OUTLET SIDE FALLS BACK UNDER ITS BARBS, STATED AND NOT MEASURED HERE. The datasheet
# gives one envelope and this module drew it as a block, because nothing had ever needed the
# face: `pump_case`'s own wall stood well clear of it. What needs it is a seat that reaches in
# BEHIND the head to hold it — under the barbs the part falls back this far off the face they
# stand on, and holds that fall from its front face up. The figure is confirmed on the part,
# and it is confirmed as barely: a consumer taking a hold in it takes the whole of it.
# --- Axial seams (case frame; -Z = head front, +Z = motor rear) -------------


# --- The two barbs, as stations ---------------------------------------------
# A peristaltic head has no fixed sense — the rotor turns whichever way the motor is wired —
# so which barb draws is the assignment of whatever seats the pump.

def barb(i: int):
    "One of the two outlet barbs: `(position, outward axis)` in the pump's own frame.\n\n    It stands on the body's +Y face, `outlet_above_skirt_bottom` above the case's skirt-bottom\n    plane, and reaches out toward the case wall — so the axis is +Y."
    return _reference_data('kamoer_kphm400', 'barb', (i,), {}, inputs={'pc': {name: getattr(pc, name) for name in ('bore_bottom_z', 'center_x', 'center_y', 'pos_y_face_y', 'skirt_bottom_z')}})


def barbs():
    "Both, in `arch_xs` order — west to east across the head's own face."
    return _reference_data('kamoer_kphm400', 'barbs', (), {}, inputs={'pc': {name: getattr(pc, name) for name in ('bore_bottom_z', 'center_x', 'center_y', 'pos_y_face_y', 'skirt_bottom_z')}})


def _zcyl(r, z0, z1, ox=cx, oy=cy):
    import cadquery as cq
    return cq.Solid.makeCylinder(r, z1 - z0, cq.Vector(ox, oy, z0), cq.Vector(0, 0, 1))


def _zbox(w, d, z0, z1, ox=cx, oy=cy):
    import cadquery as cq
    return (cq.Workplane("XY")
            .box(w, d, z1 - z0, centered=(True, True, False))
            .translate((ox, oy, z0))
            .val())


def build_head():
    """Datasheet head block clipped to the case cavity: fills the skirt +
    lower-extension void and stops at every wall instead of poking through.

    WHAT THE CLIP LEAVES THE PART IS ITS SEAT. The upper skirt runs 8 mm below the bracket
    plane, then steps to the narrower body on one horizontal face. The outlet side falls back
    under its tube casings, which is the one thing here the case did not shape and the
    datasheet does not carry — see `outlet_relief`."""
    import cadquery as cq
    box = _zbox(head_w, head_w, head_front_z, base_plane_z)
    relief = (cq.Workplane("XY")
              .box(head_w + 2.0, outlet_relief + 2.0, outlet_relief_run,
                   centered=(True, False, False))
              .translate((cx, body_y_face - outlet_relief, head_front_z))
              .val())
    head = box.intersect(pc.stepped_skirt_cavity(
        0.0, -skirt_depth,
        (skirt_body_y_min, skirt_body_y_max),
        skirt_y_max).val()).cut(relief)
    return cq.Workplane(obj=head)


def build_rotor_housing():
    """The head's offset rear boss, shaped to the octagon bore (ledges included),
    from the base plane up to the tower-bore start."""
    import cadquery as cq
    boss = (pc.WorldWorkplane(pc.xy_plane_z_up)
            .workplane(offset=base_plane_z)
            .center(cx, rear_axis_y)
            .polyline(pc._ring(pc.bore_profile)).wire()
            .extrude(octagon_top_z - base_plane_z))
    return cq.Workplane(obj=boss.val())


def build_motor_body():
    """Silver DC motor: a plain round cylinder from the boss's rear face to the
    part's own end cap. The tower bore is what it turns inside, not its length."""
    import cadquery as cq
    return cq.Workplane(obj=_zcyl(
        motor_dia / 2, octagon_top_z, motor_end_z, oy=rear_axis_y))


# The pump's body sub-bodies as (name, builder, color). Public so the pump
# assembly (pump + fittings) can seat the same body without redrawing it.
@_reference_cache
def _body_parts():
    from _materials import C_PUMP_BOSS, C_PUMP_HEAD, C_PUMP_MOTOR
    return [
        ("head",          build_head,          C_PUMP_HEAD),   # black moulded head
        ("rotor_housing", build_rotor_housing, C_PUMP_BOSS),   # the white bracket under it
        ("motor_body",    build_motor_body,    C_PUMP_MOTOR),  # the bare steel can
    ]


def build_assembly():
    import cadquery as cq
    a = cq.Assembly(name="kamoer-kphm400")
    for name, builder, color in _body_parts():
        a.add(builder(), name=name, color=color)
    return a


def build_scene():
    import cadquery as cq
    parts = [builder().val() for _, builder, _ in _body_parts()]
    return cq.Compound.makeCompound(parts)


def __getattr__(name):
    if name == "BODY_PARTS":
        return _body_parts()
    if name == 'cq':
        import cadquery as cq
        return cq
    if name in {'export_assembly'}:
        import _cadq_export
        return getattr(_cadq_export, name)
    if name in {'C_PUMP_BOSS', 'C_PUMP_MOTOR', 'C_PUMP_HEAD'}:
        import _materials
        return getattr(_materials, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
