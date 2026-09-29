# borrowed-machines on machine-that-sees-and-learns (wave 3)

The reader's view: somebody already mass-produces most of this, for another
purpose. The subject's view: the first stage of a cell is one software can
move and observe. This file pairs the two, breaks what the borrowing view can
break in their ideas as they stand after wave 2 (v8, v1b and v7 new; v1, v2,
v3, v4, v4b, v5 and v6 revised), checks their numbers, and lists what crosses
in each direction.

ribbon-as-pallet's wave-2 critique
([`ribbon-as-pallet--on--machine-that-sees-and-learns.md`](ribbon-as-pallet--on--machine-that-sees-and-learns.md))
already covers these, and they are not repeated here:
- neighbours in the side silhouette, and the piano keys;
- what sits behind the box (lance, brush, neck) and the lance-notched plate;
- the capstan grip and the soldered lug;
- roll read as height, and the roll flat;
- the rear-face-up housing and insertion along the wire axis;
- the scalpel on a free ribbon and the under-width channel with ribs;
- printed kinematic flanks under a magnet.

terminal-supply's wave-3 critique of this explorer
([`terminal-supply--on--borrowed-machines-w3.md`](terminal-supply--on--borrowed-machines-w3.md))
found that b1's catch plate has no width window and that b1c's gate has no safe
exit. Both bear on the combination below and are cited, not re-derived.

**Citations.**
- **[calc W §n]**: this exchange's numbers,
  [`../explorers/borrowed-machines/calc/exchange_sees_learns_w3.py`](../explorers/borrowed-machines/calc/exchange_sees_learns_w3.py),
  with output
  [`exchange_sees_learns_w3.out.txt`](../explorers/borrowed-machines/calc/exchange_sees_learns_w3.out.txt).
- **[calc B …]**: my earlier calcs in
  [`../explorers/borrowed-machines/calc/`](../explorers/borrowed-machines/calc/)
  (`presses`, `wave2`, `exchange_ribbon_as_pallet` as [calc X §n]).
- **[SL file §n]**: their calcs in
  [`../explorers/machine-that-sees-and-learns/calc/`](../explorers/machine-that-sees-and-learns/calc/).
- **[RP calc P §n]**: ribbon-as-pallet's
  [`exchange_on_machine_that_sees.out.txt`](../explorers/ribbon-as-pallet/calc/exchange_on_machine_that_sees.out.txt).
- **[Prime]**: a row in [`../sourcing/amazon-prime.md`](../sourcing/amazon-prime.md),
  observed 2026-09-28.

Axis words: "along the wire" and "across". b1's shuttle calls these X and Y;
v1 calls them Y and X.

---

## 1. Combinations

### A. The tack at the anvil: v8's watched tack made inside b1b's stopped crank applicator, on a contact still on its carrier

**What each side brings.**
- **v8** ([tack, look, then crimp](../explorers/machine-that-sees-and-learns/ideas/v8-tack-look-crimp.md)):
  - a loose tack of the insulation wings by a 1.2–1.5 mm steel former on a
    servo lever to a screw stop, with a load cell in the link;
  - the straight-down look into the open conductor barrel, placed between a
    cheap irreversible act (the tack) and the dear one (the conductor crimp);
  - a back-out after the tack that costs a contact, not a ribbon end.
- **v7** ([the run](../explorers/machine-that-sees-and-learns/ideas/v7-the-run.md)):
  - the MCU runs every stroke to a crawl, against a force envelope;
  - the runner, the journal, the three bands and the ask queue.
- **v5**: the after-crimp silhouette with the box as its own roll gauge.
- **b1b** ([applicator in a slow crank](../explorers/borrowed-machines/ideas/b1b-applicator-in-slow-crank-press.md)):
  - a bought OTP side-feed XH applicator in **pre-feed**, so a contact waits on
    the anvil at rest, still on its carrier;
  - a 15 mm crank on the idle 12-ton shop-press frame, with a disc stack in the
    rod and a dwell after bottom dead centre.
- **b1**: the cassette with its folded band, the valley-tine fork, the foot and
  the far-end pogo block.

**What the pairing does that neither does alone.**
- v8 has **two stations and two datums**. It carries a flagged contact from T
  to C, needs a keyed box slot at C, and needs a drop-shear for strip. Its
  back-out needs a rear shoulder in the undimensioned neck.
- Here T and C are **the same anvil**. The applicator's own strip track,
  terminal stop and feed finger locate the contact for the tack, the look, the
  crimp and the tab shear.
- b1b and b1c have to hold the conductor with a fork and a foot until the
  crimpers arrive. My wave-2 calc shows no compliant holder has a force window
  [calc B wave2 §1], so the holders have to leave by timing. b1c's 180° fork
  swing therefore races the descending ram. And b1b's gate picture is oblique,
  under a raised punch.
- Here the tack is the holder:
  - fork and foot leave before the crank turns at all;
  - the gate looks straight down through a swing-in mirror;
  - a failed look backs the conductor out with the contact still held by its
    carrier.

#### Picture it

**Where things start.**
- b1b as it stands:
  - the applicator in pre-feed on the VEVOR frame, the crank at top dead centre;
  - the contact waiting on the anvil on its carrier, wings open.
- The cassette on b1's two-rail shuttle in front. The end is split, stripped
  and folded back as one flat band. The far end is in a pogo block, and the
  applicator body is grounded.
