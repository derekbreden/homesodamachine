"""Read the dedicated ASSE drain against the actual installed appliance bodies.

Call write(enclosure_assembly._solids(a)) while the fresh assembly is in memory,
or run this file to read the exported enclosure-assembly.step. Connections share
material by design. This is nominal geometry evidence, not vent-flow qualification.
"""
from pathlib import Path
import hashlib
import json
import sys

ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "hardware/manifold-layout/drain-clearance-check.json"
NAMES = ("drain-barb-adapter", "drain-elbow", "drain-stem-reducer",
         "hose-drain-vent", "tube-drain-vent", "tube-fluid-18", "tube-fluid-28")
CONNECTED = {frozenset(pair) for pair in (
    ("hose-drain-vent", "asse1022-assembly"),
    ("hose-drain-vent", "drain-barb-adapter"),
    ("drain-barb-adapter", "drain-elbow"),
    ("drain-elbow", "drain-stem-reducer"),
    ("drain-stem-reducer", "tube-drain-vent"),
    ("tube-drain-vent", "bulkhead-drain"),
    ("tube-fluid-18", "valve-v-g"), ("tube-fluid-18", "bulkhead-flavor-a"),
    ("tube-fluid-28", "valve-v-j"), ("tube-fluid-28", "bulkhead-flavor-b"))}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(placed, output=OUTPUT):
    from OCP.BRepAdaptor import BRepAdaptor_Surface
    shapes = {name: value[0] if isinstance(value, tuple) else value
              for name, value in placed.items()}
    checks = {}
    for name in NAMES:
        body = shapes[name]
        bb = body.BoundingBox()
        row = {"valid": body.isValid(), "solids": len(body.Solids()), "neighbors": []}
        for other, obstacle in shapes.items():
            if other == name or frozenset((name, other)) in CONNECTED:
                continue
            ob = obstacle.BoundingBox()
            if any(getattr(bb, k + "max") + 1 < getattr(ob, k + "min")
                   or getattr(ob, k + "max") + 1 < getattr(bb, k + "min") for k in "xyz"):
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
                         and all(n["overlap_mm3"] <= 1e-5 for n in row["neighbors"]))
        checks[name] = row
    radii = {}
    for name in ("hose-drain-vent", "tube-drain-vent"):
        values = sorted({round(BRepAdaptor_Surface(face.wrapped).Torus().MajorRadius(), 7)
                         for face in shapes[name].Faces() if face.geomType() == "TORUS"})
        radii[name] = {"centerline_radii_mm": values,
                       "passed": ((bool(values) and min(values) >= 25 - 1e-6)
                                  or (name == "hose-drain-vent" and not values))}
    for name in ("tube-fluid-18", "tube-fluid-28"):
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
               ROOT / "hardware/reference/asse1022-assembly/asse1022_assembly.py"]
    result = {"scope": "Nominal exact B-rep clearance of the dedicated ASSE drain and its two rerouted flavor returns against every installed appliance body; connected interfaces are excluded. Pump occupied envelopes are read per component. Hardware tolerances, clamps, actual hose bending and vent performance require physical qualification.",
              "installed_body_count": len(shapes), "checks": checks, "bend_radii": radii,
              "source_sha256": {str(p.relative_to(ROOT)): sha(p) for p in sources},
              "passed": all(c["passed"] for c in checks.values()) and all(c["passed"] for c in radii.values())}
    output.write_text(json.dumps(result, indent=2) + "\n")
    print("ASSE drain clearance", result["passed"], flush=True)
    return result


if __name__ == "__main__":
    from _cadq_export import import_assembly
    sys.exit(0 if write(import_assembly(ROOT / "hardware/manifold-layout/enclosure-assembly.step"))["passed"] else 1)
