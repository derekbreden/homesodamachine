"""Lite power tray — the AC + PSU block of the Lite electronics shelf.

Mounts the Mean Well IRM-90-12ST PSU and the three Wago 221-413 AC distribution
connectors (H / N / G), plus a ground-bus tie point. **No relay** — the Lite has
no compressor and no SeaFlo diaphragm pump, so there is no 120 VAC load to
switch. It is the Kitchen power tray minus the relay, re-packed tight.

- **PSU** screws down into four **heat-set M3 insert bosses** (ruthex), the same
  insert + SHCS idiom as the rest of the shelf. The PSU sits on four low bosses
  (just tall enough to seat an insert — no clearance standoff).
- **The three Wagos** drop butt-end-first into **angled slots**: each lug tilts
  45° up toward its wire end, and the blank butt end press-fits into a slot that
  wraps it on five faces (both X, both Z, and the −Y end), open toward the wire
  end so the lug sticks halfway out for wiring.
- **Ground bus** — a heat-set boss for the ground-stud SHCS; the bus is the
  bolted ring-terminal stack (hardware/reference/ground-ring-stack/).

The PSU is turned 90° (its 109 mm length runs along X) for a wide/shallow
footprint; the Wago column packs flush to its right and the ground ring-stack
sits above the PSU. The components pack **flush** (no inter-part gaps), and the
floor is the single convex outline of every footprint. The build is
parameterised by a ``Layout`` (component centres + Z rotations). GFCI is tabled;
the C14 inlet lives on the back panel. Local frame: X right, Y deep, Z up;
origin at the floor's bottom-left corner, Z = 0 the floor underside, floor top at
``floor_t``.

The geometry engine (floor/boss/slot helpers, the constants, the ``Layout``) is
reused from the Kitchen [power tray](/hardware/printed-parts/electronics/power-tray/power_tray.py);
this module only drops the relay from the layout and the floor.
"""

import importlib.util
import sys
from pathlib import Path

import cadquery as cq

_here = Path(__file__).resolve()
_repo = next(p for p in _here.parents if (p / "hardware" / "scripts" / "_cadq_export.py").is_file())
_hw = _repo / "hardware"
for _p in (
    _hw / "scripts",
    _hw / "reference" / "meanwell-irm90",
    _hw / "reference" / "wago-221-413",
):
    sys.path.insert(0, str(_p))
from _cadq_export import export_step
import meanwell_irm90 as psu
import wago_221_413 as wago


def _load_kitchen_engine():
    """Load the Kitchen power_tray under a distinct module name. Loading by file
    path (not ``import power_tray``) avoids the name collision with this Lite
    module — both files are named ``power_tray.py``."""
    src = _hw / "printed-parts" / "electronics" / "power-tray" / "power_tray.py"
    sys.path.insert(0, str(src.parent))   # so the Kitchen module finds its own deps
    spec = importlib.util.spec_from_file_location("kitchen_power_tray", src)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


k = _load_kitchen_engine()          # the Kitchen engine

# Reuse the Kitchen constants verbatim — same floor, same bosses, same slots.
floor_t = k.floor_t
margin = k.margin
wago_tilt = k.wago_tilt
psu_boss_d = k.psu_boss_d
psu_boss_h = k.psu_boss_h
insert_depth = k.insert_depth
wago_slot_half = k.wago_slot_half
wago_pitch = k.wago_pitch
gnd_boss_d = k.gnd_boss_d
gnd_boss_h = k.gnd_boss_h
gnd_insert_depth = k.gnd_insert_depth
gnd_foot = k.gnd_foot

# Reuse the Kitchen Layout dataclass; the Lite simply leaves the relay fields
# unused (the relay is never placed, so its centre/rotation are inert).
Layout = k.Layout


def _build_floor(L):
    """A single solid floor: the convex outline of the PSU, the ground footprint,
    and every Wago slot — **no relay footprint**. Extruded at plate thickness."""
    pts = []
    pts += k._rect_corners(L.psu_c[0], L.psu_c[1], psu.width, psu.length, L.psu_rot)
    pts += k._rect_corners(L.gnd_c[0], L.gnd_c[1], gnd_foot, gnd_foot, 0.0)
    for cx, by in L.wago_places:
        bb = k._wago_slot(cx, by).val().BoundingBox()
        pts += [(bb.xmin, bb.ymin), (bb.xmax, bb.ymin),
                (bb.xmax, bb.ymax), (bb.xmin, bb.ymax)]
    return cq.Workplane("XY").polyline(k._convex_hull(pts)).close().extrude(floor_t)


def build_tray(L):
    """Build the Lite tray for a given Layout: PSU bosses + Wago slots + ground
    boss on the convex floor. No relay boss, no relay footprint."""
    tray = _build_floor(L)
    for px, py in k._hole_posts(L.psu_c[0], L.psu_c[1], psu.hole_dx, psu.hole_dy, L.psu_rot):
        tray = tray.union(k._insert_boss(px, py, psu_boss_d, psu_boss_h, insert_depth))
    for cx, by in L.wago_places:
        tray = tray.union(k._wago_slot(cx, by))
    tray = tray.union(k._insert_boss(L.gnd_c[0], L.gnd_c[1], gnd_boss_d, gnd_boss_h, gnd_insert_depth))
    return tray


# --- Layout ---------------------------------------------------------------
# PSU turned 90° (109 mm length along X) at the lower-left; the Wago column packs
# flush to its right (no relay gap); the ground ring-stack sits in the open space
# above the PSU. Re-packed tight now that the relay is gone.
_psu_c = (margin + psu.length / 2.0, margin + psu.width / 2.0)
_wago_cx = margin + psu.length + wago_slot_half
LAYOUT = Layout(
    psu_c=_psu_c, psu_rot=90.0,
    relay_c=(0.0, 0.0), relay_rot=0.0,           # unused — the Lite has no relay
    wago_places=tuple((_wago_cx, margin + 8.454 + i * wago_pitch) for i in range(3)),
    gnd_c=(margin + 22.0, margin + psu.width + 11.0),
)


def build_power_tray():
    return build_tray(LAYOUT)


def main():
    export_step(build_power_tray(), str(_here.parent / "power-tray.step"))
    print("-> power-tray.step")


if __name__ == "__main__":
    main()
