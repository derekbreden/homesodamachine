"""Scan-derived external form of the received WR1110 fixed inline regulator.

Two MINI 2 passes establish the smooth barrel, unequal wrench sections, shoulders
and outlet stub at native millimetre scale. See README.md and scan-measurements.json.
The thread crests use a smooth envelope; visible mouths are shallow display bores.
Internal pressure-control geometry and made-up NPT engagement are unmeasured.

Frame: inlet face at the origin, flow along +Y, barrel centred on X/Z.
"""

import sys
from pathlib import Path

import cadquery as cq

_here = Path(__file__).resolve()
_hw = next(p for p in _here.parents if p.name == "hardware")
sys.path.insert(0, str(_hw / "scripts"))
from _cadq_export import export_assembly, import_step
from _materials import M_ALUMINIUM, one_body

STEP = _here.parent / "wr1110-regulator.step"

# Rounded modelling dimensions from the coated, unit-scale exterior scan.
BODY_D = 18.87
BODY_START = 14.65
BODY_END = 50.05
BODY_LENGTH = BODY_END - BODY_START
INLET_HEX_AF = 19.0
INLET_HEX_D = 20.60             # turned blank clips the six corners
OUTLET_HEX_AF = 19.08
OUTLET_HEX_D = 21.76
OUTLET_HEX_CLOCK = -2.0        # degrees in the reference X/Z plane
TOTAL_LENGTH = 54.47           # inlet face to downstream hex shoulder
STUB_LENGTH = 9.18             # shoulder to tip, not an engagement measurement
STUB_D = 14.2                  # maximum root envelope; thread crests are smaller
OVERALL_LENGTH = TOTAL_LENGTH + STUB_LENGTH

# (Y station, radius). Short straight segments represent the turned end rounds.
INLET_PROFILE = ((0.0, 9.38), (.35, 9.93), (.8, INLET_HEX_D / 2),
                 (13.35, INLET_HEX_D / 2), (13.7, 10.22), (14.2, 9.78),
                 (BODY_START, BODY_D / 2))
OUTLET_PROFILE = ((BODY_END, BODY_D / 2), (50.4, 9.70), (50.9, 10.38),
                  (51.35, 10.78), (51.65, OUTLET_HEX_D / 2),
                  (53.35, OUTLET_HEX_D / 2), (53.75, 10.65), (54.1, 10.12),
                  (TOTAL_LENGTH, 9.45))
STUB_PROFILE = ((TOTAL_LENGTH, STUB_D / 2), (54.9, 6.85), (55.3, 6.48),
                (55.7, 6.10), (56.2, 6.30), (56.8, 6.65), (57.2, 6.72),
                (61.6, 6.60), (62.1, 6.48), (62.5, 6.05), (63.2, 5.50),
                (OVERALL_LENGTH, 4.10))


def inlet():
    """The upstream hex's outer face — the mouth of the 1/4" NPT female socket,
    taking a PI010822S male connector: (position, outward axis). The body is
    built from the origin along the flow axis, so the inlet face is at y = 0 and
    the outlet hex face at y = TOTAL_LENGTH, not either side of the origin."""
    return (0.0, 0.0, 0.0), (0.0, -1.0, 0.0)


def outlet():
    """The measured far end of the outlet stub: position and outward axis."""
    return (0.0, TOTAL_LENGTH + STUB_LENGTH, 0.0), (0.0, 1.0, 0.0)


def barrel():
    """The measured circular mounting band: `(midpoint station, radius, length)`.

    The enclosure locates its cradle on this band independently of wrench clock.
    """
    return (((0.0, BODY_START + BODY_LENGTH / 2.0, 0.0), (0.0, 1.0, 0.0)),
            BODY_D / 2.0, BODY_LENGTH)


def stations() -> dict:
    """Both sockets, in the order the gas meets them."""
    return {"inlet": inlet(), "outlet": outlet()}


