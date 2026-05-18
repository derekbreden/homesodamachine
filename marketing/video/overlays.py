#!/usr/bin/env python3
"""
overlays.py — render motion-graphics overlays onto a cut.py output video.

Reads an overlay sidecar JSON keyed against the OUTPUT (post-concat) timeline
and applies overlays via a single ffmpeg filter graph in one re-encode pass.

Authoring is done against output timestamps because that is the timeline a
human reviews: when you watch the rough draft and decide "the parameter
callout should land at 0:32," 0:32 is what you write down. The renderer does
no timeline translation.

USAGE (standalone)

  ./tools/video-venv/bin/python marketing/video/overlays.py \\
      <input.mp4> <sidecar.json> <output.mp4> \\
      [--captions PATH.ass] [--preset PRESET] [--crf N]

USAGE (from cut.py)

  Pass --overlays <sidecar.json> to cut.py. cut.py writes a concat
  intermediate, then calls this module as a final pass. The captions
  filter, if any, is applied in the same pass.

SIDECAR SCHEMA

Top-level:

  {
    "default_font": "Helvetica",   # optional
    "overlays": [ ...entries... ]
  }

Each entry has:
  "type":  one of: text | stamp | lower_third | hud | box | pip | magnifier
  "t":     [start_sec, end_sec] in OUTPUT timeline
  "fade":  optional seconds for ease in/out; default 0.25 (use 0 for hard cut)

POSITION VOCABULARY (used by text / stamp / lower_third / hud / pip)
  "top-left" | "top-right" | "bottom-left" | "bottom-right"
  "center"   | "top-center" | "bottom-center"
  [x, y]     — absolute pixel coordinates in OUTPUT video space

OVERLAY TYPES — implemented

text
  text:     str (single line; "\\n" inserts a line break)
  position: position spec, default "top-left"
  size:     int font size, default 56
  color:    str color, default "white"
  border:   bool, default true (4 px black outline)

stamp
  Large impact text with optional filled background panel. Use for STUCK,
  CLEAN BREAK, single-word reactions.
  text:     str
  position: default "center"
  size:     int, default 200
  color:    default "white"
  bg:       optional fill color (e.g. "#cc0000"); 40 px padding around text
  bg_alpha: 0..1 background opacity, default 0.85

lower_third
  Two-line banner anchored to a corner.
  primary:        str
  secondary:      optional str
  position:       "bottom-left" (default) | "bottom-right" | "top-left" | "top-right"
  primary_size:   int, default 64
  secondary_size: int, default 36

hud
  Persistent labeled-value table pinned in a corner. Use for parameter
  readouts visible during action.
  position:     default "top-right"
  rows:         [["LABEL", "VALUE"], ...]
  label_color:  default "#aaaaaa"
  value_color:  default "white"
  row_size:     int font size, default 36

box
  Outlined rectangle for highlighting something in frame. OUTPUT pixels.
  rect:      [x, y, w, h]
  color:     default "yellow"
  thickness: int px, default 4

pip
  Picture-in-picture inset of a static image. Path resolved relative to
  the sidecar's directory.
  source:    path/to/image.png
  position:  default "bottom-right"
  size:      [w, h] in output pixels, default [480, 270]
  border:    optional color for a 4 px border, default null
  border_w:  int px, default 4

magnifier
  Zoomed inset of a region of the MAIN video itself.
  source_rect: [x, y, w, h] in main-frame coords
  dest_rect:   [x, y, w, h] in main-frame coords
  border:      optional color, default "white"
  border_w:    int px, default 4

OVERLAY TYPES — schema reserved, not yet implemented

  arrow     — needs Pillow for clean arrowhead. Defer.
  kenburns  — pan/zoom on a still-photo segment. Defer.
  diagram   — composited generated image; same shape as pip. Use pip
              with a pre-generated PNG until a diagram generator lands.

NOTES

- All time-gated filters use `enable='between(t,start,end)'`.
- Fade is an alpha expression for drawtext, or a fade= filter for image
  overlays. A linear ramp is fine for the durations we care about.
- The renderer emits one filter_complex and runs ffmpeg once. Adds one
  re-encode over cut.py's concat output; iteration is still cheap.
- Overlays are layered in declared order; later entries draw on top.

Pure stdlib + ffmpeg. No Pillow / numpy required for the implemented types.
"""

import argparse
import json
import shlex
import subprocess
import sys
from pathlib import Path
from typing import Any

