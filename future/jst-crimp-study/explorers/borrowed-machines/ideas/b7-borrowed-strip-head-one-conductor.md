# b7 — A bought bench stripper fed one conductor at a time, and the blade geometry it has to have

The wire shop already mass-produces a machine that strips one wire end when the
end is poked into it: the sensor-triggered bench stripper. The wire's tip
touches a sensor, the machine clamps, cuts the insulation to a set diameter,
pulls the slug off, and on the better ones twists the strands on the way out.
Here that machine, bought and unmodified, stands on
[b1](b1-press-and-applicator-with-shuttle.md)'s shuttle rail beside the
applicator, or on [b2b](b2b-pedal-less-hand-station.md)'s bench, where Derek
pokes. Each split conductor is presented to it and goes straight on to the
crimp.

The idea's second half is a finding about which of these machines can work on
this wire at all. It depends on the blade geometry, and the cheap common one
cannot leave an even ring on 1.7 mm silicone over a 0.72 mm strand bundle. The
geometry that can is also sold as a hand tool, which makes a motorless first
version.

**Related:** ribbon-as-pallet's
[a8b](../../ribbon-as-pallet/ideas/a8b-spindle-with-touch-off.md) builds a
spindle that does the same job (two closing blades, a tip-stop electrode, a
twist); its [a8](../../ribbon-as-pallet/ideas/a8-rolling-ring-scorer.md) turns
the conductors under fixed blades. b7 is the bought machine and a static
die-hole head that needs no spindle. [b2b](b2b-pedal-less-hand-station.md) uses
the die-hole head as its strip nozzle; [b3](b3-gantry-carries-the-crimp-head.md)
could carry it.

Sketch: [`../sketches/w2-b7-strip-geometry.svg`](../sketches/w2-b7-strip-geometry.svg)
(the three blade geometries, drawn to scale from the cited dimensions).

Labels: [calc wave2 §n] is this explorer's [`wave2.out.txt`](../calc/wave2.out.txt);
[Prime] is a row in [`../../../sourcing/amazon-prime.md`](../../../sourcing/amazon-prime.md)
(observed 2026-09-28); [facts] is [`../../../context/xh-facts.md`](../../../context/xh-facts.md).

## Picture it

**Where things start.** A ribbon end in b1's cassette, split to the clamp edge
([b6](b6-pierce-at-the-root-pull-to-the-tip.md) or by hand) with the tips still
insulated, folded back as one band.

**The bought machine**, one of:
- **Schleuniger RotaryStrip 2400 class** (used): rotating flat carbide blades;
  "incision diameter" programmable in 0.01 mm steps; "blade way back";
  programmable clamping force; strip length 0.1–34 mm; "controlled twisting of
  inner conductor strands" for 26–13 AWG; starts "when the wire end touches the
  trigger sensor"; optional "radius centralizers"; 390 × 130 × 280 mm, 10 kg,
  100–240 VAC. Rated insulations: "PVC, PUR, rubber, Teflon, Tefzel, Kapton,
  etc." [mfr: RotaryStrip 2400 datasheet, fetched 2026-09-28]. Used units trade
  on eBay and CAE [prior-art §2]; no price was observed.
- **A Chinese sensor stripper** such as the WIREPRO SP-2015E: AWG 32–11, strip up
  to 20 mm, "touch the sensor once to start a stripping cycle", 5 kg, 110/220 V,
  "no blade replacement needed for different wire diameters", quote only
  [source: wireproauto.com, fetched 2026-09-28]. Its blade geometry is not
  stated. No Prime listing of a small-gauge sensor-triggered stripper was found
  [Prime].

**One conductor.**
1. b1's fork lays conductor *k* forward out of the band.
2. The shuttle moves Y to the stripper's nozzle axis, then X pushes the tip into
   the nozzle until it touches the trigger.
3. The stripper clamps the insulation, closes its blades to the set incision
   diameter, pulls the slug off (twisting, on the RotaryStrip) and releases.
4. The shuttle withdraws. A backlit frame of the stub checks strand count,
   length, a clean insulation edge and no flags.
5. The shuttle moves on to the crimper.

**What locates what; the reference for "fixed."** Axially, the conductor's own
tip at the trigger, so the strip line is Ls from the tip; the tip was flush-cut
at the cassette datum, so the two agree within the cut's squareness. Radially,
the machine's blades and centralizer. The shuttle only delivers the tip into the
nozzle's lead-in.

