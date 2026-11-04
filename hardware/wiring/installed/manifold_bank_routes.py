"""The Rust manifold-bank fanout, exposed to existing route callers."""
from ._wiring_data import read as _read


def dress_manifold_bank_guides(connection, guides, attachments, saved):
    result = _read("route_dress_bank", {"connection": connection, "guides": guides,
                                       "state": attachments._state, "saved": saved}, ea=attachments.ea)
    saved.clear()
    saved.update(result["saved"])
    return None if result["guides"] is None else [tuple(point) for point in result["guides"]]
