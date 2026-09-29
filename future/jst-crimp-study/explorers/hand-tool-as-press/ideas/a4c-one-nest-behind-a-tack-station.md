# A4c — One SN nest as the heavy station behind a tack station: the machine places and pins, the die set crimps

## Picture it

**Where things start.**
- **The stage.** A bed-slinger printer with its hot end removed
  (machine-that-sees-and-learns'
  [v1b](../../machine-that-sees-and-learns/ideas/v1b-printer-as-stage.md)):
  the Creality Ender-3 V3 SE, $219.00, 2,112 ratings [prime: B0F8J78BN1].
- **The pallet on the stage** (v1's fan block): a ribbon end flush-cut, split
  25–35 mm and stripped to the length set from the contact lot; fanned to
  5 mm pitch; each conductor in its own hinged key; the waiting keys hold
  their conductors' axes 5 mm above the working contact's floor.
- **The far end** in a push-in block (Wago 221-415, $28.00 for 25 [prime:
  B0107SYYGU]) wired to the station ESP32. The XH end is made first.
- **Contacts:** loose kit contacts on machine-that-sees-and-learns'
  [v4b](../../machine-that-sees-and-learns/ideas/v4b-pocket-plate.md) pocket
  plate, picked by v4's sprung nozzle; or genuine SXH strip on pilot pins.
- **Station T, the tack** (machine-that-sees-and-learns'
  [v8](../../machine-that-sees-and-learns/ideas/v8-tack-look-crimp.md)):
  - a printed frame with a box slot, a lance relief and a steel insert under
    the insulation barrel (a 3 mm HSS square blank, $9.99 for five [prime:
    B08ZSMB557]);
  - a steel former with an insulation profile, cut from the insulation section
    of a spare SN-2549 jaw piece, so the tack is the SN's own stroke paused
    (below); driven by a 35 kg·cm servo on a lever (ZOSKAY DS3235, $27.99
    [prime: B07S9XZYN2]) to a loose screw stop;
  - a 20 kg bar cell under the nest insert, not in the former's link, so it
    reads only the forming force, 33–132 N [sl w2 §5];
  - a top camera straight down (16 MP IMX298 M12 board, $69.99 [prime:
    B0C54VCKZV], with a 12 mm lens, $9.99 [prime: B07CZ49BMK]);
  - a second camera across at wing height under the lifted neighbours, and a
    16-LED ring lit one LED at a time ($18.99 for five [prime: B0B2D5QXG5]).
- **Station C, 20–40 mm along the bed,** a one-nest version of
  [a4](a4-dies-in-a-die-set.md):
  - an SN-2549 jaw set with each die piece cut to one nest, 6–7 mm wide;
  - the upper piece in a laminated holder that stays no wider than ~7.4 mm for
    the first ~5.9 mm above the crimping edge and widens above that: a
    T-section, whose neck carries 3.5–4.5 kN at 50–64 MPa [sl w3 §7];
  - an eccentric of e = 2.0–2.5 mm, die contact set 0.17–0.28 mm above BDC,
    a disc-spring stack preloaded to ~3.5 kN under the lower holder, a 500 kg
    button cell ($74.99, thin [prime: B0GZZRQC6Y]), an AS5600 on the shaft,
    and a 0.001 mm indicator across the holders (DITR-0105, $52.99 [prime:
    B07888LX1R]);
  - in front of the lower die, a **seat**: a floor ledge for the box's front
    millimetre (ahead of the lance) and a retractable front stop, with no side
    walls, so the box's silhouette stays visible;
  - beside C, v1's silhouette window (a hardened blade under the conductor
    barrel, a backlight, a gauge pin) and a backed pull plate.
- **Controllers:** machine-that-sees-and-learns'
  [v7](../../machine-that-sees-and-learns/ideas/v7-the-run.md) Stack A. The
  station ESP32 runs the eccentric's stepper, the servos, the load cells and
  the far-end inputs. A runner on the Mac owns the recipe, the journal and the
  log.

**What moves, one conductor.**
1. **T, contact in.** The nozzle drops a contact in T's box slot, or the strip
   indexes. *Look:* box on its stop, lance standing, wings upright. The top
   camera also measures this contact's box-front to conductor-barrel-rear
   distance.
2. **T, lay-in.** The stage brings key *k* over T. *Hover look:* the tip and
   the torn insulation edge; X and Y are corrected once or twice. The plunger
   presses key *k* to its stop. *Side look:* bundle in the U, edge in the
   window, nothing above the wing tips.
