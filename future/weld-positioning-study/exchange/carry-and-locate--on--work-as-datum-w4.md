# carry-and-locate on work-as-datum (wave 4): the work-hung suspension

I worked on `explorers/work-as-datum/ideas/work-hung-suspension.md` (D1, with
its plate hanger) and read branch A3 of `endcap-compass.md`.

Numbers come from `explorers/carry-and-locate/calc/wad_nose.py`. Its geometry
and masses are copied from their `suspension_calcs.py`:
- nose collar at barrel z = 30, 46 mm from the dot;
- base loop 40 mm beyond the grip butt;
- third ring at the housing top back;
- 1.6 kg of gun and shell, centre of mass at local (0, −30, 200).

Opening pose, hole dial minus 35.

My view: carrying and locating are different jobs. The question for D1 is
which loads the nose V is asked to carry, and whether its ability to locate is
borrowed from what it carries.

---

## Difficulty 1 — the nose locates only as firmly as gravity seats it, and gravity seats it lightly

**Variant.** D1 as written:
- a knife-edged ring with a 90° V bottom;
- a grooved nose collar at barrel z = 30, seated by the gun's weight share;
- an upper half closed by a ball-lock pin with clearance ("captive, not
  clamped");
- the base on a stiff X line and a Z ratchet wire;
- the third ring on a room Z wire at the housing back.

**Assumption.** Gravity seats the nose with 4.9–7 N (a 7–10 N nose share),
and that is enough to hold the nose's sideways and along-barrel loads.

**What statics says once all three vertical supports are present** (nose,
base Z wire, third ring):

- **The nose carries only ~4.1 N**, not 7–10 N. The third ring at the housing
  back takes 7.2 N and the base Z wire 4.4 N. The 7–10 N came from a two-support
  split (nose and base) before the ring was added, and the ring's position
  decides the split. At this ring position the nose is already below the ~5 N
  floor their text sets.
- **Gravity splits the nose load 0.70 into the V and 0.71 along the barrel.**
  The groove must take the along-barrel part. A 90° V-groove resists axial load
  only up to about the seating force, because the flank pushes the collar up
  out of the V. So under gravity alone the groove sits at its limit: 2.9 N of
  seating against 2.9 N along the barrel. Their own numbers show the same 1:1
  (seat 4.9–7, groove 5–7).
- **The disturbance set** (their magnitudes, and mine from the load
  inventory):

| Case | Seating left | Sideways | Along barrel | Base Z wire | Result |
|---|---|---|---|---|---|
| gravity only | 2.9 N | 0 | 2.9 | 4.4 N | at the groove's limit |
| stuck wire 5 N, +Y at the dot | −0.2 N | 3.6 | 4.9 | 5.0 | **nose unseats** |
| stuck wire 5 N, −Y | 6.0 N | 3.6 | 1.0 | 3.8 | holds |
| cable 5 N up at the grip butt | 2.4 N | 0 | 2.4 | **0.0** | **base Z wire goes slack** |
| hand on the trigger, 10 N | −0.4 N | 5.9 | 7.9 | −0.2 | **nose unseats, base slack** |
| wire push 2 N back along the barrel | 2.9 N | 0 | 0.9 | 4.4 | holds |

**The pattern:** the nose is both a carrier (it holds weight) and the locator,
and its locating capacity is borrowed from the weight it carries. Anything that
unloads it — the third ring, a lifting cable, a hand, the float that D0 hints
at — reduces how well it locates. The base Z wire has the same problem: it is
tensioned only by 4.4 N of weight, and the cable leaves the gun right there.

## Repair — preload that closes inside the loop; room lines tensioned by their own bungees

**D1-p (a branch; D1 stays as written).**

**1. A sprung upper jaw.** The loop's upper half becomes a jaw pressing the
collar down into the V with ~25 N from a leaf or coil spring, instead of a
closed half with clearance. The force closes inside the loop: nothing extra
reaches the plate, the hub or the tube.

- With 25 N, every case in the table holds: seating 24.6–31 N against at most
  5.9 N sideways and 7.9 N along the barrel.
- The only case still failing is the 10 N hand, and only at the base (next
  item).
- The ball-lock pin still opens the loop. The jaw is its spring-loaded upper
  half.

**2. Groove shape.** With the jaw, a 90° groove is fine. Without it, a steeper
groove (60° included) raises the axial capacity to ~1.7× the seating force.

**3. Base Z as a pair.** The ratchet wire plus a bungee pulling down at the
base, as their X line already is. The wire stays taut until the cable lifts
more than the bungee's preload (10–15 N suggested), instead of slackening at
4.4 N. The same fix applies to the third ring's wire.

**4. Then the weight can come off the work entirely.**
- Once every room line has its own preload and the nose has its own jaw,
  nothing needs weight for tension or seating. A constant-force balancer near
  the centre of mass can carry most of the gun.
- The plate then carries almost no weight, only disturbances. Sideways loads
  at the nose act ~185 mm above the nest, so ~0.19 N·m per newton, against
  the 0.9–2.5 N·m that lifts the loose tube.
  - A stuck-wire drag is internal (tube → wire → gun → nose → plate → tube)
    and does not tip it.
  - A 10 N hand on the trigger would put ~1.1 N·m on the first-closure tube,
    past its lift point. That is one more reason for a presser inside the
    shell.
- Derek's third-ring trade ("more weight on the ring, less on the tip") stops
  being a trade. Seating no longer comes from weight, so the ring can carry
  whatever is convenient.

**What the jaw changes, and what it leaves.**
- **Friction.** A preloaded ball joint has rotational friction:
  μ·F·r ≈ 0.2 × 25 N × ~12 mm ≈ 0.06 N·m. The room lines overcome it when
  angles are set. That is small against the 0.6–0.8 N·m gravity roll moment
  they already handle, but it adds stick-slip to fine angle moves.
- **Heat.** The jaw is metal near a printed collar 26 mm above the rim. The
  spring must sit outside the hot zone.
- **Interlock.** The jaw is at work potential and touches only the printed
  collar. Their interlock argument is unchanged.
- **Stuck-wire breakaway.** Theirs happened at 5–7 N; now it is ~25 N. The
  wire's stick-out yields at 3–5 N first, so the breakaway no longer protects
  anything the wire wouldn't. A deliberate breakaway, if wanted, is a weaker
  jaw spring.

## Difficulty 2 — mixed references: which of the "room" anchors actually matter

**Variant.** D1's room anchors (the base's X line and Z ratchet, the third
ring) hung from the ceiling or pegboard.

