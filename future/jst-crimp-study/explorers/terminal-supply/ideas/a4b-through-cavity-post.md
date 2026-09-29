# a4b — The post goes through the housing first: crimp on its tip, slide the contact home

Branch of [`a4-post-held-contacts.md`](a4-post-held-contacts.md). **What it
changes:** the post that holds the contact is long. Before the contact goes on,
the post reaches in through the housing's front post opening, runs through
cavity k and stands ~9 mm out of the rear face. The contact is mated onto the
post's tip, crimped there, then slid along the post into its cavity. Nothing has
to find the cavity.

Sketch: [`../sketches/a4b-through-cavity-post.svg`](../sketches/a4b-through-cavity-post.svg) (schematic).
Numbers: [`../calc/terminal_supply.py`](../calc/terminal_supply.py) §7–8 [ts §n];
[`../calc/w3.py`](../calc/w3.py) §1–3, §9 [w3 §n]; into-the-housing's
[`exchange_terminal_supply_w3`](../../into-the-housing/calc/exchange_terminal_supply_w3.out.txt)
calc [ith-w3 X].

**Branches and related.**
- [a4c](a4c-post-bed-one-push.md): a post through every cavity at once, every
  contact crimped on its own post, one housing move seats them all. It stores no
  feed, which is a4b's main open problem.
- into-the-housing's [i6b](../../into-the-housing/ideas/i6b-post-bed-through-the-housing.md)
  grew from a4b: a bed of posts that crimped contacts are threaded onto.
- The lit cavity is machine-that-sees-and-learns'
  [v6](../../machine-that-sees-and-learns/ideas/v6-patient-cell.md) idea. After
  any gang push (into-the-housing i3, i6, [x3](x3-stage-crimp-one-push.md)) the
  same light under the mating face is a per-cavity seat check: a seated box
  darkens its post opening.

## Picture it

1. **The housing and the web ride one stage.** An XHP housing sits in a printed
   nest on a small X stage, its mating face toward a fixed post slide. The nest
   is keyed by the lock ramp and the Circuit-1 notch [xh-facts §3]. The web clamp
   holding the split, stripped ribbon end is on the same stage: once the first
   contact latches, the ribbon is tied to the housing, and a housing that stepped
   2.5 mm under a fixed web would drag the seated conductors sideways by up to
   (n−1) × 2.5 mm, 20 mm on J1 [w3 §3]. The post slide, the dies and the camera
   are the fixed station.
2. **The lit cavity.** A light under the nest shines into the mating face. Seen
   from the rear, each empty cavity is a bright square: a straight line of sight
   along the cavity's axis. The camera finds cavity k by it and checks that the
   aperture passes a 0.64 mm post.
3. **The post.** A 0.64 mm square steel pin, ~25–30 mm long, slides in through
   cavity k's front post opening and stands ~9 mm out of the rear face.
4. **The contact goes on.** A bare contact is put onto the post's tip, box first,
   1.5–1.8 mm deep:
   - **Shuttle nest.** A nozzle drops a barrels-up contact into a small open
     pocket with a lance groove along its floor and a rear wall. The pocket slides
     along the post's axis until the tip enters the box, and the wall pushes the
     box on. The groove keeps the contact flat so its entry is where the floor
     says [w3 §2].
   - **Rear face up.** With the housing lying rear face up, the post points up; a
     contact dropped box-down into a funnel over the tip lands on it, and a light
     finger from above presses it on.
   - **From [a3](a3-hanging-rail.md)'s rail,** or Derek's fingers when the
     machine asks.
5. **Crimp.** The ribbon carriage lays conductor k into the open barrels. An
   anvil rises from below to the contact's floor, and the punch comes down
   (press, hard stop, as in [a2](a2-strip-indexer.md)). The post, cantilevered
   ~17 mm, is soft (1.2–1.7 N/mm, steel), so the die centres the barrels and the
   post only carries the contact [ts §7; w3 §8].
6. **Proof pull, before the push.** A fork in the neck between the box and the
   conductor barrel bears on the box's rear shoulder while the carriage pulls
   ~20 N. Once the contact is seated, a pull tests the lance, not the crimp, so
   this is the place for it.
7. **Push home.** A fork of two steel-shim tines either side of the wire pushes
   the contact along the post into cavity k by the insulation barrel's rear edge,
   13.95–14.45 mm from the box front 7.2–7.5 mm outside the rear face to
   6.75–6.95 mm inside it [w3 §3; ith-w3 A]. The post withdraws so its tip stays
   about 1.5 mm inside the box and never reaches the crimped strands:
   - **driven:** a second stepper withdraws the post in step with the fork;
   - **dragged:** the post slides freely in a low-friction guide and the box's
     grip (0.2–2 N) carries it forward against guide friction of ~0.01–0.05 N
     [estimate]; a flag on the post's rear end confirms it travelled.

   A load cell on the fork traces force against distance: a rise as the lance
   meets its ramp, a drop at the click, a wall at the seat.
