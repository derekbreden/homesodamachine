"""Manual current-artifact review of the four integral cartridge body stops.

Reads canonical native exports and their declared Box. It does not construct
Box, regenerate parts, write an assembly graph, contact a printer, or join a
build/check path. Run for the specific contact/backing/extraction question.
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import json
from pathlib import Path
import sys

import cadquery as cq

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
SOURCE = ROOT / "hardware/printed-parts/enclosure/enclosure/enclosure.py"
INPUT_NAMES = tuple(f"enclosure-{name}.step" for name in
                    ("front-top", "pump-cartridge", "pump-cap", "front-bottom"))


def ybox(x0, x1, y0, y1, z0, z1):
    return cq.Solid.makeBox(x1 - x0, y1 - y0, z1 - z0, cq.Vector(x0, y0, z0))

def sha(data):
    return hashlib.sha256(data).hexdigest()

def bounds(shape):
    bb = shape.BoundingBox()
    return {axis: [getattr(bb, axis + "min"), getattr(bb, axis + "max")]
            for axis in "xyz"}

def plane_faces(shape, y):
    return [face for face in shape.Faces()
            if abs(face.BoundingBox().ymin - y) < 1e-6
            and abs(face.BoundingBox().ymax - y) < 1e-6]


def final_export_review(args, source_bytes, scoped_source, datum, stops):
    """Read canonical parts as exported, without constructing/fusing stop stock."""
    checks = []

    def check(name, passed, **data):
        row = dict(check=name, passed=bool(passed), **data)
        checks.append(row)
        print(json.dumps(row), flush=True)

    check("declared helper yields four complete 4 by 12 mm bearing lands",
          len(stops) == 4 and all(abs(stop.BoundingBox().xlen - 4.0) < 1e-8
                                   and abs(stop.BoundingBox().zlen - 12.0) < 1e-8
                                   for stop in stops))
    check("current body air and integral stop depth follow the declared frame",
          abs(datum["fixed_wall_fore_y"] - datum["cartridge_aft_y"] - datum["body_gap"]) < 1e-8
          and all(abs(stop.BoundingBox().ylen - datum["wall"] - datum["body_gap"]) < 1e-8
                  for stop in stops), body_air_mm=datum["body_gap"])
    box_sha = sha(args.box.read_bytes())
    native, input_hashes = {}, {}
    for name in INPUT_NAMES:
        path = args.final_export / name
        input_hashes[name] = sha(path.read_bytes())
        native[name] = cq.importers.importStep(str(path)).val()
    fixed = native["enclosure-front-top.step"]
    cradle = native["enclosure-pump-cartridge.step"]
    cap = native["enclosure-pump-cap.step"]
    bottom = native["enclosure-front-bottom.step"]
    check("exported front-top is one valid solid",
          fixed.isValid() and len(fixed.Solids()) == 1,
          solids=len(fixed.Solids()))
    fixed_faces = plane_faces(fixed, datum["cartridge_aft_y"])
    cradle_faces = plane_faces(cradle, datum["cartridge_aft_y"])
    for index, stop in enumerate(stops, 1):
        bb = stop.BoundingBox()
        missing = stop.cut(fixed).Volume()
        backing_region = ybox(bb.xmin, bb.xmax, datum["fixed_wall_fore_y"],
                              datum["fixed_wall_fore_y"] + datum["wall"],
                              bb.zmin, bb.zmax)
        backing = backing_region.intersect(fixed).Volume()
        faces = plane_faces(stop, datum["cartridge_aft_y"])
        fixed_area = sum(face.intersect(other).Area()
                         for face in faces for other in fixed_faces)
        cradle_area = sum(face.intersect(other).Area()
                          for face in faces for other in cradle_faces)
        check(f"exported land {index}: complete stop stock survived later cuts",
              missing < 1e-5, missing_stock_mm3=missing)
        check(f"exported land {index}: complete 3 mm integral wall backing",
              abs(backing - 144.0) < 1e-5, embedded_stock_mm3=backing)
        check(f"exported land {index}: full coplanar fixed/cradle contact faces",
              abs(fixed_area - 48.0) < 1e-5 and abs(cradle_area - 48.0) < 1e-5,
              fixed_contact_face_mm2=fixed_area, cradle_contact_face_mm2=cradle_area)
    for dy in (0.0, -0.01, -0.25, -8.0, -40.0):
        for name, shape in (("cradle", cradle), ("cap", cap)):
            moved = shape.translate((0, dy, 0))
            for fixed_name, stationary in (("front-top", fixed), ("front-bottom", bottom)):
                volume = moved.intersect(stationary).Volume()
                check(f"exported {name} withdrawal Y{dy:+.2f}: {fixed_name} clear",
                      volume < 1e-6, overlap_mm3=volume)
    for dy in (0.001, 0.01):
        volume = fixed.intersect(cradle.translate((0, dy, 0))).Volume()
        check(f"exported fixed wall arrests lower-cradle overtravel {dy:.3f}",
              abs(volume - 192.0 * dy) < 1e-5, overlap_mm3=volume)
    cap_bb = cap.BoundingBox()
    cap_lane_air = min(cap_bb.xmin + 98.0, 98.0 - cap_bb.xmax)
    check("exported cap remains outside both stop X lanes for any Z lift",
          cap_lane_air > 0.0, minimum_lateral_air_mm=cap_lane_air)
    check("canonical native inputs remained stable throughout this review",
          all(sha((args.final_export / name).read_bytes()) == digest
              for name, digest in input_hashes.items())
          and (args.box is None or sha(args.box.read_bytes()) == box_sha))
    record = {
        "scope": "Canonical exported native STEP geometry read directly, with no stop fuse or other candidate construction; verifies surviving stock, contact, backing and sampled service extraction.",
        "manual_command": "HSM_NO_BUILD_LOCK=1 tools/cad-venv/bin/python hardware/printed-parts/enclosure/pump-dock/review_body_stops.py --final-export",
        "box_sha256": box_sha,
        "review_script_sha256": sha(Path(__file__).read_bytes()),
        "enclosure_source_sha256": sha(source_bytes),
        "isolated_helper_and_constants_sha256": sha(scoped_source.encode()),
        "input_step_sha256": input_hashes,
        "dimensions": datum,
        "stop_bounds_mm": [bounds(stop) for stop in stops],
        "checks": checks,
        "check_count": len(checks),
        "failed_checks": [row["check"] for row in checks if not row["passed"]],
        "limitations": "This bounded review establishes geometry in the identified exported parts. The retained physical limitations and separate complete-assembly review still apply.",
    }
    args.output.write_text(json.dumps(record, indent=2) + "\n")
    result = record
    print(json.dumps(dict(check_count=len(checks), failed_checks=result["failed_checks"])),
          flush=True)
    return bool(result["failed_checks"])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--final-export", type=Path, nargs="?", const=SOURCE.parent,
                        default=SOURCE.parent)
    parser.add_argument("--box", type=Path,
                        default=ROOT / "hardware/manifold-layout/enclosure-box.json")
    parser.add_argument("--output", type=Path, default=HERE / "body-stop-native-review.json")
    args = parser.parse_args()
    sys.path[:0] = [str(ROOT / "hardware/scripts"), str(SOURCE.parent)]
    import enclosure as enc
    import _box_spec
    declared, _ = _box_spec.read(enc.Box, enc.Bound,
                                 (enc.Pack, enc.PortField, enc.Nameplate), path=args.box)
    source_bytes = SOURCE.read_bytes()
    source = source_bytes.decode()
    nodes = [n for n in ast.parse(source).body
             if isinstance(n, ast.FunctionDef) and n.name == "pump_cartridge_body_stops"
             or isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id in {
                 "pump_body_stop_width", "pump_body_stop_height", "pump_body_stop_edge_inset"}
                 for t in n.targets)]
    scoped_source = "\n\n".join(ast.get_source_segment(source, n) for n in nodes)
    trays, plate = declared.pack.pump_trays, declared.pack.collet_plate
    datum = dict(cartridge_aft_y=enc.pump_cartridge_aft_y(trays, plate),
                 fixed_wall_fore_y=enc.bay_back_y(plate),
                 body_gap=enc.cap_kiss, cap_split_z=enc.cap_split_z(trays),
                 cap_crown_z=enc.cap_crown_z(declared), wall=enc.wall)
    return final_export_review(args, source_bytes, scoped_source, datum,
                               enc.pump_cartridge_body_stops(declared))


if __name__ == "__main__":
    raise SystemExit(main())
