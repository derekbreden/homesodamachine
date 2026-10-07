"""Conditional ASSE drain and shared-faucet-cavity calculations.

The caller supplies geometry and path measurements from the current native
generators. This module does not certify the vent device, read a physical print,
or assume a permitted backpressure. Units are stated in every input/output name.
"""
from __future__ import annotations

import argparse
from collections import defaultdict
import hashlib
import json
import math
from pathlib import Path

G = 9.80665
PSI_PA = 6894.757293168

MANUFACTURER_EVIDENCE = [
    {
        "url": "https://www.andersonbrass.com/product-page/abf-series-asse-1022-vented-dual-check-backflow",
        "supports": "The ABF atmospheric vent exhausts CO2 and water following primary-check leakage.",
        "limit": "The public page supplies no numeric allowable vent backpressure, rise or reduced-bore limit.",
    },
    {
        "url": "https://www.multiplexbeverage.com/getmedia/b03506e7-69e1-407f-bd99-f594b8f1ba88/Parts-Book-May-2022.pdf",
        "supports": "The manufacturer identifies 19-0897 and the ASSE 1022 family; page 25 gives 10–200 psi working pressure and 130 F working temperature.",
        "limit": "Those are device operating ratings, not an allowable vent-tube pressure loss.",
    },
    {
        "url": "https://assets.freshwatersystems.com/image/upload/s--N9disqrx--/gjtidjfc0tlprqbhb4ka.pdf",
        "supports": "neoFlo LLDPE-4MM-200M-X: 4 mm OD, 2.5 mm ID, 0.75 mm wall, R25 minimum; white color code W.",
        "limit": "Confirm the supplied tube is the specified product; tube pressure rating does not qualify the backflow device's vent route.",
    },
]


def _friction_factor(reynolds: float) -> float:
    """Smooth-pipe Darcy factor; upper branch through transition is a screen."""
    if reynolds <= 0:
        return 0.0
    if reynolds < 2000:
        return 64.0 / reynolds
    turbulent = 0.3164 / reynolds ** 0.25
    return max(64.0 / reynolds, turbulent) if reynolds < 4000 else turbulent


def water_pressure_pa(flow_lpm: float, length_m: float, id_mm: float,
                      rise_m: float, loss_k: float = 0.0,
                      density_kg_m3: float = 998.2,
                      viscosity_pa_s: float = 0.001002) -> float:
    """Full, steady, single-phase pipe: hydrostatic head plus Darcy losses."""
    diameter = id_mm / 1000.0
    area = math.pi * diameter ** 2 / 4.0
    velocity = flow_lpm / 60000.0 / area
    reynolds = density_kg_m3 * velocity * diameter / viscosity_pa_s
    return (density_kg_m3 * G * rise_m
            + (_friction_factor(reynolds) * length_m / diameter + loss_k)
            * density_kg_m3 * velocity ** 2 / 2.0)


def water_flow_lpm(pressure_psi: float, **pipe) -> float:
    """Unrestricted-line envelope, excluding the device and its fault opening."""
    target = pressure_psi * PSI_PA
    if target <= water_pressure_pa(0.0, **pipe):
        return 0.0
    lo, hi = 0.0, 1.0
    while water_pressure_pa(hi, **pipe) < target:
        hi *= 2.0
    for _ in range(65):
        mid = (lo + hi) / 2.0
        if water_pressure_pa(mid, **pipe) < target:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2.0


def _slot_inside(x: float, station: float, width: float,
                 length: float, corner: float) -> bool:
    dx = max(abs(x) - (width / 2.0 - corner), 0.0)
    ds = max(abs(station - length / 2.0) - (length / 2.0 - corner), 0.0)
    return dx * dx + ds * ds <= corner * corner


