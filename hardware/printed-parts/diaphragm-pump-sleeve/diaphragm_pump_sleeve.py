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
import argparse
import json
import math
import sys

HERE = Path(__file__).resolve().parent
HARDWARE = HERE.parents[1]
sys.path.insert(0, str(HARDWARE / "scripts"))

if __name__ == "__main__":
    import _rust_part
    _rust_part.start()

PORTS = {"suction": "port_yminus", "discharge": "port_yplus"}

# Siraya Tech Flex TPU 85A Clear, the stock the pump dock's wet TPU parts print in.
_COLOR_SRGB = (.92, .92, .90, .60)


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
    parameters = HARDWARE / "reference/g-ganen-pump/reference-parameters.json"
    profile = json.loads(parameters.read_text())["ports"][PORTS[port]]["profile"]
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


def tube_port():
    """Where the tube enters, in the elbow's own frame: `(position, outward axis)`."""
    return (TUBE_AXIS, TUBE_MOUTH, 0.0), (0.0, 1.0, 0.0)


def tube_mouth(tip, axis, toward):
    """Where the tube enters a seated elbow: `(position, outward axis)`."""
    length = math.sqrt(sum(v * v for v in axis))
    x = tuple(v / length for v in axis)
    dot = sum(a * b for a, b in zip(toward, x))
    across = tuple(a - b * dot for a, b in zip(toward, x))
    length = math.sqrt(sum(v * v for v in across))
    y = tuple(v / length for v in across)
    p = tuple(o + a * TUBE_AXIS + b * TUBE_MOUTH for o, a, b in zip(tip, x, y))
    return p, y


def numbers():
    """The relaxed elbow's dimensions and analytic print pose."""
    from _occt_color import rgba
    s = 1 / math.sqrt(2)
    xmin = (-BARB_DEPTH - BARB_OD / 2) * s
    xmax = (TUBE_AXIS + TUBE_OD / 2 + TUBE_MOUTH) * s
    return {
        "barb_radius": BARB_OD / 2, "barb_bore": BARB_BORE / 2,
        "barb_depth": BARB_DEPTH, "tube_radius": TUBE_OD / 2,
        "tube_bore": TUBE_BORE / 2, "tube_stop": TUBE_STOP,
        "tube_mouth": TUBE_MOUTH, "tube_axis": TUBE_AXIS,
        "neck_length": NECK, "passage_radius": PASSAGE / 2,
        "entry": ENTRY, "entry_height": ENTRY_HEIGHT,
        "foot": FOOT, "foot_span": 4 * (BARB_DEPTH + TUBE_MOUTH),
        "print_s": s, "print_shift": [-(xmin + xmax) / 2, 0.0, FOOT],
        "color": list(rgba(_COLOR_SRGB, {})[:3]),
    }


def _integral(f, a, b, tolerance=1e-7):
    """Adaptive Simpson integral for the elbow's scalar area and volume facts."""
    def panel(a, b, fa, fm, fb):
        return (b - a) * (fa + 4 * fm + fb) / 6

    def refine(a, b, fa, fm, fb, whole, epsilon, depth):
        mid = (a + b) / 2
        left, right = f((a + mid) / 2), f((mid + b) / 2)
        first = panel(a, mid, fa, left, fm)
        second = panel(mid, b, fm, right, fb)
        change = first + second - whole
        if depth == 0 or abs(change) <= 15 * epsilon:
            return first + second + change / 15
        return (refine(a, mid, fa, left, fm, first, epsilon / 2, depth - 1)
                + refine(mid, b, fm, right, fb, second, epsilon / 2, depth - 1))

    fa, fm, fb = f(a), f((a + b) / 2), f(b)
    return refine(a, b, fa, fm, fb, panel(a, b, fa, fm, fb), tolerance, 20)


def _neck_radius(y):
    t = min(1.0, max(0.0, y / NECK))
    blend = t**3 * (10.0 + t * (-15.0 + 6.0 * t))
    return BARB_OD / 2 + (TUBE_OD - BARB_OD) / 2 * blend


def _foot_neck_end():
    c = math.sqrt(2) * FOOT - TUBE_AXIS
    lo, hi = 0.0, NECK
    for _ in range(48):
        mid = (lo + hi) / 2
        radius = max(_neck_radius(mid), math.sqrt(max(0.0, (BARB_OD / 2)**2 - mid * mid)))
        if radius > mid + c:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def foot_area():
    """The foot's smooth surface area, independent of mesh chords."""
    r = BARB_OD / 2
    c = math.sqrt(2) * FOOT - TUBE_AXIS

    def negative(theta):
        y, q = r * math.sin(theta), r * math.cos(theta)
        u = y + c
        half_width = q if u < 0 else math.sqrt(max(0.0, q * q - u * u))
        return 2 * math.sqrt(2) * half_width * q

    def positive(y):
        radius2 = max(_neck_radius(y)**2, r * r - y * y)
        return 2 * math.sqrt(2) * math.sqrt(max(0.0, radius2 - (y + c)**2))

    return (_integral(negative, -math.pi / 2, 0.0)
            + _integral(positive, 0.0, _foot_neck_end()))


