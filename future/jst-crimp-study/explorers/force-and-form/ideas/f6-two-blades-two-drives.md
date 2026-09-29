# f6 — Two blades, two drives: the copper to its stop, the jacket to its own height

Explorer: force-and-form. Branch of [`f3-knee-micropress.md`](f3-knee-micropress.md) (its press).
Sketch: [`../sketches/f6-two-blades.svg`](../sketches/f6-two-blades.svg) (schematic).
Numbers: [`../calc/wave2.out.txt`](../calc/wave2.out.txt) §5–6 [calc: wave2 §n],
[`../calc/final_w3.out.txt`](../calc/final_w3.out.txt) §1 [calc final §n] (bend
strain by pin diameter; wave2 §7's pins are radii),
[`../calc/on_into_the_housing.out.txt`](../calc/on_into_the_housing.out.txt) §9;
ribbon-as-pallet's [`exchange_on_force_and_form_w3.out.txt`](../../ribbon-as-pallet/calc/exchange_on_force_and_form_w3.out.txt)
[RP w3 §n]. **[Prime]** is a row of
[`../../../sourcing/amazon-prime.md`](../../../sourcing/amazon-prime.md), observed 2026-09-28.
Used by: [`f9b`](f9b-tack-on-the-strip.md)'s heavy station, [`f10`](f10-lift-once-fin-from-below.md)'s
second-blade branch; the same second drive fits f5 and f8 (below).

## Picture it

f3's knee micro-press, with its upper tooling split in two. The **conductor
crimper** hangs from the knee as before and goes to a geometric bottom. Beside
it, face to face in the same slot, the **insulation crimper** is a separate
blade with its own drive: a small NEMA 17 lead screw on a lever, never more than
~150 N, with its own bar load cell and its own stop, a motor-set wedge that sets
the insulation crimp height. The two anvils sit side by side on the base.

A crimp goes like this:

1. **Strip, pilot, capture, look, neck blade, thread**, as in f3. Both blades
   come down together to capture height, so both barrels are captive while the
   conductor is threaded.
2. **Conductor crimp.** The knee straightens; the insulation blade stays at
   capture height. The conductor crimp is logged and re-touched as in f3.
3. **Insulation crimp.** Now the insulation blade descends on its own, to the
   height its wedge sets. Its load cell sees only this barrel: tens of newtons
   of wing forming, a gentle slope as the jacket is squeezed, and, if the wing
   tips reach the strands, a slope 20–500 times steeper [calc: wave2 §6].
4. **Look at the insulation crimp.** The camera, with a backlight behind,
   reads the insulation crimp's height and width in silhouette, and the jacket
   just behind the barrel, where squeezed-out silicone shows as a collar.
5. **Cut and proof pull**, as in f3: tab, then ~20 N against the neck blade on
   the box's rear face.
6. **Bend and look.** The wing tips of this B/F insulation crimp sit on top
   of the jacket, pressed into it, so a tip cut opens only on the outside of a
   bend that takes the wire's tail **down**. At f3's press the strip track
   lies right behind the dies, so after the tab cut a section of the track
   behind the insulation barrel drops ~3 mm on the floating shear's lever,
   leaving room below. A 2 mm (diameter) hardened pin on a servo arm then bends
   the conductor 60–90° down just behind the insulation barrel, three times
   (JST's criterion is several 60–90° bends [mfr S5]). The camera looks at the
   top of the insulation crimp's rear edge while the wire is bent: over a 2 mm
   pin the jacket's outer strain is 0.46, and a 0.2 mm cut gapes 0.23 mm, a
   through-cut 0.56 mm, bright tinned strands on black silicone
   [calc final §1]. Bending **up** would put the tips on the inside and close
   the cut while the camera looks.
7. **Release**, as in f3.

**What locates what.** As f3: the strip's pilot hole on a flush pin, then
capture. Fixed is the pair of anvils side by side on the base. The conductor
crimp's height is the knee at straight plus its wedge; the insulation crimp's
height is its own motor-set wedge, a position, not a force. **What carries the
force:** the conductor crimp closes in f3's steel loop; the insulation blade's
≤150 N closes through its own light lever and wedge into the same base. **How
it knows:** the table under "What a picture shows" below.

**The person** does what f3 hands back, plus a one-time sweep per ribbon lot
to find this wire's window (below).

## What an insulation crimp is for, on this wire

- **It is not a pull-out grip.** Squeezing 0.49 mm of Shore 50–70A silicone
  (E ~2.5–5.5 MPa by Gent's relation) by 10–30 % gives 0.7–4.6 MPa of pressure.
  The strands then slip inside the jacket at 0.4–9 N, long before the jacket
  slips in the barrel [calc: wave2 §5]. JST's 39.2 N and UL's 35.6 N pull-out
  are the conductor crimp's; UL even pulls with the insulation crimp loosened
  [prior-art §6].
- **Its jobs are three.**
  - Hold the jacket so bending happens behind the barrel, not at the conductor
    crimp's rear edge.
  - Keep the contact's rear end within the cavity's envelope so it inserts
    (into-the-housing's point that insertability is an insulation-die
    dimension).
  - Not cut the jacket.
- **The jacket is invisible in the stroke's force.** Silicone pushes back
  1–13 N against the 30–130 N the insulation wings take to form, so neither a
  force stop nor a sprung insulation crimper can find the jacket. The
  insulation crimp on silicone has to be set by position.

## The window: a floor and a ceiling, both in height

Silicone is nearly incompressible, so what the barrel squeezes out of the
section leaves along the wire as collars at the barrel's ends. Modelled with
the enclosed area of the closed barrel and a 0.1–0.3 mm tip penetration below
the roof's mean surface [calc: wave2 §5, estimate]:

| Insulation crimp | Silicone under the wing tips | Local squeeze under a tip | Fits 1.95 × 2.4 envelope |
|---|---|---|---|
| 1.8 wide × 2.3 tall (nothing squeezed out) | 0.29–0.49 mm | 0–40 % | yes |
| 1.8–1.9 wide × 2.0–2.2 tall (0–20 % squeezed out) | 0.14–0.43 mm | 12–72 % | yes |
| 2.0 wide × 1.80 tall (KONNRA's clone figure, 20 % squeezed out) | 0.04–0.24 mm | 52–92 % | width over JST's envelope |
| 1.9 wide × 1.74 tall (30 % squeezed out) | 0.01–0.21 mm | 57–98 % | yes |

- **The floor** is cutting. Under a blunt 0.2 mm tip edge, a 200–500 %
  elongation elastomer is at real risk past ~50 % local squeeze and likely to
  part past ~70 % [estimate]. Each 0.1 mm of insulation crimp height moves the
  silicone under the tips by ~0.05 mm.
- **The ceiling** is the cavity. At the 1.95 mm catalog width, a 1.7 mm
  silicone wire stands 2.0–2.3 mm tall unless jacket is squeezed out
  ([`../calc/on_into_the_housing.out.txt`](../calc/on_into_the_housing.out.txt) §9).
  The contact's end-view envelope is 2.4 mm tall [mfr S1].
- **So the window is roughly 2.0–2.2 mm tall at 1.8–1.9 mm wide** [estimate],
  above the 1.80 mm the clone spec quotes for a PVC-class 22 AWG wire. A fixed
  tool (the SN-2549's stepped nest, the WC-110's set insulation barrel) lands
  wherever its step puts it; this press puts the insulation where the window is.

## What a picture shows, and what a pull shows

| Check | What it sees | What it misses |
|---|---|---|
| Silhouette of the insulation crimp (backlit, side and top) | Height and width to ~±0.02 mm; the collar of squeezed-out jacket behind the barrel, which measures e | The tips' penetration inside the jacket |
| Bend and look, tail bent down | A cut at a wing tip gapes 0.23–0.56 mm over a 2 mm pin (0.18–0.77 mm over 1–3 mm pins) and shows tinned strands on black; a shallow nick shows as a dark line under raking light [calc final §1] | A cut that stays closed when bent; any cut at all if the bend goes up |
| Insulation blade's own force curve | The moment the tips reach copper (a slope 20–500× steeper) | Anything before it; it fires after the cut |
| Proof pull (~20 N against the box's rear face) | The conductor crimp | The insulation crimp: the gripper's squeeze passes the pull into the copper, and the jacket between grip and barrel carries almost nothing |
| Jacket tug: a light grip on the jacket 10 mm back, 3–5 N, camera on the insulation edge in the window | Whether the insulation crimp holds the jacket: the edge stays put and the jacket stretches, or the edge slides back out of the window | A threshold: none is published; it is taught from crimps that pass bend-and-look |
| Continuity, from the far end or through the contact | Nothing about the insulation crimp: wing tips that cut through touch the same conductor the contact is crimped to | Everything here |

## Finding the window once per ribbon lot

Crimp five coupons at each insulation height from 1.8 to 2.4 mm in 0.1 mm
steps (35 crimps, ~1 m of ribbon, cents of contacts). For each: silhouette,
bend-and-look, jacket tug, and a push into a kit XHP cavity with a load cell
(into-the-housing i5's sensing nest) for fit. The floor is the lowest height
with no cut in any coupon; the ceiling is the highest that still enters the
cavity cleanly. The machine runs the middle and re-checks a coupon per lot.
This is machine-that-sees-and-learns' v3 campaign pointed at the second barrel.

## Mechanism

- **Two blades in one slot.** An applicator's knife set already comes as
  separate conductor and insulation crimpers, stacked face to face and clamped
  to the ram, with separate conductor-height and insulation-height wedges
  ("CH/IH wedge type height adjusting system with the precision of 0.02 mm and
  the range of 2.0 mm" [source: crimpapplicator.com KS-EM40R, 2026-09-28]).
  Here the clamp is replaced by a slide: the insulation blade moves along the
  conductor blade's face under a cover plate, 0.01–0.02 mm clearance.
- **Loads.** The insulation blade never sees more than ~150 N, so its guide,
  lever and wedge can be light; its bar load cell reads 0.05 N.
- **Order.** Conductor first, then insulation, as JST's two-step YC tools and
  the Engineer PA-09 do [mfr S4; prior-art §4]. The conductor crimp fixes the
  wire before the insulation wings close, so the insulation stroke cannot drag
  it. change-the-question c1b reverses the order on purpose (tack first); the
  sectioning experiment in [`f3b`](f3b-two-station-forming.md) compares both.
- **Anvils.** Conductor and insulation anvils side by side; the conductor anvil
  carries f3's lance relief.

## Branches

- **Overlap insulation profile.** An insulation crimper whose wings wrap past
  each other outside, instead of curling their tips down into the jacket. It
  takes the tips out of the jacket and lowers the floor. It needs an EDM-cut
  crimper ([`f7`](f7-where-the-steel-comes-from.md)); no bought XH tool was
  seen with one. Its wing edges then meet the jacket at the sides, so the
  bend-and-look must bend sideways too, where neighbours at 3.4–5.0 mm leave
  1.7–3.3 mm between jackets against a 1.7–2.7 mm sweep [RP w3 §6].
- **Bend-and-look away from the press.** Where nothing can drop out from under
  the barrel: a separate bend nest, open below, that the carriage visits after
  release (a keyed slot holds the box and barrels; the carriage moves the wire
  down and back); or a whole crimped row bent down at once over a steel edge by
  swinging the ribbon pallet about a hinge on that edge (ribbon-as-pallet K6:
  a fan-block face 9 mm behind the edge moves 7.8–9 mm down and 4.5–9 mm toward
  it at 60–90° [RP w3 §6]), one camera frame for the row. At
  [`f9b`](f9b-tack-on-the-strip.md)'s heavy station the stage bends each wire
  down over the insulation anvil's radiused rear edge.
- **The same second drive in other presses.** f2's applicator already has an
  IH wedge, set by hand. f5's cassette could carry the insulation crimpers on
  a second, spring-returned shoe closed after the stop blocks land. f8's narrow
  press could separate them too, since the insulation crimper can be
  thin-walled at 30–130 N.

## Printed and bought

| Part | Printed or bought | Evidence |
|---|---|---|
| f3's press, knee, indicator, conductor load cell | as f3 | f3 |
| Conductor and insulation crimpers and anvils as separate blades | an OTP XH knife set, or EDM | [`f7`](f7-where-the-steel-comes-from.md) |
| Insulation blade slide, cover plate, lever, wedge | steel, laser-cut and lapped | SendCutSend ±0.127 mm, 2–4 days [source: sendcutsend.com] for plates; the slide faces lapped |
| NEMA 17 lead screw, bar load cell + HX711 | bought | [Prime: Iverntech 42HD6039-05, $27.99]; [Prime: ShangHJ 5 kg bar load cell with HX711, 2 sets, $9.99, 100+ bought in past month] |
| Bend pin on a servo arm, backlight | bought servo, 2 mm hardened pin, light pad | [Prime: DS3218MG servo, $14.99]; [Prime: XIAOSTAR A5 light pad, $16.99]; a 2 mm hardened pin (a carbide rod or drill blank): not yet confirmed on Prime; the Prime pin-gauge set stops at 1.52 mm |

## Contribution

- **The insulation crimp on silicone, worked through:** not a grip, set by
  position, with a floor (cut) and a ceiling (cavity) about 0.2–0.4 mm apart in
  height, above where a PVC-wire setting sits.
- **A second drive for the second barrel**, so the machine sets and logs each
  barrel on its own.
- **Bend-and-look, tail down**: the one cheap check that sees a jacket cut
  through at a wing tip, which continuity cannot, and only in the direction
  that opens the cut.
- **A reason for a strain relief that is not the crimp.** Since the insulation
  barrel cannot carry the loom's pull on silicone (the strands slip inside the
  jacket at 0.4–9 N), ribbon-as-pallet's
  [a3](../../ribbon-as-pallet/ideas/a3-backshell-that-ships.md) backshell,
  whose IDC-style fold carries 14–69 N at μ 0.5–1 without loading any crimp,
  does that job (ribbon-as-pallet K5).
- **Agreement across views.** The window's model agrees with
  ribbon-as-pallet's separate figure: KONNRA's 1.80 × 2.05 mm leaves the jacket
  at ~70–80 % of its area there; 20–30 % squeezed out here. At 1.8–1.9 mm wide
  the window leaves 0.6–0.7 mm between insulation crimps at 2.5 mm pitch.

## How it connects to the whole procedure

As f3: it automates placing the contact (strip), threading, both crimps, the
checks, and the tab cut. It hands back splitting, stripping, ribbon loading and
insertion.

## Major unresolved problems

- **The window is modelled, not measured.** Tip penetration below the roof,
  the cut threshold in silicone under a blunt tip, and the cavity's real rear
  opening are estimates. The sweep above measures all three.
- **Where today's SN-2549 lands.** Five hand crimps under the caliper give its
  insulation height and width, and a bend-and-look on them says whether
  today's looms already have cut jackets at the barrel.
- **The slide.** Whether a thin insulation blade sliding along the conductor
  blade stays square without binding, once the conductor blade has taken
  2.4 kN.
- **Collars.** Whether squeezed-out silicone behind the barrel interferes with
  the housing's rear entry.
- **The bend test's own cost.** Three 60–90° bends per crimp on production
  parts is JST's inspection criterion, not a service condition. Whether to run
  it on every crimp or a sample is Derek's call.
- **Room below the barrel at f3's press**: the dropping track section is
  unbuilt, and the carrier strip must already be cut there.
- **Whether a tip cut in this silicone shows only at the top**, or also where
  the wing edges meet the jacket's sides.

## Which conclusions rest on assumptions

- **Silicone modulus** from Shore hardness (Gent's relation), wire-grade
  silicone assumed 50–70A.
- **Grip** uses a thin-layer compression modulus of ~2.8 E and friction of
  0.3–0.6 [estimate].
- **The cut threshold** (50 % / 70 % local squeeze) is an estimate.
- **The enclosed-area model** (shape factor 0.85, bundle mid-height) is crude.
