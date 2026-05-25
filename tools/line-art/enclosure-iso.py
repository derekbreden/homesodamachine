"""
Isometric line-art view of the home-soda-machine enclosure.

Canonical iso layout: top of enclosure at top of image, front face (y=0) at
lower-right, right side face (x=W) at lower-left. This is a minimal first
drawing while we verify the basics — one circle on the front (ESP32-S3),
one small rectangle on the top (GFCI access band). Right side blank.

Run from the repo root:

    tools/cad-venv/bin/python tools/line-art/enclosure-iso.py

Source for dimensions and the feature inventory:
hardware/printed-parts/enclosure/README.md
"""

import sys
from pathlib import Path

# Make line_art importable when running this script directly
sys.path.insert(0, str(Path(__file__).parent))

from line_art import Scene, Box


def main() -> None:
    scene = Scene()

    # Enclosure outer dimensions (working values per the enclosure README):
    #   Width ≈ foam shell width                       (~269 mm)
    #   Depth  = foam shell depth + compressor zone    (~280 mm)
    #   Height = foam shell height + electronics shelf (~280 mm)
    appliance = scene.add(Box(W=269, D=280, H=280))

    # Front face: just the ESP32-S3 rotary display for now (~32 mm OD).
    # Face-local (a, b): a is x in 3D (0..W), b is z in 3D (0..H).
    appliance.front.add_circle(at=(135, 140), d=32, label="ESP32-S3")

    # Top face: GFCI access band (~30 × 8 mm). The GFCI module itself lives
    # on the electronics shelf; only the band is customer-visible.
    # Face-local (a, b): a is x in 3D (0..W), b is y in 3D (0..D).
    appliance.top.add_rectangle(at=(135, 140), w=30, h=8, label="GFCI access band")

    output_path = Path(__file__).parent / "enclosure-iso.svg"
    scene.render(str(output_path))
    print(f"Wrote {output_path}")


if __name__ == "__main__":
    main()
