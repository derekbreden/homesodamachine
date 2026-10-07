"""Bind native route lengths and an explicit nominal installation elevation.

This measures CAD centerlines, not installed tubing. The elevation uses the
documented cabinet clear height, current slab/stack and current enclosure floor.
The shortened viewer umbilical is extended to its factory length. Physical
installation, socket engagement and unmodelled fitting volumes remain separate.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import sys

# This reads geometry and writes only qualification JSON; it never runs a
# production exporter or supersedes another agent's build.
os.environ.setdefault("HSM_NO_BUILD_LOCK", "1")
HERE = Path(__file__).resolve().parent
REPO = next(p for p in HERE.parents if (p / "hardware").is_dir() and (p / "tools").is_dir())
FAUCET = HERE.parent
sys.path.insert(0, str(FAUCET))
sys.path.insert(0, str(REPO / "hardware" / "faucet-layout"))
sys.path.insert(0, str(REPO / "hardware" / "manifold-layout"))
import faucet_assembly as assembly
import faucet_paths as paths
import vent_seals as seals
import _drain as internal
from native_inputs import bind


def _sha(path: Path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _appliance_proof(step: Path, clearance: Path):
    step, clearance = step.resolve(), clearance.resolve()
    report = json.loads(clearance.read_text())
    if not report.get("passed"):
        raise ValueError("Complete appliance drain clearance has not passed")
    for rel, expected in report["source_sha256"].items():
        if _sha(REPO / rel) != expected:
            raise ValueError(f"Appliance clearance source changed: {rel}")
    return {
        "scope": "Producer handoff of the complete installed-body native clearance audit and its paired saved appliance STEP. This reader hashes the saved STEP; it does not independently rebuild or import the whole appliance. No hydraulic, physical fit or tolerance qualification.",
        "saved_appliance_step": str(step.relative_to(REPO)),
        "saved_appliance_step_sha256": _sha(step),
        "clearance_report": str(clearance.relative_to(REPO)),
        "clearance_report_sha256": _sha(clearance),
        "clearance_source_sha256": report["source_sha256"],
        "installed_body_count": report["installed_body_count"],
        "drain_body_checks": {name: {"valid": row["valid"], "solids": row["solids"],
                                     "neighbors_checked": len(row["neighbors"]), "passed": row["passed"]}
                              for name, row in report["checks"].items()},
        "bend_radii": report["bend_radii"],
        "passed_nominal_installed_clearance": True,
    }


def measure(*, cabinet_clear_height_mm: float = 755.7,
            appliance_step: Path | None = None, appliance_clearance_report: Path | None = None):
    if (appliance_step is None) != (appliance_clearance_report is None):
        raise ValueError("Supply both appliance STEP and clearance report")
    facts_path = REPO / "hardware" / "manifold-layout" / "enclosure-assembly.facts.json"
    source_paths = [Path(__file__), FAUCET / "faucet_paths.py", FAUCET / "vent_seals.py",
                    FAUCET / "_faucet_interface.py",
                    FAUCET / "faucet-shell" / "faucet_shell.py",
                    REPO / "hardware" / "faucet-layout" / "faucet_assembly.py",
                    REPO / "hardware" / "manifold-layout" / "_drain.py", facts_path,
                    REPO / "hardware" / "reference" / "neofit-drain-bulkhead" / "neofit_drain_bulkhead.py",
                    REPO / "marketing" / "install-envelope.md"]
    source_bindings = {str(p.relative_to(REPO)): _sha(p) for p in source_paths}
    facts_raw = facts_path.read_bytes()
    if hashlib.sha256(facts_raw).hexdigest() != source_bindings[str(facts_path.relative_to(REPO))]:
        raise ValueError("Enclosure facts changed before the measurement")
    facts = json.loads(facts_raw)
    vent = tuple(facts["card_ports"]["asse1022-assembly"]["vent-tip"]["pos"])
    bounds = facts["bodies"]["bulkhead-drain"]
    # This reference is coaxial with Y. Its min-Y end is the inboard socket
    # mouth; X/Z center is unchanged by its assembly carry.
    mouth = ((bounds[0] + bounds[3]) / 2, bounds[1], (bounds[2] + bounds[5]) / 2)
    members = internal.bodies(vent, mouth)
    hose_area = math.pi * (internal.PVC_OD ** 2 - internal.PVC_ID ** 2) / 4
    tube_area = math.pi * (internal.OD ** 2 - internal.ID ** 2) / 4
    pvc_length = members["hose-drain-vent"].Volume() / hose_area
    internal_length = members["tube-drain-vent"].Volume() / tube_area
    self_common = members["hose-drain-vent"].intersect(members["tube-drain-vent"])
    self_overlap = sum(s.Volume() for s in self_common.Solids())
    wire = assembly.drain_path()
    upper = paths.path_wire("drain", bottom_z=assembly.under_counter_plate_bottom_z)
    factory_extension = assembly.blue_cut_length - assembly.umbilical_drawn
    external_length = wire.Length() + factory_extension
    cut = paths.tube_arc_point(paths.DRAIN_CUT_S, "drain")
    enclosure_floor = facts["bodies"]["enclosure-back-bottom"][2]
    # Common cabinet-floor Z=0. The modeled faucet plate datum is above the
    # slab by the current gasket/plate stack, as stated in faucet assembly.
    faucet_datum = cabinet_clear_height_mm + assembly.countertop_thickness - assembly.countertop_top_z
    device_vent_z = vent[2] - enclosure_floor
    drain_cut_z = faucet_datum + cut[2]
    rise = drain_cut_z - device_vent_z
    evidence = {
        "scope": "Nominal native CAD centerlines and stated reference-cabinet elevation. No physical tube-length, tube-bore, device-pressure or installed-head measurement.",
        "source_sha256": source_bindings,
        "external_drawn_centerline_mm": wire.Length(),
        "external_upper_centerline_mm": upper.Length(),
        "external_lower_drawn_centerline_mm": wire.Length() - upper.Length(),
        "external_added_to_full_factory_run_mm": factory_extension,
        "external_full_factory_centerline_mm": external_length,
        "internal_small_tube_centerline_mm": internal_length,
        "total_small_tube_centerline_mm": external_length + internal_length,
        "PVC_centerline_mm": pvc_length,
        "native_internal_tube_solids_valid": all(members[name].isValid() for name in ("hose-drain-vent", "tube-drain-vent")),
        "native_internal_PVC_white_return_clearance": {
            "gap_mm": members["hose-drain-vent"].distance(members["tube-drain-vent"]),
            "overlap_mm3": self_overlap,
            "boolean_valid": self_common.isValid(),
            "passed": self_common.isValid() and self_overlap <= 1e-5,
            "scope": "These two unconnected native members only; the complete appliance audit supplies all installed neighbors.",
        },
        "internal_length_method": "Annular swept-solid volume divided by the nominal annular section area; native routing at saved enclosure device/socket coordinates.",
        "ASSE_vent_tip_enclosure_world_mm": vent,
        "bulkhead_inboard_mouth_enclosure_world_mm": mouth,
        "bulkhead_mouth_derivation": "Coaxial Y reference; min-Y end of placed bulkhead bbox, at its X/Z center. The 32.4 mm reference overall length and 22 mm flange envelope define this body.",
        "D_cut_faucet_world_mm": cut,
        "reference_installation": {
            "cabinet_clear_height_mm": cabinet_clear_height_mm,
            "cabinet_basis": "marketing/install-envelope.md; nominal product reference envelope, not a claim about every consumer cabinet",
            "slab_thickness_mm": assembly.countertop_thickness,
            "faucet_plate_datum_above_slab_mm": -assembly.countertop_top_z,
            "enclosure_local_floor_z_mm": enclosure_floor,
            "device_vent_above_cabinet_floor_mm": device_vent_z,
            "D_cut_above_cabinet_floor_mm": drain_cut_z,
            "vent_to_D_cut_rise_mm": rise,
        },
        "flow_model_scope": "Small-bore length excludes adapter/bulkhead internal bores and their minor losses. K=5 is an unmeasured fitting/bend sensitivity. PVC friction is uncredited in the K=0 higher-flow sizing envelope; its water volume is reported.",
        "fluid_volume_scope": "Nominal unobstructed bore applied to modeled endpoint lengths. Socket/barb insertion interiors and overlaps are not modeled. These volumes are not measured installed hold-up or tube cut lengths.",
    }
    if appliance_step is not None:
        evidence["completed_appliance_geometry"] = _appliance_proof(appliance_step, appliance_clearance_report)
        if not evidence["native_internal_PVC_white_return_clearance"]["passed"]:
            raise ValueError("Internal PVC/white-return collision contradicts the completed appliance audit")
    dimensions = {
        "keeper_length_mm": seals.KEEPER_LENGTH,
        "flange_groove_length_mm": seals.GROOVE_LENGTH,
        "body_length_mm": seals.BODY_LENGTH,
        "body_mid_z_mm": seals.BODY_MID_Z,
        "flange_front_z_mm": seals.BUNG_SEATED_Z,
        "protected_flange_groove_front_z_mm": seals.KEEPER_LENGTH,
        "native_seal_source_sha256": _sha(FAUCET / "vent_seals.py"),
    }
    result = bind(line_length_m=(external_length + internal_length) / 1000,
                  rise_m=rise / 1000, pvc_length_m=pvc_length / 1000,
                  measurement_evidence=evidence, gland_dimensions=dimensions)
    for rel, expected in source_bindings.items():
        if _sha(REPO / rel) != expected:
            raise ValueError(f"Route measurement source changed: {rel}")
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cabinet-clear-height-mm", type=float, default=755.7)
    parser.add_argument("--output", type=Path, default=HERE / "native-inputs.json")
    parser.add_argument("--appliance-step", type=Path)
    parser.add_argument("--appliance-clearance-report", type=Path)
    args = parser.parse_args()
    if (args.appliance_step is None) != (args.appliance_clearance_report is None):
        parser.error("Supply both --appliance-step and --appliance-clearance-report")
    data = measure(cabinet_clear_height_mm=args.cabinet_clear_height_mm,
                   appliance_step=args.appliance_step, appliance_clearance_report=args.appliance_clearance_report)
    args.output.write_text(json.dumps(data, indent=2) + "\n")
    print(json.dumps({"output": str(args.output), "small_tube_length_m": data["line_length_m"],
                      "reference_rise_m": data["rise_m"], "physical_measurement": False}))


if __name__ == "__main__":
    main()
