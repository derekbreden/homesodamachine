#!/usr/bin/env python3
"""Export fixed, insulating controller mounting parts; dimensions are mm.

Run with tools/cad-venv/bin/python hardware/gun-positioner/mounting/generate.py.
The received boards, fan and fixed frame establish the transfer-drilled holes.
No powered hardware or printer is accessed by this generator.
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
from pathlib import Path

import cadquery as cq
import trimesh

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
os.environ.setdefault("HSM_NO_BUILD_LOCK", "1")
sys.path.insert(0, str(ROOT / "hardware/scripts"))
from _cadq_export import export_step

PROFILE = ROOT / (
    "hardware/printed-parts/enclosure/tee-readiness/full-enclosure-print/"
    "native-slice-reviews/2026-09-29-nameplate-all-ink-raised-mark2-v4/"
    "effective-settings.json"
)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def make_parts():
    panel = cq.Workplane("XY").box(300, 300, 6, centered=(True, True, False))
    panel = panel.edges("|Z").fillet(3)
    spacer = cq.Workplane("XY").circle(4).circle(1.7).extrude(6)
    # Installed fan stand: rear face Y=0, base on Z=0, hole axis parallel Y.
    base = cq.Workplane("XY").box(90, 35, 4, centered=(True, False, False))
    wall = cq.Workplane("XY").box(90, 4, 90, centered=(True, False, False))
    opening = cq.Workplane("XZ", origin=(0, 5, 45)).circle(38).extrude(6)
    anchor_holes = (cq.Workplane("XY", origin=(0, 0, -1))
                    .pushPoints([(-32, 20), (32, 20)]).circle(1.7).extrude(6))
    stand = base.union(wall).cut(opening).cut(anchor_holes)
    # Rear face on bed: vertical fan opening becomes a vertical printed bore.
    print_stand = stand.rotate((0, 0, 0), (1, 0, 0), 90)
    return {
        "controller-backplane": (panel, panel, 1),
        "m3-insulating-spacer-6mm": (spacer, spacer, 28),
        "fan-stand-80mm": (stand, print_stand, 1),
    }


def main():
    profile = json.loads(PROFILE.read_text())
    if profile["printer_model"] != "Bambu Lab H2C":
        raise RuntimeError("The bound bed profile is not H2C")
    if profile["printable_area"] != ["0x0", "330x0", "330x320", "0x320"]:
        raise RuntimeError("Reassess the changed H2C bed envelope")
    records = []
    for name, (installed, printable, quantity) in make_parts().items():
        if len(installed.solids().vals()) != 1 or not installed.val().isValid():
            raise RuntimeError(f"Invalid solid: {name}")
        step, stl = OUT / f"{name}.step", OUT / f"{name}.stl"
        export_step(installed, step)
        cq.exporters.export(printable, str(stl), tolerance=0.03, angularTolerance=0.1)
        mesh = trimesh.load_mesh(stl)
        bounds = mesh.extents.tolist()
        if not mesh.is_watertight or not mesh.is_volume:
            raise RuntimeError(f"Invalid printable mesh: {name}")
        if mesh.bounds[0, 2] < -0.001:
            raise RuntimeError(f"Print orientation extends below bed: {name}")
        # Five-mm brim all round fits the conservative left-nozzle envelope.
        if bounds[0] + 10 > 325 or bounds[1] + 10 > 320:
            raise RuntimeError(f"Print exceeds conservative H2C bed: {name}")
        payload = OUT / f"{name}.step.mesh"
        if not payload.exists():
            raise RuntimeError(f"Missing viewer payload: {name}")
        records.append({
            "id": name, "quantity": quantity,
            "step": step.name, "stl": stl.name, "viewer_payload": payload.name,
            "print_bounds_mm": bounds,
            "cad_volume_mm3": installed.val().Volume(),
            "valid_one_solid": True, "stl_watertight": True,
            "stl_positive_volume": True,
            "print_orientation": ("Rear fan-wall face on bed; supplied STL already rotated"
                                  if name == "fan-stand-80mm" else
                                  "Broad flat face on bed" if name == "controller-backplane" else
                                  "Annular end on bed; bore vertical"),
            "support": "None for this supplied orientation; inspect its own slice",
        })
    mounting = {
        "M3x25": {"bolts": 36, "locking_nuts": 36, "flat_washers": 72,
                   "allocation": {"six_carriers_four_each": 24, "Pico_adapter": 4,
                                  "DIN_rail": 2, "fuse_block": 4, "fan_stand_base": 2}},
        "M4x50": {"bolts": 4, "locking_nuts": 4, "flat_washers": 8,
                   "allocation": {"fan_frame_and_two_guards": 4}},
        "M6x16": {"bolts": 4, "slot8_T_nuts": 4, "flat_washers": 4,
                   "allocation": {"fixed_backplane_to_4040": 4}},
    }
    manifest = {
        "schema": 1,
        "scope": "Fixed controller mounting only; no gravity, gun or motor reaction load. CAD/mesh checks are not physical fit, temperature, creep or print qualification.",
        "parts": records, "mounting_hardware": mounting,
        "spacer_use": "Four 6 mm insulating spacers per carrier plus four under the Pico adapter;28 total. The 6 mm dimension is the PCB-to-panel standoff. Every actual solder pin/joint must remain visibly clear of the panel and all mounting metal. Trim only excess leads with USB and24 V unplugged, then inspect and verify continuity/isolation before power.",
        "fan": {"frame_mm": 80, "opening_mm": 76, "guards": 2,
                "holes": "Transfer actual four fan holes after centering its opening; drill4.5mm only where the measured fan pattern leaves sound wall outside the76mm opening. Do not drill the fan.",
                "base_holes_mm": [[-32, 20], [32, 20]],
                "fastener_stack": "Two guards +25mm fan frame +4mm stand +two flat washers +M4 locknut; check received thickness and two full0.7mm threads beyond nut. Keep protrusions away from wires."},
        "backplane": {"size_mm": [300, 300, 6], "holes": "Transfer-drill after actual board/socket/terminal layout and fixed frame clearance check; component M3holes3.4mm, four frame M6holes6.5mm. Keep>=12mm panel edge distance for the frame holes.",
                      "component_stack": "PCB~1.6 +spacer6 +panel6 +twoM3 washers~1 +M3 nut~4 =18.6mm;M3x25 leaves6.4mm nominal protrusion. Measure actual stacks and keep two full threads beyond every locknut.",
                      "layout": "Start with two carrier columns of three, one UART group per column. Keep the fuse block, Pico and DIN rail beside them. Transfer actual component footprints; no printed hole pattern overrides received parts.",
                      "DIN": "Use the203.2mm rail in the sourced terminal kit for the clipped buck/relay and selected terminal blocks. Seat at most nine blocks in the initial layout; confirm actual component/rail clearances before drilling. VM feeds and motor returns land at the fuse/negative bus and carrier terminals; do not require twenty rail blocks."},
        "print_recipe": {"printer": "H2C", "material": "Owned SunTop unfilled clear PETG B0FP34MJ94 (2kg reservoir-candidate stock ininventory.md); use its matching filament preset and drying procedure",
                         "nozzle_mm": 0.4, "layer_mm": 0.24,
                         "first_layer_mm": 0.20, "walls": 4,
                         "top_bottom_layers": 6, "panel_and_stand_infill": "40% gyroid",
                         "spacer_infill": "Solid", "brim_mm": 5,
                         "supports": "None in supplied orientations; no transfer of another part's support settings",
                         "scope": "Offline preparation only; no G-code or printer launch. Confirm flat panel, clean spacer bores, received fit and50C upper-bound thermal gate before use."},
        "H2C_bed": {"bound_profile": str(PROFILE.relative_to(ROOT)),
                    "recorded_area_mm": [330, 320],
                    "conservative_left_nozzle_envelope_mm": [325, 320],
                    "conservative_source": "hardware/printed-parts/fixtures/weld-rotator/weld_rotator.py",
                    "panel_with_brim_mm": [310, 310], "fits_conservative_envelope": True},
    }
    (OUT / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    sources = [Path(__file__), ROOT / "hardware/scripts/_cadq_export.py",
               ROOT / "hardware/scripts/_mesh_payload.py", PROFILE,
               ROOT / "hardware/printed-parts/fixtures/weld-rotator/weld_rotator.py",
               OUT / "README.md"]
    outputs = [p for p in OUT.iterdir() if p.suffix in (".step", ".stl", ".mesh")]
    outputs.append(OUT / "manifest.json")
    receipt = {"schema": 1, "generator_command": "tools/cad-venv/bin/python hardware/gun-positioner/mounting/generate.py",
               "scope": "Binds CAD/export geometry and current assembly instructions. CAD/mesh checks do not establish physical fit, print, insulation, temperature or creep acceptance.",
               "cadquery_version": cq.__version__, "trimesh_version": trimesh.__version__,
               "source_sha256": {str(p.relative_to(ROOT)): digest(p) for p in sources},
               "output_sha256": {p.name: digest(p) for p in sorted(outputs)}}
    (OUT / "source-receipt.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps({"parts": len(records), "valid_meshes": True,
                      "panel_with_5mm_brim_fits_H2C_left_envelope": True}))


if __name__ == "__main__":
    main()
