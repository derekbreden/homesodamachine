"""Ordered fine-model inputs for the machine's Rust assembly program.

Python supplies the part files and their explicit installed frames. The program
keeps the f64 geometry and face records and writes a fine model for readers and
measurements. Drawing reduction and the production STEP/payload export have
their own caller; this module does not substitute a drawing for a model.
"""
from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass
import json
from pathlib import Path
import shutil
import tempfile
import zipfile

_KEEP_COLOR = object()


@dataclass(frozen=True)
class ModelReference:
    """A source selection and installed frame, without a geometry-object interface."""

    model: Path
    indices: tuple[int, ...]
    transform: tuple[tuple[float, ...], ...]


@dataclass(frozen=True)
class PlacedModelReference:
    """One temporary fine placement and explicit scalar readings in its installed frame."""

    reference: ModelReference
    model: Path
    summaries: tuple[dict, ...]
    raw_bounds: dict[str, tuple[tuple[float, ...], tuple[float, ...]]]
    snapped_bounds: dict[str, tuple[tuple[float, ...], tuple[float, ...]]]
    rgba: dict[str, tuple[float, ...] | None]


def reference_instance(reference):
    """The existing assembly-program specification for an explicit model reference."""
    return instance(reference.model, indices=reference.indices, transform=reference.transform)


def _metadata(model, kind):
    from _rust_data import request
    from _cadq_export import note_read
    path = Path(model).resolve()
    note_read(path)
    return request('machine-data', 'machine-data',
                   {'op': 'archive_metadata', 'kind': kind, 'path': str(path)})


def document(model):
    """A fine archive's document, read by Rust without opening geometry arrays."""
    return _metadata(model, 'document')


def identity(model):
    """The ordered per-entry names and colours, read in Rust without geometry arrays."""
    return [(name, color) for name, color in _metadata(model, 'identity')]


@contextmanager
def array_reader(model):
    """Rust reads each entry; NumPy hydrates the caller's typed array interface."""
    import numpy as np
    from _rust_data import request
    from _cadq_export import note_read
    model = Path(model).resolve()
    note_read(model)
    with tempfile.TemporaryDirectory(prefix="hsm-fine-entry-") as directory:
        def read(index):
            row = request('machine-data', 'machine-data', {'op': 'archive_entry',
                'path': str(model), 'index': index, 'output': directory})
            arrays = tuple(np.fromfile(row['arrays'][kind]['file'],
                dtype=row['arrays'][kind]['dtype']).reshape(row['arrays'][kind]['shape'],
                                                          order=row['arrays'][kind]['order'])
                for kind in ('V', 'T', 'F'))
            records = [None if record is None else {
                key: np.asarray(value, float) if isinstance(value, list) else value
                for key, value in record.items()} for record in row['records']]
            return (*arrays, records)
        yield read


def write_entries(entries, output, *, document=None, transforms=None):
    """Write ordered fine entries and explicit frames through Rust's stream writer."""
    import _machine_export
    output = Path(output).resolve()
    _machine_export._run({'op': 'entries',
        'entries': [[str(model), index, name, color]
                    for model, index, name, color in entries],
        'transforms': transforms or {}, 'document': document,
        'target': str(output)}, output.parent)


def instance(model, *, name=None, prefix="", indices=None, transform=None,
             color=_KEEP_COLOR):
    """A model's selected solids, in file order, in an explicitly supplied frame.

    With no frame, every f64 coordinate and triangle stays in its original
    order. `name` gives all selected solids one component name; otherwise their
    original names follow `prefix`. `indices` selects zero-based model entries.
    """
    row = {"model": str(Path(model).resolve())}
    if name is not None:
        row["name"] = name
    if prefix:
        row["prefix"] = prefix
    if indices is not None:
        row["indices"] = list(indices)
    if transform is not None:
        row["transform"] = [list(axis) for axis in transform]
    if color is not _KEEP_COLOR:
        row["color"] = None if color is None else list(color)
    return row


def numbers(instances, *, name="enclosure-assembly", queries=()):
    """The assembly's ordered part references and explicit per-solid queries."""
    return {"name": name, "instances": list(instances), "queries": list(queries)}


def write(instances, output, *, name="enclosure-assembly"):
    """Write only the fine model; production drawings and STEP stay separate."""
    import _rust_part

    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    return _rust_part.cut("machine", "machine-assembly-model",
                          numbers(instances, name=name), output)


def measure(instances, queries, *, component_names=(), query_only=False):
    """Fine queries and optional component bounds/volumes for named model entries."""
    import _rust_part

    inputs = numbers(instances, queries=queries)
    if component_names:
        inputs['component_names'] = list(component_names)
    if query_only:
        inputs['query_only'] = True
    return _rust_part.check("machine", "machine-assembly-model",
                            inputs)


def measure_groups(references, queries):
    """Query named fine selections, retaining each selection's original entry order.

    A reference is an existing instance specification with explicit ``indices``.
    Query endpoints name those references. Fine-mask stages name small authored
    tool references under ``references`` as well. No geometry is read in Python.
    """
    from _rust_data import request
    plan = request('machine-data', 'machine-data',
                   {'op': 'query_groups', 'references': references, 'queries': queries})
    return (measure(plan['instances'], plan['queries'], query_only=True)['queries']
            if plan['queries'] else [])


def box_commons(model, requests, *, transform=None):
    """Fine common readings for explicit source-authored axis-aligned box tools.

    Each request names original model entry `indices` and a `box` (low/high
    three-vectors). The kernel constructs that exact tool at its builder grid;
    the already authored body coordinates retain their raw f64 values.
    """
    from _rust_data import request
    requests = list(requests)
    if not requests:
        return []
    plan = request('machine-data', 'machine-data', {'op': 'query_box_plan', 'requests': requests})
    readings = measure([instance(model, indices=plan['indices'], transform=transform)], plan['queries'])['queries']
    return request('machine-data', 'machine-data', {'op': 'query_box_result', 'requests': requests,
                   'owners': plan['owners'], 'readings': readings})


def location(location):
    """The exact three by four matrix carried by an installed CQ location."""
    transform = location.wrapped.Transformation()
    return [[transform.Value(row + 1, col + 1) for col in range(4)]
            for row in range(3)]


@contextmanager
def placed(instances, *, presentation=False, summaries=False):
    """A temporary fine model assembled by Rust, available until the reader exits.

    `summaries=True` also returns the body's scalar readings from the same program run.
    """
    import _rust_part

    with tempfile.TemporaryDirectory(prefix="hsm-placed-model-") as directory:
        output = Path(directory)
        readings = _rust_part.cut("machine", "machine-assembly-model",
                                  numbers(instances, name="placed"), output,
                                  numbers_name="placed")
        model = output / "placed.step.npz"
        if presentation:
            from meshcad.presentation import placed as carry_presentation
            carry_presentation(instances, model)
        yield (model, readings['bodies']) if summaries else model
