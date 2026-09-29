# f3 — Knee micro-press: the die is the locator, the gauge is the micrometer

Explorer: force-and-form. Sketch: [`../sketches/f3-knee-micropress.svg`](../sketches/f3-knee-micropress.svg);
force curve: [`../sketches/force-stroke.svg`](../sketches/force-stroke.svg).
Numbers: [`../calc/drives.out.txt`](../calc/drives.out.txt) §B,
[`../calc/force_loop.out.txt`](../calc/force_loop.out.txt),
[`../calc/metrology.out.txt`](../calc/metrology.out.txt),
[`../calc/placement_budget.out.txt`](../calc/placement_budget.out.txt),
[`../calc/wave2.out.txt`](../calc/wave2.out.txt) [calc: wave2 §n],
[`../calc/final_w3.out.txt`](../calc/final_w3.out.txt) [calc final §n],
[`../calc/exchange_procedure_w3.out.txt`](../calc/exchange_procedure_w3.out.txt) [calc FP §n];
change-the-question's [`on_force_and_form.out.txt`](../../change-the-question/calc/on_force_and_form.out.txt)
[change-the-question calc off §n]. **[Prime]** is a row of
[`../../../sourcing/amazon-prime.md`](../../../sourcing/amazon-prime.md), observed 2026-09-28.
Branches: [`f3b-two-station-forming.md`](f3b-two-station-forming.md),
[`f6-two-blades-two-drives.md`](f6-two-blades-two-drives.md). Combinations built on it:
[`f8-narrow-press-at-the-housing-mouth.md`](f8-narrow-press-at-the-housing-mouth.md),
[`f9-tack-station-feeds-crimp-station.md`](f9-tack-station-feeds-crimp-station.md),
[`f9b-tack-on-the-strip.md`](f9b-tack-on-the-strip.md),
[`f10-lift-once-fin-from-below.md`](f10-lift-once-fin-from-below.md). Its dies:
[`f7-where-the-steel-comes-from.md`](f7-where-the-steel-comes-from.md).

## Picture it

A palm-sized steel die set sits on the bench, about 80 × 60 × 120 mm
[estimate].

- **Frame.** A steel base block carries two ground guide pins. A punch-holder
  plate slides on the pins in bushings, and a steel bridge ties the pin tops
  together.
- **Knee.** Between the bridge and the holder is a **knee**: two short steel
  links on hardened dowel pins, the same toggle that is inside every ratchet
  crimper, turned into a press. A NEMA 17 lead screw, or a hobby servo on a
  lever, pushes the knee sideways. When the links are straight, the holder is
  at the bottom of its stroke, and the bottom is set by link length, not by
  how far the motor turned.
- **Dies.** The crimpers hang from the holder. The anvil sits on the base on
  a shallow steel wedge; turning the wedge's screw raises or lowers the
  anvil, which is this press's crimp-height dial. A button load cell sits
  under the anvil. A 0.001 mm digital indicator on the base touches the
  holder right beside the dies, so the gap between crimper and anvil is
  measured directly and frame stretch drops out.

A crimp goes like this:

