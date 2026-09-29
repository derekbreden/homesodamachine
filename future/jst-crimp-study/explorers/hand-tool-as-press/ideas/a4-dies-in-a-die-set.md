# A4 — The dies leave the tool: SN jaws in a guided die set, driven by a slow eccentric

## Picture it

**Where things start.** A spare SN-2549 jaw set is two hardened, wire-EDM-cut
die pieces. The one with the punch profiles is screwed into an upper steel
holder; the one with the anvils into a lower one. Each holder has a slot cut to
the SN head's jaw slot (the listings call it "4 mm slot"), and the same M4
screws hold the die pieces as in the tool. The contact and conductor arrive as
in [a1](a1-squeezer-cradle.md) (a person at the printed locator) or
[a2](a2-ribbon-to-fixed-tool.md) (a carriage with a stub on a pin).

**What moves.** One thing, the ram:
- The upper holder is on a ram plate guided by two 8 mm ground rods in
  bushings.
- Above the ram, a 10–12 mm shaft turns in two bronze bushings. It carries an
  eccentric of 2–2.5 mm, so one turn is a 4–5 mm stroke.
- The shaft is turned by the bench's NEMA 23 through a 10:1 planetary, or a
  self-locking 12 V worm gearmotor at ~10 rpm, or, in the first build, a
  150–200 mm hand lever (below).
- An AS5600 magnet sensor on the shaft end reads its angle, and so the ram's
  position.

**What locates what.** "Fixed" is the lower die holder, sitting on the base
block.
- The printed locator of a1 (front stop, flap blade at the neck) bolts to this
  steel holder instead of the tool's jaw screw.
- The upper die is aligned to the lower by the guide rods, and by the SN
  procedure itself: loosen the screws, close the dies on each other, tighten
  [source: IWISS jaw-change instructions].
- The contact is located as in a1, or by a carrier stub's pilot hole as in a2.

**What drives and carries the crimp force.** The eccentric pushes the ram. The
ram pushes the punch die onto the contact on the anvil die. The anvil die
pushes the lower holder down through a **button load cell** onto a **stack of
disc springs preloaded to ~3.5 kN**, bolted through the base. The force loop
runs: eccentric shaft → bushings → two steel side plates in tension → base →
disc springs → load cell → lower die → upper die → ram.

**Where the dies meet.** Die contact is set **0.17–0.28 mm above bottom dead
centre**: the preload divided by the frame loop's stiffness, plus 0.05 mm. The
loop (shaft bending in bushings, bushing play, laminated holders, the button
cell) is ~15–30 kN/mm [estimate]. At that setting the dies meet on every
stroke, the stack takes the rest of the travel, and the force at BDC is
~3.6 kN whatever the loop's real stiffness [calc w3 §1; sl w3 §6]. The setting
is found on the machine: step the die-contact height down on empty strokes
(dies face to face, no contact) until the button cell shows the stack's knee.
The springs do the ratchet's job: full closure, with a force limit.

**How it knows it worked.**
- **Die force, directly.** The button cell sits in the force path at the die,
  not at a handle. That is real crimp force monitoring: teach-in from good
  crimps and a band around the curve [prior-art §6], checked every sample by
  the station ESP32.
- **Ram position** from the shaft angle. Near BDC a degree of shaft is microns
  of ram.
