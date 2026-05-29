"""
Appliance quick-start sheet generator — produces the 11×17 landscape
print artifact that ships at the top of the appliance carton.

Source of design intent: `marketing/unboxing-and-quickstart.md`.

Outputs two files into the sibling `drawings/prints-and-guides/`
directory:

- `appliance.svg` — the on-site display artifact. Inline SVG is what
  the website's drawings viewer renders in both thumbnail and modal.
- `appliance.pdf` — the print artifact. Converted from the SVG via
  rsvg-convert at the end of this script. Page size is preserved from
  the SVG's mm-based width/height.

Sheet shape: four drawings in a 2×2 grid, each with a caption below.
White page background so the modal shows "white page on dark modal
surround," matching what the printed sheet looks like in a hand.

Color system:
- red  = CO2
- blue = incoming tap water — the supply that gets teed in and run to
         the device. Paired against red for a loud two-color install.
- gray = the faucet / dispense channel, deferred to the advanced faucet
         quickstart and not shown on this install sheet.

Steps 2 and 3 have no line-art yet; those cells show only their arrows
and caption.

Run:
    tools/cad-venv/bin/python hardware/quickstart/appliance_quickstart.py
"""

import math
import os
import re
import subprocess
import sys
from pathlib import Path

_here = Path(__file__).resolve()
sys.path.insert(
    0,
    str(next(p for p in _here.parents if p.name == "hardware")),
)
from _cadq_export import export_pdf


# Enclosure iso line-art sources.
_LINEART = (
    _here.parent.parent
    / "printed-parts" / "enclosure" / "drawings" / "line-art"
)
ENCLOSURE_FRONT = _LINEART / "enclosure-iso-front.svg"
ENCLOSURE_BACK = _LINEART / "enclosure-iso-back.svg"

# Blue water-disc fill emitted by the iso renderer; used to locate the
# water inlet inside an embedded back view.
WATER_DISC_FILL = "rgb(31, 111, 235)"


# Page — 11×17 landscape, in mm
PAGE_W_MM = 431.8   # 17 in
PAGE_H_MM = 279.4   # 11 in

# Border around the four-cell grid, and gutter between cells
BORDER_MM = 12.7   # 0.5 in
GUTTER_MM = 12.7   # 0.5 in

# Inner padding within each step, the fixed caption-band height, and
# the step panel's corner radius
PAD_MM = 6.35            # 0.25 in
CAPTION_BAND_MM = 12.7   # 0.5 in
STEP_RADIUS_MM = 6.35    # 0.25 in
STEP_NUMBER_SIZE_MM = 40  # very large step numerals
HAIRLINE_MM = 0.4         # thin #000 stroke: step borders + number outlines
PORT_ARROW_GAP_MM = 5.2   # arrow-tip standoff from a port hole (matches step 1's CO2 arrow)

# Color system
COLOR_WATER = "#1f6feb"        # blue — incoming tap water
COLOR_CO2 = "#d63a3a"          # red — CO2
COLOR_TAP = "#6e6e6e"          # medium gray — faucet / dispense channel
COLOR_PLAIN = "#1a1a1a"        # plain motion arrows, captions, page text
COLOR_STEP_BG = "#eeeeee"      # shaded step panel fill

ARROW_COLORS = {
    "blue": COLOR_WATER,
    "red": COLOR_CO2,
    "gray": COLOR_TAP,
    "dark": COLOR_PLAIN,
}


def _arrow_defs():
    """SVG <defs> — arrowhead markers, two variants per color.

    Triangle viewBox `0 0 12 10`, tip at (12, 5), back edge from
    (0, 0) to (0, 10).

    `arrow-<color>`: refX=9. Marker overlaps the path near the
    endpoint; the tip extends 3 viewBox units past the endpoint.
    `arrow-<color>-back`: refX=0. Marker sits past the path
    endpoint; the back-edge is at the endpoint.
    """
    markers = []
    for name, color in ARROW_COLORS.items():
        markers.append(
            f'<marker id="arrow-{name}" viewBox="0 0 12 10" refX="9" refY="5" '
            f'markerWidth="6" markerHeight="5" orient="auto-start-reverse">'
            f'<path d="M 0 0 L 12 5 L 0 10 Z" fill="{color}" />'
            f'</marker>'
        )
        markers.append(
            f'<marker id="arrow-{name}-back" viewBox="0 0 12 10" refX="0" refY="5" '
            f'markerWidth="6" markerHeight="5" orient="auto-start-reverse">'
            f'<path d="M 0 0 L 12 5 L 0 10 Z" fill="{color}" />'
            f'</marker>'
        )
    return "  <defs>\n    " + "\n    ".join(markers) + "\n  </defs>"