3. **T, tack.** The former comes down at ~1 mm/s to its loose stop, and the
   cell under the nest logs the forming curve.
4. **T, the look that matters.** Straight down into the open conductor barrel
   under 4–8 lighting states and two focus depths: every strand between the
   wing tips, no silver outside, the brush length, the edge in the window.
   - Pass: go on.
   - Fail: the conductor backs out through the key's grip and the contact is
     discarded. It costs a contact, not a ribbon end.
5. **Carry.** Key *k* rises with the tacked contact. The box leaves T's slot
   straight up; the lance is in a relief and touches nothing. The stage moves
   the pallet to C.
6. **C, carry in high, set down.** Key *k* holds the contact's floor 1.0–1.7 mm
   above C's anvil. The stage moves +Y until the box is over the seat, then
   lowers the pallet by that 1.0–1.7 mm. The box lands on the ledge and the
   barrels on the anvil. During the carry the neighbours ride beside the
   punch's narrow section; the set-down returns them to 3.05–6.35 mm above the
   working floor [sl w3 §7]. The stage's two-level move is the lift that keeps
   the lance off the anvil face; no springs are needed.
7. **C, seat look.** The side camera runs under every neighbour at Z 0–2.85 mm
   [sl w3 §7]. It sees the conductor barrel's rear edge against the die's rear
   face (the bellmouth offset), the box flat on the ledge, and the tack where T
   left it. If the barrel's rear edge is off, the stage nudges Y, since the box
   sits on a ledge with no walls holding it.
8. **C, the stroke.** The MCU turns the eccentric fast to ~30° before BDC, then
   slowly over the last ~20°, checking the button-cell trace against the
   envelope every sample. It stops and reverses on force rising early (two
   contacts, insulation under the conductor barrel, a contact seated high).
   The dies bottom and the stack takes the overtravel. The eccentric backs off
   to a 10 N re-touch and the indicator is read: crimp height #1.
9. **C, out.** The ram rises 4–5 mm, and the stage lifts the pallet 1.0–1.7 mm
   before drawing back −Y.
10. **After-look.** The stage sets the crimp on the blade beside C.
    Machine-that-sees-and-learns' side silhouette gives crimp height #2,
    corrected for roll by the box's own silhouette (32–34 µm per degree
    [sl w2 §1]), plus the bellmouth, brush, insulation height and bend.
11. **Proof pull,** ~20 N, on the backed plate: the Y belt pulls through key
    *k*'s grip while the camera watches the edge in the window.
    - Strip contacts: the reaction can be on the tab, if a stub rides through
      C.
    - Loose contacts: on the plate at the box's rear walls, where the neck or
      a stepped plate allows ([a6](a6-foot-closed-jig-bench.md),
      [calc w3 §3]).
12. Key *k* returns to its waiting height; the next conductor. J2's cavity-3
    conductor and J7's trimmed one are skipped by the recipe.

**What locates what.**

| At | Contact located by | Conductor located by | Reference for "fixed" |
|---|---|---|---|
| T | Box slot and stop | Key groove, then the picture (tip and edge) | T's frame, seen with fiducials |
| T to C | The tack: axial position and roll against the conductor | The key | The pallet |
| C | Ledge (height, roll); stage Y set from the seat look (axial, ±0.03 mm at 0.02 mm/px [calc §7]); the closing dies (lateral) | Carried by the contact | C's lower die holder |
| Crimp height | Eccentric BDC and die faces meeting on the stack | — | Die geometry; read by re-touch and silhouette |

The front stop is a backstop for the set-down, not the reference. The picture
sets the contact against the die.

**What drives the crimp and carries its force.**
- **Drive.** A NEMA 23 through a 10:1 planetary (STEPPERONLINE, $48, 10 N·m
  permissible [prime: B0BPGMZ5LM]) turns the eccentric. The bench's NEMA 23 is
  in the weld rotator [repo], so this is a second motor or a borrowed one.
- **Load path.** Ram → punch → contact → anvil → button cell → disc stack →
  base → side plates → shaft bushings.
- **What carries none of it:** the stage, the pallet, the keys and the
  conductor.
- **Torque.** ~1.6–2.0 N·m before friction, ~2.0–3.0 N·m with it
  [calc w3 §1]. The 10:1 planetary carries it with margin; a 3:1 belt is at
  the edge.

