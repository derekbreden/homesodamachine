"""Rust housing, dressed fuse-lead and terminal-insulation recipes."""
from ._wiring_data import read as _read

RING_BORE = _read("termination_constants")["RING_BORE"]


def final_join_placements(): return _read("termination_joins")


def _cylinder(radius, height, base=(0., 0., 0.), axis=(0., 0., 1.)):
    return _read("termination_cylinder", {"radius": radius, "height": height, "base": base, "axis": axis})


def _ring_input(ea):
    return tuple(_read("termination_ring", ea=ea))


def inputs(attachments, connections, routes):
    bodies, records = _read("termination_inputs", {"state": attachments._state,
                           "connections": connections}, ea=attachments.ea)
    return [tuple(row) for row in bodies], records
