#!/usr/bin/env bash
# synthesize.sh — regenerate the SFX library used by overlays.py sound mixing.
#
# Each effect is a deterministic ffmpeg synthesis (sine/triangle generators
# and white-noise sweeps) at 48000 Hz stereo to match the rest of the video
# pipeline. v1 placeholders — usable, not perfect. Replace with real recorded
# sound design when a particular cue starts mattering.
#
# Levels are tuned to roughly -3 dBFS peak after envelope so each cue has
# headroom when mixed into a louder bed.
#
# Outputs are committed to the repo; this script exists so they can be
# regenerated when a recipe is tweaked.
#
# Run from anywhere:
#   bash marketing/video/sfx/synthesize.sh
#
# Listen on macOS:
#   afplay marketing/video/sfx/stamp-thud.wav
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

SR=48000
COMMON=(-y -hide_banner -loglevel error)
# Stereo by duplicating mono; channelmap mono -> 2ch is cleaner than
# pan= and avoids ffmpeg phantom-center weirdness.
TO_STEREO="aformat=channel_layouts=stereo,aresample=$SR"

# Each cue's final volume= boost is tuned so the file lands near -3 dBFS
# peak after envelope. Exponential envelopes lose more level than the
# nominal signal peak suggests, so we measure, boost, re-measure — these
# numbers are the result of that iteration.
normalize_to_peak() {
    # Usage: normalize_to_peak <wav> <target_peak_db>
    # Reads peak, computes boost, rewrites file in place.
    local file="$1"
    local target_db="$2"
    local peak
    peak=$(ffmpeg -hide_banner -i "$file" -af volumedetect -f null /dev/null 2>&1 \
        | awk '/max_volume/ {print $5}')
    # Cheap shell arithmetic: target - peak (peak is negative dB).
    local boost
    boost=$(awk -v t="$target_db" -v p="$peak" 'BEGIN{printf "%.2f", t-p}')
    local tmp="${file%.wav}.tmp.wav"
    ffmpeg "${COMMON[@]}" -i "$file" -af "volume=${boost}dB" "$tmp"
    mv "$tmp" "$file"
}

# ----- stamp-thud.wav -----
# Short low-frequency impact for "NO STICK" / "DON'T LET GO" stamps.
# 70 Hz sine, ~150 ms with sharp attack and exponential decay. A faint
# 140 Hz harmonic sits above to give it shape; without it the thud sounds
# like a synth bass note rather than a hit.
ffmpeg "${COMMON[@]}" \
    -f lavfi -i "sine=frequency=70:duration=0.18:sample_rate=$SR" \
    -f lavfi -i "sine=frequency=140:duration=0.18:sample_rate=$SR" \
    -filter_complex "
        [0:a]volume=1.0[a0];
        [1:a]volume=0.35[a1];
        [a0][a1]amix=inputs=2:normalize=0,
        volume='exp(-22*t)':eval=frame,
        $TO_STEREO,
        volume=-3dB
    " \
    stamp-thud.wav

# ----- whoosh.wav -----
# Fast filtered noise sweep for transitions/reveals. White noise through a
# lowpass that opens from ~300 Hz to ~5 kHz across 300 ms. ffmpeg's lowpass
# `frequency` option doesn't accept time expressions but it IS marked
# runtime-tunable, so we drive it via afftfilt-style sendcmd commands at
# discrete steps. Volume swells in and tails off so it doesn't click.
ffmpeg "${COMMON[@]}" \
    -f lavfi -i "anoisesrc=duration=0.30:color=white:sample_rate=$SR" \
    -filter_complex "
        [0:a]asendcmd='
            0.00 lowpass frequency 300;
            0.05 lowpass frequency 900;
            0.10 lowpass frequency 1800;
            0.15 lowpass frequency 2800;
            0.20 lowpass frequency 3800;
            0.25 lowpass frequency 5000
        ',lowpass=frequency=300,
        volume='if(lt(t,0.05),t/0.05,if(lt(t,0.25),1,(0.30-t)/0.05))':eval=frame,
        $TO_STEREO,
        volume=-3dB
    " \
    whoosh.wav

# ----- ding.wav -----
# Bright affirmative ping for "found it" / wire-feed-button reveals. Mix of
# 1800 Hz fundamental + 3600 Hz octave + 5400 Hz fifth, ~400 ms with a fast
# attack and a long exponential decay. The harmonics give it a bell-ish
# character rather than a synth blip.
ffmpeg "${COMMON[@]}" \
    -f lavfi -i "sine=frequency=1800:duration=0.40:sample_rate=$SR" \
    -f lavfi -i "sine=frequency=3600:duration=0.40:sample_rate=$SR" \
    -f lavfi -i "sine=frequency=5400:duration=0.40:sample_rate=$SR" \
    -filter_complex "
        [0:a]volume=1.0[a0];
        [1:a]volume=0.5[a1];
        [2:a]volume=0.25[a2];
        [a0][a1][a2]amix=inputs=3:normalize=0,
        volume='exp(-9*t)':eval=frame,
        $TO_STEREO,
        volume=-3dB
    " \
    ding.wav

# ----- sting.wav -----
# Short cinematic cold-open beat. Layered 80 Hz + 160 Hz + 320 Hz tones with
# a big front attack and a ~650 ms exponential decay. Reads as the "here we
# go" punctuation under a cold open or pre-title beat.
ffmpeg "${COMMON[@]}" \
    -f lavfi -i "sine=frequency=80:duration=0.70:sample_rate=$SR" \
    -f lavfi -i "sine=frequency=160:duration=0.70:sample_rate=$SR" \
    -f lavfi -i "sine=frequency=320:duration=0.70:sample_rate=$SR" \
    -filter_complex "
        [0:a]volume=1.0[a0];
        [1:a]volume=0.7[a1];
        [2:a]volume=0.35[a2];
        [a0][a1][a2]amix=inputs=3:normalize=0,
        volume='exp(-5.5*t)':eval=frame,
        $TO_STEREO,
        volume=-3dB
    " \
    sting.wav

# ----- click.wav -----
# Short UI tick for caption hits / chapter markers / sub-emphasis. ~40 ms.
# 2400 Hz sine clamped tight by a fast decay envelope. Useful as a quieter
# punctuation than ding — the difference between "yes" and "noted."
ffmpeg "${COMMON[@]}" \
    -f lavfi -i "sine=frequency=2400:duration=0.06:sample_rate=$SR" \
    -filter_complex "
        [0:a]volume='exp(-60*t)':eval=frame,
        $TO_STEREO,
        volume=-3dB
    " \
    click.wav

# Normalize each cue to ~-3 dBFS peak so the mixing-side `volume` knob
# (default 1.0) has a sensible meaning. Without this the cues with steep
# exponential decay envelopes end up 15-20 dB quieter than the noise-sweep
# whoosh, which makes per-cue volume knobs in the sidecar misleading.
for f in stamp-thud.wav whoosh.wav ding.wav sting.wav click.wav; do
    normalize_to_peak "$f" -3
done

echo "Wrote SFX library:"
ls -lh stamp-thud.wav whoosh.wav ding.wav sting.wav click.wav
echo
echo "Peak levels (post-normalize):"
for f in stamp-thud.wav whoosh.wav ding.wav sting.wav click.wav; do
    peak=$(ffmpeg -hide_banner -i "$f" -af volumedetect -f null /dev/null 2>&1 \
        | awk '/max_volume/ {print $5, $6}')
    echo "  $f: $peak"
done
