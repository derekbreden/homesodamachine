"""Prepare The Pour's interchangeable print specimens with the saved Mark2 profile.

    tools/cad-venv/bin/python hardware/printed-parts/calibration/soda-studies/prepare_prints.py
    tools/cad-venv/bin/python hardware/printed-parts/calibration/soda-studies/prepare_prints.py --slice

Each layer-height comparison has its own fixed-height project. Support-gap
specimens also have separate projects, retaining the same nominal layer height.
The seam comparison shares one plate. Preparation and local native slicing do
not connect to a printer or submit a job.
"""
from __future__ import annotations

import argparse
from collections import defaultdict
import hashlib
import json
import math
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
ROOT = next(p for p in HERE.parents if (p / "tools/bambu_print.py").is_file())
PROFILE = ROOT / "hardware/printed-parts/petgf.3mf"
MANIFEST = HERE / "manifest.json"
PROJECTS = HERE / "prints"
WORK = ROOT / ".cache/prints/soda-studies"
SLICER = Path("/Applications/BambuStudio.app/Contents/MacOS/BambuStudio")

# The shared 3MF writer imports the faucet generator for default dimensions.
# This preparer cuts no CAD and must not supersede a running geometry build.
os.environ.setdefault("HSM_NO_BUILD_LOCK", "1")
sys.path[:0] = [str(ROOT / "hardware/printed-parts/faucet"),
               str(ROOT / "hardware/scripts")]
import refresh_print_project as writer  # noqa: E402

GROUP_HEIGHTS = {"kit": .24, "finish-008": .08, "finish-012": .12,
                 "finish-024": .24, "seam": .12, "support-030": .24,
                 "support-045": .24, "support-060": .24}
SUPPORT_GAPS = {"support-030": .30, "support-045": .45, "support-060": .60}
SEAMS = {"NR00": ("regular", 0), "NR05": ("regular", 5),
         "NR15": ("regular", 15), "NS00": ("scarf", 0),
         "NS10": ("scarf", 10), "NS20": ("scarf", 20)}
_PRINT_SIZES = {}


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def save(path, value):
    Path(path).write_text(json.dumps(value, indent=2) + "\n")


def source_path(row):
    path = Path(row["stl"])
    if path.is_absolute():
        return path
    return ROOT / path if path.parts[0] == "hardware" else HERE / path


def print_size(row):
    path = source_path(row)
    stamp = path.stat()
    angle_degrees = float(row.get("rotation_x_degrees", 0))
    key = (path, stamp.st_mtime_ns, stamp.st_size, angle_degrees)
    if key not in _PRINT_SIZES:
        mesh = trimesh.load(path, force="mesh", process=True)
        angle = math.radians(angle_degrees)
        turn = np.array([[1, 0, 0], [0, math.cos(angle), -math.sin(angle)],
                         [0, math.sin(angle), math.cos(angle)]])
        posed = mesh.vertices @ turn.T
        _PRINT_SIZES[key] = posed.max(axis=0) - posed.min(axis=0)
    return _PRINT_SIZES[key]


