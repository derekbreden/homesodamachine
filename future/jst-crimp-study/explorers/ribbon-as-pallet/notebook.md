# Notebook: ribbon-as-pallet, wave 1

## Log

- Read the brief, shared context, working method, xh-facts and prior-art, and
  the repo's `hardware/assembly/cable-assemblies.md`. The repo facts that shape
  this view:
  - the ribbon's marked edge carries conductor 1;
  - J2 and J7 trim one conductor each;
  - the board's XH wafers are vertical THT (`hardware/pcb/pcba/jlcpcb-parts.md`);
  - looms are labelled at the housing because J4 and J7 share a 7-way housing.
- Scaled the HDGC2501-T clone drawing (LCSC, xh-facts S19). It confirms:
  - the carrier joins at the insulation-barrel end by a 0.8 mm tab;
  - there is a Ø1.5 pilot hole on each contact's centreline, with rectangular
    slots between;
  - the insulation barrel opens 2.8 × 3.0 mm and the conductor barrel
    1.8 × 1.5 mm.

  Scaling by the hole gives a carrier pitch of 6.8 mm; scaling by the box gives
  7.5 mm. The drawing says 1:1 but is not to scale, so the pitch is an estimate.
- Found two useful sources:
  - **KONNRA's guide to its KR2501 XH clone**, which quotes PS-KR2501-01:
    - insertion ≤9.8 N and retention ≥19.6 N;
    - at 22 AWG, conductor crimp 0.73 ± 0.05 × 1.75 ± 0.15 and insulation crimp
      height 1.80 ± 0.10 with width 2.05 max;
    - strip length 1.6–2.1 mm.

    These are clone numbers, and they are used only as bounds.
  - **AMP US 4,230,008 (1980)**: a cable splitter whose jaw cavity is narrower
    than the cable, so the conductors register over the teeth.
- Sogang arXiv 2608.06996 details for insertion:
  - parallel approach 3/20;
  - lean-and-slide 18/20;
  - with weaving (±26.4° at 0.625 Hz) and a guide clamp, 49/50.

  That changed a6 from a yawed nest to a staircase clamp or a lean.
- Calc correction: I first had the silicone as the conductor's spring. It is
  the copper: 60 strands give EI ≈ 14 N·mm² even when slipping freely, against
  silicone's 0.8–2.4. The strands also yield below a ~67 mm bend radius. Two
  consequences:
  1. A fan formed by a comb stays formed (a5 F1, F4).
  2. The a1 lay-in finger leaves a permanent kink, so a1 needed a ramp to lift
     crimped contacts back to the neighbours' height before indexing.
- The web-search budget for the session ran out while looking for vibratory
  loading-plate sources. a2c's shaker-loading claim is therefore labelled an
  assumption.

## Rejected directions, and what would revive them

