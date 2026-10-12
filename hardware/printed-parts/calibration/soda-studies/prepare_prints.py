"""Prepare The Pour from explicit manufacturing objects and material cohorts.

Call prepare_plate() for one plate or use the explicit print_plates in a manifest.
Preparation and requested local native slicing never connect to a printer or
change source CAD. Manufacturing transforms belong to print objects; display
assembly poses do not enter these functions. Temporary placement envelopes are
replaced by exact named volumes before the editable project is saved.
"""
from __future__ import annotations

from collections import Counter
import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET
import zipfile

import numpy as np
import trimesh

HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p / "tools/bambu_print.py").is_file())
os.environ.setdefault("HSM_NO_BUILD_LOCK", "1")
sys.path[:0] = [str(ROOT / "hardware/printed-parts/faucet"), str(ROOT / "hardware/scripts")]
import refresh_print_project as writer

sys.path.insert(0, str(HERE))
import native_reading as reading
from native_reading import native_deposits, is_model_deposit, clipped_segment

SLICER_SCOPE_SOURCE = {'tag': 'v02.08.02.61', 'path': 'src/libslic3r/PrintConfig.hpp', 'sha256': 'ec03ce1948fc40ba8be27525f95eadbe4ad925356ccb4d51a81d8bf23b09a9db', 'url': 'https://github.com/bambulab/BambuStudio/blob/v02.08.02.61/src/libslic3r/PrintConfig.hpp'}

OBJECT_KEYS = frozenset("""
    apply_scarf_seam_on_circles bridge_no_support brim_object_gap brim_type brim_width
    circle_compensation_manual_offset detect_floating_vertical_shell detect_narrow_internal_solid_infill elefant_foot_compensation enable_circle_compensation
    enable_support enable_support_ironing enforce_support_layers flush_into_infill flush_into_objects
    flush_into_support interface_shells interlocking_beam interlocking_beam_layer_count interlocking_beam_width
    interlocking_boundary_avoidance interlocking_depth interlocking_orientation internal_bridge_support_thickness layer_height
    line_width max_bridge_length min_bead_width min_feature_size mmu_segmented_region_interlocking_depth
    mmu_segmented_region_max_width only_one_wall_first_layer precise_z_height raft_contact_distance raft_expansion
    raft_first_layer_density raft_first_layer_expansion raft_layers role_base_wipe_speed scarf_angle_threshold
    seam_gap seam_placement_away_from_overhangs seam_position slice_closing_radius slicing_mode
    support_angle support_base_pattern support_base_pattern_spacing support_bottom_interface_spacing support_bottom_z_distance
    support_critical_regions_only support_expansion support_filament support_interface_bottom_layers support_interface_filament
    support_interface_loop_pattern support_interface_not_for_body support_interface_pattern support_interface_spacing support_interface_speed
    support_interface_top_layers support_ironing_direction support_ironing_flow support_ironing_inset support_ironing_pattern
    support_ironing_spacing support_ironing_speed support_line_width support_object_first_layer_gap support_object_xy_distance
    support_on_build_plate_only support_remove_small_overhang support_speed support_style support_threshold_angle
    support_top_z_distance support_type thick_bridges top_area_threshold top_one_wall_type
    tree_support_branch_angle tree_support_branch_diameter tree_support_branch_diameter_angle tree_support_branch_distance tree_support_wall_count
    wall_distribution_count wall_generator wall_transition_angle wall_transition_filter_deviation wall_transition_length
    wipe_speed xy_contour_compensation xy_hole_compensation
""".split())

REGION_KEYS = frozenset("""
    alternate_extra_wall bottom_color_penetration_layers bottom_shell_layers bottom_shell_thickness bottom_surface_density
    bottom_surface_pattern bridge_angle bridge_flow bridge_speed counterbore_hole_bridging
    detect_overhang_wall detect_thin_wall embedding_wall_into_infill enable_height_slowdown enable_overhang_speed
    ensure_vertical_shell_thickness fill_multiline filter_out_gap_fill fuzzy_skin fuzzy_skin_first_layer
    fuzzy_skin_mode fuzzy_skin_noise_type fuzzy_skin_octaves fuzzy_skin_persistence fuzzy_skin_point_distance
    fuzzy_skin_scale fuzzy_skin_thickness gap_infill_speed infill_combination infill_direction
    infill_instead_top_bottom_surfaces infill_lock_depth infill_rotate_step infill_shift_step infill_wall_overlap
    initial_layer_flow_ratio inner_wall_line_width inner_wall_speed internal_solid_infill_line_width internal_solid_infill_pattern
    internal_solid_infill_speed ironing_direction ironing_flow ironing_inset ironing_pattern
    ironing_spacing ironing_speed ironing_type locked_skeleton_infill_pattern locked_skin_infill_pattern
    minimum_sparse_infill_area monotonic_travel_into_wall outer_wall_line_width outer_wall_speed overhang_1_4_speed
    overhang_2_4_speed overhang_3_4_speed overhang_4_4_speed overhang_totally_speed override_filament_scarf_seam_setting
    precise_outer_wall print_flow_ratio seam_slope_conditional seam_slope_entire_loop seam_slope_gap
    seam_slope_inner_walls seam_slope_min_length seam_slope_start_height seam_slope_steps seam_slope_type
    skeleton_infill_density skeleton_infill_line_width skin_infill_density skin_infill_depth skin_infill_line_width
    slowdown_end_acc slowdown_end_height slowdown_end_speed slowdown_start_acc slowdown_start_height
    slowdown_start_speed small_perimeter_speed small_perimeter_threshold smooth_coefficient smooth_speed_discontinuity_area
    solid_infill_filament sparse_infill_anchor sparse_infill_anchor_max sparse_infill_density sparse_infill_filament
    sparse_infill_lattice_angle_1 sparse_infill_lattice_angle_2 sparse_infill_line_width sparse_infill_pattern sparse_infill_speed
    symmetric_infill_y_axis top_color_penetration_layers top_shell_layers top_shell_thickness top_solid_infill_flow_ratio
    top_surface_density top_surface_line_width top_surface_pattern top_surface_speed vertical_shell_speed
    wall_filament wall_loops wall_sequence
""".split())

IDENTITY = np.eye(4)
SUPPORTED_SUBTYPES = {"normal_part", "modifier_part", "support_blocker", "support_enforcer"}
SLICER = Path("/Applications/BambuStudio.app/Contents/MacOS/BambuStudio")
WORK = ROOT / ".cache/prints/soda-studies"


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def path_of(value):
    path = Path(value)
    return path if path.is_absolute() else ROOT / path


