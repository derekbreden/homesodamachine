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
    ("tube-fluid-18", "valve-v-g"), ("tube-fluid-18", "flavor-reducer-v-g"), ("tube-fluid-18", "bulkhead-flavor-a"),
    ("tube-fluid-28", "valve-v-j"), ("tube-fluid-28", "flavor-reducer-v-j"), ("tube-fluid-28", "bulkhead-flavor-b"))}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def centerline_radii(segments):
    """Actual circular radii and every polynomial Bezier curvature extremum."""
    import math
    import numpy as np
    from numpy.polynomial import Polynomial as P

    values = []
    for segment in segments:
        if segment['kind'] == 'line':
            continue
        if segment['kind'] == 'arc':
            a, b, c = np.asarray(segment['points_mm'], dtype=float)
            values.append(math.dist(a, b)*math.dist(b, c)*math.dist(c, a)
                          / (2*np.linalg.norm(np.cross(b-a, c-a))))
            continue
        q = np.asarray(segment['control_points_mm'], dtype=float)
        if q.ndim != 2 or q.shape[1] != 3 or len(q) < 2:
            raise ValueError('A Bezier centerline needs at least two 3D control points')
        degree = len(q)-1
        basis = [math.comb(degree,i)*P([0.,1.])**i*P([1.,-1.])**(degree-i)
                 for i in range(degree+1)]
        v = [sum(b*q[i,k] for i,b in enumerate(basis)).deriv() for k in range(3)]
        a = [p.deriv() for p in v]
        cross = [v[1]*a[2]-v[2]*a[1], v[2]*a[0]-v[0]*a[2],
                 v[0]*a[1]-v[1]*a[0]]
        speed2 = sum(p*p for p in v)
        cross2 = sum(p*p for p in cross)
        stationary = cross2.deriv()*speed2-3*cross2*speed2.deriv()
        candidates = [0., 1., *[float(t.real) for t in stationary.roots()
                                if abs(t.imag) < 1.e-8 and 0. <= t.real <= 1.]]
        radii = [0. if speed2(t) <= 1.e-16 else
                 math.sqrt(max(0., speed2(t))**3/cross2(t))
                 for t in candidates if cross2(t) > 1.e-16 or speed2(t) <= 1.e-16]
        if radii:
            values.append(min(radii))
    return sorted(set(round(r, 7) for r in values))


def write(placed, output=OUTPUT, *, names=NAMES, route_specs=None):
    from OCP.BRepAdaptor import BRepAdaptor_Surface
    from OCP.BRepBndLib import BRepBndLib
    from OCP.Bnd import Bnd_Box
    meshcad = sys.modules.get("meshcad")

    def meshed(shape):
        """Whether the mesh kernel holds `shape` (hardware/scripts/meshcad)."""
        return meshcad is not None and meshcad.is_mesh(shape)

    def surface(face):
        return face._geomAdaptor() if meshed(face) else BRepAdaptor_Surface(face.wrapped)

    shapes = {name: value[0] if isinstance(value, tuple) else value
              for name, value in placed.items()}
    # Conservative bounds reject distant pairs; exact B-rep distance and
    # intersection assess every remaining pair, or the mesh kernel's on its bodies.
    # Compute these once per body.
    bounds = {}
    for name, shape in shapes.items():
        if meshed(shape):
            bb = shape.BoundingBox()
            bounds[name] = (bb.xmin, bb.ymin, bb.zmin, bb.xmax, bb.ymax, bb.zmax)
            continue
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
            leaf = other.rsplit('/', 1)[-1]
            wire_body = (leaf.startswith(('wire-', 'wiring-', 'terminal-'))
                         and not leaf.startswith(('wiring-junction-', 'terminal-J')))
            if name.startswith('tube-') and wire_body:
                continue
            ob = bounds[other]
            if any(bb[i + 3] + 1 < ob[i] or ob[i + 3] + 1 < bb[i]
                   for i in range(3)):
                continue
            # The scanned pump is a union of overlapping occupied envelopes.
            # Distribute the Boolean over those native solids.
            components = obstacle.Solids() if other == "g-ganen-pump" else [obstacle]
            gap = min(body.distance(part) for part in components)
            if meshed(body) and gap > 1e-6:
                overlap = 0.0               # the mesh kernel's Boolean of two bodies apart
            else:
                overlap = sum(fragment.Volume() for part in components
                              for fragment in part.intersect(body).Solids())
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
        spec = (route_specs or {}).get('drain-vent')
        values = (centerline_radii(spec['segments']) if spec else
                  sorted({round(surface(face).Torus().MajorRadius(), 7)
                          for face in shapes[name].Faces() if face.geomType() == "TORUS"}))
        radii[name] = {"centerline_radii_mm": values,
                       "method": ("Producer centerline; circular arcs and cubic curvature extrema"
                                  if spec else "Native toroidal faces"),
                       "passed": (bool(values) or bool(spec and spec['segments']))
                                 and (not values or min(values) >= 25 - 1e-6)}
    for name in set(names) & {"tube-fluid-18", "tube-fluid-28"}:
        surfaces = [surface(face).Torus()
                    for face in shapes[name].Faces() if face.geomType() == "TORUS"]
        values = sorted({round(surface.MajorRadius(), 7) for surface in surfaces})
        radii[name] = {"centerline_radii_mm": values,
                       "stock_minimum_mm": 25.0,
                       "passed": bool(values) and min(values) >= 25.0 - 1e-6}
    sources = [Path(__file__), ROOT / "hardware/manifold-layout/_drain.py",
               ROOT / "hardware/manifold-layout/enclosure_assembly.py",
               ROOT / "hardware/manifold-layout/_lines.py",
               ROOT / "hardware/manifold-layout/rear_plumbing.py",
               ROOT / "hardware/manifold-layout/above-core.json",
               ROOT / "hardware/reference/neofit-drain-bulkhead/neofit_drain_bulkhead.py",
               ROOT / "hardware/reference/asse1022-assembly/asse1022_assembly.py",
               ROOT / "hardware/printed-parts/asse-drain-adapter/asse_drain_adapter.py"]
    method = ("Nominal mesh clearance (every body within 0.005 mm of its exact surface)"
              if any(meshed(s) for s in shapes.values()) else "Nominal exact B-rep clearance")
    result = {"scope": method + " of the direct TPU ASSE sleeve and dedicated drain against the complete installed assembly population, including cold-core bodies and retained flavor returns. Connected interfaces are excluded. Tubes exclude flexible conductors and jackets as obstacles; connector housings remain. The white 4 mm return requires at least 1 mm to every other unconnected body. Pump occupied envelopes are read per component. The sleeve's expanded shape is an occupancy approximation. Hardware tolerances, zip-tie heads, actual bending, seals and vent performance are unmeasured.",
              "conservative_cold_core_envelope_included": "foam-assembly" in shapes,
              "installed_body_count": len(shapes), "checked_members": list(names), "checks": checks, "bend_radii": radii,
              "source_sha256": {str(p.relative_to(ROOT)): sha(p) for p in sources},
              "passed": all(c["passed"] for c in checks.values()) and all(c["passed"] for c in radii.values())}
    if output is not None:                  # None: the reading is the caller's to keep
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
    saved = json.loads(_facts.ARTIFACT.read_text())
    specs = {r['id']: r for r in saved['native_runs']}
    result = write({**placed, "foam-assembly": foam}, route_specs=specs)
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
