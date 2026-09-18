"""Prepare and natively slice the labelled faucet-cover retention trials.

The CAD generator supplies trial-geometry.json and assembly-frame STLs. This
tool copies the successful Sculpted PET-GF profile, places the trial parts,
and can produce one native Bambu archive. It never contacts a printer.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
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
FAUCET = HERE.parents[1] / "faucet"
sys.path.insert(0, str(FAUCET))
import refresh_print_project as writer

TITLE = "Faucet cover retention trials"
PROJECT = HERE / "faucet-cover-retention-petgf.3mf"
MANIFEST = HERE / "trial-geometry.json"
PROFILE = FAUCET / "faucet-petgf.3mf"
PROOF = PROFILE.with_suffix(".readiness.json")
NATIVE_NAME = "faucet-cover-retention-mark2.gcode.3mf"
EXTERNAL_SPOOL = {"extruder_ams_count": ["1#0|4#0", "1#0|4#0"]}
PROFILE_SUFFIXES = (".3mf", ".print.json", ".support-audit.json", ".readiness.json")
PRODUCTION_PROJECTS = (PROFILE, FAUCET / "industrial/faucet-industrial-petgf.3mf")


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


def production_hashes() -> dict[str, str]:
    return {relative(path): sha_file(path)
            for project in PRODUCTION_PROJECTS
            for suffix in PROFILE_SUFFIXES
            if (path := project.with_suffix(suffix)).is_file()}


def successful_profile() -> dict:
    proof = json.loads(PROOF.read_text())
    validation = proof["validation"]
    profile = writer.ROOT / validation["source_profile"]
    native = writer.ROOT / validation["sliced_archive"]
    if not validation.get("sent") or not proof.get("launch", {}).get("startup_confirmed"):
        raise ValueError("The saved Sculpted readiness record does not identify a submitted baseline")
    if sha_file(profile) != validation["source_profile_sha256"]:
        raise ValueError("The successful job's saved profile snapshot changed")
    if sha_file(native) != validation["sliced_archive_sha256"]:
        raise ValueError("The successful job's native archive changed")
    if profile_members(PROFILE) != profile_members(profile):
        raise ValueError("Current Sculpted settings differ from the successful job's saved profile")
    if writer.digest(profile_members(PROFILE)[writer.SETTINGS_MEMBER]) != validation["canonical_settings_sha256"]:
        raise ValueError("The successful canonical settings digest does not match")
    return {"record": relative(PROOF), "record_sha256": sha_file(PROOF),
            "snapshot": relative(profile), "snapshot_sha256": sha_file(profile),
            "native_archive": relative(native), "native_archive_sha256": sha_file(native),
            "settings_sha256": validation["canonical_settings_sha256"],
            "requested_z_trim_mm": validation["requested_z_trim_mm"],
            "actual_trim_commands_mm": validation["actual_trim_commands_mm"]}


def trial_parts(manifest: Path) -> tuple[dict, tuple, tuple]:
    geometry = json.loads(manifest.read_text())
    if geometry.get("passed") is False:
        raise ValueError("The trial geometry report records a failure")
    sources = geometry.get("sources_sha256", geometry.get("sources", {}))
    for name, expected in sources.items():
        if sha_file(writer.ROOT / name) != expected:
            raise ValueError(f"{name} changed after the trial geometry export")
    rows = geometry["parts"]
    if not 2 <= len(rows) <= 6:
        raise ValueError("This retention plate accepts two to six labelled covers")
    parts, identifiers = [], set()
    for row in rows:
        identifier = str(row["id"])
        if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,50}", identifier) or identifier in identifiers:
            raise ValueError("Every cover needs a unique short alphanumeric trial ID")
        identifiers.add(identifier)
        source = (manifest.parent / row["stl"]).resolve()
        if not source.is_relative_to(writer.ROOT) or sha_file(source) != row["sha256"]:
            raise ValueError(f"Trial {identifier} STL differs from the geometry report")
        angle = float(row["rotation_x_degrees"])
        if angle not in (130.0, -50.0):
            raise ValueError(f"Trial {identifier} needs its agreed bezel-down or bezel-up orientation")
        parts.append((f"cover-{identifier}", source, angle))
    # 90 mm pitch leaves room around 30 x 53 mm covers for brims and supports.
    offsets = tuple((x, y) for y in (-45.0, 45.0) for x in (-90.0, 0.0, 90.0))[:len(parts)]
    return geometry, tuple(parts), offsets


def verify_sources(manifest: Path, report: dict) -> None:
    if sha_file(manifest) != report["geometry_report_sha256"]:
        raise ValueError("The trial manifest changed while preparing or slicing")
    trial_parts(manifest)
    for row in report["parts"]:
        if sha_file(writer.ROOT / row["source"]) != row["stl_sha256"]:
            raise ValueError(f"{row['name']} changed while preparing or slicing")


def write_readiness(project: Path, report: dict, native: dict | None = None,
                    audit: dict | None = None, contacts: dict | None = None,
                    lips: dict | None = None) -> dict:
    result = {
        "status": ("native slice and support audit passed; awaiting printer review"
                   if native else "project prepared; native slice pending"),
        "submitted": False, "printer": "Mark2", "printer_state_checked": False,
        "project": relative(project), "project_sha256": report["project_sha256"],
        "settings_sha256": report["settings_sha256"],
        "print_report_sha256": sha_file(project.with_suffix(".print.json")),
        "geometry_report_sha256": report["geometry_report_sha256"],
        "successful_profile": report["successful_profile"],
        "production_artifacts_unchanged": report["production_artifacts_unchanged"],
        "parts": [{key: row[key] for key in ("name", "trial_id", "source", "stl_sha256",
                                             "rotation_x_degrees", "trial_parameters")}
                  for row in report["parts"]],
        "native": native,
        "physical_trial": "Retention force, spreading, support removal and contact finish require the print.",
        "submission": "The main task checks current Mark2 compatibility and submits through Bambu Connect.",
    }
    if audit:
        result.update({"support_audit_sha256": sha_file(project.with_suffix(".support-audit.json")),
                       "plates": audit["plates"], "fit": audit["fit"],
                       "support_summary": {row["piece"]: row["summary"] for row in audit["parts"]}})
    if contacts:
        result["support_face_review_sha256"] = sha_file(project.with_suffix(".support-faces.json"))
    if lips:
        result["retaining_layers_sha256"] = sha_file(project.with_suffix(".retaining-layers.json"))
        result["retaining_layer_result"] = lips["conclusion"]
    project.with_suffix(".readiness.json").write_text(json.dumps(result, indent=2) + "\n")
    return result


def refresh(manifest: Path = MANIFEST, project: Path = PROJECT) -> dict:
    manifest, project = manifest.resolve(), project.resolve()
    if not project.is_relative_to(HERE) or project.suffix != ".3mf":
        raise ValueError("The retention project must be a .3mf inside its fixture directory")
    before = production_hashes()
    baseline = successful_profile()
    geometry, parts, offsets = trial_parts(manifest)
    report = writer.refresh(PROFILE, project, parts=parts, offsets=offsets, title=TITLE)
    if profile_members(project) != profile_members(PROFILE):
        raise ValueError("The complete successful PET-GF profile was not preserved")
    for row, supplied, offset in zip(report["parts"], geometry["parts"], offsets):
        row.update({"trial_id": supplied["id"], "trial_label": supplied.get("label", supplied["id"]),
                    "trial_parameters": supplied.get("parameters") or {
                        key: value for key, value in supplied.items() if key.endswith("_mm")},
                    "plate_position_from_shared_center_mm": list(offset)})
    report.update({"project_title": TITLE, "geometry_report": relative(manifest),
                   "geometry_report_sha256": sha_file(manifest), "successful_profile": baseline,
                   "all_profile_members_preserved_byte_for_byte": True,
                   "production_artifacts_unchanged": before})
    verify_sources(manifest, report)
    if production_hashes() != before:
        raise ValueError("A production project artifact changed during trial preparation")
    project.with_suffix(".print.json").write_text(json.dumps(report, indent=2) + "\n")
    write_readiness(project, report)
    return report


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


def validate_native(path: Path, staged: Path, directory: Path, report: dict) -> dict:
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
        if drift:
            raise ValueError(f"Native emitted settings differ from the successful Mark2 job: {drift}")
        if trim != previous_trim or trim != report["successful_profile"]["actual_trim_commands_mm"]:
            raise ValueError("Native Z-trim commands differ from the successful Mark2 job")
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
            "emitted_settings_match_successful_job": True, "actual_z_trim_commands_mm": trim,
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


def support_faces(reading: dict, report: dict, segments: list[dict]) -> dict:
    """Trace above actual labelled interface extrusion paths to the print meshes."""
    origin, tangent, normal = writer.shell._tip_frame()
    origin, tangent, normal = map(lambda v: np.array(v.toTuple()), (origin, tangent, normal))
    by_name = {row["name"]: row for row in report["parts"]}
    output = []
    for part in reading["parts"]:
        row = by_name[part["piece"]]
        source = trimesh.load(writer.ROOT / row["source"], force="mesh", process=True)
        rotation = np.array(row["build_transform"][:9]).reshape(3, 3).T
        translation = np.array(row["plate_translation_mm"])
        center = np.array(row["source_center_mm"])
        source.vertices = (source.vertices - center) @ rotation.T + translation
        interfaces = []
        for interface in part["interfaces"]:
            x0, y0, x1, y1 = interface["bbox_xy_mm"]
            candidates = []
            for segment in segments:
                if segment["object"] != row["identify_id"] or segment["feature"] != "Support interface":
                    continue
                midpoint = (np.array(segment["a"]) + segment["b"]) / 2.0
                if (x0 - .21 <= midpoint[0] <= x1 + .21 and y0 - .21 <= midpoint[1] <= y1 + .21
                        and interface["first_z_mm"] - .001 <= midpoint[2] <= interface["last_z_mm"] + .001):
                    candidates.append(midpoint + [0.0, 0.0, .001])
            if not candidates:
                raise ValueError(f"No retained interface paths for {part['piece']} {interface['id']}")
            indices = np.unique(np.linspace(0, len(candidates) - 1, min(120, len(candidates)), dtype=int))
            rays = np.array(candidates)[indices]
            hits, indices, triangles = source.ray.intersects_location(
                rays, np.tile([0., 0., 1.], (len(rays), 1)), multiple_hits=False)
            samples = []
            for hit, ray, triangle in zip(hits, indices, triangles):
                gap = float(hit[2] - rays[ray, 2])
                if gap > 2.0:
                    continue
                world = (hit - translation) @ rotation + center
                native_normal = source.face_normals[triangle] @ rotation
                n = float((world-origin) @ normal)
                dot = float(native_normal @ normal)
                surface = ("lip-bearing" if dot > .9 and n < 10.0 else
                           "planar-inner-bezel" if dot < -.99 and abs(n-writer.shell.display_face_n-writer.shell.display_cover_over_face) < .02 else
                           "curved-front-inner-bridge" if dot < -.9 and n > 15.0 else "other")
                samples.append({"display_x_s_n_mm": [float(world[0]), float((world-origin) @ tangent), n],
                                "normal_dot_display_n": dot, "surface": surface,
                                "interface_print_z_mm": float(rays[ray, 2] - .001),
                                "gap_above_interface_centerline_mm": gap + .001})
            face_counts = {name: sum(sample["surface"] == name for sample in samples)
                           for name in sorted({sample["surface"] for sample in samples})}
            # Retain representative witnesses for each face; counts cover every successful ray.
            witnesses = []
            for name in face_counts:
                group = [sample for sample in samples if sample["surface"] == name]
                witnesses.extend(group[index] for index in np.unique(
                    np.linspace(0, len(group) - 1, min(12, len(group)), dtype=int)))
            interfaces.append({"id": interface["id"], "tree": interface["tree"],
                               "last_print_z_mm": interface["last_z_mm"],
                               "rays": len(rays), "face_counts": face_counts, "samples": witnesses})
        output.append({"part": part["piece"], "trial_id": row["trial_id"],
                       "rotation_x_degrees": row["rotation_x_degrees"],
                       "unlabelled_support_bodies": part["summary"]["bodies_without_interface_labels"],
                       "interfaces": interfaces})
    return {"method": "Up to 120 vertical rays from actual labelled support-interface extrusion segment midpoints, across that island's retained layers; first actual mesh surface within 2 mm. Samples identify faces, not complete contact boundaries.",
            "limitation": "Unlabelled interfaces remain unknown. This does not measure physical support removal or finish.",
            "parts": output}


def retaining_layers(gcode: Path, report: dict, segments: list[dict]) -> dict:
    """Read lip top layers and adjacent wall paths at three transverse stations."""
    origin, tangent, normal = [np.array(v.toTuple()) for v in writer.shell._tip_frame()]
    stations = np.linspace(writer.shell.display_clip_s_bottom,
                           writer.shell.display_clip_s_top, 5)[1:-1]
    readings = []
    for row in report["parts"]:
        if row["rotation_x_degrees"] != -50.0:
            continue
        rotation = np.array(row["build_transform"][:9]).reshape(3, 3).T
        translation, center = np.array(row["plate_translation_mm"]), np.array(row["source_center_mm"])
        crossings = []
        for segment in segments:
            if segment["object"] != row["identify_id"] or segment["feature"].startswith("Support"):
                continue
            world = (np.array([segment["a"], segment["b"]]) - translation) @ rotation + center
            local = np.column_stack((world[:, 0], (world-origin) @ tangent, (world-origin) @ normal))
            a, b = local
            if abs(b[1] - a[1]) <= 1e-10 or min(a[2], b[2]) > 7.0:
                continue
            for station in stations:
                if min(a[1], b[1]) <= station <= max(a[1], b[1]):
                    hit = a + (station-a[1]) / (b[1]-a[1]) * (b-a)
                    if abs(hit[0]) >= 9.0:
                        crossings.append({"station_s_mm": float(station), "print_z_mm": segment["layer"],
                                          "display_n_mm": float(hit[2]), "display_x_mm": float(hit[0]),
                                          "feature": segment["feature"], "line_width_mm": segment["width"]})
        tops = sorted({hit["print_z_mm"] for hit in crossings if hit["feature"] == "Top surface"})
        if not tops:
            raise ValueError(f"No sliced retaining top surface found for {row['name']}")
        top = max(tops)
        nearby = [hit for hit in crossings if top - .25 <= hit["print_z_mm"] <= top + .25]
        readings.append({"trial_id": row["trial_id"], "cad_lip_height_mm": row["trial_parameters"]["lip_height_mm"],
                         "top_surface_print_z_mm": tops, "near_top_crossings": nearby})
    by_id = {row["trial_id"]: row for row in readings}
    pairs = [{"trials": [a, b], "same_retaining_top_layers":
              by_id[a]["top_surface_print_z_mm"] == by_id[b]["top_surface_print_z_mm"]}
             for a, b in (("C", "E"), ("D", "F")) if a in by_id and b in by_id]
    return {"gcode_sha256": sha_file(gcode), "layer_height_mm": report["layer_height_mm"],
            "method": "Actual native model extrusion intersections at three S stations within the broad lips; support paths excluded. G2/G3 paths are sampled at at most 0.18 mm by the shared reader.",
            "parts": readings, "pairs": pairs,
            "conclusion": ("C/E and D/F have the same retaining top layers in this slice. The 0.10 mm CAD lip increase does not resolve as an additional printed layer at 0.24 mm. E/F are repeat specimens for print and fit consistency; minor path placement differences do not establish a 0.10 mm height difference."
                           if len(pairs) == 2 and all(pair["same_retaining_top_layers"] for pair in pairs)
                           else "See the measured retaining top layers; no sub-layer printed height is inferred.")}


def review_faces(project: Path, report: dict, reading: dict, gcode: Path) -> tuple[dict, dict]:
    segments = list(extrusion_segments(gcode))
    contacts = support_faces(reading, report, segments)
    lips = retaining_layers(gcode, report, segments)
    project.with_suffix(".support-faces.json").write_text(json.dumps(contacts, indent=2) + "\n")
    project.with_suffix(".retaining-layers.json").write_text(json.dumps(lips, indent=2) + "\n")
    return contacts, lips


def native_slice(project: Path, manifest: Path, report: dict, directory: Path, slicer: Path) -> dict:
    before = production_hashes()
    verify_sources(manifest, report)
    directory.mkdir(parents=True, exist_ok=False)
    ready = directory / "ready"
    ready.mkdir()
    with zipfile.ZipFile(project) as archive:
        members = {name: archive.read(name) for name in archive.namelist()}
    settings = json.loads(members[writer.SETTINGS_MEMBER])
    settings.update(EXTERNAL_SPOOL)
    members[writer.SETTINGS_MEMBER] = (json.dumps(settings, indent=2) + "\n").encode()
    staged = directory / "faucet-cover-retention-mark2-input.3mf"
    writer.archive_write(staged, members)
    staged_report = copy.deepcopy(report)
    staged_report.update(project_sha256=sha_file(staged),
                         settings_sha256=writer.digest(members[writer.SETTINGS_MEMBER]))
    command = [str(slicer), "--slice", "0", "--arrange", "0", "--orient", "0",
               "--outputdir", str(ready), "--export-3mf", NATIVE_NAME, str(staged)]
    (directory / "native-command.json").write_text(json.dumps({"argv": command,
        "environment": {"OMP_NUM_THREADS": "1", "OPENBLAS_NUM_THREADS": "1"},
        "settings_override": EXTERNAL_SPOOL, "submitted": False}, indent=2) + "\n")
    log = ready / "bambu-cli.log"
    with log.open("w") as stream:
        result = subprocess.run(command, cwd=ready, stdout=stream, stderr=subprocess.STDOUT,
                                env={**os.environ, "OMP_NUM_THREADS": "1", "OPENBLAS_NUM_THREADS": "1"})
    if result.returncode:
        raise RuntimeError(f"Native Bambu slice exited {result.returncode}; see {log}")
    native = validate_native(ready / NATIVE_NAME, staged, ready, report)
    print(f"Native archive validated: {native['objects']} trials; {native['estimated_seconds']:.0f} seconds", flush=True)
    reading = writer.slice_review(staged, staged_report, ready)
    project.with_suffix(".support-audit.json").write_bytes(staged.with_suffix(".support-audit.json").read_bytes())
    contacts, lips = review_faces(project, report, reading, ready / "plate_1.gcode")
    verify_sources(manifest, report)
    if production_hashes() != before:
        raise ValueError("A production artifact changed during the trial slice")
    return write_readiness(project, report, native, reading, contacts, lips)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=MANIFEST)
    parser.add_argument("--project", type=Path, default=PROJECT)
    parser.add_argument("--slice-output", type=Path, help="New directory for one native slice and audit; no printer connection.")
    parser.add_argument("--slicer", type=Path,
                        default=Path("/Applications/BambuStudio.app/Contents/MacOS/BambuStudio"))
    args = parser.parse_args()
    if args.slice_output and args.slice_output.exists():
        parser.error("--slice-output must name a new directory to keep this native run distinct")
    project, manifest = args.project.resolve(), args.manifest.resolve()
    report = refresh(manifest, project)
    print(f"{project}: {len(report['parts'])} labelled covers, one plate, exact successful PET-GF profile", flush=True)
    if args.slice_output:
        result = native_slice(project, manifest, report, args.slice_output.resolve(), args.slicer.resolve())
        print(json.dumps({"status": result["status"], "native": result["native"], "fit": result["fit"]}, indent=2), flush=True)


if __name__ == "__main__":
    main()
