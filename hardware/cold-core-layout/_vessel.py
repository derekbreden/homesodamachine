"""The carbonator pressure vessel, in the foam shell's own frame.

A 5" OD × 0.065" wall 316 tube with a 1/4"-thick circular plate recessed into each end and
fillet-welded there, the 1/8" 316L float rod welded between the plates' blind registers, and a
TAISHER street elbow made up on each of the four tapped 1/4" NPT ports.

  Z         the shell's own. The tube's bottom sits one floor slab and one support ring up
            (`tank_bottom_z`); every figure below is struck off that.
  ±Y        the port axis. All four ports stand `vessel_port_offset` off the vessel's axis on
            it, two under the vessel and two over it.
  +X        the register azimuth — the rod, and the reed bridge on the outside of the wall.

Each plate is set one plate thickness in from its tube end, and that recess is where the
closure fillet is laid (`assembly/pressure-vessel.md`). So the interior runs
`interior_floor_z` to `interior_ceiling_z` in the tube's own frame and the vessel's outside is
the tube, end to end.

THE ELBOWS ARE PLACED BY THE STOREYS, NOT BY THEIR OWN REACH. `front_face_port_z` and
`top_band_z` are where the shell's lines cross those bands, and an elbow's corner is what has
to arrive there. `ELBOW_AXIS_OFFSET` is that standoff struck off the shell, and `main` holds
it against `_fittings.ELBOW_LEG` — the same distance read off the catalog part.
"""

from __future__ import annotations

import sys
from pathlib import Path

import cadquery as cq

_here = Path(__file__).resolve()
_hw = next(p for p in _here.parents if p.name == "hardware")
for _p in (_hw / "scripts", _hw / "printed-parts" / "cold-core",
           _hw / "printed-parts" / "cold-core" / "reed-bridge", _here.parent):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

import _fittings as F                                   # noqa: E402
from _cold_core_interface import (                      # noqa: E402
    hole_shift_from_edge,
    tank_height,
    tank_outer_radius,
    tank_support_ring_height,
    tank_top_plate_z,
    vessel_port_offset,
    wall_and_floor_thickness,
)
from _port_cuts import front_face_port_z                # noqa: E402
import _internal_routes as _R                           # noqa: E402

_cut = _hw / "cut-parts" / "carbonation" / "endcaps-circular"
sys.path.insert(0, str(_cut))
import endcap_circular_dxf as _endcap                    # noqa: E402

IN = 25.4

# --- The tube -----------------------------------------------------------------
TUBE_OD = 2 * tank_outer_radius                  # 127.0 — 5" OD
TUBE_WALL = 0.065 * IN                           # 1.651
TUBE_ID = TUBE_OD - 2 * TUBE_WALL
tank_bottom_z = wall_and_floor_thickness + tank_support_ring_height
tank_top_z = tank_top_plate_z                    # the tube's own top, `tank_height` above

# --- The plates ---------------------------------------------------------------
PLATE_D = _endcap.disc_diameter * IN             # 4.860" — tube ID less a slip fit
PLATE_T = _endcap.disc_thickness * IN            # 1/4"
PLATE_RECESS = PLATE_T                           # the closure fillet's own room
# Each plate's two faces, in the shell's frame.
bottom_plate_z = (tank_bottom_z + PLATE_RECESS, tank_bottom_z + PLATE_RECESS + PLATE_T)
top_plate_z = (tank_top_z - PLATE_RECESS - PLATE_T, tank_top_z - PLATE_RECESS)
interior_z = (bottom_plate_z[1], top_plate_z[0])

PORT_TAP_D = _endcap.hole_diameter * IN          # 7/16" tap drill for 1/4"-18 NPT

# --- The float rod ------------------------------------------------------------
ROD_D = 0.125 * IN                               # 1/8" 316L, Tandefio B0CY4DWJFQ
ROD_X = _endcap.register_radius * IN             # off the axis on +X, clear of both ports
REGISTER_DEPTH = _endcap.register_depth * IN     # blind, drilled from the inside face

