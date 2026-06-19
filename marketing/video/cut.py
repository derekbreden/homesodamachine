#!/usr/bin/env python3
"""
cut.py — assemble a polished video from a list of [start, end] ranges
in one or more source videos.

Reads a JSON cut list and produces a single output video by extracting
each range, optionally compositing per-cut overlays (section labels,
tool annotations), prepending a title card, cross-dissolving between
segments, and burning in subtitle captions.

The pipeline in three stages:
  1. EXTRACT each cut as its own short mp4 (per-cut drawtext overlays
     for `section` / `tool` baked in here, before any concat).
  2. (optional) GENERATE a title-card mp4 (still color background +
     centered text, silent audio).
  3. CONCAT — either hard-cut (concat demuxer, stream-copy) or
     cross-dissolve (xfade + acrossfade filter chain). The final pass
     applies the `subtitles=` filter if a captions file is given.

Why split extract + concat? Frame-accurate cuts on H.264 don't
preserve seekability with `-c copy` (cut points fall between
keyframes). We re-encode each cut once. Then the concat is either a
fast stream-copy (hard cuts) or a single xfade pass over already-h264
inputs (much faster than re-decoding the source).

For draft iterations on 4K HEVC source, --preset fast --crf 23 cuts
encode time ~3× with no review-relevant quality loss. Use --preset
medium --crf 18 for the final lock.

CUT LIST FORMATS

Two top-level JSON shapes are accepted (legacy list / dict-with-sources),
and within either, each cut entry takes one of two shapes:

  Range (default — when "type" is omitted or "range"):
    {"source": "X.mp4", "start": 12.5, "end": 38.0, "label": "..."}
    Extracts the [start, end] interval of source.

  Freeze (when "type" is "freeze"):
    {"type": "freeze", "source": "X.mp4", "at": 145.3, "duration": 2.0,
     "label": "trigger held"}
    Extracts a single frame from source at time `at`, then renders an
    N-second still segment (silent audio) that holds that frame. The
    freeze participates in the xfade chain like any other cut — cross-
    dissolves in and out cleanly. Annotate freeze segments by authoring
    the existing overlay types (arrow, text, box, stamp) in the
    overlays.json sidecar against the OUTPUT-timeline range
    corresponding to the freeze window; overlays.py needs no changes.

Top-level shapes:

  Legacy (list):
    [
      {"start": 12.5, "end": 38.0, "label": "..."},
      {"source": "synced/part2.mp4", "start": 5, "end": 24},
      {"type": "freeze", "source": "synced/part2.mp4", "at": 30, "duration": 1.5}
    ]
    Each cut may include "source" (overrides CLI source arg) and any
    of the optional per-cut overlay fields below.

  Multi-source (dict):
    {
      "sources": {
        "synced/part1.mp4": {"transcript": "...", "sync_offset": 4.6},
        "synced/part2.mp4": {"transcript": "...", "sync_offset": 6.8}
      },
      "cuts": [ ... ]
    }
    The "sources" mapping is consumed by make-subtitles.py for caption
    generation; cut.py itself only reads "cuts". The CLI source arg
    becomes the default; per-cut "source" still overrides.

PER-CUT OVERLAY FIELDS

Each cut may include:
  "section": "<text>"  — lower-third banner, ~3 s, fades. Use sparingly:
                          one per major narrative section, not every cut.
  "tool":    "<text>"  — small upper-right label, ~3 s. For the maker-
                          audience tool/material callouts ("WEN 8\"
                          benchtop drill press", "1/4 NPT tap").
  "label":   "<text>"  — log-only; printed during the run, not rendered.

USAGE

  ./tools/video-venv/bin/python marketing/video/cut.py \\
      <source-video> <cut-list.json> <output.mp4> \\
      [--preset PRESET] [--crf 0..51] \\
      [--fade SECONDS] \\
      [--title TEXT] [--title-duration SECONDS] \\
      [--captions PATH.ass] \\
      [--keep-parts]

Pure stdlib + ffmpeg + ffprobe. No numpy/scipy needed.
"""

