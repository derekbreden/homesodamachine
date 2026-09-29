# A6 — The foot-closed jig bench: today's hand procedure, a stop for every placement, no motor

## Picture it

**Where things start.**
- A baseplate at the bench's front edge carries five jigs in a row, left to
  right, and a small electronics box.
- The ribbon is cut to loom length. Its far end is stripped (it is stripped
  anyway for its Faston, ferrule or IDC [repo: `cable-assemblies.md`]) and
  pushed into the far-end block, a push-in terminal strip or Wago 221s wired
  to an ESP32. It stays there until the loom is finished.
- Contacts are the kit's loose ones in a dish, or SXH strip snipped into
  one-pitch stubs.

**The five jigs.**
1. **End jig.** A printed channel 0.2 mm under the ribbon's width, marked edge
   against its wall (ribbon-as-pallet's channel, after AMP US 4,230,008). A
   slot across it guides the KATA flush cutters, so the cut end is the datum.
   A printed line gives the split length, and a printed stop clipped to the
   Klein 11063W's jaw face gives the strip length, set from one measured
   contact of the lot in use (below).
2. **Crimp jig.**
   - The SN-2549 lies on its side in a cradle, lower handle strapped in a
     saddle. [a1](a1-squeezer-cradle.md)'s locator plate sits on the lower
     jaw's M4 screw.
   - A printed opening limiter between the handles stops the tool opening
     wider than loading needs.
   - A Dyneema cord runs from a clevis on the upper handle's grip, down over a
     608-bearing pulley, through the baseplate to a **two-stage foot treadle**
     under the bench.
3. **Pull-and-look jig.** A backed slotted steel plate takes the crimp's box
   by its rear walls, relieved below for the lance. Under the conductor barrel
   a hardened blade stands on edge; beside it a ground roll flat carries the
   box's floor under a light spring finger; a backlight on the far side and
   the ELP across give a silhouette. The wire wraps a capstan post on a lever,
   and the lever stops against a spring-steel leaf that closes a switch at
   20 N.
4. **Keyhole gauge.** A stencil-steel plate cut to the cavity's section, with
   a notch for the lance and a slot out to one side narrower than the wire.
5. **Insertion nest.** into-the-housing's
   [i5](../../into-the-housing/ideas/i5-person-inserts-on-a-sensing-nest.md):
   the XHP plugged onto a real XH header whose posts are ESP32 inputs, a lit
   cavity, and a spring-limited lever with a slotted blade.

**What moves.** The person's hands move the ribbon and the contacts. The
person's foot moves the treadle. Nothing else moves, and there is no motor.

**What locates what.**
- **The ribbon end:** the channel wall and the cut slot.
- **The contact:** "fixed" is the lower jaw. The contact sits in the nest, its
  box against the front stop and a thin insulated blade dropped into its neck.
  With strip stubs, a sprung pin in the pilot hole locates it instead
  (terminal-supply's
  [a2c](../../terminal-supply/ideas/a2c-strip-locator-for-hand-tool.md)).
- **The conductor:** sideways, the printed funnel on the jaw's rear face and
  then the wings. Axially, the strand tips reach the blade's bare rear face,
  which lights a lamp. Where the neck is too short for a blade, the ELP camera
  shows the brush on the Mac screen against a drawn line.
- **At the pull-and-look jig:** the blade sets the height reference, the roll
  flat and the box's own silhouette set roll, the plate sets the axial
  position.

**What drives and carries the crimp force.**
- The foot presses the treadle. At a 2:1 treadle the toe needs at most
  ~120 N over ~60 mm of pedal travel [calc w2 §5].
- The cord carries at most a hand's grip force, ~220 N, to the upper handle.
- The tool's linkage and dies do the forming, and the crimp force closes jaw
  to jaw inside the head, as it does in the hand.
- **Half-press:** the pedal meets a light spring step set at the ratchet's
  first tooth. The tool now holds the contact by itself, and the foot comes
  off.
- **Full press:** the pedal is pushed through the step, and the ratchet runs
  to its release.

**How it knows the crimp worked.**
- **Identity.** The ESP32 drives conductor *k* at the far end. The amber lamp
  lights when *k*'s strands touch the contact (the tool), the green one when
  they touch the blade. Any other conductor lighting buzzes: the wrong
  conductor is in the tool (J2's trimmed #3, J4's and J7's crossings).
- **The ratchet's full cycle.** It has to release before the tool opens.
- **Optional force log.** An S-type load cell in the cord line and an AS5600
  on the pulley give force against cord travel for every foot-closed crimp
  [calc w2 §6].
- **The pull-and-look jig:** a roll-corrected crimp height, the bellmouth,
  the brush, the insulation edge in the window, and a 20 N proof pull watched
  by the camera.
- **The keyhole:** a hard fail that needs no judgement.
- **At insertion,** i5 pairs conductor *k* with post *n* and tugs.

**What the person does.** Every motion, each against a stop.
1. Cut the end in the end jig, split to the line and strip against the stop.
2. For each conductor:
   - drop a contact on the locator and flap the blade down;
   - half-press;
   - bend the conductor out of the row and feed it through the funnel until
     the green lamp lights;
   - full press;
   - lift the crimp off the anvil, then draw it back;
   - drop it in the pull-and-look jig and pull until the buzzer;
   - pass it nose-first through the keyhole.
3. Insert at i5 into the lit cavities.
4. Label.

Sketch: [`../sketches/a6-jig-bench.svg`](../sketches/a6-jig-bench.svg).

## Steps it covers and what it hands back

**Takes from the person:**
- every judgement of position: the contact's axial position, the depth, the
  strip length, the cut line;
- conductor identity and pin order;
- the grip force;
- a pull, a crimp-height reading and a fit check on every crimp;
- with the cord cell, a force log per conductor.

**Hands back:** every motion: cutting, splitting, stripping; placing each
contact on the locator; steering each conductor; both presses, the pull and the
gauge; starting each contact into its cavity and pulling the lever; labelling.

**Person time** [calc w2 §9, estimates]: today ~25 s a crimp, ~22 min for 53;
on the bench ~35 s with the pull and the keyhole (~31 min), ~19 s without
(~17 min). The bench does not save minutes. It makes the crimp the same every
time, and it tests what today is only looked at.

## How it relates

- a1's squeezer with the motor replaced by a foot. Every jig carries the
  interface a motor takes later (table below).
- Branches that put the contact on the wire before the tool, so the blade and
  the first-tooth question go away:
  - [a6b](a6b-flags-by-hand-foot-crimp.md), flags made by hand, the SN-2549
    pre-forming its own contacts;
  - [a6c](a6c-flags-by-machine-foot-crimp.md), flags made by a machine that
    places and tacks every contact.
- Combines into-the-housing's
  [i5](../../into-the-housing/ideas/i5-person-inserts-on-a-sensing-nest.md)
  (its C3 pairing), ribbon-as-pallet's channel, and machine-that-sees-and-learns'
  [v5](../../machine-that-sees-and-learns/ideas/v5-inspection-booth.md) booth
  folded into the pull jig (W3 in its
  [exchange](../../../exchange/machine-that-sees-and-learns--on--hand-tool-as-press-w3.md)).
- The force log and the booth readings are rung 0.5 of
  machine-that-sees-and-learns'
  [v7](../../machine-that-sees-and-learns/ideas/v7-the-run.md) ladder (W4):
  labelled data from Derek's own crimps before any motor exists.

## Major unresolved problems

- **The neck on a kit contact.** Its length decides whether the depth stop is
  a blade or a camera line [calc w2 §1], and whether a flat pull plate fits
  (below). 0.2–0.5 mm is a reading of how the parts look, not a measurement;
  the clone drawings do not constrain it.
- **Where the first ratchet tooth falls.** It has to be at or after "contact
  held" and before "wire can no longer enter", and the treadle's step is set
  to it. The same question is open in a1.
- **The Klein on this silicone.** The end jig makes the strip length
  repeatable. It does not make the cut clean.
- **Far end first.** The far end has to be stripped before the XH end is
  crimped. That is also the recovery order the digest argues for.
- **Per-crimp pulls on loose contacts** need either a neck of ~0.35–0.5 mm for
  a flat plate or a stepped plate (below); otherwise pulls are by sample.

## Why a foot

Today one hand holds the tool and the other feeds the wire. The contact is
placed by eye before the first click traps it.

With the tool fixed and the foot closing it:
- both hands are free for the one fine act, holding the ribbon and steering
  one conductor into a 1.8 mm barrel;
- the ratchet makes the foot sufficient. At the first tooth it holds without
  the foot, and at the end it releases by itself. The foot needs no finesse
  beyond the step.

Crimp height does not change. The same dies close to the same bottom, or the
ratchet releases at the same tooth, whoever pushes.

The foot also closes the one gap in Derek's tools: nothing on the bench frees
the second hand. A lever press (the WEN drill press quill) gives force but
still takes a hand.

## Each jig, and the motor it takes later

| Jig this week | What it fixes in today's procedure | What drives it later | Developed in |
|---|---|---|---|
| End jig | Cut, split and strip length judged by eye | The Klein in a squeezer; a laser score | [a2c](a2c-one-baseplate-strip-crimp-insert.md); borrowed-machines b4 |
| Crimp jig: cradle, locator, limiter | Contact placed by eye; tool held in a hand | Unchanged parts. The cord goes to a worm winch, or the cradle takes a1's NEMA 17 pusher | [a1](a1-squeezer-cradle.md), [a1b](a1b-pawl-out.md), [a2](a2-ribbon-to-fixed-tool.md) |
| Treadle | Grip force from the hand that should be steering | The winch on the same cord | a1's winch branch |
| Far-end block and ESP32 | Nothing knows which conductor is in the tool | The same ESP32 runs the motors | a1 to a3 |
| Cord load cell and pulley AS5600 | No record of any crimp | The same sensors under a motor | a1 |
| Pull-and-look jig | No pull test and no crimp height at all | A servo or stepper on the lever, the leaf switch kept as the limit | machine-that-sees v5; a2's pull slot |
| Keyhole gauge | A crimp that will not fit found only at the housing | The keyhole on the machine's unload path | [a1b](a1b-pawl-out.md) |
| i5 nest | Pin order by eye, latch by feel | A servo on the lever; i3's housing press | into-the-housing i5, i3 |

The first build answers the measurements every later machine needs: the neck,
the first tooth, the jaws against a light, and the grip force read on the cord
cell.

## The treadle

- **Pedal.** Heel-hinged under the bench front, ~250 mm to the toe; the cord
  attaches at ~125 mm, a 2:1 ratio; printed or plywood, with a door hinge.
- **Forces and travel** [calc w2 §5]:
  - grip 100 / 175 / 220 N → toe 55 / 97 / 122 N;
  - cord travel = grip travel, 51–56 mm with the tool's full opening, or
    ~25–35 mm with the opening limiter [estimate];
  - at 2:1 that is ~60 mm of pedal travel.
- **Who can do this.** Leg-driven pedals take several hundred newtons.
  Frequent ankle work is comfortable to tens of newtons [estimate]. A unit is
  ~106 presses over half an hour, which is light work.
- **The two stages.** A sprung pin under the pedal gives a step the foot
  feels. A screw sets its height once, so the pedal at the step equals the
  first ratchet tooth. Pushing through it takes a stronger spring's worth more
  force. It is a camera shutter's half-press made for a foot.
- **Returns.** The tool's own spring opens it. A light spring returns the
  pedal, and the cord goes slack while the ratchet holds.
- **Opening limiter.** A printed block on the lower handle that the upper
  handle rests on when open, sized so the open jaw passes the contact with its
  lance clear: 3.35–4.10 mm, plus ~1 mm to lift the crimp before drawing it
  back [ith ex §2]. The jaw gap against grip span is unmeasured.
- **Fingers.** The foot is far from the pinch. At the full press the hands
  hold the ribbon 20–30 mm behind the jaw's rear face, and the kilonewtons
  exist only inside the nest, which the contact fills. This is the exposure
  of today's hand tool.

## The locator: two cases, decided by the neck

The neck is the short floor strip between the box's rear face and the conductor
barrel, 0.2–0.5 mm long [estimate, ith ex §1]. Four things compete for it: the
box's rear face; anything that stops the strands; the brush, wanted at
~0.1–0.2 mm past the barrel; the lance tip, hanging 0.6–0.9 mm below the floor,
0.24–0.64 mm behind the box.

**Case 1: transition ≥ ~0.3 mm. A thin insulated blade** [calc w2 §1].
- **Stack.** 0.10 mm steel feeler leaf, with polyimide tape or insulating
  lacquer on its front face and slot edges; 0.13–0.15 mm in all. That leaves
  0.15–0.38 mm for the brush at transitions of 0.3–0.5 mm.
- **Front face.** Its insulated front face rests on the box's rear walls,
  sides and top.
- **Slot.** It straddles the neck strip within ~0.05 mm a side, so no
  0.08 mm strand passes it.
- **Tines.** They stop at the strip's lower face, so the lance hangs below
  and between them untouched.
- **Rear face.** Bare steel, and an electrode. Because the front face is
  insulated from the contact, "strands at the blade" (green) is a different
  event from "strands on the contact" (amber).

**Case 2: transition ~0.2 mm. No blade.**
- **Strip stubs.** A 1.45 mm pin in the stub's pilot hole and a fence on the
  carrier edge: terminal-supply's a2c clip on this tool, about ±0.035 mm plus
  the stamping's hole-to-barrel tolerance. Stubs come from snipping cut strip
  with the KATA cutters onto a printed tray.
- **Loose kit contacts.** Box nose against the front stop. The stop is set
  once per contact lot by a screw, from five contacts of that lot measured
  under the ELP (box front to conductor-barrel rear), not from the clone
  drawings' ±0.25 mm [calc §7].
- **Depth.** The ELP on a stalk, looking across the neck from the open side,
  with a line drawn on the Mac's live image at the wanted brush. The person
  feeds until the strands cross it. The amber lamp still gives identity.

**Case 3: the contact arrives already on its wire** — the flag branches
[a6b](a6b-flags-by-hand-foot-crimp.md) and [a6c](a6c-flags-by-machine-foot-crimp.md).

In every case the crimp leaves in the insertion orientation (barrels up, lance
down), because the person bends the working conductor out of the row by hand.
The side-entry jaw law ([a3](a3-tool-travels-to-ribbon.md)) costs a hand
nothing.

## The strip length follows the contact

JST's 2.4 mm [mfr S6] fits a genuine conductor barrel of ~1.8–2.05 mm. On the
clone drawings' barrel (1.25–1.5 mm) and window (0.5–0.8 mm), JST's own rule
S = E + A/2 + brush gives 1.60–2.10 mm, the KONNRA clone spec [calc w3 §7;
sl w3 §4]. A 2.4 mm strip on a clone-shaped kit contact puts bare strands
0.2–0.5 mm into the insulation barrel in most cases; a 1.6 mm strip on a
genuine contact puts jacket under the conductor barrel. Neither shows in the
keyhole, and a pull may pass either. So:
- the Klein's clip-on stop is set from one contact of the lot, its conductor
  barrel E and window A measured from the side under the ELP;
- the pull-and-look jig reads the insulation edge in the window on every
  crimp, where either error shows.

## Taking the crimp out: lift first

A crimp drawn straight back while it lies in the anvil's cradle drives its
lance tip into the anvil's front face. It either stalls or folds the lance flat
before the housing ever sees it.
- The person lifts the crimp 1–1.7 mm off the anvil first [ith ex §2], then
  draws it back. The opening limiter leaves room for that.
- A printed ramp on the locator plate's rear edge can make the lift part of
  the draw: the insulation barrel rides up it as the wire is pulled.

## The pull-and-look jig

**Pull.**
- **Plate.** Spring steel on a printed block, bearing on the box's rear walls
  above the floor and relieved below, where the lance hangs. 20 N on those
  walls is ~16 MPa, 39.2 N is ~31 MPa, against 400–600 MPa for phosphor bronze
  [calc w2 §2].
- **What has to fit the neck.** A flat 0.3 mm plate with a slot for the neck
  strip has cantilevered tines between the box and the crimped barrel, so it
  fits only at transitions of ~0.35–0.5 mm, the same measurement that decides
  the blade [sl w3 §2]. Three ways past it:
  - **a stepped plate:** thick and backed wherever it bears on the box outside
    the crimped barrel's width (the barrel is ~1.4–1.6 mm wide against a
    1.85–1.95 mm box, so the side walls' rear edges stand 0.12–0.28 mm outside
    it) and above the barrel's height (~1.1 mm); thin only in the tongue that
    faces the barrel's front edge, which bears nothing. It needs the box's rear
    edges to be a clean step, not a sloped transition [calc w3 §3, estimate];
  - **a backer over the crimped barrel** reaching down to ~1 mm above the
    floor, which shortens the unbacked tines to ~1 mm: a 0.15–0.3 mm plate then
    sees ~100–630 MPa, inside hardened spring steel, so a 0.15 mm plate fits a
    0.2 mm transition [calc w3 §3, estimate];
  - **pulls by sample** for loose contacts if neither fits.
- **Capstan.** A printed Ø10 mm post on a lever arm. Two to three turns of
  silicone hold 20 N with under 0.5 N at the tail for μ ≥ 0.3 [calc w2 §7],
  ~1.2 N/mm at the drum entry, well under the jacket's strength.
- **The limit.** The lever meets a spring-steel leaf that closes a switch at
  20 N. From the 1095 blue-tempered shim assortment (to 0.032 in), a
  40 × 10 × 0.8 mm leaf deflects 5.0 mm at 20 N at ~750 MPa [calc w2 §7], inside
  hardened 1095. A hard stop just past it keeps the person from overloading
  the crimp. A digital luggage scale on a hook is the simpler form.

**Look** (machine-that-sees-and-learns'
[v5](../../machine-that-sees-and-learns/ideas/v5-inspection-booth.md)).
- A hardened blade stands on edge under the conductor barrel: a micrometer's
  blade anvil turned sideways.
- A ground roll flat under the box's floor and a light spring finger set roll
  from the square box, not the round insulation. The silhouette needs roll
  within ~1–2°; the box's own front section grows 32–34 µm per degree of roll
  in the same frame, so it corrects the rest [sl w2 §1].
- The ELP across, a backlight behind, and a gauge pin in frame give crimp
  height, bellmouth, brush length and the insulation edge in the window.
- The camera watches the edge during the pull: a crimp that slips shows it.

## The keyhole

- **The plate** [calc w2 §8]: the cavity's section, taken from a kit housing
  sliced and measured under the ELP, not from the 1.95 × 2.4 mm catalog
  envelope; a notch on the floor side, so the lance passes without folding; a
  1.3–1.5 mm slot out to one side.
- **Use.** The crimp goes through nose first, all the way. The 1.7 mm silicone
  wire then squeezes out sideways through the slot, which the 1.9–2.0 mm crimp
  cannot. Nothing is drawn back over the lance.
- **What it stops:** flared wings, strands outside a barrel, a spike of tab, a
  half-crimp.
- **What it misses:** crimp height, and strands inside the insulation barrel.
- **On 1.7 mm silicone.** The closed insulation barrel stands 2.03–2.46 mm tall
  for closed widths of 1.95–1.80 mm, the ellipse being the tallest reading
  [sl w3 §9]. The gauge is where Derek first sees whether the SN-2549's
  insulation nest makes a crimp that fits.
- **Source.** JLCPCB cuts 304 stencils from $3 and ships most within 24 h
  [source: jlcpcb.com/pcb-stencil, 2026-09-28]. The thickness options were not
  listed on the page [assumption: 0.10–0.20 mm, common SMT stencils]. Two
  stacked leaves, or a filed feeler leaf, do the same job.

## Insertion: i5 with the same far-end block

On the jig bench, into-the-housing's i5 is the last jig:
- **Wiring.** The far-end block drives conductor *k*, and the header's post
  *n* reads it when *k*'s box arrives. So the ESP32 records "conductor *k* in
  cavity *n*", not only "a contact in cavity *n*".
- **Pin-order errors** are caught as they happen: J2's post 3 must never
  close; J4's and J7's crossings are checked against the pin map; J4 and J7
  cannot be swapped, because the pairing names the conductors.
- **The blade.** i5's blade needs no electrical path through the tin.

## The record, before any motor

Per conductor, the runner on the Mac files: the cord cell's force against the
pulley's travel for the foot-closed crimp; the pull-and-look jig's height,
bellmouth, window and pull; the keyhole's pass; and i5's conductor-to-cavity
pairing, under unit, loom and pin. That is labelled data from Derek's own
crimps for machine-that-sees-and-learns' v7 force envelope and v3 windows,
before any motor exists. The keyhole is a hard-fail band that needs no judge.

## Parts

**Printed:** the end jig; the cradle, saddle and strap; the opening limiter;
the locator plate and flap; the funnel; the pulley bracket and handle clevis;
the treadle, or plywood; the pull block, capstan lever, roll flat and keyhole
holder; the ELP stalk; i5's frame.

**On hand** [repo: `tools.md`]: SN-2549; Klein 11063W; KATA cutters; ESP32
DevKitC; ELP camera; NEIKO caliper.

**Bought, small:**
- feeler leaves 0.10 mm (Hotop 17-blade set, $8.99 [prime: B08GLN7K1R]);
- polyimide tape (Amazon, Prime to be confirmed);
- 1095 blue-tempered shim assortment for the leaf and the pull plate
  ($53.39 [prime: B00065V062]);
- a 20 mm M4 screw; a 608 bearing; 1.5 mm Dyneema cord ($17.95 [prime:
  B07BKQLFRB]); compression springs ($6.99 assortment [prime: B0BVTDP29W]); a
  door hinge;
- Wago 221-415s ($28.00 for 25 [prime: B0107SYYGU]);
- LEDs and a buzzer;
- optionally an S-type cell with HX711 (the Prime S-type row is 100 kg,
  $37.71, no amplifier [prime: B077YHNNCP]; HX711 $11.50 [prime: B079LVMC6X]),
  an AS5600 ($7.99 for three [prime: B094F8H591]) and a digital luggage scale
  (Amazon, Prime to be confirmed);
- a backlight (A5 light pad, $16.99 [prime: B08QJ2JMHZ]) and a gauge pin
  (Accusize set [prime: B00JOLCSF6]).

**From distributors:** B4B/B5B/B6B/B7B/B9B-XH-A headers and a small PCB for i5
(into-the-housing sourced them; the CQRobot kit carries B2B–B4B); a JLCPCB
stencil for the keyhole and blades.

## Rests on

- **[Derek, via repo]** The SN-2549 holds a contact at its first tooth with a
  stripped conductor still able to enter: today's procedure closes one click
  and then feeds the wire.
- **[estimate]** The kit contact's neck is measurable under the ELP, and the
  lance hangs below the floor strip, narrower than it [ith ex §1; xh-facts §1].
- **[assumption]** The Klein takes a clip-on length stop on its jaw face.
- **[calc]** Grip force ≤ ~220 N, from Derek crimping by hand [calc §1].
- **[assumption]** The first tooth is far enough from the second for a foot to
  stop between them. The step makes this a setting, not a skill.

---

Citation keys: **[calc §n]** is [`../calc/hand_tool_press.out.txt`](../calc/hand_tool_press.out.txt);
**[calc w2 §n]** is [`../calc/wave2.out.txt`](../calc/wave2.out.txt);
**[calc w3 §n]** is [`../calc/wave3.out.txt`](../calc/wave3.out.txt);
**[sl w2 §n]** and **[sl w3 §n]** are machine-that-sees-and-learns'
[`wave2.out.txt`](../../machine-that-sees-and-learns/calc/wave2.out.txt) and
[`w3_on_hand_tool_as_press.out.txt`](../../machine-that-sees-and-learns/calc/w3_on_hand_tool_as_press.out.txt);
**[ith ex §n]** is into-the-housing's
[`exchange_hand_tool_as_press.out.txt`](../../into-the-housing/calc/exchange_hand_tool_as_press.out.txt);
**[prime: ASIN]** is a row of [`../../../sourcing/amazon-prime.md`](../../../sourcing/amazon-prime.md),
observed 2026-09-28.
