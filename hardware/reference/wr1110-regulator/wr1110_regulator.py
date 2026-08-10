"""Interstate Pneumatics WR1110 fixed 90 PSI secondary regulator — the
appliance's `wr1110` on the CO2 inlet chain (DERPIPE → GASHER → WR1110, running
+Y). A "Mini Body Series" fixed preset: no adjustment knob, just two wrench
hexes and a flush vent hole.

External envelope only — a round regulator body between two hex wrench
sections, flow axis along +Y. The internal diaphragm + spring and the flush
vent hole are not modeled. Ø21 across the hex corners × 57 mm.

Frame: +Y = flow axis (matches the enclosure placement); centered on X/Z. +Z up.

Run:
    tools/cad-venv/bin/python hardware/reference/wr1110-regulator/wr1110_regulator.py
"""

import sys
from pathlib import Path

import cadquery as cq

_here = Path(__file__).resolve()
_hw = next(p for p in _here.parents if p.name == "hardware")
sys.path.insert(0, str(_hw / "scripts"))
from _cadq_export import export_step

STEP = _here.parent / "wr1110-regulator.step"

HEX_ACROSS_CORNERS = 21.0   # hex circumdiameter (across corners)
TOTAL_LENGTH = 57.0         # along the flow axis
BODY_D = 19.0               # round regulator body between the hexes
HEX_LENGTH = 15.0           # each wrench hex section
BODY_LENGTH = TOTAL_LENGTH - 2 * HEX_LENGTH   # 27 mm round body


def inlet():
    """The upstream hex's outer face — a 1/4" NPT female socket, taking the
    GASHER check's male stub: (position, outward axis). The body is built from
    the origin along the flow axis, so its two faces are at y = 0 and
    y = TOTAL_LENGTH, not either side of the origin."""
    return (0.0, 0.0, 0.0), (0.0, -1.0, 0.0)


def outlet():
    """The downstream hex's outer face — a 1/4" NPT female socket, taking a
    PP010822E adapter onto 1/4" tube: (position, outward axis)."""
    return (0.0, TOTAL_LENGTH, 0.0), (0.0, 1.0, 0.0)


def barrel():
    """The round body between the two wrench hexes — `(station, radius, length)`.

    Both hexes stand on made-up NPT threads, so where their flats come to rest is wherever the
    thread stopped. The barrel is the same circle whatever the makeup did.

    `station` is its mid-point and the flow axis through it, in the same frame the two sockets
    are stated in."""
    return (((0.0, HEX_LENGTH + BODY_LENGTH / 2.0, 0.0), (0.0, 1.0, 0.0)),
            BODY_D / 2.0, BODY_LENGTH)


def stations() -> dict:
    """Both sockets, in the order the gas meets them."""
    return {"inlet": inlet(), "outlet": outlet()}


def stations_hold():
    """Hold both sockets and the barrel to `wr1110-regulator.step` — the file the enclosure
    seats, while it takes these stations out of this module's live figures.

    The regulator is a straight run on one axis, so its two stations ARE the ends of that
    solid's box: the hex faces the adapters bottom against. The hop that reaches the inlet is
    seated on this reading.

    The two sockets are extents of that solid's box. THE BARREL IS NOT — it is a section inside
    the envelope, so it is read as everything the file holds over its own Y band, and the box
    that band comes back with."""
    solid = cq.importers.importStep(str(STEP)).val()
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


def build():
    """Two hex wrench sections with a round body between, flow axis along +Y."""
    # Build along +Z, then reorient +Z -> +Y.
    inlet_hex = cq.Workplane("XY").polygon(6, HEX_ACROSS_CORNERS).extrude(HEX_LENGTH)
    body = (
        cq.Workplane("XY")
        .workplane(offset=HEX_LENGTH)
        .circle(BODY_D / 2.0)
        .extrude(BODY_LENGTH)
    )
    outlet_hex = (
        cq.Workplane("XY")
        .workplane(offset=HEX_LENGTH + BODY_LENGTH)
        .polygon(6, HEX_ACROSS_CORNERS)
        .extrude(HEX_LENGTH)
    )
    part = inlet_hex.union(body).union(outlet_hex)
    return part.rotate((0, 0, 0), (1, 0, 0), -90.0)


def main():
    part = build()
    bb = part.val().BoundingBox()
    print("Interstate Pneumatics WR1110 secondary regulator")
    print(f"  Bounding box: X [{bb.xmin:.2f}, {bb.xmax:.2f}]  "
          f"Y [{bb.ymin:.2f}, {bb.ymax:.2f}]  Z [{bb.zmin:.2f}, {bb.zmax:.2f}]")
    print(f"  Hex: {HEX_ACROSS_CORNERS} across corners × {HEX_LENGTH:g} mm each; "
          f"body Ø{BODY_D} × {BODY_LENGTH:g} mm; total {TOTAL_LENGTH:g} mm")
    for label, (pos, axis) in (("inlet  (F)", inlet()), ("outlet (F)", outlet())):
        print(f"  {label}: ({pos[0]:7.2f}, {pos[1]:6.2f}, {pos[2]:7.2f})  out {axis}")
    export_step(part, str(STEP))
    print(f"-> {STEP.name}")


if __name__ == "__main__":
    main()
