"""Local saved-STEP backing witnesses for the named faucet lint findings.

This reads exported production parts. It neither builds nor changes geometry,
and it does not establish global wall thickness or mechanical capacity.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path

os.environ.setdefault("HSM_NO_BUILD_LOCK", "1")

import cadquery as cq


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
PARTS = {
    "sculpted": (
        "hardware/printed-parts/faucet/faucet-shell/faucet-shell-base",
        "hardware/printed-parts/faucet/faucet-shell/faucet_shell.py",
    ),
    "industrial": (
        "hardware/printed-parts/faucet/industrial/industrial-shell-base",
        "hardware/printed-parts/faucet/industrial/industrial_faucet.py",
    ),
}
PICKS = {
    "sliver": ((9.085, 18.945, 7.0), (0.0, -1.0, 0.0)),
    "step": ((9.075, 13.286, 24.424), (-1.0, 0.0, 0.0)),
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def volume(shape: cq.Shape) -> float:
    return sum(s.Volume() for s in shape.Solids())


def face_at(shape: cq.Shape, point, normal):
    vertex = cq.Vertex.makeVertex(*point)
    expected = cq.Vector(*normal)
    candidates = [
        (i, f)
        for i, f in enumerate(shape.Faces())
        if f.geomType() == "PLANE"
        and f.normalAt().dot(expected) > 0.999999
        and f.distance(vertex) < 1e-6
    ]
    if len(candidates) != 1:
        raise ValueError(f"Expected one planar face at {point}; got {len(candidates)}")
    return candidates[0]


def face_record(index, face):
    b = face.BoundingBox()
    return {
        "saved_step_face_index": index,
        "face_area_mm2": face.Area(),
        "face_normal": list(face.normalAt().toTuple()),
        "face_bbox_mm": [b.xmin, b.ymin, b.zmin, b.xmax, b.ymax, b.zmax],
    }


def backing(shape, name, pick, normal):
    index, face = face_at(shape, pick, normal)
    inward = face.normalAt().multiply(-1)
    witness = cq.Solid.extrudeLinear(face.outerWire(), face.innerWires(), inward.multiply(2))
    missing = witness.cut(shape)
    line = cq.Edge.makeLine(cq.Vector(*pick), cq.Vector(*pick) + inward.multiply(25))
    common = line.intersect(shape)
    segments = [
        {
            "length_mm": e.Length(),
            "start_mm": list(e.startPoint().toTuple()),
            "end_mm": list(e.endPoint().toTuple()),
        }
        for e in common.Edges()
    ]
    valid = witness.isValid() and missing.isValid() and common.isValid()
    missing_volume = volume(missing)
    return {
        "class": name,
        "pick_mm": list(pick),
        **face_record(index, face),
        "required_inward_stock_mm": 2.0,
        "complete_witness_volume_mm3": volume(witness),
        "missing_witness_volume_mm3": missing_volume,
        "witness_and_boolean_valid": valid,
        "centre_normal_line_limit_mm": 25.0,
        "centre_normal_material_segments": segments,
        "centre_normal_material_chord_mm": sum(x["length_mm"] for x in segments),
        "pass": valid and missing_volume < 1e-7,
    }


def roof(shape, label, actual, lint_pick):
    index, face = face_at(shape, actual, (0.0, 0.0, -1.0))
    witness = cq.Solid.extrudeLinear(face.outerWire(), face.innerWires(), face.normalAt().multiply(-2))
    missing = witness.cut(shape)
    valid = witness.isValid() and missing.isValid()
    missing_volume = volume(missing)
    return {
        "class": "ceiling",
        "feature": label,
        "actual_face_point_mm": list(actual),
        "lint_plane_pick_mm": list(lint_pick),
        "lint_pick_distance_to_actual_face_mm": face.distance(cq.Vertex.makeVertex(*lint_pick)),
        **face_record(index, face),
        "required_inward_stock_mm": 2.0,
        "complete_witness_volume_mm3": volume(witness),
        "missing_witness_volume_mm3": missing_volume,
        "witness_and_boolean_valid": valid,
        "pass": valid and missing_volume < 1e-7,
        "print_pose_degrees_about_x": -15.0,
        "scope": "Named saved-face identification and complete 2 mm inward stock. Retained native toolpaths supply support evidence. Physical cleanup and contact finish are not measured.",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=HERE / "base-native-lint-witnesses.json")
    args = parser.parse_args()
    bindings = {str(Path(__file__).resolve().relative_to(ROOT)): sha(Path(__file__).resolve())}
    rows = []
    for name, (stem, source) in PARTS.items():
        for rel in (stem + ".step", stem + ".stl", source):
            bindings[rel] = sha(ROOT / rel)
        shape = cq.importers.importStep(str(ROOT / (stem + ".step"))).val()
        valid = shape.isValid() and len(shape.Solids()) == 1 and volume(shape) > 0
        if not valid:
            raise ValueError(f"Saved {name} base is not one valid positive solid")
        witnesses = [backing(shape, label, *spec) for label, spec in PICKS.items()]
        roofs = [roof(shape, "donor shoulder Z39", (0.0, 14.156, 39.0), (0.0, 14.156, 39.0))]
        if name == "industrial":
            roofs.append(roof(shape, "rear lever roof Z57.5", (-4.0, 4.932, 57.5), (0.0, 4.932, 57.5)))
        for cx, cy in ((0.0, -22.3), (-22.5, -2.0), (22.5, -2.0)):
            roofs.append(roof(shape, "registration socket roof", (cx + 3.0, cy, 3.2), (cx, cy, 3.2)))
        rows.append({
            "part": name,
            "saved_step": stem + ".step",
            "saved_stl": stem + ".stl",
            "native_shape_valid_one_positive_solid": valid,
            "native_volume_mm3": volume(shape),
            "material_witnesses": witnesses,
            "ceiling_faces": roofs,
        })
    for rel, expected in bindings.items():
        if sha(ROOT / rel) != expected:
            raise ValueError(f"Input changed while reading: {rel}")
    report = {
        "schema": 1,
        "checked_at_utc": datetime.now(timezone.utc).isoformat(),
        "scope": "Local native geometric witnesses for final saved base files; no geometry mutation, global wall guarantee, physical print, strength or lifetime result.",
        "method": "Select the named saved-STEP planar face. Extrude its complete outer and inner wires 2 mm inward, subtract the saved solid, and sum missing solid volumes. Intersect a separate 25 mm inward line from the pick with the saved solid. Require valid native operations and no missing witness volume within 1e-7 mm3.",
        "source_and_artifact_sha256": bindings,
        "all_named_backing_witnesses_pass": all(w["pass"] for row in rows for w in row["material_witnesses"]),
        "all_named_ceiling_stock_witnesses_pass": all(w["pass"] for row in rows for w in row["ceiling_faces"]),
        "parts": rows,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({"output": str(args.output), "all_named_backing_witnesses_pass": report["all_named_backing_witnesses_pass"], "all_named_ceiling_stock_witnesses_pass": report["all_named_ceiling_stock_witnesses_pass"], "parts": [{"part": row["part"], "chords_mm": {w["class"]: w["centre_normal_material_chord_mm"] for w in row["material_witnesses"]}} for row in rows]}))


if __name__ == "__main__":
    main()
