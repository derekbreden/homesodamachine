# machine-that-sees-and-learns on hand-tool-as-press (wave 3)

machine-that-sees-and-learns holds that the first stage of a cell is one
software can move and observe. hand-tool-as-press holds that the crimp tool is
already the machine. This file reads hand-tool-as-press's eleven arrangements
([summary](../explorers/hand-tool-as-press/summary.md), every idea file, its
three calc outputs) against this view's
[v1](../explorers/machine-that-sees-and-learns/ideas/v1-watched-nest.md),
[v3](../explorers/machine-that-sees-and-learns/ideas/v3-press-that-runs-experiments.md),
[v5](../explorers/machine-that-sees-and-learns/ideas/v5-inspection-booth.md),
[v7](../explorers/machine-that-sees-and-learns/ideas/v7-the-run.md) and
[v8](../explorers/machine-that-sees-and-learns/ideas/v8-tack-look-crimp.md).

It does not repeat into-the-housing's wave-2 reading
([into-the-housing--on--hand-tool-as-press.md](into-the-housing--on--hand-tool-as-press.md)):
the lance in the neck and repairs R1–R5, a3's rolled crimps, a2c's first latch,
the feed-length rule, the stencil pusher, and the gang push's force belonging
to the fixture. hand-tool-as-press has taken those in.

**Citations.**
- **[w3 §n]**: this exchange's numbers,
  [`calc/w3_on_hand_tool_as_press.py`](../explorers/machine-that-sees-and-learns/calc/w3_on_hand_tool_as_press.py),
  output [`w3_on_hand_tool_as_press.out.txt`](../explorers/machine-that-sees-and-learns/calc/w3_on_hand_tool_as_press.out.txt).
- **[sl w2 §n]**: this view's [`wave2.out.txt`](../explorers/machine-that-sees-and-learns/calc/wave2.out.txt).
- **[htp calc §n]**, **[htp w2 §n]**, **[htp ex §n]**: hand-tool-as-press's
  [`hand_tool_press.out.txt`](../explorers/hand-tool-as-press/calc/hand_tool_press.out.txt),
  [`wave2.out.txt`](../explorers/hand-tool-as-press/calc/wave2.out.txt) and
  [`exchange_procedure.out.txt`](../explorers/hand-tool-as-press/calc/exchange_procedure.out.txt).
- **[ith ex §n]**: into-the-housing's
  [`exchange_hand_tool_as_press.out.txt`](../explorers/into-the-housing/calc/exchange_hand_tool_as_press.out.txt).
- **[ff w2 §n]**: force-and-form's [`wave2.out.txt`](../explorers/force-and-form/calc/wave2.out.txt).
- **[rap P §n]**: ribbon-as-pallet's
  [`exchange_on_machine_that_sees.out.txt`](../explorers/ribbon-as-pallet/calc/exchange_on_machine_that_sees.out.txt).
- **[prime]**: a row of [`sourcing/amazon-prime.md`](../sourcing/amazon-prime.md),
  observed 2026-09-28 in Derek's signed-in Chrome.

Sketch: [`w3-t-then-c.svg`](../explorers/machine-that-sees-and-learns/sketches/w3-t-then-c.svg)
(end view at station C from cited dimensions; side elevation schematic).

---

## 1. Combinations

### W1 — Tack at T, crimp in a one-nest SN die set at C (v8 × a4, on v1's pallet and v1b's stage, run by v7)

This is the pairing developed in full here. v8 splits Derek's priority step
into a light watched station T (place the contact on the conductor, hold the
two together) and a heavy station C (crimp). v8 lists C's host loosely: "v1's
press, a1's squeezer, a knee press, or Derek's hand". hand-tool-as-press's a4
takes a spare SN-2549 jaw set out of the tool into a guided die set with an
eccentric, a disc-spring stack, a button load cell and a re-touch indicator,
and notes that one nest cut to 6–8 mm wide fits 5 mm pitch. W1 is a4's
one-nest die set as v8's C, fed by v1's pallet.

**Why the pairing does something neither does alone** [w3 §7]:
- **a4 alone** has no way to place the contact or the conductor except a1's
  locator with a person, or a2's carriage, which pays the side-entry
  stand-out (8.7–14.7 mm with crimped neighbours, §2 below).
- **v1 alone, laying in under a4's short stroke,** has no room. a4's
  eccentric (e 2.0–2.5 mm) opens the conductor punch only to 4.7–5.9 mm above
  the floor. v1's waiting conductor tops out at 5.40–5.85 mm, so the working
  conductor passes under the open punch with −1.12 to +0.33 mm before 0–0.55
  mm of spool curl [rap P §6]. The oblique camera clears a 6 mm punch only
  from 35–40° off vertical.
- **v8 alone** has no concrete C that fits between lifted neighbours. The
  SN-2549 as sold does not: its jaw spans the row (the side-entry law, §2 and
  §4).
- **Together:** the lay-in and the strictest look happen at T, where nothing
  stands over the barrel. The tacked contact rides to C on its own conductor.
  At C the die only has to pass a tacked contact, which e 2.0–2.5 does with
  0.5–1.7 mm to spare. The one-nest punch fits between neighbours that v1's
  keys already hold 5 mm up.

#### Picture it

**Where things start.**
- **The stage.** v1b's bed-slinger with its hot end removed. The Ender-3 V3 SE
  is on Prime at $219 (B0F8J78BN1, 2,112 ratings, 500+ bought in past month)
  or $186.14 (B0DD7F2BH9) [prime].
