"""Build the isolated aft-expanded funnel group through tmp/takeover/cadq.

The production definitions are loaded without calling their file writers. Only
the in-memory parameters change. Output meshes and native STEPs use the selected
study's world frame, with absolute mouth and drain stations from the plan.
"""
from pathlib import Path
import hashlib
import importlib.util
import json
import re
import sys

import cadquery as cq
import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
SOURCE = ROOT / "hardware/printed-parts/zone-c/funnel"
COVER = ROOT / "hardware/printed-parts/zone-c/funnel-cover/funnel_cover.py"


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    sys.modules[name] = result
    spec.loader.exec_module(result)
    return result


def capacity(funnel):
    """Measure the same complete wet cavity as the production generator."""
    ramp_top = funnel.brim_thickness - funnel.chute_h
    neck = ramp_top - funnel._ramp_rise
    end = -funnel.drop + funnel.plug_lift
    top = funnel.brim_thickness + funnel.apron_rise
    w, d = (funnel.collar_w - 2 * funnel.collar_wall,
            funnel.collar_d - 2 * funnel.collar_wall)
    ramp = funnel._loft_rc(w, d, 0., 0., ramp_top,
        funnel.spout_id / 2, funnel.neck_dx, funnel.neck_dy, neck,
        funnel.mouth_corner_r)
    cavity = funnel._rounded_box(w, d, funnel.mouth_corner_r, ramp_top, top + 1)
    cavity = cavity.fuse(ramp).fuse(funnel._cyl(funnel.spout_id / 2,
        neck + .01, end - 1, funnel.neck_dx, funnel.neck_dy)).clean()
    return cavity.intersect(funnel._box(600, 600, end, top, 0, 0)).Volume() / 1000


def export(name, shape, out):
    assembly = cq.Assembly(name=name)
    assembly.add(shape, name="body")
    path = out / (name + ".step")
    assembly.export(str(path))
    path.write_bytes(re.sub(rb"'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}'",
                            b"'1970-01-01T00:00:00'", path.read_bytes()))
    vertices, faces = shape.tessellate(.04, .12)
    vertices = np.array([v.toTuple() for v in vertices], np.float32)
    faces = np.array(faces, np.int32)
    np.savez_compressed(out / (name + ".npz"), v=vertices, f=faces)
    return {"valid": shape.isValid(), "solid_count": len(shape.Solids()),
            "bounds_mm": [vertices.min(0).tolist(), vertices.max(0).tolist()],
            "material_volume_mm3": shape.Volume(),
            "vertices": len(vertices), "triangles": len(faces)}


def main():
    plan = json.loads((HERE / "funnel-expansion-plan.json").read_text())
    shell_sources = {
        "expanded-funnel-ceiling": HERE.parent / "east-feed/parts/east-feed-ceiling.step",
        "expanded-funnel-left-wall": HERE.parent / "wall-supported/parts/left-wall.step",
        "expanded-funnel-right-wall": HERE.parent / "wall-supported/parts/right-wall.step",
    }
    source_paths = [SOURCE / "funnel.py", SOURCE / "funnel_frame.py",
                    SOURCE / "elbow_cradle.py", COVER, *shell_sources.values()]
    source_hashes = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
                     for p in source_paths}
    sys.path[:0] = [str(SOURCE), str(ROOT / "hardware/printed-parts/cadlib")]
    funnel = module("funnel", SOURCE / "funnel.py")
    frame = module("funnel_frame", SOURCE / "funnel_frame.py")
    # Load enclosure dimensions against the unmodified production definitions.
    # Its ordinary wall/seam/fastener dimensions are frame dependencies only.
    import enclosure

    extension = plan["aft_extension_mm"]
    center = np.array(plan["collar_center_world_mm"], float)
    outlet = np.array(plan["outlet_bore_exit_world_mm"], float)
    funnel.collar_d = plan["collar_depth_mm"]
    funnel.apron_depth = plan["apron_depth_mm"]
    funnel.neck_dx = float(outlet[0] - center[0])
    funnel.neck_dy = float(outlet[1] - center[1])
    funnel.drain_local = (funnel.neck_dx, funnel.neck_dy,
                         -funnel.drop + funnel.plug_lift)
    frame.depth = plan["frame_depth_mm"]
    frame.corbel_foot_half_depth = plan["frame_corbel_foot_half_depth_mm"]
    frame.body_width = plan["frame_body_width_mm"]
    frame.center_y = float(center[1])
    frame.forming_clearance.cache_clear()
    frame.build.cache_clear()
    cover = module("expanded_funnel_cover", COVER)

    silicone, _dimensions = funnel.build()
    silicone = silicone.val().translate(center.tolist())
    rigid = frame.build(centre=(float(center[0]), float(center[1])),
                        seat=float(center[2]))
    lid = cover.placed(float(center[0]), float(center[1]),
                       float(center[2] + funnel.brim_thickness + funnel.apron_rise))
    out = HERE / "parts"
    out.mkdir(exist_ok=True)
    shapes = {"expanded-funnel": silicone, "expanded-funnel-frame": rigid,
              "expanded-funnel-cover": lid}
    cut = plan["shell_opening_cut_mm"]
    opening = cq.Solid.makeBox(cut["xmax"] - cut["xmin"],
        cut["ymax"] - cut["ymin"], cut["zmax"] - cut["zmin"],
        cq.Vector(cut["xmin"], cut["ymin"], cut["zmin"]))
    for name, source in shell_sources.items():
        native = cq.importers.importStep(str(source)).val()
        shapes[name] = native.cut(opening).clean()
    report = {"scope": plan["scope"], "units": "mm", "source_sha256": source_hashes,
        "aft_extension_mm": extension,
        "collar_depth_mm": funnel.collar_d, "collar_center_world_mm": center.tolist(),
        "outlet_bore_exit_world_mm": (center + funnel.drain_local).tolist(),
        "drain_union_corner_world_mm": plan["drain_union_corner_world_mm"],
        "outlet_fore_of_mouth_center_mm": float(center[1] - outlet[1]),
        "capacity_to_mouth_ml": capacity(funnel),
        "capacity_method": "Complete native wet cavity closed at mouth and outlet planes; no cover displacement",
        "silicone_normal_wall_mm": funnel.collar_wall,
        "apron_thickness_mm": funnel.apron_rise,
        "frame_fasteners": list(frame.fastener_datums(centre=(float(center[0]), float(center[1])),
                                                     seat=float(center[2]))),
        "shell_opening_cut_mm": cut,
        "shell_upper_fore_edge_y_mm": cut["ymax"],
        "shell_cut_to_valve_support_fore_face_mm": plan["valve_support_fore_face_y_mm"] - cut["ymax"],
        "drain_attachment": "Elbow cradle snaps into the removable funnel frame's 3 mm bottom web",
        "parts": {name: export(name, shape, out) for name, shape in shapes.items()},
        "qualification_scope": "Native isolated arrangement geometry. Casting, print fit, support removal and capacity in use remain outside this geometric result."}
    report["apron_plan_to_valve_support_fore_face_mm"] = (
        plan["valve_support_fore_face_y_mm"] - report["parts"]["expanded-funnel"]["bounds_mm"][1][1])
    (HERE / "funnel-expansion.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
