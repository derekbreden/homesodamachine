"""Name and unit-number compositions with a constant size for every brand word."""

from __future__ import annotations

import argparse
import json
import xml.etree.ElementTree as ET
from pathlib import Path

import cairosvg

from build import HERE, HEIGHT, WIDTH, lettering
from hidden import HiddenPlate, layouts as hidden_layouts
from more import PAYLOAD


def cap_height(copy, size):
    bounds = lettering(copy, size, 0)[1]
    return bounds[3] - bounds[1]


class CohesivePlate(HiddenPlate):
    def __init__(self, key, title):
        super().__init__(key, title)
        self.brand_sizes = []
        self.unit_options = {}

    def brand(self, copy, x, y, size, align="left"):
        self.brand_sizes.append(size)
        self.text(copy, x, y, size, align=align, tracking=0)

    def stack(self, x, y, size, step):
        for row, copy in enumerate(("HOME", "SODA", "MACHINE")):
            self.brand(copy, x, y + row*step, size)

    def unit(self, x, bottom, number_size, prefix_size, default="number", align="left"):
        self.default_unit = default
        for form, copy, size in (("number", "0001", number_size),
                                 ("prefix", "NO. 0001", prefix_size)):
            assert size >= 6.5
            y = bottom - cap_height(copy, size)
            self.text(copy, x, y, size, align=align, tracking=0)
            element, bounds = self.elements.pop(), self.bounds.pop()
            self.unit_options[form] = {"copy":copy, "em":size, "bounds_mm":bounds}
            display = "inline" if form == default else "none"
            self.elements.append(f'<g class="unit-option" data-unit="{form}" '
                                 f'data-default="{default}" style="display:{display}">{element}</g>')

    def audit(self):
        assert len(set(self.brand_sizes)) == 1, (self.key, "unequal brand type")
        assert self.brand_sizes[0] >= 6.5
        for option in self.unit_options.values():
            self.bounds.append(option["bounds_mm"])
            super().audit()
            self.bounds.pop()


def layouts():
    s = CohesivePlate("S", "Four-line name")
    s.logo(6.2, 5, 30.5)
    s.qr(7.69, 36.6)
    s.stack(42, 5.8, 12.4, 13.7)
    s.unit(42, 58.06, 12.4, 9.6)

    t = CohesivePlate("T", "Name first")
    t.stack(6.4, 5.8, 12.4, 13.7)
    t.unit(6.4, 58.06, 12.4, 9.6, default="prefix")
    t.logo(69.2, 5, 30.5)
    t.qr(70.69, 36.6)

    u = CohesivePlate("U", "Two lines")
    u.logo(7, 4, 31)
    u.qr(73, 6.9)
    u.brand("HOME SODA", 7, 36.9, 13.2)
    u.brand("MACHINE", 7, 51.2, 13.2)
    u.unit(71, 51.2 + cap_height("MACHINE", 13.2), 13.2, 6.5)

    v = CohesivePlate("V", "One continuous phrase")
    v.logo(16, 4, 34)
    v.qr(64, 7.75)
    v.brand("HOME SODA MACHINE", WIDTH/2, 43.5, 8.4, align="center")
    v.unit(WIDTH/2, 61.9, 10, 10, default="prefix", align="center")

    w = CohesivePlate("W", "Full-height mark")
    w.logo(4.5, 6, 43)
    w.stack(48, 6, 11.4, 10.5)
    w.qr(76, 36.8)
    w.unit(48, 54.05, 11.4, 6.5)

    x = CohesivePlate("X", "Number on the last line")
    x.logo(6.4, 3.2, 26)
    x.qr(72.96, 3.2)
    x.stack(6.4, 31, 13, 11.3)
    x.unit(69.25, 53.6 + cap_height("MACHINE", 13), 13, 6.5)
    return [s, t, u, v, w, x]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--fragment-dir", type=Path)
    parser.add_argument("--png-dir", type=Path)
    args = parser.parse_args()
    plates = layouts()
    figures, manifest = [], []
    baseline = hidden_layouts()[0]
    figures.append(f'<figure data-layout="O" data-reference="true" hidden>'
                   f'<figcaption>O · Tall name — reference</figcaption>{baseline.svg()}</figure>')
    for plate in plates:
        plate.audit()
        name = f'{plate.key.lower()}-{plate.title.lower().replace(" ", "-")}'
        svg = plate.svg()
        (HERE/f"{name}.svg").write_text(svg+"\n")
        if args.png_dir:
            args.png_dir.mkdir(parents=True, exist_ok=True)
            for form in ("number", "prefix"):
                # Only presentation state changes; both arrangements are checked above.
                root = ET.fromstring(svg)
                for group in root.findall(".//*[@data-unit]"):
                    group.set("style", "display:inline" if group.get("data-unit") == form else "display:none")
                cairosvg.svg2png(bytestring=ET.tostring(root),
                    write_to=str(args.png_dir/f"{name}-{form}.png"),
                    output_width=1254, output_height=793)
        figures.append(f'<figure data-layout="{plate.key}"><figcaption>{plate.key} · '
                       f'{plate.title}</figcaption>{svg}</figure>')
        manifest.append({"key":plate.key, "title":plate.title,
                         "brand_em":plate.brand_sizes[0], "default_unit":plate.default_unit,
                         "unit_options":plate.unit_options, "bounds_mm":plate.bounds})
    meta = {"payload":PAYLOAD, "width_mm":WIDTH, "height_mm":HEIGHT,
            "qr_version":1, "qr_mode":"alphanumeric", "error_correction":"M",
            "active_modules":21, "quiet_zone_modules":4, "module_mm":0.9,
            "qr_with_margin_mm":26.1, "visible_domain":False,
            "treatment":"white on black", "reference":"O · Tall name",
            "retention":"concealed-retention study; production CAD unchanged",
            "layouts":manifest}
    (HERE/"cohesive-layouts.json").write_text(json.dumps(meta, indent=2)+"\n")
    fragment = (HERE/"cohesive.template.html").read_text().replace("<!-- PLATES -->", "\n".join(figures))
    assert len(fragment.encode()) < 1_000_000
    (HERE/"nameplate-cohesive.html").write_text(fragment)
    if args.fragment_dir:
        args.fragment_dir.mkdir(parents=True, exist_ok=True)
        (args.fragment_dir/"nameplate-cohesive.html").write_text(fragment)
    print(f"Six layouts, both unit wordings checked. Uniform brand size; 21×21 QR at 0.9 mm. {len(fragment.encode()):,} bytes.")


if __name__ == "__main__":
    main()
