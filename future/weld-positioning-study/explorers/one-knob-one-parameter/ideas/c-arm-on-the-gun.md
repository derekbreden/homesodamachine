# C-arm on the gun: the scene's three dials as three physical axes

**Picture it (original).**
- **Frame.** A goalpost frame straddles the rotator.
- **Yaw.** A rotary table hangs from the crossbeam with its axis on the dot's
  vertical. It carries a yaw frame, turned −15° at the opening pose.
- **Hole angle.** The yaw frame holds an R 300 mm arc centred on the dot. The
  arc lies in a vertical plane 50 mm outboard of the tangent plane; a carriage
  on it sets the grip-axis elevation (the hole dial), read straight off the arc.
- **Roll and standoff.** The carriage carries the roll joint on the grip axis
  behind the butt, and below it the roll body, standoff rail, shell and gun.
- **Work.** The rotator only translates on X/Z/Y slides, and never rotates for
  an angle change.
- **Cables.** The umbilical hangs from a balancer on the crossbeam or the yaw
  frame.
- **Fixed** is the goalpost and the baseplate.
- **Branch C-0** (wave 3, after borrowed-ecosystems) deletes the yaw table. The
  arc then hangs from the fixed goalpost, and yaw becomes the work's Y slide.

Sketch at the opening pose 45/30/−15: `../sketches/c-arm-side.svg`.

**Major unresolved problems.**
- Whether a rotary table can hang table-down.
- The arc's compliance as the carriage moves down it.
- 10–14 kg hanging at head height.
- The gun meets the yaw frame above ~60° of hole angle.

C-0 removes the first and third.

Sketch: `../sketches/c-arm-side.svg`. Same isocentre principle as
`isocentric-couch-and-gantry.md` (read that first for the knob, calibration
screw and motion-to-a-stop vocabulary and the walk test). This file keeps the
original idea whole: **all three rotations on the gun side, nested exactly as
`pose.js` nests them**, and the work never rotates.

## The idea

`pose.js` applies grip roll innermost, then the hole axis, then the vertical
axis outermost. Build that chain literally:

1. **Vertical axis (outermost).** A rotary table hung from a crossbeam, its
   axis on the vertical line through the dot, about 420 mm above the dot. It
   carries everything below it.
2. **Hole axis.** A C-arc of radius 300 mm centred on the dot, hanging from
   the yaw frame. It lies in a vertical plane 50 mm outboard of the tangent
   plane, which keeps it outside the tube and clear of the umbilical. A
   carriage runs on the arc; its position *is* the grip-axis elevation, which
   is what the scene's hole dial reads (the dial value equals the grip axis's
   elevation — checked in `geometry.py`).
3. **Grip-axis roll (innermost).** The carriage holds a preloaded bearing pair
   whose axis points at the dot along the grip axis, just behind the grip base.
   The roll body, standoff rail, shell and gun hang from it, as in the
   isocentric idea.

The rotator gets translations only: an X micrometer slide, a Y drawer, and Z
from three screw feet linked by a GT2 belt so that one knob moves all three.
Unlinking one screw makes it the calibration tilt that brings the tube axis
parallel to the yaw axis. Translations stay nearer ground than rotations,
which the principle requires. Here they sit on the work side because putting
them on the gun side would mean carrying the whole hanging assembly on an XYZ
stage.

What is different from the couch-and-gantry arrangement:

- **The work never moves for an angle change.** Purge hose, ground shoe lead,
  pedal cable, dot camera and the operator's view of the puddle stay exactly
  where they were when φ changes. In the couch version they all swing about
  the dot.
- **Each dial is the scene's dial.** Same zero, same sign, same order. A pose
  explored in the web scene is dialled as three numbers. That makes the scene
  itself the station's planning tool.
- **The hole angle is read straight off the arc.** At R 300, 0.1° is 0.52 mm
  of arc, so a vernier on the carriage reads 0.05°. It needs no gear.
- **The umbilical's support can ride on the yaw frame.** A balancer on the
  frame turns with φ, so the cable's drape relative to the gun is independent
  of φ.

## Geometry

- The gun's highest proxy point is about 240 mm above the dot at hole 45°. The
  yaw table's underside needs to clear the gun and the yaw frame's upper
  member, so it goes about 420 mm above the dot. With the ~60 mm trim stack
  and the bench at 28 in, the crossbeam comes out near 1.45 m above the floor:
  under head height, but in the space the operator's head wants.
- The arc is drawn from 8° to 78° of grip-axis elevation, 370 mm of arc. Its
  upper end sits 293 mm above the dot and 62 mm behind it; the lower end is
  about 42 mm above joint height, 297 mm behind. Every point of the arc is 300 mm
  from the X line. Anything more than about 160 mm from that line clears the tube
  at any angle, so the arc is clear of the tube at every yaw.
- The goalpost posts stand outside the yaw frame's sweep (about 330 mm radius).
  The drawn posts are at −400 and +260 mm along Y. Yaw only swings the frame's
  far (−Y) end sideways, so ±60° of yaw does not reach the +Y post.

## Trying to break it

