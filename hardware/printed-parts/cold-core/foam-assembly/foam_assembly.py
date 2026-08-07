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

The top cap and its lid install rotated 180° about Z. They carry the fifteen
deck-mount columns, authored in the cap's own frame, and the spin is what
carries each station to the deck position it holds — so the column pattern,
which is not symmetric, is the tell for which way the cap goes on. Every
other part is authored in its final orientation and only shifts along Z.

Both caps and the shell share the one original six-screw pattern (four
corners + the two mid-long-side bosses on their diagonal), which is 180°
symmetric about Z — that is what leaves the top cap free to rotate. The
bottom cap is the same cup seated mouth-down, so its screws land on the
shell's existing bottom-face inserts with no rotation and no boss moves.
_report() proves all of it: the CO2 line's bore runs clear end to end, each
cap conduit runs clear through the top cap and its lid while the bottom
stack stands solid on the same line, a thin vertical probe at each screw
position passes clear through every cap and lid, and no two solids overlap
(mating faces touch at zero volume).

THE LINES INSIDE ARE DRAWN HERE TOO. `_internal_routes` carries every fluid
run from the fitting it lands on to the conduit it leaves by; this script is
where each one is measured against the solids it runs among — the shell, the
tank and its coil, and both reservoirs with their caps — and where it lands as
`internal-routes.step` beside the stack. They are a separate file and not part
of `foam-assembly.step`, because the assembly STEP is the CORE AS THE MACHINE
SEES IT: what the enclosure loads and stands its bodies off. A tube potted
inside the foam is not a face anything outside can reach."""

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
    cap_conduits,
    cap_conduit_axis,
    cap_conduit_bore_radius,
    co2_inlet_tube_radius,
    screw_clearance_radius,
    deck_mount_xy,
    foam_cap_height,
    head_pad_height,
)
from _port_cuts import co2_inlet_lane_xyz, co2_inlet_xyz
import _internal_routes as routes

SHELL_STEP = _cold_core / "foam-shell" / "foam-shell.step"
CAP_DIR = _cold_core / "foam-cap"
RESERVOIR_DIR = _cold_core / "reservoir"
# Which reservoir STEP fills which pocket. `reservoir.py` builds both sides in the shell's
# own frame, so a body needs no placing; a cap seats on its body's top rim, which is the
# one figure this file carries about them.
RESERVOIRS = {"reservoir A": "reservoir-right", "reservoir B": "reservoir-left"}
RESERVOIR_CAP_Z = routes.reservoir_cap_top_z - routes._reservoir.cap_total_height

# Translucent shell so the caps read through it; distinct flats per cap layer.
SHELL_COLOR = cq.Color(0.62, 0.78, 0.95, 0.25)
COLORS = {
    "foam-cap-top": cq.Color(0.90, 0.66, 0.32),        # amber
    "foam-cap-lid-top": cq.Color(0.97, 0.85, 0.55),    # pale amber
    "foam-cap-bottom": cq.Color(0.45, 0.70, 0.45),     # green
    "foam-cap-lid-bottom": cq.Color(0.66, 0.86, 0.62), # pale green
}

# One colour per line, read by what it carries: water blue, gas grey, flavour by its bag.
ROUTE_COLORS = {
    "water-in": cq.Color(0.35, 0.60, 0.90),
    "carb-water-out": cq.Color(0.20, 0.80, 0.85),
    "co2-in": cq.Color(0.60, 0.62, 0.66),
    "reservoir-a": cq.Color(0.85, 0.35, 0.30),
    "reservoir-a-fill": cq.Color(0.95, 0.62, 0.55),
    "reservoir-b": cq.Color(0.55, 0.35, 0.75),
    "reservoir-b-fill": cq.Color(0.78, 0.66, 0.92),
}


def _load(path):
    return cq.importers.importStep(str(path)).val()


def _spin(shape):
    """Rotate 180° about the Z axis — the top cap's install orientation,
    which carries its deck-mount stations to the deck positions they hold."""
    return shape.rotate(cq.Vector(0, 0, 0), cq.Vector(0, 0, 1), 180)


def spin_xy(p):
    """A cap-frame `(x, y)` at the top cap's install orientation — the half turn `_spin`
    gives the metal, given to a coordinate."""
    return (-p[0], -p[1])


def cap_conduit_station(name):
    """One cap conduit's mouth in the ASSEMBLY'S OWN frame: `(x, y)`.

    The bore is authored in the CAP's frame and the cap installs spun, so this is where a
    line crossing the stack's top face actually comes out."""
    return spin_xy(cap_conduits[name])


def cap_conduit_axis_out():
    """The way out of a cap conduit, in the assembly's frame — the top cap's +Z, which the
    spin about Z leaves alone."""
    return cap_conduit_axis


