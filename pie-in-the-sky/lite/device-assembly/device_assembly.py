"""Lite Edition device assembly — the four valve-manifold tray assemblies
packed around the reservoir-pockets box.

Coordinate frame is the reservoir's (Z+ up, X left/right, Y front/back as
depth, floor on Z=0). In the enclosure the reservoir's +X doorway faces the
back (bags load from the rear); its -X wall is the enclosure front and carries
both bag-spout exits low (y = +/-36, z ~= 12). The valve manifold therefore
sits in front of the -X face, on the same floor.

Inter-tray connections are tubing (see the topology "Tube Segments" tables),
not butted ports, so the arrangement only needs connected trays close together
with their valve/Tee branches pointing up (+Z) for the pumps, bag lines, and
nozzles. The connection graph:

    source-select --2-- bib-gate --2-- bag-circuit --(bags)--> reservoir
                          |  \\ pumps                 |
                          |   `--2-- nozzle-gate --2--'
                          `--(BiB in)        `--> nozzles

bib-gate is the hub (feeds from source-select, exchanges with bag-circuit, and
drives nozzle-gate through the two pumps); bag-circuit is the one tray tied to
the reservoir bags.

Packing: the dispense path runs back-to-front, so the three pump-circuit trays
stack as flow rows in front of the reservoir, each flat (branches up) and
rotated 90 deg so its long axis lies along Y (the reservoir's width), all
centered on Y=0:

    reservoir (back) | bag-circuit | bib-gate (+pumps) | nozzle-gate (front)
                          bags ^         ^ pumps              ^ faucet

bag-circuit hugs the -X face so it straddles both bag exits; bib-gate sits one
row forward (pumps fill the bib <-> nozzle gap); nozzle-gate is front-most so
its nozzle outlets reach the faucet at the enclosure front. source-select is
the largest tray and only touches bib-gate, so rather than widen the block it
lies along the +Y side in its native orientation (long axis along X), running
the length of the rows beside bib-gate.
"""

import sys
from pathlib import Path

import cadquery as cq

_here = Path(__file__).resolve()
_repo = next(p for p in _here.parents if (p / "hardware" / "_cadq_export.py").is_file())
_hw = _repo / "hardware"
sys.path.insert(0, str(_hw))
from _cadq_export import export_assembly

_VM = _hw / "printed-parts" / "valve-manifold"
TRAY_STEPS = {
    "source-select": _VM / "source-select-tray" / "source-select-assembly.step",
    "bag-circuit": _VM / "bag-circuit-tray" / "bag-circuit-assembly.step",
    "bib-gate": _VM / "bib-gate-tray" / "bib-gate-assembly.step",
    "nozzle-gate": _VM / "nozzle-gate-tray" / "nozzle-gate-assembly.step",
}
RES_STEP = (
    _repo
    / "pie-in-the-sky"
    / "lite"
    / "printed-parts"
    / "reservoir-pockets"
    / "reservoir-pockets.step"
)

# Distinct flat colors per tray so the arrangement reads at a glance; the
# reservoir is translucent so the manifold stays visible behind/through it.
RES_COLOR = cq.Color(0.60, 0.80, 1.00, 0.28)
COLORS = {
    "source-select": cq.Color(0.45, 0.70, 0.45),  # green
    "bag-circuit": cq.Color(0.90, 0.66, 0.32),    # amber
    "bib-gate": cq.Color(0.62, 0.47, 0.82),       # violet
    "nozzle-gate": cq.Color(0.84, 0.42, 0.42),    # red
}

# --- Packing parameters ---------------------------------------------------
GAP_RES = 12.0  # near row (+X face) to reservoir -X face: bag-line room
ROW_GAP = 10.0  # near row to far row: cross-tube + pump room
COL_GAP = 8.0   # tray to tray within a row


def _load(path):
    return cq.importers.importStep(str(path)).val()


def _rotz(shape, deg):
    return shape.rotate((0, 0, 0), (0, 0, 1), deg)


