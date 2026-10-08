"""Complete local roof-stock witnesses in the current saved faucet bases.

Fresh mesh lint identifies the named roofs. Native selection includes every
downward plane at the donor shoulder, the Industrial lever roof and all socket
annuli. This neither builds product geometry nor establishes global strength.
"""
from __future__ import annotations

import argparse
import ast
from datetime import datetime, timezone
import hashlib
import json
import operator
import os
from pathlib import Path
import re
import sys

import cadquery as cq
from OCP.BRepAlgoAPI import BRepAlgoAPI_Common, BRepAlgoAPI_Cut, BRepAlgoAPI_Fuse
from OCP.TopTools import TopTools_ListOfShape

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
sys.path.insert(0, str(ROOT / "hardware/scripts"))
from _run_lock import acquire
SHELL = "hardware/printed-parts/faucet/faucet-shell/faucet_shell.py"
PARTS = {
    "sculpted": (
        "hardware/printed-parts/faucet/faucet-shell/faucet-shell-base", SHELL),
    "industrial": (
        "hardware/printed-parts/faucet/industrial/industrial-shell-base",
        "hardware/printed-parts/faucet/industrial/industrial_faucet.py"),
}
NATIVE_TOLERANCE_MM = 1e-6
MISSING_VOLUME_TOLERANCE_MM3 = 1e-7
# Mesh plane groups use geometry_lint.py's 0.02 mm offset grouping. This
# locates a feature; actual finite native membership uses the smaller limit.
LINT_LOCATOR_TOLERANCE_MM = 0.02
NUMBER = r"([-+]?\d+(?:\.\d+)?)"


