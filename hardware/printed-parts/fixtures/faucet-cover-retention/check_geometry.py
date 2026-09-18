"""Saved-cover fit checks against the protected faucet tip and display.

The lifted axial segment has a complete geometric bound. Final seating uses
eight stated positions and independent rigid wing translations; spring force
and the installed elastic shape are physical trial readings.
"""

from pathlib import Path
import json
import sys
from types import SimpleNamespace

import cadquery as cq

HERE = Path(__file__).resolve().parent
ROOT = next(parent for parent in HERE.parents if (parent / "tools").is_dir())
for directory in (HERE, ROOT / "hardware/scripts", ROOT / "hardware/faucet-layout"):
    sys.path.insert(0, str(directory))

import check_faucet_geometry as shared
import cover_retention_trial as trial
import faucet_assembly as assembly

OUTPUT = HERE / "fit-check.json"
NORMAL_STATIONS = (0.0, 0.05, 0.06, 0.35, 1.0, 3.0, 5.0, trial.INSTALL_LIFT)
SEARCH_BUDGET = 3.5
SEARCH_RESOLUTION = 0.01


def source_paths():
    return (
        Path(__file__), Path(trial.__file__), Path(shared.__file__),
        Path(assembly.__file__), Path(trial.cover.__file__), Path(trial.shell.__file__),
        trial.FAUCET / "_display_snap.py", trial.FAUCET / "_faucet_interface.py",
        ROOT / "hardware/printed-parts/cadlib/fits.py",
        ROOT / "hardware/printed-parts/cadlib/world_workplane.py",
        ROOT / "hardware/reference/touch-flo-faucet/display-reference/component-envelopes.json",
    )


def native_box(x_range, s_range, n_range):
    ranges = (x_range, s_range, n_range)
    return cq.Solid.makeBox(*(high - low for low, high in ranges),
                            cq.Vector(*(low for low, _ in ranges)))


def solid_volume(part):
    return shared.volume(part)


def hardware_clearance(cover, hardware):
    gap = cover.distance(hardware)
    overlap = solid_volume(cover.intersect(hardware)) if gap < shared.DISTANCE_TOLERANCE else 0.0
    return {"gap_mm": shared.clean_number(gap), "overlap_mm3": shared.clean_number(overlap)}


def curved_radius(face):
    from OCP.BRepAdaptor import BRepAdaptor_Surface

    surface = BRepAdaptor_Surface(face.wrapped)
    if face.geomType() == "CYLINDER":
        return surface.Cylinder().Radius()
    if face.geomType() == "TORUS":
        return surface.Torus().MinorRadius()
    return None