def _straight_arrow(x1, y1, x2, y2, color="dark", sw=1.2):
    """A line with an arrowhead at (x2, y2)."""
    c = ARROW_COLORS[color]
    # Wrap in <g stroke=...> so the line's stroke comes through inheritance
    # — beats the .quickstart-sheet path/line stroke: inherit !important
    # override (which would otherwise strand the arrow at unset/black).
    return (
        f'<g stroke="{c}">'
        f'<line x1="{x1:.2f}" y1="{y1:.2f}" x2="{x2:.2f}" y2="{y2:.2f}" '
        f'stroke-width="{sw}" stroke-linecap="round" '
        f'marker-end="url(#arrow-{color})" />'
        f'</g>'
    )


def _rotation_arrow(cx, cy, r, start_deg, sweep_deg, color="dark", sw=1.2):
    """Curved arrow indicating rotation, from start_deg through sweep_deg.

    Angles are in SVG screen coords (y down): 0° = right, 90° = down,
    180° = left, 270° = up. Positive sweep_deg goes CW on screen
    (math-positive direction in y-down).
    """
    a1 = math.radians(start_deg)
    a2 = math.radians(start_deg + sweep_deg)
    x1, y1 = cx + r * math.cos(a1), cy + r * math.sin(a1)
    x2, y2 = cx + r * math.cos(a2), cy + r * math.sin(a2)
    large_arc = 1 if abs(sweep_deg) > 180 else 0
    sweep_flag = 1 if sweep_deg > 0 else 0
    c = ARROW_COLORS[color]
    return (
        f'<g stroke="{c}" fill="none">'
        f'<path d="M {x1:.2f} {y1:.2f} A {r} {r} 0 {large_arc} {sweep_flag} {x2:.2f} {y2:.2f}" '
        f'stroke-width="{sw}" stroke-linecap="round" '
        f'marker-end="url(#arrow-{color}-back)" />'
        f'</g>'
    )


def _stub_arrow(target_x, target_y, dx, dy, color="dark", sw=1.2, length=12):
    """Short arrow whose tip lands at (target_x, target_y), pointing in
    direction (dx, dy). `length` is the line length from start to
    arrowhead — the arrowhead's back-edge sits 5.4 user units inside
    that length, so visible line behind the arrowhead is `length - 5.4`.
    """
    mag = math.sqrt(dx * dx + dy * dy)
    ux, uy = dx / mag, dy / mag
    x1, y1 = target_x - length * ux, target_y - length * uy
    return _straight_arrow(x1, y1, target_x, target_y, color, sw)


def cell_rect(col, row):
    """Return (x, y, w, h) for the cell at column col (0..1) and row row (0..1).

    Cells fill the page minus the border around the perimeter, with a
    gutter between cells.
    """
    cols, rows = 2, 2
    avail_w = PAGE_W_MM - 2 * BORDER_MM - (cols - 1) * GUTTER_MM
    avail_h = PAGE_H_MM - 2 * BORDER_MM - (rows - 1) * GUTTER_MM
    cw = avail_w / cols
    ch = avail_h / rows
    x = BORDER_MM + col * (cw + GUTTER_MM)
    y = BORDER_MM + row * (ch + GUTTER_MM)
    return x, y, cw, ch


