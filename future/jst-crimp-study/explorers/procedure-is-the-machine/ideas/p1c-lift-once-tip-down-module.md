# p1c Lift once: the cassette under a hand-tool module

Sketch: [`../sketches/p1c-lift-once.svg`](../sketches/p1c-lift-once.svg) (schematic).
Numbers: [`../calc/wave3.out.txt`](../calc/wave3.out.txt) §1 (cited as
[calc wave3 §n]), [`../calc/wave2.out.txt`](../calc/wave2.out.txt) §1 and §3
(cited as [calc wave2 §n]), force-and-form's
[`exchange_procedure_w3.out.txt`](../../force-and-form/calc/exchange_procedure_w3.out.txt)
(cited as [calc FP §n]).

**A branch of [p1](p1-cassette-and-benches.md), and a combination.** It keeps
p1's cassette, its keys (key *k* = cavity *k*), the loft where crossings are
made at loading, the key blanks and single-purpose benches on dowels. It changes
bench B and the order of acts on each conductor: conductor *k* alone is lifted
once, and every act on it (trim, strip, measure, place the contact, crimp,
pull) is done in that one pose. Then it is laid back and squared. The
neighbours are never touched. The crimp head is a dedicated SN-2549 in a module
that closes its own force loop.

Sources, by name:
- **hand-tool-as-press** [a3](../../hand-tool-as-press/ideas/a3-tool-travels-to-ribbon.md):
  the SN-2549 with its pusher bolted to its own handle, the force loop closed
  inside a ~0.8 kg module, and the side-entry jaw law: an SN tool's nest axis is
  normal to its jaw plane, so its closing direction is the contact's floor
  normal;
- **hand-tool-as-press** [a1](../../hand-tool-as-press/ideas/a1-squeezer-cradle.md):
  the flap blade in the contact's neck;
- **terminal-supply** [a4](../../terminal-supply/ideas/a4-post-held-contacts.md)
  and [x1](../../terminal-supply/ideas/x1-post-feeds-the-hand-tool.md): contacts
  held on 0.64 mm posts, their offset measured on the post;
- this view's order finding: trimming each tip in the lifted pose, at the crimp
  station, removes the split-point scatter [calc selector_and_bow §1].

[p1d](p1d-lift-once-fin-from-below.md) is the branch that keeps this order and
replaces the hand tool with a fin rising from below into a steel C, so the lift
falls from 8.7–14.7 mm to 3.5 mm.

## Picture it: J1 in its cassette at bench B

**Where things start.**
- The person has loaded J1's cassette as in p1: the 5P and the 4P clamped,
  peeled 30–35 mm and fanned into keys 1–9, the tips standing past a root comb
  of 0.64 mm steel pins. Nothing has been trimmed or stripped.
- **The far end rides on the cassette**, its cut face clipped into a pogo block
  (ribbon-as-pallet a6; P75 pins [Prime: P75 pogo pins, 100 pack, $6.49]). Pads
  under the cassette meet spring contacts in every bench's dowel plate, so every
  conductor is a wire to the controller from the moment the cassette is docked.
- **The post revolver** at the end of the cassette's X carriage carries 12
  header posts on a 20 mm radius, parallel to the wire axis, loaded with J1's
  nine contacts in key order [Prime: 2.54 mm male pin headers, $7.99].

**The module's pose.** The SN-2549 [Prime: iCrimp SN-2549, $22.29] lies **on
its side** in a printed cradle: its long axis runs across the row (X), its jaws
close vertically (Z), and the **anvil half is underneath**, so a contact sits in
the nest floor-down, the way it will sit in the housing. A NEMA 17 Tr8×2
[Prime: NEMA 17 with integrated T8×2 lead screw, $27.99] bolted to the lower
handle pushes the upper handle through a load cell [Prime: bar load cell with
HX711, $9.99]. The mouth of the jaws opens toward −X.
- The same geometry with gravity turned is hand-tool-as-press a3's **on-edge
  fixture**: the cassette stands on edge, the tool hangs tip-down and closes
  horizontally, normal to the ribbon's plane.
