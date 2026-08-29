# Modern 1/4-inch push-connect installation scenes

These CAD frames are the customer path for a home whose cold-water plumbing
already includes **1/4-inch OD LLDPE and a push-to-connect joint**.  The scene's
existing joint is the measured John Guest PP0408W union in
`hardware/reference/jg-pp0408w`.  It is a visual representative for an
equivalent existing two-ended PTC joint; the customer's make may differ.

The complete modeled sequence is:

1. leave the 1/4-inch LLDPE connected and turn the household quarter-turn
   shutoff from ON to OFF;
2. press the existing union's release collet and withdraw the original line;
3. push the short supplied LLDPE jumper into the union;
4. push one PP0208E tee onto the jumper;
5. push the original loose line into the tee's other run port;
6. push the filter/appliance branch into the tee's third port and tug-check it.

The household plumbing receives one new fitting.  No threaded joint,
compression nut, screw, wrench, or routine line cut is part of this path.  A
damaged tube end still needs to be remade square before reuse, but that repair
is outside the normal sequence shown here.

Every household/tap-water tube uses the same white LLDPE material.  Modeled
lighting and recessed dark bores keep the white geometry legible in color and
grayscale without suggesting different tube types or printed patterns.  The
PP0208E is black polypropylene.  Every tube, fitting, valve, handle, bore, and
moving collet is 3D geometry; the page supplies its own instructional text and
action arrows.

## Regenerate

From the repository root:

```sh
tools/cad-venv/bin/python \
  hardware/quickstart/plumbing/modern/render_modern_tee.py
```

The eight guide-ready outputs are:

- `art/modern-water-on.png`
- `art/modern-water-off.png`
- `art/modern-release-pressed.png`
- `art/modern-release-withdrawn.png`
- `art/modern-tee-jumper.png`
- `art/modern-tee-mounted.png`
- `art/modern-tee-existing.png`
- `art/modern-tee-complete.png`

Two extra comparison states are retained for visual development:

- `art/modern-release-ready.png` — the collet at rest before the 1.335 mm press;
- `art/modern-tee-tug-check.png` — the white branch pulled outward 3.2 mm while
  it remains inside its gripping envelope.

Every output is a 2000 × 1100 RGBA PNG with a transparent canvas.  The renderer
uses a temporary warm-neutral matte to protect the light fitting surfaces,
then clears only the matte connected to the picture edge.  The ON/OFF pair,
release trio, and tee sequence each use their own fixed orthographic camera,
target, span, and canvas.  Persistent scene geometry is registered within each
group.  Long tubes leave the crop, so no arbitrary remote tube end appears.

## Held geometry

The existing PP0408W solid is photo-measured from the part in hand.  The
release scene uses its declared 1.335 mm collet travel and 16.0 mm tube
insertion depth.

The black PP0208E customer-facing instruction solid is generated locally from
the manufacturer's official drawing, [John Guest Polypropylene Equal Tee data
sheet Pp4608_01/23](https://www.johnguest.com/sites/jg/files/2023-04/JG%20Drinks%20Polypropylene%20Equal%20Tee%20Data%20Sheet.pdf):

- tube OD A: 6.35 mm;
- run face span B: 39.0 mm;
- center-to-port reach C: 19.5 mm;
- tube insertion D: 15.7 mm;
- maximum body/collar OD E: 16.3 mm;
- through bore F: 4.3 mm;
- branch-face envelope G: 27.7 mm.

The generator checks those published bounds before exporting any frame.  The
minor profile breakpoints not dimensioned by the manufacturer are symmetric
instruction-detail features inside that held envelope.
