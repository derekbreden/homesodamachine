"""Freeze the archived comparator predictions against the registered pour schedules."""
import argparse
import hashlib
import json
from pathlib import Path

from comparators import forecast, specification


def freeze(preregistration):
    raw = preregistration.read_bytes()
    design = json.loads(raw)
    results = {}
    for name, scenario in design["scenarios"].items():
        widths = [gate[1] for gate in scenario["ideal_gates_start_ms_width_ms"]]
        heads = {head: forecast(head, widths) for head in ("A", "B")}
        for model in heads.values():
            rulers = model["restored_constant_rate"]
            model["restored_ruler_mean_ml"] = (rulers["right"]["dose_ml"] + rulers["projected_left"]["dose_ml"]) / 2
        results[name] = {
            "phase": scenario["phase"],
            "lever_open_s": sum(duration for pulses, duration in scenario["meter"] if pulses > 0) / 1000,
            "meter_trace_elapsed_s": sum(duration for _, duration in scenario["meter"]) / 1000,
            "water_equivalent_ml": scenario["nominal_water_ml"],
            "recipe_target_concentrate_ml": scenario["nominal_water_ml"] / scenario["ratio"],
            "heads": heads,
        }
    return {
        "preregistration_sha256": hashlib.sha256(raw).hexdigest(),
        "specification": specification(),
        "units": "Predicted nominal mL of undiluted concentrate on the open-hose bench. Water is an equivalent calculated from synthetic readings and the assumed meter factor. The bench dispenses concentrate only.",
        "schedules": results,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("preregistration", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    args.output.write_text(json.dumps(freeze(args.preregistration), indent=2, ensure_ascii=False, allow_nan=False) + "\n")