- **Crimp height on every crimp.** After BDC the eccentric turns back until the
  cell reads ~10 N, and an indicator across the holders is read
  (force-and-form f3's re-touch).
- **Open access.** The camera looks straight in from the side at the neck and
  the lance, because nothing but two holders surrounds the dies.
- The far-end block gives continuity and identity, as in a1.

**What the person does.** In the standalone version, what they do at a1: place
contact, feed conductor, press a pedal or pull the lever. With a2's carriage
behind it, what they do at a2: load stubs, clamp ribbon ends. Once: has the
steel holders and plates cut, seats the dies by closing them on each other.

Sketch: [`../sketches/a4-die-set.svg`](../sketches/a4-die-set.svg).

## Steps it covers and what it hands back

**Covers:** the crimp; die-force monitoring; crimp height read on every crimp;
the neck frame and lance check; optionally strip feed with an in-stroke tab
shear.

**Hands back:** whatever a1 or a2 hands back, depending on what loads it; the
metalwork of the holders and side plates.

## How it relates

- The dies of [a1](a1-squeezer-cradle.md)'s tool, lifted into a press.
- Branches:
  - [a4b](a4b-c-frame-one-nest-head.md): one nest on a C-frame arm that reaches
    over the row, on a gantry;
  - [a4c](a4c-one-nest-behind-a-tack-station.md): one nest as the heavy station
    behind machine-that-sees-and-learns' tack station;
  - [a4d](a4d-tongue-under-a-windowed-pallet.md): one nest cut to a tongue
    under change-the-question's windowed pallet.
- The re-touch is force-and-form's
  [f3](../../force-and-form/ideas/f3-knee-micropress.md). The press is one of
  machine-that-sees-and-learns'
  [v1](../../machine-that-sees-and-learns/ideas/v1-watched-nest.md)'s
  candidate presses.

## Major unresolved problems

- **The SN die pieces' seat** (slot width, depth, screw position, what the die
  bears on) has to be copied from a tool. It is not published. The only Prime
  route to a 2549 die is inside the iCrimp IWS-0723K kit ($46.59, 9 ratings
  [prime: B09CP8RV94]); whether its die mounts like the SN jaws is not stated.
  icrimptools.com sells SN jaw sets alone at $4.99–9.99 [source].
- **Whether SN dies bottom face to face.** If they do, the dies set crimp
  height and the stack caps the force. If they do not, a hard stop block
  between the holders, beside the dies, sets height and the stack caps the
  force at the stop.
- **Four custom steel parts:** two holders and two side plates. The holders'
  slots are the precision features. They carry kilonewtons, and none is a
  print.
- **Heavy disc springs are not on Prime.** The Prime Belleville row is a light
  stainless assortment ($14.99 [prime: B07CSQDS7F]); a DIN 2093-class stack for
  3.5 kN comes from an industrial supplier [assumption: not sourced here].
- **The frame loop's real stiffness and the stack's rate** are estimates. One
  empty stroke with the cell answers both.

## What lifting the dies buys

- **Die force, measured.** The load cell sits in the force path at the die, not
  at a handle through a linkage of unknown gain and friction.
- **Short stroke, slow and strong.** With die contact set for the stack, the
  peak shaft torque is ~1.6–2.0 N·m before friction and ~2.0–3.0 N·m with
  30–50 % friction [calc w3 §1].
- **BDC is geometry.** The eccentric reaches the same bottom every turn,
  whatever its speed or the motor's torque, until it stalls. Stalling is
  visible as the angle stopping short of 180°.
- **The force limit moves into steel.** With BDC set by geometry and the peak
  capped by the stack, the station MCU's stroke keeps its early-fault stop and
  a slow last ~20° for trace resolution, but does not need to crawl into a
  hard stop from a taught height (machine-that-sees-and-learns'
  [v7](../../machine-that-sees-and-learns/ideas/v7-the-run.md) rule for
  actuator-driven stops).
- **Open access.** The camera sees the barrels from the side before and after.
  A carrier strip can pass under the holders if the die piece is narrow enough
  (below). A two-step die pair fits side by side: a conductor-only and an
  insulation-only profile, as JST's YC and YRS tools and Engineer's PA-09 do
  [xh-facts §2].
- **Crimp height adjustable, if wanted.** A shim under the lower holder only
  changes where in the turn the dies meet, and so how far the stack is
  compressed. Crimp height becomes adjustable only if the eccentric stops
  short of die contact: then it is BDC plus the frame's deflection at that
  force, which is how a press applicator's dial works [xh-facts §2, CDS
  applicator].
- **The tool frame stays a hand tool.** Derek's SN-2549 stays on the bench, and
  the die set runs on $5–10 die pieces.

## Drives

| Drive | Torque at the shaft | Against 2.0–3.0 N·m [calc w3 §1] |
|---|---:|---|
| Hand lever, 150–200 mm, 20 N at the grip | 3.0–4.0 N·m | carries it |
| NEMA 23 on hand + 10:1 planetary (STEPPERONLINE, $48, 10 N·m permissible, 96 % [prime: B0BPGMZ5LM]) | ~9.6 N·m | carries it |
| Greartisan 12 V 10 rpm 40 kg·cm self-locking worm ($26.99 [prime: B07YBXB4N7]) | ~3.9 N·m if that is its working torque | carries it |
| NEMA 23 on hand + 3:1 belt | ~2.8 N·m | at the edge |
| 5840-31ZY worm gearmotor, working ($18.50 [source: nfpshop.com]) | ~2.3 N·m | at the edge |