1. **The yaw frame's centre of mass is off the yaw axis.** The gun and arc
   hang 150–300 mm behind the dot, so the moment on the yaw bearing and
   crossbeam points wherever the gun points. As φ changes, the crossbeam's
   bending and twist change and the whole hanging chain tilts a little. A
   drop of about 420 mm turns 0.1 mrad into 0.04 mm at the dot, and this walk
   is tied to φ. *Repair:* counterweight the yaw frame so its centre of mass
   sits on the yaw axis; the crossbeam then sees a pure vertical load at every
   φ. *Left:* the gun's centre of mass moves with hole and roll, so the
   balance is exact at one setting only. The residual (about 1 N·m for a
   1.2 kg gun moving 80 mm **[assumed]**) is what the walk test measures.
2. **A machinist's rotary table hung upside down.** Its table is retained for
   loads pressing it *onto* the base. Hanging 10–14 kg from it reverses that
   **[Unknown whether a given table tolerates it]**. *Repairs:* stand the
   table upright on top of the crossbeam and hang the yaw frame from a
   shouldered shaft through its MT2 centre bore; or build the yaw joint from a
   tapered-roller pair in a housing, with the module-1 worm driving a printed
   sector.
3. **Yaw axis not vertical.** A tilt δ makes a yaw change also change the
   hole elevation by about δ·sin φ. That is two parameters from one knob.
   *Repair:* level the yaw table with shims under the crossbeam mount, then
   check with the walk test (sweep φ and watch whether the dot traces a line
   rather than staying put).
4. **The arc is a curved cantilever.** If it hangs from its top alone, its
   deflection changes as the carriage moves down it: the load's lever arm
   grows. That couples hole angle to dot position. *Repair:* a strut from
   the yaw frame to the arc's lower end makes it a supported curve, and a stiff
   arc does the rest: one 12.7 mm 6061 plate cut to shape (SendCutSend lists
   .500–.750 in 6061 and MIC-6 with delivery in days). The carriage runs on
   four edge rollers (two on eccentrics for preload) and four face rollers.
   The drive is a GT2 belt bonded to the arc's outer edge, used as a rack,
   with a pinion and worm on the carriage: knob, self-lock and AS5600 in one.
   *Left:* measured arc and carriage compliance.
5. **Gun meets the yaw frame at high hole angle.** Above ~60° the gun's back
   rises toward the frame's upper member. A hard stop on the arc sets the
   limit until the scan gives the real envelope.
6. **Loading.** Yaw, hole and roll all pivot about the dot, so none of them
   takes the nozzle away from the tube. As in the couch version: wire guide
   flips up, standoff lever lifts the gun 40 mm up its barrel line, Y drawer
   slides the tube out.
7. **Weight and space overhead.** 10–14 kg hangs over the work at head
   height, from a frame that straddles the rotator and the operator's reach.
   That is a real cost against the couch version, whose gantry side stands
   on the baseplate.

## Parts that change the picture

- The **yaw joint** is the hard one. A bought rotary table fits only if it
  tolerates hanging loads (see break 2).
- The **arc** is the part Derek can print or have cut. A printed PET-GF arc
  with a bonded belt is cheap and fast. A cut aluminium plate is stiffer and
  still takes days.
- Everything else is shared with the couch version (sourcing file).

## Contribution and open problems

It keeps the work completely undisturbed by angle changes, and it makes the
scene's dials physical one for one. The price is that everything the angles
need hangs overhead from a single bearing. Open: whether the yaw table can
hang or needs a purpose-built joint; arc compliance; overhead mass and space;
the high-angle collision limit.

## Wave-3 branch: C-arm without its yaw joint (after borrowed-ecosystems)

The original above stays as the literal dial-for-dial machine. borrowed-ecosystems
pointed out that its outermost joint is redundant for a circular joint.
Rotating the gun about the dot's vertical by φ is equivalent to translating the
work along the chord: R sin φ tangentially and R(1 − cos φ) radially. The work
side already has an X micrometer and a Y drawer.

**Branch C-0.**
- The C-arc hangs from a *fixed* goalpost, and yaw becomes the Y micrometer,
  plus a printed X cam for large angles.
- Gone: the overhead bearing, the hanging-table question, the φ-dependent
  crossbeam walk (break 1), the counterweight, and 4–6 kg over the operator's
  head.
- The work still never *rotates*; it only translates, so the purge hose, ground
  lead, camera and the view stay put. That was the C-arm's main advantage over
  the couch.
- The arc now carries a load that always pushes the carriage the same way down
  the arc (1.0–3.3 N·m about the hole axis). The carriage can rest on a
  micrometer stop or a gauge stack (sine-arm style), with the belt rack kept for
  motorised sweeps.

**What it costs:** the scene's vertical dial is no longer a physical dial. For
±3° it is one knob to 0.085 mm; beyond that it is two knobs, or a cam.

**Where it lands:** C-0 is the couch-and-gantry station without the couch table,
with the hole axis on an arc rather than a table on the axis. The arc supports
the gun close in, while a single bearing on the hole axis does not. That
stiffness difference is the one real reason left to choose the arc. The two
ideas have converged; the arc-versus-table choice is the remaining fork.
