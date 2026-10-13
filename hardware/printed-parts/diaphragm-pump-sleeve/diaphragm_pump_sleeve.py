"""TPU elbow sleeve: a diaphragm pump port barb onto 1/4 in OD LLDPE, turned 90 degrees.

One part serves both ports, clocked on the barb at assembly. It prints as a V on
the flat foot at its outer corner, both mouths up: the bore crowns and lower
faces stand at 45 degrees and nothing needs support. Each socket takes one hose
clamp on its plain outside. The barb socket is sized against the scanned
G Ganen profiles; the dimensions are an unprinted fit candidate.

Local frame: the barb tip at the origin, +X out along the barb, +Y the way the
tube leaves, Z = X x Y.
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
BARB_DEPTH = 11.0  # The barb tip bottoms on the passage shelf; the mouth stops short of the casting.
TUBE_D = 6.35
TUBE_BORE = 6.10
TUBE_DEPTH = 15.0
PASSAGE = 4.40  # The corner's bore, just over the tube's 4.32 mm ID.
MIN_WALL = 2.80  # Relaxed radial wall, the same at both sockets.
BARB_OD = BARB_BORE + 2 * MIN_WALL
TUBE_OD = TUBE_BORE + 2 * MIN_WALL
TUBE_STOP = 3.50  # The tube end's shelf above the barb axis; a tube pushed past it would close the corner.
TUBE_MOUTH = TUBE_STOP + TUBE_DEPTH
CLAMP_BAND = 9.0  # YDS butterfly clamp band width.
CLAMP_RANGE = (10.0, 16.0)  # The owned YDS clamps' diameter range.
BAND_AIR = .35  # Between the barb clamp's band, flush with the mouth, and the tube leg.
ENTRY = .40
ENTRY_HEIGHT = ENTRY * math.tan(math.radians(60.0))
BEND_R = 14.0  # 1/4 in LLDPE's tightest bend (`_routing.STOCKS`), what a straight sleeve's tube turns at.
STRAIGHT_PAST_TIP = 28.51 - BARB_DEPTH  # The straight sleeve's tube mouth past the tip (c4ae85768).


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


BARB_OD_INSTALLED = installed_od(BARB_OD, BARB_BORE, crest())
TUBE_OD_INSTALLED = installed_od(TUBE_OD, TUBE_BORE, TUBE_D)
# The tube leg's axis past the barb tip: as close as the barb clamp's band leaves room for.
TUBE_AXIS = -(BARB_DEPTH - CLAMP_BAND) + BAND_AIR + TUBE_OD_INSTALLED / 2
KNUCKLE = TUBE_OD / 2  # Half-width of the square block around the corner.
PAST_TIP = TUBE_AXIS + KNUCKLE
# The foot: a flat across the knuckle's outer corner, one wall from the corner's bore.
FOOT = TUBE_AXIS / math.sqrt(2) + PASSAGE / 2 + MIN_WALL
FOOT_WIDTH = 2 * ((PAST_TIP + KNUCKLE) / math.sqrt(2) - FOOT)


def _x(r, x0, x1):
    return cq.Solid.makeCylinder(r, x1 - x0, cq.Vector(x0, 0, 0), cq.Vector(1, 0, 0))


def _y(r, y0, y1):
    return cq.Solid.makeCylinder(r, y1 - y0, cq.Vector(TUBE_AXIS, y0, 0), cq.Vector(0, 1, 0))


def _cone_x(r0, r1, x0, x1):
    return cq.Solid.makeCone(r0, r1, x1 - x0, cq.Vector(x0, 0, 0), cq.Vector(1, 0, 0))


def _cone_y(r0, r1, y0, y1):
    return cq.Solid.makeCone(r0, r1, y1 - y0, cq.Vector(TUBE_AXIS, y0, 0), cq.Vector(0, 1, 0))


def build_local(*, installed=False):
    """The elbow in its own frame: relaxed, or the envelope a placement occupies.

    The installed view opens the barb socket to the largest scanned crest and
    the tube socket to the tube OD, and grows those two outside radii by
    conserving annular section area. It is placement geometry, not an elastomer
    deformation or sealing model.
    """
    barb_d = crest() if installed else BARB_BORE
    tube_d = TUBE_D if installed else TUBE_BORE
    rb = (BARB_OD_INSTALLED if installed else BARB_OD) / 2
    rt = (TUBE_OD_INSTALLED if installed else TUBE_OD) / 2
    k = max(KNUCKLE, rt)
    outer = (_x(rb, -BARB_DEPTH, 0)
             .fuse(cq.Solid.makeBox(PAST_TIP, 2 * k, 2 * k, cq.Vector(0, -k, -k)))
             .fuse(_y(rt, 0, TUBE_MOUTH)))
    # Everything past the foot plane, across the knuckle's outer corner.
    span = 4 * (BARB_DEPTH + TUBE_MOUTH)
    foot = (cq.Solid.makeBox(span, span, span, cq.Vector(0, -span / 2, -span / 2))
            .rotate((0, 0, 0), (0, 0, 1), -45)
            .translate(cq.Vector(FOOT / math.sqrt(2), -FOOT / math.sqrt(2), 0)))
    outer = outer.cut(foot)
    cavity = (_x(barb_d / 2, -BARB_DEPTH, 0)
              .fuse(_cone_x(barb_d / 2 + ENTRY, barb_d / 2, -BARB_DEPTH - .01,
                            -BARB_DEPTH + ENTRY_HEIGHT))
              .fuse(_x(PASSAGE / 2, -.01, TUBE_AXIS))
              .fuse(cq.Solid.makeSphere(PASSAGE / 2, cq.Vector(TUBE_AXIS, 0, 0),
                                        angleDegrees1=-90))
              .fuse(_y(PASSAGE / 2, 0, TUBE_STOP + .01))
              .fuse(_y(tube_d / 2, TUBE_STOP, TUBE_MOUTH))
              .fuse(_cone_y(tube_d / 2, tube_d / 2 + ENTRY, TUBE_MOUTH - ENTRY_HEIGHT,
                            TUBE_MOUTH + .01)))
    return outer.cut(cavity).clean()


def build():
    """The printable elbow, as a V on its foot at Z = 0, centred in X and Y."""
    shape = build_local()
    s = 1 / math.sqrt(2)
    turned = shape.moved(cq.Location(cq.Plane(
        origin=(0, 0, 0), xDir=(s, 0, -s), normal=(0, -1, 0))))
    box = turned.BoundingBox()
    return turned.translate(cq.Vector(-(box.xmin + box.xmax) / 2,
                                      -(box.ymin + box.ymax) / 2, -box.zmin))


def _frame(tip, axis, toward):
    x = cq.Vector(*axis).normalized()
    t = cq.Vector(*toward)
    y = (t - x * t.dot(x)).normalized()
    return cq.Vector(*tip), x, y


def placed(tip, axis, toward):
    """Seated on a barb whose tip and outward axis are given, tube leaving `toward`."""
    origin, x, y = _frame(tip, axis, toward)
    location = cq.Location(cq.Plane(origin=origin, xDir=x, normal=x.cross(y)))
    return build_local(installed=True).moved(location)


def tube_mouth(tip, axis, toward):
    """Where the tube enters: `(position, outward axis)`."""
    origin, x, y = _frame(tip, axis, toward)
    p = origin + x * TUBE_AXIS + y * TUBE_MOUTH
    return (p.x, p.y, p.z), (y.x, y.y, y.z)


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
    box = shape.BoundingBox()
    substitute_md(HERE / "README.md", variables={
        "BARB_BORE": f"{BARB_BORE:.2f}", "BARB_DEPTH": f"{BARB_DEPTH:g}",
        "TUBE_BORE": f"{TUBE_BORE:.2f}", "TUBE_DEPTH": f"{TUBE_DEPTH:g}",
        "PASSAGE": f"{PASSAGE:.2f}", "TUBE_STOP": f"{TUBE_STOP:.1f}",
        "BARB_OD": f"{BARB_OD:g}", "TUBE_OD": f"{TUBE_OD:g}",
        "MIN_WALL": f"{MIN_WALL:.2f}",
        "INTERFERENCE": f"{TUBE_D - TUBE_BORE:.2f}", "CLAMP_BAND": f"{CLAMP_BAND:g}",
        "BEND_R": f"{BEND_R:g}",
        "TUBE_AXIS": f"{TUBE_AXIS:.2f}", "PAST_TIP": f"{PAST_TIP:.2f}",
        "TUBE_MOUTH": f"{TUBE_MOUTH:.1f}", "BAND_AIR": f"{BAND_AIR:.2f}",
        "STRAIGHT_AXIS": f"{STRAIGHT_PAST_TIP + BEND_R:.2f}",
        "FOOT_WIDTH": f"{FOOT_WIDTH:.2f}", "FOOT_LENGTH": f"{2 * KNUCKLE:g}",
        "PRINT_HEIGHT": f"{box.zlen:.1f}",
        "CREST": f"{crest():.2f}", "VALLEY": f"{valley:.2f}", "ROOT": f"{root():.2f}",
        "CREST_STRETCH": f"{(crest() / BARB_BORE - 1) * 100:.0f}",
        "BARB_OD_INSTALLED": f"{BARB_OD_INSTALLED:.2f}",
        "TUBE_OD_INSTALLED": f"{TUBE_OD_INSTALLED:.2f}",
        "VOLUME": f"{shape.Volume() / 1000:.3f}",
    })
    print(f"-> {step.name}, {stl.name}, {step.name}.mesh; {shape.Volume() / 1000:.3f} cm3")
    print(f"   tube axis {TUBE_AXIS:.2f} mm past the barb tip, outer corner {PAST_TIP:.2f}; "
          f"foot {FOOT_WIDTH:.2f} x {2 * KNUCKLE:g} mm; print height {box.zlen:.1f} mm")


if __name__ == "__main__":
    main()
