"""Replay the complete hatch recipe while retaining every published native byte.

The original producer performs all of its geometry, landing, tool and stock
checks. Its exports are captured in memory. Every captured output must match
the complete held native material before this checker refreshes only excluded
evidence fields of the existing hatch manifest.
"""
from io import BytesIO
from pathlib import Path
import argparse
import copy
import hashlib
import json
import sys
import time

import cadquery as cq

HERE = Path(__file__).resolve().parent
STUDY = HERE.parent
ROOT = STUDY.parents[1]
sys.path.insert(0, str(STUDY))
sys.path.insert(0, str(STUDY / "structure"))
from evidence_binding import content_sha256, manifest_content_sha256
from structure import assemble_prints_verified as material
from structure import build_roof_hatch as original

HATCH = STUDY / "structure/roof-hatch.json"
OUT = ROOT / ".cache/pump-first-layout/routing/roof-hatch-received"
ALLOWED_METADATA_INPUTS = {
    "future/pump-first-layout-study/wiring/controls-candidate.json",
    "future/pump-first-layout-study/wiring/control-reserves.json",
    "future/pump-first-layout-study/wiring/front-loom-handling.json",
}


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def native_records(value):
    if isinstance(value, dict):
        if isinstance(value.get("brep"), str):
            yield value
        for child in value.values():
            yield from native_records(child)
    elif isinstance(value, list):
        for child in value:
            yield from native_records(child)


