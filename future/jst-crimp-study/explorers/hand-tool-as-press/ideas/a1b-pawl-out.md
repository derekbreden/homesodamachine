# A1b — Pawl out: the tool as a plain linkage, closure owned by the machine

## Picture it

The SN-2549 sits in [a1](a1-squeezer-cradle.md)'s cradle with its ratchet pawl
removed, or held off its teeth by a servo finger on the release lug.
Everything else is a1's: the cradle, the NEMA 17 Tr8×2 pusher, the load cell,
the insulated-blade locator and the far-end block.

- **Hold.** The pusher closes at ~2 mm/s until the force rises a few newtons
  above the empty-tool curve: the wing tips have met the punch. It stops
  there, and the lead screw holds unpowered. The conductor goes in. If amber
  and green do not come, the pusher opens and the contact is re-seated or
  thrown out.
- **Crimp.** The pusher closes until the force passes a set wall well above
  the compaction peak. Die faces meeting look like a vertical cliff in force
  against position. It stops at the wall and opens.
- **Or stop short.** The pusher can instead stop at a taught grip position
  short of die contact. That is the settable, repeatable stop a crimp-height
  experiment needs (below).
- **Out.** The crimp is lifted off the anvil and drawn back
  ([a1](a1-squeezer-cradle.md)), then passes nose first through
  [a6](a6-foot-closed-jig-bench.md)'s keyhole gauge: the cavity's section, a
  lance notch, and a side slot the wire squeezes out through. A half-crimp, a
  flared wing, a strand outside or a spike of tab stops there without the
  controller's judgement. The proof pull is taken at a6's backed pull plate, or
  a2's pull slot, never in the tool.

**What locates what.** As a1. "Fixed" is the lower jaw; the contact is located
by the front stop and the insulated blade in the neck (or a pilot pin on a
strip stub); the conductor by the funnel, depth by green.

**What drives and carries the crimp force.** The pusher, through the tool's own
linkage, as in a1. The force closes jaw to jaw inside the head. Full closure is
guaranteed by the station MCU's force wall and by die contact, not by a pawl.

**How it knows it worked.**
- A smooth force curve (no pawl sawtooth), checked sample by sample on the
  station ESP32 against a taught envelope.
- Amber and green on conductor *k* only.
- The keyhole on the way out.
- A write-ahead journal on the Mac: a *squeeze intent* written before each
  squeeze and a *result* after it. On restart after a power loss, an intent
  with no result names the suspect conductor, which is re-looked at and asked
  about ([v7](../../machine-that-sees-and-learns/ideas/v7-the-run.md)'s
  journal).

**What the person does.** As a1: places the contact and feeds the conductor, or
a2's carriage does.

## Steps it covers and what it hands back

**Covers:** hold with back-out and retry, crimp to a wall or a set stop, the
force-curve check, the fit gauge on the way out, and the host role for
crimp-height sweeps, pre-forming and folding (below).

**Hands back:** as a1, including the proof pull (at a6's pull jig or a2's pull
slot).

## How it relates

- Branch of [a1](a1-squeezer-cradle.md). It changes one thing: the pawl.
- The press for machine-that-sees-and-learns'
  [v3](../../machine-that-sees-and-learns/ideas/v3-press-that-runs-experiments.md)
  campaign, with [a5](a5-two-squeeze-plier.md) as the two-barrel alternative.
- The motorised pre-former of [a6b](a6b-flags-by-hand-foot-crimp.md).
- change-the-question's [c3](../../change-the-question/ideas/c3-fold-and-solder.md)
  fold station.
- Its force wall and journal follow
  [v7](../../machine-that-sees-and-learns/ideas/v7-the-run.md).

## Major unresolved problems

- **Inside the tool the software is the whole guarantee.** A power loss
  mid-stroke leaves a half-crimp that looks like any other contact in the tool.
  The journal names it on restart; the keyhole stops it before the housing. A
  crimp that fits but is under-compacted is caught only by the force curve.
- **Taking the pawl out** is a teardown of a riveted or pinned tool, and
  whether it comes out cleanly is unknown. The release-lug servo does the same
  job without disassembly, if the lug holds the pawl off its teeth while
  pushed.
- **Stopping short of die contact makes stiffness matter.** The handles and
  pins then set the crimp at a given force or position. That is repeatable only
  while the tool does not wear or loosen over ~3,200 crimps [shared-context];
  the empty-tool curve and the knee's position at a fixed force watch it.
- **Handle stiffness is unmeasured.** It sets how far the pusher overshoots the
  wall between samples, and so the force wall's margin.

## What it changes against a1

| | a1 (ratchet in) | a1b (pawl out) |
|---|---|---|
| Hold | First ratchet tooth, wherever it falls | Any force or position the controller picks |
| Back out after hold | Only by lifting the release lug | Always |
| Full closure guaranteed by | The pawl | The station MCU's force wall plus die contact; the keyhole catches what reaches the housing |
| Force curve | Sawtooth from the pawl | Smooth |
| A stall mid-stroke | Tool locked on the contact | A partial crimp that can be pulled out; the curve rejects it, the journal names it, the keyhole stops it |
| Crimp height | Dies, plus where the tension wheel releases | Dies, or a machine-set grip position short of die contact |

## The force wall lives on the station MCU