def wet_floor_bounds(p: dict, x_mm: float = 0.0) -> tuple[float, float]:
    """Stations where the circular floor meets the actual planar gland faces.

    The center-floor bounds are mandatory inputs. Native gland coordinates,
    when supplied, also clip the opening at nonzero lateral coordinates.
    """
    native = ("upstream_gland_s_mm", "downstream_gland_s_mm",
              "gland_mid_shift_s_mm", "gland_body_mid_z_mm", "gland_length_mm")
    if not all(key in p for key in native):
        return p["cavity_start_s_mm"], p["cavity_end_s_mm"]
    radius = (p["water_radius_mm"] + p["shell_center_n_mm"]
              - math.sqrt(p["cavity_inner_radius_mm"] ** 2 - x_mm ** 2))
    rs = p["station_radius_mm"]
    shift = p["gland_mid_shift_s_mm"]
    mid = p["gland_body_mid_z_mm"]
    return (p["upstream_gland_s_mm"] + shift
            + rs * math.asin((p["gland_length_mm"] - mid) / radius),
            p["downstream_gland_s_mm"] + shift + rs * math.asin(-mid / radius))


def gravity_floor_datum(p: dict) -> tuple[float, float, float]:
    """Lowest endpoint Z, highest floor Z and crown station, without arc Z."""
    radius = p["water_radius_mm"] + p["shell_center_n_mm"] - p["cavity_inner_radius_mm"]
    split = math.radians(p["split_angle_deg"])
    rs = p["station_radius_mm"]
    start, end = wet_floor_bounds(p)
    za, zb = (radius * math.sin(split + s / rs) for s in (start, end))
    crown = (math.pi / 2 - split) * rs
    return min(za, zb), radius if start <= crown <= end else max(za, zb), crown


def port_chord_length_mm(p: dict) -> float:
    floor_radius = p["water_radius_mm"] + p["shell_center_n_mm"] - p["cavity_inner_radius_mm"]
    return 2 * floor_radius * math.sin(p["port_length_s_mm"] / (2 * p["station_radius_mm"]))


def mouth_inside(p: dict, x_mm: float, station_mm: float) -> bool:
    """Conservative mouth: minimum profile width, without the side flare."""
    width, corner = p["port_width_mm"], p["port_corner_radius_mm"]
    if p.get("outlet_coordinate_model") == "radial_chord":
        chord = port_chord_length_mm(p)
        midpoint = p["port_start_s_mm"] + p["port_length_s_mm"] / 2
        radius = (p["water_radius_mm"] + p["shell_center_n_mm"]
                  - math.sqrt(p["cavity_inner_radius_mm"] ** 2 - x_mm ** 2))
        tangent_coordinate = radius * math.sin((station_mm - midpoint) / p["station_radius_mm"])
        return _slot_inside(x_mm, tangent_coordinate + chord / 2, width, chord, corner)
    return _slot_inside(x_mm, station_mm - p["port_start_s_mm"], width,
                        p["port_length_s_mm"], corner)


def port_cells(p: dict, nx: int = 240, ns: int = 400) -> list[tuple[float, float]]:
    """(height above low floor in mm, conservative normal area in m²).

    Port width and window length are X and water-arc station dimensions. The
    radial-chord cutter tests its rounded rectangle in the actual tangent
    coordinates, using the minimum width and giving its side flare no credit.
    Its inward
    mouth follows the circular cavity floor. Use the center floor's arc-length
    scale throughout: this understates area at nonzero X, where radius grows.
    Only area exposed directly to the wet round chamber is credited. The
    intentional downstream keeper undercut receives no hydraulic area credit.
    Height varies with both station and circular cross-section. Binning heights
    to 0.005 mm bounds the integration's height approximation by 0.0025 mm.
    """
    rw = p["water_radius_mm"]
    rs = p["station_radius_mm"]
    ri = p["cavity_inner_radius_mm"]
    cn = p["shell_center_n_mm"]
    floor_radius = rw + cn - ri
    angle = math.radians(p["split_angle_deg"])
    start = p["port_start_s_mm"]
    low_z, _, _ = gravity_floor_datum(p)
    width, length = p["port_width_mm"], p["port_length_s_mm"]
    area_cell = width / nx * length / ns / 1e6 * floor_radius / rs
    cells = defaultdict(float)
    for ix in range(nx):
        x = -width / 2.0 + width * (ix + 0.5) / nx
        local_radius = rw + cn - math.sqrt(ri * ri - x * x)
        wetstart, wetend = wet_floor_bounds(p, x)
        for js in range(ns):
            s = length * (js + 0.5) / ns
            if (not mouth_inside(p, x, start + s)
                    or not wetstart <= start + s <= wetend):
                continue
            height = local_radius * math.sin(angle + (start + s) / rs) - low_z
            cells[round(height / 0.005)] += area_cell
    return sorted((key * 0.005, area) for key, area in cells.items())


