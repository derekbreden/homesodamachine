# v4 — Tap, look, pick: loose contacts on a lit tray, singulated by software, placed in the nest

Explorer: machine-that-sees-and-learns.

Sketch: [`../sketches/v4-tap-look-pick.svg`](../sketches/v4-tap-look-pick.svg) (schematic).
Numbers: [`../calc/arm_and_feeder.out.txt`](../calc/arm_and_feeder.out.txt) §3
(**[calc: arm_and_feeder §n]**); [`../calc/on_terminal_supply.out.txt`](../calc/on_terminal_supply.out.txt)
§7; borrowed-machines'
[`exchange_sees_learns_w3.out.txt`](../../borrowed-machines/calc/exchange_sees_learns_w3.out.txt)
(**[bm W §n]**). **[Prime]** is a row of
[`../../../sourcing/amazon-prime.md`](../../../sourcing/amazon-prime.md),
observed 2026-09-28.
Branch: [`v4b-pocket-plate.md`](v4b-pocket-plate.md) (shaped pockets filled by
tapping, where a contact lies flat).
Feeds: [v1](v1-watched-nest.md)'s nest, [v8](v8-tack-look-crimp.md)'s tack nest,
hand-tool-as-press's [a4c](../../hand-tool-as-press/ideas/a4c-one-nest-behind-a-tack-station.md).

## Picture it

**Where things start.**
- A small tray, ~80 × 60 mm, of frosted acrylic or thin white-printed PETG,
  lies on three flexure legs over an LED light pad (XIAOSTAR A5, $16.99
  [Prime]), so contacts read as black shapes to a camera above.
- A push-pull solenoid under one edge taps the tray (Heschen HS-0530B, 10 mm
  stroke, $7.99 [Prime]); a coin vibration motor also works.
- The person pours ~20 loose kit contacts onto the tray.

**What moves.**
1. The tapper taps. The contacts hop, spread and settle in random poses.
2. The camera takes two exposures: backlight only (the outline), then top light
   only (whether the open U faces up).
3. Software sorts every contact: barrels up, heading known; on its side;
   barrels down; touching another.
   - **A barrels-up contact does not lie flat.** The lance stands 0.6–0.9 mm
     below the box floor, so the contact rests on the lance tip and one end,
     tilted ~11–17° [estimate]. The outline and the top-lit shading both show
     the tilt, and the class carries it.
4. A pick head on the stage's Z comes down on a barrels-up contact's box top:
   - a **soft bellows cup** 2–3 mm across that seals on a top tilted 11–17°, as
     pick-and-place machines use for uneven tops (sourcing request); or
   - a rigid nozzle whose face is cut at the tilt, turned to the contact's
     heading from the picture.
   A pressure sensor in the vacuum line confirms the pick, as LumenPnP's nozzle
   sensor does [prior-art §3].
5. The head carries the contact to the nest and lowers it in. The nest's
   chamfers guide the box into its slot and the lance into its relief. The
   vacuum releases.

If nothing usable lies on the tray, it taps again.

**Where the head can deliver.** A nozzle can put a contact into an **open**
nest and nothing more [calc: on_terminal_supply §7]:
- to load a 0.64 mm post (terminal-supply's
  [a4](../../terminal-supply/ideas/a4-post-held-contacts.md)), it drops the
  contact into a loading nest and the post spears it through the nest's front
  stop;
- to stage a contact in a housing cavity (terminal-supply's
  [a5](../../terminal-supply/ideas/a5-housing-as-fixture.md)), it drops it
  box-first onto a post standing in the cavity;
- into v1's nest or v8's tack nest, it places directly.

**What locates what.** On the tray nothing is located: the picture finds each
contact's position and heading to a pixel. The head is steered there by the
stage that carries the pallet, or by a small second head. The **nest** locates
the contact finally; the picture only has to hit the nest's chamfer (±0.3 mm or
so [estimate]). The reference for "fixed" is the nest. With a rotating head any
barrels-up contact is usable; without one, only those within ±15° of the nest's
axis, and the software taps until one is.

**What drives the crimp and carries its force.** Not this idea's business. It
ends when the contact sits in the nest; the only forces are the tap and the pick.

**How it knows it worked.** The vacuum sensor says a contact is on the head. The
nest picture ([v1](v1-watched-nest.md) step 3) says it is seated: box on the
stop, barrels level, lance at its normal height. A contact with a bent lance or
crushed wings is rejected before the crimp.

**What the person does.** Pours contacts, ~60 a unit; clears a jam (two
contacts hooked by their wings that tapping cannot free).