1. **The contact arrives on its carrier strip.** A printed side-feed track
   brings the strip in from one side, behind the dies. A small servo pawl
   advances it one pitch, and tapered pins drop into the pilot holes one pitch
   either side, far from the wire path, which brings the strip within
   ±0.1–0.2 mm (terminal-supply a2's practice).
2. **Pilot from below.** A steel pin rises through the track plate into the
   lead contact's own pilot hole and stops with its flat top level with the
   carrier's top face. It locates the lead contact to ±0.01–0.03 mm, and the
   wire that later slides over the carrier meets a flush steel face, not a
   pin [calc: wave2 §3]. A sprung hold-down presses the carrier onto the pin on
   both sides of the wire path. The strip, not a printed part, sets where the
   contact is.
3. **Capture.** The knee moves until the crimpers' channel has swallowed the
   wing tips, about 1.6–1.7 mm above the anvil. The load cell shows the
   first few newtons of wing contact. The press pauses there. Nothing is
   formed yet, and the contact is held on all sides.
4. **Look.** The ELP camera looks into the rear of the captured barrel. Is it
   open, square and not rolled? With a backlight, it also photographs the
   presented tip of conductor *i* and measures its bare length: where the
   insulation edge is, and whether the brush is whole.
5. **Thread.** The ribbon, already split and stripped with a light twist on
   the strands, is clamped in a small carriage behind the press by its web
   clamp, the datum for depth. A fork holds the neighbours aside. The carriage
   slides conductor *i* forward along its own axis, over the carrier (flat at
   floor level) and the flush pin, through the insulation barrel and into the
   conductor barrel, with the carrier still attached, so the tab is in tension
   and holds the contact against the push. It stops at the depth that puts the
   measured insulation edge mid-window. That splits the strip's ±0.2 mm scatter
   into ±0.1 mm on the brush and ±0.1 mm on the window, where a stop at the
   tips would leave the whole ±0.2 mm on the window [calc final §10]. The
   anvil is grounded: with the ribbon's far end in a pogo port
   (ribbon-as-pallet a6) or on a reel (procedure-is-the-machine p6), the
   strands touching the barrel read closed, which names the conductor in the
   die.
6. **Crimp.** The knee straightens. Load cell and indicator log force against
   true die gap through the whole forming stroke.
7. **Re-touch.** The knee backs off half a millimetre and comes down again
   until the load cell reads ~10 N. The indicator now reads the crimp height
   the way a crimp micrometer would, to about a micron [calc: metrology §1–2].
8. **Cut.** A floating shear under the carrier drops the carrier away from the
   wire and parts the tab, while the dies still hold the crimp.
9. **Proof pull.** The knee opens. A 0.3 mm neck blade, insulated from the
   anvil, drops from above into the neck between the box and the brush, and the
   carriage pulls to ~20 N, half of JST's 39.2 N, with the blade bearing on the
   box's rear face. The load path is the one JST's pull test means: wire,
   crimp, contact body, box [calc: wave2 §11]. The blade arrives after the
   crimp, so it never meets the tips; the neck needs t ≥ 0.50–0.70 mm for it
   [calc final §3]. A fork behind the insulation barrel cannot do this job:
   there is 0.03–0.18 mm of rim a side there, so it would bear on silicone
   [change-the-question calc off §8]. The carriage's web clamp must squeeze the
   jacket 15–30 % over 5–20 mm, or the strands slip inside it and a good crimp
   reads as a failed pull [calc FP §4].
10. **Release.** A stripper plate peels the crimp off the crimper, the blade
    lifts, and the carriage lifts the finished conductor away.

**The person** loads the split, stripped ribbon into the carriage, loads the
strip every few hundred crimps, and inserts. Each crimp takes one to two
minutes, most of it looking.

## What drives the crimp and carries the force

- **Force loop.** Bridge, knee links and pins, holder, crimper, crimp,
  anvil, wedge, load cell, base, pins. Everything in it is steel, and it is
  short.
  - Bridge bending over a 60 mm span of 12.7 × 40 mm steel: ~8 µm at 2.4 kN
    [calc, hand: FL³/48EI].
  - Die blades: 50–80 µm at peak [calc: metrology §2]. This is constant from
    crimp to crimp, so the wedge setting absorbs it; stubby blades reduce it.
- **Knee input.** Only **60–160 N** at the knee across the modelled force
  family, for links of 20–40 mm [calc: drives §B]. As the links straighten,
  the leverage climbs faster than the crimp force.
  - A NEMA 17 on a 2 mm lead screw gives ~377 N.
  - A 60 kg·cm hobby servo on a 25 mm arm gives ~235 N.
  - An air cylinder of 32 mm bore at 90 psi gives ~500 N.
  - Any of them does it.
- **Why a knee.** Its bottom is geometric. With 30 mm links, a knee stopped
  0.2 mm short of straight leaves the holder only 1.3 µm high [calc: drives
  §B]. The motor only has to reach a knee end-stop, and the knee's own
  geometry does the rest.
- **Pin and bearing stresses** at 2.4 kN on Ø6 hardened dowels in double
  shear are ~43 MPa, trivial [calc, hand].

## Dies: what makes the crimp, and where they come from

The conductor crimp on an XH contact is an open-barrel **B (or "F") crimp**.
- **Crimper.** A channel of the crimp width W, about 1.5 mm for 22 AWG by
  JST's analog SXA-01T [mfr S14]. Its roof is two arches that meet at a centre
  cusp, with a flared entry.
- **What the stroke does.**
  - The flare gathers the wing tips.
  - The arches roll them inward and down.
  - The cusp drives the tips into the strand bundle.
  - The last 0.1–0.2 mm compacts strands and wings together
    [xh-facts §4; calc: stroke_model].
- **Anvil.** A narrow blade whose top matches the barrel floor. It enters
  the crimper channel at the bottom. Its front end stops behind the lance, or
  carries a slot under it: the XH lance hangs 0.6–0.9 mm below the floor with
  its tip 2.44 ±0.20 mm behind the contact front, under the front of the
  conductor barrel [source S22]. A flat anvil there would carry the contact on
  its lance tip and flatten the retention feature
  ([`../calc/on_into_the_housing.out.txt`](../calc/on_into_the_housing.out.txt) §1).
- **Insulation crimp.** A second crimper and anvil, stepped about 1 mm higher
  [estimate] with a channel of about 1.8–2.0 mm [mfr analog]. It wraps the
  silicone without cutting it.
- **Bellmouth.** Crimper thickness along the wire is a little less than the
  barrel length, which leaves a bellmouth of about one stock thickness at the
  rear [mfr: MKS-L §6-10].

Four routes to steel with that shape:

| Route | What it is | Evidence | What it costs the idea |
|---|---|---|---|
| **a. Harvested SN-2549 jaws** | Bolt a $9.99 replacement jaw pair into steel holders on the holder and base, with the XH nest pair facing each other. The other nests are simply unused | Jaws are wire-EDM cut and replaceable with two screws each [source: icrimptools.com, iwiss.com, 2026-09-28]. No Prime listing sells them alone; the only Prime route is the 2549 die inside the iCrimp IWS-0723K set, $46.59, thin [Prime] | If the jaws **bottom on each other**, crimp height is theirs, and the stop shows in the curve as a sudden stiffness jump. In the tool they close on an arc: at 10–35 mm from the pivot one wing meets the crimper 0.05–0.17 mm of travel before the other, and by compaction the roll is under 1.2°. Closed straight, both wings touch together, so a straight die set should crimp as the tool does or more symmetrically, once the jaws are seated by closing them on each other [calc: wave2 §2]. The jaw screw pattern and seating faces must be measured, with the caliper or the Revopoint. The insulation step is fixed |
| **b. Quick-turn wire-EDM dies** | Crimpers and anvils drawn from JST analog dimensions (W 1.5, B roof), cut in D2/SKD11 and hardened | JLCCNC offers wire EDM, stating ±0.05 mm accuracy; Xometry offers wire EDM "in days"; SKD11 hardens to 58–62 HRC [source: jlccnc.com, xometry.com, asiatools.net, 2026-09-28]. Price not observed | J.S.T. UK's own crimp-width tolerance on its analogs is ±0.05 mm [mfr S13, S14], and at a fixed height ±0.05 mm of width moves compaction ±3.3 %. So a ±0.05 mm channel is usable when its width is measured (pin gauges) and the wedge sets height for that width: ∓0.027 mm of height restores width × height [calc final §7]. The anvil is then ground to fit the channel as cut. What no quoted tolerance covers is the roof's form (arches, cusp) |
| **c. Shop-made from ground stock** | Anvil blades from precision-ground O1 flat stock; B roof from two overlapping drilled holes in a hardenable blank, faced back through the hole centres; harden and polish | McMaster-class ground flat stock and drill rod [assumption: not priced here] | Needs careful drilling and hand finishing. Derek has a drill press, not a mill [repo]. Lowest confidence for the crimper; the anvil is easy, because a blade of ground stock stood on edge has its ground thickness as its width |
| **d. An OTP XH knife set** | The spare conductor and insulation crimpers and anvils of an XH side-feed applicator, held in a slot on the holder as the applicator's ram holds them | Listings titled for XH2.54 knife sets exist [source: terminal-supply, eBay 376757376428 and AliExpress 3256803331644772 titles; prices not read] | Industrial XH profile, separate conductor and insulation blades, made to be held and moved straight. Profile tooled for some XH contact, probably a clone |

[`f7`](f7-where-the-steel-comes-from.md) sets these four sources side by side
with what each gives a machine.

Printed dies are out:
- A wing tip loading a printed crimper face at 2.4 kN reaches thousands of
  MPa against ~50–100 MPa for printed polymer [calc: force_loop §4].
- Printed parts hold, guide, funnel and cover. The strip track, carriage,
  fork, camera mount and covers are printed.

## References and tolerances

- **Fixed reference.** The anvil.
- **Crimper to anvil, lateral.** The guide pins and bushings. The anvil
  blade must enter the crimper channel with a few hundredths of clearance a
  side. The two plates are line-bored together in one setup on the drill
  press with a reamer, or a bought guide-post set is used [assumption on
  achievable accuracy].
- **Contact to anvil.** Set by the strip's pilot hole on a steel pin, about
  ±0.03–0.06 mm; the window is ±0.1 mm axially [calc: placement_budget]. Feed
  pitch and pin position are screw adjustments, as in JST's MKS-L [mfr].
- **Conductor to contact.** The carriage threads to the camera-set depth,
  ±0.1 mm on each of brush and window, and the channel walls centre the
  conductor laterally. The worst risk, strands above a wing tip, is gone by
  construction: the conductor goes in after capture, through a closed channel.
- **The bore at capture.** Capture pinches the insulation wing tips. Whether
  the jacket then passes depends on the barrel floor's width: clear at 1.9 mm
  or more, ±0.05 mm at 1.8, 0.03–0.17 mm of interference at 1.6–1.7
  [calc: wave2 §1]. The knee can stop at any height, so the capture height is
  chosen from one end-on photograph of a kit contact: low enough that the
  channel holds the barrels, high enough that the insulation wings still stand
  open at the jacket's equator.
- **Crimp-height target.** Compaction goes with crimp width × height, so the
  target is set at this die's own measured channel width: 1.20–1.32 mm² ÷ W,
  0.80–0.88 mm at 1.50 mm, 0.74–0.81 mm at 1.63 mm [calc final §7]. The JST
  reference lead, copper-corrected (change-the-question c2), supplies the
  product at its own width.
- **Crimp height.** Set by the wedge. It is verified on every crimp by
  re-touch, which reads the gap between the same two surfaces a
  point-and-blade crimp micrometer measures between [calc: metrology §2;
  assumption that the crimp does not move between stroke and re-touch].
  The carrier still holds it in place.
- **Where precision is needed.**
  - At loading: pilot pin, which is the strip's.
  - At the first die touch: guide pins.
  - At the bottom: knee straight, and the wedge.
  - At release: stripper plate.

## Printed and bought

| Part | Printed or bought | Evidence |
|---|---|---|
| Base block, bridge, holder | steel, bought as plate or bar, drilled | SendCutSend A36 to 0.500 in [source]; or bar stock |
| Guide pins Ø10 h6, bushings; knee links; Ø6 dowels | bought | commodity; Misumi sells ball-bearing guide post sets [source: misumi-ec.com, price not observed] |
| Dies | route a, b or c above | see table |
| NEMA 17 lead screw, or a 35 kg·cm servo, or an air cylinder | bought | [Prime: Iverntech 42HD6039-05 NEMA 17 with Tr8×2 screw, $27.99, thin]; [Prime: ZOSKAY DS3235 35 kg servo, $27.99, 1,755 ratings]; [Prime: TAILONZ SC32×25 cylinder, $20.99, with 4V210-08 24 V valve $16.99 and flow controls $14.99] |
| Button load cell 500 kg + HX711 | bought | [Prime: 500 kg micro button load cell, $74.99, thin]; [Prime: SparkFun HX711, $11.50] |
| 0.001 mm digital indicator with data output | bought | [Prime: Clockwise Tools DITR-0105, 0.001 mm, RS232 port, $52.99, 67 ratings; its DTCR-01 cable had no Prime listing]. Mitutoyo ID-C with SPC output $451–668 at gauge dealers [source: judgetool.com, aftfasteners.com]. TouchDRO reads Mitutoyo SPC and iGaging/Shahe protocols on an ESP32 [source: touchdro.com]. A 0.01 mm capacitive scale is too coarse [calc: metrology §1] |
| Guide rods and bushings | bought | [Prime: 4 × 10 mm case-hardened chrome rods, $17.99; tolerance not in the title]; [Prime: uxcell 10 mm sintered-bronze flange bushings, 10 pack, $11.99, thin]. Line-boring, or a bought guide-post set (Misumi, price not observed) |
| Pawl and pilot-pin servos, tab shear | bought servos, steel shear, printed levers | — |
| Strip track, carriage, fork, camera mount | printed + printer-class motion | — |
| Contacts on strip | bought | SXH-001T-P0.6 1,000-piece strip, $40.10 at Digi-Key [source: xh-facts §6] |

A rough total, excluding the camera and ESP32 already on hand: $150–350 with
harvested jaws, more with EDM dies [estimate].

## What was tried against it, and the repairs

1. **A knee overshoots.**
   - *Conflict.* Pushed past straight, the knee lifts the holder again, and
     it offers almost no resistance there, so a stepper overruns.
   - *Repair.* A hard end-stop on the knee a hair short of straight. It
     costs a micron or two of height [calc: drives §B].
2. **Harvested jaws close on an arc in the tool and straight here.** In the
   tool, with the XH nest 10–35 mm from the pivot [assumption], one wing meets
   the crimper 0.05–0.17 mm of travel before the other and the roll at
   compaction is under 1.2°. Closed straight, both wings touch together, so a
   straight die set should crimp as the tool does or more symmetrically
   [calc: wave2 §2]. Five crimps compared by re-touch height and pull against
   tool-made crimps, and one section, check it.
3. **The carrier and axial threading.** The carrier and tab continue the
   barrel floor behind the contact: a flat 0.2 mm floor, not a wall. The
   conductor slides over it [source: xh-facts §1, side feed at the rear].
4. **The crimp sticks in the crimper.** Applicators carry a stripper for this
   [mfr: MKS-L §7-4]. A steel stripper plate with a slot sits under the
   crimper face.
5. **Die-blade compression, 50–80 µm at peak.** It is constant, and the wedge
   absorbs it. Its scatter at ±25 % force is ±0.01 mm [calc: force_loop §2].
   It is also why re-touch at 10 N, not the gap at peak, is the crimp-height
   reading.
6. **Stop at force or stop at position.**
   - With harvested jaws, the jaws bottoming is the stop.
   - With EDM dies, the knee's straight position is the stop.
   - Both are position stops. A force stop, such as a current-limited motor
     or an air cylinder, would also land within ±50 µm if the real crimp
     curve is as steep as modelled [calc: metrology §4]. The logged slope
     near bottom says whether it is.
7. **A pilot pin from above stands in the threading path.**
   - *Conflict.* The lead contact's pilot hole is on its centreline, 2.2–2.65 mm
     behind the insulation barrel, exactly where the conductor slides over the
     carrier. Riding over 0.3–0.5 mm of pin tilts the conductor 6.5–12.8° up
     into a captured barrel [change-the-question calc off §2].
   - *Repair.* The flush pin from below (step 2), plus tapered pins in the
     neighbours' holes from above, where no wire passes.
   - *Alternative repair.* No pin at the lead contact at all: guide plates, a
     pressure plate and the crimper's own centring, as in JST's MKS-L.
8. **Cut the tab first or last.**
   - *Conflict.* Cut at capture, and nothing reacts the threading push: a
     contact shoved 0.1 mm forward leaves the bellmouth window. Cut last, and a
     pull fork behind the barrel has no metal to bear on.
   - *Repair.* The order in the picture: pilot, capture, thread with the
     carrier in tension, crimp, re-touch, cut, then pull against the box's rear
     face.
9. **Chase the measured height instead of setting a stop (variant).**
   - *What changes.* No wedge to set. The knee drives to a depth short of the
     expected crimp height, re-touches, reads the true unloaded height, and
     goes deeper by the measured shortfall; two or three hits land within
     ±0.01 mm of the target [calc: wave2 §10].
   - *Why it is legitimate.* Loaded in one direction, unloaded, and reloaded,
     a work-hardening metal retraces elastically to its previous peak and then
     flows on the same curve. Several hits to a final depth form the crimp as
     one stroke to that depth does [source: standard plasticity; assumption
     that friction states reset little].
   - *What it cannot fix.* The target itself (the reference crimp,
     copper-corrected), and a hit that goes too deep. Every approach comes
     from above, and the knee's straight position stays as the over-travel
     guard.
   - *Where it meets another explorer.* This is the settable-stop press
     machine-that-sees-and-learns' v3 needs to sweep crimp height and find the
     window by pulling test crimps to failure.
10. **The insulation step.** A stepped crimper sets the insulation crimp by
    the step, and on this 1.7 mm silicone the step decides between cutting the
    jacket and overfilling the cavity ([calc: wave2 §5]). Branch
    [`f6`](f6-two-blades-two-drives.md) gives the insulation its own blade and
    drive.
11. **Two stops on one axis.** A neck blade in place while threading, used as
    the depth stop, and a camera-set depth would disagree by the strip's
    scatter: half the conductors would be fed 0–0.4 mm past first touch against
    a bundle that buckles at ~6 N free, folding strands back inside the barrel
    [calc FP §5]. So depth is the camera's, and the blade comes down only after
    the crimp, for the pull.

## Contribution

- **A per-crimp crimp-height measurement for the price of an indicator.**
  The gauge sits across the dies, not on the motor.
- **Pause at capture as the inspection point.** Before the wing tips reach
  the strands, nothing is committed.
- **Capture first, then thread.** This is JST's own WC-110 order of
  operations, and it keeps strands off the wing tips by construction.
- **A knee as the whole drive.** A hobby-class actuator makes 2–3 kN, and
  the bottom is set by geometry.
- **A flush pilot pin from below** that locates the lead contact at its own
  hole without standing in the wire's path.
- **A neck blade that reacts the proof pull** on the box's rear face, placed
  after the crimp so it never meets the tips.
- **Chasing a measured height** in two or three hits, for contacts and wire
  whose right stop nobody has published.
- **Motorless first build.** A hand lever on the knee (60–160 N is a hand
  push) driven to the knee's stop, with the person threading by hand: the
  die-as-locator and the re-touch gauge work before any motor is fitted.
- **The press next to the housing.** Its force signal and gauge are what a
  force-before-distance seating check needs. With narrow dies and a floating
  housing nest in front of it, it becomes
  [`f8`](f8-narrow-press-at-the-housing-mouth.md). The proof pull must come
  before insertion: ~20 N means something about a crimp, and a latched contact
  holds 14.7 N (a Molex analog) to at least 19.6 N (the KONNRA XH clone spec)
  [calc final §9].

## How it connects to the whole procedure

| Step | Who does it |
|---|---|
| Cut | before |
| Splay | before; the fork fans at crimp time |
| Strip | before; a stripped end with a light twist is assumed |
| Place the contact | **automated** (strip, pawl, pilot pin) |
| Thread the conductor | **automated** (carriage) |
| Crimp, measure, proof-pull, cut | **automated** |
| Insert | after; or a second station using the same load cell and indicator idea |

## Major unresolved problems

- **Die supply.** Route a's jaw seat geometry (the arc-versus-straight worry
  is small on paper [calc: wave2 §2]); route b's precision at quick-turn
  prices; route c's shop skill for the crimper; route d's profile, which is
  some vendor's XH contact.
