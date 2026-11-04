"""Fake countertop: the bench stand that stands in for a counter. An inverted U as deep as
the bed with its legs 130 mm apart, the narrow cavity under the counter in Derek's kitchen;
one faucet through its 1-3/8" hole, the umbilical hanging and bending under it, one
thickness of 3 cm throughout: the thickness most US kitchen counters are, the quartz,
granite and quartzite standard, and what the faucet layout stands the faucet on.

The print stands on the show face: the slab lies on the bed and the legs rise from it, so
the show face takes the plate's texture and nothing needs support. The slab's edges on the
bed are sharp. Every other edge is rounded: the four outer corners, the legs' inner edges
and the feet, and the legs meet the slab on a rounded root. The print mesh is the faucet's
absolute-tolerance triangulation, so the rounds print as rounds.

Frame: X across the legs, Y along the front edge, +Z up from the bed; the show face is Z = 0.
In use the piece stands the other way up.

Run with tools/cad-venv/bin/python. No argument exports the print.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

_here = Path(__file__).resolve()
_hw = next(p for p in _here.parents if p.name == "hardware")
_repo = next(p for p in _here.parents if (p / "tools" / "docgen").is_dir())
for _path in (_hw / "scripts", _hw / "printed-parts" / "cadlib", _repo / "tools"):
    sys.path.insert(0, str(_path))

if __name__ == "__main__":
    import _rust_part
    _rust_part.start()


INCH = 25.4

# The H2C's plate, per its Bambu Studio machine profile: 330 x 320 x 325, of which the left
# nozzle, the one this job prints with, reaches X 0..325. The project stands inside that
# reach with a 5 mm border (`faucet/refresh_print_project.py`, `plate_border`).
LEFT_REACH_X = 325.0
LEFT_REACH_Y = 320.0
PLATE_BORDER = 5.0

# The counter hole the shank is sized for (`hardware/faucet-layout/faucet_assembly.py`).
COUNTER_HOLE_D = 1.375 * INCH

# Below the counter's top face: the shank ends at -50 and the umbilical stub at -80 in the
# faucet frame, whose counter top is at -6; the gather bends on a 30 mm radius under that.
UMBILICAL_BELOW_COUNTER = 80.0 - 6.0
UMBILICAL_BEND_R = 30.0
HAND_ROOM = 60.0

T = 30.0
HEIGHT = 220.0
# Between the legs: the narrow under-counter cavity of Derek's kitchen.
CAVITY = 130.0
SLAB_X = CAVITY + 2 * T
SLAB_Y = LEFT_REACH_Y - 2 * PLATE_BORDER
CORNER_R = 6.0
ROOT_R = 6.0
FOOT_R = 3.0

clear_height = HEIGHT - T
leg_inner_x = CAVITY / 2


def numbers():
    """The authored stock, rounds, counter hole and existing clearance checks."""
    from _materials import M_PETGF_BLACK, linear
    return {
        "slab_x": SLAB_X, "slab_y": SLAB_Y, "cavity": CAVITY,
        "thickness": T, "height": HEIGHT,
        "corner_radius": CORNER_R, "root_radius": ROOT_R, "foot_radius": FOOT_R,
        "hole_diameter": COUNTER_HOLE_D, "reach_x": LEFT_REACH_X, "reach_y": LEFT_REACH_Y,
        "umbilical_below": UMBILICAL_BELOW_COUNTER, "bend_radius": UMBILICAL_BEND_R,
        "hand_room": HAND_ROOM, "color": list(linear(M_PETGF_BLACK)),
    }


def _document(volume, output=None):
    from docgen import substitute_md
    out = Path(output) if output is not None else _here.parent
    substitute_md(out / "README.md", variables={
        "FCT_SLAB": f"{SLAB_X:g} × {SLAB_Y:g} mm",
        "FCT_CAVITY": f"{CAVITY:g} mm",
        "FCT_T": f"{T:g} mm",
        "FCT_HEIGHT": f"{HEIGHT:g} mm",
        "FCT_CLEAR": f"{clear_height:g} mm",
        "FCT_HOLE": f"{COUNTER_HOLE_D:.2f} mm",
        "FCT_CORNER_R": f"{CORNER_R:g} mm",
        "FCT_ROOT_R": f"{ROOT_R:g} mm",
        "FCT_FOOT_R": f"{FOOT_R:g} mm",
        "FCT_UMBILICAL": f"{UMBILICAL_BELOW_COUNTER + UMBILICAL_BEND_R:g} mm",
        "FCT_VOLUME": f"{volume / 1000:.0f} cm³",
    })


def main(output=None):
    """Write the current bench fixture with the Rust generator."""
    import _rust_part
    import trimesh
    from flute_skin import non_manifold_edges
    out = Path(output) if output is not None else _here.parent
    out.mkdir(parents=True, exist_ok=True)
    said = _rust_part.cut("tooling", "fake-countertop", numbers(), out)
    written = trimesh.load_mesh(out / "fake-countertop.stl")
    loose = non_manifold_edges(written)
    if loose or not written.is_watertight or not written.is_winding_consistent or len(written.split()) != 1:
        raise ValueError(f"fake-countertop.stl: expected one closed, consistently wound printable body; {loose} non-manifold edges")
    body = said["bodies"][0]
    print(json.dumps({
        "status": "CAD checks passed; the print is untested",
        "envelope_mm": [round(b-a, 2) for a, b in zip(body["min"], body["max"])],
        "clear_under_slab_mm": clear_height,
        "volume_cm3": round(body["volume"] / 1000, 1),
    }, indent=2))
    print(f"-> fake-countertop.step, fake-countertop.stl: {body['volume'] / 1000:.1f} cm³, {len(written.faces)} facets")
    _document(body["volume"], out)


if __name__ == "__main__":
    if sys.argv[1:]:
        sys.exit("usage: fake_countertop.py")
    main()
