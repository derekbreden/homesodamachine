"""Named roof/support witnesses from retained native faucet toolpaths.

Three nearby extrusion centerlines per roof are presence witnesses, not proof
of complete support coverage or a physical support-removal result.
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

os.environ.setdefault("HSM_NO_BUILD_LOCK", "1")

import cadquery as cq
import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
sys.path.insert(0, str(HERE.parent))
from prepare_display_print import extrusion_segments


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=HERE / "lint-support-witnesses.json")
    args = parser.parse_args()
    inputs = {str(Path(__file__).resolve().relative_to(ROOT)): sha(Path(__file__).resolve()),
              "hardware/printed-parts/faucet/prepare_display_print.py": sha(HERE.parent / "prepare_display_print.py")}
    proof_path = HERE / "base-native-lint-witnesses.json"
    proof = json.loads(proof_path.read_text())
    inputs[str(proof_path.relative_to(ROOT))] = sha(proof_path)
    outputs = []
    for style, stem, piece, contexts in (
        ("sculpted", "hardware/printed-parts/faucet/faucet-petgf", "faucet-shell-base", {"donor shoulder Z39": "interface-19"}),
        ("industrial", "hardware/printed-parts/faucet/industrial/faucet-industrial-petgf", "industrial-shell-base", {"donor shoulder Z39": "interface-10", "rear lever roof Z57.5": "interface-14"}),
    ):
        reports = {}
        for suffix in (".print.json", ".support-audit.json", ".native-validation.json"):
            path = ROOT / (stem + suffix)
            inputs[str(path.relative_to(ROOT))] = sha(path)
            reports[suffix] = json.loads(path.read_text())
        audit = next(p for p in reports[".support-audit.json"]["parts"] if p["piece"] == piece)
        manifest = next(p for p in reports[".print.json"]["parts"] if p["name"] == piece)
        native = reports[".native-validation.json"]
        archive = ROOT / native["archive"]
        if sha(archive) != native["archive_sha256"]:
            raise ValueError("Native archive binding mismatch")
        inputs[native["archive"]] = sha(archive)
        part = next(p for p in proof["parts"] if p["part"] == style)
        for key in ("saved_step", "saved_stl"):
            rel = part[key]
            expected = proof["source_and_artifact_sha256"][rel]
            if sha(ROOT / rel) != expected:
                raise ValueError("Saved native witness part binding mismatch")
            inputs[rel] = expected
        if audit["inputs"]["model_sha256"] != inputs[part["saved_stl"]] or manifest["stl_sha256"] != inputs[part["saved_stl"]]:
            raise ValueError("Retained slice does not bind current base")
        with zipfile.ZipFile(archive) as z:
            data = z.read("Metadata/plate_1.gcode")
        if hashlib.sha256(data).hexdigest() != native["gcode_sha256"] or native["gcode_sha256"] != audit["inputs"]["plate_gcode_sha256"]:
            raise ValueError("Native G-code binding mismatch")
        rotation = np.array(manifest["build_transform"][:9]).reshape(3, 3).T
        translation = np.array(manifest["plate_translation_mm"])
        center = np.array(manifest["source_center_mm"])
        points = []
        with tempfile.TemporaryDirectory(prefix="hsm-lint-support-") as tmp:
            gcode = Path(tmp) / "plate_1.gcode"
            gcode.write_bytes(data)
            for segment in extrusion_segments(gcode):
                if segment["object"] == audit["inputs"]["object_label"] and segment["feature"].startswith("Support"):
                    point = (np.mean([segment["a"], segment["b"]], axis=0) - translation) @ rotation + center
                    points.append({"cad_mm": point, "feature": segment["feature"], "line_width_mm": segment["width"], "plate_z_mm": segment["layer"]})
        shape = cq.importers.importStep(str(ROOT / part["saved_step"])).val()
        roof_rows = []
        for roof in part["ceiling_faces"]:
            if roof["feature"] not in contexts:
                continue
            face = shape.Faces()[roof["saved_step_face_index"]]
            b = roof["face_bbox_mm"]
            zfloor = roof["actual_face_point_mm"][2]
            candidates = [p for p in points if b[0] <= p["cad_mm"][0] <= b[3]
                          and b[1] <= p["cad_mm"][1] <= b[4]
                          and 0.15 < zfloor - p["cad_mm"][2] < 0.85]
            samples = []
            targets = (-4.0, 0.0, 4.0) if zfloor == 39 else (-5.0, -3.0, -1.0)
            for target in targets:
                found = None
                for p in sorted(candidates, key=lambda p: abs(p["cad_mm"][0] - target) + 5 * (zfloor - p["cad_mm"][2])):
                    projected = [float(p["cad_mm"][0]), float(p["cad_mm"][1]), zfloor]
                    distance = face.distance(cq.Vertex.makeVertex(*projected))
                    if distance < 1e-6:
                        found = {"support_centerline_midpoint_cad_mm": [float(x) for x in p["cad_mm"]],
                                 "projected_roof_point_cad_mm": projected,
                                 "projection_distance_to_native_face_mm": distance,
                                 "vertical_centreline_gap_mm": zfloor - float(p["cad_mm"][2]),
                                 "feature": p["feature"], "line_width_mm": p["line_width_mm"],
                                 "native_plate_layer_z_mm": p["plate_z_mm"]}
                        break
                if found is None:
                    raise ValueError(f"No actual native support witness for {style}/{roof['feature']}/{target}")
                samples.append(found)
            context = next(x for x in audit["interfaces"] if x["id"] == contexts[roof["feature"]])
            tree = next(x for x in audit["trees"] if x["id"] == context["tree"])
            roof_rows.append({"feature": roof["feature"], "native_roof_face_index": roof["saved_step_face_index"],
                              "roof_region_interface_from_audit": context, "interface_tree_from_audit": tree,
                              "actual_native_support_samples": samples})
        outputs.append({"part": style, "saved_base": part["saved_stl"], "rotation_x_degrees": manifest["rotation_x_degrees"],
                        "object_label": audit["inputs"]["object_label"], "support_segment_midpoints_read": len(points),
                        "native_support_summary": audit["summary"], "roofs": roof_rows})
    for rel, expected in inputs.items():
        if sha(ROOT / rel) != expected:
            raise ValueError(f"Input changed during review: {rel}")
    report = {"schema": 1, "checked_at_utc": datetime.now(timezone.utc).isoformat(),
              "scope": "Named roof geometry and retained native extrusion presence. The samples are not complete coverage or interface-contact proofs, and they do not establish physical support release, contact finish or part strength.",
              "method": "Read every actual Support feature extrusion for the base object from the hash-bound native archive. Invert its retained print transform. Select three centerline midpoint witnesses whose vertical projections lie on each exact native roof face. Audit interface IDs describe the roof region and supporting tree; the sampled paths are not asserted to carry those interface labels.",
              "source_and_artifact_sha256": inputs, "all_named_roofs_have_native_support_witnesses": True, "parts": outputs}
    args.output.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({"output": str(args.output), "all_named_roofs_have_native_support_witnesses": True,
                      "roofs": sum(len(x["roofs"]) for x in outputs)}))


if __name__ == "__main__":
    main()
