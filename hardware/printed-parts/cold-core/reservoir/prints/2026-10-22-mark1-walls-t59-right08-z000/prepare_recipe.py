"""Add Arachne center-wall transitions at the reservoir's floor junctions."""

from pathlib import Path
import json

HERE = Path(__file__).resolve().parent
PART = HERE.parents[1]


def main():
    recipe = json.loads((HERE / "baseline-settings.json").read_text())
    settings = recipe["project_settings"]
    before = settings["wall_transition_angle"]
    assert before == "10"
    settings["wall_transition_angle"] = "59"
    recipe["process_changes"]["wall_transition_angle"] = {"from": "10", "to": "59"}
    recipe["accepted_result_scope"] = (
        "Historical May water hold belongs to its identified article. "
        "The current 59-degree Arachne walls-only adaptation awaits its own physical result. "
        "Mark1 task 1362982574 has reported seam leakage; see its physical-result record."
    )
    (PART / "print-settings.json").write_text(json.dumps(recipe, indent=2) + "\n")
    adaptation = {
        "recorded_on_central": "2026-10-22",
        "baseline": "baseline-settings.json",
        "baseline_print": "../2026-10-21-mark1-walls-only-right08-z000-a4/README.md",
        "setting_changes": {"wall_transition_angle": {"from": before, "to": "59"}},
        "retained": (
            "999 requested walls; zero sparse/top/bottom fill; flow 1.02; 255/260 C; "
            "21 mm3/s; 70 C bed; 0.30/0.24 mm layers; nominal 0.8 mm lines; "
            "Arachne; inner then outer; random conditional scarf with 15% seam gap; "
            "May cooling and speeds; right 0.8 mm Standard; zero added user Z trim; "
            "stock Textured PEI -0.02 mm; no brim or ironing; unchanged geometry, "
            "placement and Tree(auto)/Default bed-only supports."
        ),
        "reason": (
            "Derek reports seam leakage on the walls-only article. Native comparisons "
            "show 59 degrees adds center-wall paths at the floor perimeter-convergence "
            "junctions and reduces nominal layer-12 XY pockets by about 72%. "
            "Residual modeled pockets remain; the new printed article supplies the sealing result."
        ),
        "comparison": "../2026-10-21-mark1-walls-only-right08-z000-a4/physical-result/seam-comparison.json",
        "start_slot": "A1",
        "preferred_consumption_order": ["A1", "A3"],
        "order_basis": "Fresh telemetry: A1 6%, A3 100%; A2 and A4 empty. Use each matching spool fully, with automatic refill.",
        "founder_quotes": [
            "Leaks along the seam",
            "Proceed with a print you think will work. Bed is clear.",
            "Do you understand what I meant about the spool order? That we want to use up the spools that are most empty first ..."
        ],
    }
    (HERE / "adaptation.json").write_text(json.dumps(adaptation, indent=2) + "\n")
    print("Arachne transition angle 59 degrees; all other physical settings retained.")


if __name__ == "__main__":
    main()