import argparse
import contextlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import overlays as overlays_mod  # noqa: E402


def escape_drawtext(text: str) -> str:
    """Escape characters that have meaning in ffmpeg drawtext text= field.

    Chars that break drawtext: backslash, colon, percent. Newlines
    convert to drawtext's \\n.

    The ASCII apostrophe is mapped to a typographic right single quote
    (U+2019) rather than escaped. We wrap the value in single quotes
    (text='...'), and libavfilter's single-quoted token has no working
    backslash-escape for an embedded straight quote: `\\'` silently drops
    it (renders "Ive") and the shell-style `'\\''` terminates the token,
    spilling the rest of the filter options on screen as literal text.
    Both verified against list-arg ffmpeg (no shell layer). The curly
    quote needs no escaping and reads better in a burned-in title.
    """
    return (text
            .replace("\\", "\\\\")
            .replace(":", r"\:")
            .replace("'", "’")
            .replace("%", r"\%")
            .replace("\n", r"\n"))


def section_drawtext(text: str) -> str:
    """drawtext spec for a 'section label' lower-third banner."""
    escaped = escape_drawtext(text)
    return (
        f"drawtext="
        f"text='{escaped}':"
        f"font=Helvetica:fontsize=72:"
        f"fontcolor=white:bordercolor=black:borderw=4:"
        f"x=80:y=h-th-180:"
        f"enable='lt(t\\,3)'"
    )


def tool_drawtext(text: str) -> str:
    """drawtext spec for an upper-right tool/material annotation."""
    escaped = escape_drawtext(text)
    return (
        f"drawtext="
        f"text='{escaped}':"
        f"font=Helvetica:fontsize=44:"
        f"fontcolor=white:bordercolor=black:borderw=3:"
        f"x=w-tw-80:y=80:"
        f"enable='lt(t\\,3.5)'"
    )


def extract_segment(source: str, start: float, end: float, output: Path,
                    preset: str = "medium", crf: int = 18,
                    overlays: list[str] | None = None) -> None:
    """Re-encode a single [start, end] segment with optional drawtext overlays.

    -pix_fmt yuv420p forces the broadly-compatible chroma layout (some
    sources are yuv422p/yuv444p which break Safari/Quicktime/some browsers).
    -ar 48000 normalizes audio sample rate so the concat demuxer doesn't
    refuse to stream-copy across boundaries.

    `overlays` is a list of drawtext filter strings to chain (comma-
    separated) on the video stream. Order matters for layering.
    """
    cmd = [
        "ffmpeg", "-y",
        "-ss", f"{start:.3f}",
        "-to", f"{end:.3f}",
        "-i", source,
    ]
    if overlays:
        cmd += ["-vf", ",".join(overlays)]
    cmd += [
        "-c:v", "libx264", "-preset", preset, "-crf", str(crf),
        "-pix_fmt", "yuv420p",
        # Force stereo (-ac 2) so multi-source cut lists with mismatched
        # channel counts (e.g., GoPro mono camera audio + lav stereo)
        # still concat cleanly. acrossfade can't bridge mono↔stereo.
        # ffmpeg upmixes mono by duplicating the channel, no loss.
        "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2",
        "-loglevel", "error",
        str(output),
    ]
    subprocess.run(cmd, check=True)


