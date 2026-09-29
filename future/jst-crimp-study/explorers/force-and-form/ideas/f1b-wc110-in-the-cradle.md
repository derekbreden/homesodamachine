# f1b — Branch of f1: the same cradle around JST's WC-110

Explorer: force-and-form. Parent: [`f1-motorised-ratchet-crimper.md`](f1-motorised-ratchet-crimper.md)
(its sketch shows the cradle; the WC-110 takes the SN-2549's place).
Numbers: [`../calc/final_w3.out.txt`](../calc/final_w3.out.txt) §7 [calc final §n];
change-the-question's [`on_force_and_form.out.txt`](../../change-the-question/calc/on_force_and_form.out.txt)
[change-the-question calc off §n]. **[Prime]** is a row of
[`../../../sourcing/amazon-prime.md`](../../../sourcing/amazon-prime.md).

## Picture it

This is f1 with a different tool in the cradle: **JST WC-110**, JST's own
ratchet hand tool for loose-piece SXH-001T-P0.6 (BXH-001T-P0.6). The printed
cradle, the actuator with its load cell, the X/Z ribbon carriage, the camera and
the fork are f1's.

- **The tool.** A 22 AWG cavity, a steel **flap locator** that positions the
  contact, and an insulation stop blade [mfr S6, S7; WC-110 manual via
  hand-tool-as-press].
- **The contact** goes onto JST's flap locator: clicked out, contact inserted
  to its stop, flap closed. A magazine or a strip shear feeds the flap in its
  clicked-out position, as in f1.
- **Hold.** The actuator closes lightly until the contact is held, short of
  pinching the insulation wings (f1's hold).
- **Threading.** The carriage lowers the conductor until the tool's stop blade
  halts the insulation. The stop shows as a force rise on the carriage's
  spring-mounted clamp, and it is accepted only inside a ±0.3 mm window around
  the depth the camera's bare-length measurement predicts. Outside that window
  the same rise means the insulation snagged at the barrel mouth.
- **Crimp.** The actuator completes the stroke; the curve is logged as in f1.
- **Proof pull** against a neck blade on the box's rear face, as in f1.
- **What locates what.** Fixed is the WC-110's fixed jaw; JST's flap locator
  places the contact; the stop blade and the camera-predicted window place the
  conductor. Crimp height is the tool's fixed die.
- **The person** does what f1 hands back: contact supply, ribbon loading,
  insertion.

## What it buys, taken apart

The WC-110 buys two separable things.

- **JST's locator.** f1's swinging keyed flap already supplies a locator. The
  WC-110's steel flap is JST's version of the same thing.
- **JST's die profile.** This is the part f1 cannot copy. It can be judged
  before the $536 is spent:
  - crimp five contacts on the ribbon with the SN-2549 and caliper height and
    width;
  - compare with a genuine JST factory crimp (ASXHSXH22K305, $0.90), corrected
    for copper area: H_ribbon ≈ H_ref − (A_ref − 0.302 mm²)/(W × 0.8–0.9), a
    correction of 0.02–0.07 mm at W = 1.5 mm [change-the-question calc off §6];
  - W is the crimp width, so the comparison is made at each crimp's own
    measured width: compaction goes with W × H, and the target height at a
    width W is 1.20–1.32 mm² ÷ W (0.80–0.88 mm at 1.50, 0.74–0.81 mm at 1.63)
    [calc final §7];
  - if the SN-2549 lands within ±0.05 mm of that and passes 39.2 N, what the
    WC-110 still adds is its stop blade and JST's insulation step.
- **JST's insulation step is set for a PVC-class wire.** "The insulation barrel
  is set and cannot be adjusted" [mfr S7], and JST calibrates on UL1007
  [mfr S6]. On 1.7 mm silicone the same step may sit low in this wire's window,
  where the wing tips risk cutting the jacket ([`f6`](f6-two-blades-two-drives.md)).
  A bend-and-look (bent **down** over a 2 mm pin) on the first few crimps
  answers it.

## Sourcing

| Part | Evidence |
|---|---|
| WC-110 | Digi-Key 147 in stock at $536.51; Newark 49 at $668.99; TME 15 at $564.96 (2026-09-28, via findchips) [xh-facts §2]. [Prime: JST WC-110, no listing found] |
| WC-110P replacement flap locator | Digi-Key 15 at $51.23 [xh-facts §2] |

## Major unresolved problems

- **Wire orientation.** "Side entry" [xh-facts §2]: the tool may need to stand
  on edge, with the wire horizontal and the contact laid in from above, rather
  than lie flat.
- **Handle force** is not published.
- **Ratchet release** on an aborted stroke, as in f1.
- **Cost.** $536, ten times the SN-2549 route, for a profile the $0.90
  reference crimp can judge first.
- **The insulation step on silicone** (above).
- **The fork's set** on the neighbours, as in f1.

## Which conclusions rest on assumptions

- **A flap locator can be loaded by a machine.** It is meant to be clicked out
  and checked by a person.
- **The stop window** assumes the carriage knows the expected stop depth to
  ±0.2 mm from the camera and the web clamp.
