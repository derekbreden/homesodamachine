"""Ordered fine-model inputs for the machine's Rust assembly program.

Python supplies the part files and their explicit installed frames. The program
keeps the f64 geometry and face records and writes a fine model for readers and
measurements. Drawing reduction and the production STEP/payload export have
their own caller; this module does not substitute a drawing for a model.
"""
from __future__ import annotations

from pathlib import Path

_KEEP_COLOR = object()


def instance(model, *, name=None, prefix="", indices=None, transform=None,
             color=_KEEP_COLOR):
    """A model's selected solids, in file order, in an explicitly supplied frame.

    With no frame, every f64 coordinate and triangle stays in its original
    order. `name` gives all selected solids one component name; otherwise their
    original names follow `prefix`. `indices` selects zero-based model entries.
    """
    row = {"model": str(Path(model).resolve())}
    if name is not None:
        row["name"] = name
    if prefix:
        row["prefix"] = prefix
    if indices is not None:
        row["indices"] = list(indices)
    if transform is not None:
        row["transform"] = [list(axis) for axis in transform]
    if color is not _KEEP_COLOR:
        row["color"] = None if color is None else list(color)
    return row


def numbers(instances, *, name="enclosure-assembly", queries=()):
    """The assembly's ordered part references and explicit per-solid queries."""
    return {"name": name, "instances": list(instances), "queries": list(queries)}


def write(instances, output, *, name="enclosure-assembly"):
    """Write only the fine model; production drawings and STEP stay separate."""
    import _rust_part

    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    return _rust_part.cut("machine", "machine-assembly-model",
                          numbers(instances, name=name), output)


def measure(instances, queries):
    """Queries name assembled solid indices and `gap` or `shared_volume`."""
    import _rust_part

    return _rust_part.check("machine", "machine-assembly-model",
                            numbers(instances, queries=queries))