def _read_svg_for_embed(svg_path):
    """Extract (viewBox, inner_xml) from a source SVG for embedding.

    The line-art SVGs in this repo come from two generators with slightly
    different output shapes:
    - tools/line-art/line_art.py writes an explicit viewBox.
    - The CadQuery HLR generator writes width/height in absolute units
      with no viewBox; the inner content is pre-transformed to fit that
      canvas, so a `0 0 W H` viewBox captures it correctly.

    For embedding we wrap the source's inner XML in a nested <svg>
    element with the caller-chosen position/size and a viewBox derived
    from whichever metadata the source carries.
    """
    text = Path(svg_path).read_text()
    vb = re.search(r'<svg[^>]*\bviewBox\s*=\s*"([^"]+)"', text)
    w = re.search(r'<svg[^>]*\bwidth\s*=\s*"([0-9.]+)', text)
    h = re.search(r'<svg[^>]*\bheight\s*=\s*"([0-9.]+)', text)

    if vb:
        viewbox = vb.group(1)
    elif w and h:
        viewbox = f"0 0 {float(w.group(1))} {float(h.group(1))}"
    else:
        raise ValueError(f"{svg_path}: cannot derive viewBox")

    # Slice the inner content out of the root <svg>...</svg> wrapper.
    open_tag_end = text.find(">", text.find("<svg")) + 1
    close_tag = text.rfind("</svg>")
    inner = text[open_tag_end:close_tag].strip()
    return viewbox, inner


def _embed_svg(x, y, w, h, source_path):
    """Render a nested <svg> that scale-fits the source SVG into the
    rectangle (x, y, w, h) on the host page, preserving aspect ratio and
    centering it (xMidYMid meet)."""
    viewbox, inner = _read_svg_for_embed(source_path)
    return (
        f'<svg x="{x:.2f}" y="{y:.2f}" width="{w:.2f}" height="{h:.2f}" '
        f'viewBox="{viewbox}" preserveAspectRatio="xMidYMid meet">\n'
        f'{inner}\n'
        f'</svg>'
    )


def _canvas_dims(source_path):
    """The source SVG's canvas (viewBox) width and height."""
    viewbox, _ = _read_svg_for_embed(source_path)
    _, _, cw, ch = viewbox.split()
    return float(cw), float(ch)


def _ink_bbox(text):
    """Bounding box (min_x, min_y, max_x, max_y) of the drawn line-art in
    an SVG's text, in canvas coordinates. Coordinate pairs are matched
    whitespace-tolerantly (stroke paths use "x, y", disc paths "x,y");
    the clip rectangle's ±100000 sentinel coords are excluded so the box
    tracks the appliance, not the canvas."""
    xs, ys = [], []
    for a, b in re.findall(r'(-?\d+\.?\d*)\s*,\s*(-?\d+\.?\d*)', text):
        fx, fy = float(a), float(b)
        if abs(fx) < 5000 and abs(fy) < 5000:
            xs.append(fx)
            ys.append(fy)
    return min(xs), min(ys), max(xs), max(ys)


def _embed_anchored(source_path, scale, right, bottom, color_fill=None):
    """Embed the source SVG's line-art scaled by `scale` with its ink
    bbox's bottom-right corner placed at page-mm (right, bottom) — so the
    drawing seats against a corner by its actual content, ignoring the
    canvas margin around it. Returns (svg_fragment, point) where point is
    the page-mm location of the `color_fill` path's data-target (the
    projected port hole; falls back to its centroid), or None."""
    text = Path(source_path).read_text()
    _, inner = _read_svg_for_embed(source_path)
    _, _, max_x, max_y = _ink_bbox(text)
    tx = right - max_x * scale
    ty = bottom - max_y * scale
    fragment = (
        f'<g transform="translate({tx:.3f},{ty:.3f}) scale({scale:.6f})">\n'
        f'{inner}\n</g>'
    )
    point = None
    if color_fill:
        tag = re.search(
            r'<path\b[^>]*\bfill="' + re.escape(color_fill) + r'"[^>]*>', text
        ).group(0)
        dt = re.search(r'data-target="(-?[0-9.]+)\s*,\s*(-?[0-9.]+)"', tag)
        if dt:
            cx, cy = float(dt.group(1)), float(dt.group(2))
        else:
            d = re.search(r'\bd="([^"]+)"', tag).group(1)
            pts = re.findall(r'(-?\d+\.?\d*)\s*,\s*(-?\d+\.?\d*)', d)
            cx = sum(float(a) for a, _ in pts) / len(pts)
            cy = sum(float(b) for _, b in pts) / len(pts)
        point = (tx + cx * scale, ty + cy * scale)
    return fragment, point


