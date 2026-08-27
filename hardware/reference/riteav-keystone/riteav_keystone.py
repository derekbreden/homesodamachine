"""Line-art reference solid of the RiteAV RJ11 6P4C black punchdown keystone jack — the SIG-6
signal station on the +Y wall of back-top, where the umbilical's ribbon plugs into the appliance.

A keystone snaps into a rectangular opening on its own moulded latch, so the opening is the whole
of what the wall gives this station.

Reduced to three boxes on one axis: the bezel that lands on the wall's outer face, the latch
section that passes the opening, and the body standing inboard of it carrying the 110 IDC
terminals the J3 loom is punched onto.

    Interface        RJ11 6P4C — SIG-6's four conductors (TX / RX / 5 V / GND)
    Termination      110 IDC, 90 degrees, on the inboard face
    Mounting         keystone snap-in, latch closing on the panel it passes
    Colour           black, with a snap-in dust cover in the bag
    Vendor           riteav.com mpn46181, bag of 10 (`ledger/purchases.md` §9)

EVERY FIGURE BELOW IS NOMINAL AND NONE IS MEASURED. The keystone opening is a de-facto standard,
and this part is on order — RiteAV #58999, placed 2026-08-27. `OPEN_W`, `OPEN_H` and `PANEL_MAX`
carry what faceplates are built to; a caliper across the delivered jack replaces them, and the
wall's cut follows. Nothing outside `enclosure_assembly.keystone_cutout` reads this module.

`enclosure_assembly`'s `keystone-panel` states `enclosure.wall` against `PANEL_MIN`/`PANEL_MAX`.

Coordinate convention — jg_bulkhead_union's, so this station seats like the tube crossings:
  Y = mating axis. +Y = outward, toward the customer's plug.
  Origin = the bezel's panel-seating face. The bezel sits at y >= 0; the latch and the body
      standing inboard sit at y < 0.
  +Z = up. X completes the right-handed frame.

Run:
    tools/cad-venv/bin/python hardware/reference/riteav-keystone/riteav_keystone.py
    tools/cad-venv/bin/python hardware/reference/riteav-keystone/riteav_keystone.py selftest
"""

import sys
from pathlib import Path

import cadquery as cq

_here = Path(__file__).resolve()
_hw = next(p for p in _here.parents if p.name == "hardware")
sys.path.insert(0, str(_hw / "scripts"))
sys.path.insert(0, str(_hw / "printed-parts" / "cadlib"))
from _cadq_export import export_assembly  # noqa: E402
from _materials import M_DONOR_BLACK, one_body  # noqa: E402

STEP = _here.parent / "riteav-keystone.step"

# The opening the latch section passes and the two moulded tabs close behind.
OPEN_W = 14.5
OPEN_H = 16.0
# The corner radius the opening is cut with.
OPEN_R = 0.6
# The bezel standing on the wall's outer face, overhanging the opening on every side.
BEZEL_W = 16.4
BEZEL_H = 21.0
BEZEL_T = 1.6
# How far the body reaches inboard of the wall's inner face, and the width and height it holds
# over that reach — the volume the band above the cold core leaves clear behind the opening.
BODY_DEPTH = 26.0
BODY_W = 14.5
BODY_H = 16.0
# The panel thickness band the latch closes on.
PANEL_MIN = 1.5
PANEL_MAX = 3.2


def panel_cutout() -> tuple:
    """The opening this jack passes, as `(wx, wz, radius)` — `iec_c14_inlet.panel_cutout`'s shape.
    `enclosure_assembly.keystone_cutout` turns it into a `back_ports` entry."""
    return (OPEN_W, OPEN_H, OPEN_R)


def panel_footprint() -> tuple:
    """The bezel's outline on the wall's face, as `(wx, wz)`."""
    return (BEZEL_W, BEZEL_H)


def build():
    """The jack as three boxes on the mating axis: bezel outboard of the seating face, latch
    section through the wall, body inboard of it."""
    bezel = (cq.Workplane("XZ").box(BEZEL_W, BEZEL_H, BEZEL_T)
             .translate((0.0, BEZEL_T / 2.0, 0.0)))
    latch = (cq.Workplane("XZ").box(OPEN_W, OPEN_H, PANEL_MAX)
             .translate((0.0, -PANEL_MAX / 2.0, 0.0)))
    body = (cq.Workplane("XZ").box(BODY_W, BODY_H, BODY_DEPTH)
            .translate((0.0, -PANEL_MAX - BODY_DEPTH / 2.0, 0.0)))
    return bezel.union(latch).union(body).val()


def selftest():
    """Checks the bezel overhangs the opening, the panel band runs low to high, and the built
    solid's outboard face lands on `BEZEL_T`."""
    ok = True
    if not (BEZEL_W > OPEN_W and BEZEL_H > OPEN_H):
        print("FAIL: the bezel does not overhang the opening")
        ok = False
    if not PANEL_MIN < PANEL_MAX:
        print("FAIL: the latch's panel band is inverted")
        ok = False
    bb = build().BoundingBox()
    if abs(bb.ymax - BEZEL_T) > 1e-9:
        print(f"FAIL: the bezel's outboard face is at {bb.ymax}, not BEZEL_T {BEZEL_T}")
        ok = False
    print("PASS: riteav-keystone figures are self-consistent" if ok else "FAIL")
    return ok


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "selftest":
        raise SystemExit(0 if selftest() else 1)
    export_assembly(one_body(build(), "riteav-keystone", M_DONOR_BLACK), STEP)
    print(f"-> {STEP}")


if __name__ == "__main__":
    main()
