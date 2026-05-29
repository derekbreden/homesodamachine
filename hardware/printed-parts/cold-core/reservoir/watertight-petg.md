# Printing the reservoir watertight in PETG

Standing, filament-agnostic guidance for printing the reservoir body + cap leak-free in PETG. This is generic PETG technique applied to this part's geometry. Per-attempt records live in [`print-log.md`](print-log.md).

## The part, for sealing purposes

- Open-top `[` cup: floor + four walls, 3 mm uniform PETG, closed by a separately-printed cap clamped through a TPU gasket (6× M3 into heat-set inserts).
- **Vented, non-pressurized.** A PTFE membrane in the cap equalizes the air space, so the only load on the wall is the hydrostatic head of syrup — a tall but low-pressure column (~210 mm ≈ **~0.3 psi** at the floor).
- Floor is a Y-symmetric V trough with a vertical bulkhead penetration; a TPU face washer in a wet-side counterbore seals the barrel-to-floor joint, locknut from below.
- 6 mm fillets at the internal corners.
- Cold service (8–15 °C). Food contact (mildly acidic concentrate). The wetted surface is the bare print — its food-contact + taint acceptance is [`wetted-surface-test.md`](wetted-surface-test.md) (leak-tightness, below, is a separate gate).

The consequence of *vented + low head*: **a leak here is a defect, not a strength failure.** The wall trivially survives 0.3 psi. What weeps is a continuous capillary path — between adjacent perimeter beads, up the Z-seam, or through the floor / first layer. Every lever below closes one of those paths. PETG itself is a good choice for this (water-resistant, strong layer adhesion); watertightness is a *process* property, not a material guarantee.

## Levers, highest-leverage first

### 1. Divide the wall into a whole number of lines
A 3 mm wall must be an integer multiple of the chosen line width, or the slicer inserts a thin, starved gap-fill bead down the middle of the wall — a built-in vertical capillary the full height of the part. Clean fits:

- 0.8 mm nozzle: **4 × 0.75 mm = 3.00 mm**
- 0.6 mm nozzle: **5 × 0.60 mm = 3.00 mm**

Use the **Arachne** wall generator (varies bead width to fill the wall exactly, no gap line — important at the fillets and the tapering V-floor). Define the wall by thickness + line width, not by a high perimeter count: past ~4 *fused* perimeters, more loops add print time, not tightness.

### 2. Get squish from line width, not flow ratio
Closing the inter-bead valley needs adjacent beads to over-squish and merge. Get that from **line width ~110–120 % of nozzle** plus **wall/infill overlap ~30–40 %**, which re-spaces the toolpaths so they are *planned* to overlap — clean, no surface bulge. Raising the global flow ratio achieves the same physically but bulges the surface; reserve it as a small inner-wall trim only (+0–2 %) and keep the outer wall at its clean value.

### 3. Temperature and melt-rate, together
Bead-to-bead and layer-to-layer welding is polymer diffusion across a hot interface — it needs both heat and dwell:

- Nozzle **~250–255 °C** for the wall. PETG layer adhesion peaks around 245–250 and falls off past ~260 — hotter is not always better.
- Slow the **walls to ~30–40 mm/s** and let max-volumetric-speed fall out of that. A large nozzle pushed fast under-melts: the bead lands before it can fuse.
- A **glossy** wall is fused; a **matte / grainy** wall is under-melted and will weep. Use sheen as a free, per-print fusion gauge.
- PETG brands/grades differ — dial flow and temperature per spool rather than carrying a profile across filaments.

### 4. Layer height and the floor (the real risk on a low-head part)
- Lower layer height re-presses each prior layer; for the wetted regions favor **≤ ~40 % of nozzle diameter**.
- The floor and first layer are the most common leak site. Set the solid bottom shell by **thickness (≥ ~1.5–2 mm)**, not a fixed layer count, so it stays robust if layer height changes. **Iron** the interior V-floor (it prints as a top surface). Use a **monotonic** bottom pattern (concentric spirals converge to a center void). Strong first-layer squish; a wide, slow first layer.

### 5. Cooling
PETG welds better warm. Part fan **~20–30 %**, **auxiliary fan OFF**; keep the enclosure closed for passive warmth but do not actively heat the chamber on a tall thin-wall part. This geometry is overhang-free, so a low fan costs essentially nothing in quality.