def port_flow_lpm(head_mm: float, cells: list[tuple[float, float]],
                  discharge_coefficient: float = 0.6) -> float:
    """Shallow-head orifice screen integrated over the curved floor opening."""
    return 60000.0 * discharge_coefficient * sum(
        area * math.sqrt(2.0 * G * max(head_mm - height, 0.0) / 1000.0)
        for height, area in cells)


def port_head_mm(flow_lpm: float, cells: list[tuple[float, float]],
                 discharge_coefficient: float = 0.6) -> float:
    lo, hi = 0.0, 100.0
    for _ in range(60):
        mid = (lo + hi) / 2.0
        if port_flow_lpm(mid, cells, discharge_coefficient) < flow_lpm:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2.0


def dry_co2_pressure_psi(std_flow_lpm: float, length_m: float,
                         id_mm: float, loss_k: float = 5.0) -> float:
    """Low-Mach, dry ideal-gas screen only; standard state 20 C / 1 atm.

    Integrated isothermal Darcy relation, omitting acceleration. Do not apply
    it to wet slugs, flashing liquid, high-rate/choked flow or a closed outlet.
    """
    diameter = id_mm / 1000.0
    area = math.pi * diameter ** 2 / 4.0
    temp = 293.15
    gas_constant = 8.314462618 / 0.0440095
    outlet_pa = 101325.0
    viscosity = 1.48e-5
    density = outlet_pa / (gas_constant * temp)
    mass_flow = density * std_flow_lpm / 60000.0
    reynolds = mass_flow * diameter / (area * viscosity)
    inlet_pa = math.sqrt(outlet_pa ** 2
                         + (_friction_factor(reynolds) * length_m / diameter + loss_k)
                         * mass_flow ** 2 * gas_constant * temp / area ** 2)
    return (inlet_pa - outlet_pa) / PSI_PA


