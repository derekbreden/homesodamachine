# Rear identification

Colour tiles identify the selected rear grid. TAP and DRAIN use white, SODA blue,
CO2 red and both FLAVOR ports black, with contrasting raised lettering. The tiles' centres follow rows
Z331.2, Z294.2 and Z264; their bores follow the actual fitting axes. TAP's bore
therefore includes the scanned adapter's offset from the nominal grid.

Each tile slides in a continuous side-rail channel at Y469.3–471.1, retaining
4 mm of wall before the Y465.3 nut plane and 0.2 mm below the Y471.3 flange.
Each side rail overlaps the tile's edge, leaving the color face exposed.
The channel floor is Z240.6. The upper tiles finish at Z355. Each lower tile
ends 0.2 mm below the next tile, with the words above the upper two fitting rows and below the bottom row. The rails retain 3 mm of fore–aft stock at
Y471.3–474.3, with 3 mm outer roots beside the tile channels. Their complete
sections remain plain through exterior fluting. Print with the flat back on the
bed and the raised words up. The [Mark1 identification plate](../trial-preparation/README.md)
uses PETG Basic for the opaque colours and carries the accepted filament assignments,
layer heights and side-specific trim.

The [First Edition nameplate](../nameplate/README.md) sits between the rear corner
and the port-label rail. Screws fasten its flat back to the receiver. The
[nameplate fit review](../nameplate/production-fit.json) records its production geometry.

[`rear_identification.rs`](rear_identification.rs) cuts the six compact two-colour tiles from the
above-core layout's rear grid and the bulkhead rings' words, and writes the numbers the installed
machine places and colours them by. The nameplate uses the existing unit-0001 part. The [native review](native-review.json) records zero
contact with C14, RJ11, all six bulkheads and their nuts. It also records
the cap profiles, roof stock, meter loading clearance and rear tube routes.
These are CAD clearances. The installed wire review checks the current conductors against the receiver region. The accepted receiver-coupon fit retains its own scope, and
the [completed multicolor print](../display-cover/prints/2026-11-08-identification-set-mark1-right-z005/physical-result.json)
has accepted appearance and visual nozzle registration. The
[CO2 fit result](prints/2026-11-09-co2-width-mark1/physical-result.json) records
Derek's approved clearance, applied at each side of every tile by
`SIDE_CLEARANCE` in the generator. The bores, lettering, height and thickness
retain their accepted geometry. The [geometry review](rail-clearance-review.json)
records the edge cuts in the printable solids and installed viewer payload.
