"""The display adapter exposes measured mounting datums and the authored frozen geometry."""
from __future__ import annotations

import sys
from functools import cache as _reference_cache
from pathlib import Path

_REFERENCE_DIR = Path(__file__).resolve().parent
STEP_PATH = _REFERENCE_DIR / "waveshare-43b-display.step"
PAYLOAD_PATH = _REFERENCE_DIR / "waveshare-43b-display.step.mesh"
FINE_PAYLOAD_PATH = PAYLOAD_PATH
ASSET_MANIFEST_PATH = _REFERENCE_DIR / "frozen-asset.json"
_hardware = next(p for p in _REFERENCE_DIR.parents if p.name == "hardware")
sys.path.insert(0, str(_hardware / "scripts"))
sys.path.insert(0, str(_hardware / "reference"))
from _reference_data import data as _reference_data

_reference_values = _reference_data("waveshare_43b_display")
globals().update({name: _reference_values[name] for name in (
    "body_width", "body_height", "body_depth", "bezel_width", "bezel_height",
    "bezel_depth", "bezel_corner_r", "bezel_offset_x", "bezel_offset_z",
    "bezel_y0", "bezel_y1", "body_y0", "body_y1", "total_depth",
    "bezel_y_center", "body_y_center",
)})


@_reference_cache
def _frozen_parts():
    from _cadq_export import import_assembly
    return import_assembly(STEP_PATH)


def build_body():
    """The rear assembly, grouped under the established body accessor."""
    import cadquery as cq
    rear = [shape for name, (shape, _color) in _frozen_parts().items() if name != "bezel"]
    return cq.Workplane("XY").newObject([cq.Compound.makeCompound(rear)])


def build_bezel():
    """The measured front mounting glass."""
    import cadquery as cq
    return cq.Workplane("XY").newObject([_frozen_parts()["bezel"][0]])


@_reference_cache
def _parts():
    import cadquery as cq
    return [
        (name, lambda shape=shape: cq.Workplane("XY").newObject([shape]), color)
        for name, (shape, color) in _frozen_parts().items()
    ]


def build_assembly():
    import cadquery as cq
    assembly = cq.Assembly(name="waveshare-43b-display")
    for name, (shape, color) in _frozen_parts().items():
        assembly.add(shape, name=name, color=color)
    return assembly


def build_scene():
    import cadquery as cq
    return cq.Compound.makeCompound([shape for shape, _color in _frozen_parts().values()])


def main():
    print(f"Frozen STEP: {STEP_PATH}")
    print(f"Display payload: {PAYLOAD_PATH}")


if __name__ == "__main__":
    main()


def __getattr__(name):
    if name == "_PARTS":
        return _parts()
    if name == "cq":
        import cadquery as cq
        return cq
    if name == "export_assembly":
        import _cadq_export
        return _cadq_export.export_assembly
    if name in {"C_DISPLAY_GLASS", "C_DISPLAY"}:
        import _materials
        return getattr(_materials, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
