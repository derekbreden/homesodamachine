# a4 — Hold the contact by mating it: 0.64 mm square posts

Sketch: [`../sketches/a4-post-turret.svg`](../sketches/a4-post-turret.svg) (schematic;
turret not to scale, inset from clone dimensions).
Numbers: [`../calc/terminal_supply.py`](../calc/terminal_supply.py) §7 [ts §7];
[`../calc/wave2.py`](../calc/wave2.py) §5 [w2 §5]; [`../calc/w3.py`](../calc/w3.py)
§1, §2 [w3 §n]; machine-that-sees-and-learns'
[`on_terminal_supply`](../../machine-that-sees-and-learns/calc/on_terminal_supply.out.txt)
§7, §10 [mtsl §n].

**Branches.**
- [a4b](a4b-through-cavity-post.md) runs a long post through the housing first,
  so the post that held the contact for the crimp guides it into its cavity.
- [a4c](a4c-post-bed-one-push.md) puts a post through every cavity at once and
  seats every contact with one housing move.
- [a6](a6-post-is-the-gripper.md) uses one travelling post as a pick tool
  instead of a magazine of posts; [x1](x1-post-feeds-the-hand-tool.md) takes it
  to the SN-2549.

**Related.** into-the-housing's
[i2d](../../into-the-housing/ideas/i2d-locator-the-lance-never-touches.md)″ (a
steel pocket with a post in its front wall) and
[i6b](../../into-the-housing/ideas/i6b-post-bed-through-the-housing.md) (a bed of
posts through the housing) build on the same hold.

## Picture it

- **Where things start.** A printed turret about 70–80 mm across carries 16
  radial posts around its rim. Each post is a 0.64 mm square pin cut from a
  standard 2.54 mm break-away header and pressed into a printed socket.
  - Each post rises from a shallow recess shaped like the box's outline
    (1.85 × 2.3 mm). A contact pushed onto a post can sit only U-up or U-down,
    never on its side.
  - The contacts are female; the post goes into the box from the front exactly as
    a header post does, 1.5–1.8 mm deep, so its tip stays inside the 2 mm box and
    clear of the strands' brush. The box's front stops against the recess floor.
- **Loading, by the machine.** At a loading station on the far side of the
  turret sits a loading nest: a small open pocket with a lance groove along its
  floor (1.0 mm wide, ≥ 1.0 mm deep, so a barrels-up contact lies flat instead of
  rocking on its lance [w3 §2]), a front stop with a hole for the post, and a
  rear stop at the insulation barrel's edge.
  - A vacuum nozzle picks a barrels-up contact off a lit tray
    (machine-that-sees-and-learns [v4](../../machine-that-sees-and-learns/ideas/v4-tap-look-pick.md))
    and drops it into the nest. A nozzle can place into an open pocket; it cannot
    push a box onto a post (63 mN of hold against 0.2–2 N of mating) [mtsl §7].
  - The turret's post comes through the front stop's hole and spears the box.
    The rear stop takes the push.
  - The camera confirms U-up on the post before the turret moves on. A socket
    that turns 180° under a servo corrects U-down instead of skipping it.
- **Loading, by hand.** Derek pushes kit contacts onto the posts, U-up, ~3–5 s
  each, ~3–5 minutes per unit [estimate]. Or [a3](a3-hanging-rail.md)'s hanging
  rail delivers one onto a post rising from below.
- **Magazine form.** A 16-post turret holds a third of a unit. Printed post bars
  of ~20 posts at 6 mm pitch, three per unit, can be swapped like cartridges.
- **Build order.** Loaded in loom order, with an empty post where J2's cavity 3
  stays empty, the magazine is the unit's build list [repo cable-assemblies.md].
- **At the crimp station.** A small stepper steps the turret; a detent pin fixes
  the rim's position; the camera checks the contact is there and U-up.
  - The post holder floats ±0.2 mm sideways and ±0.2 mm in Z on light springs,
    preloaded from above, so the contact's floor rests on the anvil and the
    punch's lead-in centres the barrels without the post fighting it.
  - The ribbon carriage brings conductor k in radially, over the open U, steered
    by the insulation edge as seen.
  - The punch comes down: arbor press, lead screw and hard stop, as in
    [a2](a2-strip-indexer.md).
