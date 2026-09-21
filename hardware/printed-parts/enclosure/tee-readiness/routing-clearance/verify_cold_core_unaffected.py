"""Prove one unused enclosure-interface assignment leaves the cold-core outputs current.

This reads the successful native-generation traces and their exact source/output
digests. It permits only the recorded pump_station_lead assignment change, and
rejects any other executable interface change or any changed cold-core dependency.
It does not generate geometry, change the build graph, or release an enclosure.
"""

from __future__ import annotations

import ast
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if p.name == "hardware").parent
EVIDENCE = HERE / "dependency-regeneration"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def assignment(tree: ast.Module, name: str) -> ast.Assign:
    hits = [node for node in tree.body if isinstance(node, ast.Assign)
            and any(isinstance(target, ast.Name) and target.id == name
                    for target in node.targets)]
    assert len(hits) == 1, f"Expected exactly one assignment to {name}"
    assert len(hits[0].targets) == 1, f"Aliased assignment to {name} is unsupported"
    return hits[0]


def unchanged(mapping: dict[str, str], allowed: frozenset[str] = frozenset()) -> list[str]:
    return [name for name, digest in mapping.items() if name not in allowed
            and (not (ROOT / name).is_file() or sha(ROOT / name) != digest)]


def main() -> None:
    baseline_path = EVIDENCE / "pump-station-lead-baseline.json"
    baseline = json.loads(baseline_path.read_text())
    currentness_path = EVIDENCE / "currentness.json"
    assert sha(currentness_path) == baseline["currentness_report_sha256"]
    currentness = json.loads(currentness_path.read_text())
    assert currentness["status"] == "pass"
    records = json.loads((EVIDENCE / "generation.json").read_text())
    latest = {row["generator"]: row for row in records if row["status"] == "pass"}
    changed_path = baseline["path"]
    member = baseline["proposed_change"]["assignment"]
    before = ast.parse(baseline["source"])
    after = ast.parse((ROOT / changed_path).read_text())
    before_value = ast.literal_eval(assignment(before, member).value)
    after_value = ast.literal_eval(assignment(after, member).value)
    restored_after = deepcopy(after)
    assignment(restored_after, member).value = deepcopy(assignment(before, member).value)

    checks = []

    def check(name, condition, reading):
        checks.append({"check": name, "pass": bool(condition), "reading": reading})

    check("Baseline source bytes match the successful build input",
          hashlib.sha256(baseline["source"].encode()).hexdigest() == baseline["sha256"]
          == currentness["source_sha256"][changed_path], baseline["sha256"])
    check("Only the recorded numeric assignment changes executable interface source",
          ast.dump(before, include_attributes=False)
          == ast.dump(restored_after, include_attributes=False),
          {"member": member, "before": before_value, "after": after_value})
    check("Assignment values equal the bounded proposed change",
          before_value == baseline["proposed_change"]["before"]
          and after_value == baseline["proposed_change"]["after"],
          baseline["proposed_change"])

    reads = [node.lineno for node in ast.walk(after)
             if isinstance(node, ast.Name) and node.id == member
             and isinstance(node.ctx, ast.Load)]
    check("Changed value feeds no other enclosure-interface declaration", not reads, reads)

    consumed = []
    full_module_imports = []
    changed_symbol_reads = []
    for name in currentness["source_sha256"]:
        tree = ast.parse((ROOT / name).read_text())
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module == "_enclosure_interface":
                consumed.append({"file": name, "line": node.lineno,
                                 "names": [alias.name for alias in node.names]})
            if isinstance(node, ast.Import):
                full_module_imports.extend({"file": name, "line": node.lineno,
                                            "alias": alias.asname or alias.name}
                                           for alias in node.names
                                           if alias.name == "_enclosure_interface")
            if name != changed_path and (
                    isinstance(node, ast.Name) and node.id == member
                    or isinstance(node, ast.Attribute) and node.attr == member
                    or isinstance(node, ast.Constant) and node.value == member):
                changed_symbol_reads.append({"file": name, "line": node.lineno})
    check("Cold-core source closure uses only the two unchanged interface members",
          len(consumed) == 1
          and consumed[0]["file"] == "hardware/printed-parts/cold-core/_cold_core_interface.py"
          and set(consumed[0]["names"]) == {"manifold_rise", "inner_limb_drop"}
          and not full_module_imports and not changed_symbol_reads,
          {"imports": consumed, "full_module_imports": full_module_imports,
           "changed_symbol_reads": changed_symbol_reads})

    consumed_values = {name: {"before": ast.literal_eval(assignment(before, name).value),
                             "after": ast.literal_eval(assignment(after, name).value)}
                       for name in ("manifold_rise", "inner_limb_drop")}
    check("Consumed interface values are unchanged",
          all(row["before"] == row["after"] for row in consumed_values.values()),
          consumed_values)

    source_drift = unchanged(currentness["source_sha256"], frozenset({changed_path}))
    check("All other loaded first-party source hashes match", not source_drift, source_drift)
    forbidden_runtime_reads = []
    input_drift = {}
    affected_generators = []
    for generator, row in latest.items():
        trace_path = Path(row.get("input_trace", EVIDENCE / (Path(generator).stem + ".input-trace.json")))
        trace = json.loads(trace_path.read_text())
        forbidden_runtime_reads.extend(name for name in trace["reads"]
                                       if name in ("hardware/manifold-layout/manifold_layout.py",
                                                   "hardware/manifold-layout/enclosure_assembly.py"))
        input_drift[generator] = unchanged(row["input_sha256"], frozenset({changed_path}))
        if changed_path in row["input_sha256"]:
            affected_generators.append(generator)
    check("No cold-core run loads a manifold or enclosure assembly producer",
          not forbidden_runtime_reads, sorted(set(forbidden_runtime_reads)))
    check("All other recorded native/source inputs match",
          not any(input_drift.values()), input_drift)

    output_hashes = dict(currentness["output_sha256"])
    output_hashes.update({name: row["sha256"] for name, row
                         in currentness["additional_emitted_outputs"].items()})
    output_drift = unchanged(output_hashes)
    check("All emitted native outputs and viewer payloads are unchanged",
          not output_drift, output_drift)

    result = {
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "status": "pass" if all(c["pass"] for c in checks) else "fail",
        "scope": "Unaffected-input supplement for the completed cold-core dependency chain only.",
        "baseline_currentness_sha256": sha(currentness_path),
        "baseline_record_sha256": sha(baseline_path),
        "verifier_sha256": sha(Path(__file__)),
        "interface_path": changed_path,
        "interface_before_sha256": baseline["sha256"],
        "interface_after_sha256": sha(ROOT / changed_path),
        "affected_generator_input_records": affected_generators,
        "consumed_values": consumed_values,
        "checks": checks,
        "output_sha256": output_hashes,
        "dependency_geometry_current": all(c["pass"] for c in checks),
        "assembly_current": False,
        "production_print_released": False,
        "limits": [
            "The paired manifold span edit and native cartridge/plate fit are checked separately.",
            "This proof does not qualify the Box, whole enclosure, routes in a fresh pack, or sliced support removal.",
            "The original generation manifests retain the hashes actually loaded; this supplement records the unused assignment change."
        ],
    }
    destination = EVIDENCE / "pump-station-lead-currentness.json"
    destination.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({"status": result["status"], "checks": checks,
                      "output": str(destination.relative_to(ROOT))}, indent=2))
    raise SystemExit(0 if result["status"] == "pass" else 1)


if __name__ == "__main__":
    main()