- Hung tip-down over a flat row, closing along the row, the tool would roll
  every crimp 90° (barrels open along the row, every lance at a neighbour), and
  no housing could be slid onto that row. The pose above is the one that makes
  upright crimps.

**What moves.**
- **X:** the cassette slide, one key per 2.5 mm, or to the revolver.
- **Y:** a carriage along the wire axis.
- **A short X shuttle on the Y carriage** brings one of three heads to the
  station line: a grounded trim blade, a strip head, the SN module. The heads
  come to *k*; *k* never moves while it is worked.
- **Lift:** a finger under the station line, on a servo [Prime: DS3218MG 20 kg
  servo, $14.99].
- **The pusher** inside the module, and the revolver's servo.

**One conductor, *k*** (~80–110 s [estimate]):
1. **Pick first, with *k* still in the row.** X brings the revolver's top post
   to the station line. The shuttle brings the module there, jaws open, and Y
   slides the jaw faces over the contact's barrels to the taught bellmouth
   position (the camera measured that contact's box-to-barrel offset on its
   post).
   - The pusher closes only until the upper jaw's flare touches the wing tips,
     found as the first few newtons on the load cell. That is **short of the
     first ratchet tooth**: the contact is located on the anvil and under the
     flare, and its wings stay open.
   - The flap blade drops into the neck against the box's rear face, and Y backs
     off ~3 mm, drawing the contact off its post.
2. **Index and lift.** X brings key *k* to the station line. The finger raises
   *k* by *h* = *a* + 2.7 mm, where *a* is the depth of the anvil jaw half below
   the nest floor, 6–12 mm [assumption, hand-tool-as-press a3]: *h* = 8.7–14.7
   mm. The jaw's back face then sits ~2.1 mm above the row axis, about 1 mm
   over a crimped neighbour's insulation barrel (+0.95 to +1.25 mm) [estimate
   from the contact's floor 0.56 mm below *k*'s axis].
3. **Trim.** The shuttle brings the grounded trim blade and squares *k*'s tip in
   this pose. The blade cuts copper, so the far end reads which conductor *k*
   is, and that no other conductor reads: **identity where copper is touched
   anyway.**
4. **Strip.** The shuttle brings the strip head: V-jaws closing 2.4 mm from the
   trimmed tip and pulling 3 mm, or ribbon-as-pallet's
   [a8b](../../ribbon-as-pallet/ideas/a8b-spindle-with-touch-off.md) spindle.
5. **Measure.** The ELP camera over a backlight sees *k*'s bare strands in
   silhouette: the bare length (where the insulation edge is), and whether the
   brush of 60 strands is whole.
6. **Feed.** The shuttle brings the module, holding its contact, ahead of *k*'s
   tip, and Y slides it back onto *k*. The strands enter the open conductor
   barrel (0.72 mm into 1.68–1.90 mm), and the 1.7 mm jacket enters the open
   insulation wings (2.46–3.0 mm) [xh-facts §1]; nothing pinches the bore. Y
   stops where *k*'s measured insulation edge is mid-window.
7. **Crimp.** The pusher closes. At the end of the wing curl it pauses: the
   tool is insulated in its cradle and wired, so jaws → contact → strands → far
   end reads *k* a second time. Then it completes the ratchet cycle. Force
   against pusher position is logged with the cassette ID and key.
8. **Pull.** The pusher opens to the blade, and Y backs 0.5 mm against a 20 N
   spring with a switch. The load goes box → barrels → crimp → conductor; only
   the crimp carries it.
9. **Release.** The jaws open fully and the shuttle withdraws the module in +X,
   *k* leaving through the mouth.
10. **Lay back and square.** The finger lowers *k*, and a presser on the Y
    carriage pushes the crimp past the row by its springback into a slot bar
    lined with TPU.
11. **Next key.**

J1 end to end is nine cycles, 12–17 minutes. Then bench C gang-inserts the
squared row, as in p1.

**J2 and the crossings.** Key 3 is blanked in the cassette and its post is
empty. J4's and J7's crossings were made in the loft at loading; every crimp
reads which far-end conductor it is on, so a crossing laid into the wrong key
stops bench B at that key.

## Why lift once, and what the lift costs here