**Assumption.** Room lines only carry.

In D1 the base lines locate two of the six freedoms. Their motion reaches the
dot through the lever nose→dot / nose→base: 46 / 278 = **0.165**. So:
- 0.5 mm of pegboard or bench movement (someone leaning on the bench) puts
  ~0.08 mm on the dot;
- the base X line must be stiff in the metrology sense, not just taut.

**Repair.** Anchor the base X line and base Z pair on a post standing on the
rotator's base or its common plate, not the ceiling. The third ring's line
sets roll with a longer lever and can stay on the ceiling. A float (balancer)
anchor can be anywhere: it carries only. This is a sixfold relaxation of the
room frame compared with a gun held entirely from the room, but it isn't zero.

## Difficulty 3 — setting angles moves the dot, by a known amount

Every angle is set by turning the gun about the nose, 46 mm from the dot, so
the dot moves 0.8 mm per degree. Their D1 already takes this back with an XZ
micro-stage in the stalk ("dot knobs on the work"). I agree.

Two things to add:
- The order of adjustment is fixed: **angles first, then the dot.** The stalk
  stage does not disturb the angles, because the base and ring are on the
  room.
- At the base, the X line and Z pair, when locked, make each angle a single
  length:
  - base Z ≈ hole tilt (0.23° per mm);
  - base X ≈ plan angle;
  - ring ≈ roll.
  The circle symmetry makes the plan angle a tangent move of the whole hanger's
  azimuth as well, so the hanger's tether length is a second plan-angle knob.

## Branch A3 (paddle compass), briefly

- A3's two rollers on the dot's radius make the one room-set rotation leave the
  dot fixed. That is a real advantage over D1, whose nose is 46 mm off the dot.
- Its P3 foot carries 10–13 N of weight onto a room plane. P3's height being
  the hole dial (0.23°/mm) is the cleanest one-knob angle anywhere in the study.
- **From my view:** a float carrying the gun would take P3's 10–13 N away,
  leaving P3 a pure locator. It would also end their "force-quiet gun" worry
  about cable lift at the P1–P2 line, because the float and saddle take the
  cable.
- A3 with a float is close to my new combination
  (`explorers/carry-and-locate/ideas/nose-and-tail.md`): nose on the work, tail
  on a switch-locked plate. There, the tail plate's height turns out to be the
  same 0.23°/mm hole dial.

## What D1 does that my arrangements lack

- The dot's translations are referenced to the joint's own plate at a point
  46 mm away. Runout, face tilt and tube length are followed to 83–91 %, with
  no camera and no stage. My room-anchored suspensions need a per-tube trim for
  every one of those.
- A park state that *is* Derek's suspension as he stated it, kept whole.
- The interlock thought through: work potential never touches the gun's metal.
