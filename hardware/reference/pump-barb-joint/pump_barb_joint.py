"""The joint on each of the G Ganen pump's barbs ([`ledger/bom.md`](/hardware/ledger/bom.md)):

- a short piece of neoPure PVCR-0610 reinforced clear PVC, 3/8" ID × 0.594" OD, pushed over the
  barb to its root;
- a John Guest PP061208W reducer, its 3/8" stem trimmed short, pushed into the tube's other end up
  to the stem's shoulder, its tip on the barb's tip;
- two YDS butterfly clamps, 10–16 mm with a 9 mm band, each centred on the length of fitting the
  tube covers: one on the barb, one on the stem.

The reducer's 1/4" collet carries the line on. The tube is drawn installed: its bore on the barb's
scanned profile and on the stem, its outside opened to keep its section. Each band is closed on the
tube's widest outside under it.

Frame: +X = the port's outward axis, the barb's tip at X = 0, so the tube runs from the barb's root
at negative X out over the trimmed stem. Each clamp's housing stands on +Z, and its key lies flat in
the band's plane and runs along +Y or −Y.

Run:
    tools/cad-venv/bin/python hardware/reference/pump-barb-joint/pump_barb_joint.py
"""

import math
import sys
from pathlib import Path

import cadquery as cq
import numpy as np
from scipy.spatial import ConvexHull

_here = Path(__file__).resolve()
_hw = next(p for p in _here.parents if p.name == "hardware")
for _p in ("scripts", "reference/g-ganen-pump", "reference/jg-pp061208w"):
    sys.path.insert(0, str(_hw / _p))
from _cadq_export import export_assembly
from _materials import M_JG_WHITE_PP, M_POM_ORANGE, M_PVC_CLEAR, M_STAINLESS
import g_ganen_pump as pump
import jg_pp061208w as reducer

STEP = _here.parent / "pump-barb-joint.step"
PORTS = {"suction": "port_yminus", "discharge": "port_yplus"}

# --- the tube: neoPure PVCR-0610 --------------------------------------------
TUBE_ID = 9.525             # 3/8"
TUBE_OD = 15.088            # 0.594"

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
    """The barb's root, where the tube's end stands: its x, negative."""
    return barb(port)[0][0]


def tube_length(port):
    return TRIM - root(port)


def opened(r_bore):
    """The tube's outside radius with its bore opened to `r_bore`, keeping its section."""
    return math.sqrt(r_bore ** 2 + (TUBE_OD ** 2 - TUBE_ID ** 2) / 4.0)


def bore(port):
    """`(x, radius)` of the tube's bore installed: on the barb where the barb is wider than the
    tube's own bore, and on the trimmed stem past the barb's tip."""
    rows, r0 = barb(port), TUBE_ID / 2.0
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


def mouth():
    """The reducer's 1/4" collet mouth: (position, outward axis)."""
    return (reducer.LENGTH - CUT_X, 0.0, 0.0), (1.0, 0.0, 0.0)


def build_tube(port):
    """The tube, installed: turned about X from its bore and its opened outside."""
    inner = []
    for x, r in bore(port):
        if not inner or abs(x - inner[-1][0]) > 1e-6 or abs(r - inner[-1][1]) > 1e-6:
            inner.append((x, r))
    outer = [(x, opened(r)) for x, r in inner]
    return cq.Workplane("XY").polyline(outer + inner[::-1]).close().revolve(360.0, (0, 0, 0), (1, 0, 0)).val()


def build_reducer():
    """The PP061208W with its stem cut TRIM ahead of the shoulder, the cut at X = 0."""
    cut = cq.Solid.makeBox(100.0 + CUT_X, 100.0, 100.0, cq.Vector(-100.0, -50.0, -50.0))
    return reducer.build().cut(cut).moved(cq.Location(cq.Vector(-CUT_X, 0.0, 0.0)))


def build_clamp(d, xc, keys):
    """One clamp closed on `d`, its band centred on `xc`: `(steel, key)`. The housing stands on +Z,
    and the key runs from the screw's end along `keys` × Y."""
    r = d / 2.0
    x0 = cq.Vector(xc - BAND_W / 2.0, 0.0, 0.0)
    band = (cq.Solid.makeCylinder(r + BAND_T, BAND_W, x0, cq.Vector(1, 0, 0))
            .cut(cq.Solid.makeCylinder(r, BAND_W, x0, cq.Vector(1, 0, 0))))
    top = r + BAND_T + HOUSING_H
    housing = (cq.Solid.makeBox(HOUSING_W, HOUSING_L, top, cq.Vector(xc - HOUSING_W / 2.0, -HOUSING_L / 2.0, 0.0))
               .cut(cq.Solid.makeCylinder(r + BAND_T, HOUSING_W, cq.Vector(xc - HOUSING_W / 2.0, 0.0, 0.0),
                                          cq.Vector(1, 0, 0))))
    screw_z = r + BAND_T + HOUSING_H / 2.0
    end = keys * HOUSING_L / 2.0
    neck = cq.Solid.makeCylinder(NECK_D / 2.0, NECK_L, cq.Vector(xc, end, screw_z), cq.Vector(0, keys, 0))
    # The key's outline: the hull of its neck's round and its far end's round, in the band's plane.
    t = np.linspace(0.0, 2.0 * math.pi, 48, endpoint=False)
    rounds = np.concatenate([np.column_stack([c + w / 2.0 * np.cos(t), w / 2.0 * np.sin(t)])
                             for c, w in ((KEY_NECK_W / 2.0, KEY_NECK_W), (KEY_L - KEY_W / 2.0, KEY_W))])
    outline = rounds[ConvexHull(rounds).vertices]
    start = end + keys * NECK_L
    key = (cq.Workplane("YZ", origin=(xc - KEY_T / 2.0, 0.0, 0.0))
           .polyline([(start + keys * u, screw_z + v) for u, v in outline]).close().extrude(KEY_T).val())
    return band.fuse(housing, neck).clean(), key


def build(port, keys=(-1, -1)):
    """`{name: (solid, colour)}` for the joint on `port`: the tube, the reducer, and each clamp's
    steel and key. `keys` gives the side of Y each key runs to, the barb's clamp then the stem's."""
    out = {"tube": (build_tube(port), M_PVC_CLEAR), "reducer": (build_reducer(), M_JG_WHITE_PP)}
    for (name, (xc, d)), side in zip(bands(port).items(), keys):
        steel, key = build_clamp(d, xc, side)
        out[f"{name}-clamp"] = (steel, M_STAINLESS)
        out[f"{name}-key"] = (key, M_POM_ORANGE)
    return out


def main():
    for port in PORTS:
        print(f"{port}: tube {tube_length(port):.2f} mm, root at X{root(port):.2f}; "
              + "; ".join(f"{n} band at X{xc:.2f} closed on d{d:.2f}" for n, (xc, d) in bands(port).items()))
    print(f"reducer stem trimmed to {TRIM:g} mm; the 1/4\" mouth at X{mouth()[0][0]:.2f}")
    parts = build("suction")
    a = cq.Assembly(name="pump-barb-joint")
    for name, (solid, colour) in parts.items():
        print(f"  {name:12} valid {solid.isValid()}, {solid.Volume():8.1f} mm3")
        a.add(solid, name=name, color=colour)
    export_assembly(a, str(STEP))
    print(f"-> {STEP.name}")


if __name__ == "__main__":
    main()