- **The pallet.** A ribbon end in v1's fan block rides the stage:
  - flush-cut, split 25–35 mm, stripped;
  - fanned to 5 mm pitch;
  - each conductor in its own hinged key, the waiting ones with their axes
    5 mm above the working contact's floor.

  The strip length follows the contact source (§3 item 4 below: ~1.6–2.1 mm on
  clone-shaped kit contacts, 2.4 mm on genuine SXH).
- **The far end** sits in a push-in block (Wago 221-415, $28.00 for 25 [prime])
  wired to the station ESP32. The XH end is made first.
- **Contacts:**
  - loose kit contacts on v4b's pocket plate, picked by v4's sprung nozzle;
  - or genuine SXH strip on pilot pins.
- **Station T** (v8):
  - a printed frame with a box slot, a lance relief and a steel insert under
    the insulation barrel (3 mm HSS square blank, $9.99 [prime]);
  - a 1.2–1.5 mm steel former with an insulation profile, driven by a 35 kg·cm
    servo on a lever (ZOSKAY DS3235, $27.99 [prime]) to a loose screw stop;
  - a 20 kg bar cell under the nest insert, not in the former's link. The stop
    then carries the servo's excess, and the cell reads only the forming force,
    33–132 N [sl w2 §5]. The Prime 5 kg cell with HX711 ($9.99 for two) tops
    out at 49 N, so a 20 kg bar cell is in this view's Wave 3 sourcing
    requests;
  - a top camera straight down: the 16 MP IMX298 M12 board, $69.99, with a
    12 mm lens, $9.99 [prime];
  - v1's cam 2 across at wing height under the lifted neighbours, and a 16-LED
    WS2812B ring lit one LED at a time ($18.99 for five [prime]).
- **Station C, 20–40 mm along the bed** (a4, one nest):
  - an SN-2549 jaw set with each die piece cut to one nest, 6–7 mm wide;
  - the upper piece in a laminated holder that stays no wider than ~7.4 mm for
    the first ~5.9 mm above the crimping edge and widens above that (a
    T-section; its neck carries 3.5–4.5 kN at 50–64 MPa) [w3 §7];
  - an eccentric of e = 2.0–2.5 mm;
  - under the lower holder, a disc-spring stack preloaded to ~3.5 kN and a
    500 kg (4.9 kN) button cell ($74.99, thin listing [prime]);
  - an AS5600 on the shaft ($7.99 for three [prime]);
  - a 0.001 mm digital indicator across the dies (Clockwise DITR-0105,
    $52.99 [prime]; its RS232 cable is not on Prime);
  - in front of the lower die, a **seat**: a floor ledge for the box and a
    retractable front stop. No side walls, so the box's silhouette stays
    visible;
  - beside C, v1's silhouette window (a hardened blade under the conductor
    barrel, a backlight, a gauge pin) and a backed pull plate.
- **Controllers:** v7's Stack A. The station ESP32 runs the eccentric's
  stepper, the servos, the load cells and the far-end inputs, and a runner on
  the Mac owns the recipe, the journal and the log.

**What moves, one conductor.**
1. **T, contact in.** The nozzle drops a contact in T's box slot, or the strip
   indexes. *Look:* box on its stop, lance standing, wings upright. The top
   camera also measures this contact's box front to conductor-barrel rear
   edge.
2. **T, lay-in.** The stage brings key *k* over T. *Hover look:* the tip and
   the torn insulation edge. X and Y are predicted from the pallet and
   corrected once or twice. The plunger presses key *k* to its stop. *Side
   look:* bundle in the U, edge in the window, nothing above the wing tips.
3. **T, tack.** The former comes down at ~1 mm/s to its loose stop. The cell
   under the nest logs the forming curve.
4. **T, the look that matters.** Straight down into the open conductor barrel
   under 4–8 lighting states and two focus depths. Every strand between the
   wing tips, no silver outside, the brush length, the edge in the window.
   - Pass: go on.
   - Fail: the conductor backs out through the key's grip and the contact is
     discarded. It costs a contact, not a ribbon end.
5. **Carry.** Key *k* rises with the tacked contact. The box leaves T's slot
   straight up; the lance is in a relief, so it touches nothing. The stage
   moves the pallet to C.
6. **C, carry in high, set down.**
   - Key *k* holds the contact's floor 1.0–1.7 mm above C's anvil (cradle depth
     plus lance plus margin [ith ex §2]).
   - The stage moves +Y until the box is over the seat, then lowers the pallet
     by that 1.0–1.7 mm. The box lands on the ledge and the barrels on the
     anvil.
   - During the carry the neighbours ride 1.0–1.7 mm above their working
     height, still beside the punch's narrow section, which reaches ~11.6 mm
     with the punch open. The set-down returns them to 3.05–6.35 mm above the
     working floor [w3 §7].
7. **C, seat look.** Cam 2 runs under every neighbour at Z 0–2.85 mm
   [w3 §7]. It sees the conductor barrel's rear edge against the die's rear
   face (the bellmouth offset), the box flat on the ledge, and the tack where T
   left it. If the barrel's rear edge is off, the stage nudges Y, since the box
   sits on a ledge with no walls holding it.
8. **C, the stroke.** The MCU turns the eccentric.
   - Fast to ~30° before BDC.
   - Slow over the last ~20°, checking the button-cell trace against the
     envelope every sample. It stops and reverses on force rising early (two
     contacts, insulation under the conductor barrel, a contact seated high).
   - The dies bottom and the stack takes the overtravel.
   - The eccentric backs off to a 10 N re-touch and the indicator is read:
     crimp height #1 (a4, from force-and-form's f3).
