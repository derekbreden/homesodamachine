# Dispense Flavor Tube — Bent 1/4" 316 SS

Visual-companion tube. Two of these pass through 1/4" holes in the
mounting plate of the installed Westbrass A2031-NL-62 8" Touch-Flo
(factory faucet untouched) and arc up over to terminate near the
factory spout tip — one per flavor line.

**Approximate geometry, Xometry rough-quoting only.** Geometry was
hand-eyeballed by the user against the installed faucet on 2026-04-24:

| Segment | Value |
|---|---|
| Bottom straight (40 mm below deck + 65 mm above) | 105 mm |
| Bend 1 | 30° at R 31.75 mm (1.25") *(snapped from 40 mm guess)* |
| Mid straight | 100 mm |
| Bend 2 | 90° at R 31.75 mm (1.25") *(snapped from 40 mm guess)* |
| Tip straight | 15 mm |

Resulting envelope: ~4.5" forward × ~8.9" tall, centerline ~11.3",
mass ~45 g per tube (316 SS, 0.049" wall).

**Xometry quoter constraints (learned 2026-04-25):** CLR/OD ratio must
be 2:1–5:1; CLR must be a 0.25" increment; on 1/4" OD, only 0.049"
and thicker walls are actually stocked despite the capabilities page
listing 0.035" as the minimum.

## Xometry quotes (2026-04-25)

Submitted as: **316 SS**, 1/4" OD × 0.049" wall, MIL Flat Black powder
coat, matte sheen, bag-and-tag poly-bag finish-side packaging.

| Qty | Total | $/part |
|---:|---:|---:|
| 6 | $819 | $137 |
| 20 | $1,422 | $71 |
| 100 | $2,937 | $29 |

Per-part cost crashes hard between 6 and 100 — the bender setup amortizes
across the run. At 100 units the all-in landed cost per machine for two
tubes is ~$58, vs ~$274 at the 6-tube hand-build batch.

**Xometry submission spec for re-quotes:** 316 SS, 0.049" wall, MIL Flat
Black powder coat, matte sheen, bag-and-tag poly. Quantity = 2 per
finished machine. See `hardware/harvested/touch-flo-faucet/xometry-submission-notes.md`
for the broader quote-form checklist (including the grit-blast
pre-treatment note for 304/316 SS powder adhesion).

Regenerate: `tools/cad-venv/bin/python generate_step_cadquery.py`
