#!/usr/bin/env bash
# Regenerate the native flavor portraits, firmware renditions and iOS demo artwork.
set -euo pipefail
cd "$(dirname "$0")/.."
hsm-marketing flavor-placeholders
hsm-peripheral png-to-rgb565
dest=ios/SodaMachine/SodaMachine/FlavorImages
mkdir -p "$dest"
cp images/flavor_1.png images/flavor_2.png images/flavor_3.png images/flavor_4.png "$dest/"
