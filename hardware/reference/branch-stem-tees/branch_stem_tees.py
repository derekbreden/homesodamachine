"""Estimated 1/4-inch perpendicular-stem tees for compact plumbing studies.

Native frame: run on +/-X, perpendicular male stem on +Y, common axes at origin.
The two variants are NeoFit ATBU444-E and John Guest CI580808W. Dimension and
source status are recorded beside the generated models in dimensions.json.

Only external envelopes, hollow sockets and flow bores are modeled. Collet tooth,
O-ring and molded rib detail are omitted. This is a purchased-part layout reference.

    PYTHONPATH=. tmp/takeover/cadq "branch stem tee estimates" -- \
      tools/cad-venv/bin/python hardware/reference/branch-stem-tees/branch_stem_tees.py
"""

from pathlib import Path
import json
import sys

import cadquery as cq
import numpy as np

HERE = Path(__file__).resolve().parent
HW = HERE.parents[1]
sys.path.insert(0, str(HW / "scripts"))
from _cadq_export import export_assembly
from _material_base import one_body


def specification(variant="neofit"):
    """One coherent set of native datums; JSON is the dimensional source."""
    return json.loads((HERE / "dimensions.json").read_text())["variants"][variant]


def stations(variant="neofit"):
    """Native ports as {name: {position, outward, type, ...}} in millimetres."""
    return specification(variant)["ports"]


def cyl(radius, axis, near, far):
    d = cq.Vector(*axis)
    return cq.Solid.makeCylinder(radius, far-near, d.multiply(near), d)


def cone(r0, r1, axis, near, far):
    d = cq.Vector(*axis)
    return cq.Solid.makeCone(r0, r1, far-near, d.multiply(near), d)


def build(variant="neofit"):
    """Return a CadQuery Solid, with real open sockets and a perpendicular stem."""
    p = specification(variant)["model_mm"]
    reach = p["run_span"]/2
    root_r, collar_r = p["root_od"]/2, p["collar_od"]/2
    near, far = p["collar_near"], p["collar_far"]
    collet_near = p["collet_near"]
    part = cyl(root_r, (1,0,0), -near-.01, near+.01)
    for axis in ((1,0,0),(-1,0,0)):
        arm = cone(root_r, collar_r-.45, axis, near-.05, near+.7)
        arm = arm.fuse(cyl(collar_r-.45, axis, near+.65, near+1.4))
        arm = arm.fuse(cyl(collar_r, axis, near+1.35, far))
        arm = arm.fuse(cyl(collar_r-.45, axis, far-.05, collet_near+.02))
        arm = arm.fuse(cyl(p["collet_od"]/2, axis, collet_near, reach))
        part = part.fuse(arm)
    # Short branch boss and the smaller smooth stem; tip chamfer is illustrative.
    y_shoulder, y_tip = p["stem_shoulder_y"], p["stem_tip_y"]
    part = part.fuse(cyl(p["branch_boss_od"]/2, (0,1,0), 0, y_shoulder))
    part = part.fuse(cyl(3.175, (0,1,0), y_shoulder-.05, y_tip-.25))
    part = part.fuse(cone(3.175, 2.925, (0,1,0), y_tip-.25, y_tip))
    cutters = cyl(p["flow_bore_od"]/2, (1,0,0), -reach-.5, reach+.5)
    cutters = cutters.fuse(cyl(p["flow_bore_od"]/2, (0,1,0), -.05, y_tip+.5))
    for axis in ((1,0,0),(-1,0,0)):
        cutters = cutters.fuse(cyl(3.175, axis, reach-p["female_insertion"], reach+.5))
    return part.cut(cutters).clean()


def main():
    checks = {}
    for key in ("neofit", "john-guest"):
        spec = specification(key)
        shape = build(key)
        name = spec["artifact_stem"]
        color = cq.Color(*spec["color_rgb"])
        export_assembly(one_body(shape, name, color), str(HERE/f"{name}.step"))
        vertices, faces = shape.tessellate(.07, .12)
        v = np.asarray([x.toTuple() for x in vertices], dtype=np.float32)
        f = np.asarray(faces, dtype=np.uint32)
        np.savez_compressed(HERE/f"{name}.npz", v=v, f=f)
        bb = shape.BoundingBox()
        checks[key] = {
            "valid": bool(shape.isValid()), "solid_count": len(shape.Solids()),
            "volume_mm3": shape.Volume(), "vertices": len(v), "triangles": len(f),
            "bounds_min_mm": [bb.xmin,bb.ymin,bb.zmin],
            "bounds_max_mm": [bb.xmax,bb.ymax,bb.zmax],
            "ports": stations(key),
        }
        if not checks[key]["valid"] or checks[key]["solid_count"] != 1:
            raise ValueError(f"Invalid purchased-part estimate: {key}")
        print(key, checks[key])
    (HERE/"model-check.json").write_text(json.dumps(checks,indent=2)+"\n")


if __name__ == "__main__":
    main()
