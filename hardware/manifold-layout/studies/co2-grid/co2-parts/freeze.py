"""Freeze the six authored gas meshes and interface evidence, without a CAD rebuild.

Manual source capture. The portable model API reads only the resulting local files.
"""
from pathlib import Path
import hashlib
import json
import subprocess
import sys

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p / "hardware/cad-artifacts.json").is_file())
sys.path.insert(0, str(ROOT))
from hardware.wiring.installed.review import base_name, load_mesh

SOURCE = "hardware/manifold-layout/enclosure-assembly.step.mesh"
FACTS = "hardware/manifold-layout/enclosure-assembly.facts.json"
POINTER = "hardware/cad-artifacts.json"
NAMES = ("wr1110", "gasher-co2", "co2-adapter-regulator-in",
         "co2-adapter-regulator-out", "co2-adapter-check-in", "co2-adapter-check-out")
SOURCES = (
    "hardware/manifold-layout/_gas_chain.py",
    "hardware/manifold-layout/_lines.py",
    "hardware/manifold-layout/enclosure_assembly.py",
    "hardware/reference/wr1110-regulator/wr1110_regulator.py",
    "hardware/reference/wr1110-regulator/README.md",
    "hardware/reference/wr1110-regulator/scan-measurements.json",
    "hardware/reference/wr1110-regulator/scan-model-check.json",
    "hardware/reference/gasher-check-valve/gasher_check_valve.py",
    "hardware/reference/gasher-check-valve/README.md",
    "hardware/reference/jg-pp010822e/jg_pp010822e.py",
    "hardware/reference/seaflo-discharge-chain/seaflo_discharge_chain.py",
    "hardware/printed-parts/cold-core/_cold_core_interface.py",
    "hardware/printed-parts/cold-core/foam-assembly/foam_assembly.py",
    "hardware/printed-parts/cold-core/_foam_cap.py",
    "hardware/assembly/internal-plumbing.md",
    "hardware/ledger/bom.md",
)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def merged(items):
    vs, fs, offset = [], [], 0
    for _, (v, f) in items:
        vs.append(v); fs.append(f + offset); offset += len(v)
    return np.vstack(vs), np.vstack(fs)


