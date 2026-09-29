# A2c — One baseplate, three stations: a stripper in a squeezer, a1's crimper, a housing nest

## Picture it

**Where things start.** One baseplate holds, left to right:
- the bench's **Klein 11063W** self-adjusting stripper in a second squeezer,
  with a metal-faced, grounded length stop;
- [a1](a1-squeezer-cradle.md)'s crimp squeezer with [a2](a2-ribbon-to-fixed-tool.md)'s
  stub magazine, rear-face shear and pull slot;
- a printed **housing nest** holding the XHP housing, with a slotted
  stencil-steel pusher blade on a small slide.

a2's carriage, head, comb, fork, tip camera and far-end block serve all three.
The person clamps a ribbon end whose conductors are split back 25–35 mm but not
stripped, drops the right XHP housing into the nest, and picks the loom on the
screen. The contacts are genuine SXH stubs, so the strip length is JST's
2.4 mm [mfr S6].

**What moves.** The machine works **in batches, not conductor by conductor**.
1. **Strip every conductor.**
   - The fork stands conductor *k* out and pushes its cut end into the Klein's
     mouth until the end touches the grounded length stop. The bare copper of
     the cut face reads as continuity.
   - The Y axis goes slack. The squeezer closes the Klein: its gripping jaws
     clamp, the blades bite, and the jaws move apart and pull the slug into a
     bin.
   - The camera takes one backlit frame of the stripped end, looking for
     strands standing proud or cut, and the torn insulation edge.
2. **Crimp every conductor.** a2's cycle, including the pull slot.
3. **Insert one at a time, from a stored hump.**
   - The head sets conductor *k*'s crimped contact at the rear entry of cavity
     *c(k)*, from the loom's pin map. Its nose sits on the cavity lead-in,
     leaned per Sogang's lean-and-slide [prior-art].
   - The fork forms a **hump** in *k* between comb and contact, 7.5–10 mm high
     over 20–35 mm. That stores the 7.5–7.9 mm the contact must travel to
     seat [ith ex §5; into-the-housing handover].
   - The head does not move. The pusher blade bears on the rear of the
     insulation crimp and pushes the contact home, taking the length from the
     hump.
   - Seating shows as a click and a rise to a wall. A 3–8 N pull-back then
     checks the lance: force before distance (Boeing US 11,374,374
     [prior-art §5]).
4. **Next cavity.** J2's cavity 3 is skipped by the pin map. The head can route
   any conductor to any cavity, so the machine makes J4's crossing itself (the
   3P's GND to pin 2, over three 4P conductors). The far-end block confirms
   which conductor is at the nest before each push.

**Pairs.** J1, J2, J4 and J7 take two ribbons in one housing. The first
ribbon's contacts go in and stay latched. The person unclamps the first ribbon
from the head, leaving it hanging from the housing in the nest (up to 600 mm of
loom). The second ribbon is clamped, stripped and crimped, and its contacts
fill the rest of the pin map.

**What locates what.** "Fixed" is the baseplate; each station has its own
datum the head touches off on.
- Strip: the grounded length stop on the Klein's face sets strip length.
- Crimp: as a2 (pilot pin, then nest and blade; fork and tip picture; green or
  tip plate).
- Insert: the housing nest; the head touches off on the housing's end walls to
  reach each cavity's lead-in (cavity positions are 2.50 mm non-cumulative
  [xh-facts §3]).

**What drives and carries the force.**
- Strip: the second squeezer closes the Klein; the head goes slack in Y.
- Crimp: a1's pusher, inside the tool head.
- Insert: the pusher blade's slide, reacting into the housing nest; the hump
  supplies the length, so the head carries none of it.

**How it knows it worked.** The stripped-end frame; a2's per-crimp checks; the
far-end block's identity at every push; the seating force against travel; the
3–8 N pull-back on each latch.

**What the person does.**
- Cuts ribbon to length and splits the ends.
- Loads stubs.
- Drops housings in the nest and swaps ribbon ends for pairs.
- Labels the loom.

Sketch: a2's plan ([`../sketches/a2-ribbon-to-fixed-tool.svg`](../sketches/a2-ribbon-to-fixed-tool.svg))
shows the carriage and crimp station; the stripper and the housing nest are
described here, not drawn.

## Steps it covers and what it hands back

**Covers:** strip, place contact, place conductor, crimp, tab cut, proof pull,
insert one at a time, pin order including J4's and J7's crossings, and the
latch check.

**Hands back:** cut to length and split; load stubs; drop housings in and swap
ribbon ends for pairs; label.

## How it relates

- Branch of [a2](a2-ribbon-to-fixed-tool.md): the same carriage visits a
  stripper and a housing too. The view is the same one turned on the
  neighbouring steps: the bench's hand tools are already the machines, and
  what is missing is the hand that closes them and the hand that presents the
  work.
- Its branch [a2d](a2d-batch-then-gang-push.md) inserts a whole ribbon end at
  once instead.
