"""Distinct actual native support-path witnesses beneath the named roof faces.

Finite-face projections establish local support presence only. The retained
native audit preserves body/root counts; neither proves complete contact,
physical support removal, deposited finish or mechanical capacity.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import sys
import tempfile
import zipfile

import cadquery as cq
import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
sys.path.insert(0, str(HERE.parent))
from prepare_display_print import extrusion_segments

NATIVE_MEMBERSHIP_TOLERANCE_MM = 1e-6
GAP_WINDOW_MM = (0.15, 0.85)
DISTINCT_POINT_TOLERANCE_MM = 1e-4


def sha(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024*1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def validate_bindings(inputs):
    for rel, expected in inputs.items():
        if sha(ROOT / rel) != expected:
            raise ValueError(f"Current native input binding mismatch: {rel}")


def reviewed_tuple(receipt, stem, inputs):
    rows = [row for row in receipt["records"] if row["project"]["path"] == stem+".3mf"]
    if len(rows) != 1 or receipt.get("passed") is not True:
        raise ValueError("Require the exact passed current rigid native review tuple")
    row = rows[0]
    for key in ("project", "print", "native_validation", "support_audit", "native_archive", "gcode"):
        record = row[key]
        inputs[record["path"]] = record["sha256"]
    inputs.update(row["source_sha256"])
    for review in row["reviews"].values():
        inputs[review["record"]["path"]] = review["record"]["sha256"]
        for image in review["images"]:
            inputs[image["path"]] = image["sha256"]
    validate_bindings(inputs)
    return row


def inside_roof_window(point, roof):
    b = roof["face_bbox_mm"]
    gap = roof["actual_face_point_mm"][2] - point[2]
    return b[0] <= point[0] <= b[3] and b[1] <= point[1] <= b[4] and GAP_WINDOW_MM[0] < gap < GAP_WINDOW_MM[1]


def native_samples(points, face, roof):
    zfloor = roof["actual_face_point_mm"][2]
    unique = {}
    for point in points:
        if not inside_roof_window(point["cad_mm"], roof):
            continue
        projected = [float(point["cad_mm"][0]), float(point["cad_mm"][1]), zfloor]
        distance = face.distance(cq.Vertex.makeVertex(*projected))
        if distance > NATIVE_MEMBERSHIP_TOLERANCE_MM:
            continue
        key = tuple(round(float(x), 8) for x in point["cad_mm"])
        unique.setdefault(key, {
            "native_extrusion_segment_ordinal": point["ordinal"],
            "support_centerline_midpoint_cad_mm": [float(x) for x in point["cad_mm"]],
            "projected_roof_point_cad_mm": projected,
            "projection_distance_to_native_face_mm": distance,
            "vertical_centreline_gap_mm": zfloor-float(point["cad_mm"][2]),
            "feature": point["feature"], "line_width_mm": point["width"],
            "native_plate_layer_z_mm": point["plate_z_mm"]})
    candidates = list(unique.values())
    if len(candidates) < 3:
        raise ValueError(f"Fewer than three distinct finite-face native support midpoints: {roof['feature']}")
    anchor = np.array(roof["actual_face_point_mm"][:2])
    first = min(candidates, key=lambda p: np.linalg.norm(np.array(p["projected_roof_point_cad_mm"][:2])-anchor))
    selected = [first]
    while len(selected) < 3:
        eligible = [
            p for p in candidates
            if all(np.linalg.norm(np.array(p["support_centerline_midpoint_cad_mm"])-
                                  np.array(s["support_centerline_midpoint_cad_mm"])) > DISTINCT_POINT_TOLERANCE_MM
                   for s in selected)]
        if not eligible:
            raise ValueError("Native support candidates collapse to fewer than three distinct points")
        chosen = max(eligible, key=lambda p: min(
            np.linalg.norm(np.array(p["projected_roof_point_cad_mm"][:2])-
                           np.array(s["projected_roof_point_cad_mm"][:2])) for s in selected))
        selected.append(chosen)
    if len({p["native_extrusion_segment_ordinal"] for p in selected}) != 3:
        raise ValueError("Support witnesses repeat an actual extrusion segment")
    return selected, len(candidates)


def audit_contexts(audit, face, roof):
    """Intersect current interface projection rectangles with the finite roof.

    Audit boxes describe a roof region; paths are independently proven on the
    finite face and are not asserted to inherit raster interface/tree labels.
    """
    zfloor = roof["actual_face_point_mm"][2]
    b = roof["face_bbox_mm"]
    contexts = []
    trees = {tree["id"]: tree for tree in audit["trees"]}
    for interface in audit["interfaces"]:
        box = interface["bbox_cad_xyz_mm"]
        if (box[5] < zfloor-GAP_WINDOW_MM[1] or box[2] > zfloor-GAP_WINDOW_MM[0]
                or box[0] >= b[3] or box[3] <= b[0] or box[1] >= b[4] or box[4] <= b[1]):
            continue
        corners = [(box[0], box[1], zfloor), (box[3], box[1], zfloor),
                   (box[3], box[4], zfloor), (box[0], box[4], zfloor)]
        wire = cq.Wire.makePolygon([cq.Vector(*p) for p in corners], close=True)
        rectangle = cq.Face.makeFromWires(wire)
        common = face.intersect(rectangle)
        if not common.isValid():
            raise ValueError("Invalid native roof/audit context intersection")
        area = sum(f.Area() for f in common.Faces())
        if area <= 1e-8:
            continue
        contexts.append({
            "current_interface_from_audit": interface,
            "current_tree_from_audit": trees[interface["tree"]],
            "projected_audit_region_overlap_with_finite_roof_mm2": area,
            "native_context_intersection_valid": True,
            "scope": "Geometric audit region context; sampled actual support paths are not assigned these interface or tree labels."})
    # The audit groups interface-labelled roads into raster regions. A roof
    # may have actual Support roads below it without an interface-labelled
    # region there. Exact distinct finite-face paths are the required witness;
    # keep the independent context empty when that is what the audit holds.
    return contexts


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=HERE/"lint-support-witnesses.json")
    parser.add_argument("--native-review-receipt", type=Path, default=HERE/"native-print-review-evidence.json")
    args = parser.parse_args()
    inputs = {
        str(Path(__file__).resolve().relative_to(ROOT)): sha(Path(__file__)),
        "hardware/printed-parts/faucet/prepare_display_print.py": sha(HERE.parent/"prepare_display_print.py")}
    proof_path = HERE/"base-native-lint-witnesses.json"
    proof = json.loads(proof_path.read_text())
    if (proof.get("all_named_ceiling_stock_witnesses_pass") is not True
            or proof.get("source_based_roof_selection_complete") is not True
            or proof.get("complete_native_roof_witness_count") != sum(
                len(p["ceiling_faces"]) for p in proof["parts"])):
        raise ValueError("Require passed complete current native roof stock")
    inputs.update(proof["source_and_artifact_sha256"])
    inputs[str(proof_path.relative_to(ROOT))] = sha(proof_path)
    receipt = json.loads(args.native_review_receipt.read_text())
    inputs[str(args.native_review_receipt.resolve().relative_to(ROOT))] = sha(args.native_review_receipt)
    outputs = []
    for style, stem, piece in (
        ("sculpted", "hardware/printed-parts/faucet/faucet-petgf", "faucet-shell-base"),
        ("industrial", "hardware/printed-parts/faucet/industrial/faucet-industrial-petgf", "industrial-shell-base")):
        reviewed = reviewed_tuple(receipt, stem, inputs)
        reports = {}
        for suffix in (".print.json", ".support-audit.json", ".native-validation.json"):
            path = ROOT/(stem+suffix)
            inputs[str(path.relative_to(ROOT))] = sha(path)
            reports[suffix] = json.loads(path.read_text())
        audit = next(p for p in reports[".support-audit.json"]["parts"] if p["piece"] == piece)
        manifest = next(p for p in reports[".print.json"]["parts"] if p["name"] == piece)
        native = reports[".native-validation.json"]
        archive = ROOT/native["archive"]
        if (sha(archive) != native["archive_sha256"]
                or native["archive_sha256"] != reviewed["native_archive"]["sha256"]):
            raise ValueError("Native archive binding mismatch")
        inputs[native["archive"]] = sha(archive)
        lower_record = reviewed["reviews"][".lower-supports.json"]["record"]
        lower_access = json.loads((ROOT/lower_record["path"]).read_text())["geometry_access_review"]
        if len(lower_access["reviewed_image_sha256"]) != 6:
            raise ValueError("Require all six current visual access-review images")
        validate_bindings(lower_access["reviewed_image_sha256"])
        part = next(p for p in proof["parts"] if p["part"] == style)
        roofs = [r for r in part["ceiling_faces"] if r["lint_support_witness_required"]]
        required = [r for r in part["ceiling_faces"] if r["current_lint_finding_present"]
                    and r["feature"].startswith(("donor shoulder", "donor lever corridor", "rear lever"))]
        if (not roofs or {r["roof_id"] for r in roofs} != {r["roof_id"] for r in required}
                or any(r["pass"] is not True for r in roofs)):
            raise ValueError("Every current named donor/corridor/lever finding requires its exact stock and support witnesses")
        if (audit["inputs"]["model_sha256"] != inputs[part["saved_stl"]]
                or manifest["stl_sha256"] != inputs[part["saved_stl"]]):
            raise ValueError("Native slice does not bind the current saved base")
        with zipfile.ZipFile(archive) as zipped:
            data = zipped.read("Metadata/plate_1.gcode")
        gcode_sha = hashlib.sha256(data).hexdigest()
        if (gcode_sha != native["gcode_sha256"]
                or gcode_sha != audit["inputs"]["plate_gcode_sha256"]
                or gcode_sha != reviewed["gcode"]["sha256"]):
            raise ValueError("Native G-code binding mismatch")
        rotation = np.array(manifest["build_transform"][:9]).reshape(3, 3).T
        translation = np.array(manifest["plate_translation_mm"])
        center = np.array(manifest["source_center_mm"])
        points, support_count = [], 0
        with tempfile.TemporaryDirectory(prefix="hsm-lint-support-") as tmp:
            gcode = Path(tmp)/"plate_1.gcode"
            gcode.write_bytes(data)
            for ordinal, segment in enumerate(extrusion_segments(gcode), 1):
                if segment["object"] != audit["inputs"]["object_label"] or not segment["feature"].startswith("Support"):
                    continue
                support_count += 1
                point = (np.mean([segment["a"], segment["b"]], axis=0)-translation) @ rotation + center
                if any(inside_roof_window(point, roof) for roof in roofs):
                    points.append({"cad_mm": point, "ordinal": ordinal, "feature": segment["feature"],
                                   "width": segment["width"], "plate_z_mm": segment["layer"]})
        shape = cq.importers.importStep(str(ROOT/part["saved_step"])).val()
        if not shape.isValid() or len(shape.Solids()) != 1:
            raise ValueError("Current saved base is not one valid native solid")
        roof_rows = []
        for roof in roofs:
            face = shape.Faces()[roof["saved_step_face_index"]]
            actual = cq.Vertex.makeVertex(*roof["actual_face_point_mm"])
            if (not face.isValid() or face.distance(actual) > NATIVE_MEMBERSHIP_TOLERANCE_MM
                    or abs(face.Area()-roof["face_area_mm2"]) > 1e-7):
                raise ValueError("Current finite roof no longer matches its complete stock proof")
            samples, unique_count = native_samples(points, face, roof)
            contexts = audit_contexts(audit, face, roof)
            roof_rows.append({
                "feature": roof["feature"], "roof_id": roof["roof_id"],
                "native_roof_face_index": roof["saved_step_face_index"],
                "actual_finite_native_roof_point_mm": roof["actual_face_point_mm"],
                "finite_native_support_midpoint_candidates": unique_count,
                "three_distinct_native_extrusion_midpoints": True,
                "minimum_selected_midpoint_separation_mm": min(
                    float(np.linalg.norm(np.array(a["support_centerline_midpoint_cad_mm"])-
                                         np.array(b["support_centerline_midpoint_cad_mm"])))
                    for i, a in enumerate(samples) for b in samples[i+1:]),
                "current_geometric_audit_contexts": contexts,
                "current_native_audit_interface_region_found": bool(contexts),
                "actual_sampled_support_features": sorted({p["feature"] for p in samples}),
                "actual_native_support_samples": samples})
        outputs.append({
            "part": style, "saved_base": part["saved_stl"],
            "rotation_x_degrees": manifest["rotation_x_degrees"],
            "object_label": audit["inputs"]["object_label"],
            "native_archive": native["archive"], "native_gcode_sha256": gcode_sha,
            "support_segment_midpoints_read": support_count,
            "support_midpoints_in_named_roof_windows": len(points),
            "native_support_summary": audit["summary"],
            "detailed_geometry_access_review": lower_access,
            "roofs": roof_rows})
    validate_bindings(inputs)
    report = {
        "schema": 2, "checked_at_utc": datetime.now(timezone.utc).isoformat(),
        "scope": "Every current named finite native donor/lever-corridor/lever roof finding and actual native support presence. Three distinct finite-face projections per roof do not establish complete coverage, bead contact, physical cleanup, deposited finish, strength or lifetime.",
        "method": "Read all actual Support feature extrusions for each base object from the current hash-bound native archive. Invert the retained print transform and require three distinct bead midpoints whose vertical projections lie on the exact finite native face within1e-6mm. Current audit regions are selected by valid positive-area projected rectangle/native-face intersections, not retained interface IDs; An absent interface-labelled region remains explicit while distinct actual Support paths supply the finite local presence witness; sampled paths are not asserted to inherit those labels.",
        "native_membership_tolerance_mm": NATIVE_MEMBERSHIP_TOLERANCE_MM,
        "support_midpoint_vertical_gap_selection_window_mm": list(GAP_WINDOW_MM),
        "distinct_midpoint_tolerance_mm": DISTINCT_POINT_TOLERANCE_MM,
        "gap_window_scope": "Witness selection only; no physical support-contact acceptance.",
        "source_and_artifact_sha256": inputs,
        "all_named_roofs_have_native_support_witnesses": True,
        "named_roof_count": sum(len(p["roofs"]) for p in outputs), "parts": outputs}
    args.output.write_text(json.dumps(report, indent=2)+"\n")
    print(json.dumps({"output": str(args.output), "all_named_roofs_have_native_support_witnesses": True,
                      "named_roof_count": report["named_roof_count"],
                      "samples": sum(len(r["actual_native_support_samples"]) for p in outputs for r in p["roofs"])}))


if __name__ == "__main__":
    main()
