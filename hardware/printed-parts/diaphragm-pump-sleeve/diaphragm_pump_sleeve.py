"""TPU elbow: a diaphragm pump port barb onto 1/4 in OD LLDPE, turned 90 degrees.

One part serves both ports, clocked on the barb at assembly. A rounded heel and a
smooth neck join the two round sockets, and a flat foot across the outer corner
stands it as a V with both mouths up. Each socket takes one 9 mm clamp band on
its plain outside. The barb socket is sized against the scanned G Ganen
profiles; the identified Siraya Tech Flex TPU 85A articles share this geometry.

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
from _material_base import one_body
import g_ganen_pump as pump

PORTS = {"suction": "port_yminus", "discharge": "port_yplus"}

# Siraya Tech Flex TPU 85A Clear, the stock the pump dock's wet TPU parts print in.
COLOR = cq.Color(.92, .92, .90, .60)

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
NECK = TUBE_STOP + 3.0  # The smooth reduction ends before the tube clamp's complete seat.
CLAMP_BAND = 9.0  # YDS butterfly clamp band width.
CLAMP_RANGE = (10.0, 16.0)  # The owned YDS clamps' diameter range.
BAND_AIR = 1.0  # Between the barb clamp's band, flush with the mouth, and the tube leg.
BAND_T = .6  # The closed band's own thickness, as the assembly draws it.
ENTRY = .40
ENTRY_HEIGHT = ENTRY * math.tan(math.radians(60.0))


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
# The foot: a flat across the heel's outer corner, one wall from the corner's bore.
FOOT = TUBE_AXIS / math.sqrt(2) + PASSAGE / 2 + MIN_WALL


def _x(r, x0, x1):
    return cq.Solid.makeCylinder(r, x1 - x0, cq.Vector(x0, 0, 0), cq.Vector(1, 0, 0))


def _y(r, y0, y1):
    return cq.Solid.makeCylinder(r, y1 - y0, cq.Vector(TUBE_AXIS, y0, 0), cq.Vector(0, 1, 0))


def build_local(*, installed=False, exterior=False):
    """The elbow in its own frame: relaxed, or the envelope a placement occupies.

    The neck is a revolved fifth-degree Bezier, r(t) = rb + (rt - rb)(10t^3 - 15t^4 + 6t^5),
    so radius, slope and curvature meet both round legs. The heel is the barb leg's own
    sphere about the corner.

    The installed view opens the barb socket to the largest scanned crest and the tube socket
    to the tube OD, grows those two outside radii by conserving annular section area, and
    lengthens the neck by a millimetre. It is placement geometry, not an elastomer deformation
    or sealing model.
    """
    rb = (BARB_OD_INSTALLED if installed else BARB_OD) / 2
    rt = (TUBE_OD_INSTALLED if installed else TUBE_OD) / 2
    bore_b = (crest() if installed else BARB_BORE) / 2
    bore_t = (TUBE_D if installed else TUBE_BORE) / 2
    length = NECK + (1.0 if installed else 0.0)
    profile = (cq.Workplane("XY").moveTo(0, 0).lineTo(rb, 0)
               .bezier([(rb, length / 5), (rb, 2 * length / 5),
                        (rt, 3 * length / 5), (rt, 4 * length / 5), (rt, length)],
                       includeCurrent=True)
               .lineTo(0, length).close())
    neck = profile.revolve(360, (0, 0, 0), (0, 1, 0)).val().translate((TUBE_AXIS, 0, 0))
    heel = cq.Solid.makeSphere(rb, cq.Vector(TUBE_AXIS, 0, 0), angleDegrees1=-90)
    # Sequential unions keep the tangent sphere quadrant in OCC.
    outer = (_x(rb, -BARB_DEPTH, TUBE_AXIS).fuse(heel)
             .fuse(neck).fuse(_y(rt, length, TUBE_MOUTH)))
    span = 4 * (BARB_DEPTH + TUBE_MOUTH)
    foot = (cq.Solid.makeBox(span, span, span, cq.Vector(0, -span / 2, -span / 2))
            .rotate((0, 0, 0), (0, 0, 1), -45)
            .translate(cq.Vector(FOOT / math.sqrt(2), -FOOT / math.sqrt(2), 0)))
    outer = outer.cut(foot)
    if exterior:
        return outer if installed else outer.clean()
    cavity = _x(bore_b, -BARB_DEPTH - .01, 0).fuse(
        cq.Solid.makeCone(bore_b + ENTRY, bore_b, ENTRY_HEIGHT,
                          cq.Vector(-BARB_DEPTH, 0, 0), cq.Vector(1, 0, 0)),
        _x(PASSAGE / 2, 0, TUBE_AXIS),
        _y(PASSAGE / 2, 0, TUBE_STOP),
        _y(bore_t, TUBE_STOP, TUBE_MOUTH + .01),
        cq.Solid.makeCone(bore_t, bore_t + ENTRY, ENTRY_HEIGHT,
                          cq.Vector(TUBE_AXIS, TUBE_MOUTH - ENTRY_HEIGHT, 0),
                          cq.Vector(0, 1, 0)))
    body = outer.cut(cavity)
    # An expanded envelope keeps its native face boundaries: a same-domain merge at its
    # tangent skins costs far more than the placement it serves.
    return body if installed else body.clean()


def build(exterior=False):
    """The printable elbow, as a V on its foot at Z = 0, centred in X and Y.

    The foot plane is exact. A spline's bounding box carries a tolerance that would leave the
    foot above Z = 0, so the pose is set off the analytic extremes instead: the two mouth rims
    in X, and the symmetric local Z in Y."""
    s = 1 / math.sqrt(2)
    posed = build_local(exterior=exterior).moved(cq.Location(cq.Plane(
        origin=(0, 0, 0), xDir=(s, 0, -s), normal=(0, -1, 0))))
    xmin = (-BARB_DEPTH - BARB_OD / 2) * s
    xmax = (TUBE_AXIS + TUBE_OD / 2 + TUBE_MOUTH) * s
    return posed.translate(cq.Vector(-(xmin + xmax) / 2, 0, FOOT))


def _frame(tip, axis, toward):
    x = cq.Vector(*axis).normalized()
    t = cq.Vector(*toward)
    y = (t - x * t.dot(x)).normalized()
    return cq.Vector(*tip), x, y


def location(tip, axis, toward):
    """Seated on a barb whose tip and outward axis are given, tube leaving `toward`."""
    origin, x, y = _frame(tip, axis, toward)
    return cq.Location(cq.Plane(origin=origin, xDir=x, normal=x.cross(y)))


def placed(tip, axis, toward):
    return build_local(installed=True).moved(location(tip, axis, toward))


def tube_port():
    """Where the tube enters, in the elbow's own frame: `(position, outward axis)`."""
    return (TUBE_AXIS, TUBE_MOUTH, 0.0), (0.0, 1.0, 0.0)