- The hump and the blade pusher follow into-the-housing's reading of the
  feed-length rule (its
  [exchange](../../../exchange/into-the-housing--on--hand-tool-as-press.md)).

## Major unresolved problems

- **The Klein on silicone.** Whether the 11063W strips this 22 AWG silicone
  cleanly and without nicking is not recorded.
  - The tool is rated 10–20 AWG and used down to 24 [repo: `tools.md`], and
    the silicone tears rather than cuts [xh-facts §7].
  - The self-adjusting cam grips by squeezing the insulation, and soft
    silicone gives it less to grip.
  - Whether its length stop reaches down to 2.4 mm is unknown [assumption].
- **The Klein moves the wire.** Its jaws travel apart as they pull, so the
  head yields in Y during the squeeze, and the conductor's axial position is
  re-found at the crimp station.
- **The hump in set copper** and the blade between seated neighbours are
  untested.
- **Insertion force is not public.** The analog is 14.7 N maximum (Molex
  Mini-SPOX); the clone spec says ≤ 9.8 N [ith; ribbon-as-pallet]. The push
  goes through the insulation crimp's rear edge, and above ~15 N that edge is
  the weak point.
- **The jaw law's stand-out** at the crimp station (*a* + 2.7 mm, 8.7–14.7 mm
  [calc w3 §2]) kinks every conductor. One-at-a-time insertion from a hump
  tolerates the kink.

## Why the order is batch, not per conductor

A per-conductor order (strip *k*, crimp *k*, insert *k*, then the next
conductor) stops at *k* = 1:
- Once contact 1 latches in a housing held by the fixed nest, the ribbon is
  tied to the housing.
- The head cannot carry the ribbon back to a stripper and a crimper tens of
  millimetres away without dragging the housing out of the nest, or pulling
  contact 1 back out.

Stripping all and crimping all first means nothing is tied to the housing
until the insertion pass. In that pass the head stays at the nest.

## The pusher is a blade, not a finger

- **Where the push ends.** A seated contact's rear sits 0.2–1.25 mm inside the
  housing's rear face, so the pusher's last stroke happens inside a 2.0 mm
  cavity [ith ex §10].
- **A printed finger does not fit.** A fork with ~0.4 mm tines round a 1.45 mm
  slot is 2.25 mm wide.
- **What does fit:**
  - a blade no wider than ~1.95 mm, with a 1.35–1.55 mm slot around the wire
    and 0.20–0.35 mm tines;
  - laminated stencil stainless (JLCPCB 304, from $3, most shipped within
    24 h [source: jlcpcb.com/pcb-stencil, 2026-09-28]) or filed feeler
    leaves.
- **What it bears on.** The rear edge of the insulation crimp, 0.17–0.27 mm a
  side. So the tab below it must already be cut to about one stock thickness,
  which a2's rear-face shear does.
- **Room beside it.** Seated neighbours sit on one side only, because the
  cavities fill from one end.

## The hump

- **Why it is needed.** The web is clamped in the head, and seated neighbours
  run straight from the comb to their cavities. Conductor *k* can gain the
  7.5–7.9 mm of seating travel only from length stored between comb and
  contact.
- **If the head advanced instead,** every seated neighbour would bow
  7.5–10 mm into the working space [ith ex §5].
- **How it is formed.** The fork forms the hump by pushing *k* sideways or up
  between two points, with its contact held at the cavity entry.
- **In set copper** the hump's shape is whatever the copper takes. The blade
  pushes the contact, not the hump, so the hump only has to shorten without
  kinking back on itself.

## Parts beyond a2

- **Stripper squeezer:** a second printed cradle and pusher for the Klein
  11063W [repo], with a metal-faced length stop wired to the ESP32.
- **Housing nest:** printed, keyed per XHP size, with a stencil-steel blade
  pusher on a small slide (NEMA 17 Tr8×2 or a servo) through a 5 kg bar cell
  ($9.99 for two with HX711 [prime: B09K7G3477]).

## Rests on

- **[assumption]** The Klein's length stop is conductive or can be faced with
  metal.
- **[assumption]** A contact pushed by the insulation crimp's rear edge through
  a stencil blade seats without the crimp deforming.
- **[assumption]** The lance faces the window side (xh-facts §3). One kit
  housing settles it.
- **[source, analog]** Insertion force 14.7 N maximum (Molex Mini-SPOX); ≤9.8 N
  (clone spec).

---

Citation keys: **[calc w3 §n]** is [`../calc/wave3.out.txt`](../calc/wave3.out.txt);
**[ith ex §n]** is into-the-housing's
[`exchange_hand_tool_as_press.out.txt`](../../into-the-housing/calc/exchange_hand_tool_as_press.out.txt);
**[prime: ASIN]** is a row of [`../../../sourcing/amazon-prime.md`](../../../sourcing/amazon-prime.md),
observed 2026-09-28.