def sha(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def volume(shape: cq.Shape) -> float:
    return sum(s.Volume() for s in shape.Solids())


def native_set_operation(kind, left, right):
    """Functional, copied, non-destructive native sets at zero fuzzy tolerance."""
    arguments, tools = TopTools_ListOfShape(), TopTools_ListOfShape()
    arguments.Append(left.copy().wrapped)
    tools.Append(right.copy().wrapped)
    operation = kind()
    operation.SetArguments(arguments)
    operation.SetTools(tools)
    operation.SetNonDestructive(True)
    operation.SetFuzzyValue(0.0)
    operation.Build()
    if not operation.IsDone():
        raise ValueError("Native stock set operation did not complete")
    return cq.Shape.cast(operation.Shape())


def set_record(shape):
    return {"valid": shape.isValid(), "volume_mm3": volume(shape),
            "solid_count": len(shape.Solids()),
            "solid_volumes_nonnegative": all(s.Volume() >= 0 for s in shape.Solids())}


def valid_missing(shape):
    record = set_record(shape)
    return (record["valid"] and record["solid_volumes_nonnegative"]
            and 0 <= record["volume_mm3"] < MISSING_VOLUME_TOLERANCE_MM3)


def exact_partition_stock(shape, face, complete_witness):
    """Alternative exact-set proof when the complete default Boolean is invalid.

    Native intersections partition the entire finite face, retaining its outer
    and inner boundaries. These are complete prisms, not point samples or a
    replacement wall thickness. Every accepted set must be valid, conserve the
    complete volume, and pass both coverage directions. The original operation
    is separately retained by the caller, including invalidity.
    """
    b, tolerance = face.BoundingBox(), MISSING_VOLUME_TOLERANCE_MM3
    # The native plane owns Z; a tolerance-expanded bounding box does not.
    plane_z = face.Center().z
    direction = face.normalAt().multiply(-2.0)
    cells, prisms, commons, area_sum = [], [], [], 0.0
    for ix in range(4):
        for iy in range(2):
            x0, x1 = (b.xmin+(b.xmax-b.xmin)*i/4 for i in (ix, ix+1))
            y0, y1 = (b.ymin+(b.ymax-b.ymin)*i/2 for i in (iy, iy+1))
            wire = cq.Wire.makePolygon([cq.Vector(x0, y0, plane_z),
                cq.Vector(x1, y0, plane_z), cq.Vector(x1, y1, plane_z),
                cq.Vector(x0, y1, plane_z), cq.Vector(x0, y0, plane_z)])
            finite = native_set_operation(BRepAlgoAPI_Common, face,
                                          cq.Face.makeFromWires(wire))
            if not finite.isValid():
                raise ValueError("Invalid native finite-face partition")
            for component in finite.Faces():
                if component.Area() <= 1e-9:
                    continue
                prism = cq.Solid.extrudeLinear(component.outerWire(),
                    component.innerWires(), direction)
                prism_volume = volume(prism)
                if (not prism.isValid() or prism_volume <= 0
                        or abs(prism_volume-2*component.Area()) >= tolerance):
                    raise ValueError("Finite partition is not a positive valid exact2mm prism")
                common = native_set_operation(BRepAlgoAPI_Common, prism, shape)
                direct = native_set_operation(BRepAlgoAPI_Cut, prism, shape)
                without_common = native_set_operation(BRepAlgoAPI_Cut, prism, common)
                outside_prism = native_set_operation(BRepAlgoAPI_Cut, common, prism)
                outside_saved = native_set_operation(BRepAlgoAPI_Cut, common, shape)
                common_volume = volume(common)
                consistency = (common.isValid() and common_volume > 0
                    and set_record(common)["solid_volumes_nonnegative"]
                    and common_volume <= prism_volume+tolerance
                    and abs(common_volume-prism_volume) < tolerance
                    and valid_missing(without_common) and valid_missing(outside_prism)
                    and valid_missing(outside_saved))
                cells.append({"grid": [ix, iy], "finite_face_area_mm2": component.Area(),
                    "finite_inner_wire_count": len(component.innerWires()),
                    "exact_2mm_prism": set_record(prism),
                    "original_partition_cut": set_record(direct),
                    "common_with_saved_stock": set_record(common),
                    "prism_minus_common": set_record(without_common),
                    "common_minus_prism": set_record(outside_prism),
                    "common_minus_saved": set_record(outside_saved),
                    "complete_valid_set_consistency": consistency})
                area_sum += component.Area()
                prisms.append(prism)
                commons.append(common)
    if not prisms:
        raise ValueError("No positive exact finite-face partitions")

    def union(items):
        joined = items[0].copy()
        for item in items[1:]:
            joined = native_set_operation(BRepAlgoAPI_Fuse, joined, item)
        return joined

    joined = union(prisms)
    material = union(commons)
    missed_partition = native_set_operation(BRepAlgoAPI_Cut, complete_witness, joined)
    excess_partition = native_set_operation(BRepAlgoAPI_Cut, joined, complete_witness)
    complete_missing = native_set_operation(BRepAlgoAPI_Cut, complete_witness, material)
    excess_material = native_set_operation(BRepAlgoAPI_Cut, material, complete_witness)
    outside_saved = native_set_operation(BRepAlgoAPI_Cut, material, shape)
    witness_volume = volume(complete_witness)
    coverage = (joined.isValid() and volume(joined) > 0
        and set_record(joined)["solid_volumes_nonnegative"]
        and abs(area_sum-face.Area()) < tolerance
        and abs(sum(volume(p) for p in prisms)-volume(joined)) < tolerance
        and abs(volume(joined)-witness_volume) < tolerance
        and valid_missing(missed_partition) and valid_missing(excess_partition))
    material_consistency = (material.isValid() and volume(material) > 0
        and set_record(material)["solid_volumes_nonnegative"]
        and abs(volume(material)-witness_volume) < tolerance
        and abs(sum(volume(c) for c in commons)-volume(material)) < tolerance
        and valid_missing(complete_missing) and valid_missing(excess_material)
        and valid_missing(outside_saved))
    passed = coverage and material_consistency and all(
        row["complete_valid_set_consistency"] for row in cells)
    return {"method": "exact finite-face partitions and valid common/cut set consistency",
        "fuzzy_tolerance_mm": 0.0, "non_destructive_copied_operations": True,
        "complete_witness_volume_mm3": witness_volume,
        "complete_partition_area_sum_mm2": area_sum, "partitions": cells,
        "partition_union": set_record(joined), "material_union": set_record(material),
        "witness_minus_partition_union": set_record(missed_partition),
        "partition_union_minus_witness": set_record(excess_partition),
        "witness_minus_material_union": set_record(complete_missing),
        "material_union_minus_witness": set_record(excess_material),
        "material_union_minus_saved": set_record(outside_saved),
        "complete_exact_partition_coverage_pass": coverage,
        "complete_valid_material_set_consistency_pass": material_consistency,
        "missing_witness_volume_mm3": volume(complete_missing), "pass": passed}


def source_scalar(path: Path, name: str) -> float:
    """Resolve the small numeric profile expressions without executing CAD."""
    definitions = {
        target.id: node.value
        for node in ast.parse(path.read_text()).body if isinstance(node, ast.Assign)
        for target in node.targets if isinstance(target, ast.Name)
    }
    operations = {ast.Add: operator.add, ast.Sub: operator.sub,
                  ast.Mult: operator.mul, ast.Div: operator.truediv}

    def resolve(node):
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
            return float(node.value)
        if isinstance(node, ast.Name):
            return resolve(definitions[node.id])
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub):
            return -resolve(node.operand)
        if isinstance(node, ast.BinOp) and type(node.op) in operations:
            return operations[type(node.op)](resolve(node.left), resolve(node.right))
        raise ValueError(f"Unsupported numeric profile expression for {name}")

    return resolve(definitions[name])