def _caption_text(x, y, w, h, caption):
    """Bold caption centered both ways in the band (x, y, w, h)."""
    return (
        f'<text x="{x + w / 2:.2f}" y="{y + h / 2:.2f}" '
        f'font-family="Helvetica, Arial, sans-serif" font-size="6.5" '
        f'font-weight="600" fill="{COLOR_PLAIN}" '
        f'text-anchor="middle" dominant-baseline="central">{caption}</text>'
    )


def cell(x, y, w, h, caption, embed_path=None, arrows_fn=None,
         background=False, number=None, number_corner="left"):
    """Render one drawing cell: an image band above a caption band.

    Every step has a thin #000 rounded border; with background set the
    panel is filled with COLOR_STEP_BG, otherwise transparent. Content is
    inset by PAD_MM on all sides. A captioned step reserves a fixed
    CAPTION_BAND_MM caption band at the bottom with the image band above
    it; a caption-less step gives its whole inner height to the image.
    The line-art is scale-fit and centered in the image band; the
    caption is centered in the caption band; arrows_fn, if given, is
    called with the image band and overlaid on it. A large step number
    sits in the image band's upper number_corner ("left" or "right") —
    white on a panel, unfilled on a plain step.
    """
    panel_fill = COLOR_STEP_BG if background else "none"
    panel = (
        f'<rect x="{x:.2f}" y="{y:.2f}" width="{w:.2f}" height="{h:.2f}" '
        f'rx="{STEP_RADIUS_MM}" fill="{panel_fill}" '
        f'stroke="#000000" stroke-width="{HAIRLINE_MM}" />'
    )
    ix, iy = x + PAD_MM, y + PAD_MM
    iw, ih = w - 2 * PAD_MM, h - 2 * PAD_MM
    # A captioned step reserves the caption band at the bottom; a
    # caption-less step gives its whole inner height to the image.
    cap_h = CAPTION_BAND_MM if caption else 0.0
    img_h = ih - cap_h
    num = ""
    if number is not None:
        nx = ix + iw if number_corner == "right" else ix
        anchor = "end" if number_corner == "right" else "start"
        num_fill = "#ffffff" if background else "none"
        num = (
            f'<text x="{nx:.2f}" y="{iy:.2f}" '
            f'font-family="Helvetica, Arial, sans-serif" '
            f'font-size="{STEP_NUMBER_SIZE_MM}" font-weight="700" '
            f'fill="{num_fill}" stroke="#000000" stroke-width="{HAIRLINE_MM}" '
            f'text-anchor="{anchor}" '
            f'dominant-baseline="hanging">{number}</text>'
        )
    body = _embed_svg(ix, iy, iw, img_h, embed_path) if embed_path else ""
    arrows = arrows_fn(ix, iy, iw, img_h) if arrows_fn else ""
    caption_svg = _caption_text(ix, iy + img_h, iw, cap_h, caption) if caption else ""
    return "\n".join(part for part in (panel, num, body, arrows, caption_svg) if part)


# ── Per-cell arrow specs ────────────────────────────────────────────
#
# Each function takes the cell's image-band bounds (x, y, w, img_h) and
# returns SVG for that cell's arrows. Drawings 2 and 3 have no line-art
# yet, so their arrows sit at approximate stand-in positions.


def _arrows_connect_co2(x, y, w, draw_h):
    """Drawing 1: single red arrow from the upper-left empty space
    pointing down-right at the CO2 port on the left side face. The tip
    stops short of the port hole, leaving a visible gap; the arrow's
    line, extended, meets the port."""
    return _straight_arrow(
        x + 0.312 * w, y + 0.206 * draw_h,
        x + 0.426 * w, y + 0.476 * draw_h,
        color="red",
    )