def plate_layout(rows, settings, gap=18., border=40.):
    """Center shelf-packed bed-frame specimens with space for automatic supports.

    Small plates use the narrowest centered shelves. The native review reports
    the complete deposited envelope, including the slicer's support and brim.
    """
    areas = [np.array([[float(v) for v in point.split("x")]
                      for point in area.split(",")])
             for area in settings.get("extruder_printable_area", [])]
    used = sorted({int(n) for n in settings.get("filament_nozzle_map", [])}
                  & set(range(len(areas))))
    areas = [areas[i] for i in used] if used else areas
    if not areas:
        areas = [np.array([[float(v) for v in point.split("x")]
                           for point in settings["printable_area"]])]
    low = np.max([a.min(axis=0) for a in areas], axis=0)
    high = np.min([a.max(axis=0) for a in areas], axis=0)
    available = high - low - 2 * border
    sizes = [print_size(row)[:2] for row in rows]
    order = sorted(range(len(rows)), key=lambda i: (-sizes[i][1], -sizes[i][0]))
    candidates = []
    max_width = max(s[0] for s in sizes)
    for width in np.linspace(max_width, available[0], 32):
        placed, cursor_x, cursor_y, shelf_depth = {}, 0., 0., 0.
        for index in order:
            sx, sy = sizes[index]
            if cursor_x and cursor_x + sx > width + 1e-6:
                cursor_x, cursor_y, shelf_depth = 0., cursor_y + shelf_depth + gap, 0.
            placed[index] = (cursor_x + sx / 2, cursor_y + sy / 2)
            cursor_x += sx + gap
            shelf_depth = max(shelf_depth, sy)
        occupied = np.array([max(placed[i][0] + sizes[i][0] / 2 for i in placed),
                             max(placed[i][1] + sizes[i][1] / 2 for i in placed)])
        if np.all(occupied <= available + 1e-6):
            score = max(occupied / available) + .05 * float(np.prod(occupied / available))
            candidates.append((score, occupied, placed))
    if not candidates:
        raise ValueError(f"The {len(rows)} specimens do not fit a centered plate with {border:g} mm model inset")
    _, occupied, placed = min(candidates, key=lambda item: item[0])
    return tuple(tuple(float(v) for v in np.array(placed[i]) - occupied / 2)
                 for i in range(len(rows)))


def replace_metadata(element, changes):
    for key, value in changes.items():
        for previous in list(element.findall(f"metadata[@key='{key}']")):
            element.remove(previous)
        writer.metadata(element, key, value)


def seam_recipe(identifier):
    method, gap = SEAMS[identifier]
    return dict(wall_generator="classic", seam_position="back",
                override_filament_scarf_seam_setting="1",
                seam_slope_conditional="1", scarf_angle_threshold="155",
                seam_slope_entire_loop="0", seam_slope_steps="10",
                seam_slope_inner_walls="1", seam_slope_min_length="10",
                seam_slope_start_height="10%",
                seam_slope_type="external" if method == "scarf" else "none",
                seam_gap=f"{gap:g}%" if method == "regular" else "15%",
                seam_slope_gap=f"{gap:g}%" if method == "scarf" else "0%")


def object_recipe(row, group):
    overrides = dict(row.get("object_overrides", {}))
    if row["id"] == "G":
        overrides["enable_support"] = "0"
    if group == "seam":
        overrides.update(seam_recipe(row["id"]))
    return overrides


