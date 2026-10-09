# Lidded mouth (seed, not developed this wave)

## Picture it (as it now stands)

- **Seed (mine):** a stationary lid hung from the collar a few mm over the
  turning rim, carrying gun, camera and gas ports.
- **Developed form (work-as-datum's L1):**
  - A 3 mm sheet disc rides the plate through the port seat and three
    stainless ball transfers, 3 mm above the rim.
  - It is notched from −35° to +10° for the barrel and wire.
  - Lugs park it on the collar whenever the shelf drops, and the plate picks it
    up again when the shelf rises.
- **L1a (theirs):** a nose ring on the lid holds the nozzle cone, and the
  gun's tail rests on the collar.
- **L1h (mine):** a hold-down through the centre pin keeps the lid from tipping
  under the ring load.
- **L1p (mine):** the split-mount rollers replace the ring.
- **"Fixed":** the lid is fixed to the plate; the gun's tail is fixed to the
  collar.

**Sketch:** `../sketches/lidded-mouth.svg` (seed). work-as-datum's L1 sketch is
`../../work-as-datum/sketches/xw-collar-centre-and-lid.svg`.

**Major unresolved problems:**

- Heat and spatter 3 mm above the rim.
- A ring on the copper nozzle (interlock contact, cooling).
- Nipples in the ports at weld time.
- The gun's centre of mass, which sets the ring load.


Sketch: `../sketches/lidded-mouth.svg`.

## The idea

A stationary lid a few millimetres above the turning tube's rim, hung from the
collar. The lid is workspace structure that sits closer to the joint than
anything else can, and it carries:

- a **gun port**: in the scene's opening pose the nozzle crosses the rim plane
  ~5 mm above the rim (Ø17 copper nozzle section), so the lid needs a slot
  there. A ring around the nose at that slot locates the gun's front end ~40 mm
  from the dot, like a pool-cue bridge; the tail rests on the countertop or a
  sled. Two-point support: front constrained laterally in the lid, rear on the
  plane.
- a **camera port** on the +Y side (opposite the gun), fixed geometry for a
  camera that sees the dot and the puddle.
- an **argon / extraction port**: the tube interior becomes a nearly closed
  chamber — a place to flood shielding gas from above and pull fume.

It also contains most back-reflection from the mouth, which today goes up into
the room.

## First breaks, not yet worked

- The lid is ~5 mm above a fillet weld and directly in the plume: heat,
  spatter, fogging of any camera window.
- A nose ring 40 mm from the dot carries lateral position almost 1:1 to the
  dot; the ring's position would have to be the precise element.
- It hides the mouth from the operator; everything becomes camera-mediated.
- Loading: the lid lifts with the gun or slides off.

## Why keep it

It's the one piece of workspace that can sit at the joint's scale, and it
merges three things other arrangements treat separately: laser containment,
camera mounting and gas geometry. Worth a later wave if cameras and shielding
come up in other explorers' work.

---

## Wave 3: work-as-datum's repair L1, and where it needs one more part

Source: `../../../exchange/work-as-datum--on--workspace-as-structure.md` §2.
The seed above (a collar-hung lid) is kept. Their objection: a room-hung lid
can't sit a few millimetres over a rim whose height changes by ±3.2 mm from
tube to tube and ±0.15 mm per revolution, and its nose ring is referenced to
the room while the corner moves. Accepted.

### L1 (theirs, adopted as the lid's main form): the lid rides the plate and parks on the collar

**How it rides:**

- A 3 mm sheet disc, Ø~150, sits on the plate through the port seat (centre
  pin) and three stainless ball transfers at r = 40 (50°, 170°, 280°).
- Its underside is 3 mm above the rim, a gap set only by the recess and rim
  waviness.
- A notch from −35° to +10° (for r > 42) lets the barrel and wire in; the
  plume leaves through the notch, where extraction belongs.

**How it parks:** lugs over the collar stand 5 mm above it. Drop the shelf
more than 5 mm and the lid parks on the collar; raise it and the plate picks
the lid up again. A pin in a slot holds azimuth in both states.

**What this does for this station:** it uses the shelf drop the station already
has.

### L1a (theirs): nose ring on the lid, tail on the collar

A split ring on the lid holds the nozzle cone 26 mm from the dot; the gun's
tail rests in a cradle on the collar ~220 mm behind. Work motion d reaches the
dot as 0.12d (tail 220 mm, dot 246 mm from the tail: 246/220 − 1), and the gun
tilts d/220. At full cut tolerance that is 0.38 mm and 0.83°. With T-W1
fitted (`table-opening-gantry.md`), tube length is already absorbed and the
residual is the ~0.02 mm level.

### Difficulty found in L1a: the ring load lands outside the lid's support triangle

**What the ring carries.** It takes lateral load and, if it constrains height
at the nose, part of the gun's weight: roughly 40–55% of ~15 N, i.e. 6–8 N,
with the CG about 100–150 mm behind the ring [gun CG Unknown].

**Where that load lands.** The ring sits at r ≈ 55, azimuth ≈ −10°. The lid's
balls at r = 40 put the nearest triangle edge (the chord between the 280° and
50° balls) ~17 mm from the centre, so the ring load acts ~40 mm outside it.

**Why the lid tips.** That makes 0.24–0.32 N·m tipping the lid about that
edge. The lid's own weight (~4 N for 3 mm steel, Ø150) at 17 mm restores
~0.07 N·m.

**The two ways out, both with a cost:**

- **Vertically free ring (a slot):** then the nose height comes from the tail
  cradle, and tube length reaches the dot 1:1.
- **Height-holding ring:** then the lid needs a hold-down.

### Repair L1h: a hold-down through the centre pin

This is the paddle compass's clamp: a ~30 N spring and thrust washer on the
centre pin pulling the lid onto the plate. The pin pulls the plate up and the
balls push it down 40 mm away, so the net force on the loose tube is zero.

- 30 N × ~17 mm to the edge adds ~0.5 N·m of restoring moment, enough for the
  6–8 N ring load with margin.
- The nipples carry 30 N in tension.

### Branch L1p: paddle contacts on the lid

Put the lid's two plate contacts on the dot's radius (rollers at r 36 and −40,
the paddle geometry), plus the centre pin and hold-down. Then the one rotation
the collar sets, about that line, leaves the dot fixed exactly instead of at
0.12d.

- **Cost:**
  - a roller 11–12 mm from the nozzle at the opening pose (tighter at
    vertical −30°);
  - two contacts on the plate face instead of the ring's single contact on the
    nozzle.
- **Gain:**
  - nothing grips the copper nozzle, so there is no question about interlock
    contact or nozzle heat through a ring;
  - the dot geometry is exact.

L1a stays the simpler part to build, L1p the more exact one.

### Still uncertain

- Heat and spatter on a lid 3 mm above the rim, 10–20 mm from the puddle at
  the notch edge.
- The nipples in the ports at weld time (Derek).
- Whether a ring on the nozzle cone affects the interlock or nozzle cooling
  (L1a only).
- The gun's CG, which sets the ring load and the hold-down size.
