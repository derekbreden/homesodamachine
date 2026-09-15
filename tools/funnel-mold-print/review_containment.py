"""Read the liquid spaces in the funnel mold's STEP and exported STL.

The cavity mouth is capped for the open-cavity reading. The assembled reading
caps the fill and vent mouths and seals the rod passage. In each case the
liquid must occupy one closed region separate from the surrounding air.
"""

import argparse
import hashlib
import json
from pathlib import Path

import cadquery as cq
import numpy as np
import trimesh


ROOT = Path(__file__).resolve().parents[2]
EPS = 0.02


def box(width, depth, bottom, top):
    return (cq.Workplane("XY").box(width, depth, top-bottom,
            centered=(True, True, False)).translate((0, 0, bottom)).val())


def cylinder(radius, bottom, top, x, y):
    return cq.Solid.makeCylinder(radius, top-bottom, cq.Vector(x, y, bottom))


def mesh_of(shape):
    vertices, faces = shape.tessellate(0.005, 0.05)
    mesh = trimesh.Trimesh(vertices=[v.toTuple() for v in vertices],
                           faces=faces, process=True)
    mesh.update_faces(mesh.nondegenerate_faces())
    mesh.remove_unreferenced_vertices()
    return mesh


def seal_mesh(shape):
    """The soft entry seal overlaps independently tessellated contact faces."""
    mesh = mesh_of(shape)
    copies = [mesh]
    for axis in range(3):
        for direction in (-1, 1):
            displacement = np.zeros(3)
            displacement[axis] = direction*EPS
            copies.append(mesh.copy().apply_translation(displacement))
    return trimesh.boolean.union(copies, engine="manifold")


def read_geometry(models):
    info = json.loads((models / "design.json").read_text())
    shapes = {name: cq.importers.importStep(str(models / f"{name}.step")).val()
              for name in ("cavity", "core", "rod", "funnel")}
    assembly = cq.importers.importStep(str(models / "assembly.step")).val()
    shapes["seal"] = min(assembly.Solids(), key=lambda solid: solid.Volume())
    assert abs(shapes["seal"].Volume()-info["volume_ml"]["seal"]*1000) < 0.0001
    parting = info["parting_z_mm"]
    flange = info["flange_thickness_mm"]
    rod = shapes["rod"].BoundingBox()
    x, y = (rod.xmin+rod.xmax)/2, (rod.ymin+rod.ymax)/2
    witness = (x, y, rod.zmin-3)
    cavity_box = shapes["cavity"].BoundingBox()
    width = max(cavity_box.xlen, cavity_box.ylen)+2
    surrounding = box(width+24, width+24, -2, parting+flange+8)
    mouth_cap = box(width, width, parting-EPS, parting+flange+2)
    ports = info["ports"]
    openings = [(ports["fill_xy_mm"], ports["fill_diameter_mm"])]
    openings += [(xy, ports["vent_diameter_mm"]) for xy in ports["vent_xy_mm"]]
    port_caps = [cylinder(diameter/2+EPS, parting+flange-EPS,
                          parting+flange+1, *xy) for xy, diameter in openings]
    return shapes, surrounding, mouth_cap, port_caps+[shapes["seal"]], witness


def step_reading(surrounding, tools, witness, cast):
    remainder = surrounding.cut(*tools).clean()
    assert remainder.isValid(), "invalid STEP complement"
    solids = remainder.Solids()
    containing = [solid for solid in solids if solid.isInside(cq.Vector(*witness), 1e-6)]
    outside = (-surrounding.BoundingBox().xlen/2+1, 0, 0)
    retained = [solid for solid in containing
                if not solid.isInside(cq.Vector(*outside), 1e-6)]
    target = cast.cut(*tools)
    missing = target.cut(retained[0]).Volume() if retained else target.Volume()
    return {
        "contained": len(retained) == 1 and missing < 0.0001,
        "regions": len(solids),
        "region_volumes_ml": sorted(round(s.Volume()/1000, 6) for s in solids),
        "retained_volume_ml": round(retained[0].Volume()/1000, 6) if retained else None,
        "casting_outside_retained_mm3": round(missing, 6),
    }


