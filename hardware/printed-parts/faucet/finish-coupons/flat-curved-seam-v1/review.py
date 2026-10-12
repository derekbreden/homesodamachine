"""Manual native review of this prepared diagnostic plate; never connect or Send."""
from collections import defaultdict
import hashlib
import json
import math
from pathlib import Path
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
sys.path[:0] = [str(ROOT / "hardware/printed-parts/faucet"), str(ROOT / "hardware/scripts")]
import prepare_vent_prints as prep
from prepare_display_print import extrusion_segments
from prepare import WORK


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def save(p, d):
    p.write_text(json.dumps(d, indent=2) + "\n")


def transform(vertices, text):
    t = np.array([float(v) for v in text.split()]).reshape(4, 3)
    return vertices @ t[:3] + t[3]


def main():
    report = json.loads((HERE / "preparation.json").read_text())
    prep.verify_sources(report)
    project = ROOT / report["project"]
    native = WORK / (project.stem + ".gcode.3mf")
    validation = prep.native_validation(native, project, report, WORK)
    geometry = []
    qn = prep.writer.qn
    with zipfile.ZipFile(native) as arc, zipfile.ZipFile(project) as prepared, zipfile.ZipFile(ROOT / report["settings_source"]) as baseline:
        expected = json.loads(prepared.read(prep.writer.SETTINGS_MEMBER))
        defaults = json.loads(baseline.read(prep.writer.SETTINGS_MEMBER))
        delta = {k for k in set(expected) | set(defaults) if expected.get(k) != defaults.get(k)}
        assert delta == {"machine_start_gcode", "printer_settings_id"}
        assert expected["seam_position"] == "aligned" and expected["seam_gap"] == "15%"
        assert expected["seam_slope_type"] == "none" and expected["filament_scarf_seam_type"] == ["none"]
        assert expected["enable_arc_fitting"] == "0" and expected["enable_circle_compensation"] == "0"
        assert expected["enable_wrapping_detection"] == "0"
        model = ET.fromstring(arc.read("3D/3dmodel.model"))
        objects = {o.get("id"):o for o in model.findall(f"{qn('resources')}/{qn('object')}")}
        builds = {b.get("objectid"):b for b in model.findall(f"{qn('build')}/{qn('item')}")}
        cfg = ET.fromstring(arc.read("Metadata/model_settings.config"))
        assert len(cfg.findall("object")) == 4 and len(cfg.findall(".//part")) == 4
        for part in report["parts"]:
            obj = cfg.find(f"object[@id='{part['object_id']}']")
            metadata = {m.get("key"):m.get("value") for m in obj.findall("metadata") if m.get("key")}
            assert set(metadata) == {"name", "extruder"}
            component = objects[part["object_id"]].find(f"{qn('components')}/{qn('component')}")
            child = ET.fromstring(arc.read(component.get("{" + prep.writer.PROD + "}path").lstrip("/")))
            mesh = child.find(f"{qn('resources')}/{qn('object')}/{qn('mesh')}")
            vertices = np.array([[float(v.get(k)) for k in "xyz"] for v in mesh.find(qn("vertices"))])
            triangles = list(mesh.find(qn("triangles")))
            faces = np.array([[int(t.get(k)) for k in ("v1", "v2", "v3")] for t in triangles])
            source = trimesh.load(ROOT / part["source"], force="mesh", process=True)
            assert np.array_equal(source.faces, faces)
            placed = transform(transform(vertices, component.get("transform")), builds[part["object_id"]].get("transform"))
            target = transform(source.vertices - part["source_center_mm"], " ".join(map(str, part["build_transform"])))
            error = float(abs(placed - target).max())
            assert error < 1e-4
            assert any(t.get("paint_seam") == "4" for t in triangles)
            geometry.append(dict(name=part["name"], native_vertex_error_mm=error,
                                 triangles_identical=True, seam_paint_retained=True))
        (HERE / "native-preview.png").write_bytes(arc.read("Metadata/plate_1.png"))
        (HERE / "native-top.png").write_bytes(arc.read("Metadata/top_1.png"))
    gcode = WORK / "plate_1.gcode"
    code = gcode.read_text()
    assert not re.search(r"^\s*G39(?:\s|;|$)", code, re.M)
    assert not re.search(r"^\s*M400\s+U1", code, re.M)
    bead_bounds = prep.writer.object_toolpaths(gcode, WORK / "all-beads.gcode", None)
    lo, hi = np.array(bead_bounds["extrusion_bounds_xy_mm"])
    usable_lo, usable_hi = np.array(report["shared_printable_area_mm"])
    margin = float(min(np.min(lo - usable_lo), np.min(usable_hi - hi)))
    assert margin >= 80
    first, second, layers, contours = defaultdict(list), defaultdict(list), defaultdict(dict), defaultdict(list)
    support_count = ramp_count = 0
    run = []

    def finish():
        nonlocal run
        if run:
            pts = np.array([run[0]["a"]] + [r["b"] for r in run])
            area = abs(float(np.sum(pts[:, 0] * np.roll(pts[:, 1], -1) - np.roll(pts[:, 0], -1) * pts[:, 1]) / 2))
            contours[(run[0]["object"], round(run[0]["layer"], 4))].append(dict(
                area_mm2=area, start_mm=pts[0].tolist(), end_mm=pts[-1].tolist(),
                gap_mm=float(np.linalg.norm(pts[0, :2] - pts[-1, :2]))))
        run = []

    for road in extrusion_segments(gcode):
        oid, z, feature = road["object"], road["layer"], road["feature"]
        if feature.startswith("Support"): support_count += 1
        if "wall" in feature.lower():
            layers[oid][round(z, 4)] = road["height"]
            if abs(road["a"][2] - z) > 1e-5 or abs(road["b"][2] - z) > 1e-5: ramp_count += 1
        if abs(z - .2) < 1e-5:
            first[oid].append(LineString([road["a"][:2], road["b"][:2]]).buffer(road["width"] / 2, quad_segs=4))
        elif abs(z - .44) < 1e-5 and "wall" in feature.lower():
            second[oid].append(LineString([road["a"][:2], road["b"][:2]]).buffer(road["width"] / 2, quad_segs=4))
        if feature == "Outer wall":
            if run and (oid != run[-1]["object"] or z != run[-1]["layer"] or math.dist(run[-1]["b"], road["a"]) > 1e-4): finish()
            run.append(road)
        else: finish()
    finish()
    assert support_count == 0 and ramp_count == 0
    readings = []
    fig, ax = plt.subplots(figsize=(7, 6))
    for specimen, part in zip(report["specimens"], report["parts"]):
        oid = specimen["identify_id"]
        assert len(layers[oid]) == 30
        assert all(abs(h - (.2 if z == .2 else .24)) < 1e-5 for z, h in layers[oid].items())
        bed = unary_union(first[oid])
        overlaps = [b.intersection(bed).area / b.area for b in second[oid]]
        assert overlaps and min(overlaps) > 1e-9
        starts, witnesses = [], []
        for z in sorted(layers[oid]):
            outer = max(contours[(oid, z)], key=lambda c: c["area_mm2"])
            assert outer["area_mm2"] > 450
            assert abs(outer["gap_mm"] - .06) < .002
            start = np.array(outer["start_mm"]) - np.array(part["plate_translation_mm"]) + part["source_center_mm"]
            assert abs(start[0]) < 2, (specimen["id"], z, start)
            starts.append(start.tolist())
            if z in (.44, 3.8, 6.68): witnesses.append(dict(z_mm=z, source_start_mm=start.tolist(), **outer))
        readings.append(dict(id=specimen["id"], face=specimen["face"], layers=30,
                             largest_absolute_seam_x_mm=max(abs(s[0]) for s in starts),
                             flat_face_corner_clearance_mm=6-max(abs(s[0]) for s in starts) if specimen["face"] == "flat" else None,
                             minimum_second_wall_bed_overlap_fraction=min(overlaps), witnesses=witnesses))
        color = "#ca9e52" if specimen["face"] == "flat" else "#558aa4"
        for polygon in (list(bed.geoms) if hasattr(bed, "geoms") else [bed]):
            ax.fill(*polygon.exterior.xy, color=color, alpha=.8)
            for hole in polygon.interiors: ax.fill(*hole.xy, color="white")
        center = (np.array(part["plate_bounds_mm"])[0, :2] + np.array(part["plate_bounds_mm"])[1, :2]) / 2
        ax.text(*center, f"{specimen['id']}\n{specimen['face'].upper()}", ha="center", va="center", fontsize=11, weight="bold")
        seam = np.array(witnesses[1]["start_mm"])
        ax.annotate("seam", xy=seam[:2], xytext=(seam[0], seam[1]+5), ha="center", fontsize=8, arrowprops=dict(arrowstyle="->", color="#a32626"))
    bounds = np.array(bead_bounds["extrusion_bounds_xy_mm"])
    ax.set(xlim=(bounds[0, 0]-12, bounds[1, 0]+12), ylim=(bounds[0, 1]-9, bounds[1, 1]+13),
           xlabel="Printer X (mm)", ylabel="Printer Y (mm)",
           title="Flat / curved seam diagnostic · front is bottom\nSame PET-GF settings · inspect the arrowed Y+ face")
    ax.set_aspect("equal")
    fig.tight_layout(); fig.savefig(HERE / "plate-layout.png", dpi=170); plt.close(fig)
    destination = HERE / native.name
    shutil.copyfile(native, destination)
    validation["archive"] = str(destination.relative_to(ROOT))
    result = dict(native=validation, geometry=geometry, seam_readings=readings,
                  only_geometry_factor="Outer inspection-face curvature", process_settings_common=True,
                  common_seam_paint=True, no_object_process_overrides=True,
                  minimum_full_bead_bed_margin_mm=margin, full_bead_bounds=bead_bounds,
                  support_segments=support_count, scarf_ramp_segments=ramp_count,
                  clump_probing_calls=0, gcode_postprocessed=False,
                  review_script_sha256=sha(Path(__file__)), passed=True,
                  scope="Native geometry, settings, painted seam location, commanded gap, bed overlap and footprint. Physical seam shape remains unassessed.")
    save(HERE / "native-check.json", result)
    shutil.copyfile(WORK / "result.json", HERE / "native-result.json")
    print(json.dumps(dict(minutes=validation["estimated_seconds"] / 60,
                          grams=validation["estimated_grams_saved_profile_density"],
                          minimum_edge_clearance_mm=margin, seam_readings=readings), indent=2))


if __name__ == "__main__":
    main()
