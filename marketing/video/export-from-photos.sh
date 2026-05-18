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
# ── Why osascript over osxphotos ──────────────────────────────────────
#
# osxphotos reads ~/Pictures/Photos Library.photoslibrary's SQLite
# database directly, which macOS protects behind Full Disk Access.
# Granting FDA to a terminal is a sweeping permission — it gives that
# terminal read access to ~/Library, ~/Mail, etc. forever.
#
# Instead, this script asks Photos.app to do the export via AppleScript.
# Photos.app already has access to its own library; osascript just sends
# it commands. No FDA grant on the terminal is needed.
#
# Wrapped in `with timeout of 1200 seconds` because exporting a 6 GB
# GoPro file copies a lot of bytes and the default 120 s AppleScript
# timeout will trip on 30-min clips.
#
# ── AppleScript gotchas (captured from first-pass debugging) ──────────
#
# • `media items whose date >= X` does NOT work — Photos.app's AppleScript
#   dictionary refuses to coerce the date class into a `type specifier`
#   in `whose` clauses. Filter manually in a `repeat` loop instead.
# • `kind of <media item> as string` doesn't coerce either (returns the
#   raw IPmi class). Filter by filename extension (.mp4/.mov/.m4v) to
#   distinguish movies from photos.
# • Photos sorts `media items` by date ASCENDING — newest is at index -1,
#   not 1. Walk the list from the END to find recent items; bail as soon
#   as you cross the cutoff. This keeps the scan O(recent_items) instead
#   of O(library_size), which matters on 10k+ item libraries.
# • `export <items> to <folder>` needs the destination as an `alias`,
#   which means the directory must already exist when AppleScript
#   resolves it. The shell wrapper does `mkdir -p` before invoking
#   osascript.
# • `with using originals` is the option that produces unmodified
#   originals (the raw GoPro .MP4 rather than the Photos-recompressed
#   version). Without it Photos hands back its edited / re-encoded copy.
#
# ── Fallback: manual export ───────────────────────────────────────────
#
# If osascript fails (Photos.app crashed, permissions weirdness, etc.):
# open Photos, select the clips you want, File → Export → Export
# Unmodified Originals → drop them in <output-dir> manually. Same end
# state.

set -euo pipefail

if [[ $# -lt 1 || $# -gt 2 ]]; then
  echo "usage: $0 <output-dir> [days-back]" >&2
  exit 1
fi

OUT_DIR="$1"
DAYS_BACK="${2:-1}"

mkdir -p "$OUT_DIR"
# Resolve to absolute path so AppleScript's POSIX file coercion works
# regardless of where the script was invoked from.
OUT_DIR_ABS="$(cd "$OUT_DIR" && pwd)"

echo "Exporting movies added in last $DAYS_BACK day(s) to $OUT_DIR_ABS..." >&2

# Record pre-existing files so we can report only newly exported ones.
BEFORE="$(ls -1 "$OUT_DIR_ABS" 2>/dev/null | sort || true)"

osascript - "$OUT_DIR_ABS" "$DAYS_BACK" <<'APPLESCRIPT'
on run argv
    set destPath to item 1 of argv
    set daysBack to (item 2 of argv) as integer
    set destFolder to POSIX file destPath as alias

    tell application "Photos"
        activate
        set theCutoff to (current date) - (daysBack * days)
        set allItems to media items
        set totalCount to count of allItems
        set movies to {}
        set scanned to 0
        set idx to totalCount
        -- Walk from newest (end of list) backward until we cross the
        -- cutoff date. Filename-extension filter for movies because
        -- `kind of <media item>` doesn't coerce to string reliably.
        repeat while idx > 0
            set anItem to item idx of allItems
            set d to date of anItem
            if d < theCutoff then exit repeat
            set fn to filename of anItem
            if fn ends with ".mp4" or fn ends with ".MP4" ¬
                or fn ends with ".mov" or fn ends with ".MOV" ¬
                or fn ends with ".m4v" or fn ends with ".M4V" then
                set end of movies to anItem
            end if
            set idx to idx - 1
            set scanned to scanned + 1
            -- Hard safety cap: don't iterate forever if the library
            -- has no date-sorted ordering for some reason.
            if scanned > 5000 then exit repeat
        end repeat

        set movieCount to count of movies
        log "scanned " & scanned & " recent items, found " & movieCount & " movies"
        if movieCount = 0 then
            return "0 movies in last " & daysBack & " day(s)"
        end if

        with timeout of 1200 seconds
            export movies to destFolder with using originals
        end timeout

        set msg to "exported " & movieCount & " movie(s):"
        repeat with m in movies
            set msg to msg & linefeed & "  " & (filename of m)
        end repeat
        return msg
    end tell
end run
APPLESCRIPT

echo "" >&2
echo "Files in $OUT_DIR_ABS after export:" >&2
AFTER="$(ls -1 "$OUT_DIR_ABS" 2>/dev/null | sort || true)"
NEW_FILES="$(comm -13 <(echo "$BEFORE") <(echo "$AFTER") || true)"
if [[ -n "$NEW_FILES" ]]; then
  echo "$NEW_FILES" | while read -r f; do
    [[ -z "$f" ]] && continue
    sz=$(ls -la "$OUT_DIR_ABS/$f" 2>/dev/null | awk '{print $5}')
    echo "  $f  ($sz bytes)" >&2
  done
else
  echo "  (no new files — check that videos finished syncing GoPro→Quik→Photos)" >&2
fi
