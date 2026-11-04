#!/usr/bin/env python3
"""Native-slice print estimates and machine occupancy figures, supplied by Rust."""
import sys
from pathlib import Path
from _ledger_rust import call, main as _main
from _bom_masses import GROUP_OF, MATERIALS

HERE = Path(__file__).resolve().parent
BOM = HERE.parent / 'ledger/bom.md'
MT = HERE.parent / 'ledger/machine-time.md'
FAUCET_SLICE = HERE.parent / 'printed-parts/faucet/faucet-petgf.support-audit.json'
FLOAT_SLICE = HERE.parent / 'printed-parts/cold-core/magnetic-float/all-aero/mark2-print/v1/float-preflight.json'
_CONSTANTS = call('printing.constants')
PRINTERS = _CONSTANTS['printers']
DUTY = _CONSTANTS['duty']
HOURS_PER_YEAR = _CONSTANTS['hours_per_year']
MEASURED = tuple(_CONSTANTS['measured'])
MEASURED_EXT = tuple(_CONSTANTS['measured_ext'])
PETGF_CARRY = _CONSTANTS['petgf_carry']
_BULK_PETG = _CONSTANTS['bulk_petg']
RATES = _CONSTANTS['rates']
GROUP_MARKER = _CONSTANTS['group_marker']
PRINT_WALL_MARK = '(MT_H_PRINT_WALL)'

def _paths():
    return dict(bom=BOM, machine_time=MT, faucet_slice=FAUCET_SLICE, float_slice=FLOAT_SLICE)

def is_data_row(c):
    return call('printing.is_data_row', cells=c)

def number(cell):
    return call('printing.number', cell=cell)

def printed_parts():
    return [tuple(row) for row in call('printing.printed_parts', **_paths())]

def group_masses():
    return tuple(call('printing.group_masses', **_paths()))

def print_estimate():
    return call('printing.estimate', **_paths())

def read_sections():
    sums, rows = call('printing.read_sections', **_paths())
    return {int(k):v for k,v in sums.items()}, [tuple(row) for row in rows]

def read_turnaround(wall):
    return call('printing.turnaround', wall=wall, **_paths())

def main():
    return _main('printing.main', check='--check' in sys.argv, **_paths())

if __name__ == '__main__':
    sys.exit(main())