def main():
    facts = json.loads((ROOT / FACTS).read_text())
    pointer = json.loads((ROOT / POINTER).read_text())
    raw = load_mesh(ROOT / SOURCE)
    groups = {n: [] for n in NAMES}
    for full_name, mesh in raw.items():
        name = base_name(full_name)
        if name in groups:
            groups[name].append((full_name, mesh))

    z = facts["carried_points"]["wr1110.barrel"]["pos"][2]
    reg_bb = facts["bodies"]["wr1110"]
    reg_center_x = facts["carried_points"]["wr1110.barrel"]["pos"][0]
    check_bb = facts["bodies"]["gasher-co2"]
    frames = {
        "regulator": {"rotation": np.diag([-1., -1., 1.]).tolist(),
                      "translation_mm": [reg_center_x, reg_bb[4], z]},
        "check": {"rotation": np.eye(3).tolist(),
                  "translation_mm": [(check_bb[0] + check_bb[3]) / 2,
                                     (check_bb[1] + check_bb[4]) / 2, z]},
    }
    records = {}
    (HERE / "authored").mkdir(exist_ok=True)
    (HERE / "geometry").mkdir(exist_ok=True)
    for n, parts in groups.items():
        if not parts:
            raise ValueError(f"Missing source mesh {n}")
        v, f = merged(parts)
        group = "regulator" if n == "wr1110" or "regulator" in n else "check"
        frame = frames[group]
        native = (v - frame["translation_mm"]) @ np.array(frame["rotation"])
        folder = "geometry" if n in ("wr1110", "gasher-co2") else "authored"
        path = HERE / folder / (n + ".npz")
        np.savez_compressed(path, v=native.astype(np.float32), f=f.astype(np.int32))
        records[n] = {
            "snapshot": str(path.relative_to(HERE)), "sha256": sha(path),
            "coordinate_group": group,
            "source_component_names": [name for name, _ in parts],
            "source_world_bounds_mm": [v.min(0).tolist(), v.max(0).tolist()],
            "canonical_bounds_mm": [native.min(0).tolist(), native.max(0).tolist()],
            "source_analytic_bounds_mm": facts["bodies"][n],
            "vertices": len(v), "triangles": len(f),
        }
    handoff = facts["card_ports"]["foam-assembly"]["co2-in"]
    cap = {
        "name": "foam-assembly.co2-in",
        "point_mm": handoff["pos"], "outward_axis": handoff["axis"],
        "tube_od_mm": handoff["diam"], "guide_bore_diameter_mm": 7.5,
        "connection_kind": "Passive cap conduit for a continuous red tube",
        "tube_insertion_mm": None,
        "tube_terminates_here": False,
        "route_destination_below_cap": "PI010822S on the carbonator bottom plain gas-port elbow",
        "source": FACTS + ":card_ports.foam-assembly.co2-in",
        "cross_check": {
            "cap_authored_xy_mm": [1.5, 77.5],
            "core_native_after_cap_half_turn_xy_mm": [-1.5, -77.5],
            "core_native_cap_face_z_mm": 233.4,
            "core_to_world_rotation": [[0., -1., 0.], [1., 0., 0.], [0., 0., 1.]],
            "core_to_world_translation_mm": [0.00000001564078, 323.7999999, 20.0],
            "source_basis": "cap_conduits and spin_xy; FOAM_YAW90; existing fact-pack registration",
        },
    }
    evidence = {
        "units": "mm", "scope": "Frozen CO2 hardware and interfaces for an isolated layout study",
        "source_mesh": SOURCE, "source_mesh_sha256": sha(ROOT / SOURCE),
        "facts": FACTS, "facts_sha256": sha(ROOT / FACTS),
        "pointer": POINTER, "pointer_sha256": sha(ROOT / POINTER),
        "mesh_matches_pointer": sha(ROOT / SOURCE) == pointer["solids"].get(SOURCE),
        "pointer_source": pointer["source"],
        "pointer_marks_source_unproven": SOURCE in pointer.get("unproven", {}).get("members", []),
        "observed_git_head": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        "source_sha256": {p: sha(ROOT / p) for p in SOURCES},
        "canonical_frames_to_original_world": frames,
        "authored_meshes": records,
        "cap_handoff": cap,
        "reference_scope": {
            "wr1110": "Two native MINI2 scans establish exterior; used as WR1105 same-series envelope. Internal flow path, vent and thread form are not resolved.",
            "gasher-co2": "Nominal 40mm manufacturer-drawing exterior, not a scan or measured made-up assembly.",
            "authored_adapters": "Nominal purchased gray-acetal JG PI010822S/PI450822S. Existing source reuses water-fitting dimensions; active model uses the retained manufacturer sheets instead.",
        },
        "orientation": {
            "native_flow_axis": [0., 1., 0.],
            "required_flow_order": ["inlet bulkhead", "WR1105 secondary regulator", "GASHER check", "carbonator bottom gas port"],
            "body_flow_direction": "Female inlet to male outlet for both metal bodies",
            "gravity_orientation_requirement_found": False,
            "claim_scope": "No mandatory gravity orientation found in the retained geometry/evidence sources; not an independent manufacturer operating qualification.",
        },
        "known_adapter_discrepancies": {
            "PI010822S": {"authored_collet_plus_hex_reach_mm": 18.5,
                            "authored_hex_corner_diameter_mm": 16.5,
                            "drawing_mouth_to_thread_shoulder_mm": 13.7,
                            "drawing_thread_projection_mm": 14.3,
                            "drawing_across_flats_mm": 17.5, "drawing_max_body_diameter_mm": 19.1},
            "PI450822S": {"authored_overall_mm": 26.0,
                            "authored_hex_corner_diameter_mm": 16.5,
                            "drawing_overall_mm": 32.0, "drawing_across_flats_mm": 17.5,
                            "drawing_max_body_diameter_mm": 19.1},
        },
        "primary_sources": [
            {"title": "John Guest PI010822S dimension sheet, PM/PI011S01/23",
             "url": "https://www.webstaurantstore.com/documents/specsheets/jg_drinks_grey_acetal_straight_adaptor_nptf_thread_data_sheet.pdf",
             "local": "sources/jg-pi010822s-datasheet.pdf", "dimension_page": 2,
             "interpretation": "Exact PI010822S row: B15.7 insertion, C13.7, D14.3, E4.4 bore, F17.5AF, G19.1max. B and C referenced to released collet."},
            {"title": "John Guest PI450822S dimension sheet (supplier-hosted manufacturer drawing)",
             "url": "https://assets.freshwatersystems.com/image/upload/s--4bPImpOZ--/gvawd5hhd3qlszcljx2f.pdf",
             "local": "sources/jg-pi450822s-datasheet.pdf", "dimension_page": 2,
             "interpretation": "Exact PI450822S NPTF row: B32.0 overall, C15.7 insertion, D14.8 threaded-end section, E15.0body, F17.5AF, G5.3bore, H19.1max. Page2 generic heading says BSP despite row and page1 being NPTF; dimensions recorded against exact SKU."},
            {"title": "John Guest gray acetal male connector product page",
             "url": "https://www.johnguest.com/ca/en/od-tube-fittings/acetal-gray/threaded-connectors/male-connector-nptf-thread",
             "supports": "PI010822S product identity, gray-acetal/nitrile construction and CO2 beverage gas service"},
            {"title": "John Guest gray acetal female connector product page",
             "url": "https://www.johnguest.com/us/en/od-tube-fittings/acetal-gray/threaded-connectors/female-connector-nptf-thread",
             "supports": "PI450822S product identity, gray-acetal/nitrile construction and CO2 beverage gas service"},
        ],
    }
    for row in evidence["primary_sources"]:
        if "local" in row:
            row["sha256"] = sha(HERE / row["local"])
    (HERE / "source-evidence.json").write_text(json.dumps(evidence, indent=2) + "\n")
    print(json.dumps({"parts": len(records), "source_mesh_sha256": evidence["source_mesh_sha256"],
                      "cap_handoff": cap, "frames": frames}, indent=2))


if __name__ == "__main__":
    main()
