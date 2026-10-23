"""Prepare and slice the three tube bend holders on one Mark1 plate. Manual use; does not send.

    tools/cad-venv/bin/python future/tube-bend-holder-exploration/tube_bend_holder.py
    tools/cad-venv/bin/python future/tube-bend-holder-exploration/prints/2026-10-23-walls-234-petgf-left04-z018-mark1/prepare.py

The shared `petgf.3mf` supplies every setting but the ones below: solid like the tube-insertion
fixture (six walls, 100% zig-zag), so the wall thickness is the only thing that differs
between the three. Slices into an empty directory under `.cache/` and keeps the reviewed
archive and its readiness record here.
"""
import importlib.util
import json
import os
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
os.environ.setdefault("HSM_NO_BUILD_LOCK", "1")

_spec = importlib.util.spec_from_file_location(
    "tube_insertion_print", ROOT / "hardware/printed-parts/fixtures/tube-insertion/prepare_print.py")
fixture = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(fixture)
writer = fixture.writer

STEM = "2026-10-23-tube-bend-holders-w234-petgf-left04-z018-mark1"
SPEC = {
    "id": STEM,
    "printer": "Mark1 (H2C)",
    "material": "PET-GF",
    "z_trim_mm": 0.18,
    "nozzle_mapping": "Left hardened 0.4 mm; black PET-GF external spool 254",
}
PROFILE = ROOT / "hardware/printed-parts/petgf.3mf"
SOURCE = ROOT / "future/tube-bend-holder-exploration"
# One row across the middle of the left nozzle's plate, 2 mm wall on the left.
PARTS = (("2 mm wall", "holder-w2.stl", (-28.0, 0.0)),
         ("3 mm wall", "holder-w3.stl", (0.0, 0.0)),
         ("4 mm wall", "holder-w4.stl", (29.0, 0.0)))
REQUESTED = {
    "wall_loops": "6",
    "sparse_infill_density": "100%",
    "sparse_infill_pattern": "zig-zag",
    "initial_layer_print_height": "0.2",
    "layer_height": "0.24",
    "enable_support": "1",
    "support_type": "tree(auto)",
    "support_style": "default",
    "enable_prime_tower": "0",
    "print_settings_id": "0.24mm PET-GF solid - tube bend holders",
}


def main():
    with zipfile.ZipFile(PROFILE) as archive:
        members = {name: archive.read(name) for name in archive.namelist()}
    settings = json.loads(members[writer.SETTINGS_MEMBER])
    nozzle = float(settings["nozzle_diameter"][0])
    settings["print_compatible_printers"] = [
        f"Bambu Lab H2C {nozzle:g} Standard +{SPEC['z_trim_mm']:.2f} Z trim",
        f"Bambu Lab H2C {nozzle:g} nozzle"]
    settings["filament_colour"] = ["#000000"]
    changes = {}
    for key, value in REQUESTED.items():
        if settings.get(key) != value:
            changes[key] = {"from": settings.get(key), "to": value}
            settings[key] = value
    members[writer.SETTINGS_MEMBER] = (json.dumps(settings, indent=2) + "\n").encode()
    profile = ROOT / ".cache/tube-bend-holder-print" / f"{STEM}-settings.3mf"
    writer.archive_write(profile, members)

    project = HERE / f"{STEM}.3mf"
    report = writer.refresh(
        profile, project, parts=tuple((name, SOURCE / stl, 0.0) for name, stl, _ in PARTS),
        offsets=tuple(offset for *_, offset in PARTS),
        title="Tube bend holders 2/3/4 mm - black PET-GF - Mark1",
        z_trim=SPEC["z_trim_mm"], plate_border=20.0)
    report.update(status="offline project preparation; no printer submission",
                  printer_submission=False, intended_printer=SPEC["printer"],
                  material=SPEC["material"], nozzle_mapping=SPEC["nozzle_mapping"],
                  original_settings_source=str(PROFILE.relative_to(ROOT)),
                  original_settings_source_sha256=fixture.sha(PROFILE),
                  task_process_changes=changes,
                  print_pose="flat back of the D on the plate; channel's teardrop point up")
    project.with_suffix(".print.json").write_text(json.dumps(report, indent=2) + "\n")

    slices = ROOT / ".cache/tube-bend-holder-print/slices"
    slices.mkdir(parents=True, exist_ok=True)
    attempt = slices / f"{len(list(slices.iterdir())) + 1:02d}"
    record = fixture.slice_project(project, report, SPEC, attempt, ready_directory=HERE)
    print(json.dumps({key: record[key] for key in
                      ("archive", "layers", "estimated_seconds", "estimated_filament_g",
                       "support_generated", "features", "plate_trim_commands_mm",
                       "bead_margin_mm", "slicer_warning")}, indent=1))


if __name__ == "__main__":
    main()
