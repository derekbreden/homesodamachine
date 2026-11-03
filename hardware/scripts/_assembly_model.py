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


def document(model):
    """A fine archive's small document, without loading its geometry."""
    import numpy as np

    with np.load(model, allow_pickle=False) as archive:
        return (json.loads(archive['document'].tobytes())
                if 'document' in archive.files else {})


def identity(model):
    """The stored per-entry names and linear colours, without loading geometry."""
    import numpy as np

    with np.load(model, allow_pickle=False) as archive:
        return list(zip(json.loads(archive['names'].tobytes()),
                        json.loads(archive['colors'].tobytes()), strict=True))


@contextmanager
def array_reader(model):
    """Read one fine entry at a time; no solid or query backend is constructed."""
    import numpy as np

    with np.load(model, allow_pickle=False) as archive:
        records = json.loads(archive['records'].tobytes())

        def read(index):
            recs = [None if record is None else {
                key: np.asarray(value, float) if isinstance(value, list) else value
                for key, value in record.items()} for record in records[index]]
            return (archive[f'V{index}'], archive[f'T{index}'], archive[f'F{index}'], recs)

        yield read


def write_entries(entries, output, *, document=None, transforms=None):
    """Stream ordered (model, index, name, color) references into one fine archive.

    Numeric members without an explicit frame are copied unchanged. Installed frames
    map one entry at a time. Names, colours, records and the optional document are small
    tables; no mesh or whole-model byte buffer is constructed.
    """
    from contextlib import ExitStack
    import numpy as np

    def placed_record(record, matrix):
        if record is None:
            return None
        linear, offset = matrix[:, :3], matrix[:, 3]
        scale = abs(np.linalg.det(linear)) ** (1 / 3)
        result = dict(record)
        for key in ('p', 'c'):
            if key in record:
                result[key] = linear @ np.asarray(record[key], float) + offset
        if 'd' in record:
            direction = linear @ np.asarray(record['d'], float)
            result['d'] = direction / np.linalg.norm(direction)
            if 'slope' in record and np.dot(result['d'], linear @ np.asarray(record['d'], float)) < 0:
                result['slope'] = -record['slope']
        if 'n' in record:
            normal = np.linalg.inv(linear).T @ np.asarray(record['n'], float)
            result['n'] = normal / np.linalg.norm(normal)
        for key in ('r', 'R'):
            if key in record:
                result[key] = record[key] * scale
        return {key: value.round(9).tolist() if isinstance(value, np.ndarray) else
                round(float(value), 9) if isinstance(value, (float, np.floating)) else value
                for key, value in result.items()}

    def text(archive, key):
        with archive.open(key + '.npy') as source:
            return np.load(source, allow_pickle=False).tobytes().decode()

    def record_spans(value):
        decoder = json.JSONDecoder()
        position, spans = 1, []
        while True:
            while value[position].isspace() or value[position] == ',':
                position += 1
            if value[position] == ']':
                return spans
            start = position
            _record, position = decoder.raw_decode(value, position)
            spans.append((start, position))

    def info(key):
        return zipfile.ZipInfo(key + '.npy', (1980, 1, 1, 0, 0, 0))

    with ExitStack() as stack:
        sources, tables = {}, {}
        for model, _index, _name, _color in entries:
            model = str(model)
            if model not in sources:
                sources[model] = stack.enter_context(zipfile.ZipFile(model))
                value = text(sources[model], 'records')
                tables[model] = (value, record_spans(value))
        with zipfile.ZipFile(output, 'w', zipfile.ZIP_STORED) as archive:
            records = []
            for ordinal, (model, index, _name, _color) in enumerate(entries):
                model = str(model)
                value, spans = tables[model]
                start, end = spans[index]
                frame = (transforms or {}).get(ordinal)
                if frame is None:
                    for kind in 'VTF':
                        with sources[model].open(f'{kind}{index}.npy') as source, \
                                archive.open(info(f'{kind}{ordinal}'), 'w') as target:
                            shutil.copyfileobj(source, target, length=1024 * 1024)
                    records.append((value, start, end))
                else:
                    frame = np.asarray(frame, float).reshape(3, 4)
                    for kind in 'VTF':
                        with sources[model].open(f'{kind}{index}.npy') as source:
                            values = np.load(source, allow_pickle=False)
                        if kind == 'V':
                            values = values @ frame[:, :3].T + frame[:, 3]
                        elif kind == 'T' and np.linalg.det(frame[:, :3]) < 0:
                            values = values[:, [0, 2, 1]]
                        with archive.open(info(f'{kind}{ordinal}'), 'w') as target:
                            np.lib.format.write_array(target, values, allow_pickle=False)
                    mapped = json.dumps([placed_record(record, frame)
                        for record in json.loads(value[start:end])], separators=(',', ':'))
                    records.append((mapped, 0, len(mapped)))

            def array(key, value):
                with archive.open(info(key), 'w') as target:
                    np.lib.format.write_array(target, np.frombuffer(value.encode(), np.uint8),
                                              allow_pickle=False)

            array('names', json.dumps([name for _model, _index, name, _color in entries]))
            array('colors', json.dumps([None if color is None else
                  [round(float(channel), 9) for channel in color]
                  for _model, _index, _name, color in entries]))
            length = 2 + max(0, len(records) - 1) + sum(
                len(value[start:end].encode()) for value, start, end in records)
            with archive.open(info('records'), 'w') as target:
                np.lib.format.write_array_header_1_0(target, {
                    'descr': '|u1', 'fortran_order': False, 'shape': (length,)})
                target.write(b'[')
                for index, (value, start, end) in enumerate(records):
                    if index:
                        target.write(b',')
                    target.write(value[start:end].encode())
                target.write(b']')
            if document is not None:
                array('document', json.dumps(document, separators=(',', ':'), sort_keys=True))


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
    used = dict.fromkeys(name for query in queries for name in
        (query['a'], query['b'], *(name for stage in query.get('fine_mask_stages', ())
                                  for name in stage['references'])))

    def source_key(ref):
        return json.dumps({key: value for key, value in ref.items() if key != 'indices'},
                          separators=(',', ':'), sort_keys=True)

    sources, selections = {}, {}
    for name in used:
        ref = references[name]
        key = source_key(ref)
        sources.setdefault(key, {k: value for k, value in ref.items() if k != 'indices'})
        selections.setdefault(key, set()).update(ref['indices'])
    instances, slots, offset = [], {}, 0
    for key, ref in sources.items():
        indices = sorted(selections[key])
        instances.append({**ref, 'indices': indices})
        for index in indices:
            slots[key, index] = offset
            offset += 1

    def operand(name):
        ref = references[name]
        key = source_key(ref)
        indices = [slots[key, index] for index in ref['indices']]
        return indices[0] if len(indices) == 1 else indices

    numbered = []
    for query in queries:
        row = {**query, 'a': operand(query['a']), 'b': operand(query['b'])}
        if 'fine_mask_stages' in query:
            row['fine_mask_stages'] = [
                {**{key: value for key, value in stage.items() if key != 'references'},
                 'indices': [index for name in stage['references'] for index in
                             ([operand(name)] if isinstance(operand(name), int) else operand(name))]}
                for stage in query['fine_mask_stages']]
        numbered.append(row)
    return measure(instances, numbered, query_only=True)['queries'] if numbered else []


