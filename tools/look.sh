#!/usr/bin/env bash
# look.sh — see a body in the pack, from the three orthographic directions, in one command.
#
# render-view.js takes an edition, a step path relative to THAT edition's root, an output path,
# a projection, a context mode and a size. Six arguments with one right answer each, and getting
# the path root wrong is silent (it resolves against the kitchen tree and reports "step file not
# found"). That reconstruction is the friction that kept the tool unused across nine sessions, so
# this fixes every argument that has a right answer and leaves the one a caller actually chooses:
# which bodies to look at.
#
#   tools/look.sh seaflo-pump                 # one body, three views
#   tools/look.sh fluid-23,fluid-27           # a pair — the shape a crossing shows up in
#   tools/look.sh 'divider-y-*' --views top   # a glob, plan only
#   tools/look.sh --list                      # every body name in the pack
#
# Named bodies render SOLID with feature edges and a tint each; everything else stays IN FRAME as
# edges only, so a neighbour is visible without hiding the subject. The frame carries a mm grid
# with numbered ticks and a scale bar measured through the projection used, so a coordinate is
# read off the picture rather than trusted from a table — which is the whole point, since the
# tables report bounding boxes and a bounding box is a rectangle, not a part.
#
# Prints the paths it wrote. Read them.

set -euo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
EDITION="kitchen"
STEP="manifold-layout/front-half.step"
VIEWS="top,front,right"
SIZE="1600x1200"
OUT="${TMPDIR:-/tmp}/look"

only=""
list=""
extra=()
while [[ $# -gt 0 ]]; do
  case "$1" in
    --list)    list=1; shift ;;
    --views)   VIEWS="$2"; shift 2 ;;
    --views=*) VIEWS="${1#*=}"; shift ;;
    --edition) EDITION="$2"; shift 2 ;;
    --edition=*) EDITION="${1#*=}"; shift ;;
    --step)    STEP="$2"; shift 2 ;;
    --step=*)  STEP="${1#*=}"; shift ;;
    --size)    SIZE="$2"; shift 2 ;;
    --size=*)  SIZE="${1#*=}"; shift ;;
    --out)     OUT="$2"; shift 2 ;;
    --out=*)   OUT="${1#*=}"; shift ;;
    --)        shift; extra+=("$@"); break ;;
    -*)        extra+=("$1"); shift ;;          # anything else goes straight to render-view
    *)         only="$1"; shift ;;
  esac
done

if [[ -n "$list" ]]; then
  exec node "$REPO/tools/render/render-view.js" "$STEP" --edition "$EDITION" --list
fi

if [[ -z "$only" ]]; then
  sed -n '2,21p' "${BASH_SOURCE[0]}" | sed 's/^# \{0,1\}//'
  exit 2
fi

mkdir -p "$OUT"
# One stem per subject, so two looks at different bodies do not overwrite each other and both
# stay readable side by side. Globs and commas are not filename characters.
stem="$OUT/$(printf '%s' "$only" | tr -c 'A-Za-z0-9._-' '-').png"

exec node "$REPO/tools/render/render-view.js" "$STEP" "$stem" \
  --edition "$EDITION" --views "$VIEWS" --ortho \
  --only "$only" --xray "enclosure-*" --size "$SIZE" "${extra[@]+"${extra[@]}"}"
