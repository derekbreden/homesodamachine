"""FU card dimensions from the faucet's modeled tube routes."""

from pathlib import Path
import sys


def faucet(_machine):
    root = Path(__file__).resolve().parents[3]
    sys.path.insert(0, str(root / "tools"))
    from docgen import load_module

    assembly = load_module(
        "_cards_faucet_assembly",
        root / "hardware/faucet-layout/faucet_assembly.py",
    )
    facts = {
        "FU_BLUE_CUT": f"{assembly.blue_cut_length:g} mm",
        "FU_FLAVOR_CUT": f"{assembly.flavor_cut_length:g} mm",
        "FU_CUT_DIFFERENCE": f"{assembly.flavor_cut_length - assembly.blue_cut_length:g} mm",
        "FU_TAIL_OFFSET": f"{assembly.tails_apart:.2f} mm",
    }
    return facts, {"fu-01-cut-lldpe-tubes": set(facts)}
