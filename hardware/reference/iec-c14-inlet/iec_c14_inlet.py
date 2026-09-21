"""IEC 60320 C14 panel-mount inlet, measured from the MXR AC-04 part by MINI 2 scan.

This is the two-screw male appliance inlet sold as MXR B07DCXKNXQ. A rim
1.84 mm proud of the flange frames a cavity recessed 14.3 mm into the body, and
the C13 connector nose enters that cavity until its shoulder meets the rim face.

Measured from the scan
----------------------
* 49.77 x 21.9 mm: flange nose-to-nose (calipers) and across its two long
  flats (scan); the outline runs from each flat through a taper tangent to an
  R4.885 ear arc centred 20 from the axis, 17.98 from shoulder to nose (calipers).
* 3.25 mm: flange thickness, ear faces both sides. The ear front faces crown
  about 0.2 mm toward the tips; the model keeps them flat.
* 40.21 mm: screw pitch, both holes on the mating axis, dia 3.24, countersunk
  90 degrees to dia 6.1 on the outboard face.
* 31.03 x 22.13 mm, R6, 1.84 proud: the rim around the cavity mouth.
* 24.82 x 16.26 mm: the cavity mouth, R2.3 at the top corners and 4.8 mm
  45 degree chamfers at the bottom (earth-side) corners; floor 14.3 below the
  seating plane.
* 26.10 x 18.00 x 13.65 mm: the wiring-side housing, from the flange's back face
  to its end face, 45 degree chamfers of 4.85 mm leg on its two lower long edges.
* three 4.0 x 10.0 mm bosses 1.17 proud of the end face, each carrying a
  0.8 x 6.3 mm solder tab reaching 25.0 behind the seating plane.

The plan outline of the flange follows the calipers and the pocket that holds
the part; the scan's broad faces end on that outline and its thin edge band
reads up to 0.3 mm outside it.

Left as simple forms
--------------------
Blade and tab sections are IEC nominal (2 x 4 and 0.8 x 6.3). The knuckle round
between flat and taper, the housing's upper edge rounds, the tab hole and the
two small windows in the rim's side walls are not measured to better than a few
tenths and are drawn as R1.0, R1.0, dia 2.0 and omitted respectively.

Coordinate convention
---------------------
Y is the mating axis and +Y points out of the enclosure toward the C13 cord. The
panel-seating plane is Y=0, at the outboard face of the flange's ears. The rim
stands at Y>0; flange, housing, bosses and tabs lie at Y<0. X is the flange's
49.97 mm axis, centred between the two screw holes, and +Z is up with the earth
blade below the line and neutral pair.

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


# Flange and fasteners. The plan outline is the calipered one: the scan's broad faces end
# on it, while its thin edge band reads up to 0.3 mm outside it (`scan-evidence.json`).
FLANGE_W = 49.77              # nose to nose, calipers
FLANGE_H = 21.9               # across the long flats, scan
FLANGE_T = 3.25
FLANGE_END_CHORD = 17.98      # ear nose to the end of a long flat, calipers
EAR_CX = 20.0                 # ear arc centre, calipers
EAR_R = FLANGE_W / 2.0 - EAR_CX
FLANGE_SHOULDER_X = FLANGE_W / 2.0 - math.sqrt(
    FLANGE_END_CHORD ** 2 - (FLANGE_H / 2.0) ** 2)
FLANGE_KNUCKLE_R = 1.2        # ESTIMATED round between flat and taper
SCREW_PITCH = 40.21
SCREW_D = 3.24
CSK_D = 6.1                   # 90 degree countersink on the outboard face
CSK_DEPTH = (CSK_D - SCREW_D) / 2.0

# The manufacturer's stated panel opening; the enclosure cuts `bore_outline`
# plus its own clearance.
CUTOUT_W = 30.95
CUTOUT_H = 22.15
CUTOUT_R = 3.0

# Rim and cavity on the mating side.
RIM_W = 31.03
RIM_H = 22.13
RIM_R = 6.0
RIM_PROUD = 1.84
MOUTH_W = 24.82
MOUTH_H = 16.26
MOUTH_TOP_R = 2.3
MOUTH_CHAMFER = 4.8
CAVITY_FLOOR_Y = -14.3

# Male blades: IEC nominal sections at the measured stations.
BLADE_W = 4.0                 # along Z
BLADE_T = 2.0                 # along X
BLADE_STATIONS = ((-6.45, 2.3, -2.9), (0.3, -1.9, -1.1), (6.95, 2.2, -2.9))   # (x, z, tip y)

# Wiring-side housing.
BODY_W = 26.10
BODY_H = 18.00
BODY_DEPTH = 13.65
BODY_CHAMFER_LEG = 4.85       # 45 degree chamfers on the two lower long edges
BODY_TOP_R = 1.0              # ESTIMATED rounds on the two upper long edges

# Tab bosses and solder tabs.
BOSS_W = 4.0
BOSS_H = 10.0
BOSS_R = 1.0
BOSS_PROUD = 1.17
TAB_W = 6.3                   # along Z
TAB_T = 0.8                   # along X
TAB_TIP_Y = -25.0
TAB_HOLE_D = 2.0
TAB_HOLE_FROM_TIP = 3.5
TAB_STATIONS = ((-6.7, 2.45), (0.35, -2.6), (7.1, 2.65))    # (x, z) of each tab's centre
BOSS_STATIONS = ((-6.7, 2.0), (0.35, -2.5), (7.1, 2.0))

flange_back_y = -FLANGE_T
body_end_y = flange_back_y - BODY_DEPTH
boss_end_y = body_end_y - BOSS_PROUD


def panel_cutout() -> tuple:
    """The manufacturer's stated panel opening as ``(width, height, radius)``."""
    return (CUTOUT_W, CUTOUT_H, CUTOUT_R)