DEFAULT_FONT = "Helvetica"
DEFAULT_FADE = 0.25
DEFAULT_MARGIN = 40


# ---------- escaping & expressions ----------

def escape_drawtext(text: str) -> str:
    """Escape characters that have meaning in ffmpeg drawtext text= field.

    NOTE: we set `expansion=none` on every drawtext we emit, which disables
    the format-string interpretation of `%`. So we do NOT escape `%` —
    escaping it with `\\%` would produce a literal backslash-percent on
    screen when expansion is off. This is a deliberate difference from
    cut.py.escape_drawtext (which doesn't disable expansion).
    """
    return (text
            .replace("\\", "\\\\")
            .replace(":", r"\:")
            .replace("'", r"\\\'")
            .replace("\n", r"\n"))


def enable_expr(t: list[float]) -> str:
    """`between(t,s,e)` with the commas escaped for drawtext's enable=."""
    return f"between(t\\,{t[0]:.3f}\\,{t[1]:.3f})"


def alpha_expr(t: list[float], fade: float) -> str | None:
    """Alpha (0..1) for fade-in then fade-out. None if fade <= 0.

    Expression is only evaluated inside the enable window (outside is
    masked), so we don't need to handle the outside case.
    """
    if fade <= 0:
        return None
    s, e = t
    return (f"if(lt(t-{s:.3f}\\,{fade:.3f})\\,(t-{s:.3f})/{fade:.3f}\\,"
            f"if(lt({e:.3f}-t\\,{fade:.3f})\\,({e:.3f}-t)/{fade:.3f}\\,1))")


# ---------- anchoring ----------

def anchor_text(position, margin: int = DEFAULT_MARGIN) -> tuple[str, str]:
    """For drawtext: returns (x_expr, y_expr) using text_w / text_h / w / h."""
    if isinstance(position, (list, tuple)):
        return str(position[0]), str(position[1])
    presets = {
        "top-left":      (f"{margin}",                f"{margin}"),
        "top-right":     (f"w-text_w-{margin}",       f"{margin}"),
        "bottom-left":   (f"{margin}",                f"h-text_h-{margin}"),
        "bottom-right":  (f"w-text_w-{margin}",       f"h-text_h-{margin}"),
        "center":        (f"(w-text_w)/2",            f"(h-text_h)/2"),
        "top-center":    (f"(w-text_w)/2",            f"{margin}"),
        "bottom-center": (f"(w-text_w)/2",            f"h-text_h-{margin}"),
    }
    if position not in presets:
        raise ValueError(f"Unknown position {position!r}")
    return presets[position]


def anchor_overlay(position, ovr_w, ovr_h,
                   margin: int = DEFAULT_MARGIN) -> tuple[str, str]:
    """For overlay/drawbox: returns (x_expr, y_expr) using main_w / main_h.

    ovr_w / ovr_h are the overlay's dimensions (int or expression string).
    """
    if isinstance(position, (list, tuple)):
        return str(position[0]), str(position[1])
    presets = {
        "top-left":      (f"{margin}",                       f"{margin}"),
        "top-right":     (f"main_w-{ovr_w}-{margin}",        f"{margin}"),
        "bottom-left":   (f"{margin}",                       f"main_h-{ovr_h}-{margin}"),
        "bottom-right":  (f"main_w-{ovr_w}-{margin}",        f"main_h-{ovr_h}-{margin}"),
        "center":        (f"(main_w-{ovr_w})/2",             f"(main_h-{ovr_h})/2"),
        "top-center":    (f"(main_w-{ovr_w})/2",             f"{margin}"),
        "bottom-center": (f"(main_w-{ovr_w})/2",             f"main_h-{ovr_h}-{margin}"),
    }
    if position not in presets:
        raise ValueError(f"Unknown position {position!r}")
    return presets[position]


# ---------- per-type filter emitters ----------
#
# Each emitter returns a list of drawtext/drawbox/etc. filter specs to be
# joined with commas into one chain that operates on the main video stream.
# All these types are pure "draw on top" — they don't need extra inputs.
#
# pip and magnifier are handled separately by the main renderer because
# they need an extra input or a split branch.