def extract_freeze_segment(source: str, at: float, duration: float,
                           output: Path,
                           preset: str = "medium", crf: int = 18,
                           overlays: list[str] | None = None) -> None:
    """Render an N-second still-frame segment from `source` at time `at`.

    Pulls a single frame from the source at timestamp `at` (PNG to a
    temp file), then loops it for `duration` seconds against a silent
    stereo audio source. The output is encoded to match the
    resolution + frame rate + pixel format of the source so it slots
    into the xfade chain without scaling or rate conversion.

    xfade is strict about input timebase: a freeze rendered at 30 fps
    against 29.97 source content breaks the chain with "current rate
    of 1/0 is invalid" (the same failure mode noted in
    `concat_with_fade`). We probe the source's r_frame_rate and
    re-pin it on the looped output.

    Single-frame PNG round-trip vs. trim-and-freeze with `tpad`: PNG
    is simpler and lets us avoid seeking twice through a large
    source. The encode is cheap since libx264 collapses identical
    frames trivially.

    `overlays` follows the same convention as extract_segment — a
    list of drawtext filter strings chained after the freeze. The
    typical annotation path is overlay sidecar (arrow/text/box/stamp
    in overlays.json) authored against the OUTPUT timeline, not
    here; this hook exists for section/tool consistency with
    extract_segment.
    """
    width, height, fps_str = probe_video_meta(source)
    with tempfile.TemporaryDirectory() as tmp:
        frame_path = Path(tmp) / "frame.png"
        # Grab the single frame. -ss before -i is fast (input-seek);
        # frame accuracy is fine since `at` is authored against the
        # decoded source. -update 1 + -frames:v 1 writes one image.
        subprocess.run([
            "ffmpeg", "-y",
            "-ss", f"{at:.3f}",
            "-i", source,
            "-frames:v", "1", "-update", "1",
            "-loglevel", "error",
            str(frame_path),
        ], check=True)

        # Loop the PNG against silent stereo audio. -shortest clips
        # both to the audio's `-t` duration. fps filter pins CFR
        # output at the source's r_frame_rate so xfade sees a clean
        # rate downstream. scale ensures dimensions match exactly
        # even if the PNG decoder produced a slightly different size
        # (it shouldn't, but cheap insurance).
        vf_chain = [
            f"fps={fps_str}",
            f"scale={width}:{height}",
            "format=yuv420p",
        ]
        if overlays:
            vf_chain.extend(overlays)
        cmd = [
            "ffmpeg", "-y",
            "-loop", "1", "-i", str(frame_path),
            "-f", "lavfi",
            "-i", f"anullsrc=channel_layout=stereo:sample_rate=48000",
            "-t", f"{duration:.3f}",
            "-vf", ",".join(vf_chain),
            "-c:v", "libx264", "-preset", preset, "-crf", str(crf),
            "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2",
            "-shortest",
            "-loglevel", "error",
            str(output),
        ]
        subprocess.run(cmd, check=True)


def generate_title_clip(text: str, output: Path, duration: float = 2.0,
                        width: int = 1920, height: int = 1080,
                        fps: str = "30") -> None:
    """Generate a title-card mp4: dark background + large centered text.

    Uses lavfi color source for video and anullsrc for audio so the
    output is fully decodable and concat-compatible with the cut
    segments.

    `fps` is passed verbatim to lavfi's `r=` parameter — provide the
    source video's r_frame_rate string (e.g., "30000/1001" for NTSC
    29.97) so the title's timebase matches the content xfade will
    blend it with. lavfi's rate parser accepts both integers and
    fractions, so "30" and "30000/1001" both work.

    Background is near-black (#0a0a0a) rather than pure black so the
    text outline still reads if we ever scale this up.
    """
    escaped = escape_drawtext(text)
    drawtext = (
        f"drawtext="
        f"text='{escaped}':"
        f"font=Helvetica:fontsize=180:"
        f"fontcolor=white:bordercolor=black:borderw=5:"
        f"x=(w-text_w)/2:y=(h-text_h)/2"
    )
    cmd = [
        "ffmpeg", "-y",
        "-f", "lavfi",
        "-i", f"color=c=#0a0a0a:s={width}x{height}:d={duration}:r={fps}",
        "-f", "lavfi",
        "-i", f"anullsrc=channel_layout=stereo:sample_rate=48000:d={duration}",
        "-vf", drawtext,
        "-c:v", "libx264", "-preset", "fast", "-crf", "20",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "192k",
        "-t", f"{duration:.3f}",
        "-loglevel", "error",
        str(output),
    ]
    subprocess.run(cmd, check=True)


def probe_duration(path: Path) -> float:
    """Get the precise duration of a media file via ffprobe."""
    result = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", str(path)],
        capture_output=True, text=True, check=True,
    )
    return float(result.stdout.strip())


