# i6b — Branch of i6: the target is a bed of long posts standing through the housing

- **Branch of:** [i6](i6-sort-then-push.md).
- **What it combines:**
  - terminal-supply's [a4b](../../terminal-supply/ideas/a4b-through-cavity-post.md):
    one post through one cavity, crimp on its tip, slide home;
  - terminal-supply's [a4](../../terminal-supply/ideas/a4-post-held-contacts.md):
    hold a contact by mating it;
  - the wired header behind the housing from this explorer's
    [exchange on hand-tool-as-press](../../../exchange/into-the-housing--on--hand-tool-as-press.md)
    (C6). With posts long enough to stand through the housing, each box's
    arrival is logged before the push instead of during it.
- **Sketch:** [`../sketches/i6b-post-bed.svg`](../sketches/i6b-post-bed.svg) (schematic).
- **Numbers:** [`../calc/wave2.out.txt`](../calc/wave2.out.txt) section E;
  [`../calc/wave3.out.txt`](../calc/wave3.out.txt) sections E, F and H [calc w3 X];
  [`../calc/exchange_terminal_supply_w3.out.txt`](../calc/exchange_terminal_supply_w3.out.txt) section A.
- **Related:** [i4](i4-gantry-hand-with-eyes.md) can thread onto the same bed;
  [i5](i5-person-inserts-on-a-sensing-nest.md) uses real headers as its nest;
  terminal-supply's [a4c](../../terminal-supply/ideas/a4c-post-bed-one-push.md)
  uses the same bed differently: bare contacts go onto the post tips and are
  crimped there, then one housing move seats them all. The support comb applies
  to it too.

**What it changes from i6.**
- i6 lowers each crimped contact into a U-slot comb, squares the row with a
  backing blade, and pushes the housing on, guided by a sprung comb under the
  noses.
- i6b stands the housing on a **bed of long 0.64 mm posts** at 2.50 mm pitch,
  one through every cavity from the mating face, standing ~8.5 mm out of the
  rear face. The carrier threads each crimped contact's box onto its post tip.
  Then the housing slides back along the posts onto all of them.
- The posts guide every box into its cavity, and each post is an electrode.

## Picture it

**The bed.**
- A small PCB drilled at **2.50 mm** pitch, not 2.54: over an XHP-9 (eight
  intervals) 2.54 would be 0.32 mm off end to end, ±0.16 mm if centred
  [calc w3 F].
- Square 0.64 mm pins are pressed in, one per cavity of the loom's housing,
  ~17 mm long. J2's post 3 is left out.
- Each post is wired to an ESP32 input. The loom's far end sits in a terminal
  block, or pogo pins touch its cut face (ribbon-as-pallet a6), so every
  conductor is a separate circuit.

**The support comb.**
- A slotted stencil-steel **support comb** at 2.50 mm, on its own small slide,
  closes around the posts ~3 mm below their tips.
- Without it, a post is supported only by the PCB and the housing's front-wall
  post opening. It is then free for ~15.6 mm, and a side load of 1 N moves its
  tip 0.45 mm (steel) or 0.9 mm (brass or bronze header pins) [calc w3 F]. That
  is more than the box mouth's ±0.2 mm capture.
- With the comb 3 mm below the tip, the free length is 3 mm and the pin's
  material stops mattering (0.003–0.006 mm per N). The tips then sit at the
  comb's laser-cut pitch.

**Loading.**
- The housing slides onto the posts from the tips, mating face first, until the
  posts stand ~8.5 mm out of its rear face.
- It rests on a nest on a Y slide with a load cell (i3's push drive).
- The ribbon end waits in the staging plane in ribbon order, as in i6.

**For each conductor**, lower layer first, centre outward (i6's rule):
1. The carrier takes the crimped contact by its barrels, brings its box mouth in
   line with post k's tip, 8–10 mm below the staging plane, and moves it +Y.
   - The post's chamfered tip enters the box mouth (0.60–0.70 mm [source
     S19–S21]), capturing ±0.2 mm, and the post centres the box.
2. The box slides ~1–2 mm onto the post, to a depth the carrier's Y axis sets,
   short of the support comb. When the carrier lets go, the box's own spring
   grip on the post (0.2–1.6 N [terminal-supply, Molex KK analog]) holds it
   there.
3. The controller reads continuity from the conductor's far end to post k.
   **The right conductor is on the right post, before anything latches.** A
   wrong one is taken off and moved.

**Seating.**
1. The support comb withdraws. The backing blade drops behind the insulation
   barrels as in i6. Its tines are narrow enough to follow into the cavity
   mouths by up to ~2 mm.