def relative(path):
    path = Path(path)
    return str(path.relative_to(ROOT)) if path.is_relative_to(ROOT) else str(path)


def scalar(value):
    if isinstance(value, bool):
        return "1" if value else "0"
    if isinstance(value, (int, float)):
        if not math.isfinite(value):
            raise ValueError("Print metadata numbers must be finite")
        return f"{value:g}"
    if not isinstance(value, str):
        raise ValueError("Object, volume and band metadata must be scalar slicer values")
    return value


def sparse_options(options, scope, identifier):
    allowed = {"object": OBJECT_KEYS | REGION_KEYS,
               "region": REGION_KEYS,
               "band": REGION_KEYS | {"layer_height"}}[scope]
    unsupported = set(options)-allowed
    if unsupported:
        details = {key: ("object-wide" if key in OBJECT_KEYS else "global or unknown")
                   for key in sorted(unsupported)}
        raise ValueError(f"{identifier}: {scope} settings cannot take effect here: {details}")
    return {key: scalar(value) for key, value in options.items()}


def rigid_matrix(value, identifier):
    matrix = np.asarray(value if value is not None else IDENTITY, dtype=float).reshape(4, 4)
    if (not np.all(np.isfinite(matrix)) or not np.allclose(matrix[3], [0, 0, 0, 1])
            or not np.allclose(matrix[:3, :3].T @ matrix[:3, :3], np.eye(3), atol=1e-8)
            or not np.isclose(np.linalg.det(matrix[:3, :3]), 1, atol=1e-8)):
        raise ValueError(f"{identifier}: manufacturing transforms must be finite rigid 4×4 matrices")
    return matrix


def resolved_object(obj, parts):
    if not obj.get("manufacturing_frame", {}).get("id"):
        raise ValueError(f"{obj['id']}: give the shared manufacturing frame an explicit ID")
    volumes, meshes = [], []
    for index, value in enumerate(obj["volumes"], 1):
        part_id = value["part_id"]
        part = parts[part_id]
        identifier = value.get("id", part_id)
        path = path_of(value.get("stl", part["stl"]))
        digest = sha(path)
        expected = value.get("stl_sha256", part.get("stl_sha256") if "stl" not in value else None)
        if expected and expected != digest:
            raise ValueError(f"{identifier}: frozen source STL hash does not match {path}")
        mesh = trimesh.load(path, force="mesh", process=True)
        if not mesh.is_watertight or not mesh.is_winding_consistent or mesh.volume <= 0:
            raise ValueError(f"{identifier}: a normal-part volume requires closed oriented source stock")
        paint = value.get("support_paint", {})
        if paint:
            if paint.get("source_stl_sha256") != digest:
                raise ValueError(f"{identifier}: exterior support paint needs this exact source STL hash")
            indices = np.asarray(paint.get("block_triangle_indices", []), dtype=np.int64)
            if indices.ndim != 1 or np.any(indices < 0) or np.any(indices >= len(mesh.faces)):
                raise ValueError(f"{identifier}: support paint indices must refer to processed source STL triangles")
            for index, code in paint.get("triangle_codes", {}).items():
                if not str(index).isdigit() or int(index) >= len(mesh.faces) or not re.fullmatch(r"[038]+", str(code)):
                    raise ValueError(f"{identifier}: source support paint requires valid triangle indices and Bambu subdivision codes")
        transform = rigid_matrix(value.get("transform_mm"), identifier)
        mesh.apply_transform(transform)
        meshes.append(mesh)
        slot = int(value.get("filament_slot", obj.get("filament_slot", 1)))
        if slot < 1:
            raise ValueError(f"{identifier}: filament slots are one-based")
        volumes.append({**value, "id": identifier, "part_id": part_id,
                        "name": value.get("name", part["name"]), "stl": relative(path),
                        "stl_sha256": digest, "mesh": mesh, "transform_mm": transform.tolist(),
                        "filament_slot": slot,
                        "region_overrides": sparse_options(value.get("region_overrides", {}), "region", identifier),
                        "source_part": {key: part[key] for key in (
                            "id", "name", "stl", "stl_sha256", "native_review", "native_body_window",
                            "label_windows", "recessed_label_windows", "native_release_probes", "native_gap_probes",
                            "travel_x_mm", "y_running_air_per_side_mm", "first_layer_chamfer_mm") if key in part}})
    if not volumes:
        raise ValueError(f"{obj['id']}: a printable object requires at least one named normal-part volume")
    bounds = np.array([np.min([m.bounds[0] for m in meshes], axis=0),
                       np.max([m.bounds[1] for m in meshes], axis=0)])
    if abs(bounds[0, 2]) > .002:
        raise ValueError(f"{obj['id']}: shared object frame must already be bed-normalized (minZ={bounds[0, 2]:g})")
    options = sparse_options(obj.get("object_overrides", {}), "object", obj["id"])
    return {**obj, "volumes": volumes, "bounds_mm": bounds, "object_overrides": options}


def normalized_ranges(obj, default_height):
    ranges, previous = [], None
    for value in sorted(obj.get("layer_ranges", []), key=lambda r: float(r["min_z_mm"])):
        low, high = float(value["min_z_mm"]), float(value["max_z_mm"])
        if not math.isfinite(low+high) or low < 0 or high <= low:
            raise ValueError(f"{obj['id']}: layer bands require increasing nonnegative finite print Z")
        if previous is not None and low < previous-1e-8:
            raise ValueError(f"{obj['id']}: overlapping layer bands need one explicit merged recipe")
        if high > obj["bounds_mm"][1, 2]+.01:
            raise ValueError(f"{obj['id']}: a layer band exceeds this manufacturing object's height")
        options = sparse_options(value["options"], "band", obj["id"])
        # The slicer consumes layer_height specially; include it even for a
        # scarf-only range so the model's layer schedule stays explicit.
        options.setdefault("layer_height", obj["object_overrides"].get("layer_height", scalar(default_height)))
        ranges.append({"min_z_mm": low, "max_z_mm": high, "options": options})
        previous = high
    return ranges


def placement_envelope(obj, directory):
    low, high = obj["bounds_mm"]
    mesh = trimesh.creation.box(extents=high-low)
    mesh.apply_translation((low+high)/2)
    path = directory / (re.sub(r"[^A-Za-z0-9_-]", "-", obj["id"])+".stl")
    mesh.export(path)
    return path


