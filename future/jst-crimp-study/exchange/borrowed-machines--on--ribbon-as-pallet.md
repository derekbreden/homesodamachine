# borrowed-machines on ribbon-as-pallet

Wave 2 exchange. The view doing the reading: *somebody already mass-produces
most of this, for another purpose*. The view being read: *the ribbon is a
precision part* ([`../explorers/ribbon-as-pallet/summary.md`](../explorers/ribbon-as-pallet/summary.md)).

What I bring to their ideas: the physical layout of a bought side-feed
applicator, taken from JST's own applicator manual (read this wave, below). I
also bring the slow crank and its force curve (b1b), fold-back parking and the
fixed fork (b1), the hand crimper closed in a frame (b2), the travelling C-frame
head (b3) and the laser score (b4).

Citations:
- **[calc X §n]**: this exchange's numbers,
  [`../explorers/borrowed-machines/calc/exchange_ribbon_as_pallet.py`](../explorers/borrowed-machines/calc/exchange_ribbon_as_pallet.py),
  with its output [`.out.txt`](../explorers/borrowed-machines/calc/exchange_ribbon_as_pallet.out.txt).
- **[calc R §n]**: ribbon-as-pallet's
  [`pallet_geometry.out.txt`](../explorers/ribbon-as-pallet/calc/pallet_geometry.out.txt).
- **[calc B presses/geometry §n]**: my wave-1 calcs in
  [`../explorers/borrowed-machines/calc/`](../explorers/borrowed-machines/calc/).

## A fact base used throughout: what surrounds a side-feed anvil

