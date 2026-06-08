#!/usr/bin/env bash
# Regenerate every flavor placeholder asset from the designs in
# tools/gen_flavor_placeholders.py: master PNGs, the firmware RGB565 seed
# headers (S3 240×240 + RP2040 128×115), and the iOS demo-mode bundle copies.
#
# Edit a design in tools/gen_flavor_placeholders.py, run this, commit.
set -euo pipefail
cd "$(dirname "$0")/.."
PY=tools/cad-venv/bin/python

echo "[1/3] masters    -> images/flavor_N.png"
"$PY" tools/gen_flavor_placeholders.py

echo "[2/3] RGB565     -> firmware/src_config/images + firmware/src_display"
"$PY" tools/png_to_rgb565.py

echo "[3/3] iOS bundle -> ios/SodaMachine/SodaMachine/FlavorImages"
dest=ios/SodaMachine/SodaMachine/FlavorImages
mkdir -p "$dest"
cp images/flavor_1.png images/flavor_2.png images/flavor_3.png images/flavor_4.png "$dest/"

echo "Done. LittleFS data image (needs hardware): tools/upload_image.py --build-data"
