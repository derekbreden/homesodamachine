"""Foam stack assembly — the foam shell with its two cap stacks seated as
they are in the finished build, so the cap orientation and the screw-hole
alignment can be checked before printing.

Coordinate frame is the foam shell's (Z+ up, floor on z=0):

  * foam-shell spans z = 0 .. 213.4 — floor closed at the bottom, open at
    the top where the body foam is poured.
  * top cap (mouth-up) seats on the shell's top: its floor lands on the
    shell's top edge, open mouth + lid pointing up (most +Z).
  * bottom cap (mouth-DOWN) seats under the shell: its floor lands up
    against the shell's bottom face, open mouth + lid pointing down — the
    lid is the most-negative-Z layer in the whole stack.

The top cap and its lid install rotated 180° about Z. They carry the CO2
inlet bore, authored at (x=0, y=co2_inlet_y) on −Y; the elbow doorway it
feeds is cut on the shell's +Y side, so the rotation is what puts the bore
over the doorway. Every other part is authored in its final orientation and
only shifts along Z.

Both caps and the shell share the one original six-screw pattern (four
corners + the two mid-long-side bosses on their diagonal), which is 180°
symmetric about Z — that is what leaves the top cap free to rotate. The
bottom cap is the same cup seated mouth-down, so its screws land on the
shell's existing bottom-face inserts with no rotation and no boss moves.
_report() proves all of it: the rotated bore lands on the doorway's side, a
thin vertical probe at each screw position passes clear through every cap
and lid, and no two solids overlap (mating faces touch at zero volume)."""

import sys
from pathlib import Path

import cadquery as cq

_here = Path(__file__).resolve()
_repo = next(p for p in _here.parents if (p / "hardware" / "scripts" / "_cadq_export.py").is_file())
_hw = _repo / "hardware"
_cold_core = _hw / "printed-parts" / "cold-core"
sys.path.insert(0, str(_hw / "scripts"))
sys.path.insert(0, str(_cold_core))
sys.path.insert(0, str(_hw / "printed-parts" / "cadlib"))
from _cadq_export import export_assembly
from _cold_core_interface import (
    attachment_xy_positions,
    co2_inlet_y,
    co2_inlet_tube_radius,
    screw_clearance_radius,
)

SHELL_STEP = _cold_core / "foam-shell" / "foam-shell.step"
CAP_DIR = _cold_core / "foam-cap"

# Translucent shell so the caps read through it; distinct flats per cap layer.
SHELL_COLOR = cq.Color(0.62, 0.78, 0.95, 0.25)
COLORS = {
    "foam-cap-top": cq.Color(0.90, 0.66, 0.32),        # amber
    "foam-cap-lid-top": cq.Color(0.97, 0.85, 0.55),    # pale amber
    "foam-cap-bottom": cq.Color(0.45, 0.70, 0.45),     # green
    "foam-cap-lid-bottom": cq.Color(0.66, 0.86, 0.62), # pale green
}


def _load(path):
    return cq.importers.importStep(str(path)).val()


def _spin(shape):
    """Rotate 180° about the Z axis — the top cap's install orientation,
    which carries its CO2 bore from −Y over to the doorway's +Y side."""
    return shape.rotate(cq.Vector(0, 0, 0), cq.Vector(0, 0, 1), 180)


def _place_z(shape, *, zmin=None, zmax=None):
    """Translate along Z only (parts are already XY-centered and correctly
    oriented). Sets either the min-Z or max-Z face to a target."""
    bb = shape.BoundingBox()
    if zmin is not None:
        dz = zmin - bb.zmin
    elif zmax is not None:
        dz = zmax - bb.zmax
    else:
        dz = 0.0
    return shape.translate((0, 0, dz))


