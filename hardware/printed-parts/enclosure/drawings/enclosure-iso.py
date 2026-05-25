"""
Isometric line-art view of the home-soda-machine enclosure.

Canonical iso layout: top of enclosure at top of image, front face (y=0) at
lower-right, right side face (x=W) at lower-left. This is a minimal first
drawing while we verify the basics — one circle on the front (ESP32-S3),
one small rectangle on the top (GFCI access band). Right side blank.

Run from the repo root:

    tools/cad-venv/bin/python hardware/printed-parts/enclosure/drawings/enclosure-iso.py

Source for dimensions and the feature inventory:
hardware/printed-parts/enclosure/README.md
"""

import sys
from pathlib import Path

# Make line_art (in tools/line-art/) importable when running this script
# directly. The drawing lives next to the part it describes; the library
# is shared and lives under tools/.
_REPO_ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(_REPO_ROOT / "tools" / "line-art"))

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

    # Top face: GFCI access band — cutout exposing the TEST/RESET band of the
    # Legrand 1597 duplex on the electronics shelf below. The band itself is
    # 27 mm wide × 18 mm tall in the outlet's intrinsic frame, centered on
    # the 42 × 67 mm outlet body. Tucked into the back-right corner with the
    # outlet's tall axis (67) running along the appliance's WIDTH and its
    # wide axis (42) along the DEPTH, so the underlying body sits flush
    # against the back and right edges (5 mm clearance for the mounting
    # yoke). In this rotation the band on the top face is 18 along a (width)
    # × 27 along b (depth) — a tall-narrow band, not a wide-flat one.
    appliance.top.add_rectangle(at=(230.5, 254), w=18, h=27, label="GFCI access band")

    # Top face: pump-cartridge access door for both pump cases.
    # Each pump case: 88 × 75 × 135 mm; tubes on the 75 × 135 face → inserted
    # vertically, that face mates downward into the enclosure. Minimum opening
    # per pump: 75 × 135 mm. Two pumps side by side: 150 mm (2 × 75) across ×
    # 135 mm depth. With margin: 145 mm wide (a) × 165 mm deep (b).
    # Positioned right of center with 5 mm clearance from the right edge (W=269).
    # NOTE: two identical 145 mm-wide doors would need 300+ mm total width —
    # they cannot both fit on a 269 mm top face. Hopper door is a separate size.
    appliance.top.add_rectangle(at=(192, 91), w=145, h=165, label="pump cartridge door (×2)")

    # Top face: hopper access door — PLACEHOLDER width 100 mm.
    # SodaStream bottle OD ≈ 88 mm; 100 mm gives ~6 mm clearance each side.
    # Exact size TBD. Centered left of the pump door with a 12 mm gap between.
    appliance.top.add_rectangle(at=(57, 91), w=100, h=165, label="hopper door (TBD)")

    output_path = Path(__file__).parent / "enclosure-iso.svg"
    scene.render(str(output_path))
    print(f"Wrote {output_path}")


if __name__ == "__main__":
    main()
