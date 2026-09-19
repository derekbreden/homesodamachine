# Nameplate QR studies

## Design brief

The current direction is a wide, shallow plate with faucet, complete name and
QR alongside one another. The outline follows that composition. The name reads as a continuous
`HOME SODA MACHINE`, followed by `NO. 0001` or `0001`. All three words share one
font size within each composition. The mark and code fit around that reading
sequence. White artwork sits on the black plate; no inverted identification field
or lettered domain is specified. The nameplate uses concealed retention in these
studies, with ordinary ratings on a separate permanent field.

## Horizontal composition

[The horizontal study](nameplate-horizontal.html) aligns the top and bottom of
the name with the QR's visible 23.1 mm square. The faucet is 25 mm tall, extending
0.95 mm above and below those guides. The visible gaps between the three groups
are both 5.1 mm. The QR's complete four-module quiet zone fits between the name
and the plate edge.

| Drawing | Face size | Identification |
| --- | --- | --- |
| [Horizontal](horizontal-wide.svg) | 104.53 × 38 mm | Unit identity in the QR |
| [Number inline](horizontal-number.svg) | 120.63 × 38 mm | MACHINE followed by 0001 |
| [Number with prefix](horizontal-prefix.svg) | 133.72 × 38 mm | MACHINE followed by NO. 0001 |

All three keep the same artwork sizes. The middle text column expands for a
printed number; the plate gains the necessary width. The comparison displays
both visible plates at one scale. Its guides show the name/active-code alignment
and the complete QR quiet zone; design controls choose the number wording.

Brand lettering is em 8.2, with a 5.90 mm H and identical size across the three
words. The serial is em 6.5. Every code is version 1, correction M, in alphanumeric
mode, with 1.1 mm modules. Apple Vision decodes all three full-plate PNG renders
to `HTTPS://HOSM.US/0001`; physical scan performance is not yet established.

The current enclosure's horizontal field is 114.68 mm before its two 5 mm margins.
The 104.53 × 38 mm face fits inside the existing 104.53 × 66.07 mm plate outline.
The numbered versions need more width than the current field provides. Pocket
and retention geometry remain a separate CAD step; these drawings do not change
the production enclosure.

```sh
tools/cad-venv/bin/python future/nameplate-qr-studies/horizontal.py
```

`--fragment-dir` writes the conversation comparison; `--png-dir` renders the
three plates. Generation checks the visible-art margins, the entire QR quiet
zone, non-overlap and the equality of name and active-QR heights.

## S–X · Name and number

[Six compositions](nameplate-cohesive.html) explore the reading sequence at the
existing 104.53 × 66.07 mm size. The comparison can show any candidate beside O.
Its design control switches the unit wording between `0001` and `NO. 0001`;
both versions have checked artwork bounds and QR quiet zones.

| Layout | Arrangement | Name em |
| --- | --- | --- |
| [S · Four-line name](s-four-line-name.svg) | Number continues the right-hand name column; mark and code at left | 12.4 |
| [T · Name first](t-name-first.svg) | Name and number at left; mark and code at right | 12.4 |
| [U · Two lines](u-two-lines.svg) | HOME SODA above MACHINE 0001; mark and code above the wording | 13.2 |
| [V · One continuous phrase](v-one-continuous-phrase.svg) | Complete name on one line, with identification directly below | 8.4 |
| [W · Full-height mark](w-full-height-mark.svg) | Large mark beside a compact, unbroken three-line name | 11.4 |
| [X · Number on the last line](x-number-on-the-last-line.svg) | Three-line name under the mark, ending in MACHINE 0001 | 13.0 |

The name uses outlined Helvetica Bold. The smallest alternate serial is em 6.5.
Every QR is white on black, with 21 × 21 active modules, 0.9 mm pitch and a
four-module quiet zone (26.1 mm overall). Apple Vision decodes all twelve
1254 × 793 renders, covering both unit wordings, to `HTTPS://HOSM.US/0001`.
The artwork and browser checks do not establish physical print or scan results.

```sh
tools/cad-venv/bin/python future/nameplate-qr-studies/cohesive.py
```

`--fragment-dir` writes the conversation comparison to a supplied directory;
`--png-dir` renders both wordings of each composition. The generator rejects
unequal brand-word sizes, overlaps, insufficient edge margins and visible domains.

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
