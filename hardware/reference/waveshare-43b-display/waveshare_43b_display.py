"""Reference solid for the Waveshare ESP32-S3-Touch-LCD-4.3B (Amazon
B0D925SBYF) — the 4.3" 800x480 capacitive-touch config + interaction
display set into the enclosure front panel (front-panel README §1, BOM §1).
A purchased part, not a printed one — the model is a keep-out envelope for
front-panel cutout and layout, not a manufacturing drawing.

Two stacked rectangular blocks sharing one X-Y center:

- Main body — the PCB, display module, and rear components as one block:
  [106 mm](BODY_WIDTH) (X) x [69 mm](BODY_HEIGHT) (Y) x [17 mm](BODY_DEPTH) (Z).
- Bezel — the front cover-glass / touch-panel plate, standing proud of the
  body front and overhanging it on every side:
  [112.5 mm](BEZEL_WIDTH) (X) x [75 mm](BEZEL_HEIGHT) (Y) x [1 mm](BEZEL_DEPTH) (Z).

Overall envelope: [112.5 mm](BEZEL_WIDTH) x [75 mm](BEZEL_HEIGHT) x [18 mm](TOTAL_DEPTH).

Coordinate frame
----------------
- X = width  : lateral, across the screen
- Y = height : up the screen
- Z = depth  : screen-normal; z = 0 at the device's bounding back (body
               rear), +z toward the screen (the user side)

Origin is the center of the footprint in X-Y; both blocks are centered on
it. The body spans z 0 -> [17 mm](BODY_DEPTH); the bezel caps the front,
z [17 mm](BODY_DEPTH) -> [18 mm](TOTAL_DEPTH).
"""

import sys
from pathlib import Path

import cadquery as cq

_here = Path(__file__).resolve()
sys.path.insert(0, str(next(p for p in _here.parents if p.name == "hardware") / "scripts"))
sys.path.insert(0, str(next(p for p in _here.parents if (p / "tools" / "docgen").is_dir()) / "tools"))
from _cadq_export import export_assembly
from docgen import substitute_md, substitute_py_comments

# --- Main body: PCB + display module + rear components -----------------------
body_width = 106.0    # X, lateral across the screen
body_height = 69.0    # Y, up the screen
body_depth = 17.0     # Z, screen-normal

# --- Bezel: front cover-glass / touch-panel plate ----------------------------
bezel_width = 112.5   # X
bezel_height = 75.0   # Y
bezel_depth = 1.0     # Z

# Bezel overhang per side — the glass border framing the body.
bezel_overhang_x = (bezel_width - body_width) / 2.0   # [3.25 mm](BEZEL_OVERHANG_X)
bezel_overhang_y = (bezel_height - body_height) / 2.0  # [3 mm](BEZEL_OVERHANG_Y)

# Depth seams: z = 0 at the bounding back, +z toward the screen.
body_z0 = 0.0
body_z1 = body_z0 + body_depth
bezel_z0 = body_z1
bezel_z1 = bezel_z0 + bezel_depth
total_depth = bezel_z1


def _centered_block(width, height, z0, depth):
    return (
        cq.Workplane("XY")
        .workplane(offset=z0)
        .box(width, height, depth, centered=(True, True, False))
    )


def build_body():
    """PCB + display module block, centered in X-Y, z 0 -> body_depth."""
    return _centered_block(body_width, body_height, body_z0, body_depth)


def build_bezel():
    """Front cover-glass / touch-panel plate, centered in X-Y over the body,
    z body_depth -> total_depth, overhanging the body on every side."""
    return _centered_block(bezel_width, bezel_height, bezel_z0, bezel_depth)


_PARTS = [
    ("body",  build_body,  cq.Color(0.10, 0.42, 0.22)),  # green PCB / module
    ("bezel", build_bezel, cq.Color(0.12, 0.13, 0.16)),  # dark cover glass
]


def build_assembly():
    a = cq.Assembly(name="waveshare-43b-display")
    for name, builder, color in _PARTS:
        a.add(builder(), name=name, color=color)
    return a


def build_scene():
    return cq.Compound.makeCompound([builder().val() for _, builder, _ in _PARTS])


def main():
    export_assembly(build_assembly(), str(_here.parent / "waveshare-43b-display.step"))
    bb = build_scene().BoundingBox()
    print("-> waveshare-43b-display.step")
    print("display envelope  X[%.1f, %.1f]  Y[%.1f, %.1f]  Z[%.1f, %.1f]   (Z = depth axis, screen +Z)"
          % (bb.xmin, bb.xmax, bb.ymin, bb.ymax, bb.zmin, bb.zmax))
    substitute_md(
        _here.parent / "README.md",
        variables={
            "BODY_WIDTH": f"{body_width:.4g}",
            "BODY_HEIGHT": f"{body_height:.4g}",
            "BODY_DEPTH": f"{body_depth:.4g}",
            "BEZEL_WIDTH": f"{bezel_width:.4g}",
            "BEZEL_HEIGHT": f"{bezel_height:.4g}",
            "BEZEL_DEPTH": f"{bezel_depth:.4g}",
            "TOTAL_DEPTH": f"{total_depth:.4g}",
            "BEZEL_OVERHANG_X": f"{bezel_overhang_x:.4g}",
            "BEZEL_OVERHANG_Y": f"{bezel_overhang_y:.4g}",
        },
        expected_counts={
            "BODY_WIDTH": 1, "BODY_HEIGHT": 1, "BODY_DEPTH": 3,
            "BEZEL_WIDTH": 2, "BEZEL_HEIGHT": 2, "BEZEL_DEPTH": 1,
            "TOTAL_DEPTH": 2, "BEZEL_OVERHANG_X": 1, "BEZEL_OVERHANG_Y": 1,
        },
    )
    print("-> README.md")
    substitute_py_comments(
        Path(__file__),
        variables={
            "BODY_WIDTH": f"{body_width:.4g} mm",
            "BODY_HEIGHT": f"{body_height:.4g} mm",
            "BODY_DEPTH": f"{body_depth:.4g} mm",
            "BEZEL_WIDTH": f"{bezel_width:.4g} mm",
            "BEZEL_HEIGHT": f"{bezel_height:.4g} mm",
            "BEZEL_DEPTH": f"{bezel_depth:.4g} mm",
            "TOTAL_DEPTH": f"{total_depth:.4g} mm",
            "BEZEL_OVERHANG_X": f"{bezel_overhang_x:.4g} mm",
            "BEZEL_OVERHANG_Y": f"{bezel_overhang_y:.4g} mm",
        },
        expected_counts={
            "BODY_WIDTH": 1, "BODY_HEIGHT": 1, "BODY_DEPTH": 3,
            "BEZEL_WIDTH": 2, "BEZEL_HEIGHT": 2, "BEZEL_DEPTH": 1,
            "TOTAL_DEPTH": 2, "BEZEL_OVERHANG_X": 1, "BEZEL_OVERHANG_Y": 1,
        },
    )
    print(f"-> {Path(__file__).name} (self)")


if __name__ == "__main__":
    main()
