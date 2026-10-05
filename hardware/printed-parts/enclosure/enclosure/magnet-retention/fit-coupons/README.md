# RC62 pocket press-fit samples

Seventeen small, open PET-GF samples compare X diameter grip and Y thickness
grip independently. The ring stands upright with its axis along Y, enters
downward along Z, and prints in the cartridge's +Z orientation. There is no
roof, insertion pause, center post or printing support.

The customer outcome is a ring that can be pressed in by hand and stays still
during cartridge handling and initial overprinting. The [cartridge physical
report](../v4/physical-result.json) records a sealed ring that rattles and a
wonky first layer above it. Loose X/Y grip is the reported hypothesis. These
samples select a candidate grip; they do not qualify roof deposition or the
finished assembly's magnetic retention force.

Each sample has 3 mm sidewalls, backing and pocket floor, plus the production
1.2 mm mating-face cover. The D-shaped lower seat continues into a full-width
vertical mouth. The 20.12 mm open rim leaves about 1.93 mm of the nominal ring
exposed for finger removal. Its free upper rim makes this a comparative fit
screen rather than a copy of fully encapsulated stiffness.

Letters select the X pocket width; numbers select the Y pocket depth. All
dimensions are millimetres. The dimensions describe CAD openings, not a claim
about finished printed tolerances.

| Label letter | A | B | C | D |
| --- | ---: | ---: | ---: | ---: |
| X pocket width | 19.35 | 19.15 | 19.05 | 18.95 |

| Label number | 1 | 2 | 3 | 4 |
| --- | ---: | ---: | ---: | ---: |
| Y pocket depth | 3.45 | 3.30 | 3.175 | 3.05 |

For example, **B2** is 19.15 mm wide and 3.30 mm deep. **C0** is the current
cartridge-clearance control: 19.45 mm wide and 3.575 mm deep. The
[K&J RC62 specification](https://www.kjmagnetics.com/rc62-neodymium-ring-magnet)
is 19.05 mm OD, 3.175 mm thick and ±0.1 mm dimensional tolerance. Some samples
intentionally have nominal interference.

After the samples cool, use the same labeled RC62 for each comparison:

1. Try C0 first for the existing loose-fit reference. Keep the ring upright and
   press it straight down into the lower seat.
2. Compare A1 through D4. Use fingers only; stop when a sample needs forcing.
   A useful fit takes deliberate hand pressure, seats upright, and holds the
   ring without visible rocking or an audible rattle during a gentle shake.
3. Grip the exposed ring and pull it straight out. Repeat the favored sample
   once to check that the fit is repeatable rather than a one-time edge catch.
4. Report the preferred label, any equally good neighbor, and whether either
   direction still feels loose. No caliper or force-gauge measurement is needed
   for choosing this trial's preferred hand fit.

The [Aero float observation](../../../../cold-core/magnetic-float/all-aero/physical-observations.json)
supplies the desired push-in feel. Its foam material, horizontal ring, center
collar and XY compensation differ, so its dimensions do not establish this
PET-GF upright-pocket fit.

The [centered trial](centered-trial-v4/launch-plan.json) divides the samples
between two plates, with C0 and valve V70 repeated on each:

| Printer | RC62 samples | Four-post valve panels | Native estimate |
| --- | --- | --- | --- |
| Mark2 | A1–A4, B1–B4, C0 | V72, V71, V70 | 1 h 39 m 20 s / 51.46 g |
| H2C | C1–C4, D1–D4, C0 | V70, V69, V68 | 1 h 38 m 32 s / 51.19 g |

Each plate contains twelve fit samples, with at least 86.7 mm of full-bead
clearance from the bed edges. No full enclosure or funnel-frame is included.
The samples use production PET-GF flow and XY compensation, two walls, 15%
infill, a 0.20 mm first layer and 0.24 mm normal layers. Both use the fixed
left hardened standard-flow 0.4 mm nozzle, Textured PEI and black PET-GF
external left spool labeled PET-CF/GFT01. Mark2 uses +0.04 mm user trim
(+0.02 mm emitted); H2C uses +0.18 mm (+0.16 mm emitted).

[Geometry and sample hashes](geometry.json), the
[Mark2 native and independent reviews](centered-trial-v4/mark2/README.md),
the [H2C reviews](centered-trial-v4/h2c/README.md) and the
[two-plate comparison](centered-trial-v4/independent-plate-pair-review.json)
bind the sample dimensions, labels, ordinary layers and emitted paths.
Current accepted task identities and one Send per plate are in the
[launch plan](centered-trial-v4/launch-plan.json). Physical preferred fit and
visual first-layer adhesion are pending. The
[edge-adhesion report](../../support-bottom-gap/mark2-v2/physical-result.json)
is the physical evidence for restricting these plates to the bed centers.
