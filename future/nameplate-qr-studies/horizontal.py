"""A shallow nameplate composed around the visible mark, name and QR square."""

from __future__ import annotations

import argparse
import html
import json
from pathlib import Path

import cairosvg

from build import BLACK, HERE, WIDTH as EXISTING_WIDTH, Plate, lettering
from more import CODE, PAYLOAD


HEIGHT = 38.0
MODULE = 1.1
ACTIVE = 21 * MODULE
QUIET = 4 * MODULE
BRAND_EM = 8.2
LOGO_HEIGHT = 25.0
VISIBLE_GAP = 5.1
SERIAL_EM = 6.5
SERIAL_GAP = 3.0


def text_size(copy, em):
    _, bounds = lettering(copy, em, 0)
    return bounds[2]-bounds[0], bounds[3]-bounds[1]


class HorizontalPlate(Plate):
    def __init__(self, key, title, serial=None):
        super().__init__(key, title, MODULE, code=CODE, payload=PAYLOAD)
        self.serial = serial
        name_width, last_cap = text_size("MACHINE", BRAND_EM)
        logo_width = LOGO_HEIGHT * 656/688
        ink_width = logo_width + name_width + ACTIVE + 2*VISIBLE_GAP
        margin = (EXISTING_WIDTH - ink_width)/2
        extension = SERIAL_GAP + text_size(serial, SERIAL_EM)[0] if serial else 0
        self.width = EXISTING_WIDTH + extension
        self.height = HEIGHT
        self.name_top = (HEIGHT - ACTIVE)/2
        self.name_bottom = self.name_top + ACTIVE
        self.name_x = margin + logo_width + VISIBLE_GAP
        step = (ACTIVE - last_cap)/2
        self.logo(margin, (HEIGHT-LOGO_HEIGHT)/2, LOGO_HEIGHT)
        for row, word in enumerate(("HOME", "SODA", "MACHINE")):
            self.text(word, self.name_x, self.name_top + row*step, BRAND_EM, tracking=0)
        if serial:
            self.text(serial, self.name_x+name_width+SERIAL_GAP,
                      self.name_bottom-text_size(serial, SERIAL_EM)[1], SERIAL_EM, tracking=0)
        qr_x = self.name_x + name_width + extension + VISIBLE_GAP - QUIET
        qr_y = self.name_top - QUIET
        self.qr(qr_x, qr_y)
        self.qr_bounds = (qr_x, qr_y, 29*MODULE, 29*MODULE)
        self.qr_ink = (qr_x+QUIET, qr_y+QUIET, ACTIVE, ACTIVE)
        self.elements.append(
            f'<g class="alignment-guides" style="display:none" fill="none" '
            f'stroke="#91caff" stroke-width="0.16" stroke-dasharray="0.9 0.65">'
            f'<path d="M{margin-1},{self.name_top}H{self.width-margin+1} '
            f'M{margin-1},{self.name_bottom}H{self.width-margin+1}"/>'
            f'<rect x="{qr_x}" y="{qr_y}" width="{29*MODULE}" height="{29*MODULE}"/>'
            '</g>'
        )

    def audit(self):
        for label, x, y, width, height in self.bounds:
            assert "hosm.us" not in label.lower()
            # The entire four-module QR quiet zone is inside the plate. Visible
            # artwork has its own larger edge margin; the quiet zone is blank.
            minimum = 0.5 if label.startswith("QR ") else 2.4
            assert min(x, y, self.width-x-width, self.height-y-height) >= minimum, (self.key, label)
        for i, a in enumerate(self.bounds):
            for b in self.bounds[i+1:]:
                assert not (max(a[1],b[1]) < min(a[1]+a[3],b[1]+b[3])-.01 and
                            max(a[2],b[2]) < min(a[2]+a[4],b[2]+b[4])-.01), (self.key,a[0],b[0])
        assert abs(self.qr_ink[1]-self.name_top) < 1e-6
        assert abs(self.qr_ink[1]+self.qr_ink[3]-self.name_bottom) < 1e-6

    def svg(self):
        return (
            f'<svg xmlns="http://www.w3.org/2000/svg" class="nameplate" '
            f'width="{self.width:.5f}mm" height="{self.height}mm" '
            f'viewBox="0 0 {self.width:.5f} {self.height}" role="img" '
            f'aria-label="{html.escape(self.title)}. {self.width:.1f} by {self.height:g} millimetres.">'
            f'<title>{html.escape(self.title)}</title>'
            f'<desc>Three horizontal groups: faucet mark, the complete name, and a 21 by 21 QR. '
            f'QR modules are {MODULE} millimetres; payload {PAYLOAD}. '
            f'{"Unit number also lettered after MACHINE." if self.serial else "Unit identity encoded in QR."}</desc>'
            f'<rect x="0.12" y="0.12" width="{self.width-.24:.5f}" height="{self.height-.24}" '
            f'rx="3" fill="{BLACK}" stroke="#686a6d" stroke-width="0.24"/>'
            + "".join(self.elements) + '</svg>'
        )


