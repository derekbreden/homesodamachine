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

    RING_W    how far a ring stands past the fitting's own flange, and so the width of colour
              that shows once the flange is on. The wall strikes its pockets from it and the
              iso line-art paints its discs from it
    THICK     the ring's thickness, the pocket's depth, and the field's proud height — one
              number, and `enclosure_assembly.bulkhead_seat_y` is where the wall spends it

The wall passes two families of fitting and each states its own flange and its own barrel, so
`STATIONS` is one ring geometry per family and `RING_W` is what they share.

Each ring stands in a pad of its own — a rim of printed wall one `enclosure_assembly.PORT_RING_RIM`
wide around it, standing `PORT_PAD_PROUD` off the wall. Two neighbouring rings stand one
`enclosure_assembly.PORT_PITCH` apart, and what that pitch leaves between their two rims is air;
`port-field-web` reads the two against each other.

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
           _hw / "reference" / "jg-bulkhead-union",
           _hw / "reference" / "neofit-bulkhead"):
    sys.path.insert(0, str(_p))
sys.path.insert(0, str(next(p for p in _here.parents
                            if (p / "tools" / "docgen").is_dir()) / "tools"))
from _cadq_export import export_step  # noqa: E402
from _measuring import bores  # noqa: E402
from world_workplane import xz_plane_y_up  # noqa: E402
import jg_bulkhead_union as _jg  # noqa: E402
import neofit_bulkhead as _neo  # noqa: E402
from docgen import substitute_md  # noqa: E402

# ONE ANNULUS IN TWO SIZES, because the wall takes two families of fitting. Each ring is struck on
# the flange it hides under and the barrel it passes, so a ring is named by the fitting it rings:
# `union` for the PP1208E unions the water and umbilical ports use, `neofit` for the ABU44 the CO2
# inlet uses. `RING_W` and `THICK` are the same for both.
STATIONS = {"union": _jg, "neofit": _neo}
STEPS = {name: _here.parent / f"port-ring-{name}.step" for name in STATIONS}


# How far the ring stands past the fitting's own panel footprint — the width of colour that
# shows once the flange is on. `enclosure_assembly.back_wall_field` strikes its pockets from it
# and `drawings/line-art/_appliance_model` paints its discs from it. A pocket is this ring plus
# its slip, and what one `enclosure_assembly.PORT_PITCH` leaves between two of those pockets is
# the web the field keeps between them.
RING_W = 4.05
# The ring's thickness. A fitting's flange bears this far outboard of the wall it clamps, which
# is what `enclosure_assembly.bulkhead_seat_y` adds. The pad the ring stands in is shallower —
# `enclosure_assembly.PORT_PAD_PROUD` — so the ring stands proud of its own rim.
THICK = 2.0
# The slip a ring takes around the fitting's threading — the wall's own
# `enclosure_assembly.PORT_HOLE_SLIP`. The two modules cannot import each other, so
# `port-ring-bore` is what holds them equal.
SLIP = 0.86


def ring_od(across: float) -> float:
    """The OD a ring takes on a fitting whose own panel footprint is `across`."""
    return across + 2.0 * RING_W


def od(station: str) -> float:
    """One station's ring OD, read off the flange it lies under."""
    return ring_od(STATIONS[station].flange_footprint())


def bore_d(station: str) -> float:
    """Its bore — the hole the wall passes that fitting's own barrel through."""
    return STATIONS[station].panel_hole_d(SLIP)


def seat() -> tuple:
    """The face a pad takes it by: `(position, outward axis)` on the ring's INBOARD face,
    pointing at the wall. That face lands on the back wall's own outer face, which is the floor
    the pad's rim stands off — so the wall keeps its whole thickness under every ring."""
    return ((0.0, 0.0, 0.0), (0.0, -1.0, 0.0))


def build_port_ring(across: float, bore: float):
    """One ring as a solid: a flat annulus spanning y = 0 to THICK."""
    return (cq.Workplane(xz_plane_y_up)
            .circle(ring_od(across) / 2.0)
            .circle(bore / 2.0)
            .extrude(THICK))


def build_ring(station: str):
    """One station's ring, struck on the fitting that station carries."""
    return build_port_ring(STATIONS[station].flange_footprint(), bore_d(station))


