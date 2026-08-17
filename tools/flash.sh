#!/usr/bin/env bash
#
# Flash wrapper that pauses the serial logger during upload.
#
# Usage:
#   ./tools/flash.sh pcba_bench        # flash the pcba controller board's bring-up console
#   ./tools/flash.sh esp32s3_front     # flash ESP32-S3 4.3B front-face display
#   ./tools/flash.sh esp32s3_faucet    # flash ESP32-S3 faucet display
#   ./tools/flash.sh prototype         # flash the under-counter prototype's ESP32
#   ./tools/flash.sh esp32s3_config    # flash the prototype's ESP32-S3 config display
#   ./tools/flash.sh rp2040_display    # flash the prototype's RP2040 display
#
# Also supports build-only (no upload):
#   ./tools/flash.sh pcba_bench build  # build only, no flash
#

set -e

PAUSE_FILE="/tmp/serial_logger_pause"

if [ -z "$1" ]; then
    echo "Usage: $0 <env> [build]"
    echo "  Environments: pcba_bench, esp32s3_front, esp32s3_faucet, prototype, esp32s3_config, rp2040_display"
    echo "  Add 'build' to build without flashing"
    exit 1
fi

ENV="$1"
BUILD_ONLY="${2:-}"

# Pre-flight: RP2040 USB doesn't enumerate while UART is connected to ESP32.
if [ "$ENV" = "rp2040_display" ] && [ "$BUILD_ONLY" != "build" ]; then
    echo "Note: RP2040 USB does not enumerate while its UART is wired to the ESP32."
    echo "      Disconnect the UART line before flashing, then reconnect afterward."
fi

# Pre-flight: prototype and esp32s3_config depend on a sibling PersistentLog repo
# (referenced as symlink://\${PROJECT_DIR}/../PersistentLog in platformio.ini).
# pio's lib_deps error for this is opaque, so check explicitly.
if [ "$ENV" = "prototype" ] || [ "$ENV" = "esp32s3_config" ]; then
    PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
    if [ ! -d "$PROJECT_DIR/../PersistentLog" ]; then
        echo "Error: missing dependency at $PROJECT_DIR/../PersistentLog" >&2
        echo "       platformio.ini expects PersistentLog as a sibling directory." >&2
        echo "       Place or symlink the PersistentLog repo at that path before flashing." >&2
        exit 1
    fi
fi

# Pause the serial logger
pause_logger() {
    touch "$PAUSE_FILE"
    sleep 0.5  # give logger time to release ports
}

# Resume the serial logger
resume_logger() {
    rm -f "$PAUSE_FILE"
}

# Always resume logger on exit (even on failure)
trap resume_logger EXIT

if [ "$BUILD_ONLY" = "build" ]; then
    echo "Building $ENV..."
    pio run -e "$ENV"
else
    echo "Pausing serial logger..."
    pause_logger

    echo "Building and flashing $ENV..."
    pio run -e "$ENV" -t upload

    echo "Serial logger will resume automatically."
fi
