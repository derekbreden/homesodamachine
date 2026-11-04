"""Rust shared-cable routing and transported conductor sections."""
from pathlib import Path
from ._wiring_data import read as _read
from .model import route_from_data

SOURCE = Path(__file__).with_name("bundle-routes.json")


def definitions(): return {name: value for name, value in _read("bundle_definitions")}
def cross(a, b): return tuple(_read("bundle_cross", {"a": a, "b": b}))
def rotate(v, axis, angle): return tuple(_read("bundle_rotate", {"value": v, "axis": axis, "angle": angle}))
def circle(segment): return tuple(tuple(v) for v in _read("bundle_circle", {"segment": segment}))
def offset_path(segments, section): return _read("bundle_offset", {"segments": segments, "section": section})
def trimmed(segments, front, back): return _read("bundle_trimmed", {"segments": segments, "front": front, "back": back})


def centreline(b, attachments):
    points, segments = _read("bundle_centreline", {"bundle": b, "state": attachments._state}, ea=attachments.ea)
    return [tuple(point) for point in points], segments


def entry_stations(connection, b, attachments, first):
    return [tuple(point) for point in _read("bundle_entries", {"connection": connection, "bundle": b,
                                   "state": attachments._state, "first": first}, ea=attachments.ea)]


def reed_level_segments(segments, recipe, identity=None):
    return _read("bundle_reed_levels", {"segments": segments, "recipe": recipe, "identity": identity})


def core_route(connection, attachments):
    result = _read("bundle_core_route", {"connection": connection, "state": attachments._state}, ea=attachments.ea)
    return None if result is None else route_from_data(result)


def inputs(attachments):
    bodies, records = _read("bundle_inputs", {"state": attachments._state}, ea=attachments.ea)
    return [tuple(row) for row in bodies], records


def add_jackets(assembly,attachments):
    import cadquery as cq
    bodies,records=inputs(attachments)
    for name,recipe,color in bodies:
        segments=recipe['segments']
        edges=[]
        for s in segments:
            a,end=cq.Vector(*s['start_mm']),cq.Vector(*s['end_mm'])
            edges.append(cq.Edge.makeLine(a,end) if s['kind']=='line' else
                         cq.Edge.makeThreePointArc(a,cq.Vector(*s['midpoint_mm']),end))
        wire=cq.Wire.assembleEdges(edges);start=edges[0].startPoint();axis=edges[0].tangentAt(0)
        outer=cq.Wire.makeCircle(recipe['diameter_mm']/2,start,axis)
        inner=cq.Wire.makeCircle(recipe['inner_diameter_mm']/2,start,axis)
        jacket=cq.Solid.sweep(outer,[inner],wire,makeSolid=True,isFrenet=False)
        assembly.add(jacket,name=name,color=cq.Color(*color))
    return records
