"""
Carbonator tube — the 3D solid of the cut stock, for the welding fixture and for quotes.

The pressure vessel's barrel: 5" OD × 0.065" wall 316 stainless, cut square to
length. This is purchased tube (OnlineMetals #12498) cut to size and deburred,
not a fabricated part — there is no cut file and no drawing, because a saw and a
length are the whole of it. The solid exists so the tube is a model the viewer
can open on its own, the same as the end caps that close it.

Every dimension is read off `_carbonator`, which is where the assembly builds
this same barrel. Nothing here is a second copy of a number.

The tube stands on the origin, ends square, as it lies on the saw — not at the
z it occupies inside the shell. Its assembly placement is the cold core's to
state.

Units: millimetres.
"""

import sys
from pathlib import Path

import cadquery as cq

_here = Path(__file__).resolve()
_hw = next(p for p in _here.parents if p.name == "hardware")
for _p in (_hw / "scripts", _hw / "cold-core-layout"):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

from _cadq_export import export_assembly          # noqa: E402
from _material_base import M_STAINLESS, one_body  # noqa: E402
import _carbonator as _carb                       # noqa: E402

# The barrel, as the assembly builds it.
tube_od = _carb.TUBE_OD          # 127.0 mm — 5" OD
tube_id = _carb.TUBE_ID          # bore, OD less two walls
tube_wall = _carb.TUBE_WALL      # 1.651 mm — 0.065"
tube_length = _carb.carbonator_height

out_dir = _here.parent
out_name = "carbonator-tube"


def build_tube() -> cq.Workplane:
    """The barrel as cut: bore straight through, both ends square on the origin."""
    outer = cq.Workplane("XY").circle(tube_od / 2.0).extrude(tube_length)
    # The bore tool over-runs both ends so the boolean leaves no zero-thickness face.
    bore = (
        cq.Workplane("XY")
        .workplane(offset=-0.5)
        .circle(tube_id / 2.0)
        .extrude(tube_length + 1.0)
    )
    return outer.cut(bore)


def main() -> None:
    path = out_dir / f"{out_name}.step"
    export_assembly(one_body(build_tube(), path.stem, M_STAINLESS), str(path))

    print(f"Exported: {path}")
    print(f"  Tube:   Ø{tube_od:.3f} OD × {tube_wall:.3f} wall × {tube_length:.1f} long, 316 SS")
    print(f"  Bore:   Ø{tube_id:.3f}")


if __name__ == "__main__":
    main()
