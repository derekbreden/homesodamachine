"""Read the centered RC62 retention pair from current native exports.

Optional --baseline-dir compares a retained local input with the finished cut.
The geometry and insertion sweep are design checks, not physical acceptance.
"""
import argparse
import hashlib
import json
from pathlib import Path
import sys

import cadquery as cq
import numpy as np

HERE = Path(__file__).resolve().parent
ENC = HERE.parent
ROOT = next(p for p in HERE.parents if (p / "tools/publish_now.py").is_file())
sys.path[:0] = [str(ROOT / "hardware/scripts"), str(ENC)]
import enclosure as e
import _box_spec
from materialize_pump_cartridge import _declared_box


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def volume(shape):
    """Empty native boolean results contain no interference."""
    return 0.0 if shape.wrapped.IsNull() else abs(shape.Volume())


def outside_volume(actual, allowed):
    """Keep an obstruction when its allowed envelope is empty."""
    actual_volume = volume(actual)
    if actual_volume < 1e-12:
        return 0.0
    if volume(allowed) < 1e-12:
        return actual_volume
    return volume(actual.cut(allowed))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline-dir", type=Path)
    args = parser.parse_args()
    box, _bounds, box_path = _declared_box(_box_spec, e)
    x, z = e.pump_retention_station(box)
    r = e._retention
    shapes = {}
    checks = []
    pieces = {}
    for name in ("pump-cartridge", "front-top"):
        path = ENC / f"enclosure-{name}.step"
        shape = cq.importers.importStep(str(path)).val()
        shapes[name] = shape
        face, into = e.pump_retention_face(box, name)
        d = r.dimensions((x, z), face, into)
        pocket = e.pump_retention_pocket(box, name)
        y0, y1 = d["pocket_y_mm"]
        checks.append({"check": f"{name}: one valid native solid", "pass":
                       shape.isValid() and len(shape.Solids()) == 1})
        overlap = abs(shape.intersect(pocket).Volume())
        checks.append({"check": f"{name}: cavity is empty", "pass": overlap < 1e-5,
                       "overlap_mm3": overlap})
        radius = d["pocket_radius_mm"]
        footprint = (x - radius, x + radius, d["seat_floor_z_mm"], d["roof_z_mm"])
        cover = e._ybox(footprint[0], footprint[1], *sorted((face, face + into * r.FACE_COVER)),
                        footprint[2], footprint[3])
        backing = e._ybox(footprint[0], footprint[1],
                          *sorted((face + into * (r.FACE_COVER + d["depth_mm"]),
                                   face + into * (r.FACE_COVER + d["depth_mm"] + r.BACKING))),
                          footprint[2], footprint[3])
        roof = e._ybox(footprint[0], footprint[1], y0, y1,
                       d["roof_z_mm"], d["roof_z_mm"] + r.BACKING)
        for label, stock in (("continuous mating cover", cover), ("3 mm backing", backing),
                             ("continuous flat closing roof", roof)):
            missing = abs(stock.cut(shape).Volume())
            checks.append({"check": f"{name}: {label}", "pass": missing < 1e-5,
                           "missing_stock_mm3": missing})
        nominal_ring = r.magnet((x, z), face, into)
        nominal_overlap = abs(shape.intersect(nominal_ring).Volume())
        checks.append({"check": f"{name}: nominal ring fits the selected seat",
                       "pass": nominal_overlap < 1e-5, "overlap_mm3": nominal_overlap})
        # The selected hand fit intentionally grips a maximum-size ring in X/Y.
        # Keep that declared interference separate from roof clearance and from
        # an unintended obstruction on the vertical insertion route.
        max_r = (r.OD + r.TOLERANCE) / 2
        max_t = r.THICKNESS + r.TOLERANCE
        cy0 = min(face + into * r.FACE_COVER, face + into * (r.FACE_COVER + max_t))
        max_ring = cq.Solid.makeCylinder(max_r, max_t,
            cq.Vector(x, cy0, d["seat_floor_z_mm"] + max_r), cq.Vector(0, 1, 0))
        max_ring = max_ring.cut(cq.Solid.makeCylinder((r.ID - r.TOLERANCE) / 2, max_t,
            cq.Vector(x, cy0, d["seat_floor_z_mm"] + max_r), cq.Vector(0, 1, 0)))
        interference = shape.intersect(max_ring)
        intended = max_ring.cut(pocket)
        unintended = outside_volume(interference, intended)
        seat_overlap = volume(interference)
        roof_gap = d["roof_z_mm"] - max_ring.BoundingBox().zmax
        checks.append({"check": f"{name}: maximum ring has only declared press-fit interference",
                       "pass": unintended < 1e-5,
                       "native_interference_mm3": seat_overlap,
                       "declared_fit_interference_mm3": volume(intended),
                       "unexpected_interference_mm3": unintended,
                       "maximum_x_diametral_interference_mm": d["maximum_od_x_interference_mm"],
                       "maximum_y_interference_mm": d["maximum_thickness_y_interference_mm"],
                       "scope": "Geometric interference only; no universal insertion-force or tolerance acceptance."})
        checks.append({"check": f"{name}: maximum seated ring keeps independent roof clearance",
                       "pass": roof_gap >= r.ROOF_AIR - r.TOLERANCE - 1e-6 and roof_gap > 0,
                       "clearance_mm": roof_gap,
                       "minimum_required_mm": r.ROOF_AIR - r.TOLERANCE})
        open_shape = shape.intersect(e._ybox(-200, 200, -100, 500, 0, d["roof_z_mm"] - 0.001))
        sweep_height = r.OD + r.TOLERANCE + 1
        open_aperture = pocket.fuse(e._ybox(x - radius, x + radius, y0, y1,
            d["arc_center_z_mm"], d["roof_z_mm"] + sweep_height + r.OD + 1))
        nominal_sweep, max_sweep, unexpected_sweep = [], [], []
        for dz in np.linspace(0, sweep_height, 29):
            nominal_sweep.append(abs(open_shape.intersect(nominal_ring.translate((0, 0, dz))).Volume()))
            moving = max_ring.translate((0, 0, dz))
            actual = open_shape.intersect(moving)
            max_sweep.append(volume(actual))
            allowed = moving.cut(open_aperture) if max_sweep[-1] > 1e-12 else actual
            unexpected_sweep.append(outside_volume(actual, allowed))
        checks.append({"check": f"{name}: nominal upright insertion route remains open before closure",
                       "pass": max(nominal_sweep) < 1e-5, "samples": 29,
                       "maximum_overlap_mm3": max(nominal_sweep)})
        checks.append({"check": f"{name}: maximum ring insertion has only declared press-fit contact",
                       "pass": max(unexpected_sweep) < 1e-5, "samples": 29,
                       "maximum_press_fit_overlap_mm3": max(max_sweep),
                       "maximum_unexpected_overlap_mm3": max(unexpected_sweep),
                       "scope": "The open route preserves the selected lateral press fit; print deformation and hand force are unmeasured."})
        bed = round(shape.BoundingBox().zmin, 5)
        pieces[name] = {**d, "production_print_up": "+Z", "bed_machine_z_mm": bed,
                        "roof_height_above_bed_mm": d["roof_z_mm"] - bed,
                        "magnet_nominal_top_above_bed_mm": z + r.OD / 2 - bed,
                        "magnet_maximum_top_above_bed_mm": z + r.OD / 2 + r.TOLERANCE - bed,
                        "artifact_sha256": {suffix: sha(ENC / f"enclosure-{name}{suffix}")
                                            for suffix in (".step", ".stl", ".step.mesh")}}
        if args.baseline_dir:
            old = cq.importers.importStep(str(args.baseline_dir / path.name)).val()
            added = abs(shape.cut(old).Volume())
            outside = abs(old.cut(shape).cut(pocket).Volume())
            missing_cut = abs(old.intersect(pocket).cut(old.cut(shape)).Volume())
            checks.append({"check": f"{name}: only retention pocket changes native input",
                           "pass": max(added, outside, missing_cut) < 1e-4,
                           "added_mm3": added, "removed_outside_pocket_mm3": outside,
                           "missing_pocket_cut_mm3": missing_cut})
    min_web = min(abs(hx - x) - box.pack.collet_plate["bore_r"] - (r.OD / 2 + r.RADIAL_AIR)
                  for hx, _hz in box.pack.collet_plate["holes"])
    checks.append({"check": "at least 3 mm between pocket and nearest tee collar bore",
                   "pass": min_web >= 3, "minimum_web_mm": min_web})
    checks.append({"check": "single pair centred on the four tube insertion axes",
                   "pass": abs(x) < 1e-8 and all(abs(hz - z) < 1e-8
                           for _hx, hz in box.pack.collet_plate["holes"])})
    gap = e.bay_back_y(box.pack.collet_plate) - e.pump_cartridge_aft_y(box.pack.pump_trays, box.pack.collet_plate)
    report = {"article": "One RC62 per cartridge cradle and front-top, centered on tube axes",
              "geometry_checks_pass": all(c["pass"] for c in checks), "checks": checks,
              "pieces": pieces, "magnet_count": 2, "magnet": {"model": "K&J RC62",
              "od_mm": r.OD, "id_mm": r.ID, "thickness_mm": r.THICKNESS,
              "dimensional_tolerance_mm": r.TOLERANCE, "maximum_continuous_service_c": r.MAX_SERVICE_C,
              "source": "https://www.kjmagnetics.com/rc62-neodymium-ring-magnet"},
              "nominal_frame_gap_mm": gap, "nominal_attracting_face_separation_mm": gap + 2 * r.FACE_COVER,
              "pogo_axis_z_mm": e.pump_contact_station(box)[1],
              "magnet_below_pogos_mm": e.pump_contact_station(box)[1] - z,
              "minimum_tube_bore_web_mm": min_web, "polarity":
              "Opposite poles on the two mating faces; both installed magnet north vectors point along the same machine Y direction.",
              "fit_selection": {"coupon": r.FIT_COUPON,
                  "nominal_x_air_mm": r.RADIAL_AIR, "nominal_y_air_mm": r.AXIAL_AIR,
                  "independent_roof_air_mm": r.ROOF_AIR,
                  "evidence": "fit-coupons/physical-fit-selection.json",
                  "scope": "Preferred hand fit in the printed upright PET-GF coupon; maximum-size rings intentionally interfere in X/Y."},
              "scope": "Current native geometry and insertion route only. Maximum-tolerance X/Y interference is intentional, not universal fit acceptance. Sealed-pocket roof quality, magnetic force, printed cover capacity, heat exposure, contact compression and operating tube retention are unverified.",
              "source_sha256": {str(p.relative_to(ROOT)): sha(p) for p in
                  (Path(__file__), ENC / "enclosure.py", ENC / "_cartridge_retention.py", box_path)}}
    (HERE / "geometry-check.json").write_text(json.dumps(report, indent=2) + "\n")
    # A local assembly section exposes both captured rings and the thin covers.
    section = cq.Assembly(name="centered-RC62-retention-section")
    cut = e._ybox(x, x + 28, 65, 100, z - 14, z + 14)
    for name, shape in shapes.items():
        section.add(shape.intersect(cut), name=name, color=e.PIECE_COLORS[name])
        ring = r.magnet((x, z), *e.pump_retention_face(box, name))
        section.add(ring.intersect(cut), name=f"RC62-{name}", color=cq.Color(0.72, 0.74, 0.77))
    e.export_assembly(section, str(HERE / "section.step"))
    print(json.dumps({"pass": report["geometry_checks_pass"], "checks": len(checks),
                      "magnet_axis_xz": [x, z], "face_separation_mm": gap + 2 * r.FACE_COVER,
                      "minimum_tube_web_mm": min_web}, indent=2), flush=True)
    if not report["geometry_checks_pass"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