- Two swing-in units, bolted by dowel pins to the applicator base on the
  downstream side, where only spent carrier leaves:
  - **T-arm.** A short vertical guide with the former plate in it. The
    profile is cut to the applicator's own insulation crimper, from a
    Revopoint scan in the jack test [b1b stage 0]. A lever from a DS3235
    35 kg·cm servo ($27.99 [Prime]) drives it, a screw stop sets the tack
    height, and a 5–10 kg bar load cell with an HX711 ($9.99 [Prime]) sits
    in the link.
  - **M-arm.** A 10 mm first-surface mirror at 45° (cut from the
    100 × 100 mm plate, $20.90 [Prime]) with 4–8 LEDs round its opening. The
    16 MP IMX298 M12 module ($69.99 [Prime]) with a 12 mm lens ($9.99
    [Prime]) looks in horizontally.
- A second camera looks across at wing height from the downstream side, with
  RP's thin diffuser vane standing between the active contact and the next one
  upstream.

**One conductor.**
1. **Lay in.** The shuttle indexes across. The tines drop into the valleys
   either side of conductor *i*, and the fork lays it forward into the waiting
   contact. The foot seats the jacket in the insulation barrel. With the crank
   at top dead centre, nothing hangs within ~23–31 mm of the anvil on a 30 mm
   stroke [calc W §3; estimate].
2. **Side look and continuity.** Far-end channel *i* to the applicator reads
   closed: the strands touch the contact, and it is the conductor the recipe
   expects.
3. **Tack.**
   - The T-arm swings in to its dowel stop.
   - The former descends at ~1 mm/s to its screw stop and closes the
     insulation wings loosely on the jacket, at 33–132 N into the applicator's
     own hardened insulation anvil. The forming curve is logged.
   - The T-arm rises and swings out. The former plate reaches ~14 mm up and
     its guide ~17 mm [calc W §3].
4. **Let go.** The foot lifts, and the fork opens and parks. The tack alone now
   holds the conductor:
   - **vertically,** by capture: the wings are closed over the jacket;
   - **along the wire,** by 0.2–1.5 N of grip, against tens of mN of copper
     spring-back from the lay-in bend [calc B wave2 §1].
5. **Top look.** The M-arm swings in. Its mirror spans ~4–11 mm above the
   floor [calc W §3]. The LEDs light one at a time, and the second camera
   looks across. The judge checks:
   - strands between the wing tips;
   - nothing silver on the anvil outside the outline;
   - brush length;
   - the insulation edge in the window;
   - the bundle's own shadow (below).
6. **Decide.**
   - **Pass.** The M-arm swings out. The MCU turns the crank fast to a taught
     angle 0.95–1.7 mm above bottom, then crawls at 0.05–0.1 mm/s on a speed
     profile [calc W §5], with force against shaft angle checked every
     sample. At bottom dead centre both barrels are crimped, the insulation
     crimper re-forms the tack, and the tab is sheared.
   - **Fail.** The shuttle draws the conductor straight back along its axis
     through the tack. The carrier holds the box: a 0.4–1.5 N release
     against a tab that bends only at 4–12 N of axial pull [calc W §4;
     RP calc P §3]. The draw has to stay flat, because the tab yields at only
     0.5–1.7 N of *vertical* load [calc X §5].
     - The empty tacked contact is crimped empty on the next turn, which
       matches the "contact, no wire" reference envelope.
     - It is blown off the anvil in the dwell, terminal-supply's K2 blow-off
       (TAILONZ 24 V 5/2, $16.99 [Prime]; compressor on hand [repo]).
     - A fresh contact feeds in. A look at the conductor's insulation edge
       decides whether to retry it or re-strip it.
7. **Dwell,** 40–100° after bottom dead centre:
   - the shuttle withdraws the crimp ≥7 mm;
   - a thin fork in the neck bears on the box's rear face, above the floor
     (terminal-supply's repair of b1's catch plate);
   - 20 N proof pull through the cassette's load cell;
   - backlit silhouette at the fork, with the box's front 1 mm read as a roll
     gauge (v5).
8. **Finish the turn.** The crank completes its revolution and the pre-feed
   advances a fresh contact onto the empty anvil. The fork parks the crimp in
   the band, and the shuttle indexes.

**What locates what.** The reference for "fixed" is the applicator base
throughout.

| Moment | Contact | Conductor |
|---|---|---|
| Lay-in | The applicator's strip track, terminal stop and feed finger | Tines across; cassette datum and shuttle along the wire |
| Tack | The same, with the insulation barrel on the hardened insulation anvil | Fork and foot, until the tack closes |
| Look | The same | The tack |
| Crimp | The same | The tack and the contact |
| Pull | The neck fork on the box's rear face | The cassette clamp |

The former's guide is doweled to the applicator base, so it lines up with the
insulation crimper that finishes the tack. Its screw stop sets only the tack
height, which is loose on purpose: ±0.05–0.1 mm is enough.

**What drives the crimp and carries its force.**
- **The crimp:** b1b's crank, 0.8–2.6 kN through the rod's 4 kN-preload disc
  stack and the 12-ton frame.
- **Drive:** NEMA 23 plus a 10:1 planetary (StepperOnline $48 [Prime]), or a
  30:1 worm (Heechoo, $120 [Prime]) that self-locks at every stop.
