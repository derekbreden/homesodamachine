# f7 — Where the steel comes from: die cartridges from four sources, closed by any press

Explorer: force-and-form. The tooling every press here uses
([`f3`](f3-knee-micropress.md), [`f4`](f4-crimp-head-goes-to-the-wire.md),
[`f5`](f5-die-cassette-and-the-shop-press.md), [`f5b`](f5b-half-row-cassette.md),
[`f6`](f6-two-blades-two-drives.md), [`f8`](f8-narrow-press-at-the-housing-mouth.md),
[`f9b`](f9b-tack-on-the-strip.md), [`f10`](f10-lift-once-fin-from-below.md)).
Sketch: [`../sketches/f7-die-cartridges.svg`](../sketches/f7-die-cartridges.svg) (schematic).
**[Prime]** is a row of [`../../../sourcing/amazon-prime.md`](../../../sourcing/amazon-prime.md),
observed 2026-09-28.
Numbers: [`../calc/wave2.out.txt`](../calc/wave2.out.txt) §2, §8;
[`../calc/final_w3.out.txt`](../calc/final_w3.out.txt) §7 [calc final §n];
[`../calc/on_into_the_housing.out.txt`](../calc/on_into_the_housing.out.txt) §3;
[`../calc/force_loop.out.txt`](../calc/force_loop.out.txt) §4.

## Picture it

On the bench sits one small press, f3's knee press or the 1 t arbor press, with
a steel pocket on its bed and a flat pusher. Beside it stand four **die
cartridges**. Each is a palm-sized guided die: a steel base and a steel top
plate on two ground pins, a return spring, a stop block between the plates,
one crimper and one anvil (or a stack of them), and a flat button on top. All
four share the same outer shape, the same two dowel holes in the base, and the
same button, so any of them drops into the pocket and any pusher closes it.

What differs is where the steel of the dies came from:

1. **SN jaws.** A $9.99 replacement jaw pair for the SN-2549, seated by
   closing the jaws on each other and then tightening, the way the tool itself
   is re-jawed.
2. **A knife set.** The spare conductor crimper, insulation crimper and anvils
   of an OTP-standard XH applicator, clamped in a slot as the applicator's ram
   holds them.
3. **EDM plates.** A crimper and an anvil cut by wire EDM from pre-hardened D2
   to a drawing, the drawing traced from 1 or 2 and from JST's analog contacts.
4. **Bought ground pieces.** An anvil blade of precision-ground flat stock
   stood on edge, lapped on top, or a stack of hardened shim leaves clamped face
   to face; a crimper from 1, 2 or 3.

The person drops a cartridge in, lays a contact and conductor in (or the strip
and carriage of f3 do), and the press closes it. Each cartridge's own stop,
not the press, sets the bottom.

- **What locates what.** Fixed is the cartridge's base, doweled into the
  press's pocket; the two ground pins locate crimper to anvil; the contact sits
  in a keyed nest on the base (box slot, lance relief, front stop), or on a
  strip's pilot pin in f3.
- **What carries the force.** The press's pusher onto the button, through a
  preloaded disc-spring stack, into the dies and the cartridge's stop block;
  the press frame carries only the pusher's force.
- **How it knows.** A load cell under the anvil inside the cartridge, a
  0.001 mm indicator across its plates for re-touch height, then sections and
  pulls on a sample.
- **No motor is needed.** A 1 t arbor press by hand closes any cartridge
  [Prime: VEVOR AP-1, $61.90, 281 ratings]. On a first afternoon the four cartridges crimp
the same ribbon side by side, and machine-that-sees-and-learns' v3 sweep (or a
caliper, a camera and a luggage-scale pull) says what each makes.

The point of the arrangement is that the die is the part to buy or make. The
press is a solved problem at this speed; every source of die steel brings a
different set of freedoms and limits into whatever machine carries it.

## What each source gives a machine

