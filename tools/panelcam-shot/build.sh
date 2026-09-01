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
# The signature is ad-hoc, so it is the binary's own hash. Rebuilding changes it, macOS sees a
# different app, and the grant has to be given again — expected, and the reason this script is
# not run on every capture.

set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APP="$HERE/PanelCamShot.app"

rm -rf "$APP"
mkdir -p "$APP/Contents/MacOS"
cp "$HERE/Info.plist" "$APP/Contents/Info.plist"
swiftc -O "$HERE/main.swift" -o "$APP/Contents/MacOS/PanelCamShot"
codesign --force --sign - "$APP"

echo "built $APP"
echo "first run raises the camera prompt; answer it once:"
echo "  open -W \"$APP\" --args /tmp/panelcam-probe.png 16MP 20"
