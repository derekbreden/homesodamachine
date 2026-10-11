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
                 "support-045": .24, "support-060": .24,
                 "r6": .24, "cover": .24, "host": .24}
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


def assembly_id(row):
    value = row.get("print_assembly")
    return value.get("id") if isinstance(value, dict) else value


def print_units(rows, assemblies=None):
    """Keep each declared print assembly indivisible during plate placement."""
    assemblies = assemblies or {}
    grouped = {}
    for row in rows:
        identifier = assembly_id(row)
        key = ("assembly", identifier) if identifier else ("leaf", row["id"])
        grouped.setdefault(key, []).append(row)
    units = []
    for (kind, identifier), members in grouped.items():
        if kind == "leaf":
            units.append(dict(row=members[0], members=members, assembly=None))
            continue
        if identifier not in assemblies:
            raise ValueError(f"{identifier}: declared print assembly is absent from manifest.print_assemblies")
        assembly = assemblies[identifier]
        expected = [member["id"] for member in assembly["members"]]
        if set(expected) != {row["id"] for row in members}:
            raise ValueError(f"{identifier}: a plate must retain all declared assembly leaf bodies together")
        by_id = {row["id"]: row for row in members}
        members = [by_id[identifier] for identifier in expected]
        unit_row = dict(id=f"assembly:{identifier}", name=assembly.get("name", identifier),
                        stl=assembly["stl"], rotation_x_degrees=0.)
        units.append(dict(row=unit_row, members=members, assembly=assembly))
    return units


def member_transform(member):
    matrix = np.asarray(member.get("transform_mm", np.eye(4)), dtype=float).reshape(4, 4)
    if not np.all(np.isfinite(matrix)) or not np.allclose(matrix[3], [0, 0, 0, 1]):
        raise ValueError(f"{member['id']}: a print-assembly member requires a finite 4×4 rigid transform")
    if not np.allclose(matrix[:3, :3].T @ matrix[:3, :3], np.eye(3), atol=1e-8) or not np.isclose(np.linalg.det(matrix[:3, :3]), 1.):
        raise ValueError(f"{member['id']}: print-assembly member transforms must preserve physical dimensions")
    return matrix


def placement_source(unit):
    """A temporary envelope asks the existing writer for one common bed transform.

    The envelope's mesh is replaced by the exact named leaf volumes before the
    editable project is saved. It never remains printable project geometry.
    """
    if unit["assembly"] is None:
        return source_path(unit["row"])
    mesh = trimesh.load_mesh(source_path(unit["row"]), process=True)
    low, high = mesh.bounds
    envelope = trimesh.creation.box(extents=high-low)
    envelope.apply_translation((low+high)/2)
    folder = WORK / "assembly-placement"
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / (re.sub(r"[^a-zA-Z0-9_-]", "-", unit["assembly"]["id"]) + ".stl")
    envelope.export(path)
    return path