def bore_outline() -> tuple:
    """What a wall must pass outboard of the seating plane: the rim, ``(width, height, radius)``."""
    return (RIM_W, RIM_H, RIM_R)


def panel_screws() -> tuple:
    """Two screw stations in the seating plane, relative to the inlet centre."""
    return ((-SCREW_PITCH / 2.0, 0.0), (SCREW_PITCH / 2.0, 0.0))


def panel_footprint() -> tuple:
    """Overall flange extents in the seating plane."""
    return (FLANGE_W, FLANGE_H)


def panel_stack() -> tuple:
    """Outboard rim reach and inboard moulded reach, tabs excluded."""
    return (RIM_PROUD, FLANGE_T + BODY_DEPTH + BOSS_PROUD)


def _flange_landmarks() -> dict:
    """Right-top landmarks of the flange outline: a long flat, a knuckle round at its end, the
    common external tangent shared with the ear arc, and the nose."""
    a = FLANGE_SHOULDER_X
    h = FLANGE_H / 2.0
    kr = FLANGE_KNUCKLE_R
    shoulder_center = (a, h - kr)
    ear_center = (EAR_CX, 0.0)
    dx = ear_center[0] - shoulder_center[0]
    dz = ear_center[1] - shoulder_center[1]
    span = math.hypot(dx, dz)
    if span <= abs(EAR_R - kr):
        raise ValueError("the flange shoulder and ear rounds swallow their tangent")
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
        "taper_angle_deg": math.degrees(math.atan2(q[1] - t[1], t[0] - q[0])),
    }


def flange_profile(clearance: float = 0.0) -> cq.Sketch:
    """The flange's silhouette, offset outward by ``clearance``."""
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
    """The flange's silhouette extruded from ``y0`` to ``y1``, without its screw holes."""
    if y1 <= y0:
        raise ValueError(f"flange prism ends at {y1:g}, not beyond its start {y0:g}")
    return (cq.Workplane(xz_plane_y_up).workplane(offset=y0)
            .placeSketch(flange_profile(clearance)).extrude(y1 - y0))


def _rounded_rect(w: float, h: float, r: float) -> cq.Sketch:
    return cq.Sketch().rect(w, h).vertices().fillet(r).reset()


def _polygon_xz(points) -> cq.Sketch:
    """A closed sketch from world (x, z) corners on `xz_plane_y_up`, whose local y runs along -Z."""
    local = [(px, -pz) for px, pz in points]
    sketch = cq.Sketch()
    for p0, p1 in zip(local, local[1:] + local[:1]):
        sketch = sketch.segment(p0, p1)
    return sketch.assemble()


def _mouth_profile() -> cq.Sketch:
    """The cavity mouth: rounded upper corners, chamfered lower corners."""
    hw, hh, k = MOUTH_W / 2.0, MOUTH_H / 2.0, MOUTH_CHAMFER
    sketch = _polygon_xz(((-hw, hh), (hw, hh), (hw, -(hh - k)), (hw - k, -hh),
                          (-(hw - k), -hh), (-hw, -(hh - k))))
    return sketch.vertices("<Y").fillet(MOUTH_TOP_R).reset()     # world +Z corners


