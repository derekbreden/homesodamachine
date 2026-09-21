#!/usr/bin/env python3
"""Verify publish_now's fixed and moving enclosure refresh without changing inputs.

Read-only except for the explicitly named, new JSON output. This compares payload
arrays; it never calls graft(), write(), a generator, a publisher or native CAD.
The before carrier pose is diagnostic: publication may repair its stale release
pose. The after arrays must match the exact facts-derived connected placement.
Identical input bytes are an idempotence guard, not a witnessed publication run.
"""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import sys

sys.dont_write_bytecode = True
# flute_payload's decoder imports the shared exporter. Do not acquire its
# generator mutex for this read-only payload operation.
os.environ["HSM_NO_BUILD_LOCK"] = "1"

ROOT = Path("/Users/derekbredensteiner/Developer/homesodamachine")
AGG_STEP = ROOT / "hardware/manifold-layout/enclosure-assembly.step"
AGG_PAYLOAD = AGG_STEP.with_name(AGG_STEP.name + ".mesh")
FACTS = ROOT / "hardware/manifold-layout/enclosure-assembly.facts.json"
POINTER = ROOT / "hardware/cad-artifacts.json"
EXPECTED = {
    "enclosure-front-top", "enclosure-front-bottom",
    "enclosure-back-top", "enclosure-back-bottom",
    "enclosure-pump-cartridge", "enclosure-pump-cap",
    "enclosure-tee-carrier-left", "enclosure-tee-carrier-right",
}
ARRAYS = ("pos", "nrm", "idx", "fac")
MOVING = {"enclosure-tee-carrier-left", "enclosure-tee-carrier-right"}
POSE_TOL_MM = 1e-4
TOOL_PATHS = (
    ROOT / "hardware/scripts/flute_payload.py",
    ROOT / "hardware/scripts/_mesh_payload.py",
    ROOT / "hardware/scripts/_cadq_export.py",
    ROOT / "hardware/scripts/_run_lock.py",
    ROOT / "tools/publish_now.py",
)


def label(path):
    path = Path(path).resolve()
    return str(path.relative_to(ROOT)) if path.is_relative_to(ROOT) else str(path)


def digest(path):
    path = Path(path)
    before = path.stat()
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            h.update(block)
    after = path.stat()
    if (before.st_size, before.st_mtime_ns) != (after.st_size, after.st_mtime_ns):
        raise ValueError(f"file changed while hashing: {path}")
    return h.hexdigest()


def differing_arrays(left, right, np):
    """Compare exact binary values at the payload's declared float/u32 precision."""
    different = []
    for key in ARRAYS:
        dtype = "<f4" if key in ("pos", "nrm") else "<u4"
        a = np.asarray(left[key], dtype=dtype)
        b = np.asarray(right[key], dtype=dtype)
        if a.shape != b.shape or a.tobytes() != b.tobytes():
            different.append(key)
    return different


