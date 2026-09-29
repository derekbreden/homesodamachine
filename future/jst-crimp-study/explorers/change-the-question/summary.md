# change-the-question

*The five steps as listed are one way to cut the problem.*

This page indexes every arrangement this explorer holds, with the explorer's own one-paragraph picture of each. The idea files carry the development. Paths are relative to this directory.

## Arrangements

### [c1 — Half-rows: crimp at ribbon pitch, splay with the contacts on, fill the housing in two moves (process change)](ideas/c1-half-rows.md)

The flat-stripped ribbon end sits in a web clamp; interlaced jaws put odd conductors in plane A and even in plane B, and B is folded down and back. A presser comb lays a whole half-row into a pallet of open contacts at 3.4 mm; the slide steps each carrier to a fixed steel C (spine in front of the housing nest, arms reaching back), where a steel pilot and a <=1.90 mm anvil blade lift it 3.2-4.2 mm past its neighbours into a punch of any width, box face on a front stop that backs off at capture, height from a hard stop. Both rows are crimped; at a second station a cam plate spreads them to 5.0 mm, the housing slides 7 mm onto row A, and row B is pushed in using a bow it took when its pallet parked; a real-wafer test ends it.

- contacts: either loose or strip · steel: any of several · meeting: conductor brought to a fixed die.
- **Automates:** split, place contact on conductor, crimp, verify crimp, insert, verify insertion and pin order.
- **What the person still does:** Loading loose contacts into pallets unless a loader does; laying the ribbon end in the clamp; the J4 and J7 crossings (a held-back presser tine handles J7's one crossing); housings in and finished ends out; the stripper.
- **Major unresolved problems:**
  - The lift beside worst-case clone wings leaves 0.15 mm between tips (c1c removes it)
  - J4 needs a per-loom split jaw or a hand step; c7's pin map removes it
  - Row B's stored 4.6-8.6 mm bow must stay below row A's wires as pallet B rises between them; k8's sort stores nothing
  - Silicone web under interlaced jaws and a 90 deg park fold untested (repo Open item 5)
  - Split length 12-20 mm for the jaws, 6-26 mm for row B's move (Derek's question)
  - ~0.5 mm carrier walls holding a box square and taking 20 N on the rear shoulder
  - Insertion force and latch unmeasured

### [c1b — Tack first: a light machine places and pins every contact; the heavy crimp comes after, anywhere (branch of c1)](ideas/c1b-tack-first.md)

c1's clamp, split and one-motion lay put open contacts under a half-row; a steel tack comb (profiles at 6.8 mm, two passes with wide clone wings) closes every insulation barrel loosely over a steel anvil strip, 66-660 N per half-row from a lever, toggle clamp or small lead screw, to a hard stop. Each conductor leaves carrying its contact as a flag at the right axial position and roll. The heavy conductor crimp happens elsewhere: by hand in the SN-2549 with the flag carried on a sprung seat to a leaf stop and lamp, in a WC-110, in force-and-form f9's keyed nest, or in the row (c1c).

- contacts: loose kit contacts · steel: made dies (EDM, machined, laser-cut) · meeting: pallets dock (all contacts placed at once) · usable without a motor.
- **Branch of** c1.
- **Combines:** [hand-tool-as-press/a6c](../hand-tool-as-press/summary.md), [force-and-form/f9](../force-and-form/summary.md).
- **Automates:** split, place contact on conductor.
- **What the person still does:** The conductor crimp (to the person or another machine), insertion, loading pallets, stripping, the J4/J7 crossings.
- **Major unresolved problems:**
  - Tack grip on silicone spans 0.1-50 N; it must exceed a keyed slot's 0.1-0.5 N
  - Crimp quality for tacks tighter than the single-stroke mid-point (sectioning)
  - The SN-2549 must open 3.6-4.4 mm at the nest to take a tacked flag on a seat; unmeasured
  - Inherits c1's J4/J7 crossings and split length

