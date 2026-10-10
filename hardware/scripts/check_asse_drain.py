"""Read the dedicated ASSE drain against the actual installed appliance bodies.

Call write with the pack and cold-core bodies while the fresh assembly is in memory,
or run this file to read the exported enclosure-assembly.step. Connections share
material by design. This is nominal geometry evidence, not vent-flow qualification.
"""
from pathlib import Path
import hashlib
import json
import sys

ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "hardware/manifold-layout/drain-clearance-check.json"
NAMES = ("asse-drain-adapter", "tube-drain-vent", "tube-fluid-18", "tube-fluid-28")
CONNECTED = {frozenset(pair) for pair in (
    ("asse-drain-adapter", "asse1022-assembly"),
    ("asse-drain-adapter", "tube-drain-vent"),
    ("tube-drain-vent", "bulkhead-drain"),
    ("tube-fluid-18", "valve-v-g"), ("tube-fluid-18", "bulkhead-flavor-a"),
    ("tube-fluid-28", "valve-v-j"), ("tube-fluid-28", "bulkhead-flavor-b"))}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(placed, output=OUTPUT, *, names=NAMES):
    from OCP.BRepAdaptor import BRepAdaptor_Surface
    from OCP.BRepBndLib import BRepBndLib
    from OCP.Bnd import Bnd_Box
    shapes = {name: value[0] if isinstance(value, tuple) else value
              for name, value in placed.items()}
    # Conservative bounds reject distant pairs; exact B-rep distance and
    # intersection assess every remaining pair. Compute these once per body.
    bounds = {}
    for name, shape in shapes.items():
        box = Bnd_Box()
        BRepBndLib.Add_s(shape.wrapped, box, False)
        bounds[name] = box.Get()
    checks = {}
    for name in names:
        body = shapes[name]
        bb = bounds[name]
        required_gap = 1.0 if name == "tube-drain-vent" else 0.0
        row = {"valid": body.isValid(), "solids": len(body.Solids()),
               "minimum_unconnected_gap_mm": required_gap, "neighbors": []}
        for other, obstacle in shapes.items():
            if other == name or frozenset((name, other)) in CONNECTED:
                continue
            ob = bounds[other]
            if any(bb[i + 3] + 1 < ob[i] or ob[i + 3] + 1 < bb[i]
                   for i in range(3)):
                continue
            # The scanned pump is a union of overlapping occupied envelopes.
            # Distribute the Boolean over those native solids.
            components = obstacle.Solids() if other == "g-ganen-pump" else [obstacle]
            overlap = sum(fragment.Volume() for part in components
                          for fragment in part.intersect(body).Solids())
            gap = min(body.distance(part) for part in components)
            row["neighbors"].append({"name": other, "gap_mm": round(gap, 7),
                                     "overlap_mm3": round(overlap, 7)})
            print(name, other, f"gap {gap:.4f}; overlap {overlap:.6f}", flush=True)
        row["passed"] = (row["valid"] and row["solids"] == 1
                         and all(n["overlap_mm3"] <= 1e-5
                                 and n["gap_mm"] >= required_gap - 1e-6
                                 for n in row["neighbors"]))
        checks[name] = row
    radii = {}
    for name in set(names) & {"tube-drain-vent"}:
        values = sorted({round(BRepAdaptor_Surface(face.wrapped).Torus().MajorRadius(), 7)
                         for face in shapes[name].Faces() if face.geomType() == "TORUS"})
        radii[name] = {"centerline_radii_mm": values,
                       "passed": bool(values) and min(values) >= 25 - 1e-6}
    for name in set(names) & {"tube-fluid-18", "tube-fluid-28"}:
        surfaces = [BRepAdaptor_Surface(face.wrapped).Torus()
                    for face in shapes[name].Faces() if face.geomType() == "TORUS"]
        values = sorted({round(surface.MajorRadius(), 7) for surface in surfaces
                         if surface.Location().Y() >= 280})
        radii[name] = {"new_return_centerline_radii_mm": values,
                       "existing_front_route_scope": "Front supports and their existing bends retained.",
                       "passed": bool(values) and min(values) >= 25.4 - 1e-6}
    sources = [Path(__file__), ROOT / "hardware/manifold-layout/_drain.py",
               ROOT / "hardware/manifold-layout/enclosure_assembly.py",
               ROOT / "hardware/manifold-layout/_lines.py",
               ROOT / "hardware/reference/neofit-drain-bulkhead/neofit_drain_bulkhead.py",
               ROOT / "hardware/reference/asse1022-assembly/asse1022_assembly.py",
               ROOT / "hardware/printed-parts/asse-drain-adapter/asse_drain_adapter.py"]
    result = {"scope": "Nominal exact B-rep clearance of the direct TPU ASSE sleeve and dedicated drain against the complete installed assembly population, including cold-core bodies and retained flavor returns. Connected interfaces are excluded. The white 4 mm return requires at least 1 mm to every unconnected body. Pump occupied envelopes are read per component. The sleeve's expanded shape is an occupancy approximation. Hardware tolerances, zip-tie heads, actual bending, seals and vent performance are unmeasured.",
              "conservative_cold_core_envelope_included": "foam-assembly" in shapes,
              "installed_body_count": len(shapes), "checked_members": list(names), "checks": checks, "bend_radii": radii,
              "source_sha256": {str(p.relative_to(ROOT)): sha(p) for p in sources},
              "passed": all(c["passed"] for c in checks.values()) and all(c["passed"] for c in radii.values())}
    output.write_text(json.dumps(result, indent=2) + "\n")
    print("ASSE drain clearance", result["passed"], flush=True)
    return result


def main():
    """Read the exported bodies and restore the pack's conservative foam envelope."""
    from _cadq_export import import_assembly
    import _facts

    sys.path.insert(0, str(ROOT / "hardware/manifold-layout"))
    import enclosure_assembly as assembly

    facts = _facts.read()
    if not facts.agrees_with_card() or facts.agrees_with_step() is not True:
        raise ValueError("The saved assembly, scorecard and placement facts disagree")
    expected = json.loads(_facts.ARTIFACT.read_text())["bodies"]["foam-assembly"]
    foam, _ = assembly.build_foam(expected[1])
    bounds = foam.BoundingBox()
    actual = [getattr(bounds, k) for k in ("xmin", "ymin", "zmin", "xmax", "ymax", "zmax")]
    if any(abs(a - b) > 1e-5 for a, b in zip(actual, expected)):
        raise ValueError("The native foam envelope does not match the saved placement")
    native = ROOT / "hardware/manifold-layout/enclosure-assembly.step"
    placed = import_assembly(native)
    if not any(name.startswith("cold-core/") for name in placed):
        raise ValueError("The exported assembly contains no cold-core bodies")
    result = write({**placed, "foam-assembly": foam})
    result["serialized_input_sha256"] = {
        str(p.relative_to(ROOT)): sha(p)
        for p in (native, assembly.FOAM_STEP)
    }
    result["placement_fact_bounds_mm"] = expected
    result["placement_fact_bounds_sha256"] = hashlib.sha256(
        json.dumps(expected, separators=(",", ":")).encode()).hexdigest()
    result["foam_envelope_matches_saved_placement"] = True
    OUTPUT.write_text(json.dumps(result, indent=2) + "\n")
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
