# Faucet display cover trial log

## PET-GF cover retention

Derek reported:

- "Many things about the faucet turned out great, cosmetic faces printed, etc."
- "The display cover does fit onto the dispense tip, and is technically retained, but it will fall off with even a gentle shake, or just a touch."
- "I can stretch them without breaking as far as 4.5 mm inwards in X on each wing at the same time."
- "They are tough though, and do spring back."

At the time of this report, the repository geometry has 0.30 mm radial
engagement, 0.15 mm radial clearance, 1.30 mm lip height and no designed
wing preload. The report does not identify the printed file or modified
slicer settings.

## Rear cover coverage

Derek reported: "The display cover does not actually wrap the tube in the
rear, and is in fact a bit short (not far enough aft) of even covering
everything even if it were the correct round shape."

The report does not identify a printed file hash.

## Sculpted cover — 2026-09-18

Derek reported that the new faucet print turned out great, the low-polygon
defects are gone, and the snap holds better but is still easier to remove than
he wants.

Mark2's completed job is `faucet-open-lever-mark2.gcode.3mf`. Its Sculpted cover
has 0.75 mm inward preload per wing, 3 mm tabs and 1 mm radial engagement,
printed bezel-down at CAD X +130°. The cover STL SHA-256 is
`eaada51cfc3ef32e03b150c8d828f45d11073ef703a638c1f05c4c0e876ee1ba`;
the tip STL is
`d868730d5db2ff2476391a870e9f2a686ea06be8ec6746011f7d07ef3e74ad06`.

The [A–F retention trials](../faucet-cover-retention/README.md) carry complete
covers for this same tip, with stronger preload, two tab heights and two print
orientations.