def complete_solid_parity(received, expected, label):
    """One-to-one material identity proves compound union identity as well.

    This does not sum overlapping compound material. Each whole source Solid
    has one complete counterpart, witnessed by independent full native
    Commons in both directions.
    """
    if (received.wrapped.IsNull() or expected.wrapped.IsNull()
            or not received.isValid() or not expected.isValid()):
        raise ValueError("Invalid held or replayed native output: " + label)
    first, second = received.Solids(), expected.Solids()
    if not first or len(first) != len(second):
        raise ValueError("Native output has different solid membership: " + label)
    boxes = [material.EXACT_EXTREMA.bounds(solid) for solid in second]
    remaining = set(range(len(second)))
    pairs = []
    for index, solid in enumerate(first):
        bounds = material.EXACT_EXTREMA.bounds(solid)
        attempts = []
        for target in sorted(remaining):
            error = max(abs(getattr(bounds, key) - getattr(boxes[target], key))
                        for key in ("xmin", "xmax", "ymin", "ymax", "zmin", "zmax"))
            if error >= 1e-5:
                continue
            other = second[target]
            for tolerance in (0., .0001, .00001):
                try:
                    source_volume, target_volume = material.volume(solid), material.volume(other)
                    forward, forward_witness = material.common_pair(solid, other, tolerance)
                    reverse, reverse_witness = material.common_pair(other, solid, tolerance)
                    forward_error = abs(source_volume - forward)
                    reverse_error = abs(target_volume - reverse)
                    volume_error = abs(source_volume - target_volume)
                    passed = max(forward_error, reverse_error, volume_error) < material.LIMIT_MM3
                    row = {"held_solid": index, "recipe_solid": target,
                           "native_extrema_error_mm": error, "tolerance_mm": tolerance,
                           "held_volume_mm3": source_volume, "recipe_volume_mm3": target_volume,
                           "volume_error_mm3": volume_error,
                           "held_in_recipe": {**forward_witness, "missing_mm3": forward_error},
                           "recipe_in_held": {**reverse_witness, "missing_mm3": reverse_error},
                           "pass": passed}
                    attempts.append(row)
                    if passed:
                        pairs.append(row)
                        remaining.remove(target)
                        break
                except Exception as failure:
                    attempts.append({"recipe_solid": target, "tolerance_mm": tolerance,
                                     "error": str(failure), "pass": False})
            else:
                continue
            break
        else:
            raise ValueError("Complete native output has no material counterpart: " + label + str(attempts))
    total_error = sum(row["volume_error_mm3"] + row["held_in_recipe"]["missing_mm3"]
                      + row["recipe_in_held"]["missing_mm3"] for row in pairs)
    if remaining or total_error >= material.LIMIT_MM3:
        raise ValueError("Complete output parity exceeds the material limit: " + label)
    return {"method": "complete_one_to_one_independent_native_solid_parity",
            "held_solids": len(first), "recipe_solids": len(second), "pairs": pairs,
            "complete_material_error_sum_mm3": total_error, "pass": True}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--publish", action="store_true",
                        help="Publish excluded evidence only after a complete held-content/native replay")
    args = parser.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    started = time.monotonic()
    held_raw = HATCH.read_bytes()
    held = json.loads(held_raw)
    canonical_before = content_sha256(held)
    source_inputs = {str(path.relative_to(ROOT)): digest(path.read_bytes())
                     for path in (Path(__file__), Path(original.__file__),
                                  Path(material.__file__), STUDY / "evidence_binding.py")}
    for path, sha in held["source_inputs"].items():
        if digest((ROOT / path).read_bytes()) != sha:
            raise ValueError("Held original hatch check source changed: " + path)
        source_inputs[path] = sha
    changed_inputs = []
    for path, sha in held["manifest_content_sha256"].items():
        if manifest_content_sha256(ROOT / path) != sha:
            changed_inputs.append(path)
            if path not in ALLOWED_METADATA_INPUTS:
                raise ValueError("Unexpected substantive hatch input change: " + path)
    held_bytes = {}
    for record in native_records(held):
        path = record["brep"]
        raw = held_bytes.setdefault(path, (ROOT / path).read_bytes())
        if isinstance(record.get("sha256"), str) and digest(raw) != record["sha256"]:
            raise ValueError("Held hatch native input/output changed: " + path)
    exported = []
    export_brep = cq.Shape.exportBrep
    fresh_path = OUT / "fresh-normal-report.json"

    def capture_export(shape, path):
        absolute = Path(path).resolve()
        if not absolute.is_relative_to(original.OUT):
            raise ValueError("Unexpected native export outside held hatch outputs: " + str(absolute))
        relative = str(absolute.relative_to(ROOT))
        old_raw = held_bytes.setdefault(relative, absolute.read_bytes())
        stream = BytesIO()
        result = export_brep(shape, stream)
        raw = stream.getvalue()
        if not raw:
            raise ValueError("Normal recipe produced no complete native bytes: " + relative)
        exported.append({"path": relative, "held_raw": old_raw, "recipe_raw": raw})
        return result

    try:
        cq.Shape.exportBrep = capture_export
        original.main(report_path=fresh_path)
    finally:
        cq.Shape.exportBrep = export_brep
    fresh_raw = fresh_path.read_bytes()
    fresh = json.loads(fresh_raw)
    if not fresh["pass"] or fresh.get("source_drift") or fresh.get("manifest_drift"):
        raise ValueError("Complete fresh normal hatch checks failed")
    # Ownership, mechanical recipe and exact print graph must remain fixed.
    fixed_fields = ("replacement_names", "root_owner_overrides", "pilot_owner_overrides",
                    "shell_fuse_part_names", "standalone_print_parts", "mounts", "rectangle_xy_mm",
                    "controller_islands", "carried_names", "joint", "factory_access", "scope",
                    "qualification_limits", "ground_pose_override")
    for key in fixed_fields:
        if fresh.get(key) != held.get(key):
            raise ValueError("Substantive hatch recipe/ownership changed: " + key)
    for group in ("parts", "pilot_cutters", "clearance_cutters", "ground_tail_inspection_cutters"):
        if set(fresh.get(group, {})) != set(held.get(group, {})):
            raise ValueError("Substantive hatch native graph changed: " + group)
        for name in held.get(group, {}):
            for key in ("brep", "sha256", "print_owner", "role", "detail", "inspection_only"):
                if fresh[group][name].get(key) != held[group][name].get(key):
                    raise ValueError("Substantive hatch output record changed: " + group + "/" + name + "/" + key)
    material.EXACT_EXTREMA.begin()
    parity_checks = []
    for index, item in enumerate(exported):
        same_bytes = item["held_raw"] == item["recipe_raw"]
        received = cq.Shape.importBrep(BytesIO(item["held_raw"]))
        expected = cq.Shape.importBrep(BytesIO(item["recipe_raw"]))
        parity = complete_solid_parity(received, expected, item["path"])
        parity_checks.append({"brep": item["path"], "held_sha256": digest(item["held_raw"]),
                              "recipe_sha256": digest(item["recipe_raw"]),
                              "serialized_bytes_identical": same_bytes, **parity})
        print("hatch received output", index + 1, len(exported), item["path"], "PASS", flush=True)
    extrema = material.EXACT_EXTREMA.finish()
    native_drift = [path for path, raw in held_bytes.items() if (ROOT / path).read_bytes() != raw]
    source_drift = [path for path, sha in source_inputs.items() if digest((ROOT / path).read_bytes()) != sha]
    if native_drift or source_drift or not extrema["pass"] or content_sha256(json.loads(HATCH.read_bytes())) != canonical_before:
        raise ValueError("Held hatch replay input/native/source drift")
    replay = {"check": "Complete unchanged normal hatch recipe replay with no native export",
              "changed_metadata_input_paths": changed_inputs,
              "fresh_normal_report": str(fresh_path.relative_to(ROOT)),
              "fresh_normal_report_sha256": digest(fresh_raw),
              "fresh_normal_checks_pass": fresh["pass"],
              "complete_native_output_parity": parity_checks,
              "exact_native_extrema_cache": extrema,
              "native_drift": native_drift, "source_drift": source_drift,
              "held_canonical_content_sha256": canonical_before,
              "elapsed_seconds": time.monotonic() - started, "pass": True}
    proof_path = OUT / "received-check.json"
    proof_path.write_text(json.dumps(replay, indent=2) + "\n")
    if args.publish:
        updated = copy.deepcopy(held)
        updated.setdefault("checks", {})["complete_received_normal_replay"] = replay
        updated["source_inputs"] = {**fresh["source_inputs"], **source_inputs}
        updated["source_inputs"][str(fresh_path.relative_to(ROOT))] = digest(fresh_raw)
        updated["native_inputs"] = fresh["native_inputs"]
        for path, raw in held_bytes.items():
            updated["native_inputs"]["received-replay/" + path] = {"brep": path, "sha256": digest(raw)}
        updated["manifest_sha256"] = fresh["manifest_sha256"]
        updated["manifest_content_sha256"] = fresh["manifest_content_sha256"]
        updated["source_drift"] = []
        updated["manifest_drift"] = []
        updated["pass"] = True
        if content_sha256(updated) != canonical_before:
            raise ValueError("Received hatch evidence refresh changes substantive content")
        HATCH.write_text(json.dumps(updated, indent=2) + "\n")
    print(json.dumps({"pass": True, "published": args.publish,
                      "canonical_content_held": canonical_before,
                      "native_outputs_checked": len(parity_checks)}), flush=True)


if __name__ == "__main__":
    main()
