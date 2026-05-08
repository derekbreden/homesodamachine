#!/usr/bin/env python3
"""
make-subtitles.py — generate an ASS subtitle file aligned to a cut list.

Reads a cut list and emits an Advanced SubStation Alpha (.ass) subtitle
file with each spoken phrase positioned in OUTPUT-video time. The intent
is for the file to be passed to ffmpeg's `subtitles=` filter as the
final pass of cut.py, burning the captions into the rendered video at
the right timestamps post-cut, post-cross-dissolve, and post-title-card.

Why ASS over SRT? ASS handles styled rendering natively (font, size,
outline, shadow, smart wrap) without a separate stylesheet — important
for the "TikTok / IG / modern doc" aesthetic of large bold sans-serif
white-on-black-outline burned-in captions. SRT would force us to
re-implement styling in ffmpeg drawtext, which is fiddly per-line.

Inputs:
- cut_list (JSON):
    Either a list of cut entries, or a dict with shape:
    {
      "sources": {
        "<source_video_path>": {
          "transcript": "<path to whisper json>",
          "sync_offset": <float, audio_t = video_t + offset>
        },
        ...
      },
      "cuts": [ {"source": ..., "start": ..., "end": ...}, ... ]
    }
    In list mode (legacy), each cut may carry inline "transcript" and
    "sync_offset" fields, or those are auto-discovered:
      transcript -> "transcripts/<source_stem>.json"
      sync_offset -> read from "<source_path>.sync.json"

- whisper transcripts: per-source JSON output from `whisper --output_format json`

For each cut, we walk every whisper segment whose audio_t window
overlaps the cut's video_t window (after sync offset), clip its time
to the cut, translate it to output-time, and emit a Dialogue line.

Inter-cut gaps from `--fade` are subtracted from cumulative output time
so the captions still line up after cross-dissolves overlap segments.

Filler hallucinations (single " so " segments during silence — see
segment.py for the same heuristic) are filtered out, otherwise they
litter the captions during silent stretches between speech.

Usage:
  ./tools/video-venv/bin/python marketing/video/make-subtitles.py \\
      <cut_list.json> <output.ass> \\
      [--fade SECONDS] [--title-duration SECONDS]

`--title-duration` shifts every dialogue forward by that amount, so
captions align after a prepended title card. `--fade` matches the
xfade duration cut.py was invoked with.
"""

import argparse
import json
import sys
from pathlib import Path


