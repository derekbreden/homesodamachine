# Notebook: change-the-question

## Log (wave 1)

- **Read.** The brief, shared context, working method, xh-facts and prior-art
  in full. Also the repo's `cable-assemblies.md`, the run-length script, the
  wiring schedule (loom lengths) and the BOM's ribbon and kit lines.
- **Web search** was unavailable: the session's search budget had been spent
  by earlier passes. Everything web-sourced below comes from direct fetches of
  known URLs:
  - **Würth 646 001 137 22 drawing** (WR-WTB 2.50 mm female crimp contact).
    It gives what the facts pass could not: carrier pitch 7.10 mm, carrier
    3.00 mm wide, pilot hole Ø1.50, open insulation barrel 2.3 × 2.15 mm,
    open conductor barrel 1.85 × 1.62 mm, 10k per reel.
  - **The HDGC and JXT clone drawings** again. They carry no pitch dimension.
  - **JST's KR, XH, EH, SUR and VT catalogs.** XH is "Crimp style and Mating
    style". KR is the IDC twin of PH, on the same header.
  - **Digi-Key's ASXHSXH22K305 page**: black 22 AWG, $0.65 at 100, 26,279 in
    stock, 2–12 in family.
  - **Wikipedia's JST page**: XH is used by many R/C batteries; interchangeable
    families are listed for PH and ZH only.
  - **The WERI mini-applicator manual**. It carries no pitch figure.
- **Siblings.** I skimmed their idea titles and the openings of the ones
  nearest my view, to avoid rebuilding them:
  - terminal-supply: carrier-as-handle, housing-as-fixture;
  - into-the-housing: preload the housing, converging shuttles;
  - ribbon-as-pallet: gang stop die, loose-contact cassette, spool as
    magazine;
  - force-and-form: die cassette and shop press.

  What I built instead:
  - **c1** answers into-the-housing i3's objection to odd-then-even crimping:
    the rows never share a fixture.
  - **c5** reuses ribbon-as-pallet a4's spool feed, but changes what the
    machine makes.
- **J4 and J7 orderings** were searched exhaustively over the layouts that keep
  peel pairs adjacent ([`calc/order_search.py`](calc/order_search.py)).

## Directions considered and not developed here

Each gives why it was not developed and what would revive it.

1. **The carrier strip loads several cavities in one push.**
   - Why not: it needs the carrier pitch to be a multiple of 2.5 mm. Würth's
     is 7.10 mm; the nearest multiple, 7.5, is 0.40 mm off [calc §7].
   - Revives if: JST's own SXH pitch, licence-gated, is 5.0 or 7.5 mm. One
     100-piece Digi-Key strip under a caliper settles it (xh-facts
     Unresolved 2).
2. **Gang-crimping a whole half-row's conductor barrels in one stroke at
   3.4 mm.**
   - Why not: the conductor profile needs ±0.05 mm and hardened steel. A
     laser-cut comb cannot give that. Wire EDM is a quote-and-wait service.
     The ribbon-as-pallet and force-and-form explorers already hold gang
     crimping at strip pitch with bought punches.
   - Revives if: a quick, cheap wire-EDM source turns up, or bought single
     punches narrower than ~3.2 mm.