def make_project(group, rows, baseline, project_group=None):
    PROJECTS.mkdir(parents=True, exist_ok=True)
    project_group = project_group or group
    project = PROJECTS / f"the-pour-{project_group}-petgf-left04-z004-mark2.3mf"
    border = 80.
    try:
        offsets = plate_layout(rows, baseline, border=border)
    except ValueError:
        border = 40.
        offsets = plate_layout(rows, baseline, border=border)
    report = writer.refresh(PROFILE, project,
                            parts=tuple((row["name"], source_path(row),
                                         float(row.get("rotation_x_degrees", 0))) for row in rows),
                            offsets=offsets, plate_border=border, z_trim=.04,
                            title=f"The Pour — {project_group}")
    with zipfile.ZipFile(project) as archive:
        members = {name: archive.read(name) for name in archive.namelist()}
    settings = json.loads(members[writer.SETTINGS_MEMBER])
    height = GROUP_HEIGHTS[group]
    changes = dict(layer_height=f"{height:g}", initial_layer_print_height="0.2")
    if group.startswith("finish-") or group == "seam":
        changes.update(seam_position="back", seam_gap="15%", seam_slope_type="none")
    if group in SUPPORT_GAPS:
        changes["support_top_z_distance"] = f"{SUPPORT_GAPS[group]:g}"
    settings.update(changes)
    settings["print_settings_id"] = f"The Pour {group} {height:g} mm PET-GF"
    members[writer.SETTINGS_MEMBER] = (json.dumps(settings, indent=2) + "\n").encode()
    config = ET.fromstring(members["Metadata/model_settings.config"])
    specimens = []
    for row, part in zip(rows, report["parts"], strict=True):
        overrides = object_recipe(row, group)
        cfg = config.find(f"object[@id='{part['object_id']}']")
        replace_metadata(cfg, overrides)
        specimen = dict(id=row["id"], name=row["name"], kind=row["kind"],
                        source=part["source"], source_stl_sha256=part["stl_sha256"],
                        identify_id=part["identify_id"], object_id=part["object_id"],
                        rotation_x_degrees=part["rotation_x_degrees"],
                        requested_layer_height_mm=height, object_overrides=overrides,
                        plate_bounds_mm=part["plate_bounds_mm"],
                        plate_offset_mm=list(offsets[len(specimens)]))
        if group == "seam":
            method, gap = SEAMS[row["id"]]
            specimen.update(seam_method=method, gap_percent_of_nozzle=gap,
                            gap_mm=.4 * gap / 100,
                            controlling_gap_key="seam_gap" if method == "regular" else "seam_slope_gap")
        if group in SUPPORT_GAPS:
            specimen["requested_support_top_gap_mm"] = SUPPORT_GAPS[group]
        for key in ("support_ceiling_z_mm", "ceiling_xy_bounds_mm"):
            if key in row:
                specimen[key] = row[key]
        specimens.append(specimen)
    members["Metadata/model_settings.config"] = writer.xml(config)
    writer.archive_write(project, members)
    report.update(project=str(project.relative_to(ROOT)), project_sha256=sha(project),
                  manifest_sha256=sha(MANIFEST), preparation_source_sha256=sha(__file__),
                  settings_sha256=hashlib.sha256(members[writer.SETTINGS_MEMBER]).hexdigest(),
                  settings_preserved_byte_for_byte=False,
                  layer_height_mm=height, requested_layer_height_mm=height,
                  first_layer_height_mm=.2, process=settings["print_settings_id"],
                  changes_after_profile_refresh=changes, print_settings_id=settings["print_settings_id"],
                  group=project_group, comparison_group=group, specimens=specimens,
                  printer_name="Mark2", requested_z_trim_mm=.04,
                  support_policy="Saved Tree(auto)/Default; automatic normal sections retained.",
                  support_top_z_distance_mm=float(settings["support_top_z_distance"]),
                  support_bottom_z_distance_mm=float(settings["support_bottom_z_distance"]),
                  preparation_only=True, submitted=False,
                  physical_result="Unprinted; finish, removal effort and tactile fit are unmeasured.",
                  transfer_limit="Coupon size changes cooling, perimeter length and layer return time. Physical references do not qualify complete product parts.")
    save(project.with_suffix(".print.json"), report)
    return project, report


def native_summary(project, report, archive_path, directory):
    with zipfile.ZipFile(archive_path) as archive:
        text = archive.read("Metadata/plate_1.gcode").decode()
        thumbnail = archive.read("Metadata/plate_1.png") if "Metadata/plate_1.png" in archive.namelist() else None
    gcode = directory / "plate_1.gcode"
    gcode.write_text(text)
    beads = writer.object_toolpaths(gcode, directory / "all-layer-beads.gcode", None)
    low, high = beads["extrusion_bounds_xy_mm"]
    bed_low, bed_high = report["shared_printable_area_mm"]
    margin = min(*(a-b for a,b in zip(low, bed_low)), *(b-a for a,b in zip(high, bed_high)))
    layers = [float(v) for v in re.findall(r"^; Z_HEIGHT:\s*([\d.]+)", text, re.M)]
    heights = [float(v) for v in re.findall(r"^; LAYER_HEIGHT:\s*([\d.]+)", text, re.M)]
    labels = sorted({int(v) for v in re.findall(r"^; (?:start printing object, unique label id:|OBJECT_ID:)\s*(\d+)", text, re.M)})
    estimated = re.search(r"total estimated time:\s*(.+)", text)
    grams = re.search(r"^; total filament weight \[g\]\s*:\s*([\d.,]+)", text, re.M)
    if thumbnail:
        (PROJECTS / f"{project.stem}.png").write_bytes(thumbnail)
    result = dict(archive=str(archive_path.relative_to(ROOT)), archive_sha256=sha(archive_path),
                gcode_sha256=hashlib.sha256(text.encode()).hexdigest(),
                layer_count=len(layers), first_layer_z_mm=layers[0] if layers else None,
                emitted_deposition_heights_mm=sorted({round(h, 4) for h in heights}),
                deposition_height_scope="Native LAYER_HEIGHT comments describe strand height, including 0.4 mm bridge strands. Per-object model_layer_steps_mm records the fixed model schedule.",
                model_object_identify_ids=labels,
                object_model_deposition=model_deposition_facts(text, report),
                estimated_time=estimated.group(1).strip() if estimated else None,
                saved_profile_filament_estimate_g=[float(v) for v in grams.group(1).split(",")] if grams else None,
                complete_layer_bead_bounds=beads, minimum_full_bead_bed_margin_mm=margin,
                emitted_z_trim_mm=[float(v) for v in re.findall(r"^\s*G29\.1 Z([-+.\d]+)", text, re.M)],
                support_feature_count=len(re.findall(r"^; FEATURE: Support", text, re.M)),
                support_gap_note="Requested Z distance is a slicer setting. Native layer quantization changes the commanded separation to the nominal roof underside. Strand-flow thickness, sag, removal and finish remain separate physical observations.",
                reviewer_sha256=sha(__file__), sliced_locally=True, submitted=False)
    if report["comparison_group"] in SUPPORT_GAPS:
        result["ceiling_support_reading"] = ceiling_support_reading(text, report)
    return result


