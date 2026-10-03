"""Prepare and audit one paused ASA Aero float; never submits a print."""

import copy
import hashlib
import importlib.util
import json
import math
import re
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET
import zipfile
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import trimesh
from scipy.spatial import cKDTree
from shapely.geometry import LineString, Polygon
from shapely.ops import unary_union

HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p / "tools/bambu_printer.py").is_file())
sys.path.insert(0, str(HERE))
import all_aero_float as geometry

HELPER = HERE.parent / "mark2-aero-print/v7/prepare.py"
spec = importlib.util.spec_from_file_location("nested_wall_review", HELPER)
review = importlib.util.module_from_spec(spec)
spec.loader.exec_module(review)
CORE, PROD = review.CORE, review.PROD
ET.register_namespace("", CORE)
ET.register_namespace("p", PROD)
SETTING = "Metadata/project_settings.config"
GCODE = "Metadata/plate_1.gcode"
RECORDS = HERE / "mark2-print/v1"
JOB = ROOT / ".cache/prints/magnetic-float-all-aero-mark2-v1"
NAME = "magnetic-float-all-aero-mark2-v1.gcode.3mf"
MESSAGE = ("Insert one RC62 ring into the open annular pocket, fully down onto its floor. "
           "The magnet must sit below both pocket rims. Keep the guide bore open and clear "
           "loose strings without moving the float. Resume only with the magnet fully seated.")


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def commands(program):
    return [line.split(";", 1)[0].strip() for line in program.splitlines()
            if line.split(";", 1)[0].strip() and not line.startswith("M73 ")]


def audited_roads(program):
    """Extend the existing explicit-motion reading with Z and command positions."""
    xyz = np.zeros(3)
    obj = layer = None
    width = feed = e = 0.0
    feature = ""
    absolute_xyz = relative_e = True
    result = []
    for index, raw in enumerate(program.splitlines()):
        if raw.startswith("; OBJECT_ID:"):
            obj = int(raw.split(":", 1)[1])
        elif raw.startswith("; Z_HEIGHT:"):
            layer = float(raw.split(":", 1)[1]); obj = None
        elif raw.startswith("; start printing object, unique label id:"):
            obj = int(raw.rsplit(":", 1)[1])
        elif raw.startswith("; stop printing object"):
            obj = None
        elif raw.startswith("; FEATURE:"):
            feature = raw.split(":", 1)[1].strip()
        elif raw.startswith("; LINE_WIDTH:"):
            width = float(raw.split(":", 1)[1])
        code = raw.split(";", 1)[0].strip()
        if not code:
            continue
        command = code.split()[0]
        values = {k: float(v) for k, v in re.findall(r"([XYZEF])([-+\d.]+)", code)}
        if command in ("G90", "G91"):
            absolute_xyz = command == "G90"
        elif command in ("M82", "M83"):
            relative_e = command == "M83"
        elif command == "G92":
            xyz = np.array([values.get(k, old) for k, old in zip("XYZ", xyz)])
            e = values.get("E", e)
        elif command in ("G0", "G1", "G2", "G3"):
            target = np.array([values.get(k, old) if absolute_xyz else old + values.get(k, 0)
                               for k, old in zip("XYZ", xyz)])
            delta = values.get("E", 0) if relative_e else values.get("E", e) - e
            feed = values.get("F", feed)
            if obj is not None and layer is not None and delta > 1e-9 and np.linalg.norm(target[:2] - xyz[:2]) > 1e-6:
                assert command in ("G0", "G1")
                result.append({"line_index": index, "layer": layer, "z": float(target[2]),
                               "a": tuple(xyz[:2]), "b": tuple(target[:2]), "width": width,
                               "feature": feature, "extrusion_mm": delta, "speed_mm_s": feed / 60})
            xyz = target
            if "E" in values:
                e = e + values["E"] if relative_e else values["E"]
    return result


