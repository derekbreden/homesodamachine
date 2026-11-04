"""The joint on each of the G Ganen pump's barbs ([`ledger/bom.md`](/hardware/ledger/bom.md)):

- a short piece of neoPure PVCR-0610 reinforced clear PVC, 3/8" ID × 0.594" OD, pushed over the
  barb to its casing-clear end plane;
- a John Guest PP061208W reducer, its 3/8" stem trimmed short, pushed into the tube's other end up
  to the stem's shoulder, its tip on the barb's tip;
- two YDS butterfly clamps, 10–16 mm with a 9 mm band, each centred on the length of fitting the
  tube covers: one on the barb, one on the stem.

The reducer's 1/4" collet carries the line on. The tube is drawn installed: its bore on the barb's
scanned profile and on the stem, its outside opened to keep its section. Each band is closed on the
tube's widest outside under it.

A joint can bend down: the reducer and the clamp on its stem turn about the lowest point of the
barb's tip, where the stem's tip bears on it, and the barb and its clamp stay as they are. The tube
runs straight on each and creases on the plane halfway between them.

Frame: +X = the port's outward axis, the barb's tip at X = 0, so the tube runs from its casing-clear
end at negative X out over the trimmed stem. Each clamp's housing stands on +Z, and its key lies flat in
the band's plane and runs along +Y or −Y. Down is −Z.

Numeric profiles and port frames describe the installed joint for Rust consumers.
"""

import math
import sys
from pathlib import Path

import numpy as np

_here = Path(__file__).resolve()
_hw = next(p for p in _here.parents if p.name == "hardware")
for _p in ("scripts", "reference/g-ganen-pump", "reference/jg-pp061208w"):
    sys.path.insert(0, str(_hw / _p))
import g_ganen_pump as pump
import jg_pp061208w as reducer

STEP = _here.parent / "pump-barb-joint.step"
PORTS = {"suction": "port_yminus", "discharge": "port_yplus"}

# --- the tube: neoPure PVCR-0610 --------------------------------------------
TUBE_ID = 9.525             # 3/8"
TUBE_OD = 15.088            # 0.594"
# The separately fitted molded head extends 0.668/0.710 mm beyond the first
# scanned barb station inside the tube's occupied radius. This end setback
# retains at least 0.15 mm to that shoulder and the complete 9 mm clamp band.
TUBE_ROOT_SETBACK = 0.9

# --- the reducer: the PP061208W, its stem cut short --------------------------
# The stem left ahead of the shoulder. SEEDED from Derek's photograph of the trimmed reducer,
# against its 17.3 mm mouth collar; NOT MEASURED.
TRIM = 10.0
CUT_X = reducer.STEM_LENGTH - TRIM      # where the reducer's own frame is cut

# --- the clamp: YDS butterfly SS W2, 10–16 mm --------------------------------
RANGE = (10.0, 16.0)        # the diameters it closes between
BAND_W = 9.0                # the listing's band width
BAND_T = 0.6
# SEEDED from Derek's photograph against the 9 mm band, NOT RATIFIED — measure a clamp in hand
# before anything is spaced to these.
HOUSING_L = 13.0            # along the band, the way the screw runs
HOUSING_W = 10.0            # across the band
HOUSING_H = 7.0             # off the band's outer face
NECK_D, NECK_L = 6.0, 3.0   # the screw's end, between the housing and the key
KEY_L = 27.0                # the key, from the neck to its round end
KEY_NECK_W, KEY_W = 8.0, 26.0
KEY_T = 5.0


def barb(port):
    """`(x, radius)` along the scanned barb, root to tip."""
    rows = pump.port_profile(PORTS[port])["profile"]
    return sorted((row["distance_from_tip_mm"], row["radius_mm"]) for row in rows)


def root(port):
    """The square-cut tube end, clear of the molded head/root: x, negative."""
    return barb(port)[0][0] + TUBE_ROOT_SETBACK


def tube_length(port):
    return TRIM - root(port)


def opened(r_bore):
    """The tube's outside radius with its bore opened to `r_bore`, keeping its section."""
    return math.sqrt(r_bore ** 2 + (TUBE_OD ** 2 - TUBE_ID ** 2) / 4.0)


def bore(port):
    """`(x, radius)` of the tube's bore installed: on the barb where the barb is wider than the
    tube's own bore, and on the trimmed stem past the barb's tip."""
    rows, r0 = barb(port), TUBE_ID / 2.0
    start = root(port)
    xs, radii = zip(*rows)
    rows = [(start, float(np.interp(start, xs, radii))),
            *((x, r) for x, r in rows if x > start)]
    out = []
    for (x0, a), (x1, b) in zip(rows, rows[1:]):
        out.append((x0, max(a, r0)))
        if (a - r0) * (b - r0) < 0:
            out.append((x0 + (r0 - a) / (b - a) * (x1 - x0), r0))
    out.append((0.0, max(rows[-1][1], r0)))
    stem = reducer.STEM_D / 2.0
    return out + [(0.0, stem), (TRIM, stem)]


def band_d(port, xc):
    """The diameter a band centred on `xc` closes on: the tube's widest outside under it."""
    xs, rs = zip(*bore(port))
    under = np.linspace(xc - BAND_W / 2.0, xc + BAND_W / 2.0, 181)
    return 2.0 * opened(float(np.interp(under, xs, rs).max()))


def bands(port):
    """`{clamp: (centre x, band diameter)}`: each band centred on the fitting the tube covers."""
    centres = {"barb": root(port) / 2.0, "stem": TRIM / 2.0}
    return {n: (xc, band_d(port, xc)) for n, xc in centres.items()}


def pivot(port):
    """Where the stem's tip bears on the barb's tip as the joint bends down: the tip's lowest point."""
    return (0.0, 0.0, -barb(port)[-1][1])


def mouth(port, bend=0.0):
    """The reducer's 1/4" collet mouth: (position, outward axis)."""
    b = math.radians(bend)
    c, s = math.cos(b), math.sin(b)
    x, pivot_z = reducer.LENGTH - CUT_X, pivot(port)[2]
    return ((x * c - pivot_z * s, 0.0, -x * s + pivot_z * (1.0 - c)),
            (c, 0.0, -s))