def assess(p: dict) -> dict:
    """Return evidence with explicit separation of geometry and qualification."""
    required = ("water_radius_mm", "station_radius_mm", "split_angle_deg",
                "shell_center_n_mm", "cavity_inner_radius_mm", "cavity_start_s_mm",
                "cavity_end_s_mm", "drain_cut_s_mm", "drain_center_n_mm",
                "drain_od_mm", "drain_id_mm", "flavor_od_mm", "soda_od_mm",
                "ribbon_width_mm", "ribbon_depth_mm", "port_start_s_mm",
                "port_width_mm", "port_length_s_mm", "port_corner_radius_mm",
                "line_length_m", "rise_m")
    for key in required:
        if key not in p or not math.isfinite(p[key]):
            raise ValueError(f"Missing or nonfinite input: {key}")
    for key in ("water_radius_mm", "station_radius_mm", "cavity_inner_radius_mm",
                "drain_od_mm", "drain_id_mm", "line_length_m",
                "port_width_mm", "port_length_s_mm"):
        if p[key] <= 0:
            raise ValueError(f"Nonpositive dimension: {key}")
    if not 0 < p["drain_id_mm"] < p["drain_od_mm"]:
        raise ValueError("The drain tube must have positive wall thickness")
    corner = p["port_corner_radius_mm"]
    if not 0 < corner <= min(p["port_width_mm"], p["port_length_s_mm"]) / 2:
        raise ValueError("Port corner radius outside rounded-rectangle bounds")
    if p["port_width_mm"] >= 2 * p["cavity_inner_radius_mm"]:
        raise ValueError("Port spans beyond the circular cavity")

    rw, rs, cn, ri = (p[k] for k in ("water_radius_mm", "station_radius_mm",
                                    "shell_center_n_mm", "cavity_inner_radius_mm"))
    split = math.radians(p["split_angle_deg"])
    theta_start = split + p["cavity_start_s_mm"] / rs
    theta_end = split + p["cavity_end_s_mm"] / rs
    floor_radius = rw + cn - ri
    low_z, high_z, crown_s = gravity_floor_datum(p)
    theta_d = split + p["drain_cut_s_mm"] / rs
    d_bore_low_head = ((rw + p["drain_center_n_mm"] - p["drain_id_mm"] / 2)
                       * math.sin(theta_d) - low_z)
    floor_rise = floor_radius * (math.sin(theta_end) - math.sin(theta_start))
    open_area = (math.pi * ri ** 2 - math.pi * p["soda_od_mm"] ** 2 / 4
                 - 2 * math.pi * p["flavor_od_mm"] ** 2 / 4
                 - p["ribbon_width_mm"] * p["ribbon_depth_mm"])
    checks = {
        "wet_floor_within_upper_half_of_arch": 0 < theta_start < theta_end < math.pi,
        "port_covers_entire_wet_center_floor": (
            p["port_start_s_mm"] <= p["cavity_start_s_mm"] + 1e-6
            and p["port_start_s_mm"] + p["port_length_s_mm"] >= p["cavity_end_s_mm"] - 1e-6),
        "port_has_finite_flat_end_width": p["port_width_mm"] > 2 * corner,
        "drain_end_free_inside_cavity": p["cavity_start_s_mm"] < p["drain_cut_s_mm"] < p["cavity_end_s_mm"],
        "free_area_positive": open_area > 0,
        "port_below_soda_tube": ri - cn > p["soda_od_mm"] / 2,
    }
    profile_gaps = {}
    if all(key in p for key in ("flavor_center_x_mm", "flavor_center_n_mm", "ribbon_center_n_mm")):
        fx, fn, rn = (p[k] for k in ("flavor_center_x_mm", "flavor_center_n_mm", "ribbon_center_n_mm"))
        circles = {
            "S": (0.0, 0.0, p["soda_od_mm"] / 2),
            "F1": (-fx, fn, p["flavor_od_mm"] / 2),
            "F2": (fx, fn, p["flavor_od_mm"] / 2),
            "D": (0.0, p["drain_center_n_mm"], p["drain_od_mm"] / 2),
        }
        names = tuple(circles)
        for i, name in enumerate(names):
            x, n, radius = circles[name]
            profile_gaps[name + "_to_cavity"] = ri - math.hypot(x, n - cn) - radius
            for other in names[i + 1:]:
                ox, on, other_radius = circles[other]
                profile_gaps[name + "_to_" + other] = math.hypot(x - ox, n - on) - radius - other_radius
            rx = max(abs(x) - p["ribbon_width_mm"] / 2, 0.0)
            ry = max(abs(n - rn) - p["ribbon_depth_mm"] / 2, 0.0)
            profile_gaps[name + "_to_ribbon_envelope"] = math.hypot(rx, ry) - radius
        ribbon_reach = max(math.hypot(x, n - cn)
                           for x in (-p["ribbon_width_mm"] / 2, p["ribbon_width_mm"] / 2)
                           for n in (rn - p["ribbon_depth_mm"] / 2, rn + p["ribbon_depth_mm"] / 2))
        profile_gaps["ribbon_envelope_to_cavity"] = ri - ribbon_reach
        checks["spread_bundle_is_nonintersecting_inside_round_cavity"] = min(profile_gaps.values()) >= 0
    if "wet_bundle_positions_constant" in p:
        checks["spread_bundle_constant_through_wet_cavity"] = p["wet_bundle_positions_constant"]
    plane_bounds = wet_floor_bounds(p)
    checks["native_planar_floor_endpoints_match"] = max(
        abs(a - b) for a, b in zip(plane_bounds, (p["cavity_start_s_mm"], p["cavity_end_s_mm"]))) < 1e-6
    cells = port_cells(p)
    coarse = port_cells(p, 120, 200)
    flow10 = port_flow_lpm(10.0, cells)
    pipe = dict(length_m=p["line_length_m"], id_mm=p["drain_id_mm"], rise_m=p["rise_m"])
    cold = dict(density_kg_m3=999.9, viscosity_pa_s=0.00167)
    pressure_flows = []
    for pressure in (5.0, 10.0, 43.5, 80.0, 100.0, 125.0, 200.0):
        q = water_flow_lpm(pressure, **pipe)
        head = port_head_mm(q, cells)
        pressure_flows.append({
            "available_pressure_psi": pressure,
            "unrestricted_nominal_id_flow_20C_lpm_K0": q,
            "unrestricted_nominal_id_flow_2C_lpm_K0": water_flow_lpm(pressure, **pipe, **cold),
            "cavity_head_at_20C_flow_mm_Cd0_6": head,
            "drain_bore_clearance_above_water_mm": d_bore_low_head - head,
        })
    pressure_losses = [
        {"flow_lpm": q,
         "required_pressure_20C_psi_K5": water_pressure_pa(q, **pipe, loss_k=5) / PSI_PA,
         "required_pressure_2C_psi_K5": water_pressure_pa(q, **pipe, loss_k=5, **cold) / PSI_PA}
        for q in (0.01, 0.05, 0.1, 0.25, 0.5, 1.0)
    ]
    dry = [{"dry_CO2_std_lpm_20C_1atm": q,
            "estimated_pressure_psi_K5": dry_co2_pressure_psi(q, p["line_length_m"], p["drain_id_mm"])}
           for q in (1.0, 5.0, 10.0)]
    # An independent laminar identity checks units and Darcy-factor convention.
    test_q = 0.1
    diameter = p["drain_id_mm"] / 1000
    poiseuille = (128 * 0.001002 * p["line_length_m"] * (test_q / 60000)
                  / (math.pi * diameter ** 4) + 998.2 * G * p["rise_m"])
    calculated = water_pressure_pa(test_q, **pipe)
    validation = {
        "laminar_0_1lpm_matches_Poiseuille_relative_error": abs(calculated - poiseuille) / max(abs(poiseuille), 1.0),
        "zero_cavity_head_has_zero_discharge": port_flow_lpm(0.0, cells) == 0.0,
        "pressure_below_static_head_has_zero_full_line_flow": water_flow_lpm(
            max(0, water_pressure_pa(0.0, **pipe) / PSI_PA - 0.001), **pipe) == 0.0,
        "port_quadrature_flow10_relative_change": abs(flow10 - port_flow_lpm(10.0, coarse)) / flow10,
    }
    validation_passed = (validation["laminar_0_1lpm_matches_Poiseuille_relative_error"] < 1e-12
                         and validation["zero_cavity_head_has_zero_discharge"]
                         and validation["pressure_below_static_head_has_zero_full_line_flow"]
                         and validation["port_quadrature_flow10_relative_change"] < 0.002)
    sensitivities = []
    for id_mm in (p["drain_id_mm"] - 0.15, p["drain_id_mm"], p["drain_id_mm"] + 0.15):
        q = water_flow_lpm(125.0, **(pipe | {"id_mm": id_mm}))
        for cd in (0.4, 0.6, 0.8):
            head = port_head_mm(q, cells, cd)
            sensitivities.append({"assumed_id_mm": id_mm, "assumed_Cd": cd,
                                  "available_pressure_psi": 125.0, "flow_lpm": q,
                                  "cavity_head_mm": head,
                                  "drain_bore_clearance_mm": d_bore_low_head - head})
    route_sensitivity = []
    for length in sorted(set((1.0, 1.5, p["line_length_m"]))):
        for rise in sorted(set((0.0, p["rise_m"], 1.0))):
            q = water_flow_lpm(125.0, **(pipe | {"length_m": length, "rise_m": rise}))
            head = port_head_mm(q, cells)
            route_sensitivity.append({"assumed_small_tube_length_m": length,
                                      "assumed_rise_m": rise,
                                      "available_pressure_psi": 125.0,
                                      "flow_lpm_K0": q,
                                      "cavity_head_mm_Cd0_6": head,
                                      "drain_bore_clearance_mm": d_bore_low_head - head})
    margin_flow = port_flow_lpm(d_bore_low_head - 2.0, cells)
    unit_length_pressure = water_pressure_pa(margin_flow, 1.0, p["drain_id_mm"], 0.0)
    minimum_model_length = 125.0 * PSI_PA / unit_length_pressure
    return {
        "schema": 2,
        "status": "Conditional design calculations; hydraulic qualification pending",
        "hydraulically_qualified": False,
        "inputs": p,
        "analytic_geometry_checks": checks,
        "analytic_geometry_passed": all(checks.values()),
        "numerical_validation": validation,
        "numerical_validation_passed": validation_passed,
        "geometry": {
            "wet_start_angle_deg": math.degrees(theta_start),
            "wet_end_angle_deg": math.degrees(theta_end),
            "upstream_floor_is_gravity_low": floor_rise >= 0,
            "floor_crosses_gravity_crown": p["cavity_start_s_mm"] <= crown_s <= p["cavity_end_s_mm"],
            "floor_crown_station_mm": crown_s,
            "highest_center_floor_above_gravity_low_mm": high_z - low_z,
            "drainage_rule": "The port opens the complete wet center floor, including both sides of the crown. Cross-section floor water has a path toward the open bottom center; a closed monotonic longitudinal floor is not required.",
            "floor_rise_to_downstream_end_mm": floor_rise,
            "free_cavity_area_after_three_tubes_and_ribbon_mm2": open_area,
            "minimum_free_area_before_D_cut_mm2": open_area - math.pi * p["drain_od_mm"] ** 2 / 4,
            "free_area_scope": "Area arithmetic assumes the native nonintersection and inside-cavity checks pass; D terminates at entry.",
            "spread_profile_clearances_mm": profile_gaps,
            "drain_bore_area_mm2": math.pi * p["drain_id_mm"] ** 2 / 4,
            "drain_bore_low_edge_above_low_floor_mm": d_bore_low_head,
            "nominal_under_soda_floor_clearance_mm": ri - cn - p["soda_od_mm"] / 2,
            "port_arc_station_window_length_mm": p["port_length_s_mm"],
            "port_tangent_chord_length_mm": port_chord_length_mm(p),
            "port_minimum_profile_flat_area_mm2": p["port_width_mm"] * (
                port_chord_length_mm(p) if p.get("outlet_coordinate_model") == "radial_chord"
                else p["port_length_s_mm"]) - (4 - math.pi) * corner ** 2,
            "port_conservative_projected_wet_area_mm2": sum(area for _, area in cells) * 1e6,
            "port_area_scope": "Only the round wet chamber's exposed inner-floor mouth, clipped by actual planar gland faces. Downstream keeper undercut, widening flare and transverse surface-area increase are uncredited reserve. Native cutter/seat and exterior-throat checks remain separate.",
            "quadrature_area_relative_difference": abs(sum(a for _, a in cells) - sum(a for _, a in coarse)) / sum(a for _, a in cells),
            "quadrature_flow10_relative_difference": abs(flow10 - port_flow_lpm(10.0, coarse)) / flow10,
        },
        "wet_line": {
            "static_column_pressure_20C_psi": water_pressure_pa(0.0, **pipe) / PSI_PA,
            "water_volume_in_small_bore_mL": math.pi * (p["drain_id_mm"] / 1000) ** 2 / 4 * p["line_length_m"] * 1e6,
            "water_volume_in_PVC_mL": math.pi * (p.get("pvc_id_mm", 6.35) / 1000) ** 2 / 4 * p.get("pvc_length_m", 0) * 1e6,
            "water_volume_scope": "Nominal unobstructed bore at the modeled endpoint lengths, excluding socket/barb insertion interiors and overlaps. No measured installed hold-up or tube-cut-length result.",
            "required_pressure_screen": pressure_losses,
            "pressure_to_flow_envelopes": pressure_flows,
            "bore_and_Cd_sensitivity_not_supplier_tolerances": sensitivities,
            "length_and_rise_sensitivity_not_installation_approval": route_sensitivity,
            "conditional_minimum_small_line_length_m_for_2mm_margin_at125psi_20C_K0_Cd0_6_zero_rise": minimum_model_length,
            "route_sensitivity_scope": "Shortening tubing can raise fault flow. These are single-phase model sensitivities, not required ASSE vent restrictions or a qualified installation range.",
        },
        "port": {
            "coefficient_is_assumed_not_measured": True,
            "flow_at_head_Cd0_6": [{"head_mm": h, "flow_lpm": port_flow_lpm(h, cells)} for h in (1.0, 3.0, 5.0, 8.0, 10.0, 11.0)],
            "head_at_fixture_flow_Cd0_6": [{"flow_lpm": q, "head_mm": port_head_mm(q, cells)} for q in (0.05, 1.0, 2.5, 3.0)],
            "head_limit_for_2mm_bore_clearance_mm": d_bore_low_head - 2.0,
            "flow_at_2mm_bore_clearance_lpm_Cd0_6": port_flow_lpm(d_bore_low_head - 2.0, cells),
        },
        "dry_CO2_screen": dry,
        "method": {
            "liquid": "Darcy-Weisbach; f = 64/Re below 2000; Blasius smooth-pipe correlation above 4000; upper branch through transition. Device internals excluded.",
            "capacity": "K = 0 is an unrestricted-line sizing envelope. K = 5 is an unmeasured fitting/bend sensitivity. Actual losses and fault opening are unknown.",
            "port": "Cd * integral(sqrt(2 * g * head)) * dA over the wet curved-floor opening, clipped by planar gland faces. Conservative area scale is lowest floor radius / station radius.",
            "gas": "Low-Mach dry ideal CO2 at 20 C / 1 atm; isothermal integrated Darcy screen. Slugs, flashing, choking and device internals excluded.",
            "temperature": "Water screening assumptions: 20 C density 998.2 kg/m3, viscosity 1.002 mPa*s; 2 C density 999.9 kg/m3, viscosity 1.67 mPa*s.",
        },
        "manufacturer_evidence": MANUFACTURER_EVIDENCE,
        "limits": [
            "No device-specific permissible vent pressure loss or reduced/rising-tube approval is established by the public sources reviewed.",
            "The small internal separation is a discharge cavity, not a claimed plumbing air gap.",
            "Single-phase models do not establish CO2-water fault behavior, dry-to-wet transition or retained-column effects on the ASSE device.",
            "Native geometry does not establish deposited-part water tightness, elastomer seal performance or assembly repeatability.",
        ],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    data = json.loads(args.input.read_text())
    result = assess(data)
    result["calculation_source_sha256"] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    result["input_file_sha256"] = hashlib.sha256(args.input.read_bytes()).hexdigest()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({"output": str(args.output),
                      "analytic_geometry_passed": result["analytic_geometry_passed"],
                      "numerical_validation_passed": result["numerical_validation_passed"],
                      "hydraulically_qualified": False}))
    if not result["analytic_geometry_passed"] or not result["numerical_validation_passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