def magnet_pause_review(program, mesh):
    roads = audited_roads(program)
    pauses = [i for i, line in enumerate(program.splitlines()) if line.split(";", 1)[0].strip() == "M400 U1"]
    assert len(pauses) == 1, pauses
    # Test native bead footprints over the nominal ring, not just layer labels.
    center = np.array([150, 145])
    ring = Polygon([(math.cos(a) * geometry.magnet_od / 2 + 150,
                     math.sin(a) * geometry.magnet_od / 2 + 145)
                    for a in np.linspace(0, 2 * math.pi, 720, endpoint=False)],
                   [[(math.cos(a) * geometry.magnet_id / 2 + 150,
                      math.sin(a) * geometry.magnet_id / 2 + 145)
                     for a in np.linspace(0, 2 * math.pi, 720, endpoint=False)]])
    heights = sorted({r["layer"] for r in roads})
    coverage = {}
    for z in heights:
        if geometry.magnet_seat - 0.4 <= z <= geometry.pocket_roof + 0.4:
            beads = unary_union([LineString((r["a"], r["b"])).buffer(r["width"] / 2)
                                 for r in roads if r["layer"] == z])
            coverage[z] = beads.intersection(ring).area / ring.area
    open_layers = [z for z, fraction in coverage.items() if fraction < 0.05]
    assert open_layers
    seat = max(z for z in heights if z < min(open_layers))
    rim = max(open_layers)
    first_cover = min(z for z, fraction in coverage.items() if z > rim and fraction > 0.95)
    assert first_cover == round(geometry.pause_before_z, 6)
    before = [r for r in roads if r["line_index"] < pauses[0]]
    after = [r for r in roads if r["line_index"] > pauses[0]]
    assert max(r["layer"] for r in before) == rim
    assert min(r["layer"] for r in after) == first_cover
    assert not any(r["line_index"] < pauses[0] and r["layer"] == first_cover for r in roads)
    cover = [r for r in after if r["layer"] == first_cover]
    actual_cover_z = min(r["z"] for r in cover)
    assert actual_cover_z == first_cover
    max_magnet_top = seat + geometry.magnet_thickness + geometry.magnet_tolerance
    assert rim - max_magnet_top >= 0.1
    assert actual_cover_z - max_magnet_top >= 0.3
    # The guide is through-open even on the closing layer.
    from shapely.geometry import Point
    cover_beads = unary_union([LineString((r["a"], r["b"])).buffer(r["width"] / 2) for r in cover])
    safe_open_bore = Point(150, 145).buffer(geometry.bore_diameter / 2 - 0.1)
    assert cover_beads.intersection(safe_open_bore).area < 0.01
    return {"pause_command": "M400 U1", "pause_count": 1,
            "completed_layers_before_pause": heights.index(rim) + 1,
            "last_open_pocket_layer_z_mm": rim, "printed_seat_top_z_mm": seat,
            "first_covering_layer_z_mm": actual_cover_z,
            "nominal_printed_magnet_center_z_mm": seat + geometry.magnet_thickness / 2,
            "nominal_cad_magnet_center_z_mm": geometry.magnet_midplane,
            "physical_center_scope": "Layer quantization, magnet thickness tolerance and actual printed fit limit physical centering.",
            "nominal_seated_magnet_top_z_mm": seat + geometry.magnet_thickness,
            "maximum_seated_magnet_top_z_mm": max_magnet_top,
            "minimum_magnet_recess_below_printed_rim_mm": rim - max_magnet_top,
            "minimum_first_cover_nozzle_clearance_mm": actual_cover_z - max_magnet_top,
            "ring_footprint_coverage_by_layer": {str(k): v for k, v in coverage.items()},
            "covering_roads_emitted_after_pause_only": True,
            "guide_bore_remains_open": True,
            "pause_message": MESSAGE,
            "scope": "Explicit commands and idealized bead footprints; firmware parking/resume motion, actual foam, magnet movement and hot metal adhesion remain physical-trial observations."}


