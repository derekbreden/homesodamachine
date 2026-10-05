"""Read the straight rod, open guide and complete funnel from exported STEP."""

import hashlib
import json
import sys
from pathlib import Path

import cadquery as cq
from OCP.BRepAdaptor import BRepAdaptor_Surface

ROOT = Path(__file__).resolve().parents[2]
MODELS = ROOT / "hardware/printed-parts/zone-c/funnel-mold"
FINISHED = ROOT / "hardware/printed-parts/zone-c/funnel/funnel.step"
EPS = 0.0001
sys.path.insert(0, str(ROOT / "hardware/scripts"))
from _cadq_export import import_assembly


def cylinder(radius, bottom, top, x, y):
    return cq.Solid.makeCylinder(radius, top-bottom, cq.Vector(x, y, bottom))


def main():
    info = json.loads((MODELS / "design.json").read_text())
    shapes = {name: cq.importers.importStep(str(MODELS / (name+".step"))).val()
              for name in ("rod", "core", "cavity", "funnel")}
    assert all(s.isValid() and len(s.Solids()) == 1 for s in shapes.values())
    rod = shapes["rod"]
    rb = rod.BoundingBox()
    x, y = (rb.xmin+rb.xmax)/2, (rb.ymin+rb.ymax)/2
    assert abs(rb.zlen-25) < EPS
    faces = rod.Faces()
    assert sorted(f.geomType() for f in faces) == ["CYLINDER", "PLANE", "PLANE"]
    radius = BRepAdaptor_Surface(next(f.wrapped for f in faces
                                   if f.geomType() == "CYLINDER")).Cylinder().Radius()
    assert abs(radius-3) < EPS
    guide = info["rod_support"]
    assert guide["guide_open"] and abs(guide["guide_diameter_mm"]-6.4) < EPS
    neck = guide["guide_top_mm"]-8
    end = rb.zmin+info["rod_socket"]["depth_mm"]
    through = cylinder(3.19, neck, shapes["core"].BoundingBox().zmax+1, x, y)
    open_guide_overlap = through.intersect(shapes["core"]).Volume()
    assert open_guide_overlap < EPS
    movements = []
    for lift in (0, .5, 2, 5, 8, 25, 50):
        moving = rod.translate((0, 0, lift))
        overlaps = {name: moving.intersect(shapes[name]).Volume()
                    for name in ("core", "cavity", "funnel")}
        assert max(overlaps.values()) < EPS, (lift, overlaps)
        movements.append({"upward_travel_mm": lift, "interference_mm3": overlaps})
    bore = cylinder(3, end, neck-.02, x, y)
    assert bore.intersect(shapes["funnel"]).Volume() < EPS
    rings = []
    for z in (end+.1, (end+neck)/2, neck-.1):
        empty = bool(shapes["funnel"].isInside(cq.Vector(x+2.99, y, z), 1e-7))
        wall = bool(shapes["funnel"].isInside(cq.Vector(x+3.01, y, z), 1e-7))
        assert not empty and wall
        rings.append({"z_mm": z, "radius_2_99_is_silicone": empty,
                      "radius_3_01_is_silicone": wall})
    finished = cq.importers.importStep(str(FINISHED)).val()
    shift = shapes["funnel"].BoundingBox().zmin-finished.BoundingBox().zmin
    cast = shapes["funnel"].translate((0, 0, -shift))
    differences = {"casting_minus_finished_mm3": cast.cut(finished).Volume(),
                   "finished_minus_casting_mm3": finished.cut(cast).Volume()}
    assert max(differences.values()) < EPS, differences
    machine = ROOT / "hardware/manifold-layout/enclosure-assembly.step"
    installed = {name: shape for name, (shape, _color) in import_assembly(str(machine)).items()}
    placed = finished.translate((0, 164.55, 349))
    assert placed.cut(installed["funnel"]).Volume() < EPS
    assert installed["funnel"].cut(placed).Volume() < EPS
    stub = installed["funnel-drain-stub"]
    top = stub.BoundingBox().zmax
    reach = top-placed.BoundingBox().zmin
    common = stub.intersect(placed)
    ring = cylinder(3.185, top-reach-.001, top+.001, x, 164.55+y).cut(
        cylinder(2.99, top-reach-.002, top+.002, x, 164.55+y))
    outside = common.cut(ring).Volume()
    assert common.Volume() > 0 and outside < EPS
    frame_interference = placed.intersect(installed["funnel-frame"]).Volume()
    assert frame_interference < EPS
    files = [MODELS / (name+".step") for name in shapes]
    files += [MODELS / "design.json", MODELS / "funnel_mold.py", FINISHED,
              FINISHED.with_suffix(".py"), machine, Path(__file__)]
    result = {
        "checked_date": "2026-10-05",
        "method": "Independent exported STEP reads: analytic rod faces, full guide passage, axial movement and complete casting CSG comparison.",
        "tooling": "Two printed PETG shells and one stock straight 6 x 25 mm stainless steel rod.",
        "rod": {"diameter_mm": 2*radius, "length_mm": rb.zlen,
                "faces": [f.geomType() for f in faces]},
        "open_core_guide_overlap_mm3": open_guide_overlap,
        "rod_motion": movements,
        "straight_bore_probes": rings,
        "whole_casting_difference": differences,
        "flange_plan_mm": info["flange_plan_mm"],
        "tube_od_mm": 6.35,
        "bore_diameter_mm": 6.0,
        "nominal_diametral_interference_mm": .35,
        "tube_engagement_mm": reach,
        "installed_drain_joint": {"nominal_contact_volume_mm3": common.Volume(),
                                  "contact_outside_bore_mm3": outside,
                                  "frame_interference_mm3": frame_interference},
        "scope": "Geometry and tooling completeness; cast release and seal behavior are physical outcomes.",
        "sha256": {p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
                   for p in files},
        "passed": True,
    }
    (MODELS / "rod-check.json").write_text(json.dumps(result, indent=2)+"\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
