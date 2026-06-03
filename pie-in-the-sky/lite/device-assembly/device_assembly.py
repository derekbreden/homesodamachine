"""Lite Edition device assembly — the four valve-manifold tray assemblies
packed onto two faces of the reservoir-pockets box.

Coordinate frame is the reservoir's (Z+ up, X left/right, Y front/back as
depth, floor on Z=0). The reservoir's +X doorway faces the enclosure back
(bags load from the rear); its -X wall is the enclosure front and carries both
bag-spout exits low (y = +/-36, z ~= 12).

Two faces carry the manifold:

  * bag-circuit, bib-gate, and nozzle-gate stack in Z largest-to-smallest at
    the trays' designed 63 mm pitch, butted against the reservoir's **-X face**,
    nudged +Y so the quick-connect elbows on their -Y ports clear the
    reservoir's -Y wall.

  * source-select stands vertical against the reservoir's **+Y face** (rotated
    90 deg about X, then 90 deg about Y so its 225 mm long axis runs up Z, then
    180 deg about Z), butted in -X against the tray stack and lifted off the
    floor (the Z- face) by the same clearance the stack leaves to the -Y wall,
    so its bottom port has matching elbow room. Pushing it to the -X end frees
    the +X end of the +Y wall for connections.

The two groups sit on adjacent faces and never share one, so nothing collides.
Inter-tray links are tubing (the topology "Tube Segments" tables); all valve
and Tee branches point +Z (up) or out the open tray ends for those runs.
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
RES_DIR = _repo / "pie-in-the-sky" / "lite" / "printed-parts" / "reservoir-pockets"
RES_STEP = RES_DIR / "reservoir-pockets.step"

# Reservoir wall planes (the box faces, not the rod-end bosses) for true butting.
sys.path.insert(0, str(RES_DIR))
import reservoir_pockets as _res
RES_X_FRONT = _res.outer_x_range[0]  # -77, the -X (enclosure-front) wall
RES_Y_FRONT = _res.outer_y_range[0]  # -73, the -Y wall
RES_Y_BACK = _res.outer_y_range[1]   # +73, the +Y wall

# Distinct flat colors per tray; reservoir translucent so the manifold reads
# through it.
RES_COLOR = cq.Color(0.60, 0.80, 1.00, 0.28)
COLORS = {
    "source-select": cq.Color(0.45, 0.70, 0.45),  # green
    "bag-circuit": cq.Color(0.90, 0.66, 0.32),    # amber
    "bib-gate": cq.Color(0.62, 0.47, 0.82),       # violet
    "nozzle-gate": cq.Color(0.84, 0.42, 0.42),    # red
}

# --- Packing parameters ---------------------------------------------------
GAP = 2.0       # butting clearance to the reservoir walls
Y_SHIFT = 30.0  # +Y nudge of the -X-face stack (elbow clearance off the -Y wall)


def _load(path):
    return cq.importers.importStep(str(path)).val()


def _rot(shape, axis, deg):
    return shape.rotate((0, 0, 0), axis, deg)


def _place(shape, *, xmax=None, xmin=None, xcenter=None, ycenter=None, ymin=None, zmin=None):
    """Translate so the requested bounding-box references land on targets.
    Unset axes are left where they are."""
    bb = shape.BoundingBox()
    if xmax is not None:
        dx = xmax - bb.xmax
    elif xmin is not None:
        dx = xmin - bb.xmin
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

    # bag-circuit / bib-gate / nozzle-gate: each rotated 90 about Z (ports along
    # +/-Y), nudged +Y, butted against the -X wall, stacked in Z largest-to-
    # smallest at the trays' native 63 mm pitch.
    def stack(name, zmin):
        s = _rot(_load(TRAY_STEPS[name]), (0, 0, 1), 90.0)
        s = s.translate((0.0, Y_SHIFT, 0.0))
        return _place(s, xmax=RES_X_FRONT - GAP, zmin=zmin)

    bag = stack("bag-circuit", 0.0)
    bib = stack("bib-gate", bag.BoundingBox().zmax)
    noz = stack("nozzle-gate", bib.BoundingBox().zmax)

    # The elbow clearance the stack leaves to the -Y wall (its -Y edge minus the
    # wall plane). Reuse that exact distance as source-select's lift off the
    # floor (the Z- face) so its bottom port has matching elbow room.
    trays = (bag, bib, noz)
    elbow_clear = min(t.BoundingBox().ymin for t in trays) - RES_Y_FRONT
    stack_xmax = max(t.BoundingBox().xmax for t in trays)

    # source-select: stood vertical (90 about X, then 90 about Y), flipped 180
    # about Z, on the +Y wall, butted -X against the tray stack, lifted one
    # elbow-clearance off the floor.
    src = _load(TRAY_STEPS["source-select"])
    src = _rot(src, (1, 0, 0), 90.0)
    src = _rot(src, (0, 1, 0), 90.0)
    src = _rot(src, (0, 0, 1), 180.0)
    src = _place(src, xmin=stack_xmax, ymin=RES_Y_BACK + GAP, zmin=elbow_clear)

    placed = {
        "reservoir-pockets": (res, RES_COLOR),
        "source-select": (src, COLORS["source-select"]),
        "bag-circuit": (bag, COLORS["bag-circuit"]),
        "bib-gate": (bib, COLORS["bib-gate"]),
        "nozzle-gate": (noz, COLORS["nozzle-gate"]),
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

    def bbox_overlap(a, b):
        return min(
            min(a.xmax, b.xmax) - max(a.xmin, b.xmin),
            min(a.ymax, b.ymax) - max(a.ymin, b.ymin),
            min(a.zmax, b.zmax) - max(a.zmin, b.zmin),
        )

    # Bounding boxes overlap harmlessly where the reservoir's rod-end bosses
    # (high Z, y=+/-81) share a column with a low-Z tray, so confirm any flag
    # with a real solid intersection before calling it a clash.
    names = list(placed)
    clash = False
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            a, b = placed[names[i]][0], placed[names[j]][0]
            if bbox_overlap(a.BoundingBox(), b.BoundingBox()) <= 1e-6:
                continue
            vol = a.intersect(b).Volume()
            if vol > 1e-3:
                clash = True
                print("  ** SOLID clash %s / %s = %.2f mm^3" % (names[i], names[j], vol))
            else:
                print("  (bboxes touch %s / %s; solids clear, 0 mm^3)" % (names[i], names[j]))
    print("  no solid collisions" if not clash else "  ** CLASHES PRESENT **")


def main():
    assy, placed = build()
    out = _here.parent / "device-assembly.step"
    export_assembly(assy, str(out))
    print("-> device-assembly.step")
    _report(placed)


if __name__ == "__main__":
    main()