def render(roads, pause):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.collections import LineCollection
    from matplotlib.patches import Rectangle
    fig, axes = plt.subplots(1, 3, figsize=(12, 4.5))
    ax = axes[0]
    for a, b in [(-18, -2.4), (2.4, 18)]:
        ax.add_patch(Rectangle((a, 0), b - a, geometry.height, facecolor="#e4d5a8", edgecolor="#665b42"))
    for a, b in [(-geometry.pocket_od / 2, -geometry.pocket_id / 2),
                 (geometry.pocket_id / 2, geometry.pocket_od / 2)]:
        ax.add_patch(Rectangle((a, geometry.magnet_seat), b - a, geometry.pocket_depth,
                              facecolor="white", edgecolor="#665b42", linewidth=0.6))
    for a, b in [(-geometry.magnet_od / 2, -geometry.magnet_id / 2),
                 (geometry.magnet_id / 2, geometry.magnet_od / 2)]:
        ax.add_patch(Rectangle((a, geometry.magnet_seat), b - a, geometry.magnet_thickness,
                              facecolor="#75828f", edgecolor="#35424e"))
    ax.axhline(geometry.magnet_midplane, color="#75828f", linewidth=0.7, linestyle="--")
    ax.axhline(pause["first_covering_layer_z_mm"], color="#af523c", linewidth=1, linestyle=":")
    ax.set(xlim=(-20, 20), ylim=(-1, 30), aspect="equal", title="28 mm body; magnet center at 14 mm", xlabel="X (mm)", ylabel="Z (mm)")
    for ax, z, title in zip(axes[1:], [pause["last_open_pocket_layer_z_mm"], pause["first_covering_layer_z_mm"]],
                            ["Pocket open at pause", "First layer over the inserted magnet"]):
        moves = [[(r["a"][0] - 150, r["a"][1] - 145),
                  (r["b"][0] - 150, r["b"][1] - 145)] for r in roads if r["layer"] == z]
        ax.add_collection(LineCollection(moves, colors="#244867", linewidths=0.65))
        ax.set(xlim=(-19, 19), ylim=(-19, 19), aspect="equal", title=f"{title}\nZ = {z:g} mm", xlabel="X (mm)", ylabel="Y (mm)")
    for ax in axes:
        ax.grid(alpha=0.12)
    fig.tight_layout()
    fig.savefig(RECORDS / "pause-preview.png", dpi=180)
    plt.close(fig)


