# v6 — The patient cell: the whole procedure on one stage, every act bracketed by a look, every doubt sent to a queue

Explorer: machine-that-sees-and-learns.

Sketch: [`../sketches/v6-look-act-look.svg`](../sketches/v6-look-act-look.svg) (schematic).

Numbers:
- **[calc: cycle_and_cost §n]** [`../calc/cycle_and_cost.out.txt`](../calc/cycle_and_cost.out.txt);
- **[calc: vision_budget §n]** [`../calc/vision_budget.out.txt`](../calc/vision_budget.out.txt);
- **[calc: w3htp §n]** [`../calc/w3_on_hand_tool_as_press.out.txt`](../calc/w3_on_hand_tool_as_press.out.txt);
- **[rap P §n]**, **[rap R §n]** ribbon-as-pallet's
  [`exchange_on_machine_that_sees.out.txt`](../../ribbon-as-pallet/calc/exchange_on_machine_that_sees.out.txt)
  and the ribbon-as-pallet calc it cites;
- **[bm W §n]**, **[bm wave2 §n]** borrowed-machines'
  [`exchange_sees_learns_w3.out.txt`](../../borrowed-machines/calc/exchange_sees_learns_w3.out.txt)
  and [`wave2.out.txt`](../../borrowed-machines/calc/wave2.out.txt);
- **[Prime]** a row of [`../../../sourcing/amazon-prime.md`](../../../sourcing/amazon-prime.md),
  observed 2026-09-28.

Related: controllers, software, queue and supervision in [v7](v7-the-run.md);
place and crimp by [v1](v1-watched-nest.md), [v8](v8-tack-look-crimp.md) or
[v9](v9-tack-at-the-anvil.md); inspect by [v5](v5-inspection-booth.md). The
channel, fan block, flush cut and far-end port are ribbon-as-pallet's
([a1](../../ribbon-as-pallet/ideas/a1-pallet-tour.md),
[a5](../../ribbon-as-pallet/ideas/a5-part-fan-strip-in-the-pallet.md)); the
insertion is their [a6](../../ribbon-as-pallet/ideas/a6-housing-as-last-comb.md);
the split direction is borrowed-machines'
[b6](../../borrowed-machines/ideas/b6-pierce-at-the-root-pull-to-the-tip.md)
rule, and the strip blades their
[b7](../../borrowed-machines/ideas/b7-borrowed-strip-head-one-conductor.md)
geometry.

## Picture it

**Where things start.**
- A three-axis stage ([v1b](v1b-printer-as-stage.md)'s printer or a V-slot
  build) carries:
  - the **pallet**: a channel ~0.2 mm under the ribbon's width, with a
    guillotine and a fan block of hinged keys (v1);
  - the camera at ~35°;
  - the key plunger;
  - a small servo tweezer on its own little slide.