def lint_rows(text: str) -> list[dict]:
    rows = []
    for match in re.finditer(r"(?ms)^\s*\[(\w+)( · answered)?\].*?(?=^\s*\[|\Z)", text):
        block = match.group(0)
        pick = re.search(rf"click: x={NUMBER} y={NUMBER} z={NUMBER}", block)
        if pick is None:
            raise ValueError("Lint finding lacks its printed locator")
        normal = re.search(rf"face: plane · n x={NUMBER} y={NUMBER} z={NUMBER}", block)
        rows.append({"class": match.group(1), "answered": bool(match.group(2)),
                     "pick_mm": [float(v) for v in pick.groups()],
                     "normal": [float(v) for v in normal.groups()] if normal else None})
    return rows


def fresh_lint(path: Path, bindings: dict) -> dict[str, list[dict]]:
    receipt = json.loads(path.read_text())
    if receipt["phase"] != "lint" or receipt["inputs_unchanged_during_phase"] is not True:
        raise ValueError("Require an executed fresh immutable-input lint receipt")
    bindings[str(path.resolve().relative_to(ROOT))] = sha(path)
    # The receipt embeds complete logs. Its original answer text is execution
    # provenance, not a promise that later corrected answers are unchanged.
    for rel, expected in receipt["source_and_artifact_sha256"].items():
        if sha(ROOT / rel) != expected:
            raise ValueError(f"Fresh lint no longer binds current geometry/source: {rel}")
        bindings[rel] = expected
    result = {}
    for command in receipt["commands"]:
        text = command["raw_log_text"]
        if (command["return_code"] != 0 or "lint pass failed:" in text
                or hashlib.sha256(text.encode()).hexdigest() != command["log_sha256"]):
            raise ValueError("Fresh lint execution/log failed its receipt")
        result[command["command"][2]] = lint_rows(text)
    return result


def finite_point(face: cq.Face) -> tuple[tuple, float]:
    """Choose a positive-area native triangle centroid and verify membership."""
    vertices, triangles = face.tessellate(0.05)
    candidates = []
    for triangle in triangles:
        a, b, c = (vertices[index] for index in triangle)
        area = (b-a).cross(c-a).Length / 2
        if area <= 1e-9:
            continue
        point = (a+b+c).multiply(1/3)
        distance = face.distance(cq.Vertex.makeVertex(*point.toTuple()))
        if distance <= NATIVE_TOLERANCE_MM:
            candidates.append((area, point.toTuple(), distance))
    if not candidates:
        raise ValueError("No positive native interior triangle on the selected face")
    _, point, distance = max(candidates)
    return point, distance


def face_record(index: int, face: cq.Face) -> dict:
    b = face.BoundingBox()
    return {"saved_step_face_index": index, "face_area_mm2": face.Area(),
            "face_normal": list(face.normalAt().toTuple()),
            "face_bbox_mm": [b.xmin, b.ymin, b.zmin, b.xmax, b.ymax, b.zmax],
            "inner_wire_count": len(face.innerWires())}


def locator_matches(face: cq.Face, row: dict) -> bool:
    normal = cq.Vector(*row["normal"]).normalized()
    point = cq.Vector(*row["pick_mm"])
    b, tol = face.BoundingBox(), LINT_LOCATOR_TOLERANCE_MM
    return (face.normalAt().dot(normal) > 0.999999
            and abs((point-face.Center()).dot(face.normalAt())) <= tol
            and b.xmin-tol <= point.x <= b.xmax+tol
            and b.ymin-tol <= point.y <= b.ymax+tol)


