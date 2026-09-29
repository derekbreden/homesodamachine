# A4b — One SN nest on a C-frame arm that reaches over the row

## Picture it

**Where things start.**
- **The ribbon end** lies flat in [a3](a3-tool-travels-to-ribbon.md)'s loom
  fixture: comb at 2.5 mm, tips ~8 mm proud, far end in the far-end block,
  front plate, rear clamp and housing slide on the fixture, a backlit camera
  on the tips.
- **The head** hangs from a3's gantry. It is a fist-sized steel C-frame whose
  throat opens toward the web (−Y).
  - **The lower arm** is 6–8 mm wide and 3–5.5 mm thick. It reaches 6–10 mm
    back from the C's spine, which sits in front of the row's noses.
  - **The anvil.** Set flush into a pocket at the arm's end is a one-nest
    anvil insert, cut with an abrasive disc from a spare SN-2549 lower jaw
    piece.
  - **The punch.** A guided ram in the C's upper arm carries the matching
    one-nest punch, cut from the upper jaw piece and held in a laminated
    laser-cut holder, as in [a4](a4-dies-in-a-die-set.md).
- **Drive and metrology.** A 2–2.5 mm eccentric on a small gearmotor drives the
  ram through a disc-spring cartridge preloaded to ~3.5 kN, with die contact
  set 0.17–0.28 mm above BDC so the stack engages every stroke (a4). A button
  load cell sits in the cartridge, an AS5600 on the shaft, and a re-touch
  indicator across the dies.
- **Contacts** wait on a wired post column, or as stubs.

**What moves.**
- The gantry (X, Y, Z) carries the head.
- A **lifter** finger in the fixture raises conductor *k* by 6.3–9.2 mm
  [calc w2 §4].
- The ram, once per crimp.

**What locates what.**
- "Fixed" is the fixture on the bench. The head touches off on its datum pin.
- **In the head,** the anvil insert locates the contact's floor, a1's
  insulated flap blade on the lower arm locates it axially, and the punch
  holds it at a light closure.
- **The conductor:** its comb slot for X, the lifter for Z, corrected from the
  tip picture; amber and green for Y.

**What drives and carries the crimp force.** The eccentric and ram push the
punch onto the anvil. The force goes down the lower arm to the spine and up
the C to the shaft bushings, closed inside the head. The gantry only positions
~1–1.5 kg. The disc springs let the dies bottom every stroke with the peak
capped at ~3.6 kN.

**How it knows it worked.**
- The tip picture before the slide-on.
- The die-force curve from the button cell, on the station ESP32.
- The re-touch height.
- Amber and green on conductor *k* only.
- A neck frame and a side frame. The head is open on both sides.

**What the person does.** What a3 hands back: clamps the ribbon end and lays
crossings; loads the post column; drops the housing on the fixture's slide;
unloads and labels. Once: the metalwork.

Sketch: [`../sketches/jaw-law-and-c-frame.svg`](../sketches/jaw-law-and-c-frame.svg).

## Steps it covers and what it hands back

**Covers:** placing the contact and conductor; crimping, with die force and
re-touch height on every crimp; identity; squaring and gang insertion (a3's
fixture).

**Hands back:** as a3, plus the metalwork: the C-frame plates (laser-cut
steel), the one-nest cuts in a jaw set, the laminated holders.

## How it relates

- Branch of [a4](a4-dies-in-a-die-set.md): a4's die set, eccentric and
  disc-spring stack go into a steel C-frame whose lower arm reaches back over
  the ribbon from in front of the tips, carrying one nest.
- The C-frame arm and its lift arithmetic come from into-the-housing's reading
  of a4 (its a4-c and C5, in its
  [exchange](../../../exchange/into-the-housing--on--hand-tool-as-press.md));
  it rides [a3](a3-tool-travels-to-ribbon.md)'s gantry.
- Converges with force-and-form's
  [f4](../../force-and-form/ideas/f4-crimp-head-goes-to-the-wire.md) (a head in
  a C-frame on a gantry) and borrowed-machines' b3 (applicator punches in a
  C-frame on a printer gantry). What this view adds: the cheapest die source,
  a spare SN jaw set cut to one nest; the side-entry jaw law as the reason the
  arm has to come from the front; the lift worked out with the neighbours'
  crimped noses in place.
- With the neighbours spread and narrowed, the arm goes under a pallet instead
  of over the row: [a4d](a4d-tongue-under-a-windowed-pallet.md).

## Major unresolved problems

- **Cutting a hardened SN jaw piece to one nest**, and a thin anvil insert,
  without cracking it (abrasive, wet, slow).
- **Aligning the punch on the ram to an anvil on a cantilevered arm.** The arm
  deflects 30–150 µm at load and its end tilts ~0.4–1° (slope = 1.5 ×
  deflection / length) [calc w2 §4]. With dies that bottom, the deflection
  costs travel and is part of the loop the die-contact setting is found for.
  The tilt makes the barrel ~10–25 µm higher at one end.
- **The lift still sets copper.** 6.3–9.2 mm on a 25–35 mm split gives a root
  radius of 22–63 mm [calc w2 §3]. The fronts are squared on the fixture as in
  a3.