def stations_hold():
    """Read both end stations and the circular mounting band from the exported STEP."""
    solid = import_step(str(STEP)).val()
    bb = solid.BoundingBox()
    for name, (pos, _axis), actual in (("inlet", inlet(), bb.ymin),
                                       ("outlet", outlet(), bb.ymax)):
        if abs(pos[1] - actual) > 1e-6:
            raise ValueError(
                f"wr1110 {name} stands at y = {pos[1]:g} and {STEP.name} ends at "
                f"{actual:.4f} — {abs(pos[1] - actual):.4f} mm apart. The pack seats that file "
                f"and reads this station, so the hop that closes on it reaches nothing.")
    (mid, _axis), r, length = barrel()
    y0, y1 = mid[1] - length / 2.0, mid[1] + length / 2.0
    band = solid.intersect(cq.Solid.makeBox(
        4 * r, y1 - y0, 4 * r, cq.Vector(mid[0] - 2 * r, y0, mid[2] - 2 * r)))
    got = band.BoundingBox()
    for axis, lo, hi, centre in (("X", got.xmin, got.xmax, mid[0]),
                                 ("Z", got.zmin, got.zmax, mid[2])):
        if abs((hi - lo) - 2 * r) > 1e-6 or abs((lo + hi) / 2.0 - centre) > 1e-6:
            raise ValueError(
                f"wr1110 BODY_D is {BODY_D:g}, so the {length:g} mm band at y "
                f"[{y0:g}, {y1:g}] should be {2 * r:g} across {axis} about {centre:g}; "
                f"{STEP.name} runs [{lo:.4f}, {hi:.4f}] there. A seat bored on `barrel` closes "
                f"on a section that is not the one it was drawn for.")


def _turned(profile):
    """An axial radius profile revolved about +Z before the final frame turn."""
    outline = [(0, profile[0][0]), *((r, y) for y, r in profile),
               (0, profile[-1][0])]
    return cq.Workplane("XZ").polyline(outline).close().revolve(360, (0, 0), (0, 1))


def _wrench(profile, across_flats, clock=0.0):
    import math
    prism = (cq.Workplane("XY").workplane(offset=profile[0][0])
             .polygon(6, across_flats / math.cos(math.pi / 6))
             .extrude(profile[-1][0] - profile[0][0])
             .rotate((0, 0, 0), (0, 0, 1), 30 - clock))
    return _turned(profile).intersect(prism)


def build():
    """Analytic exterior, clipped wrench hexes and observed open mouths."""
    body = (cq.Workplane("XY").workplane(offset=BODY_START)
            .circle(BODY_D / 2).extrude(BODY_LENGTH))
    part = (_wrench(INLET_PROFILE, INLET_HEX_AF).union(body)
            .union(_wrench(OUTLET_PROFILE, OUTLET_HEX_AF, OUTLET_HEX_CLOCK))
            .union(_turned(STUB_PROFILE)))
    # Only the visible mouth is represented; these blind ends are display closures.
    inlet_mouth = _turned(((0.0, 7.10), (1.3, 6.10), (4.5, 6.05)))
    outlet_mouth = _turned(((OVERALL_LENGTH - 2.5, 3.85),
                            (OVERALL_LENGTH, 4.00)))
    return part.cut(inlet_mouth).cut(outlet_mouth).rotate((0, 0, 0), (1, 0, 0), -90)


def main():
    part = build()
    bb = part.val().BoundingBox()
    print("Interstate Pneumatics WR1110 secondary regulator")
    print(f"  Bounding box: X [{bb.xmin:.2f}, {bb.xmax:.2f}]  "
          f"Y [{bb.ymin:.2f}, {bb.ymax:.2f}]  Z [{bb.zmin:.2f}, {bb.zmax:.2f}]")
    print(f"  Barrel Ø{BODY_D:g} × {BODY_LENGTH:g} mm; "
          f"hex shoulder y={TOTAL_LENGTH:g}; overall {OVERALL_LENGTH:g} mm")
    for label, (pos, axis) in (("inlet  (F)", inlet()), ("outlet (M)", outlet())):
        print(f"  {label}: ({pos[0]:7.2f}, {pos[1]:6.2f}, {pos[2]:7.2f})  out {axis}")
    export_assembly(one_body(part, "wr1110-regulator", M_ALUMINIUM), str(STEP))
    print(f"-> {STEP.name}")


if __name__ == "__main__":
    main()
