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
                   | arrow | param | title
  "t":     [start_sec, end_sec] in OUTPUT timeline
  "fade":  optional seconds for ease in/out; default 0.25 (use 0 for hard cut)
           — title defaults to 0.6 for a presented-not-flashed feel.

POSITION VOCABULARY (used by text / stamp / lower_third / hud / pip / param
                              / title)
  "top-left"  | "top-right"  | "bottom-left" | "bottom-right"
  "center"    | "top-center" | "bottom-center"
  "left-mid"  | "right-mid"  (param only — vertically centered on the side)
  [x, y]      — absolute pixel coordinates in OUTPUT video space

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

arrow
  Straight line + filled triangle arrowhead. Rendered to a transparent
  PNG via Pillow and composited like a pip. OUTPUT pixels.
  from:           [x, y] tail
  to:             [x, y] head
  color:          default "yellow"
  thickness:      int px, default 6
  arrowhead_size: int px (length of triangle), default 30

param
  Anchored panel-style parameter callout. Pillow-rendered with rounded
  corners, drop shadow, accent stripe, and a label / value / optional
  note hierarchy. Use for parameter readouts during explainer footage
  (welder settings, dimensions, recipe values) — the polished
  alternative to a plain `text` overlay.
  label:        str — small uppercase line above the value, e.g. "POWER"
  value:        str — large bold focal text, e.g. "85%"
  note:         str — optional dim italic context line, e.g.
                       "factory default: 75%"
  position:     "left-mid" (default) | "right-mid" | "top-left" |
                "top-right" | "bottom-left" | "bottom-right" | [x,y]
  accent_color: hex color for the left stripe, default "#ff7a2d"
                (a warm orange that complements warm/spark footage)

title
  Hero title overlay that sits on top of the opening (or closing) action
  shot, replacing the hard-cut black-slate convention. Same design family
  as `param` (rounded corners, drop shadow, left accent stripe, dark
  panel) but tuned for hero proportions: wider auto-sized panel with a
  generous minimum, larger demi-bold text, optional dim italic subtitle,
  heavier shadow and stripe so it reads as THE title rather than another
  callout. Anchored bottom-center by default to clear the central action
  and stay above the YouTube duration-pill safe zone.
  text:          str — large title line, e.g. "DON'T LET GO"
  subtitle:      str — optional dim italic line below the title
  position:      "bottom-center" (default) | "top-center" | "center" |
                 "bottom-left" | "bottom-right" | [x,y]
  text_size:     int, default 100
  subtitle_size: int, default 38
  accent_color:  hex color for the left stripe, default "#ff7a2d"
  fade:          float, default 0.6 (slightly slower than other overlays
                 so the title feels presented, not flashed)

OVERLAY TYPES — schema reserved, not yet implemented

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

