#!/usr/bin/env python3
"""Attended-labor parsing, batching and document figures, supplied by Rust."""
import sys
from pathlib import Path
from _ledger_rust import call, main as _main

HERE = Path(__file__).resolve().parent
LABOR = HERE.parent / 'ledger/labor.md'
_CONSTANTS = call('labor.constants')
BATCH_SIZE = _CONSTANTS['batch_size']
LABOR_RATE = _CONSTANTS['labor_rate']
INCREMENTS = tuple(_CONSTANTS['increments'])
RUN_INCREMENTS = tuple(_CONSTANTS['run_increments'])

def hm(mins):
    return call('labor.hm', minutes=mins)

def short(mins):
    return call('labor.short', minutes=mins)

def figure(mins):
    return call('labor.figure', minutes=mins)

def usd(mins):
    return call('labor.usd', minutes=mins)

def minutes(cell):
    return call('labor.minutes', cell=cell)

def duration(text):
    return call('labor.duration', text=text)

def run_of(cell):
    return call('labor.run_of', cell=cell)

def per_machine(run, batch=BATCH_SIZE):
    return call('labor.per_machine', run=run, batch=batch)

def on_ladder(v, ladder):
    return call('labor.on_ladder', value=v, ladder=ladder)

def parse(lines):
    rows, offenders = call('labor.parse', lines=lines)
    return [tuple(row) for row in rows], offenders

def write_runs(lines, rows):
    return call('labor.write_runs', lines=lines, rows=rows)

def main():
    return _main('labor.main', labor=LABOR, check='--check' in sys.argv)

if __name__ == '__main__':
    sys.exit(main())
