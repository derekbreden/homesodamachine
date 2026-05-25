"""Refactor sieve — invariants that must survive ongoing refactors.

Three complementary checks:

1. PUMP-CASE: build base + cap in-process, then check Volume +
   BoundingBox + CenterOfMass scalars against a pinned baseline. For
   refactors that change byte output (operation order shifts) but must
   preserve geometry.

2. RESERVOIR: build all 7 reservoir parts in-process (body + cap × 2
   sides, plus gasket, retaining ring, bulkhead seal), then check the
   same scalars against a pinned baseline. Same scalar-tolerance shape
   as pump-case — for the vocabulary refactor (range tuples, named
   anchors, chained CADQuery instead of _wp_at helpers).

3. COLD-CORE: SHA256-compare every downstream STEP file whose generator
   is NOT undergoing a vocabulary refactor; bytes must match exactly.

Run with:
    tools/cad-venv/bin/python hardware/printed-parts/cadlib/_refactor_sieve.py capture
    tools/cad-venv/bin/python hardware/printed-parts/cadlib/_refactor_sieve.py check
"""

import hashlib
import json
import subprocess
import sys
from pathlib import Path

_here = Path(__file__).resolve().parent
_repo = next(p for p in _here.parents if p.name == "homesodamachine")
_baseline_path = _here / "_refactor_sieve_baseline.json"

_cold_core_step_paths = [
    "hardware/printed-parts/cold-core/foam-shell/foam-shell.step",
    "hardware/printed-parts/cold-core/foam-cap/foam-cap-top.step",
    "hardware/printed-parts/cold-core/foam-cap/foam-cap-bottom.step",
    "hardware/printed-parts/cold-core/foam-cap/foam-cap-gasket.step",
    "hardware/printed-parts/cold-core/foam-cap/foam-cap-lid-top.step",
    "hardware/printed-parts/cold-core/foam-cap/foam-cap-lid-bottom.step",
    "hardware/printed-parts/cold-core/copper-plugs/copper-plug-lower.step",
    "hardware/printed-parts/cold-core/copper-plugs/copper-plug-middle.step",
    "hardware/printed-parts/cold-core/copper-plugs/copper-plug-upper.step",
    "hardware/printed-parts/cold-core/copper-plugs/copper-plug-top.step",
]

_cold_core_generators = [
    "hardware/printed-parts/cold-core/foam-shell/foam_shell.py",
    "hardware/printed-parts/cold-core/foam-cap/foam_cap.py",
    "hardware/printed-parts/cold-core/copper-plugs/copper_plugs.py",
    "hardware/printed-parts/cold-core/reservoir/reservoir.py",
]

_pump_case_generator = "hardware/printed-parts/flavor/pump-case/pump_case.py"


def _sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def _file_hashes():
    return {p: _sha256(_repo / p) for p in _cold_core_step_paths}


def _run_generator(rel_path):
    """Run a part's generator script. Returns (ok, output)."""
    py = _repo / "tools" / "cad-venv" / "bin" / "python"
    result = subprocess.run(
        [str(py), str(_repo / rel_path)],
        capture_output=True, text=True,
    )
    return result.returncode == 0, (result.stdout + result.stderr).strip()


def _pump_case_scalars():
    """Build pump-case base + cap in-process and return their scalars.

    Imports the generator's build_pump_case() so we don't depend on the
    STEP round-trip (which can subtly change vertex coords)."""
    pump_case_dir = _repo / "hardware/printed-parts/flavor/pump-case"
    sys.path.insert(0, str(pump_case_dir))
    sys.path.insert(0, str(_repo / "hardware/printed-parts/cadlib"))
    sys.path.insert(0, str(_repo / "hardware"))

    # Force a fresh import in case this script is re-run after edits.
    import importlib
    if "pump_case" in sys.modules:
        del sys.modules["pump_case"]
    mod = importlib.import_module("pump_case")

    base, cap = mod.build_pump_case()
    return {
        "base": _solid_scalars(base),
        "cap": _solid_scalars(cap),
    }


def _reservoir_scalars():
    """Build all 7 reservoir parts in-process and return their scalars.

    Imports the generator's build_reservoir_* functions so we don't
    depend on the STEP round-trip (same approach as pump-case)."""
    reservoir_dir = _repo / "hardware/printed-parts/cold-core/reservoir"
    sys.path.insert(0, str(reservoir_dir))
    sys.path.insert(0, str(_repo / "hardware/printed-parts/cadlib"))
    sys.path.insert(0, str(_repo / "hardware/printed-parts/cold-core"))
    sys.path.insert(0, str(_repo / "hardware"))

    # Force a fresh import (in case a prior call cached an older copy).
    import importlib
    if "reservoir" in sys.modules:
        del sys.modules["reservoir"]
    mod = importlib.import_module("reservoir")

    parts = {}
    for side, label in ((+1, "right"), (-1, "left")):
        parts[f"body_{label}"] = _solid_scalars(mod.build_reservoir_body(side=side))
        parts[f"cap_{label}"] = _solid_scalars(mod.build_reservoir_cap(side=side))
    parts["gasket"] = _solid_scalars(mod.build_reservoir_gasket(side=+1))
    parts["retaining_ring"] = _solid_scalars(mod.build_reservoir_retaining_ring())
    parts["bulkhead_seal"] = _solid_scalars(mod.build_reservoir_bulkhead_seal())
    return parts