| | SN jaws | OTP knife set | EDM plates to a drawing | Ground stock (anvils) and laser-cut plates (everything else) |
|---|---|---|---|---|
| **Cost, lead time** | $9.99 a set, days [source: icrimptools.com]; hand-tool-as-press saw $4.99–9.99. No Prime listing sells the jaws alone; the iCrimp IWS-0723K set carries a 2549 die in its frame, $46.59, thin [Prime] | Listings exist for XH2.54 knife sets [source: terminal-supply, eBay 376757376428 and AliExpress 3256803331644772 titles]; price not observed, ~$30–100 and 1–3 weeks from China [estimate]. No Prime listing [Prime: "OTP XH crimper and anvil blade set", none found] | Not observed; ~$50–200 a part and 1–3 weeks [estimate]. JLCCNC states ±0.05 mm; a good shop holds ±0.005–0.01 [estimate] | Ground flat stock ±0.013 mm in thickness [assumption: ±0.0005 in typical]. SendCutSend laser cutting ±0.127 mm, 2–4 days, in mild steel, 4130, 1095 (annealed, hardens after cutting to Rc 65), CPM MagnaCut (60–63 HRC after heat treatment), AR500 [source: sendcutsend.com, 2026-09-28]. JLCPCB 304 stencils from $3, ~24 h [source: into-the-housing]. Hardened shim: [Prime: Precision Brand 1095 blue-tempered shim assortment, 0.005–0.032 in, $53.39]; 0.032 + 0.025 in = 1.448 mm, 0.032 + 0.032 + 0.010 in = 1.88 mm |
| **Profile** | Today's crimp, whatever it is | An industrial XH profile, tooled for some XH contact, probably a clone | Whatever the drawing says; the first drawing is a guess | Anvils only: a flat-topped blade whose width is the stock's thickness |
| **Crimp height set by** | The jaws bottoming on each other, if they do; a shim between the bottoming faces raises it, nothing lowers it | The cartridge's stop, as the applicator's CH wedge does (0.02 mm steps over 2 mm in one maker's applicator [source: crimpapplicator.com KS-EM40R]) | The cartridge's stop, or shoulders cut on the anvil block that the crimper walls bottom on | The stop |
| **Insulation height** | Fixed by the jaw's step | Separate blade: its own stop or its own drive ([`f6`](f6-two-blades-two-drives.md)) | Separate blade if drawn so | — |
| **Width, and so where it fits** | One jaw plate carries four nests over ±10–15 mm: fits a tool frame or a single cartridge, never a row | Blades a few mm wide: a travelling head's nose (f4), or N sets side by side at a pitch no smaller than a set's width (f5) | Anything: N matched profiles in one plate cut in one program (f5, [`f5b`](f5b-half-row-cassette.md)); a 2.9 mm conductor crimper with 0.7 mm walls for the housing's mouth ([`f8`](f8-narrow-press-at-the-housing-mouth.md)); an overlap insulation profile (f6 branch) | Anvil blades of any length: a gang anvil ground as one block |
| **Lance relief** | Unknown; in the tool the box sits outside the jaw | Probably on the anvil, as applicators relieve the terminal track [assumption] | Drawn in | Filed or ground into the anvil's front end |
| **Closing on an arc or straight** | In the tool, an arc; in a cartridge, straight, and that changes little: the tool's one-wing lead is 0.05–0.17 mm at first touch, the roll at compaction under 1.2° [calc: wave2 §2] | Straight, as designed | Straight | Straight |
| **What it asks of the machine** | Copying the jaw seat (two screws, a 2.5 mm hex, seating faces unmeasured) into the cartridge | A slot and clamp that hold the blade stack as the ram does, and crimper-to-anvil centring, which JST's MKS-L manual checks "with a loupe" [mfr, via terminal-supply] | A profile to draw, and the patience to cut several widths (1.50, 1.55, 1.60 mm) in one order and keep the one whose crimp lands on target | Lapping a narrow edge flat, and hardening O1 at home if not bought hardened |
| **Ideas it serves** | f1 (in the tool), f3 route a, f10's SN-crimper branch, hand-tool-as-press a1–a4 | f2 (inside the applicator), f3 route d, f4, f6, f9b, f10, terminal-supply a2, borrowed-machines b3 | f5, f5b, f6's overlap branch, f8, f9b's nest, f10's crimper, into-the-housing i1b/i2, ribbon-as-pallet a2b | Every cartridge's anvil, f10's fin, stop blocks, shoes, holders, strippers, neck blades, combs, f9b's rail and tack comb |

## Tolerances: which source can make which feature

A crimp die has one or two features that need a hundredth, and several that
need a tenth [calc: wave2 §8; calc final §7]:

| Feature | Needs about | Sources that reach it |
|---|---|---|
| Conductor crimper channel width, single die with its own height setting | ±0.05 mm, if the width is measured (pin gauges) and the height set for it: compaction goes with width × height, and ∓0.027 mm of height restores ±0.05 mm of width at 0.8 mm. J.S.T. UK's own crimp-width tolerance on its analogs is ±0.05 [mfr S13, S14] | quick-turn EDM (JLCCNC states ±0.05); a good EDM shop; harvested SN jaws or knife-set blades as made |
| Conductor channel widths across a gang plate with one height stop | ±0.01 mm between stations, or a shim per anvil | one EDM program at a good shop; or separate ground anvils each shimmed |
| Roof form (arches, cusp height) | not toleranced by anyone here | whatever the profile's source makes; judged only by sections |
| Anvil width (clearance in the channel) | ±0.02 mm | ground stock stood on edge; a good EDM shop; harvested |
| Stop or shut height | ±0.1 mm when adjustable | any of them, with a shim, wedge or lapped stop |
| Holders, strippers, stop blocks, shoes | ±0.15 mm | laser cutting, then lapping the faces that matter |

- A 1/16 in (1.5875 mm) ground anvil with 0.04–0.08 mm clearance makes a
  1.63–1.67 mm channel and crimp width; a 1.5 mm gauge-plate anvil makes
  1.54–1.58 mm. JST's analog SXA-01T is 1.50 wide [mfr S14]; the KONNRA clone
  spec allows 1.75 ±0.15 [source via ribbon-as-pallet].
- **The target height follows the width.** The KONNRA clone's 0.73 mm at
  1.75 mm wide, the context's ~0.88 mm at 1.50 and JST's analog 0.80 at 1.50 are
  one compaction, 1.20–1.32 mm² of width × height. At the anvils above the
  targets are 0.78–0.86 mm (1.54), 0.76–0.84 (1.58), 0.74–0.81 (1.63) and
  0.72–0.79 (1.67) [calc final §7]. A height copied unchanged from a 1.5 mm
  reference over-compacts a wider crimp by 3–10 %, so the JST reference lead's
  copper correction (change-the-question c2) is redone at each die's measured
  width.
- Laser-cut steel at ±0.127 mm never makes a channel. It makes everything
  around it, in days.
- Printed parts never make a die face: a wing tip on a printed face reaches
  thousands of MPa against 50–100 MPa [calc: force_loop §4].

## The cartridge itself

- **Stop in the cartridge, spring in the pusher.** A cartridge with its own
  stop and a press with its own geometric bottom (f3's knee) must not fight.
  A preloaded disc-spring stack between pusher and button lets the cartridge's
  stop take the surplus, as in hand-tool-as-press a4. The only Prime disc
  springs are a light stainless assortment with no stated load [Prime: Hilitchi
  Belleville assortment, $14.99]; a heavy-series stack (DIN 2093 class) is not yet confirmed on Prime. A
  plain compliant rod does the same job: with stops, compliance in the loop is
  the design, since the surplus past the stop is the loop's stiffness times the
  margin (force-and-form's reading of procedure-is-the-machine, B4). An arbor press or the
  shop press simply lands on the stop, and the force it adds past the crimp
  goes into the stop block.
- **Force.** A button load cell under the anvil, inside the cartridge, reads
  the die force alone; one under the pocket reads die plus stop and still shows
  the whole curve up to the moment the stop lands.
- **Height.** A 0.001 mm indicator across the cartridge's plates, as f3's is
  across its dies, reads the re-touch height.
- **Alignment.** Two ground pins in bushings line-bored together, or a bought
  miniature die set; ±0.01–0.02 mm between crimper and anvil laterally.
- **Chasing a height.** With the stop set low as an over-travel guard only, a
  motor-driven pusher can approach the measured crimp height in two or three
  hits (f3 variant, [calc: wave2 §10]).

## What was tried against it

1. **"The first EDM drawing is a guess."** It is. The repairs are to trace the
   profile of a harvested jaw or a knife-set crimper under the ELP camera at a
   known scale, to cut several widths in one order, and to section the
   results beside the JST reference crimp. The first order is a measurement,
   not a die.
2. **Knife sets are tooled for somebody's contact.** Section an OTP crimp next
   to the $0.90 JST lead, copper-corrected (change-the-question c2). If the
   profile is a clone's, it may still crimp genuine SXH well; only the section
   and the pull say.
3. **SN jaws may not bottom.** Then crimp height depends on the cartridge's
   stop, which is fine: the cartridge has one. The jaws' faces then need not
   touch, and the stop is lapped to height.
4. **Hardening at home.** O1 and 1095 harden in oil from a torch and temper in
   a kitchen oven, with some distortion. A narrow anvil distorts little; a long
   gang anvil may bow and need lapping after.
5. **Does one cartridge per source cost four times the work?** The base, top,
   pins and stop are the same laser-cut set four times; only the die pockets
   differ.
6. **A laminated shim anvil** (1095 blue-tempered leaves clamped face to face,
   top lapped across the leaves) makes a width of any sum of shim thicknesses,
   but spring temper (~Rc 45–50 [assumption]) under 400–900 MPa of mean die
   pressure may coin its top. It is a first anvil to try, measured after each
   batch.

## Contribution

- **The die is the part to buy or make; the press is solved.** Each die source
  implies a different machine, and this sets them side by side with their
  costs, lead times and freedoms.
- **Anvils from ground stock stood on edge**: width set by a grinder
  somewhere else, to ±0.013 mm, for a few dollars.
- **SN jaws closed straight crimp as the tool does, or more symmetrically**
  (on paper).
- **A common cartridge**, so four steel sources can be compared on the same
  ribbon on the same afternoon, and whichever steel Derek settles on moves into
  f3, f4, f5, f8, f9b or f10 unchanged. At procedure-is-the-machine's reel clamp
  (p6) each qualification crimp also gets an identity, open and short check and
  a proof pull reacted by the whole reel, and a bad sample costs 6 mm of reel.
- **Channel width as a measured quantity, not a toleranced one**: cut to
  ±0.05, read with pin gauges [Prime: Accusize pin gage set, $45.58], and the
  height set for that width.

## How it connects to the whole procedure

It is the crimp step's tooling, used by every press here. As a first build it
automates nothing: the person lays contact and conductor into an open
cartridge, and the press closes it. It is useful the week it is made as a way
to find which steel makes the right crimp on this ribbon, and it becomes the
die of whatever machine follows.

## Major unresolved problems

- **Knife-set price, dimensions and profile**, unobserved.
- **EDM price and real tolerance** at a quick-turn service, unobserved, and
  the roof form, which nothing toleranced here covers.
- **The SN jaw seat geometry**, unmeasured.
- **Whether an HSS parting blade's top edge is flat enough** to serve as an
  anvil without lapping [assumption: parting blades are T-section, widest at
  the top edge].
- **Line-boring the cartridge pins** on a drill press to ±0.01–0.02 mm, or
  buying a miniature die set.

## Which conclusions rest on assumptions

- **Arc-versus-straight** rests on a pivot 10–35 mm from the XH nest.
- **Knife-set and EDM prices and lead times** are estimates.
- **Ground stock tolerance** is a typical catalogue figure, not observed.
