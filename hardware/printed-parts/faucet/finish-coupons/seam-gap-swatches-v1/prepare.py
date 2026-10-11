"""Prepare seam material-gap swatches from the frozen faucet neck section."""
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p / "tools/bambu_print.py").exists())
COARSE = HERE.parent / "coarse-start-v1/prepare.py"
spec = importlib.util.spec_from_file_location("coarse_coupon_prepare", COARSE)
builder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(builder)
SOURCE = HERE.parent / "scarf-swatches-v1"
WORK = ROOT / ".cache/printer-control/faucet-seam-gap-swatches-v1"
STEM = "2026-10-11-faucet-seam-gap-swatches-v1-petgf-left04-z004-mark2"
# Letter, regular/scarf, applicable gap as percent of the 0.4 mm nozzle, row, column.
VARIANTS = (
    ("A", "regular", 15, 1, 1), ("B", "scarf", 10, 1, 2),
    ("C", "regular", 5, 1, 3), ("D", "scarf", 25, 1, 4),
    ("E", "scarf", 0, 2, 1), ("F", "regular", 0, 2, 2),
    ("G", "scarf", 5, 2, 3), ("H", "scarf", 20, 2, 4),
    ("I", "scarf", 30, 3, 1), ("J", "scarf", 2.5, 3, 2),
    ("K", "regular", 10, 3, 3), ("L", "scarf", 15, 3, 4),
    ("M", "regular", 15, 4, 1), ("N", "scarf", 0, 4, 4),
)


def main():
    HERE.mkdir(parents=True, exist_ok=True)
    WORK.mkdir(parents=True, exist_ok=True)
    builder.guard(HERE)
    source = json.loads((SOURCE / "preparation.json").read_text())
    stl = SOURCE / "faucet-neck-swatch.stl"
    step = stl.with_suffix(".step")
    assert builder.sha(stl) == "bae74f64710d7ddee182f2888c4740baeee88e696b7ee58798e29c8098733adf"
    assert builder.sha(step) == "b00670bc0bab08d82a86c34755549eb3bf08dbe5beed5abc986cf04d3da96707"
    parent = ROOT / source["settings_source"]
    assert builder.sha(parent) == builder.PARENT_PROJECT_SHA
    definitions = []
    for letter, method, gap, row, column in VARIANTS:
        overrides = dict(wall_generator="classic", seam_position="back",
                         override_filament_scarf_seam_setting="1",
                         seam_slope_conditional="1", scarf_angle_threshold="155",
                         seam_slope_entire_loop="0", seam_slope_steps="10",
                         seam_slope_inner_walls="1", seam_slope_min_length="10",
                         seam_slope_start_height="10%",
                         seam_slope_type="external" if method == "scarf" else "none",
                         seam_gap=f"{gap:g}%" if method == "regular" else "15%",
                         seam_slope_gap=f"{gap:g}%" if method == "scarf" else "0%")
        definitions.append(dict(id=letter, name=f"{letter} {method} gap {gap:g}%", kind="scarf", source=stl,
                                offset=(-51 + 34 * (column - 1), -57.75 + 38.5 * (row - 1)),
                                fine_band=(4.04, 16.04), fine_height=.08, overrides=overrides,
                                row_from_front=row, column_from_left=column,
                                seam_method=method, tested_gap_percent_of_nozzle=gap,
                                tested_gap_mm=.4 * gap / 100,
                                regular_seam_control=method == "regular",
                                repeated_control=letter in ("A", "M", "E", "N"),
                                scarf_length_mm=10 if method == "scarf" else None,
                                scarf_start_height_percent=10 if method == "scarf" else None,
                                fine_start_height_mm=.008 if method == "scarf" else None))
    info = {key: source[key] for key in ("source_acceptance", "shipping_reference", "shipping_reference_sha256",
                                         "parent_pose", "section_cuts")}
    info.update(source_step=str(step.relative_to(ROOT)), source_step_sha256=builder.sha(step),
                source_stl=str(stl.relative_to(ROOT)), source_stl_sha256=builder.sha(stl),
                source_geometry_pointer_commit="5a9863696")
    prep = builder.make_project(HERE, STEM, parent, definitions, None, info, work_folder=WORK)
    builder.save(HERE / "study-plan.json", dict(
        schema=1, status="Prepared seam-gap screen; unprinted", preparation_only=True,
        launch_authorized=False, start_now=False, import_attempted=False, send_attempted=False, accepted=False,
        physical_basis="D has a groove; E/F have a ridge and look alike at both 0.08 and 0.24 mm. Direct operator report, not a measured profile.",
        customer_outcome="A flat seam without a ridge, groove, exposed gap or neighboring surface damage",
        factors=dict(regular_seam_gap_percent=[0, 5, 10, 15], scarf_slope_gap_percent=[0, 2.5, 5, 10, 15, 20, 25, 30]),
        fixed_scarf_settings=dict(length_mm=10, start_height_percent=10, steps=10,
                                 inner_walls=True, smart_application=True, angle_threshold_degrees=155),
        hypotheses=["Reducing the regular-seam interruption from 15% supplies more closure and may reduce D's groove.",
                    "Increasing the scarf slope gap from zero trims its overlap and may reduce E/F's ridge."],
        baseline_controls=dict(regular_15_percent=["A", "M"], scarf_zero_percent=["E", "N"]),
        selection_rule="Judge flatness under raking light and with a fingernail, separately on the 0.24 mm bands and 0.08 mm band. Prefer the smallest deviation from the current profile that removes the ridge/groove without opening a hole or roughening the adjacent wall.",
        global_settings="Exact shipping faucet profile; no overall flow, temperature, cooling, retraction or pressure-advance change",
        gap_units="Percent of the 0.4 mm nozzle diameter, not percent flow; these shorten local perimeter paths.",
        geometry="Frozen unscaled 18.2 mm neck swatch; no geometry change", specimens=prep["specimens"],
        project=prep["project"], project_sha256=prep["project_sha256"],
        transfer_limit="Short swatches and fourteen simultaneous objects change thermal and return-time conditions. Confirm a candidate in the complete faucet.",
        physical_result="Unprinted; flatness has not been established", automatic_next_print=False,
        auto_resume_authorized=False, scheduled_monitor_requested=False))
    print(json.dumps(dict(project=prep["project"], specimens=len(definitions), preparation_only=True)))


if __name__ == "__main__":
    main()
