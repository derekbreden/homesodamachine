"""Prepare the actual faucet tip and two complete covers in the saved PET-GF profile.

The native export is a local Bambu Studio operation. This script never
contacts a printer. The two cover instances share one production STL.
"""
from __future__ import annotations

import argparse
import copy
import importlib.util
import json
import hashlib
import os
from pathlib import Path
import re
import subprocess
import sys
import xml.etree.ElementTree as ET
import zipfile

import numpy as np
import trimesh

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import refresh_print_project as writer

PROJECT = HERE / "faucet-display-petgf.3mf"
BASELINE = writer.ROOT / ".cache/prints/2026-09-18-faucet-display-mark2/baseline-faucet-petgf.3mf"
BASELINE_RECORD = BASELINE.with_suffix(".readiness.json")
TITLE = "Faucet tip and complete display covers"
NATIVE_NAME = "faucet-display-mark2.gcode.3mf"
EXTERNAL_SPOOL = {"extruder_ams_count": ["1#0|4#0", "1#0|4#0"]}
PRODUCTION = (HERE / "faucet-petgf.3mf", HERE / "industrial/faucet-industrial-petgf.3mf")
SOURCE_FILES = (HERE / "faucet-shell/faucet_shell.py", HERE / "_display_snap.py",
                HERE / "faucet-display-cover/faucet_display_cover.py")
FIT_REPORT = HERE / "display-retention-check.json"
PARTS = (
    ("faucet-shell-tip", HERE / "faucet-shell/faucet-shell-tip.stl", 40.0),
    ("faucet-display-cover-front", HERE / "faucet-display-cover/faucet-display-cover.stl", 40.0),
    ("faucet-display-cover-up", HERE / "faucet-display-cover/faucet-display-cover.stl", -50.0),
)
OFFSETS = ((-80.0, 0.0), (20.0, 0.0), (95.0, 0.0))

