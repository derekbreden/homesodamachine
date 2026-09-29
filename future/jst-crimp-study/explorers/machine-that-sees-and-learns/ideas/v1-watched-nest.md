# v1 — The watched nest: a fixed press photographed at every step, fed by a stage that steers by the picture

Explorer: machine-that-sees-and-learns.

Sketches:
- [`../sketches/v1-watched-nest.svg`](../sketches/v1-watched-nest.svg)
  (schematic side elevation);
- [`../sketches/w2-v1-lifted-neighbours.svg`](../sketches/w2-v1-lifted-neighbours.svg)
  (end view at the nest from cited dimensions, and one key);
- [`../sketches/w2-v5-box-roll-gauge.svg`](../sketches/w2-v5-box-roll-gauge.svg);
- [`../sketches/w3-v8-shadow-test.svg`](../sketches/w3-v8-shadow-test.svg).

Numbers:
- **[calc: vision_budget §n]** [`../calc/vision_budget.out.txt`](../calc/vision_budget.out.txt);
- **[calc: cycle_and_cost §n]** [`../calc/cycle_and_cost.out.txt`](../calc/cycle_and_cost.out.txt);
- **[calc: wave2 §n]** [`../calc/wave2.out.txt`](../calc/wave2.out.txt);
- **[calc: campaign §n]** [`../calc/campaign.out.txt`](../calc/campaign.out.txt);
- **[calc: w3htp §n]** [`../calc/w3_on_hand_tool_as_press.out.txt`](../calc/w3_on_hand_tool_as_press.out.txt);
- **[rap P §n]** ribbon-as-pallet's
  [`exchange_on_machine_that_sees.out.txt`](../../ribbon-as-pallet/calc/exchange_on_machine_that_sees.out.txt),
  and **[rap R §n]** the ribbon-as-pallet calc cited there;
- **[bm W §n]**, **[bm X §n]** borrowed-machines'
  [`exchange_sees_learns_w3.out.txt`](../../borrowed-machines/calc/exchange_sees_learns_w3.out.txt)
  and [`exchange_ribbon_as_pallet.out.txt`](../../borrowed-machines/calc/exchange_ribbon_as_pallet.out.txt);
- **[Prime]** a row of [`../../../sourcing/amazon-prime.md`](../../../sourcing/amazon-prime.md),
  observed 2026-09-28.

Related:
- Branch [v1b](v1b-printer-as-stage.md): where the stage's motion comes from.
- Combination [v8](v8-tack-look-crimp.md): the strictest look moved to a light
  tack station ahead of the press, where the barrel is seen straight down.
- Combination [v9](v9-tack-at-the-anvil.md): what this idea becomes when the
  press is an applicator.
- [v7](v7-the-run.md): the controllers, software and supervision it runs on.
- The pallet is ribbon-as-pallet's
  [a1](../../ribbon-as-pallet/ideas/a1-pallet-tour.md) fan block with keys that
  hold the neighbours out of plane.

## Picture it

**Where things start.**
- A small crimp press stands on the bench. Its anvil carries a **nest**: a
  pocket holding one XH contact barrels-up, box forward against an end stop,
  lance in a relief. The punch hangs 15–20 mm above it when open. A load cell
  sits under the anvil.
- A black printed shroud surrounds the nest, so anything silver outside the
  contact's outline is a stray strand.
- A contact arrives in the nest one at a time: from a carrier strip, from
  [v4b](v4b-pocket-plate.md)'s plate by nozzle, or from a person's tweezers.
  The nest differs by supply form (below).
- The ribbon end is cut flush, split and stripped, to the strip length of the
  contact in use (1.6–2.1 mm for clone-drawn kit contacts, 2.4 mm for genuine
  SXH [calc: w3htp §4]). It sits in a **fan block**:
  - the web gripped 25–35 mm back in a channel ~0.2 mm under the ribbon's
    width, which registers every conductor;
  - the conductors fanned to 5 mm pitch, each in its own hinged **key**: a
    printed finger with a groove underneath and a TPU lip, hinged where the fan
    has opened to ~2.5 mm;
  - every key resting up, holding its conductor's axis ~5 mm above the anvil
    plane, above the tallest open insulation wings (2.75–3.2 mm) with margin,
    so a waiting conductor never enters the tooling or the side view
    [rap P §1];
  - each stripped tip standing ~6–8 mm proud of its key, all tips on the flush
    cut's one line.
