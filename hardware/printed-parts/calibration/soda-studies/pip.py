"""One bed-rooted captive portal for the compact print reference.

The two legs provide the crossbar's first bridge anchors. A fixed central
plinth precedes that bridge, and two fixed lips print above its shoulders.
The model-to-model release air separates those shoulders, lips and running
faces. Automatic ceiling supports may root in the empty terminal travel
pockets; remove those roots with the ceiling supports before assessing motion.
Native readings distinguish those removable roots from support touching the
initially printed moving stock. Physical cleanup and release remain unmeasured.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import cadquery as cq


XY_AIR = .25
Z_AIR = .48
STROKE = 10.
FLOOR_Z = 3.08
BAR_THICKNESS = 3.36
LIP_THICKNESS = 3.
LEG_THICKNESS = 3.
FOOT_RELIEF = .35
FOOT_HEIGHT = 1.


def box(x0, x1, y0, y1, z0, z1):
    return cq.Solid.makeBox(x1-x0, y1-y0, z1-z0,
                            cq.Vector(x0, y0, z0))


def bounds(shape):
    bb = shape.BoundingBox()
    return [bb.xmin, bb.xmax, bb.ymin, bb.ymax, bb.zmin, bb.zmax]


def fuse(shapes):
    return shapes[0].fuse(*shapes[1:]).clean()


def foot(x0, x1, y0, y1, z_top, relief):
    """The bed contact retracts every moving face, including both stop ends."""
    lower = (cq.Workplane("XY")
             .moveTo(x0+relief, y0+relief).lineTo(x1-relief, y0+relief)
             .lineTo(x1-relief, y1-relief).lineTo(x0+relief, y1-relief)
             .close().wire().val())
    upper = (cq.Workplane("XY", origin=(0, 0, FOOT_HEIGHT))
             .moveTo(x0, y0).lineTo(x1, y0).lineTo(x1, y1)
             .lineTo(x0, y1).close().wire().val())
    taper = cq.Solid.makeLoft([lower, upper], ruled=True)
    return taper.fuse(box(x0, x1, y0, y1, FOOT_HEIGHT, z_top)).clean()


def z_faces(shape, z):
    """Actual planar faces in the finished B-rep, not construction boxes."""
    out = []
    for face in shape.Faces():
        bb = face.BoundingBox()
        if (abs(bb.zmax-bb.zmin) < 1e-6
                and abs((bb.zmin+bb.zmax)/2-z) < 1e-6):
            out.append(dict(area_mm2=face.Area(), bounds_mm=bounds(face)))
    return out


def build(*, xy_air=XY_AIR, z_air=Z_AIR, stroke=STROKE,
          centre_x=0., front_y=2., floor_z=FLOOR_Z,
          foot_relief=FOOT_RELIEF):
    """Return source-frame solids, exact cuts, blockers and a CAD-only proof.

    The placement contract uses +X for motion, +Y into the arch, and +Z as
    build direction. Default bounds are X +/-18.25 including the stock ties,
    Y2..27.5, and Z0..13.88. The moving member prints in its stroke midpoint.
    All dimensions are millimetres. No native or physical release is inferred.
    """
    if xy_air <= 0 or z_air <= 0 or stroke <= 0:
        raise ValueError("Running and release gaps and stroke must be positive")
    if not 0 <= foot_relief < LEG_THICKNESS/2:
        raise ValueError("Foot relief leaves no positive bed contact")

    # 18.5 mm engagement plus exact 10 mm travel, bounded by 3.75 mm stops.
    length = 18.5
    half_leg = length/2
    x0, x1 = centre_x-half_leg, centre_x+half_leg
    stop0 = x0-stroke/2
    stop1 = x1+stroke/2
    end0, end1 = stop0-3.75, stop1+3.75
    # One quarter-millimetre overlap with the arch's X +/-18 jambs.
    tie0, tie1 = stop0-4., stop1+4.

    fy0, fy1 = front_y, front_y+3.
    leg0 = fy1+xy_air
    leg1 = leg0+LEG_THICKNESS
    leg2 = leg1+13.
    leg3 = leg2+LEG_THICKNESS
    by0, by1 = leg3+xy_air, leg3+xy_air+3.
    floor0, floor1 = leg1+xy_air, leg2-xy_air
    bar0, bar1 = floor_z+z_air, floor_z+z_air+BAR_THICKNESS
    lip0, lip1 = bar1+z_air, bar1+z_air+LIP_THICKNESS
    # A three-millimetre catch over the crossbar on each side.
    catch0, catch1 = leg1+3., leg2-3.
    tab_y0, tab_y1 = catch0+xy_air, catch1-xy_air
    tab_top = floor_z+10.80
    tab_half_x = 4.25

    legs = [foot(x0, x1, a, b, bar1, foot_relief)
            for a, b in ((leg0, leg1), (leg2, leg3))]
    crossbar = box(x0, x1, leg1, leg2, bar0, bar1)
    tab = box(centre_x-tab_half_x, centre_x+tab_half_x,
              tab_y0, tab_y1, bar1, tab_top)
    moving = fuse([*legs, crossbar, tab])

    stock = {
        "front_wall": box(end0, end1, fy0, fy1, 0, lip1),
        "back_wall": box(end0, end1, by0, by1, 0, lip1),
        "left_stop": box(end0, stop0, fy0, by1, 0, lip1),
        "right_stop": box(stop1, end1, fy0, by1, 0, lip1),
        "floor_plinth": box(stop0, stop1, floor0, floor1, 0, floor_z),
        # Each lip exists only above the initially printed portal. The
        # empty travel pockets therefore need no unsupported lip onset.
        "front_lip": box(x0, x1, fy1, catch0, lip0, lip1),
        "back_lip": box(x0, x1, catch1, by0, lip0, lip1),
        "front_tie": box(tie0, tie1, fy0, fy1, 0, lip1),
        "back_tie": box(tie0, tie1, by0, by1, 0, lip1),
    }
    fixed = fuse(list(stock.values()))

    # Sweep all physical stations, adding only named mating-face gaps.
    # These are the cuts into any existing arch/base stock. Keep ordinary
    # finish surfaces outside their bounds instead of carving a bay box.
    cuts = {
        "front_leg_corridor": box(stop0, stop1, fy1, floor0, 0, lip0),
        "back_leg_corridor": box(stop0, stop1, floor1, by0, 0, lip0),
        "crossbar_corridor": box(stop0, stop1, floor0, floor1,
                                   floor_z, lip0),
        "handle_corridor": box(centre_x-tab_half_x-stroke/2,
                                centre_x+tab_half_x+stroke/2,
                                catch0, catch1, bar1, tab_top+.24),
    }
    clearance_cut = fuse(list(cuts.values()))

    gaps = {
        "front_outer_xy": box(stop0, stop1, fy1, leg0, 0, bar1),
        "back_outer_xy": box(stop0, stop1, leg3, by0, 0, bar1),
        "front_inner_xy": box(stop0, stop1, leg1, floor0, 0, floor_z),
        "back_inner_xy": box(stop0, stop1, floor1, leg2, 0, floor_z),
        "lower_z": box(stop0, stop1, floor0, floor1, floor_z, bar0),
        "upper_front_z": box(x0, x1, leg0, catch0, bar1, lip0),
        "upper_back_z": box(x0, x1, catch1, leg3, bar1, lip0),
        "front_tab_xy": box(centre_x-tab_half_x-stroke/2,
                            centre_x+tab_half_x+stroke/2,
                            catch0, tab_y0, lip0, lip1),
        "back_tab_xy": box(centre_x-tab_half_x-stroke/2,
                           centre_x+tab_half_x+stroke/2,
                           tab_y1, catch1, lip0, lip1),
    }
    # Suppress support contacts inside the intended motion corridor. Native
    # footprint readings also distinguish removable end-pocket roots from
    # deposits touching the initially printed moving stock.
    blockers = {**cuts, **gaps}
    common_phase = all(abs((z-.20)/.24-round((z-.20)/.24)) < 1e-7
                       for z in (floor_z, bar0, bar1, lip0))

    proof = {
        "scope": "Exact B-rep geometry and sampled rigid motion. No native slice, physical release, friction, finish, strength or lifetime acceptance.",
        "placement": {"slide_axis": "+X", "build_axis": "+Z",
                      "centre_x_mm": centre_x, "front_y_mm": front_y},
        "nominal_gaps_mm": {"xy_per_face": xy_air, "lower_z": z_air,
                            "upper_z": z_air},
        "mechanical_stroke_mm": stroke,
        "printed_engagement_length_mm": length,
        "bridge_span_between_bed_rooted_legs_mm": leg2-leg1,
        "stock_mm": {"legs": LEG_THICKNESS,
                     "bed_contact_after_relief": LEG_THICKNESS-2*foot_relief,
                     "bar": BAR_THICKNESS, "lips": LIP_THICKNESS,
                     "walls_and_stops": 3., "stop_axial": 3.75,
                     "central_plinth_height": floor_z},
        "bed_relief": {"per_face_mm": foot_relief, "height_mm": FOOT_HEIGHT,
                       "scope": "Moving leg bed contacts only; full 3 mm leg stock above Z1."},
        "actual_bounds_mm": {"fixed": bounds(fixed), "moving": bounds(moving),
                             "clearance_cut": bounds(clearance_cut)},
        "contact_planes_z_mm": {"floor": floor_z, "bar_bottom": bar0,
                                "bar_top": bar1, "lip_underside": lip0,
                                "lip_top": lip1, "handle_top": tab_top},
        "actual_contact_faces": {"fixed_floor": z_faces(fixed, floor_z),
                                 "moving_lower": z_faces(moving, bar0),
                                 "moving_upper": z_faces(moving, bar1),
                                 "fixed_lip_underside": z_faces(fixed, lip0)},
        "actual_stock_bounds_mm": {name: bounds(shape) for name, shape in stock.items()},
        "actual_clearance_cut_bounds_mm": {name: bounds(shape) for name, shape in cuts.items()},
        "actual_motion_gap_bounds_mm": {name: bounds(shape) for name, shape in gaps.items()},
        "native_review_required": [
            "Complete first crossbar bridge has both moving-leg anchors.",
            "First lip model roads remain rooted to fixed walls above the moving portal.",
            "Read floor-to-first-bar-slab and last-bar-to-first-lip-slab gaps.",
            "Report bridge flow heights independently of nominal model slabs.",
            "No model, support or brim roads connect the moving first-layer feet.",
            "No support deposits touch the initially printed moving stock or bridge its model-to-model release air; report removable terminal-pocket roots separately.",
            "Keep accessible automatic supports under the independent fixed roof.",
        ],
        "contact_planes_on_common_layer_phase": common_phase,
        "predicted_common_phase_readings": [
            {"first_layer_mm": .20, "uniform_layer_mm": height,
             "last_floor_nozzle_z_mm": floor_z,
             "first_bar_nozzle_z_mm": bar0+height,
             "last_bar_nozzle_z_mm": bar1,
             "first_lip_nozzle_z_mm": lip0+height,
             "nominal_model_slab_gap_mm": z_air}
            for height in (.24, .12, .08)
        ] if common_phase else [],
    }
    return {"fixed": fixed, "moving": moving,
            "fixed_shape": fixed, "moving_shape": moving,
            "fixed_stock": stock, "clearance_cut": clearance_cut,
            "clearance_cuts": cuts, "keepouts": cuts,
            "motion_gaps": gaps, "support_blockers": blockers,
            "proof": proof}


def measure(bay):
    """Positive running clearance and zero intersection through the stroke."""
    fixed, moving = bay["fixed"], bay["moving"]
    stroke = bay["proof"]["mechanical_stroke_mm"]
    rows = []
    for dx in (-stroke/2, -stroke/4, 0., stroke/4, stroke/2):
        pose = moving.translate((dx, 0, 0))
        common = fixed.intersect(pose)
        rows.append({"dx_mm": dx, "common_volume_mm3": common.Volume(),
                     "minimum_surface_distance_mm": fixed.distance(pose),
                     "pose_bounds_mm": bounds(pose),
                     "expected_state": "Mechanical end-stop contact" if abs(dx) == stroke/2
                                       else "Positive running clearance"})
    # Contact faces come from the finished solids. Their extreme planes
    # establish both named Z gaps without relying on dimension declarations.
    faces = bay["proof"]["actual_contact_faces"]
    floor = max(row["bounds_mm"][5] for row in faces["fixed_floor"])
    lower = min(row["bounds_mm"][4] for row in faces["moving_lower"])
    upper = max(row["bounds_mm"][5] for row in faces["moving_upper"])
    lip = min(row["bounds_mm"][4] for row in faces["fixed_lip_underside"])
    vertical = []
    for dz in (-(lower-floor), 0., lip-upper):
        pose = moving.translate((0, 0, dz))
        vertical.append({"dz_mm": dz,
                         "common_volume_mm3": fixed.intersect(pose).Volume(),
                         "minimum_surface_distance_mm": fixed.distance(pose)})
    retention = []
    probe_depth = .001
    for dx in (-stroke/2, -stroke/4, 0., stroke/4, stroke/2):
        # A deliberate micron past each free Z limit measures the remaining
        # bearing area. This establishes CAD capture through the full stroke.
        up = moving.translate((dx, 0, lip-upper+probe_depth))
        down = moving.translate((dx, 0, -(lower-floor)-probe_depth))
        retention.append({"dx_mm": dx,
                          "upper_catch_area_mm2": fixed.intersect(up).Volume()/probe_depth,
                          "lower_bearing_area_mm2": fixed.intersect(down).Volume()/probe_depth})
    return {"finished_shapes": {
                "fixed": {"valid": fixed.isValid(), "solids": len(fixed.Solids()),
                          "volume_mm3": fixed.Volume()},
                "moving": {"valid": moving.isValid(), "solids": len(moving.Solids()),
                           "volume_mm3": moving.Volume()}},
            "actual_cad_z_gap_mm": {"lower": lower-floor, "upper": lip-upper},
            "stroke_samples": rows, "z_capture_samples": vertical,
            "capture_area_samples": retention,
            "capture_probe_depth_mm": probe_depth,
            "cad_captured_through_stroke": all(row["upper_catch_area_mm2"] > 0
                and row["lower_bearing_area_mm2"] > 0 for row in retention),
            "rigid_motion_clear": all(abs(row["common_volume_mm3"]) < 1e-6 for row in rows+vertical),
            "source_scope": "Short square working faces, not the complete source Z-seam geometry or its qualified assembly."}


def export_bay(output):
    output.mkdir(parents=True, exist_ok=True)
    bay = build()
    proof = {**bay["proof"], "measured": measure(bay)}
    for name in ("fixed", "moving"):
        shape = bay[name]
        cq.exporters.export(shape, str(output/f"pip-{name}.step"))
        cq.exporters.export(shape, str(output/f"pip-{name}.stl"), tolerance=.02,
                            angularTolerance=.05)
    assembly = cq.Compound.makeCompound([bay["fixed"], bay["moving"]])
    cq.exporters.export(assembly, str(output/"pip-bay.step"))
    cq.exporters.export(assembly, str(output/"pip-bay.stl"), tolerance=.02,
                        angularTolerance=.05)
    (output/"pip-proof.json").write_text(json.dumps(proof, indent=2)+"\n")
    print(json.dumps({"output": str(output), "measured": proof["measured"]}, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=Path(__file__).parent)
    export_bay(parser.parse_args().output)
