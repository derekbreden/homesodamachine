"""TPU sleeve: a diaphragm pump port barb straight onto 1/4 in OD LLDPE.

One part serves both ports. Print upright, barb socket on the bed. The internal
reducer rises 60 degrees above the bed into the tube bore, so no support stands
in either socket. Each socket's plain outside takes one hose clamp. The barb
socket is sized against the scanned G Ganen profiles; the dimensions are an
unprinted fit candidate.
"""
from pathlib import Path
import math
import sys

import cadquery as cq

HERE = Path(__file__).resolve().parent
HARDWARE = HERE.parents[1]
sys.path.insert(0, str(HARDWARE / "scripts"))
sys.path.insert(0, str(HARDWARE / "reference/g-ganen-pump"))
from _cadq_export import export_assembly
from _material_base import M_TPU_BLACK, one_body
import g_ganen_pump as pump

PORTS = {"suction": "port_yminus", "discharge": "port_yplus"}

BARB_BORE = 9.00
BARB_DEPTH = 11.0  # Stops short of the casting's root band on both ports.
TUBE_D = 6.35
TUBE_BORE = 6.10
TUBE_DEPTH = 15.0
TAPER_ANGLE = 60.0  # Degrees above the print bed.
REDUCER_LENGTH = (BARB_BORE - TUBE_BORE) / 2 * math.tan(math.radians(TAPER_ANGLE))
TUBE_START = BARB_DEPTH + REDUCER_LENGTH
LENGTH = TUBE_START + TUBE_DEPTH
MIN_WALL = 2.80  # Relaxed radial wall, the same at both sockets.
BARB_OD = BARB_BORE + 2 * MIN_WALL
TUBE_OD = TUBE_BORE + 2 * MIN_WALL
OUTER_REDUCER_START = TUBE_START - (BARB_OD - TUBE_OD) / 2 * math.tan(math.radians(TAPER_ANGLE))
ENTRY = .40
ENTRY_HEIGHT = ENTRY * math.tan(math.radians(TAPER_ANGLE))
MOUTH_BEVEL = .40
CLAMP_BAND = 9.0  # YDS butterfly clamp band width.
CLAMP_RANGE = (10.0, 16.0)  # The owned YDS clamps' diameter range.


def barb_rows(port):
    """`(distance into the barb from its tip, diameter)` for one scanned port."""
    profile = pump.port_profile(PORTS[port])["profile"]
    return sorted((-row["distance_from_tip_mm"], 2 * row["radius_mm"]) for row in profile)


def engaged(port):
    return [d for x, d in barb_rows(port) if x <= BARB_DEPTH]


def crest():
    """The largest scanned diameter either port presents inside the socket."""
    return max(max(engaged(port)) for port in PORTS)


def root():
    """The scanned diameter at the socket mouth, larger of the two ports."""
    def at(port):
        rows = barb_rows(port)
        return min(rows, key=lambda row: abs(row[0] - BARB_DEPTH))[1]
    return max(at(port) for port in PORTS)


def installed_od(relaxed_od, bore, opened):
    """Outside diameter with the bore opened, conserving the annular section."""
    return math.sqrt(relaxed_od**2 + opened**2 - bore**2)


def _revolve(profile):
    return (cq.Workplane("XZ").polyline(profile).close()
            .revolve(360, (0, 0), (0, 1)).val())


