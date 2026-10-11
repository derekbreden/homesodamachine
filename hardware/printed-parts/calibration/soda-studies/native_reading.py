"""Manual native-path readers for The Pour's supplied manufacturing windows.

These functions read a locally generated archive when a review is requested.
They are not repository hooks and do not connect to printers. Model layer slabs,
bridge flow height and commanded line-width footprints remain distinct from
physical printed clearance, fit, surface finish and acceptance.
"""
from collections import defaultdict
import hashlib
import math
from pathlib import Path
import re
import sys

import numpy as np
import trimesh

HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p / "tools/bambu_print.py").is_file())
sys.path[:0] = [str(ROOT / "hardware/scripts")]


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def object_schedule_readings(text, report):
    """Read each native parent's model schedule once, including material volumes."""
    objects = {obj["identify_id"]: obj for obj in report["print_objects"]}
    layers = {label: {} for label in objects}
    supports = defaultdict(int)
    for deposit in native_deposits(text, report.get("deposition_xy_transform_mm")):
        label = deposit["identify_id"]
        if label not in objects:
            continue
        if deposit["feature"].startswith("Support"):
            supports[label] += 1
            continue
        if not is_model_deposit(deposit):
            continue
        z = deposit["model_z_mm"]
        value = layers[label].setdefault(z, dict(features=[], heights=set(), widths=set(), nozzle_zs=set(),
            physical_tools=set(), selected_filament_codes=set(), outer_wall_length_mm=0.,
            outer_wall_moves=0, outer_wall_z_moves=0, outer_wall_z_ramps=0, nonplanar_moves=0))
        feature = deposit["feature"]
        if not value["features"] or value["features"][-1] != feature:
            value["features"].append(feature)
        for key, source in (("heights", "strand_height_mm"), ("widths", "strand_width_mm"),
                            ("physical_tools", "physical_tool_index"),
                            ("selected_filament_codes", "selected_filament_code")):
            if deposit[source] is not None:
                value[key].add(deposit[source])
        for endpoint in (deposit["commanded_nozzle_start_z_mm"], deposit["commanded_nozzle_end_z_mm"]):
            if endpoint is not None:
                value["nozzle_zs"].add(endpoint)
        ramp = (deposit["commanded_nozzle_start_z_mm"] is not None
                and deposit["commanded_nozzle_end_z_mm"] is not None
                and abs(deposit["commanded_nozzle_end_z_mm"]-deposit["commanded_nozzle_start_z_mm"]) > 1e-8)
        value["nonplanar_moves"] += int(ramp)
        if feature in {"Outer wall", "Overhang wall"}:
            value["outer_wall_length_mm"] += sum(float(np.linalg.norm(b-a)) for a, b in
                zip(deposit["points"], deposit["points"][1:]))
            value["outer_wall_moves"] += 1
            value["outer_wall_z_moves"] += int(deposit["explicit_z_move"])
            value["outer_wall_z_ramps"] += int(ramp)
    readings = []
    walls = {"Inner wall", "Outer wall", "Overhang wall"}
    infill = {"Sparse infill", "Internal solid infill", "Bottom surface", "Top surface", "Bridge"}
    for label, obj in objects.items():
        rows, previous = [], 0.
        for z, value in sorted(layers[label].items()):
            sequence = value["features"]
            wp = [i for i, name in enumerate(sequence) if name in walls]
            ip = [i for i, name in enumerate(sequence) if name in infill]
            rows.append(dict(model_nozzle_z_mm=round(z, 5), nominal_model_layer_z_mm=round(z, 5),
                nominal_model_z_step_mm=round(z-previous, 5),
                commanded_depositing_nozzle_z_extent_mm=([min(value["nozzle_zs"]), max(value["nozzle_zs"])]
                    if value["nozzle_zs"] else None),
                nonplanar_model_depositing_move_count=value["nonplanar_moves"],
                commanded_strand_heights_mm=sorted(value["heights"]),
                commanded_strand_widths_mm=sorted(value["widths"]),
                depositing_feature_sequence=sequence,
                first_wall_precedes_first_infill=min(wp) < min(ip) if wp and ip else None,
                native_filament_selector_indices=sorted(value["physical_tools"]),
                selected_filament_codes=sorted(value["selected_filament_codes"]),
                outer_wall_centerline_length_mm=round(value["outer_wall_length_mm"], 5),
                outer_wall_depositing_moves=value["outer_wall_moves"],
                outer_wall_depositing_moves_with_z=value["outer_wall_z_moves"],
                outer_wall_depositing_z_ramp_move_count=value["outer_wall_z_ramps"]))
            previous = z
        readings.append(dict(id=obj["id"], identify_id=label,
            physical_part_ids=obj["physical_part_ids"], manufacturing_frame=obj["manufacturing_frame"],
            requested_object_overrides=obj["object_overrides"], requested_layer_ranges=obj["layer_ranges"],
            emitted_model_layers=rows, model_layer_count=len(rows),
            first_model_nozzle_z_mm=rows[0]["model_nozzle_z_mm"] if rows else None,
            model_layer_steps_mm=sorted({row["nominal_model_z_step_mm"] for row in rows[1:]}),
            emitted_object_support_segment_count=supports[label],
            model_z_reading_scope="The model_nozzle_z_mm compatibility field and nominal_model_layer_z_mm read the native layer comment. Actual depositing nozzle Z endpoints are reported separately; spiral/scarf ramps are not planar slabs.",
            attribution_scope="Complete parent print object. Registered colours and captive bodies share this schedule; no individual leaf schedule is inferred."))
    return readings


