"""Bind native faucet dimensions to the conditional hydraulic calculation.

Path length and installed elevation are required caller inputs with a recorded
model or physical measurement scope. The shortened viewer umbilical is not the
factory tube length.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path
import sys

FAUCET = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(FAUCET))
import faucet_paths as paths


def bind(*, line_length_m: float, rise_m: float, pvc_length_m: float = 0.0,
         measurement_evidence: dict | None = None,
         gland_dimensions: dict | None = None) -> dict:
    p = paths
    result = {
        "water_radius_mm": p.WATER_RADIUS,
        "station_radius_mm": p.WATER_RADIUS,
        "split_angle_deg": math.degrees(p.JOINT_ANGLE),
        "shell_center_n_mm": p.SHELL_CENTER_N,
        "cavity_inner_radius_mm": p.CAVITY_RADIUS,
        "cavity_start_s_mm": p.WET_START_S,
        "cavity_end_s_mm": p.WET_END_S,
        "upstream_gland_s_mm": p.UPSTREAM_GLAND_S,
        "downstream_gland_s_mm": p.DOWNSTREAM_GLAND_S,
        "gland_mid_shift_s_mm": p.GLAND_MID_SHIFT_S,
        "gland_body_mid_z_mm": p.GLAND_BODY_MID_Z,
        "gland_length_mm": p.GLAND_LENGTH,
        "drain_cut_s_mm": p.DRAIN_CUT_S,
        "drain_center_n_mm": p.SEAL_DRAIN_N,
        "drain_od_mm": p.DRAIN_OD,
        "drain_id_mm": p.DRAIN_ID,
        "flavor_od_mm": p.FLAVOR_OD,
        "soda_od_mm": p.WATER_OD,
        "flavor_center_x_mm": p.SEAL_FLAVOR_X,
        "flavor_center_n_mm": p.SEAL_FLAVOR_N,
        "ribbon_center_n_mm": p.SEAL_RIBBON_N,
        "ribbon_width_mm": p.positions(p.WET_START_S)[4],
        "ribbon_depth_mm": 1.3,
        "wet_bundle_positions_constant": all(
            max(abs(a-b) for a, b in zip(p.positions(s), p.positions(p.WET_START_S))) < 1e-9
            for s in (p.WET_START_S, (p.WET_START_S + p.WET_END_S) / 2, p.WET_END_S)),
        "port_start_s_mm": p.PORT_START_S,
        "port_width_mm": p.PORT_WIDTH,
        "port_length_s_mm": p.PORT_LENGTH_S,
        "port_corner_radius_mm": p.PORT_CORNER_R,
        "outlet_coordinate_model": "radial_chord",
        "line_length_m": line_length_m,
        "rise_m": rise_m,
        "pvc_length_m": pvc_length_m,
        "pvc_id_mm": 6.35,
        "native_dimension_source": str((FAUCET / "faucet_paths.py").relative_to(FAUCET.parents[2])),
        "native_dimension_source_sha256": hashlib.sha256((FAUCET / "faucet_paths.py").read_bytes()).hexdigest(),
        "measurement_evidence": measurement_evidence or {},
    }
    if gland_dimensions:
        result["gland_dimensions"] = gland_dimensions
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--line-length-mm", type=float, required=True)
    parser.add_argument("--rise-mm", type=float, required=True)
    parser.add_argument("--pvc-length-mm", type=float, default=0.0)
    parser.add_argument("--measurement-evidence", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    evidence = json.loads(args.measurement_evidence.read_text()) if args.measurement_evidence else {}
    data = bind(line_length_m=args.line_length_mm / 1000,
                rise_m=args.rise_mm / 1000,
                pvc_length_m=args.pvc_length_mm / 1000,
                measurement_evidence=evidence)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(data, indent=2) + "\n")
    print(str(args.output))


if __name__ == "__main__":
    main()
