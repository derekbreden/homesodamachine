"""Bind completed native print reviews and factory cleanup routes to the files.

This marks a file set ready to print. It does not submit a print or qualify a
physical assembly, water seal or appliance.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import prepare_vent_prints as preparation


def read(path):
    return json.loads(path.read_text())


def geometry_approvals(project: Path, kind: str) -> dict:
    """Reject stale or incomplete whole-assembly evidence before finalization."""
    if kind not in ("rigid", "seals"):
        return {}
    required = [(HERE / "faucet-shell/centered-vent-check.json", 164,
                 ("geometry_source_sha256",))]
    if "industrial" in project.stem:
        required.extend([
            (HERE / "industrial/geometry-check.json", 26, ("sources_sha256",)),
            (HERE / "industrial/display-cover-check.json", 43,
             ("geometry_source_sha256", "saved_geometry_sha256", "reference_artifact_sha256")),
        ])
    approvals = {}
    for path, count, maps in required:
        evidence = read(path)
        assert evidence["passed"] is True, path
        assert len(evidence["checks"]) == count, path
        assert all(row["passed"] is True for row in evidence["checks"].values()), path
        for key in maps:
            bindings = evidence[key]
            assert bindings, (path, key)
            for name, expected in bindings.items():
                assert preparation.sha(preparation.ROOT / name) == expected, (path, name)
        if path.name == "centered-vent-check.json":
            assert len(evidence["geometry_source_sha256"]) == 22, path
            for name in ("stock:under-counter-profile", "motion:stock-under-counter-plate-slide",
                         "drain:clearance-union_a", "drain:clearance-union_b",
                         "clearance:flavor-pair"):
                assert evidence["checks"][name]["passed"] is True, (path, name)
        if path.name == "display-cover-check.json":
            assert evidence["validation_script_sha256"] == preparation.sha(HERE / "industrial/check_display_cover.py")
        approvals[preparation.relative(path)] = preparation.sha(path)
    return approvals


def finalize(project: Path, kind: str) -> dict:
    report = read(project.with_suffix(".print.json"))
    ready = read(project.with_suffix(".readiness.json"))
    approvals = geometry_approvals(project, kind)
    preparation.verify_sources(report)
    assert ready["source_sha256"] == report["source_sha256"]
    assert ready["project_sha256"] == report["project_sha256"] == preparation.sha(project)
    assert ready["settings_sha256"] == report["settings_sha256"]
    assert ready["print_report_sha256"] == preparation.sha(project.with_suffix(".print.json"))
    assert ready["support_audit_sha256"] == preparation.sha(project.with_suffix(".support-audit.json"))
    audit = read(project.with_suffix(".support-audit.json"))
    assert audit["project_sha256"] == ready["project_sha256"]
    assert audit["settings_sha256"] == ready["settings_sha256"]
    assert audit["fit"] == ready["fit"]
    assert read(project.with_suffix(".native-validation.json")) == ready["native"]
    native = preparation.ROOT / ready["native"]["archive"]
    assert ready["native"]["archive_sha256"] == preparation.sha(native)
    assert ready["native"]["gcode_sha256"] == preparation.sha(native.parent / "plate_1.gcode")
    reviews = {}

    binding = report.get("source_binding_evidence")
    if binding:
        evidence_path = preparation.ROOT / binding["path"]
        assert preparation.sha(evidence_path) == binding["sha256"]
        evidence = read(evidence_path)
        assert evidence["passed"] is True
        assert evidence["sources_unchanged_during_check"] is True
        assert ready["source_binding_evidence"] == binding
        for key in ("current_source_sha256", "exact_retained_step_stl_sha256"):
            for name, expected in evidence[key].items():
                assert preparation.sha(preparation.ROOT / name) == expected, name
        checker = preparation.ROOT / evidence["checker"]
        assert preparation.sha(checker) == evidence["checker_sha256"]
        free_binding = evidence["free_seal_geometry_proof"]
        free_path = preparation.ROOT / free_binding["path"]
        assert preparation.sha(free_path) == free_binding["sha256"]
        assert read(free_path)["passed"] is True
        project_name = preparation.relative(project)
        provenance = evidence["native_execution_provenance"][project_name]
        original_sources = provenance["original_native_execution_source_sha256"]
        assert report["native_execution_source_sha256"] == original_sources
        assert ready["native_execution_source_sha256"] == original_sources
        retained = next(row for row in evidence["retained_native_plates"]
                        if row["project"] == project_name)
        assert retained["exact_native_tuple_and_pose_unchanged"] is True
        assert retained["project_sha256"] == ready["project_sha256"]
        assert retained["settings_sha256"] == ready["settings_sha256"]
        assert retained["native_archive"] == ready["native"]["archive"]
        assert retained["native_archive_sha256"] == ready["native"]["archive_sha256"]
        assert retained["gcode_sha256"] == ready["native"]["gcode_sha256"]
        assert provenance["parts_and_print_pose"] == report["parts"]
        for path in (evidence_path, checker, free_path):
            reviews[preparation.relative(path)] = preparation.sha(path)

    def review(suffix, check_pass=False):
        path = project.with_suffix(suffix)
        evidence = read(path)
        assert evidence["gcode_sha256"] == ready["native"]["gcode_sha256"]
        assert evidence["native_archive_sha256"] == ready["native"]["archive_sha256"]
        if evidence.get("source_sha256"):
            assert evidence["source_sha256"] == report["source_sha256"]
        if evidence.get("project_sha256"):
            assert evidence["project_sha256"] == ready["project_sha256"]
        if evidence.get("print_report_sha256"):
            assert evidence["print_report_sha256"] == ready["print_report_sha256"]
        if check_pass:
            assert evidence["pass"], path
        script = HERE / ({".insert-beads.json": "review_faucet_inserts.py",
                          ".gasket-beads.json": "review_gasket_beads.py",
                          ".lower-supports.json": "review_lower_supports.py"}.get(suffix, "review_vent_prints.py"))
        assert evidence["analysis_script_sha256"] == preparation.sha(script)
        if evidence.get("section_reader_sha256"):
            assert evidence["section_reader_sha256"] == preparation.sha(HERE / "review_vent_prints.py")
        if evidence.get("gcode_reader_sha256"):
            assert evidence["gcode_reader_sha256"] == preparation.sha(HERE / "prepare_display_print.py")
        reviews[preparation.relative(path)] = preparation.sha(path)
        return evidence

    if kind == "rigid":
        review(".insert-beads.json", True)
        review(".support-faces.json")
        lower = review(".lower-supports.json")
        assert lower.get("geometry_access_review", {}).get("lower_relief_open_to_main_donor_flavor_passage")
        cleanup = [
            "Base: cut sacrificial trees into short pieces and withdraw through the counter-end, donor bay and lever opening. Clear all three insert pilots and pedestal sockets before installing brass.",
            "Lower cable route: remove supports through the common rear tube opening and open counter end. The flat ribbon must pass freely behind the flavor/drain bundle before the mounting stack closes.",
            "Tip: release the connected tree through the open neck joint, the 12 by 22 mm bottom discharge port and the open display pocket. Remove cavity fragments before either bung is installed. Clear both gland lips, body seats and flange grooves; preserve their modeled edge and radius.",
            "Continue through the dry S/F/ribbon guides from the joint and beverage/display ends. The source removes inaccessible interstice needles. Pass each actual tube freely before installing the bungs.",
            "Cover: remove supports through the open underside before the display is fitted; retain the bezel, broad snap wings and their lip-bearing faces.",
            "Counter plate: remove the three counterbore support bodies through their respective screw-head openings; retain every screw seat and locating pedestal.",
            "Brush and rinse away loose fragments. Visually inspect gland seats through the open joint and bottom port; no support stock may remain in a tube guide, seal groove or drain opening.",
        ]
        scope = "Native meshes, process, placement, nominal insert-host deposition and geometrically accessible support cleanup. Actual support release, surface finish, insert retention and assembled lifetime remain physical acceptance items."
    elif kind == "seals":
        review(".bead-review.json", True)
        review(".gasket-beads.json", True)
        cleanup = [
            "Bungs and counter gasket print flat without supports. Remove the parts without tearing the thin webs or perimeter flange.",
            "Inspect all four individual wire bores and S/F/D tube bores; preserve the interference surfaces and flange. Do not drill or enlarge these openings.",
            "Use the factory sequence in asse-vent-seals/README.md: separate the ribbon conductors locally, install the downstream bung first, and wet the bores with clean water for tube threading.",
        ]
        scope = "Every native bung layer has closed separate bore contours, open wire apertures and connected local material webs. Each countertop-gasket layer retains enclosed functional openings and a connected broad pad. Enclosed inter-road pores remain recorded. Deposited bore sizes, compression, assembly force and liquid sealing are unmeasured."
    else:
        tool = review(".tool-review.json")
        bearing_path = preparation.SEALS / "tool-bearing-check.json"
        motion_path = preparation.SEALS / "tool-motion-check.json"
        bearing, motion = read(bearing_path), read(motion_path)
        assert bearing["tool_stl_sha256"] == report["parts"][0]["stl_sha256"]
        assert bearing["generator_sha256"] == preparation.sha(HERE / "vent_seals.py")
        assert bearing["native_last_model_layer_z_mm"] == tool["highest_native_model_layer_mm"]
        assert bearing["native_tool_review_sha256"] == preparation.sha(project.with_suffix(".tool-review.json"))
        assert bearing["native_archive_sha256"] == ready["native"]["archive_sha256"]
        assert bearing["gcode_sha256"] == ready["native"]["gcode_sha256"]
        assert bearing["tool_step_sha256"] == preparation.sha(preparation.SEALS / "asse-vent-perimeter-tool.step")
        assert motion["source_sha256"]["tool_generator"] == preparation.sha(HERE / "vent_seals.py")
        assert motion["source_sha256"]["paths"] == preparation.sha(HERE / "faucet_paths.py")
        # A complete fresh pose/casing check binds all current inputs directly.
        # A bounded refresh carries its independent current bindings alongside
        # the original sampled-pose execution and geometry-equivalence proof.
        refreshed = "continuous_bound_source_sha256" in motion
        current = motion["continuous_bound_source_sha256"] if refreshed else motion["source_sha256"]
        assert current["shell"] == preparation.sha(HERE / "faucet-shell/faucet_shell.py")
        assert current["tool_generator"] == preparation.sha(HERE / "vent_seals.py")
        assert current["paths"] == preparation.sha(HERE / "faucet_paths.py")
        assert current["checker"] == preparation.sha(HERE / "asse-vent-seals/check_tool_motion.py")
        assert current["assembly"] == preparation.sha(preparation.ROOT / "hardware/faucet-layout/faucet_assembly.py")
        assert current["interface"] == preparation.sha(HERE / "_faucet_interface.py")
        assert current["plate"] == preparation.sha(HERE / "above-counter-plate/above_counter_plate.py")
        assert current["gasket"] == preparation.sha(HERE / "above-counter-gasket/above_counter_gasket.py")
        assert motion["passed"]
        if refreshed:
            assert motion["native_pose_paths_and_tool_match_current_sources"]
            assert motion["continuous_bound_dependencies_unchanged_during_check"]
        else:
            assert motion["source_unchanged_during_check"]
        lower = motion["current_lower_ribbon_continuous_motion_witness"]
        assert lower["source_sha256"] == current
        assert lower["dependencies_unchanged_during_check"]
        assert lower["passed"]
        assert all(row["casing_overlap_mm3"] == 0 for row in motion["continuous_bounds"])
        assert all(row["casing_overlap_mm3"] == 0 and all(value == 0 for value in row["tube_overlap_mm3"].values())
                   for row in motion["native_poses"])
        for path in (bearing_path, motion_path):
            reviews[preparation.relative(path)] = preparation.sha(path)
        cleanup = [tool["cleanup_route"],
                   "Inspect the curved outer sleeve and main annular bearing. They must have no support remnants, raised strings or sharp burrs before entering the seal glands."]
        scope = "Native toolpaths and accessible supports, exact retained bearing area, and CAD assembly motion clearances. Deposited fit, sleeve stiffness and insertion force are unmeasured."
    minimum_margin = 20 if kind == "rigid" else 80
    assert ready["fit"]["complete_layer_bead_minimum_bed_margin_mm"] >= minimum_margin
    ready.update(status="ready to print; native geometry and support access reviewed",
                 review_sha256=reviews, cleanup_route=cleanup, review_scope=scope,
                 finalization_script_sha256=preparation.sha(Path(__file__)),
                 submitted=False, physical_print_evaluated=False,
                 consumer_assembly_qualified=False)
    if approvals:
        assert geometry_approvals(project, kind) == approvals
        ready.update(geometry_review_pending=False, geometry_approval_sha256=approvals)
    preparation.save(project.with_suffix(".readiness.json"), ready)
    print(f"Ready to print: {preparation.relative(project)}")
    return ready


def write_manifest(actions: dict) -> None:
    """Index the complete finalized plate set, including its native estimates."""
    sources, approvals, parts, plates = {}, {}, {}, []

    def merge(destination, bindings):
        for name, expected in bindings.items():
            assert name not in destination or destination[name] == expected, name
            destination[name] = expected

    for name, (project, kind) in actions.items():
        report = read(project.with_suffix(".print.json"))
        ready_path = project.with_suffix(".readiness.json")
        ready = read(ready_path)
        assert ready["finalization_script_sha256"] == preparation.sha(Path(__file__))
        merge(sources, ready["source_sha256"])
        merge(approvals, ready.get("geometry_approval_sha256", {}))
        for part in report["parts"]:
            merge(parts, {part["source"]: part["stl_sha256"]})
        plates.append({
            "name": name, "kind": kind,
            "printer": report["printer"], "filament": report["filament"],
            "active_hotend": "left" if ready["native"]["active_nozzle"] == 0 else "right",
            "nozzle_diameter_mm": ready["native"]["nozzle_diameter_mm"],
            "project": preparation.relative(project), "project_sha256": ready["project_sha256"],
            "settings_sha256": ready["settings_sha256"],
            "print_report": preparation.relative(project.with_suffix(".print.json")),
            "print_report_sha256": ready["print_report_sha256"],
            "readiness_record": preparation.relative(ready_path), "readiness_sha256": preparation.sha(ready_path),
            "native_validation_record": preparation.relative(project.with_suffix(".native-validation.json")),
            "native_validation_sha256": preparation.sha(project.with_suffix(".native-validation.json")),
            "support_audit": preparation.relative(project.with_suffix(".support-audit.json")),
            "support_audit_sha256": ready["support_audit_sha256"],
            "native_archive": ready["native"]["archive"],
            "native_archive_sha256": ready["native"]["archive_sha256"],
            "gcode_sha256": ready["native"]["gcode_sha256"],
            "native_layers": ready["native"]["layers"],
            "native_estimated_seconds": ready["native"]["estimated_seconds"],
            "saved_profile_density_mass_estimate_g": ready["native"]["estimated_grams_saved_profile_density"],
            "complete_emitted_bead_minimum_bed_margin_mm": ready["fit"]["complete_layer_bead_minimum_bed_margin_mm"],
            "review_sha256": ready["review_sha256"],
            "geometry_approval_sha256": ready.get("geometry_approval_sha256", {}),
        })
    for name, expected in {**sources, **approvals, **parts}.items():
        assert preparation.sha(preparation.ROOT / name) == expected, name
    scripts = {preparation.relative(HERE / name): preparation.sha(HERE / name)
               for name in ("prepare_vent_prints.py", "finalize_vent_prints.py", "review_vent_prints.py",
                            "review_faucet_inserts.py", "review_gasket_beads.py", "review_lower_supports.py",
                            "prepare_display_print.py", "refresh_print_project.py")}
    preparation.save(preparation.REVIEW / "manifest.json", {
        "schema_version": 1,
        "status": "ready to print; all five native plate records finalized",
        "scope": "Current geometry approval, source meshes, editable projects, native G-code archives, commanded bead reviews and geometric support cleanup access. Estimates use the saved profile density. Physical fit, support release, seal containment, insert retention and appliance qualification are not established by these files.",
        "geometry_approval_sha256": approvals, "source_sha256": sources,
        "production_stl_sha256": parts, "scripts_sha256": scripts, "plates": plates,
        "submitted": False, "physical_print_evaluated": False, "consumer_assembly_qualified": False,
    })
    print(f"Plate manifest: {preparation.relative(preparation.REVIEW / 'manifest.json')}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("jobs", nargs="*", choices=("rigid", "seals", "tool", "industrial", "seals-industrial"))
    args = parser.parse_args()
    actions = {"rigid": (HERE / "faucet-petgf.3mf", "rigid"),
               "industrial": (HERE / "industrial/faucet-industrial-petgf.3mf", "rigid"),
               "seals": (preparation.SEALS / "vent-bungs-tpu85a.3mf", "seals"),
               "seals-industrial": (preparation.SEALS / "vent-bungs-industrial-tpu85a.3mf", "seals"),
               "tool": (preparation.SEALS / "vent-seal-tool-petgf.3mf", "tool")}
    jobs = args.jobs or list(actions)
    for name in jobs:
        finalize(*actions[name])
    if set(jobs) == set(actions):
        write_manifest(actions)