def actual_lip_reading(reading, height, seated, tip, hardware):
    f = trial.shell
    root_radius = f.display_clip_groove_radius
    faces = []
    for face in tip.Faces():
        radius = curved_radius(face)
        bounds = face.BoundingBox()
        if (radius is not None and abs(radius - root_radius) < shared.DISTANCE_TOLERANCE
                and bounds.ymin >= f.display_clip_s_bottom - f._display_snap.END_SLIP - shared.DISTANCE_TOLERANCE
                and bounds.ymax <= f.display_clip_s_top + f._display_snap.END_SLIP + shared.DISTANCE_TOLERANCE):
            faces.append(face)
    if not faces:
        raise ValueError("The protected tip has no matching cylindrical/toroidal groove faces")
    groove_bounds = cq.Compound.makeCompound(faces).BoundingBox()
    top = f.display_clip_bottom_n + height
    band = native_box((-30.0, 30.0), (f.display_clip_s_bottom, f.display_clip_s_top),
                      (f.display_clip_bottom_n, top))
    lips = seated.intersect(band)
    lip_faces = [face for face in lips.Faces()
                 if (radius := curved_radius(face)) is not None
                 and abs(radius - root_radius) < shared.DISTANCE_TOLERANCE]
    lip_bounds = cq.Compound.makeCompound(lip_faces).BoundingBox()
    measured_radius = min(curved_radius(face) for face in lip_faces)
    roof_gap = groove_bounds.zmax - lip_bounds.zmax
    floor_gap = lip_bounds.zmin - groove_bounds.zmin
    end_gaps = (lip_bounds.ymin - groove_bounds.ymin, groove_bounds.ymax - lip_bounds.ymax)
    seated_overlap = solid_volume(seated.intersect(tip))
    pushed = seated.translate((0.0, 0.0, -0.02))
    stop_contact = pushed.intersect(tip)
    outside_lips = shared.outside_material_volume(stop_contact, lips.translate((0.0, 0.0, -0.02)))
    pushed_device = solid_volume(pushed.intersect(hardware))
    lifted = seated.translate((0.0, 0.0, 0.5))
    capture = lifted.intersect(tip)
    outside_capture_lips = shared.outside_material_volume(capture, lips.translate((0.0, 0.0, 0.5)))
    shoulder_band = native_box((-30.0, 30.0), (f.display_clip_s_bottom, f.display_clip_s_top),
                               (groove_bounds.zmax, top + 0.5))
    shoulder_capture = solid_volume(capture.intersect(shoulder_band))
    device = hardware_clearance(seated, hardware)
    passed = (abs(measured_radius - root_radius) <= shared.DISTANCE_TOLERANCE
              and abs(floor_gap) <= shared.DISTANCE_TOLERANCE
              and roof_gap >= 0.05 - shared.DISTANCE_TOLERANCE
              and all(abs(gap - f._display_snap.END_SLIP) <= shared.DISTANCE_TOLERANCE for gap in end_gaps)
              and max(seated_overlap, outside_lips, outside_capture_lips, pushed_device) <= shared.VOLUME_TOLERANCE
              and solid_volume(stop_contact) > shared.VOLUME_TOLERANCE
              and shoulder_capture > shared.VOLUME_TOLERANCE
              and device["gap_mm"] >= 0.1 - shared.DISTANCE_TOLERANCE)
    reading.add(f"fit:seated-lip-{height:.2f}", passed,
                root_radius_mm=shared.clean_number(measured_radius),
                radial_engagement_mm=shared.clean_number(f.display_neck_outer_r - measured_radius),
                lip_n_range_mm=[shared.clean_number(lip_bounds.zmin), shared.clean_number(lip_bounds.zmax)],
                groove_n_range_mm=[shared.clean_number(groove_bounds.zmin), shared.clean_number(groove_bounds.zmax)],
                floor_gap_mm=shared.clean_number(floor_gap), roof_gap_mm=shared.clean_number(roof_gap),
                end_gaps_mm=[shared.clean_number(gap) for gap in end_gaps],
                seated_tip_overlap_mm3=shared.clean_number(seated_overlap), device_clearance=device,
                inward_stop_probe_mm=0.02, stop_contact_mm3=shared.clean_number(solid_volume(stop_contact)),
                stop_contact_outside_lips_mm3=shared.clean_number(outside_lips),
                inward_probe_device_overlap_mm3=shared.clean_number(pushed_device),
                outward_capture_probe_mm=0.5, actual_shoulder_capture_mm3=shared.clean_number(shoulder_capture),
                capture_outside_lips_mm3=shared.clean_number(outside_capture_lips),
                method="actual native groove/lip face radii and extents; complete seated commons and lip-classified inward/outward contact probes")
    return lips


def seating_reading(reading, free, seated, tip, base, hardware):
    f = trial.shell
    anchor = trial.cover.bezel_n_bottom
    bounds = free.BoundingBox()
    crop = native_box((bounds.xmin - SEARCH_BUDGET, bounds.xmax + SEARCH_BUDGET),
                      (bounds.ymin - 0.1, bounds.ymax + 0.1),
                      (bounds.zmin - 0.1, bounds.zmax + trial.INSTALL_LIFT + 0.1))
    base_relevant = solid_volume(base.intersect(crop))
    obstacle = tip.intersect(crop)
    rows = []
    for lift in NORMAL_STATIONS:
        row = {"normal_lift_mm": lift, "sides": []}
        for name, cover in (("nominal", seated), ("relaxed", free)):
            upper = cover.intersect(native_box((-50.0, 50.0), (-50.0, 100.0), (anchor, 60.0)))
            upper_overlap = solid_volume(upper.translate((0.0, 0.0, lift)).intersect(obstacle))
            row[f"{name}_bezel_overlap_mm3"] = shared.clean_number(upper_overlap)
            for side in (-1, 1):
                x_range = (0.0, 50.0) if side > 0 else (-50.0, 0.0)
                wing = cover.intersect(native_box(x_range, (-50.0, 100.0), (-30.0, anchor)))
                wing = wing.translate((0.0, 0.0, lift))
                low, high = 0.0, SEARCH_BUDGET
                if solid_volume(wing.intersect(obstacle)) <= shared.VOLUME_TOLERANCE:
                    high = 0.0
                elif solid_volume(wing.translate((side * high, 0.0, 0.0)).intersect(obstacle)) <= shared.VOLUME_TOLERANCE:
                    while high - low > SEARCH_RESOLUTION:
                        middle = (high + low) / 2.0
                        overlap = solid_volume(wing.translate((side * middle, 0.0, 0.0)).intersect(obstacle))
                        if overlap <= shared.VOLUME_TOLERANCE:
                            high = middle
                        else:
                            low = middle
                posed = wing.translate((side * high, 0.0, 0.0))
                remaining = solid_volume(posed.intersect(obstacle))
                carried_hardware = hardware.translate((0.0, 0.0, lift))
                hardware_overlap = max(solid_volume(wing.translate((side * high * fraction, 0.0, 0.0))
                                                    .intersect(carried_hardware)) for fraction in (0.5, 1.0))
                row["sides"].append({"state": name, "side": side,
                                      "outward_clearance_demand_mm": shared.clean_number(high),
                                      "remaining_tip_overlap_mm3": shared.clean_number(remaining),
                                      "maximum_half_full_opening_device_overlap_mm3": shared.clean_number(hardware_overlap)})
        rows.append(row)
        print(f"  F seating lift {lift:g} mm checked", flush=True)
    passed = (base_relevant <= shared.VOLUME_TOLERANCE
              and all(max(row["nominal_bezel_overlap_mm3"], row["relaxed_bezel_overlap_mm3"],
                          *(side["remaining_tip_overlap_mm3"] for side in row["sides"]),
                          *(side["maximum_half_full_opening_device_overlap_mm3"] for side in row["sides"]))
                      <= shared.VOLUME_TOLERANCE for row in rows))
    reading.add("motion:F-representative-normal-seat", passed, samples=rows,
                unchanged_base_material_in_motion_crop_mm3=shared.clean_number(base_relevant),
                outward_search_budget_mm=SEARCH_BUDGET, search_resolution_mm=SEARCH_RESOLUTION,
                peak_relaxed_outward_demand_mm=max(side["outward_clearance_demand_mm"] for row in rows
                                                 for side in row["sides"] if side["state"] == "relaxed"),
                scope="eight stated final-seating positions for F; independent rigid wing translations and carried-device commons at half/full opening. This is not a continuous elastic path, force prediction or strain certificate")