2. The nest drives the housing −Y along the posts by ~13–15 mm: box fronts
   6.5–7.5 mm outside the rear face to 6.75–7.35 mm inside it [calc
   exchange_terminal_supply_w3 A, with a front wall of 0.4–1.0 mm].
   - Each cavity rides over its box with the post already inside it.
   - Lances fold against the cavity floor and snap at the window.
   - The load cell logs the sum. The push stops at the first wall.
3. A finishing tine pushes each contact to its own wall (i6), because contact
   lengths differ [calc w3 E].

**Test and release.**
- Every box still sits 1–2 mm on its post. Continuity per post, adjacent
  shorts, J2's missing post 3 and the J4/J7 identity are read here.
- A 5 N pull-back per wire checks the latch (above the post grip).
- The housing is drawn the last 1–2 mm off the post tips, straight, within 15°
  [mfr S5 handling precautions].

## At a glance

| | |
|---|---|
| **What locates each contact** | The carrier's fingers to the post tip; then the post, inside the box, for X and Z all the way into the cavity; the carrier's Y, then the backing blade, for Y |
| **Reference for "fixed"** | The post-bed PCB, and the support comb's laser-cut slots while threading |
| **Crimp force** | None here: an insertion module. The push (≤ 9 × 9.8–25 N) is carried by the nest drive and the backing blade |
| **How it knows** | Continuity per post before the latch (conductor identity and order); the push trace; the finishing traces; continuity and shorts after; the pull-back |
| **Steps it covers** | Pin order proven before the latch, guided gang insert, continuity, shorts and J2's empty cavity, latch check |
| **What it hands back** | As i6: bringing the crimped end, loading a housing onto the posts, lifting the finished end off, labelling |

## What it gains over i6

- **Guidance all the way in.** The post is inside the box from the start, so no
  nose can miss its lead-in. There is no sprung guide comb, no timing of its
  retreat, and no lean-and-slide.
- **Identity before the latch.** Pin order, J4 against J7, and pair order are
  proven while every contact is still free to move.
- **The header test for free.** JST says continuity checks should use "the
  applicable mating (shrouded header and header, etc.)" [mfr S5]. The post bed
  is that mating, at a shallow depth.

## What it costs

- **Threading each box onto a post tip** is a small insertion of its own:
  ±0.2 mm capture and a camera-guided approach. It is less demanding than a
  cavity lead-in, and it is repeated 53 times a unit.
- **The support comb** is one more slide, and it has to be out of the way before
  the push.
- **Whether the cavity is clear along the post's line**, from the post opening to
  the rear face. terminal-supply asked Derek to push a long header pin through
  an XHP-4 to find out. If something inside catches it, i6b fails as drawn.
- **One extra partial mating cycle per contact** (i5's question). XH mating
  durability is not in any document read.
- **The push includes the boxes' grip on the posts**, 0.2–1.6 N each: small
  against the lances' fold.

## The posts

| Post | Source | Note |
|---|---|---|
| Pins pulled from extra-long male headers | uxcell 25 mm-pin headers, $15.49, Prime-confirmed; the page states neither pin section nor material [sourcing/amazon-prime.md] | Usually brass or bronze [assumption]; fine with the support comb |
| Round 0.025 in (0.635 mm) music wire | K&S 5005, $7.24, Prime-confirmed [sourcing/amazon-prime.md] | Steel; its width across matches the 0.64 mm post's flats. The box's grip on round wire is untested |
| Loose square 0.64 mm pins | Sourcing request, Wave 3 ([`../sourcing-requests.md`](../sourcing-requests.md)) | Section stated on the page |

**The bed PCB.** JLCPCB states hole position ±0.075 mm, through-hole size
+0.13/−0.08 mm and press-fit holes ±0.05 mm
([JLCPCB capabilities](https://jlcpcb.com/capabilities/pcb-capabilities),
observed 2026-09-28) [source]. That is inside the box mouth's ±0.2 mm capture.
With the support comb setting the tips, the PCB sets only the roots.

## Major unresolved problems

- **Is the cavity clear along the post line?** One header pin pushed through one
  kit housing answers it.
- **Post-tip threading repeatability** on a 0.043 g contact held by its barrels.
- **Whether the housing's post openings pass a whole XHP-9's worth of posts**
  drilled at ±0.075 mm, before the comb aligns them.
- **Box grip on round music wire**, if steel posts are wanted without the comb.

## Contribution

It makes the gang push as certain as mating, and moves the pin-order test to
before the latch, where a mistake costs one move instead of an extraction.

## What rests on assumptions

- Front wall 0.4–1.0 mm, and the housing 7.75 mm along the mating axis [mfr S2].
- Box grip 0.2–1.6 N on a 0.64 mm post [terminal-supply, secondhand analog].
- Header pins brass or bronze [assumption].
