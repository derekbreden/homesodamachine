"""Rust cable-retainer datums and local route dressing."""
from ._wiring_data import read as _read


def manifold_bank_site(): return _read("retainer_manifold_site")
def rear_level_hook_site(): return _read("retainer_rear_site")
def cable_sites(): return tuple(_read("retainer_cable_sites"))


def dress_guides(connection, guides, attachments, saved):
    result = _read("retainer_dress", {"connection": connection, "guides": guides,
                                      "state": attachments._state, "saved": saved}, ea=attachments.ea)
    saved.clear()
    saved.update(result["saved"])
    return [tuple(point) for point in result["guides"]]