**The waiting conductors are never bent.** A presser that drops every waiting
conductor 7 mm near its tip leaves it 1.3–4.5 mm low at 20 mm free and
3.7–6.5 mm at 15 mm [calc wave2 §1(a)].

***k*'s own set never enters *k*'s own crimp.** Trim, strip line, measurement,
feed and crimp all see *k* in one bent shape. The lift pulls *k*'s tip back
1.9–8.6 mm at 20–30 mm free for *h* 8.7–14.7 mm, once, before the trim [calc
wave3 §1].

**The lift this tool needs is large**, because the whole anvil jaw half has to
pass outside the row. The rise left in *k* after it is laid back [calc wave3 §1]:

| Free length | *h* 8.7 | *h* 11.7 | *h* 14.7 |
|---|---|---|---|
| 25 mm | 0.6–4.3 | 2.5–7.5 | 4.9–10.8 |
| 30 mm | 0–2.3 | 0.5–5.2 | 2.0–8.2 |
| 35 mm | 0–0.8 | 0–2.9 | 0.4–5.7 |

(Residual rise at the tip, mm.) So this form wants a **30–35 mm split** and a
squaring pass after every crimp. The next key's lower jaw passes over *k*'s
crimp, so *k* must be back within ~0.5 mm of the row before the next cycle. A
fin from below ([p1d](p1d-lift-once-fin-from-below.md)) needs 3.5 mm and leaves
0–0.05 mm at 25 mm free.

**The axial chain** [calc wave2 §3]:

| Arrangement | Worst | RSS |
|---|---|---|
| Lift once, strip in pose, contact by neck blade | ±0.29 | ±0.21 |
| Lift once, camera bare length, Y corrected, neck blade | ±0.14 | ±0.09 |
| Lift once, camera, contact offset measured on the post | ±0.12 | ±0.07 |
| Touch-off on strand tips, no camera, neck blade | ±0.35 | ±0.22 |

The window is ±0.3 mm [estimate]. Touch-off finds the strand tips, the wrong
end for the insulation edge; the camera finds the edge itself.

**Camera depth and the neck blade are two stops on one axis.** With depth set
by the camera, the strand tips must stop short of the blade whatever the strip
scatter. The neck then has to hold the blade, box clearance, the scatter gap and
a visible brush: *n* ≥ 0.70–0.90 mm [calc FP §5]. The clone drawings allow
0.30–2.28 mm [force-and-form]. If the kit contact's neck is shorter, depth
comes from touch-off on the blade instead (±0.22 mm RSS), and identity is read
at the same touch.

## Where the order of the priority step sits

| Order | Contact held by | Conductor held by | What moves at placement | Used by |
|---|---|---|---|---|
| Contact waits on an anvil, conductor laid in from above | anvil (pilot or blade) | fork + lay-in finger | conductor, down ~1.5 mm | p1 B-drop, p5, applicators |
| Contact located in the tool, conductor fed along the axis | tool at wing touch + neck blade | clamp or funnel | conductor, along the axis | p4, p4b, WC-110, a1, x1 |
| **Contact located in the tool, tool slides onto a still conductor** | tool at wing touch + neck blade | cassette comb + lift | **tool, along the axis** | **p1c, a3, p6 stage 1–SN** |
| Contact placed on the conductor first, tool closes around both | post, cavity or tack | clamp or lift | contact along the axis, then the tool | p1d, p5c, i2, a4b, c1b |

In p1c the contact is held by one thing, the tool, from the pick to the pull,
and the conductor by one thing, the cassette plus the lift. The tool must stay
short of its first ratchet tooth until the conductor is in: at that tooth the
wing tips are pinched to 1.4–1.6 mm, and a 1.7 mm jacket meets them edge-on
unless the barrel floor is 1.9 mm or wider [force-and-form calc wave2 §1].

## What locates what

| Moment | Located | Against | Held to |
|---|---|---|---|
| Dock | cassette | bench B dowels or three balls | ±0.02–0.05 mm [estimate] |
| Index | key *k* | X lead screw | ±0.02 mm |
| Lift | *k*, vertically | lift finger (bench) | ±0.1 mm [estimate] |
| Trim, strip | tip, strip line | heads on the Y carriage and shuttle | ±0.02 mm plus the strip tear |
| Measure | insulation edge | camera, fixed to bench B | ±0.05 mm |
| Pick | contact in the tool | anvil nest, flare at wing touch, neck blade | ±0.05 mm axial |
| Feed | insulation edge in the window | Y, corrected by the measurement | ±0.07–0.09 mm RSS |
| Crimp height | dies | the SN-2549's own dies, if they bottom | the tool's own, unmeasured |

