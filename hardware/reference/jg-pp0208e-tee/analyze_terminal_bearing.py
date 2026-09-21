#!/usr/bin/env python3
"""Read observed terminal-face coverage outside the circular release aperture.

This keeps the archived scan's registration and scale. Projected scan-face area
is evidence for an assembly trial, not a guaranteed simultaneous contact area or
a material-strength calculation. No native production geometry is generated.
"""

from __future__ import annotations

import ast
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

import numpy as np
from shapely.geometry import Point, Polygon
from shapely.ops import unary_union
import trimesh


HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if p.name == "hardware").parent


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def literal_assignment(path, name):
    tree = ast.parse(path.read_text())
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(
                isinstance(target, ast.Name) and target.id == name for target in node.targets):
            return ast.literal_eval(node.value)
    raise ValueError(name)


def main():
    registration_path = HERE / "scan-registration.json"
    ring_path = HERE / "terminal-ring-scan.json"
    operating_path = HERE / "branch-operating-measurements.json"
    registration = json.loads(registration_path.read_text())
    ring = json.loads(ring_path.read_text())
    operating = json.loads(operating_path.read_text())
    scan_path = Path(registration["mesh_archive_path"])
    if sha(scan_path) != registration["mesh_sha256"]:
        raise ValueError("Registered scan bytes differ")
    if (sha(registration_path) != ring["input_sha256"][registration_path.name]
            or sha(operating_path) != ring["input_sha256"][operating_path.name]):
        raise ValueError("Terminal fit inputs differ from the recorded registration or measurements")

    mesh = trimesh.load(scan_path, process=False)
    origin = np.asarray(registration["frame"]["origin_in_scan_mm"])
    basis = np.asarray(registration["frame"]["reference_axes_in_scan_columns"])
    vertices = (mesh.vertices - origin) @ basis
    points = (mesh.triangles_center - origin) @ basis
    normals = mesh.face_normals @ basis
    radius = np.linalg.norm(points[:, [0, 2]], axis=1)
    face = ring["terminal_face"]
    plane_error = (points[:, 1] - face["axis_intercept_y_mm"]
                   - points[:, [0, 2]] @ np.asarray(face["plane_slopes_xz"]))
    selected = ((points[:, 1] > 21.0) & (points[:, 1] < 21.8)
                & (radius > 3.2) & (radius < 5.8) & (normals[:, 1] > .85)
                & (abs(plane_error) < .3))
    triangles = vertices[mesh.faces[selected]][:, :, [0, 2]]
    observed_face = unary_union([Polygon(triangle) for triangle in triangles])

    assembly_source = ROOT / "hardware/manifold-layout/enclosure_assembly.py"
    tee_source = ROOT / "hardware/reference/tee-connector/tee_connector.py"
    aperture_d = literal_assignment(assembly_source, "PLATE_HOLE_D")
    nominal_collar_d = literal_assignment(tee_source, "COLLAR_NOMINAL_D")
    envelope_d = literal_assignment(tee_source, "COLLAR_ENVELOPE_D")
    fixed_end = literal_assignment(tee_source, "BRANCH_FIXED_END")
    aperture_r = aperture_d / 2
    if aperture_d != 8.5:
        raise ValueError("Review the bearing selections for a changed release aperture")

    def circle(radius, x=0., z=0.):
        return Point(x, z).buffer(radius, quad_segs=180)

    bands = []
    for inner, outer in ((4.25, 4.50), (4.25, 4.75), (4.25, 5.00)):
        band = circle(outer).difference(circle(inner))
        retained = observed_face.intersection(band).area
        bands.append({"inner_radius_mm": inner, "outer_radius_mm": outer,
                      "annular_band_area_mm2": band.area,
                      "observed_projected_area_mm2": retained,
                      "coverage_fraction": retained / band.area,
                      "unobserved_projected_area_mm2": band.area - retained})

    sectors = []
    for i in range(36):
        angles = np.linspace(-np.pi + i*np.pi/18, -np.pi + (i+1)*np.pi/18, 25)
        sectors.append(Polygon([(0, 0), *np.c_[8*np.cos(angles), 8*np.sin(angles)].tolist(), (0, 0)]))
    offset_readings = []
    # 0.25 is the journal air over the sampled envelope. 0.35 is the journal
    # air over nominal Ø16.3; 0.50 is an additional sensitivity case only.
    for offset in (0., .25, .35, .50):
        rows = []
        for angle in np.linspace(-np.pi, np.pi, 72, endpoint=False):
            x, z = offset * np.array([np.cos(angle), np.sin(angle)])
            overlap = observed_face.difference(circle(aperture_r, x, z))
            areas = [overlap.intersection(sector).area for sector in sectors]
            rows.append({"offset_angle_degrees": float(np.degrees(angle)),
                         "projected_area_mm2": overlap.area,
                         "minimum_10_degree_sector_area_mm2": min(areas),
                         "sectors_with_observed_face": sum(area > 1e-6 for area in areas)})
        offset_readings.append({"offset_mm": offset, "angles_sampled": len(rows),
                                "minimum_projected_area_mm2": min(row["projected_area_mm2"] for row in rows),
                                "minimum_sector_area_mm2": min(row["minimum_10_degree_sector_area_mm2"] for row in rows),
                                "minimum_present_sectors": min(row["sectors_with_observed_face"] for row in rows)})

    wall = ((points[:, 1] > 20.) & (points[:, 1] < 20.75)
            & (radius > 4.5) & (radius < 6.) & (abs(normals[:, 1]) < .35))
    raw_wall_min = float(radius[wall].min())
    nominal = operating["derived_nominal_stations"]
    fixed_face = next(item for item in ring["fixed_reduced_barrel_face_candidates"]
                      if item["arm"] == "branch")
    nominal_pressed = nominal["pressed_branch_face_from_run_axis_mm"]

    report = {
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "scope": __doc__,
        "input_sha256": {"archived_scan": sha(scan_path),
                         registration_path.name: sha(registration_path),
                         ring_path.name: sha(ring_path), operating_path.name: sha(operating_path)},
        "source_sha256": {str(Path(__file__).relative_to(ROOT)): sha(__file__),
                          str(assembly_source.relative_to(ROOT)): sha(assembly_source),
                          str(tee_source.relative_to(ROOT)): sha(tee_source)},
        "scale": 1.0,
        "selection": {"branch_y_mm": [21., 21.8], "radius_mm": [3.2, 5.8],
                      "outward_normal_y_minimum": .85,
                      "absolute_fitted_face_plane_residual_maximum_mm": .3,
                      "triangles": int(sum(selected)),
                      "description": "Union of actual selected triangle projections; no filling of missing sectors or rescaling."},
        "aperture_diameter_mm": aperture_d,
        "projected_terminal_face_area_mm2": observed_face.area,
        "projected_face_outside_aperture_mm2": observed_face.difference(circle(aperture_r)).area,
        "annular_bands": bands,
        "offset_sensitivity": offset_readings,
        "offset_qualification": "Sampled offsets illustrate radial registration/journal play. They are not manufacturing tolerance bounds or a mechanical contact simulation.",
        "outer_wall_measurement": {
            "fitted_diameter_mm": ring["terminal_wall"]["diameter_at_mid_station_mm"],
            "held_out_radial_p95_mm": ring["terminal_wall"]["held_out_surface_residual"]["absolute_p95_mm"],
            "minimum_selected_radius_about_registered_branch_axis_mm": raw_wall_min,
            "minimum_selected_radius_minus_aperture_radius_mm": raw_wall_min-aperture_r,
            "qualification": "Observed side-wall samples and residuals only. The rounded front edge makes the near-planar contact face smaller than this outside diameter."},
        "axial_contact": {
            "moving_feature_authority": operating["user_statement"],
            "extended_width_mm": operating["extended_width_mm"],
            "pressed_width_mm": operating["pressed_width_mm"],
            "travel_mm": operating["branch_collet_travel_mm"],
            "nominal_collar_back_diameter_mm": nominal_collar_d,
            "extended_face_from_run_axis_mm": nominal["extended_branch_face_from_run_axis_mm"],
            "pressed_face_from_run_axis_mm": nominal_pressed,
            "observed_fixed_reduced_face_outermost_station_mm": fixed_face["outer_face_station_quantiles_mm"]["max"],
            "production_fixed_reduced_barrel_envelope_end_mm": fixed_end,
            "nominal_pressed_face_to_fixed_envelope_air_mm": nominal_pressed-fixed_end,
            "clearance_collar_envelope_diameter_mm": envelope_d,
            "seam_relevance": "The plate pushes the measured outermost face. Its 1.5 mm travel and endpoint datums do not require the unmeasured rear seam; the wider fixed barrel remains behind the pressed contact plane."},
        "witness_distinction": "The native R4.26–5.0 annulus proves printed-plate stock. R5.0 is not a measured minimum ring-face radius; this scan observes only about 89% of the wider R4.25–5.0 near-planar band.",
        "assessment": {
            "sufficient_terminal_geometry_for_assembly_test_print": True,
            "additional_scan_required_before_trial": False,
            "exact_terminal_diameter_qualified": False,
            "exact_terminal_rear_seam_qualified": False,
            "physical_release_qualified": False,
            "reason": "Measured moving-face identity and stroke, observed bearing in all angular sectors and retained circular plate stock support the complete enclosure assembly trial.",
            "physical_trial_observation": "Verify that each actual ring bears on the flat shoulder, reaches release over the measured travel, and allows tube withdrawal/relocking without the larger fixed barrel bottoming on the plate.",
            "minimum_extra_measurement_if_trial_reveals_an_issue": "Measure the affected terminal ring's flat front-face outside diameter and inspect the plate contact mark; another whole-tee scan is not the first step.",
        },
        "limits": [
            "Merged-scan sleeve state is intermediate or mixed; no absolute rear seam is inferred.",
            "Projected scan area is not guaranteed flat simultaneous contact area or a strength/load rating.",
            "Scan residuals are not uncertainty bounds or production tolerances.",
            "Current full front-top stock, actual sliced support cleanup, printed fit and release effort are separate checks."
        ],
    }
    (HERE / "terminal-bearing-review.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({"face_triangles": report["selection"]["triangles"],
                      "projected_area_outside_aperture_mm2": report["projected_face_outside_aperture_mm2"],
                      "annular_bands": bands, "offset_sensitivity": offset_readings,
                      "assessment": report["assessment"]}, indent=2))


if __name__ == "__main__":
    main()
