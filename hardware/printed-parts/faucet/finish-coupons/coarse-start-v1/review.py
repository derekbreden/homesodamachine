"""Manually inspect either prepared native plate; no launch or automatic gate."""
from collections import defaultdict
from pathlib import Path
from types import SimpleNamespace
import argparse
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
from shapely.geometry import LineString, Point
from shapely.ops import unary_union
import trimesh

HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p / "tools/bambu_print.py").exists())
WORK = ROOT / ".cache/printer-control/faucet-coarse-start-v1"
sys.path.insert(0, str(ROOT / "hardware/scripts"))
from verify_round_layer_band import wall_layers, check_span


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save(path, value):
    path.write_text(json.dumps(value, indent=2) + "\n")


def reader(file, name):
    tree = ast.parse(file.read_text())
    function = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == name)
    env = dict(Path=Path, np=np, sys=sys, re=re, math=math, writer=SimpleNamespace(ROOT=ROOT))
    exec(compile(ast.Module(body=[function], type_ignores=[]), str(file), "exec"), env)
    return env[name]


def transform(points, text):
    tf = np.array([float(x) for x in text.split()]).reshape(4, 3)
    return points @ tf[:3] + tf[3]


def seam_material(gcode, specimens):
    """Count emitted positive E on moving outer-wall commands, once per arc."""
    selected = {s["identify_id"]: s for s in specimens if s["kind"] == "scarf"}
    totals = defaultdict(float)
    oid, plane, feature, relative, extruder = None, None, None, True, 0.
    xy = [0., 0.]
    for line in gcode.splitlines():
        if line.startswith("; OBJECT_ID:"):
            oid = int(line.split(":", 1)[1])
        elif line.startswith("; Z_HEIGHT:"):
            plane = float(line.split(":", 1)[1])
        elif line.startswith("; FEATURE:"):
            feature = line.split(":", 1)[1].strip()
        code = line.split(";", 1)[0].strip()
        if not code:
            continue
        command = code.split()[0]
        if command in ("M82", "M83"):
            relative = command == "M83"
        words = {k: float(v) for k, v in re.findall(r"([XYE])([-+]?\d*\.?\d+(?:[eE][-+]?\d+)?)", code)}
        if command == "G92" and "E" in words:
            extruder = words["E"]
        if command not in ("G0", "G1", "G2", "G3"):
            continue
        end = [words.get("X", xy[0]), words.get("Y", xy[1])]
        de = words.get("E", 0.) if relative else words.get("E", extruder) - extruder
        if "E" in words:
            extruder = extruder + de if relative else words["E"]
        if oid in selected and feature == "Outer wall" and de > 0 and (end != xy or command in ("G2", "G3")):
            for target in (1.40, 4.12):
                if plane is not None and abs(plane - target) < 1e-5:
                    totals[oid, target] += de
        xy = end
    result = [dict(id=s["id"], method=s["seam_method"], gap_percent_of_nozzle=s["tested_gap_percent_of_nozzle"],
                   coarse_outer_wall_E_mm=round(totals[oid, 1.40], 6),
                   fine_outer_wall_E_mm=round(totals[oid, 4.12], 6)) for oid, s in selected.items()]
    for item in result:
        assert item["coarse_outer_wall_E_mm"] > 0 and item["fine_outer_wall_E_mm"] > 0, item
    for method in ("regular", "scarf"):
        values = [v["fine_outer_wall_E_mm"] for v in result if v["method"] == method]
        if values:
            assert max(values) - min(values) > 1e-5, (method, values)
    return dict(samples=result, coarse_nozzle_Z_mm=1.40, fine_nozzle_Z_mm=4.12,
                scope="Emitted positive filament length on moving outer-wall commands. Local gap changes are present in deposition; these totals do not predict physical seam height.")