# --- The elbows ---------------------------------------------------------------
# The standoff from a plate's outer face to the lateral axis its elbow turns onto, struck off
# the shell's own storeys. It reads the same at both plates.
ELBOW_AXIS_OFFSET = hole_shift_from_edge + PLATE_RECESS

# Which port carries what. `up` is the direction the male leg threads, `out` the way the
# female socket faces once the elbow is made up.
PORTS = {
    # bottom plate, under the liquid
    "co2-in":         {"y": -vessel_port_offset, "plate": "bottom"},
    "carb-water-out": {"y": +vessel_port_offset, "plate": "bottom"},
    # top plate, over it
    "water-in":       {"y": +vessel_port_offset, "plate": "top"},
    "prv":            {"y": -vessel_port_offset, "plate": "top"},
}


def port_corner(name: str) -> tuple:
    """Where one port's elbow crosses — the point its two leg axes share."""
    spec = PORTS[name]
    if spec["plate"] == "bottom":
        z = bottom_plate_z[0] - ELBOW_AXIS_OFFSET
    else:
        z = top_plate_z[1] + ELBOW_AXIS_OFFSET
    return (0.0, spec["y"], z)


def port_up(name: str) -> tuple:
    """The way that port's male leg threads — into the plate it lands on."""
    return (0.0, 0.0, 1.0) if PORTS[name]["plate"] == "bottom" else (0.0, 0.0, -1.0)


# Which line each port hands to, and which end of that line the port is. A socket is clocked
# by the run it receives, so the clocking is read off the line rather than stated here.
PORT_LINES = {
    "co2-in": ("co2-in", "end"),
    "carb-water-out": ("carb-water-out", "start"),
    "water-in": ("water-in", "start"),
}
# The PRV carries no line into the core — its relief leaves down the port lane, which is −Y.
PRV_OUT = (0.0, -1.0, 0.0)


def port_out(name: str) -> tuple:
    """The way that port's female socket faces — the direction its own line leaves on."""
    spec = PORT_LINES.get(name)
    if spec is None:
        return PRV_OUT
    line, which = spec
    pts = _R.routes[line]
    a, b = (pts[0], pts[1]) if which == "start" else (pts[-1], pts[-2])
    return tuple(cq.Vector(*b).sub(cq.Vector(*a)).normalized().toTuple())


def build_tube() -> cq.Solid:
    outer = cq.Solid.makeCylinder(TUBE_OD / 2, tank_height,
                                  cq.Vector(0, 0, tank_bottom_z), cq.Vector(0, 0, 1))
    bore = cq.Solid.makeCylinder(TUBE_ID / 2, tank_height + 2,
                                 cq.Vector(0, 0, tank_bottom_z - 1), cq.Vector(0, 0, 1))
    return outer.cut(bore)


def build_plate(which: str) -> cq.Solid:
    """One endcap plate, its two 1/4" NPT ports tapped through and its rod register blind."""
    z0, z1 = bottom_plate_z if which == "bottom" else top_plate_z
    plate = cq.Solid.makeCylinder(PLATE_D / 2, PLATE_T,
                                  cq.Vector(0, 0, z0), cq.Vector(0, 0, 1))
    for spec in PORTS.values():
        if spec["plate"] != which:
            continue
        plate = plate.cut(cq.Solid.makeCylinder(
            PORT_TAP_D / 2, PLATE_T + 2, cq.Vector(0, spec["y"], z0 - 1), cq.Vector(0, 0, 1)))
    # The register is drilled from the INSIDE face and must not pierce the plate.
    inside_z = z1 if which == "bottom" else z0
    direction = -1.0 if which == "bottom" else +1.0
    plate = plate.cut(cq.Solid.makeCylinder(
        _endcap.register_drill_diameter * IN / 2, REGISTER_DEPTH,
        cq.Vector(ROD_X, 0, inside_z), cq.Vector(0, 0, direction)))
    return plate


