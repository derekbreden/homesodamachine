"""Reference solid for the Waveshare ESP32-S3-Touch-LCD-4.3B (Amazon
B0D925SBYF) — the 4.3" 800x480 capacitive-touch config + interaction
display let into the 45° facet chamfered across `enclosure-front-top`'s
top-front arris (enclosure/enclosure README, BOM §1). A purchased part, not a
printed one — the model is a keep-out envelope for the facet's cutout and
layout, not a manufacturing drawing.

Two stacked rectangular blocks sharing one X-Z center, the screen facing
the user (-Y, forward):

- Main body — the PCB, display module, and rear components as one block:
  (X) x (Z) x (Y).
- Bezel — the front cover-glass / touch-panel plate, standing proud of the
  body front and overhanging it on every side, larger than the body and offset
  on it, its outline corners rounded:
  (X) x (Z) x (Y).

Overall envelope: (X) x (Z) x (Y).

Coordinate frame (the repo world frame)
---------------------------------------
- X = width  : lateral, across the screen
- Z = height : up the screen
- Y = depth  : screen-normal; the screen faces -Y (forward, toward the
               user). The front cover-glass face sits at Y = 0; the device
               extends back into the appliance toward +Y.

Origin is the center of the body in X-Z; the body is centered on it and the
bezel is offset in X and in Z.
The bezel caps the front, Y 0 ->; the body runs behind it,
Y ->.


The reference STEP and payloads are declared in `frozen-asset.json`.
Native builder functions remain available to current composition callers.
"""

from __future__ import annotations

import sys
from pathlib import Path
from functools import cache as _reference_cache

_REFERENCE_DIR = Path(__file__).resolve().parent
STEP_PATH = _REFERENCE_DIR / 'waveshare-43b-display.step'
PAYLOAD_PATH = _REFERENCE_DIR / 'waveshare-43b-display.step.mesh'
FINE_PAYLOAD_PATH = _REFERENCE_DIR / 'waveshare-43b-display.step.mesh'
ASSET_MANIFEST_PATH = _REFERENCE_DIR / "frozen-asset.json"


_here = Path(__file__).resolve()
sys.path.insert(0, str(next(p for p in _here.parents if p.name == "hardware") / "scripts"))
sys.path.insert(0, str(next(p for p in _here.parents if (p / "tools" / "docgen").is_dir()) / "tools"))

# --- Main body: PCB + display module + rear components -----------------------

_reference_hardware = next(p for p in Path(__file__).resolve().parents if p.name == 'hardware')
import sys as _reference_sys
_reference_sys.path.insert(0, str(_reference_hardware / 'reference'))
from _reference_data import data as _reference_data
_reference_values = _reference_data('waveshare_43b_display')
globals().update({name: _reference_values[name] for name in ('body_width', 'body_height', 'body_depth', 'bezel_width', 'bezel_height', 'bezel_depth', 'bezel_corner_r', 'bezel_offset_x', 'bezel_offset_z', 'bezel_y0', 'bezel_y1', 'body_y0', 'body_y1', 'total_depth', 'bezel_y_center', 'body_y_center')})


# --- Bezel: front cover-glass / touch-panel plate ----------------------------

# The bezel is larger than the body and sits offset on it — its border reaches
# further up and to the left of the body. How it lands in the enclosure facet
# (which centers the glass) is the enclosure's business.

# Depth seams along Y (screen-normal). The screen faces -Y (toward the user);
# the front cover-glass face sits at Y = 0, and the device extends back into
# the appliance toward +Y.



def _block(width, height, depth, y_center, x_center=0.0, z_center=0.0):
    """Box of the given size, centered in X (width) and Z (height) on
    (x_center, z_center) and at y_center along Y (screen-normal)."""
    import cadquery as cq
    return (
        cq.Workplane("XY")
        .box(width, depth, height, centered=True)
        .translate((x_center, y_center, z_center))
    )


def build_body():
    """PCB + display module block, behind the bezel, Y body_y0 -> body_y1."""
    return _block(body_width, body_height, body_depth, body_y_center)


def build_bezel():
    """Front cover-glass / touch-panel plate, screen facing -Y, standing proud
    of the body and overhanging it on every side, offset on the body, its
    outline corners rounded. Y 0 -> bezel_depth."""
    return (
        _block(bezel_width, bezel_height, bezel_depth, bezel_y_center,
               bezel_offset_x, bezel_offset_z)
        .edges("|Y").fillet(bezel_corner_r)
    )


@_reference_cache
def _parts():
    from _materials import C_DISPLAY, C_DISPLAY_GLASS
    return [
        ("body",  build_body,  C_DISPLAY),        # the module's own blue solder mask
        ("bezel", build_bezel, C_DISPLAY_GLASS),  # the cover glass over the panel
    ]


def build_assembly():
    import cadquery as cq
    a = cq.Assembly(name="waveshare-43b-display")
    for name, builder, color in _parts():
        a.add(builder(), name=name, color=color)
    return a


def build_scene():
    import cadquery as cq
    return cq.Compound.makeCompound([builder().val() for _, builder, _ in _parts()])


def main():
    print(f"Frozen STEP: {STEP_PATH}")
    print(f"Display payload: {PAYLOAD_PATH}")
    print(f"Fine payload: {FINE_PAYLOAD_PATH}")


if __name__ == "__main__":
    main()


def __getattr__(name):
    if name == '_PARTS':
        return _parts()
    if name == 'cq':
        import cadquery as cq
        return cq
    if name in {'export_assembly'}:
        import _cadq_export
        return getattr(_cadq_export, name)
    if name in {'C_DISPLAY_GLASS', 'C_DISPLAY'}:
        import _materials
        return getattr(_materials, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