def main():
    RECORDS.mkdir(parents=True, exist_ok=True)
    prior = json.loads((HERE.parent / "mark2-aero-print/v7/insert-preflight.json").read_text())
    baseline_project = ROOT / prior["project"]
    assert sha(baseline_project) == prior["project_sha256"]
    original = review.members(baseline_project)
    settings = json.loads(original[SETTING])
    selected = copy.deepcopy(settings)
    start = selected["machine_start_gcode"]
    assert start.count("X110 Y14 I181 J146") == 3
    selected["machine_start_gcode"] = start.replace("X110 Y14 I181 J146", "X110 Y14 I181 J154")
    selected["name"] = "All-ASA Aero float with RC62 insertion pause"
    selected["print_settings_id"] = selected["name"]
    assert selected["wall_loops"] == "300" and selected["machine_pause_gcode"].strip() == "M400 U1"
    mesh = trimesh.load(HERE / "float-aero.stl", force="mesh", process=True)
    assert mesh.is_watertight and abs(mesh.bounds[0, 2]) < 1e-6
    assert abs(mesh.bounds[1, 2] - geometry.height) < 1e-6
    config = ET.fromstring(original["Metadata/model_settings.config"])
    obj, = config.findall("object")
    part, = obj.findall("part")
    for item in obj.findall("metadata"):
        if item.get("key") == "name": item.set("value", "All-ASA Aero float")
    for item in part.findall("metadata"):
        if item.get("key") == "name": item.set("value", "float-aero")
        if item.get("key") == "source_file": item.set("value", "float-aero.stl")
        if item.get("key") == "source_offset_z": item.set("value", str(geometry.height / 2))
    part.find("mesh_stat").set("face_count", str(len(mesh.faces)))
    for item in config.find("plate").findall("metadata"):
        if item.get("key") == "plater_name": item.set("value", selected["name"])
    model = ET.fromstring(original["3D/3dmodel.model"])
    model.set("xmlns:BambuStudio", "http://schemas.bambulab.com/package/2021")
    component = model.find(f".//{{{CORE}}}component")
    member = component.get(f"{{{PROD}}}path").lstrip("/")
    build, = model.find(f"{{{CORE}}}build")
    build.set("transform", f"1 0 0 0 1 0 0 0 1 150 145 {geometry.height / 2}")
    embedded = ET.fromstring(original[member])
    xml_mesh = embedded.find(f".//{{{CORE}}}mesh")
    xml_mesh.clear()
    vertices = mesh.vertices - [0, 0, geometry.height / 2]
    xml_vertices = ET.SubElement(xml_mesh, f"{{{CORE}}}vertices")
    for x, y, z in vertices:
        ET.SubElement(xml_vertices, f"{{{CORE}}}vertex", x=f"{x:.8f}", y=f"{y:.8f}", z=f"{z:.8f}")
    triangles = ET.SubElement(xml_mesh, f"{{{CORE}}}triangles")
    for a, b, c in mesh.faces:
        ET.SubElement(triangles, f"{{{CORE}}}triangle", v1=str(a), v2=str(b), v3=str(c))
    pauses = ET.Element("custom_gcodes_per_layer")
    plate = ET.SubElement(pauses, "plate")
    ET.SubElement(plate, "plate_info", id="1")
    ET.SubElement(plate, "layer", top_z=f"{geometry.pause_before_z:.6f}", type="1", extruder="1",
                  color="", extra=MESSAGE, gcode="M400 U1")
    ET.SubElement(plate, "mode", value="SingleExtruder")
    revised = {n: b for n, b in original.items() if not n.startswith("Metadata/plate_")}
    revised[SETTING] = json.dumps(selected).encode()
    for name, xml in [("Metadata/model_settings.config", config), ("3D/3dmodel.model", model),
                      (member, embedded), ("Metadata/custom_gcode_per_layer.xml", pauses)]:
        revised[name] = ET.tostring(xml, encoding="UTF-8", xml_declaration=True)
    project = HERE / "all-aero-float.3mf"
    native_dir = JOB / "native"
    native = native_dir / NAME
    if not native.exists():
        assert not JOB.exists(), "Inspect an incomplete preparation before making another export."
        native_dir.mkdir(parents=True)
        with zipfile.ZipFile(project, "w", zipfile.ZIP_DEFLATED) as z:
            for name, data in revised.items(): z.writestr(name, data)
        with (JOB / "slice.log").open("w") as log:
            subprocess.run([str(review.STUDIO), "--arrange", "0", "--orient", "0", "--slice", "0",
                            "--export-3mf", NAME, "--outputdir", str(native_dir), str(project)],
                           cwd=native_dir, stdout=log, stderr=subprocess.STDOUT, check=True)
    assert review.members(project) == revised
    output = review.members(native)
    gcode = output[GCODE]
    program = gcode.decode()
    assert hashlib.md5(gcode).hexdigest() == output[GCODE + ".md5"].decode().strip().lower()
    effective = json.loads(output[SETTING])
    for field in ("wall_loops", "top_one_wall_type", "only_one_wall_first_layer", "top_shell_layers",
                  "bottom_shell_layers", "sparse_infill_density", "filament_nozzle_map", "filament_flow_ratio",
                  "curr_bed_type", "nozzle_temperature", "eng_plate_temp", "chamber_temperatures",
                  "enable_support", "skirt_loops", "brim_type", "machine_start_gcode"):
        assert effective[field] == selected[field], (field, effective[field], selected[field])
    native_model = ET.fromstring(output["3D/3dmodel.model"])
    native_component = native_model.find(f".//{{{CORE}}}component")
    native_member = native_component.get(f"{{{PROD}}}path").lstrip("/")
    native_mesh = ET.fromstring(output[native_member])
    native_vertices = np.array([[float(v.get(a)) for a in "xyz"]
                                for v in native_mesh.findall(f".//{{{CORE}}}vertex")])
    assert native_vertices.shape == vertices.shape
    delta = float(np.abs(native_vertices - vertices).max())
    assert delta < 1e-6
    assert [t.attrib for t in native_mesh.findall(f".//{{{CORE}}}triangle")] == [
        t.attrib for t in embedded.findall(f".//{{{CORE}}}triangle")]
    assert cKDTree(mesh.vertices).query(native_vertices + [0, 0, geometry.height / 2])[0].max() < 1e-6
    parent_startup = review.members(ROOT / prior["archive"])[GCODE].decode().split("; MACHINE_START_GCODE_END")[0]
    startup = program.split("; MACHINE_START_GCODE_END")[0]
    assert commands(startup.replace("X110 Y14 I181 J154", "X110 Y14 I181 J146")) == commands(parent_startup)
    def priming_block(text):
        return text.rsplit(";===== ASA Aero bed priming strip =====", 1)[1].split(";===== ASA Aero bed priming strip end =====")[0]
    assert sha(ROOT / prior["archive"]) == prior["archive_sha256"]
    assert commands(priming_block(startup)) == commands(priming_block(parent_startup))
    trims = [float(v) for v in re.findall(r"^\s*G29\.1 Z([-+.\d]+)", program, re.M)]
    assert trims == [0.0, 0.04]
    summary = json.loads((native_dir / "result.json").read_text())["sliced_plates"][0]
    assert not summary["warning_message"] and len(summary["objects"]) == 1
    roads, travels, retracts = review.roads_and_travels(program)
    assert roads and len({r["object"] for r in roads}) == 1
    features = Counter(r["feature"] for r in roads)
    assert set(features) <= {"Inner wall", "Outer wall", "Overhang wall", "Gap infill"}, features
    coverage = review.coverage_review(roads, mesh)
    pause = magnet_pause_review(program, mesh)
    ready = JOB / "ready"
    ready.mkdir(exist_ok=True)
    archive = ready / NAME
    if archive.exists(): assert archive.read_bytes() == native.read_bytes()
    else: shutil.copyfile(native, archive)
    archive.chmod(0o444)
    (ready / "plate_1.gcode").write_bytes(gcode)
    (RECORDS / "native-preview.png").write_bytes(output["Metadata/plate_1.png"])
    render(roads, pause)
    mass = sum(r["extrusion_mm"] for r in roads) * math.pi * (1.75 / 2) ** 2 * 0.99 / 1000
    design = json.loads((HERE / "design.json").read_text())
    source_paths = [HERE / "all_aero_float.py", HERE / "design.json", HERE / "prepare_print.py", HELPER]
    record = {"article": "All-ASA Aero magnetic float with RC62 insertion pause", "printer": "Mark2",
              "status": "prepared_not_submitted", "send_attempts": 0, "preview_inspected": False,
              "source_commit": None, "source_snapshot": {str(p.relative_to(ROOT)): sha(p) for p in source_paths},
              "source_stl_sha256": {"float-aero": sha(HERE / "float-aero.stl")},
              "source_step_sha256": sha(HERE / "float-aero.step"),
              "recipe_project": prior["project"], "recipe_project_sha256": prior["project_sha256"],
              "project": str(project.relative_to(ROOT)), "project_sha256": sha(project),
              "archive": str(archive.relative_to(ROOT)), "archive_sha256": sha(archive),
              "gcode_sha256": hashlib.sha256(gcode).hexdigest(),
              "slicer_version": re.search(r"^; BambuStudio ([^\n]+)", program, re.M)[1],
              "native_mesh_vertex_max_delta_mm": delta, "native_triangle_connectivity_retained": True,
              "native_geometry_matches_frozen_stl": True, "center_xy_mm": [150, 145], "bed_z_mm": 0,
              "bed": "Engineering Plate, with glue", "requested_z_trim_mm": 0.04,
              "emitted_z_trim_commands_mm": trims, "native_recipe_retained": True,
              "adaptive_leveling_bounds_mm": {"x_min": 110, "x_max": 291, "y_min": 14, "y_max": 168},
              "startup_printing_commands_retained_except_leveling_bounds": True,
              "corner_priming_strip_printing_commands_retained": True,
              "corner_priming_strip_progress_estimates": "Native M73 progress estimates differ; motion, extrusion and heating commands are retained.",
              "recipe": {"wall_loops": 300, "top_shell_layers": 0, "bottom_shell_layers": 0,
                         "sparse_infill_density_percent": 0, "layer_height_mm": 0.2, "line_width_mm": 0.48,
                         "flow_ratio": 0.52, "nozzle_c": 270, "bed_c": 90, "chamber_c": 60},
              "material_mapping": {"material": "Bambu ASA Aero White 46100", "filament_id": "GFB02",
                                   "source": "Polymaker drybox", "external_slot": 255,
                                   "nozzle": "right fixed hardened standard-flow 0.4 mm",
                                   "send_dialog_tile_required": "Ext ASA-AERO R", "send_dialog_verified": False},
              "native_slice_summary": {"estimated_time_s": summary["total_predication"],
                                       "filament_mass_g": summary["filaments"][0]["total_used_g"],
                                       "object_feed_mass_g": mass,
                                       "feed_mass_per_cad_foam_volume_g_cc": mass / design["volumes_cc"]["asa_aero"],
                                       "scope": "Slicer/feed accounting excludes magnet, startup waste and firmware extrusion; it is not measured foam density.",
                                       "object_count": 1, "warnings": []},
              "path_features": dict(features), "layers": len({r["layer"] for r in roads}),
              "coverage_review": coverage, "travel_review": review.travel_review(roads, travels, retracts),
              "magnet_pause_review": pause, "skirt_paths": 0, "brim_paths": 0, "support_paths": 0,
              "prepared_utc": datetime.now(timezone.utc).isoformat(),
              "physical_print_completed": False, "density_verified": False, "buoyancy_verified": False}
    (RECORDS / "float-preflight.json").write_text(json.dumps(record, indent=2) + "\n")
    print(json.dumps({"archive": record["archive"], "minutes": summary["total_predication"] / 60,
                      "pause": pause, "features": dict(features)}, indent=2))


if __name__ == "__main__":
    main()