def comparison_band_readings(report, schedules):
    """Summarize supplied comparison windows from emitted parent paths."""
    by_id = {row["id"]: row for row in schedules}
    readings = []
    for obj in report["print_objects"]:
        schedule = by_id[obj["id"]]
        for band in obj.get("native_review", {}).get("comparison_bands", []):
            low, high = band["print_z_mm"]
            guard = float(band.get("interior_guard_mm", .48))
            rows = [row for row in schedule["emitted_model_layers"]
                    if low+guard <= row["nominal_model_layer_z_mm"] <= high-guard]
            lengths = [row["outer_wall_centerline_length_mm"] for row in rows]
            extents = [row["commanded_depositing_nozzle_z_extent_mm"] for row in rows
                       if row["commanded_depositing_nozzle_z_extent_mm"] is not None]
            readings.append(dict(print_object_id=obj["id"], requested_band=band,
                interior_guard_mm=guard, sampled_model_layer_count=len(rows),
                sampled_nominal_model_layer_z_extent_mm=([rows[0]["nominal_model_layer_z_mm"],
                    rows[-1]["nominal_model_layer_z_mm"]] if rows else None),
                emitted_nominal_model_z_steps_mm=sorted({row["nominal_model_z_step_mm"] for row in rows}),
                commanded_depositing_nozzle_z_extent_mm=([min(v[0] for v in extents),
                    max(v[1] for v in extents)] if extents else None),
                outer_wall_centerline_length_per_layer_mm=dict(minimum=min(lengths), maximum=max(lengths),
                    mean=sum(lengths)/len(lengths)) if lengths else None,
                outer_wall_depositing_z_ramp_move_count=sum(row["outer_wall_depositing_z_ramp_move_count"]
                    for row in rows),
                outer_wall_moves_with_explicit_z_word=sum(row["outer_wall_depositing_moves_with_z"] for row in rows),
                scope="Interior native parent layer comments, depositing Z ramps and outer/overhang centerline lengths. Requested gap/type values are not physical groove/ridge or closure measurements."))
    return readings