9. **C, out.** The ram rises 4–5 mm, and the stage lifts the pallet 1.0–1.7 mm
   before drawing back −Y (R1).
10. **After-look.** The stage sets the crimp on the blade beside C at first
    silhouette contact. v1's side silhouette gives crimp height #2, corrected
    for roll by the box's own silhouette (32–34 µm per degree [sl w2 §1]),
    plus the bellmouth, brush, insulation height and bend.
11. **Proof pull,** ~20 N, on the backed plate: the Y belt pulls through key
    *k*'s grip while the camera watches the edge in the window.
    - Strip contacts: the reaction is on the tab if a stub rides through C.
    - Loose contacts: on the plate in the neck, if the neck allows (§2 below,
      a6).
12. Key *k* returns to its waiting height; the next conductor. J2's cavity-3
    conductor and J7's trimmed one are skipped by the recipe.

**What locates what.**

| At | Contact located by | Conductor located by | Reference for "fixed" |
|---|---|---|---|
| T | Box slot and stop | Key groove, then the picture (tip and edge) | T's frame, seen with fiducials |
| T to C | The tack: axial position and roll against the conductor | The key | The pallet |
| C | Ledge (height, roll); stage Y set from the seat look (axial, ±0.03 mm at 0.02 mm/px [htp calc §7]); the closing dies (lateral) | Carried by the contact | C's lower die holder |
| Crimp height | Eccentric BDC and die faces meeting on the stack | — | Die geometry; read by re-touch and silhouette |

The front stop is a backstop for the set-down, not the reference. The picture
sets the contact against the die, as v1 does.

**What drives the crimp and carries its force.**
- **Drive.** A NEMA 23 through a 10:1 planetary (STEPPERONLINE, $48, 10 N·m
  permissible [prime]) turns the eccentric. The bench's NEMA 23 is in the
  weld rotator [repo: shared-context], so this is a second motor or a
  borrowed one.
- **Load path.** Ram → punch → contact → anvil → button cell → disc stack →
  base → side plates → shaft bushings.
- **What carries none of it:** the stage, the pallet, the keys and the
  conductor.
- **Torque.** Once the die contact point is set by the frame's real stiffness,
  the peak is 1.6–1.95 N·m before friction and 2.0–2.9 N·m with it [w3 §6].
  - The 10:1 planetary carries that with margin.
  - A 3:1 belt (~2.7–3 N·m) sits at the edge.
  - The Greartisan 40 kg·cm self-locking worm gearmotor (~3.9 N·m, $26.99
    [prime]) carries it, if its figure is the working torque.

**How it knows the crimp worked.**
- T's forming curve and top-down look, before anything irreversible.
- C's seat look.
- The die-force trace, measured directly at the die, not through a handle.
- **Two crimp heights from independent routes,** re-touch indicator and
  silhouette. Each is a running check on the other:
  - a die piece loosening in its holder shows as the re-touch drifting;
  - a knocked camera shows as the silhouette drifting.

  v3's calibration is built into production.
- Continuity and identity through the far end.
- The proof pull, where the contact form allows one.

**What the person does.**
- Loads 14 ribbon ends into pallets (10–30 min a unit [digest]) and pours
  ~60 contacts onto the pocket plate.
- Answers 1–2 asks a unit in steady state [sl w2 §7].
- Inserts into housings, or hands the pallet to an insertion station.
- Once: gets the die-set steel laser-cut, cuts a jaw set to one nest (abrasive,
  wet, slow), and seats the dies by closing them on each other.

**Time** [estimate]:
- T side 29–81 s [sl w2 §5].
- C side ~37–63 s: carry and set-down, seat look, a ~8 s stroke with its slow
  last 20°, re-touch, lift, silhouette, pull.
- 66–144 s a conductor, ~1–2 h unattended a unit.

**Problems kept beside it.**
- **Cutting hardened SN pieces to one nest** without cracking (a4's problem,
  unchanged).