def _arrows_tee_into_water(x, y, w, draw_h):
    """Drawing 2: the left side carries the tee/valve arrows — a blue
    rotation arrow on the angle stop in its top half, and two blue stub
    arrows pointing inward at the tee's outlets in its bottom half. The
    right side carries the enclosure back view with a blue arrow pointing
    at its water inlet."""
    # Left-side tee/valve arrows, centered in the left of the cell.
    left_cx = x + 0.25 * w
    # Rotation arrow — top half of the left side.
    rotation = _rotation_arrow(left_cx, y + 0.25 * draw_h, 5, 30, 240, color="blue")
    # Inward stub arrows — bottom half of the left side.
    stub_y = y + 0.75 * draw_h
    stub_len = 12.0
    stubs = (
        _stub_arrow(left_cx - 15, stub_y, +1, 0, color="blue", length=stub_len)
        + _stub_arrow(left_cx + 15, stub_y, -1, 0, color="blue", length=stub_len)
    )
    # Enclosure back view at the same scale as the captioned steps (their
    # image band fits the canvas height into draw_h - CAPTION_BAND_MM),
    # with its line-art anchored by its own bottom-right corner into the
    # cell's bottom-right padding corner.
    canvas_w, canvas_h = _canvas_dims(ENCLOSURE_BACK)
    scale = min(w / canvas_w, (draw_h - CAPTION_BAND_MM) / canvas_h)
    back, (px, py) = _embed_anchored(
        ENCLOSURE_BACK, scale, x + w, y + draw_h, color_fill=WATER_DISC_FILL,
    )
    # Blue arrow to the water inlet's port hole. Its tail sits at the
    # same height as the right inward arrow's back, a gap to its right
    # (so the two backs align on one horizontal line and don't touch);
    # its tip stops the same gap short of the hole as the CO2 arrow in
    # step 1.
    back_x, back_y = left_cx + 15 + stub_len, stub_y
    back_gap = 8.0
    tail_x, tail_y = back_x + back_gap, back_y
    span = math.hypot(px - tail_x, py - tail_y)
    ux, uy = (px - tail_x) / span, (py - tail_y) / span
    inlet_arrow = _straight_arrow(
        tail_x, tail_y,
        px - ux * PORT_ARROW_GAP_MM, py - uy * PORT_ARROW_GAP_MM,
        color="blue",
    )
    return back + rotation + stubs + inlet_arrow


def _arrows_open_valves(x, y, w, draw_h):
    """Drawing 3: red rotation arrow on the CO2 cylinder valve + blue
    rotation arrow on the water angle-stop handle, paired side-by-side.
    Both turn counterclockwise (lefty-loosy) to open."""
    y_strip = y + 0.65 * draw_h
    return (
        _rotation_arrow(x + 0.30 * w, y_strip, 7, 30, -240, color="red")
        + _rotation_arrow(x + 0.70 * w, y_strip, 7, 30, -240, color="blue")
    )


def _arrows_fill_hopper(x, y, w, draw_h):
    """Drawing 4: plain motion arrow on the inverted bottle, pointing
    down. Placed above the appliance line-art at the cell's horizontal
    center."""
    cx = x + 0.50 * w
    return _straight_arrow(cx, y + 0.05 * draw_h, cx, y + 0.22 * draw_h, color="dark")


