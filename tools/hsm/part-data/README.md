# Printed-part document figures

`part-data` computes the figures two printed parts' documents quote:

- The water-inlet jet's drilling jaws.
- The valve seat's socket and plinth.

One JSON request is the command-line argument. It names `part`, an optional `method`,
and the raw upstream inputs that provider uses. The response is its JSON result on
stdout.

`comparison.json` and `tools/hsm/conversion-results/parts-final-2026-11-04.json` record the
fixed source/input hashes and completed provider comparisons.
