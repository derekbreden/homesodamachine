#!/usr/bin/env bash
# export-from-photos.sh — pull recent video originals out of Photos.app
# into a working directory, ready for the sync/cut pipeline.
#
# Usage:
#   ./export-from-photos.sh <output-dir> [days-back]
#
# Examples:
#   ./export-from-photos.sh ~/Desktop/soda-edit/2026-05-08-first-tap/video 1
#   ./export-from-photos.sh ./video                                         3
#
# Default days-back is 1. Anything added to the Photos library in the last
# N days that's a movie gets exported as its unmodified original (the
# raw GoPro .MP4 — not the Photos-recompressed version).
#
# ── One-time setup: Full Disk Access ──────────────────────────────────
#
# This script reads the Photos library SQLite database directly via
# osxphotos. macOS protects ~/Pictures/Photos Library.photoslibrary
# behind System Integrity Protection — the script will fail with
# "Operation not permitted" until the terminal that's running this
# script has Full Disk Access.
#
#   System Settings → Privacy & Security → Full Disk Access
#   → toggle on for whichever terminal you use (Terminal, iTerm, etc.)
#   → restart that terminal for the change to take effect
#
# This is a one-time setup. After that, exports run with no prompts.
#
# ── Fallback: manual export ───────────────────────────────────────────
#
# If granting FDA isn't an option for this run: open Photos, select the
# clips you want, File → Export → Export Unmodified Originals → drop
# them in <output-dir> manually. Same end state.
#
# ── Why osxphotos over AppleScript ────────────────────────────────────
#
# AppleScript-driven Photos export works but is unbearably slow on
# multi-thousand-item libraries: filtering `media items whose filename
# ends with ".MP4"` iterates every item and times out. osxphotos talks
# directly to the SQLite DB and is essentially instantaneous.

set -euo pipefail

if [[ $# -lt 1 || $# -gt 2 ]]; then
  echo "usage: $0 <output-dir> [days-back]" >&2
  exit 1
fi

OUT_DIR="$1"
DAYS_BACK="${2:-1}"

mkdir -p "$OUT_DIR"

if ! command -v osxphotos >/dev/null 2>&1; then
  echo "osxphotos not found. Install with: pipx install osxphotos" >&2
  exit 2
fi

echo "Exporting movies added in last $DAYS_BACK day(s) to $OUT_DIR..." >&2

# --download-missing pulls iCloud-only items down on demand.
# --skip-edited keeps us on the originals (Photos sometimes recompresses).
# --convert-to-jpeg=False is the default but worth being explicit if Photos
#   ever flips it.
osxphotos export "$OUT_DIR" \
  --only-movies \
  --added-in-last "$DAYS_BACK days" \
  --download-missing \
  --skip-edited \
  --filename "{filename}" \
  --report "$OUT_DIR/export-report.json" \
  --verbose

echo "" >&2
echo "Exported files:" >&2
ls -la "$OUT_DIR" | grep -iE "\.(mp4|mov)$" >&2 || echo "  (none — check that videos finished syncing GoPro→Quik→Photos)" >&2
