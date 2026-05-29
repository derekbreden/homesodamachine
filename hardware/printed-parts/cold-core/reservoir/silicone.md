# Casting the reservoir in food-grade silicone

Standing guidance for making the reservoir as a cast food-grade silicone vessel: an FDM-printed two-part mold, platinum-cure silicone cast in the gap, the cured rubber as the wetted part. Generic silicone-casting technique applied to this part's geometry and its food-contact + 10-year requirements. Companion to [`watertight-petg.md`](watertight-petg.md) (the printed-PETG path) and [`floor-and-bulkhead.md`](floor-and-bulkhead.md) (floor + bulkhead geometry).

## The part, for casting purposes

- Open-top `[` cup: floor + four walls, ~2–4 mm wall, closed by a separate cap through a TPU gasket; vertical bulkhead through the V-floor trough.
- **Vented, non-pressurized** — the only wall load is ~210 mm of syrup head, ≈ **0.3 psi**. The rubber trivially holds that; the failure mode is a **through-wall void or pinhole** left by trapped air during the cast, i.e. a leak, not a strength failure.
- Silicone is **flexible**, so the foam-shell pocket carries the vessel's shape — it is not self-standing the way the rigid print is. The cap and the bulkhead are separate rigid parts.
- Cold service (8–15 °C), food contact, mildly acidic concentrate. The wetted surface is the cured silicone.

Two things make this geometry hard to cast: the wall is **thin and tall** (a deep narrow gap is the worst case for trapped air and complete fill), and the wetted volume must come out **void-free** because any pinhole is a leak.

## The silicone — use platinum-cure (addition), food-contact rated

Platinum/addition-cure, not tin/condensation-cure (tin shrinks and ages worse). The real scarcity is **certification**: only a couple of Prime listings carry a regulatory-backed food-contact claim; the rest say "food safe" or "non-toxic" with no CFR citation — the same weak-claim category to be wary of.

