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

## Complete tip and two Sculpted covers — 2026-09-18, Mark2

The submitted job was `faucet-display-mark2.gcode.3mf`: one production tip
at CAD X +40°, one complete cover on its front wall at +40°, and an identical
complete cover bezel up at −50°. The retained native archive SHA-256 is
`defdde770a54b0f22db742c291448d5238ae0a6fe6165c4670103c0786b3034e`.
The [submission record](../../faucet/faucet-display-petgf.readiness.json)
identifies the exact geometry, 0.24 mm layer profile and printer startup.

Both covers use 1.25 mm inward preload per wing, 3.00 mm lips with 0.25 mm
inner-corner relief, 1.20 mm radial engagement, 0.48 mm groove roof allowance
and 0.30 mm clearance at each groove end.

Derek reported that both covers snapped into place and retained firmly.
He rejected the tip's +40° orientation because supports marked its finished
surface, and rejected the front-wall-down cover because its visible face
contacted the print bed. The requested full Sculpted print uses white PET-GF,
with the tip at −105° and cover bezel up at −50°.

This is a physical seating and retention observation; repeated cycling and
long-term preload were not reported.
