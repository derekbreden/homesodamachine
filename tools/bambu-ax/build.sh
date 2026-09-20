#!/usr/bin/env bash
# build.sh — compile bambu-ax, which drives Bambu Connect without taking the screen.
#
#   tools/bambu-ax/build.sh          # writes the bambu-ax binary beside this script
#
# NO BUNDLE IS NEEDED HERE, unlike panelcam-shot. Accessibility trust is inherited from the
# process that runs the binary, so the grant already held by the shell carries over. A bare
# binary is the right shape.
#
# THE SCREEN IS WHAT THIS BUYS. Bambu Connect is Electron, and AXManualAccessibility exposes its
# Chromium tree to AXUIElementPerformAction, which presses a control where it stands. Synthesized
# input cannot: CGEvent delivery to .cghidEventTap follows the frontmost application, so a click
# costs the screen and every step after it.
set -euo pipefail
here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
swiftc -O "$here/main.swift" -o "$here/bambu-ax"
echo "built $here/bambu-ax"
