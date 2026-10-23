"""Plain orthogonal ceiling slab and underside recesses for a layout study.

Plan dimensions are millimetres in the assembly frame::

    {
      "slab": {"xmin": -115, "xmax": 115, "ymin": 230, "ymax": 467,
               "zmin": 346, "zmax": 355},
      "pockets": [{"name": "water-group", "xmin": -100, "xmax": 0,
                   "ymin": 300, "ymax": 440, "zmax": 352}],
      "minimum_stock_mm": 3
    }

Pocket zmin defaults to the slab underside. Pockets may extend outside the
slab; their intersections with the slab are the recesses. Each recess must
open through the underside and retain minimum_stock_mm above its roof.

Import build(plan_dict_or_path) for a CQ Solid, or export(plan, output_base)
for STEP, NPZ (v/f arrays), and a JSON report. No enclosure geometry is imported.

    PYTHONPATH=. tmp/takeover/cadq "ceiling fit slab" -- \
      tools/cad-venv/bin/python hardware/manifold-layout/studies/ceiling-fit/ceiling.py \
      --plan PLAN.json --out OUTPUT_BASE
"""

import argparse
import json
import math
from pathlib import Path

import cadquery as cq
import numpy as np


def _bounds(data, label):
    result = {f"{axis}{end}": float(data[f"{axis}{end}"])
              for axis in "xyz" for end in ("min", "max")}
    if not all(math.isfinite(value) for value in result.values()):
        raise ValueError(f"{label}: bounds must be finite")
    if any(result[f"{axis}min"] >= result[f"{axis}max"] for axis in "xyz"):
        raise ValueError(f"{label}: each maximum must exceed its minimum")
    return result


def _dimensions(bounds):
    return {axis: bounds[f"{axis}max"] - bounds[f"{axis}min"] for axis in "xyz"}


def _plan(plan):
    data = json.loads(Path(plan).read_text()) if isinstance(plan, (str, Path)) else plan
    slab = _bounds(data["slab"], "slab")
    minimum = float(data.get("minimum_stock_mm", 3.0))
    if not math.isfinite(minimum) or minimum <= 0:
        raise ValueError("minimum_stock_mm must be positive")
    if slab["zmax"] - slab["zmin"] < minimum - 1e-8:
        raise ValueError("The slab is thinner than minimum_stock_mm")
    pockets = []
    for index, raw in enumerate(data["pockets"]):
        name = str(raw.get("name", f"pocket-{index + 1}"))
        bounds = _bounds({"zmin": slab["zmin"], **raw}, name)
        if bounds["zmin"] > slab["zmin"] + 1e-8:
            raise ValueError(f"{name}: a ceiling recess must open through the underside")
        clipped = {f"{axis}{end}": (max if end == "min" else min)(
                       bounds[f"{axis}{end}"], slab[f"{axis}{end}"])
                   for axis in "xyz" for end in ("min", "max")}
        active = all(clipped[f"{axis}max"] > clipped[f"{axis}min"] for axis in "xyz")
        if active and slab["zmax"] - clipped["zmax"] < minimum - 1e-8:
            raise ValueError(f"{name}: pocket roof leaves less than {minimum:g} mm ceiling stock")
        pockets.append({"name": name, "requested_bounds_mm": bounds,
                        "bounds_mm": clipped if active else None, "active": active})
    return {"slab": slab, "pockets": pockets, "minimum_stock_mm": minimum}


def _box(bounds):
    d = _dimensions(bounds)
    return cq.Solid.makeBox(d["x"], d["y"], d["z"],
                            cq.Vector(bounds["xmin"], bounds["ymin"], bounds["zmin"]))


def _build(normalized):
    slab = _box(normalized["slab"])
    for pocket in normalized["pockets"]:
        if pocket["active"]:
            # Start the cutter just below the shared underside to avoid a
            # coincident Boolean face without changing the finished recess.
            cutter_bounds = dict(pocket["bounds_mm"])
            cutter_bounds["zmin"] -= .01
            slab = slab.cut(_box(cutter_bounds))
    return slab.clean()


def build(plan):
    """Build one native slab Solid from a plan dictionary or JSON path."""
    return _build(_plan(plan))


def _overlap_xy(a, b):
    return all(min(a[f"{axis}max"], b[f"{axis}max"]) >
               max(a[f"{axis}min"], b[f"{axis}min"]) for axis in "xy")


def report(plan, shape=None):
    """Describe dimensions, removed volume and the stock over every recess."""
    p = _plan(plan)
    shape = _build(p) if shape is None else shape
    slab_dimensions = _dimensions(p["slab"])
    original_volume = math.prod(slab_dimensions.values())
    pockets = []
    for pocket in p["pockets"]:
        item = dict(pocket)
        if pocket["active"]:
            b = pocket["bounds_mm"]
            highest_roof = max(other["bounds_mm"]["zmax"] for other in p["pockets"]
                               if other["active"] and _overlap_xy(b, other["bounds_mm"]))
            item.update({"dimensions_mm": _dimensions(b), "roof_z_mm": b["zmax"],
                         "ceiling_stock_mm": p["slab"]["zmax"] - b["zmax"],
                         "minimum_stock_within_footprint_mm": p["slab"]["zmax"] - highest_roof})
        pockets.append(item)
    bb = shape.BoundingBox()
    return {"units": "mm", "slab_bounds_mm": p["slab"],
            "slab_dimensions_mm": slab_dimensions, "minimum_stock_mm": p["minimum_stock_mm"],
            "pockets": pockets, "valid": bool(shape.isValid()), "solid_count": len(shape.Solids()),
            "uncut_volume_mm3": original_volume, "volume_mm3": shape.Volume(),
            "removed_volume_mm3": original_volume - shape.Volume(),
            "bounds_mm": {"xmin": bb.xmin, "xmax": bb.xmax, "ymin": bb.ymin,
                          "ymax": bb.ymax, "zmin": bb.zmin, "zmax": bb.zmax}}


def export(plan, output_base):
    """Write OUTPUT_BASE.step/.npz/.report.json, returning the report dictionary."""
    p = _plan(plan)
    shape = _build(p)
    result = report(plan, shape)
    base = Path(output_base)
    base.parent.mkdir(parents=True, exist_ok=True)
    step_path, mesh_path, report_path = (Path(str(base) + suffix)
                                        for suffix in (".step", ".npz", ".report.json"))
    cq.exporters.export(shape, str(step_path))
    vertices, faces = shape.tessellate(.1, .15)
    v = np.asarray([point.toTuple() for point in vertices], dtype=np.float32)
    f = np.asarray(faces, dtype=np.uint32)
    np.savez_compressed(mesh_path, v=v, f=f)
    result.update({"vertices": len(v), "triangles": len(f),
                   "artifacts": {"step": step_path.name, "npz": mesh_path.name}})
    report_path.write_text(json.dumps(result, indent=2) + "\n")
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan", required=True, type=Path)
    parser.add_argument("--out", type=Path, help="Output prefix; defaults to PLAN_DIR/ceiling-fit")
    args = parser.parse_args()
    result = export(args.plan, args.out or args.plan.parent / "ceiling-fit")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
