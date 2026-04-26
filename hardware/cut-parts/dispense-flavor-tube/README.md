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

## Open problem — single-CLR constraint vs. real Touch-Flo asymmetric radii

A photo-measurement pass against a Westbrass D2031 spec image and a
clean side-view product photo (2026-04-25) showed the real Touch-Flo
gooseneck has **two different bend radii** — bend 1 ≈ 12 mm CLR,
bend 2 ≈ 48 mm CLR. Xometry's tube-bending DFM page recommends a
single CLR per part "for ease of manufacturability" — multi-CLR parts
need either multi-stack tooling or an additional setup, which the
quoter charges for (or refuses entirely).

The current STEP uses **one** CLR (1.25" / 31.75 mm) for both bends,
which is the largest legal value Xometry will accept for 1/4" OD
(5:1 ratio cap). That oversells bend 1 (off by ~2.6×) and undersells
bend 2 (off by ~1.5×). The silhouette drifts from the real faucet
visibly, especially at the upper transition.

**Status:** documented, not solved. Two paths forward if the silhouette
mismatch turns out to matter:
- Try a tube-bending shop that supports multiple CLRs per part natively
  (most niche tube benders do; instant-quote services tend not to). This
  generally means custom-quote workflows and longer lead times.
- Accept the single-CLR approximation and adjust adjacent geometry
  (mid-straight length, sweep angles) to recover apparent silhouette
  fidelity even with a single CLR.

**Tube-bending alternatives surveyed (2026-04-25):**
- **OSH Cut** — instant-quote tube bending in-browser, similar UX to
  SendCutSend. Supports steel and 304 SS only (no 316 listed in their
  tube stock); OD range 0.75"–1.5" is also above our 0.25". Not viable
  for this part as currently spec'd.
- **Niche tube-bending shops** (Tube-Tec, Triad Products, Noble
  Industries, Woolf Aircraft) — handle multi-CLR parts routinely but
  use email/RFQ workflows, not instant quoting.

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
