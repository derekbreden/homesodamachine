#!/usr/bin/env bash
# Package the source flavor portraits for firmware and copy their iOS demo artwork.
set -euo pipefail
cd "$(dirname "$0")/.."
hsm-marketing make-logos -o .pio/build/esp32s3_front/logos.bin
mkdir -p .pio/build/esp32s3_faucet
cp .pio/build/esp32s3_front/logos.bin .pio/build/esp32s3_faucet/logos.bin
hsm-marketing make-logos --store -o .pio/build/esp32s3_faucet/logos-store.bin
dest=ios/SodaMachine/SodaMachine/FlavorImages
mkdir -p "$dest"
cp images/flavor_1.png images/flavor_2.png images/flavor_3.png images/flavor_4.png "$dest/"
