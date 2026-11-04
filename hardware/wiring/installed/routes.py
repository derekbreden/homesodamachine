"""Rust installed route selection with typed Python compatibility records."""
from pathlib import Path
from ._wiring_data import read as _read
from .model import route_from_data

OVERRIDES = Path(__file__).with_name("route-overrides.json")
RIBBON_PITCH_MM = _read("route_constants")["RIBBON_PITCH_MM"]


def station(spec, attachments): return attachments.station(spec)


def routed(connections, attachments):
    return [route_from_data(row) for row in _read("route_routed", {"connections": connections,
                            "state": attachments._state}, ea=attachments.ea)]


def guide_points(c, at, groups, saved=None):
    return [tuple(point) for point in _read("route_guide", {"connection": c, "state": at._state,
                                    "groups": groups, "saved": saved or {}}, ea=at.ea)]


def pump_lead_guides(c, at, n):
    return [tuple(point) for point in _read("route_pump_lead", {"connection": c, "state": at._state, "n": n})]


def pump_terminal_guides(c, at, n):
    return [tuple(point) for point in _read("route_pump_terminal", {"connection": c, "state": at._state, "n": n})]


def pump_internal_guides(at, x, terminal_x, lane, n):
    return [tuple(point) for point in _read("route_pump_internal", {"state": at._state, "x": x,
                                          "terminal_x": terminal_x, "lane": lane, "n": n})]


def display_internal_guides(at, n):
    return [tuple(point) for point in _read("route_display_internal", {"state": at._state, "n": n})]