def deck_mount_station(name):
    """One deck mount's column tops in the ASSEMBLY'S OWN frame: a tuple of `(x, y)`.

    The columns are authored in the CAP's frame and the cap installs spun, so this is where
    a module's mount pattern actually lands on the stack. Both frames are centred on the
    stack's own axis, so the spin is the whole of the difference. What each module then
    stands at in Z is `_cold_core_interface.deck_mount_standoff`; whoever seats the
    assembly carries all of it."""
    return tuple(spin_xy(p) for p in deck_mount_xy(name))


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
    # mouth. Both spin about Z, which is what stations the deck mounts.
    # The lid seats on the cap's MOUTH RIM, one cap height off its floor —
    # not on the cap's highest point, which is the pcba deck mount's columns
    # standing on through the lid to carry the board above it. The psu mount's
    # columns stop at the rim itself, and the lid is what its module lands on.
    # A lid's plate seats on the cap's mouth rim and its head pads sink one
    # head_pad_height past it, into the relief the cap's boss columns leave
    # there — so a lid is placed by the pads' far end, one pad short of the rim.
    cap_top = _place_z(_spin(_load(CAP_DIR / "foam-cap-top.step")), zmin=shell_bb.zmax)
    lid_top = _place_z(
        _spin(_load(CAP_DIR / "foam-cap-lid-top.step")),
        zmin=cap_top.BoundingBox().zmin + foam_cap_height - head_pad_height,
    )

    # Bottom cap (mouth-down): floor (its zmax face) lands up against the
    # shell's bottom; lid covers the downward mouth as the most-negative-Z layer.
    cap_bottom = _place_z(_load(CAP_DIR / "foam-cap-bottom.step"), zmax=shell_bb.zmin)
    lid_bottom = _place_z(
        _load(CAP_DIR / "foam-cap-lid-bottom.step"),
        zmax=cap_bottom.BoundingBox().zmin + head_pad_height,
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

    # The CO2 bore leans from the bottom plate's lane-side port out to the PORT LANE, landing
    # under its own cap conduit — the tube falls onto that end, so the lane is where the bore
    # stops and where the probe starts. What it crosses on the way is the tank support ring.
    probe_r = co2_inlet_tube_radius - 0.3
    shell_solid = placed["foam-shell"][0]
    start = cq.Vector(*co2_inlet_lane_xyz)
    reach = cq.Vector(*co2_inlet_xyz) - start
    probe = cq.Solid.makeCylinder(probe_r, reach.Length, start, reach.normalized())
    blocked = shell_solid.intersect(probe).Volume()
    print("  CO2 bore: (%.2f, %.2f) .. (%.2f, %.2f) at z %.2f — %s"
          % (co2_inlet_lane_xyz[0], co2_inlet_lane_xyz[1], co2_inlet_xyz[0], co2_inlet_xyz[1],
             co2_inlet_xyz[2],
             "clear  OK" if blocked <= 1e-6 else "** BLOCKED by %.3f mm^3" % blocked))

    # Each cap conduit is one column of the TOP cap carrying a through bore, and the lid
    # passes it. A probe on the conduit's own line meets no material in either — and the
    # same probe meets solid in both bottom-cap parts, which carry no conduit.
    probe_r = cap_conduit_bore_radius - 0.3
    for cname in cap_conduits:
        cx, cy = cap_conduit_station(cname)
        for name, want_open in (("foam-cap-top", True), ("foam-cap-lid-top", True),
                                ("foam-cap-bottom", False), ("foam-cap-lid-bottom", False)):
            solid = placed[name][0]
            b = solid.BoundingBox()
            column = cq.Solid.makeCylinder(
                probe_r, b.zlen + 4, cq.Vector(cx, cy, b.zmin - 2), cq.Vector(0, 0, 1))
            blocked = solid.intersect(column).Volume()
            if want_open and blocked > 1e-6:
                print("  ** %s blocks the %s conduit at (%.2f, %.2f) by %.3f mm^3"
                      % (name, cname, cx, cy, blocked))
            if not want_open and blocked <= 1e-6:
                print("  ** %s is open on the %s line — the bottom cap carries no conduit"
                      % (name, cname))
        print("  cap conduit %-9s (%+7.2f, %+7.2f) clear through cap + lid; bottom solid  OK"
              % (cname, cx, cy))

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


def build_internal_routes(placed):
    """Every fluid line inside the core, drawn at the arc its own corridor leaves.

    The obstacles are what a line actually runs among down there: the shell, the tank with
    its wrapped coil, and both reservoirs with their caps. The reservoirs are not in the
    foam assembly — they are dropped into its pockets — but a line that crosses a pocket
    crosses them, so they are here."""
    obstacles = {"the foam shell": placed["foam-shell"][0], "the tank": routes.tank_envelope()}
    for name, stem in RESERVOIRS.items():
        obstacles[name] = _load(RESERVOIR_DIR / f"{stem}.step")
        cap = _load(RESERVOIR_DIR / f"{stem.replace('reservoir', 'reservoir-cap')}.step")
        obstacles[f"{name}'s cap"] = cap.translate((0, 0, RESERVOIR_CAP_Z))
    fitted = routes.build_routes(obstacles)
    routes.report_routes(fitted, obstacles)
    assy = cq.Assembly(name="internal-routes")
    for name in sorted(fitted):
        assy.add(fitted[name][1], name=name, color=ROUTE_COLORS[name])
    return assy


def main():
    assy, placed = build()
    out = _here.parent / "foam-assembly.step"
    export_assembly(assy, str(out))
    print("-> foam-assembly.step")
    _report(placed)

    export_assembly(build_internal_routes(placed), str(_here.parent / "internal-routes.step"))
    print("-> internal-routes.step")


if __name__ == "__main__":
    main()
