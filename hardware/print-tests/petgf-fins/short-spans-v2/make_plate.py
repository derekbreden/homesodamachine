"""Build the two matched PET-GF diagnostic plates. Run manually; does not send."""
from pathlib import Path
import hashlib
import json
import math
import sys
import uuid
import xml.etree.ElementTree as ET
import zipfile

import cadquery as cq
import numpy as np
import trimesh

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
sys.path.insert(0, str(HERE.parent))
from build import block, label, FIRST, LAYER, PROFILE
sys.path.insert(0, str(ROOT / "tools/funnel-mold-print"))
from profiles import PROD, REL, mesh_object, metadata, qn

SPANS = (2, 4, 6, 8)
DEPTH = 12.0
POST_WIDTH = 3.0
UNDERLAP = 1.2
GAP = 0.24
ROOF_THICKNESS = 8 * LAYER
FOOT_HEIGHT = FIRST + 2 * LAYER
FANS = (0, 30)


def stem(fan):
    return f"2026-10-14-fin-v2-fan{fan}-petgf-left04-z004-mark2"


def roof_bottom(span):
    # All six ramps finish before a roof begins. Each shorter roof finishes
    # before the next span begins, preserving early results after a later pause.
    return FIRST + (75 + 10 * SPANS.index(span)) * LAYER


def anchor(span, fin=False, name=None):
    z = roof_bottom(span)
    left = block(POST_WIDTH, DEPTH, z)
    left = left.union(block(POST_WIDTH, DEPTH + 7, FOOT_HEIGHT, (0, -6, 0)))
    if not fin:
        right_x = POST_WIDTH + span
        right = block(POST_WIDTH, DEPTH, z, (right_x, 0, 0))
        right = right.union(block(POST_WIDTH, DEPTH + 2, FOOT_HEIGHT, (right_x, -1, 0)))
        width = right_x + POST_WIDTH
        detail = {"kind": "solid_anchor_bridge", "fin_count": 0}
    else:
        width = POST_WIDTH + span + UNDERLAP
        right_x = width + GAP
        right = block(1, DEPTH, z + ROOF_THICKNESS + LAYER, (right_x, 0, 0))
        right = right.edges("|Y and >Z").fillet(.45)
        right = right.union(block(3.2, DEPTH + 2, FOOT_HEIGHT, (right_x, -1, 0)))
        # These low teeth carry both perimeter beads and reach the front/back
        # corners. Upper tines attach sideways across the body clearance.
        for y, tine_width in ((.4, .8), (2, .5), (4, .5), (6, .5),
                              (8, .5), (10, .5), (11.6, .8)):
            right = right.union(block(UNDERLAP + GAP + .02, tine_width, LAYER,
                                     (POST_WIDTH + span, y-tine_width/2, z-LAYER)))
        for height in (z + 2 * LAYER, z + 5 * LAYER):
            for y in (2, 6, 10):
                right = right.union(block(GAP + .03, .5, LAYER,
                                         (width - .01, y - .25, height)))
        detail = {"kind": "fin_landing_bridge", "fin_count": 1,
                  "horizontal_body_gap_mm": GAP, "lower_tooth_underlap_mm": UNDERLAP,
                  "lower_teeth": 7, "upper_tines": 6, "tine_width_mm": .5,
                  "lower_corner_tine_width_mm": .8,
                  "tine_height_mm": LAYER, "tooth_nozzle_z_mm": z}
    roof = block(width, DEPTH, ROOF_THICKNESS, (0, 0, z))
    part = left.union(right).union(roof)
    name = name or (("F" if fin else "C") + str(span))
    part = part.union(label(name, 2.5, (POST_WIDTH / 2, -3, FOOT_HEIGHT)))
    detail.update(clear_span_mm=span, bridge_axis="X", bridge_angle_override="180",
                  roof_bottom_z_mm=z, first_roof_nozzle_z_mm=z + LAYER,
                  roof_top_z_mm=z + ROOF_THICKNESS, roof_depth_mm=DEPTH,
                  roof_thickness_mm=ROOF_THICKNESS,
                  clear_span_bounds_local_mm=[POST_WIDTH, POST_WIDTH + span],
                  roof_bounds_local_mm=[[0, 0, z], [width, DEPTH, z + ROOF_THICKNESS]])
    return part.clean(), detail