def volume():
    """The smooth solid volume: unioned round legs/neck, foot and intersecting bores."""
    rb, rt = BARB_OD / 2, TUBE_OD / 2

    def positive_section(theta):
        y, q = rb * math.sin(theta), rb * math.cos(theta)
        r = _neck_radius(y)
        if q >= r:
            return (2 * q * (TUBE_AXIS + BARB_DEPTH) + math.pi * q * q / 2) * q
        section = (2 * q * (TUBE_AXIS + BARB_DEPTH) + math.pi * r * r
                   - q * math.sqrt(max(0.0, r * r - q * q))
                   - r * r * math.asin(max(-1.0, min(1.0, q / r))))
        return section * q

    outer = (math.pi * rb * rb * (TUBE_AXIS + BARB_DEPTH) / 2
             + math.pi * rb**3 / 3 + _integral(positive_section, 0.0, math.pi / 2)
             + math.pi * rt * rt * (TUBE_MOUTH - rb))
    c = math.sqrt(2) * FOOT - TUBE_AXIS

    def cap(r, u):
        if u >= r:
            return 0.0
        return r * r * math.acos(max(-1.0, min(1.0, u / r))) - u * math.sqrt(max(0.0, r * r - u * u))

    def foot_negative(theta):
        y, q = rb * math.sin(theta), rb * math.cos(theta)
        u = y + c
        area = math.pi * q * q / 2 - 2 * q * u if u < 0 else cap(q, u)
        return area * q

    outer -= _integral(foot_negative, -math.pi / 2, 0.0)
    outer -= _integral(lambda y: cap(max(_neck_radius(y), math.sqrt(max(
        0.0, rb * rb - y * y))), y + c), 0.0, _foot_neck_end())
    bore_b, bore_t, passage = BARB_BORE / 2, TUBE_BORE / 2, PASSAGE / 2
    cavity = (math.pi * (bore_b**2 * BARB_DEPTH + bore_t**2 * TUBE_DEPTH
                         + passage**2 * (TUBE_AXIS + TUBE_STOP))
              - 4 * passage**3 / 3
              + math.pi * ENTRY_HEIGHT * (ENTRY * (bore_b + bore_t) + 2 * ENTRY**2 / 3))
    return outer - cavity


def _document(solid_volume, foot, height):
    sys.path.insert(0, str(HARDWARE.parent / "tools"))
    from docgen import substitute_md
    valley = min(min(d for x, d in barb_rows(port) if 2.0 <= x <= BARB_DEPTH - 2.0)
                 for port in PORTS)
    substitute_md(HERE / "README.md", variables={
        "BARB_BORE": f"{BARB_BORE:.2f}", "BARB_DEPTH": f"{BARB_DEPTH:g}",
        "TUBE_BORE": f"{TUBE_BORE:.2f}", "TUBE_DEPTH": f"{TUBE_DEPTH:g}",
        "PASSAGE": f"{PASSAGE:.2f}", "TUBE_STOP": f"{TUBE_STOP:.1f}",
        "BARB_OD": f"{BARB_OD:g}", "TUBE_OD": f"{TUBE_OD:g}",
        "MIN_WALL": f"{MIN_WALL:.2f}", "NECK": f"{NECK:g}",
        "INTERFERENCE": f"{TUBE_D - TUBE_BORE:.2f}", "CLAMP_BAND": f"{CLAMP_BAND:g}",
        "TUBE_AXIS": f"{TUBE_AXIS:.2f}", "TUBE_MOUTH": f"{TUBE_MOUTH:.1f}",
        "BAND_AIR": f"{BAND_AIR:g}", "FOOT_AREA": f"{foot:.1f}",
        "PRINT_HEIGHT": f"{height:.1f}",
        "CREST": f"{crest():.2f}", "VALLEY": f"{valley:.2f}", "ROOT": f"{root():.2f}",
        "CREST_STRETCH": f"{(crest() / BARB_BORE - 1) * 100:.0f}",
        "BARB_OD_INSTALLED": f"{BARB_OD_INSTALLED:.2f}",
        "TUBE_OD_INSTALLED": f"{TUBE_OD_INSTALLED:.2f}",
        "VOLUME": f"{solid_volume / 1000:.3f}",
    })


def main(output=None):
    import _rust_part
    out = Path(output) if output is not None else HERE
    out.mkdir(parents=True, exist_ok=True)
    _rust_part.cut("tooling", "diaphragm-pump-sleeve", numbers(), out)
    solid_volume, foot = volume(), foot_area()
    s = 1 / math.sqrt(2)
    height = FOOT + max(BARB_DEPTH + BARB_OD / 2,
                        TUBE_MOUTH - TUBE_AXIS + TUBE_OD / 2) * s
    _document(solid_volume, foot, height)
    print(f"-> diaphragm-pump-sleeve.step, diaphragm-pump-sleeve.stl, "
          f"diaphragm-pump-sleeve.step.mesh; {solid_volume / 1000:.3f} cm3")
    print(f"   tube axis {TUBE_AXIS:.2f} mm past the barb tip; foot {foot:.1f} mm2; "
          f"print height {height:.1f} mm")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    options = parser.parse_args()
    main(options.output)