def v3_probe_adapter(report):
    """Map physical leaves and supplied common-frame windows to the probe readers."""
    specimens, parts = [], []
    for obj in report["print_objects"]:
        physical = {}
        for volume in obj["volumes"]:
            if volume["subtype"] == "normal_part":
                physical.setdefault(volume["part_id"], volume)
        shift = np.asarray(obj.get('native_probe_to_plate_mm',obj["manufacturing_to_plate_mm"]))[:3, 3]
        for identifier, volume in physical.items():
            source = volume["source_part"]
            review = {**source.get("native_review", {}), **volume.get("native_review", {})}
            recipe = {"native_parent": obj["id"], **obj.get("native_review", {}), **review}
            specimen = {**source, **review, "id": identifier, "identify_id": obj["identify_id"],
                "requested_print_recipe": recipe, "requested_layer_ranges": obj["layer_ranges"],
                "requested_layer_height_mm": float(obj["object_overrides"].get("layer_height", report["layer_height_mm"])),
                "source_stl_sha256": source.get("stl_sha256", volume["source_stl_sha256"])}
            window = review.get("body_window", source.get("native_body_window"))
            if window is not None:
                specimen["native_body_window"] = window
            if len(physical) > 1:
                specimen["print_assembly_id"] = obj["id"]
            parts.append(dict(source=source["stl"], identify_id=obj["identify_id"],
                rotation_x_degrees=0., source_center_mm=[0., 0., 0.], plate_translation_mm=shift.tolist()))
            specimens.append(specimen)
    return dict(specimens=specimens, parts=parts, first_layer_height_mm=report["first_layer_height_mm"],
                requested_layer_height_mm=report["layer_height_mm"],deposition_xy_transform_mm=report.get('deposition_xy_transform_mm'))


def ceiling_support_readings(text, report, schedules=None):
    """Read isolated ceiling probes using their actual parent model Z schedule."""
    schedules = schedules if schedules is not None else object_schedule_readings(text, report)
    schedule_map = {row["id"]: row["emitted_model_layers"] for row in schedules}
    targets = []
    for obj in report["print_objects"]:
        shift = np.asarray(obj.get("native_probe_to_plate_mm",obj["manufacturing_to_plate_mm"]))[:3, 3]
        probes = list(obj.get("native_review", {}).get("ceiling_probes", []))
        for volume in obj["volumes"]:
            if volume["subtype"] == "normal_part":
                probes.extend(volume.get("native_review", {}).get("ceiling_probes", []))
                probes.extend(volume["source_part"].get("native_review", {}).get("ceiling_probes", []))
        for probe in probes:
            window = np.asarray(probe["window_xy_mm"], dtype=float)+shift[:2]
            if window.shape != (2, 2) or np.any(window[1] <= window[0]):
                raise ValueError(f"{obj['id']}: ceiling probes need increasing common-frame XY bounds")
            targets.append(dict(obj=obj, probe=probe, window=window,
                ceiling=float(probe["nominal_ceiling_z_mm"])+shift[2], supports=set(), roofs=set()))
    for deposit in native_deposits(text, report.get("deposition_xy_transform_mm")):
        for target in targets:
            low, high = target["window"]
            if not any(clipped_segment(a, b, low, high) is not None for a, b in
                       zip(deposit["points"], deposit["points"][1:])):
                continue
            z = deposit["model_z_mm"]
            if deposit["feature"].startswith("Support") and z < target["ceiling"]:
                target["supports"].add(z)
            elif (deposit["identify_id"] == target["obj"]["identify_id"] and z >= target["ceiling"]
                  and deposit["feature"] in {"Bottom surface", "Bridge", "Internal solid infill"}):
                target["roofs"].add((z, deposit["strand_height_mm"], deposit["feature"]))
    readings = []
    for target in targets:
        obj, probe = target["obj"], target["probe"]
        roof_z = min((value[0] for value in target["roofs"]), default=None)
        step = next((row["nominal_model_z_step_mm"] for row in schedule_map[obj["id"]]
                     if abs(row["model_nozzle_z_mm"]-roof_z) < 1e-6), None) if roof_z is not None else None
        underside = roof_z-step if roof_z is not None and step is not None else None
        support_top = max(target["supports"], default=None)
        readings.append(dict(id=obj["id"], name=probe.get("name", "flat ceiling"),
            nominal_cad_ceiling_z_mm=probe["nominal_ceiling_z_mm"],
            sampled_window_xy_mm=probe["window_xy_mm"], requested_support_top_gap_mm=probe.get("requested_support_top_gap_mm"),
            highest_support_nozzle_z_mm=support_top, first_ceiling_model_nozzle_z_mm=roof_z,
            nominal_model_layer_height_mm=step, nominal_first_roof_underside_mm=round(underside, 5) if underside is not None else None,
            first_ceiling_strand_flow_heights_mm=sorted({h for z, h, _ in target["roofs"] if z == roof_z and h is not None}),
            first_ceiling_features=sorted({f for z, _, f in target["roofs"] if z == roof_z}),
            commanded_nominal_roof_separation_mm=round(underside-support_top, 5) if underside is not None and support_top is not None else None,
            support_layer_tops_below_ceiling_mm=sorted(target["supports"]),
            scope="Highest support nozzle Z in the isolated interior window to first roof underside from its actual parent Z step. Bridge flow height, sag, bead shape and physical release are separate."))
    return readings


