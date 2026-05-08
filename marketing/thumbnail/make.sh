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
# ── Gotchas (read before tweaking) ──────────────────────────────────────────
#
# YouTube paints a duration pill in the bottom-RIGHT corner of every thumbnail
# in feed and grid views (search results, channel page, related, sidebar — any
# surface that's NOT the watch page itself). On mobile that pill takes a
# larger proportion of the thumbnail and reliably stomps on bottom-positioned
# text — even text "lifted" 120 px above the bottom edge gets visually
# clipped on a phone-sized render. The clean solution is to put the text at
# the TOP of the thumbnail and keep the bottom half clear for the pill.
# This script does that: gravity=north + TOP_PAD=80 plants the headline near
# the top edge with breathing room from the screen edge for safe-zone
# considerations on cropped previews.
#
# Aspect ratio: source images can be any shape. -resize 1280x720^ + -extent
# 1280x720 first scales the smallest dimension to fit, then center-crops to
# exact 16:9. If the action you want is NOT centered in the source, pre-crop
# before passing in, or this script will lose it. Sources that are wider than
# 16:9 (e.g. iPhone Pro Max landscape screenshots, ~2.17:1) lose left/right;
# sources taller than 16:9 lose top/bottom.
#
# Two-pass text draw: the script draws TEXT twice on purpose — once with
# strokewidth=STROKE and black fill (the outline pass), then once with no
# stroke and white fill (the fill pass). Collapsing this into a single
# annotate call with stroke + fill makes the stroke eat into the letter
# interiors, which thins the white and looks muddy at small sizes. Don't
# "simplify" it back.
#
# Font: Helvetica-Bold reliable on macOS, dense enough to read at feed-
# thumbnail size. Swap to Impact, AvenirNext-Heavy, or any installed bold
# sans-serif via the FONT knob below. Run `magick -list font` to see what
# else is on the system.
#
# Stroke width: scales with point size. STROKE=12 looks right at POINTSIZE=115.
# If you bump POINTSIZE to ~150+, push STROKE to ~16. If you drop POINTSIZE
# below ~80, drop STROKE to ~8. Keep them roughly proportional.
#
# Word count: big text only works when there are FEW words (2-3 ideal, 4 max).
# A 5+ word headline at POINTSIZE=115 will overflow the 1280-px width; either
# shorten the headline or drop POINTSIZE. Single-line layout is the design
# convention here — multi-line is doable but starts to look wall-of-text-y.
#
# ── Dependencies ────────────────────────────────────────────────────────────
#
# ImageMagick. Install with `brew install imagemagick`.

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
TOP_PAD=80  # Distance from top edge to the text baseline area. See gotchas.

magick "$SRC" \
  -resize "1280x720^" \
  -gravity center -extent 1280x720 \
  -font "$FONT" -pointsize "$POINTSIZE" -gravity north \
  -stroke black -strokewidth "$STROKE" -fill black -annotate "+0+${TOP_PAD}" "$TEXT" \
  -stroke none -fill white -annotate "+0+${TOP_PAD}" "$TEXT" \
  "$OUT"

echo "wrote $OUT"