def turned_bridge(fin):
    part, detail = anchor(4, fin, ("F" if fin else "C") + "4Y")
    part = part.rotate((0, 0, 0), (0, 0, 1), 90)
    lo, hi = detail["roof_bounds_local_mm"]
    detail["roof_bounds_local_mm"] = [[-hi[1], lo[0], lo[2]], [-lo[1], hi[0], hi[2]]]
    detail.update(bridge_axis="Y", bridge_angle_override="90", rotation_degrees=90)
    return part, detail


def ramp(angle, reverse=False):
    start, reach, bottom, thickness = 4.0, 14.0, FIRST + 12 * LAYER, 2.4
    tangent = math.tan(math.radians(angle))
    rise = reach * tangent
    bar = cq.Workplane("XZ").polyline([
        (start-.1, bottom-.1*tangent), (start+reach, bottom+rise),
        (start+reach, bottom+rise+thickness), (start-.1, bottom+thickness-.1*tangent)
    ]).close().extrude(-DEPTH)
    part = block(start, DEPTH, bottom+thickness).union(bar)
    part = part.union(block(5, DEPTH+7, FOOT_HEIGHT, (0, -6, 0)))
    name = ("R" if reverse else "S") + str(angle)
    part = part.union(label(name, 2.6, (2.5, -3, FOOT_HEIGHT))).clean()
    detail = {"kind": "slope", "angle_from_bed_degrees": angle,
              "horizontal_reach_mm": reach, "depth_mm": DEPTH,
              "vertical_thickness_mm": thickness, "underside_start_z_mm": bottom,
              "rotation_degrees": 180 if reverse else 0,
              "orientation": "reversed" if reverse else "original"}
    if reverse:
        part = part.rotate((0, 0, 0), (0, 0, 1), 180)
    return part, detail


