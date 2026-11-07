"""Python value marshalling for the Rust project-evidence ledger reader."""
import datetime
from _ledger_rust import call


def _call(operation, **values):
    return call('analysis.' + operation, _program='ledger-analysis', **values)


_DEFINITIONS = _call('definitions')
for _name, _value in _DEFINITIONS.items():
    globals()[_name] = set(_value) if isinstance(_value, list) else _value


def plain_text(value):
    return _call('plain_text', value=value)


def parse_date(value):
    return _call('parse_date', value=value)


def date_bounds(value):
    bounds = _call('date_bounds', value=value)
    return tuple(datetime.date.fromisoformat(day) for day in bounds) if bounds is not None else None


def date_month(value):
    return _call('date_month', value=value)


def to_minor(amount, currency, scales):
    return _call('to_minor', value=amount, currency=currency, scales=scales)


def format_minor(amount, currency='USD', scales=None):
    return _call('format_minor', value=amount, currency=currency, scales=scales or {'USD': 2})


def load_evidence(path):
    return call('ledger.load_evidence', _program='ledger-analysis', path=path)


def input_fingerprint(ledger_path, evidence):
    return _call('fingerprint', path=ledger_path, evidence=evidence)


def analyze(rows, evidence, fingerprint=None):
    return _call('analyze', rows=rows, evidence=evidence, fingerprint=fingerprint)


def validate(data, errors, warnings):
    errors[:], warnings[:] = _call('validate', data=data, errors=errors, warnings=warnings)


def _relationships(data):
    result = _call('relationships', data=data)
    data.clear()
    data.update(result)


def summaries(data):
    return _call('summaries', data=data)


def export_json(data):
    return _call('export_json', data=data)


def export_csv(data):
    return _call('export_csv', data=data)


def render_report(data, audit=False):
    return _call('report', data=data, audit=audit)


def _row(value):
    from decimal import Decimal
    result = dict(value)
    for name in ('cost', 'unit_price'):
        if result.get(name) is not None:
            result[name] = Decimal(str(result[name]))
    return result


def parse(path):
    """The purchase ledger's status, section and labor totals, its ambiguous rows and its rows."""
    from decimal import Decimal
    totals, sections, labor, ambiguous, rows = call('ledger.parse', _program='ledger-analysis', path=path)
    return ({k: Decimal(v) for k, v in totals.items()},
            {k: Decimal(v) for k, v in sections.items()}, Decimal(labor),
            [tuple(value) for value in ambiguous], [_row(value) for value in rows])


def reconcile_orders(rows, orders, tolerance=None):
    from decimal import Decimal
    tolerance = Decimal('0.01') if tolerance is None else tolerance
    mismatch, unknown, split = call('ledger.reconcile', _program='ledger-analysis', rows=rows,
                                    orders=orders, tolerance=tolerance)
    return ([(oid, Decimal(allocated), Decimal(project), count)
             for oid, allocated, project, count in mismatch],
            [(oid, Decimal(allocated)) for oid, allocated in unknown], split)


def variables_from_totals(status_totals, sections, labor, analysis=None):
    return call('ledger.variables', _program='ledger-analysis', statuses=status_totals,
                sections=sections, labor=labor, analysis=analysis)