- **The tack:** 33–132 N from the servo, reacting through the applicator's
  anvil.
- The shuttle, the fork and the arms carry a few newtons at most.

**How it knows.** Each check, in order:
- continuity at lay-in;
- the forming curve at the tack (no jacket, or the jacket off centre);
- the top look and the side look;
- force against crank angle through the crawl;
- the stack switch;
- in the dwell: silhouette height corrected for roll, the 20 N pull, and
  continuity through the crimp.

**What the person does.** As b1b:
- cuts the ribbon and loads the cassette;
- docks it at the prep station and closes the fold lid;
- changes reels;
- inserts by hand, or keeps b1's insertion extension stocked;
- answers v7's asks;
- checks crimp height by micrometer on samples, until the silhouette is
  trusted.

That is ~27 attended minutes a unit with hand insertion [calc B wave2 §5].
The machine takes 72–142 s a conductor, 1.1–2.1 h a unit [calc W §11].

#### Numbers that decide it

- **Room.** A 30–40 mm stroke leaves ~23–42 mm under the raised crimper faces,
  depending on what hangs below them [calc W §3]. The former and its guide need
  ~17 mm, and the mirror ~11 mm.
- **On b1c's shaft the same room exists only near top dead centre** [calc W §14]:
  - 0°: ~30.8 mm; 40°: 26.8 mm; 90°: 14.7 mm; b1c's gate at 115°: 8.5 mm.
  - So on b1c, lay-in, tack and look move to a stop at 0–40°. That is
    terminal-supply's repair (b) ("gate before the band") with a physical
    reason added.
  - The back-out at that stop needs the along-wire withdraw on its own servo,
    not on cam 4, or terminal-supply's latched followers.
- **What the second stroke meets first.** After a tack, the insulation crimper
  meets the tacked barrel with +0.20 to +0.70 mm of stroke left. The
  conductor wings are met at 0.62–0.87 mm [calc W §1]. So the conductor wings
  are touched first, the reverse of an untacked stroke.
  - What stays true is v8's substance: the jacket is gripped before
    compaction.
  - The sectioning that v8 already names (force-and-form f3b) is where it
    shows.
- **The bundle is off the floor.** Held by its jacket, the gathered 0.72 mm
  bundle hovers **0.30–0.52 mm above the conductor-barrel floor**, with its
  top 0.98–1.25 mm up, against wing tips at 1.50–1.60 mm [calc W §2; the
  insulation and conductor floors are assumed to share one plane, as the
  clone drawings show].
  - A strand lying on the floor has left the bundle.
  - Two focus slices cannot separate it: depth of field at 86–122 px/mm is
    ~0.55–1.5 mm [calc W §2, estimate].
  - A **displaced shadow** does. LEDs at 60–75° elevation, the lowest that
    reach the floor past the walls (53–66°), throw the bundle's shadow
    0.08–0.30 mm aside. That is 7–26 px at 86 px/mm and 10–36 px at
    122 px/mm. A strand on the floor casts none.
  - This is v8's unresolved "strand flat against the barrel floor", turned
    into a shadow test.

#### What stays uncertain

- **Room at top dead centre.** What hangs below the OTP crimper faces:
  hold-down, terminal stripper, wire-hold-spring slot. The MKS-L manual shows
  a terminal stripper and a pressure-plate assembly [MKS-L manual pp. 9, 20, via my
  [wave-2 exchange](borrowed-machines--on--ribbon-as-pallet.md)]. The jack test measures it.
- **The former's profile and alignment.** Doweling a guide to the applicator
  base modifies a bought tool. The profile is taken from a scan of the
  crimper.
- **The tack on this silicone.** v8's pliers-and-scale test settles it.
- **The tack height.** It is set against the final insulation height at the
  same width, from v3's tack arm, not as an absolute figure (§3, row 1).
- **Blow-off.** Whether a 0.043 g crimped empty leaves the anvil every time.
- **Pre-feed only.** On b1's fast mute press with post-feed, the anvil is empty
  at rest, so there is nothing to tack. A belongs to b1b and b1c.

#### Branches

- **A1, on b1c's one shaft.** The shaft stops at 0–40° for lay-in, tack and
  look. The tack and mirror arms run on their own servos, and the cams keep
  the crimp, withdraw, pull and park. The fork's 20–80° swing under a
  descending ram disappears from b1c's problem list.
- **A0, by hand in the first week.** The jack test plus a former on a POWERTEC
  305CM push-pull toggle ($18.25 a pair [Prime]) plus the ELP over a hand-held
  mirror:
  - Derek lays the conductor in by hand;
  - throws the toggle for the tack;
  - looks, then pumps the jack.

  It answers the tack's grip, the order question by section, and the room
  question on the real applicator before anything is motorised. It is useful
  on its own as a crimper where the contact no longer has to be juggled.

### Other combinations, named more briefly

