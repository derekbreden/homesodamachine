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
    cuts = {
        "FU_BLUE_CUT": f"{assembly.blue_cut_length:g} mm",
        "FU_FLAVOR_CUT": f"{assembly.flavor_cut_length:g} mm",
        "FU_CUT_DIFFERENCE": f"{assembly.flavor_cut_length - assembly.blue_cut_length:g} mm",
        "FU_TAIL_OFFSET": f"{assembly.tails_apart:.2f} mm",
        # A White faucet's flavor pair, white to its unions and black from them, and the 3/8"
        # soda faucet tube either finish cuts from its own stock.
        "FU_WHITE_A_CUT": f"{assembly.white_cut_length(+1):g} mm",
        "FU_WHITE_B_CUT": f"{assembly.white_cut_length(-1):g} mm",
        "FU_BLACK_A_CUT": f"{assembly.black_run_cut_length(+1):g} mm",
        "FU_BLACK_B_CUT": f"{assembly.black_run_cut_length(-1):g} mm",
        "FU_SODA_FAUCET_CUT": f"{assembly.soda_faucet_cut_length:g} mm",
    }
    # The foam's run on the blue tube, from below the lower union to the wall's bare stretch.
    foam = {
        "FU_FOAM_LENGTH": f"{assembly.foam_length:.0f} mm",
        "FU_FOAM_BARE_TOP": f"{assembly.foam_bare_at_westbrass:.0f}",
        "FU_FOAM_BARE_WALL": f"{assembly.foam_bare_at_wall:g}",
        "FU_BLUE_CUT": cuts["FU_BLUE_CUT"],
    }
    facts = {**cuts, **foam}
    return facts, {"fu-01-cut-lldpe-tubes": set(cuts),
                   "fu-03-insulate-and-sleeve": set(foam)}