**How it knows the crimp worked.**
- T's forming curve and top-down look, before anything irreversible.
- C's seat look.
- The die-force trace, measured at the die, not through a handle.
- **Two crimp heights from independent routes,** re-touch and silhouette. Each
  checks the other: a die piece loosening in its holder shows as the re-touch
  drifting; a knocked camera shows as the silhouette drifting. Machine-that-sees-and-learns'
  [v3](../../machine-that-sees-and-learns/ideas/v3-press-that-runs-experiments.md)
  calibration is built into production.
- Continuity and identity through the far end.
- The proof pull, where the contact form allows one.

**What the person does.**
- Loads 14 ribbon ends into pallets (10–30 min a unit [digest]) and pours ~60
  contacts onto the pocket plate.
- Answers 1–2 asks a unit in steady state [sl w2 §7].
- Inserts into housings, or hands the pallet to an insertion station.
- Once: has the die-set steel laser-cut, cuts a jaw set to one nest (abrasive,
  wet, slow), cuts T's former from a second jaw's insulation section, and
  seats the dies by closing them on each other.

**Time** [estimate]: T side 29–81 s [sl w2 §5]; C side ~37–63 s; 66–144 s a
conductor; ~1–2 h unattended a unit.

Sketch: [`../sketches/a4c-t-then-c.svg`](../sketches/a4c-t-then-c.svg)
(schematic); machine-that-sees-and-learns' end view at C from cited dimensions
is [`w3-t-then-c.svg`](../../machine-that-sees-and-learns/sketches/w3-t-then-c.svg).

## Steps it covers and what it hands back

**Covers:** supplying contacts (nozzle or strip), placing the contact on the
conductor, holding the two together (the tack), the crimp with die force and
two crimp heights, identity, and the proof pull where the contact allows.

**Hands back:** cut, split and strip; loading pallets and the pocket plate;
answering asks; housing insertion; the label; the one-time steelwork.

## How it relates

- Branch of [a4](a4-dies-in-a-die-set.md): a4's die set cut to one nest and
  given a T-section holder.
- A combination proposed as W1 in machine-that-sees-and-learns'
  [exchange](../../../exchange/machine-that-sees-and-learns--on--hand-tool-as-press-w3.md):
  - [v8](../../machine-that-sees-and-learns/ideas/v8-tack-look-crimp.md)'s
    station T and its straight-down look;
  - [v1](../../machine-that-sees-and-learns/ideas/v1-watched-nest.md)'s fan
    block, keys, silhouette window and pull plate;
  - [v1b](../../machine-that-sees-and-learns/ideas/v1b-printer-as-stage.md)'s
    printer stage;
  - [v4b](../../machine-that-sees-and-learns/ideas/v4b-pocket-plate.md)'s
    pocket plate;
  - [v7](../../machine-that-sees-and-learns/ideas/v7-the-run.md)'s controllers
    and journal.
- Its motorless-crimp sibling, with T kept and the heavy crimp done by foot in
  the SN-2549: [a6c](a6c-flags-by-machine-foot-crimp.md).
- Its motorless sibling with no T at all:
  [a6b](a6b-flags-by-hand-foot-crimp.md).

## Why the pairing does something neither does alone

- **a4 alone** has no way to place the contact or the conductor except a1's
  locator with a person, or a2's carriage, which pays the side-entry
  stand-out (8.7–14.7 mm with crimped neighbours [calc w3 §2]).
- **v1 alone, laying in under a4's short stroke,** has no room. An eccentric of
  2.0–2.5 mm opens the conductor punch only to 4.7–5.9 mm above the floor,
  and a waiting conductor's top is at 5.85 mm before up to 0.55 mm of spool
  curl: −1.1 to +0.05 mm of clearance [calc w3 §4; sl w3 §7]. An oblique
  camera clears a 6 mm punch only from 35–40° off vertical.
- **v8 alone** has no concrete C that fits between lifted neighbours. The
  SN-2549 as sold does not: its jaw spans the row (the side-entry jaw law).
- **Together:** the lay-in and the strictest look happen at T, where nothing
  stands over the barrel. The tacked contact rides to C on its own conductor.
  At C the die only has to pass a tacked contact carried level, which an
  eccentric of 2.0–2.5 mm does with 0.5–1.7 mm to spare [calc w3 §4]. The
  one-nest punch fits between neighbours that the keys already hold 5 mm up:
  7.45 mm is free between crimped neighbours' boxes with 0.3 mm clearance.

## The tack is the SN's own stroke, paused

