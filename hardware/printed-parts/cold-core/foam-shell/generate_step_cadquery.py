"""Foam shell — the PETG enclosure for the cold core's pressure
vessel + copper evaporator coil + flavor reservoir pockets. See
README.md for the design intent and the layer-by-layer geometry.
(Previously named foam-bag-shell when the reservoirs were flexible
bags; renamed to foam-shell when the design moved to printed PETG
reservoirs.)"""

import sys
from pathlib import Path

_here = Path(__file__).resolve().parent
sys.path.insert(0, str(next(p for p in _here.parents if p.name == "printed-parts") / "cadlib"))
sys.path.insert(0, str(next(p for p in _here.parents if p.name == "hardware")))
sys.path.insert(0, str(_here.parent))
sys.path.insert(0, str(next(p for p in _here.parents if (p / "tools" / "docgen").is_dir()) / "tools"))

from _cadq_export import export_step
from _foam_shell import build_full_shell
from _cold_core_interface import (
    foam_shell_outer_height,
    outer_shell_foam_gap,
    outer_shell_x_length,
    outer_shell_z_length,
)
from docgen import substitute_md


def main():
    foam_shell = build_full_shell()
    export_step(foam_shell, str(_here / "foam-shell.step"))
    print("-> foam-shell.step")

    solid = foam_shell.val()
    bbox = solid.BoundingBox()
    volume = solid.Volume()
    centroid = solid.Center()

    # Short names scoped to this README. Units live inside the value so the
    # script controls them — change a unit in source and the markdown follows.
    substitute_md(
        _here / "README.md",
        variables={
            "OUTER_H": f"{foam_shell_outer_height:g} mm",
            "OUTER_X": f"{outer_shell_x_length:g} mm",
            "OUTER_Z": f"{outer_shell_z_length:g}",  # unit implied from OUTER_X
            "OUTER_GAP": f"{outer_shell_foam_gap:g} mm",
            "VOLUME": f"{volume:.3f} mm³",
            "BBOX_X": f"{bbox.xmin:.3f} to {bbox.xmax:.3f} mm",
            "BBOX_Y": f"{bbox.ymin:.3f} to {bbox.ymax:.3f} mm",
            "BBOX_Z": f"{bbox.zmin:.3f} to {bbox.zmax:.3f} mm",
            "CENTROID": f"({centroid.x:.6f}, {centroid.y:.6f}, {centroid.z:.6f}) mm",
        },
        expected_counts={
            "OUTER_H": 2,
            "OUTER_X": 1,
            "OUTER_Z": 1,
            "OUTER_GAP": 2,
            "VOLUME": 1,
            "BBOX_X": 1,
            "BBOX_Y": 1,
            "BBOX_Z": 1,
            "CENTROID": 1,
        },
    )
    print("-> README.md")


if __name__ == "__main__":
    main()
