"""Manually inspect the provisional native slice; this does not send a print."""
from collections import defaultdict
from pathlib import Path
from types import SimpleNamespace
import ast
import hashlib
import json
import math
import re
import shutil
import sys
import xml.etree.ElementTree as ET
import zipfile

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from shapely.geometry import LineString
from shapely.ops import unary_union
import trimesh

HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p / "tools/bambu_print.py").exists())
WORK = ROOT / ".cache/printer-control/faucet-scarf-swatches-v1"
sys.path.insert(0, str(ROOT / "hardware/scripts"))
from verify_round_layer_band import wall_layers, check_span


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save(path, value):
    path.write_text(json.dumps(value, indent=2) + "\n")


def pure_reader(file, name):
    # Reuse the G-code readers without importing CAD and its generation lock.
    tree = ast.parse(file.read_text())
    function = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == name)
    env = dict(Path=Path, np=np, sys=sys, re=re, math=math, writer=SimpleNamespace(ROOT=ROOT))
    exec(compile(ast.Module(body=[function], type_ignores=[]), str(file), "exec"), env)
    return env[name]


def transform(points, text):
    tf = np.array([float(x) for x in text.split()]).reshape(4, 3)
    return points @ tf[:3] + tf[3]


def main():
    prep = json.loads((HERE / "preparation.json").read_text())
    plan = json.loads((HERE / "study-plan.json").read_text())
    assert prep["preparation_only"] and not plan["launch_authorized"]
    assert not any(plan[k] for k in ("import_attempted", "send_attempted", "accepted"))
    project = ROOT / prep["project"]
    native = WORK / (project.stem + ".gcode.3mf")
    assert sha(project) == prep["project_sha256"]
    assert sha(ROOT / prep["settings_source"]) == prep["settings_source_sha256"]
    assert sha(ROOT / prep["source_step"]) == prep["source_step_sha256"]
    assert sha(ROOT / prep["source_stl"]) == prep["source_stl_sha256"]
    assert sha(ROOT / prep["shipping_reference"]) == prep["shipping_reference_sha256"]
    geometry = []
    with zipfile.ZipFile(native) as arc, zipfile.ZipFile(project) as source:
        assert arc.testzip() is None
        payload = arc.read("Metadata/plate_1.gcode")
        gcode_sha = hashlib.sha256(payload).hexdigest()
        assert arc.read("Metadata/plate_1.gcode.md5").decode().strip().lower() == hashlib.md5(payload).hexdigest()
        gcode = payload.decode()
        (WORK / "native.gcode").write_bytes(payload)
        settings = json.loads(arc.read("Metadata/project_settings.config"))
        expected = json.loads(source.read("Metadata/project_settings.config"))
        normalizations = {k: [expected.get(k), settings.get(k)] for k in set(expected) | set(settings)
                          if expected.get(k) != settings.get(k)}
        allowed = {"filament_prime_volume": [["30"], ["45"]], "filament_map_2": [None, ["1"]]}
        assert all(k in allowed and v == allowed[k] for k, v in normalizations.items()), normalizations
        with zipfile.ZipFile(ROOT / prep["settings_source"]) as parent:
            assert source.read("Metadata/project_settings.config") == parent.read("Metadata/project_settings.config")
        assert settings["curr_bed_type"] == "Textured PEI Plate"
        assert settings["support_type"] == "tree(auto)" and settings["support_style"] == "default"
        assert settings["support_top_z_distance"] == "0.45"
        assert settings["enable_wrapping_detection"] == "0" and settings["wrapping_detection_gcode"] == ""
        assert not re.search(r"^\s*G39(?:\s|;|$)", gcode, re.M)
        trims = [float(x) for x in re.findall(r"^\s*G29\.1 Z([-+.\d]+)", gcode, re.M)]
        assert trims == [0., .02], trims
        cfg = ET.fromstring(arc.read("Metadata/model_settings.config"))
        assert not cfg.findall(".//part[@subtype='negative_part']")
        assert not cfg.findall(".//part[@subtype='modifier_part']")
        objects = {next(m.get("value") for m in o.findall("metadata") if m.get("key") == "name"): o
                   for o in cfg.findall("object")}
        assert set(objects) == {s["name"] for s in prep["specimens"]}
        ns = {"m": "http://schemas.microsoft.com/3dmanufacturing/core/2015/02"}
        prod = "http://schemas.microsoft.com/3dmanufacturing/production/2015/06"
        model = ET.fromstring(arc.read("3D/3dmodel.model"))
        resources = {o.get("id"): o for o in model.findall("m:resources/m:object", ns)}
        builds = {b.get("objectid"): b for b in model.findall("m:build/m:item", ns)}
        for part, specimen in zip(prep["parts"], prep["specimens"], strict=True):
            stl = ROOT / part["source"]
            assert sha(stl) == part["stl_sha256"]
            mesh = trimesh.load(stl, force="mesh", process=True)
            obj = objects[part["name"]]
            meta = {m.get("key"): m.get("value") for m in obj.findall("metadata")}
            for k, v in specimen["object_overrides"].items():
                assert meta[k] == v, (part["name"], k, meta.get(k), v)
            normal = obj.find("part[@subtype='normal_part']")
            component = next(c for c in resources[obj.get("id")].findall("m:components/m:component", ns)
                             if c.get("objectid") == normal.get("id"))
            child = ET.fromstring(arc.read(component.get("{" + prod + "}path").lstrip("/")))
            geo = child.find("m:resources/m:object[@id='" + normal.get("id") + "']/m:mesh", ns)
            vertices = np.array([[float(v.get(a)) for a in "xyz"] for v in geo.find("m:vertices", ns)])
            faces = np.array([[int(v.get(a)) for a in ("v1", "v2", "v3")] for v in geo.find("m:triangles", ns)])
            assert np.array_equal(faces, mesh.faces)
            placed = transform(transform(vertices, component.get("transform", "1 0 0 0 1 0 0 0 1 0 0 0")),
                               builds[obj.get("id")].get("transform"))
            target = transform(mesh.vertices - np.array(part["source_center_mm"]), " ".join(map(str, part["build_transform"])))
            error = float(np.abs(placed - target).max())
            assert error < 1e-4, (part["name"], error)
            geometry.append(dict(id=specimen["id"], native_vertex_rounding_maximum_mm=error,
                                 triangle_indices_identical=True, source_stl_sha256=sha(stl)))
        for member, target in (("Metadata/plate_1.png", "native-preview.png"), ("Metadata/top_1.png", "native-top.png")):
            (HERE / target).write_bytes(arc.read(member))

    native_result = json.loads((WORK / "result.json").read_text())
    assert native_result["return_code"] == 0 and len(native_result["sliced_plates"]) == 1
    plate = native_result["sliced_plates"][0]
    assert not plate["warning_message"], plate["warning_message"]
    layer_checks = []
    for specimen in prep["specimens"]:
        layers = wall_layers(native, specimen["identify_id"])
        lo, hi = specimen["layer_band_print_z_mm"]
        reading = check_span(layers, specimen["name"], lo, hi, specimen["fine_layer_height_mm"], .001)
        assert reading["pass"], reading
        layer_checks.append(reading)
    bounds_reader = pure_reader(ROOT / "hardware/printed-parts/faucet/refresh_print_project.py", "object_toolpaths")
    bounds = bounds_reader(WORK / "native.gcode", WORK / "all-layer-beads.gcode", None)
    lo, hi = np.array(bounds["extrusion_bounds_xy_mm"])
    margin = float(min(np.min(lo), np.min(np.array([325, 320]) - hi)))
    assert margin >= 40, bounds

    segment_reader = pure_reader(ROOT / "hardware/printed-parts/faucet/prepare_display_print.py", "extrusion_segments")
    first, second = defaultdict(list), defaultdict(list)
    support_count = defaultdict(int)
    ramps, starts, lengths = defaultdict(list), defaultdict(list), defaultdict(lambda: defaultdict(float))
    lookup = {s["identify_id"]: s for s in prep["specimens"]}
    for segment in segment_reader(WORK / "native.gcode"):
        oid, z, kind = segment["object"], segment["layer"], segment["feature"]
        if kind.startswith("Support"):
            support_count[oid] += 1
        if abs(z - .2) < 1e-5 or abs(z - .44) < 1e-5:
            bead = LineString([segment["a"][:2], segment["b"][:2]]).buffer(segment["width"] / 2, quad_segs=4)
            if abs(z - .2) < 1e-5:
                first[oid].append(bead)
            elif kind in ("Outer wall", "Inner wall", "Overhang wall"):
                second[oid].append(bead)
        if oid in lookup and 4.04 < z <= 16.04 and kind == "Outer wall":
            za, zb = segment["a"][2], segment["b"][2]
            if abs(za - z) > 1e-5 or abs(zb - z) > 1e-5:
                ramps[oid].append([z, za, zb])
                starts[oid].append(min(za, zb) - (z - .08))
                lengths[oid][z] += math.dist(segment["a"][:2], segment["b"][:2])
    assert not support_count, support_count
    first_second, scarf_checks = [], []
    fig, ax = plt.subplots(figsize=(9, 9))
    for index, specimen in enumerate(prep["specimens"]):
        oid = specimen["identify_id"]
        bed, walls = unary_union(first[oid]), unary_union(second[oid])
        assert not bed.is_empty and not walls.is_empty
        overlap = [bead.intersection(bed).area / bead.area for bead in second[oid]]
        assert all(a > 1e-9 for a in overlap), specimen["id"]
        first_second.append(dict(id=specimen["id"], second_wall_segments=len(overlap),
                                 no_first_layer_overlap_segments=sum(a <= 1e-9 for a in overlap),
                                 minimum_segment_overlap_fraction=min(overlap),
                                 total_second_wall_footprint_overlap_fraction=walls.intersection(bed).area / walls.area))
        control = specimen["regular_seam_control"]
        if control:
            assert not ramps[oid], specimen["id"]
        else:
            assert ramps[oid], specimen["id"]
            assert abs(min(starts[oid]) - specimen["fine_start_height_mm"]) <= .00051, (specimen["id"], min(starts[oid]))
        scarf_checks.append(dict(id=specimen["id"], ordinary_control=control,
                                 fine_outer_wall_Z_ramp_segment_count=len(ramps[oid]),
                                 expected_start_above_previous_layer_mm=specimen["fine_start_height_mm"],
                                 lowest_emitted_start_above_previous_layer_mm=min(starts[oid]) if starts[oid] else None,
                                 requested_scarf_length_mm=specimen["scarf_length_mm"],
                                 first_fine_layer_ramping_deposition_xy_length_mm=lengths[oid].get(4.12, 0),
                                 witnesses=ramps[oid][:4]))
        polygons = list(bed.geoms) if hasattr(bed, "geoms") else [bed]
        color = "#777777" if control else plt.get_cmap("viridis")(specimen["scarf_start_height_percent"] / 30)
        for polygon in polygons:
            x, y = polygon.exterior.xy
            ax.fill(x, y, color=color, alpha=.7)
            for hole in polygon.interiors:
                x, y = hole.xy
                ax.fill(x, y, color="white")
        x, y = bed.centroid.x, bed.centroid.y
        detail = "regular" if control else f"{specimen['scarf_length_mm']} / {specimen['scarf_start_height_percent']}%"
        ax.text(x, y, specimen["id"] + "\n" + detail, ha="center", va="center", fontsize=8, weight="bold")
    ax.plot([40, 285, 285, 40, 40], [40, 40, 280, 280, 40], "k--", lw=1)
    ax.set(xlim=(0, 325), ylim=(0, 320), xlabel="Printer X (mm)", ylabel="Printer Y (mm)",
           title=f"Provisional scarf swatches: {margin:.1f} mm full-bead edge clearance\nNative first-layer beads; front is bottom; labels identify length (mm) / start height (%)")
    ax.set_aspect("equal")
    fig.tight_layout()
    fig.savefig(HERE / "plate-layout.png", dpi=150)
    plt.close(fig)
    destination = HERE / native.name
    shutil.copyfile(native, destination)
    report = dict(schema=1, preparation_only=True, archive=str(destination.relative_to(ROOT)), archive_sha256=sha(native),
                  gcode_sha256=gcode_sha, prepared_project=prep["project"], prepared_project_sha256=sha(project),
                  geometry=geometry, inherited_global_settings_identical_to_accepted_faucet=True,
                  native_settings_normalizations=normalizations, layer_band_checks=layer_checks,
                  complete_model_support_brim_bead_bounds=bounds, minimum_full_bead_bed_margin_mm=margin,
                  first_second_layer_overlap=first_second, support_deposition_segment_count=0,
                  scarf_checks=scarf_checks, requested_Z_trim_mm=.04, emitted_Z_trim_commands_mm=trims,
                  probing_clump_detection=False, gcode_postprocessed=False,
                  native_estimated_seconds=plate["total_predication"],
                  native_estimated_grams_saved_profile_density=sum(f["total_used_g"] for f in plate["filaments"]),
                  scope="Native geometry, layer heights, bead footprints and scarf emission. Physical results pending; preparation grants no launch authorization.",
                  **{"pass": True})
    save(HERE / "native-check.json", report)
    shutil.copyfile(WORK / "result.json", HERE / "native-result.json")
    for record in (prep, plan):
        record.update(native_archive=report["archive"], native_archive_sha256=report["archive_sha256"],
                      gcode_sha256=gcode_sha, native_estimated_seconds=report["native_estimated_seconds"],
                      native_estimated_grams_saved_profile_density=report["native_estimated_grams_saved_profile_density"],
                      minimum_full_bead_bed_margin_mm=margin,
                      native_check=str((HERE / "native-check.json").relative_to(ROOT)), native_check_sha256=sha(HERE / "native-check.json"))
    save(HERE / "preparation.json", prep)
    save(project.with_suffix(".print.json"), prep)
    save(HERE / "study-plan.json", plan)
    print(json.dumps(dict(margin_mm=margin, seconds=report["native_estimated_seconds"],
                         grams=report["native_estimated_grams_saved_profile_density"], scarf_checks=scarf_checks,
                         preparation_only=True), indent=2))


if __name__ == "__main__":
    main()