def object_document(part_id, mesh, center, support_paint=None):
    document = ET.Element(writer.qn("model"), unit="millimeter")
    resources = ET.SubElement(document, writer.qn("resources"))
    obj = ET.SubElement(resources, writer.qn("object"), id=part_id, type="model")
    geometry = ET.SubElement(obj, writer.qn("mesh"))
    vertices = ET.SubElement(geometry, writer.qn("vertices"))
    triangles = ET.SubElement(geometry, writer.qn("triangles"))
    for vertex in mesh.vertices-center:
        ET.SubElement(vertices, writer.qn("vertex"), **dict(zip("xyz", (f"{v:.9f}" for v in vertex))))
    blocked = set((support_paint or {}).get("block_triangle_indices", []))
    codes = (support_paint or {}).get("triangle_codes", {})
    for index, face in enumerate(mesh.faces):
        attributes = dict(zip(("v1", "v2", "v3"), map(str, face)))
        if index in blocked:
            attributes["paint_supports"] = "8"
        if str(index) in codes:
            attributes["paint_supports"] = codes[str(index)]
        ET.SubElement(triangles, writer.qn("triangle"), **attributes)
    return writer.xml(document)


def embed_objects(members, report, objects, default_height):
    model = ET.fromstring(members["3D/3dmodel.model"])
    config = ET.fromstring(members["Metadata/model_settings.config"])
    relationships = ET.fromstring(members["3D/_rels/3dmodel.model.rels"])
    ranges_xml = ET.Element("objects")
    next_id = 2*len(objects)+1
    object_reports, volume_reports = [], []
    for index, (obj, placement) in enumerate(zip(objects, report["parts"], strict=True), 1):
        center = np.asarray(placement["source_center_mm"])
        shift = np.asarray(placement["plate_translation_mm"])-center
        owner = model.find(f".//{writer.qn('object')}[@id='{placement['object_id']}']")
        components = owner.find(writer.qn("components"))
        components.clear()
        cfg = config.find(f"object[@id='{placement['object_id']}']")
        for part in list(cfg.findall("part")):
            cfg.remove(part)
        replace_metadata(cfg, {"name": obj.get("name", obj["id"]), **obj["object_overrides"]})
        geometry_entries = [*obj["volumes"]]
        for modifier in obj.get("modifiers", []):
            subtype = modifier["subtype"]
            if subtype not in SUPPORTED_SUBTYPES-{"normal_part"}:
                raise ValueError(f"{modifier['id']}: unsupported modifier role {subtype}")
            transform = rigid_matrix(modifier.get("transform_mm"), modifier["id"])
            bounds = np.asarray(modifier["bounds_mm"], dtype=float) if "bounds_mm" in modifier else None
            geometry_source = {}
            if "stl" in modifier:
                source = path_of(modifier["stl"])
                digest = sha(source)
                if modifier.get("stl_sha256") and modifier["stl_sha256"] != digest:
                    raise ValueError(f"{modifier['id']}: frozen modifier STL hash does not match")
                mesh = trimesh.load(source, force="mesh", process=True)
                geometry_source = {"stl": relative(source), "stl_sha256": digest}
            elif bounds is not None:
                if bounds.shape != (2, 3) or not np.all(np.isfinite(bounds)) or np.any(bounds[1] <= bounds[0]):
                    raise ValueError(f"{modifier['id']}: primitive modifier bounds require increasing finite XYZ")
                mesh = trimesh.creation.box(extents=bounds[1]-bounds[0])
                mesh.apply_translation(bounds.mean(axis=0))
            else:
                raise ValueError(f"{modifier['id']}: give an exact modifier STL or source primitive bounds")
            mesh.apply_transform(transform)
            options = sparse_options(modifier.get("options", {}), "region", modifier["id"])
            geometry_entries.append({**modifier, "name": modifier.get("name", modifier["id"]),
                                     "mesh": mesh, "region_overrides": options,
                                     "bounds_mm": bounds.tolist() if bounds is not None else None,
                                     "transform_mm": transform.tolist(), **geometry_source})
        source_reports = []
        for volume_index, entry in enumerate(geometry_entries):
            part_id = placement["part_id"] if volume_index == 0 else str(next_id)
            member = placement["member"] if volume_index == 0 else f"3D/Objects/volume-{next_id}.model"
            if volume_index:
                next_id += 1
                ET.SubElement(relationships, f"{{{writer.REL}}}Relationship", Target="/"+member,
                              Id=f"volume-{part_id}", Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel")
            mesh = entry["mesh"]
            members[member] = object_document(part_id, mesh, center, entry.get("support_paint"))
            ET.SubElement(components, writer.qn("component"), objectid=part_id,
                          transform="1 0 0 0 1 0 0 0 1 0 0 0", **{
                              f"{{{writer.PROD}}}path": "/"+member,
                              f"{{{writer.PROD}}}UUID": writer.identifier(obj["id"]+"/"+entry["id"]+"/component")})
            subtype = entry.get("subtype", "normal_part")
            part_cfg = ET.SubElement(cfg, "part", id=part_id, subtype=subtype,
                                     uuid=writer.identifier(obj["id"]+"/"+entry["id"]+"/part"))
            metadata = {"name": entry["name"], "matrix": "1 0 0 0 0 1 0 0 0 0 1 0 0 0 0 1"}
            if subtype == "normal_part":
                metadata.update(extruder=entry["filament_slot"], source_file=Path(entry["stl"]).name,
                                source_object_id=0, source_volume_id=volume_index,
                                source_offset_x=center[0], source_offset_y=center[1], source_offset_z=center[2])
            metadata.update(entry["region_overrides"])
            for key, value in metadata.items():
                writer.metadata(part_cfg, key, value)
            ET.SubElement(part_cfg, "mesh_stat", face_count=str(len(mesh.faces)), edges_fixed="0",
                          degenerate_facets="0", facets_removed="0", facets_reversed="0", backwards_edges="0")
            row = {"id": entry["id"], "part_id": entry.get("part_id"), "print_object_id": obj["id"],
                   "subtype": subtype, "object_id": placement["object_id"], "volume_id": part_id,
                   "identify_id": placement["identify_id"], "layer_range_object_index": index,
                   "member": member, "triangles": len(mesh.faces),
                   "shared_frame_bounds_mm": mesh.bounds.tolist(),
                   "plate_bounds_mm": (mesh.bounds+shift).tolist(),
                   "source_center_mm": center.tolist(), "plate_translation_mm": placement["plate_translation_mm"],
                   "embedded_vertex_error_mm": float(np.max(np.abs(np.round(mesh.vertices-center, 9)-(mesh.vertices-center))))}
            if subtype == "normal_part":
                row.update(source=entry["stl"], source_stl_sha256=entry["stl_sha256"],
                           filament_slot=entry["filament_slot"], source_to_shared_frame_mm=entry["transform_mm"],
                           region_overrides=entry["region_overrides"], source_part=entry["source_part"],
                           native_review=entry.get("native_review", {}))
                if entry.get("support_paint"):
                    row["support_paint"] = entry["support_paint"]
            else:
                row.update(modifier_bounds_mm=entry["bounds_mm"], region_overrides=entry["region_overrides"],
                           source_to_shared_frame_mm=entry["transform_mm"])
                if "stl" in entry:
                    row.update(source=entry["stl"], source_stl_sha256=entry["stl_sha256"])
            source_reports.append(row)
            volume_reports.append(row)
        for metadata in cfg.findall("metadata"):
            if "face_count" in metadata.attrib:
                metadata.set("face_count", str(sum(len(v["mesh"].faces) for v in obj["volumes"])))
        ranges = normalized_ranges(obj, default_height)
        if ranges:
            range_obj = ET.SubElement(ranges_xml, "object", id=str(index))
            for value in ranges:
                band = ET.SubElement(range_obj, "range", min_z=f"{value['min_z_mm']:.9f}", max_z=f"{value['max_z_mm']:.9f}")
                for key, val in value["options"].items():
                    ET.SubElement(band, "option", opt_key=key).text = val
        object_reports.append({"id": obj["id"], "name": obj.get("name", obj["id"]),
                               "manufacturing_frame": obj["manufacturing_frame"],
                               "object_id": placement["object_id"], "identify_id": placement["identify_id"],
                               "layer_range_object_index": index,
                               "object_overrides": obj["object_overrides"], "layer_ranges": ranges,
                               "manufacturing_to_plate_mm": np.vstack([np.column_stack([np.eye(3), shift]), [0, 0, 0, 1]]).tolist(),
                               "native_review": obj.get("native_review", {}),
                               "pauses": obj.get("pauses", []),
                               "recipe_sources": obj.get("recipe_sources", []),
                               "physical_part_ids": sorted({v["part_id"] for v in obj["volumes"]}),
                               "volumes": source_reports,
                               "native_schedule_scope": "One model schedule per parent, including registered material/captive volumes. Leaf deposition witnesses require their supplied windows or material tool attribution."})
    members["3D/3dmodel.model"] = writer.xml(model)
    members["Metadata/model_settings.config"] = writer.xml(config)
    members["3D/_rels/3dmodel.model.rels"] = writer.xml(relationships).replace(b"ns0:", b"").replace(b"xmlns:ns0=", b"xmlns=")
    if list(ranges_xml):
        members["Metadata/layer_config_ranges.xml"] = writer.xml(ranges_xml)
    else:
        members.pop("Metadata/layer_config_ranges.xml", None)
    pauses = ET.Element("custom_gcodes_per_layer")
    plate = ET.SubElement(pauses, "plate")
    ET.SubElement(plate, "plate_info", id="1")
    events = []
    for obj in objects:
        for pause in obj.get("pauses", []):
            z = float(pause["print_z_mm"])
            if not math.isfinite(z) or not 0 < z < obj["bounds_mm"][1, 2]:
                raise ValueError(f"{obj['id']}: an insertion pause needs a finite interior print height")
            events.append((z, pause))
    for z, pause in sorted(events, key=lambda event: event[0]):
        ET.SubElement(plate, "layer", top_z=f"{z:.6f}", type="1", extruder="1", color="",
                      extra=pause["message"], gcode="M400 U1")
    ET.SubElement(plate, "mode", value="SingleExtruder")
    if events:
        members["Metadata/custom_gcode_per_layer.xml"] = writer.xml(pauses)
    else:
        members.pop("Metadata/custom_gcode_per_layer.xml", None)
    report["print_objects"] = object_reports
    report["volumes"] = volume_reports
    report.pop("parts")  # The placement envelopes are not physical source parts.


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
    sizes = [trimesh.load(path_of(row["stl"]), force="mesh").extents[:2] for row in rows]
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

def turn_single_instance(members,report,angle):
    """Turn one complete native parent in the bed plane; source volumes stay exact."""
    if len(report['print_objects'])!=1:
        raise ValueError('A bed-plane turn currently requires one complete parent on its plate')
    rad=math.radians(float(angle));c,s=math.cos(rad),math.sin(rad)
    rotation=np.array([[c,-s,0.],[s,c,0.],[0.,0.,1.]])
    obj=report['print_objects'][0];first=obj['volumes'][0]
    center=np.asarray(first['source_center_mm']);placement=np.asarray(first['plate_translation_mm'])
    transform=' '.join(f'{v:.9f}' for v in [c,s,0.,-s,c,0.,0.,0.,1.,*placement])
    model=ET.fromstring(members['3D/3dmodel.model'])
    item=model.find(f".//{writer.qn('item')}[@objectid='{obj['object_id']}']")
    item.set('transform',transform);members['3D/3dmodel.model']=writer.xml(model)
    config=ET.fromstring(members['Metadata/model_settings.config'])
    for item in config.findall('assemble/assemble_item'):
        if item.get('object_id')==str(obj['object_id']):item.set('transform',transform)
    members['Metadata/model_settings.config']=writer.xml(config)
    obj['native_probe_to_plate_mm']=obj['manufacturing_to_plate_mm']
    matrix=np.eye(4);matrix[:3,:3]=rotation;matrix[:3,3]=placement-rotation@center
    obj['manufacturing_to_plate_mm']=matrix.tolist()
    obj['plate_rotation_z_degrees']=float(angle)
    for volume in obj['volumes']:
        b=np.asarray(volume['shared_frame_bounds_mm'])
        corners=np.array([[x,y,z] for x in b[:,0] for y in b[:,1] for z in b[:,2]])
        q=(corners-center)@rotation.T+placement
        volume['plate_bounds_mm']=[q.min(axis=0).tolist(),q.max(axis=0).tolist()]
        volume['plate_bounds_scope']='Containment envelope of the turned volume; contact/probe readings inverse-transform actual native paths, without oblique gap envelopes.'
    inverse=np.eye(4);inverse[:3,:3]=rotation.T;inverse[:3,3]=placement-rotation.T@placement
    report['deposition_xy_transform_mm']=inverse[:2,[0,1,3]].tolist()
    report['plate_rotation_z_degrees']=float(angle)
    report['native_probe_frame_scope']='Actual native XY paths are inverse-turned about the instance origin into its translated manufacturing frame before clipping source contact/body/letter windows. Source STL, common captive transforms and print-up axis remain unchanged.'


def prepare_plate(manifest, cohort, print_objects, output, *, offsets=None, border_mm=30., spacing_mm=18., rotation_z_degrees=0.):
    """Create one editable plate from an explicit cohort and native-parent list."""
    output = Path(output).resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    work = WORK / output.stem
    work.mkdir(parents=True, exist_ok=True)
    source_profile = path_of(cohort["settings_source"])
    with zipfile.ZipFile(source_profile) as archive:
        profile_members = {name: archive.read(name) for name in archive.namelist()}
    saved_settings = profile_members[writer.SETTINGS_MEMBER]
    settings = json.loads(saved_settings)
    settings.update(cohort.get("global_overrides", {}))
    profile_members[writer.SETTINGS_MEMBER] = (json.dumps(settings, indent=2)+"\n").encode()
    profile = work / "cohort-profile.3mf"
    writer.archive_write(profile, profile_members)
    parts = {row["id"]: row for row in manifest["parts"]}
    objects = [resolved_object(obj, parts) for obj in print_objects]
    slots = len(settings["filament_settings_id"])
    for obj in objects:
        if any(v["filament_slot"] > slots for v in obj["volumes"]):
            raise ValueError(f"{obj['id']}: a volume references a missing cohort material slot")
    folder = work / "placement-envelopes"
    folder.mkdir(exist_ok=True)
    envelopes = [placement_envelope(obj, folder) for obj in objects]
    if offsets is None:
        offsets = plate_layout([{ "stl": str(path), "rotation_x_degrees": 0 }
                                        for path in envelopes], settings, gap=spacing_mm, border=border_mm)
    report = writer.refresh(profile, output,
                            parts=tuple((obj.get("name", obj["id"]), path, 0.) for obj, path in zip(objects, envelopes)),
                            offsets=tuple(offsets), title=f"{manifest.get('title', 'The Pour')} — {cohort['id']}",
                            z_trim=cohort.get("requested_z_trim_mm"), plate_border=border_mm)
    with zipfile.ZipFile(output) as archive:
        members = {name: archive.read(name) for name in archive.namelist()}
    embed_objects(members, report, objects, float(settings["layer_height"]))
    if rotation_z_degrees:turn_single_instance(members,report,rotation_z_degrees)
    writer.archive_write(output, members)
    counts = Counter(v["part_id"] for obj in report["print_objects"] for v in obj["volumes"] if v["subtype"] == "normal_part")
    report.update(schema=3, cohort=cohort["id"], project=relative(output), project_sha256=sha(output),
                  settings_source=relative(source_profile), settings_source_sha256=sha(source_profile),
                  requested_global_overrides=cohort.get("global_overrides", {}),
                  first_layer_height_mm=float(settings["initial_layer_print_height"]),
                  material_volume_counts=dict(counts), printable_part_ids=sorted(counts),
                  preparation_source_sha256=sha(__file__), preparation_only=True, submitted=False,
                  reader_source_sha256=sha(reading.__file__), slicer_option_scope_source=SLICER_SCOPE_SOURCE,
                  saved_project_settings_sha256=hashlib.sha256(saved_settings).hexdigest(),
                  material_source=cohort.get("material_source", {}),
                  native_material_mapping={key: settings.get(key) for key in (
                      "filament_settings_id", "filament_colour", "filament_type", "filament_nozzle_map",
                      "nozzle_diameter", "extruder_offset", "enable_prime_tower")},
                  physical_result="Unprinted reference preparation; no release, fit, strength or lifetime acceptance.")
    output.with_suffix(".print.json").write_text(json.dumps(report, indent=2)+"\n")
    return output, report


def save(path, value):
    Path(path).write_text(json.dumps(value, indent=2)+"\n")


def native_summary(project, report, archive_path, directory):
    """Read requested native facts without connecting to a printer."""
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(archive_path) as archive:
        text = archive.read("Metadata/plate_1.gcode").decode()
        thumbnail = archive.read("Metadata/plate_1.png") if "Metadata/plate_1.png" in archive.namelist() else None
    (directory / "plate_1.gcode").write_text(text)
    if thumbnail:
        Path(project).with_suffix(".png").write_bytes(thumbnail)
    low, high, max_width = np.full(2, np.inf), np.full(2, -np.inf), 0.
    feature_counts = Counter()
    for deposit in native_deposits(text):
        feature = deposit["feature"]
        if feature.startswith("Custom"):
            continue
        width = deposit["strand_width_mm"] or .6
        max_width = max(max_width, width)
        padding = width/2+.1  # Arc-sampling allowance in addition to commanded width.
        low = np.minimum(low, deposit["points"].min(axis=0)-padding)
        high = np.maximum(high, deposit["points"].max(axis=0)+padding)
        feature_counts[feature] += 1
    if not np.all(np.isfinite([low, high])):
        raise ValueError(f"{project}: native archive contains no attributable layer deposits")
    bed_low, bed_high = np.asarray(report["shared_printable_area_mm"])
    margin = float(min(*(low-bed_low), *(bed_high-high)))
    layer_zs = [float(v) for v in re.findall(r"^; Z_HEIGHT:\s*([\d.]+)", text, re.M)]
    estimated = re.search(r"total estimated time:\s*(.+)", text)
    grams = re.search(r"^; total filament weight \[g\]\s*:\s*([\d.,]+)", text, re.M)
    schedules = reading.object_schedule_readings(text, report)
    result = dict(archive=relative(archive_path), archive_sha256=sha(archive_path),
        source_project_sha256=sha(project), gcode_sha256=hashlib.sha256(text.encode()).hexdigest(),
        layer_count=len(layer_zs), first_layer_z_mm=layer_zs[0] if layer_zs else None,
        object_model_deposition=schedules,
        estimated_time=estimated.group(1).strip() if estimated else None,
        saved_profile_filament_estimate_g=[float(v) for v in grams.group(1).split(",")] if grams else None,
        complete_layer_bead_bounds=dict(extrusion_bounds_xy_mm=[low.tolist(), high.tolist()],
            maximum_line_width_mm=max_width, arc_sampling_allowance_mm=.1,
            scope="Commanded width footprints for model, support, brim/skirt and prime-tower layer deposits. Machine Custom purge is excluded."),
        minimum_full_bead_bed_margin_mm=margin,
        layer_depositing_segment_counts_by_feature=dict(feature_counts),
        emitted_z_trim_mm=[float(v) for v in re.findall(r"^\s*G29\.1 Z([-+.\d]+)", text, re.M)],
        reviewer_sha256=sha(reading.__file__), sliced_locally=True, submitted=False,
        physical_scope="Requested settings and native model slabs/strand footprints; physical release, fit, seal, finish, strength and lifetime remain unmeasured.")
    result['material_frame_reading']=reading.native_material_frames(text)
    ceilings = reading.ceiling_support_readings(text, report, schedules)
    if ceilings:
        result["ceiling_support_readings"] = ceilings
    bands = reading.comparison_band_readings(report, schedules)
    if bands:
        result["comparison_band_readings"] = bands
    adapter = reading.v3_probe_adapter(report)
    specimens = adapter["specimens"]
    if any(s.get("label_windows") for s in specimens):
        result["lettering_reading"] = reading.native_lettering_reading(text, adapter, directory)
    if any(s.get("recessed_label_windows") for s in specimens):
        result["recessed_identity_reading"] = reading.native_recessed_lettering_reading(text, adapter, directory)
    if any(s.get("requested_print_recipe", {}).get("wall_probes") for s in specimens):
        result["source_profile_reading"] = reading.native_source_profile_reading(text, adapter)
    if any(s.get("native_release_probes") or s.get("native_gap_probes") for s in specimens):
        body = reading.model_deposition_facts(text, adapter)
        result["attributed_body_deposition"] = body
        result["captive_release_reading"] = reading.native_release_reading(text, adapter, body)
    if any(obj.get("pauses") for obj in report["print_objects"]):
        result["insertion_pause_reading"] = reading.native_pause_reading(text, report)
    return result


def native_slice(project, report):
    directory = WORK / Path(project).stem / "native"
    directory.mkdir(parents=True, exist_ok=True)
    archive_name = Path(project).stem+".gcode.3mf"
    command = [str(SLICER), "--slice", "0", "--arrange", "0", "--orient", "0",
               "--outputdir", str(directory), "--export-3mf", archive_name, str(project)]
    save(directory / "slice-command.json", dict(argv=command, printer_connection=False))
    print(f"Native slicing {report['plate_id']}: {len(report['print_objects'])} print objects", flush=True)
    with (directory / "slice.log").open("w") as log:
        result = subprocess.run(command, cwd=directory, stdout=log, stderr=subprocess.STDOUT)
    if result.returncode:
        raise RuntimeError(f"Bambu Studio exited {result.returncode}: {directory / 'slice.log'}")
    report["native"] = native_summary(project, report, directory / archive_name, directory)
    report["preparation_only"] = False
    save(Path(project).with_suffix(".print.json"), report)
    print(json.dumps(dict(plate=report["plate_id"], estimated_time=report["native"]["estimated_time"],
        filament_g=report["native"]["saved_profile_filament_estimate_g"],
        full_bead_margin_mm=round(report["native"]["minimum_full_bead_bed_margin_mm"], 2))), flush=True)


def by_id(rows):
    values = list(rows.values()) if isinstance(rows, dict) else list(rows)
    result = {row["id"]: row for row in values}
    if len(result) != len(values):
        raise ValueError("Print manifest IDs must be unique within each collection")
    return result


def estimates_seconds(value):
    return sum(float(amount)*dict(d=86400, h=3600, m=60, s=1)[unit]
               for amount, unit in re.findall(r"([\d.]+)\s*([dhms])", value or ""))


def report_matches_plan(report, manifest, cohort, objects):
    """Bind a retained plate to unchanged source bytes, transforms and settings."""
    if (report.get("settings_source_sha256") != sha(path_of(cohort["settings_source"]))
            or report.get("requested_global_overrides") != cohort.get("global_overrides", {})):
        return False
    existing = {obj["id"]: obj for obj in report.get("print_objects", [])}
    if set(existing) != {obj["id"] for obj in objects}:
        return False
    parts = by_id(manifest["parts"])
    for obj in objects:
        prior = existing[obj["id"]]
        if (prior["manufacturing_frame"] != obj["manufacturing_frame"]
                or prior["object_overrides"] != sparse_options(obj.get("object_overrides", {}), "object", obj["id"])
                or prior.get("pauses", []) != obj.get("pauses", [])
                or prior.get("native_review", {}) != obj.get("native_review", {})):
            return False
        previous_volumes = {v["id"]: v for v in prior["volumes"] if v["subtype"] == "normal_part"}
        if set(previous_volumes) != {v.get("id", v["part_id"]) for v in obj["volumes"]}:
            return False
        for value in obj["volumes"]:
            part = parts[value["part_id"]]
            identifier = value.get("id", value["part_id"])
            volume = previous_volumes[identifier]
            source = path_of(value.get("stl", part["stl"]))
            if (volume["source_stl_sha256"] != sha(source)
                    or volume["filament_slot"] != int(value.get("filament_slot", obj.get("filament_slot", 1)))
                    or not np.allclose(volume["source_to_shared_frame_mm"], rigid_matrix(value.get("transform_mm"), identifier))
                    or volume["region_overrides"] != sparse_options(value.get("region_overrides", {}), "region", identifier)
                    or volume.get("support_paint", {}) != value.get("support_paint", {})
                    or volume.get("native_review", {}) != value.get("native_review", {})):
                return False
        bounds = np.array([np.min([v["shared_frame_bounds_mm"][0] for v in previous_volumes.values()], axis=0),
                           np.max([v["shared_frame_bounds_mm"][1] for v in previous_volumes.values()], axis=0)])
        if prior["layer_ranges"] != normalized_ranges({**obj, "bounds_mm": bounds,
                "object_overrides": sparse_options(obj.get("object_overrides", {}), "object", obj["id"])}, report["layer_height_mm"]):
            return False
        prior_modifiers = [v for v in prior["volumes"] if v["subtype"] != "normal_part"]
        if len(prior_modifiers) != len(obj.get("modifiers", [])):
            return False
        for prior_modifier, modifier in zip(prior_modifiers, obj.get("modifiers", []), strict=True):
            if (prior_modifier["id"] != modifier["id"] or prior_modifier["subtype"] != modifier["subtype"]
                    or prior_modifier["modifier_bounds_mm"] != modifier.get("bounds_mm")
                    or not np.allclose(prior_modifier["source_to_shared_frame_mm"], rigid_matrix(modifier.get("transform_mm"), modifier["id"]))
                    or ("stl" in modifier and prior_modifier.get("source_stl_sha256") != sha(path_of(modifier["stl"])))
                    or prior_modifier["region_overrides"] != sparse_options(modifier.get("options", {}), "region", modifier["id"])):
                return False
    return True


def retained_layout_matches(report, plate):
    """A retained native project keeps the same parent placements and inset."""
    if abs(float(report.get('plate_border_mm', 0))-float(plate.get('model_border_mm', 30))) > 1e-6:
        return False
    if abs(float(report.get('plate_rotation_z_degrees',0))-float(plate.get('rotation_z_degrees',0))) > 1e-7:
        return False
    requested=plate.get('offsets_mm')
    if requested is None:
        if len(report['print_objects'])==1:
            requested=[[0.,0.]]
        else:
            return report.get('requested_layout') == {key:plate.get(key) for key in
                ('offsets_mm','model_border_mm','model_spacing_mm')}
    center=np.asarray(report['shared_printable_area_mm']).mean(axis=0)
    placements=report.get('parts') or [obj['volumes'][0] for obj in report['print_objects']]
    offsets=[(np.asarray(row['plate_translation_mm'])[:2]-center).tolist() for row in placements]
    return len(offsets)==len(requested) and np.allclose(offsets,requested,atol=1e-5)


def retain_reviewed_projects(manifest_path, output_directory, source_directories):
    """Copy exact reviewed editable projects and retain their native archives.

    Only unchanged source hashes, rigid manufacturing transforms, recipes and
    placements qualify. Public source-path rebinding is metadata; serialization
    is deliberately avoided so the reviewed project and archive stay identical.
    """
    manifest_path=Path(manifest_path).resolve();manifest=json.loads(manifest_path.read_text())
    objects,cohorts=(by_id(manifest[k]) for k in ('print_objects','print_cohorts'))
    output_directory=Path(output_directory).resolve();output_directory.mkdir(parents=True,exist_ok=True)
    retained=[]
    for plate in manifest['print_plates']:
        name=plate.get('filename','the-pour-'+plate['id']);target=output_directory/(name+'.3mf')
        for folder in source_directories:
            candidate=Path(folder).resolve()/(name+'.3mf');sidecar=candidate.with_suffix('.print.json')
            if not candidate.exists() or not sidecar.exists():continue
            report=json.loads(sidecar.read_text());native=report.get('native',{})
            values=[objects[i] for i in plate['object_ids']]
            if (not native or sha(candidate)!=report['project_sha256']
                    or not report_matches_plan(report,manifest,cohorts[plate['cohort']],values)
                    or not retained_layout_matches(report,plate)
                    or not path_of(native['archive']).exists()
                    or sha(path_of(native['archive']))!=native['archive_sha256']):
                continue
            if candidate != target:shutil.copyfile(candidate,target)
            if candidate.with_suffix('.png').exists() and candidate != target:
                shutil.copyfile(candidate.with_suffix('.png'),target.with_suffix('.png'))
            rebind_current_sources(report,manifest,cohorts[plate['cohort']],plate,manifest_path,target)
            report.update(bound_to_current_manifest_sha256=sha(manifest_path),
                retained_reviewed_project=relative(candidate),
                requested_layout={key:plate.get(key) for key in ('offsets_mm','model_border_mm','model_spacing_mm')},
                retention_scope='Byte-identical reviewed project/native archive; current source hashes, transforms, settings and placements matched. Source filenames inside the immutable project retain their reviewed names.')
            save(target.with_suffix('.print.json'),report);retained.append(plate['id']);break
    return retained


def rebind_current_sources(report,manifest,cohort,plate,manifest_path,project):
    """Bind reviewed embedded geometry to its current public source filenames."""
    parts=by_id(manifest['parts']);objects=by_id(manifest['print_objects'])
    lookup={}
    for obj in report['print_objects']:
        inputs={v.get('id',v['part_id']):v for v in objects[obj['id']]['volumes']}
        for volume in obj['volumes']:
            if volume['subtype']!='normal_part':continue
            part=parts[volume['part_id']];source=inputs[volume['id']].get('stl',part['stl'])
            if sha(path_of(source))!=volume['source_stl_sha256']:
                raise ValueError(f"{volume['id']}: rebinding requires byte-identical source geometry")
            volume['source']=source;volume['source_part']['stl']=part['stl']
            lookup[volume['id']]=volume
    for volume in report.get('volumes',[]):
        if volume.get('id') in lookup:
            source=lookup[volume['id']];volume['source']=source['source']
            volume['source_part']['stl']=source['source_part']['stl']
    report.setdefault('reviewed_original_manifest',dict(path=report.get('source_manifest'),
        sha256=report.get('source_manifest_sha256')))
    report.update(project=relative(project),source_manifest=relative(manifest_path),
        source_manifest_sha256=sha(manifest_path),bound_to_current_manifest_sha256=sha(manifest_path),
        material_source=cohort.get('material_source',{}),current_binding_source_sha256=sha(__file__),
        source_filename_binding_scope='Current public source paths and manifest digest bind the same embedded mesh bytes, manufacturing transforms, settings and native archive. The immutable editable project retains original internal filenames; no reslice is implied.')


def compact_project_report(report,output_directory):
    """Link the full per-project evidence while keeping the kit index readable."""
    metadata=Path(output_directory)/Path(report['project']).with_suffix('.print.json').name
    native=report.get('native',{})
    def compact(value):
        if isinstance(value,list):return [compact(v) for v in value]
        if isinstance(value,dict):return {k:compact(v) for k,v in value.items() if k not in
            ('layers','emitted_model_layers','model_layer_nozzle_z_mm','support_layer_tops_below_ceiling_mm','segments','paths')}
        return value
    keep=('archive','archive_sha256','gcode_sha256','source_project_sha256','estimated_time',
        'saved_profile_filament_estimate_g','minimum_full_bead_bed_margin_mm','first_layer_z_mm','layer_count',
        'ceiling_support_readings','comparison_band_readings','captive_release_reading','insertion_pause_reading',
        'lettering_reading','recessed_identity_reading','source_profile_reading','registered_marking_readings',
        'material_frame_reading','sliced_locally','submitted')
    return dict(plate_id=report.get('plate_id'),project=report['project'],project_sha256=report['project_sha256'],
        preparation_metadata=relative(metadata),preparation_metadata_sha256=sha(metadata),
        cohort=report['cohort'],settings_source=report['settings_source'],settings_source_sha256=report['settings_source_sha256'],
        material_source=report.get('material_source',{}),native_material_mapping=report.get('native_material_mapping',{}),
        print_object_ids=[o['id'] for o in report['print_objects']],
        physical_part_ids=sorted({i for o in report['print_objects'] for i in o['physical_part_ids']}),
        native=compact({k:native[k] for k in keep if k in native}),
        submitted=False,scope='Full source paint, geometry transforms and native deposition arrays are in the linked per-project metadata.')


def prepare_manifest(manifest_path, *, output_directory=None, selected_plates=None, slice_native=False,
                     collect_only=False, reuse_directories=()):
    """Prepare an explicit manual plate plan; existing unrelated projects are retained."""
    manifest_path = Path(manifest_path).resolve()
    manifest = json.loads(manifest_path.read_text())
    if not all(key in manifest for key in ("print_objects", "print_cohorts", "print_plates")):
        raise ValueError("A plate manifest requires print_objects, print_cohorts and print_plates.")
    objects, cohorts, plates = (by_id(manifest[key]) for key in ("print_objects", "print_cohorts", "print_plates"))
    assigned = Counter(identifier for plate in plates.values() for identifier in plate["object_ids"])
    if set(assigned) != set(objects) or any(count != 1 for count in assigned.values()):
        raise ValueError("Each declared native print object must occur on exactly one explicit plate")
    selected = set(selected_plates or plates)
    unknown = selected-set(plates)
    if unknown:
        raise ValueError(f"Unknown plate IDs: {sorted(unknown)}")
    output_directory = Path(output_directory or manifest_path.parent / "prints").resolve()
    output_directory.mkdir(parents=True, exist_ok=True)
    if reuse_directories:
        retain_reviewed_projects(manifest_path,output_directory,reuse_directories)
    digest = sha(manifest_path)
    reports = []
    for plate_id, plate in plates.items():
        path = output_directory / (plate.get("filename", "the-pour-"+plate_id)+".3mf")
        previous_path = path.with_suffix(".print.json")
        previous = json.loads(previous_path.read_text()) if previous_path.exists() else None
        cohort = cohorts[plate["cohort"]]
        values = [objects[identifier] for identifier in plate["object_ids"]]
        if collect_only or plate_id not in selected:
            if (previous and report_matches_plan(previous, manifest, cohort, values)
                    and retained_layout_matches(previous,plate)
                    and path.exists() and sha(path) == previous["project_sha256"]):
                rebind_current_sources(previous,manifest,cohort,plate,manifest_path,path)
                previous["bound_to_current_manifest_sha256"] = digest
                save(previous_path,previous)
                reports.append(previous)
            continue
        if any(value["cohort"] != cohort["id"] for value in values):
            raise ValueError(f"{plate_id}: every native object must belong to this material/process cohort")
        if (previous and report_matches_plan(previous,manifest,cohort,values)
                and retained_layout_matches(previous,plate) and path.exists()
                and sha(path)==previous['project_sha256'] and previous.get('native')
                and path_of(previous['native']['archive']).exists()
                and sha(path_of(previous['native']['archive']))==previous['native']['archive_sha256']):
            previous['bound_to_current_manifest_sha256']=digest
            save(previous_path,previous)
            reports.append(previous)
            print(f"Reusing {plate_id}: unchanged source, recipe, placement and reviewed native archive",flush=True)
            continue
        project, report = prepare_plate(manifest, cohort, values, path,
            offsets=plate.get("offsets_mm"), border_mm=float(plate.get("model_border_mm", 30)),
            spacing_mm=float(plate.get("model_spacing_mm", 18)),rotation_z_degrees=float(plate.get('rotation_z_degrees',0)))
        report.update(plate_id=plate_id, source_manifest=relative(manifest_path), source_manifest_sha256=digest)
        report['requested_layout']={key:plate.get(key) for key in ('offsets_mm','model_border_mm','model_spacing_mm')}
        if (previous and previous.get("project_sha256") == report["project_sha256"] and previous.get("native")
                and path_of(previous["native"]["archive"]).exists()
                and sha(path_of(previous["native"]["archive"])) == previous["native"]["archive_sha256"]):
            report["native"] = previous["native"]
            report["native"]["reused_identical_input_project"] = True
            report["preparation_only"] = False
            print(f"Reusing {plate_id}: byte-identical editable project and frozen native archive", flush=True)
        elif slice_native:
            native_slice(project, report)
        save(previous_path, report)
        reports.append(report)
    index_path = output_directory.parent / "print-preparation.json"
    index = dict(schema=3, title=manifest.get("title", "The Pour"), source_manifest=relative(manifest_path),
        source_manifest_sha256=digest, preparation_source_sha256=sha(__file__), reader_source_sha256=sha(reading.__file__),
        requested_plate_ids=list(plates), prepared_plate_ids=[row.get("plate_id") for row in reports],
        native_project_count=sum(bool(row.get("native")) for row in reports), projects=[], submitted=False)
    expected_parts = {row["id"] for row in manifest["parts"] if row.get("printable", True)}
    coverage = Counter(identifier for report in reports for obj in report["print_objects"] for identifier in obj["physical_part_ids"])
    index["physical_part_coverage"] = dict(expected_part_count=len(expected_parts),
        prepared_unique_part_count=len(coverage), missing_part_ids=sorted(expected_parts-set(coverage)),
        unexpected_part_ids=sorted(set(coverage)-expected_parts),
        parts_in_multiple_native_parents={identifier: count for identifier, count in coverage.items() if count > 1},
        material_volume_scope="Registered colour volumes count as one physical part inside their common parent.")
    native = [row["native"] for row in reports if row.get("native")]
    index.update(total_estimated_seconds=sum(estimates_seconds(row["estimated_time"]) for row in native),
        total_saved_profile_filament_estimate_g=round(sum(sum(row.get("saved_profile_filament_estimate_g") or []) for row in native), 2),
        minimum_full_bead_bed_margin_mm=min((row["minimum_full_bead_bed_margin_mm"] for row in native), default=None),
        native_estimate_scope="Prepared native projects only; saved profile material/time estimates, not observed consumption or runtime.")
    index['projects']=[compact_project_report(row,output_directory) for row in reports]
    save(index_path, index)
    return index


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=HERE / "manifest.json")
    parser.add_argument("--output-directory", type=Path)
    parser.add_argument("--plate", action="append", help="Prepare only this explicit plate ID; can be repeated")
    parser.add_argument("--slice", action="store_true", help="Slice locally; never submit to a printer")
    parser.add_argument('--collect',action='store_true',help='Collect matching existing projects without preparing or slicing')
    parser.add_argument('--reuse-reviewed',action='append',type=Path,default=[],help='Copy matching reviewed projects from this directory, preserving their bytes')
    args = parser.parse_args()
    prepare_manifest(args.manifest, output_directory=args.output_directory,
                     selected_plates=args.plate, slice_native=args.slice,collect_only=args.collect,
                     reuse_directories=args.reuse_reviewed)


if __name__ == "__main__":
    main()
