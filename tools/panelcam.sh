#!/usr/bin/env bash
# panelcam.sh — look at a physical display on the machine, from the shell, without a human.
#
#   tools/panelcam.sh list                 # what AVFoundation can see
#   tools/panelcam.sh shot front           # one frame of the 4.3B, cropped to the panel
#   tools/panelcam.sh shot faucet          # one frame of the 1.47
#   tools/panelcam.sh shot front --full    # the same frame uncropped, to re-aim the rig
#   tools/panelcam.sh auth                 # whether this process may open a camera at all
#   tools/panelcam.sh controls             # what the attached camera lets a program change
#   tools/panelcam.sh get absolute_focus
#   tools/panelcam.sh reset                # unwedge a lens that has stopped moving
#   tools/panelcam.sh set auto_focus 0     # then set absolute_focus, and it stays put
#
# ZOOM IS A CROP AND FOCUS IS A CONTROL, and they are not the same kind of thing. macOS
# AVFoundation publishes neither: `lensPosition`, `videoZoomFactor` and every
# `isFocusModeSupported` come back unavailable or false on this platform, so nothing Apple
# offers moves a lens. UVC control transfers do, and `panelcam-uvc/uvc.js` carries them — which
# is why focus and exposure are set through `set` and zoom is not. Framing is bought in sensor
# pixels once and spent per shot in `--crop`, so it costs no motor and cannot drift.
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
# THE FRAME IS TAKEN BY AN APP, BECAUSE ONLY AN APP MAY TAKE IT. macOS grants the camera to a
# process it can raise a prompt for, and a shell is not one: ffmpeg here blocks forever on a
# dialog nobody can answer. `panelcam-shot/PanelCamShot.app` is a bundle TCC can name, launched
# through `open` so launchd is the responsible process — it opens the camera, writes a PNG and
# exits, and this reads the file. The permission belongs to the app; this shell never needs it.
# `auth` still reports the shell's own state, which stays notDetermined and no longer matters.

set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONF="$HERE/panelcam.targets.conf"
OUT_DIR="${PANELCAM_OUT:-$HERE/../.panelcam}"
APP="$HERE/panelcam-shot/PanelCamShot.app"

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
  awk -v t="$1" -v f="$2" '$1==t && $2==f {
        v = ""; for (i = 3; i <= NF; i++) v = v (i > 3 ? " " : "") $i; print v; found = 1
      } END {exit !found}' "$CONF" ||
    die "target '$1' has no '$2' in $(basename "$CONF")"
}

# Control goes to the camera's own unit ids, read from its descriptors. `uvcc` guesses those ids
# and every control on the ELP stalls; uvc.js reads them and every control answers.
uvc() { node "$HERE/panelcam-uvc/uvc.js" "$@"; }

cmd_controls() {
  # The one command that settles what a camera actually implements, with each value and its
  # range. A module advertising autofocus may or may not publish absolute_focus.
  uvc show
}

