# Touch-Flo shell — material choice

Rationale for printing the touch-flo-shell in PET-CF rather than any of
the easier-to-print alternatives.

## What this part is and does

The shell is a printed shroud that wraps the harvested Westbrass
Touch-Flo valve body, the carbonated-water tube, and the two flavor
tubes. The harvested body is what carries the dispense pressure and the
factory shank-nut clamp into the countertop; the shell is a precision
shroud over that body, not a pressure vessel. See [`ASSEMBLY.md`](ASSEMBLY.md)
for the joint geometry and [`generate_step_cadquery.py`](generate_step_cadquery.py)
for the per-zone construction.

Service loads on the shell are limited to:

- The lever-actuation reaction (small, transient, per dispense).
- Occasional user grab / lean on the faucet.
- Sustained M3 heat-set insert loads at the plate-to-shell joint
  (two ruthex inserts, see ASSEMBLY.md Step 1).
- Kitchen-environment exposure: ambient humidity, splash, occasional
  cleaning chemicals, sponge contact.

The shell sees **no food contact** — water and soda travel inside LLDPE
tubes that pass through cutouts; the dispensed liquid never touches
shell material.

## Requirements

Derived from [`../../../future.md`](../../../future.md) (10-year design
lifetime, premium hand-built appliance) and
[`../../../../marketing/target-market.md`](../../../../marketing/target-market.md)
(Founder Edition at $7,500, visible-surface legitimacy):

1. **10-year service life in a kitchen environment.** Continuous
   ambient humidity, periodic splash and steam from the adjacent sink,
   periodic cleaning chemistry (citrus, ammonia, dilute bleach).
2. **Visible above-counter surface at premium price point.** The
   faucet is the only fixed above-counter user-facing element on
   the appliance. Target-market.md is explicit that legitimacy at
   $7,500 lives on visible surfaces. The shell must read as a
   serious-engineering object, not a hobby print.
3. **Precision body-bore fit.** The Ø 32.0 mm body bore is a slip fit
   to the harvested Westbrass body (Ø 31.5 mm + 0.25 mm clearance per
   side). Drift in that diameter from moisture absorption, creep, or
   thermal cycling degrades the fit over the service life.
4. **Heat-set insert retention, cold and hot.** Two M3 ruthex inserts
   pressed at 230 °C; service joint torqued by hand, no spec. Material
   must hold the inserts without crater formation at install and
   without pull-out at service torque. Over-torque is the documented
   failure mode (ASSEMBLY.md Step 3).
5. **Static loading only.** The shell is not impact-loaded — the
   faucet is fixed to a countertop and is not handled like a tool.
   Brittleness matters during print and handling, not in service.
6. **Cosmetic durability.** Surface must not yellow, chalk, or scratch
   visibly under typical kitchen wipe-down (sponge + dish soap; Bar
   Keepers Friend equivalent occasionally).
7. **Printable on the Bambu H2C in-house.** With a hardened nozzle and
   enclosed chamber the H2C can do this; calibration history is in
   [`print-log.md`](print-log.md). Material must remain practical
   within that printer envelope.
8. **No food-contact requirement.** The wet path is fully internal to
   LLDPE; this relaxes the material space significantly.

## Material evaluation

| Material              | Verdict           | Reasoning |
| --------------------- | ----------------- | --------- |
| PLA / PLA-CF          | Disqualified      | Cold-creeps under sustained insert load over a decade. Tg ~60 °C is below dishwasher-steam range. |
| PETG / PETG-CF        | Possible, downgraded | Easier to print, similar matte-CF aesthetic for the CF variant, but creep over 10 years is materially worse than PET-CF at the heat-set joint, and Tg is lower. Acceptable for a one-shot print; concedes ground that doesn't need conceding on a $7,500 / 10-year part. |
| PA-CF / PAHT-CF (nylon-based) | **Disqualified — decisive elimination** | PA6/PA12-based composites absorb 3–9% water at saturation vs PET-CF's 0.37%. In continuous kitchen humidity the shell would slowly grow, soften, and drift the precision body-bore fit out of spec. The exact failure mode the application can least tolerate. |
| ASA / ABS             | Disqualified      | Stiffness and creep behavior insufficient for the insert joint over a decade. Matte aesthetic reads as hobby print, not premium visible surface. (UV stability is moot — kitchen.) |
| PC-CF                 | Overkill, no benefit | Higher HDT and toughness than PET-CF, but the thermal and impact envelopes are not binding here. More expensive, harder to print, no compensating advantage for this application. |
| PPS-CF                | Overkill, no benefit | Even better chemical resistance and HDT than PET-CF; no requirement here pushes those envelopes. ~2–3× cost, substantially harder to print. |
| PEEK / Ultem          | Not actionable    | Outside the H2C envelope. |
| CNC-machined aluminum | Not actionable    | Would be aesthetically peak-premium but is killed by geometry: the gooseneck spout, the irregular harvested-body bore, the lever-clearance ramp, the multi-piece slip-fit splits are all engineered for printing. |
| **PET-CF**            | **Selected**      | Hits every requirement: low moisture absorption (the only common engineering-CF filament that does), high stiffness and modulus (lever feel + insert retention), very low creep (10-year design life), low CTE (body bore stays in spec across thermal cycles), premium matte-CF aesthetic on a visible surface, chemically inert to typical kitchen cleaners, holds heat-set inserts. |

## Decisive factors

The combination that selects PET-CF over the nearest contenders is:

- **Low moisture absorption** disqualifies the entire PA-CF family,
  which would otherwise be the natural "premium engineering composite"
  default. PET-CF's ~0.37% saturated water absorption is what makes it
  fit-for-kitchen.
- **Low long-term creep** disqualifies PETG-CF for a 10-year heat-set
  joint, even though PETG-CF prints more easily and looks similar.

Either factor alone could be argued around. Together they leave PET-CF
as the natural fit. The matte CF surface finish, premium on the visible
above-counter surface, is a free bonus that the alternatives also share.

## Brand vs material class

The rationale above is **material-class rationale, not brand
rationale**. Any true PET-CF that hits the published spec envelope —
low moisture absorption, ~15–17% CF, ISO-disclosed mechanicals —
satisfies these requirements.

Currently sourced as Bambu PET-CF (default for the in-house H2C +
matching print profile, see [`print-log.md`](print-log.md) for the
calibration history that got attempt 7 printing cleanly). The closest
Prime-available alternative for evaluation is **Polymaker Fiberon
PET-CF17**: true PET + 17% CF, full ISO data sheet, Polymaker is a
~14-year-established filament manufacturer with global presence and
published Bambu X1C profiles. The faucet shell is the easiest part in
the build to substitute for a print-print comparison, since none of
the application's binding requirements distinguish between Bambu and
Polymaker at this material class.
