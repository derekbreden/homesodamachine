"""IEC 60320 C14 panel-mount inlet measured from the MXR AC-04 part.

This is the two-screw, 40 mm-pitch male appliance inlet sold as MXR B07DCXKNXQ.
The photographed moulding has three different profiles: a tapered two-ear flange,
a rounded mating-face shroud around the C13 cavity, and a chamfered wiring-side
housing carrying the Faston tabs. Measurements taken on one face are not projected
through the part.

Calipered from the part
-----------------------
* 49.77 x 22.17 mm: flange tip-to-tip and across its central long flats.
* 17.98 mm: the in-plane chord from an ear's extreme nose to the shoulder where
  that end taper meets a central long flat. It is not a Y depth or perimeter length.
* 40.00 mm: screw pitch, with both screws on the mating axis.
* 26.46 x 18.18 mm: wiring-side housing envelope.
* 7.04 mm: the straight 45 degree segment across one housing corner, between its
  two rounded transitions. It is not the cavity depth.
* 30.95 x 22.15 mm, R3: the established panel opening this inlet mounts through.

Estimated from the photographs
------------------------------
The flange shoulder round is R1.2 and the housing transitions are R0.9. The
unmeasured Y stack and mating-face details use a 2 mm flange, 9 mm shroud,
8 mm cavity, 22 mm housing and 5 mm tabs.

Coordinate convention
---------------------
Y is the mating axis and +Y points out of the enclosure toward the C13 cord. The
panel-seating plane is Y=0, at the outboard face of the flange. The shroud reaches
through the panel at Y>=0; flange, housing and terminals lie at Y<0. X is the
flange's 49.77 mm axis and +Z is up.

Run:
    tools/cad-venv/bin/python hardware/reference/iec-c14-inlet/iec_c14_inlet.py
    tools/cad-venv/bin/python hardware/reference/iec-c14-inlet/iec_c14_inlet.py selftest
"""

import math
import sys
from pathlib import Path

import cadquery as cq

_here = Path(__file__).resolve()
_hw = next(p for p in _here.parents if p.name == "hardware")
sys.path.insert(0, str(_hw / "scripts"))
sys.path.insert(0, str(_hw / "printed-parts" / "cadlib"))
from _cadq_export import export_assembly, import_step  # noqa: E402
from _materials import C_C14, one_body  # noqa: E402
from world_workplane import xz_plane_y_up  # noqa: E402

STEP = _here.parent / "iec-c14-inlet.step"


# Flange and fasteners: all face dimensions below are calipered.
FLANGE_W = 49.77
FLANGE_H = 22.17
FLANGE_END_CHORD = 17.98
SCREW_PITCH = 40.0
EAR_R = (FLANGE_W - SCREW_PITCH) / 2.0
FLANGE_SHOULDER_X = FLANGE_W / 2.0 - math.sqrt(
    FLANGE_END_CHORD ** 2 - (FLANGE_H / 2.0) ** 2)
FLANGE_KNUCKLE_R = 1.2       # ESTIMATED from the four shoulder transitions
FLANGE_T = 2.0               # ESTIMATED
SCREW_D = 3.0                # M3 clearance

# The panel opening is a mounting datum, independent of either housing profile.
CUTOUT_W = 30.95
CUTOUT_H = 22.15
CUTOUT_R = 3.0

# Mating-face shroud and cavity: estimated from the photographs.
SHROUD_W = 24.0
SHROUD_H = 18.0
SHROUD_T = 1.6
SHROUD_PROUD = 9.0
CAVITY_W = SHROUD_W - 2.0 * SHROUD_T
CAVITY_H = SHROUD_H - 2.0 * SHROUD_T
CAVITY_DEPTH = 8.0
SHROUD_FILLET = 1.5

# Wiring-side housing: envelope and bevel are calipered; rounding is estimated.
BODY_W = 26.46
BODY_H = 18.18
BODY_CHAMFER = 7.04
BODY_CORNER_R = 0.9
BODY_CORNER_TRIM = BODY_CORNER_R * math.tan(math.pi / 8.0)
# Filleting a 45 degree polygon corner trims this much off both ends of its diagonal.
# Enlarge the construction leg so the remaining physical straight is exactly 7.04 mm.
BODY_CHAMFER_LEG = (
    BODY_CHAMFER + 2.0 * BODY_CORNER_TRIM
) / math.sqrt(2.0)
BODY_DEPTH = 22.0             # ESTIMATED

# Male blades and Faston tabs: IEC/generic estimates.
BLADE_W = 4.0
BLADE_T = 1.0
BLADE_PROUD = 7.0
LN_SPACING = 14.0
EARTH_OFFSET_Z = 8.0
TAB_W = 4.8
TAB_T = 0.8
TAB_PROUD = 5.0