These facts come from JST's MKS-L side-feed applicator instruction manual
[mfr: [MKSL_Instr_Man.pdf](https://media.digikey.com/pdf/Data%20Sheets/JST%20PDFs/MKSL_Instr_Man.pdf),
fetched 2026-09-28, text and drawings read]. OTP-type clones are assumed to be
laid out the same way [assumption].

- **Specification.** Pre-feed cam, feed distance 30 mm max, shut height 160 mm
  for the AP-K2N (not the 135.8 mm mini-applicator standard a1 cites). Crimp
  height is set on two dials, about 0.05 mm per graduation. The manual says to
  adjust the dials, "Do not adjust the shut height... to adjust crimp height."
- **Ram stack, in order along the wire axis** (p. 13):
  - spacer (A);
  - crimper (A), the conductor crimper;
  - spacer (B);
  - crimper (B), the insulation crimper;
  - spacer (C);
  - punch (157), which drives the floating shear blade (158) down on its
    spring (159) to cut the tab.

  The crimper plates neck down to narrow tongues at the bottom (exploded
  drawings, pp. 13 and 19).
- **A wire hold spring is a factory accessory** (p. 19). It is a sprung leaf
  mounted in the ram stack, either between crimper (A) and crimper (B) or
  between crimper (B) and the punch. A ram-mounted spring that holds the wire
  during the stroke already exists in the applicator's own design, which is
  a1's lay-in finger.
- **A terminal stripper** (147) keeps the crimped contact from riding up with
  the crimper. Its position depends on the strip length, and set "too far
  forward" it sits under crimper (A) (p. 20).
- **Upstream along the strip.**
  - A feed plate carries guide plates (L) and (R). The strip moves "freely from
    left to right" with "no movement front to back".
  - A spring-loaded pressure plate with a wing bolt holds the strip against
    back-drag.
  - A feed finger sits in a slot of guide plate (L), driven by a cam roller
    (pp. 9, 16–19).

  In the p. 9 photo the pressure-plate assembly extends several centimetres
  upstream of the ram at strip height [estimate from the photo, not to scale].
- **Wire-entry side, under the tab line.** The shear blade supporter and a
  scrap cover, a chute that carries chopped carrier pieces down and away
  (p. 20).
- **JST YRS-110** [mfr S8, fetched]: a "parallel action, ratchet style
  handtool... designed to crimp the applicable contact in strip form", with
  "1 crimping section with removable dies". It sells for $1,565.93 and Digi-Key
  has 9 in stock [xh-facts §2]. Whether it cuts the carrier, and how its body
  clears the next contact on the strip, are not stated.

---

## a1 Pallet tour: fixed strip-fed station, lay-in finger on the ram

### Break a1-1: the finger acts at the fan block's face, so a 5 mm drop has nowhere to happen

**Conflict.** The fan block holds the conductor at h = 5 mm with 9 mm
overhanging to the tip. Measured back from the tip, the finger acts at 5.6–7.8
mm: barrels and gap total 2.6–3.8 mm, plus a1's 3–4 mm behind the insulation
barrel. That leaves **1.2–3.5 mm of free conductor** between the block face and
the finger. An S-bend that drops 5 mm and comes back level needs:
- 11.3 mm at a1's own fan rule (R 5 mm, 30°);
- 5.2 mm even at a harsh R 2 mm, 60°.

[calc X §1]

**Physical consequence.** The conductor is sheared over the block's front edge,
or the block has to give. The point finger also applies no moment where it
presses, so the conductor ahead of it keeps its slope:
- 24–34° at 11 mm of free length;
- 40–51° at 6 mm.

The stripped tip then points 2.5–7 mm below the finger level: into the box or
the anvil face, not along the barrel floor [calc X §1].

**Repair A: move the crimp-station block back.** An overhang of 17–19 mm meets
the R 5 / 30° rule, 11–13 mm the harsh rule. That adds 2–10 mm of parted length
over a1's 20–35 mm [calc X §1].
- What changes: the lay-in is possible.
- What stays uncertain: tip wander at 17 mm of cantilever. Gravity is still only
  about 0.03 mm [calc R §4]; set from handling dominates. The V still has to
  capture it.

**Repair B: a flat sole instead of a V point.** This is b1's presser foot. A
sole at least 3 mm long along the conductor, with a V-groove for lateral
capture, presses the conductor onto the carrier and shear-blade line behind the
insulation barrel. That line lies in the contact's floor plane, so the sole
levels the conductor by applying a moment.
- What changes:
  - The tip lies along the barrel floor instead of diving.
  - The MKS-L's wire-hold-spring position (between crimper B and the punch) is
    a factory slot for exactly this part. That answers a1's "room on the ram
    for the finger" for JST's layout.
- What stays uncertain:
  - Whether an OTP clone has that slot.
  - The floating shear drops the carrier at BDC, and the conductor pressed on it
    goes down by the shear's travel [unmeasured].

### Break a1-2: the neighbours held at h sit over the applicator's feed side

**Conflict.** a1 holds every other conductor at h ≈ 5 mm across the station, on
both sides of the anvil. On the upstream side (X+) the strip carries waiting
contacts, and above them are the guide plates, the pressure plate with its wing
bolt, and the feed finger with its lever and cam roller.

- **Waiting contacts.** With neighbours in the anvil plane at 5.0 mm crimp
  pitch, some neighbour falls into a waiting contact at every strip pitch from
  6.8 to 9.5 mm [calc X §2]. That is why a1 needs h.
- **h over bare contacts** is 4.1–4.55 mm, so a1's 5 mm works for bare
  contacts.
- **h over the plates.** It rises to 6.3 mm if the plate tops are 5 mm above
  the strip, and to 9.3 mm at 8 mm [calc X §2, plate heights an estimate].
- **Lay-in.** Raising h lengthens the active conductor's S-bend to 13.6–18.8 mm
  at R 5 / 30° [calc X §2]. That adds to Break a1-1.
- **How many neighbours.** Up to 3 (4P), 4 (5P) or 8 (J1 fanned as one) sit
  spread over X = 5–40 mm upstream, which is where those plates are.

**Physical consequence.** Uncrimped stripped tips drag across the pressure plate
and feed finger as the stage indexes, and crimped contacts on the neighbours can
catch under the wing bolt. At the ends of the row, the stage cannot bring the
far conductors to the anvil without the fan passing through the feed mechanism.

**Repair C: crimp from the upstream end, park after crimp** (a1 × b1, see
combination C2).
- Order the crimps so that every uncrimped conductor is always downstream (X−).
  Downstream there are no waiting contacts; the MKS-L chops the spent carrier
  and drops it down the scrap chute.
- A fork fixed on the applicator's axis folds each crimped conductor back 180°
  over the pallet top before the index, so nothing ever sits upstream.
- What changes:
  - Downstream neighbours can lie in the anvil plane, so h, the S-bend, the kink
    and the ramp all disappear.
  - The tooling's lowest 3 mm then has to be no wider than a half-width of 3.95
    mm beside a bare conductor at 5 mm pitch [calc X §4].
- What stays uncertain:
  - Whether the crimper tongues are that narrow. Nothing about an applicator's
    function guarantees 5 mm (below).
  - What downstream parts (side block, scrap cover) sit at plane height.
  - The fold of each crimped conductor at its root.

**Repair D: full fold-back (b1 as it stands, on a1's pallet).**
- Every conductor except the active one is parked folded back. The active one is
  laid forward flat by the fork, at the clamp's own height.
- What changes: parted length falls to **8–15 mm** instead of 20–35 [calc B
  geometry §1]. No crimp-pitch fan block is needed, only the 2.5 mm one.
- What stays uncertain:
  - Web-root peel at the fold.
  - Every conductor is folded twice, so its root carries set that insertion has
    to straighten.

**Branch: a strip segment instead of the reel.** No waiting contacts, and no
feed hardware upstream. That is combination C1.

### Break a1-3: the pre-feed can push the next contact into the crimped one

**Conflict.** a1's cycle runs: ram rises, pre-feed puts the next contact on the
anvil, stage backs out. A pre-feed applicator advances the strip during the
return so that a contact waits at rest [prior-art §3]. The crimped contact, now
cut free, is still sitting on the anvil. A hand-held wire yields when the new
contact shoves it aside; a pallet holding the conductor 6–9 mm back does not
resist either, but it deforms.
- The 60-strand bundle yields at 40–60 mN at that lever.
- A feed finger pushes with newtons [estimate].

**Physical consequence.** One of two things happens:
- the crimped conductor is bent 37–58° sideways, permanently, one strip pitch
  over [calc X §3];
- or the incoming contact's wings ride against the crimped barrels and the feed
  jams, with bent wings.

**Repair E: a crank that stops between the punch clearing and the feed moving**
(from b1b).
- A stepper crank stops at the crank angle where the punch has cleared the
  crimped contact but the feed cam has not begun to rise.
- The stage backs out, then the crank completes the turn.
- A bought fast press cannot do this.
- The a1b hand-lever version does it naturally: the person pauses the lever.
- What stays uncertain: whether that angular window exists on the OTP cam.
- Measurement: hand-cycle the applicator on arrival and note the ram height at
  which the feed finger starts to move.
- Setting the cam to post-feed is not a repair. The contact would then arrive
  on the downstroke, under a conductor that is already laid in.

**The same break is in my b1.** Its step 6 backs the cassette off after a full
press cycle.

### Break a1-4: the ramp sits where the shear blade and scrap chute are

**Conflict.** The fixed printed ramp "behind the anvil" occupies the wire-entry
zone next to the anvil. The MKS-L puts its floating shear blade, the shear blade
supporter and the scrap chute there (p. 20). The ramp would also be under the
lay-in path of the next conductor.

**Repairs.**
- Make the lifter part of the pallet: a small comb under the conductors at the
  pallet's front, raised by a cam when the stage bumps a stop while backing
  out. This is a1's own passive-pallet habit.
- Or use b1's fork to lift and park the crimped conductor (Repair C/D).

**What stays uncertain:** the bend-back of the kink. It persists with the
lifter, and it goes away only if the kink is never made (Repairs B + C/D).

### a1's "crimp height not measured in line": a transfer from b1b

Bottom dead centre fixes where the ram would stop. Frame stretch under the
actual peak moves it. So a strain gauge on the frame or connecting rod, read
through a slow crank, gives each crimp's height deviation as ΔF/k:

| Frame stiffness | ±15 % force scatter on a 2 kN crimp | Resolution at 30 N |
|---|---|---|
| 13 kN/mm | ±23 µm | ~2 µm |
| 39 kN/mm | ±8 µm | ~1 µm |

[calc X §9]
- A micrometer sets the baseline on the first crimps.
- This needs a slow bottom of stroke. An HX711 at 80 Hz gets:
  - 0.3 samples in the last 0.2 mm from a bought press;
  - 0.8 from a hand lever;
  - 19 from a 10 s crank, because of its dwell at BDC [calc X §10].

a1's load cell under the applicator base therefore only draws a curve on the
crank press.

### What else a1 has not yet seen
- **Guarding.** An XY stage firing a press on its own needs an interlocked
  enclosure. At a crank's walking pace it is a pinch point, not a 2 t blow
  (b1, b1b).
- **The applicator's envelope decides a1's h, the sole's room and C1.** It is
  unknown until a unit arrives. The Revopoint MINI 2 on hand (0.02 mm) can scan
  the wire-entry face and the upstream side into CAD. The pallets are then
  designed against the scan, not against estimates.
- **The zero-build first test.** The VEVOR 12 t press's own jack strokes an
  applicator by hand, with a hard-stop collar (b1b). a1's fan block, sole and
  flush cut can be tried against a real anvil before any stage exists.

---

## a1b Hand shuttle

- **Break: the SN-2549 variant.** A scissor or ratchet tool's die axis is
  normal to its jaw plane. With contacts along Y and the crimp in Z, the jaw
  therefore lies along X, the row direction, toward its pivot. At 5 mm pitch
  every neighbour within the jaw's 20–40 mm span [estimate, b2] is under or over
  a jaw [calc X §6].
  - At the captive click the conductor must also go in along its axis, since
    the upper jaw is over the nest. Neighbours at h = 5 mm meet the jaw's front
    face, whose top is ~10–15 mm above the nest [estimate].
  - Repair: park by fold-back (combination C3). What stays uncertain is a
    person's speed at folding.
- **What a1b gets for free: the pause between crimp and feed.** The person on
  the lever stops between crimp and feed, which fixes Break a1-3 without
  electronics.
- **Transfer: the hand press.** The VEVOR jack with a hard-stop collar, or the
  $79.98 KAMsnaps DK93 snap press as a guided lever frame for harvested
  applicator blades [source, b1b and notebook], can stand in for the TE
  91085-2-class frame.
- **Transfer: sensing.** A hand lever gives under one HX711 sample in the last
  0.2 mm [calc X §10], so the check is the person's look, as a1b already says.

---

## a2 Two pallets meet

### Break a2-1: the tab's Z window is a tenth of a millimetre

**Conflict.** Each contact cantilevers on its tab, about 0.8–1.0 × 0.20 mm. The
walking head's lower jaw slides under the barrels from the box end.
- The tab yields at 0.5–0.9 N applied at the box, or 1.0–1.7 N at the barrels.
- Its elastic lift at 3 mm is 0.10–0.14 mm before yield [calc X §5].

**Consequence.** A jaw arriving 0.1 mm high lifts the contact and bends the tab
for good. The contact's roll and pitch relative to the carrier then change
before the crimp.

**Repair.** The head's lower arm rides a hardened rail on the strip pallet
whose top is flush with the contacts' floor, and the head floats in Z on that
rail. Z comes from the strip pallet, not from the carriage. a2 already floats
the head; the rail gives it something to float on.

**What stays uncertain:** the stamping's floor-height scatter along a strip.

### Break a2-2: the pilot pin reaches under the carrier

**Conflict.** The round pilot hole lies behind the tab, in the carrier.
- A pin rising from the lower jaw has to reach 7–8 mm in from the box end.
- It then has to pass through a relief in the strip pallet under every hole.
- The ribbon's insulation lies directly on top of that hole.

**Repair.** Do what applicators do: centre in X by the anvil's own cradle as the
crimper closes. The MKS-L centres its crimpers to its anvils once, by eye
against white paper (p. 15), and uses no pin at the terminal. The slot pins of
the strip pallet already hold the contact to about ±0.05 mm [a2 assumption].

**What it changes:** no relief under the carrier, and a shorter lower jaw.

### Break a2-3: the gang shear needs a die under every contact

**Conflict.** A tab shears at 50–160 N, so 250–800 N for five. That is 20–200
times the tab's own yield moment at 1–3 mm [calc X §5]. Without a die edge under
each contact's rear, the crimped contacts bend down with the carrier, and the
tab tears long and ragged. JST lists "too much cut-off length" as a fault
[mfr S5].

**Repair.** A shear comb:
- a lower bar with one notch per contact at strip pitch, its edge at the
  contacts' rear;
- an upper pad on the crimped insulation barrels;
- the carrier driven down past the edge, as a floating shear does.

Tab length is then the bar edge's position against the slot pins.

**Branch.** The head carries its own shear, the MKS-L's punch (157) over a
floating blade, and cuts each tab at BDC as an applicator does.
- What changes: the flush-tab problem is solved per contact.
- What it costs: a2's proof pull against the carrier. The pull then goes
  against a slotted catch plate, as in b1.

### Break a2-4: a hand-tool head cannot walk a row

The same jaw-along-X geometry as a1b applies. At 7.1 mm strip pitch, 1–4
neighbours lie within a 10–30 mm nest-to-pivot jaw extent [calc X §6].
- Cutting the jaw down to its XH nest removes the far side, never the pivot
  side.
- The ratchet-crimper-with-actuator candidate for a2's head crushes or lifts
  neighbours on that side.

Two routes stand beside it:
- **b3's C-frame head, turned for a2.**
  - The C opens toward the carrier, with its back beyond the box end. Its arms
    are ≤10 mm wide in X, which clears at 7 mm [calc R §3b].
  - A NEMA 17 with 10:1 turning a 3 mm crank gives 3.8 kN at 0.1 mm above BDC.
  - The head is about 1 kg. A 10–40 kN/mm C gives ±30 to ±8 µm [calc B
    presses §5].
  - It uses a harvested OTP crimper and anvil.
  - What a2 contributes to b3: the head no longer holds a captive contact or
    slides a conductor in axially. The two worst problems of b3, strand splay
    on axial entry and buckling, vanish.
- **YRS-110.** It is JST's one hand tool made "to crimp... in strip form",
  parallel action, one section. Its purpose implies it tolerates the next
  contact on the strip beside the die, at least on one side [assumption].

### A detail in a2's proof pull

The fanned outer conductors reach their contacts through S-bends. A single
spring pull on the pallet loads the straightest conductors first. At ~20 N the
copper, which yields at 0.36 N·mm [calc R §4], straightens the outer S-bends
until they take load, and the fan's shape changes.
- Repair: grip each conductor at the fan block's front face, at ≥20–40 N normal
  [calc R §4].
- Or pull one conductor at a time with a hook on the stage.

### Combination C1: the docked cassette runs through a feedless applicator (a2 × b1b)

**The fact that makes it work.** An applicator's tooling is narrow enough, by
its function, for a contact standing open one strip pitch upstream. Its lowest
~3 mm must fit within a half-width of 5.1–5.4 mm at 6.8 mm pitch, or 5.4–5.7 mm
at 7.1 mm [calc X §4]. a2's docked row is exactly that: open contacts at strip
pitch, each with its conductor lying inside the wings. Nothing guarantees
clearance at a1's 5 mm (needs ≤3.95 mm).

**Arrangement.**
- **The applicator.** A bought OTP side-feed applicator, in b1b's slow crank or
  on the shop press's jack. It is stripped of what covers the carrier line
  upstream: the pressure plate, the feed finger, and the guide plate on the
  wire-entry side.
- **What it keeps:**
  - crimpers, anvils and dials;
  - the terminal stripper;
  - the track surface the strip slides on;
  - optionally the shear.
- **The strip pallet** holds the carrier from above, with a2's comb clamp bar
  between the conductor paths and pins down into the rectangular slots. The
  applicator's own track supports the contacts from below as they slide onto
  the anvil. The swing-away support comb is not needed.
- **Docking.** The ribbon pallet docks on the strip pallet as in a2, with every
  conductor placed in its contact.
- **Indexing.** A single X stage moves the pair by strip pitch, and the crank
  turns once per contact.

**What each side contributes.**
- a2: placement by docking, the carrier as fixture, continuity to the grounded
  carrier before any stroke, and one pallet type per loom.
- Mine:
  - a bought, aligned die set with dials, so a2's "die making is the hard part"
    goes away;
  - a slow force curve;
  - stop-before-bottom when the curve is wrong;
  - the applicator's own track as the contact support.

**What stays uncertain.**
- Which OTP parts unbolt.
- Whether the shear punch's width at the carrier line clears neighbouring
  conductors lying over the carrier at ±7 mm (needs a half-width ≲6 mm).
- What happens downstream, where crimped contacts on conductors pass the scrap
  chute.
- a2's 21–30 mm parted length per ribbon is unchanged.

---

## a2b Gang stroke in the 12 t press

- **Transfer: one load reading sees a gross miss.**
  - For a 5-contact stroke, a missing conductor drops the total by 12–20 %, and
    a missing contact by 20 %.
  - One strand of 60 is 0.34 %, invisible [calc X §11].
  - Against a ±4 % band [digest], a load cell or strain gauges on the lower
    shoe catch the gross faults while the person pumps. The pumping is slow, so
    the HX711 has time.
  - The camera says which contact.
  - This answers a2b's "missing contact is a silent miss".
- **Transfer: the stripper plate.** The applicator's terminal stripper (MKS-L
  147) is the pattern for a2b's unresolved "punch retraction": a plate that
  holds the work down as the crimper rises, one finger per contact, positioned
  by strip length.
- **Die sourcing from my view.** N harvested OTP crimper/anvil sets at
  $125–165 each [source, b1] are the bought route to a2b's "harvest" option.
  - Each pair was aligned in its own applicator by the side block (MKS-L p.
    15). In a2b's shoes each pair needs its own side adjustment and its own
    height shim.
  - The stop blocks set the shoe gap, not each punch's protrusion.
  - This is the same alignment problem as my b3, multiplied by N.

---

## a2c Loose-contact cassette

- **Transfer: load the nest bar from strip with b2's mechanism.** b2 has an
  SMT-style sprocket feeder, a tab shear and a tweezer gripper that holds the
  contact by its box, outside any die. Aimed at a2c's pockets instead of the
  SN-2549's nest, it gives:
  - free pitch (a2c's reason to exist);
  - orientation carried from the strip;
  - no shaking and no tangling;
  - cheap reel stock ($0.0235 genuine, $0.008 clone [digest]).
  - What stays uncertain: b2's own tab-cut position and gripper repeatability.
- **Transfer: the stapler magazine** (b2's fallback, from my notebook). Loose
  BXH contacts stacked nose to tail in a printed stick, pushed by a spring,
  one sheared or picked from the front. It is a middle path between tweezers
  and a shaker. Loading the stick in orientation is still the person's job.
- **Where a2c stays useful from my view:** it is the only route for the kit
  contacts actually on hand. The strip route needs a purchase.

---

## a2d By hand

- **Break: the cut-down jaw** (the same geometry as a2-4). At 7.1 mm pitch, 1–4
  neighbours lie on the pivot side within a 10–30 mm jaw extent [calc X §6]. A
  cut-down SN-2549 on a detented rail crimps the contact at the row's pivot-side
  end, and then the next one lands its jaw on the crimped one.
  - Using alternate contacts (14.2 mm) leaves 0–2 neighbours, depending on jaw
    extent. It wastes half the strip, and the fan doubles.
- **Repairs that keep "no motors".**
  - **YRS-110 on the rail**, for its strip-form purpose [mfr S8; body clearance
    an assumption].
  - **One harvested applicator die pair in a guided hand frame** (the snap
    press, or the shop press's jack over the cassette), the cassette sliding
    under it on a2d's detents. The force comes vertically through a narrow die,
    not through a jaw along the row.
- **What a2d still tests unchanged:** placement by docking, the cheapest test
  of a2's core. It needs no crimp tool at all: dock, photograph, check
  continuity to the carrier.

---

## a3 The backshell that ships

- **Height numbers.** a3 puts the backshell at the split root, so its height
  above the board depends on the parted length:

  | Parting | Parted length | Top of backshell above the board |
  |---|---|---|
  | Fold-back parking | 8–15 mm | 30–37 mm |
  | Housing fan only | 14–18 mm | 36–40 mm |
  | a2, per ribbon | 21–30 mm | 43–52 mm |
  | a1, 5 mm crimp pitch | 20–35 mm | 42–57 mm |

  [calc X §7, housing mated height 9.8 mm, backshell 12 mm]. a3's own 35–45 mm
  estimate holds only for the short partings.
- **Transfer: the IDC strain-relief fold.** Every IDC ribbon connector ships
  with one, mass-produced: the cable folds 180° over the connector's back and a
  clip snaps over it.
  - A 180° wrap multiplies what the clip holds by e^(μπ): 4.8× at μ = 0.5 and
    23× at μ = 1.0.
  - A clip holding 3 N on the tail resists 14–69 N [calc X §8].
  - Ridges biting silicone need high local pressure on a material that tears at
    15–25 N/mm.
  - What changes: the grip comes from friction around a bar, not from cutting
    into the web.
  - What stays uncertain: silicone's μ on PETG. The doubled ribbon also adds
    ~1.7 mm of thickness at the backshell.
- **Transfer both ways with my cassette.**
  - b1 needs the clamp edge exactly on the split root, or the fold-back peels
    the web. b4's laser can split the webs from a face and score the strip ring
    at a set distance from the flush-cut face. The backshell's front face is
    that face (combination C5).

---

## a4 Spool as magazine

- **The a1 breaks carry over.** a4's clamp and X slide index under a fixed
  applicator with a1's finger and ramp. Breaks a1-1 to a1-4 all apply, and
  Repairs B–E apply too.
  - Fold-back parking fits: parked conductors fold back over the clamp toward
    the spool.
- **Transfer: the bought machine for a4's feed-and-cut.** Bench wire
  cut-to-length machines are mass-produced for exactly a4's job: a stepper
  roller or belt feed, an encoder and a guillotine [assumption on
  ribbon-width guides and price; filed in my sourcing requests]. a4's feed
  module does not need designing. The press's reel arm (b1) keeps the contact
  reel threaded: an 8,000 reel is about 150 units [digest].
- **What a4 has not seen: the guillotine exposes two ends at once.** When it
  cuts, the finished loom's far end lies just past the blade, held by the pull
  gripper or at the top of the drop tube. The same press, with a second bought
  applicator for 6.3 mm Faston on reel [assumption: commonly sold in the same
  OTP market], could terminate that far end before the loom is released.
  - Ferrule ends have their own mass-produced strip-and-crimp machines
    [assumption].
  - IDC and screw-terminal ends stay with the person.
  - Every a1–a4 arrangement currently hands all far ends back.

---

## a5 Part, fan and strip module

- **Transfer: b4's laser in a5's pallet.**
  - The H2C takes Bambu's 455 nm modules: $698 (10 W) and $1,348 (40 W) kits,
    in stock [source, b4].
  - Slits across the web and a score ring top and bottom to 80 % of the wall
    leave 4–11 N of tear-off per conductor. With ±45° flank passes it is
    1.6–4.4 N. Unscored it is 7.5–20 N [calc B geometry §3].
  - a5's S1 whole-end slug estimate of 6–25 N per conductor agrees with my
    unscored figure. Flank passes are the cheap fix for S1's ragged flank tear:
    a flat blade scores top and bottom, the laser the flanks.
  - What stays uncertain: silicone under 455 nm is untested. Copper absorbs
    ~65 % at 450 nm, so the laser must score, never strip through. a5's
    isolated-blade nick detector cannot watch a beam.
- **Transfer: the strip-crimp applicator.** JST names MKS-SC (and in 2022
  MKS-L) a "strip-crimp applicator" [mfr S2, S4]. Kingsing's KS-T903 strips and
  then crimps a wire placed in position [source, b1 notebook].
  - If a strip-crimp OTP unit for XH exists [assumption], a1's strip station
    joins the crimp station.
  - Silicone flaps are the risk, and a camera frame the check.

---

## a6 The housing is the last comb

- **Transfer: Molex US 4,936,011 slide-along jaws** (b1's insertion
  extension). The jaws close lightly on the conductor and slide forward until
  they meet the rear of the insulation crimp, then push on that shoulder.
  - The push goes into the crimped barrel, not through friction on silicone.
  - It answers a6's worst unknown, whether the clamp can follow the contact
    home. If the crimp's rear latches up to ~1 mm inside the cavity, the last
    1 mm is pushed through a free length that buckles only at ~150 N [calc R
    §4], against ≤9.8 N of insertion.
  - What stays uncertain: that depth, which one kit housing shows.
- **Transfer: a6's pogo port and my b1.** Covered under "Where their work
  changes mine".

---

## Combinations

| # | Theirs | Mine | What each contributes | What stays uncertain |
|---|---|---|---|---|
| C1 | a2 docking and strip pallet | b1b applicator in a slow crank, feed removed | Theirs: placement by docking, carrier as fixture and continuity check. Mine: a bought die set with dials, a force curve, the applicator's track as support. Clearance at strip pitch is guaranteed by the applicator's function [calc X §4] | Which OTP parts unbolt; the shear punch beside neighbours; the downstream side; 21–30 mm parting |
| C2 | a1 pallet, flush cut, in-plane downstream fan | b1 fork: park after crimp, crimp upstream-first | Theirs: each conductor folds once (after crimp), not twice; the flush-cut reference. Mine: nothing ever upstream, so no h, no finger S-bend, no ramp, no feed conflict | Crimper tongue ≤ ~7.9 mm wide at 5 mm pitch [calc X §4]; downstream parts at plane height |
| C3 | a1b kinematic seats, X detents, Y stop | b1 fold-back cassette + b2 SN-2549 in a frame with strip feeder, box gripper, blade stop | Theirs: every position the hand needs is a seat or detent, the flush cut sets strip length. Mine: the contact never touched by hand, the $21 tool, the captive click. The person folds a conductor forward, slides, taps a pedal | SN-2549 crimp quality on this wire; person time per crimp (~10–15 s estimate) |
| C4 | a2 docked cassette | b3 C-frame head on a cheap gantry | Theirs: no captive contact, no axial slide-in. Mine: a head that fits between contacts at 7 mm, force closed in 1 kg | Harvested die alignment at ±0.02 mm; tab Z window (Break a2-1) |
| C5 | a3 backshell as clamp, datum and label | b4 laser split and score from the backshell face; b1 fold-back over it | Theirs: the part that ships and the recipe code. Mine: the split root is exactly the backshell face, so fold-back parking at 8–15 mm; backshell top 30–37 mm above the board [calc X §7] | Silicone under 455 nm; web tear at the root; Derek adding a part |
| C6 | a2b gang stroke | b1b sensing | Theirs: one stroke per ribbon, height by stop blocks. Mine: a load cell under the shoe catching a missing wire or contact (12–20 % for 5) [calc X §11] | N matched dies |

---

## Where their work changes my own ideas (for my revision)

1. **Under-width channel and a centred datum in my cassette** (AMP US
   4,230,008).
   - From a centred datum a 5P's worst conductor is 0.23 mm off, against b1's
     assumed ±0.4 mm [calc R §1].
   - b1's fork can take conductors blind, with the camera confirming rather
     than locating.
2. **A flush-cut guillotine in the cassette.** It removes b4's hand step of
   trimming tips square. That step was b4's main person-time item besides
   loading.
3. **Copper takes set below R ≈ 67 mm** [calc R §4]. Fold-back parking bends
   each root about R 2 mm, at 2 % strain per reversal. That is three to four
   reversals: park, lay forward, park crimped, lay forward to insert.
   - Fatigue is not the concern at that count [estimate]. The shape is.
   - b1's insertion extension must straighten each root in a comb (a5 F1, a6's
     grooved clamp), not trust the fork.
4. **Feed timing (Break a1-3) is in b1.** With a bought fast press, b1's
   cassette backs off only after the feed has run. b1 needs a compliant
   cassette mount, or it needs b1b's crank to stop between crimp and feed.
5. **The factory wire hold spring.** If the OTP applicator has the MKS-L's
   slot, b1's servo presser foot may be a bought spring. It still needs a flat
   sole of at least 3 mm (Break a1-1 applies to my foot too).
6. **Docking plus the applicator's strip-pitch clearance** makes C1 a branch of
   my b1b family. It removes the fork and the fold-back entirely, at the price
   of a 21–30 mm parting.
7. **The far-end pogo port** (a6) gives b1 a pre-fire check: each conductor
   reads continuous to the grounded applicator before the relay fires, and a
   strand-contact event during lay-in. The camera and pull stay.
8. **a3's backshell** could be b1's cassette clamp, left on the loom.

## Measurements that settle most of the above

- **Hand-cycle the applicator when it arrives.** Note the ram height at which
  the feed finger starts to move. This settles a1-3, b1 and C1's indexing.
- **Scan the applicator's wire-entry face and upstream side** with the
  Revopoint MINI 2. The scan settles:
  - a1's h;
  - the sole's room;
  - the crimper tongue width (C2, a1 at 5 mm);
  - b1's split length;
  - which parts must go for C1.
- **The $4.71 strip** (already on every list). Add the tab's width and
  thickness to the list; they set a2's Z window [calc X §5].
