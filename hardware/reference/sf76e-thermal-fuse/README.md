# BOJACK SF76E SEFUSE thermal cutoff — reference solid

The hardware-only backstop on the compressor's AC hot leg (`hardware/ledger/bom.md`
§5): a one-shot axial thermal cutoff that opens for good at **77 °C** and is never
read, never switched and never reset. Safety rationale in
[`assembly/refrigerant-loop.md`](/hardware/assembly/refrigerant-loop.md) "Safety".

`sf76e-thermal-fuse.step` is a generated stand-in. Geometry is the SEFUSE
**SF/E series** outline (NEC/SCHOTT), the series the SF76E is a temperature
variant of; the rating figures are that series' own standard-rating table.

## Geometry

| | mm |
|---|---|
| Case (Ø × L) | **4.2 ± 0.2 × 11 ± 0.5** |
| Lead wire | **Ø1.0 ± 0.1** |
| Leads, as supplied | 20 and 35, **66 end to end** |
| Modeled envelope | **17 × 4.2 × 4.2** |

The case is a plain cylinder here. The real one tapers into each lead, so this is
the loose envelope rather than the silhouette.

**Only 3 mm of each lead is drawn.** The datasheet forbids bending a lead closer
than 3 mm to the body, so that stub is the length whose pose the part fixes; past it
the lead is wire and goes where the loom goes.
[`../ground-ring-stack/`](../ground-ring-stack/) draws its tongues and omits the
cable the same way.

## Rating

| | |
|---|---|
| T_F, rated functioning temperature | **77 °C** — opens here, permanently |
| T_H, holding temperature | 62 °C — indefinitely safe below |
| T_M, maximum temperature limit | 150 °C |
| Rated current / voltage | 10 A / 250 V AC |

## Frame

X is the fuse's own axis, origin at the case's mid-length. **Z = 0 is the seating
plane** — the generatrix the case lies on — so whatever straps it down reads its own
surface as this plane. The axis runs one case radius up and both leads run on the
axis, which leaves a lead 1.6 mm clear of the seat: **the case is the whole of the
thermal contact.**

## Where it stands

Lying along the compressor's power box — the outboard face of the donor's moulded
cover over the terminal block and the PTC start relay, which
[`compressor.power_face()`](../compressor/compressor.py) states and
`enclosure_assembly.build_thermal_fuse` seats it on. Nothing on the compressor
reaches past that face, so the case lies against the part on one side and stands in
the open on the other five.

**Nothing holds it there yet.** The fuse is spliced into the hot leg and its case is
laid on the face; what clamps it into thermal contact is not designed, and the
`held` / `mounted` axes on the enclosure scorecard carry that as an open joint.

## Regenerate

```
tools/cad-venv/bin/python hardware/reference/sf76e-thermal-fuse/sf76e_thermal_fuse.py
```