def model_deposition_facts(text, report):
    """Retain native object layers and scarf-ramp witnesses from model deposition."""
    from enclosure_support_audit import _WORD

    facts = {s["identify_id"]: dict(id=s["id"], layers=set(), heights=set(),
                                   outer_wall_moves=0, outer_wall_z_moves=0)
             for s in report["specimens"]}
    current = None
    layer_z = height = None
    feature = ""
    for line in text.splitlines():
        label = re.match(r"; (?:start printing object, unique label id:|OBJECT_ID:)\s*(\d+)", line)
        if label:
            current = int(label.group(1))
        elif line.startswith("; stop printing object"):
            current = None
        elif line.startswith("; Z_HEIGHT:"):
            layer_z = float(line.split(":", 1)[1])
        elif line.startswith(("; LAYER_HEIGHT:", "; HEIGHT:")):
            height = float(line.split(":", 1)[1])
        elif line.startswith("; FEATURE:"):
            feature = line.split(":", 1)[1].strip()
        if current not in facts or layer_z is None:
            continue
        if not line.startswith(("G1 ", "G2 ", "G3 ")) or feature.startswith(("Support", "Skirt", "Brim", "Custom", "Prime")):
            continue
        words = {k: float(v) for k, v in _WORD.findall(line.split(";", 1)[0])}
        if words.get("E", 0) <= 0 or not ({"X", "Y"} & words.keys()):
            continue
        fact = facts[current]
        fact["layers"].add(layer_z)
        if height is not None:
            fact["heights"].add(height)
        if feature in ("Outer wall", "Overhang wall"):
            fact["outer_wall_moves"] += 1
            fact["outer_wall_z_moves"] += int("Z" in words)
    return [dict(id=f["id"], identify_id=identifier,
                 model_layer_count=len(f["layers"]),
                 model_layer_steps_mm=sorted({round(b-a, 4) for a, b in zip(sorted(f["layers"]), sorted(f["layers"])[1:])}),
                 model_deposition_heights_mm=sorted({round(h, 4) for h in f["heights"]}),
                 deposition_height_scope="Strand heights include native bridge thickness; model Z steps describe the nominal layer schedule.",
                 outer_wall_depositing_moves=f["outer_wall_moves"],
                 outer_wall_depositing_moves_with_z=f["outer_wall_z_moves"],
                 z_witness_scope="Explicit Z on depositing outer-wall moves witnesses native height ramps; it does not measure seam flatness.")
            for identifier, f in facts.items()]