- Along the front of the work area, left to right, are the stations: load shelf;
  split; twist and strip; place and crimp (v1, v8 or v9); inspect (v5 in line);
  housing nest, mating axis along the wire; tester (v5's wafer board).
- **The person clamps a ribbon end** into the pallet's channel with its marked
  edge on the datum wall. One guillotine stroke puts every tip on one line.
- **The tail.** The XH end is made first. The loom's tail coils in a cup on the
  pallet, its cut face in a pogo block, so the station MCU has a wire to every
  conductor.
- **The recipe,** chosen on the Mac: the housing; which conductor goes to which
  cavity; J2's empty cavity 3 and its trimmed conductor; J7's trimmed conductor;
  the J4/J7 crossings and the insertion order they need; the label [repo:
  shared-context per-unit table].

**What moves, station by station.**

1. **Split.**
   - **Mechanism.** The channel squeezes the ribbon ~0.2 mm under its nominal
     width, registering every valley over a thin steel rib standing in the
     channel floor, one rib per lower valley (a razor back or a 0.3 mm shim
     edge): AMP's under-width splitter, US 4,230,008. The ribbon's own pitch
     stack from a centred datum is 0.12–0.43 mm worst case for 3 to 9 conductors
     [rap R §1].
   - **Look:** a line laser across the ribbon (650 nm focusable module, $42.00
     [Prime]), seen at an angle, draws the profile and **checks** that the
     channel registered the valleys over the ribs.
   - **Act:** a fixed blade **plunges at the root**, just ahead of the clamp
     face, onto the rib. The stage then draws the pallet so the blade runs out
     **toward the tip**. The free length between clamp and blade is in tension,
     the root is where the blade went in, and any tear runs only toward the tip,
     where the split goes anyway (borrowed-machines' b6 rule). The blade is
     electrically isolated and wired as a sense line.
   - **Look:** the slit from above, lit low. Tinned copper against black
     silicone is the highest-contrast thing in the procedure. A blade touching
     copper has already registered through the far end, with the conductor's
     number.
   - **Decide:** copper touched or seen, back out (a guillotine stroke 6–10 mm
     further in); a slit that wandered, retry; a web torn rather than cut,
     accept if no copper shows.
   - **Alternatives:** if the web zips (repo Open item 5), a notch at the tip and
     a wedge pulled back, with the clamp face as the tear stop; a laser score
     (borrowed-machines' [b4](../../borrowed-machines/ideas/b4-laser-slits-and-scores.md)).
2. **Fan.** The parted conductors go into the fan block's S-grooves and keys at
   5 mm pitch, each key where the recipe puts it. *Look:* every conductor in its
   key, in recipe order, with continuity confirming which is which.
3. **Twist and strip,** one conductor at a time.
   - **Look:** the tip on the backlight; with the flush cut every tip is on one
     line, so the look confirms the line and finds strays.
   - **Act:** **die-hole blades** (or a rotary blade centred to the bundle) close
     at the strip length of the contact in use, back from the tip as seen
     (1.6–2.1 mm for clone-drawn kit contacts, 2.4 mm for genuine SXH
     [calc: w3htp §4]). Die-hole blades at 0.94 mm leave an even 0.04–0.19 mm
     ring of silicone; two 90° V-blades set to part this silicone would cut to
     within 0.02 mm of the strands at four points while leaving 0.35 mm at
     four others; a single orbiting blade needs the bundle centred to
     ±0.05 mm [bm wave2 §3]. The stage then pulls the slug **with a twist**:
     0.1–1.2 N·mm is needed and 2.5–15 N·mm is available, so the twist shears the
     remaining ring and lays the strands in the same motion [bm wave2 §3]. A
     pinch on the jacket at the strip line makes the stub twist rather than the
     whole bundle spin in its jacket (spinning the parted length resists ~7× the
     twist [rap P §10]). The blades are isolated and sensed, as at the split.
   - **Alternative:** a whole-end slug stripped while the ribbon is still webbed,
     before the split (ribbon-as-pallet's a5).
   - **Look:** strip length; the torn edge (a tag longer than ~0.2 mm fails
     [estimate]); bundle width; strays; a cut strand.
   - **Decide:** short by up to ~0.2 mm, strip again; a slug left on, pull again;
     longer, or a cut strand, back out the whole end with the guillotine (a
     single short conductor would skew the housing).
4. **Place and crimp:** [v1](v1-watched-nest.md)'s steps 1–11,
   [v8](v8-tack-look-crimp.md)'s tack, look and crimp, or, on strip,
   [v9](v9-tack-at-the-anvil.md) at an applicator.
5. **Inspect:** v5 in line, with roll held by the pallet and read from the box.
6. **Insert, along the wire axis** (ribbon-as-pallet's a6).
   - The housing sits in a nest with its mating axis along the wire, mating face
     away from the pallet.
   - The fan block closes to 2.5 mm: a 2.5 mm block swaps in, or a pitch changer
     closes the keys.
   - A grooved clamp grips every conductor within ~2 mm behind its insulation
     crimp. A free conductor buckles at ~6 N over 5 mm and ~40 N over 2 mm
     [digest].
   - Contacts go in one after another, by a staircase clamp face or by Sogang's
     lean-and-slide (18/20 against 3/20 for a straight push [digest]). A load
     cell under the nest records each one.
   - **Look, through the mating face.** XH housings show a trapezoidal window
     below each post opening [mfr S1, S2], read as the lance's catch
     [assumption, from the drawing]. A small first-surface mirror in front of the
     nest turns that view up to a camera. A latched contact shows its lance tip
     in its window; an unlatched one does not. This reads the latch itself, where
     a pull-back needs a retention threshold nobody has.
   - **Decide:** no latch, push again; still no latch, extract through the window
     with an extraction tip (JRready XH2.54PRO kit, $34.00 [Prime]; JST's XJ-06
     at $63.69 [xh-facts §2]) and ask.
   - **Crossing looms** (J4 needs 2–3 crossings, J7 1–2 [digest]) cannot go in
     as one row:
     - **per conductor:** the tweezer on its own slide takes any conductor to any
       cavity. **The crossing conductor goes into its cavity last,** so it lies on
       top of conductors already tethered in the plane; the recipe carries an
       insertion order separate from the crimp order. Crossing conductors need
       slack in the parted length, and beside an inserted neighbour the jaw has
       only 0.8 mm of room at 2.5 mm pitch [rap P §8];
     - **by hand:** the person inserts J4's and J7's contacts at a lit cavity,
       and the tester checks them.
7. **Test.** The whole housing onto v5's wafer board: continuity to the recipe,
   including J2's open cavity 3. The far-end pogo port does the same pin map and
   adjacent-shorts check from the other end before the housing leaves the nest.

**What locates what.** The pallet's channel and flush cut make the nominal:
every valley over its rib, every tip on one line, every conductor in its key. At
every station the camera checks the nominal and finds the exceptions (the
ribbon's profile, the tip as seen, the anvil's fiducials, the housing's
windows). **The stage is a mover, never a ruler;** the reference for "fixed" at
each station is that station's fiducials, seen in the frame.

**What drives the crimp and carries its force.** v1's press, v8's C, or v9's
crank applicator. The split, strip and insert forces are small (tens of newtons
at most), and the head carries them.

**How it knows each step worked.** The look after each act; the far-end channel
(which conductor, what touched copper, what connects to what). Two
irreversible acts get the strictest look before them: the conductor crimp, and
the lance catching in the housing.

**What the person does.**
- Cuts ribbon to length and pallets 14 ribbon ends a unit (~15–30 min).
- Keeps contacts and housings stocked.
- Inserts J4's and J7's crossing conductors, if the tweezer route is not built.
- Answers the queue ([v7](v7-the-run.md)).
- Labels the loom; the cell prints the label text from the recipe.
- Terminates each loom's far end (Fastons, ferrules, IDC [repo]) after the XH
  end.

Per conductor ~3.1–7.5 min; per unit ~2.8–6.6 h unattended
[calc: cycle_and_cost §2].

**Steps it covers:** split, fan, twist and strip, place the contact, crimp,
insert, verify the crimp, verify insertion and pin order.
**What it hands back:** cutting to length and palleting; stocking; crossings if
the tweezer route is not built; the queue; labels; far-end terminations.

## The queue

In [v7](v7-the-run.md): an ask parks the conductor with its photo, numbers and a
proposal, and the cell moves on; Derek answers from the phone or the bench;
every answer becomes a labelled example.

## Branch, not in its own file: the spool as the pallet

ribbon-as-pallet's [a4](../../ribbon-as-pallet/ideas/a4-spool-as-magazine.md),
procedure-is-the-machine's [p3](../../procedure-is-the-machine/ideas/p3-terminate-at-the-spool-cut-last.md)
and change-the-question's [c5](../../change-the-question/ideas/c5-ends-as-stock.md)
terminate the XH end while the ribbon is still on its spool, then feed out and
cut.
- **With v6's stations:** the clamp at the spool's leading end is the pallet,
  and the stations come to it on the stage; the far-end port is a slip ring on
  the spool's inner end (12-circuit capsule ring, $19.99 [Prime]); the cut that
  frees a loom is also the next end's flush cut.
- **What it takes from the person:** cutting and palleting. It leaves spool
  changes.
- **Uncertain:** the machine's size (a drop of ~0.6–0.7 m); whether the BNTECHGO
  spool's inner end is reachable.

## Hand-backs other views could take

| Handed back | Taken by |
|---|---|
| Cutting to length | The spool branch above |
| Palleting | The spool branch, or ribbon-as-pallet's [a3](../../ribbon-as-pallet/ideas/a3-backshell-that-ships.md) snap-on backshell |
| Labelling | a3's embossed backshell, or a printed label from the recipe |
| Housing supply | a6's gravity magazine |
| Crossing insertion | The tweezer route, if built |

## Problems, and what answers them

- **One head doing everything means everything waits for it.** At this pace a
  unit in 3–7 hours needs no parallelism.
- **A split drawn toward the clamp.** If the blade entered at the tip and ran
  toward the clamp, the free length would be in compression: a 5P held down at
  the blade buckles at 1.1–2.2 N over 25–35 mm, against a drag of 0.2–3 N for
  one web and 0.8–12 N for four [bm W §9]. The ribbon would bow up, the web lift
  off its rib, and the root land wherever the tear ran ahead of the blade. The
  plunge at the root and the draw to the tip avoid it.
- **Back-out shortens conductors.** A guillotine stroke 6–10 mm in puts every
  tip back on one line; the pallet starts with that allowance in its free
  length. Per-conductor re-strips are kept for +0.2 mm corrections.
- **Lighting the housing.** The mating-face window view needs the lance tip to
  show through white PA 6 at the camera's resolution; a black clone housing may
  need light through the post openings from the side. One photograph of a kit
  housing.
- **Pin order.** The recipe drives which key goes to which cavity; the far-end
  channel and the tester confirm it.
- **A housing rear-face-up, fed from a horizontal pallet,** is set aside: every
  conductor would take a quarter-bend at R ≤16–22 mm, well under copper's
  ~67 mm yield radius, and keep it; and the housing would tether the pallet after
  the first latch [rap P §8]. It revives if the housing, not the conductors,
  turns through 90° (a nest that rotates after each latch); the tether remains.

## Contribution

- A way to take the whole procedure (split, strip, place, crimp, insert, verify)
  with slow, mostly borrowed mechanisms: the precision in the pallet and the
  geometric bottoms, the judgment in pictures and the far-end channel.
- It shows where the person is still needed, and gives them a queue instead of
  a station.

## Major unresolved problems

- **Stripping silicone cleanly.** Die-hole blades and a twisting pull are the
  mechanism; the cell measures and retries, but the tearing is physics it does
  not solve.
- **Splitting the web.** Plunge-and-draw on ribs, peel, or laser: all untested
  (repo Open item 5), and whether a blade plunged onto a rib pierces the web
  cleanly is open.
- **XH insertion and retention forces are not public** [xh-facts §3]. The
  mating-face latch view sidesteps the threshold, if the lance shows in its
  window.
- **Lance-side orientation, and how deep the contact's rear seats** in a latched
  cavity, are still to be seen on a real housing.
- **Crossing looms** need the tweezer's slack and its 0.8 mm jaw room, or hands.
- **Crowding on one head** (camera, plunger, tweezer, pallet): a tool changer or
  a second small head.

## What rests on assumptions

- Web geometry, and that ribs stay under the web as the ribbon is drawn.
- The lance being visible through the mating-face window.
- Translucency of the housings.
- The 3–7.5 min per conductor estimate.
- That queue answers stay rare: a handful a unit ([v7](v7-the-run.md)).
