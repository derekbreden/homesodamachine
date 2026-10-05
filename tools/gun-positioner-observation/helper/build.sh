#!/usr/bin/env bash
# build.sh — assemble GPOCapture.app, the process that holds this toolkit's camera permission.
#
#   tools/gun-positioner-observation/helper/build.sh           # stable signing identity if one exists
#   tools/gun-positioner-observation/helper/build.sh --adhoc   # ad-hoc signature (tests; no keychain use)
#
# Output: helper/build/GPOCapture.app (ignored by git). As with tools/panelcam-shot, macOS grants
# camera access to an app bundle with NSCameraUsageDescription, launched through LaunchServices
# (`open`); a shell-launched binary is attributed to the terminal application instead. A
# Developer ID or Apple Development identity keeps the grant across rebuilds; an ad-hoc
# signature changes every build, so macOS asks again.

set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APP="$HERE/build/GPOCapture.app"

IDENTITY=""
if [ "${1:-}" != "--adhoc" ]; then
  IDENTITY="$(security find-identity -v -p codesigning 2>/dev/null \
    | awk -F'"' '/Developer ID Application/{print $2; exit}')" || true
  [ -n "$IDENTITY" ] || IDENTITY="$(security find-identity -v -p codesigning 2>/dev/null \
    | awk -F'"' '/Apple Development/{print $2; exit}')" || true
fi

rm -rf "$APP"
mkdir -p "$APP/Contents/MacOS"
cp "$HERE/Info.plist" "$APP/Contents/Info.plist"
swiftc -O "$HERE/main.swift" -o "$APP/Contents/MacOS/GPOCapture"

if [ -n "$IDENTITY" ]; then
  codesign --force --timestamp=none --sign "$IDENTITY" "$APP"
  echo "built $APP, signed as: $IDENTITY"
else
  codesign --force --sign - "$APP"
  echo "built $APP (ad-hoc signature; macOS asks for camera access again after each rebuild)"
fi
