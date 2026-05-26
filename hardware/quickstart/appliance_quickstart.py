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


def placeholder(x, y, w, h, view_text, caption):
    """A drawing cell with an outlined drawing area + caption.

    The drawing area shows the brief's view description as wrapped text,
    so the placeholder hints at what the real drawing will look like
    when it's slotted in.
    """
    # Drawing area takes the top ~78% of the cell, caption gets the rest.
    draw_h = h * 0.78
    cap_h = h - draw_h
    draw_y = y
    cap_y = y + draw_h + 2

    # Wrap the view text to fit the cell width, in mm-ish character units.
    # Use a rough char-width of 2.0 mm at the placeholder text size to
    # pick a wrap column. Whatever it lands at is fine — the placeholder
    # is hint text, not the final art.
    inner_pad = 6.0
    wrap_cols = max(20, int((w - 2 * inner_pad) / 2.0))
    wrapped = textwrap.wrap(view_text, width=wrap_cols)
    line_h = 4.2

    text_lines = []
    text_y = draw_y + inner_pad + line_h
    for line in wrapped[:8]:  # cap at 8 lines so it doesn't overflow
        text_lines.append(
            f'<text x="{x + inner_pad:.2f}" y="{text_y:.2f}" '
            f'font-family="Helvetica, Arial, sans-serif" font-size="3.6" '
            f'fill="{COLOR_PLACEHOLDER_TEXT}">{line}</text>'
        )
        text_y += line_h

    return (
        # Drawing area outline
        f'<rect x="{x:.2f}" y="{draw_y:.2f}" width="{w:.2f}" height="{draw_h:.2f}" '
        f'fill="{COLOR_PLACEHOLDER_FILL}" stroke="{COLOR_PLACEHOLDER_STROKE}" '
        f'stroke-width="0.4" stroke-dasharray="2,2" rx="2" />\n'
        # Tag the placeholder
        f'<text x="{x + w - inner_pad:.2f}" y="{draw_y + inner_pad + 3:.2f}" '
        f'font-family="Helvetica, Arial, sans-serif" font-size="3.2" '
        f'fill="{COLOR_PLACEHOLDER_TEXT}" text-anchor="end" '
        f'font-style="italic">placeholder</text>\n'
        # View description as wrapped text
        + "\n".join(text_lines) + "\n"
        # Caption underneath, centered horizontally in the cell
        + f'<text x="{x + w / 2:.2f}" y="{cap_y + cap_h * 0.7:.2f}" '
        f'font-family="Helvetica, Arial, sans-serif" font-size="6.5" '
        f'font-weight="600" fill="{COLOR_PLAIN}" '
        f'text-anchor="middle">{caption}</text>'
    )


def main():
    here = Path(__file__).resolve().parent
    out_dir = here / "drawings" / "prints-and-guides"
    out_dir.mkdir(parents=True, exist_ok=True)
    svg_path = out_dir / "appliance.svg"
    pdf_path = out_dir / "appliance.pdf"

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
        },
        {
            "view": (
                "3/4 top view of the appliance, hopper lid lifted, "
                "funnel visible. One SodaStream concentrate bottle "
                "inverted over the funnel. One plain motion arrow on "
                "the bottle."
            ),
            "caption": "Empty a flavor into the hopper.",
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
        body_parts.append(placeholder(x, y, w, h, drawing["view"], drawing["caption"]))

    body = "\n".join(body_parts)

    svg = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'viewBox="0 0 {PAGE_W_MM} {PAGE_H_MM}" '
        f'width="{PAGE_W_MM}mm" height="{PAGE_H_MM}mm">\n'
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
