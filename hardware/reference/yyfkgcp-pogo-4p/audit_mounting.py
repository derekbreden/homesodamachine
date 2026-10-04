"""Read the current exported pogo seats and bound the drawing tolerance stack.

This writes a local design audit. It does not regenerate CAD, slice a print or
turn nominal geometry into physical acceptance.
"""
from pathlib import Path
import hashlib
import json
import sys

import cadquery as cq

HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p / "hardware/scripts").is_dir())
ENC = ROOT / "hardware/printed-parts/enclosure/enclosure"
sys.path[:0] = [str(ROOT / "hardware/scripts"), str(ENC),
               str(ROOT / "hardware/manifold-layout")]
import enclosure as e
import enclosure_assembly as assembly
import _box_spec
from materialize_pump_cartridge import _declared_box

# Seller's male drawing, observed on the Prime 4-pin-with-ear listing.
OVERALL_TIP_HEIGHT_TOL = 0.15
BODY_DEPTH_TOL = 0.05
FACE_FLUSH_TOL = 0.05


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    box, _bounds, box_path = _declared_box(_box_spec, e)
    e._last_box[0] = box
    paths = {name: ENC / f"enclosure-{name}.step"
             for name in ("front-top", "pump-cap", "pump-cartridge")}
    pieces = {name: cq.importers.importStep(str(path)).val()
              for name, path in paths.items()}
    contacts = assembly.build_pump_contacts(box)
    bound = assembly._pump_contact_bound(contacts, pieces, box)
    if not bound.ok:
        raise ValueError(bound._asdict())
    cuts = {"front-top": e._pump_contact_fixed_cuts(box),
            "pump-cap": e._pump_contact_cap_cuts(box)}
    rows = [{"check": "nominal installed contacts", "pass": bound.ok,
             "reading": bound._asdict()}]
    for name, shape in pieces.items():
        valid = shape.isValid() and len(shape.Solids()) == 1
        rows.append({"check": f"{name} native solid", "pass": valid})
        if not valid:
            raise ValueError(name)
    for name, cutters in cuts.items():
        volumes = [abs(pieces[name].intersect(cutter).Volume())
                   for cutter in cutters]
        passed = max(volumes) < 1e-5
        rows.append({"check": f"{name} current seat and lead passages",
                     "pass": passed, "cutter_overlap_mm3": volumes})
        if not passed:
            raise ValueError(rows[-1])
    coupon_dir = ENC / "contact-pair-coupon"
    coupon_record_path = coupon_dir / "geometry-check.json"
    coupon_record = json.loads(coupon_record_path.read_text())
    coupon_paths = []
    for half, item in coupon_record["coupons"].items():
        piece_name = item["piece"].removeprefix("enclosure-")
        crop = pieces[piece_name].intersect(e._ybox(*item["crop_in_machine_frame"]))
        pose = item["machine_to_bed"]
        if pose["turn"] is not None:
            turn = pose["turn"]
            crop = crop.rotate((0, 0, 0), turn["axis"], turn["degrees"])
        crop = crop.translate(pose["then_shift"])
        coupon_path = coupon_dir / f"contact-pair-{half}-coupon.step"
        coupon_paths.append(coupon_path)
        saved = cq.importers.importStep(str(coupon_path)).val()
        difference = abs(crop.cut(saved).Volume()) + abs(saved.cut(crop).Volume())
        passed = difference < 1e-5
        rows.append({"check": f"{half} printed coupon crop matches current export",
                     "pass": passed, "symmetric_difference_mm3": difference})
        if not passed:
            raise ValueError(rows[-1])
    plate, trays = box.pack.collet_plate, box.pack.pump_trays
    gap = e.bay_back_y(plate) - e.pump_cartridge_aft_y(trays, plate)
    press = e._pogo.PIN_PROUD - gap
    protrusion_error = OVERALL_TIP_HEIGHT_TOL + BODY_DEPTH_TOL
    stack_error = protrusion_error + 2 * FACE_FLUSH_TOL
    limits = [press - stack_error, press + stack_error]
    passed = 0 < limits[0] and limits[1] < e._pogo.STROKE
    rows.append({"check": "drawing extremes and coupon face criterion at nominal frame gap",
                 "pass": passed, "compression_range_mm": limits})
    if not passed:
        raise ValueError(rows[-1])
    inputs = [Path(__file__), box_path, ENC / "enclosure.py", coupon_record_path,
              ROOT / "hardware/manifold-layout/enclosure_assembly.py",
              HERE / "yyfkgcp_pogo_4p.py",
              ENC / "contact-pair-coupon/contact_pair_coupon.py",
              ROOT / "hardware/printed-parts/cadlib/fits.py",
              ROOT / "hardware/scripts/_box_spec.py"]
    report = {
        "scope": "Current exported seats and nominal connector placement; drawing tolerance analysis at the nominal frame gap. No physical fit, magnetic retention, installed gap or endurance result.",
        "geometry_checks_pass": all(row["pass"] for row in rows),
        "checks": rows,
        "construction": {"connector": "YYFKGCP B0GCBNTBT8, 4-pin with ears",
                         "magnet_housings": "Two factory-contained magnets per purchased half",
                         "female_location": "Pump-cap aft face",
                         "male_location": "Front-top bay bulkhead fore face",
                         "separate_print_in_retention_magnets": True,
                         "retention_pair_location": "One RC62 in lower cartridge cradle and one in front-top, centered on the tube axes",
                         "retention_record": "../../printed-parts/enclosure/enclosure/magnet-retention/geometry-check.json",
                         "magnet_insertion_pause_required": True,
                         "paused_parts": ["pump-cartridge", "front-top"]},
        "drawing_source": "https://www.amazon.com/dp/B0GCBNTBT8?th=1",
        "drawing_observed_local_date": "2026-10-03",
        "prime_listing_verified": True,
        "dimensions_mm": {"nominal_frame_gap": gap,
                          "nominal_pin_compression": press,
                          "stated_stroke": e._pogo.STROKE,
                          "male_overall_tip_height_tolerance": OVERALL_TIP_HEIGHT_TOL,
                          "body_depth_general_tolerance": BODY_DEPTH_TOL,
                          "conservative_pin_protrusion_range": [e._pogo.PIN_PROUD - protrusion_error,
                                                                e._pogo.PIN_PROUD + protrusion_error],
                          "coupon_face_flush_tolerance_each": FACE_FLUSH_TOL,
                          "compression_range_at_nominal_frame_gap": limits,
                          "additional_closing_error_before_maximum_stroke": e._pogo.STROKE - limits[1],
                          "face_gap_range_at_nominal_frame_gap": [gap - 2 * FACE_FLUSH_TOL,
                                                                  gap + 2 * FACE_FLUSH_TOL]},
        "assembly_limits": {"minimum_face_gap_for_maximum_drawing_pin_without_overstroke_mm":
                            e._pogo.PIN_PROUD + protrusion_error - e._pogo.STROKE,
                            "maximum_face_gap_for_minimum_drawing_pin_to_make_contact_mm":
                            e._pogo.PIN_PROUD - protrusion_error,
                            "actual_compression_equation": "Measured unloaded protrusion minus measured assembled plastic-face gap at each pin; greater than zero and less than stated stroke.",
                            "frame_position_tolerance_bounded": False,
                            "magnetic_pull_at_installed_gap_specified": False,
                            "installed_contact_resistance_verified": False,
                            "whole_cartridge_retention_verified": False},
        "source_sha256": {str(path.relative_to(ROOT)): sha(path) for path in inputs},
        "artifact_sha256": {str(path.relative_to(ROOT)): sha(path)
                            for path in [*paths.values(), *coupon_paths]},
        "physical_record": "physical-observations.json",
    }
    (HERE / "mounting-audit.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({"geometry_checks_pass": report["geometry_checks_pass"],
                      "checks": len(rows), "nominal_gap_mm": gap,
                      "compression_range_mm": limits,
                      "additional_closing_error_mm": e._pogo.STROKE - limits[1]}, indent=2))


if __name__ == "__main__":
    main()
