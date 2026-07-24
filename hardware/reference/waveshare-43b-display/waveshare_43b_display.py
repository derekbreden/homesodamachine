"""Reference solid for the Waveshare ESP32-S3-Touch-LCD-4.3B (Amazon
B0D925SBYF) — the 4.3" 800x480 capacitive-touch config + interaction
display set into the enclosure front panel (front-panel README §1, BOM §1).
A purchased part, not a printed one — the model is a keep-out envelope for
front-panel cutout and layout, not a manufacturing drawing.

Two stacked rectangular blocks sharing one X-Z center, the screen facing
the user (-Y, forward):

- Main body — the PCB, display module, and rear components as one block:
  [106 mm](BODY_WIDTH) (X) x [69 mm](BODY_HEIGHT) (Z) x [17 mm](BODY_DEPTH) (Y).
- Bezel — the front cover-glass / touch-panel plate, standing proud of the
  body front and overhanging it on every side, larger than the body and offset
  on it, its outline corners rounded [2.5 mm](BEZEL_CORNER_R):
  [113.5 mm](BEZEL_WIDTH) (X) x [77 mm](BEZEL_HEIGHT) (Z) x [1 mm](BEZEL_DEPTH) (Y).

Overall envelope: [113.5 mm](BEZEL_WIDTH) (X) x [77 mm](BEZEL_HEIGHT) (Z) x [18 mm](TOTAL_DEPTH) (Y).

Coordinate frame (the repo world frame)
---------------------------------------
- X = width  : lateral, across the screen
- Z = height : up the screen
- Y = depth  : screen-normal; the screen faces -Y (forward, toward the
               user). The front cover-glass face sits at Y = 0; the device
               extends back into the appliance toward +Y.

Origin is the center of the body in X-Z; the body is centered on it and the
bezel is offset [-0.5 mm](BEZEL_OFFSET_X) in X and [1 mm](BEZEL_OFFSET_Z) in Z.
The bezel caps the front, Y 0 -> [1 mm](BEZEL_DEPTH); the body runs behind it,
Y [1 mm](BEZEL_DEPTH) -> [18 mm](TOTAL_DEPTH).
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
body_height = 69.0    # Z, up the screen
body_depth = 17.0     # Y, screen-normal (into the appliance)

# --- Bezel: front cover-glass / touch-panel plate ----------------------------
bezel_width = 113.5   # X
bezel_height = 77.0   # Z
bezel_depth = 1.0     # Y
bezel_corner_r = 2.5  # rounded corners of the cover-glass outline

# The bezel is larger than the body and sits offset on it — its border reaches
# further up and to the left of the body. How it lands in the enclosure facet
# (which centers the glass) is the enclosure's business.
bezel_offset_x = -0.5  # [-0.5 mm](BEZEL_OFFSET_X) glass center offset from the body, toward −X
bezel_offset_z = 1.0   # [1 mm](BEZEL_OFFSET_Z) glass center offset from the body, up the screen

# Depth seams along Y (screen-normal). The screen faces -Y (toward the user);
# the front cover-glass face sits at Y = 0, and the device extends back into
# the appliance toward +Y.
bezel_y0 = 0.0
bezel_y1 = bezel_y0 + bezel_depth
body_y0 = bezel_y1
body_y1 = body_y0 + body_depth
total_depth = body_y1

bezel_y_center = bezel_y0 + bezel_depth / 2.0
body_y_center = body_y0 + body_depth / 2.0


def _block(width, height, depth, y_center, x_center=0.0, z_center=0.0):
    """Box of the given size, centered in X (width) and Z (height) on
    (x_center, z_center) and at y_center along Y (screen-normal)."""
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
    print("display envelope  X[%.1f, %.1f]  Y[%.1f, %.1f]  Z[%.1f, %.1f]   (screen faces -Y; Y = depth axis)"
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
            "BEZEL_CORNER_R": f"{bezel_corner_r:.4g}",
            "TOTAL_DEPTH": f"{total_depth:.4g}",
            "BEZEL_OFFSET_X": f"{bezel_offset_x:.4g} mm",
            "BEZEL_OFFSET_Z": f"{bezel_offset_z:.4g} mm",
        },
        expected_counts={
            "BODY_WIDTH": 1, "BODY_HEIGHT": 1, "BODY_DEPTH": 1,
            "BEZEL_WIDTH": 2, "BEZEL_HEIGHT": 2, "BEZEL_DEPTH": 3,
            "BEZEL_CORNER_R": 1,
            "TOTAL_DEPTH": 2, "BEZEL_OFFSET_X": 1, "BEZEL_OFFSET_Z": 1,
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
            "BEZEL_CORNER_R": f"{bezel_corner_r:.4g} mm",
            "TOTAL_DEPTH": f"{total_depth:.4g} mm",
            "BEZEL_OFFSET_X": f"{bezel_offset_x:.4g} mm",
            "BEZEL_OFFSET_Z": f"{bezel_offset_z:.4g} mm",
        },
        expected_counts={
            "BODY_WIDTH": 1, "BODY_HEIGHT": 1, "BODY_DEPTH": 1,
            "BEZEL_WIDTH": 2, "BEZEL_HEIGHT": 2, "BEZEL_DEPTH": 3,
            "BEZEL_CORNER_R": 1,
            "TOTAL_DEPTH": 2, "BEZEL_OFFSET_X": 2, "BEZEL_OFFSET_Z": 2,
        },
    )
    print(f"-> {Path(__file__).name} (self)")


if __name__ == "__main__":
    main()