The bench's NEMA 23 is in the weld rotator [repo], so a motor drive is a
second NEMA 23 or a borrowed one.

**The first build has no motor.** A lever on the eccentric shaft is a hand
press whose bottom is geometry: the person pulls ~15–20 N at a 150–200 mm lever
over the last ~40° of the turn [calc w3 §1], the stack caps the force, the
button cell and the re-touch still read every crimp, and a1's locator still
places the contact. The motor later replaces the lever on the same shaft.

## The frame

- **Side plates.** Two laser-cut steel plates, ~6 mm, carry the shaft bushings
  and are tied to the base with bolts. At ~3.6 kN each plate carries ~1.8 kN in
  tension, which two M5 bolts carry many times over [estimate]. Laser-cut
  steel from an online cutting service [assumption on service; not sourced
  here].
- **Die holders as laminations.** Each holder is a stack of laser-cut plates
  bolted together. The middle plate has the die piece's outline cut out, so
  the stack forms the slot without machining. The die pieces then seat by the
  SN procedure (close on each other, tighten). Laser-cut outline tolerance is
  on the order of ±0.1 mm [assumption], and the closing-and-tightening takes up
  what the cut leaves.
- **Printed parts** locate, cover and guide: the locator plate, the camera arm,
  the cable routing. None carries crimp force.
- **Bushings, not small ball bearings, on the shaft.** A 608's static rating is
  ~1.4 kN, below the peak. Bronze bushings at a few rpm carry it [estimate from
  common bearing tables]; 10 mm sintered bronze flange bushings are $11.99 for
  ten [prime: B0GCH3THWM].
- **Guide rods** carry only side load: 8 × 100 mm case-hardened rods, h8,
  $6.99 a pair [prime: B09RVS4PXZ]. The dies also align each other at closure,
  as they do in the tool's slot.

## Narrow dies

An SN jaw carries four nests side by side. A carrier strip passing through a
die set hits the jaw beside the working nest (contacts on the strip are
7–9.5 mm apart, unmeasured), and so does any neighbour conductor held near the
working one.
- **Cut the jaw.** A spare jaw piece is cut with an abrasive disc to leave the
  usable nest with material either side. The pieces are hardened
  [assumption], so the cut is abrasive, slow and wet. A cracked piece costs
  one more set.
- **How narrow, for what:**

| Use | Width allowed | Where developed |
|---|---|---|
| Strip feed under the holders; stubs need none | 6–8 mm | here |
| into-the-housing's i3 shuttles at 5 mm pitch (8.3 mm free between neighbour wires [ith calc §2]) | 6–8 mm | here |
| Between lifted crimped neighbours at 5 mm pitch | ≤ 7.45 mm up to ~5.9 mm above the crimping edge, wider above (a T-section holder) | [a4c](a4c-one-nest-behind-a-tack-station.md) |
| In a row at 3.4 mm beside pre-formed neighbours | ≤ 4.45 mm tongue; anvil a ≤ 1.90 mm blade | [a4d](a4d-tongue-under-a-windowed-pallet.md) |
| In the row at 2.5 mm | does not fit: punch walls need 0.47–1.12 mm each, a punch 2.8–4.1 mm wide against 3.3 mm free [ith ex §15] | — |

With a narrowed die, the strip runs under the holders the way it runs through
an applicator [prior-art §3]:
- a pawl, driven by a servo or by a cam on the eccentric shaft, advances it
  one pitch per stroke through the pilot holes;
- a spring drag stops it sliding back;
- a shear blade on the ram cuts the tab at the bottom of the stroke (~40–100 N
  [calc §9]).

## Crimp height read on every crimp

force-and-form's f3 re-touches: after the stroke it closes again at ~10 N and
reads an indicator mounted across the dies. The gap at peak force is 50–80 µm
low because the die blades compress, so the re-touch is the reading that means
crimp height [force-and-form: `calc/metrology.out.txt` §1–2].
- **How it fits a4.** A digital indicator on the upper holder bears on a pad on
  the lower holder, beside the die pieces.
- **The re-touch.** After BDC the eccentric turns back until the load cell
  reads ~10 N, and the indicator is read. That is the crimp's height plus a
  fixed offset, found once by micrometering a few crimps.
