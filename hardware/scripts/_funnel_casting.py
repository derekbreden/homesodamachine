"""Rust reader for the funnel CAD volume and silicone allocation."""
from pathlib import Path
from _ledger_rust import call

DESIGN = Path(__file__).resolve().parents[1] / 'printed-parts/zone-c/funnel-mold/design.json'
DENSITY_G_ML = 1.13
MIX_ALLOWANCE = 0.10

def casting_estimate():
    return call('labor.casting_estimate', design=DESIGN, density=DENSITY_G_ML, allowance=MIX_ALLOWANCE)

def figures():
    return call('labor.casting_figures', design=DESIGN, density=DENSITY_G_ML, allowance=MIX_ALLOWANCE)
