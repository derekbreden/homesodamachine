"""Manually review the prepared centered faucet; no printer connection."""
from collections import defaultdict
import hashlib
import json
from pathlib import Path
import re
import shutil
import sys
import xml.etree.ElementTree as ET
import zipfile

import numpy as np
from shapely.geometry import LineString
from shapely.ops import unary_union
import trimesh

HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p / "tools/bambu_print.py").exists())
FAUCET = ROOT / "hardware/printed-parts/faucet"
WORK = ROOT / ".cache/printer-control/faucet-current-review-20261011"
PROJECT = FAUCET / "industrial/faucet-industrial-petgf.3mf"
STEM = "2026-10-11-industrial-faucet-centered-mount-shoulders012-petgf-left04-z004-mark2"
sys.path[:0] = [str(FAUCET), str(ROOT / "hardware/scripts")]
import prepare_vent_prints as prep
from prepare_display_print import extrusion_segments
import review_faucet_inserts
import review_lower_supports
from verify_round_layer_band import wall_layers, check_span


def arrays(geometry):
    qn = prep.writer.qn
    return (np.array([[float(v.get(a)) for a in "xyz"] for v in geometry.find(qn("vertices"))]),
            np.array([[int(t.get(a)) for a in ("v1", "v2", "v3")] for t in geometry.find(qn("triangles"))]))


def first_second(gcode, parts):
    bed, second = defaultdict(list), defaultdict(list)
    for road in extrusion_segments(gcode):
        if road["layer"] > .440001:
            break
        bead = LineString([road["a"][:2], road["b"][:2]]).buffer(road["width"] / 2)
        if abs(road["layer"] - .2) < .0001:
            bed[road["object"]].append(bead)
        elif abs(road["layer"] - .44) < .0001 and "wall" in road["feature"].lower():
            second[road["object"]].append(bead)
    rows = []
    for part in parts:
        oid = part["identify_id"]
        first = unary_union(bed[oid])
        beads = second[oid]
        assert beads, part["name"]
        overlap = [b.intersection(first).area / b.area for b in beads]
        assert min(overlap) > 1e-9, (part["name"], min(overlap))
        whole = unary_union(beads)
        rows.append(dict(part=part["name"], second_wall_segments=len(beads),
                         segments_without_first_layer_overlap=0,
                         minimum_segment_overlap_fraction=min(overlap),
                         total_second_wall_overlap_fraction=whole.intersection(first).area / whole.area))
    return dict(layers_z_mm=[.20, .44], objects=rows,
                method="Commanded bead footprints at emitted width; labelled first-layer model/support/brim carries each object's second-layer walls",
                scope="Native contact footprints; physical adhesion is not measured")


def exterior_runs(gcode, report):
    base = report["parts"][0]
    tf = np.array(base["build_transform"]).reshape(4, 3)
    inverse, center = np.linalg.inv(tf[:3]), np.array(base["source_center_mm"])
    ends, run = [], []

    def finish():
        nonlocal run
        if run:
            points = np.array([run[0]["a"]] + [s["b"] for s in run])
            cad = (points - tf[3]) @ inverse + center
            gap = float(np.linalg.norm(points[0] - points[-1]))
            width = min(s["width"] for s in run)
            length = float(np.linalg.norm(np.diff(points, axis=0), axis=1).sum())
            area = abs(float(np.sum(points[:, 0] * np.roll(points[:, 1], -1)
                                    - np.roll(points[:, 0], -1) * points[:, 1]) / 2))
            if gap > .015:
                for index, label in ((0, "start"), (-1, "stop")):
                    pt = cad[index]
                    if .5 < pt[2] < 13.9 and 28.7 < np.linalg.norm(pt[:2]) < 29.7:
                        ends.append(dict(cad_mm=pt.tolist(), end=label, print_z_mm=run[0]["layer"],
                                         complete_contour_seam=gap <= width / 2 and length > 100 and area > 1500,
                                         run_length_mm=length, closure_gap_mm=gap,
                                         projected_area_mm2=area, minimum_width_mm=width))
        run = []

    for road in extrusion_segments(gcode):
        if road["layer"] > 30:
            finish()
            break
        if road["object"] == 1901 and road["feature"] in ("Outer wall", "Overhang wall"):
            if run and (run[-1]["layer"] != road["layer"]
                        or np.linalg.norm(np.array(run[-1]["b"]) - road["a"]) >= 1e-4):
                finish()
            run.append(road)
        else:
            finish()
    finish()
    rows = []
    for region in report["review_host_regions"]:
        low, high = np.array(region["applied_source_bounds_mm"])
        near = []
        for end in ends:
            point = end["cad_mm"]
            distances = [abs(point[axis] - side) for axis in (0, 1)
                         if low[1-axis]-.6 <= point[1-axis] <= high[1-axis]+.6
                         for side in (low[axis], high[axis])]
            if distances and min(distances) < .6 and low[2] < point[2] < high[2]:
                near.append(end)
        partitions = [e for e in near if not e["complete_contour_seam"]]
        assert not partitions, (region["name"], partitions)
        rows.append(dict(name=region["name"], partition_endpoints=0,
                         complete_contour_seam_endpoints=len(near), witnesses=near))
    return dict(original_screw_host_boundaries=rows, all_outer_foot_endpoints=ends,
                repeated_reinforcement_boundary_tracks_absent=True,
                method="Connected positive-extrusion Outer/Overhang runs; CAD Z0.5–13.9 and R28.7–29.7; host sides within0.6 mm. Full-contour seams have closure gap <= half width, length >100 mm and projected area >1500 mm².",
                scope="Emitted endpoints at the reported screw-point defect sites; physical finish remains unmeasured")


