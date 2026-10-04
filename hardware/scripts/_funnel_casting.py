"""Silicone allocation from the current funnel's committed CAD volume.

Density and the mixing/port allowance are estimates. The geometry supplies the
finished casting volume; it does not measure batch losses or silicone density.
This reader is shared by the BOM and attended-labor ledgers and writes nothing.
"""
import json
from pathlib import Path

DESIGN = (Path(__file__).resolve().parents[1] / "printed-parts" / "zone-c" /
          "funnel-mold" / "design.json")
DENSITY_G_ML = 1.13
MIX_ALLOWANCE = 0.10


def casting_estimate():
    volume = json.loads(DESIGN.read_text(encoding="utf-8"))["volume_ml"]["funnel"]
    if volume <= 0:
        raise ValueError("Funnel CAD volume must be positive")
    finished = volume * DENSITY_G_ML
    return {"volume_ml": volume, "density_g_ml": DENSITY_G_ML,
            "finished_g": finished, "mix_allowance": MIX_ALLOWANCE,
            "mixed_g": finished * (1 + MIX_ALLOWANCE)}


def figures():
    estimate = casting_estimate()
    return {"FUNNEL_VOLUME_ML": f"{estimate['volume_ml']:.1f}",
            "FUNNEL_DENSITY_G_ML": f"{estimate['density_g_ml']:.2f}",
            "FUNNEL_FINISHED_G": f"{estimate['finished_g']:.0f}",
            "FUNNEL_MIX_ALLOWANCE": f"{estimate['mix_allowance']:.0%}",
            "FUNNEL_MIXED_G": f"{estimate['mixed_g']:.0f}"}
