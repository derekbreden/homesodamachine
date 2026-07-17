"""Refactor sieve — invariants that must survive ongoing refactors.

Six complementary checks:

1. PUMP-CASE: build base + cap in-process, then check Volume +
   BoundingBox + CenterOfMass scalars against a pinned baseline. For
   refactors that change byte output (operation order shifts) but must
   preserve geometry.

2. RESERVOIR: build all 7 reservoir parts in-process (body + cap × 2
   sides, plus gasket, retaining ring, bulkhead seal), then check the
   same scalars against a pinned baseline. Same scalar-tolerance shape
   as pump-case — for the vocabulary refactor (range tuples, named
   anchors, chained CADQuery instead of _wp_at helpers).

3. SHELL: build all 4 touch-flo-shell pieces in-process (full + bottom +
   middle + top), then check Volume + BoundingBox + CenterOfMass scalars
   against a pinned baseline. Same scalar-tolerance shape as reservoir —
   for the +Y-up native-authoring rebase (drops the internal Z-up frame
   + boundary rotation wrappers).

4. FAUCET-PARTS: build the three small printed faucet parts in-process
   (mounting plate, mounting gasket, TPU o-ring), then check the same
   scalars against a pinned baseline.

5. FAUCET-ASSEMBLY: build the water dispense tube, both flavor tubes
   (+1/-1), and the lever blob in-process from the harvested faucet
   assembly script, then check the same scalars against a pinned
   baseline.

6. BYTE-HASHED STEPS: SHA256-compare frozen STEP outputs; bytes must
   match exactly. Spans the cold-core single parts (foam, copper,
   coil-mandrel, prv-shroud), the flavor parts (cap-sense sleeves,
   peristaltic tube), every valve-manifold tray and its named assembly,
   and the reference STEPs (beduan solenoid, JG bulkhead union,
   water-test cup, valve body, CO2 coupling, servo-valve mock, faucet
   assembly).

Module also exposes _solid_invariants(wp) + _compare_invariants(...) at
top level — volume + sorted bbox spans + sorted |COM| coords, compared
with the same volume/scalar tolerances as _compare_scalars.

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

# Frozen STEP outputs (single solids and named assemblies). Their geometry
# is not under a scalar-gated refactor, so bytes must match exactly. The
# scalar-gated parts (pump-case, reservoir, shell, faucet-parts) are checked
# by in-process scalars instead; faucet-assembly is checked both ways.
_byte_hashed_step_paths = [
    # cold-core
    "hardware/printed-parts/cold-core/foam-shell/foam-shell.step",
    "hardware/printed-parts/cold-core/foam-cap/foam-cap-top.step",
    "hardware/printed-parts/cold-core/foam-cap/foam-cap-bottom.step",
    "hardware/printed-parts/cold-core/foam-cap/foam-cap-lid-top.step",
    "hardware/printed-parts/cold-core/foam-cap/foam-cap-lid-bottom.step",
    "hardware/printed-parts/cold-core/foam-cap/foam-cap-gasket.step",
    "hardware/printed-parts/cold-core/copper-plugs/copper-plug-lower.step",
    "hardware/printed-parts/cold-core/copper-plugs/copper-plug-middle.step",
    "hardware/printed-parts/cold-core/copper-plugs/copper-plug-upper.step",
    "hardware/printed-parts/cold-core/copper-plugs/copper-plug-top.step",
    "hardware/printed-parts/cold-core/coil-mandrel/coil-mandrel.step",
    "hardware/printed-parts/cold-core/prv-shroud/prv-shroud.step",
    # flavor
    "hardware/printed-parts/flavor/cap-sense-sleeve/cap-sense-sleeve-pos-y.step",
    "hardware/printed-parts/flavor/cap-sense-sleeve/cap-sense-sleeve-neg-y.step",
    "hardware/printed-parts/flavor/peristaltic-tube/peristaltic-tube.step",
    # valve-manifold (each tray and its named assembly)
    "hardware/printed-parts/valve-manifold/bag-circuit-tray/bag-circuit-tray.step",
    "hardware/printed-parts/valve-manifold/bag-circuit-tray/bag-circuit-assembly.step",
    "hardware/printed-parts/valve-manifold/nozzle-gate-tray/nozzle-gate-tray.step",
    "hardware/printed-parts/valve-manifold/nozzle-gate-tray/nozzle-gate-assembly.step",
    "hardware/printed-parts/valve-manifold/source-select-tray/source-select-tray.step",
    "hardware/printed-parts/valve-manifold/source-select-tray/source-select-assembly.step",
    "hardware/printed-parts/valve-manifold/single-tray/single-tray.step",
    # reference
    "hardware/reference/touch-flo-faucet/valve-body-reference/touch-flo-valve-body-reference.step",
    "hardware/reference/co2-coupling-body/co2-coupling-body.step",
    "hardware/reference/touch-flo-faucet/faucet-assembly/touch-flo-faucet-assembly.step",
    "hardware/reference/servo-valve-mock/servo-valve-mock.step",
    "hardware/reference/servo-valve-mock/coupling-detail.step",
    "hardware/reference/beduan-solenoid/beduan-solenoid.step",
    "hardware/reference/jg-bulkhead-union/jg-bulkhead-union.step",
    "hardware/reference/water-test-cup/water-test-cup.step",
]

_cold_core_generators = [
    "hardware/printed-parts/cold-core/foam-shell/foam_shell.py",
    "hardware/printed-parts/cold-core/foam-cap/foam_cap.py",
    "hardware/printed-parts/cold-core/copper-plugs/copper_plugs.py",
    "hardware/printed-parts/cold-core/reservoir/reservoir.py",
    "hardware/printed-parts/cold-core/coil-mandrel/coil_mandrel.py",
    "hardware/printed-parts/cold-core/prv-shroud/prv_shroud.py",
]

_pump_case_generator = "hardware/printed-parts/flavor/pump-case/pump_case.py"

_shell_generator = "hardware/printed-parts/faucet/touch-flo-shell/touch_flo_shell.py"

_faucet_assembly_generator = "hardware/reference/touch-flo-faucet/faucet-assembly/faucet_assembly.py"

_servo_generators = [
    "hardware/reference/servo-valve-mock/coupling_detail.py",
    "hardware/reference/servo-valve-mock/servo_valve_mock.py",
]

_flavor_generators = [
    "hardware/printed-parts/flavor/cap-sense-sleeve/cap_sense_sleeve.py",
    "hardware/printed-parts/flavor/peristaltic-tube/peristaltic_tube.py",
]

# Each tray, then the assembly that imports it.
_valve_manifold_generators = [
    "hardware/printed-parts/valve-manifold/bag-circuit-tray/bag_circuit_tray.py",
    "hardware/printed-parts/valve-manifold/bag-circuit-tray/bag_circuit_assembly.py",
    "hardware/printed-parts/valve-manifold/nozzle-gate-tray/nozzle_gate_tray.py",
    "hardware/printed-parts/valve-manifold/nozzle-gate-tray/nozzle_gate_assembly.py",
    "hardware/printed-parts/valve-manifold/source-select-tray/source_select_tray.py",
    "hardware/printed-parts/valve-manifold/source-select-tray/source_select_assembly.py",
    "hardware/printed-parts/valve-manifold/single-tray/single_tray.py",
]

_reference_step_generators = [
    "hardware/reference/beduan-solenoid/beduan_solenoid.py",
    "hardware/reference/jg-bulkhead-union/jg_bulkhead_union.py",
    "hardware/reference/water-test-cup/water_test_cup.py",
]


def _sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def _file_hashes():
    return {p: _sha256(_repo / p) for p in _byte_hashed_step_paths}


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
    sys.path.insert(0, str(_repo / "hardware" / "scripts"))

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
    sys.path.insert(0, str(_repo / "hardware" / "scripts"))

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
    parts["bulkhead_seal_wet"] = _solid_scalars(mod.build_reservoir_bulkhead_seal(mod.bulkhead_seal_wet_od))
    parts["bulkhead_seal_dry"] = _solid_scalars(mod.build_reservoir_bulkhead_seal(mod.bulkhead_seal_dry_od))
    return parts


def _shell_scalars():
    """Build all 4 touch-flo-shell pieces in-process and return scalars.

    Imports the generator's build_shell* functions so we don't depend on
    the STEP round-trip (same approach as pump-case + reservoir). The
    bottom and middle splits accept an optional pre-built full shell to
    avoid rebuilding it three times; we pass the same `full` solid into
    both so the four scalars line up with what main() exports."""
    shell_dir = _repo / "hardware/printed-parts/faucet/touch-flo-shell"
    sys.path.insert(0, str(shell_dir))
    sys.path.insert(0, str(_repo / "hardware/printed-parts/faucet"))
    sys.path.insert(0, str(_repo / "hardware/printed-parts/cadlib"))
    sys.path.insert(0, str(_repo / "hardware" / "scripts"))

    # Force a fresh import (in case a prior call cached an older copy).
    import importlib
    if "touch_flo_shell" in sys.modules:
        del sys.modules["touch_flo_shell"]
    mod = importlib.import_module("touch_flo_shell")

    full = mod.build_shell()
    return {
        "full":   _solid_scalars(full),
        "bottom": _solid_scalars(mod.build_shell_bottom(full)),
        "middle": _solid_scalars(mod.build_shell_middle(full)),
        "top":    _solid_scalars(mod.build_shell_top(full)),
    }


def _faucet_parts_scalars():
    """Build the three small printed faucet parts in-process and return
    their scalars.

    Imports each generator's build_*() function so we don't depend on
    the STEP round-trip (same approach as pump-case + reservoir + shell)."""
    plate_dir = _repo / "hardware/printed-parts/faucet/touch-flo-mounting-plate"
    gasket_dir = _repo / "hardware/printed-parts/faucet/touch-flo-mounting-gasket"
    o_ring_dir = _repo / "hardware/printed-parts/faucet/touch-flo-tpu-o-ring"
    sys.path.insert(0, str(plate_dir))
    sys.path.insert(0, str(gasket_dir))
    sys.path.insert(0, str(o_ring_dir))
    sys.path.insert(0, str(_repo / "hardware/printed-parts/faucet"))
    sys.path.insert(0, str(_repo / "hardware/printed-parts/cadlib"))
    sys.path.insert(0, str(_repo / "hardware" / "scripts"))

    # Force fresh imports (in case a prior call cached older copies).
    import importlib
    for mod_name in ("touch_flo_mounting_plate",
                     "touch_flo_mounting_gasket",
                     "touch_flo_tpu_o_ring"):
        if mod_name in sys.modules:
            del sys.modules[mod_name]
    plate_mod = importlib.import_module("touch_flo_mounting_plate")
    gasket_mod = importlib.import_module("touch_flo_mounting_gasket")
    o_ring_mod = importlib.import_module("touch_flo_tpu_o_ring")

    return {
        "mounting_plate":  _solid_scalars(plate_mod.build_mounting_plate()),
        "mounting_gasket": _solid_scalars(gasket_mod.build_mounting_gasket()),
        "tpu_o_ring":      _solid_scalars(o_ring_mod.build_o_ring()),
    }


def _faucet_assembly_scalars():
    """Build the harvested faucet-assembly's tubes + lever in-process
    and return their scalars.

    Imports faucet_assembly and calls build_water_dispense_tube,
    build_flavor_tube(±1), and build_lever directly — bypassing the
    STEP round-trip (same approach as pump-case + reservoir + shell)."""
    assembly_dir = _repo / "hardware/reference/touch-flo-faucet/faucet-assembly"
    sys.path.insert(0, str(assembly_dir))
    sys.path.insert(0, str(_repo / "hardware/printed-parts/faucet/touch-flo-mounting-plate"))
    sys.path.insert(0, str(_repo / "hardware/printed-parts/faucet/touch-flo-mounting-gasket"))
    sys.path.insert(0, str(_repo / "hardware/printed-parts/faucet/touch-flo-shell"))
    sys.path.insert(0, str(_repo / "hardware/printed-parts/faucet"))
    sys.path.insert(0, str(_repo / "hardware/printed-parts/cadlib"))
    sys.path.insert(0, str(_repo / "hardware" / "scripts"))

    # Force a fresh import (in case a prior call cached an older copy).
    import importlib
    if "faucet_assembly" in sys.modules:
        del sys.modules["faucet_assembly"]
    mod = importlib.import_module("faucet_assembly")

    return {
        "water_tube":      _solid_scalars(mod.build_water_dispense_tube()),
        "flavor_tube_pos": _solid_scalars(mod.build_flavor_tube(+1)),
        "flavor_tube_neg": _solid_scalars(mod.build_flavor_tube(-1)),
        "lever":           _solid_scalars(mod.build_lever()),
    }


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


def _solid_invariants(wp):
    """Rotation- and reflection-invariant scalars for a single solid.

    Returns volume + sorted bbox spans + sorted |COM| coords:
      - volume_mm3:        unchanged from _solid_scalars.
      - bbox_spans_sorted: [xmax-xmin, ymax-ymin, zmax-zmin] sorted
                           ascending — invariant under axis permutation.
      - com_abs_sorted:    [|com.x|, |com.y|, |com.z|] sorted ascending
                           — invariant under axis permutation AND
                           per-axis sign flip.
    """
    solid = wp.val()
    bb = solid.BoundingBox()
    com = solid.Center()
    spans = [bb.xmax - bb.xmin, bb.ymax - bb.ymin, bb.zmax - bb.zmin]
    com_abs = [abs(com.x), abs(com.y), abs(com.z)]
    return {
        "volume_mm3": round(solid.Volume(), 4),
        "bbox_spans_sorted": [round(v, 4) for v in sorted(spans)],
        "com_abs_sorted":    [round(v, 4) for v in sorted(com_abs)],
    }


def _compare_invariants(expected, actual, tol_mm3=0.01, tol_mm=1e-3):
    """Walk the invariant dict (or dict-of-invariant-dicts); collect any
    field that drifted past tol. Same return shape as _compare_scalars.

    Volume gets tol_mm3; list entries in bbox_spans_sorted / com_abs_sorted
    get tol_mm."""
    drift = []
    def walk(path, e, a):
        if isinstance(e, dict):
            for k in e:
                walk(f"{path}.{k}" if path else k, e[k], a[k])
        elif isinstance(e, list):
            for i, (ev, av) in enumerate(zip(e, a)):
                walk(f"{path}[{i}]", ev, av)
        else:
            tol = tol_mm3 if path.endswith("volume_mm3") else tol_mm
            if abs(e - a) > tol:
                drift.append(f"{path}: expected {e}, actual {a} (Δ={a-e:+.6f})")
    walk("", expected, actual)
    return drift


def capture():
    """Capture current state as the baseline."""
    print("Capturing pump-case scalars...")
    pump = _pump_case_scalars()
    print("Capturing reservoir scalars...")
    reservoir = _reservoir_scalars()
    print("Capturing shell scalars...")
    shell = _shell_scalars()
    print("Capturing faucet-parts scalars...")
    faucet_parts = _faucet_parts_scalars()
    print("Capturing faucet-assembly scalars...")
    faucet_assembly = _faucet_assembly_scalars()
    print("Capturing byte-hashed STEP file hashes...")
    hashes = _file_hashes()
    baseline = {
        "pump_case": pump,
        "reservoir": reservoir,
        "shell": shell,
        "faucet_parts": faucet_parts,
        "faucet_assembly": faucet_assembly,
        "byte_hashed_steps": hashes,
    }
    _baseline_path.write_text(json.dumps(baseline, indent=2, sort_keys=True))
    print(f"Baseline written to {_baseline_path.relative_to(_repo)}")
    print(f"  Pump-case base volume: {pump['base']['volume_mm3']} mm³")
    print(f"  Pump-case cap volume:  {pump['cap']['volume_mm3']} mm³")
    print(f"  Reservoir parts captured:       {len(reservoir)}")
    print(f"  Shell pieces captured:          {len(shell)}")
    print(f"  Faucet-parts solids captured:   {len(faucet_parts)}")
    print(f"  Faucet-assembly solids captured:{len(faucet_assembly)}")
    print(f"  Byte-hashed STEPs hashed: {len(hashes)}")


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

    print("Regenerating shell STEPs...")
    ok, output = _run_generator(_shell_generator)
    if not ok:
        print(f"FAIL: shell generator\n{output}", file=sys.stderr)
        sys.exit(1)

    print("Regenerating faucet-assembly STEP...")
    ok, output = _run_generator(_faucet_assembly_generator)
    if not ok:
        print(f"FAIL: faucet-assembly generator\n{output}", file=sys.stderr)
        sys.exit(1)

    print("Regenerating servo-valve-mock STEPs...")
    for gen in _servo_generators:
        ok, output = _run_generator(gen)
        if not ok:
            print(f"FAIL: {gen}\n{output}", file=sys.stderr)
            sys.exit(1)

    for label, gens in (
        ("flavor", _flavor_generators),
        ("valve-manifold", _valve_manifold_generators),
        ("reference", _reference_step_generators),
    ):
        print(f"Regenerating {label} STEPs...")
        for gen in gens:
            ok, output = _run_generator(gen)
            if not ok:
                print(f"FAIL: {gen}\n{output}", file=sys.stderr)
                sys.exit(1)

    print("Checking byte-hashed STEP hashes...")
    drift = []
    expected_hashes = baseline["byte_hashed_steps"]
    actual_hashes = _file_hashes()
    for path in expected_hashes:
        if expected_hashes[path] != actual_hashes.get(path):
            drift.append((path, expected_hashes[path], actual_hashes.get(path)))
    if drift:
        print("BYTE-HASHED STEP DRIFT:", file=sys.stderr)
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

    print("Checking shell scalars...")
    actual_shell = _shell_scalars()
    shell_drift = _compare_scalars(baseline["shell"], actual_shell)
    if shell_drift:
        print("SHELL DRIFT:", file=sys.stderr)
        for line in shell_drift:
            print(f"  {line}", file=sys.stderr)
        sys.exit(1)
    print(f"  {len(actual_shell)} shell pieces match.")

    print("Checking faucet-parts scalars...")
    actual_faucet_parts = _faucet_parts_scalars()
    faucet_parts_drift = _compare_scalars(baseline["faucet_parts"], actual_faucet_parts)
    if faucet_parts_drift:
        print("FAUCET-PARTS DRIFT:", file=sys.stderr)
        for line in faucet_parts_drift:
            print(f"  {line}", file=sys.stderr)
        sys.exit(1)
    print(f"  {len(actual_faucet_parts)} faucet parts match.")

    print("Checking faucet-assembly scalars...")
    actual_faucet_assembly = _faucet_assembly_scalars()
    faucet_assembly_drift = _compare_scalars(baseline["faucet_assembly"], actual_faucet_assembly)
    if faucet_assembly_drift:
        print("FAUCET-ASSEMBLY DRIFT:", file=sys.stderr)
        for line in faucet_assembly_drift:
            print(f"  {line}", file=sys.stderr)
        sys.exit(1)
    print(f"  {len(actual_faucet_assembly)} faucet-assembly solids match.")

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
