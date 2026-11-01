"""Ordered fine-model inputs for the machine's Rust assembly program.

Python supplies the part files and their explicit installed frames. The program
keeps the f64 geometry and face records and writes a fine model for readers and
measurements. Drawing reduction and the production STEP/payload export have
their own caller; this module does not substitute a drawing for a model.
"""
from __future__ import annotations

from contextlib import contextmanager
import json
from pathlib import Path
import tempfile

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


def location(location):
    """The exact three by four matrix carried by an installed CQ location."""
    transform = location.wrapped.Transformation()
    return [[transform.Value(row + 1, col + 1) for col in range(4)]
            for row in range(3)]


@contextmanager
def placed(instances):
    """A temporary fine model assembled by Rust, available until the reader exits."""
    import _rust_part

    with tempfile.TemporaryDirectory(prefix="hsm-placed-model-") as directory:
        output = Path(directory)
        path = output / "placed.numbers.json"
        path.write_text(json.dumps(numbers(instances, name="placed"), sort_keys=True) + "\n")
        _rust_part.run("machine", "machine-assembly-model", path, output)
        yield output / "placed.step.npz"