- **The neck.** Whether the transition between box and conductor barrel
  takes a 0.3 mm blade in front of a visible brush: t ≥ 0.50–0.70 mm
  [calc final §3] (a kit contact side-on under the ELP camera).
- **The capture height** that holds the barrels without closing the
  insulation bore (the kit contact's floor width, end-on).
- **The flush pin's hold-down.** Whether sprung fingers either side of the
  wire path keep a 0.2 mm carrier seated on a pin engaged only 0.2 mm.
- **Carrier-strip geometry.** Pitch, pilot hole, tab length. Unmeasured;
  one $4.71 strip of 100 settles it [xh-facts Unresolved 2].
- **Threading 60 fine strands** into a captured barrel without a strand
  folding back. The twist, the funnel and the retry cover it on paper, and
  only a trial shows it.
- **How the 0.001 mm indicator is read.** The Prime-confirmed DITR-0105 has
  an RS232 port whose cable (DTCR-01) had no Prime listing; low-cost
  indicators' data protocols vary.
- **Whether a machine-made B-crimp from these dies matches JST's crimp
  height** for this ribbon, as for every idea here. That number is
  licence-gated [xh-facts Unresolved 1].

## Which conclusions rest on assumptions

- **Knee force (60–160 N)** rests on force-and-form's modelled crimp force
  family, peak 0.75–2.43 kN at the conductor barrel; xh-facts' estimate is
  0.75–2.3 kN for compaction and 0.8–2.6 kN in all, design to 3 kN. The two
  agree within the insulation crimp and tab cut that the family leaves out.
- **Frame and blade stiffness** are beam estimates on assumed sections.
- **Re-touch equals micrometer crimp height** assumes the crimp does not
  shift, and that the crimper arches and anvil touch the lobes and floor as
  the micrometer's blade and point do.
- **Line-boring on a drill press** is assumed to reach a few hundredths.
