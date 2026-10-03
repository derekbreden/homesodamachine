"""Prepare frozen float pieces separately with filled nested wall paths."""

import copy
import hashlib
import json
import math
import re
import shutil
import subprocess
import xml.etree.ElementTree as ET
import zipfile
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import trimesh
from scipy.spatial import cKDTree
from shapely.geometry import LineString, Polygon
from shapely.ops import linemerge, unary_union

HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p / "tools/bambu_printer.py").is_file())
FLOAT = HERE.parent.parent
BASE = HERE.parent / "v6/pair-preflight.json"
STUDIO = Path("/Applications/BambuStudio.app/Contents/MacOS/BambuStudio")
CORE = "http://schemas.microsoft.com/3dmanufacturing/core/2015/02"
PROD = "http://schemas.microsoft.com/3dmanufacturing/production/2015/06"
SETTING = "Metadata/project_settings.config"
GCODE = "Metadata/plate_1.gcode"
NATIVE_REVISION = 8
ET.register_namespace("", CORE)
ET.register_namespace("p", PROD)
ET.register_namespace("BambuStudio", "http://schemas.bambulab.com/package/2021")


def digest(data):
    return hashlib.sha256(data).hexdigest()


def members(path):
    with zipfile.ZipFile(path) as z:
        assert z.testzip() is None
        return {n: z.read(n) for n in z.namelist()}


def metadata(element):
    return {e.get("key"): e.get("value") for e in element.findall("metadata")}


def roads_and_travels(program):
    """Read explicit object G0/G1 moves; firmware-generated motion is excluded."""
    xyz = np.zeros(3)
    e = feed = width = 0.0
    absolute_xyz, relative_e = True, True
    obj, layer, feature = None, None, ""
    roads, travels, retracts = [], [], []
    deposited_layers = set()
    for raw in program.splitlines():
        if raw.startswith("; OBJECT_ID:"):
            obj = int(raw.split(":", 1)[1])
        elif raw.startswith("; Z_HEIGHT:"):
            layer = float(raw.split(":", 1)[1])
            obj = None
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
            delta_e = values.get("E", 0) if relative_e else values.get("E", e) - e
            feed = values.get("F", feed)
            distance = float(np.linalg.norm(target[:2] - xyz[:2]))
            if obj is not None and layer is not None:
                if delta_e > 1e-9 and distance > 1e-6:
                    assert command in ("G0", "G1"), "Arc fitting must remain disabled."
                    roads.append({"object": obj, "layer": layer, "feature": feature,
                                  "width": width, "a": tuple(xyz[:2]), "b": tuple(target[:2]),
                                  "extrusion_mm": delta_e, "speed_mm_s": feed / 60,
                                  "feed_volume_mm3_s": delta_e * math.pi * (1.75 / 2) ** 2
                                  * feed / 60 / distance})
                    deposited_layers.add(layer)
                elif distance > 1e-6 and delta_e <= 1e-9:
                    travels.append({"object": obj, "layer": layer, "distance_mm": distance,
                                    "before_first_deposition_on_layer": layer not in deposited_layers,
                                    "a": tuple(xyz[:2]), "b": tuple(target[:2]),
                                    "z_lift_mm": float(target[2] - xyz[2])})
                if delta_e < -1e-9:
                    retracts.append({"object": obj, "layer": layer, "filament_mm": -delta_e})
            xyz = target
            if "E" in values:
                e = e + values["E"] if relative_e else values["E"]
    return roads, travels, retracts


