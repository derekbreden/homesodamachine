# A4d — One SN nest cut to a tongue, crimping in the row under change-the-question's windowed pallet

## Picture it

**Where things start.** change-the-question's
[c1c](../../change-the-question/ideas/c1c-crimp-in-the-row.md) layout on one
baseplate:
- **One X slide** on an MGN12 rail ($20.49 [prime: B07ZVFFXQZ]) with a NEMA 17
  lead screw, carrying as one body: the web clamp with its side fence and tip
  stop; **pallet A** and **pallet B**, each a row of printed carriers at
  3.4 mm on a small swing arm; and the **housing nest** in front.
- **A carrier** holds one contact: a 2.0 mm box slot with a lance groove
  running out through the open front, a pocket floor 0.1–0.2 mm below the
  anvil's top, and a window underneath.
- **Contacts arrive narrowed**, so open neighbours never clash:
  - pre-formed in loom-order sticks, by [a6b](a6b-flags-by-hand-foot-crimp.md)'s
    click in a second SN-2549 (insulation barrel 1.8–2.05 mm wide) or by
    change-the-question's [c6](../../change-the-question/ideas/c6-pre-form-the-contact.md)
    keyhole pre-former (1.96–2.14 mm);
  - or open kit contacts narrowed on the wire by
    [c1b](../../change-the-question/ideas/c1b-tack-first.md)'s tack comb.
- **The press** is [a4](a4-dies-in-a-die-set.md)'s die set, one nest, in a
  fixed steel C:
  - the C's **spine stands in front of the housing nest**, its arms reaching
    back 20–26 mm over and under the nest to the working carrier;
  - **punch:** one XH nest cut from a spare 2549 jaw to a **tongue ≤ 4.45 mm
    wide**, narrow for 2.1–2.3 mm above the anvil beside c6 keyholes, or
    2.6–3.3 mm beside tool-made pre-forms [htq §5; calc w3 §6];
  - **anvil:** a 3 × 3 mm HSS blank ($9.99 for five [prime: B08ZSMB557])
    ground to **≤ 1.90 mm** so it passes the carrier's 2.0 mm pocket, fixed in
    a die block, over a button cell and a disc stack preloaded to ~3.5 kN;
  - a **hard stop** between the ram's holder and the anvil block sets crimp
    height;
  - a 2–2.5 mm eccentric on the ram, turned by the bench NEMA 23 through a
    10:1 planetary ($48 [prime: B0BPGMZ5LM]) or the self-locking 12 V worm
    gearmotor ($26.99 [prime: B07YBXB4N7]);
  - a 0.001 mm indicator across ram holder and anvil block (DITR-0105, $52.99
    [prime: B07888LX1R]).
- **Electrodes.** The anvil block and the punch are wired. The ribbon's far end
  is in a far-end block, or on c5's slip ring through the spool (6-circuit,
  $9.99 [prime: B07H2SRMXP]).

**What moves.** c1c's cycle, one ribbon end:
1. The ribbon end, stripped flat by another station, is clamped; interlaced
   jaws split odd conductors into plane A and even into plane B.
2. Pallet A swings up under plane A, its pockets filled from a stick. A
   presser comb snaps every jacket into its pre-formed barrel and lays every
   strand bundle in its U (or the tack comb closes the insulation barrels in
   two passes).
3. The slide steps carrier *k* over the anvil: the pallet's swing arm lifts
   1–2 mm to step past the fixed anvil and settles back, so the anvil alone
   sets the contact's plane. The ram closes to the stop. The slide steps
   3.4 mm to the next.
4. Row A parks down and back; row B is laid and crimped the same way.
5. Each pallet's cam plate spreads its carriers from 3.4 to 5.0 mm; row A is
   pushed into the odd cavities, the housing shifts 2.5 mm, row B into the
   even ones.
6. A wafer test on a real XH header.

