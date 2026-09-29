# a7 — If the contacts switch to genuine SXH strip: what changes, arrangement by arrangement

This is a supply decision seen through every arrangement in the study, not a
machine. The decision is Derek's (it is on several explorers' lists). The file
sets out what physically changes in each arrangement if the contacts come as
genuine JST SXH-001T-P0.6 on carrier strip, and does the same for the other
supplies on the table:
- **clone strip:** an LCSC clone reel;
- **loose:** the CQRobot kit contacts on hand, or genuine loose BXH-001T-P0.6;
- **pre-formed:** any of these with the insulation barrel pre-formed into a
  keyhole on the bench before any wire (change-the-question
  [c6](../../change-the-question/ideas/c6-pre-form-the-contact.md)).

Numbers: [`../calc/wave2.py`](../calc/wave2.py) §7, §10 [w2 §n];
[`../calc/terminal_supply.py`](../calc/terminal_supply.py) §1 [ts §1];
[`../calc/w3.py`](../calc/w3.py) §7 [w3 §7]; into-the-housing's
[`exchange_terminal_supply_w3`](../../into-the-housing/calc/exchange_terminal_supply_w3.out.txt)
§J [ith-w3 J]; machine-that-sees-and-learns'
[`on_terminal_supply`](../../machine-that-sees-and-learns/calc/on_terminal_supply.out.txt)
§2 [mtsl §2]; [xh-facts](../../../context/xh-facts.md) §1, §2, §6.

## Picture it

- **What arrives.**
  - A Digi-Key 100-piece cut strip, 455-1135-100-ND, $4.71, 3,100 in stock: two
    units.
  - Then a reel: 8,000 pieces, $0.0235 each at Digi-Key, 1,329,000 in stock; LCSC
    C140573 at $0.0100 per 1k. No Prime listing for XH strip was found
    [sourcing/amazon-prime.md].
  - One reel is 0.44 of the whole program if every contact is used, and 0.89 with
    every other one removed ([a2d](a2d-skip-pitch-crown.md)) [w2 §7; xh-facts §6].
  - The strip: every contact in the same pose, joined at the rear of its
    insulation barrel by a 0.7–1.15 mm tab to a 3 mm carrier, with a Ø1.5 mm pilot
    hole on each contact's centreline, every ~7.1 mm (pitch from the Würth analog;
    SXH unmeasured).
- **What comes with it.** A crimp-height target: JST's crimp specification for
  SXH-001T-P0.6 on 22 AWG exists, behind a licence form that emails it (CHM-1-151)
  [xh-facts §1]. Genuine factory crimps to measure: the ASXHSXH22K305 lead at $0.90
  (change-the-question c2).
- **What stays.** The kit's loose contacts become hand-repair stock and feed any
  loose route. The kit housings stay, or genuine XHP-n replace them: XHP-4 to
  XHP-7 are plentiful at Digi-Key, and XHP-9 is 3,408 in stock [xh-facts §6].
- **What the person does differently.** Mounts a strip or reel instead of shaking
  contacts from a bag. A new step, cutting the contact from its carrier, appears
  somewhere: in the machine, or with flush cutters for hand crimping.

## Nine things that change

1. **Pose is given.** Every contact arrives in the same pose, roll and pitch.
   Singulation and orientation disappear: hopper, tray, pocket plate, flap loading,
   hand-loaded posts.
2. **A carrier must be cut, and its stub is inspected.** JST faults both "no
   cut-off length" and "too much" [xh-facts §1]. Each arrangement cuts it in one of
   three places:
   - under the wire, by dropping the carrier: applicators, a2, a2d, f5's floating
     shear, f8;
   - before any wire exists: a6, f1's strip-over-flap, b2's shear, f4's servo
     shear, hand-tool-as-press a2's stubs;
   - by bending it off after the crimp: a2b, a2c's variants.
