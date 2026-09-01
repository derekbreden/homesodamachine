#!/usr/bin/env bash
# build.sh — assemble PanelCamShot.app, the one process on this machine allowed to open the camera.
#
#   tools/panelcam-shot/build.sh          # writes PanelCamShot.app beside this script
#
# THE BUNDLE IS THE POINT, not the code inside it. macOS grants camera access to a process it can
# name and show a prompt for, and a bare CLI binary is neither: `AVCaptureDevice.requestAccess`
# from a shell returns denied instantly, raises no dialog, and leaves the status at
# notDetermined — the app never reaches System Settings > Privacy & Security > Camera, and that
# list has no way to add one by hand. An .app with `NSCameraUsageDescription` in its Info.plist
# is something TCC can attribute, so the prompt appears and the answer sticks.
#
# LAUNCH IT WITH `open`, NOT BY PATH. Exec the binary from a shell and TCC blames the shell's
# host application — the same unpromptable process as before, and the same instant denial.
# Under `open`, launchd is the responsible process and the bundle answers for itself.
#
# SIGN WITH A STABLE IDENTITY SO THE GRANT SURVIVES A REBUILD. TCC keys the camera permission to
# the code's designated requirement. An ad-hoc signature is the binary's own hash, so every
# rebuild is a new identity and a fresh prompt — which is why approving this once was never once.
# A Development (or Developer ID) certificate keys the requirement to the team and bundle id
# instead, both of which hold across rebuilds, so the grant is given a single time. This picks up
# such an identity from the login keychain automatically and falls back to ad-hoc only when there
# is none — in which case the every-rebuild reprompt returns.

set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APP="$HERE/PanelCamShot.app"

# First code-signing identity in the keychain: a Developer ID Application if present, else an
# Apple Development cert. Either is stable across rebuilds; both beat ad-hoc here.
IDENTITY="$(security find-identity -v -p codesigning 2>/dev/null \
  | awk -F'"' '/Developer ID Application/{print $2; found=1} END{exit !found}')" || \
IDENTITY="$(security find-identity -v -p codesigning 2>/dev/null \
  | awk -F'"' '/Apple Development/{print $2; exit}')" || true

rm -rf "$APP"
mkdir -p "$APP/Contents/MacOS"
cp "$HERE/Info.plist" "$APP/Contents/Info.plist"
swiftc -O "$HERE/main.swift" -o "$APP/Contents/MacOS/PanelCamShot"

if [ -n "${IDENTITY:-}" ]; then
  codesign --force --timestamp=none --sign "$IDENTITY" "$APP"
  echo "built $APP"
  echo "signed as: $IDENTITY"
  echo "the grant survives rebuilds; you are prompted only the first time this identity is used."
else
  codesign --force --sign - "$APP"
  echo "built $APP (ad-hoc: no signing identity found)"
  echo "WARNING: ad-hoc signature changes every build, so macOS reprompts for the camera each rebuild."
fi
echo "first run raises the camera prompt if the identity is new; answer it once:"
echo "  open -W \"$APP\" --args --out /tmp/panelcam-probe.png --match 16MP --mode probe"
