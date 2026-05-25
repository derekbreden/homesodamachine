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

    substitute_md(
        _here / "README.md",
        variables={
            "FOAM_SHELL_OUTER_HEIGHT": f"{foam_shell_outer_height:g}",
            "OUTER_SHELL_FOAM_GAP": f"{outer_shell_foam_gap:g}",
            "OUTER_SHELL_X_LENGTH": f"{outer_shell_x_length:g}",
            "OUTER_SHELL_Z_LENGTH": f"{outer_shell_z_length:g}",
            "BBOX_VOLUME": f"{volume:.6f}",
            "BBOX_X_MIN": f"{bbox.xmin:.3f}",
            "BBOX_X_MAX": f"{bbox.xmax:.3f}",
            "BBOX_Y_MIN": f"{bbox.ymin:.3f}",
            "BBOX_Y_MAX": f"{bbox.ymax:.3f}",
            "BBOX_Z_MIN": f"{bbox.zmin:.3f}",
            "BBOX_Z_MAX": f"{bbox.zmax:.3f}",
            "CENTROID_X": f"{centroid.x:.6f}",
            "CENTROID_Y": f"{centroid.y:.6f}",
            "CENTROID_Z": f"{centroid.z:.6f}",
        },
        expected_counts={
            "FOAM_SHELL_OUTER_HEIGHT": 2,
            "OUTER_SHELL_FOAM_GAP": 2,
            "OUTER_SHELL_X_LENGTH": 1,
            "OUTER_SHELL_Z_LENGTH": 1,
            "BBOX_VOLUME": 1,
            "BBOX_X_MIN": 1,
            "BBOX_X_MAX": 1,
            "BBOX_Y_MIN": 1,
            "BBOX_Y_MAX": 1,
            "BBOX_Z_MIN": 1,
            "BBOX_Z_MAX": 1,
            "CENTROID_X": 1,
            "CENTROID_Y": 1,
            "CENTROID_Z": 1,
        },
    )
    print("-> README.md")


if __name__ == "__main__":
    main()
