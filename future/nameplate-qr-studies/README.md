# Nameplate QR studies

Six layouts on the 104.53 × 66.07 mm nameplate, with the production screw positions,
faucet mark, Helvetica Bold lettering, serial number, input rating and notices.
The QR payload is `https://hosm.us/0001`; the visible link is `hosm.us/0001`.

| Layout | Arrangement | QR module | QR with clear margin |
| --- | --- | --- | --- |
| [A · Lower right](a-lower-right.svg) | Full-size brand, link and details at left | 0.60 mm | 19.80 mm |
| [B · Upper corner](b-upper-corner.svg) | Code beside HOME and SODA, centered details | 0.56 mm | 18.48 mm |
| [C · Serial group](c-serial-group.svg) | Code and prominent serial grouped below the brand | 0.60 mm | 19.80 mm |
| [D · Right column](d-right-column.svg) | Code, link and serial in a separate column | 0.70 mm | 23.10 mm |
| [E · White footer](e-white-footer.svg) | Code and details in one light inlay field | 0.60 mm | 19.80 mm |
| [F · Centered](f-centered.svg) | Code on the center axis, electrical details beside it | 0.60 mm | 19.80 mm |

[The comparison](nameplate-qr.html) is an inline visualization fragment. A–F select an
enlarged plate. The host's design controls select black-on-white or white-on-black QR
treatments. The SVGs contain outlined type and retain their millimetre dimensions.

The code is QR version 2, error correction M, with 25 × 25 active modules and a
four-module clear margin on each side, as specified by
[DENSO WAVE](https://www.qrcode.com/en/howto/code.html). The drawings represent flat
artwork and are layout studies; they contain no new CAD solids or print scan results.
Apple Vision decodes all six 1254 × 793 PNG renders to `https://hosm.us/0001`,
including the five white-on-black codes and the black-on-white footer code.

Regenerate on macOS:

```sh
tools/cad-venv/bin/python future/nameplate-qr-studies/build.py
```

`--fragment-dir` also writes the conversation fragment into a supplied directory.
`--png-dir` renders the six plates as PNGs. Generation checks artwork bounds,
clearance to the screw counterbores, and separation of artwork from QR clear margins.