def stations_hold():
    """Hold the figures the wall and the drawing read to each ring's own STEP.

    The OD is an extent of that solid, the thickness its run along the axis, and the bore a
    turned face inside it — so a ring exported from different numbers is caught here rather
    than by a pocket it will not drop into."""
    for station, step in STEPS.items():
        solid = cq.importers.importStep(str(step)).val()
        bb = solid.BoundingBox()
        for what, claimed, actual in (("ring OD", od(station), bb.xlen),
                                      ("ring height", od(station), bb.zlen),
                                      ("ring thickness", THICK, bb.ylen)):
            if abs(claimed - actual) > 1e-6:
                raise ValueError(
                    f"port-ring {station} {what} is {claimed:g} and {step.name} carries "
                    f"{actual:.4f} — a wall pocketed to the declared figure does not take the "
                    f"ring that is there.")
        radii = sorted({r for _axis, r in bores(solid)})
        if not any(abs(2.0 * r - bore_d(station)) <= 1e-6 for r in radii):
            raise ValueError(
                f"the {station} ring's bore is declared Ø{bore_d(station):g} and {step.name} "
                f"turns no face at that diameter — it carries "
                f"Ø{[round(2 * r, 3) for r in radii]}. A ring bored under the wall's own figure "
                f"closes on the barrel the wall passes.")


def selftest() -> int:
    """Each ring against the fitting it rings and the wall that pockets it."""
    fails = []
    for station, fitting in STATIONS.items():
        flange = fitting.flange_footprint()
        if od(station) <= flange:
            fails.append(f"a {station} ring of Ø{od(station):g} shows nothing past a "
                         f"Ø{flange:g} flange")
        if bore_d(station) <= fitting.THREAD_D:
            fails.append(
                f"the {station} ring's bore Ø{bore_d(station):g} does not pass the fitting's "
                f"own Ø{fitting.THREAD_D:g} barrel")
    if THICK >= _jg.THREAD_LEN:
        fails.append(
            f"a ring {THICK:g} thick stands in the {_jg.THREAD_LEN:g} mm of thread the union "
            f"has, and leaves none of it for the nut")
    if THICK >= _neo.PANEL_THREAD:
        fails.append(
            f"a ring {THICK:g} thick stands in the {_neo.PANEL_THREAD:.2f} mm of barrel the "
            f"ABU44 offers outboard of its flange, and leaves none of it for the wall")
    try:
        stations_hold()
    except Exception as exc:                                     # noqa: BLE001
        fails.append(str(exc))
    for line in fails:
        print(f"FAIL {line}")
    if not fails:
        print("ok  port-ring  " + ", ".join(
            f"{s} Ø{od(s):g} × Ø{bore_d(s):g}" for s in STATIONS)
            + f" × {THICK:g}, {RING_W:g} mm of colour past each flange")
    return 1 if fails else 0


def main():
    volumes = {}
    for station, step in STEPS.items():
        part = build_ring(station)
        bb = part.val().BoundingBox()
        volumes[station] = part.val().Volume() / 1000.0
        print(f"Port ring — {station} station")
        print(f"  OD Ø{od(station):g} / bore Ø{bore_d(station):g} / thickness {THICK:g}")
        print(f"  Colour showing past the flange: {RING_W:g} mm")
        print(f"  Canonical-frame bounding box: "
              f"X [{bb.xmin:.2f}, {bb.xmax:.2f}]  "
              f"Y [{bb.ymin:.2f}, {bb.ymax:.2f}]  "
              f"Z [{bb.zmin:.2f}, {bb.zmax:.2f}]")
        print(f"  Solid valid: {part.val().isValid()}")
        export_step(part, str(step))
        print(f"-> {step.name}")

    variables = {
        "RING_W": f"{RING_W:g}",
        "RING_THICK": f"{THICK:g}",
        "RING_OD": f"{od('union'):g}",
        "RING_BORE": f"{bore_d('union'):g}",
        "RING_VOL": f"{volumes['union']:.2f}",
        "CO2_RING_OD": f"{od('neofit'):.2f}",
        "CO2_RING_BORE": f"{bore_d('neofit'):g}",
        "CO2_RING_VOL": f"{volumes['neofit']:.2f}",
    }
    substitute_md(_here.parent / "README.md", variables=variables,
                  expected_counts={"RING_W": 1, "RING_THICK": 2, "RING_OD": 1,
                                   "RING_BORE": 1, "RING_VOL": 1, "CO2_RING_OD": 1,
                                   "CO2_RING_BORE": 1, "CO2_RING_VOL": 1})
    print("-> README.md")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "selftest":
        sys.exit(selftest())
    main()
