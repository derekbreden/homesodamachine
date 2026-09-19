# Nameplate QR studies

## O–R · Concealed retention

[Four compositions](nameplate-hidden.html) use the complete face, with no screw
heads. [The retention concept](retention.md) applies the Faucet print findings to
long spring rails behind the side edges of the plate. The production plate and
enclosure remain the screw-retained CAD; the concept has no physical fit result.

| Layout | Arrangement | Serial treatment |
| --- | --- | --- |
| [O · Tall name](o-tall-name.svg) | Tall three-line name beside the mark and code | Inline NO. 0001 |
| [P · Across the plate](p-across-the-plate.svg) | Mark, HOME, SODA and code above a full-width MACHINE | Inline NO. 0001 between the name lines |
| [Q · Interlocking blocks](q-interlocking-blocks.svg) | Large mark and HOME/SODA, with MACHINE beside the lower code | Number alone in the remaining space |
| [R · Light lower field](r-light-lower-field.svg) | Two-line name above a light QR and identification field | Inline SERIAL 0001 |

Each QR uses the same 21 × 21 active grid, 0.9 mm modules and a four-module quiet
zone: 26.1 mm overall. No domain is lettered. Ordinary appliance ratings belong on
their separate permanent field. Serial lettering is at least em 6.5, the type size
selected in the collar print comparison; this does not establish nameplate print
legibility. The drawings include no tiny serial heading.

```sh
tools/cad-venv/bin/python future/nameplate-qr-studies/hidden.py
```

The generator checks boundaries and separation, including QR quiet zones. It
accepts `--fragment-dir` and `--png-dir`. The SVGs use the actual brand paths and
outlined Helvetica Bold, with dimensions in millimetres. Apple Vision decodes
all four 1254 × 793 PNG renders to `HTTPS://HOSM.US/0001`. Desktop and narrow
browser reviews cover selection, layout and light/dark display. Physical printing,
QR scanning and snap retention remain untested for these nameplate concepts.

## G–N

[Eight further compositions](nameplate-more.html) use a 21 × 21 code, a larger brand,
and `SERIAL` above large `0001` lettering. No domain is lettered on these plates.
Seven have no dividing line; I has a horizontal rule.

L illustrates balanced use of space among logo, name, code and serial. It is an
example of compositional quality, not a prescribed layout or serial treatment.
The separate [refrigerant warning proof](../../hardware/markings/README.md) carries
the household warning specification and long safety copy.

| Layout | Arrangement | QR module |
| --- | --- | --- |
| [G · Code left](g-code-left.svg) | Large three-line brand; QR, ratings and serial below | 0.90 mm |
| [H · Code right](h-code-right.svg) | Large three-line brand; serial, ratings and QR below | 0.90 mm |
| [I · Two-line name](i-two-line-name.svg) | Wide name, ratings above a horizontal rule | 0.80 mm |
| [J · Upper code](j-upper-code.svg) | Code beside the name; ratings at the collar's em 6.5 | 0.80 mm |
| [K · Serial above code](k-serial-above-code.svg) | Large serial beside HOME and SODA, code below | 0.90 mm |
| [L · Big faucet](l-big-faucet.svg) | 36 mm faucet; serial beside the lower code | 0.90 mm |
| [M · Separate ratings label](m-separate-ratings-label.svg) | Brand, code and serial on this plate; ratings on a separate label | 0.90 mm |
| [N · Full-width MACHINE](n-full-width-machine.svg) | MACHINE across the plate beneath the mark, HOME, SODA and code | 0.80 mm |

The payload is `HTTPS://HOSM.US/0001`, explicitly encoded in QR alphanumeric mode,
version 1, correction M. A payload that exceeds that version fails generation.
Four-module margins give overall squares of 23.2 or 26.1 mm. Apple Vision decodes
all eight 1254 × 793 PNG renders to the exact uppercase payload. Physical QR printing
and scanning are untested. [The marking review](marking-review.md) records the scope
of the simplified electrical copy, separate refrigerant markings, and text print evidence.

```sh
tools/cad-venv/bin/python future/nameplate-qr-studies/more.py
```

The generator accepts the same `--fragment-dir` and `--png-dir` options as `build.py`.

## A–F

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
