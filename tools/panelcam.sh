#!/usr/bin/env bash
# panelcam.sh — read a physical display on the machine, from the shell, without a human.
#
#   tools/panelcam.sh shot front           # the 4.3B panel, cropped, at 3.6 camera px per panel px
#   tools/panelcam.sh shot front --full    # the same frame uncropped, to re-aim the rig
#   tools/panelcam.sh list                 # cameras, and the sizes the attached one streams
#   tools/panelcam.sh controls             # what the camera lets a program change
#   tools/panelcam.sh get absolute_focus
#   tools/panelcam.sh set gain 0
#   tools/panelcam.sh reset                # re-enumerate a camera whose lens has stopped moving
#
# A TARGET IS A CAMERA, A RECTANGLE, AND A FOCUS RANGE. `targets.conf` fixes them per display, so
# two shots an hour apart are the same picture of the same thing and can be compared.
#
# THE FRAME IS TAKEN BY AN APP, BECAUSE ONLY AN APP MAY TAKE ONE. macOS grants the camera to a
# process it can raise a prompt for, and a shell is not one. `panelcam-shot/PanelCamShot.app` holds
# the grant, writes a PNG, and exits; this crops the file, which needs no permission.

set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONF="$HERE/panelcam.targets.conf"
OUT_DIR="${PANELCAM_OUT:-$HERE/../.panelcam}"
APP="$HERE/panelcam-shot/PanelCamShot.app"
LOGFILE="$HOME/.panelcam-shot.log"
UVC_JS="$HERE/panelcam-uvc/uvc.js"

die() { echo "panelcam: $*" >&2; exit 1; }

uvc() { node "$UVC_JS" "$@"; }

cmd_controls() { uvc show; }
cmd_get() { uvc get "${1:?usage: panelcam.sh get <control>}"; }
cmd_set() { uvc set "${1:?usage: panelcam.sh set <control> <value>}" "${2:?usage: panelcam.sh set <control> <value>}"; }

# The lens can stop answering: every focus value gives the same soft frame, and re-enumerating the
# device is what frees it. The camera comes back on a new index, which is why a target names it.
cmd_reset() {
  node -e '
    const usb = require("usb");
    const d = usb.getDeviceList().find(x => x.deviceDescriptor.idVendor === 0x32e4);
    if (!d) { console.error("no ELP camera on the bus"); process.exit(1); }
    d.open();
    d.reset(err => {
      console.log(err ? "reset failed: " + err.message : "usb reset ok — controls are back to defaults");
      try { d.close(); } catch (e) {}
      process.exit(err ? 1 : 0);
    });
  ' 2>/dev/null || (cd "$HERE/panelcam-uvc" && node -e '
    const usb = require("usb");
    const d = usb.getDeviceList().find(x => x.deviceDescriptor.idVendor === 0x32e4);
    if (!d) { console.error("no ELP camera on the bus"); process.exit(1); }
    d.open();
    d.reset(err => {
      console.log(err ? "reset failed: " + err.message : "usb reset ok — controls are back to defaults");
      try { d.close(); } catch (e) {}
      process.exit(err ? 1 : 0);
    });
  ')
}

cmd_list() {
  { ffmpeg -hide_banner -f avfoundation -list_devices true -i "" 2>&1 || true; } |
    sed -n '/video devices/,/audio devices/p' | sed 's/^\[[^]]*\] //' | grep -v 'audio devices'
  [ -d "$APP" ] || return 0
  : > "$LOGFILE"
  open -W "$APP" --args --list --match "$(target_field_opt front match)" >/dev/null 2>&1 || true
  sed -n 's/^[^ ]*  \( *[0-9]*x[0-9]* .*\)/\1/p' "$LOGFILE"
}

target_field() {
  [ -f "$CONF" ] || die "no $CONF"
  awk -v t="$1" -v f="$2" '$1==t && $2==f {
        v = ""; for (i = 3; i <= NF; i++) v = v (i > 3 ? " " : "") $i; print v; found = 1
      } END {exit !found}' "$CONF" ||
    die "target '$1' has no '$2' in $(basename "$CONF")"
}
target_field_opt() { target_field "$1" "$2" 2>/dev/null || true; }

take_frame() {   # out, target
  local t="$2" dwell uvc
  dwell="$(target_field_opt "$t" dwell)"; dwell="${dwell:-0.5}"
  # The conf separates control=value pairs with spaces; the app takes one comma-joined argument.
  uvc="$(target_field "$t" uvc | tr -s ' ' ',')"
  : > "$LOGFILE"
  open -W "$APP" --args \
    --out "$1" \
    --match "$(target_field "$t" match)" \
    --format "$(target_field "$t" format)" \
    --score "$(target_field "$t" score)" \
    --focus-range "$(target_field "$t" focus-range)" \
    --settle "$dwell" \
    --target "$(target_field_opt "$t" target || true)" \
    --max "$(target_field_opt "$t" max || true)" \
    --uvc "$uvc" \
    --uvc-node "$(command -v node)" \
    --uvc-js "$UVC_JS" >/dev/null 2>&1 || true
}

best_score() { sed -n 's/.*best=\([0-9.]*\) of.*/\1/p' "$LOGFILE" 2>/dev/null | tail -1; }

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

  [ -d "$APP" ] || die "no $APP — build it once with panelcam-shot/build.sh"

  local crop; crop="${crop_override:-$(target_field "$target" crop)}"
  local floor; floor="$(target_field_opt "$target" floor)"; floor="${floor:-0.02}"

  # A dark panel photographs as an unlit rectangle; the machine is told a finger landed.
  local wake_port; wake_port="$(target_field_opt "$target" wake)"
  [ -n "$wake_port" ] && python3 "$HERE/panelcam-wake.py" "$wake_port" >/dev/null 2>&1 || true

  mkdir -p "$OUT_DIR"
  out="${out:-$OUT_DIR/$target.png}"
  local raw="$OUT_DIR/$target.raw.png"
  rm -f "$raw"

  take_frame "$raw" "$target"

  # A whole focus sweep that comes back soft is a lens that has stopped moving, not a scene without
  # detail. Re-enumerating frees it; the same panel scores 0.003 wedged and 0.05 after.
  local best; best="$(best_score)"
  if [ -z "$best" ] || awk -v b="${best:-0}" -v f="$floor" 'BEGIN { exit !(b < f) }'; then
    cmd_reset >/dev/null 2>&1 || true
    [ -n "$wake_port" ] && python3 "$HERE/panelcam-wake.py" "$wake_port" >/dev/null 2>&1 || true
    take_frame "$raw" "$target"
    best="$(best_score)"
  fi

  [ -f "$raw" ] || die "no frame — $(tail -1 "$LOGFILE" 2>/dev/null || echo 'the app wrote no log')"

  if [ "$full" -eq 1 ]; then
    mv "$raw" "$out"
  else
    ffmpeg -hide_banner -loglevel error -i "$raw" -vf "crop=$crop" -y "$out"
    rm -f "$raw"
  fi

  echo "$out"
  sed -n 's/.*\(focus bracket .*\)/  \1/p' "$LOGFILE" | tail -1
}

case "${1:-}" in
  list)     shift; cmd_list "$@" ;;
  controls) shift; cmd_controls "$@" ;;
  get)      shift; cmd_get "$@" ;;
  set)      shift; cmd_set "$@" ;;
  reset)    shift; cmd_reset "$@" ;;
  shot)     shift; cmd_shot "$@" ;;
  *) sed -n '2,18p' "${BASH_SOURCE[0]}" | sed 's/^# \{0,1\}//'; exit 1 ;;
esac