def _place(shape, *, xmax=None, xcenter=None, ycenter=None, ymin=None, zmin=None):
    """Translate so the requested bounding-box references land on targets."""
    bb = shape.BoundingBox()
    if xmax is not None:
        dx = xmax - bb.xmax
    elif xcenter is not None:
        dx = xcenter - 0.5 * (bb.xmin + bb.xmax)
    else:
        dx = 0.0
    if ycenter is not None:
        dy = ycenter - 0.5 * (bb.ymin + bb.ymax)
    elif ymin is not None:
        dy = ymin - bb.ymin
    else:
        dy = 0.0
    dz = (zmin - bb.zmin) if zmin is not None else 0.0
    return shape.translate((dx, dy, dz))


def build():
    res = _load(RES_STEP)
    front_x = res.BoundingBox().xmin  # reservoir -X (enclosure-front) face

    # Pump-circuit trays rotated +90 deg about Z: long axis (local X) -> Y, the
    # ~72 mm depth -> X, branches stay +Z (up). Flow rows march forward (-X)
    # from the reservoir, all centered on Y=0.
    bag = _place(
        _rotz(_load(TRAY_STEPS["bag-circuit"]), 90.0),
        xmax=front_x - GAP_RES, ycenter=0.0, zmin=0.0,
    )
    bib = _place(
        _rotz(_load(TRAY_STEPS["bib-gate"]), 90.0),
        xmax=bag.BoundingBox().xmin - ROW_GAP, ycenter=0.0, zmin=0.0,
    )
    noz = _place(
        _rotz(_load(TRAY_STEPS["nozzle-gate"]), 90.0),
        xmax=bib.BoundingBox().xmin - ROW_GAP, ycenter=0.0, zmin=0.0,
    )

    # source-select stays native (long axis along X) and lies along the +Y
    # side, centered over the three rows, beside bib-gate (its only neighbor).
    rows = [bag.BoundingBox(), bib.BoundingBox(), noz.BoundingBox()]
    rows_xmid = 0.5 * (min(b.xmin for b in rows) + max(b.xmax for b in rows))
    rows_ymax = max(b.ymax for b in rows)
    src = _place(
        _load(TRAY_STEPS["source-select"]),
        xcenter=rows_xmid, ymin=rows_ymax + COL_GAP, zmin=0.0,
    )

    placed = {
        "reservoir-pockets": (res, RES_COLOR),
        "bag-circuit": (bag, COLORS["bag-circuit"]),
        "bib-gate": (bib, COLORS["bib-gate"]),
        "nozzle-gate": (noz, COLORS["nozzle-gate"]),
        "source-select": (src, COLORS["source-select"]),
    }
    assy = cq.Assembly(name="lite-device-assembly")
    for name, (shape, color) in placed.items():
        assy.add(shape, name=name, color=color)
    return assy, placed


def _report(placed):
    print("  part               X range            Y range            Z range")
    xs, ys, zs = [], [], []
    for name, (shape, _c) in placed.items():
        b = shape.BoundingBox()
        xs += [b.xmin, b.xmax]
        ys += [b.ymin, b.ymax]
        zs += [b.zmin, b.zmax]
        print(
            "  %-16s [%7.1f,%7.1f]  [%7.1f,%7.1f]  [%7.1f,%7.1f]"
            % (name, b.xmin, b.xmax, b.ymin, b.ymax, b.zmin, b.zmax)
        )
    print(
        "  ENVELOPE         %.1f (X) x %.1f (Y) x %.1f (Z) mm"
        % (max(xs) - min(xs), max(ys) - min(ys), max(zs) - min(zs))
    )

    def overlap(a, b):
        ox = min(a.xmax, b.xmax) - max(a.xmin, b.xmin)
        oy = min(a.ymax, b.ymax) - max(a.ymin, b.ymin)
        oz = min(a.zmax, b.zmax) - max(a.zmin, b.zmin)
        return min(ox, oy, oz)

    names = list(placed)
    clash = False
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            o = overlap(placed[names[i]][0].BoundingBox(), placed[names[j]][0].BoundingBox())
            if o > 1e-6:
                clash = True
                print("  ** bbox overlap %s / %s by %.2f mm" % (names[i], names[j], o))
    print("  no bounding-box overlaps" if not clash else "  ** CLASHES PRESENT **")


def main():
    assy, placed = build()
    out = _here.parent / "device-assembly.step"
    export_assembly(assy, str(out))
    print("-> device-assembly.step")
    _report(placed)


if __name__ == "__main__":
    main()