Near closure the die already crawls: at 2 mm/s at the grip and a gain of 15–40
it moves 0.05–0.13 mm/s [sl w3 §2]. The pusher does not. After the die faces
meet, the grip sees a stiffness of roughly 3–60 N/mm [estimate: handle and pin
compliance in series with the die loop through the gain squared], so:
- one HX711 sample at 80 SPS (12.5 ms) is 25 µm of grip, 3–21 N extra at the
  dies;
- a 30 ms USB round trip is 6–51 N;
- a 0.5 s stall on the Mac is 108–857 N [sl w3 §2].

So the ESP32 runs whole squeezes, checks every sample, and holds the wall. The
Mac commands a squeeze and reads its trace.

## Why the proof pull is not taken in the tool

Re-closing the dies lightly on the crimped barrels and pulling the wire does
not test the strands. A few newtons at the grip is 30–200 N at the dies through
the end-of-stroke gain, and die friction adds 4–100 N of grip (μ 0.15–0.5) to
a 20 N test [sl w3 §1]. To keep that under 2 N the held die force must stay
under 4–13 N, which is 0.1–0.9 N at the grip, inside the empty tool's own
repeatability of perhaps ±0.5–1 N [estimate]. A crimp with little grip of its
own would pass.

Holding the dies open at a position and pulling against the jaw's front face
does not help either: wherever the lance tip hangs in front of the anvil face,
it meets the face after 0.11–0.26 mm of travel, before the box's rear shoulder
does [sl w3 §1].

The pull goes to a backed plate on the box's rear walls with the lance
relieved ([a6](a6-foot-closed-jig-bench.md)'s pull jig, a2's pull slot).

## The press that finds its own crimp height

machine-that-sees-and-learns'
[v3](../../machine-that-sees-and-learns/ideas/v3-press-that-runs-experiments.md)
needs "a press with a settable, repeatable stop". a1b is that press, at the
price of an SN-2549 ($22.29 [prime: B01N4L8QMW]).
- **The sweep.** Stops short of die contact at 16 grip positions × 5 coupons.
- **Pulls to failure grip copper, not jacket.** At 100 N a 10–15 mm capstan
  puts 6–34 MPa of shear into silicone rated at 8–11 MPa [ribbon-as-pallet calc
  P §4]. So the coupon's far end is a soldered lug or bare copper wrapped on a
  pin [v3]. (a6's capstan at 20 N is fine: ~1.2 N/mm at the drum entry.)
- **Each proof pull is paired with a destructive one on the same setting,** so
  the proof load is known to lie under the failure load.
- **Grip position is a setting, not a length.** Each level's crimps are
  micrometered, or silhouetted in v5's booth with the box as its own roll
  gauge, to map grip position to crimp height. The map holds while the tool
  does not wear, which the knee's position at a fixed force watches.
- **The target.** change-the-question's
  [c2](../../change-the-question/ideas/c2-buy-the-crimp.md) JST lead
  (ASXHSXH22K305, a genuine 22 AWG crimp) gives the crimp height and
  insulation height the map is set to.

## The same stroke, stopped early, does two other jobs

**Pre-forming a contact for a flag** ([a6b](a6b-flags-by-hand-foot-crimp.md)).
A single-stroke tool touches the tall insulation wings (2.75–3.20 mm open)
before the short conductor wings (1.50–1.60 mm). On an edge model of the die,
the insulation wings are pushed inside the die width over 0.65–1.7 mm of stroke
before the conductor die touches anything [htq §3, estimate]. a1b stops an
empty contact inside that window at a taught grip position, instead of at a
ratchet click. The force rise on that stroke is the contact's wing height, so
mixed-maker contacts in a kit bag sort themselves before they reach a stick.

**Folding for change-the-question's c3.** c3's steel arch curls both barrels at
0.1–0.3 kN and stops 0.2–0.3 mm above crimp height. That is the SN-2549's own
stroke stopped short of die contact: 3–20 N at the grip through a gain of
15–30 [htq, K5]. No custom arch is needed, and the fold is in the profile the
contact was designed around.

## Rests on

- **[assumption]** The release lug holds the pawl off its teeth when pushed,
  rather than only releasing at a tooth.
- **[assumption]** The pusher's lead screw holds position unpowered at hold
  force. A Tr8×2 is self-locking at these loads.
- **[estimate]** Handle-and-pin stiffness 20–100 N/mm and a die loop of
  5–30 kN/mm, which set the overshoot figures.
- **[estimate]** The insulation-first window on the SN-2549 exists; on a
  pessimistic apex model it can vanish [htq §3]. One slow close on an empty
  contact under the ELP settles it.

---

Citation keys: **[sl w3 §n]** is machine-that-sees-and-learns'
[`w3_on_hand_tool_as_press.out.txt`](../../machine-that-sees-and-learns/calc/w3_on_hand_tool_as_press.out.txt);
**[htq §n]** is [`../calc/exchange_ctq_w3.out.txt`](../calc/exchange_ctq_w3.out.txt)
(K5 is a combination in
[`hand-tool-as-press--on--change-the-question-w3.md`](../../../exchange/hand-tool-as-press--on--change-the-question-w3.md));
**[prime: ASIN]** is a row of [`../../../sourcing/amazon-prime.md`](../../../sourcing/amazon-prime.md),
observed 2026-09-28.