def native_deposits(text, xy_transform_mm=None):
    """Yield positive native XY deposits, preserving model Z and strand flow.

    Model Z comes from the native layer comment; explicit Z ramps are retained
    separately. Arc moves are subdivided by the existing native-path reader.
    """
    from enclosure_support_audit import _WORD, _arc_points

    x = y = e = 0.
    nozzle_z = None
    current = None
    layer_z = height = width = feed = None
    physical_tool = selected_filament_code = None
    feature = ""
    absolute_xy, relative_e = True, True
    for line_number, raw in enumerate(text.splitlines(), 1):
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
        if re.fullmatch(r"T\d+", command):
            physical_tool = int(command[1:])
        elif command == "M620" and "S" in words:
            selected_filament_code = int(words["S"])
        elif command in {"G90", "G91"}:
            absolute_xy = command == "G90"
        elif command in {"M82", "M83"}:
            relative_e = command == "M83"
        elif command == "G92":
            x, y, e = words.get("X", x), words.get("Y", y), words.get("E", e)
            nozzle_z = words.get("Z", nozzle_z)
        elif command in {"G0", "G1", "G2", "G3"}:
            nx = words.get("X", x) if absolute_xy else x+words.get("X", 0.)
            ny = words.get("Y", y) if absolute_xy else y+words.get("Y", 0.)
            nz = (words.get("Z", nozzle_z) if absolute_xy else
                  nozzle_z+words.get("Z", 0.) if nozzle_z is not None else None)
            de = words.get("E", 0.) if relative_e else words.get("E", e)-e
            feed = words.get("F", feed)
            if layer_z is not None and de > 1e-9 and (nx != x or ny != y):
                points = ([(x, y), (nx, ny)] if command in {"G0", "G1"}
                          else _arc_points((x, y), (nx, ny), words, command == "G2"))
                points=transformed_xy(points,xy_transform_mm)
                yield dict(identify_id=current, model_z_mm=layer_z, strand_height_mm=height,
                           gcode_line_1based=line_number,
                           strand_width_mm=width, feature=feature,
                           native_filament_selector_index=physical_tool,
                           physical_tool_index=physical_tool, selected_filament_code=selected_filament_code,
                           commanded_nozzle_start_z_mm=nozzle_z, commanded_nozzle_end_z_mm=nz,
                           feed_mm_s=feed/60 if feed is not None else None,
                           explicit_z_move="Z" in words, points=points)
            x, y, nozzle_z = nx, ny, nz
            if "E" in words:
                e = e+words["E"] if relative_e else words["E"]


def transformed_xy(points,matrix=None):
    value=np.asarray(points)
    if matrix is None:return value
    matrix=np.asarray(matrix,float)
    return value@matrix[:,:2].T+matrix[:,2]