shroud_rim_y = SHROUD_PROUD
cavity_floor_y = shroud_rim_y - CAVITY_DEPTH
flange_back_y = -FLANGE_T
body_back_y = flange_back_y - BODY_DEPTH


def panel_cutout() -> tuple:
    """Established axis-centred panel opening as ``(width, height, radius)``."""
    return (CUTOUT_W, CUTOUT_H, CUTOUT_R)


def panel_screws() -> tuple:
    """Two screw stations in the seating plane, relative to the inlet centre."""
    return ((-SCREW_PITCH / 2.0, 0.0), (SCREW_PITCH / 2.0, 0.0))


def panel_footprint() -> tuple:
    """Overall flange extents in the seating plane."""
    return (FLANGE_W, FLANGE_H)


def panel_stack() -> tuple:
    """Outboard shroud reach and inboard moulded reach, terminals excluded."""
    return (SHROUD_PROUD, FLANGE_T + BODY_DEPTH)


def _flange_landmarks() -> dict:
    """Right-top landmarks of the final rounded flange outline.

    ``shoulder`` is the measured long-flat endpoint. A radius at that point joins
    the flat to the common external tangent shared with the screw-ear circle.
    The construction preserves the 17.98 mm shoulder-to-nose chord after rounding.
    """
    a = FLANGE_SHOULDER_X
    h = FLANGE_H / 2.0
    kr = FLANGE_KNUCKLE_R
    shoulder_center = (a, h - kr)
    ear_center = (SCREW_PITCH / 2.0, 0.0)
    dx = ear_center[0] - shoulder_center[0]
    dz = ear_center[1] - shoulder_center[1]
    span = math.hypot(dx, dz)
    if span <= abs(EAR_R - kr):
        raise ValueError("the flange shoulder and screw-ear rounds swallow their tangent")
    ux, uz = dx / span, dz / span
    along = (kr - EAR_R) / span
    across = math.sqrt(1.0 - along * along)
    nx = along * ux + across * (-uz)
    nz = along * uz + across * ux
    q = (shoulder_center[0] + kr * nx, shoulder_center[1] + kr * nz)
    t = (ear_center[0] + EAR_R * nx, ear_center[1] + EAR_R * nz)
    theta = math.atan2(nz, nx)
    mid_theta = (math.pi / 2.0 + theta) / 2.0
    mid = (shoulder_center[0] + kr * math.cos(mid_theta),
           shoulder_center[1] + kr * math.sin(mid_theta))
    return {
        "shoulder": (a, h),
        "round_mid": mid,
        "tangent_start": q,
        "ear_tangent": t,
        "nose": (FLANGE_W / 2.0, 0.0),
    }


def flange_profile(clearance: float = 0.0) -> cq.Sketch:
    """Canonical rounded flange silhouette, offset outward by ``clearance``.

    The enclosure imports this function for its insertion pocket and collar, so
    the purchased part and printed surround cannot drift to different outlines.
    """
    if clearance < 0.0:
        raise ValueError("flange-profile clearance must be non-negative")
    p = _flange_landmarks()
    a, h = p["shoulder"]
    mx, mz = p["round_mid"]
    qx, qz = p["tangent_start"]
    tx, tz = p["ear_tangent"]
    nose_x = p["nose"][0]
    sketch = (
        cq.Sketch()
        .segment((-a, h), (a, h))
        .arc((a, h), (mx, mz), (qx, qz))
        .segment((qx, qz), (tx, tz))
        .arc((tx, tz), (nose_x, 0.0), (tx, -tz))
        .segment((tx, -tz), (qx, -qz))
        .arc((qx, -qz), (mx, -mz), (a, -h))
        .segment((a, -h), (-a, -h))
        .arc((-a, -h), (-mx, -mz), (-qx, -qz))
        .segment((-qx, -qz), (-tx, -tz))
        .arc((-tx, -tz), (-nose_x, 0.0), (-tx, tz))
        .segment((-tx, tz), (-qx, qz))
        .arc((-qx, qz), (-mx, mz), (-a, h))
        .assemble()
        .reset()
    )
    if clearance:
        face = sketch._faces.Faces()[0]  # CadQuery Sketch has no public wire accessor.
        wires = face.outerWire().offset2D(clearance)
        if len(wires) != 1:
            raise ValueError(
                f"a {clearance:g} mm flange offset produced {len(wires)} outlines")
        sketch = cq.Sketch().face(wires[0]).reset()
    return sketch