| Product | ASIN | Price | $/kg | Shore A | Mix | Food-contact claim |
|---|---|---|---|---|---|---|
| **Smooth-SIL 940** (gallon, ~4.5 kg) | [B00EOA25X2](https://www.amazon.com/dp/B00EOA25X2) | $170.09 | ~$38 | 40A | 10:1 by weight (needs a scale) | **TDS-backed food grade** (Smooth-On bulletin) — strongest |
| Smooth-SIL 940 (1 kg trial) | [B00EOA25X2](https://www.amazon.com/dp/B00EOA25X2) | $52.99 | ~$53 | 40A | 10:1 | same |
| Cast-A-Mold Platinum (1 gal) | [B06XBRGGZ3](https://www.amazon.com/dp/B06XBRGGZ3) | $164.99 | ~$40 | ~25A | 1:1 | "FDA-compliant" (moderate, no CFR cited) |
| Siraya Tech Defiant 25 (2 kg) | [B0F99BHP2N](https://www.amazon.com/dp/B0F99BHP2N) | $40.47 | ~$20 | 25A | 1:1, thin, self-degassing | "food safe" (stated, no CFR) |
| SHORE RESIN 15A (2 gal, ~8 kg) | [B0DT99Y8SH](https://www.amazon.com/dp/B0DT99Y8SH) | $105.99 | ~$13 | 15A | 1:1 | "food safe once cured" (weak) |
| Nicpro 20A (80 oz, ~2.3 kg) | [B08GHGM721](https://www.amazon.com/dp/B08GHGM721) | $34.99 | ~$15 | 20A | 1:1 | "non-toxic / food contact" (weakest) |

For a wetted vessel, **Smooth-SIL 940** is the credible choice (Shore 40A is firm enough to hold form, and its food-grade claim is TDS-backed). Its 10:1-by-weight ratio needs a 0.1 g scale; the 1:1 grades pour easier but carry weaker claims.

**How much, per reservoir:** silicone forms only the walls. Wetted area ≈ 810 cm² (≈ 75 cm² floor + ≈ 750 cm² walls). At a 3 mm wall that is ≈ 245 cm³ ≈ **~280 g per reservoir** (2 mm ≈ 190 g, 4 mm ≈ 375 g; density ~1.1–1.16 g/cm³).

**Cost, per reservoir (Smooth-SIL 940 @ ~$38/kg):** ~$11 of rubber at 3 mm, **~$15 with casting waste**; **~$30/build** (two reservoirs). A **$170 gallon ≈ 5–8 builds.** The weak-claim grades run ~$4–7/reservoir.

## The mold (FDM)

- **Two-part: outer cavity + inner core**, the gap between them is the wall. Assembled mold ≈ **260 mm tall** with a ~160 × 70 mm footprint — this height drives the void-control rig sizing below.
- **Demolding a thin flexible wall off a core** is the constraint: put **draft** on the core, use a **release agent**, and lean on the rubber's flexibility to peel; a **split cavity** helps lift the part free of the centerward concave wall and corner fillets without tearing.
- **Air escape:** fill from the **low point (the trough)** so air is pushed up and out; add **vents / risers** at the trough ends, the corner fillets, and the bulkhead boss — the spots where air otherwise stalls in a thin gap.
- **Bulkhead port:** either cast around a placed insert at the trough, or cast the trough solid-ish and pierce + mount the PureSec after (it is a through-wall panel-mount fitting — see [`floor-and-bulkhead.md`](floor-and-bulkhead.md)).
- An FDM mold under pressure-cast loads wants robust walls (or a rigid backing shell) so it does not flex or leak at ~50 psi.

## Void control (the crux)

A thin, tall gap traps air, and trapped air in the wetted wall is a leak. Two stages:

1. **Degas the mixed silicone** before pouring — pull entrained air out in a vacuum chamber. The mix froths ~3–4× then collapses; pull until it stops rising. Self-degassing low-viscosity grades (Siraya Defiant) reduce but do not remove this need.
2. **Clear gap-trapped air in the filled mold** — either vacuum the filled mold or **pressure-cast** it. Pressure casting (pour, seal, cure under ~40–60 psi) crushes any remaining bubbles small and holds them there through cure; it is generally the more reliable route for a thin-wall part.

The rig has to **fit the ~260 mm (≈10.2") mold**, which rules out the common 2-gallon/2.5-gallon units. A **5-gallon** chamber or pot (≈11.8–14" interior) clears it.

**Vacuum chamber (degas; fits the mold at 5 gal, ≈11.8" interior):**
- Chamber only: [PB Motor Tech 5-gal, $89.59](https://www.amazon.com/dp/B0D78ZM928).
- Chamber + 4.5 CFM pump: [$126.99](https://www.amazon.com/dp/B0FQV9R4GQ) (pump oil not included, ~$12 extra).
- Glass-lid chamber + pump, well-reviewed: [BACOENG, $229.99](https://www.amazon.com/dp/B07X5TVPTB).

**Pressure pot (pressure-cast; fits at 5 gal — a 2.5-gal's ~10" interior does *not* clear a 10.2" mold):**
- [TCP Global 5-gal, $289.99](https://www.amazon.com/dp/B08G5BTH74) — 13" interior, regulator included, **50 psi max** (fine at the 40–45 psi people cast at).
- California Air Tools CAT-365C 5-gal, 80 psi, [$310](https://www.amazon.com/dp/B017BXZ8B4) — fits, but it is a third-party listing without a confirmed Prime delivery; verify at checkout.
- Does **not** fit: [CAT 255C 2.5-gal, $187.59](https://www.amazon.com/dp/B09T3YTG5Q) — 10" interior, shorter than the mold.

The shop air compressor (the pressure-test pancake) already covers the pressure route, so that path is just the pot.

## Process

1. Print the two-part mold; apply release agent.
2. Mix to ratio (0.1 g scale for Smooth-SIL 940's 10:1; the 1:1 grades by eye/scale).
3. Degas the mix in the chamber until it stops frothing.
4. Pour into the mold from the trough/low point — or seal and pressure-cast at ~45 psi.
5. Cure ~24 h at room temp (heat accelerates; check the grade's bulletin).
6. Demold, trim the rim, install the bulkhead + TPU washer, fit the cap.

## Leak / qualification

The failure mode is a **through-wall void or pinhole**, not strength, so test for path, not pressure (same as the printed part):

- **Air-bubble submerge test:** cap the mouth, plumb a barb + 0–15 psi gauge + bleed, submerge in clear water, step to **1 then 3 psi** (~9× service), 60 s each; a bubble stream is a fail and the bubble column marks the pinhole. **Never exceed ~5 psi.**
- **Cold dyed-column soak:** dyed water at 2–3× head, 24 h at 8–15 °C, pre/post weigh; pass = no dye bleed, < ~0.1 g/24 h gain.
- **Permeation/aroma soak (specific to silicone):** because silicone is gas-permeable, a long cold soak with the actual concentrate, checking for flavor migration through the wall and mass change, is this material's added qualification.

## Open questions

- **Flexibility** — the foam-shell pocket must fully support the vessel; it does not stand on its own.
- **Aroma / gas permeability** — flavor migration through the wall over a 10-year flavor reservoir is unquantified.
- **Cert duty** — even Smooth-SIL 940's food-grade rating is for *molds that contact food* (intermittent), not continuous 10-year acidic immersion. Silicone is chemically inert to dilute acid, so the chemistry is favorable; the regulatory paperwork for *this* duty is the gap.
- **Thin-wall fill** — whether a 2–3 mm wall fills void-free down a 200 mm gap, with venting + degas alone or only under pressure, is the make-or-break process question.
- **Demold** — releasing a thin flexible wall off the core without tearing, given the concave centerward wall and corner fillets.

## References

- Smooth-On Smooth-SIL 940 — product page + food-grade Technical Bulletin: https://www.smooth-on.com/products/smooth-sil-940/
- FDA 21 CFR 177.2600 — rubber articles intended for repeated use in food contact (the regulation a credibly food-grade silicone is tested against).
- Smooth-On — "Vacuum Degassing vs. Pressure Casting" technique overview: https://www.smooth-on.com/support/
