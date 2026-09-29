# a3 — Loose contacts hang by their insulation wings on a slotted rail

Sketch: [`../sketches/a3-hanging-rail.svg`](../sketches/a3-hanging-rail.svg) (schematic;
rail cross-section from clone dimensions).
Numbers: [`../calc/terminal_supply.py`](../calc/terminal_supply.py) §1, §6 [ts §n];
[`../calc/wave2.py`](../calc/wave2.py) §10 [w2 §10]; machine-that-sees-and-learns'
[`on_terminal_supply`](../../machine-that-sees-and-learns/calc/on_terminal_supply.out.txt)
§11 [mtsl §11].

**Branches and uses.**
- [a3b](a3b-crimp-where-it-hangs.md) crimps the contact in the rail's end pocket
  without laying it down.
- The rail can hand contacts to [a4](a4-post-held-contacts.md)'s posts or to
  [a6](a6-post-is-the-gripper.md)'s travelling post head.
- Its box-down pose is the pose a housing lying rear face up accepts by gravity:
  the rail's escapement over such a housing stages contacts for
  [x3](x3-stage-crimp-one-push.md) and into-the-housing's
  [i2b](../../into-the-housing/ideas/i2b-preload-the-whole-housing.md) (below).

## Picture it

- **Where things start.** Loose contacts from the CQRobot kit bags are poured
  into a hopper. At a bulk packing of 0.1–0.2, a 200 cc hopper holds ~360–720
  contacts, 7–14 units [ts §1].
- **Lifting and dropping.** A printed scoop wheel turns slowly, a few rpm like
  Boeing's rotating-arm contact feeder [prior-art §3]. It lifts a few contacts at
  a time and drops them onto the high end of a tilted rail with a slot down its
  middle.
- **Hanging.** A contact that lands with its box over the slot drops in and
  hangs box-down, caught by its insulation barrel, whose open wings (2.46–3.0 mm
  on the clone drawings) are wider than the slot, like a screw hanging by its
  head in a screw presenter.
  - Anything lying flat, crossed or tangled is swept back into the hopper by a
    soft brush over the rail.
  - The slot is stepped: 2.4 mm at the barrels, 2.05 mm at the box. A contact
    whose box arrived turned 90° cannot enter the narrow part, rides ~2 mm high,
    and a height wiper knocks it off.
- **Travelling.** A small vibration motor walks the hanging contacts down the
  rail to an escapement of two gates that releases one at a time into an end
  pocket.
- **Orienting.** The rail's edges are black (black oxide, or a black printed cap
  on the ground edge), and a light shines up through the slot from below. Seen
  from above, a hanging contact is a silhouette: the box's rectangle inside the
  insulation U, with light passing only between the wing tips on the U's open
  side. That notch is 0.40–1.00 mm deep, 18–45 px on the stock ELP [mtsl §11].
  - The notch says which way the U opens, fore or aft along the rail. If it opens
    the wrong way, the end pocket, on a servo, turns 180°.
  - The same silhouette shows a tangled pair (two outlines, or a doubled wall)
    and a bent wing (a lopsided notch); those go back to the hopper.
