"""Typed Python boundaries for shared Rust scalar providers."""
from dataclasses import asdict, is_dataclass
import math
from pathlib import Path
import sys
import _rust_data
import _rust_part


def _encode(value):
    if isinstance(value, float) and not math.isfinite(value):
        return {'_hsm_float': str(value)}
    if isinstance(value, Path):
        return str(value)
    if is_dataclass(value):
        return _encode(asdict(value))
    if isinstance(value, dict):
        return {str(k): _encode(v) for k,v in value.items()}
    if isinstance(value, (list, tuple, set, frozenset)):
        return [_encode(v) for v in value]
    if hasattr(value, 'tolist'):
        return _encode(value.tolist())
    if hasattr(value, 'toTuple'):
        return _encode(value.toTuple())
    return value


def _decode(value):
    if isinstance(value, dict):
        if set(value) == {'_hsm_float'}:
            return float(value['_hsm_float'])
        return {k:_decode(v) for k,v in value.items()}
    if isinstance(value, list):
        return [_decode(v) for v in value]
    return value


def call(operation, **values):
    try:
        return _decode(_rust_data.request('shared-data', 'shared-data', _encode({'op': operation, **values})))
    except ValueError as error:
        message = str(error)
        for kind in (KeyError, TypeError, AssertionError, StopIteration):
            marker = kind.__name__ + ': '
            if marker in message:
                raise kind(message.split(marker, 1)[1]) from None
        raise


def color_record(color):
    if isinstance(color, str):
        return {'args':[color], 'kwargs':{}}
    made = getattr(color, '__dict__', {}).get('_made')
    if made:
        return {'args':made[0], 'kwargs':made[1]}
    from OCP.Quantity import Quantity_TypeOfColor
    return {'linear':tuple(color.wrapped.GetRGB().Values(Quantity_TypeOfColor.Quantity_TOC_RGB)),
            'srgb':color.toTuple()}


def box_record(box):
    return {name:getattr(box,name) for name in ('xmin','xmax','ymin','ymax','zmin','zmax')}