def stl_reading(surrounding, tools, witness, cast):
    for mesh in tools:
        assert mesh.is_watertight and mesh.is_winding_consistent, "invalid STL input"
    remainder = trimesh.boolean.difference([surrounding, *tools], engine="manifold")
    assert remainder.is_watertight and remainder.is_winding_consistent, "invalid STL complement"
    # A surrounding region has a positive outer boundary and negative boundaries
    # around the tooling. A separately enclosed liquid region is positive too.
    surfaces = remainder.split(only_watertight=False)
    positive = [surface for surface in surfaces if surface.volume > 0.0001]
    negligible = [abs(float(surface.volume)) for surface in surfaces
                  if abs(surface.volume) <= 0.0001]
    outside = np.array([[-surrounding.extents[0]/2+1, 0, 0]])
    retained = [surface for surface in positive
                if surface.contains(np.array([witness]))[0]
                and not surface.contains(outside)[0]]
    target = trimesh.boolean.difference([cast, *tools], engine="manifold")
    if retained:
        escaped = trimesh.boolean.difference([target, retained[0]], engine="manifold")
        missing = float(escaped.volume) if len(escaped.faces) else 0.0
    else:
        missing = float(target.volume)
    return {
        "contained": len(retained) == 1 and missing < 0.001,
        "positive_regions": len(positive),
        "boundary_volumes_ml": sorted(round(s.volume/1000, 6) for s in surfaces
                                      if abs(s.volume) > 0.0001),
        "negligible_boundaries": {"count": len(negligible),
                                  "max_abs_volume_mm3": max(negligible, default=0.0)},
        "retained_volume_ml": round(retained[0].volume/1000, 6) if retained else None,
        "casting_outside_retained_mm3": round(missing, 6),
    }


def review(models):
    shapes, surround, mouth_cap, plugs, witness = read_geometry(models)
    meshes = {name: trimesh.load(models / f"{name}.stl", force="mesh", process=True)
              for name in ("cavity", "core")}
    results = {}
    for label, pieces in (
        ("cavity", [shapes["cavity"], mouth_cap]),
        ("assembled", [shapes["cavity"], shapes["core"], shapes["rod"], *plugs]),
    ):
        results[f"{label}_step"] = step_reading(surround, pieces, witness, shapes["funnel"])
    surround_mesh = mesh_of(surround)
    for label, pieces in (
        ("cavity", [meshes["cavity"], mesh_of(mouth_cap)]),
        ("assembled", [meshes["cavity"], meshes["core"], mesh_of(shapes["rod"]),
                       *[mesh_of(plug) for plug in plugs[:-1]], seal_mesh(shapes["seal"])]),
    ):
        results[f"{label}_stl"] = stl_reading(surround_mesh, pieces, witness,
                                              mesh_of(shapes["funnel"]))
    return {
        "models": str(models.resolve()),
        "method": "Exact B-rep and manifold mesh complements; capped intended openings; no layer-height sampling.",
        "seal_mesh_contact_overlap_mm": EPS,
        "seal_mesh_contact_overlap_scope": "Actual entry seal only; translations along each axis.",
        "witness_mm": list(witness),
        "sha256": {name: hashlib.sha256((models/name).read_bytes()).hexdigest()
                   for name in ("cavity.step", "cavity.stl", "core.step", "core.stl", "rod.step", "funnel.step", "assembly.step", "design.json")},
        "readings": results,
        "contained": all(result["contained"] for result in results.values()),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--models", type=Path,
                        default=ROOT/"hardware/printed-parts/zone-c/funnel-mold")
    parser.add_argument("--output", type=Path)
    parser.add_argument("--expect-leaks", action="store_true",
                        help="Require all four readings to detect leaks in a regression fixture.")
    args = parser.parse_args()
    result = review(args.models)
    encoded = json.dumps(result, indent=2)+"\n"
    if args.output:
        args.output.write_text(encoded)
    print(encoded, end="", flush=True)
    if args.expect_leaks:
        assert all(not reading["contained"] for reading in result["readings"].values()), result
    else:
        assert result["contained"], "The intended liquid space communicates with outside air."


if __name__ == "__main__":
    main()