- **Handing off**, one of four ways:
  - **(a3)** the hinged end pocket tips the contact 90° and lays it floor-down on
    a horizontal anvil, where a sprung flap pushes it against a stop (the WC-110
    flap-locator idea [xh-facts §2]);
  - **(a3b)** it is crimped where it hangs;
  - **(to a4 or a6)** a 0.64 mm post rises from below into the hanging box
    through a hole in the pocket's floor, lifts the contact until its wings clear
    the rail edges, and leaves through the pocket's open end along the rail;
  - **(to a housing lying rear face up)** the escapement drops the contact
    box-first into cavity k's rear mouth. Left to itself it slides until its
    lance tip meets the rear face, about 2.4 mm deep, which puts the conductor
    barrel's front at the face and leaves no room for an anvil. A post standing
    up through the cavity's front opening, tip set so the box stops 1.5 mm deep
    ([a5](a5-housing-as-fixture.md)'s gravity variant), gives the staging depth
    x3 crimps at. Odd cavities first, because clone wings collide at 2.5 mm
    pitch.
- **What the person does.** Tips a kit's contacts into the hopper every ~7–14
  units; clears the jams the machine could not; separates the kit housings from
  the kit contacts (the bags mix them).

## What locates what

| What | Reference | Note |
|---|---|---|
| Contact height (along its own axis, hanging) | the insulation barrel's lower edge on the rail top | that edge is ~0.4 mm from the conductor barrel, so hanging references the barrels directly; a carrier references them through a 0.7–1.15 mm tab that varies between brands [ts §2] |
| Box orientation (two of four roll states) | the stepped slot: 2.05 at the box, 2.4 at the barrels | [ts §6] |
| The last 180° | the camera's silhouette and the servo turn pocket | — |
| Position at hand-off | the end pocket (steel-lined) | then the receiving station's own reference |

**The reference for "fixed"** is the rail's ground edges and the end pocket
bolted to the same base. The rail carries no crimp force; it is a supply.

## How it knows it worked

A photo-interrupter at the escapement counts contacts. The camera sees presence
and U direction before release. At the crimp, the receiving station's checks
apply.

**Jams, before asking.** If no contact reaches the escapement within N seconds,
or the camera sees one riding high at the wiper, the machine reverses the
vibration, runs one extra brush pass and looks again. Only then does it ask,
with a photo. The log counts tangles and jams from the first day, which is a3's
unknown rate.

## The physics that makes it work

- **Why the contact hangs box-down.** It is supported at the insulation barrel,
  its rear end, and everything else is below the support, so its centre of mass
  hangs under the rail. Upside down it would stand on its wings with its mass
  above them, fall over, and be brushed off.
- **What a slot can tell apart** [ts §6; clone tolerances ±0.10 on the box,
  ±0.25 on open barrels]:

  | Slot | Box across (1.85 wide) | Box turned (2.2–2.35) | Conductor barrel (1.55–2.15 with tol.) | Insulation wings (2.45–3.25) |
  |---|---|---|---|---|
  | 2.05 | always passes | never passes | may jam | never passes |
  | 2.40 | always passes | may pass | always passes | never passes (0.05 mm margin at worst) |

  The stepped slot takes the good half of each and leaves two roll states.
- **The last 180°.** Mechanical discrimination is awkward: the U's opening and
  the lance both point along the rail, not at its walls. The camera looking down
  the U sees it plainly, and a slow machine has time to look and turn.
- **The lance does not snag.** It stands 0.6–0.9 mm proud on the floor side
  [xh-facts §1], which faces along the rail when the box is across the slot, so
  it never rubs a slot wall.

## Building it

- **Buy a screw presenter.** Bench screw presenters with adjustable M1–M5 rails
  exist: the CGOLDENWALL automatic screw feeder (Prime, $185.00, thin listing,
  adjustable track, slot range not stated [sourcing/amazon-prime.md]); eBay
  listings at ~$123–189; ATO at $369.38 with a 200–220 cc hopper; Hakko AT-1050
  at $630.17 [source]. ATO's rail rule is "bite-wing ~0.5 mm larger than thread
  thickness", so a rail set for ~M1.8–M2 gives the ~2.3–2.4 mm slot. The
  presenter has no step at the box level; a printed insert or a pair of shims
  under the rail could add one.
- **Or print it.** Hopper, scoop wheel and frame printed; the rail's two edges
  ground flat stock or hardened dowels, clamped with a feeler gauge as the spacer
  (Hotop 0.02–1.00 mm set, Prime, $8.99); a coin vibration motor (20-pack, Prime,
  $12.99); two servo pins as gates; a printed turn pocket on a servo.
- **The handoff pocket.** A hinged steel-lined pocket turned 90° by a servo lays
  the contact floor-down onto the anvil, which has a stop for the box's front face
  and a sprung flap that pushes the contact against it.

## Measuring a bag, not a contact

a3 turns on whether the kit contacts have a head: open wings wider than 2.4 mm
over a box that passes 2.05 mm. Twenty kit contacts poured on a light pad and
photographed once give the spread of a bag, every open-wing width and box width
to ~0.02 mm at 45 px/mm, and the pose odds a tray or pocket plate needs. The slot
widths are then set from the tail of that spread, not from clone drawings.

## Problems and repairs

1. **Genuine JST contacts may have no head.** JST's catalog end view is
   1.95 × 2.4 mm [xh-facts §1]. If genuine open wings are inside 1.95 mm, the
   contact is no wider at the rear than at the box and falls through any slot
   that passes the box; the Würth analog's 2.3 mm wings would too [w2 §10]. The
   clone drawings show 2.46–3.0 mm wings. So this feeder is for contacts with
   wider wings, likely the kit contacts and the LCSC clones. Hanging a genuine
   contact on its lance instead would load a spring that should not carry a
   vibrating part; not pursued. [a7](a7-if-the-contacts-switch-to-strip.md) sets
   out what else the supply choice changes.
2. **The open conductor barrel's ±0.25 tolerance jams a narrow slot.** Repair:
   the stepped slot.
3. **Open-barrel contacts nest,** a box slid into another contact's open U.
   Repair: a slow scoop, a brush, and a rail that rejects anything not hanging
   singly. The tangle rate is unknown. The scoop can make ten passes for one good
   contact.
4. **Vibration bends thin wings.** Repair: gentle vibration, and the camera
   rejects visibly bent wings back to the hopper. Unquantified.
5. **The tip transfer must land the floor flat and the box against its stop.**
   Repair: the flap locator; or skip the transfer (a3b), or hand to a post (a4,
   a6), which then carries the location with it.
6. **Silver on silver.** Tin-plated wings on steel rail edges read poorly.
   Repair: black rail edges and the light from below.
7. **Landing box-first in a rear-face-up housing** needs the escapement to put
   the box into a 1.9–2.1 mm mouth [assumption, mouth unmeasured]. That is the
   same landing-accuracy question as the tip transfer, plus which way the U faces
   relative to the cavity's window side, which the turn pocket sets. Without a
   depth-stop post, gravity stages the contact at the lance's own stop (~2.4 mm),
   too deep for a crimp at the mouth.

## Steps covered, and what it hands back

- **Covers:** supply, orientation and singulation of loose contacts; placing the
  contact at a hand-off (a nest, a post, a housing mouth). With a3b or a4 it goes
  on to hold and crimp.
- **Hands back:** refilling the hopper; splay, strip and conductor presentation;
  the crimp itself in the a3 handoff (any press station); insertion.
- **Why loose at all.** Strip-form contacts cost $0.47–2.50 per unit [ts §1] and
  avoid all of this. The loose route matters when Derek wants to use the kit
  contacts already on hand, or the only die available was cut for a loose-piece
  contact.

## Contribution

A gravity-and-slot orienter borrowed from screw presenters. It fits the kit
contacts' own shape: wide rear wings as a head, a narrow box as a shank. It
references the barrels by the insulation barrel's edge, and it can feed any of
the other stations, including a housing lying rear face up.

## Major unresolved problems

- **The kit contacts' real open-wing width and box size;** whether genuine JST
  contacts have a head at all.
- **Tangle and jam rate.**
- **Wing damage from vibration.**
- **Landing accuracy** of the tip transfer or the drop into a housing mouth.
- **Whether a bought screw presenter's rail and brush can be adapted,** or a
  printed one is the easier path.

## What each conclusion rests on

- **Facts [mfr, source]:** clone contact dimensions and tolerances (S19–S22);
  JST's envelope; lance height [xh-facts §1]; screw-presenter listings and ATO's
  rail rule; Prime listings.
- **Calculations [calc]:** hopper capacity [ts §1]; slot discrimination [ts §6];
  genuine versus clone wing gaps [w2 §10]; notch size in pixels [mtsl §11].
- **Estimates:** bulk packing 0.1–0.2.
- **Assumptions:** the kit contacts are clone-shaped [xh-facts §6].