- **The tack's grip window on silicone,** 0.2–1.5 N wanted and 0.4–9 N
  estimated (v8's problem). The T-to-C carry adds a load case: a snag during
  the +Y carry under the punch is resisted only by the tack.
- **Whether a tacked insulation barrel re-formed by the SN insulation die ends
  like a one-pass crimp.** v8 argues the one-stroke order already closes the
  insulation wings first [sl w2 §5]; sectioning settles it.
- **The per-crimp pull on loose contacts** needs a neck gap the plate fits in
  (§2, a6). Strip stubs can keep their tab through C, if the stub, which lies
  across X in the floor plane at the contact's rear, clears the anvil holder.
  That is undrawn.
- **The a4 unknowns:** whether SN die faces meet face to face, and the jaw
  seat geometry to copy.
- **Pallet loading** is the person's time, as everywhere [digest].

**Rests on:** v1's neighbour height (5 mm) and pitch (5 mm); clone dimensions
for the contact [xh-facts §1]; the tacked barrel at 2.3–2.5 mm [v8 estimate];
a frame of 15–30 kN/mm [w3 §6, estimate].

### W2 — Tacked by the machine, crimped by the foot (v8's T × a6's bench)

A pairing with less to build, and the first motorised rung v7 names for v8.
Station T runs a whole ribbon end unattended, tacking every conductor. The
person takes the ribbon end to a6's crimp jig and crimps each tacked contact
with the foot.

Batch tacking asks one thing of T that v8 does not: the former, its guide and
its lever must pass between tacked neighbours hanging at 5 mm pitch, which
occupy 3.05–6.5 mm above T's floor. Everything of T at that height must be
no wider than ~7.3 mm, a little under W1's 7.45 because a tacked barrel is
~2.0–2.1 mm wide [w3 §7, estimate].

**What changes at a6's crimp jig.**
- **The blade goes.** a1's locator plate loses its insulated flap blade and
  gains a seat in front of the jaw's front face: a floor ledge with a lance
  relief, and a front stop.
  - The conductor's depth in the contact was set and photographed at T, so
    nothing has to find it at the tool.
  - With no stage to nudge Y, the front stop is the axial reference here. It
    is set once per contact lot by a screw, from the box-front-to-barrel
    distances T's top camera measured on that lot. T refuses to tack a contact
    outside the lot's band.
  - a6's first open problem, whether the kit contact's neck (0.2–0.5 mm
    [estimate]) holds a 0.13–0.15 mm blade plus a brush [htp w2 §1], stops
    mattering for the crimp.
- **The first tooth stops mattering.** No conductor has to enter a contact
  held at the first tooth, because it is already in it. The half-press
  remains as an optional clamp before the full press.
- **The opening limiter closes further.** A tacked contact needs 3.90–4.40 mm
  of jaw opening with its 1 mm carry-clear, against 4.35–5.10 mm for an open
  one. That is 0.45–0.70 mm less opening and ~3–8 mm less pedal at 2:1
  [w3 §8].
- **The person's fine act becomes a coarse one.** Steering a stripped
  conductor into a 1.8 mm barrel becomes carrying a contact already on its
  wire into a 4 mm opening and setting it on a ledge.

**The jaw law still applies at C,** because the SN-2549 as sold spans the row
(§2). So the ribbon end leaves the stage at C.
- The person holds the pallet's body, or unclamps the web, and bends each
  conductor out of the row by hand, as a6 describes.
- The tacks are unaffected, since the bend is 20–30 mm behind the contact.
- The copper sets (§2), which one-at-a-time insertion at i5 tolerates.

**Person time** [w3 §8, estimate]:
- 23–37 s a crimp with the booth pull and keyhole, 20–33 min a unit;
- 9–15 min without them;
- plus 10–30 min of pallet loading for T.

Today's is ~22 min [htp w2 §9]. The minutes do not fall. The fine placement
leaves the person, every contact is placed under a top-down look, and the
machine does the step Derek most wants automated while the person does the
squeeze.

**What it leaves open.** The same tack window as W1. Also whether a person
handling a pallet of tacked contacts rolls any of them past the tack's
~0.34 N·mm roll resistance [sl w2 §5]. The seat's ledge squares a small roll;
a large one shows in the seat frame.

### Other pairings, briefly

- **W3. a6's pull jig and keyhole with v5's booth (one station).** a6's backed
  slotted plate on the box's rear walls is v5's lance-notched stop: the same
  part.
  - Adding v5's hardened blade under the conductor barrel, a roll flat under
    the box, a backlight and the ELP across gives every foot-closed crimp a
    roll-corrected crimp height, bellmouth, brush and window reading.
  - The capstan lever pulls to the leaf switch, and the keyhole follows.
  - a6's side frame (roll within ±10–15°) is loose for insertion. The
    silhouette needs roll within 1–2° [sl w2 §1], which the roll flat and the
    box's own silhouette give.
- **W4. a6's electronics as v7's rung 0.5.**
  - Record per conductor: a6's cord load cell and pulley AS5600 give a
    force-against-travel curve for every foot-closed crimp, and W3 gives its
    measured height. The runner files both under unit, loom and pin, beside
    i5's conductor-to-cavity pairing.
  - What it yields: labelled data for v7's force envelope and v3's windows,
    from Derek's own crimps, before any motor exists.
  - a6's keyhole acts as a hard-fail band that needs no judge.
- **W5. a3's gantry steered by v1's pictures.** a3's gantry is v1b's stage
  role.
  - A camera across the fixture at the pulled-out tip, and v1's backlit
    tip look (splay, a strand standing out, strip length, the torn edge), come
    before every slide-on.
  - The gantry corrects X and Z to the tip's real axis, or sends the tip to a
    twist. Numbers in §2, a3.
- **W6. a1b and a5 as v3's first campaign presses.**
  - A $22.29 second SN-2549 [prime] or a $38.99 PA-09 [prime, B002AVVO7K,
    1,719 ratings, 200+ bought in past month] with a pusher sweeps grip
    positions.
  - v5's silhouette maps each level to a length, and v3's pulls to failure
    grip copper, not jacket (§3 item 7).
  - a5's separate insulation squeeze lets v3 sweep insulation height
    independently. Its cut-through side needs xh-facts' bend test (60–90°,
    several times [mfr S5]) as well as pulls, since a cut jacket can still
    pass a pull. v3's servo bend arm and the camera on the wing tips do that.
- **W7. v4/v4b's classification in front of a2b's revolver.** The camera
  measures each contact before it is loaded: box length, wing width and pose.
  a2b's chute is then sized to the lot's measured end view, not to the clone
  drawings' ±0.25 mm, and outliers never reach the chute.
- **W8. v7's write-ahead journal under a1b.** a1b names its gap: "a power loss
  mid-stroke leaves a half-crimp that looks like any other contact in the
  tool". The journal holds a *squeeze intent* with no *result*, so on restart
  the runner knows which conductor is suspect, re-looks and asks. The keyhole
  still stops what reaches the housing.
- **W9. a2's tip plate beside v1's hover picture.** A grounded tip plate at a
  known Y gives each conductor's tip position electrically.
  - Against the picture's reading, it checks the camera's scale and focus
    drift on every conductor.
  - A tip that touches early against the picture is a splayed strand, found
    before the lay-in.

---