3. **The next contact stands beside the die.** An open contact sits 7.1 mm
   upstream, in the plane where the ribbon's other conductors want to lie and in
   the camera's line along the strip. No 4P or 5P fan pitch clears it [mtsl §2;
   w2 §1]. Every single-die strip station answers it one of three ways:
   - lift or fold the other conductors: borrowed-machines b1's fold-back,
     procedure-is-the-machine p1's slotted presser and p1c's single lift,
     ribbon-as-pallet a1's conductors held 5 mm up and a1c's fold after crimp,
     a2's lifter bar;
   - take the fresh contacts out of the plane: a2d (and, for a housing station,
     the same crown under f8 and into-the-housing i2's strip branch);
   - move the pick away from the die: a6, b2, f4.
4. **The wings may be narrower.** JST's catalog end view is 1.95 × 2.4 mm. Every
   clone drawing shows open insulation wings of 2.46–3.0 mm. If genuine wings sit
   inside the envelope (unmeasured), open contacts side by side change [w2 §10]:

   | Pitch | Genuine (1.95) | Clone (2.46–3.0) |
   |---:|---:|---:|
   | 2.5 mm | clear by 0.55 mm | −0.50 to +0.04 mm (collide) |
   | 3.4 mm | clear by 1.45 mm | clear by 0.40–0.94 mm |
   | 5.0 mm | clear by 3.05 mm | clear by 2.00–2.54 mm |

   - **What narrower wings make possible:** every cavity of a housing preloaded at
     once (into-the-housing i2b; this explorer's [x3](x3-stage-crimp-one-push.md)
     and [a4c](a4c-post-bed-one-push.md) staging), and more margin for
     change-the-question c1's 3.4 mm half-rows.
   - **What they do not make possible:** crimping every preloaded contact in one
     pass. The 3.1 mm narrow conductor step clears an open neighbour's conductor
     barrel (clone 1.68–1.90 mm) by only 0.00–0.11 mm [ith-w3 J], so the odd/even
     order stays unless genuine conductor barrels are narrower too.
   - **What they break:** the two orienters that use the wings as a head, a3's
     hanging rail and v4b's rejection of barrels-down contacts.
   - **Pre-forming** (c6) makes any contact ~2.0–2.1 mm wide before a wire,
     about JST's envelope, with the same gains and the same break.
5. **The die must fit the contact.**
   - **OTP "XH2.54" applicators and knife sets** are sold into Chinese harness
     shops and are most likely cut for clone reels [assumption]. A genuine contact
     in a clone-cut insulation crimper may close loosely if its wings are shorter.
     JST's own applicator, APLMK SXH001-06, is $3,440 and out of stock [xh-facts §2].
   - **WC-110** is JST's hand tool for this contact and takes it loose [xh-facts
     §2]: strip contacts are cut from the carrier first. **YRS-110** ($1,566) is
     JST's hand tool for the contact on strip. **The SN-2549's XH nest** fits
     whichever contact iCrimp cut it for, which is unknown; it crimps the kit
     contacts today.
6. **A target exists.** With genuine contacts, machine-that-sees-and-learns v3's
   campaign becomes a check against a known crimp height, not a search. For kit
   contacts the only published number is a clone specification (KONNRA:
   0.73 ± 0.05 mm at 22 AWG) [ribbon-as-pallet].
7. **The first strip settles the geometry questions.** One Digi-Key strip under
   the caliper or the Revopoint answers about a dozen explorers' questions: pitch,
   pilot hole, tab, contact length (6.1 or 6.5 mm, which JST's editions disagree
   on), genuine open-wing width, box-to-barrel length, lance position.
8. **The housing pairing.** Genuine contacts in kit (probably clone, PA 66)
   housings need one test: does the lance catch? Genuine in genuine satisfies JST's
   handling precaution to check continuity only against the applicable header
   [xh-facts §3].
9. **Cost.** $0.67–2.50 per unit in contacts [ts §1], against kit contacts already
   paid for.

## Each explorer's arrangements

Key: **strip** = needs strip form; **loose** = needs loose contacts; **either** =
works with both; **—** = does not handle contacts. The first tables were read
from each explorer's summary before their revisions; each explorer's own final
account governs its ideas. The last table adds arrangements that appeared later,
read from each file's opening sections.