def main():
    here = Path(__file__).resolve().parent
    repo_root = here.parent.parent
    out_dir = here / "drawings" / "prints-and-guides"
    out_dir.mkdir(parents=True, exist_ok=True)
    svg_path = out_dir / "appliance.svg"
    pdf_path = out_dir / "appliance.pdf"

    # Line-art sources. Drawings 1 and 4 embed the enclosure iso views
    # full-cell; drawing 2 embeds the back view in its lower-right corner
    # (see _arrows_tee_into_water); drawing 3 has no line-art yet.
    enclosure_front = ENCLOSURE_FRONT
    enclosure_back = ENCLOSURE_BACK

    # The four drawings, sourced from
    # marketing/unboxing-and-quickstart.md.
    drawings = [
        {
            "caption": "Connect the CO2.",
            "embed": enclosure_front,
            "arrows": _arrows_connect_co2,
        },
        {
            "caption": None,
            "embed": None,
            "arrows": _arrows_tee_into_water,
            "background": True,
        },
        {
            "caption": "Open the CO2. Open the water.",
            "embed": None,
            "arrows": _arrows_open_valves,
            "background": True,
        },
        {
            "caption": "Empty a flavor into the hopper.",
            "embed": enclosure_back,
            "arrows": _arrows_fill_hopper,
        },
    ]

    # 2×2 layout — drawing 1 top-left, 2 top-right, 3 bottom-left, 4 bottom-right.
    cells = [
        (0, 0),
        (1, 0),
        (0, 1),
        (1, 1),
    ]

    body_parts = []
    for i, ((col, row), drawing) in enumerate(zip(cells, drawings)):
        x, y, w, h = cell_rect(col, row)
        body_parts.append(
            cell(
                x, y, w, h,
                drawing["caption"],
                embed_path=drawing["embed"],
                arrows_fn=drawing["arrows"],
                background=drawing.get("background", False),
                number=i + 1,
                number_corner="right" if col == 1 else "left",
            )
        )

    body = "\n".join(body_parts)

    # The site's viewer.css recolors every path/line stroke to var(--text)
    # (white) under .drawing-svg / .card .drawing-thumb — the assumption
    # being that drawings sit on a dark surface. This sheet has its OWN
    # white page background, so that recolor turns the embedded line-art
    # into white-on-white. The class + <style> block below scope-restore
    # stroke inheritance with !important so the embedded paths show
    # their original presentation-attribute colors (black for visible,
    # gray for hidden) regardless of the page CSS.
    svg = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'viewBox="0 0 {PAGE_W_MM} {PAGE_H_MM}" '
        f'width="{PAGE_W_MM}mm" height="{PAGE_H_MM}mm" '
        f'class="quickstart-sheet">\n'
        '  <style>\n'
        '    .quickstart-sheet path, .quickstart-sheet line {\n'
        '      stroke: inherit !important;\n'
        '    }\n'
        '  </style>\n'
        + _arrow_defs() + "\n"
        # Page background
        f'  <rect width="100%" height="100%" fill="white" />\n'
        # Page outer frame — very thin, gives a visible page boundary
        # in the modal when the modal's surround is dark.
        f'  <rect x="0.5" y="0.5" width="{PAGE_W_MM - 1}" height="{PAGE_H_MM - 1}" '
        f'fill="none" stroke="#e5e5e5" stroke-width="0.3" />\n'
        f'{body}\n'
        f'</svg>\n'
    )

    svg_path.write_text(svg)

    # PDF — rsvg-convert preserves the SVG's mm dimensions, producing
    # a real 11×17 landscape page that prints to scale. SOURCE_DATE_EPOCH
    # makes Cairo's embedded /CreationDate, /ModDate, and /ID array
    # reproducible (Cairo honors the reproducible-builds standard); the
    # metadata lives inside compressed object streams, so regex-level
    # canonicalization in _canonicalize_pdf can't reach it the way it
    # does for ReportLab output.
    def _build_pdf(out_path):
        env = os.environ.copy()
        env.setdefault("SOURCE_DATE_EPOCH", "0")
        subprocess.run(
            ["rsvg-convert", "-f", "pdf", "-o", str(out_path), str(svg_path)],
            check=True,
            capture_output=True,
            env=env,
        )

    try:
        export_pdf(_build_pdf, str(pdf_path))
    except FileNotFoundError:
        print("rsvg-convert not found on PATH; skipping PDF generation.")
    except subprocess.CalledProcessError as e:
        print(f"rsvg-convert failed: {e.stderr.decode() if e.stderr else e}")

    print(f"-> {svg_path.relative_to(here.parent.parent)}")
    if pdf_path.exists():
        print(f"-> {pdf_path.relative_to(here.parent.parent)}")


if __name__ == "__main__":
    main()