def native_material_frames(text):
    """Read filament selectors and the source nozzle-coordinate compensation.

    H2C Tn selects a filament, rather than directly naming a physical nozzle.
    Bambu's point_to_gcode subtracts the selected extruder offset from model XY;
    adding that offset restores model coordinates for a registered-glyph view.
    """
    def values(key):
        match=re.search(rf'^; {key} = (.+)$',text,re.M)
        return match.group(1).split(',') if match else []
    mapping=[int(v) for v in values('filament_map')]
    offsets=[[float(v) for v in pair.split('x')] for pair in values('extruder_offset')]
    physical=[int(v) for v in values('physical_extruder_map')]
    rows=[]
    for index,extruder in enumerate(mapping):
        rows.append(dict(filament_slot=index+1,native_T_selector_index=index,
            native_extruder_id_one_based=extruder,
            physical_extruder_map_id=physical[extruder-1] if extruder<=len(physical) else None,
            offset_to_add_to_Gcode_XY_for_model_frame_mm=offsets[extruder-1] if extruder<=len(offsets) else None))
    return dict(filament_map=mapping,physical_extruder_map=physical,extruder_offset_mm=offsets,
        material_slots=rows,
        scope='Native Tn is a filament selector. The emitted filament_map chooses its extruder; model XY equals G-code XY plus that extruder offset. This is source coordinate compensation, not observed physical registration.')

def native_pause_reading(text, report):
    """Locate source insertion pauses before the sampled sealed-cover deposits."""
    markers = [index for index, line in enumerate(text.splitlines(), 1)
               if re.match(r"^\s*M400\s+U1(?:\s|;|$)", line)]
    targets = []
    for obj in report["print_objects"]:
        shift = np.asarray(obj.get("native_probe_to_plate_mm",obj["manufacturing_to_plate_mm"]))[:3, 3]
        for pause in obj.get("pauses", []):
            targets.append(dict(object_id=obj["id"], identify_id=obj["identify_id"],
                pause=pause, bounds=np.asarray(pause["cover_probe_bounds_mm"])+shift,
                first_cover=None))
    for deposit in native_deposits(text, report.get("deposition_xy_transform_mm")):
        if not is_model_deposit(deposit) or deposit["feature"] not in {"Bridge", "Bottom surface", "Internal solid infill"}:
            continue
        for target in targets:
            if (target["first_cover"] is None and deposit["identify_id"] == target["identify_id"]
                    and intersects_native_window(deposit, target["bounds"])):
                target["first_cover"] = dict(line_1based=deposit["gcode_line_1based"],
                    nominal_model_z_mm=deposit["model_z_mm"], feature=deposit["feature"])
    rows = []
    for target in targets:
        first = target["first_cover"]
        preceding = [line for line in markers if first and line < first["line_1based"]]
        rows.append(dict(id=target["object_id"], requested=target["pause"],
            emitted_pause_lines_1based=markers, first_sampled_cover_deposit=first,
            pause_precedes_first_sampled_cover_deposit=bool(preceding)))
    return dict(readings=rows, scope="Actual M400 U1 command and positive model paths in the supplied sealed-cover window. This establishes command order; physical insertion, polarity, fit, magnetic force and sealing remain unmeasured.")


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
    for deposit in native_deposits(text, report.get("deposition_xy_transform_mm")):
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
                        points = transformed_xy(points,report.get("deposition_xy_transform_mm"))
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
    for deposit in native_deposits(text, report.get("deposition_xy_transform_mm")):
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
    for deposit in native_deposits(text, report.get("deposition_xy_transform_mm")):
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
        nominal_height = float(specimen.get("requested_layer_height_mm", nominal_height))
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
            elif axis == "y":
                outward = int(label.get("outward_sign", 1))
                if outward not in {-1, 1}:
                    raise ValueError(f"{specimen['id']}: side lettering needs outward_sign -1 or +1")
                surface = float(label["surface_y_mm"])+shift[1]
                if outward > 0:
                    bounds[0, 1] = max(bounds[0, 1], surface+1e-6)
                else:
                    bounds[1, 1] = min(bounds[1, 1], surface-1e-6)
                bounds[0, 2] -= nominal_height
                bounds[1, 2] += nominal_height
                projected = (0, 2)
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
                points = [np.array((px, py, layer_z)) for px, py in transformed_xy(points,report.get("deposition_xy_transform_mm"))]
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