def emit_text(entry: dict, font: str) -> list[str]:
    text = entry["text"]
    pos = entry.get("position", "top-left")
    size = entry.get("size", 56)
    color = entry.get("color", "white")
    border = entry.get("border", True)
    fade = entry.get("fade", DEFAULT_FADE)
    t = entry["t"]

    x, y = anchor_text(pos)
    parts = [
        # `drawtext=expansion=none` disables the format parser so `%`
        # renders literally. Done in every emit_* below.
        f"drawtext=expansion=none:text='{escape_drawtext(text)}'",
        f"font={font}",
        f"fontsize={size}",
        f"fontcolor={color}",
    ]
    if border:
        parts.append("bordercolor=black")
        parts.append("borderw=4")
    parts.append(f"x={x}")
    parts.append(f"y={y}")
    parts.append(f"enable='{enable_expr(t)}'")
    alpha = alpha_expr(t, fade)
    if alpha:
        parts.append(f"alpha='{alpha}'")
    return [":".join(parts)]


def emit_stamp(entry: dict, font: str) -> list[str]:
    text = entry["text"]
    pos = entry.get("position", "center")
    size = entry.get("size", 200)
    color = entry.get("color", "white")
    bg = entry.get("bg")
    bg_alpha = entry.get("bg_alpha", 0.85)
    fade = entry.get("fade", DEFAULT_FADE)
    t = entry["t"]

    x, y = anchor_text(pos)
    parts = [
        f"drawtext=expansion=none:text='{escape_drawtext(text)}'",
        f"font={font}",
        f"fontsize={size}",
        f"fontcolor={color}",
        "bordercolor=black",
        f"borderw={6 if not bg else 4}",
    ]
    if bg:
        parts += [
            "box=1",
            f"boxcolor={bg}@{bg_alpha}",
            "boxborderw=40",
        ]
    parts += [
        f"x={x}",
        f"y={y}",
        f"enable='{enable_expr(t)}'",
    ]
    alpha = alpha_expr(t, fade)
    if alpha:
        parts.append(f"alpha='{alpha}'")
    return [":".join(parts)]


def emit_lower_third(entry: dict, font: str) -> list[str]:
    primary = entry["primary"]
    secondary = entry.get("secondary", "")
    pos = entry.get("position", "bottom-left")
    p_size = entry.get("primary_size", 64)
    s_size = entry.get("secondary_size", 36)
    fade = entry.get("fade", DEFAULT_FADE)
    t = entry["t"]

    line_h = int(p_size * 1.15)
    is_bottom = pos.startswith("bottom")

    # Anchor each line independently. For bottom-anchored, primary sits
    # one line UP from the bottom margin; secondary sits at the bottom
    # margin. For top-anchored, primary at top margin; secondary one line
    # down.
    px, _ = anchor_text(pos)
    sx, _ = anchor_text(pos)
    if is_bottom:
        py = f"h-text_h-{DEFAULT_MARGIN + line_h}"
        sy = f"h-text_h-{DEFAULT_MARGIN}"
    else:
        py = f"{DEFAULT_MARGIN}"
        sy = f"{DEFAULT_MARGIN + line_h}"

    alpha = alpha_expr(t, fade)
    alpha_part = f":alpha='{alpha}'" if alpha else ""

    filters = [
        f"drawtext=expansion=none:text='{escape_drawtext(primary)}':"
        f"font={font}:fontsize={p_size}:fontcolor=white:"
        f"bordercolor=black:borderw=4:"
        f"x={px}:y={py}:enable='{enable_expr(t)}'{alpha_part}"
    ]
    if secondary:
        filters.append(
            f"drawtext=expansion=none:text='{escape_drawtext(secondary)}':"
            f"font={font}:fontsize={s_size}:fontcolor=#cccccc:"
            f"bordercolor=black:borderw=3:"
            f"x={sx}:y={sy}:enable='{enable_expr(t)}'{alpha_part}"
        )
    return filters