def travel_review(roads, travels, retracts):
    within_layer = [m for m in travels if not m["before_first_deposition_on_layer"]]
    by_layer = defaultdict(list)
    for move in travels:
        by_layer[move["layer"]].append(move["distance_mm"])
    samples = {str(z): {"xy_move_count": len(by_layer[z]),
                       "xy_distance_mm": sum(by_layer[z]),
                       "longest_xy_move_mm": max(by_layer[z], default=0)}
               for z in sorted({roads[0]["layer"], roads[len(roads) // 2]["layer"], roads[-1]["layer"]})}
    return {"explicit_object_xy_travel_move_count": len(travels),
            "explicit_object_xy_travel_distance_mm": sum(m["distance_mm"] for m in travels),
            "longest_explicit_object_xy_travel_mm": max((m["distance_mm"] for m in travels), default=0),
            "moves_longer_than_5_mm": sum(m["distance_mm"] > 5 for m in travels),
            "within_layer_xy_move_count": len(within_layer),
            "within_layer_xy_distance_mm": sum(m["distance_mm"] for m in within_layer),
            "longest_within_layer_xy_move_mm": max((m["distance_mm"] for m in within_layer), default=0),
            "object_retraction_count": len(retracts), "sample_layers": samples,
            "zero_travel": not travels,
            "scope": "Explicit object G0/G1 moves with no positive extrusion, including retraction wipes and initial positioning. The first transfer from the startup strip is included in total travel, and excluded from within-layer travel. Firmware motion, timelapse internals and moves outside object labels are excluded. Ring transitions, seam positioning and layer changes can still require travel."}


def coverage_review(roads, mesh):
    heights = sorted({r["layer"] for r in roads})
    selected = sorted({heights[0], heights[1], heights[len(heights) // 2], heights[-1]})
    result = []
    for height in selected:
        section = trimesh.intersections.mesh_plane(
            mesh, plane_origin=[0, 0, height - 0.0001], plane_normal=[0, 0, 1])
        assert len(section)
        loops = linemerge([LineString(np.round(edge[:, :2], 9)) for edge in section])
        contours = [loops] if loops.geom_type == "LineString" else list(loops.geoms)
        nominal = Polygon()
        for contour in contours:
            assert contour.is_ring
            nominal = nominal.symmetric_difference(Polygon(contour))
        # Retained +0.05 contour / -0.05 hole compensation expands solid by 0.05.
        from shapely.affinity import translate
        nominal = translate(nominal.buffer(0.05), 150, 145)
        layer_roads = [r for r in roads if r["layer"] == height]
        beads = unary_union([LineString((r["a"], r["b"])).buffer(r["width"] / 2)
                             for r in layer_roads])
        fraction = beads.intersection(nominal).area / nominal.area
        result.append({"layer_z_mm": height, "nominal_solid_area_mm2": nominal.area,
                       "bead_footprint_coverage_fraction": fraction,
                       "scope": "Idealized native bead footprints against compensated frozen STL section; this does not model actual foaming or establish physical density."})
        assert fraction > 0.97, (height, fraction)
    return result


def prepare(part, baseline):
    key = "core" if part == "body-aero" else "insert"
    job = ROOT / f".cache/prints/magnetic-float-{key}-mark2-aero-v{NATIVE_REVISION}"
    original = members(ROOT / baseline["project"])
    settings = json.loads(original[SETTING])
    selected = copy.deepcopy(settings)
    selected.pop("only_one_wall_top", None)
    selected.update(wall_loops="300", top_one_wall_type="not apply", only_one_wall_first_layer="0", top_shell_layers="0",
                    bottom_shell_layers="0", top_shell_thickness="0", bottom_shell_thickness="0",
                    sparse_infill_density="0%")
    changes = {k: {"source": settings.get(k), "selected": value}
               for k, value in selected.items() if settings.get(k) != value}
    config = ET.fromstring(original["Metadata/model_settings.config"])
    obj = next(o for o in config.findall("object") if metadata(o.find("part"))["name"] == part)
    oid = obj.get("id")
    plate, = config.findall("plate")
    for other in list(config):
        if other is not plate and other is not obj:
            config.remove(other)
    for instance in list(plate.findall("model_instance")):
        if metadata(instance)["object_id"] != oid:
            plate.remove(instance)
    for item in plate.findall("metadata"):
        if item.get("key") == "plater_name":
            item.set("value", f"ASA Aero {key} nested walls")
    assert metadata(obj)["xy_contour_compensation"] == "0.05"
    assert metadata(obj)["xy_hole_compensation"] == "-0.05"
    model = ET.fromstring(original["3D/3dmodel.model"])
    model.set("xmlns:BambuStudio", "http://schemas.bambulab.com/package/2021")
    resources = model.find(f"{{{CORE}}}resources")
    build = model.find(f"{{{CORE}}}build")
    for resource in list(resources):
        if resource.get("id") != oid:
            resources.remove(resource)
    for item in list(build):
        if item.get("objectid") != oid:
            build.remove(item)
    item, = list(build)
    transform = item.get("transform").split()
    transform[9:11] = ["150", "145"]
    item.set("transform", " ".join(transform))
    component = resources.find(f".//{{{CORE}}}component")
    member = component.get(f"{{{PROD}}}path").lstrip("/")
    embedded = ET.fromstring(original[member])
    vertices = np.array([[float(v.get(a)) for a in "xyz"]
                         for v in embedded.findall(f".//{{{CORE}}}vertex")])
    mesh = trimesh.load(FLOAT / f"{part}.stl", force="mesh", process=True)
    errors = cKDTree(mesh.vertices).query(vertices + [0, 0, float(transform[11])])[0]
    assert errors.max() < 1e-6
    assert abs(vertices[:, 2].min() + float(transform[11])) < 1e-6
    relationships = ET.fromstring(original["3D/_rels/3dmodel.model.rels"])
    for relation in list(relationships):
        if relation.get("Target").lstrip("/") != member:
            relationships.remove(relation)
    revised = {n: b for n, b in original.items()
               if not n.startswith("3D/Objects/") or n == member}
    revised[SETTING] = json.dumps(selected).encode()
    revised["Metadata/model_settings.config"] = ET.tostring(config, encoding="UTF-8", xml_declaration=True)
    revised["3D/3dmodel.model"] = ET.tostring(model, encoding="UTF-8", xml_declaration=True)
    revised["3D/_rels/3dmodel.model.rels"] = ET.tostring(
        relationships, encoding="UTF-8", xml_declaration=True).replace(b"ns0:", b"").replace(b"xmlns:ns0=", b"xmlns=")
    project = job / f"magnetic-float-{key}-mark2-aero-v{NATIVE_REVISION}-input.3mf"
    native_dir = job / "native"
    native = native_dir / f"magnetic-float-{key}-mark2-aero-v{NATIVE_REVISION}.gcode.3mf"
    if not native.exists():
        assert not job.exists(), "Inspect incomplete preparation before retrying."
        native_dir.mkdir(parents=True)
        with zipfile.ZipFile(project, "x", zipfile.ZIP_DEFLATED) as z:
            for name, data in revised.items():
                z.writestr(name, data)
        print(f"Slicing {part}, 300 walls, no surface or infill passes", flush=True)
        with (job / "slice.log").open("w") as log:
            subprocess.run([str(STUDIO), "--arrange", "0", "--orient", "0", "--slice", "0",
                            "--export-3mf", native.name, "--outputdir", str(native_dir), str(project)],
                           cwd=native_dir, stdout=log, stderr=subprocess.STDOUT, check=True)
    assert members(project) == revised
    output = members(native)
    gcode = output[GCODE]
    assert hashlib.md5(gcode).hexdigest() == output[GCODE + ".md5"].decode().strip().lower()
    effective = json.loads(output[SETTING])
    normalizations = {field: {"input": wanted, "native": effective.get(field)}
                      for field, wanted in selected.items() if effective.get(field) != wanted}
    permitted = {"best_object_pos", "enable_long_retraction_when_cut", "extruder_height_gap",
                 "extruder_clearance_radius", "deretract_speed_extruder_change",
                 "unprintable_filament_types", "adaptive_layer_height", "bottom_surface_density",
                 "monotonic_travel_into_wall", "infill_lock_depth", "layer_time_smoothing",
                 "layer_time_smoothing_threshold", "only_one_wall_top", "skin_infill_depth",
                 "support_ironing_inset", "top_surface_density", "wall_infill_order",
                 "fuzzy_skin_scale", "filament_dev_chamber_drying_bed_temperature",
                 "filament_dev_chamber_drying_time", "filament_long_retractions_when_ec",
                 "filament_prime_volume", "filament_retraction_distances_when_ec",
                 "filament_ingredients_safe", "filament_emission_safe", "filament_contact_safe", "name"}
    assert set(normalizations) <= permitted, normalizations
    # Verify executed startup rather than relying on normalized legacy fields.
    parent_gcode = members(ROOT / baseline["archive"])[GCODE]
    def printing_commands(program):
        return [line.strip() for line in program.splitlines()
                if line.strip() and not line.lstrip().startswith((b";", b"M73 "))]
    startup = gcode.split(b"; MACHINE_START_GCODE_END")[0]
    prior_startup = parent_gcode.split(b"; MACHINE_START_GCODE_END")[0]
    assert printing_commands(startup) == printing_commands(prior_startup)
    assert effective["wall_loops"] == "300"
    assert effective["top_one_wall_type"] == "not apply"
    assert effective["only_one_wall_first_layer"] == "0"
    for field in ("top_shell_layers", "bottom_shell_layers", "top_shell_thickness", "bottom_shell_thickness"):
        assert float(effective[field]) == 0
    assert effective["sparse_infill_density"] == "0%"
    native_model = ET.fromstring(output["3D/3dmodel.model"])
    native_component = native_model.find(f".//{{{CORE}}}component")
    native_member = native_component.get(f"{{{PROD}}}path").lstrip("/")
    native_mesh = ET.fromstring(output[native_member])
    native_vertices = np.array([[float(v.get(a)) for a in "xyz"]
                                for v in native_mesh.findall(f".//{{{CORE}}}vertex")])
    assert native_vertices.shape == vertices.shape
    native_vertex_delta = float(np.abs(native_vertices - vertices).max())
    assert native_vertex_delta < 1e-6
    assert [v.attrib for v in native_mesh.findall(f".//{{{CORE}}}triangle")] == [
        v.attrib for v in embedded.findall(f".//{{{CORE}}}triangle")]
    assert effective["filament_nozzle_map"] == ["1"]
    assert effective["filament_flow_ratio"] == ["0.52"]
    assert effective["curr_bed_type"] == "Engineering Plate"
    assert effective["nozzle_temperature"] == ["270"]
    assert effective["eng_plate_temp"] == ["90"]
    assert effective["chamber_temperatures"] == ["60"]
    trims = [float(v) for v in re.findall(rb"^\s*G29\.1 Z([-+.\d]+)", gcode, re.M)]
    assert trims == [0.0, 0.04]
    summary = json.loads((native_dir / "result.json").read_text())["sliced_plates"][0]
    assert not summary["warning_message"] and len(summary["objects"]) == 1
    roads, travels, retracts = roads_and_travels(gcode.decode())
    assert roads and {r["feature"] for r in roads} <= {"Inner wall", "Outer wall", "Overhang wall", "Gap infill"}
    assert len({r["object"] for r in roads}) == 1
    coverage = coverage_review(roads, mesh)
    ready = job / "ready"
    ready.mkdir(exist_ok=True)
    archive = ready / native.name
    if archive.exists():
        assert archive.read_bytes() == native.read_bytes()
    else:
        shutil.copyfile(native, archive)
    archive.chmod(0o444)
    (ready / "plate_1.gcode").write_bytes(gcode)
    (HERE / f"{key}-preview.png").write_bytes(output["Metadata/plate_1.png"])
    mass = sum(r["extrusion_mm"] for r in roads) * math.pi * (1.75 / 2) ** 2 * 0.99 / 1000
    counts = Counter(r["feature"] for r in roads)
    record = {"printer": "Mark2", "part": part, "quantity": 1,
              "physical_trial_revision": 7, "native_archive_revision": NATIVE_REVISION,
              "status": "prepared_not_submitted", "submitted": False, "preview_inspected": False,
              "source_commit": baseline["source_commit"], "source_snapshot": baseline["source_snapshot"],
              "preparation_script_sha256": digest(Path(__file__).read_bytes()),
              "slicer_version": re.search(rb"^; BambuStudio ([^\n]+)", gcode, re.M)[1].decode(),
              "source_stl_sha256": {part: baseline["source_stl_sha256"][part]},
              "source_project": baseline["project"], "source_project_sha256": baseline["project_sha256"],
              "project": str(project.relative_to(ROOT)), "project_sha256": digest(project.read_bytes()),
              "archive": str(archive.relative_to(ROOT)), "archive_sha256": digest(archive.read_bytes()),
              "gcode_sha256": digest(gcode), "selected_recipe_changes": changes,
              "native_setting_normalizations": normalizations,
              "startup_printing_commands_identical_to_parent": True,
              "input_mesh_bytes_retained": revised[member] == original[member],
              "native_mesh_bytes_retained": output[native_member] == original[member],
              "input_mesh_member": member, "native_mesh_member": native_member,
              "native_vertex_max_coordinate_delta_mm": native_vertex_delta,
              "native_triangle_connectivity_retained": True,
              "embedded_vertex_error_mm": float(errors.max()),
              "orientation_retained": True, "center_xy_mm": [150, 145], "bed_z_mm": 0,
              "bed": "Engineering Plate", "requested_z_trim_mm": 0.04,
              "emitted_z_trim_commands_mm": trims,
              "material_mapping": {"physical_material": "Bambu ASA Aero White 46100", "filament_id": "GFB02",
                                   "nozzle": "right standard-flow hardened 0.4 mm",
                                   "physical_source": "Polymaker drybox, reported by user",
                                   "send_dialog_source_verified": False,
                                   "scope": "External feed must be verified in the actual Send dialog before any launch; AMS HT is not the requested source."},
              "native_slice_summary": {"estimated_time_s": summary["total_predication"],
                                       "filament_mass_g": summary["filaments"][0]["total_used_g"],
                                       "object_extrusion_mass_g": mass, "object_count": 1, "warnings": []},
              "path_features": dict(counts), "layers": len({r["layer"] for r in roads}),
              "coverage_review": coverage, "travel_review": travel_review(roads, travels, retracts),
              "maximum_commanded_cold_filament_volume_mm3_s": max(r["feed_volume_mm3_s"] for r in roads),
              "skirt_paths": 0, "brim_paths": 0, "support_paths": 0,
              "physical_adhesion_verified": False, "physical_fit_verified": False,
              "density_verified": False, "buoyancy_verified": False,
              "prepared_utc": datetime.now(timezone.utc).isoformat()}
    (HERE / f"{key}-preflight.json").write_text(json.dumps(record, indent=2) + "\n")
    print(json.dumps({"part": part, "estimate_minutes": summary["total_predication"] / 60,
                      "features": dict(counts), "travel": record["travel_review"],
                      "object_extrusion_mass_g": mass}), flush=True)


def render_paths():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.collections import LineCollection
    from matplotlib.lines import Line2D
    figure, axes = plt.subplots(1, 3, figsize=(12, 4.4))
    for axis, (key, height, title) in zip(axes, [("core", 22.2, "Core, middle"),
                                               ("core", 44.0, "Core, top / magnet pocket"),
                                               ("insert", 5.2, "Insert, middle")]):
        preflight = json.loads((HERE / f"{key}-preflight.json").read_text())
        program = members(ROOT / preflight["archive"])[GCODE].decode()
        roads, travels, _ = roads_and_travels(program)
        lines = [[(r["a"][0] - 150, r["a"][1] - 145),
                  (r["b"][0] - 150, r["b"][1] - 145)] for r in roads if r["layer"] == height]
        moves = [[(r["a"][0] - 150, r["a"][1] - 145),
                  (r["b"][0] - 150, r["b"][1] - 145)] for r in travels
                 if r["layer"] == height and not r["before_first_deposition_on_layer"]]
        axis.add_collection(LineCollection(lines, colors="#244867", linewidths=0.75))
        axis.add_collection(LineCollection(moves, colors="#d66023", linewidths=1.1, linestyles="dashed"))
        axis.set(xlim=(-16, 16), ylim=(-16, 16), aspect="equal", xlabel="X (mm)", ylabel="Y (mm)",
                 title=f"{title}\nZ = {height:g} mm")
        axis.grid(alpha=0.12)
    figure.legend([Line2D([0], [0], color="#244867"), Line2D([0], [0], color="#d66023", linestyle="--")],
                  ["Depositing wall paths", "Remaining non-depositing moves / wipes"],
                  loc="lower center", ncol=2, frameon=False)
    figure.tight_layout(rect=(0, 0.13, 1, 0.9))
    figure.savefig(HERE / "path-preview.png", dpi=180, bbox_inches="tight", pad_inches=0.15)
    plt.close(figure)


def main():
    baseline = json.loads(BASE.read_text())
    assert digest((ROOT / baseline["project"]).read_bytes()) == baseline["project_sha256"]
    assert digest((ROOT / baseline["archive"]).read_bytes()) == baseline["archive_sha256"]
    for part, frozen in baseline["source_stl_sha256"].items():
        assert digest((FLOAT / f"{part}.stl").read_bytes()) == frozen
    for path, wanted in baseline["source_snapshot"].items():
        saved = subprocess.check_output(["git", "show", baseline["source_commit"] + ":" + path], cwd=ROOT)
        assert digest(saved) == wanted, path
    for part in ("body-aero", "insert-aero"):
        prepare(part, baseline)
    render_paths()


if __name__ == "__main__":
    main()