def tube_mouth(tip, axis, toward):
    """Where the tube enters a seated elbow: `(position, outward axis)`."""
    origin, x, y = _frame(tip, axis, toward)
    p = origin + x * TUBE_AXIS + y * TUBE_MOUTH
    return (p.x, p.y, p.z), (y.x, y.y, y.z)


def bands(tip, axis, toward):
    """The two clamp bands, closed, flush with their mouths. The housing, screw and key stand
    outside this ring and are not drawn."""
    origin, x, y = _frame(tip, axis, toward)
    out = {}
    for name, start, normal, diameter in (
            ("barb", origin - x * BARB_DEPTH, x, BARB_OD_INSTALLED),
            ("tube", origin + x * TUBE_AXIS + y * (TUBE_MOUTH - CLAMP_BAND), y,
             TUBE_OD_INSTALLED)):
        ring = cq.Solid.makeCylinder(diameter / 2 + BAND_T, CLAMP_BAND, start, normal)
        out[name] = ring.cut(cq.Solid.makeCylinder(diameter / 2, CLAMP_BAND, start, normal))
    return out


def main():
    shape = build()
    stl = HERE / "diaphragm-pump-sleeve.stl"
    step = HERE / "diaphragm-pump-sleeve.step"
    cq.exporters.export(shape, str(stl), tolerance=.025, angularTolerance=.08)
    export_assembly(one_body(shape, "diaphragm-pump-sleeve", COLOR), str(step))
    import flute_payload
    flute_payload.cut(step, stl, preserve_print_triangles=True)
    sys.path.insert(0, str(HARDWARE.parent / "tools"))
    from docgen import substitute_md
    valley = min(min(d for x, d in barb_rows(port) if 2.0 <= x <= BARB_DEPTH - 2.0)
                 for port in PORTS)
    box = shape.BoundingBox()
    s = 1 / math.sqrt(2)
    foot = build_local(exterior=True).moved(cq.Location(cq.Plane(
        origin=(0, 0, 0), xDir=(s, 0, -s), normal=(0, -1, 0))))
    foot_area = sum(f.Area() for f in cq.Workplane().add(foot).faces("<Z").vals())
    substitute_md(HERE / "README.md", variables={
        "BARB_BORE": f"{BARB_BORE:.2f}", "BARB_DEPTH": f"{BARB_DEPTH:g}",
        "TUBE_BORE": f"{TUBE_BORE:.2f}", "TUBE_DEPTH": f"{TUBE_DEPTH:g}",
        "PASSAGE": f"{PASSAGE:.2f}", "TUBE_STOP": f"{TUBE_STOP:.1f}",
        "BARB_OD": f"{BARB_OD:g}", "TUBE_OD": f"{TUBE_OD:g}",
        "MIN_WALL": f"{MIN_WALL:.2f}", "NECK": f"{NECK:g}",
        "INTERFERENCE": f"{TUBE_D - TUBE_BORE:.2f}", "CLAMP_BAND": f"{CLAMP_BAND:g}",
        "TUBE_AXIS": f"{TUBE_AXIS:.2f}", "TUBE_MOUTH": f"{TUBE_MOUTH:.1f}",
        "BAND_AIR": f"{BAND_AIR:g}", "FOOT_AREA": f"{foot_area:.1f}",
        "PRINT_HEIGHT": f"{box.zlen:.1f}",
        "CREST": f"{crest():.2f}", "VALLEY": f"{valley:.2f}", "ROOT": f"{root():.2f}",
        "CREST_STRETCH": f"{(crest() / BARB_BORE - 1) * 100:.0f}",
        "BARB_OD_INSTALLED": f"{BARB_OD_INSTALLED:.2f}",
        "TUBE_OD_INSTALLED": f"{TUBE_OD_INSTALLED:.2f}",
        "VOLUME": f"{shape.Volume() / 1000:.3f}",
    })
    print(f"-> {step.name}, {stl.name}, {step.name}.mesh; {shape.Volume() / 1000:.3f} cm3")
    print(f"   tube axis {TUBE_AXIS:.2f} mm past the barb tip; foot {foot_area:.1f} mm2; "
          f"print height {box.zlen:.1f} mm")


if __name__ == "__main__":
    main()
