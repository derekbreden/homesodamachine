#!/usr/bin/env bash
# make.sh — turn a source image plus a single-line headline into a YouTube-ready
# 1280x720 thumbnail with big white-on-photo text and a black outline.
#
# usage: ./make.sh <source-image> <output-image> "HEADLINE TEXT"
#
# Examples:
#   ./make.sh first-weld-source.png first-weld.png "I'VE NEVER WELDED"
#   ./make.sh some-shot.png next-thumbnail.png "DAY ONE OF FOAM"
#
# Design notes:
#   - YouTube thumbnail spec is 1280x720, 16:9, PNG/JPG, < 2MB. We resize-and-
#     center-crop the source to exactly 1280x720 with -resize ^ + -extent.
#   - Text sits in the bottom band so the action photo above stays visible.
#   - Two-pass draw (black stroke pass, then white fill pass) gives a clean
#     white-with-outline result instead of the stroke eating into the fill.
#   - Font is Helvetica-Bold by default — reliable on macOS and dense enough to
#     read at feed-thumbnail size. Swap to Impact, AvenirNext-Heavy, or any
#     installed bold sans-serif by editing the FONT variable below.
#   - Stroke width scales with point size; tune STROKE if a future thumbnail
#     uses much smaller or larger text.
#
# Dependency: ImageMagick (`magick` command). Install with `brew install imagemagick`.

set -euo pipefail

if [[ $# -ne 3 ]]; then
  echo "usage: $0 <source-image> <output-image> \"HEADLINE TEXT\"" >&2
  exit 1
fi

SRC="$1"
OUT="$2"
TEXT="$3"

FONT="Helvetica-Bold"
POINTSIZE=115
STROKE=12
BOTTOM_PAD=50

magick "$SRC" \
  -resize "1280x720^" \
  -gravity center -extent 1280x720 \
  -font "$FONT" -pointsize "$POINTSIZE" -gravity south \
  -stroke black -strokewidth "$STROKE" -fill black -annotate "+0+${BOTTOM_PAD}" "$TEXT" \
  -stroke none -fill white -annotate "+0+${BOTTOM_PAD}" "$TEXT" \
  "$OUT"

echo "wrote $OUT"