### [c1c — Half-rows crimped where they lie: narrowed neighbours, a fixed press, both rows crimped before either is inserted (combination)](ideas/c1c-crimp-in-the-row.md)

One X slide carries the web clamp, two pallets at 3.4 mm on swing arms, and the housing nest through the throat of a fixed steel C whose spine stands in front of the nest's path. Pallets are filled from loom-order sticks of pre-formed contacts (or strip, or open contacts later tacked); a presser comb snaps a whole half-row, and because every neighbour is ~2 mm wide a one-nest punch (or an SN nest cut to a <=4.45 mm tongue) crimps each contact where it lies over a fixed <=1.90 mm anvil, the pallet floating in X so the punch's flare centres it, a retracting stop on the box face, and an anvil electrode naming the conductor before force. Both rows crimped and proof-pulled into the slide, they go into the housing at a second station: two moves (cam spread, housing onto row A, bowed row B pushed) or into-the-housing's sort into one row (k8).

- contacts: pre-formed contacts · steel: any of several · meeting: conductor brought to a fixed die.
- **Branch of** c1.
- **Combines:** [terminal-supply/a2](../terminal-supply/summary.md), [force-and-form/f3](../force-and-form/summary.md), [hand-tool-as-press/a4d](../hand-tool-as-press/summary.md), [into-the-housing/k8](../into-the-housing/summary.md).
- **Automates:** split, supply contacts, place contact on conductor, crimp, verify crimp, insert, verify insertion and pin order.
- **What the person still does:** Keeping sticks or strip and housings in their feeds; laying each ribbon end in the clamp (14 calls per unit, one per run from c5's spool); J4/J7 crossings at the lay in the two-move ending; the stripper.
- **Major unresolved problems:**
  - Final crimp over a pre-formed or tacked insulation barrel (an O over a keyhole, a B over the tall shapes); re-registration unmeasured
  - Split length 6-12 mm (T4) to 15-26 mm (J1) for the two-move ending, ~25-30 mm on J4/J7 for the sort
  - Two-move ending: row B's bow staying clear; sort ending: lower pad through a window sized for an anvil
  - ~0.5 mm carrier walls
  - An SN tongue over a flat HSS anvil loses the SN's lower cradle; cutting a hardened jaw to 4.45 mm
  - Insertion force and latch not public

### [c2 — Buy the crimp: factory-crimped XH leads, and what is left to build (part and product change)](ideas/c2-buy-the-crimp.md)

Contacts arrive already crimped: JST's ASXHSXH22K leads (black 22 AWG, SXH both ends, <=12 in, $0.65 at 100), RC balance leads with populated XH housings on 22 AWG silicone (Prime, 200-300 mm), or pre-crimped single silicone XH wires (Prime kit). On the bench the person inserts, dresses, cuts to length and makes the far end, with a lot check by sectioning and pull. The $0.90 JST lead is also every arrangement's genuine reference crimp: crimp and insulation form, JST's tab stub, pull, insertion trace, and the target for grip-position maps and per-barrel sweeps.

- contacts: bought pre-crimped · steel: no crimp dies (tack, solder, IDC or bought) · meeting: not applicable (supporting station or module) · usable without a motor.
- **Combines:** [hand-tool-as-press/a1b](../hand-tool-as-press/summary.md), [hand-tool-as-press/a5](../hand-tool-as-press/summary.md), [into-the-housing/i2](../into-the-housing/summary.md).
- **Automates:** strip, place contact on conductor, crimp.
- **What the person still does:** Insertion (a, c), extracting J2's contact 3 (b), dressing discrete coloured wires flat, cut to length, the far end.
- **Major unresolved problems:**
  - Lengths: JST leads stop at 12 in, Prime balance leads 200-300 mm; only J5 fits
  - Discrete coloured wire loses flat dress, clip channels and all-black
  - J4, J6, J7 must be silicone
  - J2's guard cavity needs an extraction per unit with (b)
  - Crimp height transfers only roughly from the JST lead (different stranding)

### [c3 — Fold and solder: light fold, solder makes the joint (joint change; not a crimp, outside JST's support)](ideas/c3-fold-and-solder.md)

A contact in a steel-inserted nest (or still on its strip) receives the laid-in conductor; a sheet-steel arch in a printed holder, closed by a servo or small stepper at ~0.1-0.3 kN, curls the wings around the strands and stops 0.2-0.3 mm above crimp height. Or the SN-2549's own stroke, stopped short by hand-tool-as-press a1b's cradle, is the fold. The Hakko FX-888D on a Z slide with a stepper-fed 0.5 mm solder wire solders the barrel at the brush in 1-3 s; on strip the tab neck is a thermal choke, so the contact is folded and soldered before the shear. The camera sees the fillet, a four-wire milliohm check and a pull verify it.

- contacts: either loose or strip · steel: no crimp dies (tack, solder, IDC or bought) · meeting: die head brought to a still conductor · usable without a motor.
- **Combines:** [hand-tool-as-press/a1b](../hand-tool-as-press/summary.md), [terminal-supply/a2](../terminal-supply/summary.md).
- **Automates:** place contact on conductor, crimp, verify crimp.
- **What the person still does:** Insertion, loading contacts or strip, solder and tip upkeep, and the decision whether a soldered XH joint is acceptable.
- **Major unresolved problems:**
  - Not a crimp: JST disclaims non-JST tooling; IPC/WHMA-A-620 probably treats solder in a crimp as a defect
  - Solder wicking under silicone and fatigue at the wick line under vibration
  - Flux into the box versus wicking toward the insulation when tilted
  - A cold joint inside the barrel is invisible to the camera

### [c4 — Change the part, not the machine: an IDC twin for the XH wafer, and XH contacts chosen for the machine (part change)](ideas/c4-parts-that-mate-the-wafer.md)

If an IDC housing mated the XH wafer, the ribbon end would be split, laid in a 2.5 mm comb over the housing, and pressed once, with the housing placing every contact at once; JST makes none for XH (its IDC twin KR serves PH) and neither search nor the Prime pass found one. The contact half sets out genuine BXH, SXH strip, clone reels, kit contacts, pre-formed contacts (keyhole 1.96-2.14 mm; tall shapes 1.82-2.05 mm) and P0.6N by open insulation width and supply form, and says which arrangements each suits. Wurth 646 001 137 22 has a 1.45 x 2.00 mm box and is not XH; its 7.10 mm carrier pitch is still the only public one of the class.

- contacts: not applicable · steel: no crimp dies (tack, solder, IDC or bought) · meeting: the housing locates the contact.
- **Automates:** place contact on conductor, crimp.
- **What the person still does:** Splitting and laying the ribbon in the comb, one press stroke, the test (IDC case); otherwise it is a part-selection input.
- **Major unresolved problems:**
  - No XH-mating IDC housing found
  - 60-strand 1.7 mm silicone is outside any IDC qualification seen
  - Open insulation-wing width of genuine BXH and of the kit contacts unmeasured
  - JST SXH carrier pitch unpublished

### [c5 — Ends as stock: the machine makes XH-ended ribbon in spool runs, not looms (process and scheduling)](ideas/c5-ends-as-stock.md)

A 4P spool feeds its leading end, squared by the last cut, into a hosted termination arrangement (c1c, force-and-form f2c, borrowed-machines b8, into-the-housing k7 on strip, or hand-tool-as-press a3/a2d with no configurability); the end is tested on a real wafer through the rest of the spool on a slip ring; the feed pushes out 400 or 700 mm and a guillotine cuts; ends drop into bins by type. A long T4 run is 21 ends, 84 contacts (one 100-piece strip) and 21 XHP-4, so spool, strip and housing stick change on one visit, ~3-4 h unattended. With c7's one ribbon per housing, every end type becomes its own spool run.

- contacts: either loose or strip · steel: any of several · meeting: not applicable (supporting station or module).
- **Combines:** [force-and-form/f2c](../force-and-form/summary.md), [borrowed-machines/b8](../borrowed-machines/summary.md), [procedure-is-the-machine/p3](../procedure-is-the-machine/summary.md), [hand-tool-as-press/a3](../hand-tool-as-press/summary.md), [hand-tool-as-press/a2d](../hand-tool-as-press/summary.md), [into-the-housing/k7](../into-the-housing/summary.md).
- **Automates:** cut, cut to length, verify insertion and pin order.
- **What the person still does:** Spool, strip (or sticks) and housing-stick changes per run; emptying bins; at build, cutting to length, peeling branches and the far end; the pair types if they stay by hand; reading J4/J7 tags.
- **Major unresolved problems:**
  - Depends on a termination arrangement that runs a spool unattended; each host is unbuilt
  - Strip-fed pallet loader and housing-stick escapement not built
  - J3's loom length unmeasured
  - Pair ends need two spools fed edge to edge (or c7 (b))

### [c6 — Pre-form every contact before it meets a wire: an insulation barrel the conductor snaps into (a new step in front of the five)](ideas/c6-pre-form-the-contact.md)

A palm-sized steel pre-former, fed from strip, from an orienting rail, post or pocket plate, or by hand, holds each contact by its box (steel nest or a cut XHP stub, lance untouched), slides a mandrel into the open insulation barrel and closes steel jaws around it at 10-80 N; the mandrel is chosen from the measured jacket OD (1.56-1.57 mm for a 1.70 mm jacket, go 1.57, no-go 1.62-1.65). A round pin gives a keyhole (1.96-2.14 mm wide) that a B-die only pinches into an O with a narrowed throat; a flat blade gives a tall keyhole whose tips the die finishes into a B; the crimper's own stroke stopped early gives the same tall U (hand-tool-as-press a6b). Contacts stack nose to tail in loom-order sticks; at the next station a presser snaps the jacket in (0.3-30 N) and a front tine lays the strands, so the contact hangs on its conductor (0.1-3.5 N axially).

- contacts: pre-formed contacts · steel: made dies (EDM, machined, laser-cut) · meeting: not applicable (supporting station or module) · usable without a motor.
- **Automates:** supply contacts, place contact on conductor.
- **What the person still does:** The crimp and insertion to a host; orienting loose contacts to a rail, plate, post or person; dropping contacts into the nest by hand if nothing feeds it.
- **Major unresolved problems:**
  - Which pre-form and whether its final crimp is sound: the keyhole's O-shaped crimp needs qualifying on bends and vibration; re-registration of a narrowed barrel
  - Whether the SN-2549 has an insulation-first window (edge model 0.65-1.7 mm of die travel, apex model possibly none)
  - The SN-2549's insulation die profile and width (sets how far the keyhole's throat closes)
  - Snap force and retention span an order of magnitude on estimates
  - Jacket OD and its variation along a spool set the mandrel
  - Springback scatter across kit clones
  - Crimp beside open neighbours at 2.5 mm in a one-pass preloaded housing still up to 0.2 mm short
  - Roll held only by friction once a flag leaves its pocket