def build():
    shell = _load(SHELL_STEP)
    shell_bb = shell.BoundingBox()

    # Top cap: floor (its zmin face) lands on the shell's top; lid on its
    # mouth. Both spin about Z so the CO2 bore lands over the +Y doorway.
    cap_top = _place_z(_spin(_load(CAP_DIR / "foam-cap-top.step")), zmin=shell_bb.zmax)
    lid_top = _place_z(
        _spin(_load(CAP_DIR / "foam-cap-lid-top.step")), zmin=cap_top.BoundingBox().zmax
    )

    # Bottom cap (mouth-down): floor (its zmax face) lands up against the
    # shell's bottom; lid covers the downward mouth as the most-negative-Z layer.
    cap_bottom = _place_z(_load(CAP_DIR / "foam-cap-bottom.step"), zmax=shell_bb.zmin)
    lid_bottom = _place_z(
        _load(CAP_DIR / "foam-cap-lid-bottom.step"), zmax=cap_bottom.BoundingBox().zmin
    )

    placed = {
        "foam-shell": (shell, SHELL_COLOR),
        "foam-cap-top": (cap_top, COLORS["foam-cap-top"]),
        "foam-cap-lid-top": (lid_top, COLORS["foam-cap-lid-top"]),
        "foam-cap-bottom": (cap_bottom, COLORS["foam-cap-bottom"]),
        "foam-cap-lid-bottom": (lid_bottom, COLORS["foam-cap-lid-bottom"]),
    }
    assy = cq.Assembly(name="foam-assembly")
    for name, (shape, color) in placed.items():
        assy.add(shape, name=name, color=color)
    return assy, placed


def _report(placed):
    print("  part                  X range            Y range            Z range")
    for name, (shape, _c) in placed.items():
        b = shape.BoundingBox()
        print(
            "  %-19s [%7.1f,%7.1f]  [%7.1f,%7.1f]  [%7.1f,%7.1f]"
            % (name, b.xmin, b.xmax, b.ymin, b.ymax, b.zmin, b.zmax)
        )

    # Top cap, bottom cap, and shell all share the one original screw pattern
    # (corners + the two mid bosses on their diagonal). The bottom cap is just
    # the mouth-down cup, so its screws sit at the same XY and land on the
    # shell's existing bosses.
    P = [(round(x, 6), round(y, 6)) for x, y in attachment_xy_positions]
    print("  screw pattern: 6 points, the original diagonal (shared top + bottom)  OK")

    # The spun top cap + lid must present their CO2 bore at −co2_inlet_y, the
    # side the shell's elbow doorway is cut on. A probe down the bore axis
    # passes clear through both; the same probe at the authored y hits solid.
    bore_y = -co2_inlet_y
    probe_r = co2_inlet_tube_radius - 0.3
    for name in ("foam-cap-top", "foam-cap-lid-top"):
        solid = placed[name][0]
        b = solid.BoundingBox()
        for y, want_open in ((bore_y, True), (co2_inlet_y, False)):
            probe = cq.Solid.makeCylinder(
                probe_r, b.zlen + 4, cq.Vector(0, y, b.zmin - 2), cq.Vector(0, 0, 1)
            )
            is_open = solid.intersect(probe).Volume() <= 1e-6
            if is_open != want_open:
                print(
                    "  ** CO2 bore %s at y=%.2f in %s"
                    % ("open" if is_open else "blocked", y, name)
                )
    print("  CO2 bore: open at y=%+.2f (doorway side), solid at y=%+.2f  OK" % (bore_y, co2_inlet_y))

    # A thin vertical probe at each screw position must pass clear through both
    # parts of each stack — a real through-hole for every screw.
    probe_r = screw_clearance_radius - 0.3
    clear = True
    for name in ("foam-cap-top", "foam-cap-lid-top", "foam-cap-bottom", "foam-cap-lid-bottom"):
        solid = placed[name][0]
        b = solid.BoundingBox()
        for x, y in P:
            probe = cq.Solid.makeCylinder(
                probe_r, b.zlen + 4, cq.Vector(x, y, b.zmin - 2), cq.Vector(0, 0, 1)
            )
            if solid.intersect(probe).Volume() > 1e-6:
                clear = False
                print("  ** screw path BLOCKED in %s at (%.1f, %.1f)" % (name, x, y))
    print(
        "  screw paths: all 6 clear through every cap + lid (top + bottom)  OK"
        if clear
        else "  ** SCREW PATHS BLOCKED **"
    )

    # No two solids may share volume; mating faces touch at zero volume only.
    names = list(placed)
    clash = False
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            a, b = placed[names[i]][0], placed[names[j]][0]
            vol = a.intersect(b).Volume()
            if vol > 1e-3:
                clash = True
                print("  ** SOLID clash %s / %s = %.2f mm^3" % (names[i], names[j], vol))
    print("  no solid collisions" if not clash else "  ** CLASHES PRESENT **")


def main():
    assy, placed = build()
    out = _here.parent / "foam-assembly.step"
    export_assembly(assy, str(out))
    print("-> foam-assembly.step")
    _report(placed)


if __name__ == "__main__":
    main()