A single-stroke tool touches the tall insulation wings (2.75–3.20 mm open)
before the short conductor wings (1.50–1.60 mm). On an edge model of the die,
the insulation wings are pushed inside the die width over 0.65–1.7 mm of
stroke before the conductor die touches anything [htq §3, estimate]; v8 reaches
the same order from the other side [sl w2 §5].

So if T's former is the insulation section of the same SN jaw that C crimps
with, the tack is the state C's own stroke passes through, and the stroke at C
continues it. That narrows v8's open question ("does a tacked barrel re-formed
by the SN insulation die end like a one-pass crimp?") to re-registration: at C
the tacked barrel meets the punch's arches in the shape those arches left it,
if it sits where T put it. The seat look checks that. A laser-cut former of
another profile leaves the full question open.

## The other order: C tacks for itself

The die set could make the tack itself: lay in at C, turn the eccentric to a
part stroke inside the insulation window, look, then finish. That removes T and
the T-to-C handover, which rides on a 0.2–1.5 N tack. It needs room for the
lay-in under the open punch: an eccentric of 3.0–3.5 mm gives +0.3 to +2.1 mm
over a waiting conductor with its curl, at ~1.10–1.18× the torque of
e = 2.5 mm [calc w3 §4]. What it gives up is the straight-down look: under a
punch open at ~7.7 mm the look is oblique again. Set beside a4c, not
developed.

## Major unresolved problems

- **Cutting hardened SN pieces to one nest** without cracking them, twice (C's
  die pair and T's former).
- **The tack's grip window on silicone:** 0.2–1.5 N wanted, 0.4–9 N estimated
  across squeezes [v8]. The carry from T to C adds a load case: a snag during
  the +Y carry under the punch is resisted only by the tack. The seat look
  exists to catch a contact that moved.
- **Tacked, then re-formed, against one pass,** for the insulation crimp.
  Sectioning and pull tests settle it; a former cut from the SN's own
  insulation section narrows it (above).
- **The per-crimp pull on loose contacts** needs a neck gap the plate fits in,
  or a stepped plate that bears outside the crimped barrel ([calc w3 §3]).
  Strip stubs can keep their tab through C if the stub, which lies across X in
  the floor plane at the contact's rear, clears the anvil holder. That is
  undrawn.
- **The a4 unknowns:** whether SN die faces meet face to face, and the jaw seat
  geometry to copy.
- **The keys set copper at their roots.** A key root bends the conductor at a
  radius of 24–60 mm [ribbon-as-pallet calc P §9], below the 67–78 mm yield
  radius, so each conductor leaving the fan block carries a kink of roughly
  5–12° 20–30 mm behind its contact [sl w3 §4, estimate]. A gang insertion from
  the pallet needs a front plate and late rear clamp to square it; one at a
  time insertion tolerates it.
- **Pallet loading** is the person's time, as everywhere [digest].

## Parts

Beyond a4's die set and machine-that-sees-and-learns' T, pallet and stage
(each with its own sourcing): a second spare SN jaw set for T's former; the
laminated T-section punch holder; the seat ledge and retractable stop (a
micro servo, MG90S, $13.88 for four [prime: B0CP98TZJ2]).

## Rests on

- **[estimate]** Neighbour height (5 mm) and pitch (5 mm) from v1; clone
  dimensions for the contact [xh-facts §1]; a tacked barrel 2.3–2.5 mm tall
  [v8 estimate].
- **[estimate]** A frame loop of 15–30 kN/mm and a stack rate of ~3 kN/mm
  [calc w3 §1].
- **[estimate]** The insulation-first window on the SN die (edge model); on the
  apex model it can vanish [htq §3].
- **[assumption]** The T-section holder's neck (7 × 10 mm) is stiff enough to
  keep the punch on the anvil's axis.

---

Citation keys: **[calc §n]** is [`../calc/hand_tool_press.out.txt`](../calc/hand_tool_press.out.txt);
**[calc w3 §n]** is [`../calc/wave3.out.txt`](../calc/wave3.out.txt);
**[htq §n]** is [`../calc/exchange_ctq_w3.out.txt`](../calc/exchange_ctq_w3.out.txt);
**[sl w2 §n]** and **[sl w3 §n]** are machine-that-sees-and-learns'
[`wave2.out.txt`](../../machine-that-sees-and-learns/calc/wave2.out.txt) and
[`w3_on_hand_tool_as_press.out.txt`](../../machine-that-sees-and-learns/calc/w3_on_hand_tool_as_press.out.txt);
**[prime: ASIN]** is a row of [`../../../sourcing/amazon-prime.md`](../../../sourcing/amazon-prime.md),
observed 2026-09-28.