def ceiling_support_reading(text, report):
    """Read support nozzle Z and the first roof's nominal layer slab.

    The slab underside uses the fixed model schedule, not a bridge strand's
    flow height. This does not measure deposited shape or physical free air.
    """
    from enclosure_support_audit import _WORD, _arc_points

    specimen = report["specimens"][0]
    if "support_ceiling_z_mm" not in specimen or "ceiling_xy_bounds_mm" not in specimen:
        return dict(scope="No flat-ceiling window supplied; no contact-gap reading.")
    part = report["parts"][0]
    center = np.array(part["source_center_mm"])
    translation = np.array(part["plate_translation_mm"])
    window = np.array(specimen["ceiling_xy_bounds_mm"], dtype=float)
    # Exported specimens stand in their manufacturing frame, without a 3MF turn.
    if abs(part["rotation_x_degrees"]) > 1e-6:
        return dict(scope="Flat-ceiling reading requires a bed-normalized specimen.")
    window += translation[:2] - center[:2]
    ceiling = float(specimen["support_ceiling_z_mm"]) + translation[2] - center[2]
    # Avoid the corner transition and vertical jambs at the window boundary.
    inset = np.minimum((window[1] - window[0]) / 5., 1.)
    low, high = window[0] + inset, window[1] - inset
    x = y = e = 0.
    layer_z = height = None
    feature = ""
    absolute_xy, relative_e = True, True
    support_z = set()
    nominal_height = float(report["requested_layer_height_mm"])
    model_deposits = set()
    for raw in text.splitlines():
        line = raw.strip()
        if line.startswith("; Z_HEIGHT:"):
            layer_z = float(line.split(":", 1)[1])
        elif line.startswith(("; LAYER_HEIGHT:", "; HEIGHT:")):
            height = float(line.split(":", 1)[1])
        elif line.startswith("; FEATURE:"):
            feature = line.split(":", 1)[1].strip()
        code = line.split(";", 1)[0].strip()
        if not code:
            continue
        command = code.split(None, 1)[0]
        words = {k: float(v) for k, v in _WORD.findall(code)}
        if command in {"G90", "G91"}:
            absolute_xy = command == "G90"
        elif command in {"M82", "M83"}:
            relative_e = command == "M83"
        elif command == "G92":
            x, y, e = words.get("X", x), words.get("Y", y), words.get("E", e)
        elif command in {"G0", "G1", "G2", "G3"}:
            nx = words.get("X", x) if absolute_xy else x + words.get("X", 0.)
            ny = words.get("Y", y) if absolute_xy else y + words.get("Y", 0.)
            de = words.get("E", 0.) if relative_e else words.get("E", e) - e
            if de > 1e-9 and layer_z is not None and (nx != x or ny != y):
                points = [(x, y), (nx, ny)] if command in {"G0", "G1"} else _arc_points((x, y), (nx, ny), words, command == "G2")
                points = np.array(points)
                occupied = np.any(np.all((points >= low) & (points <= high), axis=1))
                # A straight deposit may cross the window with both ends outside it.
                p_low, p_high = points.min(axis=0), points.max(axis=0)
                crosses = np.all(p_high >= low) and np.all(p_low <= high)
                if occupied or crosses:
                    if feature.startswith("Support") and layer_z < ceiling:
                        support_z.add(round(layer_z, 5))
                    elif feature in ("Bottom surface", "Bridge", "Internal solid infill") and height is not None and layer_z >= ceiling:
                        model_deposits.add((round(layer_z, 5), round(height, 5), feature))
            x, y = nx, ny
            if "E" in words:
                e = e + words["E"] if relative_e else words["E"]
    roof_z = min((z for z, _, _ in model_deposits), default=None)
    roof = (round(roof_z-nominal_height, 5), roof_z, nominal_height) if roof_z is not None else None
    first_strands = [(height, feature) for z, height, feature in sorted(model_deposits) if z == roof_z]
    top = max(support_z) if support_z else None
    separation = round(roof[0]-top, 5) if roof and top is not None else None
    return dict(scope="Commanded separation from the highest support nozzle Z to the first roof's nominal underside (roof nozzle Z minus fixed model layer height), within the flat-ceiling window. Circular strand flow height and physical sag do not define this nominal underside; deposited free-air gap and bead shape are unmeasured.",
                nominal_cad_ceiling_z_mm=round(ceiling, 5),
                sampled_window_xy_mm=[low.tolist(), high.tolist()],
                requested_support_top_gap_mm=specimen["requested_support_top_gap_mm"],
                highest_support_nozzle_z_mm=top,
                first_ceiling_model_nozzle_z_mm=roof_z,
                nominal_model_layer_height_mm=nominal_height,
                first_ceiling_model_slab_mm=list(roof) if roof else None,
                first_ceiling_strand_flow_heights_mm=sorted({height for height, _ in first_strands}),
                first_ceiling_features=sorted({feature for _, feature in first_strands}),
                commanded_nominal_roof_separation_mm=separation,
                commanded_slab_gap_mm=separation,
                support_layer_tops_below_ceiling_mm=sorted(support_z))


