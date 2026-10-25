# YYFKGCP 4-pin magnetic pogo connector

[`yyfkgcp_pogo_4p.py`](yyfkgcp_pogo_4p.py) models the YYFKGCP four-pin magnetic pogo
connector with ears ([B0GCBNTBT8](https://www.amazon.com/dp/B0GCBNTBT8)) and exports its two
halves, [`pogo-4p-female.step`](pogo-4p-female.step) and
[`pogo-4p-male.step`](pogo-4p-male.step). The female half carries four flush gold pads between
two magnets; the male half carries four spring pins between two magnets.

```sh
tools/cad-venv/bin/python hardware/reference/yyfkgcp-pogo-4p/yyfkgcp_pogo_4p.py
```

## Envelope

The model is the external envelope only, read off the listing's two drawings.

| | |
|---|---|
| body, either half | one moulded body 4.00 mm deep: a 17.54 × 4.00 mm stadium nose from the mating face to the ear plate, the plate, and the stadium again behind it |
| ear plate | 1.00 mm thick, its front face 2.00 mm under the mating face; two ears, each a semicircle on the body's width, holed Ø1.50 mm on a 20.44 mm pitch |
| ear reach | 23.4 mm overall, read off the drawing's scale; the drawing does not dimension it |
| contacts | four on a 2.54 mm pitch, each with a Ø0.70 mm solder tail standing 1.50 mm off the back |
| magnets | flush in the nose face on a 13.54 mm pitch, N at −X as drawn face-on |
| male pins | Ø0.90 mm, standing 1.00 mm above the nose at rest (5.00 ± 0.15 mm overall), 1.10 mm of travel |
| female pads | Ø1.50 mm, flush |

The model's frame puts the mating face on the XY plane at Z = 0, facing +Z, with the body
hanging −Z. The long axis is X, with the contacts and ears on it, and the origin is the face's
centre. `build_male` takes the pins' reach, so a caller mating the pair across a known gap
draws them at that reach instead of at rest.

## Ratings

The listing states, per contact, 12 V and 2 A with 30 mΩ maximum at working height; a spring
force of 45 ± 10 gf at the 1.0 mm working height and 10,000 cycles; a UL94 V-0 housing; and
C3604 brass plunger and barrel, gold over nickel.

## Physical evidence

[`physical-observations.json`](physical-observations.json) records the founder's accepted
connector fit and mating/compression in a printed seat coupon, reported 2026-10-04. The report
gives no numerical gap or pin-travel measurement. Insert retention, installed face gap,
attracting orientation, four-channel continuity, magnetic retention force, operating contact
resistance and endurance have no reported result.
