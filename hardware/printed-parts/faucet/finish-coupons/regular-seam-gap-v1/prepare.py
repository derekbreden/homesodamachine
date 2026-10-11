"""Prepare one ordinary-seam-gap comparison using petgf.3mf; no printer connection."""
import hashlib
import json
from pathlib import Path
import sys
import xml.etree.ElementTree as ET
import zipfile

HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p / "tools/bambu_print.py").exists())
FAUCET = ROOT / "hardware/printed-parts/faucet"
sys.path.insert(0, str(FAUCET))
import refresh_print_project as writer

PROFILE = ROOT / "hardware/printed-parts/petgf.3mf"
SWATCH = HERE.parent / "scarf-swatches-v1/faucet-neck-swatch.stl"
WORK = ROOT / ".cache/printer-control/faucet-regular-seam-gap-v1-20261011"
STEM = "2026-10-11-faucet-regular-seam-gap-v1-petgf-left04-z004-mark2"
# Letter, ordinary gap % of nozzle, row from front, column from left, offset.
VARIANTS = (
    ("A", 0, 1, 1, (-34, -39)),
    ("B", 20, 1, 2, (0, -39)),
    ("C", 10, 1, 3, (34, -39)),
    ("D", 25, 2, 1, (-34, 0)),
    ("E", 15, 2, 2, (0, 0)),
    ("F", 5, 2, 3, (34, 0)),
    ("G", 30, 3, 2, (0, 39)),
)
QUOTE = ('I would like you to focus on just the seam gap setting, with no scarf setting back to our petgf.3mf defaults, '
         'and have one control, and have variations in both directions, with whatever you can fit in about a 30 minute '
         'to 120 minute print (aiming for 60 minutes maybe, but it does not have to be precise) time.')


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save(path, value):
    path.write_text(json.dumps(value, indent=2) + "\n")