3. **Axial stagger instead of two planes** (odd conductors cut 8 mm longer so
   the two rows' contacts sit at different stations).
   - Why not: at the even contacts' station the odd conductors pass 1.7 mm
     away and collide with open wings by ~0.65 mm. It would also leave 8 mm
     slack loops in the finished loom.
   - Revives: only combined with out-of-plane separation, which c1 already
     does.
4. **Both half-rows crimped in place at once**, row A opening up and row B
   opening down.
   - Why not: row A's anvil blade and row B's conductors interfere by
     ~0.05 mm in section.
   - Repair used instead: c1 parks plane B folded down and back.
5. **Pre-curling the conductor wings as the tack** in c1b.
   - Why not: it risks a malformed B-crimp in the final die.
   - Kept as a test inside c1b, not adopted.
6. **Pre-tinning (solder-dipping) the strands before crimping** to stop
   splaying.
   - Why not: general practice advises against crimping solder-dipped
     conductors, because the solder cold-flows and the crimp loosens
     [assumption, not sourced here].
   - Revives if: a sourced standard says otherwise for this contact.
7. **Laser-welding the strands to the barrel with the XLaserlab.**
   - Why not: it is a kW-class tool against 0.2 mm bronze and 0.08 mm strands.
   - Revives if: a low-power pulsed source is available and a trial shows
     control.
8. **Buying pigtails and splicing them to ribbon.**
   - Why not: it adds a joint per conductor on every loom. The repo builds a
     loom as a tested unit and avoids solder splices on field-serviceable
     branches [repo cable-assemblies.md].
   - Revives if: bought pigtails exist only in lengths too short to run the
     whole loom and splices become acceptable.
9. **A ribbon already at 2.5 mm pitch** (no splay step).
   - Why not: it changes the looms' wire. No 22 AWG silicone ribbon at 2.5
     mm pitch is known here, and XH's 1.9 mm maximum insulation OD means it
     would need a 0.6 mm or wider web between conductors.
   - Revives if: such a ribbon is found.
10. **A plain 2.54 mm female header on the XH wafer.**
    - Why not: it mates the posts but loses the XH housing's polarisation. A
      reversed plug puts 12 V on signal pins. Out of bounds: the brief says
      the loom ends in XH housings.
11. **The housing as the comb** (preload uncrimped contacts into the XHP
    housing, crimp at its rear face, push home).
    - Why not: developed by the into-the-housing and terminal-supply
      explorers.
    - What I add: the wing-width gap table [calc §3]. Clone wings collide at
      2.5 mm (−0.30 to −0.75 mm); JST's catalog envelope, if the wings really
      fit inside it, leaves 0.55 mm. (The Würth contact first listed here has a
      1.45 mm box and is not an XH contact; see wave 2.)

## Open questions I could not settle

- Whether any third-party IDC housing mates the XH wafer. There was no
  search; it is in the sourcing requests.
- The RC balance-lead market's real gauges and lengths. There was no search;
  it is in the sourcing requests.
- Whether a pitch-changing cam pallet at 3.4 → 5.0 mm is something industry
  sells. I believe variable-pitch pick heads exist, but this is unsourced.

## Log (wave 2)

- **Read.** terminal-supply's critique of this explorer in full; the digest;
  every other explorer's summary; the wave-2 files that build on this view
  (force-and-form f5b, f9, f2c; borrowed-machines b8; machine-that-sees-and-learns
  v8; procedure-is-the-machine p6; into-the-housing i6, i6b, i2d, k6;
  terminal-supply a6, a7, x1, a2d; hand-tool-as-press a2d, a4b, a6); the
  coordinator's Prime pass (`sourcing/amazon-prime.md`).
- **Web.** WebSearch was spent. One WebFetch: the Würth 646 001 137 22 drawing
  PDF, read as an image. Section C-C gives the box as 1.45 × 2.00 mm, so the
  contact is smaller than XH (1.85–1.95 × 2.2–2.4). terminal-supply's point
  stands. ctq.py no longer puts Würth in any XH table; c4 says what the
  drawing is still good for (the only public carrier pitch of the class).
- **The critique, point by point.**
  - c1 Break 1 (fixed punch vs stepping ram): agreed. c1 now has a fixed C
    and a slide that steps clamp and pallets together.
  - c1 Break 2 (row A's wires in row B's zone): agreed; Repair A adopted
    (both rows crimped, then two pushes with the housing still). Repair B
    (flip) does not clear the wires: the housing sits on the flip axis at the
    tip plane, so the flip only mirrors the wires in the working plane, and
    lifting first puts them where the rising ram is. Residual: split length
    6–26 mm [w2 §6].
  - c1 Break 3 (wing clash on the lift): agreed as a real conflict. In-place
    repairs (steel pilot, end-first order, load at 5.0 mm) reduce it; branch
    c1c removes it by narrowing the neighbours.
  - c1 Break 4 (bellmouth through printed links): adopted, box face on a
    hardened front stop in the die block.
  - c1 Break 5 (lance): adopted, lance groove out the front, anvil top above
    the pocket floor, windows-down housing (assumption flagged).
  - c1b Breaks 1–3: adopted (two-pass tack at 6.8 mm; grip bands and what they
    must resist; flag box-first through open jaws to a box-keyed clip).
    force-and-form adds that JST's two-step tools form the conductor barrel
    first; tack-first reverses it. The physics of why it might matter
    (rearward strand extrusion into the window against a held jacket) is in
    c1b tried 2.
  - c2: reference crimp also gives the tab stub target and a genuine
    insertion sample; transfer of height is rougher (stranding). Harness
    house added as the far end of the "buy" axis. Prime pass filled in (b)
    and (c): right gauge and jacket, too short.
  - c3: the folding arch is steel; fold-and-solder on strip added.
  - c4: Würth corrected; supply form and "which arrangements each wing width
    suits" added.
  - c5: supply for a run added (strip + housing stick; or c6 sticks).
- **New direction: c6, pre-form the contact.** The five steps start from the
  contact as bought. Adding a step before them, done in bulk with no wire,
  changes the contact's shape so the later steps get easier: a keyhole
  insulation barrel (bore 1.55–1.60, throat 1.3–1.5, outside ~2.0 mm). It
  narrows open contacts to about JST's catalog envelope, turns placement into
  a snap, and stops loose contacts nesting. c6b is the motorless first build;
  c1c is the combination with c1.
- **Where c6 conflicts with others.** The hanging rail (terminal-supply a3),
  post plate (a6) and pocket plate (v4b) orient by the wide wings. Order
  resolves it: orient, then pre-form.

## Directions considered in wave 2 and not developed

1. **The skew end** [w2 §8]. Part the webs back to a diagonal root line at
   angle β to the conductors, and bend every free conductor by the same angle
   (90° − β). Their pitch becomes 1.7/sin β: β = 42.8° gives 2.5 mm with a
   47.2° bend, 30° gives 3.4 mm, 19.9° gives 5.0 mm. Every conductor makes the
   same bend, so one groove shape translated N times replaces a fan block, and
   the free length is only the bend (~5–7 mm) against 14–18 mm for a fan.
   Neighbours touch (1.7 mm apart) before the bend and part after it; they
   never cross.
   - Why not developed: the finished loom leaves the housing ~47° off the
     contact axis, in the row's plane, over the neighbouring wafers; it needs a
     diagonal fold or a backshell to turn it back. And it helps the splay and
     insertion, not the crimp: before the bend the tips are staggered only
     1.83 mm per conductor at 1.7 mm lateral pitch, so open contacts still
     collide.
   - Revives if: the board layout leaves room for an oblique exit, or a
     backshell (ribbon-as-pallet a3) is adopted anyway and can carry the fold.
2. **The parallelogram converge.** With a diagonal root at 19.9°, crimp at
   5.0 mm, then rotate every conductor about its root by the same angle to
   close the pitch to 2.5 mm, like a parallel ruler. Equal free lengths keep
   the conductors parallel but stagger the tips by 4.33 mm per conductor;
   unequal lengths chosen to align the tips at 2.5 mm break the parallelogram.
   - Why not developed: the tip stagger defeats a gang push, and J1 would need
     a 42 mm diagonal split.
   - Revives if: insertion is one contact at a time anyway, where stagger does
     not matter.
3. **Pre-narrowing the conductor barrel too** (to ~1.6 mm), so the preloaded
   housing's narrow punch fits beside open neighbours at 2.5 mm.
   - Why not developed: it risks the B-crimp's formation, the one place where
     precision matters.
   - Revives if: sectioning of pre-formed insulation barrels shows the final
     die re-forms them cleanly, which would make a light conductor pre-curl
     worth one trial.
4. **The full ring** (c6 sub-variant): wings closed to a ring just over the
   jacket, conductor threaded axially. Kept as a paragraph in c6; it serves
   force-and-form f3/f4's axial threading.
5. **One pallet used twice in c1.** Incompatible with crimping both rows
   before either push. Revives only with a press that works from above the
   ribbon plane.

## Open questions after wave 2

- How hard a pre-formed kit contact grips the jacket, and what it takes to
  snap it in. Five minutes with a kit contact, a 1.55 mm pin, flat pliers and
  the bench scale.
- Whether a real crimper's insulation profile re-forms a keyhole cleanly. One
  SN-2549 crimp on a pre-formed contact, cut and looked at under the ELP.
- The SN-2549's full-open gap at the XH nest (pin gauges).

## Files

- `summary.md` is rendered by the coordinator from this explorer's structured
  return; the harness refuses summary files from subagents.
- Ideas: c1, c1b, c1c, c2, c3, c4, c5, c6, c6b, c7 in `ideas/`.
- Calc: `calc/ctq.py` (wave 1, Würth removed from XH tables),
  `calc/order_search.py`, `calc/on_force_and_form.py` (exchange),
  `calc/wave2.py` (Würth box, pre-form geometry, forming force and springback,
  snap and grip, sticks, c1 split length, c5 run supply, skew end),
  `calc/on_into_the_housing_w3.py` (exchange), `calc/wave3.py` (the keyhole
  under a B-die, the tall and tool-made pre-forms, the mandrel rule, throat
  retention, row B's stored bow, c7's pin maps and housing widths, pre-forming
  in a host's press).
- Sketches, all schematic: c1, c1b, c1c, c3, c5, c6 (pre-former), c6-shapes,
  c6b-bench, c7 in `sketches/`. `sketches/make_w3_sketches.py` generates
  c6-shapes, c6b-bench, c1c and c7; the others are hand-written SVG.

## Log (wave 3, exchange with into-the-housing)

- Wrote [`../../exchange/change-the-question--on--into-the-housing-w3.md`](../../exchange/change-the-question--on--into-the-housing-w3.md);
  numbers in [`calc/on_into_the_housing_w3.out.txt`](calc/on_into_the_housing_w3.out.txt).
- Open against this explorer's own files, from that exchange (carried into the idea files in the final pass, below):
  - c1 and c1c: their two row pushes with web and housing still need ~7 mm of stored length per
    pushed conductor (4-9 mm bows) [w3 section 7]; S2 (sort into one row, housing moves) is the repair
    that stores none.
  - c1c's hardened box-face front stop and c6b's clip stop block the conductor barrel's forward
    growth [w3 section 3]; hold until capture, then back off, or a 10-30 N detent.
  - c1c's anvil blade must satisfy into-the-housing's lance condition (t >= 0.34-0.74 mm or a slot).

## Log (wave 3, final pass)

- **Read.** hand-tool-as-press's reading of this explorer
  ([`../../exchange/hand-tool-as-press--on--change-the-question-w3.md`](../../exchange/hand-tool-as-press--on--change-the-question-w3.md))
  and its calc; its new files a4d (K2), a6b (K1), a6c and the flag-seat sketch;
  into-the-housing's k7 and k8 (built from this explorer's S1 and S2); the
  repo's `pcba.tsx` for J1, J2, J4 and J7 pin orders.
- **Acted on, point by point.**
  - H1 (the round keyhole is a shape the die neither makes nor re-forms):
    agreed that the tips are never turned over; disagreed that the final
    stroke only indents the jacket. The die's side walls pinch the ring, and
    because the tips sit higher than the widest point they move in 1.3–2.2
    times as far: with a 1.80–1.90 mm insulation section the throat closes to
    ~0.75–1.4 mm [calc wave3 §1]. The result is an O with a narrowed gap, not a
    B; whether it passes JST's bend criterion is a test, now written into c6.
    c6 sets out three pre-forms side by side (keyhole, tall keyhole on a blade
    mandrel, tool-made U) with what the final die does to each; new sketch
    c6-shapes.
  - H2 (grip quoted at the mandrel): agreed. c6 now chooses the mandrel from
    the measured jacket (bore 0.08–0.12 mm under it) and states go and no-go
    pins by that rule [calc wave3 §3].
  - H3 (a flag dragged box-first drags its lance): agreed. c6b and c1b's hand
    crimp use hand-tool-as-press's flag seat. c6b adds a coin-cell lamp through
    a floor strip and the leaf, so it needs no microcontroller. The "enter from
    the front" fallback is dropped: a split ribbon end cannot be threaded back
    through a nest; the fallback is now the PA-09 (Prime-confirmed).
  - H4 (cam plate and anvil in one place): c1 and c1c spread at a second
    station at another X; c1c's ending B has no cam plate at all.
  - H5 (carriers against a fixed stop; proof pull restraint): a retracting
    front stop (seated before a crimp, backs off at capture, out while
    stepping) answers both H5's stepping problem and the growth problem (B4 in
    this explorer's exchange with into-the-housing). Rear hard stops in the
    tracks and a latch pin into the slide take the proof pull.
  - H6 (C orientation): the spine stands in front of the housing nest's path,
    arms reaching back.
  - H7 and consistency 7 (punch and anvil widths): tongue ≤4.45 mm, anvil
    ≤1.90 mm, carried into c1 and c1c.
  - Consistency 3 (throat retention): restated as half to all of push-in,
    0.15–30 N by throat [calc wave3 §4].
  - Consistency 4 (lance numbers): c1 now quotes xh-facts (0.6–0.9 proud,
    ~2.4–2.6 behind the front).
  - Consistency 5 and 6 (box plus lance 2.8–3.3; tack-first order): c1b
    rewritten; a single-stroke tool touches the insulation wings first, so
    only tacks tighter than that mid-stroke state are in question.
  - K1 and K2: developed by hand-tool-as-press as a6b and a4d. Not duplicated
    here; c6, c6b, c1c and c1b link them and carry the parts that change this
    explorer's ideas (the seat, the tool-made pre-form, the tongue and anvil
    widths, the electrode at the anvil).
  - K3 (stick as a2b's chute), K4 (c5's T4 under a3 / a2d), K5 (a1b as c3's
    fold station), K6 (the JST lead as a sweep target): one line or paragraph
    each in c6, c5, c3 and c2.
  - From this explorer's own exchange with into-the-housing: the feed-length
    rule is now in c1 and c1c (the housing moves onto row A; row B stores its
    7 mm as a bow formed at the park; or k8's sort), the lance condition on the
    anvil, steel as master in X, a held-back presser tine for J7's crossing.
- **New idea: c7, straight across.** The pin map is the only reason J4 and J7
  cross. Four ways to remove it: swap J4's pins 2 and 5 and move J7's GND to
  pin 5 (board); ribbon assignment by pin block for J4 and GND on the 3P for J7
  (no board change, far-end cost); one ribbon per housing (board, ~9–11 mm of
  edge); one wider ribbon per loom (sourcing unknown). New sketch c7.
- **Every idea file** now opens with "Picture it", states what locates what
  and the reference for fixed, and reads as the idea as it stands.

## Directions considered in wave 3 and not developed

1. **A c6c file for the tool-made pre-form bench (K1).** hand-tool-as-press's
   a6b is that bench, whole. Revives if a6b is withdrawn, or if the tool-made
   pre-form gets a machine form of its own here (a host's press pre-forming on
   strip before the shear [calc wave3 §7]).
2. **Pre-forming in c1c's own press, in the pallet.** A ≤4.45 mm tongue meets
   open neighbours' wing tips below ~3.6–4.0 mm pitch [calc wave3 §7], and the
   pallet runs at 3.4. Revives with strip (pre-form before the shear) or a
   5.0 mm load pallet that closes to 3.4 after pre-forming, which brings back
   a cam plate under the pallet.
3. **A flag entering the SN-2549 from the front, conductor threaded back
   through the nest.** Impossible for a split ribbon end, whose other
   conductors are webbed behind. Revives only for a single-conductor lead.
4. **Dragging a flag on the anvil with a pusher behind the box's rear
   shoulder.** A person cannot reach through a nest. Revives in a machine,
   where a pusher finger can (hand-tool-as-press's a2 / a2b family).
5. **Side lead-in ramps on c1c's front stop** (hand-tool-as-press H5's first
   repair). The retracting stop also solves growth, so it was used. Revives if
   a solenoid at the die block is unwanted.
6. **A cam plate with a window at every carrier** (H4 repair a). 1.5 mm
   printed webs carrying the spread's side loads. Revives only if the spread
   must happen at the press.
7. **Storing no length in either row of a two-move fill.** Moving the web
   clamp instead of the housing only moves the storage to the other row; all
   contacts entering together (k8) is the only way to store none.
8. **Raising the flag's grip to feel the stop by hand.** A bore 0.15–0.2 mm
   under the jacket gives ~5 N, still below what a person can sense through a
   jacket, and doubles the snap force. The lamp was used instead.

## Open questions after wave 3

- The SN-2549, empty contact, closed one click at a time under the ELP: is
  there an insulation-first window, and at which click?
- The SN-2549's XH insulation section: a B or not, and how wide (1.8–2.0 mm
  assumed)? It decides how far a keyhole's throat closes.
- The SN-2549's opening at the XH nest, jaw to jaw: 3.5–4.9 mm is needed for a
  flag seat.
- The jacket OD of five split conductors, and whether it wanders along a
  spool.
- One keyhole-pre-formed contact crimped in the SN-2549, cut and looked at,
  then bent toward the throat a few times: does it hold?
- Would a board revision of J4's and J7's pin orders be acceptable, or a wiring
  change (J4 by pin block, J7's GND on the 3P)? Is there board edge for one
  housing per ribbon?