## 2. What still breaks in their revised and new ideas

### a1b (pawl out): the proof pull at hold is not a strand test

**Conflict.** a1b re-closes the dies "until the force rises a few newtons" and
pulls the wire to ~20 N while the dies hold the crimped barrels. The load cell
is at the grip. A few newtons at the grip is 30–200 N at the dies through the
end-of-stroke gain of 15–40.

**Consequence.** The dies' clamp adds μ × that to the strands' grip: 4–100 N
across μ 0.15–0.5 [w3 §1]. That is the same order as the 20 N being tested.
- A crimp with little grip of its own passes.
- To keep the added grip under 2 N, the held die force must stay under
  4–13 N, which is 0.1–0.9 N at the grip.
- The empty-tool curve repeats to perhaps ±0.5–1 N at the grip [estimate].
  That is ±8–40 N of unknown die force.

hand-tool-as-press's own [htp ex §3] reached the same result for p4: "above
~100 N of held die force, a crimp with no grip of its own passes a 20 N pull".

**Branch: position hold instead of force hold.** The dies stop short of the
barrels, and the pull reacts on the jaw's front face. It does not help
[w3 §1].
- Where the lance tip hangs in front of the anvil face, the tip meets the
  face after 0.11–0.26 mm of travel, before the box's rear shoulder (0.35–0.5
  mm).
- Where it sits over a relief, what meets steel first depends on the relief's
  unknown rear end.

**Repair.** The pull goes to a6's backed plate or a2's pull slot, which
hand-tool-as-press already use for a1 and a2. a1b keeps what the pawl removal
does give: back-out after hold, a smooth curve, and a settable stop for v3.

**Uncertain.** Whether the jaw-face contact through the box is ever reachable
before the lance, on a real kit contact (the neck photo).

### a1b: the force wall has to live on the station MCU

**Conflict.** a1b's only guard at full closure is "a force wall in software".

**Consequence** [w3 §2]:
- The pusher runs 2 mm/s at the grip. After the die faces meet, the grip
  sees a stiffness of roughly 3–60 N/mm (handle and pin compliance in series
  with the die loop through the gain squared) [estimate].
- A typical 30 ms USB round trip is 60 µm of grip, 6–51 N extra at the dies.
- A 0.5 s stall on the Mac is 1 mm of grip, 108–857 N at the dies. That is the
  same order v7 found for a steel press at crawl (375–750 N [sl w2 §3]).
- The handle crawls the die, but the pusher does not crawl.

**Repair.** v7's rule: the ESP32 runs whole squeezes, checks every HX711
sample (12.5 ms, 3–21 N), and holds the wall. The Mac commands squeezes and
reads traces.

**What the handle does give.** Near closure the die moves 0.05–0.13 mm/s at a
2 mm/s grip speed, which is v7's crawl without a crawl phase [w3 §2].

**Uncertain.** The handle and cradle stiffness; measured by closing the empty
tool against the cell.

### a4 and a4b: 0.15 mm of overtravel is a rigid-frame figure

**Conflict.** a4 sets the eccentric "~0.15 mm past the point where the die
faces meet", so the dies bottom and the stack takes the rest, with a peak of
~4–5 kN [htp calc §6]. a4 itself puts a button cell in series that "deflects
on the order of 0.1 mm at full scale". Add 10–12 mm shaft bending in bushings,
bushing play and laminated holders, and the frame is ~15–30 kN/mm [estimate].

**Consequence** [w3 §6]:
- **At 15 kN/mm** a 2.6 kN crimp keeps the dies apart at BDC (F_BDC 2.41 kN).
  Crimp height then follows frame stiffness, which is what the stack was
  there to prevent.
- **Below ~23 kN/mm** the stack never engages.
- **The peak at BDC is 2.3–3.7 kN,** not 4–5.

hand-tool-as-press's own [htp ex §4] found for p5 that a soft frame moves die
contact away from BDC. a4 as written does not carry that across.

**Repair.**
- Set die contact at preload / k_frame + 0.05 mm: 0.17–0.28 mm above BDC.
  Then the stack engages at every stiffness in the range, and the peak torque
  is 1.6–1.95 N·m before friction (2.0–2.9 with).
- Find the setting on the machine: step the die-contact height down on empty
  strokes (dies face to face, no contact) until the button cell shows the
  stack's knee.
- The drive the numbers leave room for is the NEMA 23 through the Prime 10:1
  planetary. The 3:1 belt a4 names is at its edge.

**Uncertain.** The real frame stiffness and stack rate. One empty stroke with
the cell answers both.

**Sourcing, from [prime]:**
- no heavy-series disc springs on Prime, only a light stainless Belleville
  assortment ($14.99);
- the 500 kg button cell ($74.99, thin) reaches 4.9 kN, which covers
  3.6–3.7 kN at BDC but not a4's 4–5 kN;
- no loose SN-2549 jaw set on Prime; the iCrimp IWS-0723K kit ($46.59, 9
  ratings) is the only Prime route to a 2549 die. icrimptools.com sells jaws
  alone at $4.99–9.99 [htp, source].

### a2, a2b, a3: the stand-out leaves out the crimped neighbours

**Conflict.** The side-entry law puts the stand-out at a + 1.9 mm [htp w2 §3].
That 1.9 is 1.05 mm (working floor to axis) plus 0.85 mm (a bare neighbour's
radius), with no clearance. Once half the row is crimped, the neighbour's top
above its axis is the crimped insulation barrel (~1.25 mm) or the box
(1.35 mm). hand-tool-as-press's own a4b budget counts the box [htp w2 §4].