def tag(fan):
    part = block(18, 8, FOOT_HEIGHT)
    part = part.union(label(f"FAN {fan}", 2.5, (9, 4, FOOT_HEIGHT), rotation=0))
    return part.clean(), {"kind": "plate_identifier", "part_fan_percent": fan}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def make(fan):
    (HERE / "parts").mkdir(parents=True, exist_ok=True)
    groups = [
        (118, [(f"C{s}", *anchor(s)) for s in SPANS] + [("C4Y", *turned_bridge(False))]),
        (144, [(f"F{s}", *anchor(s, True)) for s in SPANS] + [("F4Y", *turned_bridge(True))]),
        (174, [(f"S{a}", *ramp(a)) for a in (30, 35, 40)]
              + [(f"R{a}", *ramp(a, True)) for a in (30, 35, 40)]),
        (197, [(f"FAN{fan}", *tag(fan))]),
    ]
    with zipfile.ZipFile(PROFILE) as z:
        settings = json.loads(z.read("Metadata/project_settings.config"))
        data = {name: z.read(name) for name in
                ("Metadata/filament_settings_1.config", "[Content_Types].xml")}
    changes = {
        "enable_support": "0", "brim_type": "no_brim", "skirt_loops": "0",
        "filament_colour": ["#161616"], "filament_multi_colour": ["#161616"],
        "filament_density": ["1.43"], "filament_map_mode": "Manual",
        "filament_map": ["1"], "filament_map_2": ["1"],
        "filament_nozzle_map": ["0"], "filament_volume_map": ["0"],
        "extruder_ams_count": ["1#0|4#0", "1#0|4#0"],
        "fan_min_speed": [str(fan)], "fan_max_speed": [str(fan)],
        "overhang_fan_speed": [str(fan)], "full_fan_speed_layer": ["4"],
        "close_fan_the_first_x_layers": ["3"],
        "first_x_layer_fan_speed": ["0"], "first_x_layer_part_fan_speed": ["0"],
        "printer_settings_id": "Bambu Lab H2C 0.4 Standard +0.04 Z trim",
        "print_settings_id": f"PET-GF short bridges; fixed part fan {fan}%",
    }
    edits = {k: {"profile": settings.get(k), "plate": v} for k, v in changes.items()
             if settings.get(k) != v}
    settings.update(changes)
    data["Metadata/project_settings.config"] = json.dumps(settings, indent=2).encode()
    filament = json.loads(data["Metadata/filament_settings_1.config"])
    for k, v in changes.items():
        if k in filament or k.startswith("fan_") or k in (
                "overhang_fan_speed", "full_fan_speed_layer", "first_x_layer_fan_speed",
                "first_x_layer_part_fan_speed", "close_fan_the_first_x_layers"):
            filament[k] = v
    data["Metadata/filament_settings_1.config"] = json.dumps(filament, indent=2).encode()
    model = ET.Element(qn("model"), unit="millimeter", requiredextensions="p",
                       **{"xmlns:BambuStudio": "http://schemas.bambulab.com/package/2021"})
    for k, v in (("Application", "BambuStudio-02.08.02.61"),
                 ("BambuStudio:3mfVersion", "1"), ("Title", stem(fan))):
        ET.SubElement(model, qn("metadata"), name=k).text = v
    resources = ET.SubElement(model, qn("resources"))
    build = ET.SubElement(model, qn("build"), **{f"{{{PROD}}}UUID": str(uuid.uuid4())})
    config = ET.Element("config")
    plate = ET.SubElement(config, "plate")
    for k, v in {"plater_id": 1, "plater_name": stem(fan), "locked": "false",
                 "filament_map_mode": "Manual", "filament_maps": "1",
                 "filament_volume_maps": "0", "bed_type": "Textured PEI Plate"}.items():
        metadata(plate, k, v)
    rels = ET.Element(f"{{{REL}}}Relationships")
    records, placed = [], []
    for group, (cy, items) in enumerate(groups, 1):
        meshes = []
        for name, shape, detail in items:
            path = HERE / "parts" / f"{name}.stl"
            if fan == 0 or name.startswith("FAN"):
                cq.exporters.export(shape, str(path), tolerance=.015, angularTolerance=.12)
            mesh = trimesh.load(path, force="mesh", process=True)
            meshes.append((name, shape, detail, path, mesh))
        total = sum(m.bounds[1, 0] - m.bounds[0, 0] for *_, m in meshes) + 3 * (len(meshes) - 1)
        cursor = 162.5 - total / 2
        for name, shape, detail, path, mesh in meshes:
            center = mesh.bounds.mean(axis=0)
            width = mesh.bounds[1, 0] - mesh.bounds[0, 0]
            cx = cursor + width / 2
            translation = np.array([cx, cy, center[2]]) - center
            bounds = mesh.bounds + translation
            number = len(records) + 1
            pid, oid = str(2 * number - 1), str(2 * number)
            subpath = f"/3D/Objects/object_{number}.model"
            sub = ET.Element(qn("model"), unit="millimeter")
            mesh_object(ET.SubElement(sub, qn("resources")), pid, mesh, center)
            data[subpath.lstrip("/")] = ET.tostring(sub, encoding="UTF-8", xml_declaration=True)
            obj = ET.SubElement(resources, qn("object"), id=oid, type="model",
                                **{f"{{{PROD}}}UUID": str(uuid.uuid4())})
            ET.SubElement(ET.SubElement(obj, qn("components")), qn("component"),
                          objectid=pid, transform="1 0 0 0 1 0 0 0 1 0 0 0",
                          **{f"{{{PROD}}}path": subpath, f"{{{PROD}}}UUID": str(uuid.uuid4())})
            ET.SubElement(build, qn("item"), objectid=oid, printable="1",
                          transform=f"1 0 0 0 1 0 0 0 1 {cx:.9f} {cy:.9f} {center[2]:.9f}")
            ET.SubElement(rels, f"{{{REL}}}Relationship", Target=subpath, Id=f"rel-{number}",
                          Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel")
            cfg = ET.SubElement(config, "object", id=oid)
            metadata(cfg, "name", name)
            metadata(cfg, "extruder", "1")
            if "bridge_angle_override" in detail:
                metadata(cfg, "bridge_angle", detail["bridge_angle_override"])
            ET.SubElement(cfg, "metadata", face_count=str(len(mesh.faces)))
            part = ET.SubElement(cfg, "part", id=pid, subtype="normal_part")
            for k, v in {"name": path.name, "matrix": "1 0 0 0 0 1 0 0 0 0 1 0 0 0 0 1",
                         "source_file": path.name, "source_object_id": 0, "source_volume_id": 0,
                         "source_offset_x": center[0], "source_offset_y": center[1],
                         "source_offset_z": center[2]}.items():
                metadata(part, k, v)
            inst = ET.SubElement(plate, "model_instance")
            for k, v in {"object_id": oid, "instance_id": 0, "identify_id": 5100 + number}.items():
                metadata(inst, k, v)
            records.append({"id": name, "row": group, "object_id": int(oid),
                            "identify_id": 5100 + number, "mesh": str(path.relative_to(HERE)),
                            "mesh_sha256": sha(path), "plate_translation_mm": translation.tolist(),
                            "plate_bounds_mm": bounds.tolist(), "triangles": len(mesh.faces),
                            "cad_valid": shape.val().isValid(), "cad_solids": len(shape.solids().vals()),
                            "mesh_watertight": bool(mesh.is_watertight),
                            "mesh_winding_consistent": bool(mesh.is_winding_consistent),
                            "mesh_bodies": mesh.body_count, **detail})
            m = mesh.copy()
            m.apply_translation(translation)
            placed.append(m)
            cursor += width + 3
    package = ET.Element(f"{{{REL}}}Relationships")
    ET.SubElement(package, f"{{{REL}}}Relationship", Target="/3D/3dmodel.model", Id="rel-1",
                  Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel")
    for path, element in (("3D/3dmodel.model", model), ("Metadata/model_settings.config", config),
                          ("3D/_rels/3dmodel.model.rels", rels), ("_rels/.rels", package)):
        data[path] = ET.tostring(element, encoding="UTF-8", xml_declaration=True).replace(
            b"ns0:", b"").replace(b"xmlns:ns0=", b"xmlns=")
    project = HERE / f"{stem(fan)}.3mf"
    with zipfile.ZipFile(project, "w", zipfile.ZIP_DEFLATED) as z:
        for path, payload in data.items():
            z.writestr(path, payload)
    bounds = trimesh.util.concatenate(placed).bounds
    report = {"project": project.name, "project_sha256": sha(project),
              "source_profile": str(PROFILE.relative_to(ROOT)), "source_profile_sha256": sha(PROFILE),
              "printer": "Mark2", "material": "Polymaker Fiberon PET-GF15",
              "nozzle": "Left fixed hardened Standard 0.4 mm; external spool 254",
              "plate": "Textured PEI Plate", "requested_z_trim_mm": .04,
              "expected_emitted_z_trim_mm": .02, "first_layer_mm": FIRST,
              "normal_layer_mm": LAYER, "part_fan_percent": fan,
              "settings_edits": edits, "cad_plate_bounds_mm": bounds.tolist(),
              "parts": records, "physical_result": "pending", "submitted": False}
    (HERE / f"{stem(fan)}.print.json").write_text(json.dumps(report, indent=2) + "\n")
    if fan == 0:
        render_layout(records)
    print(json.dumps({"project": str(project), "fan_percent": fan, "specimens": len(records),
                      "bounds_mm": bounds.tolist(),
                      "invalid": [r["id"] for r in records if not r["cad_valid"]
                                  or not r["mesh_watertight"] or r["mesh_bodies"] != 1]}))


def render_layout(records):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import Rectangle
    fig, ax = plt.subplots(figsize=(10, 7), dpi=150)
    colors = {"solid_anchor_bridge": "#6a9fbd", "fin_landing_bridge": "#91b887",
              "slope": "#e4aa6b", "plate_identifier": "#b4b0bb"}
    for r in records:
        lo, hi = np.asarray(r["plate_bounds_mm"])
        ax.add_patch(Rectangle(lo[:2], hi[0]-lo[0], hi[1]-lo[1],
                              facecolor=colors[r["kind"]], edgecolor="#354451"))
        ax.text(*(lo[:2]+hi[:2])/2, r["id"], ha="center", va="center", fontsize=9, fontweight="bold")
    for y, title in ((104, "C: solid anchors · 2 / 4 / 6 / 8 mm; 4 mm rotated at right"),
                     (130, "F: model anchor + removable fin · same spans"),
                     (157, "S: original ramps / R: reversed ramps · 30 / 35 / 40°")):
        ax.text(162.5, y, title, ha="center", fontsize=9)
    ax.set(xlim=(85, 240), ylim=(99, 210), xlabel="Bed X (mm)", ylabel="Bed Y (mm)")
    ax.set_aspect("equal")
    ax.grid(alpha=.15)
    ax.set_title("PET-GF short-span diagnostic · Mark2\nRamps finish first; bridge roofs begin at 2 → 4 → 6 → 8 mm", pad=15)
    ax.text(.5, -.16, "Facing the printer: front is at the bottom. FAN tag distinguishes the two cooling plates.",
            transform=ax.transAxes, ha="center", fontsize=9)
    fig.tight_layout()
    fig.savefig(HERE / "plate-layout.png", bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    for value in FANS:
        make(value)
