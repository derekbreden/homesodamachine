"""Native rear wall and roof for the selected TPU CO2 arrangement.

The six bare bulkheads share one interior relief and retain 6 mm of panel.
Dry-side openings use the selected C14 and keystone poses. Side walls come
from the parent study; connector retention and carriers are outside this model.

Run manually through the CAD queue to export only back-wall and ceiling::

    PYTHONPATH=. tmp/takeover/cadq "TPU CO2 context" -- \\
      tools/cad-venv/bin/python \\
      hardware/manifold-layout/studies/co2-tpu/context.py
"""
from pathlib import Path
import importlib.util
import json

import cadquery as cq
import numpy as np

HERE = Path(__file__).resolve().parent


def box(bounds):
    return cq.Solid.makeBox(
        bounds["xmax"] - bounds["xmin"],
        bounds["ymax"] - bounds["ymin"],
        bounds["zmax"] - bounds["zmin"],
        cq.Vector(bounds["xmin"], bounds["ymin"], bounds["zmin"]),
    )


def ceiling_builder():
    spec = importlib.util.spec_from_file_location(
        "co2_tpu_ceiling", HERE.parent / "ceiling-fit/ceiling.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def build():
    plan = json.loads((HERE / "context-plan.json").read_text())
    back = box(plan["rear_wall"])
    back = back.cut(box(plan["interior_panel_relief"]))
    for port in plan["wet_ports"]:
        bore = cq.Solid.makeCylinder(
            port["bore_diameter_mm"] / 2,
            9.02,
            cq.Vector(port["center_x_mm"], 462.29, port["center_z_mm"]),
            cq.Vector(0, 1, 0),
        )
        back = back.cut(bore)

    inlet = plan["dry_openings"]["c14"]
    center = np.array(inlet["flange_center_mm"])
    rotation = np.array(inlet["rotation"])

    def inlet_opening(half_xz, ymin):
        half_x, half_z = half_xz
        corners = np.array([
            [dx, 0, dz]
            for dx in (-half_x, half_x)
            for dz in (-half_z, half_z)
        ]) @ rotation.T + center
        low, high = corners.min(0), corners.max(0)
        return box({"xmin": low[0], "xmax": high[0],
                    "ymin": ymin, "ymax": 471.31,
                    "zmin": low[2], "zmax": high[2]})

    back = back.cut(inlet_opening(
        inlet["flange_pocket_half_xz_mm"], inlet["flange_pocket_ymin_mm"]
    ))
    back = back.cut(inlet_opening(
        inlet["body_opening_half_xz_mm"], inlet["body_opening_ymin_mm"]
    ))
    for dx in (-inlet["mount_pitch_mm"] / 2, inlet["mount_pitch_mm"] / 2):
        point = center + rotation @ np.array([dx, 0, 0])
        back = back.cut(cq.Solid.makeCylinder(
            inlet["mount_hole_radius_mm"], 9.02,
            cq.Vector(point[0], 462.29, point[2]), cq.Vector(0, 1, 0),
        ))
    back = back.cut(box(plan["dry_openings"]["keystone"]))
    return {
        "back-wall": back.clean(),
        "ceiling": ceiling_builder().build(HERE / plan["roof_plan"]),
    }


def main():
    out = HERE / "parts"
    out.mkdir(exist_ok=True)
    plan = json.loads((HERE / "context-plan.json").read_text())
    for name, shape in build().items():
        cq.exporters.export(shape, str(out / (name + ".step")))
        vertices, faces = shape.tessellate(.08, .12)
        np.savez_compressed(
            out / (name + ".npz"),
            v=np.array([point.toTuple() for point in vertices], dtype=np.float32),
            f=np.array(faces, dtype=np.uint32),
        )
        bb = shape.BoundingBox()
        report = {
            "units": "mm", "valid": bool(shape.isValid()),
            "solid_count": len(shape.Solids()), "volume_mm3": shape.Volume(),
            "bounds_mm": [[bb.xmin, bb.ymin, bb.zmin],
                          [bb.xmax, bb.ymax, bb.zmax]],
            "vertices": len(vertices), "triangles": len(faces),
            "scope": "Native study context; connector retention and equipment carriers are outside this model",
        }
        if name == "back-wall":
            report.update(retained_wet_panel_mm=6.0, wet_bore_count=6,
                          interior_relief_mm=plan["interior_panel_relief"],
                          dry_openings=plan["dry_openings"])
        else:
            report["roof"] = ceiling_builder().report(
                HERE / plan["roof_plan"], shape
            )
        (out / (name + ".report.json")).write_text(
            json.dumps(report, indent=2) + "\n"
        )
        print(name, report["valid"], report["solid_count"], report["volume_mm3"])


if __name__ == "__main__":
    main()
