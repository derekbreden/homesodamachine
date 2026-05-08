#!/usr/bin/env python3
"""
segment.py — cluster Whisper speech segments into candidate scenes
with broad pre/post context windows.

Reads a Whisper JSON transcript (segment-level timestamps from a run
with --output_format json) and:
  1. Groups segments into "speech clusters" — runs of speech with no
     gap longer than --gap (default 10 s).
  2. Expands each cluster into a "scene" by padding by --pad-before
     and --pad-after seconds (defaults 30 / 30).
  3. Merges any scenes that overlap after padding.

Why broad pads? In build-in-public footage the interesting visual
moment usually starts BEFORE the words ("look what just happened")
and ends AFTER ("…and that's why it broke"). Tight cuts to speech
boundaries strip the cause and the reaction. We start broad here
and let the visual-analysis pass tighten where appropriate.

Tunable parameters live behind CLI flags so you can A/B different
values without re-transcribing. Defaults assume narration over
hands-on shop work; tweak for talking-head footage where the words
are the primary content.

Input JSON shape (from `whisper --output_format json`):
  { "text": "...", "segments": [ {"start": float, "end": float, "text": str, ...} ], ... }

Output JSON shape:
  {
    "input": "<path to whisper json>",
    "scenes": [
      {
        "scene_start":  10.5,   # padded, sec
        "scene_end":    98.0,   # padded, sec (merged if scenes overlapped)
        "speech_start": 40.5,   # earliest segment start in this scene
        "speech_end":   88.0,   # latest segment end in this scene
        "duration":     87.5,
        "text":         "stitched transcript across all segments",
        "segments":     [ {"start": ..., "end": ..., "text": ...}, ... ]
      },
      ...
    ],
    "params": { "gap_s": 10, "pad_before_s": 30, "pad_after_s": 30 }
  }

Usage:
  ./tools/video-venv/bin/python marketing/video/segment.py \\
      <whisper.json> [-o <output.json>] [--gap 10] [--pad-before 30] [--pad-after 30]

Pure stdlib — no numpy/scipy needed for this stage.
"""

import argparse
import json
import sys
from pathlib import Path

DEFAULT_GAP_S = 10.0
DEFAULT_PAD_BEFORE_S = 30.0
DEFAULT_PAD_AFTER_S = 30.0

# Whisper occasionally emits standalone " so" segments during silent
# stretches — single-token filler that breaks clustering. The no_speech_prob
# field is window-level (shared across multiple segments in a window) so it
# can't disambiguate per-segment; we filter by text content + duration
# instead. These tokens added below cover what we've seen empirically; add
# more if you find Whisper hallucinating other words on your audio.
FILLER_TOKENS = {"so", "um", "uh", "uhh", "hmm", "mm", "mhm", "ah"}


def is_filler_segment(seg):
    """A segment is filler if its text is empty or made entirely of filler tokens
    AND the segment is short (long ones might be a real verbal pause that's
    still semantically meaningful)."""
    text = seg.get("text", "").strip().lower()
    duration = seg.get("end", 0) - seg.get("start", 0)
    if not text or duration < 0.05:
        return True
    if duration > 3.0:
        return False  # too long to be filler hallucination
    tokens = text.split()
    return all(t.strip(",.?!") in FILLER_TOKENS for t in tokens)


def filter_hallucinations(segments):
    """Drop hallucinated filler segments (see FILLER_TOKENS / is_filler_segment)."""
    return [s for s in segments if not is_filler_segment(s)]


def cluster_segments(segments, gap_s):
    """Group consecutive segments into clusters separated by gaps > gap_s."""
    if not segments:
        return []
    clusters = [[segments[0]]]
    for seg in segments[1:]:
        if seg["start"] - clusters[-1][-1]["end"] <= gap_s:
            clusters[-1].append(seg)
        else:
            clusters.append([seg])
    return clusters


def expand_clusters(clusters, pad_before_s, pad_after_s, end_of_audio):
    """Expand each cluster into a padded scene; merge overlapping scenes."""
    if not clusters:
        return []
    scenes = []
    for cluster in clusters:
        speech_start = cluster[0]["start"]
        speech_end = cluster[-1]["end"]
        scenes.append({
            "scene_start": max(0.0, speech_start - pad_before_s),
            "scene_end": min(end_of_audio, speech_end + pad_after_s),
            "speech_start": speech_start,
            "speech_end": speech_end,
            "segments": list(cluster),
        })

    merged = [scenes[0]]
    for s in scenes[1:]:
        if s["scene_start"] <= merged[-1]["scene_end"]:
            merged[-1]["scene_end"] = max(merged[-1]["scene_end"], s["scene_end"])
            merged[-1]["speech_end"] = max(merged[-1]["speech_end"], s["speech_end"])
            merged[-1]["segments"].extend(s["segments"])
        else:
            merged.append(s)

    for s in merged:
        s["text"] = " ".join(seg["text"].strip() for seg in s["segments"])
        s["duration"] = s["scene_end"] - s["scene_start"]
    return merged


def fmt_time(t):
    m, sec = divmod(t, 60)
    return f"{int(m):02d}:{sec:05.2f}"


def main():
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    ap.add_argument("whisper_json", help="Path to a Whisper JSON transcript")
    ap.add_argument("-o", "--output", help="Output JSON path (default: <input>.scenes.json)")
    ap.add_argument("--gap", type=float, default=DEFAULT_GAP_S,
                    help=f"Max silence (s) inside a single cluster (default {DEFAULT_GAP_S})")
    ap.add_argument("--pad-before", type=float, default=DEFAULT_PAD_BEFORE_S,
                    help=f"Pre-roll context (s) before first speech (default {DEFAULT_PAD_BEFORE_S})")
    ap.add_argument("--pad-after", type=float, default=DEFAULT_PAD_AFTER_S,
                    help=f"Post-roll context (s) after last speech (default {DEFAULT_PAD_AFTER_S})")
    ap.add_argument("--no-filter", action="store_true",
                    help="Disable hallucination filtering (keep all segments verbatim)")
    args = ap.parse_args()

    transcript = json.loads(Path(args.whisper_json).read_text())
    raw_segments = transcript.get("segments", [])
    segments = raw_segments if args.no_filter else filter_hallucinations(raw_segments)
    n_dropped = len(raw_segments) - len(segments)
    end_of_audio = max((s["end"] for s in raw_segments), default=0.0)

    clusters = cluster_segments(segments, args.gap)
    scenes = expand_clusters(clusters, args.pad_before, args.pad_after, end_of_audio)

    out = {
        "input": args.whisper_json,
        "scenes": scenes,
        "params": {
            "gap_s": args.gap,
            "pad_before_s": args.pad_before,
            "pad_after_s": args.pad_after,
        },
    }

    output_path = Path(args.output) if args.output else Path(args.whisper_json + ".scenes.json")
    output_path.write_text(json.dumps(out, indent=2))

    drop_note = f" (dropped {n_dropped} hallucinated)" if n_dropped else ""
    print(f"wrote {output_path}: {len(scenes)} scenes from {len(segments)} segments"
          f"{drop_note}", file=sys.stderr)
    for i, s in enumerate(scenes, 1):
        print(f"  scene {i}: {fmt_time(s['scene_start'])}–{fmt_time(s['scene_end'])} "
              f"({s['duration']:.1f}s, speech {fmt_time(s['speech_start'])}–{fmt_time(s['speech_end'])})",
              file=sys.stderr)


if __name__ == "__main__":
    main()