Stdlib + ffmpeg for everything except `arrow`, which uses Pillow to
pre-render the arrow shape as a transparent PNG.
"""

import argparse
import json
import math
import shlex
import shutil
import subprocess
import sys
import tempfile
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
        # Fade timings are expressed in MAIN-video time. The looped PNG
        # input's local PTS happens to align with main-t since both start
        # at 0, so st=s lines the fade-in up with the overlay's enable
        # window opening. Using input-local 0 would complete the fade-in
        # before the window opened, and the one-shot fade-out would lock
        # alpha at 0 long before the window closed — pip invisible mid-
        # clip for any t[0] != 0.
        parts[0] += (f",fade=t=in:st={s:.3f}:d={fade},"
                     f"fade=t=out:st={max(0, e - fade):.3f}:d={fade}")
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


# ---------- arrow (Pillow-rendered PNG, overlayed like pip) ----------

def render_arrow_png(entry: dict, video_w: int, video_h: int,
                     out_path: Path) -> None:
    """Render a single arrow as a transparent PNG sized to the full output
    frame, with the arrow placed at the entry's absolute coordinates.
    Drawing at full-frame size keeps the overlay's x/y trivially at 0,0
    and avoids subpixel positioning headaches.
    """
    # Imported lazily so the module still imports for users who only use
    # the non-arrow overlay types and haven't installed Pillow.
    from PIL import Image, ImageDraw

    x0, y0 = entry["from"]
    x1, y1 = entry["to"]
    color = entry.get("color", "yellow")
    thickness = int(entry.get("thickness", 6))
    head_len = int(entry.get("arrowhead_size", 30))
    head_w = max(2, int(round(head_len * 0.6)))

    img = Image.new("RGBA", (video_w, video_h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Unit vector from from->to.
    dx, dy = x1 - x0, y1 - y0
    length = math.hypot(dx, dy)
    if length < 1e-3:
        # Degenerate arrow; render nothing rather than crashing.
        img.save(out_path)
        return
    ux, uy = dx / length, dy / length
    # Perpendicular (right-hand normal).
    px, py = -uy, ux

    # Shorten the shaft so it ends at the back of the arrowhead instead
    # of poking through the tip. Without this the line shows on top of
    # the triangle and gives a fuzzy double-tip.
    shaft_end_x = x1 - ux * head_len
    shaft_end_y = y1 - uy * head_len
    draw.line(
        [(x0, y0), (shaft_end_x, shaft_end_y)],
        fill=color, width=thickness,
    )

    # Triangle: tip at (x1,y1), base centered at shaft_end with width head_w.
    base_cx, base_cy = shaft_end_x, shaft_end_y
    left = (base_cx + px * (head_w / 2), base_cy + py * (head_w / 2))
    right = (base_cx - px * (head_w / 2), base_cy - py * (head_w / 2))
    draw.polygon([(x1, y1), left, right], fill=color)

    img.save(out_path)


def emit_arrow_branch(entry: dict, png_path: Path, input_idx: int,
                      out_label: str) -> tuple[str, list[str]]:
    """Build a filter_complex branch for one arrow overlay.

    Same shape as emit_pip_branch: consumes `[<input_idx>:v]` (a looped
    image input), applies fade in/out, and emits `[<out_label>]`.

    Fade timings are expressed in MAIN-video time (the looped PNG input's
    local PTS happens to align with main-t since both start at 0). This
    matters: if we used input-local 0 for fade-in start, the fade-in
    would complete before the overlay's enable window opened, and the
    one-shot fade-out would lock alpha at 0 long before the window
    closed — leaving the arrow invisible inside its window.
    """
    fade = entry.get("fade", DEFAULT_FADE)
    s, e = entry["t"]

    parts = [f"[{input_idx}:v]null"]
    if fade > 0:
        parts[0] += (f",fade=t=in:st={s:.3f}:d={fade}:alpha=1,"
                     f"fade=t=out:st={max(0, e - fade):.3f}:d={fade}:alpha=1")
    parts[0] += f"[{out_label}]"
    extra_input = ["-loop", "1", "-i", str(png_path)]
    return parts[0], extra_input


def emit_arrow_overlay(entry: dict, arrow_label: str,
                       in_label: str, out_label: str) -> str:
    """Composite the pre-rendered full-frame arrow PNG onto the main video.

    Since the PNG is drawn at output-frame resolution with the arrow
    placed at the right absolute pixels, the overlay position is just 0,0.
    """
    t = entry["t"]
    return (
        f"[{in_label}][{arrow_label}]"
        f"overlay=x=0:y=0:format=auto:"
        f"enable='{enable_expr(t)}'"
        f"[{out_label}]"
    )


# ---------- param panel (Pillow-rendered PNG, overlayed like arrow) ----------

# Font index map for Avenir Next.ttc. Each .ttc index resolves to a different
# (family, style) variant; these were verified empirically on macOS Sequoia.
# If Avenir Next isn't present we fall back to Helvetica.ttc (which has its
# own indices, so the fallback is best-effort, not perfectly weight-matched).
_AVENIR_NEXT = "/System/Library/Fonts/Avenir Next.ttc"
_HELVETICA = "/System/Library/Fonts/Helvetica.ttc"
_PARAM_FONT_PROFILE = {
    # weight name -> (path, index)
    "medium":    (_AVENIR_NEXT, 5),   # for the small uppercase label
    "demi_bold": (_AVENIR_NEXT, 2),   # for the large value
    "italic":    (_AVENIR_NEXT, 4),   # for the optional note
}
_PARAM_FONT_FALLBACK = {
    "medium":    (_HELVETICA, 0),
    "demi_bold": (_HELVETICA, 1),
    "italic":    (_HELVETICA, 2),
}


def _load_param_font(weight: str, size: int):
    """Load a param-panel font at the given weight + size, with fallback."""
    from PIL import ImageFont
    profile = (_PARAM_FONT_PROFILE
               if Path(_AVENIR_NEXT).exists()
               else _PARAM_FONT_FALLBACK)
    path, index = profile[weight]
    return ImageFont.truetype(path, size, index=index)


def render_param_png(entry: dict, video_w: int, video_h: int,
                     out_path: Path) -> None:
    """Render a parameter-callout panel as a transparent full-frame PNG.

    Panel layout (left-to-right):
      [ACCENT STRIPE]  [PADDING]  [LABEL]            <- small dim caps
                                  [VALUE]            <- large bold focal
                                  [NOTE (optional)]  <- small dim italic

    Drawing at full output frame size lets the overlay sit at x=0:y=0 and
    keeps positioning math (relative to the panel anchor) inside this
    function. The panel auto-sizes to fit the longest text + padding;
    its on-frame position is determined by the entry's `position` field.

    A subtle drop shadow gives the panel separation from the footage
    without the cinema-style heaviness of a hard outline.
    """
    from PIL import Image, ImageDraw, ImageFilter

    label = str(entry["label"]).upper()
    value = str(entry["value"])
    note = str(entry.get("note") or "")
    accent = entry.get("accent_color", "#ff7a2d")
    position = entry.get("position", "left-mid")

    # Type system.
    label_font = _load_param_font("medium", 28)
    value_font = _load_param_font("demi_bold", 88)
    note_font = _load_param_font("italic", 26) if note else None

    # Measure text. getbbox returns (x0, y0, x1, y1) of the rendered ink
    # box; we use width = x1 - x0 (ignoring left-side bearing) and height
    # as the ascent+descent for that font size.
    def w(text, font):
        x0, _, x1, _ = font.getbbox(text)
        return x1 - x0
    label_w_px = w(label, label_font)
    value_w_px = w(value, value_font)
    note_w_px = w(note, note_font) if note_font else 0
    content_w = max(label_w_px, value_w_px, note_w_px)

    # Use the font's own metrics for line heights so descenders / ascenders
    # don't get clipped. Pillow's getmetrics() returns (ascent, descent).
    label_lh = sum(label_font.getmetrics())
    value_lh = sum(value_font.getmetrics())
    note_lh = sum(note_font.getmetrics()) if note_font else 0

    stripe_w = 8
    pad_left_inside = 36     # space between stripe and text column
    pad_other = 32           # top / right / bottom interior padding
    gap_label_value = 16
    gap_value_note = 16
    radius = 10

    panel_w = stripe_w + pad_left_inside + int(content_w) + pad_other
    panel_h = (pad_other
               + label_lh
               + gap_label_value + value_lh
               + ((gap_value_note + note_lh) if note_font else 0)
               + pad_other)

    # Compute panel top-left position on the output frame.
    margin = 60   # safe-area margin from frame edges for side anchors
    pos_map = {
        "left-mid":      (margin, (video_h - panel_h) // 2),
        "right-mid":     (video_w - panel_w - margin, (video_h - panel_h) // 2),
        "top-left":      (margin, margin),
        "top-right":     (video_w - panel_w - margin, margin),
        "bottom-left":   (margin, video_h - panel_h - margin),
        "bottom-right":  (video_w - panel_w - margin, video_h - panel_h - margin),
        "center":        ((video_w - panel_w) // 2, (video_h - panel_h) // 2),
        "top-center":    ((video_w - panel_w) // 2, margin),
        "bottom-center": ((video_w - panel_w) // 2, video_h - panel_h - margin),
    }
    if isinstance(position, (list, tuple)):
        panel_x, panel_y = int(position[0]), int(position[1])
    elif position in pos_map:
        panel_x, panel_y = pos_map[position]
    else:
        raise ValueError(f"Unknown param position {position!r}")

    # Build the canvas (RGBA, transparent everywhere except where we draw).
    img = Image.new("RGBA", (video_w, video_h), (0, 0, 0, 0))

    # Drop shadow: draw a slightly-larger dark rounded rect into its own
    # layer, blur it, paste underneath the panel. Offset down a few px.
    shadow_extend = 10
    shadow_offset_y = 6
    shadow_pad = 20  # extra pad on the shadow layer so the blur isn't clipped
    sh_w = panel_w + 2 * shadow_extend + 2 * shadow_pad
    sh_h = panel_h + 2 * shadow_extend + 2 * shadow_pad
    sh = Image.new("RGBA", (sh_w, sh_h), (0, 0, 0, 0))
    sh_draw = ImageDraw.Draw(sh)
    sh_draw.rounded_rectangle(
        (shadow_pad - shadow_extend, shadow_pad - shadow_extend,
         shadow_pad + panel_w + shadow_extend,
         shadow_pad + panel_h + shadow_extend),
        radius=radius + shadow_extend,
        fill=(0, 0, 0, 130),
    )
    sh = sh.filter(ImageFilter.GaussianBlur(radius=14))
    img.alpha_composite(
        sh,
        (panel_x - shadow_pad, panel_y - shadow_pad + shadow_offset_y),
    )

    draw = ImageDraw.Draw(img)

    # Panel background: dark with slight transparency so the underlying
    # image grades through faintly. 92% opacity is enough to ensure text
    # contrast over any background.
    draw.rounded_rectangle(
        (panel_x, panel_y, panel_x + panel_w - 1, panel_y + panel_h - 1),
        radius=radius,
        fill=(12, 12, 12, 235),
    )

    # Accent stripe: full-height rectangle on the left edge. We draw a
    # rounded-rect that exceeds the stripe width and then clip the right
    # side back with a sharp-corner rect of the panel-bg color — gives a
    # left-rounded / right-square stripe that hugs the panel corner.
    stripe_rgba = _hex_to_rgba(accent, alpha=255)
    draw.rounded_rectangle(
        (panel_x, panel_y, panel_x + stripe_w + radius, panel_y + panel_h - 1),
        radius=radius,
        fill=stripe_rgba,
    )
    draw.rectangle(
        (panel_x + stripe_w, panel_y,
         panel_x + stripe_w + radius, panel_y + panel_h - 1),
        fill=(12, 12, 12, 235),
    )

    # Text column.
    text_x = panel_x + stripe_w + pad_left_inside
    cur_y = panel_y + pad_other
    draw.text((text_x, cur_y), label, font=label_font,
              fill=(160, 160, 160, 255))
    cur_y += label_lh + gap_label_value
    draw.text((text_x, cur_y), value, font=value_font,
              fill=(255, 255, 255, 255))
    if note_font:
        cur_y += value_lh + gap_value_note
        draw.text((text_x, cur_y), note, font=note_font,
                  fill=(160, 160, 160, 255))

    img.save(out_path)


def _hex_to_rgba(hex_color: str, alpha: int = 255) -> tuple[int, int, int, int]:
    """Parse '#RRGGBB' or '#RGB' into an RGBA tuple."""
    s = hex_color.lstrip("#")
    if len(s) == 3:
        s = "".join(c * 2 for c in s)
    if len(s) != 6:
        raise ValueError(f"Bad hex color {hex_color!r}")
    return (int(s[0:2], 16), int(s[2:4], 16), int(s[4:6], 16), alpha)


def emit_param_branch(entry: dict, png_path: Path, input_idx: int,
                      out_label: str) -> tuple[str, list[str]]:
    """Build a filter_complex branch for one param-panel overlay.

    Same shape as emit_arrow_branch (the PNG is already at full-frame
    size with the panel placed at the right pixels, so the overlay sits
    at x=0:y=0). Fade timings are in MAIN-video time.
    """
    fade = entry.get("fade", DEFAULT_FADE)
    s, e = entry["t"]

    parts = [f"[{input_idx}:v]null"]
    if fade > 0:
        parts[0] += (f",fade=t=in:st={s:.3f}:d={fade}:alpha=1,"
                     f"fade=t=out:st={max(0, e - fade):.3f}:d={fade}:alpha=1")
    parts[0] += f"[{out_label}]"
    extra_input = ["-loop", "1", "-i", str(png_path)]
    return parts[0], extra_input


def emit_param_overlay(entry: dict, param_label: str,
                       in_label: str, out_label: str) -> str:
    """Composite the pre-rendered full-frame param PNG onto the main video."""
    t = entry["t"]
    return (
        f"[{in_label}][{param_label}]"
        f"overlay=x=0:y=0:format=auto:"
        f"enable='{enable_expr(t)}'"
        f"[{out_label}]"
    )


# ---------- title (Pillow-rendered hero title-over-action) ----------

# The title type's role: replace the old "hard cut to a black slate" intro
# convention. Modern doc/build channels keep the action visible behind the
# title; the title is a polished overlay, not a separate beat. Sits in the
# same design family as `param` (rounded corners, accent stripe, drop shadow,
# dark panel) but with hero proportions — wider panel, larger type, slightly
# heavier panel + stripe + shadow than `param` so it reads as THE title
# rather than another callout. Anchored bottom-center by default to clear
# the central action without competing with the YouTube duration pill
# (which lives bottom-right on most surfaces).

_TITLE_FONT_PROFILE = {
    "demi_bold": (_AVENIR_NEXT, 2),   # the large title text
    "italic":    (_AVENIR_NEXT, 4),   # the optional subtitle
}
_TITLE_FONT_FALLBACK = {
    "demi_bold": (_HELVETICA, 1),
    "italic":    (_HELVETICA, 2),
}


def _load_title_font(weight: str, size: int):
    """Load a title font at the given weight + size, with fallback."""
    from PIL import ImageFont
    profile = (_TITLE_FONT_PROFILE
               if Path(_AVENIR_NEXT).exists()
               else _TITLE_FONT_FALLBACK)
    path, index = profile[weight]
    return ImageFont.truetype(path, size, index=index)


def render_title_png(entry: dict, video_w: int, video_h: int,
                     out_path: Path) -> None:
    """Render a hero title panel as a transparent full-frame PNG.

    Layout (left-to-right):
      [ACCENT STRIPE]  [PADDING]  [TITLE]               <- large demi-bold
                                  [SUBTITLE (optional)] <- smaller italic dim

    Panel auto-sizes to the longest text + generous padding, with a minimum
    width so short titles still feel hero-sized. The panel is centered
    horizontally and anchored to the bottom-center by default (lifts above
    the YouTube duration-pill safe zone).
    """
    from PIL import Image, ImageDraw, ImageFilter

    text = str(entry["text"])
    subtitle = str(entry.get("subtitle") or "")
    accent = entry.get("accent_color", "#ff7a2d")
    position = entry.get("position", "bottom-center")
    text_size = int(entry.get("text_size", 100))
    subtitle_size = int(entry.get("subtitle_size", 38))

    text_font = _load_title_font("demi_bold", text_size)
    subtitle_font = _load_title_font("italic", subtitle_size) if subtitle else None

    def w(text, font):
        x0, _, x1, _ = font.getbbox(text)
        return x1 - x0
    text_w_px = w(text, text_font)
    subtitle_w_px = w(subtitle, subtitle_font) if subtitle_font else 0
    content_w = max(text_w_px, subtitle_w_px)

    text_lh = sum(text_font.getmetrics())
    subtitle_lh = sum(subtitle_font.getmetrics()) if subtitle_font else 0

    stripe_w = 12
    pad_left_inside = 48     # space between stripe and text column
    pad_other = 56           # top / right / bottom interior padding
    gap_text_subtitle = 16
    radius = 12

    # Min/max widths: short titles still look hero, long titles still fit
    # inside the safe area. The minimum gives a confident presence; the
    # maximum keeps 120 px of clear space on each side of the frame.
    min_panel_w = 800
    max_panel_w = video_w - 240
    desired_w = stripe_w + pad_left_inside + int(content_w) + pad_other
    panel_w = max(min_panel_w, min(max_panel_w, desired_w))

    panel_h = (pad_other
               + text_lh
               + ((gap_text_subtitle + subtitle_lh) if subtitle_font else 0)
               + pad_other)

    # Position anchors. Bottom-center default — lifts the panel above the
    # YouTube duration pill zone (bottom-right corner on most surfaces).
    bottom_margin = 140
    side_margin = 120
    pos_map = {
        "bottom-center": ((video_w - panel_w) // 2,
                          video_h - panel_h - bottom_margin),
        "top-center":    ((video_w - panel_w) // 2, bottom_margin),
        "center":        ((video_w - panel_w) // 2, (video_h - panel_h) // 2),
        "bottom-left":   (side_margin, video_h - panel_h - bottom_margin),
        "bottom-right":  (video_w - panel_w - side_margin,
                          video_h - panel_h - bottom_margin),
    }
    if isinstance(position, (list, tuple)):
        panel_x, panel_y = int(position[0]), int(position[1])
    elif position in pos_map:
        panel_x, panel_y = pos_map[position]
    else:
        raise ValueError(f"Unknown title position {position!r}")

    img = Image.new("RGBA", (video_w, video_h), (0, 0, 0, 0))

    # Drop shadow — heavier than param's so the title reads as the hero
    # element. 16 px blur, 8 px y-offset.
    shadow_extend = 12
    shadow_offset_y = 8
    shadow_pad = 24
    sh_w = panel_w + 2 * shadow_extend + 2 * shadow_pad
    sh_h = panel_h + 2 * shadow_extend + 2 * shadow_pad
    sh = Image.new("RGBA", (sh_w, sh_h), (0, 0, 0, 0))
    sh_draw = ImageDraw.Draw(sh)
    sh_draw.rounded_rectangle(
        (shadow_pad - shadow_extend, shadow_pad - shadow_extend,
         shadow_pad + panel_w + shadow_extend,
         shadow_pad + panel_h + shadow_extend),
        radius=radius + shadow_extend,
        fill=(0, 0, 0, 150),
    )
    sh = sh.filter(ImageFilter.GaussianBlur(radius=16))
    img.alpha_composite(
        sh,
        (panel_x - shadow_pad, panel_y - shadow_pad + shadow_offset_y),
    )

    draw = ImageDraw.Draw(img)

    # Panel background — dark, slightly more solid than param (235→240) so
    # the title's typography sits clearly above any background scene.
    draw.rounded_rectangle(
        (panel_x, panel_y, panel_x + panel_w - 1, panel_y + panel_h - 1),
        radius=radius,
        fill=(10, 10, 10, 240),
    )

    # Accent stripe — same hugging-the-rounded-corner pattern as param,
    # 12 px wide (heavier than param's 8).
    stripe_rgba = _hex_to_rgba(accent, alpha=255)
    draw.rounded_rectangle(
        (panel_x, panel_y, panel_x + stripe_w + radius, panel_y + panel_h - 1),
        radius=radius,
        fill=stripe_rgba,
    )
    draw.rectangle(
        (panel_x + stripe_w, panel_y,
         panel_x + stripe_w + radius, panel_y + panel_h - 1),
        fill=(10, 10, 10, 240),
    )

    # Text column.
    text_x = panel_x + stripe_w + pad_left_inside
    cur_y = panel_y + pad_other
    draw.text((text_x, cur_y), text, font=text_font,
              fill=(255, 255, 255, 255))
    if subtitle_font:
        cur_y += text_lh + gap_text_subtitle
        draw.text((text_x, cur_y), subtitle, font=subtitle_font,
                  fill=(170, 170, 170, 255))

    img.save(out_path)


def emit_title_branch(entry: dict, png_path: Path, input_idx: int,
                      out_label: str) -> tuple[str, list[str]]:
    """Build a filter_complex branch for one title overlay.

    Same shape as emit_param_branch (PNG drawn at full-frame size, overlay
    sits at x=0:y=0). Default fade is slightly slower than other overlays
    so the title feels presented rather than flashed.
    """
    fade = entry.get("fade", 0.6)
    s, e = entry["t"]

    parts = [f"[{input_idx}:v]null"]
    if fade > 0:
        parts[0] += (f",fade=t=in:st={s:.3f}:d={fade}:alpha=1,"
                     f"fade=t=out:st={max(0, e - fade):.3f}:d={fade}:alpha=1")
    parts[0] += f"[{out_label}]"
    extra_input = ["-loop", "1", "-i", str(png_path)]
    return parts[0], extra_input


def emit_title_overlay(entry: dict, title_label: str,
                       in_label: str, out_label: str) -> str:
    """Composite the pre-rendered full-frame title PNG onto the main video."""
    t = entry["t"]
    return (
        f"[{in_label}][{title_label}]"
        f"overlay=x=0:y=0:format=auto:"
        f"enable='{enable_expr(t)}'"
        f"[{out_label}]"
    )


# ---------- top-level renderer ----------

DRAWLIKE_TYPES = {"text", "stamp", "lower_third", "hud", "box"}


def probe_video_dims(path: str) -> tuple[int, int]:
    """Return (width, height) of the first video stream via ffprobe."""
    out = subprocess.check_output([
        "ffprobe", "-v", "error",
        "-select_streams", "v:0",
        "-show_entries", "stream=width,height",
        "-of", "csv=p=0:s=x",
        path,
    ], text=True).strip()
    w, h = out.split("x")
    return int(w), int(h)


def build_filter_graph(sidecar: dict, sidecar_dir: Path,
                       captions: str | None = None,
                       video_w: int | None = None,
                       video_h: int | None = None,
                       arrow_tmp_dir: Path | None = None,
                       ) -> tuple[str, list[str]]:
    """Build a complete filter_complex string + the extra ffmpeg input args.

    The graph's main video input is assumed to be `[0:v]`. The graph's
    final video stream is labelled `[vout]`.

    `video_w` / `video_h` are only required if the sidecar contains any
    arrow overlays (which need a full-frame PNG canvas). `arrow_tmp_dir`
    is the directory in which pre-rendered arrow PNGs will be written.

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
        elif t == "arrow":
            if video_w is None or video_h is None or arrow_tmp_dir is None:
                raise RuntimeError(
                    "arrow overlays require video_w / video_h / "
                    "arrow_tmp_dir; call render() or pass them explicitly."
                )
            flush_drawlike()
            png_path = arrow_tmp_dir / f"arrow_{next_input_idx}.png"
            render_arrow_png(entry, video_w, video_h, png_path)
            arrow_label = f"arrow{next_input_idx}"
            branch_stmt, ffmpeg_in = emit_arrow_branch(
                entry, png_path, next_input_idx, arrow_label)
            statements.append(branch_stmt)
            extra_inputs.extend(ffmpeg_in)
            next_input_idx += 1
            out = f"v{next_stage}"
            next_stage += 1
            statements.append(emit_arrow_overlay(entry, arrow_label, cur, out))
            cur = out
        elif t == "param":
            if video_w is None or video_h is None or arrow_tmp_dir is None:
                raise RuntimeError(
                    "param overlays require video_w / video_h / "
                    "arrow_tmp_dir (shared PNG temp dir); call render() "
                    "or pass them explicitly."
                )
            flush_drawlike()
            png_path = arrow_tmp_dir / f"param_{next_input_idx}.png"
            render_param_png(entry, video_w, video_h, png_path)
            param_label = f"param{next_input_idx}"
            branch_stmt, ffmpeg_in = emit_param_branch(
                entry, png_path, next_input_idx, param_label)
            statements.append(branch_stmt)
            extra_inputs.extend(ffmpeg_in)
            next_input_idx += 1
            out = f"v{next_stage}"
            next_stage += 1
            statements.append(emit_param_overlay(entry, param_label, cur, out))
            cur = out
        elif t == "title":
            if video_w is None or video_h is None or arrow_tmp_dir is None:
                raise RuntimeError(
                    "title overlays require video_w / video_h / "
                    "arrow_tmp_dir (shared PNG temp dir); call render() "
                    "or pass them explicitly."
                )
            flush_drawlike()
            png_path = arrow_tmp_dir / f"title_{next_input_idx}.png"
            render_title_png(entry, video_w, video_h, png_path)
            title_label = f"title{next_input_idx}"
            branch_stmt, ffmpeg_in = emit_title_branch(
                entry, png_path, next_input_idx, title_label)
            statements.append(branch_stmt)
            extra_inputs.extend(ffmpeg_in)
            next_input_idx += 1
            out = f"v{next_stage}"
            next_stage += 1
            statements.append(emit_title_overlay(entry, title_label, cur, out))
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

    # Probe output-video dims for any arrow overlays (which need a
    # full-frame PNG canvas). Cheap enough to always do.
    video_w, video_h = probe_video_dims(input_video)

    arrow_tmp_dir = Path(tempfile.mkdtemp(prefix="overlays-arrow-"))
    try:
        filter_complex, extra_inputs = build_filter_graph(
            sidecar, sidecar_dir, captions=captions,
            video_w=video_w, video_h=video_h,
            arrow_tmp_dir=arrow_tmp_dir,
        )

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
    finally:
        shutil.rmtree(arrow_tmp_dir, ignore_errors=True)


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
