"""Manual review of lower-shell core-stop ownership using an existing Box.

The snapshot mode builds only two lower quadrants in scratch. The final-export
mode only reads actual parts and an existing Box, appending its results without
changing earlier evidence. Neither derives Box, constructs the assembly graph,
regenerates other parts, or joins a recurring check path.
"""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from pathlib import Path
import sys
import time

import cadquery as cq


ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
ENC = ROOT / "hardware/printed-parts/enclosure/enclosure"
NAMES = ("front-bottom", "back-bottom", "front-top", "back-top",
         "pump-cartridge", "pump-cap")


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def bounds(shape):
    bb = shape.BoundingBox()
    return {a: [getattr(bb, a + "min"), getattr(bb, a + "max")] for a in "xyz"}


def final_export_review(args, enc, box_spec):
    original_bytes = args.output.read_bytes()
    record = json.loads(original_bytes)
    original_items = dict(record)
    if args.record_key in record:
        raise ValueError("This review scope already exists; preserve it")
    box, _bounds = box_spec.read(
        enc.Box, enc.Bound, (enc.Pack, enc.PortField, enc.Nameplate), path=args.box)
    box_sha = sha(args.box)
    source_sha = sha(Path(enc.__file__))
    paths = {name: args.final_export / f"enclosure-{name}.step" for name in NAMES}
    input_hashes = {name: sha(path) for name, path in paths.items()}
    front = cq.importers.importStep(str(paths["front-bottom"])).val()
    back = cq.importers.importStep(str(paths["back-bottom"])).val()
    checks = []

    def check(name, passed, **data):
        row = dict(check=name, passed=bool(passed), **data)
        checks.append(row)
        print(json.dumps(row), flush=True)

    for name, solid in (("front-bottom", front), ("back-bottom", back)):
        check(f"actual exported {name}: one valid solid",
              solid.isValid() and len(solid.Solids()) == 1, solids=len(solid.Solids()))
    overlap = front.intersect(back).Volume()
    check("actual exported lower-shell pair is clear", overlap < 1e-6,
          overlap_mm3=overlap)
    station_data = []
    for cx, cy, radius in box.pack.core_stops:
        side = 1.0 if cx > 0 else -1.0
        slip = enc.core_stop_slip / 2.0
        face_y = cy - radius - slip
        x0, x1 = sorted((cx - side * radius, cx))
        z0, z1 = box.inner[4], box.inner[4] + enc.core_stop_rise
        check(f"exported stop X{cx:+.3f}: bearing station belongs to front column",
              enc._piece_bands(box, "front-bottom")[0] <= face_y <= box.y_joint,
              forward_bearing_y_mm=face_y)
        web = enc._ybox(x0, x1, face_y-enc.core_stop_web, face_y, z0, z1)
        missing = web.cut(front).Volume()
        check(f"exported stop X{cx:+.3f}: full forward web",
              missing < 1e-5, missing_web_mm3=missing,
              web_volume_mm3=web.Volume(), web_depth_mm=enc.core_stop_web,
              stop_height_mm=enc.core_stop_rise)
        root = enc._ybox(x0, x1, face_y-enc.core_stop_web, face_y,
                         z0-enc.wall, z0)
        missing_root = root.cut(front).Volume()
        check(f"exported stop X{cx:+.3f}: full integral 3 mm floor root",
              missing_root < 1e-5, missing_root_mm3=missing_root,
              root_stock_mm3=root.Volume())
        flat_faces = [f for f in web.Faces()
                      if abs(f.BoundingBox().ymin-face_y) < 1e-6
                      and abs(f.BoundingBox().ymax-face_y) < 1e-6]
        flat_area = sum(f.intersect(front).Area() for f in flat_faces)
        check(f"exported stop X{cx:+.3f}: full flat bearing face",
              abs(flat_area-radius*enc.core_stop_rise) < 1e-5,
              bearing_area_mm2=flat_area)
        bore = enc._zcyl(radius+slip, cx, cy, z0, z1)
        quarter = enc._ybox(min(cx, cx+side*(radius+slip)),
                           max(cx, cx+side*(radius+slip)), face_y, cy, z0, z1)
        curved = [f.intersect(quarter) for f in bore.Faces() if f.geomType() == "CYLINDER"]
        bare_area = sum(f.Area() for f in curved)
        lower, upper = enc.y_stack(box.inner)
        for x_in, sx in ((box.inner[0], 1.0), (box.inner[1], -1.0)):
            for rows, depth in ((lower, enc.y_stack_low_depth),
                                (upper, enc.y_stack_high_depth)):
                for who, za, zb, ga, gb in rows:
                    if who.startswith("back"):
                        air = enc._y_knuckle_air(x_in, sx, box.y_joint, who, za, zb, ga, gb, depth)
                        curved = [f.cut(air) for f in curved]
        after_knuckle_area = sum(f.Area() for f in curved)
        tail_air = enc._core_stop_handhold_air(box.inner, (cx, cy, radius), box.y_joint)
        if tail_air is not None:
            curved = [f.cut(tail_air) for f in curved]
        expected = sum(f.Area() for f in curved)
        present = sum(f.intersect(front).Area() for f in curved)
        check(f"exported stop X{cx:+.3f}: full rounded face outside required knuckle air",
              abs(present-expected) < 1e-5, present_area_mm2=present,
              expected_area_mm2=expected,
              required_knuckle_clearance_area_mm2=bare_area-after_knuckle_area,
              required_handhold_tail_clearance_area_mm2=after_knuckle_area-expected)
        # Read the actual two parts in a finite handhold-mate footprint. The
        # window excludes the ordinary Y-seam air and the curved boundary so
        # the distance measures the stop tail beneath the rear roof itself.
        roof = enc._handhold_levels(box.inner)[1]
        gap = enc._y_stack_gap(False, True)
        xa, xb = sorted((side*(abs(cx)+radius+.75001),
                         side*(abs(cx)+radius+2.99999)))
        window = enc._ybox(xa, xb, box.y_joint+enc.fits.slip+1e-5,
                           cy-1e-5, roof-2.0, roof+2.0)
        tail, mate = front.intersect(window), back.intersect(window)
        native_gap = tail.distance(mate)
        check(f"exported stop X{cx:+.3f}: actual rear-handhold roof running/support gap",
              abs(native_gap-gap) < 1e-5
              and abs(tail.BoundingBox().zmax-(roof-gap)) < 1e-6
              and abs(mate.BoundingBox().zmin-roof) < 1e-6,
              native_gap_mm=native_gap, required_gap_mm=gap,
              front_tail_bounds_mm=bounds(tail), back_roof_bounds_mm=bounds(mate))
        station_data.append(dict(x=cx, corner_axis_y=cy, forward_bearing_y=face_y,
                                 radius=radius, rise=enc.core_stop_rise, forward_web=enc.core_stop_web))
    check("identified source, Box and six native exports stayed stable",
          source_sha == sha(Path(enc.__file__)) and box_sha == sha(args.box)
          and all(input_hashes[n] == sha(p) for n, p in paths.items()))
    record[args.record_key] = {
        "scope": "Direct read of final canonical lower native parts and current declared Box, including both stop-tail/rear-handhold mate clearances. No candidate fusion, part construction, Box derivation or graph write.",
        "manual_command": "tools/cad-venv/bin/python hardware/printed-parts/enclosure/pump-dock/review_core_stops.py --final-export"
                          + f" --record-key {args.record_key} --box hardware/manifold-layout/enclosure-box.json",
        "prior_scoped_record_sha256_before_append": hashlib.sha256(original_bytes).hexdigest(),
        "source_sha256": source_sha,
        "review_script_sha256": sha(Path(__file__)),
        "box_sha256": box_sha,
        "input_step_sha256": input_hashes,
        "station_datums_mm": station_data,
        "checks": checks,
        "check_count": len(checks),
        "failed_checks": [r["check"] for r in checks if not r["passed"]],
        "limitations": "Geometry/contact/root stock and lower-pair clearance only. Earlier scoped analytical and physical limitations remain unchanged; complete appliance review is separate.",
    }
    if any(record[key] != value for key, value in original_items.items()):
        raise ValueError("Earlier scoped evidence must remain unchanged")
    args.output.write_text(json.dumps(record, indent=2)+"\n")
    result = record[args.record_key]
    print(json.dumps(dict(check_count=len(checks), failed_checks=result["failed_checks"])), flush=True)
    return bool(result["failed_checks"])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--snapshots", type=Path)
    mode.add_argument("--final-export", type=Path, nargs="?", const=ENC)
    parser.add_argument("--box", type=Path, default=ROOT / "hardware/manifold-layout/enclosure-box.json")
    parser.add_argument("--record-key", default="final_export_review")
    parser.add_argument("--output", type=Path, default=HERE / "core-stop-native-review.json")
    args = parser.parse_args()
    sys.path[:0] = [str(ROOT / "hardware/scripts"), str(ENC)]
    import enclosure as enc
    import _box_spec
    if args.final_export is not None:
        return final_export_review(args, enc, _box_spec)

    box_path = args.snapshots / "enclosure-box.json"
    box, declared_bounds = _box_spec.read(
        enc.Box, enc.Bound, (enc.Pack, enc.PortField, enc.Nameplate), path=box_path)
    enc.BOUNDS[:] = declared_bounds
    enc._last_box[0] = box
    paths = {name: args.snapshots / f"enclosure-{name}.step" for name in NAMES}
    input_hashes = {name: sha(path) for name, path in paths.items()}
    source_hash = sha(Path(enc.__file__))
    pieces = {name: cq.importers.importStep(str(path)).val() for name, path in paths.items()}
    checks = []

    def check(name, passed, **data):
        row = dict(check=name, passed=bool(passed), **data)
        checks.append(row)
        print(json.dumps(row), flush=True)

    old_clash = pieces["front-bottom"].intersect(pieces["back-bottom"])
    initial = {"overlap_mm3": old_clash.Volume(), "bounds_mm": bounds(old_clash),
               "regions": [{"overlap_mm3": s.Volume(), "bounds_mm": bounds(s)}
                           for s in old_clash.Solids()]}
    print(json.dumps(dict(initial_native_bottom_pair=initial)), flush=True)
    generated = {}
    for name in ("front-bottom", "back-bottom"):
        started = time.monotonic()
        print(f"Building only {name} from the existing declared Box", flush=True)
        piece = enc.build_piece(box, *name.split("-")).val()
        path = args.snapshots / f"corrected-enclosure-{name}.step"
        cq.exporters.export(piece, str(path))
        generated[name] = {"step_sha256": sha(path), "seconds": time.monotonic() - started}
        pieces[name] = piece
        check(f"corrected {name}: one valid solid", piece.isValid() and len(piece.Solids()) == 1,
              solids=len(piece.Solids()), bounds_mm=bounds(piece), **generated[name])
    for a, b in itertools.combinations(NAMES, 2):
        volume = pieces[a].intersect(pieces[b]).Volume()
        check(f"corrected six-piece pair: {a} / {b}", volume < 1e-6, overlap_mm3=volume)
    station_data = []
    for cx, cy, radius in box.pack.core_stops:
        side = 1.0 if cx > 0 else -1.0
        slip = enc.core_stop_slip / 2.0
        face_y = cy - radius - slip
        lap = cx - side * radius
        x0, x1 = sorted((lap, cx))
        z0, z1 = box.inner[4], box.inner[4] + enc.core_stop_rise
        front_band = enc._piece_bands(box, "front-bottom")
        back_band = enc._piece_bands(box, "back-bottom")
        check(f"core stop X{cx:+.3f}: bearing face belongs to front-bottom only",
              front_band[0] <= face_y <= front_band[1]
              and not back_band[0] <= face_y <= back_band[1],
              corner_axis_y_mm=cy, forward_bearing_y_mm=face_y)
        web = enc._ybox(x0, x1, face_y - enc.core_stop_web, face_y, z0, z1)
        missing = web.cut(pieces["front-bottom"]).Volume()
        check(f"core stop X{cx:+.3f}: complete 6 mm forward web retained",
              missing < 1e-5, missing_web_mm3=missing, web_volume_mm3=web.Volume())
        bearing_faces = [f for f in web.Faces()
                         if abs(f.BoundingBox().ymin - face_y) < 1e-6
                         and abs(f.BoundingBox().ymax - face_y) < 1e-6]
        area = sum(f.intersect(pieces["front-bottom"]).Area() for f in bearing_faces)
        check(f"core stop X{cx:+.3f}: full flat bearing face retained",
              abs(area - radius * enc.core_stop_rise) < 1e-5, bearing_area_mm2=area)
        bore = enc._zcyl(radius + slip, cx, cy, z0, z1)
        quarter = enc._ybox(min(cx, cx + side * (radius + slip)),
                           max(cx, cx + side * (radius + slip)),
                           face_y, cy, z0, z1)
        curved = [f.intersect(quarter) for f in bore.Faces() if f.geomType() == "CYLINDER"]
        bare_area = sum(f.Area() for f in curved)
        # The fixed corner stack owns a small part of the round's trailing end.
        # Its real source-defined mating clearance remains open in front-bottom.
        lower, upper = enc.y_stack(box.inner)
        for x_in, sx in ((box.inner[0], 1.0), (box.inner[1], -1.0)):
            for rows, depth in ((lower, enc.y_stack_low_depth),
                                (upper, enc.y_stack_high_depth)):
                for who, za, zb, ga, gb in rows:
                    if who.startswith("back"):
                        air = enc._y_knuckle_air(x_in, sx, box.y_joint, who, za, zb, ga, gb, depth)
                        curved = [f.cut(air) for f in curved]
        expected_area = sum(f.Area() for f in curved)
        present_area = sum(f.intersect(pieces["front-bottom"]).Area() for f in curved)
        check(f"core stop X{cx:+.3f}: complete rounded face outside corner-knuckle clearance",
              abs(present_area - expected_area) < 1e-5,
              untrimmed_quarter_area_mm2=bare_area,
              required_knuckle_clearance_area_mm2=bare_area-expected_area,
              expected_area_mm2=expected_area, present_area_mm2=present_area)
        station_data.append(dict(x=cx, corner_axis_y=cy, radius=radius,
                                 forward_bearing_y=face_y, web_fore_y=face_y-enc.core_stop_web))
    check("source and native snapshot inputs stable during review",
          source_hash == sha(Path(enc.__file__))
          and all(sha(paths[n]) == digest for n, digest in input_hashes.items())
          and sha(box_path) == sha(ROOT / "hardware/manifold-layout/enclosure-box.json"))
    record = {
        "review": "Lower-shell core-stop ownership and complete functional bearing geometry",
        "scope": "Two lower quadrants built directly from the identified existing Box; remaining four native pieces read from snapshots. No placement, other-piece or assembly-graph generation.",
        "source_sha256": source_hash,
        "review_script_sha256": sha(Path(__file__)),
        "box_sha256": sha(box_path),
        "input_step_sha256": input_hashes,
        "initial_native_bottom_pair": initial,
        "station_datums_mm": station_data,
        "generated_scratch_parts": generated,
        "functional_load_path": "Both full front corner stops and their 6 mm forward webs belong to the front-bottom slab, selected by their working forward bearing plane. Their rounded axes may extend aft across the Y seam. The front-bottom handhold backing is part of the same piece; back-bottom retains its own cleared handhold and mating joinery.",
        "reconciliation": "The identified current native inputs contain the measured bottom-pair overlap. An earlier zero-overlap result does not establish clearance for these changed placement/export inputs. Current canonical assembly clearance requires rematerializing both affected lower quadrants and reading their actual exported pair.",
        "limitations": "Native geometry establishes stock, modeled clearance and intended load path; it does not establish printed fit, support removal, strength or lifetime.",
        "checks": checks,
        "check_count": len(checks),
        "failed_checks": [r["check"] for r in checks if not r["passed"]],
    }
    args.output.write_text(json.dumps(record, indent=2) + "\n")
    print(json.dumps(dict(check_count=len(checks), failed_checks=record["failed_checks"])), flush=True)
    return bool(record["failed_checks"])


if __name__ == "__main__":
    raise SystemExit(main())