def emit_hud(entry: dict, font: str) -> list[str]:
    pos = entry.get("position", "top-right")
    rows = entry["rows"]
    row_size = entry.get("row_size", 36)
    label_color = entry.get("label_color", "#aaaaaa")
    value_color = entry.get("value_color", "white")
    label_col_w = entry.get("label_col_w", int(row_size * 6))
    fade = entry.get("fade", DEFAULT_FADE)
    t = entry["t"]

    line_h = int(row_size * 1.3)
    n = len(rows)
    block_h = line_h * n

    # Per-row positions. The block is anchored as a whole; each row's y
    # is computed from the block anchor + row index.
    if pos in ("top-left", "top-center", "top-right"):
        base_y = DEFAULT_MARGIN
        row_y = lambda i: f"{base_y + i * line_h}"
    else:  # bottom-anchored
        row_y = lambda i: f"h-{row_size}-{DEFAULT_MARGIN + (n - 1 - i) * line_h}"

    # Column x-anchors. Left-anchored is simple. Right-anchored: the
    # value column hugs the right edge (each value's own text_w is used),
    # the label column is offset left by `label_col_w` from a notional
    # value-column-right edge. For symmetry we pick a fixed value-column
    # right edge (the frame right minus margin) and place the label
    # `label_col_w` to its left.
    if pos in ("top-left", "bottom-left", "top-center", "bottom-center"):
        if pos.endswith("center"):
            label_x_fn = lambda label: f"(w/2)-{label_col_w}+(({label_col_w}-text_w)/2)"
            value_x_fn = lambda value: f"(w/2)+20"
        else:
            label_x_fn = lambda label: f"{DEFAULT_MARGIN}"
            value_x_fn = lambda value: f"{DEFAULT_MARGIN + label_col_w}"
    else:  # right-anchored
        # value: right edge at w - margin
        value_x_fn = lambda value: f"w-text_w-{DEFAULT_MARGIN}"
        # label: right edge at w - margin - 200 (value column reserve)
        # with text_w of the label, x = w - text_w - margin - 200 - label_col_w_extra
        # Simpler: anchor LABEL right edge at value_x_left - small_gap.
        # We can't reference another drawtext's x in ffmpeg, so we put
        # labels at a fixed x = w - margin - label_col_w (left edge of
        # label column).
        label_x_fn = lambda label: f"w-{label_col_w}-{DEFAULT_MARGIN + 200}"

    alpha = alpha_expr(t, fade)
    alpha_part = f":alpha='{alpha}'" if alpha else ""

    filters = []
    for i, (label, value) in enumerate(rows):
        y = row_y(i)
        filters.append(
            f"drawtext=expansion=none:text='{escape_drawtext(label)}':"
            f"font={font}:fontsize={row_size}:fontcolor={label_color}:"
            f"bordercolor=black:borderw=3:"
            f"x={label_x_fn(label)}:y={y}:enable='{enable_expr(t)}'{alpha_part}"
        )
        filters.append(
            f"drawtext=expansion=none:text='{escape_drawtext(value)}':"
            f"font={font}:fontsize={row_size}:fontcolor={value_color}:"
            f"bordercolor=black:borderw=3:"
            f"x={value_x_fn(value)}:y={y}:enable='{enable_expr(t)}'{alpha_part}"
        )
    return filters


def emit_box(entry: dict) -> list[str]:
    x, y, w, h = entry["rect"]
    color = entry.get("color", "yellow")
    thickness = entry.get("thickness", 4)
    t = entry["t"]
    return [
        f"drawbox=x={x}:y={y}:w={w}:h={h}:"
        f"color={color}:thickness={thickness}:"
        f"enable='{enable_expr(t)}'"
    ]


# ---------- pip / magnifier (need their own filter_complex branches) ----------

def emit_pip_branch(entry: dict, sidecar_dir: Path, input_idx: int,
                    out_label: str) -> tuple[str, list[str]]:
    """Build a filter_complex branch for one pip overlay.

    Returns (branch_filter_str, extra_ffmpeg_input_args).
    The branch consumes `[<input_idx>:v]` (the pre-declared image input)
    and produces `[<out_label>]`, a stream ready for overlay onto main.
    """
    src = (sidecar_dir / entry["source"]).resolve()
    if not src.exists():
        raise FileNotFoundError(f"pip source not found: {src}")
    w, h = entry.get("size", [480, 270])
    border = entry.get("border")
    border_w = entry.get("border_w", 4)
    fade = entry.get("fade", DEFAULT_FADE)
    s, e = entry["t"]
    dur = e - s

    # Pre-process the image stream: scale, optional border, fade in/out.
    parts = [f"[{input_idx}:v]scale={w}:{h}"]
    if border:
        pad_w, pad_h = w + 2 * border_w, h + 2 * border_w
        parts[0] += f",pad={pad_w}:{pad_h}:{border_w}:{border_w}:color={border}"
    if fade > 0:
        # The image stream's local timeline starts at 0 (loop input). Fade
        # in at start, fade out at (dur - fade). The overlay's enable=
        # gates when it's actually composited, so fade values that fall
        # outside the enable window are simply discarded.
        parts[0] += (f",fade=t=in:st=0:d={fade},"
                     f"fade=t=out:st={max(0, dur - fade):.3f}:d={fade}")
    parts[0] += f"[{out_label}]"
    branch = parts[0]
    extra_input = ["-loop", "1", "-i", str(src)]
    return branch, extra_input


