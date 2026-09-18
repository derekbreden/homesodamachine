"""Eight nameplate compositions with version-1 QR codes and no lettered domain."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import cairosvg
import qrcode
from qrcode.util import MODE_ALPHA_NUM, QRData

from build import HERE, HEIGHT, WHITE, WIDTH, Plate


PAYLOAD = "HTTPS://HOSM.US/0001"
CODE = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_M, border=4)
CODE.add_data(QRData(PAYLOAD, mode=MODE_ALPHA_NUM))
CODE.make(fit=False)
assert CODE.modules_count == 21
assert len(CODE.get_matrix()) == 29


def plate(key, title, pitch=0.9):
    return Plate(key, title, pitch, code=CODE, payload=PAYLOAD)


def brand(p, logo_height=29.4):
    p.logo(12, 4, logo_height)
    for i, word in enumerate(("HOME", "SODA", "MACHINE")):
        p.text(word, 45.15, 4 + i * 10.6, 10.2, tracking=0)


def serial(p, x=86.5, y=46):
    p.text("SERIAL", x, y, 2.8, align="center")
    p.text("0001", x, y + 5.5, 9.4, align="center", tracking=0)


def rating(p, x, y, size=3.7, step=5.0):
    p.text("120V 60Hz", x, y, size)
    p.text("5A 600W", x, y + step, size)


def layouts():
    g = plate("G", "Code left")
    brand(g)
    g.qr(11.5, 37.6)
    rating(g, 43, 46.8, 3.7)
    serial(g)

    h = plate("H", "Code right")
    brand(h)
    serial(h, 23, 46)
    rating(h, 40, 46.8, 3.7)
    h.qr(69.8, 37.6)

    i = plate("I", "Two-line name", 0.8)
    i.logo(10.5, 3.7, 26)
    i.text("HOME SODA", 39, 5, 9.0, tracking=0)
    i.text("MACHINE", 39, 16.5, 12.0, tracking=0)
    i.text("120V 60Hz 5A 600W", WIDTH/2, 33.0, 4.0, align="center")
    i.elements.append(f'<path d="M13,38.2H91.5" stroke="{WHITE}" stroke-width="0.45"/>')
    i.bounds.append(("horizontal rule", 13, 37.975, 78.5, 0.45))
    i.qr(16.5, 40.6)
    serial(i, 80, 47.0)

    j = plate("J", "Upper code", 0.8)
    j.logo(12, 4, 31)
    for word, y in (("HOME", 5), ("SODA", 15.3), ("MACHINE", 27)):
        j.text(word, 45.15, y, 10.2, tracking=0)
    j.qr(77.2, 2.4)
    rating(j, 14, 43, 6.5, 7.3)
    serial(j)

    k = plate("K", "Serial above code")
    brand(k)
    serial(k, 88.8, 5.0)
    rating(k, 14, 44, 5.0, 6.0)
    k.qr(73.5, 37.6)

    l = plate("L", "Big faucet")
    l.logo(12, 4, 36)
    for row, word in enumerate(("HOME", "SODA", "MACHINE")):
        l.text(word, 52, 5 + row * 9.6, 9.0, tracking=0)
    rating(l, 14, 50.5, 3.8, 5.0)
    serial(l, 57, 46)
    l.qr(73.5, 37.6)

    m = plate("M", "Separate ratings label")
    brand(m, 31)
    m.qr(18, 37.6)
    serial(m, 79, 46)

    n = plate("N", "Full-width MACHINE", 0.8)
    n.logo(13, 3.2, 26)
    n.text("HOME", 44, 3.3, 10.2, tracking=0)
    n.text("SODA", 44, 15.0, 10.2, tracking=0)
    n.qr(77.2, 2.4)
    n.text("MACHINE", 13, 32, 16.8, tracking=0)
    n.text("120V 60Hz 5A 600W", 14, 53.0, 4.5)
    serial(n, 86.5, 49.5)
    return [g, h, i, j, k, l, m, n]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--fragment-dir", type=Path)
    parser.add_argument("--png-dir", type=Path)
    args = parser.parse_args()
    plates = layouts()
    figures, manifest = [], []
    for p in plates:
        p.audit()
        name = f'{p.key.lower()}-{p.title.lower().replace(" ", "-")}'
        svg = p.svg()
        assert not any("hosm.us" in str(b[0]).lower() for b in p.bounds)
        (HERE / f"{name}.svg").write_text(svg + "\n")
        if args.png_dir:
            args.png_dir.mkdir(parents=True, exist_ok=True)
            cairosvg.svg2png(bytestring=svg.encode(), write_to=str(args.png_dir / f"{name}.png"),
                            output_width=1254, output_height=793)
        figures.append(f'<figure data-layout="{p.key}"><figcaption>{p.key} · '
                       f'{p.title}</figcaption>{svg}</figure>')
        manifest.append({"key":p.key, "title":p.title, "module_mm":p.pitch,
                         "active_qr_mm":round(21*p.pitch, 2),
                         "qr_with_margin_mm":round(29*p.pitch, 2),
                         "rating_on_plate":p.key != "M", "serial_em":9.4,
                         "serial_label_em":2.8})
    (HERE / "more-layouts.json").write_text(json.dumps({"payload":PAYLOAD,
                "width_mm":WIDTH,"height_mm":HEIGHT,"qr_version":1,"error_correction":"M",
                "qr_mode":"alphanumeric","quiet_zone_modules":4,
                "visible_domain":False,"layouts":manifest}, indent=2) + "\n")
    fragment = (HERE / "more.template.html").read_text().replace("<!-- PLATES -->", "\n".join(figures))
    assert len(fragment.encode()) < 1_000_000
    (HERE / "nameplate-more.html").write_text(fragment)
    if args.fragment_dir:
        args.fragment_dir.mkdir(parents=True, exist_ok=True)
        (args.fragment_dir / "nameplate-more.html").write_text(fragment)
    print(f"Eight 21×21 layouts; bounds, quiet zones, screw clearances and visible copy checked. {len(fragment.encode()):,} bytes.")


if __name__ == "__main__":
    main()