- **What it gives.** The stack guarantees the dies bottom. The indicator
  measures what that bottom produced, crimp by crimp, and shows a die piece
  loosening in its slot as a drift.
- **The indicator.** Clockwise Tools DITR-0105, 0.001 mm, RS232 port, $52.99,
  67 ratings [prime: B07888LX1R]. Its DTCR-01 data cable has no Prime listing;
  the ELP camera can read its display instead [assumption].

## The open die set is where the lance and the neck can be seen

- **The neck frame, at hold.** With only two holders around the dies, a
  camera looks straight across the neck: the blade on the box, the brush
  length, and the lance tip in front of the anvil face.
- **A lance check before release.** After the crimp and before the lift, a
  2–3 N rearward nudge must meet the anvil face within the expected travel.
  The camera watches the lance meet it.
- **Unloading.** The crimp lifts off the lower die by 1–1.7 mm before it is
  drawn back [ith ex §2]. The ram's top position leaves room.

## Parts

**Bought:**
- SN jaw sets (icrimptools.com $4.99–9.99 [source]; the IWS-0723K kit on
  Prime [prime: B09CP8RV94]);
- 8 mm ground rods and bushings; 10 mm bronze bushings;
- disc springs (~20–25 mm OD, heavy series; industrial supplier);
- button load cell, 500 kg (4.9 kN) compression, $74.99, thin listing
  [prime: B0GZZRQC6Y]; covers the ~3.6 kN at BDC;
- HX711 ($11.50 [prime: B079LVMC6X]);
- a drive from the table above;
- AS5600 ($7.99 for three [prime: B094F8H591]);
- DITR-0105 indicator [prime: B07888LX1R].

**Custom steel:** two die holders and two side plates.

**Printed:** locator, covers, camera arm, strip guide, lever grip.

## Tried against it

- **"The SN dies are designed to be pushed by a toggle linkage, not a ram."**
  The die sees a closing force across its faces either way. In the tool, the
  upper die moves on an arc of a few millimetres near closure, close to
  straight at the end [assumption; iCrimp calls the action "parallel"
  [source]]. On a guided ram it moves straight.
- **"Disc springs let the dies bounce."** At a few rpm there is no bounce.
  Below the preload the stack is solid.
- **"The load cell in the force path adds compliance."** It does, ~0.06 mm at
  3 kN [sl w3 §6, estimate]. That compliance is part of the frame loop the
  die-contact setting is found for, so it moves the setting, not the crimp.

## Rests on

- **[assumption]** SN dies bottom at closure; if not, a hard stop block.
- **[assumption]** SN die pieces seat on flat faces with screws, so a holder
  can copy the seat.
- **[assumption]** The upper die piece mounts to a moving part in the tool that
  a ram plate can imitate. In the tool it may pivot. If it does, the holder
  copies its closed-position pose.
- **[estimate]** A 3.5 kN preload is above the crimp's peak (0.8–2.6 kN
  [xh-facts §4]). If the peak is higher than estimated, the springs yield
  during the crimp. The load cell shows that as a flat top on the curve.
- **[estimate]** Frame loop 15–30 kN/mm, stack rate ~3 kN/mm.

Measurements that bear on it:
- a caliper and the Revopoint scanner on a spare jaw set, and the SN head with
  one jaw removed;
- the SN-2549 closed against a light;
- a real XH crimp's force (xh-facts Unresolved 8);
- one empty stroke with the button cell: loop stiffness and the stack's knee.

---

Citation keys: **[calc §n]** is [`../calc/hand_tool_press.out.txt`](../calc/hand_tool_press.out.txt);
**[calc w3 §n]** is [`../calc/wave3.out.txt`](../calc/wave3.out.txt);
**[sl w3 §n]** is machine-that-sees-and-learns'
[`w3_on_hand_tool_as_press.out.txt`](../../machine-that-sees-and-learns/calc/w3_on_hand_tool_as_press.out.txt);
**[ith ex §n]** is into-the-housing's
[`exchange_hand_tool_as_press.out.txt`](../../into-the-housing/calc/exchange_hand_tool_as_press.out.txt);
**[ith calc §n]** is its [`insertion_geometry.out.txt`](../../into-the-housing/calc/insertion_geometry.out.txt);
**[prime: ASIN]** is a row of [`../../../sourcing/amazon-prime.md`](../../../sourcing/amazon-prime.md),
observed 2026-09-28.