def emit_pip_overlay(entry: dict, pip_label: str,
                     in_label: str, out_label: str) -> str:
    """Build the overlay= statement that composites a pre-processed pip
    onto the main video stream.

    `pip_label` is the output of emit_pip_branch.
    `in_label` is the current main video stream label.
    `out_label` is the new main video stream label after this overlay.
    """
    pos = entry.get("position", "bottom-right")
    w, h = entry.get("size", [480, 270])
    if entry.get("border"):
        border_w = entry.get("border_w", 4)
        w += 2 * border_w
        h += 2 * border_w
    x_expr, y_expr = anchor_overlay(pos, w, h)
    t = entry["t"]
    return (
        f"[{in_label}][{pip_label}]"
        f"overlay=x={x_expr}:y={y_expr}:"
        f"enable='{enable_expr(t)}'"
        f"[{out_label}]"
    )


def emit_magnifier(entry: dict, in_label: str, out_label: str,
                   tmp_label_prefix: str) -> list[str]:
    """Build filter statements for one magnifier overlay.

    Magnifier needs to split the main stream, crop+scale one copy, then
    overlay it back onto the other. Returns a list of filter statements.
    """
    sx, sy, sw, sh = entry["source_rect"]
    dx, dy, dw, dh = entry["dest_rect"]
    border = entry.get("border", "white")
    border_w = entry.get("border_w", 4)
    fade = entry.get("fade", DEFAULT_FADE)
    t = entry["t"]

    main_a = f"{tmp_label_prefix}_main"
    main_b = f"{tmp_label_prefix}_src"
    mag = f"{tmp_label_prefix}_mag"

    # Step 1: split current main into two streams.
    split_stmt = f"[{in_label}]split=2[{main_a}][{main_b}]"

    # Step 2: crop+scale the second stream into the magnified inset, with
    # optional bordering frame around it.
    crop_parts = [f"[{main_b}]crop={sw}:{sh}:{sx}:{sy},scale={dw}:{dh}"]
    if border:
        pw, ph = dw + 2 * border_w, dh + 2 * border_w
        crop_parts[0] += f",pad={pw}:{ph}:{border_w}:{border_w}:color={border}"
    if fade > 0:
        # Fade is applied locally on the inset; the enable window gates
        # the actual composition.
        dur = t[1] - t[0]
        crop_parts[0] += (f",fade=t=in:st={t[0]:.3f}:d={fade},"
                          f"fade=t=out:st={max(0, t[1] - fade):.3f}:d={fade}")
    crop_parts[0] += f"[{mag}]"

    # Step 3: overlay magnified inset onto the unchanged copy.
    eff_dx = dx - (border_w if border else 0)
    eff_dy = dy - (border_w if border else 0)
    overlay_stmt = (
        f"[{main_a}][{mag}]"
        f"overlay=x={eff_dx}:y={eff_dy}:"
        f"enable='{enable_expr(t)}'"
        f"[{out_label}]"
    )

    return [split_stmt, crop_parts[0], overlay_stmt]


# ---------- top-level renderer ----------

DRAWLIKE_TYPES = {"text", "stamp", "lower_third", "hud", "box"}


