# i2c — Branch of i2: a real housing cut short as a permanent crimp locator, latched by the lance

- **Branch of:** [i2](i2-crimp-in-the-cavity.md).
- **Its own branch:** [i2d](i2d-locator-the-lance-never-touches.md), which keeps the
  stub but never lets the lance engage it.
- **Numbers:** [`../calc/insertion_geometry.out.txt`](../calc/insertion_geometry.out.txt)
  [calc geometry §n], force-and-form's [`on_into_the_housing.out.txt`](../../force-and-form/calc/on_into_the_housing.out.txt) [f&f §n].

**What it changes from i2.**
- i2 uses the product housing as the locator. i2c uses a **sacrificial XHP
  housing cut down** and mounted permanently on the press.
- The contact latches into the stub by its own lance, so the lance catch is the
  axial reference. The barrels stand out behind the cut face.
- After the crimp, a pin through the stub's window lifts the lance, as JST's
  XJ-06 extraction tool does [mfr S10]. The crimped contact is withdrawn and
  carried to the product housing.
- It exists for the case where i2's lance condition fails, or the product
  housing is a poor thing to crimp against.

## Picture it

- A real XHP-2 or XHP-3 is cut with a flush cutter or a fine saw just behind
  where the lance catches, ~3 mm from the mating face [estimate: lance tip
  2.44 mm behind the contact's front (source S22) plus a ~0.6 mm front wall].
- The stub is bonded into a steel holder whose rear face is the die's front
  wall.
- A contact is pushed box-first into the stub until its lance snaps behind the
  molded shoulder. Its Y position is now set by the feature the product housing
  will use.
  - With the stub cut at ~3.2 mm, the conductor barrel's front sits at the cut
    face, 0–0.5 mm proud.
  - A thin front wall on the die and a slight bellmouth-side offset take the
    tolerance.
- The conductor is laid in and crimped by whatever press carries the stub (i2's
  knee in a steel C, or a hand tool's jaw set behind it).
- A spring pin enters the window from the mating-face side and presses the lance
  flat.
- A gripper on the crimped barrels draws the contact back out of the stub and
  carries it to the product housing, as in [i1](i1-lift-to-the-head.md),
  [i4](i4-gantry-hand-with-eyes.md) or [i6](i6-sort-then-push.md).

## At a glance

| | |
|---|---|
| **What locates the contact** | The stub's cavity walls (X, Z, roll) and its lance shoulder (Y) |
| **Reference for "fixed"** | The steel holder the stub is bonded into, on the press frame |
| **What drives and carries the crimp** | Whatever press carries the stub; the stub carries none of the crimp force, only the contact's axial position |
| **How it knows** | The latch click into the stub (a force trace on the loading pusher); the press's own trace; after transfer, the product housing's insertion trace |
| **Steps it covers** | Place the contact on a locator, crimp |
| **What it hands back** | The transfer to the product housing (another arrangement's job); ribbon presentation as in the host press |

## What it keeps and what it gives up

- **Keeps:** a locator that costs a few cents, molded to the contact's shape at
  the right pitch, whose axial stop is the lance itself. A spent stub is
  replaced with another housing.
- **Gives up:**
  - the product housing as locator;
  - the no-transfer property. A crimped contact is released and must find a
    cavity again, which brings the dexterous step back;
  - the lance's first fold. The feed-length rule applies to the transfer
    (~8 mm) [calc geometry §9].

## Problems it meets

- **The lance takes a set with every fold** [f&f §8].
  - A 0.2 mm bronze lance 1–3 mm long reaches first yield at 0.015–0.18 mm of
    tip travel, against 0.6–0.9 mm of stand-proud. Folding it into any cavity is
    partly plastic by design [assumption: the lance is about as long as the
    drawings suggest].
  - i2c adds three folds: a latch into the stub, a lift to release it, and a
    second latch into the product housing. Each costs lance height by an
    unknown amount.
  - This is i2c's largest problem, and the reason for i2d.
- **The cut plane.** Too far forward loses the lance shoulder; too far back puts
  the conductor barrel inside. Cutting a few stubs at 0.2 mm steps and trying
  each with a contact finds it, with $0.03 housings.
- **Lifting the lance repeatedly.** JST warns that removal beyond the specified
  angle damages contacts [mfr S5, removal work]. Unknown: whether a contact
  released once still holds full retention. Pull-test a few.
- **PA6 stub wear.** The shoulder the lance catches on wears each cycle, and is
  counted by use.

## Contribution

It names the axial reference no printed nest can copy: the lance catch itself.
Its cost, three lance folds, is what leads to i2d.

## Major unresolved problems

- Retention of a contact whose lance was folded, lifted and folded again.
- The transfer to the product housing.
- The cut position tolerance.

## What rests on assumptions

- Lance length and yield figures [assumption, f&f §8].
- Front wall ~0.6 mm [estimate].