### borrowed-machines

| Arrangement | Form | With genuine SXH strip |
|---|---|---|
| b1 press + OTP applicator + shuttle | strip | Runs as drawn. The applicator's die was cut for one contact: buy the vendor's clone reel, or test genuine SXH in it. Fold-back parking unchanged |
| b1b applicator in a slow crank press | strip | As b1 |
| b2 SN-2549 in a frame, strip sprocket, tweezer, shear | strip (or loose by tweezer) | Runs as drawn. The WC-110 alternative needs b2's shear first, which b2 has |
| b3 gantry head picks from a strip feeder | strip | Runs as drawn; the head's harvested OTP blades face b1's die-match question |
| b4 laser slit and score, b5 arm | — | None |

### change-the-question

| Arrangement | Form | With genuine SXH strip |
|---|---|---|
| c1 half-rows in 3.4 mm pallets | loose | Strip pitch (~7.1) is not 3.4; contacts are cut off and loaded loose. Narrower wings raise the 3.4 mm margin from 0.40–0.94 to 1.45 mm |
| c1b tack first | loose | As c1 |
| c2 buy the crimp | — (bought pre-crimped) | Genuine leads already; unchanged |
| c3 fold and solder | either | None |
| c4 parts that mate the wafer | — | This file is its companion on contact choice |
| c5 ends as stock | either | Inherits whichever termination it hosts |

### force-and-form

| Arrangement | Form | With genuine SXH strip |
|---|---|---|
| f1 SN-2549 in a cradle, keyed flap | either | The flap takes a contact cut from strip by its shear, or a loose one |
| f1b WC-110 in the cradle | loose (cut from strip) | The one hand tool whose die is made for genuine SXH |
| f2, f2b applicator in a crank or arbor press | strip | As b1: die match |
| f3 knee micro-press, strip on a pilot pin | strip | Runs as drawn once pitch and pilot hole are measured; change 3 applies |
| f3b curl, then coin | strip | Strip carries parts between stations |
| f4 crimp head goes to the wire, picks from strip | strip | Runs as drawn |
| f5 die cassette in the 12-ton press | strip | Station pitch = strip pitch unless contacts are cut into pockets; 5P fans 30–38 mm |

### hand-tool-as-press

| Arrangement | Form | With genuine SXH strip |
|---|---|---|
| a1 squeezer cradle | either | Stubs with a pin locate axially; loose contacts use the neck blade |
| a1b pawl out | either | None |
| a2 ribbon to fixed tool, carrier stubs | strip | Runs as drawn |
| a2b gravity, revolver of loose contacts | loose | Genuine contacts (if no head) may tumble in the chute differently; unmeasured |
| a2c one baseplate, stubs | strip | Runs as drawn |
| a3 tool travels, post column | either | Whole strip pushed onto the post column and tabs gang-cut |
| a4 SN jaws in a die set | either | None, beyond die match |
| a5 PA-09 two squeezes | either | PA-09 is listed by its maker for SXH and BXH [xh-facts §2] |

### into-the-housing