def build_filter_graph(sidecar: dict, sidecar_dir: Path,
                       captions: str | None = None) -> tuple[str, list[str]]:
    """Build a complete filter_complex string + the extra ffmpeg input args.

    The graph's main video input is assumed to be `[0:v]`. The graph's
    final video stream is labelled `[vout]`.

    Returns (filter_complex, extra_inputs_flat).
    """
    font = sidecar.get("default_font", DEFAULT_FONT)
    overlays = sidecar.get("overlays", [])

    statements: list[str] = []
    extra_inputs: list[str] = []
    # Stream label currently representing the main video.
    cur = "0:v"
    # Counter for unique input indices (1-indexed; 0 is the main video).
    next_input_idx = 1
    # Counter for unique label names.
    next_stage = 0

    # Group consecutive draw-like overlays into one drawtext/drawbox chain
    # for efficiency (one ffmpeg filter node per group rather than per
    # overlay). pip and magnifier break the chain because they need extra
    # inputs or splits.
    drawlike_buf: list[str] = []

    def flush_drawlike():
        nonlocal cur, next_stage, drawlike_buf
        if not drawlike_buf:
            return
        out = f"v{next_stage}"
        next_stage += 1
        chain = ",".join(drawlike_buf)
        statements.append(f"[{cur}]{chain}[{out}]")
        cur = out
        drawlike_buf = []

    for entry in overlays:
        t = entry["type"]
        if t == "text":
            drawlike_buf.extend(emit_text(entry, font))
        elif t == "stamp":
            drawlike_buf.extend(emit_stamp(entry, font))
        elif t == "lower_third":
            drawlike_buf.extend(emit_lower_third(entry, font))
        elif t == "hud":
            drawlike_buf.extend(emit_hud(entry, font))
        elif t == "box":
            drawlike_buf.extend(emit_box(entry))
        elif t == "pip":
            flush_drawlike()
            pip_label = f"pip{next_input_idx}"
            branch_stmt, ffmpeg_in = emit_pip_branch(
                entry, sidecar_dir, next_input_idx, pip_label)
            statements.append(branch_stmt)
            extra_inputs.extend(ffmpeg_in)
            next_input_idx += 1
            out = f"v{next_stage}"
            next_stage += 1
            statements.append(emit_pip_overlay(entry, pip_label, cur, out))
            cur = out
        elif t == "magnifier":
            flush_drawlike()
            out = f"v{next_stage}"
            tmp = f"m{next_stage}"
            next_stage += 1
            statements.extend(emit_magnifier(entry, cur, out, tmp))
            cur = out
        else:
            raise ValueError(f"Unknown overlay type {t!r}")

    flush_drawlike()

    # Captions go on top of everything overlay-wise.
    if captions:
        out = "vout"
        # subtitles filter requires the .ass path; we escape the colon in
        # the path (Windows drive letters etc.) but on macOS / Linux it's
        # rarely needed. Wrap in single quotes just in case.
        cap_escaped = captions.replace("'", r"\\\'")
        statements.append(f"[{cur}]subtitles='{cap_escaped}'[{out}]")
        cur = out
    else:
        # Rename the final stream to vout for a consistent map target.
        # Trivial null filter is cheaper than another encode pass.
        out = "vout"
        statements.append(f"[{cur}]null[{out}]")

    return ";".join(statements), extra_inputs


def render(input_video: str, sidecar_path: str, output_video: str,
           captions: str | None = None,
           preset: str = "medium", crf: int = 18,
           dry_run: bool = False) -> None:
    """Apply a sidecar to an input video, writing output_video.

    If dry_run, print the assembled ffmpeg command and return without
    invoking it. Useful for inspecting the filter graph during authoring.
    """
    sidecar_path_p = Path(sidecar_path)
    sidecar = json.loads(sidecar_path_p.read_text())
    sidecar_dir = sidecar_path_p.parent

    filter_complex, extra_inputs = build_filter_graph(
        sidecar, sidecar_dir, captions=captions)

    cmd = ["ffmpeg", "-y", "-i", input_video]
    cmd += extra_inputs
    cmd += [
        "-filter_complex", filter_complex,
        "-map", "[vout]", "-map", "0:a",
        "-c:v", "libx264", "-preset", preset, "-crf", str(crf),
        "-pix_fmt", "yuv420p",
        "-c:a", "copy",
        "-shortest",  # extra image inputs are looped; bound to main video
        "-loglevel", "error",
        output_video,
    ]

    if dry_run:
        print(" ".join(shlex.quote(c) for c in cmd))
        return
    subprocess.run(cmd, check=True)


def main():
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    ap.add_argument("input", help="Input video (typically cut.py's concat output)")
    ap.add_argument("sidecar", help="Overlay sidecar JSON")
    ap.add_argument("output", help="Output video")
    ap.add_argument("--captions", default=None,
                    help="Optional ASS subtitle file to burn in alongside overlays.")
    ap.add_argument("--preset", default="medium",
                    choices=["ultrafast", "superfast", "veryfast", "faster",
                             "fast", "medium", "slow", "slower", "veryslow"])
    ap.add_argument("--crf", type=int, default=18)
    ap.add_argument("--dry-run", action="store_true",
                    help="Print the ffmpeg command without running it.")
    args = ap.parse_args()

    render(args.input, args.sidecar, args.output,
           captions=args.captions, preset=args.preset, crf=args.crf,
           dry_run=args.dry_run)
    if not args.dry_run:
        print(f"wrote {args.output}", file=sys.stderr)


if __name__ == "__main__":
    main()