def flange_prism(clearance: float, y0: float, y1: float) -> cq.Workplane:
    """The canonical flange silhouette extruded from ``y0`` to ``y1``.

    This deliberately contains no screw holes. It is the material envelope used
    both for the moulding and for true-profile enclosure offsets.
    """
    if y1 <= y0:
        raise ValueError(f"flange prism ends at {y1:g}, not beyond its start {y0:g}")
    return (cq.Workplane(xz_plane_y_up).workplane(offset=y0)
            .placeSketch(flange_profile(clearance)).extrude(y1 - y0))


def _body_profile() -> cq.Sketch:
    hw, hh, k = BODY_W / 2.0, BODY_H / 2.0, BODY_CHAMFER_LEG
    points = (
        (-(hw - k), hh), (hw - k, hh), (hw, hh - k), (hw, -(hh - k)),
        (hw - k, -hh), (-(hw - k), -hh), (-hw, -(hh - k)), (-hw, hh - k),
    )
    sketch = cq.Sketch()
    for p0, p1 in zip(points, points[1:] + points[:1]):
        sketch = sketch.segment(p0, p1)
    return sketch.assemble().vertices().fillet(BODY_CORNER_R).reset()


def build_flange() -> cq.Workplane:
    """Measured tapered flange from Y=-2 to the seating plane at Y=0."""
    flange = flange_prism(0.0, flange_back_y, 0.0)
    for sx, sz in panel_screws():
        bore = (cq.Workplane(xz_plane_y_up).workplane(offset=flange_back_y)
                .center(sx, -sz).circle(SCREW_D / 2.0).extrude(FLANGE_T))
        flange = flange.cut(bore)
    return flange


def build_shroud() -> cq.Workplane:
    """Rounded mating shroud and its recessed C13 cavity at Y=0..9."""
    ring = (cq.Workplane(xz_plane_y_up).rect(SHROUD_W, SHROUD_H)
            .extrude(SHROUD_PROUD).edges("|Y").fillet(SHROUD_FILLET))
    cavity = (cq.Workplane(xz_plane_y_up).workplane(offset=shroud_rim_y)
              .rect(CAVITY_W, CAVITY_H).extrude(-CAVITY_DEPTH))
    return ring.cut(cavity)


def build_blades() -> cq.Workplane:
    """Three IEC male blades standing from the cavity floor toward +Y."""
    blades = None
    ln_z_local = EARTH_OFFSET_Z / 2.0
    for sx in (-1.0, 1.0):
        blade = (cq.Workplane(xz_plane_y_up).workplane(offset=cavity_floor_y)
                 .center(sx * LN_SPACING / 2.0, ln_z_local)
                 .rect(BLADE_W, BLADE_T).extrude(BLADE_PROUD))
        blades = blade if blades is None else blades.union(blade)
    earth = (cq.Workplane(xz_plane_y_up).workplane(offset=cavity_floor_y)
             .center(0.0, ln_z_local - EARTH_OFFSET_Z)
             .rect(BLADE_T, BLADE_W).extrude(BLADE_PROUD))
    return blades.union(earth)


def build_body() -> cq.Workplane:
    """Measured, chamfered wiring housing behind the flange."""
    return (cq.Workplane(xz_plane_y_up).workplane(offset=flange_back_y)
            .placeSketch(_body_profile()).extrude(-BODY_DEPTH))


def build_terminals() -> cq.Workplane:
    """Three Faston tabs projecting from the wiring housing toward -Y."""
    tabs = None
    ln_z_local = EARTH_OFFSET_Z / 2.0
    for sx in (-1.0, 1.0):
        tab = (cq.Workplane(xz_plane_y_up).workplane(offset=body_back_y)
               .center(sx * LN_SPACING / 2.0, ln_z_local)
               .rect(TAB_W, TAB_T).extrude(-TAB_PROUD))
        tabs = tab if tabs is None else tabs.union(tab)
    earth = (cq.Workplane(xz_plane_y_up).workplane(offset=body_back_y)
             .center(0.0, ln_z_local - EARTH_OFFSET_Z)
             .rect(TAB_T, TAB_W).extrude(-TAB_PROUD))
    return tabs.union(earth)


def build_iec_c14_inlet() -> cq.Workplane:
    """The complete inlet as one reference solid."""
    return (build_flange().union(build_shroud()).union(build_blades())
            .union(build_body()).union(build_terminals()))