- **Release.** The carriage pulls conductor k back radially. The crimped contact
  slides off its post at an unmating friction of ~0.2–2 N [ts §7] and leaves on
  its conductor. The turret steps on.
- **What the person does.** Pours contacts on the tray, or loads posts by hand;
  splays, strips and inserts, unless other stations do.

## What locates what

| Direction | What sets it | Note |
|---|---|---|
| In the plane (across the contact) | the post in the box | the box's spring leaves centre it |
| Axial | box front against the recess floor | the small tongue at the box's front, 0.60–0.70 mm wide on clone drawings, touches first. Consistent, but not the box face. The camera can measure box front to conductor barrel on the post and the station stop corrected by it, as in a6 |
| Height | anvil top; the holder floats in Z | preload from above |
| Roll | the recess outline (two states), then the camera and the 180° socket | — |
| Turret angle | a detent pin at the station | a stepper with printed gears is ±0.05 mm or worse at the rim [estimate]; the detent takes it out |
| Pin entering the box at loading | the nest's floor and lance groove put the box entry at floor + 1.10–1.18 mm; a near-pointed pin tip captures ±0.18–0.31 mm | [w3 §1, §2] |

**The reference for "fixed" is the anvil block at the crimp station**, with the
detent that parks the turret against it. The turret is a carrier; it sets
nothing at the crimp except the contact's presence and roll.

## What drives and carries the crimp force

As a2: the punch lands on a hard stop on the anvil block, 0.8–2.6 kN closing
through the die. The post carries none of it; it only locates, and floats so the
die can centre the barrels. A short post is stiff (a 3 mm brass cantilever is
~155 N/mm [ts §7]), and a contact 0.1 mm off the anvil's centre would take ~15 N
of lead-in against a rigid post and bend the box or the transition; hence the
float.

## How it knows it worked

- **Before the wire:** presence and orientation. From above, U-up shows two wing
  tips and the open U; U-down shows the flat floor and the lance.
