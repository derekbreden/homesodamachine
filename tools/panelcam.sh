#!/usr/bin/env bash
# panelcam.sh — read a physical display on the machine, from the shell, without a human.
#
#   tools/panelcam.sh shot front           # the 4.3B panel on its own 800x480 grid, 3 px per panel px
#   tools/panelcam.sh shot front --full    # the frame as the camera delivered it
#   tools/panelcam.sh aim front            # find the panel's corners in a full frame and write them
#   tools/panelcam.sh list                 # cameras, and the sizes the attached one streams
#   tools/panelcam.sh controls             # what the camera lets a program change
#   tools/panelcam.sh get absolute_focus
#   tools/panelcam.sh set gain 0
#   tools/panelcam.sh reset                # re-enumerate the camera; its controls return to their defaults
#
# A TARGET IS A CAMERA, A RECTANGLE, AND A FOCUS RANGE. `targets.conf` fixes them per display, so
# two shots an hour apart are the same picture of the same thing and can be compared.
#
# THE FRAME IS TAKEN BY AN APP, BECAUSE ONLY AN APP MAY TAKE ONE. macOS grants the camera to a
# process it can raise a prompt for, and a shell is not one. `panelcam-shot/PanelCamShot.app` holds
# the grant, writes a PNG, and exits; this lays the file onto the panel's grid, which needs no
# permission.
#
# THE PICTURE IS THE PANEL'S OWN GRID. A shot is the frame warped, in one projective resampling,
# from the quadrilateral the panel occupies onto its 800x480 pixel grid at `scale` px per panel px:
# a rotated or keystoned panel comes out square, and output pixel (3i+k, 3j+l) is a piece of panel
# pixel (i, j). `panelcam-rectify.py` says what that keeps.

set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONF="$HERE/panelcam.targets.conf"
OUT_DIR="${PANELCAM_OUT:-$HERE/../.panelcam}"
APP="$HERE/panelcam-shot/PanelCamShot.app"
LOGFILE="$HOME/.panelcam-shot.log"
UVC_JS="$HERE/panelcam-uvc/uvc.js"
RECTIFY="$HERE/panelcam-rectify.py"
PY="$HERE/cad-venv/bin/python"

die() { echo "panelcam: $*" >&2; exit 1; }

uvc() { node "$UVC_JS" "$@"; }

cmd_controls() { uvc show; }
cmd_get() { uvc get "${1:?usage: panelcam.sh get <control>}"; }
cmd_set() { uvc set "${1:?usage: panelcam.sh set <control> <value>}" "${2:?usage: panelcam.sh set <control> <value>}"; }

# A USB reset is the one thing that returns every control to the camera's own default. The camera
# comes back on a new index, which is why a target names it.
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

take_frame() {   # out, target, [score-rect], [extra control=value …]
  local t="$2" dwell uvc score
  dwell="$(target_field_opt "$t" dwell)"; dwell="${dwell:-0.3}"
  score="${3:-$(target_field "$t" score)}"
  # The conf separates control=value pairs with spaces; the app takes one comma-joined argument.
  uvc="$(target_field "$t" uvc | tr -s ' ' ',')"
  [ -n "${4:-}" ] && uvc="$uvc,$4"
  : > "$LOGFILE"
  open -W "$APP" --args \
    --out "$1" \
    --match "$(target_field "$t" match)" \
    --format "$(target_field "$t" format)" \
    ${score:+--score "$score"} \
    --focus-range "$(target_field "$t" focus-range)" \
    --dwell "$dwell" \
    --max "$(target_field_opt "$t" max || true)" \
    --uvc "$uvc" \
    --uvc-node "$(command -v node)" \
    --uvc-js "$UVC_JS" >/dev/null 2>&1 || true
}

best_score() { sed -n 's/.*best=\([0-9.]*\) of.*/\1/p' "$LOGFILE" 2>/dev/null | tail -1; }