def _solid_scalars(wp):
    solid = wp.val()
    bb = solid.BoundingBox()
    com = solid.Center()
    return {
        "volume_mm3": round(solid.Volume(), 4),
        "bbox": {
            "xmin": round(bb.xmin, 4), "xmax": round(bb.xmax, 4),
            "ymin": round(bb.ymin, 4), "ymax": round(bb.ymax, 4),
            "zmin": round(bb.zmin, 4), "zmax": round(bb.zmax, 4),
        },
        "com": {
            "x": round(com.x, 4), "y": round(com.y, 4), "z": round(com.z, 4),
        },
    }


def capture():
    """Capture current state as the baseline."""
    print("Capturing pump-case scalars...")
    pump = _pump_case_scalars()
    print("Capturing reservoir scalars...")
    reservoir = _reservoir_scalars()
    print("Capturing cold-core STEP file hashes...")
    hashes = _file_hashes()
    baseline = {
        "pump_case": pump,
        "reservoir": reservoir,
        "cold_core_hashes": hashes,
    }
    _baseline_path.write_text(json.dumps(baseline, indent=2, sort_keys=True))
    print(f"Baseline written to {_baseline_path.relative_to(_repo)}")
    print(f"  Pump-case base volume: {pump['base']['volume_mm3']} mm³")
    print(f"  Pump-case cap volume:  {pump['cap']['volume_mm3']} mm³")
    print(f"  Reservoir parts captured: {len(reservoir)}")
    print(f"  Cold-core STEPs hashed: {len(hashes)}")


def check():
    """Regenerate everything and compare against the baseline."""
    if not _baseline_path.exists():
        print(f"No baseline at {_baseline_path}; run capture first.", file=sys.stderr)
        sys.exit(2)
    baseline = json.loads(_baseline_path.read_text())

    print("Regenerating cold-core STEPs...")
    failures = []
    for gen in _cold_core_generators:
        ok, output = _run_generator(gen)
        if not ok:
            failures.append((gen, output))
    if failures:
        for gen, output in failures:
            print(f"FAIL: {gen}\n{output}", file=sys.stderr)
        sys.exit(1)

    print("Regenerating pump-case STEPs...")
    ok, output = _run_generator(_pump_case_generator)
    if not ok:
        print(f"FAIL: pump-case generator\n{output}", file=sys.stderr)
        sys.exit(1)

    print("Checking cold-core STEP hashes...")
    drift = []
    expected_hashes = baseline["cold_core_hashes"]
    actual_hashes = _file_hashes()
    for path in expected_hashes:
        if expected_hashes[path] != actual_hashes.get(path):
            drift.append((path, expected_hashes[path], actual_hashes.get(path)))
    if drift:
        print("COLD-CORE DRIFT:", file=sys.stderr)
        for path, exp, act in drift:
            print(f"  {path}\n    expected {exp}\n    actual   {act}", file=sys.stderr)
        sys.exit(1)
    print(f"  {len(actual_hashes)} STEPs match.")

    print("Checking pump-case scalars...")
    actual_pump = _pump_case_scalars()
    pump_drift = _compare_scalars(baseline["pump_case"], actual_pump)
    if pump_drift:
        print("PUMP-CASE DRIFT:", file=sys.stderr)
        for line in pump_drift:
            print(f"  {line}", file=sys.stderr)
        sys.exit(1)
    print(f"  base volume: {actual_pump['base']['volume_mm3']} mm³")
    print(f"  cap volume:  {actual_pump['cap']['volume_mm3']} mm³")

    print("Checking reservoir scalars...")
    actual_reservoir = _reservoir_scalars()
    reservoir_drift = _compare_scalars(baseline["reservoir"], actual_reservoir)
    if reservoir_drift:
        print("RESERVOIR DRIFT:", file=sys.stderr)
        for line in reservoir_drift:
            print(f"  {line}", file=sys.stderr)
        sys.exit(1)
    print(f"  {len(actual_reservoir)} reservoir parts match.")

    print("\nAll sieve checks pass.")


def _compare_scalars(expected, actual, tol_mm3=0.01, tol_mm=1e-3):
    """Walk the nested scalar dict; collect any field that drifted past tol.

    Volume gets a looser tolerance (0.01 mm³) because boolean-operation
    float ordering can produce sub-µL noise even when geometry is exactly
    identical. Bbox and COM coords use 1e-3 mm — any real geometric shift
    surfaces there before volume noise can mask it."""
    drift = []
    def walk(path, e, a):
        if isinstance(e, dict):
            for k in e:
                walk(f"{path}.{k}" if path else k, e[k], a[k])
        else:
            tol = tol_mm3 if path.endswith("volume_mm3") else tol_mm
            if abs(e - a) > tol:
                drift.append(f"{path}: expected {e}, actual {a} (Δ={a-e:+.6f})")
    walk("", expected, actual)
    return drift


if __name__ == "__main__":
    if len(sys.argv) != 2 or sys.argv[1] not in {"capture", "check"}:
        print(__doc__, file=sys.stderr)
        sys.exit(2)
    {"capture": capture, "check": check}[sys.argv[1]]()
