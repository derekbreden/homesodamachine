"""Typed access to the Rust enclosure electrical graph."""
from .model import Connection
from ._wiring_data import read as _read

_constants = _read("graph_constants")
UNUSED = _constants["UNUSED"]
BOUNDARIES = _constants["BOUNDARIES"]


def owner(part):
    return _read("owner", {"part": part})


def interfaces(terminals, graph):
    return _read("interfaces", {"terminals": terminals, "graph": graph})


def connections():
    return [Connection(**row) for row in _read("connections")]
