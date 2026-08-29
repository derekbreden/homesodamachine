# Modern 1/4-inch water-line tee scenes

These registered-camera CAD frames explore the install-kit path for a home
whose cold-water feed under the sink is already **1/4-inch OD LLDPE**.  The
existing line is cool gray, the appliance branch is light gray-white with a
narrow modeled tracer for grayscale legibility, and the union tee is black
polypropylene.

The first frame keeps the two square-cut existing-line ends apart and stages
the tee plus the new appliance branch below them.  The second frame seats both
run ends and the white branch in the fitting.  No connector or tube is a 2D
overlay.

## Regenerate

From the repository root:

```sh
tools/cad-venv/bin/python \
  hardware/quickstart/plumbing/modern/render_modern_tee.py
```

Outputs:

- `art/modern-inline-tee-before.png`
- `art/modern-inline-tee-after.png`

Both outputs are 2000 × 1100 white-background PNGs with one fixed orthographic
camera, target, span, and canvas.  The existing line continues through the
left and right frame edges, and the appliance branch continues through the
lower-right crop; no arbitrary remote tube end is shown.

## Geometry dependency

The tee comes directly from
`hardware/reference/tee-connector/tee-connector.step`.  That file is the
repository's current visual reference for the John Guest PP0208E and is a
McMaster 51175K143 geometric stand-in, not a measured production PP0208E.  The
source dependency stays explicit in `render_modern_tee.py` so a future measured
PP0208E solid replaces the scene geometry in one place.

Tube outside diameter is 6.35 mm (1/4 inch).  The open state models hollow,
square-cut ends; the connected state carries each tube four millimetres beyond
the visible collet face so the connection cannot read as a gap.