def roof_stock(shape, index, face, feature, lint_row):
    point, membership_distance = finite_point(face)
    witness = cq.Solid.extrudeLinear(
        face.outerWire(), face.innerWires(), face.normalAt().multiply(-2.0))
    missing = native_set_operation(BRepAlgoAPI_Cut, witness, shape)
    common = native_set_operation(BRepAlgoAPI_Common, witness, shape)
    witness_volume = volume(witness)
    missing_volume = volume(missing)
    original_cut, original_common = set_record(missing), set_record(common)
    original_consistency = (missing.isValid() and common.isValid()
        and original_cut["solid_volumes_nonnegative"]
        and original_common["solid_volumes_nonnegative"]
        and 0 <= missing_volume <= witness_volume+MISSING_VOLUME_TOLERANCE_MM3
        and 0 < volume(common) <= witness_volume+MISSING_VOLUME_TOLERANCE_MM3
        and abs(missing_volume+volume(common)-witness_volume) < MISSING_VOLUME_TOLERANCE_MM3)
    positive = face.Area() > 1e-9 and witness_volume > 1e-9
    area_volume_agrees = abs(witness_volume-2*face.Area()) < MISSING_VOLUME_TOLERANCE_MM3
    alternative = None
    if (not original_consistency and face.isValid() and witness.isValid()
            and positive and area_volume_agrees):
        try:
            alternative = exact_partition_stock(shape, face, witness)
        except Exception as error:
            alternative = {"pass": False, "error": f"{type(error).__name__}: {error}"}
    alternative_pass = bool(alternative and alternative["pass"])
    accepted_method = ("complete copied non-destructive cut/common consistency"
        if original_consistency else "exact finite-partition set proof"
        if alternative_pass else "no valid complete stock proof")
    if alternative_pass:
        missing_volume = alternative["missing_witness_volume_mm3"]
    valid = face.isValid() and witness.isValid() and (original_consistency or alternative_pass)
    locator = lint_row["pick_mm"] if lint_row else None
    return {"class": "ceiling", "feature": feature,
            "roof_id": f"face-{index}", **face_record(index, face),
            "actual_face_point_mm": list(point),
            "actual_point_distance_to_finite_native_face_mm": membership_distance,
            "native_membership_tolerance_mm": NATIVE_TOLERANCE_MM,
            "lint_plane_pick_mm": locator,
            "lint_pick_distance_to_actual_face_mm": (
                face.distance(cq.Vertex.makeVertex(*locator)) if locator else None),
            "lint_locator_tolerance_mm": LINT_LOCATOR_TOLERANCE_MM,
            "current_lint_finding_present": lint_row is not None,
            "lint_support_witness_required": bool(lint_row and (
                feature.startswith(("donor shoulder", "donor lever corridor", "rear lever")))),
            "required_inward_stock_mm": 2.0,
            "complete_witness_volume_mm3": witness_volume,
            "complete_area_times_2mm_agrees": area_volume_agrees,
            "original_complete_default_cut": original_cut,
            "original_complete_common": original_common,
            "original_complete_cut_common_consistency_pass": original_consistency,
            "finite_partition_alternative": alternative,
            "complete_stock_proof_method": accepted_method,
            "missing_witness_volume_mm3": missing_volume,
            "witness_and_boolean_valid": valid,
            "face_and_witness_positive": positive,
            "pass": (valid and positive and area_volume_agrees
                     and membership_distance <= NATIVE_TOLERANCE_MM
                     and missing_volume < MISSING_VOLUME_TOLERANCE_MM3),
            "print_pose_degrees_about_x": -15.0,
            "scope": "Complete finite native face with every inner wire and exactly 2 mm inward stock. Original cut/common invalidity remains explicit; an alternative needs complete exact partition coverage and valid native set consistency. Rounded mesh locators are separate from actual native membership. Native toolpaths supply separate support presence; no physical cleanup, contact, strength or lifetime result."}