def probe_video_meta(path: Path) -> tuple[int, int, str]:
    """Get (width, height, fps_str) of the first video stream.

    fps_str is whatever ffprobe reports for r_frame_rate — typically a
    fraction like "30000/1001" for 29.97 NTSC content or "30/1" for true
    30 fps. Pass it back to ffmpeg verbatim (its rate parsers accept
    fractions natively) when you need exact timebase alignment with the
    source — e.g., generating a title card that will xfade against this
    source. xfade is strict about matching timebases between its inputs;
    a 30 fps title against 29.97 fps content silently breaks with
    "First input link main timebase ... do not match" before any frame
    is emitted.
    """
    result = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "v:0",
         "-show_entries", "stream=width,height,r_frame_rate",
         "-of", "csv=p=0", str(path)],
        capture_output=True, text=True, check=True,
    )
    parts = result.stdout.strip().split(",")
    return int(parts[0]), int(parts[1]), parts[2]


def concat_hard(segment_paths: list[Path], output: str,
                captions: str | None = None,
                preset: str = "medium", crf: int = 18) -> None:
    """Hard-cut concat. Stream-copy unless captions need burning in."""
    if captions:
        # Captions require a re-encode. Use concat filter rather than
        # demuxer so we can layer subtitles= after.
        cmd = ["ffmpeg", "-y"]
        for p in segment_paths:
            cmd += ["-i", str(p)]
        n = len(segment_paths)
        # concat filter: [0:v][0:a][1:v][1:a]...concat=n=N:v=1:a=1[v][a]
        inputs = "".join(f"[{i}:v][{i}:a]" for i in range(n))
        filter_complex = (
            f"{inputs}concat=n={n}:v=1:a=1[vc][a];"
            f"[vc]subtitles={captions}[v]"
        )
        cmd += [
            "-filter_complex", filter_complex,
            "-map", "[v]", "-map", "[a]",
            "-c:v", "libx264", "-preset", preset, "-crf", str(crf),
            "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
            "-loglevel", "error",
            output,
        ]
        subprocess.run(cmd, check=True)
        return

    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        for path in segment_paths:
            escaped = str(path.resolve()).replace("'", r"'\''")
            f.write(f"file '{escaped}'\n")
        list_path = f.name
    try:
        cmd = [
            "ffmpeg", "-y",
            "-f", "concat", "-safe", "0",
            "-i", list_path,
            "-c", "copy",
            "-loglevel", "error",
            output,
        ]
        subprocess.run(cmd, check=True)
    finally:
        Path(list_path).unlink(missing_ok=True)


