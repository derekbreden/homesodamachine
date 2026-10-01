"""Refresh the full machine's bottom pieces and grip inserts from current CAD.

The enclosure producer owns the receiver cuts. This visual update carries its
current bottom solids and both source-built covers into the existing machine;
all other component solids and viewer surfaces are retained.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import sys

import cadquery as cq

ROOT = Path(__file__).resolve().parents[2]
ENC = ROOT / "hardware/printed-parts/enclosure/enclosure"
sys.path[:0] = [str(ENC), str(ROOT / "hardware/scripts")]
import enclosure as e
import _box_spec
import _mesh_payload
import flute_payload
from _cadq_export import export_assembly, import_assembly, import_step
from _materials import M_PETGF_BLACK
from materialize_pump_cartridge import _declared_box


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    box, _, _ = _declared_box(_box_spec, e)
    step = ROOT / "hardware/manifold-layout/enclosure-assembly.step"
    payload = step.with_suffix(".step.mesh")
    bodies = import_assembly(step)
    held = flute_payload.read_payload(payload)
    if held is None:
        raise ValueError("The full machine needs an existing readable viewer payload.")
    bottom_names = {f"enclosure-{side}-bottom" for side in ("front", "back")}
    if not bottom_names <= bodies.keys():
        raise ValueError("The full machine is missing a named bottom quadrant.")
    for name in bottom_names:
        bodies[name] = (import_step(ENC / f"{name}.step").val(), bodies[name][1])
    covers = e.grip_covers(box)
    for name, shape in covers.items():
        bodies[name] = (shape, M_PETGF_BLACK)
    assembly = cq.Assembly(name="enclosure-assembly")
    for name, (shape, color) in bodies.items():
        assembly.add(shape, name=name, color=color)
    previous_skip = os.environ.get("HSM_SKIP_MESH_PAYLOAD")
    os.environ["HSM_SKIP_MESH_PAYLOAD"] = "1"
    try:
        export_assembly(assembly, str(step))
    finally:
        if previous_skip is None:
            os.environ.pop("HSM_SKIP_MESH_PAYLOAD", None)
        else:
            os.environ["HSM_SKIP_MESH_PAYLOAD"] = previous_skip
    inserts = cq.Assembly(name="grip-inserts")
    for name, shape in covers.items():
        inserts.add(shape, name=name, color=M_PETGF_BLACK)
    entries = [entry for entry in held if entry["name"] not in covers]
    entries.extend(_mesh_payload.from_assembly(inserts))
    temporary = payload.with_name(payload.name + ".grips.tmp")
    _mesh_payload.write(entries, str(temporary), src=_mesh_payload.source_digest(step))
    surfaces = flute_payload.surfaces(flute_payload.ENCLOSURE_DIRS)
    count = flute_payload.graft(temporary, {n: surfaces[n] for n in bottom_names},
                                same_frame=True)
    if count != len(bottom_names):
        raise ValueError(f"Expected two bottom surfaces, got {count}.")
    refreshed = {entry["name"]: entry for entry in flute_payload.read_payload(temporary)}
    untouched = [entry for entry in held if entry["name"] not in bottom_names | covers.keys()]
    assert all(refreshed[entry["name"]] == entry for entry in untouched)
    assert set(covers) <= refreshed.keys()
    temporary.replace(payload)
    report = {
        "status": "pass",
        "covers": sorted(covers),
        "bottom_surfaces": sorted(bottom_names),
        "unchanged_viewer_surfaces": len(untouched),
        "source_sha256": {str(p.relative_to(ROOT)): sha(p) for p in (
            Path(__file__), ENC / "enclosure.py", ENC / "_grip_interface.py",
            ROOT / "hardware/manifold-layout/enclosure_assembly.py",
            *(ENC / f"{n}.step" for n in sorted(bottom_names)))},
        "artifacts_sha256": {str(p.relative_to(ROOT)): sha(p) for p in (step, payload)},
    }
    out = ENC.parent / "grip-cover/assembly-integration.json"
    out.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