- **B. v3's campaign on the jack test, then on the crank as its own gauge.**
  - **Week one.** b1b's jack test is v3's campaign press with no settable stop:
    - an indicator from the applicator's ram to its base, read at a 10 N
      re-touch, takes up every internal clearance in the loading direction;
    - coupons come off the production reel through the production feed;
    - v5's booth does the pulls. The tab is sheared in the stroke, so pulls
      react on a neck fork, not the tab.
    - A hand pump's travel per stroke is coarse near bottom [estimate], so the
      knob is the stop collar and a shim stack (ribbon-as-pallet a2b's
      stack), not the pump.
  - **On the crank.** Stopped short of bottom dead centre, the crank moves the
    ram 0.16–0.51 µm per microstep through 10:1, and 0.05–0.17 µm through 30:1,
    over the last 0.02–0.2 mm [calc W §6].
    - Holding 3 kN at 0.1 mm takes 6.5 N·m at the crank, which the worm holds
      unpowered.
    - A 10 N re-touch read by a 14-bit shaft encoder gives 0.2–0.5 µm of
      height per count near the re-touch point (AS5600 12-bit: 0.9–2.0 µm).
      So the crank is its own crimp-height gauge once throw, rod and bottom
      dead centre are calibrated against one gauge block.
    - Production then runs at bottom dead centre, with the rod-end thread set
      to the campaign's height.
  - **Uncertain.** With both crimpers on one ram, a re-touch reads whichever
    barrel springs back higher. An indicator across the dies has the same
    ambiguity.
- **C. v7 hosting b1b, b1c and b8 on stack C, with force and angle streamed.**
  - Klipper's API server has `load_cell/dump_force` ("to subscribe to force
    data produced by a load_cell") and `angle/dump_angle` subscriptions over
    its Unix socket [source: klipper3d.org/API_Server.html, fetched
    2026-09-28]. This answers v7's open question.
  - Klipper's `[load_cell]` also takes CS1237, ADS1220 and ADS131M0x besides
    the HX711 and HX717 [source: klipper3d.org/Config_Reference.html,
    fetched 2026-09-28].
  - The runner then gets force against crank angle as one stream, and a
    load-cell probe's `trigger_force` halts the crank's move [SL v7, source].
  - b1c's switch cams become the runner's gates. The worm's self-locking makes
    shaft angle plus journal the whole machine state after a power loss.
  - Which angle chips Klipper reads is not confirmed here [assumption: SPI
    parts such as the AS5047 class, and not the I²C AS5600].
  - For b8's long spool runs, the slip ring is v1's electrical channel and the
    rip-force trace is one more envelope.
- **D. v1b turned over: b3's head on the carriage, the fan block on the bed.**
  - [b3](../explorers/borrowed-machines/ideas/b3-gantry-carries-the-crimp-head.md)'s
    ~1 kg head closes its crimp force inside its own laser-cut C-frame, so the
    carriage and belts carry none of it. That is v1b's "press rides the bed"
    problem with the heavy object moved to the axis made for a tool head.
  - v1's fan block and keys ride the bed, and v1's cameras mount on the head's
    frame, so camera-to-anvil never changes.
  - Open problems:
    - the head's punch at the neighbours' height must be narrower than ~8 mm,
      as in v1;
    - the C-frame's throat must reach past a 5P fan at 5 mm pitch (±10 mm);
    - b3's harvested punches and its C-frame stiffness at low mass.
- **E. v8's T feeding b2's SN-2549 on edge, loaded box-first along the wire.**
  - The tacked contact enters the open jaws from the wire side and travels
    box-first to a front stop. The lance trails, so it slides over the die
    edges in its folding direction.
  - This uses b2's actuator, spring link and axial path in place of f9's
    "nest from above".
  - It does not save jaw opening: box plus lance (2.8–3.3 mm) is what either
    direction must pass.
- **F. v4b's pocket plate as b3's supply for kit contacts,** in place of an
  SMT-style strip feeder that only takes strip.

---

## 2. What still breaks in their revised and new ideas

### v8 (new)

**B-v8-1. The tack height is given as an absolute figure that their own wave-3
calc can put below the final crimp.**
- **Conflict.** v8 estimates the tack at ~2.3–2.5 mm, "somewhat taller" than
  force-and-form's 2.0–2.3 mm final insulation crimp. Their own
  [`w3_on_hand_tool_as_press.out.txt`](../explorers/machine-that-sees-and-learns/calc/w3_on_hand_tool_as_press.out.txt)
  §9 puts the closed height on this silicone at **2.03–2.46 mm** for W
  1.80–1.95 with no silicone flow.
- **Consequence.** Against those heights the tacked barrel meets the final
  crimper at −0.16 to +0.47 mm [calc W §1]. At W 1.80 a 2.3 mm "tack" is
  tighter than the final crimp. That is a crimp, not a tack. The final die
  then does not finish it: it meets a barrel already smaller than the die, and
  the grip window (0.2–1.5 N) is exceeded.
- **Repair.** Define the tack as a height above the final insulation height at
  the same profile width. v3's tack arm ("tack heights in 0.05 mm steps above
  the final insulation height") already does this. The former is then cut to
  the final crimper's width.
- **Uncertain.** The final height on this silicone, until sections exist.

**B-v8-2. "The tack is the first part of an ordinary stroke" holds for the
untacked stroke, not for the one after the tack.** [calc W §1]:
- Untacked, the insulation wings are met with 0.65–1.40 mm left and the
  conductor wings at 0.62–0.87 mm. The insulation is met first, as v8 says.
- After a 2.3–2.5 mm tack, the insulation crimper meets the tacked barrel with
  +0.20–0.70 mm left, so the conductor wings are met first.
- **Consequence.** In both cases the jacket is held before compaction, the
  last 0.1–0.2 mm. What differs is the wing curl: after a tack the conductor
  wings curl for up to ~0.67 mm of stroke before the insulation crimper
  touches, while in an untacked stroke the insulation wings are already being
  formed during that curl.
