#!/usr/bin/env bash
# around.sh — walk around the pack the way it is read in the viewer, and CLICK what you find.
#
# `look.sh` answers "where is this body" — it names a subject, renders it solid and drops
# everything else to edges. This answers the other question: "what IS this thing, and what
# is it next to." Every body stays solid in its own colour, the four enclosure quadrants and
# the funnel come off, and the camera walks a circle instead of standing on one of six views.
#
# That is Derek's own view of the assembly, and the flags that make it have one right answer
# each — hide the walls and the funnel, keep the per-part colours, no labels, perspective,
# no grid. Fixed here, so the one thing a caller chooses is where to stand.
#
#   tools/around.sh                              # one slow turn, 15° a frame, 24 frames
#   tools/around.sh --spin x                     # tumble front→top→back instead of turntable
#   tools/around.sh --step 30                    # coarser turn, 12 frames
#   tools/around.sh --at 73,127,261 --near 0.95  # stand close to a point and turn there
#   tools/around.sh --click 500,350              # what is at that pixel? (amber, named)
#   tools/around.sh --show tee-y-a               # light a body you can already name
#   tools/around.sh --still 0.47,-0.81,0.34      # one frame down that camera direction
#
# READ THE FRAMES IN ORDER. The point of a turn is the transition: a silhouette that is
# ambiguous at one angle is resolved by the frame either side of it, and six named views
# never show you that. One parse serves the whole sweep, so a finer step is nearly free.
#
# --click casts from that pixel through the frame exactly as the viewer's component picker
# does, and paints what it hit in the picker's own amber. THAT IS THE CHECK: a name is the
# name of the thing you meant only when the thing that lit up is the thing you meant. Look
# at the frame before you quote the name. Pixels are read off a frame this tool wrote, so
# --click normally rides --still or a --spin angle you have already looked at.
#
# Prints the paths it wrote, and the name under every click. Read them.

set -euo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
EDITION="kitchen"
STEP="manifold-layout/enclosure-assembly.step"
SIZE="1400x1080"
OUT="${TMPDIR:-/tmp}/around"

# The walls and the funnel are what you take off to see the arrangement at all: the four
# quadrants wrap the whole pack and the funnel roofs the assembly.
HIDE="enclosure-*,hopper-funnel"

SPIN="z"
STEP_DEG="15"
ELEV="20"
TARGET=""
ZOOM="2.5"
STILL=""
extra=()
stem="turn"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --spin)    SPIN="$2"; shift 2 ;;
    --spin=*)  SPIN="${1#*=}"; shift ;;
    --step)    STEP_DEG="$2"; shift 2 ;;
    --step=*)  STEP_DEG="${1#*=}"; shift ;;
    --elev)    ELEV="$2"; shift 2 ;;
    --elev=*)  ELEV="${1#*=}"; shift ;;
    --at)      TARGET="$2"; shift 2 ;;
    --at=*)    TARGET="${1#*=}"; shift ;;
    --near)    ZOOM="$2"; shift 2 ;;
    --near=*)  ZOOM="${1#*=}"; shift ;;
    --still)   STILL="$2"; shift 2 ;;
    --still=*) STILL="${1#*=}"; shift ;;
    --click)   extra+=(--pick "$2"); shift 2 ;;
    --click=*) extra+=(--pick "${1#*=}"); shift ;;
    --show)    extra+=(--select "$2"); stem="show"; shift 2 ;;
    --show=*)  extra+=(--select "${1#*=}"); stem="show"; shift ;;
    --size)    SIZE="$2"; shift 2 ;;
    --size=*)  SIZE="${1#*=}"; shift ;;
    --out)     OUT="$2"; shift 2 ;;
    --out=*)   OUT="${1#*=}"; shift ;;
    --step-file) STEP="$2"; shift 2 ;;
    --edition) EDITION="$2"; shift 2 ;;
    --help|-h) sed -n '2,30p' "${BASH_SOURCE[0]}" | sed 's/^# \{0,1\}//'; exit 0 ;;
    --)        shift; extra+=("$@"); break ;;
    *)         extra+=("$1"); shift ;;          # anything else goes straight to render-view
  esac
done

# A camera given outright is one frame; otherwise it is a sweep on one axis.
if [[ -n "$STILL" ]]; then
  extra+=(--cam "$STILL" --up 0,0,1)
  stem="still"
else
  # 359.9 rather than 360 so the sweep stops one step short of its own start: a full turn
  # that closes on the frame it opened with writes that frame twice.
  extra+=(--orbit "$SPIN:0,359.9,$STEP_DEG${ELEV:+,$ELEV}")
fi

# Standing somewhere other than the middle of the pack is what a zoom IS here: --near scales
# the eye's distance off the whole model's radius, so it goes under 1 to get close.
[[ -n "$TARGET" ]] && extra+=(--target "$TARGET")

mkdir -p "$OUT"

exec node "$REPO/tools/render/render-view.js" "$STEP" "$OUT/$stem.png" \
  --edition "$EDITION" --hide "$HIDE" --no-tint --no-label \
  --zoom "$ZOOM" --size "$SIZE" "${extra[@]+"${extra[@]}"}"