**Consequence.** With 0.3 mm clearance the stand-out is a + 2.7 mm: 8.7–14.7 mm
for a = 6–12 mm [w3 §3].
- Root radius 9–47 mm on a 20–35 mm free length, against the 67–78 mm at which
  the strands yield.
- Tip pull-back 1.3–6.5 mm.

The free length is shorter than the 25–35 mm split wherever the comb holds
8–10 mm of each conductor (a2), which moves both further.

**Where the box sits.** The neighbours' crimped boxes lie just ahead of the
jaw's front face, in the plane of a1's locator plate and flap.

**Repair.**
- Keep the locator plate inside the jaw half's depth on the row's side, so it
  does not add to a.
- Budget the stand-out at a + 2.7.
- Squaring before a gang push stays as it stands.

**Uncertain.** a, still the unmeasured number most of hand-tool-as-press rests
on.

### a6, and a2b with kit contacts: the strip length belongs to the contact

**Conflict.** a1, a2 and a2c strip 2.4 mm, JST's figure for genuine SXH
[mfr S6]. a6's end jig and a2b's revolver use the kit contacts, whose clone
drawings give a conductor barrel of 1.25–1.5 mm [xh-facts §1].

**Consequence** [w3 §4]:
- Putting the brush 0.1–0.2 mm past the barrel and the edge mid-window
  (S = E + A/2 + b, JST's own form [mfr S5]) gives 1.60–2.10 mm on clone
  dimensions.
  - That is exactly the KONNRA clone spec's 1.6–2.1 [digest].
  - A 2.4 mm strip on those contacts puts bare strands 0.2–0.5 mm into the
    insulation barrel in three of four corners.
- The reverse error on genuine contacts (1.6 mm strip, E 1.8–2.0) puts the
  jacket 0.35–0.55 mm under the conductor barrel, a named defect [mfr S5].

**Why a6 does not see it.**
- a6's Case 2 camera line looks across the neck at the brush, not down at the
  window.
- The keyhole cannot catch it, since strands inside the insulation barrel fit
  the cavity.
- The pull may pass it.

**Repair.**
- Set the Klein stop from one measured kit contact: E and A under the ELP.
- a6's side frame, and a1's, also looks at the window between the barrels.
- In this view, v1/v8's per-conductor edge reading catches either error by
  construction.

**Uncertain.** Which barrel the kit contacts have. One contact photographed
from the side settles it, and the same photo gives the neck.

### a6 (and a2's pull slot): the pull plate needs the same neck as the blade

**Conflict.** a6's pull plate is 0.3 mm spring steel whose slot takes the neck
strip and bears on the box's rear walls. It has to sit between the box's rear
face and the crimped conductor barrel: the transition, 0.2–0.5 mm
[ith ex §1], less the brush (0.1–0.2 mm) wherever the brush lies under the
tines.

It cannot be backed from behind inside the neck, because the barrel is there.
So its tines are cantilevers. a6 uses 0.3 mm because thinner tines yield at
20 N [htp w2 §2].

**Consequence.**
- The plate fits only at transitions of ~0.35–0.5 mm. That is the same
  measurement that decides the blade, in the same direction.
- When the neck is too short for a blade (a6's Case 2), it is also too short
  for a per-crimp pull on loose contacts.

**Branches:**
- A steel backer that sits over the crimped conductor barrel, reaching down to
  ~1 mm above the floor, shortens the unbacked tines to ~1 mm. That may allow
  a 0.15–0.2 mm plate [estimate].
- Strip stubs react on the tab in compression (72–96 N [rap P §3]).
- Below both, loose contacts get pulls by sample only (v1's third row; v3's
  re-checks).

This view's v1 and v5 lance-notched plates carry the identical constraint;
the two views converge on one part and one measurement.

### a5: the 1.8 mm-thick die over a clone conductor barrel

**Conflict.** The PA-09's 1.6 and 1.9 nests sit in a 1.8 mm-thick die
[mfr S18], and Engineer's rule is "die thickness = barrel length". a5 places
the conductor barrel's rear edge 0.1–0.2 mm proud of the die's rear face.

**Consequence** [w3 §5]:
- With a clone barrel of 1.25–1.5 mm, the die's front face lands 0.40–0.75 mm
  ahead of the barrel's front edge. Across a transition of 0.2–0.5 mm, that
  reaches the box's rear by up to 0.55 mm.
- The other placement (die flush with the box) loses the bellmouth.
- On a barrel of ~1.8 mm it fits, which is what Engineer's rule and JST's
  2.4 mm strip both suggest for genuine SXH (§3 item 4 below).

**Repair or branch.**
- a5 with genuine SXH or BXH as drawn.
- With kit contacts: measure E first. If it is short, a5 is a genuine-contact
  arrangement.

**Uncertain.** Whether Engineer lists the PA-09 for SXH with a deliberate
overhang.

### a3: slide-on capture without a look first

**Conflict.** a3 assumes the slide-on needs the nest on the conductor's axis
within ~±0.5 mm [estimate], and has no camera on the tip before it.

**Consequence** [w3 §10]:
- The open conductor barrel captures a gathered 0.72 mm bundle within
  ±0.48–0.59 mm, but a splayed 1.0–1.2 mm bundle only within ±0.24–0.45 mm
  [sl w2 §2].
- A tip 8 mm proud of a comb whose exit is 2–3° off axis sits 0.28–0.42 mm
  aside, and spool curl adds up to 0.55 mm [rap P §6]: 0.28–0.69 mm in all.
- Sliding end-on over a splayed tip is where a strand is bent back outside a
  wing. Nothing in a3 sees it before the crimp. The fixed camera looks at the
  crimped conductor.

**Repair.** W5: a picture of each pulled-out tip before the slide-on, the
gantry correcting to it, and a twist step for splayed tips.

**Uncertain.** How often this ribbon's tips splay after the Klein.

---

## 3. Consistency

1. **a1b's proof pull at hold** against hand-tool-as-press's own
   [htp ex §3]. The exchange calc is right: a grip-side "few newtons" is
   30–200 N at the dies and flatters by 4–100 N (§2 above).

2. **a4's overtravel and peak** [htp calc §6: 0.15 mm, 4–5 kN, "NEMA 23
   through 3:1 has margin"] against their [htp ex §4] and a4's own button-cell
   compliance. With a 15–30 kN/mm frame the dies may not meet at 0.15 mm, and
   the peak is 2.3–3.7 kN. Set for stack engagement, the peak torque is
   2.0–2.9 N·m with friction [w3 §6].

3. **The jaw-law +1.9 mm** [htp w2 §3] against their own C-frame budget,
   which counts the crimped box's 1.35 mm and a 0.3 mm clearance [htp w2 §4].
   The latter is the consistent one: a + 2.7 mm.

4. **Strip length.** The digest lists 2.4 mm (JST) against 1.6–2.1 mm (KONNRA)
   as a disagreement. On the clone drawings' barrel (1.25–1.5 mm) and window
   (0.5–0.8 mm), JST's own form S = E + A/2 + b reproduces 1.60–2.10 exactly.
   Run backwards from 2.4, it implies a genuine barrel of 1.80–2.05 mm
   [w3 §4].
   - Engineer's rule with the PA-09's 1.8 mm die, listed for SXH-001T-P0.6,
     points to the same ~1.8 [mfr S17, S18; estimate].
   - So xh-facts' "conductor barrel ~1.25–1.5 [estimate, reading clone
     drawings]" is a clone figure, and genuine SXH is probably longer
     [estimate].
   - Both strip lengths are right, each for its own contact. hand-tool-as-press
     uses 2.4 throughout, which is right for a2's SXH stubs and not for a6's or
     a2b's kit contacts.

5. **Insulation crimp height on 1.7 mm silicone.** hand-tool-as-press's keyhole
   [htp w2 §8] and a5, through [ith ex §9], use an elliptical section:
   1.80 mm wide gives 2.46 mm, over the 2.4 mm envelope. force-and-form uses a
   section factor of 0.85, between ellipse and rectangle: 2.31 mm, inside it
   [ff w2 §5].
   - A B/F insulation crimp's section is squarer than an ellipse, so the
     ellipse is the upper bound [w3 §9].
   - The room under 2.4 mm is ~0.1–0.3 mm with no silicone flow, and more with
     collars.
   - a5's "floor and ceiling perhaps ~0.1 mm apart" is the pessimistic end.
   - The keyhole is right to copy a sliced kit housing rather than the
     catalog envelope.

6. **a5's "±0.15–0.5 mm of axial room"** in the 1.9 die holds for the
   insulation barrel, where overhang onto the jacket or the finished conductor
   crimp touches nothing. The conductor die is the constraining one (§2).

7. **a1b's campaign "each coupon pulled to failure on a capstan"** against
   ribbon-as-pallet's coupon calc [rap P §4]. At 100 N a 10–15 mm drum puts
   6–34 MPa of shear into the jacket at the drum entry, against 8–11 MPa
   silicone tensile strength.
   - ribbon-as-pallet is right for pulls to failure. v3 grips copper: a
     soldered far-end lug (500–750 N) or bare copper wrapped on a pin
     [sl w2 §6].
   - a6's capstan at 20 N is fine: ~1.2 N/mm at the drum entry for μ 0.3 on a
     10 mm post.

8. **The lance tip.** hand-tool-as-press and into-the-housing use 0.24–0.64 mm
   behind the box (CJT 2.44 ± 0.20 [ith ex §1]). This view's v1, v5 and v8 use
   xh-facts' nominal 0.4–0.6.
   - Theirs is the range to design to for anything in the neck.
   - v1's notched plate, v5's stop and v8's rear shoulder take 0.24–0.64.

9. **The neck.** hand-tool-as-press uses 0.2–0.5 mm [estimate, ith ex §1].
   v8 cites −0.7 to +2.0 mm of free gap from summing clone lengths
   [rap P §3].
   - Neither is a measurement. The sum shows the drawings do not constrain the
     neck; the 0.2–0.5 is a reading of how the parts look.
   - If genuine barrels are ~1.8 mm (item 4), genuine and clone necks may
     differ as well.

10. **a3's "±0.5 mm" slide-on capture** against this view's [sl w2 §2]:
    ±0.48–0.59 mm gathered, ±0.24–0.45 mm splayed (§2 above).

11. **Sourcing** [prime], against the figures in their files:

| Their figure | Prime on 2026-09-28 |
|---|---|
| PA-09 £37.99 (precisehandtools) | $38.99, next day, B002AVVO7K |
| SN-2549 $17.99–20.99 | $22.29, B01N4L8QMW |
| SN jaw set alone $4.99–9.99 | Not on Prime; IWS-0723K kit with a 2549 die $46.59 (thin) |
| 0.001 mm indicator $451–668 | Clockwise DITR-0105 $52.99, RS232; cable not on Prime |
| Disc springs for a 3.5 kN preload | Only a light stainless assortment |
| 5 kN button cell | 500 kg (4.9 kN) $74.99, thin |
| 5840-31ZY $18.50 | Greartisan 40 kg·cm self-locking worm, $26.99 |
| 40 × 10 × 1.0 mm leaf (a6) | No 1.0 mm strip on Prime. The 1095 shim assortment tops at 0.032 in (0.81 mm): at 40 × 10 × 0.8 the leaf gives 5.0 mm at 20 N and 750 MPa [htp w2 §7], inside blue-tempered 1095 |
| NEMA 17 Tr8×2 external nut | $27.78, thin, nut not anti-backlash |
| Laser-engraver gantry (a3) | LONGER Ray5 $268.99; head payload not stated |

---

## 4. Transfers

### From this view into theirs

- **The tack answers a6's and a1's two open questions** (W2). With the
  conductor in the contact before the tool, the first-tooth position and the
  neck blade stop deciding whether the crimp can be made. The neck still
  decides the per-crimp pull.
- **The station MCU owns the squeeze** (a1, a1b). The force wall, the
  ratchet-release detection (force collapse) and a heartbeat hold live on the
  ESP32 [w3 §2]. v7's stack table takes a1's squeezer as a station unchanged.
- **The write-ahead journal** gives a1b the guarantee the pawl gave (W8).
- **The silhouette and the box as its own roll gauge** turn a6's pull jig into
  a crimp-height station (W3). a1's side frame gains a number, not only a
  pass or fail.
- **Per-lot calibration** sets stops from the lot's own measured spread, not
  from the drawings' ±0.25 mm [htp calc §7]:
  - five contacts measured at the start of a contact lot, or every contact
    measured at T;
  - a6's Case 2 box-front stop, a2b's chute and W1's seat are all set this way.
- **Pictures before irreversible acts** (W5, W9): a backlit tip look before
  a2's feed and a3's slide-on, and the tip plate checked against the picture.
- **Grip copper, not jacket, for pulls to failure** (§3 item 7). Pair every
  proof pull with a destructive one on the same setting, so the proof load is
  known to be under the failure load [v3].
- **Asks on an unattended head.** a2's head holds one ribbon end, so a parked
  conductor would stall it. v7's per-conductor state lets the recipe skip it,
  finish the others and return. In a1b the doubtful conductor can be backed
  out; in a1 past the first tooth it cannot.

### From their view into this one

- **The side-entry jaw law narrows v8's list of hosts at C.**
  - The SN-2549 in a1's squeezer cannot be fed by v1's pallet at 5 mm pitch.
    Its jaw spans the neighbours' X positions at their height, and clearing it
    takes a stand-out of a + 2.7 mm.
  - v8's C list divides in two:
    - narrow-punch hosts, where the pallet feeds the die directly: W1's
      one-nest die set, and a knee press with a narrow punch;
    - the SN-2549 as sold, where the ribbon end leaves the pallet (W2).
  - v1's rule "punch body under ~8 mm wide at the neighbours' height" becomes
    ≤ 7.45 mm with crimped neighbours and 0.3 mm clearance [w3 §7].
- **v1's key sets copper at its root.**
  - The key root bends the conductor at R 24–60 mm [rap P §9], below the
    67–78 mm yield radius.
  - hand-tool-as-press's own elastic-plastic table keeps 47–81 % of a
    4–7 mm bend over 10 mm of free length [htp ex §1].
  - Every conductor that leaves v1's fan block therefore carries a kink of
    roughly 5–12° (that share of the key's 9.6–14.5° drop) 20–30 mm behind
    its contact.
  - For a gang insertion from the pallet (v6 or a2d-style), the front plate
    and late rear clamp are the squaring step. v6's grip within 2 mm of the
    contact is less exposed.
- **An eccentric with a disc stack moves v7's force limit into steel.**
  - With BDC set by geometry and the peak capped by the stack, v7's stroke on
    such a press keeps the early-fault stop and the slow last ~20° for trace
    resolution.
  - The crawl-from-a-taught-height rule, needed where an actuator drives into
    a hard stop, relaxes.
- **The handle's rising gain is a free crawl** [w3 §2]. v7's hosting table
  can mark squeezer stations as needing no crawl phase.
- **a6's foot and cord cell make a rung below v7's first motor** (W4). a6's
  keyhole is a mechanical hard fail.
- **The backed plate on the box's rear walls, relieved below for the lance,**
  is v1's and v5's lance-notched plate. It is one part with one governing
  measurement, the neck.
- **The lance-tip range** 0.24–0.64 mm replaces 0.4–0.6 in v1, v5 and v8
  (§3 item 8).
- **a1b and a5 are $22–39 v3 hosts** (W6). The grip position is a
  setting, not a length, so every v3 level needs v5's silhouette. The map
  drifts with wear, which v7's trend on the knee position at fixed force
  watches.
- **"The tool is the gripper"** (a3) names W1's weak joint. There, the T-to-C
  handover rides on a 0.2–1.5 N tack. The seat look at C exists to catch a
  contact that moved on the way.

---

## Questions this exchange adds for Derek

1. Photograph one kit contact from the side under the ELP beside a steel rule.
   How long are the conductor barrel and the window?
   - A barrel near 1.25–1.5 mm means a ~1.6–2.1 mm strip for kit contacts.
   - A barrel near 1.8 mm means 2.4 mm.
   - The same photo gives the neck, which decides the blade, the pull plate
     and the lance clearance for both views.
2. With the SN-2549 closed on nothing, clamp it in a vise by one handle and
   hang a known weight from the other grip. How far does the grip move?
   That is the handle stiffness that sets a1b's overshoot and a1's force
   curve.
3. When a die set is built (a4 or W1), one empty stroke with the button cell
   gives the frame's stiffness and the stack's knee, and so the eccentric's
   setting.
