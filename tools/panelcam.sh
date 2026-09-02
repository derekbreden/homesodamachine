#!/usr/bin/env bash
# panelcam.sh — read a physical display on the machine, from the shell, without a human.
#
#   tools/panelcam.sh shot front           # the 4.3B panel on its own 800x480 grid, 3 px per panel px;
#                                          #   beside it the same at one px per panel px, and that with
#                                          #   every pixel the camera reads as a palette colour so drawn
#   tools/panelcam.sh shot front --full    # the frame as the camera delivered it
#   tools/panelcam.sh aim front            # put the test screen up, read the panel's corners, write them
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
# pixel (i, j). `<target>.panel.png` beside it is the mean of each such block: one pixel per panel
# pixel, the frame as the camera read it; `<target>.palette.png` is that picture with every pixel the
# camera reads as one of the firmware's palette colours drawn in that colour, which an aim learns from
# the test screen. `panelcam-rectify.py` says what the warp keeps and how a colour is read.

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
# In a subshell of its own: target_field's die exits the shell it runs in, and
# under set -e that would be this script rather than the field.
target_field_opt() { ( target_field "$1" "$2" ) 2>/dev/null || true; }

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
  local console; console="$(target_field_opt "$target" console)"
  [ -n "$console" ] && python3 "$HERE/panelcam-wake.py" "$console" >/dev/null 2>&1 || true

  mkdir -p "$OUT_DIR"
  out="${out:-$OUT_DIR/$target.png}"
  local raw="$OUT_DIR/$target.raw.png"
  rm -f "$raw"

  take_frame "$raw" "$target"

  # A sweep that comes back soft is a panel that was dark or a rig that has moved. The panel is woken
  # again and the shot taken once more; the second answer stands.
  local best; best="$(best_score)"
  if [ -z "$best" ] || awk -v b="${best:-0}" -v f="$floor" 'BEGIN { exit !(b < f) }'; then
    [ -n "$console" ] && python3 "$HERE/panelcam-wake.py" "$console" >/dev/null 2>&1 || true
    take_frame "$raw" "$target"
    best="$(best_score)"
  fi

  [ -f "$raw" ] || die "no frame — $(tail -1 "$LOGFILE" 2>/dev/null || echo 'the app wrote no log')"

  if [ "$full" -eq 1 ]; then
    mv "$raw" "$out"
  else
    "$PY" "$RECTIFY" warp "$raw" "$out" --corners "$corners" --panel "$panel" --scale "$scale"
    "$PY" "$RECTIFY" reduce "$out" "${out%.png}.panel.png" --scale "$scale"
    local palette; palette="$(target_field_opt "$target" palette)"
    [ -n "$palette" ] && "$PY" "$RECTIFY" classify "${out%.png}.panel.png" "${out%.png}.palette.png" --palette "$palette" >/dev/null
    rm -f "$raw"
  fi

  echo "$out"
  [ "$full" -eq 1 ] || { echo "${out%.png}.panel.png"; [ -n "${palette:-}" ] && echo "${out%.png}.palette.png"; }
  sed -n 's/.*\(focus [0-9].*\)/  \1/p' "$LOGFILE" | tail -1
  awk -v b="${best:-0}" -v f="$floor" 'BEGIN { exit !(b < f) }' &&
    echo "  best $best is under the floor $floor: the panel was dark, or the rig has moved — aim it again" >&2
  return 0
}

# The test screen is what an aim reads: the enclosure's own pixels drawn as four white squares at
# known panel coordinates and a white frame on the outermost ones, put up by the main board's
# console for 120 s. The squares' centres fix where the panel is; the frame and the screen's pixel
# patterns say how well; its palette row says how the camera renders each colour the firmware draws.
cmd_aim() {
  local target="${1:-}"
  [ -n "$target" ] || die "usage: panelcam.sh aim <target>"
  local console; console="$(target_field_opt "$target" console)"
  [ -n "$console" ] || die "target '$target' has no console: the test screen is what an aim reads"
  mkdir -p "$OUT_DIR"
  local full="$OUT_DIR/$target.test.png"
  python3 "$HERE/panelcam-console.py" "$console" test 120 | grep -q -i test ||
    die "the console on $console did not put the test screen up"
  take_frame "$full" "$target"
  python3 "$HERE/panelcam-console.py" "$console" test off >/dev/null 2>&1 || true
  [ -f "$full" ] || die "no frame — $(tail -1 "$LOGFILE" 2>/dev/null)"
  local found; found="$("$PY" "$RECTIFY" find "$full")" || die "could not read the test screen in $full"
  local corners score
  corners="$(sed -n 's/^corners //p' <<<"$found")"; score="$(sed -n 's/^score //p' <<<"$found")"
  awk -v t="$target" -v s="$score" -v c="$corners" '
    $1 == t && $2 == "score"   { $0 = sprintf("%-7s %-12s %s", t, "score", s) }
    $1 == t && $2 == "corners" { $0 = sprintf("%-7s %-12s %s", t, "corners", c) }
    { print }' "$CONF" > "$CONF.new" && mv "$CONF.new" "$CONF"
  # The proof: laid onto its grid, the screen's one-pixel stripes come out as alternate columns and
  # the panel's pixel lattice lands at `scale` px per panel px.
  local proof="$OUT_DIR/$target.aim.png"
  "$PY" "$RECTIFY" warp "$full" "$proof" --corners "$corners" \
    --panel "$(target_field "$target" panel)" --scale "$(target_field "$target" scale)"
  local read; read="$("$PY" "$RECTIFY" palette "$proof" --scale "$(target_field "$target" scale)")"
  local palette; palette="$(sed -n 's/^palette //p' <<<"$read")"
  awk -v t="$target" -v p="$palette" '
    $1 == t && $2 == "palette" { $0 = sprintf("%-7s %-12s %s", t, "palette", p) }
    { print }' "$CONF" > "$CONF.new" && mv "$CONF.new" "$CONF"
  echo "$full"
  echo "  corners $corners  -> written to $(basename "$CONF")"
  "$PY" "$RECTIFY" check "$proof" --scale "$(target_field "$target" scale)" | sed 's/^/  /'
  echo "  palette: $(wc -w <<<"$palette" | tr -d ' ') colours -> written; $(sed -n 's/^closest as captured: //p' <<<"$read")"
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