def build_rod() -> cq.Solid:
    """The float guide, register to register — tacked into the bottom plate, entering the
    top plate's at closure."""
    z0 = interior_z[0] - REGISTER_DEPTH
    z1 = interior_z[1] + REGISTER_DEPTH
    return cq.Solid.makeCylinder(ROD_D / 2, z1 - z0,
                                 cq.Vector(ROD_X, 0, z0), cq.Vector(0, 0, 1))


def rod_length() -> float:
    return (interior_z[1] + REGISTER_DEPTH) - (interior_z[0] - REGISTER_DEPTH)


def build_elbows() -> dict:
    """The four street elbows, name → `(solid, mouth)`.

    The male leg is `ELBOW_AXIS_OFFSET` — the plate face is where it stops."""
    return {name: F.street_elbow(corner=port_corner(name), up=port_up(name), out=port_out(name),
                                 up_leg=ELBOW_AXIS_OFFSET)
            for name in PORTS}


def bodies() -> dict:
    """Every solid the vessel is, by the name it goes into the assembly under."""
    out = {
        "carbonator-tube": build_tube(),
        "endcap-bottom": build_plate("bottom"),
        "endcap-top": build_plate("top"),
        "float-rod-carb": build_rod(),
    }
    for name, (solid, _mouth) in build_elbows().items():
        out[f"vessel-elbow-{name}"] = solid
    return out


def mouths() -> dict:
    """Each port's lateral mouth — where the next fitting or line lands."""
    return {name: mouth for name, (_solid, mouth) in build_elbows().items()}


def report() -> None:
    print("  carbonator vessel")
    print(f"    tube            ⌀{TUBE_OD:.1f} × {TUBE_WALL:.3f} wall × {tank_height:.1f}, "
          f"z {tank_bottom_z:.2f}..{tank_top_z:.2f}")
    print(f"    plates          ⌀{PLATE_D:.2f} × {PLATE_T:.2f}, bottom z "
          f"{bottom_plate_z[0]:.2f}..{bottom_plate_z[1]:.2f}, top z "
          f"{top_plate_z[0]:.2f}..{top_plate_z[1]:.2f}")
    slip = TUBE_ID - PLATE_D
    print(f"    plate-to-bore   {slip:.3f} mm slip on ⌀{TUBE_ID:.3f} bore")
    print(f"    interior        z {interior_z[0]:.2f}..{interior_z[1]:.2f} "
          f"({interior_z[1] - interior_z[0]:.1f} mm of column)")
    print(f"    float rod       ⌀{ROD_D:.3f} × {rod_length():.1f} at x {ROD_X:+.2f}")
    # The two readings of one distance: what the storeys ask an elbow to stand off, and what
    # the catalog part reaches. A gap here is a fitting that cannot put its mouth on the band.
    print(f"    elbow standoff  {ELBOW_AXIS_OFFSET:.2f} off the plate face (shell storeys) "
          f"vs {F.ELBOW_LEG:.2f} (catalog leg) — Δ{F.ELBOW_LEG - ELBOW_AXIS_OFFSET:+.2f}")
    for name in PORTS:
        c = port_corner(name)
        m = mouths()[name]
        print(f"    {name:15} corner ({c[0]:+.1f}, {c[1]:+.2f}, {c[2]:.2f})  "
              f"mouth ({m.pos[0]:+.1f}, {m.pos[1]:+.2f}, {m.pos[2]:.2f})")
    # Both bands the shell's own lines cross at, against the corners that have to meet them.
    for band, name in ((front_face_port_z, "co2-in"),
                       (tank_top_plate_z + hole_shift_from_edge, "water-in")):
        got = port_corner(name)[2]
        print(f"    band {band:7.2f}    {name} corner at {got:.2f} — "
              f"{'on it' if abs(band - got) < 1e-6 else f'OFF by {got - band:+.3f}'}")


if __name__ == "__main__":
    report()