def concat_with_fade(segment_paths: list[Path], output: str,
                     fade: float, preset: str, crf: int,
                     captions: str | None = None,
                     target_size: tuple[int, int] | None = None,
                     target_fps: str | None = None) -> None:
    """Cross-dissolve concat via xfade (video) + acrossfade (audio).

    Each transition consumes `fade` seconds from the END of the outgoing
    segment and the START of the incoming one. Total output duration is
    sum(segment durations) - (n-1) * fade. The xfade `offset` parameter
    is the cumulative timestamp of the transition START (i.e. the moment
    the dissolve begins), measured in the OUTPUT timeline of the chain
    so far.

    If `target_size` is given, every input is scaled to that resolution
    before xfade. xfade requires identical input sizes; the title card
    is typically 1080p while content segments are 4K, so we scale all
    to the title's resolution (or vice versa, given by caller).

    If `captions` is given, the subtitles= filter burns the ASS file
    into the final video stream.
    """
    n = len(segment_paths)
    if n == 1:
        # No fades possible.
        if captions:
            # Still need a re-encode pass to burn captions.
            cmd = [
                "ffmpeg", "-y",
                "-i", str(segment_paths[0]),
                "-vf", f"subtitles={captions}",
                "-c:v", "libx264", "-preset", preset, "-crf", str(crf),
                "-pix_fmt", "yuv420p",
                "-c:a", "copy",
                "-loglevel", "error",
                output,
            ]
            subprocess.run(cmd, check=True)
            return
        concat_hard(segment_paths, output)
        return

    durations = [probe_duration(p) for p in segment_paths]

    # Compute xfade offsets in cumulative OUTPUT timeline.
    offsets = []
    cum_out = 0.0
    for i in range(n - 1):
        cum_out += durations[i] - fade
        offsets.append(cum_out)

    # Pre-normalize every input's video stream. xfade is strict on its
    # inputs in three ways:
    #   1. constant frame rate (fps filter — without this, xfade errors
    #      with "current rate of 1/0 is invalid" on sources that have
    #      VFR or that have been touched by settb/setpts)
    #   2. matching timebase between adjacent inputs (settb=AVTB)
    #   3. matching SAR / size (setsar + scale+pad if target_size)
    # All three are easy to satisfy and the cost is tiny; not satisfying
    # them produces opaque late-stage failures. We always pin fps; pass
    # target_fps to align with source content (e.g., "30000/1001" for
    # NTSC 29.97), defaulting to 30 if no source is available.
    # Per-input video normalization for xfade. Empirical findings on
    # ffmpeg 7.1 with chained xfade:
    #   - `fps=<rate>` is required: xfade demands CFR.
    #   - `format=yuv420p` is required: makes pixel format explicit so
    #     xfade's output advertises a real rate (not 1/0).
    #   - `setpts=PTS-STARTPTS` BREAKS the chain: it resets timestamps
    #     in a way that destroys downstream rate metadata, even with
    #     fps still in the chain. The first xfade then errors out with
    #     "current rate of 1/0 is invalid". Don't add setpts here.
    #   - `setsar=1` is a no-op for our square-pixel sources and harmless
    #     when omitted.
    # If you ever need to align mismatched-resolution sources, the
    # scale+pad path here keeps the same fps,format minimum.
    fps = target_fps if target_fps else "30"
    scale_filters = []
    for i in range(n):
        if target_size:
            tw, th = target_size
            chain = (
                f"[{i}:v]fps={fps},"
                f"scale={tw}:{th}:force_original_aspect_ratio=decrease,"
                f"pad={tw}:{th}:(ow-iw)/2:(oh-ih)/2:color=black,"
                f"format=yuv420p[v{i}n]"
            )
        else:
            chain = f"[{i}:v]fps={fps},format=yuv420p[v{i}n]"
        scale_filters.append(chain)
    v_label = lambda i: f"v{i}n"

    # Build the video xfade chain.
    #
    # Subtle gotcha: ffmpeg's xfade does NOT propagate frame-rate metadata
    # from its inputs to its OUTPUT cleanly. Chaining xfades naively —
    # `[A][B]xfade=...[C]; [C][D]xfade=...` — breaks at the second
    # xfade with "current rate of 1/0 is invalid", because [C] is
    # advertising rate 0/0. The fix is to re-pin format and fps after
    # every xfade so the next xfade sees a CFR input. This adds two
    # filters per transition but is cheap (no actual sample work).
    # The very last xfade in the chain doesn't need it (its output goes
    # to the encoder which has its own rate handling).
    v_filters = []
    last_v = v_label(0)
    for i in range(n - 1):
        is_last_xfade = (i == n - 2)
        next_v = f"vx{i+1}" if (not is_last_xfade or captions) else "v"
        # Last xfade: skip the format+fps repair if going straight to
        # encoder (no captions). With captions, we keep the repair so
        # the subtitles filter sees a clean stream.
        repair = "" if (is_last_xfade and not captions) else \
                 f",format=yuv420p,fps={fps}"
        v_filters.append(
            f"[{last_v}][{v_label(i+1)}]"
            f"xfade=transition=fade:duration={fade}:offset={offsets[i]:.3f}"
            f"{repair}"
            f"[{next_v}]"
        )
        last_v = next_v

    # If captions, apply subtitles filter to the final (already
    # rate-repaired) video stream.
    if captions:
        v_filters.append(f"[{last_v}]subtitles={captions}[v]")

    a_filters = []
    last_a = "0:a"
    for i in range(n - 1):
        next_a = f"a{i+1}" if i < n - 2 else "a"
        a_filters.append(
            f"[{last_a}][{i+1}:a]acrossfade=d={fade}[{next_a}]"
        )
        last_a = next_a

    filter_complex = ";".join(scale_filters + v_filters + a_filters)

    cmd = ["ffmpeg", "-y"]
    for p in segment_paths:
        cmd += ["-i", str(p)]
    cmd += [
        "-filter_complex", filter_complex,
        "-map", "[v]", "-map", "[a]",
        "-c:v", "libx264", "-preset", preset, "-crf", str(crf),
        "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
        "-loglevel", "error",
        output,
    ]
    subprocess.run(cmd, check=True)