### [c6b — By hand this week: a lever pre-former, a snap block, and a flag seat with a lamp on the SN-2549 (branch of c6)](ideas/c6b-by-hand-this-week.md)

On one printed baseplate: a toggle-clamp steel pre-former where Derek pre-forms a unit's 53 kit contacts into labelled loom-order sticks while a print runs; a snap block with a steel-floored keyed pocket, tip stop and backlit window where a two-tine thumb tool snaps one stripped conductor into its contact; and the SN-2549 in a simple cradle carrying hand-tool-as-press's flag seat (rear U on the jacket, keyed front slot, both at 1.1-1.7 mm above the anvil on 1-3 N springs) so the lance never drags, with an insulated leaf stop preloaded 10-30 N and a coin-cell LED that lights when the box bridges the slot's floor strip and the leaf: stop pushing, then squeeze. Insertion is into-the-housing's i5 sensing nest. No motor, no microcontroller.

- contacts: pre-formed contacts · steel: SN-2549 or similar hand-tool dies · meeting: conductor brought to a fixed die · usable without a motor.
- **Branch of** c6.
- **Combines:** [terminal-supply/a2c](../terminal-supply/summary.md), [hand-tool-as-press/a6b](../hand-tool-as-press/summary.md), [into-the-housing/i5](../into-the-housing/summary.md), [into-the-housing/i2d](../into-the-housing/summary.md).
- **Automates:** —.
- **What the person still does:** Every motion, done by the person; each act has one part and one stop. Estimated 20-32 s per contact against ~25 s today; the case is consistency, not minutes.
- **Major unresolved problems:**
  - Whether the SN-2549 opens 3.5-4.3 mm (keyhole) or 3.6-4.9 mm (tall keyhole) at the nest for the seat; if not, the fallback is the Prime PA-09
  - Everything c6 leaves: the final crimp over a pre-formed barrel, snap and grip on real kit contacts, springback, jacket OD
  - Strip length for the tip stop: 2.4 mm (JST) vs 1.6-2.1 mm (clone spec)
  - Whether three simple steps are quicker in total than today's one