def build(*, installed=False):
    """Relaxed printable solid, or the expanded envelope a placement occupies.

    The installed view opens the barb socket to the largest scanned crest and
    the tube socket to the tube OD, and grows the outside radii by conserving
    annular section area. It is placement geometry, not an elastomer
    deformation or sealing model.
    """
    barb_d = crest() if installed else BARB_BORE
    tube_d = TUBE_D if installed else TUBE_BORE
    rb = installed_od(BARB_OD, BARB_BORE, barb_d) / 2
    rt = installed_od(TUBE_OD, TUBE_BORE, tube_d) / 2
    outer = _revolve([
        (0, 0), (rb - MOUTH_BEVEL, 0), (rb, MOUTH_BEVEL),
        (rb, OUTER_REDUCER_START), (rt, TUBE_START),
        (rt, LENGTH - MOUTH_BEVEL), (rt - MOUTH_BEVEL, LENGTH), (0, LENGTH),
    ])
    bore = _revolve([
        (0, -.1), (barb_d / 2 + ENTRY, -.1),
        (barb_d / 2 + ENTRY, 0), (barb_d / 2, ENTRY_HEIGHT),
        (barb_d / 2, BARB_DEPTH), (tube_d / 2, TUBE_START),
        (tube_d / 2, LENGTH - ENTRY_HEIGHT),
        (tube_d / 2 + ENTRY, LENGTH),
        (tube_d / 2 + ENTRY, LENGTH + .1), (0, LENGTH + .1),
    ])
    return outer.cut(bore).clean()


def placed(tip, axis):
    """Seated with the barb tip BARB_DEPTH inside the mouth, tube end outward."""
    z = cq.Vector(*axis).normalized()
    origin = cq.Vector(*tip) - z * BARB_DEPTH
    ref = cq.Vector(0, 0, 1) if abs(z.z) < .9 else cq.Vector(1, 0, 0)
    x = ref.cross(z).normalized()
    location = cq.Location(cq.Plane(origin=origin, xDir=x, normal=z))
    return build(installed=True).moved(location)


def tube_mouth(tip, axis):
    """Where the tube enters: `(position, outward axis)`."""
    z = cq.Vector(*axis).normalized()
    p = cq.Vector(*tip) + z * (LENGTH - BARB_DEPTH)
    return (p.x, p.y, p.z), (z.x, z.y, z.z)


def main():
    shape = build()
    stl = HERE / "diaphragm-pump-sleeve.stl"
    step = HERE / "diaphragm-pump-sleeve.step"
    cq.exporters.export(shape, str(stl), tolerance=.025, angularTolerance=.08)
    export_assembly(one_body(shape, "diaphragm-pump-sleeve", M_TPU_BLACK), str(step))
    import flute_payload
    flute_payload.cut(step, stl, preserve_print_triangles=True)
    sys.path.insert(0, str(HARDWARE.parent / "tools"))
    from docgen import substitute_md
    valley = min(min(d for x, d in barb_rows(port) if 2.0 <= x <= BARB_DEPTH - 2.0)
                 for port in PORTS)
    substitute_md(HERE / "README.md", variables={
        "BARB_BORE": f"{BARB_BORE:.2f}", "BARB_DEPTH": f"{BARB_DEPTH:g}",
        "TUBE_BORE": f"{TUBE_BORE:.2f}", "TUBE_DEPTH": f"{TUBE_DEPTH:g}",
        "TAPER_ANGLE": f"{TAPER_ANGLE:g}", "LENGTH": f"{LENGTH:.2f}",
        "BARB_OD": f"{BARB_OD:g}", "TUBE_OD": f"{TUBE_OD:g}",
        "MIN_WALL": f"{MIN_WALL:.2f}",
        "CREST": f"{crest():.2f}", "VALLEY": f"{valley:.2f}", "ROOT": f"{root():.2f}",
        "CREST_STRETCH": f"{(crest() / BARB_BORE - 1) * 100:.0f}",
        "BARB_OD_INSTALLED": f"{installed_od(BARB_OD, BARB_BORE, crest()):.2f}",
        "TUBE_OD_INSTALLED": f"{installed_od(TUBE_OD, TUBE_BORE, TUBE_D):.2f}",
        "BEYOND_TIP": f"{LENGTH - BARB_DEPTH:.2f}",
        "VOLUME": f"{shape.Volume() / 1000:.3f}",
    })
    print(f"-> {step.name}, {stl.name}, {step.name}.mesh; {shape.Volume() / 1000:.3f} cm3")
    print(f"   crest {crest():.2f}, installed barb OD "
          f"{installed_od(BARB_OD, BARB_BORE, crest()):.2f} in a "
          f"{CLAMP_RANGE[0]:g}-{CLAMP_RANGE[1]:g} mm clamp")


if __name__ == "__main__":
    main()