- **Electrically:** the post is metal and mated to the contact, so continuity
  runs from the post, through the contact and crimp, to the conductor's bared far
  end (a terminal block, a pogo pin on the cut face, or the spool's slip ring).
  It separates joined from open; it cannot grade a crimp (a good crimp is
  ~0.2–1 mΩ, the post-to-box contact 5–30 mΩ and variable, the conductor 6–35 mΩ
  over a loom [mtsl §10]).
- **On release:** the carriage's load cell feels the slide-off. If the contact
  stays on the post when the conductor pulls away, the crimp did not grip. That
  is 1–5 % of JST's 39.2 N: a check that the crimp gripped at all.
- **A proof pull:** a fork swung in behind the box, between the box and the
  conductor barrel, lets the carriage pull ~20 N against the box while the camera
  watches the insulation edge for slip.

## Why a post

- **It is the contact's own designed reference.** The female box exists to grip a
  0.64 mm square post and centre on it. The XH headers on the main board use
  "□0.64" posts [xh-facts §3], as do standard 2.54 mm pin headers.
- **A post holds the contact by the part the crimp never touches.** "The wire
  crimp section is mechanically decoupled from the post insertion section"
  [mfr S12].
- **It works for every supply form:** loose kit contacts, loose BXH, strip
  contacts pushed onto a post and then cut off their carrier, and contacts from
  the hanging rail.
- **Its grip is proportioned right.**

  | Load | Size |
  |---|---|
  | Grip (axial hold) | a few tenths of a newton to ~1.6 N [ts §7] |
  | Contact's weight | ~0.0004 N |
  | Sliding stranded conductor into an open U | ~0.01–0.1 N [estimate] |
  | Pulling the crimped contact off | 0.2–2 N |
  | What the conductor can carry | ~85–100 N breaking strength [xh-facts §1] |

  The grip is ~500–4,000 times the contact's weight and far below the
  conductor's strength, so the release is a pull on the wire.

## Problems and repairs

1. **Four roll states on a square post.** Repair: a box-outline recess cuts it to
   two; the camera and a 180° socket settle the last.
2. **A stiff post fights the die.** Repair: the floating holder, in X and in Z.
3. **A nozzle cannot load a post** [mtsl §7]. The nozzle places, the post holds:
   the loading nest. Spearing straight from the tray, with a backstop behind the
   contact, carried to its end, is [a6](a6-post-is-the-gripper.md).
4. **A barrels-up contact rocks on its lance** on a flat floor, 8–22° nose-up or
   nose-down, with the box front floor 0.9–1.7 mm high: the pin meets the box face
   instead of the entry [w3 §2, ith-w3 E]. Repair: the lance groove along the
   nest's floor.
5. **Post wear.** 3,500 crimps on 16 posts is ~220 matings each. A tin-plated
   header pin is rated for far fewer mating cycles as a connector, but here it
   only has to keep its shape; brass under worn tin holds dimension. Repair:
   replace posts per batch, or use hardened pins.
6. **The turret's rim position.** Repair: the detent at the station.
7. **Continuity through the post cannot grade a crimp.** It separates joined from
   open, and needs a bared far end. The proof pull and the pictures do the
   grading.

## Steps covered, and what it hands back

- **Covers:** loading contacts into a magazine in build order (nozzle and nest);
  holding the contact before and during the crimp; placing it on the anvil;
  crimping; release; a per-crimp joined/open check, a grip check and a proof
  pull.
- **Hands back:** pouring contacts on the tray (or loading posts by hand); splay,
  strip and conductor presentation; insertion, unless a4b or a4c is used.

## Printed and bought

| Part | Printed / bought | Evidence |
|---|---|---|
| Posts | 2.54 mm break-away male headers (20-piece strips, Prime, $7.99, 500+ bought in past month; pin cross-section not stated on the page [sourcing/amazon-prime.md]); or hardened 0.64 mm square pins for wear ([`../sourcing-requests.md`](../sourcing-requests.md) #16) | The CQRobot kits may already include male headers (question for Derek) |
| Turret or post bars, recesses, floating holder, detent, loading nest with lance groove, 180° sockets | printed; leaf springs from 1095 shim; the nest's front stop steel shim | — |
| Turret drive | 28BYJ-48 with ULN2003 (Prime, $14.99 5-pack) | [sourcing/amazon-prime.md] |
| Nozzle and tray | machine-that-sees-and-learns v4 | — |
| Anvil, punch, press, lever drive | as [a2](a2-strip-indexer.md) | — |
| Continuity check | a two-wire check on the ESP32 through a far-end terminal block, pogo pin or slip ring | — |

## Contribution

"Hold the contact by mating it": a holder that is precise, gentle, electrically
connected, releases by a pull, and fits any supply form. Loaded in loom order,
the magazine doubles as the build list.

## Major unresolved problems

- **The real grip force** of kit contacts on a header post. Unmeasured; a 0.1 g
  scale and a hanging weight settle it.
- **Whether clone boxes centre on a post** as well as JST's double-leaf design
  [mfr eXH "Original double-leaf contact design"].
- **The box entry's real size** (0.60–0.70 mm on clone drawings) and how much
  formed lead-in it has, which sets the capture.
- **The floating holder's design.**
- **Whether the box's 0.2 mm walls take a 20 N pull on a fork edge.**
- **The header pins' true cross-section** in the Prime-listed strips.

## What each conclusion rests on

- **Facts [mfr, source]:** the 0.64 mm post; JST's decoupled crimp and post
  sections; clone box and entry dimensions; Prime listings.
- **Calculations [calc]:** post stiffness and grip bracket [ts §7]; capture at the
  entry and the lance-groove geometry [w3 §1, §2]; rest angles without a groove
  [ith-w3 E]; nozzle hold [mtsl §7]; resistances [mtsl §10].
- **Estimates:** loading time; conductor slide force; rim accuracy.
- **Assumptions [secondhand]:** post grip 0.2–1.6 N from a search summary of the
  Molex KK 254 specification PS-10-07-001 (200 g minimum normal force, 57 g
  minimum unmating on 0.64 mm posts); the document itself was not opened.
