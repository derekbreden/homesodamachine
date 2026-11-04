"""OCCT-compatible color arithmetic supplied by the Rust shared provider."""
from _shared_data import call

def rgba(args,kwargs):
    result = call('color.rgba',args=args,kwargs=kwargs)
    return tuple(result) if result is not None else None

def srgb(rgb):
    return tuple(call('color.srgb',rgb=rgb))

def _f32(value):
    return call('color.f32',value=value)

def _curve(value):
    return call('color.curve',value=value)

def _curve32(value):
    return call('color.curve32',value=value)

def _inverse(value):
    return call('color.inverse',value=value)