8. **Seat checks.** A 5 N pull on the wire confirms the lance caught (force
   arrives before distance), well under the 14.7–19.6 N retention [w3 §9]; the
   post withdraws out the front, unmating at 0.2–2 N, and if the contact comes
   with it the lance did not catch; and after the post leaves, a seated box sits
   behind the post opening, so the square stays dark.
9. **Next cavity, in layer order.** For the eight one-layer looms the stage steps
   2.5 mm (5.0 mm past J2's empty cavity 3). J4 and J7 need a second layer (J4:
   3V3 and GND ride over the others to pins 1 and 2; J7: GND to pin 7), which
   lands at an end of the housing [into-the-housing i6]. The stage visits
   cavities lower layer first, and the upper-layer conductors wait lifted until
   last.

- **What the person does.** Loads the housing in the nest and the ribbon end in
  the web clamp, and takes the finished assembly out; pours contacts for the
  nozzle, if the shuttle nest is used; splays and strips, unless other stations
  do.

## Where conductor k's length comes from

Each contact is crimped ~14 mm short of its seat and pushed home alone. With one
web clamp, square-cut ends and every contact seated taut, conductor k must be
~14 mm longer than the straight line at the moment of its crimp. Stored as a
hump between the web and the post tip, that is 11–15 mm high over a 25–40 mm
split, with a tightest radius of 2.6–3.5 mm; the strands yield, so the hump holds
its shape and the push draws it straight with a few hundredths of a newton
[ith-w3 B; w3 §3]. Three ways to supply it:

- **A hump presser** (a saddle behind the post line, as into-the-housing's i1 and
  i2 use): the conductor is laid long and pressed into a hump before the crimp.
  Where the hump can stand with a punch holder above the post tip is open; near
  the barrels a clamped hump is still ~2 mm high 4 mm from the barrel end.
- **The web follows each push.** The web clamp's Y advances ~14 mm with the fork,
  so conductor k is straight at its crimp. Every seated conductor bows while the
  web is forward and straightens when it returns: 0.7–1.5 % strand strain,
  hundreds of bows to failure against at most eight per housing [w3 §3,
  estimate]. The waiting conductors advance too, so they must wait lifted above
  the housing's top.
- **Every post at once, one push** ([a4c](a4c-post-bed-one-push.md)): nothing is
  stored.