def embed_print_assemblies(members, config, report, units):
    """Replace each placement envelope with separately named normal-part volumes."""
    model = ET.fromstring(members["3D/3dmodel.model"])
    relationships = ET.fromstring(members["3D/_rels/3dmodel.model.rels"])
    next_id = 2*len(units)+1
    expanded, assembly_rows = [], []
    for index, (unit, placement) in enumerate(zip(units, report["parts"], strict=True), 1):
        if unit["assembly"] is None:
            expanded.append({**placement, "layer_range_object_index": index})
            continue
        assembly = unit["assembly"]
        owner = model.find(f".//{writer.qn('object')}[@id='{placement['object_id']}']")
        components = owner.find(writer.qn("components"))
        for component in list(components):
            components.remove(component)
        cfg = config.find(f"object[@id='{placement['object_id']}']")
        for part in list(cfg.findall("part")):
            cfg.remove(part)
        center = np.array(placement["source_center_mm"])
        matrix = np.array(placement["build_transform"][:9]).reshape(3, 3).T
        shift = np.array(placement["plate_translation_mm"])
        poses = {member["id"]: member_transform(member) for member in assembly["members"]}
        leaf_records = []
        for leaf_index, row in enumerate(unit["members"]):
            path = source_path(row)
            mesh = trimesh.load_mesh(path, process=True)
            pose = poses[row["id"]]
            body = mesh.copy()
            body.apply_transform(pose)
            vertices = body.vertices-center
            part_id = placement["part_id"] if leaf_index == 0 else str(next_id)
            member = placement["member"] if leaf_index == 0 else f"3D/Objects/assembly-leaf-{next_id}.model"
            if leaf_index:
                next_id += 1
                ET.SubElement(relationships, "{http://schemas.openxmlformats.org/package/2006/relationships}Relationship",
                              Target="/"+member, Id=f"assembly-leaf-{part_id}",
                              Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel")
            document = ET.Element(writer.qn("model"), unit="millimeter")
            resources = ET.SubElement(document, writer.qn("resources"))
            volume = ET.SubElement(resources, writer.qn("object"), id=part_id, type="model")
            geometry = ET.SubElement(volume, writer.qn("mesh"))
            points, triangles = ET.SubElement(geometry, writer.qn("vertices")), ET.SubElement(geometry, writer.qn("triangles"))
            for point in vertices:
                ET.SubElement(points, writer.qn("vertex"), **dict(zip("xyz", (f"{v:.9f}" for v in point))))
            for triangle in mesh.faces:
                ET.SubElement(triangles, writer.qn("triangle"), **dict(zip(("v1", "v2", "v3"), map(str, triangle))))
            members[member] = writer.xml(document)
            ET.SubElement(components, writer.qn("component"), objectid=part_id,
                          transform="1 0 0 0 1 0 0 0 1 0 0 0", **{
                              f"{{{writer.PROD}}}path": "/"+member,
                              f"{{{writer.PROD}}}UUID": writer.identifier(row["name"]+"/component")})
            normal = ET.SubElement(cfg, "part", id=part_id, subtype="normal_part",
                                   uuid=writer.identifier(row["name"]+"/normal-part"))
            for key, value in dict(name=row["name"], matrix="1 0 0 0 0 1 0 0 0 0 1 0 0 0 0 1",
                                   source_file=path.name, source_object_id=0, source_volume_id=0,
                                   source_offset_x=center[0], source_offset_y=center[1], source_offset_z=center[2]).items():
                writer.metadata(normal, key, value)
            ET.SubElement(normal, "mesh_stat", face_count=str(len(mesh.faces)), edges_fixed="0",
                          degenerate_facets="0", facets_removed="0", facets_reversed="0", backwards_edges="0")
            placed = vertices @ matrix.T + shift
            leaf = {**placement, "name": row["name"], "source": str(path.relative_to(ROOT)),
                    "stl_sha256": sha(path), "triangles": len(mesh.faces), "part_id": part_id,
                    "member": member, "print_assembly_id": assembly["id"],
                    "member_transform_mm": pose.tolist(), "source_leaf_bounds_mm": mesh.bounds.tolist(),
                    "assembly_body_bounds_mm": body.bounds.tolist(), "layer_range_object_index": index,
                    "plate_bounds_mm": [placed.min(axis=0).tolist(), placed.max(axis=0).tolist()],
                    "source_center_scope": "Common print-assembly center; attribution windows use shared manufacturing coordinates",
                    "embedded_vertex_error_mm": float(np.max(np.abs(np.round(vertices, 9)-vertices)))}
            expanded.append(leaf)
            leaf_records.append(dict(id=row["id"], part_id=part_id, source=leaf["source"],
                                     source_stl_sha256=leaf["stl_sha256"], member_transform_mm=pose.tolist()))
        for metadata in cfg.findall("metadata"):
            if "face_count" in metadata.attrib:
                metadata.set("face_count", str(sum(p["triangles"] for p in expanded
                                                   if p["object_id"] == placement["object_id"])))
        assembly_rows.append(dict(id=assembly["id"], object_id=placement["object_id"],
                                  identify_id=placement["identify_id"], members=leaf_records,
                                  source=assembly["stl"], source_stl_sha256=sha(source_path(unit["row"])),
                                  build_transform=placement["build_transform"],
                                  common_source_center_mm=placement["source_center_mm"],
                                  placement_scope="One shared object; separate named normal parts; one bed transform preserves member XYZ gaps"))
    members["3D/3dmodel.model"] = writer.xml(model)
    members["3D/_rels/3dmodel.model.rels"] = writer.xml(relationships).replace(b"ns0:", b"").replace(b"xmlns:ns0=", b"xmlns=")
    report["parts"] = expanded
    if assembly_rows:
        report["print_assemblies"] = assembly_rows


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
    recipe = row.get("print_recipe", {})
    if recipe:
        if "wall_generator" in recipe:
            if recipe["wall_generator"] not in {"classic", "arachne"}:
                raise ValueError(f"{row['id']}: unsupported source wall_generator")
            overrides["wall_generator"] = recipe["wall_generator"]
        if "layer_height_mm" in recipe or "bottom_and_body_layer_height_mm" in recipe:
            overrides["layer_height"] = f"{recipe_height(row, group):g}"
        if "supports_enabled" in recipe:
            overrides["enable_support"] = "1" if recipe["supports_enabled"] else "0"
        if recipe.get("supports"):
            if not str(recipe["supports"]).lower().startswith("tree (auto)"):
                raise ValueError(f"{row['id']}: print_recipe supports must retain Tree (auto)")
            overrides.update(enable_support="1", support_type="tree(auto)", support_style="default")
        if "elsewhere_wall_loops" in recipe:
            overrides["wall_loops"] = str(int(recipe["elsewhere_wall_loops"]))
        if "wall_infill_order" in recipe:
            if recipe["wall_infill_order"] != "inner wall/outer wall, then infill":
                raise ValueError(f"{row['id']}: source wall order must retain walls before infill")
            overrides.update(wall_sequence="inner wall/outer wall", is_infill_first="0")
        if "infill_wall_overlap" in recipe:
            overrides["infill_wall_overlap"] = str(recipe["infill_wall_overlap"])
        if "initial_layer_height_mm" in recipe and abs(float(recipe["initial_layer_height_mm"])-.20) > 1e-9:
            raise ValueError(f"{row['id']}: these shared plates retain the 0.20 mm first bed layer")
    if row["id"] == "G":
        overrides["enable_support"] = "0"
    if group == "seam":
        overrides.update(seam_recipe(row["id"]))
    return overrides


def recipe_height(row, group):
    recipe = row.get("print_recipe", {})
    height = float(recipe.get("bottom_and_body_layer_height_mm",
                              recipe.get("layer_height_mm", GROUP_HEIGHTS[group])))
    if not math.isfinite(height) or height <= 0:
        raise ValueError(f"{row['id']}: print_recipe needs a positive finite layer height")
    return height


def recipe_layer_ranges(row, group):
    """Merge height and wall bands into the production Bambu range format."""
    recipe = row.get("print_recipe", {})
    bands = []
    for span_key, value_key, option_key in (
            ("top_round_print_z_mm", "top_round_layer_height_mm", "layer_height"),
            ("local_wall_print_z_mm", "local_wall_loops", "wall_loops")):
        if span_key not in recipe and value_key not in recipe:
            continue
        if span_key not in recipe or value_key not in recipe:
            raise ValueError(f"{row['id']}: {span_key} and {value_key} must be supplied together")
        span = np.asarray(recipe[span_key], dtype=float)
        if span.shape != (2,) or not np.all(np.isfinite(span)) or span[0] < 0 or span[1] <= span[0]:
            raise ValueError(f"{row['id']}: invalid manufacturing Z band {span_key}")
        value = float(recipe[value_key])
        if not math.isfinite(value) or value <= 0 or (option_key == "wall_loops" and value != int(value)):
            raise ValueError(f"{row['id']}: invalid {value_key}")
        bands.append((span, option_key, f"{value:g}"))
    if not bands:
        return []
    if abs(float(row.get("rotation_x_degrees", 0))) > 1e-6:
        raise ValueError(f"{row['id']}: source-profile ranges require its manufacturing rotation baked into the STL")
    cuts = sorted({0., *(float(v) for span, _, _ in bands for v in span)})
    ranges = []
    for low, high in zip(cuts, cuts[1:]):
        options = dict(layer_height=f"{recipe_height(row, group):g}")
        for span, key, value in bands:
            if span[0] <= (low+high)/2 <= span[1]:
                options[key] = value
        ranges.append(dict(min_z_mm=low, max_z_mm=high, options=options))
    return ranges


def layer_ranges_member(specimens):
    """Range object IDs are the one-based loaded-object indices, as in production."""
    objects = ET.Element("objects")
    by_object = defaultdict(list)
    for index, specimen in enumerate(specimens, 1):
        ranges = specimen.get("requested_layer_ranges", [])
        if not ranges:
            continue
        by_object[specimen.get("layer_range_object_index", index)].extend(ranges)
    for index, ranges in sorted(by_object.items()):
        obj = ET.SubElement(objects, "object", id=str(index))
        cuts = sorted({r[k] for r in ranges for k in ("min_z_mm", "max_z_mm")})
        merged = []
        for low, high in zip(cuts, cuts[1:]):
            options = {}
            for row in ranges:
                if row["min_z_mm"] <= (low+high)/2 <= row["max_z_mm"]:
                    for key, value in row["options"].items():
                        if key in options and options[key] != value:
                            raise ValueError(f"Shared print object {index} has conflicting {key} Z ranges")
                        options[key] = value
            if options:
                merged.append(dict(min_z_mm=low, max_z_mm=high, options=options))
        for row in merged:
            band = ET.SubElement(obj, "range", min_z=f"{row['min_z_mm']:.6f}",
                                 max_z=f"{row['max_z_mm']:.6f}")
            for key, value in row["options"].items():
                ET.SubElement(band, "option", opt_key=key).text = value
    return writer.xml(objects)


def make_project(group, rows, baseline, project_group=None, assemblies=None):
    PROJECTS.mkdir(parents=True, exist_ok=True)
    project_group = project_group or group
    project = PROJECTS / f"the-pour-{project_group}-petgf-left04-z004-mark2.3mf"
    previous = json.loads(project.with_suffix(".print.json").read_text()) if project.with_suffix(".print.json").is_file() else None
    units = print_units(rows, assemblies)
    layout_rows = [unit["row"] for unit in units]
    rows = [row for unit in units for row in unit["members"]]
    border = 80.
    try:
        offsets = plate_layout(layout_rows, baseline, border=border)
    except ValueError:
        border = 40.
        offsets = plate_layout(layout_rows, baseline, border=border)
    report = writer.refresh(PROFILE, project,
                            parts=tuple((unit["row"]["name"], placement_source(unit),
                                         float(unit["row"].get("rotation_x_degrees", 0))) for unit in units),
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
    if any(unit["assembly"] for unit in units):
        embed_print_assemblies(members, config, report, units)
    else:
        for index, part in enumerate(report["parts"], 1):
            part["layer_range_object_index"] = index
    specimens = []
    shared_overrides = defaultdict(dict)
    for row, part in zip(rows, report["parts"], strict=True):
        overrides = object_recipe(row, group)
        cfg = config.find(f"object[@id='{part['object_id']}']")
        for key, value in overrides.items():
            held = shared_overrides[part["object_id"]]
            if key in held and held[key] != value:
                raise ValueError(f"{row['id']}: shared print-assembly object has conflicting {key} settings")
            held[key] = value
        replace_metadata(cfg, overrides)
        specimen = dict(id=row["id"], name=row["name"], kind=row["kind"],
                        source=part["source"], source_stl_sha256=part["stl_sha256"],
                        identify_id=part["identify_id"], object_id=part["object_id"],
                        rotation_x_degrees=part["rotation_x_degrees"],
                        requested_layer_height_mm=recipe_height(row, group), object_overrides=overrides,
                        effective_supports_enabled=str(overrides.get("enable_support", settings.get("enable_support", "0"))) == "1",
                        plate_bounds_mm=part["plate_bounds_mm"],
                        layer_range_object_index=part["layer_range_object_index"],
                        plate_offset_mm=list(offsets[part["layer_range_object_index"]-1]))
        if part.get("print_assembly_id"):
            specimen["print_assembly_id"] = part["print_assembly_id"]
        if row.get("print_recipe"):
            specimen["requested_print_recipe"] = row["print_recipe"]
        ranges = recipe_layer_ranges(row, group)
        if ranges:
            if max(r["max_z_mm"] for r in ranges) > float(print_size(row)[2])+.01:
                raise ValueError(f"{row['id']}: a source-profile Z band exceeds the printed body")
            specimen["requested_layer_ranges"] = ranges
        if group == "seam":
            method, gap = SEAMS[row["id"]]
            specimen.update(seam_method=method, gap_percent_of_nozzle=gap,
                            gap_mm=.4 * gap / 100,
                            controlling_gap_key="seam_gap" if method == "regular" else "seam_slope_gap")
        if group in SUPPORT_GAPS:
            specimen["requested_support_top_gap_mm"] = SUPPORT_GAPS[group]
        for key in ("support_ceiling_z_mm", "ceiling_xy_bounds_mm", "label_windows",
                    "recessed_label_windows",
                    "native_body_window", "native_release_probes", "native_gap_probes",
                    "travel_x_mm", "top_release_gap_mm", "lower_release_gap_mm",
                    "y_running_air_per_side_mm", "first_layer_chamfer_mm"):
            if key in row:
                specimen[key] = row[key]
        specimens.append(specimen)
    members["Metadata/model_settings.config"] = writer.xml(config)
    if any(s.get("requested_layer_ranges") for s in specimens):
        members["Metadata/layer_config_ranges.xml"] = layer_ranges_member(specimens)
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
                  support_policy="Saved Tree(auto)/Default for support-enabled objects, including automatic normal sections. Explicit source or separate captive-group recipes can disable support locally.",
                  support_top_z_distance_mm=float(settings["support_top_z_distance"]),
                  support_bottom_z_distance_mm=float(settings["support_bottom_z_distance"]),
                  preparation_only=True, submitted=False,
                  physical_result="Unprinted; finish, removal effort and tactile fit are unmeasured.",
                  transfer_limit="Coupon size changes cooling, perimeter length and layer return time. Physical references do not qualify complete product parts.")
    if previous and previous.get("project_sha256") == report["project_sha256"] and previous.get("native"):
        archive = ROOT / previous["native"]["archive"]
        if archive.is_file() and sha(archive) == previous["native"]["archive_sha256"]:
            report["native"] = native_summary(project, report, archive, archive.parent)
            report["native"]["reused_identical_input_project"] = True
            print(f"Reusing native slice {project_group}: identical input project and recorded archive", flush=True)
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
    if any(s.get("label_windows") for s in report["specimens"]):
        result["lettering_reading"] = native_lettering_reading(text, report, directory)
    if any(s.get("recessed_label_windows") for s in report["specimens"]):
        result["recessed_identity_reading"] = native_recessed_lettering_reading(text, report, directory)
    if any(s.get("requested_print_recipe") for s in report["specimens"]):
        result["source_profile_reading"] = native_source_profile_reading(text, report)
    if any(s.get("native_release_probes") or s.get("native_gap_probes") for s in report["specimens"]):
        result["captive_release_reading"] = native_release_reading(text, report, result["object_model_deposition"])
    return result


def native_deposits(text):
    """Yield positive native XY deposits, preserving model Z and strand flow.

    Model Z comes from the native layer comment; explicit Z ramps are retained
    separately. Arc moves are subdivided by the existing native-path reader.
    """
    from enclosure_support_audit import _WORD, _arc_points

    x = y = e = 0.
    current = None
    layer_z = height = width = feed = None
    feature = ""
    absolute_xy, relative_e = True, True
    for raw in text.splitlines():
        line = raw.strip()
        label = re.match(r"; (?:start printing object, unique label id:|OBJECT_ID:)\s*(\d+)", line)
        if label:
            current = int(label.group(1))
        elif line.startswith("; stop printing object"):
            current = None
        elif line.startswith("; Z_HEIGHT:"):
            layer_z = float(line.split(":", 1)[1])
        elif line.startswith(("; LAYER_HEIGHT:", "; HEIGHT:")):
            height = float(line.split(":", 1)[1])
        elif line.startswith(("; LINE_WIDTH:", "; WIDTH:")):
            width = float(line.split(":", 1)[1])
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
            nx = words.get("X", x) if absolute_xy else x+words.get("X", 0.)
            ny = words.get("Y", y) if absolute_xy else y+words.get("Y", 0.)
            de = words.get("E", 0.) if relative_e else words.get("E", e)-e
            feed = words.get("F", feed)
            if layer_z is not None and de > 1e-9 and (nx != x or ny != y):
                points = ([(x, y), (nx, ny)] if command in {"G0", "G1"}
                          else _arc_points((x, y), (nx, ny), words, command == "G2"))
                yield dict(identify_id=current, model_z_mm=layer_z, strand_height_mm=height,
                           strand_width_mm=width, feature=feature,
                           feed_mm_s=feed/60 if feed is not None else None,
                           explicit_z_move="Z" in words, points=np.array(points))
            x, y = nx, ny
            if "E" in words:
                e = e+words["E"] if relative_e else words["E"]


def is_model_deposit(deposit):
    return not deposit["feature"].startswith(("Support", "Skirt", "Brim", "Custom", "Prime"))


def native_bounds(value, identifier):
    bounds = np.asarray(value.get("bounds_mm") if isinstance(value, dict) else value, dtype=float)
    if bounds.shape != (2, 3) or not np.all(np.isfinite(bounds)) or np.any(bounds[1] <= bounds[0]):
        raise ValueError(f"{identifier}: native attribution requires finite increasing 2×3 XYZ bounds")
    return bounds


def intersects_native_window(deposit, bounds):
    if not bounds[0, 2]-1e-6 <= deposit["model_z_mm"] <= bounds[1, 2]+1e-6:
        return False
    return any(clipped_segment(a, b, bounds[0, :2], bounds[1, :2]) is not None
               for a, b in zip(deposit["points"], deposit["points"][1:]))


def native_targets(report):
    """Leaf identities remain distinct even when their native object label is shared."""
    targets, by_object = {}, defaultdict(list)
    for specimen, part in zip(report["specimens"], report["parts"], strict=True):
        shift = np.array(part["plate_translation_mm"])-np.array(part["source_center_mm"])
        window = specimen.get("native_body_window")
        if window is not None and abs(float(part["rotation_x_degrees"])) > 1e-6:
            raise ValueError(f"{specimen['id']}: native attribution windows require a bed-normalized manufacturing frame")
        if specimen.get("print_assembly_id") and window is None:
            raise ValueError(f"{specimen['id']}: shared native object needs a unique native_body_window")
        bounds = native_bounds(window, specimen["id"])+shift if window is not None else None
        target = dict(specimen=specimen, part=part, shift=shift, bounds=bounds)
        targets[specimen["id"]] = target
        by_object[specimen["identify_id"]].append(target)
    return targets, by_object


def model_deposition_facts(text, report):
    """Retain leaf deposit witnesses and the correct shared nominal Z schedule."""
    targets, by_object = native_targets(report)
    facts = {identifier: dict(layers=set(), heights=set(), outer_wall_moves=0, outer_wall_z_moves=0)
             for identifier in targets}
    object_zs = defaultdict(set)
    for deposit in native_deposits(text):
        if not is_model_deposit(deposit):
            continue
        label, z = deposit["identify_id"], deposit["model_z_mm"]
        if label not in by_object:
            continue
        object_zs[label].add(z)
        for target in by_object[label]:
            if target["bounds"] is not None and not intersects_native_window(deposit, target["bounds"]):
                continue
            fact = facts[target["specimen"]["id"]]
            fact["layers"].add(z)
            if deposit["strand_height_mm"] is not None:
                fact["heights"].add(deposit["strand_height_mm"])
            if deposit["feature"] in ("Outer wall", "Overhang wall"):
                fact["outer_wall_moves"] += 1
                fact["outer_wall_z_moves"] += int(deposit["explicit_z_move"])
    readings = []
    for identifier, target in targets.items():
        specimen, fact = target["specimen"], facts[identifier]
        zs = sorted(fact["layers"])
        schedule = sorted(object_zs[specimen["identify_id"]])
        reading = dict(id=identifier, identify_id=specimen["identify_id"],
                       model_layer_count=len(zs), model_layer_nozzle_z_mm=zs,
                       first_attributed_model_nozzle_z_mm=zs[0] if zs else None,
                       model_layer_steps_mm=sorted({round(b-a, 4) for a, b in zip(schedule, schedule[1:])}),
                       model_layer_schedule_scope=("Common print-assembly object schedule; leaf deposition is clipped to its unique supplied window."
                           if specimen.get("print_assembly_id") else "Complete native object model deposition."),
                       model_deposition_heights_mm=sorted({round(h, 4) for h in fact["heights"]}),
                       deposition_height_scope="Strand heights include native bridge thickness; shared object Z steps describe the nominal layer schedule.",
                       outer_wall_depositing_moves=fact["outer_wall_moves"],
                       outer_wall_depositing_moves_with_z=fact["outer_wall_z_moves"],
                       z_witness_scope="Explicit Z on depositing outer-wall moves witnesses native height ramps; it does not measure seam flatness.")
        if specimen.get("print_assembly_id"):
            reading.update(print_assembly_id=specimen["print_assembly_id"],
                           sampled_body_window=specimen["native_body_window"])
        readings.append(reading)
    return readings


def probe_crossing(a, b, start, end):
    """Position of a transverse wall centerline crossing on a finite probe."""
    direction, probe = b-a, end-start
    def cross(u, v):
        return float(u[0]*v[1]-u[1]*v[0])
    denominator = cross(direction, probe)
    if abs(denominator) < 1e-10:
        return None
    t, u = cross(start-a, probe)/denominator, cross(start-a, direction)/denominator
    if -1e-7 <= t <= 1+1e-7 and -1e-7 <= u <= 1+1e-7:
        return float(u*np.linalg.norm(probe))
    return None


def native_source_profile_reading(text, report):
    """Read model Z schedules, feature order and local wall lanes from native moves.

    A wall probe is a transverse manufacturing-frame XY line through one simple
    wall land. Its crossings count emitted road centerlines, independent of the
    saved wall_loops option; coincident endpoints are counted only once. The
    source's physical bead shape and overhang surface remain unmeasured.
    """
    from enclosure_support_audit import _WORD, _arc_points

    targets = {}
    for specimen, part in zip(report["specimens"], report["parts"], strict=True):
        recipe = specimen.get("requested_print_recipe")
        if not recipe:
            continue
        if abs(float(part["rotation_x_degrees"])) > 1e-6:
            raise ValueError(f"{specimen['id']}: native source-profile probes require a bed-normalized STL")
        shift = np.array(part["plate_translation_mm"])-np.array(part["source_center_mm"])
        probes = []
        for probe in recipe.get("wall_probes", []):
            line = np.array(probe["line_xy_mm"], dtype=float)
            span = np.array(probe.get("print_z_mm", recipe.get("local_wall_print_z_mm")), dtype=float)
            if line.shape != (2, 2) or not np.all(np.isfinite(line)) or np.linalg.norm(line[1]-line[0]) < 1e-6:
                raise ValueError(f"{specimen['id']}: invalid wall probe line")
            if span.shape != (2,) or not np.all(np.isfinite(span)) or span[1] <= span[0]:
                raise ValueError(f"{specimen['id']}: wall probes need a finite increasing print_z_mm span")
            probes.append(dict(id=specimen["id"], name=probe.get("name", "source wall land"),
                               source_line=line, plate_line=line+shift[:2],
                               span=span, layers=defaultdict(list),
                               expected=probe.get("expected_wall_roads", recipe.get("local_wall_loops"))))
        target = targets.setdefault(specimen["identify_id"], dict(specimens=[], shift=shift,
                                                                  probes=[], layers={}, support_segments=0))
        if not np.allclose(target["shift"], shift):
            raise ValueError(f"{specimen['id']}: shared native object has inconsistent manufacturing-frame shifts")
        target["specimens"].append(specimen)
        target["probes"].extend(probes)
    for target in targets.values():
        label = target["specimens"][0]["identify_id"]
        target["specimens"] = [s for s in report["specimens"] if s["identify_id"] == label]
    x = y = e = 0.
    current = None
    layer_z = strand_height = strand_width = feed = None
    feature = ""
    absolute_xy, relative_e = True, True
    walls = {"Inner wall", "Outer wall", "Overhang wall"}
    infill = {"Sparse infill", "Internal solid infill", "Bottom surface", "Top surface", "Bridge"}
    for raw in text.splitlines():
        line = raw.strip()
        label = re.match(r"; (?:start printing object, unique label id:|OBJECT_ID:)\s*(\d+)", line)
        if label:
            current = int(label.group(1))
        elif line.startswith("; stop printing object"):
            current = None
        elif line.startswith("; Z_HEIGHT:"):
            layer_z = float(line.split(":", 1)[1])
        elif line.startswith(("; LAYER_HEIGHT:", "; HEIGHT:")):
            strand_height = float(line.split(":", 1)[1])
        elif line.startswith(("; LINE_WIDTH:", "; WIDTH:")):
            strand_width = float(line.split(":", 1)[1])
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
            nx = words.get("X", x) if absolute_xy else x+words.get("X", 0.)
            ny = words.get("Y", y) if absolute_xy else y+words.get("Y", 0.)
            de = words.get("E", 0.) if relative_e else words.get("E", e)-e
            feed = words.get("F", feed)
            target = targets.get(current)
            if target and layer_z is not None and de > 1e-9 and (nx != x or ny != y):
                if feature.startswith("Support"):
                    target["support_segments"] += 1
                elif not feature.startswith(("Skirt", "Brim", "Custom", "Prime")):
                    z = round(layer_z-target["shift"][2], 5)
                    layer = target["layers"].setdefault(z, dict(features=[], heights=set(), feeds=defaultdict(set)))
                    if not layer["features"] or layer["features"][-1] != feature:
                        layer["features"].append(feature)
                    if strand_height is not None:
                        layer["heights"].add(round(strand_height, 5))
                    if feed is not None:
                        layer["feeds"][feature].add(round(feed/60, 3))
                    if feature in walls:
                        points = ([(x, y), (nx, ny)] if command in {"G0", "G1"}
                                  else _arc_points((x, y), (nx, ny), words, command == "G2"))
                        points = [np.array(p) for p in points]
                        for probe in target["probes"]:
                            if not probe["span"][0]-1e-6 <= z <= probe["span"][1]+1e-6:
                                continue
                            for a, b in zip(points, points[1:]):
                                position = probe_crossing(a, b, *probe["plate_line"])
                                if position is not None:
                                    probe["layers"][z].append(dict(distance_on_probe_mm=round(position, 5),
                                                                   feature=feature, commanded_width_mm=strand_width))
            x, y = nx, ny
            if "E" in words:
                e = e+words["E"] if relative_e else words["E"]
    readings = []
    for target in targets.values():
        specimen = target["specimens"][0]
        zs = sorted(target["layers"])
        previous_z = 0.
        layer_rows = []
        for z in zs:
            layer = target["layers"][z]
            sequence = layer["features"]
            wall_positions = [i for i, name in enumerate(sequence) if name in walls]
            infill_positions = [i for i, name in enumerate(sequence) if name in infill]
            layer_rows.append(dict(model_nozzle_z_mm=z, nominal_model_z_step_mm=round(z-previous_z, 5),
                                   commanded_strand_heights_mm=sorted(layer["heights"]),
                                   depositing_feature_sequence=sequence,
                                   first_wall_precedes_first_infill=(min(wall_positions) < min(infill_positions)
                                       if wall_positions and infill_positions else None),
                                   commanded_wall_feed_rates_mm_s=sorted({v for name in walls for v in layer["feeds"].get(name, [])})))
            previous_z = z
        probe_rows = []
        for probe in target["probes"]:
            layers = []
            expected = int(probe["expected"]) if probe["expected"] is not None else None
            for z, hits in sorted(probe["layers"].items()):
                unique = []
                for hit in sorted(hits, key=lambda h: h["distance_on_probe_mm"]):
                    if not unique or abs(hit["distance_on_probe_mm"]-unique[-1]["distance_on_probe_mm"]) > 1e-4:
                        unique.append(hit)
                layers.append(dict(model_nozzle_z_mm=z, wall_lane_count=len(unique), crossings=unique,
                                   matches_requested_wall_roads=(len(unique) == expected if expected is not None else None)))
            outer_roads = []
            for layer in layers[:2]:
                outer = [hit for hit in layer["crossings"] if hit["feature"] in {"Outer wall", "Overhang wall"}]
                if outer:
                    outer_roads.append(dict(model_nozzle_z_mm=layer["model_nozzle_z_mm"],
                                             **min(outer, key=lambda hit: hit["distance_on_probe_mm"])))
            overlap = None
            if len(outer_roads) == 2 and all(hit["commanded_width_mm"] is not None for hit in outer_roads):
                overlap = (sum(hit["commanded_width_mm"] for hit in outer_roads)/2
                           -abs(outer_roads[1]["distance_on_probe_mm"]-outer_roads[0]["distance_on_probe_mm"]))
            probe_rows.append(dict(id=probe["id"], name=probe["name"], line_xy_mm=probe["source_line"].tolist(),
                                   print_z_mm=probe["span"].tolist(), requested_wall_roads=expected,
                                   sampled_model_layer_count=len(layers),
                                   emitted_wall_lane_counts=sorted({r["wall_lane_count"] for r in layers}),
                                   first_two_sampled_outer_wall_roads=outer_roads,
                                   first_two_sampled_outer_wall_nominal_footprint_overlap_mm=round(overlap, 5) if overlap is not None else None,
                                   footprint_overlap_scope="Two commanded line-width footprints on this transverse land; physical bead shape, contact area and bonding are unmeasured.",
                                   layers=layers))
        shared = specimen.get("print_assembly_id")
        reading = dict(id=shared or specimen["id"], identify_id=specimen["identify_id"],
                       emitted_model_layers=layer_rows,
                       emitted_object_support_segment_count=target["support_segments"],
                       wall_probes=probe_rows,
                       local_wall_count_scope=("Emitted wall-road crossings on supplied simple lands; corners, narrow stock and other islands can have different wall counts."
                           if probe_rows else "No wall probe supplied; emitted local wall count has not been measured."))
        if shared:
            reading.update(print_assembly_id=shared,
                           member_ids=[s["id"] for s in target["specimens"]],
                           requested_member_recipes=[dict(id=s["id"], print_recipe=s.get("requested_print_recipe", {}),
                                                         layer_ranges=s.get("requested_layer_ranges", []))
                                                     for s in target["specimens"]],
                           attribution_scope="Complete shared print-object schedule, reported once under the assembly ID; no individual leaf schedule is inferred from this object label.")
        else:
            reading.update(requested_print_recipe=specimen["requested_print_recipe"],
                           requested_layer_ranges=specimen.get("requested_layer_ranges", []),
                           attribution_scope="Complete standalone source specimen native object.")
        readings.append(reading)
    return dict(scope="Native positive extrusion moves attributed to standalone source objects or shared assembly objects. Model nozzle-Z steps, strand-flow heights, wall-lane counts, commanded wall feeds and feature order are observed separately from requested 3MF options. Per-layer feature sequences can contain multiple islands; first-wall order does not qualify every island. Physical bead shape, infill overlap, surface and strength are unmeasured.",
                specimens=readings)


def clipped_segment(a, b, low, high):
    """Clip a centerline to a supplied Cartesian marking window."""
    delta = b-a
    begin, end = 0., 1.
    for position, change, minimum, maximum in zip(a, delta, low, high):
        if abs(change) < 1e-10:
            if position < minimum or position > maximum:
                return None
            continue
        enter, leave = sorted(((minimum-position)/change, (maximum-position)/change))
        begin, end = max(begin, enter), min(end, leave)
        if begin > end:
            return None
    return a+begin*delta, a+end*delta


def native_release_reading(text, report, body_deposition=None):
    """Observe captive contacts in their preserved common manufacturing frame."""
    targets, by_object = native_targets(report)
    contacts, lateral = [], []
    for specimen in report["specimens"]:
        target = targets[specimen["id"]]
        for probe in specimen.get("native_release_probes", []):
            fixed, moving = targets[probe["fixed_body_id"]], targets[probe["moving_body_id"]]
            if not np.allclose(fixed["shift"], moving["shift"]):
                raise ValueError(f"{specimen['id']}: captive release contacts require one common manufacturing frame")
            sides = {}
            for side, body, default in (("fixed", fixed, "top"), ("moving", moving, "bottom")):
                kind = probe.get(f"{side}_surface", default)
                if kind not in {"top", "bottom"}:
                    raise ValueError(f"{specimen['id']}: captive contact surface must be top or bottom")
                sides[side] = dict(target=body, kind=kind,
                                   bounds=native_bounds(probe[f"{side}_contact_bounds_mm"], specimen["id"])+body["shift"],
                                   layers=defaultdict(list))
            if {side["kind"] for side in sides.values()} != {"top", "bottom"}:
                raise ValueError(f"{specimen['id']}: a vertical air probe requires one top and one bottom contact")
            gap_bounds = native_bounds(probe["support_gap_bounds_mm"], specimen["id"])+target["shift"]
            # Given planes delimit the air; depositing exactly on either
            # contact plane belongs to the contact rather than its interior.
            gap_bounds[0, 2] += 1e-5
            gap_bounds[1, 2] -= 1e-5
            contacts.append(dict(id=specimen["id"], probe=probe, sides=sides,
                                 support_bounds=gap_bounds, support_layers=set(), support_segments=0,
                                 model_in_gap_layers=set()))
        for probe in specimen.get("native_gap_probes", []):
            fixed, moving = targets[probe["fixed_body_id"]], targets[probe["moving_body_id"]]
            if not np.allclose(fixed["shift"], moving["shift"]):
                raise ValueError(f"{specimen['id']}: lateral captive probes require a common manufacturing frame")
            line = np.asarray(probe["line_xy_mm"], dtype=float)
            span = np.asarray(probe["print_z_mm"], dtype=float)
            intervals = {side: np.asarray(probe[f"{side}_interval_mm"], dtype=float) for side in ("fixed", "moving")}
            if line.shape != (2, 2) or not np.all(np.isfinite(line)) or np.linalg.norm(line[1]-line[0]) < 1e-6:
                raise ValueError(f"{specimen['id']}: invalid lateral probe line")
            if span.shape != (2,) or not np.all(np.isfinite(span)) or span[1] <= span[0]:
                raise ValueError(f"{specimen['id']}: lateral probes need an increasing print_z_mm span")
            if any(v.shape != (2,) or not np.all(np.isfinite(v)) or v[1] <= v[0] for v in intervals.values()):
                raise ValueError(f"{specimen['id']}: lateral probe wall intervals must increase")
            if not (intervals["fixed"][1] < intervals["moving"][0] or intervals["moving"][1] < intervals["fixed"][0]):
                raise ValueError(f"{specimen['id']}: lateral wall intervals must be disjoint")
            lateral.append(dict(id=specimen["id"], probe=probe, fixed=fixed, moving=moving,
                                line=line+fixed["shift"][:2], span=span+fixed["shift"][2],
                                intervals=intervals, layers=defaultdict(lambda: defaultdict(list))))
    schedules = defaultdict(set)
    for deposit in native_deposits(text):
        label, z = deposit["identify_id"], deposit["model_z_mm"]
        model = is_model_deposit(deposit)
        if model and label in by_object:
            schedules[label].add(z)
        for contact in contacts:
            for side in contact["sides"].values():
                if model and label == side["target"]["specimen"]["identify_id"] and intersects_native_window(deposit, side["bounds"]):
                    side["layers"][z].append((deposit["strand_height_mm"], deposit["feature"]))
            if intersects_native_window(deposit, contact["support_bounds"]):
                if deposit["feature"].startswith("Support"):
                    contact["support_layers"].add(z)
                    contact["support_segments"] += 1
                elif model:
                    contact["model_in_gap_layers"].add(z)
        if not model or deposit["feature"] not in {"Inner wall", "Outer wall", "Overhang wall"}:
            continue
        for probe in lateral:
            if not probe["span"][0]-1e-6 <= z <= probe["span"][1]+1e-6:
                continue
            for side in ("fixed", "moving"):
                if label != probe[side]["specimen"]["identify_id"]:
                    continue
                interval = probe["intervals"][side]
                for a, b in zip(deposit["points"], deposit["points"][1:]):
                    position = probe_crossing(a, b, *probe["line"])
                    if position is not None and interval[0]-1e-6 <= position <= interval[1]+1e-6:
                        probe["layers"][z][side].append(dict(distance_on_probe_mm=round(position, 5),
                                                              commanded_width_mm=deposit["strand_width_mm"],
                                                              feature=deposit["feature"]))
    schedule_steps = {}
    for label, zs in schedules.items():
        previous = 0.
        for z in sorted(zs):
            schedule_steps[label, z] = z-previous
            previous = z
    vertical_rows = []
    for contact in contacts:
        sides = {}
        for name, side in contact["sides"].items():
            body = side["target"]
            zs = sorted(side["layers"])
            selected = ((max(zs) if side["kind"] == "top" else min(zs)) if zs else None)
            step = schedule_steps.get((body["specimen"]["identify_id"], selected))
            surface = selected if side["kind"] == "top" else (selected-step if selected is not None and step is not None else None)
            selected_strands = side["layers"].get(selected, [])
            sides[name] = dict(body_id=body["specimen"]["id"], surface=side["kind"],
                               sampled_contact_bounds_mm=contact["probe"][f"{name}_contact_bounds_mm"],
                               contact_model_nozzle_z_mm=round(selected, 5) if selected is not None else None,
                               nominal_model_z_step_mm=round(step, 5) if step is not None else None,
                               nominal_contact_surface_z_mm=round(surface, 5) if surface is not None else None,
                               contact_strand_flow_heights_mm=sorted({h for h, _ in selected_strands if h is not None}),
                               contact_features=sorted({f for _, f in selected_strands}),
                               sampled_model_nozzle_z_mm=zs)
        top = next(side for side in sides.values() if side["surface"] == "top")
        bottom = next(side for side in sides.values() if side["surface"] == "bottom")
        air = (bottom["nominal_contact_surface_z_mm"]-top["nominal_contact_surface_z_mm"]
               if bottom["nominal_contact_surface_z_mm"] is not None and top["nominal_contact_surface_z_mm"] is not None else None)
        vertical_rows.append(dict(id=contact["id"], name=contact["probe"].get("name", "captive contact"),
                                  requested_geometry_gap_mm=contact["probe"].get("requested_gap_mm"),
                                  fixed=sides["fixed"], moving=sides["moving"],
                                  commanded_nominal_air_mm=round(air, 5) if air is not None else None,
                                  support_gap_bounds_mm=contact["probe"]["support_gap_bounds_mm"],
                                  emitted_support_segment_count_in_gap=contact["support_segments"],
                                  emitted_support_nozzle_z_mm_in_gap=sorted(contact["support_layers"]),
                                  emitted_model_nozzle_z_mm_in_gap=sorted(contact["model_in_gap_layers"])))
    lateral_rows = []
    for probe in lateral:
        layers = []
        fixed_is_lower = probe["intervals"]["fixed"][1] < probe["intervals"]["moving"][0]
        for z, hits in sorted(probe["layers"].items()):
            selected = {}
            for side in ("fixed", "moving"):
                if hits[side]:
                    choose = max if (side == "fixed") == fixed_is_lower else min
                    selected[side] = choose(hits[side], key=lambda h: h["distance_on_probe_mm"])
            if len(selected) == 2:
                center_air = abs(selected["fixed"]["distance_on_probe_mm"]-selected["moving"]["distance_on_probe_mm"])
                widths = [selected[side]["commanded_width_mm"] for side in ("fixed", "moving")]
                footprint = center_air-sum(widths)/2 if all(v is not None for v in widths) else None
                layers.append(dict(model_nozzle_z_mm=round(z-probe["fixed"]["shift"][2], 5),
                                   fixed_wall=selected["fixed"], moving_wall=selected["moving"],
                                   centerline_separation_mm=round(center_air, 5),
                                   commanded_width_footprint_air_mm=round(footprint, 5) if footprint is not None else None))
        lateral_rows.append(dict(id=probe["id"], name=probe["probe"].get("name", "lateral motion gap"),
                                 requested_per_face_geometry_gap_mm=probe["probe"].get("requested_gap_mm"),
                                 line_xy_mm=probe["probe"]["line_xy_mm"], print_z_mm=probe["probe"]["print_z_mm"],
                                 sampled_model_layer_count=len(layers),
                                 emitted_commanded_width_footprint_air_mm=sorted({row["commanded_width_footprint_air_mm"]
                                      for row in layers if row["commanded_width_footprint_air_mm"] is not None}),
                                 layers=layers))
    body_deposition = body_deposition if body_deposition is not None else model_deposition_facts(text, report)
    first_z = {row["id"]: row["first_attributed_model_nozzle_z_mm"] for row in body_deposition}
    bodies = [dict(id=s["id"], print_assembly_id=s.get("print_assembly_id"),
                   first_attributed_model_nozzle_z_mm=first_z.get(s["id"]),
                   geometric_travel_x_mm=s.get("travel_x_mm"),
                   y_running_air_per_face_geometry_mm=s.get("y_running_air_per_side_mm"),
                   first_layer_chamfer_geometry_mm=s.get("first_layer_chamfer_mm"))
              for s in report["specimens"] if s.get("native_release_probes")]
    return dict(scope="Native model-to-model contacts in the preserved print-assembly frame. Nominal bottom surfaces are first model nozzle Z minus the actual shared object model Z step; top surfaces are last model nozzle Z. Bridge strand-flow height is reported separately. Gap-window deposits exclude the exact contact planes. Lateral air subtracts half of each commanded line width from measured centerline separation. Travel is the supplied geometric stroke, not observed physical motion. These commanded slabs and strand-width footprints do not measure bead shape, sag, physical clearance, release force or reliable motion.",
                moving_bodies=bodies,
                vertical_contacts=vertical_rows, lateral_contacts=lateral_rows)


def native_recessed_lettering_reading(text, report, directory):
    """Compare first bed-layer footprints with the CAD's actual recessed voids."""
    from shapely.geometry import Polygon, LineString, box as rectangle
    from shapely.geometry.polygon import orient
    from shapely.ops import polygonize, unary_union
    from matplotlib import pyplot as plt
    from matplotlib.path import Path as PlotPath
    from matplotlib.patches import PathPatch

    windows, by_object = [], defaultdict(list)
    for specimen, part in zip(report["specimens"], report["parts"], strict=True):
        shift = np.array(part["plate_translation_mm"])-np.array(part["source_center_mm"])
        for label in specimen.get("recessed_label_windows", []):
            if label.get("view_axis") != "-z" or abs(float(part["rotation_x_degrees"])) > 1e-6:
                raise ValueError(f"{specimen['id']}: recessed identity review requires a bed-normalized underside -Z marking")
            bounds = native_bounds(label, specimen["id"])
            window = dict(id=specimen["id"], specimen=specimen, part=part, label=label,
                          shift=shift, bounds=bounds, layers=defaultdict(list))
            windows.append(window)
            by_object[specimen["identify_id"]].append(window)
    for deposit in native_deposits(text):
        if not is_model_deposit(deposit) or deposit["strand_width_mm"] is None:
            continue
        for window in by_object.get(deposit["identify_id"], []):
            label, shift = window["label"], window["shift"]
            z = round(deposit["model_z_mm"]-shift[2], 5)
            if not float(label["surface_z_mm"])+1e-6 < z < float(label["surface_z_mm"])+float(label["nominal_recess_mm"])-1e-6:
                continue
            low, high = window["bounds"][:, :2]
            points = deposit["points"]-shift[:2]
            for a, b in zip(points, points[1:]):
                clipped = clipped_segment(a, b, low-.75, high+.75)
                if clipped is not None and np.linalg.norm(clipped[1]-clipped[0]) > 1e-8:
                    window["layers"][z].append((clipped, deposit["strand_width_mm"]))
    # Every current underside channel is straight through the first two model
    # layers. Section below the first nozzle plane avoids boundary ambiguity.
    meshes, materials = {}, {}
    readings, visual = [], []
    for window in windows:
        part, label, bounds = window["part"], window["label"], window["bounds"]
        source = ROOT / part["source"]
        mesh = meshes.setdefault(source, None)
        if mesh is None:
            mesh = meshes[source] = trimesh.load_mesh(source, process=True)
        surface = float(label["surface_z_mm"])
        sample_z = surface+min(float(label["nominal_recess_mm"])/2, float(report["first_layer_height_mm"])/2)
        key = (source, sample_z)
        if key not in materials:
            segments = trimesh.intersections.mesh_plane(mesh, plane_origin=[0, 0, sample_z],
                                                       plane_normal=[0, 0, 1])
            if not len(segments):
                raise ValueError(f"{window['id']}: no CAD bed section at recessed marking")
            # Work directly from mesh-plane segments: trimesh's contour graph
            # needs the optional networkx package. Quantization rejoins the
            # floating endpoints of adjacent triangles, far below STL precision.
            contours = polygonize(unary_union([LineString(np.round(points[:, :2], 7))
                                               for points in segments]))
            rings_by_key = {}
            for contour in contours:
                for ring in (contour.exterior, *contour.interiors):
                    polygon = Polygon(ring).normalize()
                    rings_by_key[polygon.wkb] = polygon
            material = Polygon()
            rings = sorted(rings_by_key.values(), key=lambda shape: shape.area, reverse=True)
            for ring in rings:
                material = material.symmetric_difference(ring)
            materials[key] = material
        low, high = bounds[:, :2]
        view = rectangle(*low, *high)
        channel = view.difference(materials[key])
        layer_rows = []
        first_footprint = None
        for z, roads in sorted(window["layers"].items()):
            footprint = unary_union([LineString(points).buffer(width/2)
                                     for points, width in roads]).intersection(view)
            covered = channel.intersection(footprint).area
            layer_rows.append(dict(model_nozzle_z_mm=z, depositing_segment_count=len(roads),
                                   commanded_strand_widths_mm=sorted({width for _, width in roads}),
                                   commanded_footprint_in_CAD_channel_mm2=round(covered, 5),
                                   CAD_channel_area_clear_of_commanded_footprints_fraction=round(max(0., 1-covered/channel.area), 6)
                                       if channel.area > 0 else None))
            if first_footprint is None:
                first_footprint = footprint
        readings.append(dict(id=window["id"], text=label["text"], view_axis="-z",
                             source_stl_sha256=window["specimen"]["source_stl_sha256"],
                             CAD_section_z_mm=sample_z, nominal_recess_mm=label["nominal_recess_mm"],
                             CAD_recessed_channel_area_mm2=round(channel.area, 5),
                             sampled_open_model_layer_count=len(layer_rows), layers=layer_rows))
        visual.append((window, channel, first_footprint))
    plot_path = directory / "native-recessed-identity.png"
    if visual:
        figure, axes = plt.subplots(len(visual), 1, figsize=(12, 2.8*len(visual)), squeeze=False)
        for ax, (window, channel, footprint) in zip(axes.flat, visual):
            for geometry, color, alpha in ((channel, "#db9f42", .45), (footprint, "#255c82", .85)):
                if geometry is None:
                    continue
                for polygon in (list(geometry.geoms) if hasattr(geometry, "geoms") else [geometry]):
                    if polygon.is_empty or not hasattr(polygon, "exterior"):
                        continue
                    polygon = orient(polygon)
                    points, codes = [], []
                    for ring in (polygon.exterior, *polygon.interiors):
                        contour = np.array(ring.coords)
                        points.extend(contour)
                        codes.extend([PlotPath.MOVETO, *([PlotPath.LINETO]*(len(contour)-2)), PlotPath.CLOSEPOLY])
                    ax.add_patch(PathPatch(PlotPath(np.array(points), codes), facecolor=color,
                                           edgecolor="none", alpha=alpha))
            low, high = window["bounds"][:, :2]
            ax.set_xlim(high[0]+.4, low[0]-.4)
            ax.set_ylim(low[1]-.4, high[1]+.4)
            ax.set_aspect("equal")
            ax.set_title(f"{window['id']}: {window['label']['text']} — underside first-layer footprints", fontsize=11)
            ax.axis("off")
        figure.suptitle("Gold: CAD recessed channels; blue: commanded positive bead footprints; physical legibility unmeasured", fontsize=11)
        figure.tight_layout()
        figure.savefig(plot_path, dpi=140)
        plt.close(figure)
    return dict(scope="Negative-space underside identity review. Actual STL bed-section channels are compared with positive native road centerlines buffered by half their commanded width on the open recess layers. Coverage is a nominal strand-width footprint, not physical bead shape, recess depth or legibility.",
                windows=readings, plot=str(plot_path.relative_to(ROOT)) if visual else None)


def native_lettering_reading(text, report, directory):
    """Retain positive native model deposits beyond each marking's body face.

    This manual native-slice review witnesses retained glyph paths. It does not
    measure physical legibility or require a check on routine CAD builds.
    """
    from enclosure_support_audit import _WORD, _arc_points
    from matplotlib import pyplot as plt

    nominal_height = float(report["requested_layer_height_mm"])
    windows, by_object = [], defaultdict(list)
    for specimen, part in zip(report["specimens"], report["parts"], strict=True):
        shift = np.array(part["plate_translation_mm"])-np.array(part["source_center_mm"])
        for label in specimen.get("label_windows", []):
            bounds = np.array(label["bounds_mm"], dtype=float)+shift
            axis = label.get("view_axis", "x" if "surface_x_mm" in label else "z")
            if axis == "z":
                # A complete nominal slab above the face cannot be the base.
                bounds[0, 2] = float(label["surface_z_mm"])+shift[2]+nominal_height-1e-6
                bounds[1, 2] += nominal_height
                projected = (0, 1)
            elif axis == "x":
                # Body outer walls have their centerline inside the plain face.
                outward = int(label.get("outward_sign", 1))
                if outward not in {-1, 1}:
                    raise ValueError(f"{specimen['id']}: side lettering needs outward_sign -1 or +1")
                surface = float(label["surface_x_mm"])+shift[0]
                if outward > 0:
                    bounds[0, 0] = max(bounds[0, 0], surface+1e-6)
                else:
                    bounds[1, 0] = min(bounds[1, 0], surface-1e-6)
                bounds[0, 2] -= nominal_height
                bounds[1, 2] += nominal_height
                projected = (1, 2)
            else:
                raise ValueError(f"Unsupported label view axis {axis!r} for {specimen['id']}")
            window = dict(id=specimen["id"], text=label["text"], view_axis=axis,
                          outward_sign=int(label.get("outward_sign", 1)),
                          bounds=bounds, shift=shift, projected=projected,
                          layers=set(), features=set(), widths=set(), segments=[])
            windows.append(window)
            by_object[specimen["identify_id"]].append(window)
    x = y = e = 0.
    layer_z = None
    line_width = None
    current = None
    feature = ""
    absolute_xy, relative_e = True, True
    for raw in text.splitlines():
        line = raw.strip()
        label = re.match(r"; (?:start printing object, unique label id:|OBJECT_ID:)\s*(\d+)", line)
        if label:
            current = int(label.group(1))
        elif line.startswith("; stop printing object"):
            current = None
        elif line.startswith("; Z_HEIGHT:"):
            layer_z = float(line.split(":", 1)[1])
        elif line.startswith(("; LINE_WIDTH:", "; WIDTH:")):
            line_width = float(line.split(":", 1)[1])
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
            nx = words.get("X", x) if absolute_xy else x+words.get("X", 0.)
            ny = words.get("Y", y) if absolute_xy else y+words.get("Y", 0.)
            de = words.get("E", 0.) if relative_e else words.get("E", e)-e
            eligible = [w for w in by_object.get(current, [])
                        if layer_z is not None and w["bounds"][0, 2] <= layer_z <= w["bounds"][1, 2]]
            if eligible and de > 1e-9 and (nx != x or ny != y) and not feature.startswith(("Support", "Skirt", "Brim", "Custom", "Prime")):
                points = [(x, y), (nx, ny)] if command in {"G0", "G1"} else _arc_points((x, y), (nx, ny), words, command == "G2")
                points = [np.array((px, py, layer_z)) for px, py in points]
                for window in eligible:
                    for a, b in zip(points, points[1:]):
                        clipped = clipped_segment(a, b, *window["bounds"])
                        if clipped is not None and np.linalg.norm(clipped[1]-clipped[0]) > 1e-6:
                            window["segments"].append(tuple((p-window["shift"])[list(window["projected"])] for p in clipped))
                            window["layers"].add(round(layer_z, 5))
                            window["features"].add(feature)
                            if line_width is not None:
                                window["widths"].add(round(line_width, 5))
            x, y = nx, ny
            if "E" in words:
                e = e+words["E"] if relative_e else words["E"]
    count = len(windows)
    plot_path = directory/"native-lettering.png"
    if count:
        columns = min(3, count)
        rows = math.ceil(count/columns)
        figure, axes = plt.subplots(rows, columns, figsize=(4*columns, 2.3*rows), squeeze=False)
        for ax, window in zip(axes.flat, windows):
            for a, b in window["segments"]:
                ax.plot((a[0], b[0]), (a[1], b[1]), color="#19262c", linewidth=1.0)
            bounds = window["bounds"]-window["shift"]
            indices = list(window["projected"])
            low, high = bounds[:, indices]
            ax.set_xlim(low[0]-.8, high[0]+.8)
            ax.set_ylim(low[1]-.8, high[1]+.8)
            ax.set_aspect("equal")
            ax.set_title(f"{window['id']}: {window['text']} ({len(window['segments'])} segments)", fontsize=10)
            ax.axis("off")
        for ax in list(axes.flat)[count:]:
            ax.axis("off")
        figure.suptitle("Native depositing centerlines in marking windows; physical legibility unmeasured", fontsize=12)
        figure.tight_layout()
        figure.savefig(plot_path, dpi=130)
        plt.close(figure)
    readings = [dict(id=w["id"], text=w["text"], view_axis=w["view_axis"],
                     outward_sign=w["outward_sign"],
                     clipped_depositing_segment_count=len(w["segments"]),
                     depositing_layer_z_mm=sorted(w["layers"]),
                     commanded_strand_widths_mm=sorted(w["widths"]),
                     model_features=sorted(w["features"]),
                     retained_centerline_length_mm=round(sum(float(np.linalg.norm(b-a)) for a, b in w["segments"]), 3))
                for w in windows]
    return dict(scope="Positive native model centerlines in CAD marking windows. XY labels exclude nominal slabs touching the body face; side labels exclude centerlines inside the plain side face. Path retention does not establish physical legibility.",
                label_window_count=count,
                windows_with_deposition=sum(bool(w["segments"]) for w in windows),
                plot=str(plot_path.relative_to(ROOT)) if count else None,
                labels=readings)


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


def report_matches_manifest(report, current, assemblies):
    """Retain a partial run only for identical source bodies, poses and recipes."""
    if not report.get("specimens") or report.get("settings_source_sha256") != sha(PROFILE):
        return False
    project = ROOT / report["project"]
    if not project.is_file() or sha(project) != report.get("project_sha256"):
        return False
    if report.get("native"):
        archive = ROOT / report["native"]["archive"]
        if not archive.is_file() or sha(archive) != report["native"]["archive_sha256"]:
            return False
    held_assemblies = {row["id"]: row for row in report.get("print_assemblies", [])}
    for specimen in report["specimens"]:
        row = current.get(specimen["id"])
        if row is None:
            return False
        group = report["comparison_group"]
        if (row["print_group"] != group or row["name"] != specimen["name"]
                or float(row.get("rotation_x_degrees", 0)) != specimen["rotation_x_degrees"]
                or object_recipe(row, group) != specimen["object_overrides"]
                or recipe_height(row, group) != specimen["requested_layer_height_mm"]
                or recipe_layer_ranges(row, group) != specimen.get("requested_layer_ranges", [])
                or row.get("print_recipe", {}) != specimen.get("requested_print_recipe", {})
                or (assembly_id(row) or None) != specimen.get("print_assembly_id")
                or sha(source_path(row)) != specimen["source_stl_sha256"]):
            return False
        for key in ("support_ceiling_z_mm", "ceiling_xy_bounds_mm", "label_windows",
                    "recessed_label_windows",
                    "native_body_window", "native_release_probes", "native_gap_probes",
                    "travel_x_mm", "top_release_gap_mm", "lower_release_gap_mm",
                    "y_running_air_per_side_mm", "first_layer_chamfer_mm"):
            if row.get(key) != specimen.get(key):
                return False
        identifier = assembly_id(row)
        if identifier:
            assembly, held = assemblies.get(identifier), held_assemblies.get(identifier)
            if assembly is None or held is None or sha(source_path(assembly)) != held["source_stl_sha256"]:
                return False
            if [m["id"] for m in assembly["members"]] != [m["id"] for m in held["members"]]:
                return False
            for member, old in zip(assembly["members"], held["members"], strict=True):
                if not np.allclose(member_transform(member), np.array(old["member_transform_mm"]), atol=1e-9, rtol=0):
                    return False
    return True


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument("--slice", action="store_true", help="Run local Bambu Studio CLI; do not submit a print")
    modes.add_argument("--review", action="store_true", help="Read existing native archives without re-preparing or re-slicing")
    parser.add_argument("--group", choices=tuple(GROUP_HEIGHTS), action="append", help="Prepare only these project groups")
    args = parser.parse_args()
    manifest = json.loads(MANIFEST.read_text())
    assemblies = {row["id"]: row for row in manifest.get("print_assemblies", [])}
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
                batches = split_kit(groups[group], baseline, assemblies)
            for index, batch in enumerate(batches, 1):
                label = group if len(batches) == 1 else f"{group}-{index:02d}"
                project, report = make_project(group, batch, baseline, project_group=label, assemblies=assemblies)
                if args.slice and "native" not in report:
                    native_slice(project, report)
                reports.append(report)
        remove_stale_projects(groups.keys(), {r["project"] for r in reports})
    if args.group or args.review:
        # Carrier/display-placement refinements do not change a stable specimen's
        # manufacturing geometry. Keep its already-sliced project when every
        # specimen and recipe still belongs to the current printable manifest.
        current = {row["id"]: row for row in manifest["printable"]}
        held_reports = [json.loads(path.read_text()) for path in sorted(PROJECTS.glob("*.print.json"))]
        reports = [r for r in held_reports if report_matches_manifest(r, current, assemblies)]
    specimen_ids = [s["id"] for r in reports for s in r["specimens"]]
    manifest_ids = {row["id"] for row in manifest["printable"]}
    native_ids = {s["id"] for r in reports if "native" in r for s in r["specimens"]}
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
                 manifest_specimen_count=len(manifest_ids),
                 missing_manifest_specimen_ids=sorted(manifest_ids-set(specimen_ids)),
                 extra_specimen_ids=sorted(set(specimen_ids)-manifest_ids),
                 duplicate_specimen_ids=sorted(identifier for identifier in set(specimen_ids)
                                               if specimen_ids.count(identifier) > 1),
                 native_complete_for_manifest=native_ids == manifest_ids and len(specimen_ids) == len(manifest_ids),
                 total_saved_profile_estimated_seconds=seconds,
                 total_saved_profile_filament_estimate_g=round(grams, 2) if grams is not None else None,
                 physical_result="Unprinted; comparative specimens have no physical acceptance.",
                 preparation_only=True, submitted=False)
    save(HERE / "print-preparation.json", index)
    print(f"Prepared {len(reports)} The Pour projects; no jobs submitted", flush=True)


def split_kit(rows, baseline, assemblies=None):
    """Give the complete kit as many centered plates as its actual footprint needs."""
    units = print_units(rows, assemblies)
    sizes = {unit["row"]["id"]: print_size(unit["row"]) for unit in units}
    ordered = sorted(units, key=lambda unit: -float(np.prod(sizes[unit["row"]["id"]][:2])))
    batches = []
    for unit in ordered:
        for batch in batches:
            try:
                plate_layout([item["row"] for item in [*batch, unit]], baseline, border=40.)
            except ValueError:
                continue
            batch.append(unit)
            break
        else:
            batches.append([unit])
    return [[row for unit in batch for row in unit["members"]] for batch in batches]


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