def _body_profile() -> cq.Sketch:
    """The housing section: 45 degree chamfers below, rounds above."""
    hw, hh, k = BODY_W / 2.0, BODY_H / 2.0, BODY_CHAMFER_LEG
    sketch = _polygon_xz(((-hw, hh), (hw, hh), (hw, -(hh - k)), (hw - k, -hh),
                          (-(hw - k), -hh), (-hw, -(hh - k))))
    return sketch.vertices("<Y").fillet(BODY_TOP_R).reset()      # world +Z corners


def _prism(sketch: cq.Sketch, y0: float, y1: float) -> cq.Workplane:
    return (cq.Workplane(xz_plane_y_up).workplane(offset=y0)
            .placeSketch(sketch).extrude(y1 - y0))


def build_flange() -> cq.Workplane:
    """Measured flange from Y=-3.25 to the seating plane, with its countersunk holes."""
    flange = flange_prism(0.0, flange_back_y, 0.0)
    for sx, sz in panel_screws():
        bore = (cq.Workplane(xz_plane_y_up).workplane(offset=flange_back_y - 1.0)
                .center(sx, -sz).circle(SCREW_D / 2.0).extrude(FLANGE_T + RIM_PROUD + 2.0))
        cone = cq.Solid.makeCone(CSK_D / 2.0 + 0.5, SCREW_D / 2.0, CSK_DEPTH + 0.5,
                                 cq.Vector(sx, 0.5, sz), cq.Vector(0.0, -1.0, 0.0))
        flange = flange.cut(bore).cut(cq.Workplane().add(cone))
    return flange


def build_rim() -> cq.Workplane:
    """The rim standing on the flange's outboard face."""
    return _prism(_rounded_rect(RIM_W, RIM_H, RIM_R), 0.0, RIM_PROUD)


def build_body() -> cq.Workplane:
    """Measured chamfered wiring housing behind the flange."""
    return _prism(_body_profile(), body_end_y, flange_back_y)


def build_bosses() -> cq.Workplane:
    """Three tab bosses proud of the housing's end face."""
    bosses = None
    for bx, bz in BOSS_STATIONS:
        boss = _prism(_rounded_rect(BOSS_W, BOSS_H, BOSS_R), boss_end_y, body_end_y).translate((bx, 0.0, bz))
        bosses = boss if bosses is None else bosses.union(boss)
    return bosses


def cavity_cutter() -> cq.Workplane:
    """The mouth profile carried from above the rim down to the cavity floor."""
    return _prism(_mouth_profile(), CAVITY_FLOOR_Y, RIM_PROUD + 1.0)


def build_blades() -> cq.Workplane:
    """Three IEC male blades standing from the cavity floor toward +Y."""
    blades = None
    for bx, bz, tip in BLADE_STATIONS:
        blade = (cq.Workplane(xz_plane_y_up).workplane(offset=CAVITY_FLOOR_Y - 0.5)
                 .center(bx, -bz).rect(BLADE_T, BLADE_W).extrude(tip - CAVITY_FLOOR_Y + 0.5))
        blades = blade if blades is None else blades.union(blade)
    return blades


def build_terminals() -> cq.Workplane:
    """Three solder tabs projecting from their bosses toward -Y, each with its hole."""
    tabs = None
    for tx, tz in TAB_STATIONS:
        tab = (cq.Workplane(xz_plane_y_up).workplane(offset=TAB_TIP_Y)
               .center(tx, -tz).rect(TAB_T, TAB_W).extrude(boss_end_y - TAB_TIP_Y + 0.3))
        hole = (cq.Workplane("YZ").workplane(offset=tx - 1.0)
                .center(TAB_TIP_Y + TAB_HOLE_FROM_TIP, tz).circle(TAB_HOLE_D / 2.0).extrude(2.0))
        tabs = tab.cut(hole) if tabs is None else tabs.union(tab.cut(hole))
    return tabs


def build_iec_c14_inlet() -> cq.Workplane:
    """The complete inlet as one reference solid."""
    moulding = (build_flange().union(build_rim()).union(build_body()).union(build_bosses())
                .cut(cavity_cutter()))
    return moulding.union(build_blades()).union(build_terminals())