**What carries the force.** The machine's own clamp holds the insulation; the
slug pull of ~1–4 N (with an even ligament) reaches back to the cassette clamp
through the conductor in tension.

**How it knows it worked.** The backlit stub frame. With the loom's far end in a
pogo block and the stripper's blades isolated from its frame, a blade touching
strands reads continuous on that conductor: Schleuniger's own SmartDetect idea
on DC [prior-art §2]. On a bought machine that needs the blade holder insulated,
which is a modification.

**What the person does.** Nothing on b1's shuttle. At b2b, Derek pokes each
conductor into the nozzle.

## Steps it covers and what it hands back

- **Covers:** strip, one conductor at a time, inside the crimp loop; a stub check;
  blade-touch detection through the far end.
- **Hands back:** splitting; presenting (at b2b); everything from the contact
  onward.

## Which blade geometry works on this wire

The strands fill a 0.69–0.74 mm bundle inside a 1.7 ±0.1 mm jacket; the wall is
0.43–0.55 mm, so the bundle can sit ~0.06 mm off centre [facts §7; calc wave2
§3]. The goal is a thin, **even** ring of silicone left over the strands, which
the pull (or a twist) tears at the cut.

| Geometry | Where it is sold | Ligament left, all round | Tear-off | What goes wrong |
|---|---|---|---|---|
| **Two V-blades** closed to an inscribed radius *ri* (most cut-strip machines, many cheap sensor strippers) | everywhere | *ri* 0.45: **+0.02 mm at four points, 0.35 mm at the V bottoms and crossings** (*ri*√2) | 1.5–4.2 N | the cut reaches within 0.02 mm of the strands at four points and only ~0.15 mm into the 0.49 mm wall at four others; the tear wanders at the thick places and leaves flags, and a smaller *ri* nicks. Soft silicone also squeezes into the Vs |
| **Two die-hole blades** (two semicircles) of radius *rd* (precision "die" hand strippers made for PTFE; blades sold by gauge [assumption]) | hand-tool trade | *rd* 0.47 (0.94 mm hole): **0.04–0.19 mm, even around, varying only with the bundle's offset** | 1.1–2.9 N | the hole must suit the bundle: a 0.88 mm hole is +0.01 mm at worst, a 1.00 mm hole leaves up to 0.22 |
| **One blade orbiting** at a fixed radius about a guide axis (RotaryStrip principle) | small-shop machines | at ±0.05 mm centring **−0.01 to +0.02 mm worst**; at ±0.10 mm, **nicks** | ~1–3 N | the conductor must be centred in the guide to ±0.05 mm; that is what the RotaryStrip's centralizers, or a8b's two closing blades, are for |

[calc wave2 §3]

**Twisting.** Shearing an even ring of 0.05–0.15 mm takes only 0.1–1.2 N·mm;
blades gripping the slug with 10–30 N give 2.5–15 N·mm [calc wave2 §3d]. So a
twist during the pull tears the ring around the cut instead of stretching the
slug, and it lays the 60 strands together for the barrel. The conductor behind
the cut must not turn with it: the cassette clamp and a V-clamp just behind the
blades hold it.

**What this says about buying.** A RotaryStrip-class machine with centralizers
is worth a test strip on this ribbon. A V-blade machine is predicted to nick or
flag, whatever its price. The Klein 11063W on the bench is self-adjusting, not a
die-hole tool.

## The die-hole head (the build route)

- **Blades.** A matched pair of die-hole blades with a 0.90–0.94 mm hole:
  replacement blades from a precision die stripper if one is sold near that size
  (a 20 AWG hole is near it [assumption]), or a pair laser- or wire-cut from
  0.5 mm hardened steel.
- **Closer.** A printed parallel closer driven by a servo to screw stops, so the
  blades meet each other: the hole is exact every time, whatever the servo does.
- **Twist.** Optional. The closer sits in a 6700 bearing and an N20 turns it a
  quarter to half a turn during the pull, through a GT2 belt.
- **Tip stop.** A steel plate Ls behind the blade plane, set by shim for the
  contact in use (2.4 mm for genuine JST, 1.85–2.1 mm for clone contacts [facts
  §1; terminal-supply calc w3 §3]), isolated and wired: the conductor's tip
  touching it reads continuous on its far-end channel. That is the trigger, and
  it is ribbon-as-pallet a8b's touch-off.
- **Isolation.** The blades are isolated and wired; any touch on strands is
  logged against the conductor.
