"""Project-neutral stock appearances and the one-body assembly boundary."""
from __future__ import annotations
from _shared_data import call

_CATALOG = call('color.catalog')
_STOCK_RGB = {name:tuple(_CATALOG['colors'][name]) for name in _CATALOG['stock_names']}
_WHITEST = _CATALOG['whitest']
__all__ = ['annotations','cq',*_STOCK_RGB,'step_safe','one_body','stock_srgb']


def __getattr__(name):
    if name == 'cq':
        import cadquery
        globals()[name] = cadquery
        return cadquery
    if name in _STOCK_RGB:
        import cadquery as cq
        result = cq.Color(*_STOCK_RGB[name])
        globals()[name] = result
        return result
    raise AttributeError(name)


def __dir__():
    return sorted(set(globals()) | set(_STOCK_RGB) | {'cq'})


def stock_srgb(name):
    return tuple(call('color.stock_srgb',name=name))


def step_safe(color):
    import cadquery as cq
    args = call('color.step_safe',srgb=color.toTuple())
    return color if args is None else cq.Color(*args)


def one_body(shape,name,color):
    import cadquery as cq
    return cq.Assembly(shape,name=name,color=step_safe(color))
