"""Presentation and exported-file readings for Rust-backed part drivers."""
from pathlib import Path

import _rust_part
from _rust_data import request


def summary(body, **options):
    if path := options.get('countertop_stl'):
        path = Path(path).resolve()
        try:
            _rust_part._READ_TARGETS.add(path.relative_to(_rust_part.ROOT.resolve()).as_posix())
        except ValueError:
            pass
        options['countertop_stl'] = str(path)
    return request('part-data', 'part-data', {'part': 'output', 'body': body, **options})