- The fan block rides a three-axis stage ([v1b](v1b-printer-as-stage.md)):
  across the conductors, along the wire toward the die, and height.
- The loom's far end, unterminated because the XH end is made first, sits in a
  pogo block or push-in terminal block, giving the station MCU a wire to every
  conductor.

**What moves.**
1. The stage brings key *k* over the nest.
2. From one hover picture it corrects across and along so the strands land over
   the conductor barrel and the insulation edge in the window between the
   barrels.
3. A servo plunger presses key *k* down 5 mm to a hard stop on the fan block.
   Only that conductor drops into the open U. The wings are its funnel; the
   key's groove is the hold-down on the insulation.
4. The cameras check. The punch comes down slowly, crimps and returns.
5. The key lifts the crimped contact back to its waiting height.
6. The stage sets the crimp on a blade support in the silhouette window,
   proof-pulls it where the contact form allows, and moves to key *k+1*.

**What locates what.**
- The **nest** locates the contact on the anvil: box in its slot, box face on
  the end stop, barrels on the anvil profile.
- The **camera** locates the conductor relative to the contact. Both are
  measured in one picture with two fiducials on the anvil block.
- The **channel and keys** deliver each conductor to about ±0.1 mm at the key;
  the flush cut puts every tip on one line.
- The stage is steered by the picture, not by its step count.
- **The reference for "fixed" is the anvil,** as the camera sees it in every
  frame.

**What drives the crimp and carries its force.**
- A press from the force explorers, with four properties:
  - a punch that opens high enough for an oblique camera to see the nest, and
    whose body stays under **7.45 mm** wide for the first ~5.9 mm above the
    crimping edge, so it fits between crimped neighbours at 5 mm pitch with
    0.3 mm clearance [calc: w3htp §7];
  - a load cell in the force path;
  - a stroke that the station MCU runs whole against a force envelope
    ([v7](v7-the-run.md));
  - a bottom held to ±0.02–0.05 mm by geometry (a steel stop, dies meeting, a
    crank at bottom dead centre), not by the actuator [digest].
- Hosts with those properties: force-and-form's
  [f3](../../force-and-form/ideas/f3-knee-micropress.md) knee with a narrow
  punch; hand-tool-as-press's one-nest SN die set
  ([a4](../../hand-tool-as-press/ideas/a4-dies-in-a-die-set.md), one nest cut
  6–7 mm wide as in [a4c](../../hand-tool-as-press/ideas/a4c-one-nest-behind-a-tack-station.md)).
  The 7.45 mm is a requirement; whether a given tool meets it is a measurement
  on that tool.
- The force path: ram → punch → contact → anvil → load cell → frame, peaking at
  0.8–2.6 kN [xh-facts §4]. The stage, the keys and the conductor carry none of
  it; the plunger carries a few newtons.