def compare_entries(before, after, surfaces, fp, np, check, carrier_offset_y):
    names_before = [x["name"] for x in before]
    names_after = [x["name"] for x in after]
    check("entry names and order identical", names_before == names_after,
          before_count=len(before), after_count=len(after))
    check("all host colors identical in order",
          [x["color"] for x in before] == [x["color"] for x in after])
    owner = fp.payload_owner(AGG_PAYLOAD)
    mappings = {}
    for scope, entries in (("before", before), ("after", after)):
        mapped = [(i, x["name"], fp.fluted_key(x["name"], surfaces, owner=owner))
                  for i, x in enumerate(entries)]
        selected = [(i, name, key) for i, name, key in mapped if key is not None]
        counts = Counter(key for _i, _name, key in selected)
        check(f"{scope} contains exactly the eight canonical enclosure/carrier entries",
              set(counts) == EXPECTED and all(n == 1 for n in counts.values())
              and len(selected) == 8, mapped_entries=selected)
        mappings[scope] = mapped

    changed, unexpected, canonical_failures, placements = [], [], [], []
    for index, entry in enumerate(after):
        key = mappings["after"][index][2]
        if key is not None:
            expected_surface = surfaces[key]
            if key in MOVING:
                expected_translation = np.array([0.0, carrier_offset_y, 0.0])
                before_placement = fp.placement_onto(before[index], surfaces[key]) if index < len(before) else None
                after_placement = fp.placement_onto(entry, surfaces[key])
                # A prior fixed-frame publication could reset this viewer-only
                # group to release. Keep that observation without requiring it
                # to be correct; the exact AFTER pose is the repair contract.
                diagnostic = {"name": entry["name"], "before_pose_is_diagnostic": True,
                              "before_pose_recovered": before_placement is not None,
                              "facts_translation_mm": expected_translation.tolist()}
                if before_placement is not None:
                    diagnostic["before_rotation"] = before_placement[0].tolist()
                    diagnostic["before_translation_mm"] = before_placement[1].tolist()
                check(f"moving placement recovered from after entry: {entry['name']}",
                      after_placement is not None)
                if after_placement is not None:
                    rotation, translation = after_placement
                    identity = bool(np.array_equal(rotation, np.eye(3)))
                    error = float(np.max(np.abs(translation - expected_translation)))
                    check(f"after moving carrier matches facts working pose: {entry['name']}",
                          identity and error <= POSE_TOL_MM,
                          identity_rotation=identity, measured_translation_mm=translation.tolist(),
                          expected_translation_mm=expected_translation.tolist(),
                          maximum_translation_error_mm=error, tolerance_mm=POSE_TOL_MM)
                    diagnostic["after_rotation"] = rotation.tolist()
                    diagnostic["after_translation_mm"] = translation.tolist()
                placements.append(diagnostic)
                expected_surface = fp.carried(surfaces[key], (np.eye(3), expected_translation))
            if expected_surface is not None:
                different = differing_arrays(entry, expected_surface, np)
                strategy = "carried moving" if key in MOVING else "same-frame static"
                check(f"{strategy} canonical arrays: {entry['name']}", not different,
                      canonical_piece=key, differing_arrays=different)
                if different:
                    canonical_failures.append(entry["name"])
        if index < len(before):
            different = differing_arrays(before[index], entry, np)
            if different:
                row = {"index": index, "name": entry["name"],
                       "canonical_piece": key, "arrays": different}
                changed.append(row)
                if key is None:
                    unexpected.append(row)
    # A count/name mismatch is already a failure; do not let zip truncation
    # turn absent noncanonical entries into an apparent unchanged result.
    check("every other entry's four arrays unchanged",
          names_before == names_after and not unexpected,
          compared_noncanonical_entries=sum(key is None for _, _, key in mappings["after"]),
          unexpected_changes=unexpected)
    check("only the eight allowed entries may change",
          names_before == names_after and not unexpected,
          changed_entry_count=len(changed))
    return {"aggregate_owner": owner, "entry_count": len(after),
            "expected_canonical_entries": sorted(EXPECTED),
            "canonical_array_failures": canonical_failures,
            "changed_entries": changed,
            "same_frame_static_entries": sorted(EXPECTED - MOVING),
            "carried_moving_entries": placements}


