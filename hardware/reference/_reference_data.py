"""Type and path marshalling for the compiled Rust reference dimensions."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'hardware/scripts'))
import _rust_part
from _rust_data import request

_TYPES = {}


def register_types(**types):
    _TYPES.update(types)


def _encode(value):
    if type(value).__name__ in ('Env', 'Heap'):
        return {'$env': {'kind': type(value).__name__, **{
            name: _encode(getattr(value, name)) for name in ('name', 'x', 'y', 'z', 'bound', 'source')}}}
    if type(value).__name__ == 'Holder':
        return {'$holder': {name: _encode(getattr(value, name)) for name in (
            'name', 'shape', 'x_u', 'y_u', 'height_u', 'takes', 'note', 'opts')}}
    if isinstance(value, Path):
        return {'$path': str(value)}
    if isinstance(value, tuple):
        return {'$tuple': [_encode(v) for v in value]}
    if isinstance(value, list):
        return [_encode(v) for v in value]
    if isinstance(value, dict):
        return {'$dict': [[_encode(k), _encode(v)] for k, v in value.items()]}
    return value


def _decode(value):
    if isinstance(value, list):
        return [_decode(v) for v in value]
    if isinstance(value, dict):
        if set(value) in ({'$env'}, {'$holder'}):
            record = value.get('$env', value.get('$holder'))
            kind = record.get('kind', 'Holder')
            cls = _TYPES.get(kind)
            if cls is None:
                import importlib
                cls = getattr(importlib.import_module('holders' if kind == 'Holder' else '_bound'), kind)
            instance = object.__new__(cls)
            for name, field in record.items():
                if name != 'kind':
                    object.__setattr__(instance, name, _decode(field))
            return instance
        if set(value) == {'$namespace'}:
            from types import SimpleNamespace
            return SimpleNamespace(**_decode(value['$namespace']))
        if set(value) == {'$tuple'}:
            return tuple(_decode(v) for v in value['$tuple'])
        if set(value) == {'$dict'}:
            return {_decode(k): _decode(v) for k, v in value['$dict']}
        if set(value) == {'$path'}:
            return Path(value['$path'])
        return {k: _decode(v) for k, v in value.items()}
    return value


def data(module, method='state', args=(), kwargs=None, inputs=None, overrides=None):
    upstream = {module: {name: _encode(value) for name, value in (inputs or {}).items()}}
    said = request('part-data', 'part-data', {
        'part': 'reference', 'module': module, 'method': method, 'root': str(ROOT),
        'args': [_encode(v) for v in args], 'kwargs': {name: _encode(value) for name, value in (kwargs or {}).items()}, 'inputs': upstream,
        'overrides': {module: {name: _encode(value) for name, value in (overrides or {}).items()}},
    })
    _rust_part._READ_TARGETS.update(said['reads'])
    for message in said.get('messages', ()):
        print(message)
    if said.get('holder_updates') is not None and overrides and 'HOLDERS' in overrides:
        for target, source in zip(overrides['HOLDERS'], _decode(said['holder_updates'])):
            target.height_u = source.height_u
    return _decode(said['result'])