1. **Pre-loading contacts side by side at housing pitch (2.5 mm) for gang or
   sequential crimping.**
   - Why not: open insulation barrels are 2.46–3.00 mm wide on the clone
     drawings, so they touch or overlap at 2.5 mm [calc §3a], and no tooling
     fits between them.
   - Revive if the contacts on hand have insulation wings under ~1.9 mm open
     (JST's 1.95 mm envelope hints at this). Even then, only for a
     staggered-depth scheme.
2. **Crimping contacts that are already half-inserted in the housing.** Same
   collision, and no room for an anvil. Not revivable for XH.
3. **Staggered strip lines, odd conductors crimped further forward than even,
   to crimp at 2.5 mm pitch.**
   - Why not: the odd conductors end up 5–8 mm long and must bow in the fan
     for good.
   - Revive if parted length has to be minimal and a permanent bow is
     acceptable.
4. **A vertical fan** (conductors stacked one above another at the crimp
   station). They sit in the punch's path. Not revivable with a vertical punch.
   A side-acting crimp head would change that.
5. **Cryogenic stripping.** Silicone stays rubbery far below any practical
   bench temperature. Not revivable here.
6. **Abrasive stripping.** Soft silicone is expected to smear rather than
   abrade [assumption]. Revive if a quick test with a fine wheel shows clean
   removal.
7. **Pushing contacts into the housing from the pallet through a long free
   conductor.** It buckles: about 6 N at 5 mm free length, and 1.5 N at 10 mm
   [calc §4]. Replaced by a clamp right behind the barrels. Revive only with a
   closed guide channel all the way.
8. **Stripping with Derek's XLaserlab fiber laser.** It is a kW-class welder,
   near-infrared, which copper absorbs better than CO₂ light. Revive only with
   serious attenuation, and as a curiosity.
9. **A yawed-nest zipper for insertion.** A contact entering a cavity 5–8° off
   axis is ~0.5–0.8 mm off laterally over its ~6 mm length, so it would jam.
   Replaced by the staircase clamp. Revive if the cavities turn out to have
   deep entry chamfers.

## Questions I could not answer from documents

- Web thickness, notch depth and tear path of the BNTECHGO ribbon.
- The contact's carrier pitch. The kit contacts are loose, so measuring it
  needs a bought strip.
- How deep the contact's rear sits in a latched cavity.
- Whether the ribbon's marked edge is visible to a camera (it is all-black).
- Whether a lance snap shows on an HX711 load cell.
- The slim-nose width of a real XH side-feed applicator at the anvil.

## Wave 2: exchange on machine-that-sees-and-learns

- Written: [`../../exchange/ribbon-as-pallet--on--machine-that-sees-and-learns.md`](../../exchange/ribbon-as-pallet--on--machine-that-sees-and-learns.md).
  Numbers in [`calc/exchange_on_machine_that_sees.py`](calc/exchange_on_machine_that_sees.py)
  and its `.out.txt`.
- Carried into my own revision (the exchange's last section lists them in
  full):
  - piano-key fan block for a1's lay-in;
  - in-line silhouette crimp height at a1's station;
  - box hold-down for a2's proof pull;
  - lance relief under a2c's shoulder;
  - the floor on "copper keeps its shape": curls gentler than R ~23–47 mm
    are elastic under reversal;
  - a latch picture through the mating-face window for a6, and
    per-conductor insertion for the crossing looms.

# Notebook: ribbon-as-pallet, wave 2

## Log

- Read borrowed-machines' critique of this directory
  ([`../../exchange/borrowed-machines--on--ribbon-as-pallet.md`](../../exchange/borrowed-machines--on--ribbon-as-pallet.md))
  and every other explorer's summary. Checked their exchange calc against the
  physics before taking it in. Every break they raised holds:
  - **a1-1**, the finger acts too close to the fan block to drop 5 mm, and a
    point load leaves the tip diving. Agreed. A 5–6 mm drop costs 10–12 mm of
    parted length whatever makes it (my calc W2 §7 matches theirs).
  - **a1-2**, the neighbours at h sit over the feed plates. Agreed, and not
    repairable inside a1 without knowing the applicator's upstream envelope.
  - **a1-3**, the pre-feed collision. Agreed; their yield numbers for the
    conductor (40–60 mN at 6–9 mm) come from the same 0.36 N·mm plastic
    moment as my calc §4.
  - **a1-4**, the ramp's location. Agreed.
  - **a2-1 to a2-4.** Agreed, including that a ratchet tool's jaw lies along
    the row toward its pivot. That kills a2's and a2d's cut-down hand-tool
    heads, which I had listed as candidates.
- **A physics point of my own**, found while writing the stripping station.
  A fan pulls its outer conductors' tips back, because a curved groove is
  longer than its straight span. For a 5P it is 0.31 mm at 2.5 mm pitch,
  1.65 mm at 5 mm and 2.77 mm at 7.1 mm [calc W2 §3]. My wave-1 order put the
  flush cut first and the strip after the fan, which would have left a 5P's
  outer conductors 1.6 mm short of bare copper at 5 mm pitch and their
  insulation edges off the docking line. The order is now part, fan,
  flush-cut at the fan block's face, strip. The same geometry runs backward
  when a fan closes to 2.5 mm for insertion: the outer contacts come forward
  by 1.3–2.5 mm, which a6's clamp absorbs as bow.
- **The web as tangent circles.** Pitch equals OD, so neighbouring jackets meet
  at a line. That makes parting a question of one number, the fused neck
  thickness t_n against the 0.49 mm wall. Below ~0.6 of the wall a tear should
  stay in the neck; at or above the wall it wanders into a jacket [calc W2 §2,
  energy argument]. One cross-section photograph settles it.
- **Copper as a hinge in the tear.** The conductors yield at 0.36 N·mm, so a
  wedge-driven tear does not run far ahead as it would between elastic beams.
  The split root is set by where the tines stop, to about a millimetre, with
  the clamp as backstop. This is what makes a7's split root a pallet
  property.
- **Rolling instead of turning.** Looking for a full ring score without a
  rotating head: pads moving equal and opposite spin every conductor of a
  fanned row about its own axis, so two fixed razors score them all at once.
  A pinion between two racks makes the motions equal by construction. At
  housing pitch there is 0.8 mm between jackets, enough that neighbours never
  rub.
- **The insulation crimp on silicone** (a least-developed item in the digest).
  KONNRA's 1.80 × 2.05 mm insulation crimp leaves room for ~1.8 mm² inside;
  this conductor is 2.27 mm². So the jacket is squeezed to 70–80 % of its area
  and, being nearly incompressible, bulges out of both ends of the barrel
  [calc W2 §9]. The front bulge lands in the window between the barrels.
- **Contact use in a2e.** At N + 4 per ribbon end a unit takes about 110
  contacts, so a 100-piece strip is about one unit.
- Web search is exhausted for the session. Nothing new was fetched. New numbers
  are calculation or other explorers' cited findings.

## Rejected directions this wave, and what would revive them

1. **Scalloped form blades** (a row of semicircular notches at 1.7 mm pitch,
   closing top and bottom to strip a whole webbed end at once).
   - Why not: the blades must match the ribbon's real pitch. A 5P's
     accumulated error from a centred datum is up to 0.23 mm, against a
     margin of 0.06–0.19 mm between notch edge and strands. And sharp edges
     inside a 0.6 mm notch radius cannot be ground by hand.
   - Revive if the measured ribbon pitch stack is under ~0.05 mm across a 5P,
     or with one wire-EDM pair made to the measured mean pitch.
2. **Skiving the jacket with a fixed-radius rotating blade** (coax-tool style,
   the conductor fed axially into a turning blade). It leaves a skin on the
   strands if the radius is safe, and nicks them if it is not. Not revived.
3. **Quarter-rows onto the strip.** Four ribbon pitches are 6.8 mm, near a
   ~7.1 mm strip pitch, so every fourth conductor could dock onto a strip with
   no fan and 0.3 mm of error per pitch. It needs four dockings per ribbon, and
   a strip pitch nobody has measured. Revive if the measured strip pitch is
   within ~0.1 mm of 6.8 mm.
4. **Keeping a1's neighbours at h and raising h to clear the feed plates.**
   Every millimetre of h costs about two of parted length. It is left open in
   a1 until the applicator's upstream side is scanned, rather than rejected.
5. **Staggered-length fan grooves** (inner conductors given a hump so every
   path length equals the outermost one, like length-matched PCB traces). It
   would let the flush cut come before the fan. Flush-cutting after the fan is
   simpler. Revive if some station needs the tips on a line before fanning.

## Questions I could not answer from documents

- The ribbon's neck thickness t_n, valley depth and the bundle's eccentricity
  in its jacket: one fresh cross-section under the ELP camera.
- Whether a ring score tears cleanly on this silicone: a razor, a drill blank
  and one conductor.
- The OTP applicator's envelope: upstream plate heights (a1), downstream room
  for crimped contacts on their carrier (a2e), downstream tooling width at
  crimp pitch (a1c), and whether the terminal stripper lets a crimped contact
  leave along X.
- Whether the OTP cam has a window between the crimpers clearing and the feed
  moving.
- Silicone-on-PETG friction, for a3's fold.

## Wave 3: exchange on force-and-form

- **Written.** [`../../exchange/ribbon-as-pallet--on--force-and-form-w3.md`](../../exchange/ribbon-as-pallet--on--force-and-form-w3.md),
  numbers in [`calc/exchange_on_force_and_form_w3.py`](calc/exchange_on_force_and_form_w3.py)
  and its `.out.txt`. Two Amazon candidates added under "Wave 3" in
  [`sourcing-requests.md`](sourcing-requests.md).
- **Combination developed (K1).** Dock on strip, tack every insulation barrel
  on the strip in one stroke, cut the tabs with the tack comb as the pad, then
  crimp each tacked contact in a keyed steel nest (f9's heavy station with
  f3's knee and re-touch, f6's insulation blade, f4/f8's C). The carrier's job
  ends at the tack; neighbours stand a strip pitch apart at the press (jaws
  ≤10.8–11.4 mm); no planes, fork or fold.
- **Found against my own ideas.**
  - The lance props a contact 7.6–15.9° on a flat shelf or support comb (a2,
    a2e, a2b): each needs a groove along X, or a rail under the insulation
    barrel only.
  - a2's walking head, approaching from the box end, needs the transition
    t ≥ 0.34–0.74 mm to rise behind the lance, as f8 does.
  - A proof pull against the carrier folds the tab at 2.5–4.6 N (arm 0.95 mm);
    a pad on the crimped barrels or a blade on the box's rear face is needed.
  - f8's crown answers a2e's downstream room.
- **Found against force-and-form's.** The later half-row in f5b, f2c and f4
  has no stored feed (6–9 mm stroke against ≤0.42 mm of spread slack); f5b
  strips before its spread (0.14–0.42 mm stagger on rows of 4–5); f6's
  bend-and-look at the press can only bend up, closing top tip cuts; f9's
  station C has the other plane to park; f1's fork sets neighbours 30–46°.
- **Consistency.** KONNRA's 0.73 × 1.75 and the context's 0.88 × 1.5 are one
  compaction (W·H 1.28–1.32 mm²); target height scales with channel width.
  f7's ±0.01 mm channel against J.S.T. UK's published ±0.05 mm width.
  f&f wave2 §7's pin sizes are radii.

# Notebook: ribbon-as-pallet, final pass

## Log

- Read procedure-is-the-machine's reading of this directory
  ([`../../exchange/procedure-is-the-machine--on--ribbon-as-pallet-w3.md`](../../exchange/procedure-is-the-machine--on--ribbon-as-pallet-w3.md))
  and its calc. Checked each break against the physics before taking it in.
  Every break holds:
  - **B1** a2e's pull against a carrier held by end grips bows a 2.5–3 mm
    carrier 0.2–2.7 mm. Together with my own finding that the tab pitches at
    2.5–4.6 N with nothing on the barrels, the pull now runs with slot pins at
    every slot and the shear comb's pad down (tab in compression, 125 MPa,
    buckling >1.7 kN [calc F §3]), or through a blade on the box's rear face.
  - **B2** downstream reach ~43 mm with grips in spare contacts; grips in the
    carrier's end slots bring it to ~32–35 mm for a 5P.
  - **B3** a feedless applicator needs only a 6–8 mm stroke: a 3–4 mm eccentric
    on a NEMA 17 + 26.85:1 planetary, 1.0–1.7 N·m, with twice the samples. The
    bench's NEMA 23 and DM542T are installed in the cap-weld tube rotator; every
    file that called them "on hand" now says so.
  - **B4** a8b's 15 mm head butts the flat neighbours at 5 mm; a snout ≤7.8 mm,
    or lift-once. a1c and a4 strip with a8 at the fan face instead.
  - **B5** spool curl lifts a 35–50 mm protrusion out of the nicker's plane;
    covered floor, straightener, 80 mm rewind.
  - **B6** "a slight bow" is 2.2–4.5 mm; the fronts are left to step as a V and
    the clamp face is stepped to match.
  - **B7** the person's minutes in a1b and a2e with hand prep are above today's;
    recorded in both files as where the time goes.
  - **B8** J4's and J7's crossings run between the two ribbons; gapped closing
    blocks, the loft, the J7 wiring choice.
- **The capture reading (C2).** The clone drawings do not say whether the open
  widths are inside or outside; read as outside at the low tolerance, the jacket
  has ~0.01 mm a side. Docking may have to press: a finger comb at ~0.5–2 N per
  conductor, reacted by the rail [calc F §4].
- **The finished loom carries order A's length difference.** Working through
  X1's insertion step showed that the V staircase at insertion and the bow in
  the finished loom are the same length: in order A (cut after the fan) a 5P's
  outer conductors stay 1.34–2.46 mm long for good, a 3–5 mm arc in the split
  [calc F §5]. Order B (cut at the root before the split, equal-path fan) leaves
  every conductor one length; its V at insertion comes from the humps and is
  pulled out by the clamp's push at 0.06–0.23 N. a5 now holds three orders.
- **Kinematic seats.** The Prime dowel row is precision-ground 304, not
  hardened. Ball contacts at 10–40 N of magnet pull run 1,050–2,070 MPa; the
  stainless dents, hardened balls and case-hardened rod do not [calc F §1].
  Seats are now ball pairs or cut lengths of the Prime case-hardened rod.
- **Developed as ideas:** X1 as [a9](ideas/a9-reel-end-docks.md) (with three
  differences: a slip ring because the puller turns the reel; grips before the
  dock; the V from the humps); my K1 as [a10](ideas/a10-dock-tack-then-nest.md)
  and its no-motor branch [a10b](ideas/a10b-tacked-row-into-the-hand-tool.md).
  X4 went into a2c, X5 into a6, X6 into a8b, X3 into a3.
  The equal-path fan, rejected direction 5 of the wave-2 list, is revived: p7
  (strip before the split) is the station that needs the tips on a line before
  fanning.
- **Sketches.** [`sketches/make_sketches_w3.py`](sketches/make_sketches_w3.py)
  redraws a2, a2e, a3, a4, a5, a6 with current labels and draws a2b, a2c, a8b,
  a9 and a10 (with a10b). a1, a1c, a7 and a8 keep their earlier drawings, whose
  labels still hold.
- **Numbers aligned:** strip pitch 7.1 mm (Würth analog) with clone drawings at
  6.8–9.5 mm (xh-facts says 7–9.5, my HDGC scaling 6.8–7.5); strand yield radius
  39–78 mm and plastic moment 0.31–0.61 N·mm (my 67 mm and 0.36 N·mm are the
  70 MPa point); contacts per unit 55 / 67 / 81 / 111 by arrangement
  [calc F §7]; backshell heights recomputed for every split [calc F §2]; pogo
  pins are the Prime P75-E2 conical row; slip ring $9.99 Prime, two for a pair.
- No web search was available; nothing was fetched. New numbers are
  calculation, or other explorers' cited calcs.

## Rejected directions this pass, and what would revive them

1. **A proof pull against a carrier held only at its ends.** The carrier bows
   and the tab pitches long before 20 N. Revived only with slot pins at every
   slot and a pad on the barrels, which is the pull as it now stands.
2. **Grips in spare contacts' pilot holes.** They cost four contacts per end and
   push the row ~43 mm past the anvil. Revive if a pin in a rectangular slot
   turns out not to hold the carrier's Y; a rail along the carrier's edge is the
   first alternative.
3. **A 15–20 mm crank on a feedless applicator.** Revive if the OTP unit's ram
   or terminal stripper needs its full stroke to work.
4. **Forcing insertion fronts onto one line after a wide fan.** Revive in order B
   with the humps pressed flat, where the fronts are on one line anyway and a
   straight gang push (up to 39 N for a 4P) or lean-and-slide does the rest.
5. **a8b's head at 5 mm pitch without a snout.** Revive at a pitch of ~9 mm or
   more, where the neighbours' jackets are clear of the 7.5 mm bearing radius.
6. **Unhardened stainless dowels as seat grooves.** Revive with hardened, ground
   alloy dowels, which did not surface in the Prime pass.
7. **A flying lead on the hub socket through a powered draw.** The reel turns
   about once per loom. Revive where the draw is by hand and the lead is
   unplugged for it (procedure-is-the-machine's p6 stage 0).

## Questions I could not answer from documents

- The carrier's width, temper and slot size (B1, a9's pins, a2e's pilot): the
  $4.71 strip.
- Whether the clone drawings' open widths are inside or outside widths (C2): the
  same strip, and five kit contacts, under the caliper.
- The neck t between box and conductor barrel: it decides a2's head, the pull
  blade, a10's nest anvil and the neck-blade comb. One contact side-on under the
  ELP camera.
- Whether the OTP ram has a return spring, and its shut height.
- The BNTECHGO spool's hub radius and whether its inner end is reachable.
- Whether the SN-2549's insulation die re-forms a pre-closed (tacked) barrel.
- Whether an HX711 separates two lances latching together (the V's pairs).
- How much of an arc in a split behind the housing Derek accepts (order A).