def stations_hold() -> None:
    """Hold public mounting figures to the materialized STEP geometry."""
    solid = import_step(str(STEP)).val()
    bb = solid.BoundingBox()
    for what, claimed, actual in (
            ("face width", FLANGE_W, bb.xlen), ("face height", RIM_H, bb.zlen)):
        if abs(claimed - actual) > 1e-6:
            raise ValueError(
                f"iec-c14-inlet {what} is {claimed:g}, STEP carries {actual:.4f}")
    out = cq.Solid.makeBox(bb.xlen + 2.0, bb.ymax + 1.0, bb.zlen + 2.0,
                           cq.Vector(bb.xmin - 1.0, 1e-3, bb.zmin - 1.0))
    ob = solid.intersect(out).BoundingBox()
    bore_w, bore_h, _bore_r = bore_outline()
    for what, through, opening in (("width", ob.xlen, bore_w), ("height", ob.zlen, bore_h)):
        if through > opening + 1e-6:
            raise ValueError(
                f"the {through:.4f} mm outboard {what} does not pass its {opening:g} bore")
    for sx, sz in panel_screws():
        if abs(sx) + CSK_D / 2.0 > FLANGE_W / 2.0:
            raise ValueError(f"the screw at ({sx:g}, {sz:g}) leaves the flange")
        if abs(sx) - CSK_D / 2.0 < bore_w / 2.0:
            raise ValueError(f"the screw at ({sx:g}, {sz:g}) breaks into the bore")
    outboard, inboard = panel_stack()
    if abs(ob.ymax - outboard) > 1e-6:
        raise ValueError(f"panel stack says {outboard:g} out, STEP carries {ob.ymax:.4f}")
    if abs(bb.ymin - TAB_TIP_Y) > 1e-6:
        raise ValueError(f"tabs reach {TAB_TIP_Y:g}, STEP reaches {bb.ymin:.4f}")
    if abs(-inboard - boss_end_y) > 1e-9:
        raise ValueError(f"panel stack says {inboard:g} in, the bosses end at {boss_end_y:.4f}")


def selftest() -> int:
    """Verify the measured constraints and the shared enclosure profile."""
    fails = []
    p = _flange_landmarks()
    if abs(EAR_CX + EAR_R - FLANGE_W / 2.0) > 1e-9:
        fails.append("the ear arcs do not reach the flange noses")
    chord = math.dist(p["shoulder"], p["nose"])
    if abs(chord - FLANGE_END_CHORD) > 1e-9:
        fails.append(f"flange shoulder-to-nose chord is {chord:.6f}, not {FLANGE_END_CHORD:g}")
    if abs(SCREW_PITCH / 2.0 - EAR_CX) > 0.5:
        fails.append("the screw holes are not centred in the ears")
    if MOUTH_W > RIM_W - 2.0 or MOUTH_H > RIM_H - 2.0:
        fails.append("the cavity mouth leaves the rim less than 1 mm of wall")
    if RIM_H <= FLANGE_H:
        fails.append("the rim no longer stands proud of the ear flats in Z, as scanned")
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
            f"ok  C14 flange {FLANGE_W:g} x {FLANGE_H:g} x {FLANGE_T:g}, chord {FLANGE_END_CHORD:g}, taper "
            f"{p['taper_angle_deg']:.1f} deg; rim {RIM_W:g} x {RIM_H:g} R{RIM_R:g} proud {RIM_PROUD:g}; "
            f"mouth {MOUTH_W:g} x {MOUTH_H:g}; housing {BODY_W:g} x {BODY_H:g} x {BODY_DEPTH:g}; "
            f"screws {SCREW_PITCH:g} apart")
    return 1 if fails else 0


def main() -> None:
    part = build_iec_c14_inlet()
    bb = part.val().BoundingBox()
    print("IEC 60320 C14 panel-mount AC inlet — MXR AC-04 / B07DCXKNXQ")
    print(f"  X [{bb.xmin:.2f}, {bb.xmax:.2f}]  Y [{bb.ymin:.2f}, {bb.ymax:.2f}]  "
          f"Z [{bb.zmin:.2f}, {bb.zmax:.2f}]")
    print(f"  flange {FLANGE_W:g} x {FLANGE_H:g} x {FLANGE_T:g}, rim {RIM_W:g} x {RIM_H:g} "
          f"proud {RIM_PROUD:g}, mouth {MOUTH_W:g} x {MOUTH_H:g}")
    print(f"  housing {BODY_W:g} x {BODY_H:g} x {BODY_DEPTH:g}, lower chamfer leg {BODY_CHAMFER_LEG:g}")
    print(f"  solid valid: {part.val().isValid()}")
    export_assembly(one_body(part, "iec-c14-inlet", C_C14), str(STEP))
    print(f"-> {STEP.name}")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "selftest":
        sys.exit(selftest())
    main()