**What locates what.** "Fixed" is the C's die block.
- **Axially:** the box's mating face on a hardened front stop on the die block
  (c1c's rule).
- **Laterally:** the slide's step and the carrier's box slot; the closing punch
  finishes it.
- **Vertically:** the anvil top, 0.1–0.2 mm above the pocket floor.
- **Conductor to contact:** the snap (or tack), made at the lay and never
  undone, because the contact never leaves its pocket.

**What drives and carries the crimp force.** Ram → punch → contact → HSS anvil →
button cell → disc stack → the C's lower arm → spine → upper arm → ram guides.
A lower arm 12 mm thick and 15–25 mm wide deflects 11–41 µm at 3 kN; with the
height stop in the die block beside the anvil, that deflection is travel, not
crimp height [htq §7]. The slide, the pallets and the printed carriers carry
none of it.

**How it knows it worked.**
- The camera at the lay: strands in the U, none over a wing tip, the
  insulation edge in the window.
- **Identity at the anvil.** When the pallet settles carrier *k* onto the
  anvil, the conductor that answers must be the one the pin map puts there.
  That catches a mis-laid J7 GND-over-CLO before any force.
- Die force against ram position, every stroke, on the station ESP32.
- Crimp height by re-touch on every crimp.
- A proof pull on the carriers' rear shoulders (below), the pushers' traces,
  and the wafer test.

**What the person does.** Keeps sticks and housings fed, lays each ribbon end
in the clamp, makes J4's crossings at the lay, takes each finished end off the
wafer. Pre-forms contacts at a6b's click station while a print runs, unless
[a1b](a1b-pawl-out.md) does it.

Sketch: [`../sketches/a4d-tongue.svg`](../sketches/a4d-tongue.svg) (end view at
the press, to scale from cited dimensions); change-the-question's layout is
[`c1c-crimp-in-the-row.svg`](../../change-the-question/sketches/c1c-crimp-in-the-row.svg).

## Steps it covers and what it hands back

**Covers:** split, supply contacts (sticks), place every contact of a half-row
on its conductor in one motion, crimp in the row with die force and crimp
height, identity at the anvil, spread, insert both rows, and the pin-order
test on a wafer.

**Hands back:** stripping (another station), pre-forming (by hand at a6b's
click, or a1b), feeding sticks and housings, laying each ribbon end, J4's
crossings, labelling.

## How it relates

- Branch of [a4](a4-dies-in-a-die-set.md): the one-nest die cut to a tongue,
  its anvil a narrow HSS blade, height from a stop.
- Combines change-the-question's
  [c1c](../../change-the-question/ideas/c1c-crimp-in-the-row.md) (half-rows at
  3.4 mm, pockets, snap, a fixed press, spread and push) and
  [c6](../../change-the-question/ideas/c6-pre-form-the-contact.md) (narrowed
  contacts), proposed as K2 in this explorer's
  [exchange](../../../exchange/hand-tool-as-press--on--change-the-question-w3.md).
  c1c names a4 as one of its presses.
- It is where [a4b](a4b-c-frame-one-nest-head.md)'s arm goes when the
  neighbours are spread and narrowed: under the pallet instead of over the
  row.

## Why the side-entry jaw law stops applying here

The jaw law (8.7–14.7 mm of stand-out and strands set at 9–47 mm root radius
[calc w3 §2]) is a property of a whole SN jaw lying along a row at 2.5 mm. Two
changes remove it:
- change-the-question's split puts neighbours 3.4 mm apart in plane;
- narrowed neighbours are 1.8–2.14 mm wide instead of 2.46–3.25 mm open.

A tongue ≤ 4.45 mm wide then fits between them with 0.1 mm a side [calc w3 §6],
leaving walls of 1.43–1.48 mm either side of a 1.5–1.6 mm conductor arch. No
conductor is lifted or stood out, so none is kinked by the crimp.

## Major unresolved problems

- **Cutting a hardened jaw to a 4.45 mm tongue** without cracking it: a4b's
  problem, tighter.
- **The SN's lower XH cradle is replaced by a flat HSS blade.** The crimp's
  underside then differs from the hand tool's, and any face-to-face bottoming
  the SN jaws have in the hand tool is gone: the stop alone sets height
  [assumption: the SN's lower die shape is unrecorded].
- **The cam plate and the anvil want the same place** under carrier *k*. c1c's
  slotted cam plate for the 3.4 → 5.0 mm spread sits under the pallet, where
  the anvil rises. Repairs: ≤ 1.9 mm windows in the cam plate at every carrier
  position, leaving 1.5 mm webs that also carry the slanted slots; or the cam
  plate moved to the carriers' rear, driving pins on the carrier tails [htq,
  H4]. Whether a 1.5 mm printed web carries the spread's side loads is
  unknown.
- **Carriers sprung forward against a fixed front stop** meet it sideways when
  the slide steps: side lead-in ramps (30–45° push the box back 0.2–0.5 mm over
  0.2–0.87 mm of the step), or a stop that retracts during each step
  [htq §6].
- **The proof pull.** 20 N per contact on a row of 2–5 is 40–100 N rearward on
  carriers whose only rearward restraint is a 0.1–0.5 N spring [htq §6]. A rear
  latch per carrier, or the tracks' rear ends as a hard stop, carries it into
  the slide; or the row is pulled at a separate plate.
- **The pre-form's own questions:** whether the SN-2549's insulation-first
  window exists ([a6b](a6b-flags-by-hand-foot-crimp.md)); whether c6's round
  keyhole is re-formed by the die at all (its tips sit 0.14–0.52 mm below the
  closed height [htq §1]).
- **Everything c1c leaves:** split length behind the housing (6–12 mm for T4,
  15–26 mm for J1), row B's push between row A's wires, ~0.5 mm carrier walls,
  and J4.

## Rests on

- **[estimate]** Pre-formed widths 1.8–2.14 mm; punch walls and the 4.45 mm
  tongue [htq §5].
- **[estimate]** Arm deflection 11–41 µm at 3 kN for a 12 mm arm [htq §7].
- **[assumption]** A tongue this narrow keeps the SN's upper profile intact
  when cut.
- **[assumption]** Everything c1c, c6 and c1b rest on.

---

Citation keys: **[calc w3 §n]** is [`../calc/wave3.out.txt`](../calc/wave3.out.txt);
**[htq §n]** and **[htq, Hn]** are [`../calc/exchange_ctq_w3.out.txt`](../calc/exchange_ctq_w3.out.txt)
and the breaks in
[`hand-tool-as-press--on--change-the-question-w3.md`](../../../exchange/hand-tool-as-press--on--change-the-question-w3.md);
**[prime: ASIN]** is a row of [`../../../sourcing/amazon-prime.md`](../../../sourcing/amazon-prime.md),
observed 2026-09-28.