"Fixed" for position is bench B's frame, which carries the X and Y rails, the
shuttle, the lift, the camera and the revolver. "Fixed" for crimp height is the
tool's own jaws.

## What drives the crimp and carries its force

The NEMA 17 on its Tr8×2 screw pushes the upper handle against the lower handle
it is bolted to. The force loop is handle → pivot → jaws → contact → jaws →
pivot → handle, inside the tool. The ~280 N at the grip [digest] never leaves
the module; the frame, the rails and the cassette carry positioning loads only.

## How it knows it worked

Identity at the trim and at the end of the curl; the force curve against pusher
position; the backlit silhouette before and after; the 20 N pull and its
switch; the squaring presser's force.

## Steps it covers, and what it hands back

- **Automated:** trim in the pose, strip in the pose, measure bare length, pick
  the contact, place the conductor in it, crimp, proof pull through the box,
  identity before the crimp, square into the row.
- **Handed back:** cutting, peeling and loading the cassette (crossings in the
  loft); loading the post revolver in key order; bench C gang insertion or hand
  insertion; labelling.

## Printed and bought

- **Printed:** the module cradle (insulating), the Y carriage and X shuttle, the
  trim-blade and strip-jaw carriers, the lift finger, the squaring presser and
  TPU slot bar, the post revolver, the pogo block, p1's cassette.
- **Bought** (Prime rows observed 2026-09-28): a dedicated SN-2549 ($22.29), NEMA
  17 T8×2 ($27.99) and MGN12 rails [Prime: MGN12 rail, $20.49], a bar load cell
  with HX711 ($9.99), a DS3218 servo ($14.99), 0.30 mm leaves for the flap blade
  [Prime: feeler gauge set, $8.99], header pins ($7.99), P75 pogo pins ($6.49),
  the light pad [Prime: LED light pad, A5, $16.99]. The ELP camera is on hand
  [repo].

## Contribution

- **"Lift once, and do everything to *k* in that pose"** applies to every
  arrangement that selects one conductor from a row: p1, p2, p3, p5, p6. It
  removes the waiting conductors' set and the split-point scatter together.
- **The axial chain shrinks to what the Y carriage and one camera frame know:**
  ±0.07–0.09 mm RSS against a ±0.3 mm window.
- **A $22 tool on hand makes the crimp**, with its force loop closed inside a
  module that any light slide can carry.
- **The pose that makes upright crimps with a hand tool**, and its price in
  lift, stated with numbers; p1d is the branch that pays less lift for made
  steel.

## Major unresolved problems

- ***a*, the anvil jaw half's depth below the nest**, over the ~20 mm of jaw on
  the pivot side that crosses the row. It sets the lift, and with it the split
  length and the set in each conductor.
- **A 30–35 mm split** behind the housing: whether Derek accepts it.
- **Squaring each crimp** back to within ~0.5 mm of the row, and whether copper
  that yielded twice stays where it is put.
- **The neck *n*** against the blade (above).
- **Crimp height is the SN-2549's**, fixed, and so is its insulation step on
  silicone. hand-tool-as-press a5 is the branch where height is a setting.
- **The proof pull's reaction** passes through the cassette's clamp on the
  jacket: the clamp must squeeze 15–30 % over 5–20 mm, or the copper creeps and
  good crimps fail [calc FP §4].
- **Gang insertion** still needs fronts on one line: bench C, p1's open problem.

## What rests on assumptions

- *a* = 6–12 mm, and the anvil half being the shallower half.
- Strand yield 60–120 MPa and silicone modulus 2–6 MPa behind the set tables.
- Cycle times, and the lift finger's ±0.1 mm.
- The post grip of 0.2–1.6 N is terminal-supply's estimate.
- Wing touch as a force threshold the pusher can find repeatably.