- **Slide-on capture** as in a3: ±0.24–0.59 mm depending on splay, against a
  tip that may sit 0.28–0.69 mm off [sl w3 §10]. The tip picture corrects it.
- **A 1–1.5 kg head on a light gantry.**

## Why the arm comes from the front

- **The side-entry jaw law** [calc w2 §3; calc w3 §2]. A hand tool that makes
  upright crimps lies along the row. Its jaw half facing the ribbon, 6–12 mm
  deep (assumed), must be cleared by standing the working conductor out by
  *a* + 2.7 mm. A tool closing across the row makes rolled crimps.
- **A C-frame whose arm comes in along Y breaks the law.** Only the arm's
  thickness and the anvil lie under the working conductor, and the neighbours
  pass under the arm.
- **What sets the lift** [calc w2 §4]:
  - the neighbours' crimped boxes, up to ~1.35 mm above the conductor axis,
    since the arm passes over their noses;
  - 0.3 mm of clearance;
  - the arm, 2.6–5.5 mm thick for 1.5–3 kN at 6–10 mm long and 6–8 mm wide,
    at 1,000 MPa;
  - ~1 mm of anvil above the arm;
  - the contact floor to the conductor axis, ~1.05 mm.
- **In total** 6.3–9.2 mm (9.9 mm for a 13 mm arm), whatever shape the SN jaw
  has.
- **Where the neck sits.** The arm's length is set by the working contact's box
  (it sticks out ~2.5 mm ahead of the barrels) and by the spine clearing the
  neighbours' noses on the same line.

**Against a3's on-edge fixture:**
- if the SN jaw half is shallow (~6 mm), the two cost about the same stand-out
  (8.7 mm against 6.3–9.2);
- if it is deep (~12 mm), a4b's stand-out is ~5 mm less;
- a4b makes steel parts and cuts a hardened jaw, where a3 uses the tool as
  sold.

**A supported arm.** A post under the arm's end, rising between neighbours,
would remove the bending and bring the lift down to ~3 mm. That needs the
neighbours spread wider than 2.5 mm: i3's 5 mm shuttles, or change-the-question
c1's 3.4 mm half-rows. At 2.5 mm pitch there is 0.8 mm between insulation, and
no post fits. [a4d](a4d-tongue-under-a-windowed-pallet.md) takes the 3.4 mm
route with the arm under the pallet.

## The cycle, one conductor

1. **Pick.** The head takes a contact off the post column with the anvil ≥ 1 mm
   clear of its floor, steps down onto it, drops the flap and closes the ram
   to a light hold.
2. **Lift and look.** The lifter raises conductor *k* 6.3–9.2 mm; the camera
   takes the backlit tip; splayed tips go to a twist or a question.
3. **Present.** The head's lower arm slides in along −Y above the neighbours,
   nest on *k*'s corrected axis, ~2 mm ahead of the tip.
4. **Slide on.** The head moves −Y until green on *k*.
5. **Crimp.** One eccentric revolution, the dies bottoming. Then the re-touch
   reading.
6. **Release.** The ram lifts. The head drops ~1.5 mm, so the crimp lifts off
   the anvil. The head moves +Y and the arm withdraws from over the row. The
   crimp never moves rearward low in the nest.
7. **Lower.** The lifter returns *k* to its slot.

Then, per ribbon end, a3's squaring and the housing slide's gang push.

## Parts

- **Steel:** C-frame plates (laser-cut), laminated punch holder, anvil pocket
  insert, a spare SN jaw set cut to one nest (icrimptools.com $4.99–9.99
  [source]; the IWS-0723K kit is the Prime route [prime: B09CP8RV94]).
- **Drive:** a small self-locking worm gearmotor ($26.99 [prime: B07YBXB4N7])
  or a NEMA 17 planetary ($41.91, 3 N·m permissible [prime: B00QEUZ9EM]) on
  the eccentric; the head's mass decides.
- **Metrology:** button cell ($74.99 [prime: B0GZZRQC6Y]), AS5600, DITR-0105
  indicator ($52.99 [prime: B07888LX1R]).
- **Stack:** heavy-series disc springs from an industrial supplier (the Prime
  assortment is light duty).

## Rests on

- **[assumption]** SN dies bottom face to face, so arm deflection costs travel,
  not crimp height.
- **[assumption]** A one-nest SN punch crimps the same moving straight as on the
  tool's arc (the question force-and-form's f3 also carries).
- **[assumption]** 1,000 MPa is a safe working stress for a hardened tool-steel
  arm under thousands of slow cycles.
- **[estimate]** The neighbours' crimped boxes are ~2.4 mm tall with the floor
  at the jacket's underside [xh-facts §1].

---

Citation keys: **[calc w2 §n]** is [`../calc/wave2.out.txt`](../calc/wave2.out.txt);
**[calc w3 §n]** is [`../calc/wave3.out.txt`](../calc/wave3.out.txt);
**[sl w3 §n]** is machine-that-sees-and-learns'
[`w3_on_hand_tool_as_press.out.txt`](../../machine-that-sees-and-learns/calc/w3_on_hand_tool_as_press.out.txt);
**[prime: ASIN]** is a row of [`../../../sourcing/amazon-prime.md`](../../../sourcing/amazon-prime.md),
observed 2026-09-28.
