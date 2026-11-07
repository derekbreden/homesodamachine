"""
Under-counter plate — sheet-metal plate that sits beneath
the countertop, between the countertop's underside and the
under-counter nut/washer that clamps the entire faucet from
below.

Disc with two open-edge channels — one for the shank, one for the
umbilical's flavor-tube bundle — and a shank pocket and a pill
pocket at the channels' inner ends. At install the plate slides
laterally from below onto the dangling umbilical; each cylinder
enters through its channel mouth and seats in its terminal pocket.
Washer and nut then clamp the plate flat against the countertop.
See `../../../assembly/faucet-and-umbilical.md` for the full install
motion.

MOUNTING INTERFACE
==================
The 0.060-inch 316 stainless plate shares the printed counter stack's
centered rear row. Its shank pocket is 12.6 mm; its rear terminal pocket
is 18.15 by 7.25 mm, centered at DXF (18.925, 0). The two flavor centers
are world X = +/-5.45 mm; the drain and flat ribbon are on world X = 0.
Both open channels admit these complete sections during the sideways slide.

CHANNEL DIRECTION
=================
Both channels extend in −Y of the DXF frame from their cylinder
pockets to the rim (lateral in world — the slide-on direction):
- Shank channel: from the shank's bottom semicircle (DXF Y < 0)
  downward to the rim, matching the shank diameter in X.
- Pill channel: from the pill's bottom rectangle edge downward to
  the rim, matching the pill's short axis in X.

The shank pocket sits at X = 0 and the pill pocket sits at the
flavor-tube X offset; the two channels exit the rim at different
points on the lower arc.

CHANNEL-MOUTH FILLETS
=====================
Each of the four wall-meets-rim corners is rounded with a tangent
arc of the fillet radius.

STACK-UP (top → bottom, world-Z range in faucet-assembly coords):
- Above-counter plate (PET-GF),   Z = [-4, 0]
- Above-counter gasket (85A black), Z = [-6, -4]
- Countertop                  (varies — laminate ~32 mm, granite ~38 mm)
- Under-counter plate (this part)
- Washer + factory shank nut on the threaded shank

THICKNESS / MATERIAL
====================
0.060" (1.524 mm) 316 stainless, SendCutSend. Order qty 1 per
appliance.

UNITS
=====
Drawing is in mm with $INSUNITS = 4.
"""

import sys
from pathlib import Path

_here = Path(__file__).resolve()
_hardware_dir = next(p for p in _here.parents if p.name == "hardware")
sys.path[:0] = [str(_hardware_dir.parent / "tools"), str(_hardware_dir / "scripts")]
from _rust_data import request


def _data(**values):
    return request("faucet-data", "faucet-data", {"op": "under-counter-plate", **values})


globals().update(_data()["datums"])


def rim_y_lower(x):
    """The disc rim's lower Y at X, from the Rust outline program."""
    return _data(rim_x=x)


def channel_corner_fillet(wall_x, material_side, r=None):
    """Fillet centre, wall tangent and rim tangent from the Rust outline program."""
    return tuple(tuple(p) for p in _data(wall_x=wall_x, material_side=material_side, radius=r))


def ccw_arc(msp, center, radius, start_pt, end_pt):
    """Compatibility for a native drawing caller's modelspace."""
    arc = _data(arc={"center": center, "radius": radius, "start": start_pt, "end": end_pt})
    msp.add_arc(center, radius, start_angle=arc["start_angle"], end_angle=arc["end_angle"])
