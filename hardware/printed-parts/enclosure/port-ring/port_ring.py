"""Port ring — the colour one of the rear wall's connections is read by.

A flat annulus lying in a pocket of the back wall's port field, with a through-wall fitting's
own flange landing on it. Nothing fastens it: the fitting's nut makes up on the inboard side
and draws flange, ring and wall together, so the ring is in the clamped stack the way the wall
is. It is round, and the pocket is its own thickness deep.

At the rear face the customer meets identical black fittings in a black wall, one of which
takes the blue tube — `../back-panel/README.md` §"Umbilical port — tube identification". What
a colour means on that wall is stated once, in `../back-panel/_back_panel_dimensions.py`.

The push a 1/4" push-to-connect takes to seat — past the collet's grabbers and an EPDM O-ring —
lands on this ring, and the ring carries it to the pocket floor across its whole face.

    RING_W    how far a ring stands past the fitting's own panel footprint, and so the width of
              colour that shows once the flange is on. The wall strikes its pockets from it and
              the iso line-art paints its discs from it
    THICK     the ring's thickness, the pocket's depth, and the field's proud height — one
              number, and `enclosure_assembly.bulkhead_seat_y` is where the wall spends it

Two neighbouring rings stand one `enclosure_assembly.PORT_PITCH` apart, and what that pitch
leaves between their pockets is the pad the field keeps between them; `port-field-web` reads
the two against each other.

Coordinate frame — THE FITTING'S, so `enclosure_assembly` seats one on a union's own station
with no turn of its own:
  Y = the fitting's flow axis. +Y = outboard, toward the customer's tube.
  Origin = the ring's INBOARD face, the one that lands in the pocket. The ring spans
      y = 0 to y = THICK, and the flange lands on that far face.
  +Z = up. X completes the right-handed frame.

It prints flat, many to a bed, in the colour the port it rings is named by.

Run:
    tools/cad-venv/bin/python hardware/printed-parts/enclosure/port-ring/port_ring.py
    tools/cad-venv/bin/python hardware/printed-parts/enclosure/port-ring/port_ring.py selftest
"""

import sys
from pathlib import Path

import cadquery as cq

_here = Path(__file__).resolve()
_hw = next(p for p in _here.parents if p.name == "hardware")
for _p in (_hw / "scripts",
           _hw / "printed-parts" / "cadlib",
           _hw / "reference" / "jg-bulkhead-union"):
    sys.path.insert(0, str(_p))
sys.path.insert(0, str(next(p for p in _here.parents
                            if (p / "tools" / "docgen").is_dir()) / "tools"))
from _cadq_export import export_step  # noqa: E402
from _measuring import bores  # noqa: E402
from world_workplane import xz_plane_y_up  # noqa: E402
import jg_bulkhead_union as _jg  # noqa: E402
from docgen import substitute_md  # noqa: E402

UNION_STEP = _here.parent / "port-ring-union.step"


# How far the ring stands past the fitting's own panel footprint — the width of colour that
# shows once the flange is on. `enclosure_assembly.back_wall_field` strikes its pockets from it
# and `drawings/line-art/_appliance_model` paints its discs from it. A pocket is this ring plus
# its slip, and what one `enclosure_assembly.PORT_PITCH` leaves between two of those pockets is
# the web the field keeps between them.
RING_W = 5.55
# The ring's thickness, the pocket's depth, and the field's proud height — one number. A
# fitting's flange bears this far outboard of the wall it clamps, which is what
# `enclosure_assembly.bulkhead_seat_y` adds.
THICK = 3.0
# The slip a ring takes around the fitting's threading — the wall's own
# `enclosure_assembly.PORT_HOLE_SLIP`. The two modules cannot import each other, so
# `port-ring-bore` is what holds them equal.
SLIP = 0.86


def ring_od(across: float) -> float:
    """The OD a ring takes on a fitting whose own panel footprint is `across`."""
    return across + 2.0 * RING_W


def union_od() -> float:
    """The PP1208E union's ring, read off the fitting."""
    return ring_od(_jg.BODY_D)


def union_bore_d() -> float:
    """Its bore — the hole the wall passes the same threading through."""
    return _jg.panel_hole_d(SLIP)


def seat() -> tuple:
    """The face a pocket takes it by: `(position, outward axis)` on the ring's INBOARD face,
    pointing at the wall. That face lands on the pocket's floor, which is the back wall's own
    outer face, so `enclosure_assembly` seats a ring on the plane the field was raised off
    rather than on the crown the field raised."""
    return ((0.0, 0.0, 0.0), (0.0, -1.0, 0.0))