def sha_file(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            value.update(chunk)
    return value.hexdigest()

def relative(path: Path) -> str:
    path = path.resolve()
    return str(path.relative_to(writer.ROOT) if path.is_relative_to(writer.ROOT) else path)

def profile_members(path: Path) -> dict[str, bytes]:
    with zipfile.ZipFile(path) as archive:
        return {name: archive.read(name) for name in archive.namelist()
                if name == writer.SETTINGS_MEMBER
                or name.startswith("Metadata/filament_settings_") and name.endswith(".config")}

def emitted_config(archive: zipfile.ZipFile) -> tuple[dict, list[float], int]:
    config, trims, layers = {}, [], None
    inside = False
    with archive.open("Metadata/plate_1.gcode") as stream:
        for payload in stream:
            line = payload.decode("utf-8", errors="replace").rstrip()
            if line == "; CONFIG_BLOCK_START":
                inside = True
            elif line == "; CONFIG_BLOCK_END":
                inside = False
            elif inside and (match := re.match(r"; ([a-z0-9_]+) = (.*)$", line)):
                config[match.group(1)] = match.group(2)
            elif match := re.match(r"\s*G29\.1 Z([-+.\d]+)", line):
                trims.append(float(match.group(1)))
            elif match := re.match(r"; total layer number: (\d+)", line):
                layers = int(match.group(1))
    if not config or layers is None:
        raise ValueError("Native G-code lacks its emitted configuration or layer count")
    return config, trims, layers

def validate_native(path: Path, staged: Path, directory: Path, report: dict,
                    expected_config_changes: dict | None = None,
                    expected_trim_commands: list[float] | None = None) -> dict:
    baseline = writer.ROOT / report["successful_profile"]["native_archive"]
    with zipfile.ZipFile(staged) as archive:
        expected = json.loads(archive.read(writer.SETTINGS_MEMBER))
    with zipfile.ZipFile(baseline) as previous:
        previous_config, previous_trim, _ = emitted_config(previous)
    with zipfile.ZipFile(path) as archive:
        if archive.testzip() is not None:
            raise ValueError("The native archive has a damaged member")
        effective = json.loads(archive.read(writer.SETTINGS_MEMBER))
        differences = {key: [expected.get(key), effective.get(key)]
                       for key in set(expected) | set(effective)
                       if expected.get(key) != effective.get(key)}
        allowed = {"filament_prime_volume": [["30"], ["45"]],
                   "filament_map_2": [None, ["1"]]}
        if any(key not in allowed or value != allowed[key] for key, value in differences.items()):
            raise ValueError(f"Unexpected native settings normalization: {differences}")
        current_config, trim, layers = emitted_config(archive)
        drift = {key: [previous_config.get(key), current_config.get(key)]
                 for key in set(previous_config) | set(current_config)
                 if previous_config.get(key) != current_config.get(key)}
        if drift != (expected_config_changes or {}):
            raise ValueError(f"Native emitted settings differ from the requested changes; changed keys: {sorted(drift)}")
        target_trim = previous_trim if expected_trim_commands is None else expected_trim_commands
        if trim != target_trim:
            raise ValueError(f"Native Z-trim commands differ from the requested values: {trim} vs {target_trim}")
        if previous_trim != report["successful_profile"]["actual_trim_commands_mm"]:
            raise ValueError("Successful job trim differs from its saved record")
        value, md5 = hashlib.sha256(), hashlib.md5()
        with archive.open("Metadata/plate_1.gcode") as stream:
            for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                value.update(chunk)
                md5.update(chunk)
        gcode_sha = value.hexdigest()
        if gcode_sha != sha_file(directory / "plate_1.gcode"):
            raise ValueError("Loose audit G-code differs from the native archive")
        if archive.read("Metadata/plate_1.gcode.md5").decode().strip().lower() != md5.hexdigest():
            raise ValueError("Native G-code MD5 metadata does not match its payload")
        plates = ET.fromstring(archive.read("Metadata/slice_info.config")).findall("plate")
        if len(plates) != 1:
            raise ValueError("Expected one native trial plate")
        metadata = {node.get("key"): node.get("value") for node in plates[0].findall("metadata")}
        objects = plates[0].findall("object")
        if metadata.get("outside") != "false" or any(row.get("skipped") != "false" for row in objects):
            raise ValueError("Native export has an outside or skipped object")
        if {row.get("name") for row in objects} != {row["name"] for row in report["parts"]}:
            raise ValueError("Native object names differ from the trial manifest")
    result = json.loads((directory / "result.json").read_text())
    if result.get("return_code") != 0 or len(result["sliced_plates"]) != 1:
        raise ValueError("Native slice did not finish successfully with one plate")
    plate = result["sliced_plates"][0]
    if plate["warning_message"] or plate["triangle_count"] != sum(row["triangles"] for row in report["parts"]):
        raise ValueError("Native slice reported a warning or changed triangle count")
    return {"archive": relative(path), "archive_sha256": sha_file(path),
            "gcode_sha256": gcode_sha, "layers": layers,
            "staged_input": relative(staged), "staged_input_sha256": sha_file(staged),
            "staged_settings_override": EXTERNAL_SPOOL,
            "native_export_settings_normalizations": differences,
            "emitted_settings_match_successful_job": not drift,
            "emitted_settings_match_requested_changes": True,
            "intentional_emitted_config_changes": drift, "actual_z_trim_commands_mm": trim,
            "slicer_return_code": result["return_code"], "warning": plate["warning_message"],
            "objects": len(objects), "triangles": plate["triangle_count"],
            "estimated_seconds": plate["total_predication"],
            "estimated_grams_saved_profile_density": sum(row["total_used_g"] for row in plate["filaments"])}

def extrusion_segments(gcode: Path):
    """Read the retained native extrusion paths, including sampled G2/G3 arcs."""
    sys.path.insert(0, str(writer.ROOT / "hardware/scripts"))
    from enclosure_support_audit import _WORD, _arc_points
    current, feature, layer = None, "", None
    x = y = z = e = width = 0.0
    absolute_xy, relative_e = True, True
    for raw in gcode.open():
        line = raw.strip()
        start = re.match(r"; start printing object, unique label id: (\d+)", line)
        if start:
            current, feature = int(start.group(1)), ""
        elif line.startswith("; stop printing object"):
            current = None
        elif line.startswith("; FEATURE:"):
            feature = line.split(":", 1)[1].strip()
        elif line.startswith("; Z_HEIGHT:"):
            layer = float(line.split(":", 1)[1])
        elif line.startswith("; LINE_WIDTH:"):
            width = float(line.split(":", 1)[1])
        code = line.split(";", 1)[0].strip()
        if not code:
            continue
        command = code.split(None, 1)[0]
        words = {key: float(value) for key, value in _WORD.findall(code)}
        if command in {"G90", "G91"}:
            absolute_xy = command == "G90"
        elif command in {"M82", "M83"}:
            relative_e = command == "M83"
        elif command == "G92":
            x, y, z, e = (words.get("X", x), words.get("Y", y),
                          words.get("Z", z), words.get("E", e))
        elif command in {"G0", "G1", "G2", "G3"}:
            nx = words.get("X", x) if absolute_xy else x + words.get("X", 0.0)
            ny = words.get("Y", y) if absolute_xy else y + words.get("Y", 0.0)
            nz = words.get("Z", z) if absolute_xy else z + words.get("Z", 0.0)
            de = words.get("E", 0.0) if relative_e else words.get("E", e) - e
            if current is not None and layer is not None and de > 1e-9 and (nx != x or ny != y):
                points = [(x, y)] + ([(nx, ny)] if command in {"G0", "G1"} else
                                     _arc_points((x, y), (nx, ny), words, command == "G2"))
                for a, b in zip(points, points[1:]):
                    yield {"object": current, "feature": feature, "layer": layer,
                           "width": width, "a": [*a, z], "b": [*b, nz]}
            x, y, z = nx, ny, nz
            if "E" in words:
                e = e + words["E"] if relative_e else words["E"]


def production_hashes() -> dict[str, str]:
    return {relative(path): sha_file(path)
            for project in PRODUCTION
            for suffix in (".3mf", ".print.json", ".support-audit.json", ".readiness.json")
            if (path := project.with_suffix(suffix)).is_file()}


def successful_profile(profile: Path, record: Path) -> dict:
    proof = json.loads(record.read_text())
    validation = proof["validation"]
    if not validation.get("sent") or not proof.get("launch", {}).get("startup_confirmed"):
        raise ValueError("The baseline record does not identify a submitted, started job")
    if sha_file(profile) != validation["project_sha256"]:
        raise ValueError("The saved baseline project differs from the submitted job")
    native = writer.ROOT / validation["sliced_archive"]
    if sha_file(native) != validation["sliced_archive_sha256"]:
        raise ValueError("The successful native archive changed")
    settings = profile_members(profile)
    if writer.digest(settings[writer.SETTINGS_MEMBER]) != validation["canonical_settings_sha256"]:
        raise ValueError("The successful PET-GF settings digest does not match")
    return {"record": relative(record), "record_sha256": sha_file(record),
            "snapshot": relative(profile), "snapshot_sha256": sha_file(profile),
            "native_archive": relative(native), "native_archive_sha256": sha_file(native),
            "settings_sha256": validation["canonical_settings_sha256"],
            "requested_z_trim_mm": validation["requested_z_trim_mm"],
            "actual_trim_commands_mm": validation["actual_trim_commands_mm"]}


def verify_sources(report: dict) -> None:
    for name, expected in report["cad_sources_sha256"].items():
        if sha_file(writer.ROOT / name) != expected:
            raise ValueError(f"{name} changed after project preparation")
    for row in report["parts"]:
        if sha_file(writer.ROOT / row["source"]) != row["stl_sha256"]:
            raise ValueError(f"{row['name']} changed after project preparation")


def write_readiness(project: Path, report: dict, native: dict | None = None,
                    audit: dict | None = None, contacts: dict | None = None,
                    roads: dict | None = None) -> dict:
    result = {"status": ("native slice and support audit passed; awaiting printer review"
                         if native else "project prepared; native slice pending"),
              "submitted": False, "printer": "Mark2", "printer_state_checked": False,
              "project": relative(project), "project_sha256": report["project_sha256"],
              "settings_sha256": report["settings_sha256"],
              "print_report_sha256": sha_file(project.with_suffix(".print.json")),
              "successful_profile": report["successful_profile"],
              "cad_sources_sha256": report["cad_sources_sha256"],
              "parts": [{key: row[key] for key in ("name", "source", "stl_sha256", "rotation_x_degrees")}
                        for row in report["parts"]],
              "native": native,
              "scope": "One real production tip and two identical complete production covers in different print poses.",
              "plate_identity": {"left": "tip, dispense face down", "middle": "cover, front edge down",
                                 "right": "cover, bezel up"},
              "physical_trial": "Retention, assembly force, support removal and contact finish require the print.",
              "submission": "The main task checks current Mark2 compatibility and submits through Bambu Connect."}
    if FIT_REPORT.is_file():
        result["geometry_fit_report"] = {"file": relative(FIT_REPORT), "sha256": sha_file(FIT_REPORT)}
    if audit:
        result.update({"support_audit_sha256": sha_file(project.with_suffix(".support-audit.json")),
                       "plates": audit["plates"], "fit": audit["fit"],
                       "support_summary": {row["piece"]: row["summary"] for row in audit["parts"]}})
    if contacts:
        result["support_face_review_sha256"] = sha_file(project.with_suffix(".support-faces.json"))
    if roads:
        if not native or roads["gcode_sha256"] != native["gcode_sha256"]:
            raise ValueError("The retention toolpath reading belongs to a different native G-code")
        result["retention_toolpath_review"] = {
            "file": relative(project.with_suffix(".retention-toolpaths.json")),
            "sha256": sha_file(project.with_suffix(".retention-toolpaths.json")),
            "sample_columns_per_part": {row["part"]: len(row["samples"]) for row in roads["parts"]},
            "height_allowances": roads["height_allowances"],
            "limitation": roads["limitation"],
        }
    project.with_suffix(".readiness.json").write_text(json.dumps(result, indent=2) + "\n")
    return result


def refresh(profile: Path, record: Path, project: Path) -> dict:
    before = production_hashes()
    baseline = successful_profile(profile, record)
    source_hashes = {relative(path): sha_file(path) for path in SOURCE_FILES}
    report = writer.refresh(profile, project, parts=PARTS, offsets=OFFSETS, title=TITLE)
    if profile_members(project) != profile_members(profile):
        raise ValueError("The complete successful PET-GF profile was not preserved")
    if report["parts"][1]["stl_sha256"] != report["parts"][2]["stl_sha256"]:
        raise ValueError("Both complete cover instances must contain the exact same STL")
    report.update(project_title=TITLE, successful_profile=baseline, cad_sources_sha256=source_hashes,
                  all_profile_members_preserved_byte_for_byte=True,
                  production_artifacts_unchanged=before)
    verify_sources(report)
    if production_hashes() != before:
        raise ValueError("A production project changed while preparing the display project")
    project.with_suffix(".print.json").write_text(json.dumps(report, indent=2) + "\n")
    write_readiness(project, report)
    return report


def refresh_production(profile: Path) -> None:
    """Refresh the two editable full-part projects without slicing either one."""
    main = PRODUCTION[0]
    report = writer.refresh(profile, main, title="Sculpted faucet PET-GF")
    if profile_members(main) != profile_members(profile):
        raise ValueError("Sculpted project settings changed")
    prior = main.with_suffix(".support-audit.json")
    readiness = {"status": "project refreshed; current full-plate slice pending",
                 "submitted": False, "project": relative(main),
                 "project_sha256": report["project_sha256"],
                 "settings_sha256": report["settings_sha256"],
                 "print_report_sha256": sha_file(main.with_suffix(".print.json")),
                 "source_stls": {row["source"]: row["stl_sha256"] for row in report["parts"]},
                 "profile_snapshot": relative(profile), "profile_snapshot_sha256": sha_file(profile),
                 "current_full_plate_sliced": False}
    if prior.is_file():
        previous = json.loads(prior.read_text())
        readiness["retained_previous_support_reading"] = {
            "file": relative(prior), "sha256": sha_file(prior),
            "project_sha256": previous["project_sha256"], "applies_to_current_project": False}
    main.with_suffix(".readiness.json").write_text(json.dumps(readiness, indent=2) + "\n")
    spec = importlib.util.spec_from_file_location("industrial_print", HERE / "industrial/prepare_print_project.py")
    industrial = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(industrial)
    industrial.refresh(profile, PRODUCTION[1])


def surface_name(name: str, local: np.ndarray, normal_s: float, normal_n: float) -> str:
    x, s, n = local
    shell = writer.shell
    if "cover" in name:
        if normal_n > .9 and n < 8.0:
            return "lip-bearing"
        if normal_n < -.98 and abs(n-shell.display_face_n-shell.display_cover_over_face) < .03:
            return "planar-inner-bezel"
        if normal_s < -.9 and abs(s-shell.display_clip_s_bottom) < .5:
            return "front-lip-end"
        if normal_s < -.7 and s > shell._display_housing_center_s:
            return ("rear-window-edge" if n > shell.display_face_n + shell.display_cover_over_face
                    else "inner-rear-closure")
        if normal_n < -.7 and s < shell.display_s_bottom + 1.0:
            return "front-inner-bridge"
    else:
        if abs(n-shell.display_clip_bottom_n) < .03 and normal_n > .9:
            return "groove-floor"
        if abs(n-shell.display_clip_top_n-shell._display_snap.BEARING_SLIP) < .03 and normal_n < -.9:
            return "groove-roof"
        if normal_s < -.9 and abs(s-shell.display_clip_s_top-shell._display_snap.END_SLIP) < .3:
            return "aft-groove-end"
        if normal_s < -.9 and abs(s-shell.display_s_top) < .03:
            return "aft-display-channel-wall"
        origin, tangent, normal = [np.array(v.toTuple()) for v in shell._tip_frame()]
        world = origin + [x, 0.0, 0.0] + s*tangent + n*normal
        radial_n = np.hypot(shell.soda_faucet_tube_y-world[1]-shell._path_center_bend2[0],
                            world[2]-shell.zone5_z_top-shell._path_center_bend2[1]) - shell.gn_bend2_r
        distances = {
            "soda-bore": abs(np.hypot(x, radial_n)-shell._tube_soda_bore_r),
            "flavor-pill-passage": abs(np.hypot(max(0.0, abs(x)-shell._tube_pill_cap_x),
                                                radial_n-shell.flavor_offset_y_from_water)-shell._tube_pill_bore_r),
            "signal-lane": abs(np.hypot(max(0.0, abs(x)-(shell.signal_lane_width-shell.signal_lane_depth)/2.0),
                                        radial_n-shell.signal_lane_center_n)-shell.signal_lane_depth/2.0),
            "outer-neck-joint-plug": abs(np.hypot(x, radial_n-shell.tube_shell_center_y)
                                          -shell.tube_shell_outer_r+shell.split_plug_shrink),
        }
        closest = min(distances, key=distances.get)
        if s > 60.0 and distances[closest] < .02:
            return closest
    return "other; see local coordinate and normal"


def support_faces(reading: dict, report: dict, gcode: Path) -> dict:
    origin, tangent, normal = [np.array(v.toTuple()) for v in writer.shell._tip_frame()]
    by_name = {row["name"]: row for row in report["parts"]}
    interfaces = [segment for segment in extrusion_segments(gcode) if segment["feature"] == "Support interface"]
    output = []
    for part in reading["parts"]:
        row = by_name[part["piece"]]
        mesh = trimesh.load(writer.ROOT / row["source"], force="mesh", process=True)
        rotation = np.array(row["build_transform"][:9]).reshape(3, 3).T
        translation, center = np.array(row["plate_translation_mm"]), np.array(row["source_center_mm"])
        mesh.vertices = (mesh.vertices-center) @ rotation.T + translation
        readings = []
        for island in part["interfaces"]:
            x0, y0, x1, y1 = island["bbox_xy_mm"]
            candidates = []
            for segment in interfaces:
                if segment["object"] != row["identify_id"]:
                    continue
                point = (np.array(segment["a"]) + segment["b"]) / 2.0
                if (x0-.21 <= point[0] <= x1+.21 and y0-.21 <= point[1] <= y1+.21
                        and island["first_z_mm"]-.001 <= point[2] <= island["last_z_mm"]+.001):
                    candidates.append(point + [0.0, 0.0, .001])
            if not candidates:
                raise ValueError(f"No interface paths for {part['piece']} {island['id']}")
            indices = np.unique(np.linspace(0, len(candidates)-1, min(150, len(candidates)), dtype=int))
            rays = np.array(candidates)[indices]
            hits, ray_ids, triangle_ids = mesh.ray.intersects_location(
                rays, np.tile([0.0, 0.0, 1.0], (len(rays), 1)), multiple_hits=False)
            samples = []
            for hit, ray_id, triangle in zip(hits, ray_ids, triangle_ids):
                gap = float(hit[2]-rays[ray_id, 2]+.001)
                if gap > 2.0:
                    continue
                world = (hit-translation) @ rotation + center
                native_normal = mesh.face_normals[triangle] @ rotation
                local = np.array([world[0], (world-origin) @ tangent, (world-origin) @ normal])
                dot_s, dot_n = float(native_normal @ tangent), float(native_normal @ normal)
                samples.append({"display_x_s_n_mm": local.tolist(),
                                "surface": surface_name(part["piece"], local, dot_s, dot_n),
                                "normal_x_s_n": [float(native_normal[0]), dot_s, dot_n],
                                "interface_print_z_mm": float(rays[ray_id, 2]-.001),
                                "gap_above_interface_centerline_mm": gap})
            names = sorted({sample["surface"] for sample in samples})
            witnesses = []
            for name in names:
                group = [sample for sample in samples if sample["surface"] == name]
                witnesses.extend(group[index] for index in np.unique(
                    np.linspace(0, len(group)-1, min(12, len(group)), dtype=int)))
            readings.append({"id": island["id"], "trees": island.get("trees", [island.get("tree")]), "rays": len(rays),
                             "face_counts": {name: sum(sample["surface"] == name for sample in samples) for name in names},
                             "samples": witnesses})
        output.append({"part": part["piece"], "rotation_x_degrees": row["rotation_x_degrees"],
                       "unlabelled_support_bodies": part["summary"]["bodies_without_interface_labels"],
                       "interfaces": readings})
    return {"gcode_sha256": sha_file(gcode),
            "method": "Vertical rays from actual labelled support-interface extrusion paths to the placed STL. Up to150 rays per island; representative witnesses retained by contacted face.",
            "limitation": "Samples locate faces, not complete contact boundaries. Unlabelled contacts remain unknown. Removal and finish require the physical print.",
            "parts": output}


def retention_toolpaths(report: dict, gcode: Path) -> dict:
    """Sample the ideal commanded-road envelope across the groove and both lips."""
    origin, tangent, normal = [np.array(v.toTuple()) for v in writer.shell._tip_frame()]
    rows = {row["identify_id"]: row for row in report["parts"]}
    transforms = {key: (np.array(row["build_transform"][:9]).reshape(3, 3).T,
                        np.array(row["source_center_mm"]), np.array(row["plate_translation_mm"]))
                  for key, row in rows.items()}
    layers = {key: {} for key in rows}
    for segment in extrusion_segments(gcode):
        key = segment["object"]
        if key not in rows or segment["feature"].startswith("Support"):
            continue
        rotation, center, translation = transforms[key]
        points = np.array([segment["a"], segment["b"]])
        world = (points-translation) @ rotation + center
        local = np.column_stack((world[:, 0], (world-origin) @ tangent, (world-origin) @ normal))
        if (local[:, 1].max() < 10.0 or local[:, 1].min() > 38.0
                or local[:, 2].max() < 2.5 or local[:, 2].min() > 7.5):
            continue
        layers[key].setdefault(round(segment["layer"], 4), []).append(
            [*points[0, :2], *points[1, :2], segment["width"]])
    readings = []
    for key, row in rows.items():
        rotation, center, translation = transforms[key]
        roads_by_layer = {z: np.array(values) for z, values in layers[key].items()}
        is_tip = row["name"] == "faucet-shell-tip"
        samples = []
        xs = (-12.3, -12.1, 12.1, 12.3) if is_tip else (-11.5, -11.0, 11.0, 11.5)
        for s in (12.2, 18.2, 24.2, 30.2, 36.2):
            for x in xs:
                ns = np.linspace(2.8, 7.2, 2201)
                world = origin + [x, 0.0, 0.0] + s*tangent + ns[:, None]*normal
                points = (world-center) @ rotation.T + translation
                zs = np.round(.2 + np.maximum(0.0, np.ceil((points[:, 2]-.2-1e-8)/.24))*.24, 4)
                occupied = np.zeros(len(ns), dtype=bool)
                for z in np.unique(zs):
                    indices = np.where((zs == z) & (points[:, 2] >= max(0.0, z-.24)-1e-8))[0]
                    if not len(indices):
                        continue
                    roads = roads_by_layer.get(float(z))
                    if roads is None:
                        continue
                    low, high = points[indices, :2].min(axis=0)-.5, points[indices, :2].max(axis=0)+.5
                    roads = roads[np.all(np.maximum(roads[:, :2], roads[:, 2:4]) >= low, axis=1)
                                  & np.all(np.minimum(roads[:, :2], roads[:, 2:4]) <= high, axis=1)]
                    if not len(roads):
                        continue
                    starts, vectors = roads[:, :2], roads[:, 2:4]-roads[:, :2]
                    length2 = np.maximum(np.sum(vectors*vectors, axis=1), 1e-20)
                    delta = points[indices, None, :2]-starts[None, :, :]
                    fraction = np.clip(np.sum(delta*vectors[None, :, :], axis=2)/length2, 0.0, 1.0)
                    distance2 = np.sum((delta-fraction[:, :, None]*vectors[None, :, :])**2, axis=2)
                    occupied[indices] = np.any(distance2 <= (roads[:, 4]/2.0)[None, :]**2, axis=1)
                if is_tip:
                    material = ~occupied
                    middle = int(np.argmin(abs(ns-4.8)))
                    if not material[middle]:
                        raise ValueError(f"Groove road interference at {x},{s}")
                    left = right = middle
                    while left > 0 and material[left-1]:
                        left -= 1
                    while right < len(ns)-1 and material[right+1]:
                        right += 1
                else:
                    # The process has sparse infill inside the lip. Its outer
                    # height envelope uses both skins, including any air between.
                    present = np.flatnonzero(occupied)
                    if not len(present):
                        raise ValueError(f"No lip roads at {x},{s}")
                    left, right = int(present[0]), int(present[-1])
                bounded = left > 0 and right < len(ns)-1
                samples.append({"x_mm": x, "s_mm": s, "lower_n_mm": float(ns[left]),
                                "upper_n_mm": float(ns[right]), "span_mm": float(ns[right]-ns[left]),
                                "bounded_both_sides": bounded})
        bounded = [sample["span_mm"] for sample in samples if sample["bounded_both_sides"]]
        if len(bounded) != len(samples):
            raise ValueError(f"An intended retention section is unbounded for {row['name']}")
        readings.append({"part": row["name"], "kind": "continuous empty groove" if is_tip else "outer lip height envelope",
                         "minimum_span_mm": min(bounded), "maximum_span_mm": max(bounded), "samples": samples})
    groove = readings[0]["minimum_span_mm"]
    margins = [{"cover": row["part"], "minimum_sampled_groove_minus_maximum_sampled_lip_mm": groove-row["maximum_span_mm"]}
               for row in readings[1:]]
    if any(row["minimum_sampled_groove_minus_maximum_sampled_lip_mm"] <= 0.0 for row in margins):
        raise ValueError("The sampled commanded road envelope closes the groove/lip height allowance")
    return {"gcode_sha256": sha_file(gcode), "sample_pitch_n_mm": .002,
            "method": "Actual model extrusion polylines buffered by half their commanded XY width and extended from layer Z minus .24 to layer Z (first layer0..0.2). Twenty independent X/S columns per part read a continuous empty groove or the lip's outer height envelope including internal infill voids. Shared arc parser samples G2/G3 paths at most0.18 mm apart.",
            "limitation": "Ideal commanded-road envelope only. This does not model bead cross-section, sag, shrinkage, surface roughness or elastic assembly, and does not replace a physical fit reading.",
            "parts": readings, "height_allowances": margins}


def review_native(project: Path, report: dict, directory: Path) -> dict:
    before = production_hashes()
    verify_sources(report)
    staged = directory / "faucet-display-mark2-input.3mf"
    ready = directory / "ready"
    native = validate_native(ready / NATIVE_NAME, staged, ready, report)
    staged_report = copy.deepcopy(report)
    with zipfile.ZipFile(staged) as archive:
        staged_report.update(project_sha256=sha_file(staged),
                             settings_sha256=writer.digest(archive.read(writer.SETTINGS_MEMBER)))
    reading = writer.slice_review(staged, staged_report, ready)
    project.with_suffix(".support-audit.json").write_bytes(staged.with_suffix(".support-audit.json").read_bytes())
    contacts = support_faces(reading, report, ready / "plate_1.gcode")
    project.with_suffix(".support-faces.json").write_text(json.dumps(contacts, indent=2) + "\n")
    roads = retention_toolpaths(report, ready / "plate_1.gcode")
    project.with_suffix(".retention-toolpaths.json").write_text(json.dumps(roads, indent=2) + "\n")
    verify_sources(report)
    if production_hashes() != before:
        raise ValueError("A production artifact changed during the native review")
    return write_readiness(project, report, native, reading, contacts, roads)


def native_slice(project: Path, report: dict, directory: Path, slicer: Path) -> dict:
    verify_sources(report)
    directory.mkdir(parents=True, exist_ok=False)
    ready = directory / "ready"
    ready.mkdir()
    with zipfile.ZipFile(project) as archive:
        members = {name: archive.read(name) for name in archive.namelist()}
    settings = json.loads(members[writer.SETTINGS_MEMBER])
    settings.update(EXTERNAL_SPOOL)
    members[writer.SETTINGS_MEMBER] = (json.dumps(settings, indent=2) + "\n").encode()
    staged = directory / "faucet-display-mark2-input.3mf"
    writer.archive_write(staged, members)
    command = [str(slicer), "--slice", "0", "--arrange", "0", "--orient", "0",
               "--outputdir", str(ready), "--export-3mf", NATIVE_NAME, str(staged)]
    (directory / "native-command.json").write_text(json.dumps({"argv": command,
        "environment": {"OMP_NUM_THREADS": "1", "OPENBLAS_NUM_THREADS": "1"},
        "settings_override": EXTERNAL_SPOOL, "submitted": False}, indent=2) + "\n")
    with (ready / "bambu-cli.log").open("w") as stream:
        result = subprocess.run(command, cwd=ready, stdout=stream, stderr=subprocess.STDOUT,
                                env={**os.environ, "OMP_NUM_THREADS": "1", "OPENBLAS_NUM_THREADS": "1"})
    if result.returncode:
        raise RuntimeError(f"Native Bambu slice exited {result.returncode}; see {ready / 'bambu-cli.log'}")
    return review_native(project, report, directory)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", type=Path, default=PROJECT)
    parser.add_argument("--settings-from", type=Path, default=BASELINE)
    parser.add_argument("--baseline-record", type=Path, default=BASELINE_RECORD)
    parser.add_argument("--refresh-production", action="store_true",
                        help="Refresh Sculpted and Industrial mesh projects; neither full plate is sliced.")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--slice-output", type=Path, help="New directory for one native slice and audit.")
    group.add_argument("--review-existing", type=Path, help="Read an existing native output without re-slicing.")
    parser.add_argument("--slicer", type=Path,
                        default=Path("/Applications/BambuStudio.app/Contents/MacOS/BambuStudio"))
    args = parser.parse_args()
    project = args.project.resolve()
    if args.slice_output and args.slice_output.exists():
        parser.error("--slice-output must be a new directory")
    if project in [path.resolve() for path in PRODUCTION] or project == args.settings_from.resolve():
        parser.error("The display output must not replace a full-part project or its baseline")
    if args.review_existing:
        if args.refresh_production:
            parser.error("--review-existing does not refresh projects")
        report = json.loads(project.with_suffix(".print.json").read_text())
        if sha_file(project) != report["project_sha256"]:
            raise ValueError("The prepared project changed")
        result = review_native(project, report, args.review_existing.resolve())
    else:
        if args.refresh_production:
            successful_profile(args.settings_from.resolve(), args.baseline_record.resolve())
            refresh_production(args.settings_from.resolve())
        report = refresh(args.settings_from.resolve(), args.baseline_record.resolve(), project)
        print(f"{project}: one real tip and two identical complete cover meshes; exact successful PET-GF profile", flush=True)
        if not args.slice_output:
            return
        result = native_slice(project, report, args.slice_output.resolve(), args.slicer.resolve())
    print(json.dumps({"status": result["status"], "native": result["native"], "fit": result["fit"]}, indent=2), flush=True)


if __name__ == "__main__":
    main()