@contextlib.contextmanager
def parts_dir(output: str, keep: bool):
    """Yield a directory for per-segment files. Persistent if keep=True."""
    if keep:
        d = Path(output + ".parts")
        d.mkdir(exist_ok=True)
        yield d
    else:
        with tempfile.TemporaryDirectory() as tmp:
            yield Path(tmp)


def main():
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    ap.add_argument("source", help="Default source video file (per-cut 'source' overrides)")
    ap.add_argument("cut_list", help="Cut list JSON (list or dict-with-sources format)")
    ap.add_argument("output", help="Output video file")
    ap.add_argument("--keep-parts", action="store_true",
                    help="Keep per-segment intermediate files in <output>.parts/")
    ap.add_argument("--preset", default="medium",
                    choices=["ultrafast", "superfast", "veryfast", "faster",
                             "fast", "medium", "slow", "slower", "veryslow"],
                    help="libx264 preset. Use 'fast' for draft iterations "
                         "(~3× faster on 4K source). Default 'medium' for final.")
    ap.add_argument("--crf", type=int, default=18,
                    help="libx264 CRF (0=lossless, 18=visually-lossless, "
                         "23=ffmpeg default, 28=YouTube-acceptable). Default 18.")
    ap.add_argument("--fade", type=float, default=0.0,
                    help="Cross-dissolve duration in seconds at every cut "
                         "boundary. 0 = hard cuts (default). 0.3–0.5 is the "
                         "modern-doc sweet spot.")
    ap.add_argument("--title", default=None,
                    help="Title text for an opening title card. If given, a "
                         "still card with this text is prepended to the output.")
    ap.add_argument("--title-duration", type=float, default=2.0,
                    help="Title card duration in seconds (default 2.0).")
    ap.add_argument("--captions", default=None,
                    help="Path to an ASS subtitle file to burn into the final "
                         "video. Generate with make-subtitles.py.")
    ap.add_argument("--overlays", default=None,
                    help="Path to an overlay sidecar JSON (motion-graphics "
                         "layer: text callouts, HUD, lower thirds, stamps, "
                         "pip, magnifier). See overlays.py for the schema. "
                         "When set, captions are burned in the same final "
                         "pass as the overlays.")
    args = ap.parse_args()

    raw = json.loads(Path(args.cut_list).read_text())
    if isinstance(raw, dict):
        cuts = raw["cuts"]
    else:
        cuts = raw
    if not cuts:
        print("Cut list is empty — nothing to do.", file=sys.stderr)
        sys.exit(1)

    with parts_dir(args.output, args.keep_parts) as d:
        segment_paths = []

        # Optionally generate title card as the FIRST segment so it
        # participates in the xfade chain (title fades into seg 1).
        # Render at the same resolution as the first content source so
        # xfade doesn't have to scale anything (xfade requires
        # identical input sizes).
        if args.title:
            first_src = cuts[0].get("source", args.source)
            title_w, title_h, title_fps = probe_video_meta(first_src)
            print(f"Generating title card '{args.title}' "
                  f"({args.title_duration}s, {title_w}x{title_h} @ {title_fps})",
                  file=sys.stderr)
            title_path = d / "part-000-title.mp4"
            generate_title_clip(args.title, title_path,
                                duration=args.title_duration,
                                width=title_w, height=title_h,
                                fps=title_fps)
            segment_paths.append(title_path)

        for i, cut in enumerate(cuts, 1):
            seg_out = d / f"part-{i:03d}.mp4"
            label_descr = cut.get("label", "")
            section = cut.get("section")
            tool = cut.get("tool")
            cut_type = cut.get("type", "range")
            extras = []
            if section:
                extras.append(f"section={section!r}")
            if tool:
                extras.append(f"tool={tool!r}")
            extras_str = f"  [{', '.join(extras)}]" if extras else ""
            label_str = f"  ({label_descr})" if label_descr else ""

            overlays = []
            if section:
                overlays.append(section_drawtext(section))
            if tool:
                overlays.append(tool_drawtext(tool))

            cut_source = cut.get("source", args.source)
            if cut_type == "freeze":
                print(f"  segment {i}/{len(cuts)}: freeze "
                      f"@ {cut['at']:.2f}s for {cut['duration']:.2f}s"
                      f"{label_str}{extras_str}",
                      file=sys.stderr)
                extract_freeze_segment(cut_source, cut["at"], cut["duration"],
                                       seg_out,
                                       preset=args.preset, crf=args.crf,
                                       overlays=overlays or None)
            else:
                print(f"  segment {i}/{len(cuts)}: "
                      f"{cut['start']:.2f}–{cut['end']:.2f}s"
                      f"{label_str}{extras_str}",
                      file=sys.stderr)
                extract_segment(cut_source, cut["start"], cut["end"], seg_out,
                                preset=args.preset, crf=args.crf,
                                overlays=overlays or None)
            segment_paths.append(seg_out)

        # All segments share the same resolution (title was rendered
        # to match the first content source). target_size=None skips
        # the scale+pad step. We do still pass target_fps so the fps
        # filter pins frame rate to match the source's r_frame_rate
        # rather than defaulting to 30 fps and double-converting.
        target_size = None
        target_fps = None
        if cuts:
            first_src = cuts[0].get("source", args.source)
            _, _, target_fps = probe_video_meta(first_src)

        # When overlays are requested, concat goes to an intermediate file
        # and a final pass applies overlays + captions together. Otherwise
        # captions get burned in during the concat pass directly (one fewer
        # encode for the common case of no overlays).
        if args.overlays:
            concat_target = str(d / "concat.mp4")
            concat_captions = None  # deferred to overlay pass
        else:
            concat_target = args.output
            concat_captions = args.captions

        if args.fade > 0:
            print(f"Concat with {args.fade:.2f}s cross-dissolves "
                  f"({len(segment_paths)} segments) → {concat_target}",
                  file=sys.stderr)
            concat_with_fade(segment_paths, concat_target, args.fade,
                             preset=args.preset, crf=args.crf,
                             captions=concat_captions,
                             target_size=target_size,
                             target_fps=target_fps)
        else:
            print(f"Hard-cut concat ({len(segment_paths)} segments) "
                  f"→ {concat_target}", file=sys.stderr)
            concat_hard(segment_paths, concat_target, captions=concat_captions,
                        preset=args.preset, crf=args.crf)

        if args.overlays:
            print(f"Applying overlays from {args.overlays} → {args.output}",
                  file=sys.stderr)
            overlays_mod.render(
                concat_target, args.overlays, args.output,
                captions=args.captions,
                preset=args.preset, crf=args.crf,
            )

    # Sum runtime across mixed range/freeze entries: range cuts have
    # [start, end], freeze cuts have a fixed duration.
    total = sum(
        c["duration"] if c.get("type") == "freeze" else c["end"] - c["start"]
        for c in cuts
    )
    if args.title:
        total += args.title_duration
    if args.fade > 0:
        n_transitions = len(cuts) + (1 if args.title else 0) - 1
        total -= n_transitions * args.fade
    print(f"wrote {args.output}  ({total:.1f}s total, "
          f"{len(cuts)} cuts{' + title' if args.title else ''})",
          file=sys.stderr)


if __name__ == "__main__":
    main()