### [c7 — Straight across: change the pin map, the housing count or the ribbon width, so every XH end lies in ribbon order (product change or wiring choice)](ideas/c7-straight-across.md)

Eight of the ten housings already take their ribbons in ribbon order; J4 and J7 cross only because of the board's pin order (J4: 3V3, GND, V5, IO25, IO26, IO27, IO23; J7: RB1-RB4, CLO, CHI, GND). Swapping J4's pins 2 and 5 and moving J7's GND to pin 5 makes both one layer with no crossing in one plane or in half-rows; with no board change, J4 by pin block (4P = pins 1-4, 3P = 5-7) and J7 with GND on the 3P are straight at a far-end peeling cost. Splitting every two-ribbon housing into one housing per ribbon (~9-11 mm of board edge) makes every end a single ribbon (4P into XHP-4 becomes 7 of 14 ends); a wider 6P/7P/9P ribbon per loom moves the crossing to the hand-made far end. Every comb, pallet, preload and sort machine then needs no crossing mechanism.

- contacts: not applicable · steel: not applicable · meeting: not applicable (supporting station or module) · usable without a motor.
- **Combines:** [procedure-is-the-machine/p3](../procedure-is-the-machine/summary.md), [into-the-housing/i6](../into-the-housing/summary.md).
- **Automates:** —.
- **What the person still does:** The board or wiring decision; in (a') and (c) extra peeling at the far end; in (b) more identical housings carried by labels and loom length.
- **Major unresolved problems:**
  - Routing cost of a J4/J7 pin change on the board not assessed
  - Far-end cost of (a') and (c)
  - Board edge for one housing per ribbon
  - Availability of 6P/7P/9P 22 AWG silicone ribbon
  - Whether reservoir B's reed common can ride J7's 3P

## Combinations with other explorers

- c1c = change-the-question c1 (half-rows) + c6 (pre-formed contacts) or c1b (tack) + terminal-supply's repairs (fixed press, both rows first, box-face stop, lance groove, strip-fed pallet loader) + a press from force-and-form f3 (knee), hand-tool-as-press a4d (SN nest cut to a <=4.45 mm tongue over a <=1.90 mm anvil) or terminal-supply a2 (OTP knife set) + into-the-housing's rules (lance condition, growth-safe stop, steel as master in X). Its two endings: two moves (housing onto row A, bowed row B pushed) or into-the-housing k8's sort into one row.
- c6 x into-the-housing i2/K1: pre-formed contacts snapped and crimped in their own cavity; the stepped crimper's insulation mouth swallows a keyhole with 0.23-0.52 mm to spare. Developed by into-the-housing as k7.
- c1c x into-the-housing i6: crimped half-rows sorted into one 2.5 mm row, housing pushed on; no cam plate, no stored length, crossings become an order of placement. Developed by into-the-housing as k8.
- c6/c6b x hand-tool-as-press a6/a1b: the SN-2549 pre-forms its own contacts (click k), a snap block makes flags, a foot-closed SN-2549 crimps each on a sprung flag seat with electrode stops. Developed by hand-tool-as-press as a6b; c6 and c6b link it rather than duplicate it.
- c6b x hand-tool-as-press's flag seat x into-the-housing i2d stub x terminal-supply's box-keyed clip: the SN-2549 by hand with a keyed seat at h = 1.1-1.7 mm and a coin-cell lamp through the box, no microcontroller.
- c1c x hand-tool-as-press a4: one SN nest cut to a tongue crimps in the row with no stand-out beside narrowed neighbours at 3.4 mm; anvil <=1.90 mm; height by stop, force cap by a disc stack, height read by re-touch on a DITR-0105. Developed by hand-tool-as-press as a4d.
- c5 x hand-tool-as-press a3 / a2d: T4 spool runs need no configurability; the unspooled remainder on a slip ring is the far-end electrode array before any loom exists.
- c3 x hand-tool-as-press a1b: the SN-2549's own stroke stopped 0.2-0.3 mm above crimp height is c3's fold, in the contact's own profile, at 3-20 N of grip.
- c2 x hand-tool-as-press a1b/a5 and into-the-housing K1: the $0.90 JST lead's insulation height and width as the target for grip-position maps, per-barrel sweeps and a custom insulation step; cut open, it is the reference B against which a pre-formed barrel is judged.
- c6 x hand-tool-as-press a2b: a loom-order stick of pre-formed contacts stood over the flat tool's nest is its chute, replacing the revolver disc.
- c7 x every comb, pallet, preload or sort arrangement (c1, c1c, k8, i6, force-and-form f5b, ribbon-as-pallet a2): with J4's pins 2 and 5 swapped and J7's GND on pin 5, every loom lies straight and those machines need no crossing mechanism; c7 (b) x c5: every end a single ribbon, every type its own spool run.

## Transferable mechanisms

- Pre-form the part before it meets the wire, and choose the pre-form by what the final die does to it: a round keyhole is only pinched into an O by a B-die (throat 1.3-1.5 to ~0.75-1.4 mm at a 1.8-1.9 mm die), while a tall keyhole or the crimper's own stroke stopped early leaves the tips above the closed height for the die to finish into a B.
- Size a gripping bore from the measured part, not the nominal: bore 0.08-0.12 mm under the measured jacket OD, mandrel chosen to stay in that window across springback, go and no-go pins set by the same rule.
- The crimp tool as its own pre-former: a single-stroke die touches the tall insulation wings before the conductor wings, so stopping it inside that window (a ratchet click or a set grip) narrows the barrel in the profile that will finish it (from hand-tool-as-press).
- When a held part's grip is below what a person can feel, end the push with a signal: a coin cell and LED wired through the part itself (floor strip and leaf stop bridged by the box), no microcontroller.
- A stop that retracts: seated before the crimp, backs off ~0.3 mm at capture, out of the way while the slide steps. It lets the conductor barrel grow under coining and keeps stepping boxes from meeting the stop sideways.
- Carry a flag level on sprung supports above the anvil so its lance never drags over a jaw edge; the punch seats it and the springs lift the crimp back out (hand-tool-as-press's flag seat).
- A fixed steel C with its spine in front of the work's path and arms reaching back; the slide carries the work through the throat in X, so tails and parked pallets stay outside the loop.
- Do the spread at a second station, not under the press; at the press only the anvil sits under a carrier.
- Proof-pull loads go into the slide through a latch pin and rear hard stops in the tracks, never through a swing-arm pivot or a carrier spring.
- Two sequential fills of one housing need stored length in one row (the feed-length rule): move the housing onto the first row and store the second row's travel as a bow formed when its pallet parks; or sort everything into one row and store nothing.
- Change the pin map instead of the machine: two pin orders are the only reason looms cross; a swap on the board, a ribbon assignment by pin block, one housing per ribbon, or one wider ribbon per loom removes every crossing mechanism downstream.
- Loom-order sticks of non-nesting contacts are the build list (J2's blank spacer), and size the supply to the run so the spool change and the strip change fall on one visit (from wave 2, still standing).

## Key findings

- A round keyhole under a B-profile insulation die is not re-formed into a B: its metal ends at 1.28-1.66 mm, below the ~1.8 mm closed height, so the arches never reach the tips; the die's side walls pinch the ring and, the tips sitting above the widest point, close the throat 1.3-2.2 times the side travel, from 1.3-1.5 mm to ~0.75-1.4 mm with a 1.80-1.90 mm die and hardly at all with 2.00 mm [calc explorers/change-the-question/calc/wave3.out.txt s1; hand-tool-as-press htq s1]. The result is an O with a narrowed gap; it needs its own bend and vibration qualification.
- The mandrel must follow the measured jacket: for a 1.70 mm jacket, a 1.56-1.57 mm mandrel keeps the bore at 1.58-1.62 mm across 0.02-0.05 mm springback (go pin 1.57, no-go 1.62-1.65) and grips 0.13-3.5 N; a 1.60 mm mandrel chosen from the nominal grips nothing on a 1.60 mm jacket. The Prime-confirmed Accusize set (to 1.52 mm) covers only a ~1.60 mm jacket [calc wave3 s3; sourcing/amazon-prime.md].
- A tall pre-form (blade mandrel, or the crimper stopped early) has a U 1.38-1.69 mm inside, 0.01-0.21 mm per side of interference on a 1.6-1.8 mm jacket, and grips 0.02-3.5 N axially with walls and silicone in series; with the tips still vertical it retains the jacket only by friction (0.02-3.5 N), and once the curl starts (tip gap 1.2-1.4 mm) by 0.3-27 N [calc wave3 s2].
- Throat retention of the keyhole, taken as half to all of push-in, is 0.15-11 N at a 1.5 mm throat, 0.25-20 N at 1.4 mm and 0.35-30 N at 1.3 mm [calc wave3 s4].
- A <=4.45 mm one-nest tongue clears open clone neighbours only from 3.6-4.0 mm pitch up, so a host press can make the tool-made pre-form on strip or at 5.0 mm, not in a 3.4 mm pallet [calc wave3 s7].
- In a two-move fill, row B's 7 mm of travel stored as a bow over a 6-26 mm split is 4.6-8.6 mm deep, and drawing it costs only the conductor's 0.2-4 N buckling load [calc wave3 s5; on_into_the_housing_w3 s7].
- J4 and J7 are the only looms that cross, and only because of two pin orders [repo hardware/pcb/pcba/pcba.tsx]. Swapping J4's pins 2 and 5 and moving J7's GND to pin 5 makes both one layer with no crossing in one plane and none in half-rows; J4 by pin block and J7 with GND on the 3P do it with no board change [calc wave3 s6].
- One housing per ribbon (J1 5+4, J2 2+3, J4 4+3, J7 5+2) costs ~6.7 mm of housing width, ~9-11 mm of board edge with gaps, and makes 4P into XHP-4 7 of 14 ends and 28 of 53 crimps [calc wave3 s6].
- The Engineer PA-09 is Prime-confirmed ($38.99, 1,719 ratings) as the by-hand fallback if the SN-2549 opens too little for a flag seat; a 12 V push-pull solenoid (Heschen HS-0530B, $7.99, 5 N) is Prime-confirmed for a retracting front stop [sourcing/amazon-prime.md].
- Pre-formed widths, gaps and punch room still stand: keyhole 1.96-2.14 mm; 0.36 mm between keyholes at 2.5 mm; at 3.4 mm beside a keyhole the insulation punch has 0.23-0.42 mm and the conductor punch 0.33-0.65 mm to spare [calc wave2 s2]. A T4 spool run of 21 ends fits one 100-piece strip [calc wave2 s7]. The Wurth 646 001 137 22 box is 1.45 x 2.00 mm, not XH [calc wave2 s1].

## Where this view still had trouble

- J4 without changing the pin map: every half-row or comb variant still needs a per-loom split jaw, a sort, or a person's hands; this view found no machine form that absorbs it cheaply, only the question change (c7).
- Turning a round keyhole into a true B: no variant was found that re-curls tips already sitting below the closed height, short of a second forming step, so the keyhole's final crimp stays an O that needs qualifying.
- A purely mechanical 'at the stop' signal a person can use when the flag's grip is 0.1-3.5 N: the coin-cell lamp works, but a no-electrics cue (a pointer, a click) that fires before the grip is exceeded was not found.
- The tool-made pre-form inside a 3.4 mm pallet: the tongue meets open neighbours below ~3.6-4.0 mm pitch, and every workaround (strip, a 5.0 mm load pallet) brings back something else (a shear, a cam plate under the pallet).
- Row B's stored bow in a two-move fill staying clear of row A's wires as its pallet rises between them: plausible on paper, hard to picture as reliable; the sort ending avoids it but adds a pick.
- Stripping soft silicone at 22 AWG: every idea here receives a stripped end; this view produced no stripper of its own.
- Orienting loose kit contacts without a person, rail, post or plate upstream: pre-forming helps only after something has oriented them.
- The far end: c7 (a') and (c) move crossing and peeling work to the far end, which no machine in this view makes.
- Re-registration of a pre-narrowed barrel in a die, and insertion force and latch behaviour, remain beyond what estimates can settle.

## Questions for Derek

- Close the SN-2549 one click at a time on an empty kit contact, releasing after each, and look end-on under the ELP: at which click are the insulation wings inside the die width, and at which does the conductor barrel first show a mark? It decides whether the crimper can make its own pre-form.
- What does the SN-2549's XH insulation section look like, and how wide is it closed (a B, 1.8-2.0 mm assumed)? One crimp on a bare jacket, cut through, shows it. It decides how far a keyhole's throat closes.
- How wide does the SN-2549 open at the XH nest, jaw to jaw, handles fully open? A flag carried on a seat needs 3.5-4.9 mm.
- Would you caliper the jacket OD of five split conductors (not the ribbon pitch), and check whether it wanders along a spool? It sets the mandrel.
- Five-minute pre-form test: squeeze a kit contact's insulation wings with flat pliers around a ~1.55 mm pin, pull the pin, press a stripped conductor in with your thumb. Does it snap in and stay, and roughly how many newtons does it take to slide it along the wire?
- Would one keyhole-pre-formed contact, crimped in the SN-2549, cut open and bent toward the throat a few times, be worth doing? It shows whether the O-shaped insulation crimp holds.
- Would a board revision of J4's and J7's pin orders be on the table (J4: swap pins 2 and 5; J7: GND to pin 5)? Or a wiring change instead (J4 by pin block, J7's GND on the 3P)? Is there ~10 mm of board edge for one housing per ribbon?
- Does anyone sell 22 AWG silicone flat ribbon at 6, 7, 9 or 10 conductors that you would use?
- How long a parted split behind the housing is acceptable? Half-rows need ~6-12 mm on the 4P looms and 15-26 mm on J1.
- Which of J7's 3P conductors is the trimmed 'third': the one beside the 5P, or the far one?
- Would you caliper the open insulation-wing width of a few kit contacts? At or under ~2.3 mm they may need no pre-form for a narrow insulation step.
- Carried over: is a soldered (non-crimp) XH joint acceptable in principle (c3)? Would a first machine that makes only 4P into XHP-4 ends be a useful start (c5)? What is J3's loom length? Is it worth buying five JST ASXHSXH22K305 leads (~$4.50) as genuine reference crimps?