- **Pull.** The shuttle backs off 3 mm.

**The motorless version.** The same die-hole blades in a hand lever, or a
precision die hand stripper whose hole suits the bundle, with a printed sleeve
over its jaws that is the tip stop at Ls, wired to an LED through the far end.
Derek pokes, the LED says the tip is at the stop, and he squeezes and pulls.

## Branches looked at inside b7

- **Thermal blades.** A heated blade does not nick strands and a slow machine can
  wait for it. Hakko's FT-802 thermal stripper closes heated blades on the wire
  and strips "even very fine AWG 38", with output in 5 % steps [mfr: hakko.com,
  fetched]; it is on Prime at $516.14, but no G4 blade for about 22 AWG is (the
  G4-1603 seen is 26–38 AWG) [Prime]. The page says nothing on silicone. The
  bench's FX-888D takes knife-shaped tips that could be a single hot blade on a
  servo. Silicone does not melt and decomposes slowly above ~300 °C [prior-art
  §2], so the rate is unknown, and the tin on the strands melts at 232 °C, so
  the strands at the strip line may solder together. One test strip settles
  whether it is minutes or hopeless.
- **An ultrasonic knife.** Hobby ultrasonic cutters (the ~40 kHz handheld class
  sold for model-making and support removal) are said to cut soft rubber without
  the drag that makes a cold blade tear it [assumption; not sourced]. On a depth
  shoe it would score the crowns for a whole-tip strip (b6) without a laser's ash
  and fumes. It still nicks copper if it reaches it.
- **A tightened wire noose.** It cuts silicone evenly from all sides but is not
  self-limiting at the copper: once it reaches the bundle, a 2–5 N loop puts
  0.4–1.1 N on each 0.08 mm strand it crosses, a Hertz peak of several thousand
  MPa against copper's 70–100 MPa yield [calc wave2 §2]. It needs a stop, like any
  blade, and is not developed.

## Problems and their repairs, as they stand

- **Strippers are made for a free wire in a hand, not a split ribbon end.** The
  neighbours are parked in b1's band behind the fold line, so only conductor *k*
  is forward. The machine's clamp sits some millimetres inside its nozzle
  [assumption], so the split must cover the strip length plus that grip:
  ~12–15 mm rather than 8.
- **Silicone stretches instead of cutting.** Under two V-blades it squashes;
  under die-hole blades it is cut evenly and torn at the ring; the twist finishes
  the tear. The backlit frame catches flags.

## Printed and bought

- **Bought:** a RotaryStrip-class or sensor stripper (used market or quote), or
  die-hole blades; a servo, an N20, a 6700 bearing, GT2 pulleys ($5.99 for five
  [Prime]); pogo pins for the far end [Prime].
- **Printed:** nozzle funnel, closer, V-clamp (TPU), mounts, the hand version's
  sleeve.

## Contribution

- The small-shop bench stripper as a station in the crimp loop, fed by the same
  shuttle.
- A rule for choosing one: die-hole or centred rotary blades, not V-blades, on
  soft insulation over fine strands, with the numbers behind it.
- The twist as the tool that finishes silicone's tear at the cut.

## Major unresolved problems

- **The bought machines on this silicone:** untested; the RotaryStrip's rated list
  does not name silicone; used price unknown; no Prime route.
- **Nozzle depth:** how far inside the nozzle the machine grips, which sets the
  split length.
- **Die-hole blades near 0.94 mm:** whether any are sold for a precision stripper
  at this size; otherwise they are made.
- **The strip length** belongs to the contact: 2.4 mm (JST) against the clone
  spec's 1.6–2.1 mm [facts §1]; the stop is set per reel.
- **Isolating a bought machine's blades** for touch detection.

## What rests on what

- **Derek:** the Klein 11063W is the bench stripper today, used down to 24 AWG
  [repo tools.md].
- **Facts:** bundle, wall and jacket [facts §7]; strip lengths [facts §1]; the
  RotaryStrip, WIREPRO and Hakko pages [mfr, source].
- **Calculations:** ligaments by geometry, twist torque, noose contact [calc
  wave2 §2, §3].
- **Estimates:** slug pull with an even ligament.
- **Assumptions:** silicone tensile 4–11 MPa; bundle offset ≤0.06 mm from the wall
  range; rigid-jacket geometry for the V-blade ring (the soft jacket squeezes,
  which makes the V case worse, not better); a 20 AWG die hole is near 0.9 mm.