def main():
    import trimesh

    sources_before = shared.hashes(source_paths())
    manifest_path = HERE / "trial-geometry.json"
    manifest = json.loads(manifest_path.read_text())
    manifest_sha = shared.digest(manifest_path)
    reading = shared.Reading()
    protected = manifest["production_artifacts_unchanged"]
    unchanged = all(shared.digest(ROOT / name) == digest for name, digest in protected.items())
    sources_match = all(shared.digest(ROOT / name) == digest
                        for name, digest in manifest["sources_sha256"].items())
    reading.add("provenance:unchanged-printed-tip", unchanged and sources_match
                and shared.digest(trial.TIP_STL) == manifest["printed_tip_stl_sha256"],
                printed_tip_stl_sha256=manifest["printed_tip_stl_sha256"],
                protected_artifacts_sha256=protected, generator_sources_current=sources_match)

    f = trial.shell
    placement = trial.frame()
    tip = cq.importers.importStep(str(trial.TIP)).val().moved(placement.inverse)
    base_path = trial.FAUCET / "faucet-shell/faucet-shell-base.step"
    base_world = cq.importers.importStep(str(base_path)).val()
    base = base_world.moved(placement.inverse)
    body_world = assembly.build_display_body().val()
    screen_world = assembly.build_display_screen().val()
    hardware = cq.Compound.makeCompound([body_world, screen_world]).moved(placement.inverse)
    seated = {height: trial.seated_native(height) for height in sorted({part.lip_height_mm for part in trial.TRIALS})}
    lip_witnesses = {height: actual_lip_reading(reading, height, body, tip, hardware)
                     for height, body in seated.items()}
    baseline = trial.seated_native(3.0)
    protected_bezel_top = f.display_cover_top_n - trial.LABEL_DEPTH
    bezel_witness = baseline.intersect(native_box((-50.0, 50.0), (-50.0, 100.0),
                                                  (trial.cover.bezel_n_bottom, protected_bezel_top)))
    world_parts, native_parts, saved_hashes = {}, {}, {}
    by_id = {row["id"]: row for row in manifest["parts"]}
    for variant in trial.TRIALS:
        row = by_id[variant.id]
        step_path, stl_path = HERE / row["step"], HERE / row["stl"]
        world = cq.importers.importStep(str(step_path)).val()
        native = world.moved(placement.inverse)
        world_parts[variant.id], native_parts[variant.id] = world, native
        hashes = {"step": shared.digest(step_path), "stl": shared.digest(stl_path)}
        saved_hashes[variant.id] = hashes
        hash_match = hashes == {"step": row["step_sha256"], "stl": row["sha256"]}
        mesh = trimesh.load_mesh(stl_path, process=True)
        device = hardware_clearance(native, hardware)
        missing_bezel = shared.outside_material_volume(bezel_witness, native)
        missing_lips = []
        for side in (-1, 1):
            x_range = (0.0, 50.0) if side > 0 else (-50.0, 0.0)
            witness = lip_witnesses[variant.lip_height_mm].intersect(
                native_box(x_range, (-50.0, 100.0), (-30.0, 60.0)))
            witness = witness.transformGeometry(trial.wing_transform(side, variant.preload_mm))
            missing_lips.append(shared.outside_material_volume(witness, native))
        raised = native.translate((0.0, 0.0, trial.INSTALL_LIFT))
        cylinder = cq.Solid.makeCylinder(f.tube_shell_outer_r, 200.0,
                                         cq.Vector(0.0, -100.0, f.tube_shell_center_y), cq.Vector(0.0, 1.0, 0.0))
        axial = hardware_clearance(raised, cylinder)
        passed = (hash_match and native.isValid() and len(native.Solids()) == 1
                  and mesh.is_watertight and mesh.is_winding_consistent and len(mesh.split()) == 1
                  and device["gap_mm"] >= 0.1 - shared.DISTANCE_TOLERANCE
                  and axial["gap_mm"] >= 0.1 - shared.DISTANCE_TOLERANCE
                  and max(missing_bezel, *missing_lips) <= shared.VOLUME_TOLERANCE)
        reading.add(f"fit:saved-cover-{variant.id}", passed,
                    saved_sha256=hashes, generator_hashes_match=hash_match,
                    valid=native.isValid(), solids=len(native.Solids()),
                    mesh_triangles=len(mesh.faces), mesh_watertight=mesh.is_watertight,
                    mesh_consistent_winding=mesh.is_winding_consistent,
                    preload_at_n6_3_mm=variant.preload_mm, lip_height_mm=variant.lip_height_mm,
                    free_device_clearance=device, complete_axial_cylinder_clearance=axial,
                    missing_complete_bezel_floor_mm3=shared.clean_number(missing_bezel),
                    protected_bezel_thickness_mm=protected_bezel_top - trial.cover.bezel_n_bottom,
                    missing_complete_preformed_lip_witnesses_mm3=[shared.clean_number(value) for value in missing_lips],
                    scope="actual saved STEP and STL; the complete original aperture-bearing bezel floor remains under the lettering, and both complete preformed lips remain present")

    worst = next(part for part in trial.TRIALS if part.id == "F")
    seating_reading(reading, native_parts["F"], seated[worst.lip_height_mm], tip, base, hardware)
    context = SimpleNamespace(**vars(f))
    context.display_cartridge_lift_n = trial.INSTALL_LIFT
    seated_world = seated[worst.lip_height_mm].moved(placement)
    parts = {"shell_base": base_world, "shell_tip": tip.moved(placement)}
    tubes = {"soda-tube": assembly.build_soda_faucet_tube(),
             "flavor-a": assembly.build_flavor_tube(1), "flavor-b": assembly.build_flavor_tube(-1)}
    shared.display_cartridge_axial_reading(reading, context, parts, seated_world, world_parts["F"],
                                           body_world, screen_world, tubes)
    shared.display_loading_reading(reading, context, trial.cover, body_world, screen_world, world_parts["F"])
    ribbon = assembly.build_display_ribbon()
    shared.clearance_reading(reading, "clearance:F-final-ribbon", world_parts["F"], ribbon, 0.1)

    if sources_before != shared.hashes(source_paths()) or manifest_sha != shared.digest(manifest_path):
        raise RuntimeError("Cover geometry sources or manifest changed during the fit readings")
    if not all(shared.digest(ROOT / name) == digest for name, digest in protected.items()):
        raise RuntimeError("A protected production artifact changed during the trial audit")
    for identifier, hashes in saved_hashes.items():
        row = by_id[identifier]
        if hashes != {"step": shared.digest(HERE / row["step"]), "stl": shared.digest(HERE / row["stl"])}:
            raise RuntimeError(f"Cover {identifier} changed during the audit")
    result = {
        "passed": all(row["passed"] for row in reading.rows.values()),
        "sources_sha256": sources_before, "trial_manifest_sha256": manifest_sha,
        "protected_tip_stl_sha256": manifest["printed_tip_stl_sha256"],
        "reference_base_step_sha256": shared.digest(base_path),
        "saved_parts_sha256": saved_hashes, "checks": reading.rows,
        "scope": "Six display-cover trials on the unchanged printed tip. Both seated lip heights and all saved free covers are checked; F supplies the bounded seating and complete loading readings. No spring force, material strain, retention force or support-surface finish is inferred from CAD.",
    }
    temporary = OUTPUT.with_suffix(".json.tmp")
    temporary.write_text(json.dumps(result, indent=2) + "\n")
    temporary.replace(OUTPUT)
    print(f"{'PASS' if result['passed'] else 'FAIL'} cover retention fit: {len(reading.rows)} readings", flush=True)
    return int(not result["passed"])


if __name__ == "__main__":
    sys.exit(main())