A shorter post ([a5](a5-housing-as-fixture.md)'s, ~2 mm out) cuts the hump to
6–8 mm but brings the dies to the housing face, where the seated neighbours must
be swept 17–30° instead of 2–4°.

## What locates what

| Moment | Reference | Located part |
|---|---|---|
| Finding the cavity | the lit square | cavity k's axis |
| Contact on the tip | the post (in plane); the shuttle's rear wall and floor with lance groove (at loading) | contact |
| The crimp | anvil and punch lead-in; the soft post only carries | barrels |
| The push | the post's line, which runs through cavity k by construction; then the cavity walls | box |
| The seat | the housing's own shoulder | contact |

**The reference for "fixed" is the station**: post slide, anvil block, punch
guide and camera on one base. The stage carries the housing and the web together
past it.

## What drives and carries the crimp force

The crimp closes through the anvil block and the punch's hard stop as in a2; the
anvil rises under the floor 9 mm clear of the rear face, and neither the post nor
the housing carries any of it. The push is 5–25 N per contact [estimate, KONNRA
clone ≤ 9.8 N] through the fork into the fork's slide, reacted by the nest.

## How it knows it worked

The lit square before the post; the contact's picture on the tip; the crimp's
stop and force trace; the proof-pull trace; the push trace (rise, drop, wall);
the 5 N pull-back; the post's clean withdrawal; the square going dark.

## Why it works, and what it avoids

- **Insertion is the hard part.** Sogang's printed ribbon inserter failed mostly
  in moving the floppy cable [prior-art, Start here]; Cellios measures the crimp
  in the gripper after every handling; Boeing aligns contact and hole with two
  cameras [prior-art §5]. Here the contact is threaded on a line that already
  passes through the target cavity.
- **Every hand-off stays on the post.** It locates the contact for the crimp,
  guides it into the cavity and gives the seat checks.
- **Die clearance on the seated side.** At 9 mm behind the rear face, the seated
  neighbours' wires need to move only ~0.3–0.55 mm sideways to clear punches
  3.5–4 mm wide [ts §8]: a 2–4° sweep, which a comb finger does.

## Problems and repairs

1. **The post's tip would meet the crimped conductor** if it stood still while
   the contact slid home. Repair: the post withdraws with the contact, driven or
   dragged.
2. **Conductor k's stored length** (above). Repairs: hump presser, web follows the
   push, or a4c.
3. **The waiting conductors lie in the die's path.** Conductor k+1's tip reaches
   the same Y as k's. At web pitch it lies inside any punch (−0.50 to −1.15 mm);
   fanned to 2.5 mm it clears a 2.7 mm punch (+0.30) and a 3.1 mm stepped crimper
   (+0.10) but meets 3.5–4.0 mm punches by 0.10–0.35 mm [ith-w3 C]. Repair: the
   waiting side waits lifted (a loft or finger), or narrow dies.
4. **Loading onto a post tip among wires.** Repair: a comb finger holds the seated
   neighbours back; the shuttle brings the contact along the post's axis, or
   gravity and a finger with the housing rear face up.
5. **The fork's tines in the neighbours' lanes.** Tines 0.4 mm either side of a
   1.7 mm wire total 2.5 mm, the pitch exactly. Repair: the comb finger holds the
   seated neighbours aside at the face, or the fork pushes on the crimped
   insulation barrel's top edge from above-behind instead of straddling.
6. **Is the post's path through the cavity clear?** The lance's catch is on the
   window side of the cavity, not on its axis [xh-facts §3, assumption]; the front
   opening is on the axis by design. One phone photograph of an XHP-4 held against
   a flashlight, square-on from the rear, shows whether each cavity has a clear
   straight line and how large it is, and whether white PA 6 lights up for the
   camera.
7. **Pin order is not cavity index on J4 and J7.** Repair: layer order (above).
8. **A 10 N seat pull** would be 51–68 % of retention. Repair: 5 N.

## Backing out

- A contact rejected before the wire: the shuttle draws it back off the post, or
  the post withdraws and the contact is stripped off at the rear face.
- A crimp rejected after the stroke: still outside the cavity on the post's tip;
  the carriage draws it off with its conductor, the machine stops that ribbon end
  and queues a cut-back.
- A fault found only at a seat check: extraction with an XJ-06 tool, and an ask.

## Steps covered, and what it hands back

- **Covers:** finding cavity k and checking its line; loading the contact onto
  the post; holding it; crimping; a proof pull before insertion; insertion; three
  seat checks; pin order in layers.
- **Hands back:** pouring contacts; splay, strip and conductor presentation;
  housing load and unload; the final continuity test.

## Printed and bought

| Part | Printed / bought |
|---|---|
| Housing nest and web clamp on one X stage, post slide, fork holder, comb finger, shuttle nest with lance groove | printed |
| Post | 0.64 mm square steel pin ≥ 25 mm, or an extra-long header pin: uxcell 30-piece 2.54 mm headers with 25 mm pins (Prime, $15.49; pin cross-section not stated [sourcing/amazon-prime.md]) |
| Low-friction post guide (dragged branch) | PTFE sleeve or printed V-guide ([`../sourcing-requests.md`](../sourcing-requests.md) #25) |
| X stage and post-slide drives | two small steppers with lead screws (28BYJ-48 5-pack, Prime, $14.99) |
| Light under the nest | LED and a diffuser, or 1 mm PMMA fibre (AZIMOM, Prime, $10.89) |
| Fork load cell | ShangHJ 5 kg bar cell with HX711 (Prime, $9.99) |
| Anvil, punch, press | as a2 |

## Contribution

It turns insertion from alignment into threading. The line the contact will
travel is established through the target cavity before the contact exists at the
station, and the same object holds it for the crimp. Light through the cavity
checks the line, guides the post and confirms the seat.

## Major unresolved problems

- **Conductor k's ~14 mm** at its crimp: a hump, a travelling web, or a4c.
- **Clearance of a 0.64 mm post through the cavity** past the housing's inner
  features (the photograph).
- **The dragged post:** whether the cavity walls hold it back more than the box's
  grip carries it.
- **Fork clearance among seated neighbours.**
- **The front-wall thickness,** which sets the push length (assumed 0.8–1.0 mm).

## What each conclusion rests on

- **Facts [mfr, source]:** housing height 7.75 mm and polarization [xh-facts §3];
  post size; Prime listings; prior-art on insertion failures.
- **Calculations [calc]:** push length, hump, stage drag [w3 §3; ith-w3 A, B];
  waiting-side clearances [ith-w3 C]; post stiffness [ts §7; w3 §8]; seated-side
  sweep [ts §8]; force ladder [w3 §9]; bow fatigue [w3 §3, with estimated
  constants].
- **Estimates:** guide friction; insertion force per contact.
- **Assumptions:** the cavity is clear on its axis; the front wall is 0.8–1.0 mm;
  post grip 0.2–2 N (secondhand Molex analog); white PA 6 passes enough light
  (v6's assumption); the lance's force signature (rise, drop, wall).