def build_port_ring(across: float, bore_d: float):
    """One ring as a solid: a flat annulus spanning y = 0 to THICK."""
    return (cq.Workplane(xz_plane_y_up)
            .circle(ring_od(across) / 2.0)
            .circle(bore_d / 2.0)
            .extrude(THICK))


def build_union_ring():
    """The ring the two marked PP1208E stations wear — carbonated water in blue, tap water in
    white. One geometry, two colours."""
    return build_port_ring(_jg.BODY_D, union_bore_d())


def stations_hold():
    """Hold the figures the wall and the drawing read to `port-ring-union.step` itself.

    The OD is an extent of that solid, the thickness its run along the axis, and the bore a
    turned face inside it — so a ring exported from different numbers is caught here rather
    than by a pocket it will not drop into."""
    solid = cq.importers.importStep(str(UNION_STEP)).val()
    bb = solid.BoundingBox()
    for what, claimed, actual in (("ring OD", union_od(), bb.xlen),
                                  ("ring height", union_od(), bb.zlen),
                                  ("ring thickness", THICK, bb.ylen)):
        if abs(claimed - actual) > 1e-6:
            raise ValueError(
                f"port-ring {what} is {claimed:g} and {UNION_STEP.name} carries {actual:.4f} — "
                f"a wall pocketed to the declared figure does not take the ring that is there.")
    radii = sorted({r for _axis, r in bores(solid)})
    if not any(abs(2.0 * r - union_bore_d()) <= 1e-6 for r in radii):
        raise ValueError(
            f"the ring's bore is declared Ø{union_bore_d():g} and {UNION_STEP.name} turns no "
            f"face at that diameter — it carries Ø{[round(2 * r, 3) for r in radii]}. A ring "
            f"bored under the wall's own figure closes on the threading the wall passes.")


def selftest() -> int:
    """The ring against the fitting it rings and the wall that pockets it."""
    fails = []
    if union_od() <= _jg.BODY_D:
        fails.append(f"a ring of Ø{union_od():g} shows nothing past a Ø{_jg.BODY_D:g} flange")
    if union_bore_d() <= _jg.THREAD_D:
        fails.append(
            f"the ring's bore Ø{union_bore_d():g} does not pass the fitting's own "
            f"Ø{_jg.THREAD_D:g} threading")
    if THICK >= _jg.THREAD_LEN:
        fails.append(
            f"a ring {THICK:g} thick stands in the {_jg.THREAD_LEN:g} mm of thread the fitting "
            f"has, and leaves none of it for the nut")
    try:
        stations_hold()
    except Exception as exc:                                     # noqa: BLE001
        fails.append(str(exc))
    for line in fails:
        print(f"FAIL {line}")
    if not fails:
        print(f"ok  port-ring  Ø{union_od():g} × Ø{union_bore_d():g} × {THICK:g}, "
              f"{RING_W:g} mm of colour past the flange")
    return 1 if fails else 0


def main():
    part = build_union_ring()
    bb = part.val().BoundingBox()
    print("Port ring — PP1208E union station")
    print(f"  OD Ø{union_od():g} / bore Ø{union_bore_d():g} / thickness {THICK:g}")
    print(f"  Colour showing past the flange: {RING_W:g} mm")
    print(f"  Canonical-frame bounding box: "
          f"X [{bb.xmin:.2f}, {bb.xmax:.2f}]  "
          f"Y [{bb.ymin:.2f}, {bb.ymax:.2f}]  "
          f"Z [{bb.zmin:.2f}, {bb.zmax:.2f}]")
    print(f"  Solid valid: {part.val().isValid()}")

    export_step(part, str(UNION_STEP))
    print(f"-> {UNION_STEP.name}")

    variables = {
        "RING_W": f"{RING_W:g}",
        "RING_THICK": f"{THICK:g}",
        "RING_OD": f"{union_od():g}",
        "RING_BORE": f"{union_bore_d():g}",
        "RING_VOL": f"{part.val().Volume() / 1000.0:.2f}",
    }
    substitute_md(_here.parent / "README.md", variables=variables,
                  expected_counts={"RING_W": 1, "RING_THICK": 2, "RING_OD": 1,
                                   "RING_BORE": 1, "RING_VOL": 1})
    print("-> README.md")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "selftest":
        sys.exit(selftest())
    main()