def main():
    HERE.mkdir(parents=True, exist_ok=True)
    WORK.mkdir(parents=True, exist_ok=True)
    for name in ("launch-plan.json", "launch.json"):
        if (HERE / name).exists():
            live = json.loads((HERE / name).read_text())
            if any(live.get(k) for k in ("import_attempted", "send_attempted", "accepted")):
                raise ValueError("Preserve any attempted or accepted archive")
    assert sha(SWATCH) == "bae74f64710d7ddee182f2888c4740baeee88e696b7ee58798e29c8098733adf"
    with zipfile.ZipFile(PROFILE) as z:
        default = json.loads(z.read(writer.SETTINGS_MEMBER))
        assert default["seam_gap"] == "15%"
        assert default["seam_slope_type"] == "none" and default["filament_scarf_seam_type"] == ["none"]
        assert default["layer_height"] == "0.24" and default["initial_layer_print_height"] == "0.2"
        assert default["enable_wrapping_detection"] == "0"
    project = HERE / (STEM + ".3mf")
    names = [f"{v[0]} seam gap {v[1]}%" + (" control" if v[0] == "E" else "") for v in VARIANTS]
    report = writer.refresh(PROFILE, project,
                            parts=tuple((name, SWATCH, 0.0) for name in names),
                            offsets=tuple(v[4] for v in VARIANTS), plate_border=80,
                            z_trim=.04, title="Regular seam gap only - PET-GF defaults - one 15% control")
    with zipfile.ZipFile(project) as z:
        members = {n: z.read(n) for n in z.namelist()}
    settings = json.loads(members[writer.SETTINGS_MEMBER])
    settings["filament_colour"] = ["#161616"]
    members[writer.SETTINGS_MEMBER] = (json.dumps(settings, indent=2) + "\n").encode()
    cfg = ET.fromstring(members["Metadata/model_settings.config"])
    specimens = []
    for part, (letter, gap, row, column, _) in zip(report["parts"], VARIANTS, strict=True):
        control = letter == "E"
        obj = cfg.find(f"object[@id='{part['object_id']}']")
        # The single control inherits the profile's 15%; only other gaps override it.
        overrides = {} if control else {"seam_gap": f"{gap}%"}
        for key, value in overrides.items():
            writer.metadata(obj, key, value)
        specimens.append(dict(id=letter, name=part["name"], control=control,
                              seam_gap_percent_of_nozzle=gap, nominal_path_gap_mm=.4*gap/100,
                              row_from_front=row, column_from_left=column,
                              identify_id=part["identify_id"], object_id=part["object_id"],
                              object_overrides=overrides, plate_bounds_mm=part["plate_bounds_mm"]))
    members["Metadata/model_settings.config"] = writer.xml(cfg)
    writer.archive_write(project, members)
    changes = {k: [default.get(k), settings.get(k)] for k in set(default) | set(settings)
               if default.get(k) != settings.get(k)}
    assert set(changes) <= {"machine_start_gcode", "printer_settings_id", "filament_colour"}
    report.update(project=str(project.relative_to(ROOT)), project_sha256=sha(project),
                  settings_sha256=hashlib.sha256(members[writer.SETTINGS_MEMBER]).hexdigest(),
                  native_settings_sha256=hashlib.sha256(members[writer.SETTINGS_MEMBER]).hexdigest(),
                  settings_changes=changes, printer="Mark2", connection_alias="Mark2",
                  requested_z_trim_mm=.04, active_nozzle=0,
                  source_stl=str(SWATCH.relative_to(ROOT)), source_stl_sha256=sha(SWATCH),
                  source_sha256={str(p.relative_to(ROOT)):sha(p) for p in (PROFILE, SWATCH, Path(writer.__file__), Path(__file__))},
                  geometry="Seven identical unscaled 18.2 mm sections of the actual faucet neck, retained in their cut production pose",
                  specimens=specimens, control_id="E", factor="ordinary seam_gap only",
                  profile_settings_inherited_except_printer_identity_trim_and_spool_colour=True,
                  scarf_enabled=False, added_scarf_overrides=False, added_fine_layer_bands=False,
                  seam_position=default["seam_position"], preparation_only=True,
                  launch_authorized=False, import_attempted=False, send_attempted=False,
                  submitted=False, accepted=False, start_now=False)
    save(HERE / "preparation.json", report)
    save(project.with_suffix(".print.json"), report)
    save(HERE / "study-plan.json", dict(
        schema=1, status="Ordinary seam-gap comparison; native review pending",
        authorization_quotes=[QUOTE,"Both beds are clear."], preparation_only=True,
        customer_outcome="Find a regular seam with less ridge or groove at PET-GF defaults",
        factor="ordinary Seam gap", control_id="E", control_percent=15,
        seam_gap_percent=[0,5,10,15,20,25,30], specimens=specimens,
        fixed_settings="Saved petgf.3mf defaults: aligned seam, scarf off, 0.20 mm first bed layer, 0.24 mm model layers, saved temperature/cooling/flow/retraction/support settings",
        comparison_allocation="Keep the single control and all variants on one machine/plate to hold nozzle, Z trim and thermal cycle in common. Mark2 has the longer known idle-and-PET-GF-loaded period.",
        time_goal_minutes=60, acceptable_native_time_minutes=[30,120],
        assessment="Keep the letter with each specimen. Compare the aligned seam under raking light and with a fingernail; record ridge, groove, exposed gap and adjacent damage. No winner is assumed.",
        physical_result_pending=True,
        transfer_limit="This short full-scale neck section and seven simultaneous specimens change layer return time and height relative to a complete curved faucet. A selected gap still needs complete-print confirmation.",
        launch_authorized=False, import_attempted=False, send_attempted=False, accepted=False,
        automatic_next_print=False, auto_resume_authorized=False, scheduled_monitor_requested=False))
    command = ["/Applications/BambuStudio.app/Contents/MacOS/BambuStudio", "--slice", "0", "--arrange", "0", "--orient", "0",
               "--outputdir", str(WORK), "--export-3mf", STEM + ".gcode.3mf", str(project)]
    save(WORK / "slice-command.json", dict(argv=command, printer_connection=False))
    save(HERE / "slice-command.json", dict(executable=command[0], arguments=["--slice","0","--arrange","0","--orient","0","--outputdir","<private output directory>","--export-3mf",STEM+".gcode.3mf",str(project.relative_to(ROOT))],printer_connection=False))
    print(json.dumps(dict(project=report["project"], specimen_count=len(specimens), only_process_factor="seam_gap", control="E 15%", scarf=False),indent=2))


if __name__ == "__main__":
    main()
