"""Four compositions for a nameplate with concealed retention."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import cairosvg

from build import BLACK, HERE, HEIGHT, WHITE, WIDTH, Plate
from more import CODE, PAYLOAD


class HiddenPlate(Plate):
    def __init__(self, key, title):
        super().__init__(key, title, 0.9, code=CODE, payload=PAYLOAD)

    def svg(self):
        return (
            f'<svg xmlns="http://www.w3.org/2000/svg" class="nameplate" '
            f'width="{WIDTH}mm" height="{HEIGHT}mm" viewBox="0 0 {WIDTH} {HEIGHT}" '
            f'role="img" aria-label="{self.key}: {self.title}. Unit 0001 nameplate.">'
            f'<title>{self.key} · {self.title}</title>'
            f'<desc>{WIDTH} by {HEIGHT} millimetres. Concealed mounting. '
            f'QR encodes {PAYLOAD}; 21 by 21 active modules, '
            '0.9 millimetre pitch and four-module quiet zone.</desc>'
            f'<rect x="0.12" y="0.12" width="{WIDTH-.24}" height="{HEIGHT-.24}" '
            f'rx="3" fill="{BLACK}" stroke="#686a6d" stroke-width="0.24"/>'
            + "".join(self.elements) + '</svg>'
        )

    def audit(self):
        for label, x, y, width, height in self.bounds:
            assert min(x, y, WIDTH-x-width, HEIGHT-y-height) >= 2.4, (self.key, label)
            assert "hosm.us" not in label.lower()
        for i, a in enumerate(self.bounds):
            for b in self.bounds[i+1:]:
                assert not (
                    max(a[1], b[1]) < min(a[1]+a[3], b[1]+b[3]) - 0.01
                    and max(a[2], b[2]) < min(a[2]+a[4], b[2]+b[4]) - 0.01
                ), (self.key, "overlap", a[0], b[0])


def layouts():
    o = HiddenPlate("O", "Tall name")
    o.logo(8.6, 4, 30)
    o.qr(9.8, 36)
    for word, y in (("HOME", 5), ("SODA", 19), ("MACHINE", 33)):
        o.text(word, 44, y, 12, tracking=0)
    o.text("NO. 0001", 44, 54, 6.5, tracking=0)

    p = HiddenPlate("P", "Across the plate")
    p.logo(5, 5, 34)
    p.text("HOME", 41.5, 6, 10.5, tracking=0)
    p.text("SODA", 41.5, 20, 10.5, tracking=0)
    p.qr(75.8, 4.5)
    p.text("NO. 0001", 41.5, 34, 6.5, tracking=0)
    p.text("MACHINE", 5, 44, 20.6, tracking=0)

    q = HiddenPlate("Q", "Interlocking blocks")
    q.logo(5, 5, 43)
    q.text("HOME", 51, 6, 16, tracking=0)
    q.text("SODA", 51, 22, 16, tracking=0)
    q.text("0001", 51, 42, 7.2, tracking=0)
    q.qr(74, 36)
    q.text("MACHINE", 5, 53, 13.5, tracking=0)

    r = HiddenPlate("R", "Light lower field")
    r.logo(5, 4.5, 30)
    r.text("HOME SODA", 38, 5, 9.7, tracking=0)
    r.text("MACHINE", 38, 19, 12.9, tracking=0)
    r.elements.append(f'<rect x="4" y="36" width="96.53" height="26.1" '
                      f'rx="0.8" fill="{WHITE}"/>')
    r.qr(4, 36, light=True)
    r.text("SERIAL 0001", 65.3, 46.2, 7.5, align="center", tracking=0, fill=BLACK)
    return [o, p, q, r]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--fragment-dir", type=Path)
    parser.add_argument("--png-dir", type=Path)
    args = parser.parse_args()
    figures, manifest = [], []
    for plate in layouts():
        plate.audit()
        name = f'{plate.key.lower()}-{plate.title.lower().replace(" ", "-")}'
        svg = plate.svg()
        (HERE / f"{name}.svg").write_text(svg + "\n")
        if args.png_dir:
            args.png_dir.mkdir(parents=True, exist_ok=True)
            cairosvg.svg2png(bytestring=svg.encode(), write_to=str(args.png_dir/f"{name}.png"),
                            output_width=1254, output_height=793)
        figures.append(f'<figure data-layout="{plate.key}"><figcaption>{plate.key} · '
                       f'{plate.title}</figcaption>{svg}</figure>')
        ordinary = [b for b in plate.bounds if b[0] not in {
            "faucet mark", "QR including quiet zone", "HOME", "SODA", "MACHINE", "HOME SODA"}]
        manifest.append({"key": plate.key, "title": plate.title,
                         "serial_copy": ordinary[0][0], "serial_cap_mm": ordinary[0][4],
                         "bounds_mm": plate.bounds})
    meta = {"payload": PAYLOAD, "width_mm": WIDTH, "height_mm": HEIGHT,
            "retention": "concealed spring-rail concept; not production CAD",
            "qr_version": 1, "qr_mode": "alphanumeric", "error_correction": "M",
            "active_modules": 21, "quiet_zone_modules": 4, "module_mm": 0.9,
            "active_qr_mm": 18.9, "qr_with_margin_mm": 26.1, "visible_domain": False,
            "ratings": "separate permanent appliance-rating block", "layouts": manifest}
    (HERE/"hidden-layouts.json").write_text(json.dumps(meta, indent=2)+"\n")
    fragment = (HERE/"hidden.template.html").read_text().replace("<!-- PLATES -->", "\n".join(figures))
    assert len(fragment.encode()) < 1_000_000
    (HERE/"nameplate-hidden.html").write_text(fragment)
    if args.fragment_dir:
        args.fragment_dir.mkdir(parents=True, exist_ok=True)
        (args.fragment_dir/"nameplate-hidden.html").write_text(fragment)
    print(f"Four layouts. 21×21 QR; 0.9 mm modules; clear bounds and quiet zones. {len(fragment.encode()):,} bytes.")


if __name__ == "__main__":
    main()