def layouts():
    return [HorizontalPlate("wide", "Horizontal"),
            HorizontalPlate("number", "Number inline", "0001"),
            HorizontalPlate("prefix", "Number inline", "NO. 0001")]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--fragment-dir", type=Path)
    parser.add_argument("--png-dir", type=Path)
    args = parser.parse_args()
    plates = layouts()
    figures, manifest = [], []
    for plate in plates:
        plate.audit()
        svg = plate.svg()
        (HERE/f"horizontal-{plate.key}.svg").write_text(svg+"\n")
        if args.png_dir:
            args.png_dir.mkdir(parents=True, exist_ok=True)
            cairosvg.svg2png(bytestring=svg.encode(),
                            write_to=str(args.png_dir/f"horizontal-{plate.key}.png"),
                            output_width=round(plate.width*12), output_height=round(plate.height*12))
        figures.append(f'<figure data-layout="{plate.key}" data-width="{plate.width}" '
                       f'{"hidden" if plate.key == "prefix" else ""}>'
                       f'<figcaption>{plate.title} · {plate.width:.1f} × {plate.height:g} mm</figcaption>'
                       f'{svg}</figure>')
        manifest.append({"key":plate.key,"title":plate.title,"width_mm":plate.width,
                         "height_mm":plate.height,"serial":plate.serial,
                         "brand_em":BRAND_EM,"serial_em":SERIAL_EM if plate.serial else None,
                         "logo_height_mm":LOGO_HEIGHT,"name_top_mm":plate.name_top,
                         "name_bottom_mm":plate.name_bottom,"qr_ink_bounds_mm":plate.qr_ink,
                         "qr_quiet_bounds_mm":plate.qr_bounds,"bounds_mm":plate.bounds})
    meta = {"payload":PAYLOAD,"qr_version":1,"qr_mode":"alphanumeric",
            "error_correction":"M","active_modules":21,"module_mm":MODULE,
            "quiet_zone_modules":4,"visible_gap_mm":VISIBLE_GAP,"layouts":manifest}
    (HERE/"horizontal-layouts.json").write_text(json.dumps(meta,indent=2)+"\n")
    fragment = (HERE/"horizontal.template.html").read_text().replace("<!-- PLATES -->", "\n".join(figures))
    assert len(fragment.encode()) < 1_000_000
    (HERE/"nameplate-horizontal.html").write_text(fragment)
    if args.fragment_dir:
        args.fragment_dir.mkdir(parents=True, exist_ok=True)
        (args.fragment_dir/"nameplate-horizontal.html").write_text(fragment)
    print(json.dumps({"plates":[[p.key,round(p.width,3),p.height] for p in plates],
                      "active_qr_mm":ACTIVE,"brand_cap_mm":text_size("H",BRAND_EM)[1],
                      "fragment_bytes":len(fragment.encode())}))


if __name__ == "__main__":
    main()
