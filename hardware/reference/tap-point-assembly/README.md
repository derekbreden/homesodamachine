# Tap-point assembly

The Basics MTB-0606WP barb tee with the two adapters that fasten onto its branch:
the run takes 3/8" hose end to end, the branch necks down through the PP451223W +
PP061208W to a 1/4" regulator feed for V-A.

```
3/8" hose → [MTB-0606WP] → 3/8" hose → SeaFlo suction
                 └ branch ↑ PP451223W → PP061208W → 1/4" LLDPE → regulator → V-A
```

The flavor manifold's clean-water tap is the 1/4" **water-split**
([`../water-split/`](../water-split/)), a JG PP0208E union tee on the ASSE 1022's
1/4" outlet. This directory is a geometry reference for the MTB-0606WP barb-tee
build.

| part | role | model |
|---|---|---|
| Basics MTB-0606WP | 3/8" barb × 3/8" barb × 3/8" MNPT branch — clamped inline in the silicone hose | [`../basics-mtb-0606wp/`](../basics-mtb-0606wp/) |
| John Guest PP451223W | 3/8" NPTF F × 3/8" PTC — threads onto the branch | [`../jg-pp451223w/`](../jg-pp451223w/) |
| John Guest PP061208W | 3/8" stem × 1/4" PTC — plugs into the adapter, necks to the 1/4" run | [`../jg-pp061208w/`](../jg-pp061208w/) |

## The branch is bench work

Made up, the adapter's 7/8" hex bottom face lands 2.92 mm above the tee's 11/16"
hex top face, and overhangs it by 2.35 mm a side. No second jaw reaches the tee
once the adapter is on it, so the joint is made up on the bench before the tee
goes into the hose line. The reducer above it has no flats at all and its stem
swivels in its socket — what the 1/4" collet points at is set by the tube, not by
the fittings.

Both barb crests are Ø10.92 into 9.53 mm ID hose: 1.4 mm of diametral
interference, which wants heat or lube and will not go on or come off by hand.
Each leg leaves 7.65 mm of smooth land between its last ridge and the body, so a
LOKMAN band straddles the last ridge rather than seating wholly on the land.

## Model

External envelopes only, composed. Each fitting's own module states how deep its
thread makes up or how far its stem is swallowed, and this file stacks those
reaches along the branch axis — change a length in any of them and the stack
closes on the new one. The joints share a surface and no volume; the assembly's
parts do not interfere.

| terminal | position | out |
|---|---|---|
| `hose_a()` | (−28.07, 0, 0) | −X |
| `hose_b()` | (28.07, 0, 0) | +X |
| `tube_out()` | (0, 0, 80.29) | +Z |

Overall 56.1 × 25.7 × 85.8 mm. The run bore is Ø6.22 — this tee necks the 3/8"
line to just under 1/4" ID on the main path, not only on the branch, and it sits
on the SeaFlo's suction side.

Frame: the tee's own — the run along **±X** with the barb tips at ±`RUN_LENGTH`/2,
the branch climbing **+Z**. The tee is symmetric about its branch, so either barb
leg takes either end of the hose.

## Sourcing

The tee's dimensions are the Thogus TT3666 drawing's, read off the PDF's vector
content stream at the sheet's 3:2 scale, `/PP` row. The John Guest fittings'
internals — tube stops, bores, insertion depths — are John Guest's own published
Cavity Dimensional Detail table; their threads are ASME B1.20.1. Their outer
profiles are the estimated part: the PP451223W's envelope is scaled from a
dimensioned drawing of the same JG family one thread size down, and the
PP061208W's is photogrammetry off John Guest's product photo, ±4% axial. Calipers
on a PP061208W would move the weakest numbers here — its overall length and body
Ø — onto measured footing.

## Regenerate

Builds its parts from their modules in-process, so only this one command:

```
tools/cad-venv/bin/python hardware/reference/tap-point-assembly/tap_point_assembly.py
```
