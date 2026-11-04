#!/usr/bin/env python3
"""Rust purchase totals and project-evidence reports, with Python caller types.

The write, check, report, audit, export-json and export-csv modes retain their
existing flags. Named inspection modes read without mutating the ledger.
"""
import argparse
import sys
from decimal import Decimal
from pathlib import Path
from _ledger_rust import call

HERE = Path(__file__).resolve().parent
LEDGER = HERE.parent / 'ledger/purchases.md'
ORDERS = HERE.parent / 'ledger/purchases.orders.json'
EVIDENCE = HERE.parent / 'ledger/purchases.evidence.json'
EXCLUDE_SECTIONS = {'Totals'}
STATUS_KEYWORDS = ('LIKELY-TO-BUY', 'NOT NEEDED', 'alt option', 'ON-ORDER', 'ACQUIRED',
                   'MISSING', 'PARTIAL', 'CANCELLED', 'RETURNED', 'REPLACEMENT', 'REPLACED', 'UNRESOLVED')
EM = '—'
STALE_ON_ORDER_DAYS = 45
RECONCILE_TOLERANCE = Decimal('0.01')
ZERO = Decimal('0')


def _call(operation, **values):
    return call('ledger.' + operation, _program='ledger-analysis', **values)


def _row(value):
    result = dict(value)
    for name in ('cost', 'unit_price'):
        if result.get(name) is not None:
            result[name] = Decimal(str(result[name]))
    return result


def _decimals(value):
    if isinstance(value, float):
        return Decimal(str(value))
    if isinstance(value, list):
        return [_decimals(v) for v in value]
    if isinstance(value, dict):
        return {k:_decimals(v) for k,v in value.items()}
    return value


def first_price(cell):
    result = _call('first_price', cell=cell)
    return Decimal(result) if result is not None else None


def lead_int(cell):
    return _call('lead_int', cell=cell)


def parse(path):
    totals, sections, labor, ambiguous, rows = _call('parse', path=path)
    return ({k:Decimal(v) for k,v in totals.items()},
            {k:Decimal(v) for k,v in sections.items()}, Decimal(labor),
            [tuple(value) for value in ambiguous], [_row(value) for value in rows])


def load_orders(path=ORDERS):
    return _decimals(_call('load_orders', path=path))


def days_since(iso_date, today):
    return _call('days_since', date=iso_date, today=today)


def reconcile_orders(rows, orders, tolerance=RECONCILE_TOLERANCE):
    mismatch, unknown, split = _call('reconcile', rows=rows, orders=orders, tolerance=tolerance)
    return ([(oid, Decimal(allocated), Decimal(project), count) for oid, allocated, project, count in mismatch],
            [(oid, Decimal(allocated)) for oid, allocated in unknown], split)


def stale_on_order(rows, today):
    aged, undated = _call('aged', rows=rows, today=today)
    return [(age, _row(row)) for age,row in aged], [_row(row) for row in undated]


def unrecorded_orders(rows, orders):
    return [(oid,_decimals(order)) for oid,order in _call('unrecorded', rows=rows, orders=orders)]


def variables_from_totals(status_totals, sections, labor, analysis=None):
    return _call('variables', statuses=status_totals, sections=sections, labor=labor, analysis=analysis)


def stale_markers(path, variables):
    return _call('stale_markers', path=path, variables=variables)


def generated_paths(path):
    return tuple(Path(name) for name in _call('generated_paths', path=path))


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group()
    names = ('write','check','report','audit','export-json','export-csv')
    for mode in names:
        modes.add_argument('--' + mode, action='store_true')
    parser.add_argument('--ledger', default=LEDGER)
    parser.add_argument('--orders', default=ORDERS)
    parser.add_argument('--evidence', default=EVIDENCE)
    args = parser.parse_args(argv)
    mode = next((name for name in names if getattr(args,name.replace('-','_'))), 'write')
    try:
        result = _call('main', mode=mode, ledger=args.ledger, orders=args.orders, evidence=args.evidence)
    except (OSError, ValueError, TypeError, KeyError) as error:
        print(f'Ledger integrity error: {error}', file=sys.stderr)
        return 1
    sys.stdout.write(result['output'])
    sys.stderr.write(result.get('stderr',''))
    return result['status']


if __name__ == '__main__':
    sys.exit(main())
