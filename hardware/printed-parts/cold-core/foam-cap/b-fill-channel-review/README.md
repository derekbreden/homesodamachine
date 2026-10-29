# B-fill channel and three-point lid clamp

The cap's front-facing guide turns one continuous 1/4-inch tube at R14 from
world (−43.5, 182.6, 247.55) to the existing reservoir seat at X−43.5/Y233.3.
Its short end reaches Z228.15. A plain rectangular block spans world
X−60.0…−27.0/Y182.6…248.3 through the complete cup-height footprint, with three recessed M3 × 10 screws
and full RX-M3×5.7 inserts fastening the lid above them.

The circular Ø6.8 mm channel has insertion lead-ins at both ends.
The supported channel crown has 0.25 mm of relief toward print-up (+Z).
The nominal axis and lower envelope stay fixed. The straight crown reaches
Z251.20 beneath the Z253.4 lid face, retaining 2.20 mm of roof stock.
The cup's channel opening has a 0.5 mm lead-in at its parting edge.
The accepted 0.5 mm mouth lead-in has 1.70 mm of roof above it. The normal
0.15 mm printed seating allowance remains at every clamped cup/lid face.

The fore screws occupy X−54.0/−33.0 at Y205.6. They straddle the straight
inlet, 23.0 mm aft of its face. The aft screw remains at
(−43.5, 242.3). The lift reference lies inside this screw triangle. This is
the specified load-support arrangement; the reference does not predict a
measured force or establish a load rating.

Each screw head seats 3.15 mm below the lid face. The Ø4 × 9 mm blind insert
pilots retain 5.30 mm of backing and 1.40 mm of nominal screw-tip air.
Fit the inserts in the open cup, and tighten all three local lid screws
before foaming, tube threading or PCB installation. Their driver approaches
cross the installed board; later access requires PCB removal.

The [manual native receipt](native-review.json) records the production-source
cup and lid, their source hashes, and the following local readings. It adds
no build or commit check.

| Interface | Native reading |
| --- | ---: |
| Cup and lid | Each valid, one solid |
| Cup/lid material overlap | 0 mm³ |
| Tube-channel obstruction in cup or lid | 0 mm³ |
| Reed-B passage obstruction in cup | 0 mm³ |
| Minimum insert envelope to Reed-B passage | 2.859 mm |
| Nominal seating gap at each clamp | 0.15 mm |
| Guide to original PCB and plug housings | 1.60 mm |
| Recessed screw to original PCB | 1.75 mm |
| Guide to Ø20 pour opening at X−73.0/Y212.6 | 3.000 mm |
| Minimum clamp-pilot to channel gap | 4.199 mm |
| Material missing at the closed upper opening | 0 mm³ |

These readings cover the stated source geometry. The combined assembly
export, print slice and physical fit have their own artifact scopes.

The [local Mark1 test](../prints/2026-10-28-b-fill-round-fore-20560/README.md)
contains the cup and matching lid cropped from the production pieces, with
the fore pair at Y205.60. Its receipt records the native archive and printer
task. The full lid's print preparation uses the current source STL.

The [post-publication surface reading](post-publication-review.json) records
the published STL review. The cup's 1.569 mm exposed flat meets the rounded
cable carrier; a normal ray at the diagnostic pick crosses 33.0 mm of
continuous block material. The lid has no unaddressed findings in the
step/bump/sliver review. The full cup's Reed-B passage has 0 mm³ obstruction.