### 6. The Z-seam
On a walled (non-vase) part the seam is a top leak path: every perimeter loop starts and stops at one point, and those voids stack into a vertical channel. Vase mode is not available here (the part has a cap and a floor penetration), so engineer the seam out:

- **Staggered inner seams ON** — de-stacks the per-loop seams across the wall thickness.
- **Seam gap → 0** — fills the closure notch locally instead of via a global flow bump.
- **Scarf joint** seam — ramps the start/stop so there is no butt-joint column. Verify in slice preview that it actually deposits on the *inner* wall; if it misbehaves on the concave inner loop, fall back to **Random** (the part is hidden, so speckle is a non-issue).
- Wall order **inner / outer / inner**, so the wet outer-adjacent bead lands on solid backing.
- Calibrate **pressure advance** (flow dynamics) so the loop closure neither oozes nor starves at the seam restart.

### 7. Dry the filament — verify by weight, not the dryer's RH
Wet PETG flashes to steam in the melt and leaves micro-voids that become leak paths. A dryer's chamber-RH readout is the *air*, which equilibrates in minutes; the 1.75 mm core diffuses out over hours. **Weigh the spool, dry, reweigh hourly until the weight stops dropping.** For a long, tall print, feed from the heated dry-box so the upper wall does not print from re-wetted filament.

### 8. Geometry that helps the seal
- The 6 mm internal fillets are correct — keep them, and ensure the floor-to-wall transition is filleted too, not just the vertical corners.
- A flat-walled box is the weakest watertight form: walls bow under head, opening the layer interface in tension. 3 mm is a sensible wall; the cheapest added robustness is reinforcing the lower third (an external rib or a thicker low wall), since head is highest at the bottom.
- **Penetrations and sealing faces:** seal on a flat, ironed, upward-facing top surface, never on a layer-line wall. Keep heat-set inserts and bolt bores ≥ ~2 mm of solid PETG away from the wetted volume. Let the TPU washer / gasket do the sealing (face seal at a controlled squeeze) — do not rely on printed-plastic tightness against the bulkhead barrel.

## Leak test (so each iteration gets a real pass/fail)

Service load is only ~0.3 psi, so test well above it but never near a pressure-vessel regime:

- **Air-bubble test (primary — it localizes the leak):** cap the mouth, plumb a barb + 0–15 psi gauge + bleed valve, submerge in clear water, step to **1 psi then 3 psi** (~9× service), 60 s each. A continuous bubble stream is a fail; the bubble column marks the exact leak path. **Never exceed ~5 psi** — this is not a pressure vessel.
- **Assembled confirmation:** dyed water column at **2–3× head** (a clear tube taped to the mouth), held **cold (8–15 °C) for 24 h**, exterior pre- and post-weighed on a 0.01 g scale. Pass = no dye bleed anywhere and < ~0.1 g/24 h mass gain.

## If the bare print cannot seal: the food-safe coating fallback

Bare-print watertight at 0.3 psi is well within reach — slicer settings alone have matched epoxy-coated parts at multi-bar pressures — so treat coating as a true last resort. If used, it must be a named **direct**-food-contact, acid-tolerant epoxy, fully cured plus a forced post-cure, flood-coated (not brushed), over scuffed + IPA-degreased plastic (IPA does not attack PETG). The standing risk is that epoxy adhesion to cold, slightly-flexing PETG is poor. Do **not** use XTC-3D or solvent (acetone) smoothing on the wetted surface — neither is food-safe on PETG.

## References

- Prusa — Watertight 3D printing, Part 1 (open models): https://blog.prusa3d.com/watertight-3d-printing-pt1-vases-cups-and-other-open-models_48949/
- Prusa — Watertight 3D printing, Part 2 (airtight *closable* models — closest analog to a capped reservoir): https://blog.prusa3d.com/watertight-3d-printing-part-2_53638/
- Prusa Knowledge Base — Watertight prints: https://help.prusa3d.com/article/watertight-prints_112324
- Gordeev et al., *PLOS One* 2018 — FDM porosity vs extrusion multiplier; the quantitative basis for "squish to seal": https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0198370
- Brick Layers (CNC Kitchen) — staggered perimeters + internal-perimeter flow for watertightness: https://www.cnckitchen.com/blog/brick-layers-make-3d-prints-stronger