def main():
    report = json.loads(PROJECT.with_suffix(".print.json").read_text())
    assert report["preparation_only"] and not report["launch_authorized"]
    assert not report["send_attempted"] and not report["submitted"]
    prep.verify_sources(report)
    assert prep.sha(PROJECT) == report["project_sha256"]
    native = WORK / (STEM + ".gcode.3mf")
    validation = prep.native_validation(native, PROJECT, report, WORK)
    geometries, walls, face_checks = [], [], []
    with zipfile.ZipFile(native) as arc, zipfile.ZipFile(PROJECT) as source, zipfile.ZipFile(ROOT / report["accepted_recipe"]) as accepted:
        assert source.read(prep.writer.SETTINGS_MEMBER) == accepted.read(prep.writer.SETTINGS_MEMBER)
        assert source.read("Metadata/layer_config_ranges.xml") == accepted.read("Metadata/layer_config_ranges.xml")
        settings = json.loads(arc.read(prep.writer.SETTINGS_MEMBER))
        assert settings["support_type"] == "tree(auto)" and settings["support_style"] == "default"
        assert settings["infill_wall_overlap"] == "15%" and settings["max_bridge_length"] == "0"
        assert settings["enable_wrapping_detection"] == "0" and settings["wrapping_detection_gcode"] == ""
        assert not re.search(r"^\s*G39(?:\s|;|$)", arc.read("Metadata/plate_1.gcode").decode(), re.M)
        cfg = ET.fromstring(arc.read("Metadata/model_settings.config"))
        assert not cfg.findall(".//part[@subtype='negative_part']")
        objects = {o.find("metadata[@key='name']").get("value"): o for o in cfg.findall("object")}
        assert set(objects) == {p["name"] for p in report["parts"]}
        base = objects[report["parts"][0]["name"]]
        assert base.find("metadata[@key='wall_generator']").get("value") == "arachne"
        mods = base.findall("part[@subtype='modifier_part']")
        assert len(mods) == 1
        for key, value in dict(wall_loops="6", sparse_infill_density="100%", sparse_infill_pattern="zig-zag").items():
            assert mods[0].find(f"metadata[@key='{key}']").get("value") == value
        model = ET.fromstring(arc.read("3D/3dmodel.model")); qn = prep.writer.qn
        resources = {o.get("id"): o for o in model.find(qn("resources"))}
        builds = {b.get("objectid"): b for b in model.find(qn("build"))}
        for part in report["parts"]:
            obj = objects[part["name"]]
            normal = obj.find("part[@subtype='normal_part']")
            component = resources[obj.get("id")].find(f"{qn('components')}/{qn('component')}[@objectid='{normal.get('id')}']")
            child = ET.fromstring(arc.read(component.get("{" + prep.writer.PROD + "}path").lstrip("/")))
            geo = child.find(f"{qn('resources')}/{qn('object')}[@id='{normal.get('id')}']/{qn('mesh')}")
            vertices, faces = arrays(geo)
            mesh = trimesh.load(ROOT / part["source"], force="mesh", process=True)
            assert mesh.is_watertight and mesh.is_winding_consistent and mesh.body_count == 1
            error = float(np.abs(vertices + part["source_center_mm"] - mesh.vertices).max())
            placement_error = float(np.abs(np.array([float(x) for x in builds[obj.get('id')].get('transform').split()]) - part["build_transform"]).max())
            assert error < 1e-5 and placement_error < 1e-5 and np.array_equal(faces, mesh.faces)
            geometries.append(dict(part=part["name"], source_stl_sha256=part["stl_sha256"],
                                   native_mesh_error_mm=error, native_placement_error_mm=placement_error,
                                   triangles_identical=True, single_closed_oriented_volume=True))
    for part in report["parts"]:
        layers = wall_layers(native, part["identify_id"])
        assert layers and np.allclose(layers[0], [.2, .2], atol=.001)
        if part["identify_id"] == 1901:
            face_checks = [check_span(layers, f"shoulder_CAD_Z{f['cad_z_mm']}", *f["print_z_span_mm"], .12, .001) for f in report["selected_faces"]]
            assert all(c["pass"] for c in face_checks), face_checks
        for z, h in layers:
            if z <= .201:
                continue
            fine = (part["identify_id"] == 1901 and any(z > f["fine_band_print_z_mm"][0] + .001
                    and z <= f["fine_band_print_z_mm"][1] + .001 for f in report["selected_faces"]))
            assert abs(h - (.12 if fine else .24)) < .001, (part["name"], z, h)
        walls.append(dict(part=part["name"], layer_count=len(layers), first_wall_layer=layers[0],
                          fine_wall_layers=sum(abs(h-.12)<.001 for z,h in layers),
                          last_wall_layer=layers[-1]))
    first_second_reading = first_second(WORK / "plate_1.gcode", report["parts"])
    exterior = exterior_runs(WORK / "plate_1.gcode", report)
    print("Native meshes, complete parts, fine bands, first/second contact and screw-site contours passed", flush=True)
    support = prep.writer.slice_review(PROJECT, report, WORK)
    print("Support topology and full model/support/brim bed envelope read", flush=True)
    target = HERE / native.name
    shutil.copyfile(native, target)
    shutil.copyfile(WORK / "plate_1.gcode", HERE / "plate_1.gcode")
    validation["archive"] = prep.relative(target)
    ready = dict(status="Baseline native slice reviewed; scarf/lift choices pending", project_sha256=report["project_sha256"],
                 print_report_sha256=prep.sha(PROJECT.with_suffix(".print.json")), native=validation,
                 preparation_only=True, launch_authorized=False, submitted=False,
                 finish_choices_pending=report["finish_choices_pending"], physical_finish_evaluated=False)
    prep.save(PROJECT.with_suffix(".readiness.json"), ready)
    inserts = review_faucet_inserts.review(PROJECT)
    assert inserts["pass"]
    lower = review_lower_supports.review(PROJECT)
    result = dict(native=validation, geometry=geometries, wall_layers=walls,
                  shoulder_band_checks=face_checks, first_second_layer_overlap=first_second_reading,
                  screw_point_contours=exterior, support_summary={p["piece"]:p["summary"] for p in support["parts"]},
                  plate_fit=support["fit"], insert_deposition_pass=inserts["pass"],
                  lower_support_review=prep.relative(PROJECT.with_suffix(".lower-supports.json")),
                  probing_clump_detection=False, bare_G39_commands=0,
                  support_blockers=0, supports="Tree(auto), saved Default; native automatic decisions retained",
                  preparation_only=True, launch_authorized=False, submitted=False,
                  finish_choices_pending=report["finish_choices_pending"],
                  scope="Native geometry, layer recipe, accessible-support locations and nominal insert stock; physical finish, release, fit, strength and lifetime require the identified physical article.",
                  **{"pass":True})
    prep.save(HERE / "native-check.json", result)
    prep.save(HERE / "preparation.json", report)
    prep.save(HERE / "native-result.json", json.loads((WORK / "result.json").read_text()))
    shutil.copyfile(WORK / "native-preview.png", HERE / "native-preview.png")
    ready.update(native_check=prep.relative(HERE / "native-check.json"), native_check_sha256=prep.sha(HERE / "native-check.json"),
                 support_audit_sha256=prep.sha(PROJECT.with_suffix(".support-audit.json")),
                 insert_beads_sha256=prep.sha(PROJECT.with_suffix(".insert-beads.json")),
                 lower_supports_sha256=prep.sha(PROJECT.with_suffix(".lower-supports.json")))
    prep.save(PROJECT.with_suffix(".readiness.json"), ready)
    prep.verify_sources(report)
    # The exported archive retains the G-code; the loose copy is temporary for the readers.
    loose = HERE / "plate_1.gcode"
    assert prep.sha(loose) == validation["gcode_sha256"]
    loose.unlink()
    print(json.dumps(dict(estimated_seconds=validation["estimated_seconds"], parts=validation["objects"],
                          minimum_full_bead_margin_mm=support["fit"]["complete_layer_bead_minimum_bed_margin_mm"],
                          preparation_only=True, launch_authorized=False), indent=2), flush=True)


if __name__ == "__main__":
    main()