def native_slice(project, report):
    directory = WORK / report["group"]
    directory.mkdir(parents=True, exist_ok=True)
    archive_name = project.stem + ".gcode.3mf"
    command = [str(SLICER), "--slice", "0", "--arrange", "0", "--orient", "0",
               "--outputdir", str(directory), "--export-3mf", archive_name, str(project)]
    save(directory / "slice-command.json", dict(argv=command, printer_connection=False))
    print(f"Native slicing {report['group']}: {len(report['specimens'])} specimens", flush=True)
    with (directory / "slice.log").open("w") as log:
        result = subprocess.run(command, cwd=directory, stdout=log, stderr=subprocess.STDOUT)
    if result.returncode:
        raise RuntimeError(f"Bambu Studio exited {result.returncode}: {directory / 'slice.log'}")
    archive_path = directory / archive_name
    report["native"] = native_summary(project, report, archive_path, directory)
    save(project.with_suffix(".print.json"), report)
    reading = report["native"]
    print(json.dumps(dict(group=report["group"], estimated_time=reading["estimated_time"],
                          filament_g=reading["saved_profile_filament_estimate_g"],
                          layers=reading["layer_count"],
                          full_bead_margin_mm=round(reading["minimum_full_bead_bed_margin_mm"], 2),
                          ceiling_gap_mm=reading.get("ceiling_support_reading", {}).get("commanded_slab_gap_mm"))), flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument("--slice", action="store_true", help="Run local Bambu Studio CLI; do not submit a print")
    modes.add_argument("--review", action="store_true", help="Read existing native archives without re-preparing or re-slicing")
    parser.add_argument("--group", choices=tuple(GROUP_HEIGHTS), action="append", help="Prepare only these project groups")
    args = parser.parse_args()
    manifest = json.loads(MANIFEST.read_text())
    with zipfile.ZipFile(PROFILE) as archive:
        baseline = json.loads(archive.read(writer.SETTINGS_MEMBER))
    groups = defaultdict(list)
    for row in manifest["printable"]:
        group = row["print_group"]
        if group not in GROUP_HEIGHTS:
            raise ValueError(f"{row['id']} declares unsupported print_group {group!r}; expected one of {', '.join(GROUP_HEIGHTS)}")
        if not args.group or group in args.group:
            groups[group].append(row)
    if args.group:
        absent = set(args.group) - groups.keys()
        if absent:
            raise ValueError(f"The printable manifest has no specimens for {', '.join(sorted(absent))}")
    reports = []
    if args.review:
        for path in sorted(PROJECTS.glob("*.print.json")):
            report = json.loads(path.read_text())
            if args.group and report["comparison_group"] not in args.group:
                continue
            if "native" not in report:
                continue
            project = ROOT / report["project"]
            if sha(project) != report["project_sha256"]:
                raise ValueError(f"{project.name} differs from the input project recorded for its native slice")
            archive_path = ROOT / report["native"]["archive"]
            if sha(archive_path) != report["native"]["archive_sha256"]:
                raise ValueError(f"{archive_path.name} differs from its recorded native slice")
            report["native"] = native_summary(project, report, archive_path, archive_path.parent)
            save(path, report)
            reports.append(report)
    else:
        for group in GROUP_HEIGHTS:
            if group not in groups:
                continue
            batches = [groups[group]]
            if group == "kit":
                batches = split_kit(groups[group], baseline)
            for index, batch in enumerate(batches, 1):
                label = group if len(batches) == 1 else f"{group}-{index:02d}"
                project, report = make_project(group, batch, baseline, project_group=label)
                if args.slice:
                    native_slice(project, report)
                reports.append(report)
        remove_stale_projects(groups.keys(), {r["project"] for r in reports})
    if args.group or args.review:
        # Carrier/display-placement refinements do not change a stable specimen's
        # manufacturing geometry. Keep its already-sliced project when every
        # specimen and recipe still belongs to the current printable manifest.
        current = {row["id"]: row for row in manifest["printable"]}
        held_reports = [json.loads(path.read_text()) for path in sorted(PROJECTS.glob("*.print.json"))]
        reports = [r for r in held_reports if all(
            specimen["id"] in current
            and current[specimen["id"]]["print_group"] == r["comparison_group"]
            and float(current[specimen["id"]].get("rotation_x_degrees", 0)) == specimen["rotation_x_degrees"]
            and object_recipe(current[specimen["id"]], r["comparison_group"]) == specimen["object_overrides"]
            and sha(source_path(current[specimen["id"]])) == specimen["source_stl_sha256"]
            for specimen in r.get("specimens", []))
            and r.get("settings_source_sha256") == sha(PROFILE)]
    specimen_ids = [s["id"] for r in reports for s in r["specimens"]]
    complete_native = bool(reports) and all("native" in r for r in reports)
    seconds = sum(sum(int(v) * {"h": 3600, "m": 60, "s": 1}[unit]
                      for v, unit in re.findall(r"(\d+)\s*([hms])", r["native"].get("estimated_time") or ""))
                  for r in reports) if complete_native else None
    grams = sum(sum(r["native"].get("saved_profile_filament_estimate_g") or [])
                for r in reports) if complete_native else None
    index = dict(schema=1, name="The Pour", material="Fiberon PET-GF15", nozzle_mm=.4,
                 printer="Mark2", requested_z_trim_mm=.04, first_layer_height_mm=.2,
                 manifest=str(MANIFEST.relative_to(ROOT)), manifest_sha256=sha(MANIFEST),
                 settings_source=str(PROFILE.relative_to(ROOT)), settings_source_sha256=sha(PROFILE),
                 preparation_source_sha256=sha(__file__), projects=reports,
                 project_count=len(reports), native_project_count=sum("native" in r for r in reports),
                 printable_specimen_count=len(specimen_ids), unique_specimen_count=len(set(specimen_ids)),
                 total_saved_profile_estimated_seconds=seconds,
                 total_saved_profile_filament_estimate_g=round(grams, 2) if grams is not None else None,
                 physical_result="Unprinted; comparative specimens have no physical acceptance.",
                 preparation_only=True, submitted=False)
    save(HERE / "print-preparation.json", index)
    print(f"Prepared {len(reports)} The Pour projects; no jobs submitted", flush=True)


def split_kit(rows, baseline):
    """Give the complete kit as many centered plates as its actual footprint needs."""
    sizes = {row["id"]: print_size(row) for row in rows}
    ordered = sorted(rows, key=lambda row: -float(np.prod(sizes[row["id"]][:2])))
    batches = []
    for row in ordered:
        for batch in batches:
            try:
                plate_layout([*batch, row], baseline, border=40.)
            except ValueError:
                continue
            batch.append(row)
            break
        else:
            batches.append([row])
    return batches


def remove_stale_projects(selected_groups, current_projects):
    """Keep only this preparation's editable plates for the selected families."""
    for path in PROJECTS.glob("*.print.json"):
        report = json.loads(path.read_text())
        if report.get("comparison_group") not in selected_groups or report.get("project") in current_projects:
            continue
        project = ROOT / report["project"]
        if project.parent != PROJECTS or not project.name.startswith("the-pour-"):
            continue
        for obsolete in (project, project.with_suffix(".print.json"), project.with_suffix(".png")):
            obsolete.unlink(missing_ok=True)


if __name__ == "__main__":
    main()