def verify(before_path, after_path, repair_script=None):
    report = {
        "schema": 1, "status": "fail", "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "scope": "Read-only publication transformation: six exact same-frame surfaces and two carrier surfaces at the exact facts-derived working pose. Before carrier pose is diagnostic and may be repaired; every other entry must remain unchanged. Not a CAD, print or physical-fit qualification.",
        "before_payload": str(before_path), "after_payload": str(after_path),
        "before_sha256": None, "after_sha256": None, "source_step_sha256": None,
        "checks": [], "failures": [], "source_sha256": {}, "input_sha256": {},
        "print_released": False,
    }

    def check(name, passed, **details):
        row = {"check": name, "pass": bool(passed)}
        row.update(details)
        report["checks"].append(row)
        if not passed:
            report["failures"].append(name)

    try:
        tool_paths = (Path(__file__).resolve(), *TOOL_PATHS)
        if repair_script is not None:
            tool_paths += (repair_script,)
            report["publication_repair_script"] = label(repair_script)
        for path in tool_paths:
            report["source_sha256"][label(path)] = digest(path)
        sys.path.insert(0, str(ROOT / "hardware/scripts"))
        import flute_payload as fp
        import numpy as np

        report["before_sha256"] = digest(before_path)
        report["after_sha256"] = digest(after_path)
        report["source_step_sha256"] = digest(AGG_STEP)
        report["input_sha256"][label(AGG_STEP)] = report["source_step_sha256"]
        report["input_sha256"][label(FACTS)] = digest(FACTS)
        facts = json.loads(FACTS.read_text())
        carrier = facts["box"]["tee_carrier"]
        state = carrier["assembly_state"]
        connected_offset = float(carrier["connected_offset_y"])
        state_offset = float(carrier["states"][state]["offset_y"])
        check("facts name a consistent connected carrier assembly state",
              state == "connected" and np.isfinite(connected_offset)
              and abs(state_offset - connected_offset) <= POSE_TOL_MM,
              assembly_state=state, connected_offset_y_mm=connected_offset,
              state_offset_y_mm=state_offset)
        report["carrier_pose"] = {"facts": label(FACTS), "assembly_state": state,
                                  "expected_translation_mm": [0.0, connected_offset, 0.0],
                                  "required_rotation": "identity", "tolerance_mm": POSE_TOL_MM}
        identical = report["before_sha256"] == report["after_sha256"]
        report["input_relationship"] = "identical_payload_bytes_idempotence_guard" if identical else "distinct_pre_post_payload_bytes"
        report["publication_invoked_by_verifier"] = False
        for scope, path in (("before", before_path), ("after", after_path)):
            header = fp._mesh_payload.read_header(path)
            check(f"{scope} payload src is current aggregate STEP SHA256",
                  header.get("src") == report["source_step_sha256"], src=header.get("src"))
            check(f"{scope} uses the current payload version",
                  header.get("v") == fp._mesh_payload.VERSION, version=header.get("v"))

        pieces = fp.pieces(fp.ENCLOSURE_DIRS)
        check("canonical piece catalog is exactly the expected eight triplets",
              len(pieces) == 8 and {step.stem for step, _stl in pieces} == EXPECTED,
              piece_stems=[step.stem for step, _stl in pieces])
        triplets = []
        for step, stl in pieces:
            payload = step.with_name(step.name + ".mesh")
            paths = {"step": step, "stl": stl, "payload": payload}
            row = {}
            for role, path in paths.items():
                value = digest(path)
                report["input_sha256"][label(path)] = value
                row[role] = {"path": label(path), "sha256": value}
            triplets.append(row)
        # surfaces() independently enforces each canonical payload's exact STEP
        # stamp. No native import, tessellation, graft or writer is called.
        surfaces = fp.surfaces(fp.ENCLOSURE_DIRS)
        check("surfaces validates all eight canonical STEP stamps",
              set(surfaces) == EXPECTED and len(surfaces) == 8)
        report["canonical_triplets"] = triplets
        after = fp.read_payload(after_path)
        before = after if identical else fp.read_payload(before_path)
        check("both payloads decode", bool(before) and bool(after))
        if not before or not after:
            raise ValueError("payload decoding returned no entries")
        report["comparison"] = compare_entries(before, after, surfaces, fp, np, check,
                                                connected_offset)

        pointer = json.loads(POINTER.read_text())
        expected_pointer = {label(AGG_STEP): report["source_step_sha256"],
                            label(AGG_PAYLOAD): report["after_sha256"]}
        selected = {key: pointer.get("solids", {}).get(key) for key in expected_pointer}
        check("current pointer names the exact after payload and aggregate STEP",
              selected == expected_pointer, selected_entries=selected)
        report["pointer"] = {"path": label(POINTER), "selected_entries": selected,
                             "expected_entries": expected_pointer,
                             "whole_file_hash_required": False}
        check("after payload is the current canonical aggregate payload",
              digest(AGG_PAYLOAD) == report["after_sha256"])

        drift = []
        for group in ("source_sha256", "input_sha256"):
            for name, expected in report[group].items():
                path = Path(name) if Path(name).is_absolute() else ROOT / name
                if digest(path) != expected:
                    drift.append(name)
        if digest(before_path) != report["before_sha256"]:
            drift.append(str(before_path))
        if digest(after_path) != report["after_sha256"]:
            drift.append(str(after_path))
        final_pointer = json.loads(POINTER.read_text()).get("solids", {})
        if {key: final_pointer.get(key) for key in expected_pointer} != selected:
            drift.append("selected pointer entries")
        check("all bound source/input/payload bytes and selected pointer entries stable",
              not drift, changed_during_verification=drift)
        # before is intentionally excluded: the collector must compare its
        # digest with the last producer output and its immutable before file.
        check("before payload is excluded from current input_sha256",
              label(before_path) not in report["input_sha256"])
    except Exception as exc:
        check("verification completed without an exception", False,
              exception_type=type(exc).__name__, message=str(exc))
    report["status"] = "pass" if report["checks"] and not report["failures"] else "fail"
    return report


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--before", type=Path, required=True)
    parser.add_argument("--after", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--publication-repair-script", type=Path,
                        help="Bind the one-time carrier viewer repair script as source evidence; never execute it.")
    args = parser.parse_args(argv)
    before, after, output = (p.resolve() for p in (args.before, args.after, args.output))
    if output.exists() or not output.parent.is_dir():
        parser.error("--output must be a new file in an existing directory")
    protected = {before, after, AGG_STEP, AGG_PAYLOAD, FACTS, POINTER,
                 Path(__file__).resolve(), *TOOL_PATHS}
    repair_script = args.publication_repair_script.resolve() if args.publication_repair_script else None
    if repair_script is not None:
        protected.add(repair_script)
    if output in protected:
        parser.error("--output must not replace an input or tool")
    report = verify(before, after, repair_script)
    with output.open("x") as stream:
        json.dump(report, stream, indent=2, allow_nan=False)
        stream.write("\n")
    print(f"{report['status']}: {len(report['checks'])} checks, {len(report['failures'])} failures; {output}")
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
