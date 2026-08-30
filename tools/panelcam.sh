#!/usr/bin/env bash
# panelcam.sh — look at a physical display on the machine, from the shell, without a human.
#
#   tools/panelcam.sh list                 # what AVFoundation can see
#   tools/panelcam.sh shot front           # one frame of the 4.3B, cropped to the panel
#   tools/panelcam.sh shot faucet          # one frame of the 1.47
#   tools/panelcam.sh shot front --full    # the same frame uncropped, to re-aim the rig
#   tools/panelcam.sh auth                 # whether this process may open a camera at all
#   tools/panelcam.sh controls             # what the attached camera lets a program change
#   tools/panelcam.sh set absolute_focus 120
#
# ZOOM IS A CROP AND FOCUS IS A CONTROL, and they are not the same kind of thing. macOS
# AVFoundation publishes neither: `lensPosition`, `videoZoomFactor` and every
# `isFocusModeSupported` come back unavailable or false on this platform, so nothing Apple
# offers moves a lens. UVC control transfers do, and `uvcc` carries them — which is why focus
# and exposure are set through `set` and zoom is not. Framing is bought in sensor pixels once
# and spent per shot in `--crop`, so it costs no motor and cannot drift.
#
# A TARGET IS A CAMERA AND A CROP, and the crop is the point. A photograph of the machine is
# not a reading of its panel: the panel is a tenth of the frame, off-centre, and every shot
# frames it differently. `targets.conf` fixes one camera index and one pixel rectangle per
# display, so the same rectangle comes back every time and two shots taken an hour apart are
# the same picture of the same thing. Re-aim the rig and the rectangle is what you edit.
#
# THE FIRST FRAMES ARE NOT THE PICTURE. AVFoundation hands over frames while auto-exposure is
# still ramping, so `-frames:v 1` returns a black rectangle or a blown one. This discards the
# ramp and keeps a settled frame.
#
# PERMISSION IS THE WHOLE GAME. macOS gates the camera per responsible process, and a shell
# that has never asked sits at notDetermined — where ffmpeg blocks forever on a prompt nobody
# can answer. `auth` reports that state before a capture spends a minute finding it out.

set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONF="$HERE/panelcam.targets.conf"
OUT_DIR="${PANELCAM_OUT:-$HERE/../.panelcam}"
WARMUP="${PANELCAM_WARMUP:-16}"      # frames discarded before the one that is kept

die() { echo "panelcam: $*" >&2; exit 1; }

cmd_auth() {
  local swift_src; swift_src="$(mktemp -t panelcam).swift"
  cat > "$swift_src" <<'EOF'
import AVFoundation
let names = [0: "notDetermined", 1: "restricted", 2: "denied", 3: "authorized"]
print(names[AVCaptureDevice.authorizationStatus(for: .video).rawValue] ?? "unknown")
EOF
  local status; status="$(swift "$swift_src" 2>/dev/null | tail -1)"
  rm -f "$swift_src"
  echo "${status:-unknown}"
}

require_auth() {
  local s; s="$(cmd_auth)"
  [ "$s" = authorized ] && return 0
  cat >&2 <<EOF
panelcam: camera access is '$s' for this process — a capture would hang, not fail.

  System Settings > Privacy & Security > Camera, and enable the app running this shell.
  An app appears in that list only after it has asked once; 'tools/panelcam.sh ask' asks.
EOF
  exit 2
}

cmd_ask() {
  # Open a capture session for its side effect: macOS raises the prompt against this process.
  local swift_src; swift_src="$(mktemp -t panelcam).swift"
  cat > "$swift_src" <<'EOF'
import AVFoundation
let sem = DispatchSemaphore(value: 0)
AVCaptureDevice.requestAccess(for: .video) { ok in
  print(ok ? "authorized" : "denied"); sem.signal()
}
_ = sem.wait(timeout: .now() + 120)
EOF
  swift "$swift_src"; rm -f "$swift_src"
}

cmd_list() {
  # Listing devices is an error path in ffmpeg — it enumerates, then fails to open "".
  { ffmpeg -hide_banner -f avfoundation -list_devices true -i "" 2>&1 || true; } |
    sed -n '/video devices/,/audio devices/p' | sed 's/^\[[^]]*\] //' | grep -v 'audio devices'
}

target_field() {   # target field -> value
  [ -f "$CONF" ] || die "no $CONF — copy panelcam.targets.conf.example and aim the rig"
  awk -v t="$1" -v f="$2" '$1==t && $2==f {print $3; found=1} END {exit !found}' "$CONF" ||
    die "target '$1' has no '$2' in $(basename "$CONF")"
}

uvcc() { npx --yes uvcc "$@"; }

cmd_controls() {
  # The one command that settles what a camera actually implements. A module advertising
  # autofocus may or may not publish absolute_focus; this is the answer, not the listing.
  uvcc export
}

cmd_set() {
  local control="${1:?usage: panelcam.sh set <control> <value>}"
  local value="${2:?usage: panelcam.sh set <control> <value>}"
  uvcc set "$control" "$value"
  uvcc get "$control"
}

cmd_shot() {
  local target="${1:-}"; shift || true
  [ -n "$target" ] || die "usage: panelcam.sh shot <target> [--full] [--out FILE]"

  local full=0 out="" crop_override=""
  while [ $# -gt 0 ]; do
    case "$1" in
      --full) full=1; shift ;;
      --out)  out="${2:?--out needs a path}"; shift 2 ;;
      --crop) crop_override="${2:?--crop needs w:h:x:y}"; shift 2 ;;
      *) die "unknown option $1" ;;
    esac
  done

  require_auth

  local device size crop
  device="$(target_field "$target" device)"
  size="$(target_field "$target" size)"
  crop="${crop_override:-$(target_field "$target" crop)}"

  mkdir -p "$OUT_DIR"
  out="${out:-$OUT_DIR/$target.png}"

  local vf="select=gte(n\\,$WARMUP)"
  [ "$full" -eq 1 ] || vf="$vf,crop=$crop"

  ffmpeg -hide_banner -loglevel error \
    -f avfoundation -framerate 30 -video_size "$size" -i "$device" \
    -vf "$vf" -vsync 0 -frames:v 1 -y "$out"

  echo "$out"
}

case "${1:-}" in
  list)     shift; cmd_list "$@" ;;
  controls) shift; cmd_controls "$@" ;;
  set)      shift; cmd_set "$@" ;;
  shot)     shift; cmd_shot "$@" ;;
  auth)     shift; cmd_auth "$@" ;;
  ask)      shift; cmd_ask "$@" ;;
  *) sed -n '2,33p' "${BASH_SOURCE[0]}" | sed 's/^# \{0,1\}//'; exit 1 ;;
esac