# THE LENS CAN WEDGE, and it does not report that it has. absolute_focus goes on reading back
# whatever was last written while the actuator sits where it stopped, autofocus cannot move it
# either, and a whole focus sweep comes back flat — every position equally soft, background
# included. Re-enumerating the device frees it. The camera returns on a new AVFoundation index,
# which is why a target names its camera rather than numbering it.
cmd_reset() {
  node -e '
    const usb = require("usb");
    const d = usb.getDeviceList().find(x => x.deviceDescriptor.idVendor === 0x32e4);
    if (!d) { console.error("no ELP camera on the bus"); process.exit(1); }
    d.open();
    d.reset(err => {
      console.log(err ? "reset failed: " + err.message : "usb reset ok — settings are back to defaults");
      try { d.close(); } catch (e) {}
      process.exit(err ? 1 : 0);
    });
  ' --experimental-default-type=commonjs 2>/dev/null ||
  (cd "$HERE/panelcam-uvc" && node -e '
    const usb = require("usb");
    const d = usb.getDeviceList().find(x => x.deviceDescriptor.idVendor === 0x32e4);
    if (!d) { console.error("no ELP camera on the bus"); process.exit(1); }
    d.open();
    d.reset(err => {
      console.log(err ? "reset failed: " + err.message : "usb reset ok — settings are back to defaults");
      try { d.close(); } catch (e) {}
      process.exit(err ? 1 : 0);
    });
  ')
}

cmd_get() { uvc get "${1:?usage: panelcam.sh get <control>}"; }

cmd_set() {
  uvc set "${1:?usage: panelcam.sh set <control> <value>}" \
          "${2:?usage: panelcam.sh set <control> <value>}"
}

target_field_opt() { target_field "$1" "$2" 2>/dev/null || true; }

LOGFILE="$HOME/.panelcam-shot.log"

# `open --args` drops empty strings and silently shifts every argument after them, so an absent
# option is passed as "-" rather than "".
take_frame() {
  : > "$LOGFILE"
  open -W "$APP" --args "$1" "$2" "$3" "${4:--}" video - "${5:-12}"
}

# THE CAMERA FORGETS. UVC controls live in the device and not in a profile: a replug or a power
# cycle puts every one back to auto, which is precisely the setting that cannot read a screen.
# Applying the target's own numbers before each frame is what makes two shots a week apart
# comparable, and costs one control transfer each.
apply_uvc() {
  local pairs kv key val moved=0
  pairs="$(target_field_opt "$1" uvc)"
  [ -n "$pairs" ] || return 0
  for kv in $pairs; do
    key="${kv%%=*}"; val="${kv#*=}"
    # WRITE EVERY TIME, and never skip on a matching read. absolute_focus reads back the number
    # last asked for, not where the lens is standing: opening a capture session moves it and
    # leaves the register saying 480 over a lens that is somewhere else. A frame taken on that
    # agreement is soft, and the control that would have fixed it is the one being skipped.
    uvc set "$key" "$val" >/dev/null || die "could not set $key"
    [ "$key" = absolute_focus ] && moved=1
  done
  # THE LENS IS A MOTOR. A frame grabbed the instant after the write records the position the
  # lens is leaving, not the one asked for — which reads as a camera that cannot focus.
  [ "$moved" -eq 1 ] && sleep 2
  return 0
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

  local match warmup raw
  match="$(target_field "$target" match)"
  warmup="$(target_field "$target" warmup)"
  crop="${crop_override:-$(target_field "$target" crop)}"

  [ -d "$APP" ] || die "no $APP — build it once with panelcam-shot/build.sh"

  # A dark panel photographs as an unlit rectangle; the machine is told a finger landed.
  local wake_port; wake_port="$(target_field_opt "$target" wake)"
  [ -n "$wake_port" ] && python3 "$HERE/panelcam-wake.py" "$wake_port" >/dev/null 2>&1 || true

  mkdir -p "$OUT_DIR"
  out="${out:-$OUT_DIR/$target.png}"
  raw="$OUT_DIR/$target.raw.png"
  rm -f "$raw"

  apply_uvc "$target"

  # `open` returns when the app exits and forwards no output, so the app keeps its own log.
  # Settings go in before the stream: this camera moves the lens when a session opens and will
  # not hold a focus value through one, which is why the app keeps the sharpest frame it sees
  # rather than trusting any single one.
  local preset candidates
  preset="$(target_field_opt "$target" preset)"
  candidates="$(target_field_opt "$target" candidates)"
  take_frame "$raw" "$match" "$warmup" "$preset" "$candidates"

  # THE LENS WEDGES, AND A WEDGED LENS IS SILENT. It parks away from focus and stops hunting,
  # so every candidate in the sweep is equally soft and the frame comes back looking like a
  # camera that simply cannot focus. Re-enumerating frees it. The app reports the sharpness it
  # kept, which makes the condition testable rather than a thing to notice by eye — and after a
  # reset the same scene scored 0.129 where the wedged pass scored 0.004.
  local best; best="$(sed -n 's/.*best=\([0-9.]*\).*/\1/p' "$LOGFILE" 2>/dev/null | tail -1)"
  if [ -n "$best" ] && awk -v b="$best" 'BEGIN { exit !(b < 0.02) }'; then
    cmd_reset >/dev/null 2>&1 || true
    apply_uvc "$target"
    take_frame "$raw" "$match" "$warmup" "$preset" "$candidates"
  fi

  [ -f "$raw" ] || die "no frame — $(tail -1 "$HOME/.panelcam-shot.log" 2>/dev/null || echo 'the app wrote no log')"

  if [ "$full" -eq 1 ]; then
    mv "$raw" "$out"
  else
    ffmpeg -hide_banner -loglevel error -i "$raw" -vf "crop=$crop" -y "$out"
    rm -f "$raw"
  fi

  echo "$out"
}

case "${1:-}" in
  list)     shift; cmd_list "$@" ;;
  controls) shift; cmd_controls "$@" ;;
  get)      shift; cmd_get "$@" ;;
  reset)    shift; cmd_reset "$@" ;;
  set)      shift; cmd_set "$@" ;;
  shot)     shift; cmd_shot "$@" ;;
  auth)     shift; cmd_auth "$@" ;;
  ask)      shift; cmd_ask "$@" ;;
  *) sed -n '2,33p' "${BASH_SOURCE[0]}" | sed 's/^# \{0,1\}//'; exit 1 ;;
esac