def main():
    acquire(str(Path(__file__).resolve()))
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=HERE / "base-native-lint-witnesses.json")
    parser.add_argument("--lint-receipt", type=Path, default=HERE / "roof-correction-fresh-lint-execution.json")
    args = parser.parse_args()
    bindings = {str(Path(__file__).resolve().relative_to(ROOT)): sha(Path(__file__).resolve()),
                SHELL: sha(ROOT / SHELL)}
    lint = fresh_lint(args.lint_receipt, bindings)
    levels = {"donor": source_scalar(ROOT / SHELL, "zone2_z_top"),
              "corridor": source_scalar(ROOT / SHELL, "lever_rest_top_z"),
              "lever": source_scalar(ROOT / SHELL, "zone4_z_top"),
              "socket": source_scalar(ROOT / SHELL, "base_insert_bottom_z")}
    parts = []
    for style, (stem, source) in PARTS.items():
        for rel in (stem+".step", stem+".stl", source):
            bindings[rel] = sha(ROOT / rel)
        findings = lint[stem+".stl"]
        material = [row for row in findings if row["class"] in ("step", "sliver")]
        if material:
            raise ValueError(f"Current {style} material finding needs its own finite-face review")
        ceilings = [row for row in findings if row["class"] == "ceiling"]
        shape = cq.importers.importStep(str(ROOT / (stem+".step"))).val()
        valid = shape.isValid() and len(shape.Solids()) == 1 and volume(shape) > 0
        if not valid:
            raise ValueError(f"Saved {style} base is not one valid positive solid")
        roofs, matches, counts = [], set(), {"donor": 0, "corridor": 0, "lever": 0, "socket": 0}
        for index, face in enumerate(shape.Faces()):
            if (face.geomType() != "PLANE"
                    or face.normalAt().dot(cq.Vector(0, 0, -1)) < 0.999999):
                continue
            b = face.BoundingBox()
            kind = next((k for k, z in levels.items() if abs(b.zmin-z) <= NATIVE_TOLERANCE_MM
                         and abs(b.zmax-z) <= NATIVE_TOLERANCE_MM), None)
            if kind is None or (kind == "lever" and style != "industrial"):
                continue
            paired = [(i, row) for i, row in enumerate(ceilings) if locator_matches(face, row)]
            if len(paired) > 1:
                raise ValueError(f"Ambiguous lint locator for {style}/face-{index}")
            row = paired[0][1] if paired else None
            if paired:
                if paired[0][0] in matches:
                    raise ValueError("One rounded lint locator matched multiple finite native faces")
                matches.add(paired[0][0])
            if kind == "donor":
                side = (("left" if row["pick_mm"][0] < 0 else "right") if row
                        else f"unflagged native plane face-{index}")
                feature = f"donor shoulder Z{levels['donor']:g} {side}"
            elif kind == "corridor":
                feature = f"donor lever corridor roof Z{levels['corridor']:g}"
            elif kind == "lever":
                feature = f"rear lever roof Z{levels['lever']:g}"
            else:
                feature = "registration socket roof"
                if len(face.innerWires()) != 1:
                    raise ValueError("The registration roof must retain its pilot inner wire")
            counts[kind] += 1
            roofs.append(roof_stock(shape, index, face, feature, row))
        if (counts["donor"] < 1 or counts["socket"] != 3
                or counts["lever"] != int(style == "industrial")
                or (style == "sculpted" and counts["corridor"] < 1)):
            raise ValueError(f"Unexpected actual native roof set: {style}/{counts}")
        if len(matches) != len(ceilings):
            raise ValueError(f"A current {style} ceiling lacks an unambiguous native face")
        parts.append({"part": style, "saved_step": stem+".step", "saved_stl": stem+".stl",
                      "native_shape_valid_one_positive_solid": valid,
                      "native_volume_mm3": volume(shape), "selected_native_roof_counts": counts,
                      "current_material_finding_count": 0, "absent_lint_classes": ["step", "sliver"],
                      "material_witnesses": [], "ceiling_faces": roofs})
    for rel, expected in bindings.items():
        if sha(ROOT / rel) != expected:
            raise ValueError(f"Input changed during native review: {rel}")
    report = {"schema": 2, "checked_at_utc": datetime.now(timezone.utc).isoformat(),
              "scope": "Current saved-base finite roof geometry only; no global wall guarantee, deposited print, mechanical capacity or lifetime result.",
              "method": "Resolve every donor/lever-corridor/socket elevation from the current source without executing it, plus the Industrial lever roof. Select all actual downward native planes at those elevations and match every current ceiling locator separately. Extrude complete outer and every inner wire exactly 2 mm inward; require positive valid volume and native cut/common consistency with missing volume below 1e-7 mm3. An invalid original operation can only use the separately reported exact finite-partition proof with complete bidirectional coverage and valid set consistency; it cannot pass from sampled rays or numerical validity alone.",
              "source_and_artifact_sha256": bindings, "resolved_roof_elevations_mm": levels,
              "current_material_finding_count": 0,
              "material_finding_scope": "Fresh executed lint has no step or sliver finding. No backing measurement is asserted for absent findings.",
              "all_named_backing_witnesses_pass": True,
              "all_named_ceiling_stock_witnesses_pass": all(r["pass"] for p in parts for r in p["ceiling_faces"]),
              "complete_native_roof_witness_count": sum(len(p["ceiling_faces"]) for p in parts),
              "source_based_roof_selection_complete": True,
              "parts": parts}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2)+"\n")
    print(json.dumps({"output": str(args.output), "current_material_finding_count": 0,
                      "complete_native_roof_witness_count": report["complete_native_roof_witness_count"],
                      "all_named_ceiling_stock_witnesses_pass": report["all_named_ceiling_stock_witnesses_pass"],
                      "failed_faces": [{"part": p["part"], "feature": r["feature"],
                                        "face_index": r["saved_step_face_index"], "missing_mm3": r["missing_witness_volume_mm3"]}
                                       for p in parts for r in p["ceiling_faces"] if not r["pass"]]}))
    if not report["all_named_ceiling_stock_witnesses_pass"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
