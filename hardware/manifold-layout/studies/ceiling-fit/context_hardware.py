"""Native wall context and straight PCB standoffs for the ceiling-fit study.

The assembly frame and supplied current PCB mounting-hole locations are used
directly. These solids are isolated study geometry; no production geometry,
mounts or enclosure generator is imported.

    PYTHONPATH=. tmp/takeover/cadq "ceiling fit wall context" -- \
      tools/cad-venv/bin/python \
      hardware/manifold-layout/studies/ceiling-fit/context_hardware.py

build() returns a dictionary of CadQuery solids. export(output_dir) writes each
as native STEP, an NPZ mesh with v/f arrays, and a JSON geometry report. The
default output directory is parts/ beside this file.
"""

import argparse
import json
import math
from pathlib import Path

import cadquery as cq
import numpy as np


HERE = Path(__file__).resolve().parent
Y_BOUNDS = (244.0, 471.3)
Z_BOUNDS = (253.4, 346.0)
WALLS = {
    "right-wall": {"x": (98.5, 107.5), "y": Y_BOUNDS, "z": Z_BOUNDS},
    "back-wall": {"x": (-98.5, 98.5), "y": (462.3, 471.3), "z": Z_BOUNDS},
    "left-wall": {"x": (-107.5, -98.5), "y": Y_BOUNDS, "z": Z_BOUNDS},
}
PCB_Y = (361.3160675048828, 439.3160675048828)
PCB_Z = (259.9000061035156, 326.2000061035156)
PCB_MATING_X = 90.25
BOSS_OD = 10.0
BOSS_LENGTH = 98.5 - PCB_MATING_X
PILOT_OD = 4.0
PILOT_DEPTH = 6.0
BACK_HOLE_X = 37.2499988712316
BACK_HOLE_Z = 334.3760478805363
BACK_HOLE_OD = 17.44


def _wall(bounds):
    dimensions = [bounds[axis][1] - bounds[axis][0] for axis in "xyz"]
    return cq.Solid.makeBox(*dimensions, cq.Vector(*(bounds[axis][0] for axis in "xyz")))


def mounting_centers():
    """Four explicit PCB contact points, at the board underside plane."""
    return [(PCB_MATING_X, y, z) for y in PCB_Y for z in PCB_Z]


def build():
    """Return {part_name: native CQ Solid} for the three separate wall parts."""
    right = _wall(WALLS["right-wall"])
    for x, y, z in mounting_centers():
        boss = cq.Solid.makeCylinder(BOSS_OD/2, BOSS_LENGTH,
                                     cq.Vector(x, y, z), cq.Vector(1, 0, 0))
        right = right.fuse(boss)
    for x, y, z in mounting_centers():
        pilot = cq.Solid.makeCylinder(PILOT_OD/2, PILOT_DEPTH + .01,
                                      cq.Vector(x-.01, y, z), cq.Vector(1, 0, 0))
        right = right.cut(pilot)
    back = _wall(WALLS["back-wall"])
    y0, y1 = WALLS["back-wall"]["y"]
    through = cq.Solid.makeCylinder(BACK_HOLE_OD/2, y1-y0+.02,
                                    cq.Vector(BACK_HOLE_X, y0-.01, BACK_HOLE_Z),
                                    cq.Vector(0, 1, 0))
    return {"right-wall": right.clean(),
            "back-wall": back.cut(through).clean(),
            "left-wall": _wall(WALLS["left-wall"])}


def report(name, shape):
    """Describe the requested wall envelope and actual native solid."""
    bounds = WALLS[name]
    dimensions = {axis: bounds[axis][1]-bounds[axis][0] for axis in "xyz"}
    bb = shape.BoundingBox()
    result = {"part": name, "units": "mm", "valid": bool(shape.isValid()),
              "solid_count": len(shape.Solids()), "volume_mm3": shape.Volume(),
              "wall_bounds_mm": {axis: list(bounds[axis]) for axis in "xyz"},
              "wall_dimensions_mm": dimensions,
              "bounds_mm": {"x": [bb.xmin, bb.xmax], "y": [bb.ymin, bb.ymax],
                            "z": [bb.zmin, bb.zmax]}}
    expected_volume = math.prod(dimensions.values())
    if name == "right-wall":
        result["pcb_standoffs"] = {
            "source": "Current PCBA_TURN and MH1-MH4 hole rectangle, 78 by 66.3 mm; PCB raised 3 mm above cap",
            "centers_at_pcb_underside_mm": [list(point) for point in mounting_centers()],
            "axis_toward_wall": [1, 0, 0], "outer_diameter_mm": BOSS_OD,
            "length_mm": BOSS_LENGTH, "wall_contact_x_mm": 98.5,
            "pcb_contact_x_mm": PCB_MATING_X, "pilot_diameter_mm": PILOT_OD,
            "pilot_depth_mm": PILOT_DEPTH, "pilot_blind_end_x_mm": PCB_MATING_X+PILOT_DEPTH,
        }
        expected_volume += len(mounting_centers()) * math.pi * (
            (BOSS_OD/2)**2*BOSS_LENGTH - (PILOT_OD/2)**2*PILOT_DEPTH)
    elif name == "back-wall":
        result["through_hole"] = {"diameter_mm": BACK_HOLE_OD,
                                  "axis": [0, 1, 0], "center_x_mm": BACK_HOLE_X,
                                  "center_z_mm": BACK_HOLE_Z,
                                  "y_interval_mm": list(bounds["y"])}
        expected_volume -= math.pi*(BACK_HOLE_OD/2)**2*dimensions["y"]
    result["analytic_volume_mm3"] = expected_volume
    result["volume_difference_mm3"] = shape.Volume()-expected_volume
    return result


def export(output_dir=None):
    """Export three STEP/NPZ/report sets; return reports keyed by part name."""
    directory = Path(output_dir) if output_dir is not None else HERE/"parts"
    directory.mkdir(parents=True, exist_ok=True)
    results = {}
    for name, shape in build().items():
        result = report(name, shape)
        step_path, mesh_path = directory/f"{name}.step", directory/f"{name}.npz"
        cq.exporters.export(shape, str(step_path))
        vertices, faces = shape.tessellate(.08, .12)
        v = np.asarray([point.toTuple() for point in vertices], dtype=np.float32)
        f = np.asarray(faces, dtype=np.uint32)
        np.savez_compressed(mesh_path, v=v, f=f)
        result.update({"vertices": len(v), "triangles": len(f),
                       "artifacts": {"step": step_path.name, "npz": mesh_path.name}})
        (directory/f"{name}.report.json").write_text(json.dumps(result, indent=2)+"\n")
        results[name] = result
    return results


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out-dir", type=Path, help="Defaults to parts/ beside this script")
    args = parser.parse_args()
    print(json.dumps(export(args.out_dir), indent=2))


if __name__ == "__main__":
    main()