| Arrangement | Form | With genuine SXH strip |
|---|---|---|
| i1 lift to the head | either (the head's feed) | The head's feed can be a strip |
| i1b narrow tooling in the row | loose (from below) [assumption] | Contacts cut from strip first |
| i2 crimp in the cavity | either | The transition-length question is measured on the genuine part; its strip branch can take a2d's crown |
| i2b preload the whole housing | loose | Narrower wings let every cavity be preloaded at once, but not crimped in one pass (change 4) |
| i2c cut-down housing locator | either | None |
| i2d locator the lance never touches | loose, or strip contacts cut first | None |
| i3, i3b shuttles and gang push | either (the head's feed) | None |
| i4 gantry hand, pocket tray | loose tray, or force-and-form f3's strip | Contacts cut from strip, or strip picked directly |
| i5 person inserts on a sensing nest | — | Genuine contacts on a genuine header: JST's precaution met |
| i6, i6b sort then push; post bed | — (crimped contacts only) | None |
| k6 one gantry crimps in the fan, then sorts | strip (force-and-form f4's dispenser) | Runs as drawn |

### machine-that-sees-and-learns

| Arrangement | Form | With genuine SXH strip |
|---|---|---|
| v1, v1b watched nest | either | With strip it becomes a2 or a2d with v1's gate |
| v2 arm | — | None |
| v3 press that runs experiments | either | A known target to check against; its genuine-versus-kit test compares two supplies |
| v4 tap-look-pick | loose | Pose odds for genuine contacts are different and unmeasured |
| v4b pocket plate | loose | Genuine wings may let barrels-down contacts into a 2.05 mm channel; the camera must reject them |
| v5 inspection booth | — | Records supply and lot per crimp |
| v6 patient cell | either | Inherits its place-and-crimp station |

### procedure-is-the-machine

| Arrangement | Form | With genuine SXH strip |
|---|---|---|
| p1, p1b benches with a pre-fed contact on a 1.6 mm anvil blade | strip | Runs as drawn |
| p2 tool turret, reel of 100–200 on the head | strip | Runs as drawn |
| p3, p3b terminate at the spool | strip (via p1's tools) | Runs as drawn |
| p4 person presents, machine takes | strip (pre-fed) | Runs as drawn |
| p5 camshaft | strip (pawl feed) | Runs as drawn |

### ribbon-as-pallet

| Arrangement | Form | With genuine SXH strip |
|---|---|---|
| a1, a1b pallet tour with a side-feed applicator | strip | As b1: die match |
| a2 two pallets meet: strip segment on pins | strip | Runs as drawn once pitch is measured |
| a2b gang stroke in the 12-ton press | strip | As a2 |
| a2c loose-contact cassette | loose | Contacts cut from strip, or keep kit contacts here |
| a2d by hand | strip | Runs as drawn |
| a3–a6 | — or via a1 | None |

### terminal-supply (this explorer)

| Arrangement | Form | With genuine SXH strip |
|---|---|---|
| a1 applicator on a slow ram | strip | Die match |
| a2, a2b, a2c, a2d | strip | Run as drawn |
| a3, a3b hanging rail | loose, clone-shaped | Genuine wings inside 2.4 mm fall through [w2 §10]; kit contacts only |
| a4, a4b, a4c, a5 | either | Strip contacts pushed onto posts, then cut; loose natural. Narrower wings let a4c and x3 load every cavity at once |
| a6 post as gripper, x1 | either | Pick from the strip, tab cut before the wire |
| x2 crown, then sort and push | strip (a loose branch uses a6 at the die) | Runs as drawn |
| x3 stage every other cavity, one push | either | As a5 |

### Arrangements added later, across explorers

Read from each file's opening sections; each explorer's own account governs.

| Arrangement | Form |
|---|---|
| borrowed-machines b1c one-shaft applicator press; b8 spool-fed line | strip (applicator) |
| borrowed-machines b2b pedal-less hand station | strip (SN-2549 with strip feed and shear) |
| borrowed-machines b4b, b6, b7 (laser heads, pierce-and-pull split, bought stripper) | — |
| change-the-question c1c half-rows crimped in the row | loose, or pre-formed (c6) |
| change-the-question c6, c6b pre-formed contacts | pre-formed, from strip, a3's rail, a6's post, v4b's plate, or loose kit contacts by hand (c6b) |
| force-and-form f2c applicator station makes T4 ends | strip |
| force-and-form f5b half-row cassette | loose, into steel pockets |
| force-and-form f6 two blades, two drives | strip (f3's press) |
| force-and-form f7 where the steel comes from | — (die sources) |
| force-and-form f8 narrow press at the housing mouth | strip, dropped by a crown (a2d's elastic skip-2 crown applies) |
| force-and-form f9 tack station feeds crimp station | loose |
| hand-tool-as-press a2d batch then gang push | strip (stubs) |
| hand-tool-as-press a4b C-frame one-nest head | either (post column or stubs) |
| hand-tool-as-press a6 foot-closed jig bench | either (kit contacts or SXH stubs) |
| machine-that-sees-and-learns v7 the run | — (control) |
| machine-that-sees-and-learns v8 tack, look, crimp | loose |
| procedure-is-the-machine p1c, p4b, p5b | strip |
| procedure-is-the-machine p6 spool-end bench that grows | either (a hand-tool crimp stage) |
| procedure-is-the-machine p7 strip before split | — |
| ribbon-as-pallet a1c, a2e | strip (applicator) |
| ribbon-as-pallet a7, a7b, a8, a8b (split and strip stations) | — |

**Count** [estimate, from the tables above]. Of roughly 85 arrangements that
handle contacts, about half (~43) need strip form and cannot use the kit contacts
at all; about a fifth (~17) need loose contacts; about a third (~27) take either.
The loose ones can use genuine contacts cut from strip, at the cost of a cut.
Pre-forming (c6) is a supply of its own that any source can feed.

## Four supplies side by side

| | Genuine SXH strip | Clone strip (LCSC CJT A2501-TP, HDGC2501-T) | Loose (kit contacts, or genuine BXH) | Pre-formed (c6, from any of these) |
|---|---|---|---|---|
| Form | carrier strip | carrier strip | loose | loose, keyhole insulation barrel, stackable in loom order |
| Price, observed 2026-09-28 | $0.0235 (DK reel) – $0.0471 (DK 100) [xh-facts §6] | $0.0073–0.0079 (LCSC reel) [xh-facts §6] | kit: on hand; BXH $0.0423 @ 100 (DK) | the source's price plus a pre-forming step |
| Open width | JST envelope 1.95 (unmeasured) | wings 2.46–3.0 on drawings | kit: unmeasured, probably clone-like; BXH as genuine | ~2.0–2.1 [change-the-question c6] |
| Crimp-height target | JST's, via licence form | clone spec (KONNRA 0.73 ± 0.05) | kit: none; BXH as genuine | the source's |
| Die match to an OTP applicator or knife set | test it | likely | kit: likely; BXH: test it | the insulation crimper meets a pre-closed barrel: test it |
| Arrangements it serves | strip ones; loose ones after a cut | strip ones; loose ones after a cut | loose and either ones | loose ones, and ones that need narrow neighbours (c1c) |
| What it settles | geometry, target | geometry | nothing new | neighbour width |

A clue to the kit contacts' origin: a short tab stub at the rear of a kit contact's
insulation barrel would show it was cut from a reel, most likely a clone reel. The
same reel, bought whole, would be the kit contact on strip.

## Steps covered, and what it hands back

It covers no step; it maps the supply decision onto every step it reaches (pose,
sever, neighbour geometry, die match, crimp-height target, insertion pairing).
It hands back the decision itself, buying one strip, and the measurements that
settle genuine wing width and die match.

## Contribution

A single map of how the contact's arrival form reaches into every arrangement: its
pose, its carrier and stub, what stands beside the die, wing width, die match, the
crimp-height target, the geometry one strip settles, the housing pairing and cost.
It lets the supply question be decided knowing which arrangements it opens and
closes.

## Major unresolved problems

- **Genuine open-wing width,** and genuine conductor-barrel width. One caliper
  reading on one contact.
- **Which contact the OTP applicators and knife sets are cut for.** The vendor can
  say; one crimp of each supply in the same die shows it.
- **Whether kit contacts have tab stubs.**
- **Lance catch of genuine contacts in kit housings.**

## What each conclusion rests on

- **Derek:** the kit contacts are what is on hand [repo bom.md].
- **Facts [mfr, source]:** part names, tools, stock and prices [xh-facts §1, §2,
  §6]; clone drawings; KONNRA specification (via ribbon-as-pallet).
- **Calculations [calc]:** reel coverage and cost [w2 §7; ts §1]; open-neighbour
  gaps [w2 §10]; preloaded neighbours against the narrow step [ith-w3 J];
  fresh-contact clearance [mtsl §2; w2 §1].
- **Estimates:** the classification counts.
- **Assumptions:** OTP tooling cut for clone contacts; kit contacts clone-shaped;
  classifications read from summaries and opening sections, not re-derived.