def review(combined, seam_only=False):
    folder = HERE.parent / "seam-gap-swatches-v1" if seam_only else HERE / "combined" if combined else HERE
    work = ROOT / ".cache/printer-control/faucet-seam-gap-swatches-v1" if seam_only else WORK / ("combined" if combined else "lift")
    prep = json.loads((folder / "preparation.json").read_text())
    plan = json.loads((folder / "study-plan.json").read_text())
    assert prep["preparation_only"] and not plan["launch_authorized"]
    assert not any(plan[k] for k in ("import_attempted", "send_attempted", "accepted"))
    project = ROOT / prep["project"]
    native = work / (project.stem + ".gcode.3mf")
    assert sha(project) == prep["project_sha256"]
    assert sha(ROOT / prep["settings_source"]) == prep["settings_source_sha256"]
    assert sha(ROOT / prep["source_step"]) == prep["source_step_sha256"]
    assert sha(ROOT / prep["source_stl"]) == prep["source_stl_sha256"]
    assert sha(ROOT / prep["shipping_reference"]) == prep["shipping_reference_sha256"]
    geometries = []
    with zipfile.ZipFile(native) as arc, zipfile.ZipFile(project) as source:
        assert arc.testzip() is None
        payload = arc.read("Metadata/plate_1.gcode")
        gcode_sha = hashlib.sha256(payload).hexdigest()
        assert arc.read("Metadata/plate_1.gcode.md5").decode().strip().lower() == hashlib.md5(payload).hexdigest()
        gcode = payload.decode()
        (work / "native.gcode").write_bytes(payload)
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
            assert mesh.is_watertight and mesh.body_count == 1
            obj = objects[part["name"]]
            meta = {m.get("key"): m.get("value") for m in obj.findall("metadata")}
            for k, v in specimen["object_overrides"].items():
                assert meta[k] == str(v), (part["name"], k, meta.get(k), v)
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
            mods = obj.findall("part[@subtype='modifier_part']")
            assert len(mods) == (1 if specimen["kind"] == "lip" else 0)
            if mods:
                m = {n.get("key"): n.get("value") for n in mods[0].findall("metadata")}
                recorded_walls = prep.get("reinforcement_wall_loops", 6)
                assert m.get("wall_loops") == (str(recorded_walls) if recorded_walls is not None else None)
                assert m["sparse_infill_density"] == "100%" and m["sparse_infill_pattern"] == "zig-zag"
            geometries.append(dict(id=specimen["id"], native_vertex_rounding_maximum_mm=error,
                                   triangle_indices_identical=True, source_stl_sha256=sha(stl)))
        for member, target in (("Metadata/plate_1.png", "native-preview.png"), ("Metadata/top_1.png", "native-top.png")):
            (folder / target).write_bytes(arc.read(member))
    native_result = json.loads((work / "result.json").read_text())
    assert native_result["return_code"] == 0 and len(native_result["sliced_plates"]) == 1
    plate = native_result["sliced_plates"][0]
    assert not plate["warning_message"], plate["warning_message"]
    layers, coarse_checks = [], []
    for specimen in prep["specimens"]:
        walls = wall_layers(native, specimen["identify_id"])
        lo, hi = specimen["layer_band_print_z_mm"]
        # Verify the full declared interval, including the fine top layer
        # that ends at 25.04 while crossing the horizontal cut at 25.00.
        reading = check_span(walls, specimen["name"], lo, hi, specimen["fine_layer_height_mm"], .001)
        assert reading["pass"], reading
        layers.append(reading)
        if specimen["kind"] == "lip":
            count = specimen["requested_coarse_layers"]
            actual = [z for z, h in walls if 15.3199 <= z <= lo + .0001 and abs(h - .24) < .001]
            assert len(actual) == (count or 0), (specimen["id"], count, actual)
            first_fine = next([z, h] for z, h in walls if z > lo + .0001)
            assert abs(first_fine[1] - .12) < .001
            coarse_checks.append(dict(id=specimen["id"], requested_coarse_layers=count,
                                      last_starting_lip_first_coarse_nozzle_Z_mm=15.32,
                                      counted_coarse_nozzle_Z_mm=actual,
                                      coarse_count_from_last_starting_lip=len(actual),
                                      first_fine_model_layer=first_fine))
    bounds_reader = reader(ROOT / "hardware/printed-parts/faucet/refresh_print_project.py", "object_toolpaths")
    bounds = bounds_reader(work / "native.gcode", work / "all-layer-beads.gcode", None)
    lo, hi = np.array(bounds["extrusion_bounds_xy_mm"])
    margin = float(min(np.min(lo), np.min(np.array([325, 320]) - hi)))
    assert margin >= 40, bounds
    segment_reader = reader(ROOT / "hardware/printed-parts/faucet/prepare_display_print.py", "extrusion_segments")
    first, second, supports, models = defaultdict(list), defaultdict(list), defaultdict(list), defaultdict(list)
    support_count, ramps, starts = defaultdict(int), defaultdict(list), defaultdict(list)
    lookup = {s["identify_id"]: s for s in prep["specimens"]}
    part_lookup = {p["identify_id"]: p for p in prep["parts"]}
    source_probe = np.array([3., -math.sqrt(29.5**2 - 3.**2) * math.cos(math.radians(15)) + .30])
    for segment in segment_reader(work / "native.gcode"):
        oid, z, kind = segment["object"], segment["layer"], segment["feature"]
        if oid not in lookup:
            continue
        if kind.startswith("Support"):
            support_count[oid] += 1
        if abs(z - .2) < 1e-5 or abs(z - .44) < 1e-5:
            bead = LineString([segment["a"][:2], segment["b"][:2]]).buffer(segment["width"] / 2, quad_segs=4)
            if abs(z - .2) < 1e-5:
                first[oid].append(bead)
            elif kind in ("Outer wall", "Inner wall", "Overhang wall"):
                second[oid].append(bead)
        specimen = lookup[oid]
        if specimen["kind"] == "lip" and 11 < z <= 16:
            part = part_lookup[oid]
            xy = source_probe - np.array(part["source_center_mm"][:2]) + np.array(part["plate_translation_mm"][:2])
            # Actual bead overlap at a full-scale front-lip witness point.
            if LineString([segment["a"][:2], segment["b"][:2]]).distance(Point(xy)) <= segment["width"] / 2 + .01:
                (supports if kind.startswith("Support") else models)[oid].append([z, segment["height"], kind])
        if specimen["kind"] == "scarf" and 4.04 < z <= 16.04 and kind == "Outer wall":
            za, zb = segment["a"][2], segment["b"][2]
            if abs(za - z) > 1e-5 or abs(zb - z) > 1e-5:
                ramps[oid].append([z, za, zb])
                starts[oid].append(min(za, zb) - (z - .08))
    first_second, contacts, scarf_checks = [], [], []
    fig, ax = plt.subplots(figsize=(9, 9))
    for specimen in prep["specimens"]:
        oid = specimen["identify_id"]
        bed, walls = unary_union(first[oid]), unary_union(second[oid])
        assert not bed.is_empty and not walls.is_empty, specimen["id"]
        overlap = [bead.intersection(bed).area / bead.area for bead in second[oid]]
        assert all(a > 1e-9 for a in overlap), (specimen["id"], min(overlap))
        first_second.append(dict(id=specimen["id"], second_wall_segments=len(overlap),
                                 no_first_layer_overlap_segments=sum(a <= 1e-9 for a in overlap),
                                 minimum_segment_overlap_fraction=min(overlap),
                                 total_second_wall_footprint_overlap_fraction=walls.intersection(bed).area / walls.area))
        if specimen["kind"] == "lip":
            assert support_count[oid] > 0, specimen["id"]
            assert models[oid], specimen["id"]
            seed = min(models[oid], key=lambda m: m[0])
            beneath = sorted({z for z, h, kind in supports[oid] if z < seed[0] - seed[1] - .001})
            assert beneath, specimen["id"]
            gap = seed[0] - seed[1] - beneath[-1]
            contacts.append(dict(id=specimen["id"], parent_print_frame_probe_xy_mm=source_probe.tolist(),
                                 first_model_nozzle_Z_mm=seed[0], first_model_height_mm=seed[1],
                                 highest_underlapping_support_nozzle_Z_mm=beneath[-1],
                                 emitted_top_gap_at_probe_mm=round(gap, 6),
                                 support_deposition_segments=support_count[oid],
                                 scope="Commanded bead overlap at one lip point; not a physical contact or bond measurement"))
            detail = "current" if specimen["requested_coarse_layers"] is None else f"{specimen['requested_coarse_layers']} x 0.24"
            color = "#777777" if specimen["requested_coarse_layers"] is None else "#d6a443"
            b = np.array(specimen["plate_bounds_mm"])
            ax.add_patch(plt.Rectangle(b[0, :2], *(b[1, :2] - b[0, :2]), facecolor=color, alpha=.35, edgecolor=color))
            x, y = b[:, 0].mean(), b[:, 1].mean()
        else:
            assert not support_count[oid], specimen["id"]
            control = specimen["regular_seam_control"]
            if control:
                assert not ramps[oid], specimen["id"]
            else:
                assert ramps[oid], specimen["id"]
                assert abs(min(starts[oid]) - specimen["fine_start_height_mm"]) <= .00051, specimen["id"]
            scarf_checks.append(dict(id=specimen["id"], ordinary_control=control,
                                     fine_outer_wall_Z_ramp_segment_count=len(ramps[oid]),
                                     expected_start_above_previous_layer_mm=specimen["fine_start_height_mm"],
                                     lowest_emitted_start_above_previous_layer_mm=min(starts[oid]) if starts[oid] else None))
            detail = f"{specimen.get('seam_method', 'regular' if control else 'scarf')}\ngap {specimen['tested_gap_percent_of_nozzle']:g}%"
            color = "#777777" if control else "#377dac"
            x, y = bed.centroid.x, bed.centroid.y
        for polygon in list(bed.geoms) if hasattr(bed, "geoms") else [bed]:
            px, py = polygon.exterior.xy
            ax.fill(px, py, color=color, alpha=.7)
            for hole in polygon.interiors:
                px, py = hole.xy
                ax.fill(px, py, color="white")
        ax.text(x, y, specimen["id"] + "\n" + detail, ha="center", va="center", fontsize=8, weight="bold")
    ax.plot([40, 285, 285, 40, 40], [40, 40, 280, 280, 40], "k--", lw=1)
    ax.plot([lo[0], hi[0], hi[0], lo[0], lo[0]], [lo[1], lo[1], hi[1], hi[1], lo[1]], color="#9b3333", lw=1)
    ax.set(xlim=(0, 325), ylim=(0, 320), xlabel="Printer X (mm)", ylabel="Printer Y (mm)",
           title=f"{'Seam gap' if seam_only else 'Combined lift and seam gap' if combined else 'Faucet lip coarse-start'} plate: {margin:.1f} mm minimum bead inset\nNative bed beads and lip model outlines; front is bottom")
    ax.set_aspect("equal")
    fig.tight_layout()
    fig.savefig(folder / "plate-layout.png", dpi=150)
    plt.close(fig)
    destination = folder / native.name
    shutil.copyfile(native, destination)
    report = dict(schema=1, preparation_only=True, archive=str(destination.relative_to(ROOT)), archive_sha256=sha(native),
                  gcode_sha256=gcode_sha, prepared_project=prep["project"], prepared_project_sha256=sha(project),
                  geometry=geometries, inherited_global_settings_identical_to_shipping_faucet=True,
                  native_settings_normalizations=normalizations, layer_band_checks=layers,
                  coarse_start_checks=coarse_checks, lip_support_contacts=contacts, scarf_checks=scarf_checks,
                  seam_material_commands=seam_material(gcode, prep["specimens"]),
                  complete_model_support_brim_bead_bounds=bounds, minimum_full_bead_bed_margin_mm=margin,
                  first_second_layer_overlap=first_second, requested_Z_trim_mm=.04, emitted_Z_trim_commands_mm=trims,
                  probing_clump_detection=False, gcode_postprocessed=False,
                  native_estimated_seconds=plate["total_predication"],
                  native_estimated_grams_saved_profile_density=sum(f["total_used_g"] for f in plate["filaments"]),
                  scope="Native geometry, coarse counts, fine heights, bead footprints and support-gap witness. No physical recovery, appearance or bond result. Preparation grants no launch authorization.",
                  **{"pass": True})
    save(folder / "native-check.json", report)
    shutil.copyfile(work / "result.json", folder / "native-result.json")
    for record in (prep, plan):
        record.update(native_archive=report["archive"], native_archive_sha256=report["archive_sha256"],
                      gcode_sha256=gcode_sha, native_estimated_seconds=report["native_estimated_seconds"],
                      native_estimated_grams_saved_profile_density=report["native_estimated_grams_saved_profile_density"],
                      minimum_full_bead_bed_margin_mm=margin, native_check=str((folder / "native-check.json").relative_to(ROOT)),
                      native_check_sha256=sha(folder / "native-check.json"))
    save(folder / "preparation.json", prep)
    save(project.with_suffix(".print.json"), prep)
    save(folder / "study-plan.json", plan)
    print(json.dumps(dict(combined=combined, margin_mm=margin, seconds=report["native_estimated_seconds"],
                          grams=report["native_estimated_grams_saved_profile_density"], coarse_checks=coarse_checks,
                          support_gap_witness=contacts, preparation_only=True), indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--combined", action="store_true")
    parser.add_argument("--seam-only", action="store_true")
    args = parser.parse_args()
    review(args.combined, args.seam_only)
