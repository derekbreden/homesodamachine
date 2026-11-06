"""The declared enclosure Box: the first existing declaration this source reads."""

from __future__ import annotations

from pathlib import Path


_HERE = Path(__file__).resolve()
_ROOT = next(p for p in _HERE.parents if (p / "tools" / "docgen").is_dir())
_BOXES = (
    _ROOT / "hardware" / "manifold-layout" / "enclosure-box.json",
    _ROOT / "bazel-bin" / "out" / "enclosure-box" / "hardware" / "manifold-layout"
    / "enclosure-box.json",
)


def _declared_box(box_spec, enc):
    """The first existing declared Box this source can read, with its path.

    A carried Box may trail a source checkpoint while the most recent completed producer output
    remains in bazel-bin.  Shape/schema validation belongs to `_box_spec.read`; this path never
    runs the placement producer to repair an old document.
    """
    refused = []
    for path in _BOXES:
        try:
            box, bounds = box_spec.read(
                enc.Box, enc.Bound, (enc.Pack, enc.PortField, enc.Nameplate), path=path)
            return box, bounds, path
        except (FileNotFoundError, ValueError) as error:
            refused.append(f"{path.relative_to(_ROOT)}: {error}")
    raise ValueError("no existing enclosure-box declaration matches this source:\n  "
                     + "\n  ".join(refused))