ASS_HEADER = """[Script Info]
ScriptType: v4.00+
WrapStyle: 2
ScaledBorderAndShadow: yes
PlayResX: 1920
PlayResY: 1080

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Helvetica,54,&H00FFFFFF,&H000000FF,&H00000000,&H00000000,1,0,0,0,100,100,0,0,1,4,1,2,80,80,90,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

# Same FILLER set as segment.py — keep them in sync if you add tokens
# (refactor target: extract a shared helper if this list grows).
FILLER_TOKENS = {"so", "um", "uh", "uhh", "hmm", "mm", "mhm", "ah"}


def fmt_ass_time(t: float) -> str:
    """Format seconds as ASS timestamp: H:MM:SS.cc (centiseconds)."""
    h = int(t // 3600)
    m = int((t % 3600) // 60)
    sec = t - h * 3600 - m * 60
    return f"{h}:{m:02d}:{sec:05.2f}"


def is_filler(text: str, duration: float) -> bool:
    text = text.strip().lower()
    if not text:
        return True
    if duration > 3.0:
        return False
    tokens = text.split()
    return all(t.strip(",.?!") in FILLER_TOKENS for t in tokens)


# Caption chunking: TikTok / Casey-Neistat-doc burned-in captions break
# at ~3 s or ~6 words to keep each line glanceable. We split each whisper
# segment's word list (after cut-window clipping) into chunks bounded by
# both duration and word count. Sentence-ending punctuation forces a
# break too — keeps natural phrasing intact.
CHUNK_MAX_DURATION_S = 3.5
CHUNK_MAX_WORDS = 7
SENTENCE_END_PUNCT = (".", "!", "?")


def chunk_words(words: list[tuple[float, float, str]]):
    """Split a list of (start, end, text) word tuples into subtitle chunks.

    Yields lists of word tuples. Each chunk respects the duration / word-
    count caps and breaks at sentence-ending punctuation.
    """
    if not words:
        return
    current = []
    for w in words:
        if current:
            chunk_dur = w[1] - current[0][0]
            prev_text = current[-1][2].strip()
            sentence_break = prev_text.endswith(SENTENCE_END_PUNCT)
            if (sentence_break
                    or chunk_dur > CHUNK_MAX_DURATION_S
                    or len(current) >= CHUNK_MAX_WORDS):
                yield current
                current = []
        current.append(w)
    if current:
        yield current


def escape_ass(text: str) -> str:
    """Escape characters that have meaning in ASS dialogue text."""
    return (text
            .replace("\\", "\\\\")
            .replace("{", "\\{")
            .replace("}", "\\}")
            .replace("\n", "\\N"))


def resolve_source_meta(cut: dict, sources_top: dict) -> tuple[str, float]:
    """Determine transcript path and sync_offset for a cut.

    Resolution order:
      1. cut's own "transcript" / "sync_offset" fields (legacy/override)
      2. top-level sources mapping for cut["source"]
      3. auto-discovery: transcripts/<stem>.json, <source>.sync.json
    """
    src = cut["source"]
    transcript = cut.get("transcript")
    sync_offset = cut.get("sync_offset")

    if src in sources_top:
        meta = sources_top[src]
        transcript = transcript or meta.get("transcript")
        if sync_offset is None:
            sync_offset = meta.get("sync_offset")

    if transcript is None:
        transcript = f"transcripts/{Path(src).stem}.json"

    if sync_offset is None:
        sidecar = Path(src + ".sync.json")
        if sidecar.exists():
            sync_offset = json.loads(sidecar.read_text()).get("offset_seconds", 0.0)
        else:
            sync_offset = 0.0

    return transcript, float(sync_offset)


def main():
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    ap.add_argument("cut_list", help="Cut list JSON (list or dict-with-sources format)")
    ap.add_argument("output_ass", help="Output .ass file path")
    ap.add_argument("--fade", type=float, default=0.0,
                    help="xfade duration cut.py was invoked with (seconds)")
    ap.add_argument("--title-duration", type=float, default=0.0,
                    help="Title-card duration prepended to output (seconds)")
    args = ap.parse_args()

    raw = json.loads(Path(args.cut_list).read_text())
    if isinstance(raw, dict):
        sources_top = raw.get("sources", {})
        cuts = raw["cuts"]
    else:
        sources_top = {}
        cuts = raw

    has_title = args.title_duration > 0
    # output_t accumulates OUTPUT-time position; updated per cut so it
    # equals "start of this cut in output" by the time we emit its
    # dialogues. xfade overlaps (title→cut1, cut1→cut2, ...) consume
    # `fade` seconds each.
    output_t = args.title_duration

    # Collect (output_start, output_end, text) tuples; post-process for
    # overlap removal before formatting as ASS.
    dialogues: list[tuple[float, float, str]] = []
    n_filtered = 0

    for i, cut in enumerate(cuts):
        if (i > 0 or has_title) and args.fade > 0:
            output_t -= args.fade

        transcript_path, sync_offset = resolve_source_meta(cut, sources_top)
        cut_v_start = cut["start"]
        cut_v_end = cut["end"]
        cut_dur = cut_v_end - cut_v_start

        try:
            transcript = json.loads(Path(transcript_path).read_text())
        except FileNotFoundError:
            print(f"WARN: transcript {transcript_path} not found for cut {i+1} "
                  f"({cut['source']}); cut will have no captions",
                  file=sys.stderr)
            output_t += cut_dur
            continue

        for seg in transcript.get("segments", []):
            seg_v_start = seg["start"] - sync_offset
            seg_v_end = seg["end"] - sync_offset

            if seg_v_end <= cut_v_start or seg_v_start >= cut_v_end:
                continue

            # Use word-level data when available. Strict inclusion: only
            # words whose ENTIRE duration fits inside the cut window
            # are kept. Words that extend past the cut boundary would
            # be cut off audibly (mid-syllable when we trim mid-segment
            # for editorial reasons), so we drop them so the subtitle
            # stays in sync with what the viewer actually hears.
            words = seg.get("words", [])
            if words:
                kept: list[tuple[float, float, str]] = []
                for w in words:
                    w_v_start = w["start"] - sync_offset
                    w_v_end = w["end"] - sync_offset
                    if w_v_start < cut_v_start or w_v_end > cut_v_end:
                        continue
                    kept.append((w_v_start, w_v_end, w["word"]))
                if not kept:
                    continue

                # Split into shorter subtitle chunks for the modern look.
                for chunk in chunk_words(kept):
                    text = "".join(w[2] for w in chunk).strip()
                    cv_start = chunk[0][0]
                    cv_end = chunk[-1][1]
                    if is_filler(text, cv_end - cv_start):
                        n_filtered += 1
                        continue
                    o_start = output_t + (cv_start - cut_v_start)
                    o_end = output_t + (cv_end - cut_v_start)
                    dialogues.append((o_start, o_end, text))
            else:
                # No word-level data — fall back to whole-segment line.
                text = seg.get("text", "").strip()
                cv_start = max(seg_v_start, cut_v_start)
                cv_end = min(seg_v_end, cut_v_end)
                if is_filler(text, cv_end - cv_start):
                    n_filtered += 1
                    continue
                o_start = output_t + (cv_start - cut_v_start)
                o_end = output_t + (cv_end - cut_v_start)
                dialogues.append((o_start, o_end, text))

        output_t += cut_dur

    # Post-process: enforce non-overlap. xfade boundaries cause adjacent
    # cuts' subtitles to share `fade` seconds — without this, ASS
    # renders both stacked. Truncate the earlier line's end to the
    # later line's start. Drop any line that ends up with zero or
    # negative duration.
    dialogues.sort(key=lambda d: d[0])
    cleaned: list[tuple[float, float, str]] = []
    for i, (start, end, text) in enumerate(dialogues):
        if i + 1 < len(dialogues):
            next_start = dialogues[i + 1][0]
            if end > next_start:
                end = next_start
        if end - start < 0.15:
            # Drop subtitles that would flash for less than ~150 ms;
            # they're more visual noise than information.
            continue
        cleaned.append((start, end, text))

    out_lines = [ASS_HEADER]
    for start, end, text in cleaned:
        out_lines.append(
            f"Dialogue: 0,{fmt_ass_time(start)},{fmt_ass_time(end)},"
            f"Default,,0,0,0,,{escape_ass(text)}"
        )
    n_dialogue = len(cleaned)

    Path(args.output_ass).write_text("\n".join(out_lines) + "\n")
    print(f"wrote {args.output_ass}: {n_dialogue} dialogue lines "
          f"({n_filtered} filler segments filtered)", file=sys.stderr)


if __name__ == "__main__":
    main()