- A steel ceiling sits in series with the drive (a disc stack preloaded above
  the crimp peak, its switch in the drivers' enable line), so the force limit
  does not live only in firmware ([v7](v7-the-run.md)).

**How it knows the crimp worked.**
- About eight pictures, one force trace, a continuity reading and, where
  possible, a proof pull, each compared with limits.
- **Before the stroke:** the contact seated; the strands gathered and every
  strand between the wing tips; the conductor touching the contact, and the
  right conductor (continuity through the far end); the insulation edge in the
  window.
- **After the stroke:** crimp height and bellmouth in silhouette, with the
  box's own silhouette correcting for roll; the brush, the insulation edge, any
  strand outside the seam.
- Every result goes into a log keyed to unit, loom and pin.

**What the person does.**
- Loads fan blocks and contacts.
- Answers the few conductors the machine parks with a question
  ([v7](v7-the-run.md)'s queue).
- Inserts into housings, unless [v6](v6-patient-cell.md)'s stations do it.

The machine runs a unit's 53 crimps in ~1.1–2.9 hours unattended
[calc: cycle_and_cost §1].

**Steps it covers:** place the contact on the conductor (hover prediction, key
lay-in, gate), hold both in the die (nest; key groove as hold-down), crimp
(a borrowed press, MCU-owned stroke), verify (pictures, roll-corrected
silhouette height, force envelope, continuity, proof pull).
**What it hands back:** cutting, splitting and stripping unless v6 does them;
loading fan blocks; contact supply by hand unless strip or v4/v4b; insertion;
answering parked conductors.

## The cycle, one crimp

Each step is a look, an act and a look. The strictest look comes just before
the stroke, because the stroke is the one step that cannot be undone.

1. **Look: empty nest.** Fiducials found; no leftover contact or strand.
2. **Contact in,** by strip index, nozzle or hand.
3. **Look: contact seated.** Box on its stop; barrels level, wings upright;
   lance at its normal height (0.6–0.9 mm proud [xh-facts §1]); centreline
   within ±0.03 mm of the nest axis; the box's own silhouette height recorded
   for the roll check after the crimp.
4. **Look: the stripped tip on the backlight.** Strip length against the
   contact's own figure; bundle width (~0.72 mm gathered); any strand standing
   out; the torn insulation edge. A splayed tip goes to a twist step
   ([v6](v6-patient-cell.md)); a strip outside its band goes back.
5. **Hover and predict.** One picture with the key still up gives the tip and
   the insulation edge.
   - **Across.** The key's groove sets it to about ±0.1 mm, and the open
     conductor barrel captures a gathered bundle within ±0.48–0.59 mm with no
     picture [rap P §2]. So it is predicted and checked. A splayed bundle
     (1.0–1.2 mm) is captured only within ±0.24–0.45 mm, and a groove exit
     2–3° off the wire axis puts the tip 0.24–0.37 mm aside at 7 mm proud
     [calc: wave2 §2]. Those are the tips the picture is for.
   - **Along the wire,** per conductor, from both the tip (the brush past the
     conductor barrel) and the insulation edge (the window). Strip scatter of
     ±0.1–0.3 mm on silicone uses 20–120 % of a 0.5–1.0 mm window
     [calc: wave2 §2], so one reading per ribbon end is not enough.
   - One or two corrections from the prediction usually suffice, each
     approached from the same side so the stage's backlash drops out.
6. **Lay in.** The plunger presses key *k* to its stop. The bend happens at
   the key's root, 20–30 mm behind the contact, at R 24–60 mm [rap P §9]; the
   5 mm in front of the contact stays straight. Spool curl (0.0–0.55 mm at
   7 mm proud [rap P §6]) is not pressed out; the side look measures where the
   tip actually is. A three-roller straightener at the fan block's entry is the
   mechanical alternative.
7. **Gate.** The oblique view, the side silhouette under the lifted
   neighbours, one to eight lighting states, and continuity. It passes only if
   all of these hold:
   - the contact has not moved since step 3;
   - no silver outside the contact outline on the black shroud;
   - no strand above the wing tips in the side silhouette;
   - the bundle casts its displaced shadow under LEDs at 60–75° elevation,
     placed between the raised punch and the lifted neighbours (a strand lying
     on the barrel floor casts none; the geometry is v8's, [bm W §2]);
   - the insulation edge in the window; the brush will protrude past the
     barrel's front;
   - the conductor reads continuous to the grounded contact, and it is the
     conductor the recipe expects.

   Clear passes and fails are decided by thresholds; borderlines go to
   Claude ([v7](v7-the-run.md)'s judge). On a fail the key lifts, the tip is
   re-twisted or the contact re-seated, and it tries again. After two or three
   failures the conductor is parked with a photo and a question.
8. **Stroke,** run whole by the station MCU: approach at ~2 mm/s to a taught
   crawl height ≥0.3 mm above the first wing touch, crawl at 0.05–0.1 mm/s to
   the geometric bottom against a force envelope checked every sample, dwell,
   return. Gross faults stop it: no wire, a second contact, insulation under
   the conductor barrel. A few cut strands (1.7 % of the copper each) do not
   show [calc: campaign §3]; step 4's picture guards against those.
9. **Look: after the crimp.** The key lifts the crimp; the stage sets it over
   the silhouette window beside the nest, onto a hardened blade at the barrel
   centre, stopping at **first silhouette contact**, not at a force. The
   conductor, still webbed into the fan block, then holds the roll the nest
   gave it: at 10–20 mN, 0.3–1.1° [rap P §5]. A gauge pin lies in the same
   frame.
   - **Side silhouette:** conductor and insulation crimp heights at the barrel
     centres, bellmouth, brush length, bend-up or bend-down.
   - **Roll from the box.** The box's silhouette grows 32–34 µm per degree of
     roll [calc: wave2 §1]. Against its step-3 reading and the lot's reference
     height it gives roll to ~0.05–0.3°, and the crimp height is corrected by
     the crimp's width × sin(roll). A crimp rolled more than 2° is re-seated.
   - **Top view** (front-lit, dark ground): crimp width, seam centred, strands
     escaping, twist against the box, insulation in the window.
10. **Proof pull,** where the contact form allows one (next section). The key
    grips the conductor 1–2 mm behind the insulation crimp with its TPU lip, so
    the pull stays local; pulling through the fan instead straightens the
    conductor's S-bend and moves the crimp [rap R §4]. A move of the insulation
    edge over ~0.05 mm at 20 N is a fail.
11. **Clear.** A strip contact's tab is cut by a drop-shear: the carrier is
    pushed down, away from the wire lying on the tab. The key returns to its
    waiting height.

Time: ~69–177 s a crimp, 1.1–2.9 h a 53-crimp unit [calc: cycle_and_cost §1].

## The nest, by supply form

| Form | Nest | Where the proof pull reacts | Side view | Tab |
|---|---|---|---|---|
| Genuine SXH strip | Pilot pins in the neighbours' holes ([terminal-supply a2](../../terminal-supply/ideas/a2-strip-indexer.md)); the station's own hole is under the wire | Through the still-attached **carrier tab**, with a hold-down 3–5 mm ahead of the tab on the box top (1.6–5.7 N at 20 N) and a support under the tab. The tab is then in compression, good to 72–96 N [rap P §3] | Cam 2 on the **downstream** side, where only empty carrier remains. Upstream, fresh contacts stand one strip pitch away (7.1–9.5 mm [xh-facts §1, estimate]) at wing height; a thin side-lit diffuser vane stands in the gap (≥4.1 mm) between the active contact and the next | Drop-shear after the pull |
| Loose kit or BXH | Box slot, lance relief, front stop | A **lance-notched plate** slid into the neck behind the box: thinner than the measured neck gap less 0.2 mm, notched ≥0.9 mm deep and wider than the floor strip and lance, bearing on the box's side walls (and top wall, if it comes down from above): 23 MPa at 20 N [rap P §3]. The lance tip stands 0.24–0.64 mm behind the box [into-the-housing's [`exchange_hand_tool_as_press.out.txt`](../../into-the-housing/calc/exchange_hand_tool_as_press.out.txt) §1, CJT drawing 2.44 ±0.20 mm]. A plate under the floor strip would load the lance at its rated retention (19.6 N clone minimum) | Clear on both sides | None |
| Loose, neck too short for a plate | As above | No per-crimp pull; pull strength by [v3](v3-press-that-runs-experiments.md)'s destructive re-check samples | Clear | None |

Neither width nor height tells the box from the crimped insulation barrel
across lots (box 1.85–1.95 × 2.2–2.4 mm against an insulation crimp of
1.8–1.95 × 2.03–2.46 mm on this silicone [bm W §8]), so anything that reacts on
the box does it in the neck, never by a slot narrower than the box.

## When the press is an applicator

An OTP applicator in a slow crank press (borrowed-machines'
[b1b](../../borrowed-machines/ideas/b1b-applicator-in-slow-crank-press.md))
has v1's "bottom by geometry", but four of v1's asks do not carry to it
[borrowed-machines' exchange on this view, reading the MKS-L manual pp. 9, 20]:
- **The load cell under the anvil.** The anvil is the applicator's hardened
  block in its base; the force path is read by strain gauges on the connecting
  rod.
- **The nest by supply form.** An applicator takes strip only.
- **Neighbours lifted 5 mm.** Upstream of the anvil the strip runs under a
  spring pressure plate several centimetres long at strip height; the wire side
  carries the shear-blade supporter and scrap cover. A 5P fan at 5 mm pitch puts
  neighbours ±5–10 mm across, over exactly those parts, their undersides at
  4.15 mm. An applicator guarantees narrow tooling only for neighbours one strip
  pitch away [bm X §4].
- **The silhouette window beside the nest.** Upstream is live strip; downstream
  is spent carrier and the shear.

So on an applicator the waiting conductors are folded back as one band (b1's
cassette) or the end is crimped upstream-first and parked after
(ribbon-as-pallet's [a1c](../../ribbon-as-pallet/ideas/a1c-crimp-upstream-first-park-after.md));
the rod carries the gauges; the silhouette moves to the dwell's withdraw
position, ≥7 mm out of the applicator. Keeping v1's straight-down look and
dropping the keys gives [v9](v9-tack-at-the-anvil.md).

## Seeing: cameras, light and focus

- **Where the cameras go.** The punch sits right above the nest, so nothing
  looks straight down while it is there.
  - **Cam 1** looks in obliquely, 30–40° from vertical. At 45° the near lifted
    neighbour hides the lowest 0.2–1.2 mm of the U [rap P §1].
  - **Cam 2** looks straight across at wing height and runs under both
    neighbours, with a backlight on the far side.
  - One camera and a small first-surface mirror can serve both, at two focus
    settings.
  - A camera tilted 9.9–11.9° to pass above one in-plane neighbour and below
    the other mixes ~0.3 mm of crimp width into the height [rap P §1], which is
    why the neighbours are lifted.
- **Resolution** [calc: vision_budget §1–3]:

  | Set-up | px/mm | Strand | Crimp height ±0.05 mm |
  |---|---:|---:|---:|
  | Stock ELP at 100 mm | ~45 | 3.6 px | 2.3 px |
  | ELP with a +20 D close-up lens | ~86 | 6.9 px | 4.3 px |
  | 16 MP M12 board, 12 mm lens | ~122 | 9.7 px | 6.1 px |

  Edge fits on backlit silhouettes repeat to ~2–9 µm on the stock ELP.
- **Silver on silver.** Tinned strands in a tin-plated barrel are the camera's
  worst case. The design routes round it: the bundle is checked alone on a
  backlight; the gate looks for silver *outside* the outline on black, for
  strands *above* the wing tips in silhouette, and for a strand with no
  displaced shadow on the floor. [v8](v8-tack-look-crimp.md) gets the same look
  straight down.
- **Glare.** A white diffuse dome for the after-crimp top view.
- **Focus.** Walked upward once per view per run; the lens lands ~60 units
  differently by direction [repo: `tools/panelcam.targets.conf`]. A sharpness
  score on every frame.
- **Capture.** One long-lived capture app holds the camera grant and keeps the
  stream open all run ([v7](v7-the-run.md)). MJPG only; the IMX298 module lists
  4656 × 3496 at 10 fps [Prime]. A sync LED in frame marks the lighting state.

## The electrical channel beside every picture

- **Placement.** The contact is grounded through the nest, and the far end is
  on the pogo or terminal block. A conductor reads continuous the instant its
  strands touch the barrel, independent of the silver-on-silver picture, and it
  names the conductor, so a wrong key is caught.
- **Order of the ends.** The XH end is made first. The far end is a bare cut
  face, and a bad crimp scraps a few millimetres of a loom, not a finished one
  [digest].
- **Limits.** Continuity cannot grade a crimp: 6–34 mΩ of loom against a
  1–2 mΩ crimp [rap R §9].

## Why the picture still reads each conductor

The channel and the flush cut register every conductor, so a picture mostly
checks rather than finds:
- **Across, for a good tip:** checked, not searched.
- **Along the wire:** the flush cut sets the tip, but the window is set by each
  conductor's own torn insulation edge, scattered ±0.1–0.3 mm. The edge is read
  per conductor.
- **The bad tips:** a splayed bundle halves the capture, and a 2–3° groove exit
  uses most of what is left [calc: wave2 §2]. The picture exists for those, and
  also has to find *that* they are those.

The pallet makes the nominal; the picture catches the exceptions and keeps the
record the thresholds learn from.

## References and tolerances: when precision is needed

| Moment | What must be right | What makes it right | What checks it |
|---|---|---|---|
| Contact loading | Centred ±0.03–0.05 mm, box on its stop | The nest pocket, or pilot pins | Step 3 picture |
| Hover | Tip and edge found | Pallet prediction (channel, keys, flush cut) | Cam 1 |
| Lay-in | Bundle within the barrel's capture (±0.24–0.59 mm by bundle width); insulation edge in the 0.5–1.0 mm window | Key groove plus one or two corrections | Side silhouette under the neighbours; continuity |
| First die touch | Contact where the nest put it; conductor held | Nest; key groove as hold-down | Gate picture, then force rise at the expected height |
| Bottom of stroke | Die gap ±0.02–0.05 mm | The press's geometric bottom | After-crimp height with roll correction; force envelope |
| Release | Crimp leaves the die with the wire | Key lift; a stripper plate on the punch [assumption: needed] | After-picture found where expected |
| Proof pull | Load reacted without touching the lance | Carrier tab with hold-down, or a lance-notched plate in the neck | Camera on the insulation edge; load cell |

## Printed and bought

**Printed:** fan block and keys with TPU lips; black shroud; camera and mirror
brackets; diffuse dome; silhouette-window holder; key plunger mount; pogo block
body.

**Steel:** proof plate or tab support; blade support; gauge pin (Accusize pin
gauge set, $45.58 [Prime]).

**Bought or on hand:**

| Item | Source |
|---|---|
| ELP 16 MP camera | On hand [repo: tools.md] |
| Close camera | 16 MP IMX298 M12 module $69.99 with a 12 mm lens $9.99 [Prime]; or a Raspberry Pi HQ camera ($55) with a 16 mm lens ($77.50) ([Adafruit](https://www.adafruit.com/product/4561), 2026-09-28), which needs a Pi |
| Mirror, LED ring, backlight | First-surface mirror $20.90; WS2812B rings $18.99 for five; opal acrylic $11.98 [Prime] |
| Pogo pins | P75-E2, $6.49 per 100 [Prime] |
| Load cell and HX711 | Bar cell with HX711 $9.99 [Prime] for light loads; the anvil cell is the press's |
| Stage | [v1b](v1b-printer-as-stage.md) |
| Press | From the force explorers (above) |
| Servos, ESP32 | [v7](v7-the-run.md) |

## Problems, and what answers them

- **Neighbours in the side silhouette.** With the fan in one plane every inner
  conductor has a neighbour on each side of the view, and tilting the view
  mixes width into height. The keys hold the waiting conductors 5 mm up and
  lower one at a time. borrowed-machines' fold-back band
  ([b1](../../borrowed-machines/ideas/b1-press-and-applicator-with-shuttle.md))
  needs no lift; each root then takes a set of R ~2 mm per reversal.
- **The key root sets the copper.** The key bends the conductor at R 24–60 mm,
  under the 67–78 mm at which the strands yield; 47–81 % of the bend is kept
  [hand-tool-as-press's [`exchange_procedure.out.txt`](../../hand-tool-as-press/calc/exchange_procedure.out.txt) §1]. Every
  conductor that leaves the fan block carries a kink of roughly 5–12°, 20–30 mm
  behind its contact. For a gang insertion from the pallet a squaring step is
  needed; a grip within 2 mm of the contact (v6) is less exposed.
- **The punch blocks the straight-down view.** Oblique and side cameras and a
  long open stroke answer it here. With a tack holding the conductor in the
  contact, the look moves to where nothing stands over the barrel:
  [v8](v8-tack-look-crimp.md).
- **The contact shifts at lay-in.** The gate re-measures it. Whether the
  barrels rock under the key's groove is open.
- **A bad crimp after the stroke.** The whole end is cut back 6–10 mm with the
  fan block's guillotine, so every tip is again on one line. Single-conductor
  re-crimps would leave one conductor short and skew the housing.
- **The camera mount moves when the press fires.** Measurements are relative
  to the anvil fiducials in the same frame, and pictures are taken at rest.

## Contribution

- It lets "place the contact on the conductor and hold both in something that
  crimps" be done by a light, imprecise stage and a printed pallet: the
  picture, the key's groove and the barrel's own funnel share the job.
- It turns every crimp into a record with measurements, pictures and a
  continuity reading.
- It works with any press whose punch opens high enough to be seen past and
  stays under 7.45 mm wide at the neighbours' height.

## Major unresolved problems

- **Silver on silver inside the U** under a raised punch: the shadow test's
  LEDs need room between the punch and the lifted neighbours [estimate], and
  whether a tin floor gives a findable shadow edge is one photograph away.
- **The neck gap,** which decides the loose-contact proof plate. One kit
  contact under the camera.
- **Key design:** a TPU lip's grip on silicone during lift-out and pull;
  0.3–0.4 mm printed walls at a 2.5 mm hinge pitch; the 5–12° kink the key root
  leaves.
- **Punch body width** at the neighbours' height for the host chosen.
- **Silhouette against micrometer crimp height.** ~10 crimps measured both
  ways.
- **Release.** Whether a crimped XH contact sticks in the punch.

## What rests on assumptions

- ELP focal length and nearest focus, which scale every px/mm figure.
- Edge-fit repeatability of 0.05–0.3 px under MJPG.
- Barrel and window lengths from clone drawings.
- That the shadow separates a strand on the floor from the bundle.
- Box-to-box height spread within a lot (roll correction); five contacts under
  the camera measure it.
