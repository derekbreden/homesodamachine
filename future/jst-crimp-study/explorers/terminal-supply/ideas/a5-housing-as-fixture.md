# a5 — The housing is the fixture: stage a bare contact in its cavity, crimp at the mouth, push home

Sketch: [`../sketches/a5-housing-as-fixture.svg`](../sketches/a5-housing-as-fixture.svg) (schematic;
plan with 2.5 mm pitch and 1.7 mm wire to scale, and a side view).
Numbers: [`../calc/terminal_supply.py`](../calc/terminal_supply.py) §8 [ts §8];
[`../calc/wave2.py`](../calc/wave2.py) §8 [w2 §8]; [`../calc/w3.py`](../calc/w3.py)
§2–4, §7, §9 [w3 §n]; into-the-housing's
[`exchange_terminal_supply_w3`](../../into-the-housing/calc/exchange_terminal_supply_w3.out.txt)
calc [ith-w3 X]; machine-that-sees-and-learns'
[`on_terminal_supply`](../../machine-that-sees-and-learns/calc/on_terminal_supply.out.txt)
§7, §8 [mtsl §n].

**Branches and related.**
- [x3](x3-stage-crimp-one-push.md) stages every other cavity, crimps each where it
  stands, then the rest, and pushes once for all: nothing stored in any conductor
  (with into-the-housing's i2b).
- into-the-housing's [i2](../../into-the-housing/ideas/i2-crimp-in-the-cavity.md)
  reached the same inversion from the insertion side; force-and-form's
  [f8](../../force-and-form/ideas/f8-narrow-press-at-the-housing-mouth.md) puts a
  narrow press at the mouth.
- The gravity variant crimps with [a3b](a3b-crimp-where-it-hangs.md)'s turned
  punch.

## Picture it

- **Where things start.** An empty XHP housing sits in a printed nest on an X
  stage, rear face toward the machine, keyed so it goes in one way. The web clamp
  with the splayed, stripped ribbon end rides the same stage, so the ribbon never
  moves relative to the housing once a contact is in [w3 §3]. The dies, the
  staging post and the camera are the fixed station. A light under the nest
  shines into the mating face, so each empty cavity shows the camera a bright
  square.
- **The nest floats.** It is located only in Y and floats ±0.2 mm in X and Z on a
  printed parallelogram flexure (into-the-housing i2). The seated wires resist that
  float with 0.01–0.09 N [ith-w3 G], so the fixed anvil, rising under the staged
  barrels, drags the housing to its own line.
- **Staging, by the post pulling the contact in.** A 0.64 mm post slides in
  through cavity k's front post opening, runs through the cavity and stands ~2 mm
  out of the rear face.
  - A nozzle drops a bare contact barrels-up into a small shuttle nest with a
    lance groove along its floor and a rear wall. The shuttle slides along the
    post's axis and its wall pushes the box onto the post's tip. A nozzle alone
    cannot push a box onto a post (63 mN against 0.2–2 N [mtsl §7]); the wall can.
  - The post withdraws toward the front and drags the box, by its grip, into the
    cavity's rear mouth. The camera looks along the row from the empty side,
    measures how deep the box sits, and stops the post at 1.5 mm. The lance tip is
    then ~0.9 mm outside the face; the conductor barrel sits 1.1–2.5 mm behind
    the face, the insulation barrel 3.0–4.5 mm [ts §8].
  - The post stays in the box through the crimp.
- **Staging, by gravity (variant).** The housing lies rear face up. The post rises
  from below through the front opening and stops with its tip where the box
  should stand. A contact dropped box-down into the mouth, from
  [a3](a3-hanging-rail.md)'s rail or a funnel, slides onto the tip and stops at
  1.5 mm; without the post it would slide to its lance's own stop, ~2.4 mm, too
  deep for an anvil. Look, move the post, look again sets the depth. The contact
  then stands vertical, so the crimp is a3b's turned crimp, with its sideways
  punch, fixed wall and finger.
- **The neighbours are cleared.**
  - **Seated side:** the wires of the contacts already seated leave the rear face;
    a printed finger sweeps them toward the done side, 20–35° from the face.
  - **Waiting side:** the conductors for the empty cavities wait lifted ~4 mm on a
    loft at the root. Fanned flat at 2.5 mm they would meet a 3.5 mm punch by
    0.10 mm and a 4.0 mm insulation punch by 0.35 mm [ith-w3 C; w3 §7].
- **Crimp at the mouth.** The fixed anvil comes in under the barrels just behind
  the rear face; the carriage lays conductor k into the open barrels, steered by
  the insulation edge as seen; the gate requires the staged contact's axis to
  match the cavity's within a threshold; the punch comes down onto a hard stop,
  with spring overtravel. The housing holds the box; the anvil carries the crimp.
- **Proof pull at the mouth, before the push.** A slotted fork drops behind the
  insulation barrel's rear edge (~4.5 mm behind the face at 1.5 mm staging), and
  conductor k is pulled −Y to 20 N while the camera watches its insulation edge.
  The contact is staged and unlatched, so the pull loads the crimp, not the
  lance.
- **Push home.** The anvil and punch withdraw and the post draws back out of the
  front. A fork behind the insulation barrel pushes the contact 5.25–5.45 mm
  [w3 §3; ith-w3 A], and the lance clicks behind its shoulder. The force trace
  shows the click, a 5 N pull confirms it, and the cavity's square stays dark.
- **Next cavity, in layer order.** The stage steps 2.5 mm (5.0 mm past J2's empty
  cavity 3). On J4 and J7 the upper-layer conductors (J4's 3V3 and GND, J7's GND)
  wait on the loft until last; their cavities lie at an end of the housing
  [into-the-housing i6].
- **What the person does.** Loads and unloads the housing and the ribbon end;
  keeps the contact supply filled, or stages contacts at the lit cavity when the
  machine asks; splays and strips.

## Where conductor k's length comes from

Conductor k is crimped 5.25–5.45 mm short of its seat and pushed home alone. With
one web clamp and every contact seated taut, it must carry that length at its
crimp as a 6–8 mm hump between the web and the die, beside the swept, seated
wires; the strands yield, so the hump keeps its shape, and the push draws it
straight with a few hundredths of a newton [ith-w3 B; w3 §3]. Ways to supply it:

- **A saddle presser** behind the die sets the hump before the crimp. Where the
  hump stands relative to the punch holder, ~1 mm from the housing face, is open.
- **The web follows the push:** the web clamp's Y advances 5.3 mm with the fork,
  so conductor k is straight at its crimp; the seated conductors bow while the web
  is forward and straighten when it returns (hundreds of such bows to strand
  failure against at most eight [w3 §3, estimate]); the waiting conductors, which
  advance too, wait lifted above the housing's top.
- **Nothing stored:** [x3](x3-stage-crimp-one-push.md).

## What locates what

| Moment | Reference | Located part |
|---|---|---|
| Staging | the staging post in the box; the camera's depth measure | contact, 1.5 mm into cavity k |
| The crimp | the fixed anvil; the floating nest lets the housing follow it | barrels on the anvil's line |
| Crimp height | hard stop between punch holder and anvil block | crimp |
| Proof pull | slotted fork behind the insulation barrel | contact |
| Push and seat | fork behind the insulation barrel; the housing's own shoulder | contact |

**The reference for "fixed" is the anvil block**, with the staging post slide,
the punch guide and the camera on the same base. The housing floats to the
anvil.

## The pivot in the mouth, and what the anvil must match

- **The staged box can pivot.** At 1.5 mm engagement, 0.05–0.10 mm of clearance a
  side lets the contact tilt ±3.8–7.6°, so the conductor barrel's centre, ~1.8 mm
  out, can sit ±0.12–0.24 mm off the anvil's height; at 1.0 mm engagement up to
  ±0.46 mm [mtsl §8].
- **The droop before the anvil arrives costs nothing.** A contact drooping in the
  mouth is lifted flat by an anvil at the cavity's floor line, without force on
  the box. The transition bends only when the anvil sits further from that line
  than the clearance allows; then the box is pressed against the mouth's wall and
  the barrels meet the anvil at an angle, and bend-up or bend-down follows, a JST
  shape fault [xh-facts §5].
- **So the tolerance is on the anvil's height against the cavity's floor line.**
  Two ways to hold it:
  - **the floating nest** (above): the anvil is the master and the housing
    follows, with no per-cavity measurement;
  - **a self-locking 2–3° steel wedge** under the anvil, set per cavity from the
    camera's measurement of the floor line. It is self-locking at friction
    coefficients of 0.10–0.15 under 3 kN and raises the anvil 35–52 µm per mm of
    travel [w2 §8]. With the nest floating, the wedge keeps one use: setting the
    fixed anvil or the hard stop once, or sweeping crimp height.
- **The post steadies the wing curl.** As the wings first curl, the punch's
  lead-in pushes sideways on the barrels; the post in the box and the mouth hold
  the box at two points. The soft post (~24 N/mm for 7 mm of free steel) does not
  fight the die.

## The lance and the anvil's front edge

The anvil's front edge must stand behind the lance tip and ahead of the conductor
barrel's front. Staged 1.5 mm deep, with the lance tip ~0.9 mm outside the face
and the conductor barrel starting ~1.1 mm behind it, that leaves ~0.06 mm
[ith-w3 D]. Across the clone drawings' ranges a flat anvil fits in about half the
cases (−0.30 to +0.10 mm on xh-facts' lance tip of 2.4–2.6 mm; −0.34 to +0.26 mm
on the 2.24–2.64 mm range) [w3 §4]. The other half needs a lance slot in the
anvil's front, 0.8–1.0 mm wide, with the conductor barrel's first 0.1–0.3 mm
carried on the slot's shoulders, ~1 mm from the housing face. One side
photograph of a kit contact settles it.

## The numbers that shape it

- **Staging depth** is a trade [ts §8; w3 §3]:

  | Staged | Lance tip | Conductor barrel behind face | Push after the crimp |
  |---|---|---|---|
  | 1.0 mm | 1.44 mm outside | 1.6–3.0 mm | 5.75–5.95 mm |
  | 1.5 mm | 0.94 mm outside | 1.1–2.5 mm | 5.25–5.45 mm |
  | 2.0 mm | 0.44 mm outside | 0.6–2.0 mm | 4.75–4.95 mm |

- **Neighbour clearance, seated side.** A 2.7 mm-wide conductor punch clears a
  seated neighbour's wire with no help. A 3.5 mm punch needs the neighbour moved
  0.3 mm sideways (17° at 1 mm behind the face, 8.5° at 2 mm); a 4.0 mm
  insulation punch needs 0.55 mm (29° at 1 mm, 15° at 2 mm) [ts §8]. Thin die
  walls are not the answer: a 0.5 mm wall under 100–300 N of side load reaches
  ~2,400–7,200 MPa in bending [ts §8].
- **Neighbour clearance, waiting side:** as above, the waiting conductors wait
  lifted, or narrow stepped dies (3.1 mm conductor step, 2.5–2.7 mm insulation
  step) clear them flat by +0.10 and +0.30–0.40 mm [ith-w3 C].

## What drives and carries the crimp force

As a2: a knife-set punch driven by an arbor press on a lead screw lands on a hard
stop on the anvil block; 0.8–2.6 kN closes through punch, barrels and anvil. The
housing carries none of it: the box, ahead of the anvil, sits in the mouth. The
push (5–25 N per contact [estimate]) goes through the fork into its slide,
reacted by the nest.

## How it knows it worked

The lit square (cavity found and empty); the staging depth and axis, measured
twice; the gate; stop and force; the after look; the proof-pull trace; the push
trace (rise, click, wall); the 5 N pull; the square going dark.

**Checking the person's staging.** When Derek stages a contact at the lit cavity,
the machine runs the same look on his placement (depth, axis, the right cavity by
the recipe) and proceeds only after it. A mis-staged contact is caught before the
stroke rather than by the tester.

## Why stage the bare contact

- Every other arrangement inserts a crimped contact on a floppy wire; the prior
  art identifies that transfer as where failures happen [prior-art, Sogang;
  Cellios].
- Here the contact enters its cavity while it is still a rigid 0.04 g part, and
  what remains of insertion is a short straight push of a box already in the
  right hole.
- The housing is the most accurate reference for where the contact must end up,
  and here it also holds the contact for the wire and the crimp.

## Problems and repairs

1. **Staging all cavities at once.** Open clone wings 2.46–3.0 mm wide collide at
   2.5 mm pitch, and ordinary dies cannot fit between staged neighbours. Repair
   here: one cavity at a time. Every other cavity at once, with narrow dies, is
   [x3](x3-stage-crimp-one-push.md).
2. **Crimping beside a seated neighbour.** Repair: sweep the seated wires (above).
3. **The waiting side.** Repair: the loft, or narrow stepped dies.
4. **Conductor k's 5.3 mm** at its crimp (above).
5. **The staged box pivots.** Repair: the floating nest (or the wedge); the post
   steadies the curl; the gate checks the axis. The clearance itself is unmeasured
   (one kit contact in one kit housing, photographed from the side at 1.5 mm, then
   nudged with a needle).
6. **Staging a 0.04 g contact without a hand.** Repair: the post takes the contact
   from the shuttle and pulls it in; or, rear face up, gravity onto the post tip as
   a depth stop. The mouth's friction on an entering box, and where inside the box
   the leaves first touch a post, are found on the first contact.
7. **The lance window.** Repair: a lance slot in the anvil.
8. **Cavity index is conductor index** only on the eight one-layer looms. Repair:
   layer order for J4 and J7.

## Steps covered, and what it hands back

- **Covers:** placing the contact, first into its cavity, then on the conductor;
  holding; crimping; a proof pull before insertion; insertion; pin order in
  layers; seat checks.
- **Hands back:** staging supply (a nozzle and shuttle nest, a3's rail, or Derek
  at the lit cavity when asked); splay and strip; housing load and unload; the
  continuity test.

## Printed and bought

| Part | Printed / bought |
|---|---|
| Floating housing nest and web clamp on one X stage, neighbour-sweep finger, loft, fork holder, shuttle nest with lance groove, funnel | printed |
| Light under the nest | LED and a diffuser, or 1 mm PMMA fibre (AZIMOM, Prime, $10.89) |
| Staging post and its slide | 0.64 mm square pin (uxcell 25 mm-pin headers, Prime, $15.49; pin cross-section not stated) on a small lead-screw stage |
| Anvil and punch | OTP XH knife-set pieces in holders narrow enough to work within ~1 mm of the housing face, the anvil with a lance slot if needed (as [a2](a2-strip-indexer.md)) |
| Anvil wedge (optional) | ground 2–3° steel wedge on a small stepper ([`../sourcing-requests.md`](../sourcing-requests.md) #22) |
| Press, lever drive, hard stop | as a2 |
| Fork load cell | ShangHJ 5 kg bar cell with HX711 (Prime, $9.99) |

## Contribution

The inversion: insert first, crimp second. The contact meets the housing while it
is rigid and has no wire, and the housing holds it for the crimp. What remains of
insertion is a short straight push, and the anvil's height against the cavity's
floor line is the one tolerance that matters.

## Major unresolved problems

- **Crimping within ~1 mm of the housing face** with dies narrow enough, and the
  lance window there.
- **Conductor k's 5.3 mm** at its crimp.
- **The mouth's clearance, the rear-mouth geometry and the front-wall thickness,**
  read from no document here.
- **Whether the staged contact stays square as the wings first curl,** with the
  post in.
- **Two-ribbon housings (J1, J4, J7):** the second ribbon's conductors arrive past
  the first ribbon's swept wires; layer order handles the crossings.

## What each conclusion rests on

- **Facts [mfr, source]:** housing height and polarization [xh-facts §3]; clone
  contact dimensions and lance position [xh-facts §1]; JST's shape faults
  [xh-facts §5]; Prime listings.
- **Calculations [calc]:** staging depth and die clearances [ts §8]; wedge [w2 §8];
  push, stored length, stage drag, bow fatigue [w3 §3; ith-w3 A, B]; waiting side
  [ith-w3 C; w3 §7]; lance window [w3 §4; ith-w3 D]; floating nest [ith-w3 G];
  pivot [mtsl §8]; nozzle [mtsl §7]; force ladder [w3 §9].
- **Estimates:** barrel positions from the front read from clone drawings; die
  wall widths of 2.7–4.0 mm; wedge friction 0.10–0.15; that silicone neighbours
  can be swept 20–35° at the face without harming their fresh crimps.
- **Assumptions:** the front wall is 0.8–1.0 mm; mouth clearance 0.05–0.10 mm a
  side.
