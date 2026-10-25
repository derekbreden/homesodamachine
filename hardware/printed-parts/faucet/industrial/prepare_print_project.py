"""Prepare the complete Industrial faucet with the accepted PET-GF recipe.

The project contains the Industrial base, relaxed cover and mounting plate,
plus the shared faucet tip and side-down lever. The TPU gasket is a separate print. Optional
slicing runs Bambu Studio locally and never connects to a printer.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys
import xml.etree.ElementTree as ET
import zipfile

import numpy as np
import trimesh


HERE = Path(__file__).resolve().parent
FAUCET = HERE.parent
sys.path.insert(0, str(FAUCET))
import refresh_print_project as writer

TITLE = "Industrial faucet PET-GF"
PROJECT = HERE / "faucet-industrial-petgf.3mf"
ACCEPTANCE = HERE / "physical-acceptance.json"
ACCEPTED = json.loads(ACCEPTANCE.read_text())
RECIPE = writer.ROOT / ACCEPTED["prepared_project"]
PROFILE = RECIPE
FINISH = HERE / "finish-selection.json"
GASKET = HERE / "industrial-above-counter-gasket.stl"
# Separate spaces for each part's brim and automatically generated supports.
PART_OFFSETS = ((-77.0, 0.0), (20.0, 47.0), (89.0, 86.0), (43.0, -52.0), (-17.5, -60.0))
PROTECTED_SCULPTED = tuple((FAUCET / "faucet-petgf.3mf").with_suffix(suffix) for suffix in (
    ".3mf", ".print.json", ".support-audit.json", ".readiness.json"))


def relative(path: Path) -> str:
    path = path.resolve()
    return str(path.relative_to(writer.ROOT) if path.is_relative_to(writer.ROOT) else path)


def profile_members(path: Path) -> dict[str, bytes]:
    with zipfile.ZipFile(path) as archive:
        return {
            name: archive.read(name)
            for name in archive.namelist()
            if name == writer.SETTINGS_MEMBER
            or name.startswith("Metadata/filament_settings_") and name.endswith(".config")
        }


def protected_hashes() -> dict[str, str]:
    return {relative(path): writer.digest(path.read_bytes())
            for path in PROTECTED_SCULPTED if path.is_file()}


def industrial_parts() -> tuple:
    # Assembly-frame STLs use the shared production print rotations.
    rotations = {name: rotation for name, _, rotation in writer.PARTS}
    parts = (
        ("industrial-shell-base", HERE / "industrial-shell-base.stl",
         rotations["faucet-shell-base"]),
        ("faucet-shell-tip", FAUCET / "faucet-shell/faucet-shell-tip.stl",
         rotations["faucet-shell-tip"]),
        ("industrial-display-cover", HERE / "industrial-display-cover.stl",
         rotations["faucet-display-cover"]),
        ("industrial-above-counter-plate", HERE / "industrial-above-counter-plate.stl", 0.0),
        ("lever-replica", FAUCET / "lever-replica/lever-replica-side-down.stl", 0.0),
    )
    missing = [relative(path) for _, path, _ in parts if not path.is_file()]
    if missing:
        raise FileNotFoundError("Generate the Industrial STLs before preparing the project: "
                                + ", ".join(missing))
    return parts


def enforce_rear_seam(members: dict[str, bytes], report: dict, target: dict) -> dict:
    """Paint the complete rear silhouette in the actual build pose.

    Include the tilted stage shoulders as well as the cylindrical/curved faces.
    Select using each facet's center-strip intersection, rather than its centroid:
    long stage facets can span several transitions. Geometry is unchanged.
    """
    row = next(p for p in report["parts"] if p["name"] == target["part"])
    root = ET.fromstring(members[row["member"]])
    mesh = root.find(f".//{writer.qn('mesh')}")
    vertices = np.array([[float(v.get(k)) for k in "xyz"]
                         for v in mesh.find(writer.qn("vertices"))])
    vertices += row["source_center_mm"]
    triangles = list(mesh.find(writer.qn("triangles")))
    indices = np.array([[int(t.get(k)) for k in ("v1", "v2", "v3")]
                        for t in triangles])
    points = vertices[indices]
    rotation = np.array(row["build_transform"][:9]).reshape(3, 3)
    build_vertices = vertices @ rotation
    build_points = build_vertices[indices]
    normals = np.cross(build_points[:, 1] - build_points[:, 0],
                       build_points[:, 2] - build_points[:, 0])
    normals /= np.maximum(np.linalg.norm(normals, axis=1), 1e-12)[:, None]
    half_width = target["half_width_mm"]
    selected = ((normals[:, 1] > 1e-5) & (abs(normals[:, 0]) < .35)
                & (points[:, :, 0].min(axis=1) <= half_width)
                & (points[:, :, 0].max(axis=1) >= -half_width))
    # Read the rear boundary at build Z, following its translation in plate Y.
    # CAD-horizontal sections omit the tilted shoulder surfaces.
    shape = trimesh.Trimesh(vertices=build_vertices, faces=indices, process=False)
    segments = trimesh.intersections.mesh_plane(shape, [1, 0, 0], [0, 0, 0])
    low = segments[:, :, 2].min(axis=1)
    high = segments[:, :, 2].max(axis=1)
    if target.get("surface") == "curved_outer_arc":
        import faucet_paths
        arc_center = np.array([faucet_paths.WATER_Y - faucet_paths.WATER_RADIUS,
                               faucet_paths.ARC_START_Z])
        arc_radius = (faucet_paths.WATER_RADIUS + faucet_paths.SHELL_CENTER_N
                      + faucet_paths.SHELL_RADIUS)
    for index in np.flatnonzero(selected):
        triangle = build_points[index]
        xmin, xmax = triangle[:, 0].min(), triangle[:, 0].max()
        x = min(max(0.0, xmin + 1e-9), xmax - 1e-9)
        cuts = []
        for a, b in ((triangle[0], triangle[1]), (triangle[1], triangle[2]),
                     (triangle[2], triangle[0])):
            if (a[0] - x) * (b[0] - x) <= 0 and abs(a[0] - b[0]) > 1e-10:
                cuts.append(a + (b - a) * (x - a[0]) / (b[0] - a[0]))
        if len(cuts) < 2:
            selected[index] = False
            continue
        midpoint = np.mean(cuts, axis=0)
        if target.get("surface") == "curved_outer_arc":
            cad_midpoint = midpoint @ rotation.T
            if abs(np.linalg.norm(cad_midpoint[1:] - arc_center) - arc_radius) > .15:
                selected[index] = False
                continue
        z = midpoint[2]
        section = segments[(low <= z) & (high >= z)]
        dz = section[:, 1, 2] - section[:, 0, 2]
        section = section[abs(dz) > 1e-8]
        dz = section[:, 1, 2] - section[:, 0, 2]
        y = section[:, 0, 1] + (z - section[:, 0, 2]) / dz * (section[:, 1, 1] - section[:, 0, 1])
        if not len(y) or abs(midpoint[1] - y.max()) > .15:
            selected[index] = False
    for index in np.flatnonzero(selected):
        triangles[index].set("paint_seam", "4")
    members[row["member"]] = writer.xml(root)
    model = ET.fromstring(members["3D/3dmodel.model"])
    version = model.find(f"{writer.qn('metadata')}[@name='BambuStudio:SeamPaintingVersion']")
    if version is None:
        version = ET.SubElement(model, writer.qn("metadata"), name="BambuStudio:SeamPaintingVersion")
    version.text = "0"
    members["3D/3dmodel.model"] = writer.xml(model)
    chosen = points[selected].reshape(-1, 3)
    return {**target, "enforced_triangles": int(selected.sum()),
            "painted_facet_bounds_cad_mm": [chosen.min(axis=0).tolist(), chosen.max(axis=0).tolist()],
            "mesh_vertices_and_triangle_indices_unchanged": True}


def shoulder_readings(report: dict, recipe_report: dict) -> list[dict]:
    row = report["parts"][0]
    mesh = trimesh.load(writer.ROOT / row["source"], force="mesh", process=True)
    rotation = np.array(row["build_transform"][:9]).reshape(3, 3)
    readings = []
    for reference in recipe_report["selected_faces"]:
        z = reference["cad_z_mm"]
        mask = ((np.abs(mesh.triangles[:, :, 2] - z).max(axis=1) < 1e-5)
                & (mesh.face_normals[:, 2] > .9999))
        if not mask.any():
            raise ValueError(f"The current base has no upward shoulder at CAD Z{z:g}")
        points = mesh.triangles[mask].reshape(-1, 3)
        placed = (points - row["source_center_mm"]) @ rotation + row["plate_translation_mm"]
        readings.append({"cad_z_mm": z, "pick_mm": reference["pick_mm"],
                         "measurement": "Current source STL upward planar facets at the selected CAD Z",
                         "area_mm2": float(mesh.area_faces[mask].sum()),
                         "cad_bounds_mm": [points.min(axis=0).tolist(), points.max(axis=0).tolist()],
                         "print_z_span_mm": [float(placed[:, 2].min()), float(placed[:, 2].max())],
                         "fine_band_print_z_mm": reference["fine_band_print_z_mm"]})
    return readings


def write_readiness(project: Path, report: dict, reading: dict | None = None,
                    slice_directory: Path | None = None) -> dict:
    """Record what this offline preparation actually checked."""
    result = {
        "project_title": TITLE,
        "status": ("selected finish offline slice and support audit passed"
                   if reading is not None else "complete current project prepared with selected finish; native review pending"),
        "preparation_only": True,
        "launch_authorized": False,
        "finish_choices_pending": [],
        "finish_selection": relative(FINISH),
        "project": relative(project),
        "project_sha256": report["project_sha256"],
        "settings_sha256": report["settings_sha256"],
        "print_report_sha256": writer.digest(project.with_suffix(".print.json").read_bytes()),
        "profile_source": report["profile_source"],
        "all_profile_members_preserved_byte_for_byte": report["all_profile_members_preserved_byte_for_byte"],
        "source_stls": {part["source"]: part["stl_sha256"] for part in report["parts"]},
        "mesh_and_placement": {
            "closed_oriented_single_body_meshes": True,
            "embedded_meshes_match_source_stls": True,
            "parts": len(report["parts"]),
            "plates": report["plate_count"],
            "minimum_required_model_bed_margin_mm": 40.0,
        },
        "offline_slice": {"completed": reading is not None},
        "printer_submission": {"performed_by_this_tool": False},
        "physical_print": {
            "evaluated": False,
            "remaining": "Support removal, contact finish, display fit and retention are physical print readings.",
        },
        "gasket": {"source": relative(GASKET), "material": "TPU", "included_in_petgf_project": False},
        "color": "The same meshes and project geometry serve black and white PET-GF.",
        "sculpted_artifacts_unchanged": report["sculpted_artifacts_unchanged"],
    }
    if reading is not None:
        result["offline_slice"].update({
            "directory": relative(slice_directory),
            "slicer": reading["slicer"],
            "support_audit_sha256": writer.digest(project.with_suffix(".support-audit.json").read_bytes()),
            "plates": reading["plates"],
            "fit": reading["fit"],
            "physical_support_removal_validated": False,
        })
    project.with_suffix(".readiness.json").write_text(json.dumps(result, indent=2) + "\n")
    return result


def apply_overhang_recipe(settings: dict, selected: dict) -> dict:
    """Keep ordinary PET-GF paths uncooled; cool bridges and qualifying overhangs."""
    changes = writer.petgf_cooling.apply(settings)

    def put(key, value):
        old = settings[key]
        new = [str(value)] * len(old) if isinstance(old, list) else str(value)
        if old != new:
            changes[key] = {"from": old, "to": new}
            settings[key] = new

    put("overhang_fan_speed", selected["fan_percent"])
    put("overhang_fan_threshold", selected["fan_threshold"])
    for key in ("close_fan_the_first_x_layers", "close_additional_fan_first_x_layers"):
        put(key, selected["fan_off_bed_layers"])
    for key in ("first_x_layer_fan_speed", "first_x_layer_part_fan_speed"):
        put(key, 0)
    for key in ("bridge_speed", "filament_bridge_speed"):
        put(key, selected["bridge_speed_mm_s"])
    put("bridge_flow", selected["bridge_flow"])
    maximum = selected["maximum_overhang_speed_mm_s"]
    for prefix in ("", "filament_"):
        for kind in ("1_4", "2_4", "3_4", "4_4", "totally"):
            key = f"{prefix}overhang_{kind}_speed"
            old = settings[key]
            new = [str(min(float(v), maximum)) if float(v) > 0 else str(maximum) for v in old]
            if old != new:
                changes[key] = {"from": old, "to": new}
                settings[key] = new
    return changes


def refresh(settings_from: Path = PROFILE, output: Path = PROJECT,
            printer: str | None = None, filament_colour: str | None = None) -> dict:
    settings_from, output = settings_from.resolve(), output.resolve()
    finish = json.loads(FINISH.read_text())
    printer = printer or finish["default_printer"]
    trim = {"Mark1": .18, "Mark2": .04}[printer]
    filament_colour = filament_colour or finish["default_filament_colour"]
    if output == settings_from or output == RECIPE.resolve() or output in {path.resolve() for path in PROTECTED_SCULPTED}:
        raise ValueError("The Industrial output must not replace its settings source or the Sculpted project")
    if output.suffix.lower() != ".3mf":
        raise ValueError("The Industrial project needs a .3mf filename")
    before = protected_hashes()
    if writer.digest(RECIPE.read_bytes()) != ACCEPTED["prepared_project_sha256"]:
        raise ValueError("The accepted five-part recipe has changed")
    recipe_report = json.loads((RECIPE.parent / "preparation.json").read_text())
    preserved = profile_members(settings_from)
    parts = industrial_parts()
    report = writer.refresh(settings_from, output, parts=parts,
                            offsets=PART_OFFSETS, title=TITLE, plate_border=40.0,
                            z_trim=trim)
    # The complete foot receives solid infill with the ordinary wall settings.
    regions = tuple({"part": r["part"], "name": r["name"],
                     "source_bounds_mm": r["source_bounds_mm"], "clip_to_part_bounds": False}
                    for r in recipe_report["local_solid_regions"])
    writer.add_local_solid_regions(output, report, regions)
    with zipfile.ZipFile(output) as archive, zipfile.ZipFile(RECIPE) as recipe:
        members = {name: archive.read(name) for name in archive.namelist()}
        config = ET.fromstring(members["Metadata/model_settings.config"])
        source_config = ET.fromstring(recipe.read("Metadata/model_settings.config"))
        source_objects = {obj.find("metadata[@key='name']").get("value"): obj
                          for obj in source_config.findall("object")}
        for obj in config.findall("object"):
            name = obj.find("metadata[@key='name']").get("value")
            for setting in source_objects[name].findall("metadata"):
                key = setting.get("key")
                if key and key not in ("name", "extruder"):
                    writer.metadata(obj, key, setting.get("value"))
        members["Metadata/model_settings.config"] = writer.xml(config)
        members["Metadata/layer_config_ranges.xml"] = recipe.read("Metadata/layer_config_ranges.xml")
        settings = json.loads(members[writer.SETTINGS_MEMBER])
        original_colour = settings["filament_colour"]
        settings["filament_colour"] = [filament_colour]
        for key, value in finish["filament_overrides"].items():
            settings[key][0] = value
        layer_changes = {}
        for key, value in {
            "layer_height": str(finish["normal_layer_height_mm"]),
            "initial_layer_print_height": str(finish["first_bed_layer_height_mm"]),
            "independent_support_layer_height": "0",
        }.items():
            if settings[key] != value:
                layer_changes[key] = {"from": settings[key], "to": value}
                settings[key] = value
        overhang_changes = apply_overhang_recipe(settings, finish["overhang_recipe"])
        members[writer.SETTINGS_MEMBER] = (json.dumps(settings, indent=2) + "\n").encode()
        for obj in config.findall("object"):
            name = obj.find("metadata[@key='name']").get("value")
            for setting in list(obj.findall("metadata")):
                key = setting.get("key", "")
                if key.startswith("seam_") or key in ("scarf_angle_threshold", "override_filament_scarf_seam_setting"):
                    obj.remove(setting)
            overrides = (finish["seam_object_overrides"] if name in finish["seam_parts"]
                         else finish["corner_seam_object_overrides"])
            for key, value in overrides.items():
                writer.metadata(obj, key, value)
        ranges = ET.Element("objects")
        bands = finish.get("base_fine_bands_print_z_mm", [])
        if bands:
            # Bambu layer ranges use one-based object order, not 3MF resource IDs.
            base_index = next(i for i, p in enumerate(report["parts"], 1)
                              if p["name"] == "industrial-shell-base")
            band_object = ET.SubElement(ranges, "object", id=str(base_index))
            for low, high in bands:
                band = ET.SubElement(band_object, "range", min_z=f"{low:.4f}", max_z=f"{high:.4f}")
                ET.SubElement(band, "option", opt_key="layer_height").text = str(finish["fine_layer_height_mm"])
        members["Metadata/model_settings.config"] = writer.xml(config)
        members["Metadata/layer_config_ranges.xml"] = writer.xml(ranges)
    if finish.get("rear_seam_enforcement"):
        report["rear_seam_enforcement"] = enforce_rear_seam(members, report, finish["rear_seam_enforcement"])
    if finish.get("tip_rear_seam_enforcement"):
        report["tip_rear_seam_enforcement"] = enforce_rear_seam(members, report, finish["tip_rear_seam_enforcement"])
    if finish.get("base_rim_supports"):
        from rim_supports import add_selected_base_rim
        report["base_rim_supports"] = add_selected_base_rim(members, report, finish["base_rim_supports"])
    if finish.get("tip_supports"):
        from tip_supports import add_selected_tip_supports
        report["tip_supports"] = add_selected_tip_supports(members, report, finish["tip_supports"])
    writer.archive_write(output, members)
    if report["plate_count"] != 1 or len(report["parts"]) != 5:
        raise ValueError("The complete Industrial project needs five rigid parts on one plate")
    actual_profile = profile_members(output)
    before_settings = json.loads(preserved[writer.SETTINGS_MEMBER])
    after_settings = json.loads(actual_profile[writer.SETTINGS_MEMBER])
    changed_settings = {k for k in set(before_settings) | set(after_settings)
                        if before_settings.get(k) != after_settings.get(k)}
    if changed_settings - {"machine_start_gcode", "printer_settings_id", "filament_colour",
                           *finish["filament_overrides"], *overhang_changes,
                           *layer_changes,
                           *writer.petgf_cooling.VALUES}:
        raise ValueError("Unexpected change to the complete PET-GF profile")
    normalized_profile = dict(preserved)
    writer.petgf_cooling.apply_members(normalized_profile)
    if any(actual_profile.get(n) != data for n, data in normalized_profile.items()
           if n != writer.SETTINGS_MEMBER):
        raise ValueError("A non-cooling PET-GF filament setting changed")
    if protected_hashes() != before:
        raise ValueError("A Sculpted project artifact changed during Industrial preparation")
    for row in report["parts"]:
        if writer.digest((writer.ROOT / row["source"]).read_bytes()) != row["stl_sha256"]:
            raise ValueError(f"{row['name']} changed while preparing the project")
    report.update({
        "project_title": TITLE,
        "profile_source": relative(settings_from),
        "project_sha256": writer.digest(output.read_bytes()),
        "settings_sha256": writer.digest(actual_profile[writer.SETTINGS_MEMBER]),
        "native_settings_sha256": writer.digest(actual_profile[writer.SETTINGS_MEMBER]),
        "all_profile_members_preserved_byte_for_byte": actual_profile == preserved,
        "profile_member_sha256": {name: writer.digest(data) for name, data in actual_profile.items()},
        "sculpted_artifacts_unchanged": before,
        "shared_tip_source": relative(parts[1][1]),
        "gasket_included": False,
        "color_independent_geometry": True,
        "accepted_recipe": relative(RECIPE),
        "accepted_recipe_sha256": ACCEPTED["prepared_project_sha256"],
        "accepted_geometry_tag": ACCEPTED["tag"],
        "active_nozzle": 0,
        "printer": printer,
        "requested_z_trim_mm": trim,
        "layer_height_mm": float(after_settings["layer_height"]),
        "first_bed_layer_height_mm": float(after_settings["initial_layer_print_height"]),
        "selected_faces": shoulder_readings(report, recipe_report),
        "insert_review_regions": recipe_report["insert_review_regions"],
        "review_host_regions": recipe_report["review_host_regions"],
        "preparation_only": True,
        "launch_authorized": False,
        "submitted": False,
        "send_attempted": False,
        "finish_choices_pending": [],
        "finish_selection": relative(FINISH),
        "selected_finish": finish,
        "selected_finish_scope": "A2 with Back on base, tip and mounting plate; complete build-pose rear seam enforcement on the base and matching exposed curved tip meridian; default corner seams on cover and lever; selected base layer bands with ordinary layers elsewhere and independent support heights off; native125% bridge flow; ordinary part cooling off, 70% on bridges and walls with at least 50% unsupported bead width after three off bed layers; Bridge15mm/s and overhang limits<=15 preserving existing10mm/s; accepted segmented base-rim arcs, tip eight fins and local lip trees, and the removable hidden-root disc. Tree(auto)/Default elsewhere.",
        "base_layer_bands": [{"print_z_mm": band, "layer_height_mm": finish["fine_layer_height_mm"]}
                             for band in bands],
    })
    for key in finish["filament_overrides"]:
        if before_settings.get(key) != after_settings.get(key):
            report["settings_changes"][key] = {"from": before_settings.get(key), "to": after_settings.get(key)}
    report["settings_changes"].update(overhang_changes)
    report["settings_changes"].update(layer_changes)
    if original_colour != [filament_colour]:
        report["settings_changes"]["filament_colour"] = {"from": original_colour, "to": [filament_colour]}
    for face in report["selected_faces"]:
        face.pop("fine_band_print_z_mm", None)
        face["model_layer_height_mm"] = float(after_settings["layer_height"])
    from prepare_vent_prints import source_hashes
    report["source_sha256"] = source_hashes(parts)
    for path in (Path(__file__), RECIPE, ACCEPTANCE, FINISH):
        report["source_sha256"][relative(path)] = writer.digest(path.read_bytes())
    if report.get("base_rim_supports"):
        for path in (HERE / 'rim_supports.py', writer.ROOT / finish['base_rim_supports']['source_project']):
            report['source_sha256'][relative(path)] = writer.digest(path.read_bytes())
    if report.get("tip_supports"):
        for path in (HERE / 'tip_supports.py', writer.ROOT / finish['tip_supports']['source_project']):
            report['source_sha256'][relative(path)] = writer.digest(path.read_bytes())
    output.with_suffix(".print.json").write_text(json.dumps(report, indent=2) + "\n")
    write_readiness(output, report)
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", type=Path, default=PROJECT)
    parser.add_argument("--settings-from", type=Path, default=PROFILE)
    parser.add_argument("--printer", choices=("Mark1", "Mark2"),
                        help="Apply this printer's standard Z trim; default is the selected finish recipe's printer.")
    parser.add_argument("--filament-colour", help="Spool colour reported by the destination printer, as #RRGGBB.")
    parser.add_argument("--slice-output", type=Path,
                        help="Optional empty directory for an offline Bambu Studio slice; no printer connection.")
    parser.add_argument("--slicer", type=Path,
                        default=Path("/Applications/BambuStudio.app/Contents/MacOS/BambuStudio"))
    args = parser.parse_args()
    directory = args.slice_output.resolve() if args.slice_output else None
    if directory and directory.exists() and any(directory.iterdir()):
        parser.error("--slice-output must be empty so the audit cannot consume an earlier slice")
    project = args.project.resolve()
    report = refresh(args.settings_from, project, args.printer, args.filament_colour)
    print(f"{project}: five rigid parts on one plate; exact PET-GF settings {report['settings_sha256']}", flush=True)
    for row in report["parts"]:
        print(f"  {row['name']}: Rx {row['rotation_x_degrees']:g} degrees; {row['triangles']} triangles", flush=True)
    if directory is None:
        return
    before = protected_hashes()
    directory.mkdir(parents=True, exist_ok=True)
    command = [str(args.slicer.resolve()), "--slice", "0", "--arrange", "0", "--orient", "0",
               "--outputdir", str(directory), str(project)]
    log = directory / "bambu-cli.log"
    with log.open("w") as stream:
        result = subprocess.run(command, cwd=directory, stdout=stream, stderr=subprocess.STDOUT)
    print(f"Offline slice exited {result.returncode}; {log}", flush=True)
    if result.returncode:
        raise SystemExit(result.returncode)
    reading = writer.slice_review(project, report, directory)
    if protected_hashes() != before:
        raise ValueError("A Sculpted project artifact changed during the Industrial slice")
    write_readiness(project, report, reading, directory)
    print(json.dumps(reading["fit"], indent=2), flush=True)


if __name__ == "__main__":
    main()
