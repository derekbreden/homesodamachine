"""Build published-size purchased JG adapter envelopes from local frozen dimensions.

Run manually through the repository CAD queue. No production module is imported.
"""
from pathlib import Path
import hashlib
import json
import math

import cadquery as cq
import numpy as np

HERE = Path(__file__).resolve().parent


def cylinder(radius, y0, y1):
    return cq.Solid.makeCylinder(radius, y1-y0, cq.Vector(0, y0, 0), cq.Vector(0, 1, 0))


def hexagon(y0, y1):
    # Published max19.1 clips a regular17.5AF hex's corners.
    plane = cq.Plane(origin=(0, y0, 0), xDir=(1, 0, 0), normal=(0, 1, 0))
    polygon = cq.Workplane(plane).polygon(6, 17.5 / math.cos(math.pi/6)).extrude(y1-y0).val()
    return polygon.intersect(cylinder(19.1/2, y0, y1))


def male():
    # MouthY0, thread shoulder13.7, thread tip28.0; collet released.
    solid = cylinder(7, 0, 1.5).fuse(cylinder(7.5, 1.5, 3.0),
        cylinder(8.5, 3.0, 9.0), hexagon(9.0, 13.7), cylinder(6.85, 13.7, 28.0))
    return solid.clean().cut(cylinder(3.175, -.01, 15.7)).cut(cylinder(2.2, 15.7, 28.01))


def female(thread_diameter=13.7, engagement=11.0):
    # MouthY0; threaded socket faceY32. Profile transitions are occupancy estimates.
    solid = cylinder(6.75, 0, 1.5).fuse(cylinder(7.5, 1.5, 17.2), hexagon(17.2, 32))
    return (solid.clean().cut(cylinder(3.175, -.01, 15.7))
            .cut(cylinder(2.65, 15.7, 32.01))
            .cut(cylinder(thread_diameter/2, 32-engagement, 32.01)))


def save(name, solid):
    v, triangles = solid.tessellate(.04, .15)
    points = np.array([p.toTuple() for p in v], dtype=np.float32)
    faces = np.array(triangles, dtype=np.int32)
    path = HERE / "geometry" / (name + ".npz")
    np.savez_compressed(path, v=points, f=faces)
    cq.exporters.export(solid, str(HERE / "geometry" / (name + ".step")))
    return {"file": str(path.relative_to(HERE)), "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            "bounds_mm": [points.min(0).tolist(), points.max(0).tolist()],
            "vertices": len(points), "triangles": len(faces)}


def main():
    (HERE / "geometry").mkdir(exist_ok=True)
    result = {"fitting-pi010822s": save("fitting-pi010822s", male()),
              "fitting-pi450822s": save("fitting-pi450822s", female())}
    # Male shanks are inside their metal hosts at the selected nominal full projection.
    external_male = male().intersect(cylinder(20, 0, 13.7))
    for name, face_y in [("co2-adapter-regulator-in", 0.), ("co2-adapter-check-in", -20.)]:
        result[name] = save(name, external_male.translate((0, face_y-13.7, 0)))
    for name, metal_tip, engagement, diameter in [
        ("co2-adapter-regulator-out", 63.65, 9.18, 14.2),
        ("co2-adapter-check-out", 20., 11., 13.7)]:
        # Canonical parent flow+Y. Female mouth is its upstream Y0 when standalone,
        # so turn it half a turn to put its mouth beyond the host's male tip.
        part = female(diameter, engagement).rotate((0, 0, 0), (1, 0, 0), 180)
        part = part.translate((0, metal_tip+32-engagement, 0))
        result[name] = save(name, part)
    record = {
        "units": "mm", "meshes": result,
        "publication_supported": {
            "male": {"mouth_to_thread_shoulder_mm": 13.7, "thread_projection_mm": 14.3,
                     "max_diameter_mm": 19.1, "across_flats_mm": 17.5, "bore_mm": 4.4},
            "female": {"overall_mm": 32., "thread_section_mm": 14.8,
                       "body_diameter_mm": 15., "max_diameter_mm": 19.1,
                       "across_flats_mm": 17.5, "bore_mm": 5.3},
            "tube_insertion_released_collet_mm": 15.7,
        },
        "estimates": [
            "Undimensioned collet, hex and body transition lengths are envelope estimates.",
            "Simple cylindrical NPT envelopes and socket cavities do not reproduce the thread form or sealing mechanism.",
            "Selected male inlet engagement is the full14.3mm published thread projection, placing its shoulder at the metal female face. Actual NPT make-up can stand the shoulder further out.",
            "Selected female outlet engagements retain source11mm on Gasher and scanned-stub-bounded9.18mm on regulator. Actual engagement is not measured.",
            "Both fitting mouth datums and15.7mm tube insertion use the sheet's released-collet position; resting collet travel is not established for these exact parts.",
        ],
    }
    (HERE / "adapter-dimensions.json").write_text(json.dumps(record, indent=2) + "\n")
    print(json.dumps({k: v["bounds_mm"] for k, v in result.items()}, indent=2))


if __name__ == "__main__":
    main()