- **Uncertain.** Whether that difference shows in the finished crimp at all.
  f3b's sections show it.

**B-v8-3. The top look's "two focus depths" cannot do what v8 hopes; a shadow
can.**
- **The numbers** are in Combination A above [calc W §2]:
  - the bundle hovers 0.30–0.52 mm off the floor;
  - depth of field is ~0.55–0.76 mm at 122 px/mm and ~1.1–1.5 mm at 86 px/mm;
  - near-vertical LEDs at 60–75° displace the bundle's shadow by
    0.08–0.30 mm (10–36 px at 122 px/mm).
- **What changes.**
  - The photometric states should include at least two LEDs on opposite sides
    at 60–75°.
  - The judge looks for silver with no displaced shadow: a strand on the
    floor.
- **Uncertain.** Whether tinned strands on a tin floor give a shadow edge the
  fit can find. One photograph of a tacked conductor settles it.

**B-v8-4. With C as b1b (v8's own host list via v1), C has no box slot.** An
applicator locates a contact by strip track, terminal stop and feed finger.
- A drop-sheared, tacked loose contact lowered onto an applicator anvil has
  nothing to locate it along the wire.
- The side-feed track beside the anvil (pressure plate upstream, scrap cover
  on the wire side [MKS-L manual pp. 9, 20, via my
  [wave-2 exchange](borrowed-machines--on--ribbon-as-pallet.md)]) leaves no place to add a
  keyed slot without rebuilding the anvil block.
- **Repair.** Combination A: tack on the carrier at the applicator's own anvil,
  so C is the same place.

### v1 (revised) and its press candidates

**B-v1-1. v1 names b1b as a candidate press, and four of v1's asks do not
carry to an applicator.**
- **Load cell under the anvil.** The anvil is the applicator's hardened block
  inside its base. The force path in b1b is strain gauges on the connecting
  rod.
- **The nest by supply form** (strip, v4b plate, tweezers). An applicator takes
  strip only.
- **Neighbours lifted 5 mm.**
  - Upstream of the anvil, the side-feed strip runs under a spring pressure
    plate that extends several centimetres at strip height. The wire-entry
    side carries the shear blade supporter and scrap cover [MKS-L manual
    pp. 9, 20, via my [wave-2 exchange](borrowed-machines--on--ribbon-as-pallet.md)].
  - A 5P fan at 5 mm pitch puts neighbours ±5–10 mm across, over exactly
    those parts, with their undersides at 4.15 mm.
  - Whether the pressure-plate assembly and its wing bolt stay under 4 mm is
    unmeasured [assumption].
  - My earlier calc found that an applicator's function guarantees narrow
    tooling only for neighbours one strip pitch (6.8–9.5 mm) away, not at
    5 mm [calc X §4].
- **The silhouette window beside the nest.** Upstream is live strip, and
  downstream is spent carrier and the shear.
- **Repair.**
  - b1's fold-back band, or C2 of my wave-2 exchange ("crimp upstream-first,
    park after", with nothing ever upstream).
  - Strain gauges on the rod in place of the anvil load cell.
  - The silhouette moved to the dwell's withdraw position, outside the
    applicator.
  - Or Combination A, which keeps v1's look and drops the keys.
- **Uncertain.** The OTP unit's upstream geometry, seen in the jack test.

### v1b (new)

**B-v1b-1. Nothing gives the pallet its along-wire axis when the press cannot
ride the bed.**
- **Conflict.**
  - On a bed-slinger the bed has only Y. The carriage has X and the gantry Z.
  - v1b's "turn it around" branch takes Y from "a small slide under the press".
  - That works for a 3–6 kg press. It cannot work for b1b's shop-press frame,
    b1's 38–55 kg mute press, or the idle 12-ton press v3 names for a2b's
    stop blocks.
  - The axis lost is the one v1 needs per conductor: insulation edge in the
    window, ±0.1–0.3 mm scatter [SL wave2 §2], and the proof pull.
- **Repairs.**
  - **The Ender on its back.** The carriage stays X. The gantry's Z lead
    screws now run along the wire, and the bed axis becomes vertical and
    unused. The key height is set once. A 20 N proof pull on a Tr8 lead screw
    needs 0.02–0.09 N·m at the motor, against 0.13 N·m on the bed's GT2
    belt [calc W §7]. The Ender 3 V3 SE is Prime at $219 or $186.14
    [Prime].
  - **b1's two MGN12 rails** (along and across) bolted in front of the press.
  - **Combination D.**
- **Uncertain.** An Ender frame's stiffness lying on its back, and its stock
  firmware homing a gravity-free Z [assumption].

### v7 (new)

**B-v7-1. Hosting a crank (v7's own table row for b1b) needs a speed profile,
not "one revolution".**
- **At constant turning** [calc W §5], at 30 s a revolution:
  - the ram passes 0.3 mm above bottom at 0.67 mm/s and 0.1 mm at 0.39 mm/s;
  - one HX711 sample is 4.9–8.4 µm of travel there: 194–837 N into a
    40–100 kN/mm obstruction loop;
  - at 10 s a revolution it is 15–25 µm and 0.6–2.5 kN.
- **Repair.** The MCU profiles the stepper so the ram crawls at 0.05–0.1 mm/s
  from a taught *angle*:
  - 9–34 s from 0.95–1.7 mm;
  - 582 microsteps/s at 0.05 mm above bottom through 30:1 is well inside a
    DM542T's range.
- **What changes.** A doubled contact, met ~0.2 mm early, is caught at the
  envelope's excess plus one sample: ~200–212 N with an HX711 at a profiled
  crawl, 242–367 N at constant 30 s turning [calc W §5; the 200 N band is an
  estimate]. The 4 kN disc stack stays as the ceiling if the MCU is wrong.
- **Uncertain.** How tight the band can be through wing curl, which v3's
  reference strokes set.

**B-v7-2. The force limit lives only in firmware.**
- **Conflict.** Every stack in v7 puts the limit in an MCU: its envelope, a
  probe line, or Klipper's `force_safety_limit`. "Stop-on-fault" assumes the
  firmware notices.
  - A wrong taught height, a wrong envelope after a threshold change, or a
    stuck HX711 reading zero lets the MCU crawl on into a steel stop at the
    drive's full thrust.
  - That is ~1.4 kN on a NEMA 23 and Tr8×2 screw, ~4–10 kN through ball
    screws [xh-facts §4], and 8–10 kN at a crank's bottom dead centre
    [calc B presses; procedure calc §3].
- **Repair: a steel ceiling in series with any drive.**
  - A disc stack preloaded above the crimp peak, whose travel trips a switch
    wired into the same enable line as v7's e-stop and lid switch (b1b).
  - Or, for a hand-tool host, b2's spring link at ~1.25× the handle need.
  - The ceiling then holds whatever the firmware believes. v7's hosting table
    (a1 squeezer, f3 knee, b1b crank) each gains one line.
- **Uncertain.** Disc springs sized for ~4 kN. The Prime Belleville
  assortment is stainless and light duty [Prime], so DIN 2093 parts come from
  elsewhere.

**B-v7-3. Two of v7's open items have answers.**
- **Klipper streaming.** `load_cell/dump_force` exists (Combination C).
- **Frame rate.** The Prime row for an IMX298 M12 module, the ELP's sensor,
  lists MJPEG 4656 × 3496 at 10 fps and 2048 × 1536 at 30 fps [Prime]. v7's
  10 fps rows apply: 8 lighting states in 2.6–4.2 s [SL wave2 §4].
  - The ELP board itself is not confirmed.

### v4 (revised)

**B-v4-1. A nozzle on "a few tenths of a newton" cannot level a barrels-up
contact that rests on its lance.**
- **Conflict.** v4 now says the sprung nozzle "levels the tilted box by
  flexing the lance elastically".
- **Numbers.** As a plain cantilever (length 1.5–2.5 mm, width 0.5–0.8 mm,
  0.20 mm stock, all assumptions), the lance is **7–52 N/mm** stiff
  [calc W §13]:
  - pressing it flat (0.6–0.9 mm) takes 4–47 N;
  - a 0.2–0.5 N spring moves its tip 0.003–0.1 mm.
  - As a plain cantilever it would pass first yield after 0.03–0.12 mm of tip
    travel. Real lances survive insertion, so they are longer or shaped
    differently than this model. Even at three times the softest row's
    compliance, levelling takes ~1.5–2 N.
- **Consequence.** The nozzle lands on a box top tilted 11–17°. A flat rigid
  nozzle leaks there. The Juki 503 tungsten nozzle on the Prime list is
  rigid [Prime].
  - Pressing harder to level the contact is the lance-bending v4 wants to
    avoid.
- **Repairs.**
  - A soft bellows cup of 2–3 mm, as pick-and-place machines use for uneven
    tops (Wave 3 sourcing request).
  - A nozzle face cut at the tilt, with the heading from the picture.
  - Or pick only from v4b's lance-relieved pockets, where the contact already
    lies flat.
- **Uncertain.** The lance's real stiffness. Press one kit contact barrels-up
  against the 0.1 g scale with a probe on the box top.

### v6 (revised)

**B-v6-1. Which way the ribbon is drawn under the split blade decides whether
the free length is in tension.**
- **Conflict.** "The stage draws the ribbon 25–35 mm under a fixed blade that
  scores down onto a rib." The direction is not stated.
- **Numbers.** If the blade enters at the tip and runs toward the clamp, the
  free length between clamp and blade is in compression. A 5P held down at the
  blade buckles at **1.1–2.2 N** over 25–35 mm [calc W §9, from calc B wave2
  §2]. The drag is 0.2–3 N for one web and 0.8–12 N for four [calc B wave2
  §2, estimate].
- **Consequence.** Unless a lid guides it, the ribbon bows up out of the
  channel, the web lifts off its rib, and the score wanders or the ribbon
  sets. The root lands wherever the tear runs ahead of the blade: 0.6–2 mm
  past where the stage stopped [calc B wave2 §2].
- **Repair (b6's rule).**
  - Plunge the blade at the root, just ahead of the clamp face, onto the rib.
  - Draw the pallet so the blade runs out at the tip.
  - The free length is then in tension, the root is where the blade went in,
    and any tear runs only toward the tip, where the split goes anyway.
- **Uncertain.** Whether a blade plunged onto a rib pierces the web cleanly
  (repo Open item 5, the neck).

**B-v6-2. The strip blades are unnamed, and the geometry decides the nick.**
From my wave-2 calc [calc B wave2 §3]:
- two 90° V-blades set to part this silicone cut to within 0.02 mm of the
  strands at four points while leaving 0.35 mm of wall at four others;
- die-hole blades at 0.94 mm leave an even 0.04–0.19 mm ring;
- a single orbiting blade needs the bundle centred to ±0.05 mm.

v6's "blades cut shallow and the stage pulls the slug" needs die-hole or
centred rotary blades. A twist during the slug pull (0.1–1.2 N·mm needed,
2.5–15 available) shears the ring and lays the strands, which folds v6's
separate twist step into the pull.

**B-v6-3. Crossing insertion.** For v6's per-conductor tweezer route, b1's
order rule applies: the crossing conductor goes into its cavity **last**, so it
lies on top of conductors already tethered in the plane. The recipe carries an
insertion order separate from the crimp order.

### v3, v5, v2

- **v3 on an applicator:** see Combination B. The tab is sheared at bottom
  dead centre, so v3's "carrier tab in compression to 72–96 N" reaction needs
  the shear punch taken out for campaign crimps. Pulls on sheared coupons need
  a neck fork.
- **v5:** nothing breaks. Its box roll gauge crosses into my b1b (§4).
- **v2:** consistency only (§3).

---

## 3. Consistency

| # | Their file and number | Disagrees with | Which holds |
|---|---|---|---|
| 1 | v8: tack ~2.3–2.5 mm, "somewhat taller" than the final 2.0–2.3 | Their own `w3_on_hand_tool_as_press.out.txt` §9: closed height 2.03–2.46 mm at W 1.80–1.95 | Both are estimates. The tack must be defined relative to the final height at the same width (B-v8-1) [calc W §1] |
| 2 | v8: "a tack, then the full stroke, is that order with a pause in it" ([SL wave2 §5]) | Same calc's inputs, applied to the stroke after the tack: insulation met at +0.20–0.70 mm, conductor at 0.62–0.87 mm | The first-touch order reverses; the "jacket held before compaction" part holds [calc W §1] |
| 3 | v8: "per 53-crimp unit ~1–2 h" | Its own parts: tack 29–81 s + C 40–80 s = 69–161 s a crimp, **1.0–2.4 h** | The parts [calc W §12] |
| 4 | `cycle_and_cost` §1: press "crimp 1 mm @0.05–0.1 mm/s" (10–20 s) | v7's rule (crawl from ≥0.3 mm above first wing touch) with [SL wave2 §5]'s first touch at 0.65–1.40 mm: 0.95–1.7 mm, 9–34 s | v7's rule; the press line is up to 14 s short a crimp, ~12 min a unit [calc W §10] |
| 5 | v2: "about 6 mm RSS of tip wander from backlash", attributed to me | My [`cycle_and_arm.out.txt`](../explorers/borrowed-machines/calc/cycle_and_arm.out.txt) §2: 6.0 mm RSS when approaches vary; **1.2 mm RSS (2.2 mm worst)** when every dock is approached the same way | Both are mine, under different conditions. v2's ≥5 mm funnels work either way. The same-direction figure is the one taught waypoints give |
| 6 | v1: punch body under ~8 mm at the neighbours' height "matches borrowed-machines' tongue limit" | My [calc X §4]: that is a *requirement* at 5 mm pitch. An applicator's function only guarantees tooling ≤10.8–11.3 mm at the wings for a 7.1 mm strip pitch | Requirement and property differ; the OTP tooling width is unmeasured |
| 7 | v4: the sprung nozzle levels the contact "by flexing the lance elastically"; RP's exchange: "elastically at nozzle forces under a newton" | [calc W §13]: 7–52 N/mm as a cantilever; a few tenths of a newton moves the tip ≤0.1 mm | Nothing levels at those forces. The pick must seal on a tilted top (B-v4-1) |
| 8 | terminal-supply's w3 on me: the box roof stands 0.4–0.6 mm proud of a ~1.8 mm insulation crimp, so a plate ~2.0 mm up can bear on the roof | [SL w3 §9] 2.03–2.46 mm and force-and-form 2.0–2.3 mm for this silicone; box 2.2–2.4 mm | On silicone the height margin is −0.26 to +0.37 mm [calc W §8]. The 1.8 mm figure is KONNRA's for PVC wire. terminal-supply's other repair, the neck fork, holds |
| 9 | `cycle_and_cost` §3: cache reads "$0.20/MTok on Opus 5.5 / Sonnet 5.5" | `wave2.py` §7: Opus input $4/MTok at 0.1× for cache reads, i.e. $0.40 | Internal to their files; I did not re-read the price table. Effect: cents per unit |
| 10 | v8 and v1: fresh strip contacts wait "at ~7.1 mm" | xh-facts §1: pitch not dimensioned, clone drawings 7–9.5 mm [estimate]; 7.1 is Würth's analog (digest) | Carry 7.1–9.5 until the $4.71 strip is measured. RP's diffuser vane gap (4.1–4.6 mm at 7.1) only widens |
| 11 | v7: ELP MJPG frame rate at full resolution unmeasured | [Prime] IMX298 M12 module: 4656 × 3496 MJPEG at 10 fps | Same sensor, listed rate; the ELP board is not confirmed |
| 12 | v1b: Ender 3 V3 SE $199 (Creality store) | [Prime] $219 (2,112 ratings, 500+ a month) and $186.14 | No conflict; the Prime rows add a volume signal |

Checked and consistent:
- v5's 32–34 µm per degree [SL wave2 §1];
- v3's tab yield 72–96 N as 1.8× 39.2 N;
- v8's servo force at the former (123 N for 25 kg·cm on a 20 mm horn);
- v8's anvil stress of 14–57 MPa;
- v1's strip-edge window use of 20–120 %.

---

## 4. Transfers

### From borrowed machines into theirs

- **The applicator is T and C at once** (Combination A). It is the one host
  where the tack's contact never leaves its datum, the back-out reacts on the
  carrier, and the tab is sheared by the same stroke that crimps. → v8, and v7's
  ladder rung 1–2.
- **A steel force ceiling in series, wired into the enable line** (b1b's disc
  stack, b2's spring link). → v7's stroke, every hosted station (B-v7-2).
- **Crank kinematics.**
  - Crawl by a speed profile indexed to angle. → v7's hosting of b1b and b1c
    (B-v7-1).
  - Crank angle as the height knob and a 10 N re-touch read by the shaft
    encoder as the height gauge. → v3's campaign (Combination B).
- **The jack test** as a zero-build first campaign press on the production
  applicator and reel. → v3, v7's first day.
- **Klipper's `load_cell/dump_force` and `angle/dump_angle`,** and ADS1220 and
  CS1237 support. → v7 stack C (Combination C).
- **The fold-back band, or crimping upstream-first and parking after,** when the
  host is an applicator, whose upstream pressure plate and wire-side scrap
  cover sit under v1's lifted neighbours (B-v1-1).
- **b6's rule, tension not compression:** plunge at the root, draw to the tip.
  → v6's rib split (B-v6-1).
- **b7's blade geometry and twist-on-pull.** → v6's strip station (B-v6-2).
- **Crossing conductor last.** → v6's per-conductor insertion (B-v6-3).
- **Stages for a bench-fixed press.**
  - The Ender on its back, or b1's two rails.
  - b3's self-contained head on the carriage (Combination D).
  - → v1b (B-v1b-1).
- **The bundle hovers 0.3–0.5 mm off the floor; look for its shadow.** → v8's
  top look and v1's gate (B-v8-3).
- **Pick-and-place bellows nozzles** for a tilted box top. → v4 (B-v4-1).

### From theirs into borrowed machines

- **v8's tack removes b1b's and b1c's holder-timing problem.**
  - With the tack as holder, the fork and foot leave before the crank turns.
  - The fork swing no longer races the ram, which removes b1c's "clearance
    under the descending ram" problem.
  - b1c's lay-in and gate move to a stop at 0–40°, where there is room for a
    former and a mirror [calc W §14].
  - This is Combination A and A1.
- **v7's crawl and position-indexed envelope** change b1b's claim that "the
  force curve cannot flag early enough" on a short stiff obstruction.
  - That claim holds for a crank turning at constant speed.
  - With a profiled crawl, a doubled contact is stopped at a few hundred
    newtons [calc W §5]. The disc stack remains, as the ceiling.
  - b1b's "~19–39 HX711 samples through compaction" becomes 160–320 at a
    0.05 mm/s crawl.
- **v5's box roll gauge and blade silhouette** give b1 and b1b the in-line
  crimp height they lack ("there is no in-line crimp height"). At the dwell's
  withdraw position the crimp is ≥7 mm out of the applicator, with nothing
  above or beside it: a backlight, a blade under the barrel, and the box's
  front 1 mm read for roll.
  - Combination B's crank re-touch is a second, independent reading.
- **The neck, not width or height, is where anything reacts on the box** (RP's
  lance-notched plate, taken in by v1, v3 and v5).
  - It confirms terminal-supply's break of my catch plate. On silicone,
    height gives no margin either [calc W §8].
  - Every pull in b1, b1b, b1c and b8 uses a neck fork above the floor.
- **v7's journal, three bands and ask queue** go to b8's long unattended spool
  runs and b1c. The ask ("park this conductor with a photo") is what b8
  lacks when the belt slips.
- **v7's capture app, sync LED and cameras matched by name** go to every
  camera in my ideas. The ELP's focus re-park on stream start applies to b1b's
  dwell pictures as much as to v1.
- **v4b's pocket plate** feeds kit contacts to b3's head (Combination F) and to
  a post pick, where b3 as it stands takes strip only.

---

## Measurements that settle most of this

1. **The jack test** with an OTP XH applicator (b1b stage 0). Record:
   - clear height under the raised crimper faces and what hangs below them;
   - the height of the upstream pressure plate and the wire-side scrap cover;
   - a scan of the insulation crimper's profile for the former.

   It settles Combination A's room, B-v1-1 and the former.
2. **A0 by hand.** Tack three contacts on the applicator's anvil with a lever
   former, pull each with the 0.1 g scale, then pump the jack and section one.
   It settles the tack's grip on silicone, B-v8-1's height and B-v8-2's order.
3. **One tacked conductor under the ELP** with two LEDs at ~65° on opposite
   sides. Does the bundle's displaced shadow show, and does a strand pushed to
   the floor lose it? (B-v8-3.)
4. **One kit contact barrels-up under a probe on the 0.1 g scale.** Record the
   force at 0.1, 0.3 and 0.6 mm of box-top travel, and whether the lance
   returns. (B-v4-1.)
