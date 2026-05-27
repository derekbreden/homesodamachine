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

Color system from the brief:
- blue   = carbonated water
- red    = CO2
- gray   = tap water (substituted for "white" — white doesn't render on
           a white page; gray reads as the neutral / default channel)

Most of the drawings don't yet exist as real line-art. Where they don't,
the cell shows an outlined placeholder with the brief's view description
inside, so the layout's shape is visible and the next drawing pass
slots straight in.

Run:
    tools/cad-venv/bin/python hardware/quickstart/appliance_quickstart.py
"""

import math
import re
import subprocess
import textwrap
from pathlib import Path


# Page — 11×17 landscape, in mm
PAGE_W_MM = 431.8   # 17 in
PAGE_H_MM = 279.4   # 11 in

# Margin around the four-cell grid
MARGIN_MM = 14.0

# Color system
COLOR_CARBONATED = "#1f6feb"   # blue
COLOR_CO2 = "#d63a3a"          # red
COLOR_TAP = "#6e6e6e"          # medium gray (substitute for "white")
COLOR_PLAIN = "#1a1a1a"        # plain motion arrows, captions, page text
COLOR_PLACEHOLDER_STROKE = "#bdbdbd"
COLOR_PLACEHOLDER_FILL = "#fafafa"
COLOR_PLACEHOLDER_TEXT = "#888888"

ARROW_COLORS = {
    "blue": COLOR_CARBONATED,
    "red": COLOR_CO2,
    "gray": COLOR_TAP,
    "dark": COLOR_PLAIN,
}


def _arrow_defs():
    """SVG <defs> with one arrowhead marker per color. Each <line> /
    <path> arrow references its marker via marker-end=url(#arrow-<color>).
    The marker's tip extends well past refX so the line's round endcap
    sits under the triangle fill and the visible tip reads sharp.
    """
    markers = []
    for name, color in ARROW_COLORS.items():
        markers.append(
            f'<marker id="arrow-{name}" viewBox="0 0 12 10" refX="9" refY="5" '
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
        f'marker-end="url(#arrow-{color})" />'
        f'</g>'
    )


def _stub_arrow(target_x, target_y, dx, dy, color="dark", sw=1.2, length=5):
    """Short arrow whose tip lands at (target_x, target_y), pointing in
    direction (dx, dy). Used for the two inward stub-arrows on the tee."""
    mag = math.sqrt(dx * dx + dy * dy)
    ux, uy = dx / mag, dy / mag
    x1, y1 = target_x - length * ux, target_y - length * uy
    return _straight_arrow(x1, y1, target_x, target_y, color, sw)


def cell_rect(col, row):
    """Return (x, y, w, h) for the cell at column col (0..1) and row row (0..1).

    Cells fill the page minus MARGIN around the perimeter, with a small
    inner gutter between cells.
    """
    gutter = 8.0
    cols, rows = 2, 2
    avail_w = PAGE_W_MM - 2 * MARGIN_MM - (cols - 1) * gutter
    avail_h = PAGE_H_MM - 2 * MARGIN_MM - (rows - 1) * gutter
    cw = avail_w / cols
    ch = avail_h / rows
    x = MARGIN_MM + col * (cw + gutter)
    y = MARGIN_MM + row * (ch + gutter)
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
    rectangle (x, y, w, h) on the host page, preserving aspect ratio."""
    viewbox, inner = _read_svg_for_embed(source_path)
    return (
        f'<svg x="{x:.2f}" y="{y:.2f}" width="{w:.2f}" height="{h:.2f}" '
        f'viewBox="{viewbox}" preserveAspectRatio="xMidYMid meet">\n'
        f'{inner}\n'
        f'</svg>'
    )


def _caption_text(x, y, w, h, caption):
    """Bold centered caption underneath the drawing area."""
    return (
        f'<text x="{x + w / 2:.2f}" y="{y + h * 0.7:.2f}" '
        f'font-family="Helvetica, Arial, sans-serif" font-size="6.5" '
        f'font-weight="600" fill="{COLOR_PLAIN}" '
        f'text-anchor="middle">{caption}</text>'
    )


def _placeholder_body(x, y, w, h, view_text):
    """Dashed-outline drawing area showing the brief's view description.

    Used when there's no real line art to embed for a given cell yet.
    Reads as "this is what's coming," not as final art.
    """
    inner_pad = 6.0
    wrap_cols = max(20, int((w - 2 * inner_pad) / 2.0))
    wrapped = textwrap.wrap(view_text, width=wrap_cols)
    line_h = 4.2

    text_lines = []
    text_y = y + inner_pad + line_h
    for line in wrapped[:8]:
        text_lines.append(
            f'<text x="{x + inner_pad:.2f}" y="{text_y:.2f}" '
            f'font-family="Helvetica, Arial, sans-serif" font-size="3.6" '
            f'fill="{COLOR_PLACEHOLDER_TEXT}">{line}</text>'
        )
        text_y += line_h

    return (
        f'<rect x="{x:.2f}" y="{y:.2f}" width="{w:.2f}" height="{h:.2f}" '
        f'fill="{COLOR_PLACEHOLDER_FILL}" stroke="{COLOR_PLACEHOLDER_STROKE}" '
        f'stroke-width="0.4" stroke-dasharray="2,2" rx="2" />\n'
        f'<text x="{x + w - inner_pad:.2f}" y="{y + inner_pad + 3:.2f}" '
        f'font-family="Helvetica, Arial, sans-serif" font-size="3.2" '
        f'fill="{COLOR_PLACEHOLDER_TEXT}" text-anchor="end" '
        f'font-style="italic">placeholder</text>\n'
        + "\n".join(text_lines)
    )


def cell(x, y, w, h, view_text, caption, embed_path=None, arrows_fn=None):
    """Render one drawing cell — drawing area on top, caption below.

    If embed_path is given, the drawing area shows that SVG scale-fit
    into the cell. Otherwise the drawing area shows a dashed-outline
    placeholder with the brief's view description inside. If arrows_fn
    is given, it's called with (x, y, w, draw_h) and the returned SVG
    is overlaid on top of the cell body — used to put the brief's
    motion / rotation / stub arrows on the page even before their
    precise targets exist in the line-art.
    """
    draw_h = h * 0.78
    cap_y = y + draw_h + 2
    cap_h = h - draw_h

    if embed_path:
        body = _embed_svg(x, y, w, draw_h, embed_path)
    else:
        body = _placeholder_body(x, y, w, draw_h, view_text)
    arrows = arrows_fn(x, y, w, draw_h) if arrows_fn else ""
    return body + "\n" + arrows + "\n" + _caption_text(x, cap_y, w, cap_h, caption)


# ── Per-cell arrow specs ────────────────────────────────────────────
#
# Each function takes the cell's drawing-area bounds (x, y, w, draw_h)
# and returns SVG for the arrows. Positions are approximate stand-ins
# for the brief's specified arrow targets — the real targets (CO2
# inlet, water inlet, hopper opening, cylinder valves) aren't yet in
# the line-art, so these point at sensible spots that demonstrate the
# color system and arrow vocabulary.


def _arrows_connect_co2(x, y, w, draw_h):
    """Drawing 1: single red arrow pointing at the CO2 inlet's mouth on
    the right side face. The mouth — the visible entry plane at the
    far end of the coupling body's cup — projects to cell-frac
    (0.456, 0.531)."""
    return _straight_arrow(
        x + 0.30 * w, y + 0.18 * draw_h,
        x + 0.436 * w, y + 0.500 * draw_h,
        color="red",
    )


def _arrows_tee_into_water(x, y, w, draw_h):
    """Drawing 2: gray rotation arrow on the angle stop + two stub
    arrows pointing inward at the tee's outlets + gray straight arrow
    at the appliance water inlet. Laid out in a horizontal strip in
    the lower half of the placeholder so the view-description text
    above stays legible."""
    y_strip = y + 0.65 * draw_h
    target_x = x + 0.48 * w
    return (
        _rotation_arrow(x + 0.14 * w, y_strip, 5, 30, 240, color="gray")
        + _stub_arrow(target_x - 2, y_strip, +1, 0, color="gray")
        + _stub_arrow(target_x + 2, y_strip, -1, 0, color="gray")
        + _straight_arrow(
            x + 0.74 * w, y_strip,
            x + 0.92 * w, y_strip,
            color="gray",
        )
    )


def _arrows_open_valves(x, y, w, draw_h):
    """Drawing 3: red rotation arrow on the CO2 cylinder valve + gray
    rotation arrow on the angle-stop handle, paired side-by-side."""
    y_strip = y + 0.65 * draw_h
    return (
        _rotation_arrow(x + 0.30 * w, y_strip, 7, 30, 240, color="red")
        + _rotation_arrow(x + 0.70 * w, y_strip, 7, 30, 240, color="gray")
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

    # Existing line-art sources that exist today, used where they fit
    # the brief's specified view. None of them carry the supply-side
    # subjects (CO2 cylinder + regulator + hose, under-counter
    # plumbing, concentrate bottle), so drawings 2 and 3 stay as
    # placeholders and drawings 1 and 4 show only the appliance side
    # of their scene.
    enclosure_front = repo_root / "hardware" / "printed-parts" / "enclosure" / "drawings" / "line-art" / "enclosure-iso-front.svg"
    enclosure_back = repo_root / "hardware" / "printed-parts" / "enclosure" / "drawings" / "line-art" / "enclosure-iso-back.svg"

    # The four drawings, sourced from
    # marketing/unboxing-and-quickstart.md.
    drawings = [
        {
            "view": (
                "Front 3/4 view of the appliance. The CO2 cylinder sits "
                "in the foreground beside the appliance, regulator on "
                "top, hose extending toward the front-panel CO2 inlet. "
                "Single red arrow at the front-panel CO2 inlet."
            ),
            "caption": "Connect the CO2.",
            "embed": enclosure_front,
            "arrows": _arrows_connect_co2,
        },
        {
            "view": (
                "Under-counter view. The customer's angle stop comes out "
                "of the wall with its outlet now empty. The existing "
                "supply line dangles disconnected beside it. The tee "
                "floats in the gap, with the 3/8\" tube pre-attached to "
                "one outlet, extending across the drawing toward the "
                "appliance's back-panel water inlet. Gray rotation arrow "
                "on the angle stop. Two gray stub-arrows pointing inward "
                "at the tee's two open outlets. Gray arrow at the "
                "appliance water inlet."
            ),
            "caption": "Tee into the water. Run the tube to the device.",
            "embed": None,
            "arrows": _arrows_tee_into_water,
        },
        {
            "view": (
                "Two foreground subjects side by side at the same scale: "
                "the CO2 cylinder with its top valve handle, and the "
                "angle stop with the tee on it and its shutoff handle. "
                "Red rotation arrow at the CO2 cylinder valve. Gray "
                "rotation arrow at the angle stop handle."
            ),
            "caption": "Open the CO2. Open the water.",
            "embed": None,
            "arrows": _arrows_open_valves,
        },
        {
            "view": (
                "3/4 top view of the appliance, hopper lid lifted, "
                "funnel visible. One SodaStream concentrate bottle "
                "inverted over the funnel. One plain motion arrow on "
                "the bottle."
            ),
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
    for (col, row), drawing in zip(cells, drawings):
        x, y, w, h = cell_rect(col, row)
        body_parts.append(
            cell(
                x, y, w, h,
                drawing["view"], drawing["caption"],
                embed_path=drawing["embed"],
                arrows_fn=drawing["arrows"],
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
    # a real 11×17 landscape page that prints to scale.
    try:
        subprocess.run(
            ["rsvg-convert", "-f", "pdf", "-o", str(pdf_path), str(svg_path)],
            check=True,
            capture_output=True,
        )
    except FileNotFoundError:
        print("rsvg-convert not found on PATH; skipping PDF generation.")
    except subprocess.CalledProcessError as e:
        print(f"rsvg-convert failed: {e.stderr.decode() if e.stderr else e}")

    print(f"-> {svg_path.relative_to(here.parent.parent)}")
    if pdf_path.exists():
        print(f"-> {pdf_path.relative_to(here.parent.parent)}")


if __name__ == "__main__":
    main()
