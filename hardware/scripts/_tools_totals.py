#!/usr/bin/env python3
"""Tool-purchase resolution and document totals, supplied by Rust."""
import sys
from pathlib import Path
from _ledger_rust import call, main as _main

HERE = Path(__file__).resolve().parent
PUR = HERE.parent / 'ledger/purchases.md'
TOOLS_MD = HERE.parent / 'ledger/tools.md'

class _Resolver:
    def __init__(self, specification):
        self.specification = specification
    def __call__(self):
        return call('tools.resolve', resolver=self.specification, rows=ROWS)

def load_purchases():
    rows = call('tools.load', purchases=PUR)
    for row in rows:
        row['asins'] = set(row['asins'])
    return rows

def _pick(matches, label):
    return call('tools.pick', matches=matches, label=label)

def A(asin):
    return _Resolver({'A':asin})

def A2(asins):
    return _Resolver({'A2':asins})

def AN(asin):
    return _Resolver({'AN':asin})

def L(contains=None, section=None, status=None, order=None):
    return _Resolver({'line':dict(contains=contains, section=section, status=status, order=order)})

def SUM(parts):
    return _Resolver({'sum':[p.specification for p in parts]})

def FIXED(value):
    return _Resolver({'FIXED':value})

ROWS = load_purchases()
TOOLS = [(t['match'],t['marker'],_Resolver(t['resolver'])) for t in call('tools.definitions')]

def compute():
    return [tuple(row) for row in call('tools.compute', rows=ROWS)]

def inject_structure(text):
    return call('tools.inject', text=text)

def main():
    _main('tools.main', rows=ROWS, tools=TOOLS_MD, dry='--dry' in sys.argv)

if __name__ == '__main__':
    main()
