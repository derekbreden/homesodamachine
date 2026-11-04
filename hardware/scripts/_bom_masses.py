#!/usr/bin/env python3
"""Print-model mappings and model-derived filament masses, supplied by Rust."""
import sys
from pathlib import Path
from _ledger_rust import call, main as _main

REPO = Path(__file__).resolve().parents[2]
BOM = REPO / 'hardware/ledger/bom.md'
PARTS_DIR = REPO / 'hardware/printed-parts'
_DEFINITIONS = call('printing.definitions')
MATERIALS = {k:tuple(v) for k,v in _DEFINITIONS['materials'].items()}
PROFILES = {k:tuple(v) for k,v in _DEFINITIONS['profiles'].items()}
GAP = _DEFINITIONS['gap']
PARTS = _DEFINITIONS['parts']
MODEL_OF = _DEFINITIONS['model_of']
GROUP_OF = [tuple(row) for row in _DEFINITIONS['group_of']]
PRINTED = '<!--@printed-->'
_SOLIDS = {}

def _drawn(path):
    return tuple(call('printing.drawn', path=path))

def measure(rel):
    return tuple(call('printing.measure', rel=rel, parts_dir=PARTS_DIR))

def laid_cm3(volume, area, group):
    return call('printing.laid', volume=volume, area=area, group=group)

def group_of(label):
    return call('printing.group_of', label=label)

def material_of(cell):
    return call('printing.material_of', cell=cell)

def mass_kg(label, material):
    return call('printing.mass_kg', label=label, material=material, parts_dir=PARTS_DIR)

def main():
    return _main('printing.mass_main', bom=BOM, parts_dir=PARTS_DIR, check='--check' in sys.argv)

if __name__ == '__main__':
    sys.exit(main())
