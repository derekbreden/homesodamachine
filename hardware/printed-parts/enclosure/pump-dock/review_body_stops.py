"""Manual native review of the four integral cartridge body-stop lands.

Run only for the geometry question this record answers. Use --snapshots for
the pre-stop candidate review, or --final-export after final materialization
to append actual-artifact results while preserving that candidate record.
Neither mode constructs Box or the assembly graph, regenerates parts,
contacts a printer, or joins a build/check path.
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import json
from pathlib import Path
import sys
from types import SimpleNamespace

import cadquery as cq


ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
SOURCE = ROOT / "hardware/printed-parts/enclosure/enclosure/enclosure.py"
EXPECTED_INPUTS = {
    "enclosure-front-top.step": "ee0a7fed45aa58670beb0f91d3ed6be2dd550f6a7b587ef017f970b6344425a5",
    "enclosure-pump-cartridge.step": "775637bda29a6ab3517feac4ff47a6082c7dc9e0c98b07bd7e9937afb9035b27",
    "enclosure-pump-cap.step": "fac7b993816d8640e72b44ca5a6de5e901a9734ffd1e4ed0cec87f90e45a44d0",
    "enclosure-front-bottom.step": "980bafd2d6d95415de47af5a9321dfb510dbfef196e62b069fcc26bdea202ed5",
}
HELPER = "pump_cartridge_body_stops"
CONSTANTS = {
    "pump_body_stop_width", "pump_body_stop_height", "pump_body_stop_edge_inset"
}


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
    original_bytes = args.output.read_bytes()
    record = json.loads(original_bytes)
    if record.get("check_count") != 58 or len(record.get("checks", [])) != 58:
        raise ValueError("The existing 58-check candidate record must be retained")
    if args.record_key in record:
        raise ValueError("This final-export review key is already recorded; preserve it")
    original_items = dict(record)
    checks = []

    def check(name, passed, **data):
        row = dict(check=name, passed=bool(passed), **data)
        checks.append(row)
        print(json.dumps(row), flush=True)

    check("final source retains the candidate stop helper and constants",
          sha(scoped_source.encode()) == record["isolated_helper_and_constants_sha256"],
          isolated_helper_and_constants_sha256=sha(scoped_source.encode()))
    box_sha = None
    if args.box is not None:
        # Read the declared producer output; this does not derive placement or Box.
        sys.path[:0] = [str(ROOT / "hardware/scripts"), str(SOURCE.parent)]
        import enclosure as enc
        import _box_spec
        box_sha = sha(args.box.read_bytes())
        declared, _bounds = _box_spec.read(
            enc.Box, enc.Bound, (enc.Pack, enc.PortField, enc.Nameplate), path=args.box)
        actual_stops = enc.pump_cartridge_body_stops(declared)
        actual_bounds = [bounds(stop) for stop in actual_stops]
        check("current declared Box yields the same four body-stop regions",
              len(actual_stops) == len(stops)
              and all(abs(actual[axis][end] - reference[axis][end]) < 1e-8
                      for actual, reference in zip(actual_bounds, [bounds(stop) for stop in stops])
                      for axis in "xyz" for end in (0, 1)),
              box_stop_bounds_mm=actual_bounds)
    native, input_hashes = {}, {}
    for name in EXPECTED_INPUTS:
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
    record[args.record_key] = {
        "scope": "Canonical exported native STEP geometry read directly, with no stop fuse or other candidate construction; verifies surviving stock, contact, backing and sampled service extraction.",
        "manual_command": "tools/cad-venv/bin/python hardware/printed-parts/enclosure/pump-dock/review_body_stops.py --final-export"
                          + f" --record-key {args.record_key}"
                          + (" --box hardware/manifold-layout/enclosure-box.json" if args.box else ""),
        "prior_scoped_record_sha256_before_append": sha(original_bytes),
        "box_sha256": box_sha,
        "review_script_sha256": sha(Path(__file__).read_bytes()),
        "enclosure_source_sha256": sha(source_bytes),
        "isolated_helper_and_constants_sha256": sha(scoped_source.encode()),
        "input_step_sha256": input_hashes,
        "checks": checks,
        "check_count": len(checks),
        "failed_checks": [row["check"] for row in checks if not row["passed"]],
        "limitations": "This bounded review establishes geometry in the identified exported parts. The retained physical limitations and separate complete-assembly review still apply.",
    }
    if any(record[key] != value for key, value in original_items.items()):
        raise ValueError("Appending a final review must not alter the candidate record")
    args.output.write_text(json.dumps(record, indent=2) + "\n")
    result = record[args.record_key]
    print(json.dumps(dict(check_count=len(checks), failed_checks=result["failed_checks"])),
          flush=True)
    return bool(result["failed_checks"])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--snapshots", type=Path)
    mode.add_argument("--final-export", type=Path, nargs="?", const=SOURCE.parent,
                      help="Append direct native checks after final materialization; defaults to canonical exports")
    parser.add_argument("--record-key", default="final_export_review",
                        help="Append a distinct scope without replacing an earlier review")
    parser.add_argument("--box", type=Path,
                        help="Bind the current declared Box and compare its stop regions")
    parser.add_argument("--output", type=Path, default=HERE / "body-stop-native-review.json")
    args = parser.parse_args()
    source_bytes = SOURCE.read_bytes()
    source = source_bytes.decode()
    tree = ast.parse(source)
    nodes = [node for node in tree.body
             if (isinstance(node, ast.FunctionDef) and node.name == HELPER)
             or (isinstance(node, ast.Assign)
                 and any(isinstance(t, ast.Name) and t.id in CONSTANTS
                         for t in node.targets))]
    if len(nodes) != 4:
        raise ValueError("Expected exactly the stop helper and its three constants")
    scoped_source = "\n\n".join(ast.get_source_segment(source, n) for n in nodes)
    # Datum fixture from the retained default pack and native exports. Executing
    # this isolated AST cannot invoke the generator or alter the original file.
    datum = dict(cartridge_aft_y=79.269, fixed_wall_fore_y=79.515,
                 cap_split_z=214.925, cap_crown_z=284.174,
                 positive_cap_span_x=107.5, wall=3.0)
    env = {
        "_ybox": ybox, "wall": datum["wall"],
        "pump_cartridge_aft_y": lambda trays, plate: datum["cartridge_aft_y"],
        "bay_back_y": lambda plate: datum["fixed_wall_fore_y"],
        "_cap_x_span": lambda bay: (-datum["positive_cap_span_x"],
                                   datum["positive_cap_span_x"]),
        "cap_split_z": lambda trays: datum["cap_split_z"],
        "cap_crown_z": lambda box: datum["cap_crown_z"],
    }
    exec(compile(ast.Module(body=nodes, type_ignores=[]), str(SOURCE), "exec"), env)
    box = SimpleNamespace(pack=SimpleNamespace(pump_trays=None, collet_plate=None),
                          pump_bay=None)
    stops = env[HELPER](box)
    if args.final_export is not None:
        return final_export_review(args, source_bytes, scoped_source, datum, stops)
    checks = []

    def check(name, passed, **data):
        row = dict(check=name, passed=bool(passed), **data)
        checks.append(row)
        print(json.dumps(row), flush=True)

    native = {}
    input_hashes = {}
    for name, expected in EXPECTED_INPUTS.items():
        path = args.snapshots / name
        input_hashes[name] = sha(path.read_bytes())
        check(f"snapshot binding: {name}", input_hashes[name] == expected,
              sha256=input_hashes[name])
        if input_hashes[name] != expected:
            raise ValueError("This review requires the explicitly bound pre-stop snapshots")
        native[name] = cq.importers.importStep(str(path)).val()
    fixed = native["enclosure-front-top.step"]
    cradle = native["enclosure-pump-cartridge.step"]
    cap = native["enclosure-pump-cap.step"]
    bottom = native["enclosure-front-bottom.step"]
    check("four stop lands", len(stops) == 4)
    face_y = datum["cartridge_aft_y"]
    cradle_faces = [face for face in cradle.Faces()
                    if abs(face.BoundingBox().ymin - face_y) < 1e-6
                    and abs(face.BoundingBox().ymax - face_y) < 1e-6]
    check("retained cradle has nominal aft body-plane faces", bool(cradle_faces),
          planar_faces=len(cradle_faces), native_bounds_mm=bounds(cradle))
    contact_area = 0.0
    for index, stop in enumerate(stops, 1):
        bb = stop.BoundingBox()
        fore_faces = [face for face in stop.Faces()
                      if abs(face.BoundingBox().ymin - face_y) < 1e-6
                      and abs(face.BoundingBox().ymax - face_y) < 1e-6]
        area = sum(face.intersect(other).Area()
                   for face in fore_faces for other in cradle_faces)
        backing = stop.intersect(fixed).Volume()
        contact_area += area
        check(f"land {index}: full nominal body-face bearing", abs(area - 48.0) < 1e-5,
              contact_area_mm2=area, bounds_mm=bounds(stop))
        check(f"land {index}: complete 3 mm native wall backing", abs(backing - 144.0) < 1e-5,
              embedded_stock_mm3=backing)
        check(f"land {index}: no cap interference", stop.intersect(cap).Volume() < 1e-7,
              lateral_air_to_cap_mm=bb.xmin-cap.BoundingBox().xmax if bb.xmin > 0
              else cap.BoundingBox().xmin-bb.xmax)
    candidate = fixed.fuse(*stops).clean()
    added = candidate.cut(fixed).Volume()
    check("candidate fixed front-top is one valid solid",
          candidate.isValid() and len(candidate.Solids()) == 1,
          solids=len(candidate.Solids()))
    check("four short projections fill only the intended body air", abs(added - 47.232) < 1e-5,
          added_stock_mm3=added, total_contact_area_mm2=contact_area)
    for dy in (0.0, -0.01, -0.25, -1.0, -8.0, -20.0, -40.0):
        for name, shape in (("cradle", cradle), ("cap", cap)):
            moved = shape.translate((0, dy, 0))
            for fixed_name, stationary in (("front-top", candidate), ("front-bottom", bottom)):
                volume = moved.intersect(stationary).Volume()
                check(f"{name} withdrawal Y{dy:+.2f}: {fixed_name} clear", volume < 1e-6,
                      overlap_mm3=volume)
    all_stops = cq.Compound.makeCompound(list(stops))
    for dy in (0.001, 0.01, 0.10):
        volume = all_stops.intersect(cradle.translate((0, dy, 0))).Volume()
        check(f"positive Y overtravel {dy:.3f} meets lower-cradle lands",
              abs(volume - 192.0 * dy) < 1e-5, overlap_mm3=volume)
    for dz in (0.0, 1.0, 20.0, 40.0, 80.0, 110.0):
        volume = all_stops.intersect(cap.translate((0, 0, dz))).Volume()
        check(f"stop stock clear of cap Z removal {dz:.0f}", volume < 1e-6,
              overlap_mm3=volume)
    integration = "for stop in pump_cartridge_body_stops(box):\n                piece = piece.fuse(stop)"
    check("source integrates stops after fixed-wall cutters", integration in source
          and source.index(integration) > source.index("_stems.fixed_wall_cutter(box.pack.collet_plate"))
    record = {
        "review": "Four integral fixed-wall PET-GF body-stop lands",
        "scope": "Bounded native addition to explicitly hashed pre-stop exports; no Box or graph construction. The complete materialized assembly is reviewed separately.",
        "manual_command": "tools/cad-venv/bin/python hardware/printed-parts/enclosure/pump-dock/review_body_stops.py --snapshots .cache/pump-dock-engineering/mechanism/body-stop-review",
        "review_script_sha256": sha(Path(__file__).read_bytes()),
        "enclosure_source_sha256": sha(source_bytes),
        "isolated_helper_and_constants_sha256": sha(scoped_source.encode()),
        "isolated_helper_and_constants": scoped_source,
        "input_step_sha256": input_hashes,
        "datum_fixture_mm": datum,
        "stop_bounds_mm": [bounds(stop) for stop in stops],
        "load_path": "Four 4 x 12 mm fixed-wall fore faces bear directly on retained outboard lower-cradle aft stock. Each stop embeds 3 mm into continuous PET-GF wall. Two X stations and two Z rows resist seating moments. The cap, magnets, stem tips and TPU are not the rigid Y datum.",
        "factory_datum": "Seat the lower cradle against all four stop lands before match-setting bare moving magnet faces to cured fixed magnet faces. Nominal body air is 0.246 mm away from the stop lands.",
        "clearances_mm": {"lateral_to_full_height_cap_lane": 4.65,
                          "above_top_of_stem_guard": 20.751},
        "limitations": "Native contact, stock and extraction geometry establish the intended load path. They do not establish printed contact conformity, load capacity, creep life, magnetic force or wet sealing. Small edge finishing must preserve the four coplanar Y bearing datums.",
        "checks": checks,
        "check_count": len(checks),
        "failed_checks": [row["check"] for row in checks if not row["passed"]],
    }
    args.output.write_text(json.dumps(record, indent=2) + "\n")
    print(json.dumps(dict(check_count=len(checks), failed_checks=record["failed_checks"])), flush=True)
    return bool(record["failed_checks"])


if __name__ == "__main__":
    raise SystemExit(main())
