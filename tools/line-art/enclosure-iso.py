"""
Isometric line-art view of the home-soda-machine enclosure.

Shows the appliance from front-right-above. Visible faces: front, right side,
top. Front face carries the customer-attention features: RP2040 round display,
ESP32-S3 round display, front-dispense spout (opening + lever indication),
GFCI access band, CO2 inlet.

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

    # ------------------------------------------------------------------
    # Front face features
    # Face-local 2D coords (a, b): a is horizontal-from-left (0..269),
    # b is vertical-from-bottom (0..280).
    # ------------------------------------------------------------------

    # RP2040 round display — Waveshare 0.99" round LCD (~25 mm OD).
    # Detachable; the cord pays out behind the panel as the customer pulls.
    appliance.front.add_circle(at=(70, 230), d=25, label="RP2040")

    # ESP32-S3 1.28" rotary display — Meshnology (~32 mm OD).
    appliance.front.add_circle(at=(200, 230), d=32, label="ESP32-S3")

    # Front-dispense spout — opening + lever indication.
    # The opening is where carbonated flavored water comes out; the small
    # rectangle below indicates the user-actuation lever.
    appliance.front.add_circle(at=(135, 160), d=20, label="front-dispense opening")
    appliance.front.add_rectangle(at=(135, 140), w=25, h=4, label="front-dispense lever")

    # GFCI access band — cutout exposing the Legrand 1597's TEST/RESET/LED
    # band. The GFCI module itself lives on the electronics shelf; only the
    # band is customer-visible through this small cutout.
    appliance.front.add_rectangle(at=(135, 100), w=30, h=8, label="GFCI access band")

    # CO2 inlet — DERPIPE 5/16" tube push-to-connect bulkhead (~15 mm OD).
    # Sits toward the right edge of the front face, near where the cylinder
    # neighbors the appliance in the cabinet side gap.
    appliance.front.add_circle(at=(220, 60), d=15, label="CO2 inlet")

    output_path = Path(__file__).parent / "enclosure-iso.svg"
    scene.render(str(output_path))
    print(f"Wrote {output_path}")


if __name__ == "__main__":
    main()