def box_commons(model, requests, *, transform=None):
    """Fine common readings for explicit source-authored axis-aligned box tools.

    Each request names original model entry `indices` and a `box` (low/high
    three-vectors). The kernel constructs that exact tool at its builder grid;
    the already authored body coordinates retain their raw f64 values.
    """
    requests=list(requests)
    if not requests:
        return []
    if any(not row['indices']for row in requests):
        raise ValueError('A box common needs a fine model entry')
    selected=sorted({index for row in requests for index in row['indices']})
    slots={index:i for i,index in enumerate(selected)}
    queries=[];owners=[]
    for owner,row in enumerate(requests):
        for index in row['indices']:
            query={'kind':'common','a':slots[index],'b_box':row['box']}
            if row.get('positive_components', False):
                query['positive_components']=True
            queries.append(query)
            owners.append(owner)
    said=measure([instance(model,indices=selected,transform=transform)],queries)['queries']
    if len(said)!=len(queries):
        raise ValueError('Box common coverage differs from the requested entries')
    grouped=[[]for _ in requests]
    for owner,row in zip(owners,said):
        if 'error'in row:
            raise ValueError(row['error'])
        grouped[owner].append(row['common']['raw'])
    result=[]
    for request,rows in zip(requests,grouped):
        material=[row for row in rows if row['min']is not None]
        raw={'volume_mm3':sum(row['volume_mm3']for row in rows),
                   'min':[min(row['min'][k]for row in material)for k in range(3)]if material else None,
                   'max':[max(row['max'][k]for row in material)for k in range(3)]if material else None}
        if request.get('positive_components', False):
            raw['components']=[component for row in rows for component in row['components']]
        result.append({'indices':list(request['indices']),'box':request['box'],'raw':raw})
    return result


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
        path = output / "placed.numbers.json"
        path.write_text(json.dumps(numbers(instances, name="placed"), sort_keys=True) + "\n")
        readings = _rust_part.run("machine", "machine-assembly-model", path, output)
        model = output / "placed.step.npz"
        if presentation:
            from meshcad.presentation import placed as carry_presentation
            carry_presentation(instances, model)
        yield (model, json.loads(readings)['bodies']) if summaries else model