**Steps it covers:** supply contacts (singulation and orientation of loose
contacts), placement into an open nest. **What it hands back:** pouring, jams,
and everything after the nest.

## Where it comes from

Industry singulates loose terminals with vibratory bowls tuned to one part
[prior-art §3]. Robot cells use "flexible feeders": a vision system and a tapped
or vibrated surface, as in FlexiBowl ([flexibowl.com](https://www.flexibowl.com/)).
OpenPnP's ReferenceHeapFeeder picks a random part from a bin and drops it in a
box to make it bounce, uses vision to see which parts are upside up, and picks
and drops again if none are; it is, in its own words, "very slow"
([OpenPnP wiki](https://github.com/openpnp/openpnp/wiki/ReferenceHeapFeeder)).
Slow is the premise here.

## Why the head cannot press the contact flat

The lance, as a plain cantilever (1.5–2.5 mm long, 0.5–0.8 mm wide, 0.20 mm
stock, all assumptions), is **7–52 N/mm** stiff [bm W §13]:
- pressing it flat (0.6–0.9 mm) takes 4–47 N, and as a plain cantilever passes
  first yield after 0.03–0.12 mm of tip travel;
- a 0.2–0.5 N nozzle spring moves its tip 0.003–0.1 mm.

Real lances survive insertion, so they are longer or shaped differently than
this model; even at three times the softest row's compliance, levelling takes
~1.5–2 N. So the head seals on the tilted top instead of levelling it: a
bellows cup, a face cut at the tilt, or picking only from
[v4b](v4b-pocket-plate.md)'s lance-relieved pockets, where the contact already
lies flat. The Juki 503 tungsten nozzle on Prime ($14.99 [Prime]) is rigid and
suits the last case.

## Numbers

How many taps a pick needs depends on how often a contact settles barrels-up,
and on how many are on the tray. With barrels-up odds of 0.15–0.5 and 10–40
contacts [calc: arm_and_feeder §3]:
- **with a rotating head,** almost every tap offers a usable contact: ~3 s a
  pick;
- **without one,** 1.2–8.5 taps: 4–25 s a pick.

Either hides inside the previous crimp's stroke. **The tray measures its own
odds:** twenty contacts, fifty taps, every pose counted by the camera, one
unattended hour.

## The other singulator: the strip

For genuine SXH on strip, shearing the tab over the nest drops every contact
into the nest's pose (barrels up, box forward, lance down) with no vision. The
tray is for the loose contacts on hand, and for BXH.

## Problems, and what answers them

- **Tangling.** Open-barrel contacts hook each other by the wings [assumption:
  common in feeder design]. Few contacts on the tray (10–20); a sharper tap when
  two touch; the head lifts one of a hooked pair and drops it from 10 mm (the
  HeapFeeder's move); a pair still hooked after three tries goes to a reject
  corner.
- **The box top may not be flat** where the head wants it [assumption]. A cup
  over the box's solid wall, or a servo tweezer gripping the box sides.
- **Tapping bends lances.** Soft taps on a slightly compliant tray; every lance
  is looked at in the nest anyway.
- **Magnetic pick.** Phosphor bronze and tin are not magnetic, and the nickel
  underplating on some clones [xh-facts §6] is far too thin to lift a part
  [assumption].
- **Static.** A 0.043 g contact [xh-facts §1] can cling to a printed tray.
  Acrylic or glass on top, and taps rather than vibration.

## Contribution

- It turns the loose contacts Derek already has into a machine-fed supply, with
  singulation as a loop in software instead of a tuned bowl.
- The same tray and camera count contacts, spot deformed ones, and tell a genuine
  JST contact from a clone by outline (clone drawings show wider insulation
  wings [xh-facts §6]).

## Major unresolved problems

- Pose odds and tangling rate: one photo session with a kit.
- Whether a bellows cup or a tilt-cut face holds a tilted 0.043 g contact
  through the carry, and releases it square into the nest.
- Whether the nest's chamfers seat a contact dropped from the head every time,
  or it needs a tamp.
- Vacuum and rotation on a stage that also carries a pallet: separate Z axes, or
  a tool change.
- The lance's real stiffness: press one kit contact barrels-up against the 0.1 g
  scale with a probe on the box top, at 0.1, 0.3 and 0.6 mm.

## What rests on assumptions

- Pose probabilities.
- Box-top flatness.
- The lance as a cantilever of assumed size.
- The ±0.3 mm the nest's chamfers can absorb.