def stations_hold() -> None:
    """Hold public mounting figures to the materialized STEP geometry."""
    solid = import_step(str(STEP)).val()
    bb = solid.BoundingBox()
    for what, claimed, actual in (
            ("face width", FLANGE_W, bb.xlen), ("face height", FLANGE_H, bb.zlen)):
        if abs(claimed - actual) > 1e-6:
            raise ValueError(
                f"iec-c14-inlet {what} is {claimed:g}, STEP carries {actual:.4f}")
    out = cq.Solid.makeBox(bb.xlen + 2.0, bb.ymax + 1.0, bb.zlen + 2.0,
                           cq.Vector(bb.xmin - 1.0, 1e-3, bb.zmin - 1.0))
    ob = solid.intersect(out).BoundingBox()
    cut_w, cut_h, _cut_r = panel_cutout()
    for what, through, opening in (("width", ob.xlen, cut_w), ("height", ob.zlen, cut_h)):
        if through > opening + 1e-6:
            raise ValueError(
                f"the {through:.4f} mm outboard {what} does not pass its {opening:g} opening")
    for sx, sz in panel_screws():
        if abs(sx) + SCREW_D / 2.0 > FLANGE_W / 2.0:
            raise ValueError(f"the screw at ({sx:g}, {sz:g}) leaves the flange")
        if abs(sx) - SCREW_D / 2.0 < cut_w / 2.0:
            raise ValueError(f"the screw at ({sx:g}, {sz:g}) breaks into the panel opening")
    outboard, inboard = panel_stack()
    if abs(ob.ymax - outboard) > 1e-6:
        raise ValueError(f"panel stack says {outboard:g} out, STEP carries {ob.ymax:.4f}")
    if abs(bb.ymin + inboard + TAB_PROUD) > 1e-6:
        raise ValueError(
            f"panel stack says {inboard:g} in plus {TAB_PROUD:g} tabs, STEP reaches {bb.ymin:.4f}")


def selftest() -> int:
    """Verify every photographed constraint and the shared enclosure profile."""
    fails = []
    p = _flange_landmarks()
    chord = math.dist(p["shoulder"], p["nose"])
    if abs(chord - FLANGE_END_CHORD) > 1e-9:
        fails.append(f"flange shoulder-to-nose chord is {chord:.6f}, not {FLANGE_END_CHORD:g}")
    if abs(SCREW_PITCH + 2.0 * EAR_R - FLANGE_W) > 1e-9:
        fails.append("the screw-ear circles do not reach the measured flange tips")
    straight = math.sqrt(2.0) * BODY_CHAMFER_LEG - 2.0 * BODY_CORNER_TRIM
    if abs(straight - BODY_CHAMFER) > 1e-9:
        fails.append(f"rounded body leaves a {straight:.6f} mm chamfer, not {BODY_CHAMFER:g}")
    if SHROUD_W > CUTOUT_W or SHROUD_H > CUTOUT_H:
        fails.append("the mating shroud does not pass the established panel opening")
    try:
        nominal = flange_prism(0.0, -1.0, 0.0).val().BoundingBox()
        slipped = flange_prism(0.5, -1.0, 0.0).val().BoundingBox()
        if abs(nominal.xlen - FLANGE_W) > 1e-6 or abs(nominal.zlen - FLANGE_H) > 1e-6:
            fails.append("canonical flange profile does not carry the measured extents")
        if abs(slipped.xlen - FLANGE_W - 1.0) > 1e-6 or abs(
                slipped.zlen - FLANGE_H - 1.0) > 1e-6:
            fails.append("the shared 0.5 mm flange offset is not 0.5 mm per side")
        stations_hold()
    except Exception as exc:  # noqa: BLE001
        fails.append(str(exc))
    for line in fails:
        print(f"FAIL {line}")
    if not fails:
        print(
            f"ok  C14 flange {FLANGE_W:g} x {FLANGE_H:g}, chord {FLANGE_END_CHORD:g}; "
            f"housing {BODY_W:g} x {BODY_H:g}, chamfer {BODY_CHAMFER:g}; "
            f"cutout {CUTOUT_W:g} x {CUTOUT_H:g}")
    return 1 if fails else 0


def main() -> None:
    part = build_iec_c14_inlet()
    bb = part.val().BoundingBox()
    print("IEC 60320 C14 panel-mount AC inlet — MXR AC-04 / B07DCXKNXQ")
    print(f"  X [{bb.xmin:.2f}, {bb.xmax:.2f}]  Y [{bb.ymin:.2f}, {bb.ymax:.2f}]  "
          f"Z [{bb.zmin:.2f}, {bb.zmax:.2f}]")
    print(f"  flange {FLANGE_W:g} x {FLANGE_H:g}, end chord {FLANGE_END_CHORD:g}")
    print(f"  rear housing {BODY_W:g} x {BODY_H:g}, 45-degree chamfer {BODY_CHAMFER:g}")
    print(f"  solid valid: {part.val().isValid()}")
    export_assembly(one_body(part, "iec-c14-inlet", C_C14), str(STEP))
    print(f"-> {STEP.name}")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "selftest":
        sys.exit(selftest())
    main()