cmd_shot() {
  local target="${1:-}"; shift || true
  [ -n "$target" ] || die "usage: panelcam.sh shot <target> [--full] [--out FILE]"

  local full=0 out=""
  while [ $# -gt 0 ]; do
    case "$1" in
      --full) full=1; shift ;;
      --out)  out="${2:?--out needs a path}"; shift 2 ;;
      *) die "unknown option $1" ;;
    esac
  done

  [ -d "$APP" ] || die "no $APP — build it once with panelcam-shot/build.sh"

  local corners panel scale
  corners="$(target_field "$target" corners)"; panel="$(target_field "$target" panel)"; scale="$(target_field "$target" scale)"
  local floor; floor="$(target_field_opt "$target" floor)"; floor="${floor:-0.02}"

  # A dark panel photographs as an unlit rectangle; the machine is told a finger landed.
  local wake_port; wake_port="$(target_field_opt "$target" wake)"
  [ -n "$wake_port" ] && python3 "$HERE/panelcam-wake.py" "$wake_port" >/dev/null 2>&1 || true

  mkdir -p "$OUT_DIR"
  out="${out:-$OUT_DIR/$target.png}"
  local raw="$OUT_DIR/$target.raw.png"
  rm -f "$raw"

  take_frame "$raw" "$target"

  # A sweep that comes back soft is a panel that was dark or a rig that has moved. The panel is woken
  # again and the shot taken once more; the second answer stands.
  local best; best="$(best_score)"
  if [ -z "$best" ] || awk -v b="${best:-0}" -v f="$floor" 'BEGIN { exit !(b < f) }'; then
    [ -n "$wake_port" ] && python3 "$HERE/panelcam-wake.py" "$wake_port" >/dev/null 2>&1 || true
    take_frame "$raw" "$target"
    best="$(best_score)"
  fi

  [ -f "$raw" ] || die "no frame — $(tail -1 "$LOGFILE" 2>/dev/null || echo 'the app wrote no log')"

  if [ "$full" -eq 1 ]; then
    mv "$raw" "$out"
  else
    "$PY" "$RECTIFY" warp "$raw" "$out" --corners "$corners" --panel "$panel" --scale "$scale"
    rm -f "$raw"
  fi

  echo "$out"
  sed -n 's/.*\(focus [0-9].*\)/  \1/p' "$LOGFILE" | tail -1
  awk -v b="${best:-0}" -v f="$floor" 'BEGIN { exit !(b < f) }' &&
    echo "  best $best is under the floor $floor: the panel was dark, or the rig has moved — aim it again" >&2
  return 0
}

# The lit panel's edges are read against the bezel: in the saved PNG at the 16 ms shutter its darkest
# navy reads 29 and up and the glossy bezel 11 to 24; at the 4 ms shutter of a shot the two are 13
# and 10, so the aiming frame is taken at 16 ms.
cmd_aim() {
  local target="${1:-}"
  [ -n "$target" ] || die "usage: panelcam.sh aim <target>"
  mkdir -p "$OUT_DIR"
  local full="$OUT_DIR/$target.full.png"
  local wake_port; wake_port="$(target_field_opt "$target" wake)"
  [ -n "$wake_port" ] && python3 "$HERE/panelcam-wake.py" "$wake_port" >/dev/null 2>&1 || true
  take_frame "$full" "$target" "" "absolute_exposure_time=167"
  [ -f "$full" ] || die "no frame — $(tail -1 "$LOGFILE" 2>/dev/null)"
  local found; found="$("$PY" "$RECTIFY" find "$full")" || die "could not find the panel in $full"
  local corners score tilt
  corners="$(sed -n 's/^corners //p' <<<"$found")"; score="$(sed -n 's/^score //p' <<<"$found")"
  tilt="$(sed -n 's/^tilt //p' <<<"$found")"
  awk -v t="$target" -v s="$score" -v c="$corners" '
    $1 == t && $2 == "score"   { $0 = sprintf("%-7s %-12s %s", t, "score", s) }
    $1 == t && $2 == "corners" { $0 = sprintf("%-7s %-12s %s", t, "corners", c) }
    { print }' "$CONF" > "$CONF.new" && mv "$CONF.new" "$CONF"
  # The proof: laid onto its grid, the panel's pixel lattice lands at `scale` px per panel px.
  local proof="$OUT_DIR/$target.aim.png"
  "$PY" "$RECTIFY" warp "$full" "$proof" --corners "$corners" \
    --panel "$(target_field "$target" panel)" --scale "$(target_field "$target" scale)"
  echo "$full"
  echo "  corners $corners  tilt $tilt deg  -> written to $(basename "$CONF")"
  echo "  $proof: panel pixel $("$PY" "$RECTIFY" grid "$proof" | sed 's/^period //') px at scale $(target_field "$target" scale)"
}

case "${1:-}" in
  list)     shift; cmd_list "$@" ;;
  controls) shift; cmd_controls "$@" ;;
  get)      shift; cmd_get "$@" ;;
  set)      shift; cmd_set "$@" ;;
  reset)    shift; cmd_reset "$@" ;;
  shot)     shift; cmd_shot "$@" ;;
  aim)      shift; cmd_aim "$@" ;;
  *) sed -n '2,19p' "${BASH_SOURCE[0]}" | sed 's/^# \{0,1\}//'; exit 1 ;;
esac
