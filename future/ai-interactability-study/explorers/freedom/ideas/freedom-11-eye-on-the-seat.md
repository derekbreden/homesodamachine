# freedom-11: eye on the seat (the gun-borne eye's trim range, spent per newton, and where its camera can stand)

Scene: `scenes/freedom-11-eye-on-the-seat`. Origin: combination of `eyes-01-gun-borne-eye` (deep) and `freedom-01b-nose-seat` (mine), drawn in wave 2 from the exchange `exchange/freedom--on--eyes-w2.md` (section 1). Depth: developed (four break-and-repair entries, numbers from `calc/eye-support.js`, `calc/29-eye-support-budget.cjs`, `calc/30-eye-support.cjs`). Every stiffness, mass and force is **illustrative**; gun mass, centre of mass and the umbilical's pull are **[unknown]**.

## Picture it

The gun with eyes-01's camera and line laser on its barrel, hung one of two ways. Either from a rod to a lug on the housing, the rod carried by a stage that hangs from one elastic (eyes-01 as drawn), or from freedom-01b's cone seat near the nozzle with a two-wire, two-bungee bridle at the tail. A slider for the umbilical's pull is the disturbance; the gun was hand-set at a setup pull and the eye's trim stage (the nose stage, in the seat variant) is asked to bring the dot back. The readouts say how far the dot moved per newton, how many newtons fill the trim, and how far the beam turned where the eye cannot see. A small table of green and red cells is the camera map: which station on the barrel and which clock angle keep the corner in view once the cup, collar and stage are there.

## The proposal

Keep eyes-01's idea (measure the seam against the dot in the gun's frame, so the support can be loose and a small stage does the fine work) and ask what "loose" has to mean. A support is soft in a motion only if something else holds the motions the sensor does not see. Two supports, one eye:

- **One elastic under a rigid lug.** The dot moves with every change of pull and the beam turns with it, because nothing holds rotation.
- **The nose seat and tail bridle.** The pivot is 60 to 110 mm from the dot, so a tilt costs little at the dot and the tail wires hold the tilts with wires 200 N/mm stiff at a 160 mm half-width. The eye's trim is the nose stage; each of the seat's six actuators keeps its own job (nose X, Z: the eye's r and z; nose Y: tangent, left free; tail wires: pitch and roll, to be closed on the IMU of eyes-11 or the eye's line slopes; the yaw bungee anchor: yaw).

## What carries loads, what establishes position, what is free or restrained

- **Load:** the elastic and rod (lug variant), or the cone seat with a preload spring and the tail wires (seat variant). The umbilical pulls at the grip base; the pull is a slider.
- **Position:** the corner in the eye's image; no world reference. In the seat variant the seat also fixes the pivot near the dot.
- **Restrained:** in the lug variant, three translations by the elastic and the rotation by whatever the stage base is (none, or a stiffness you choose). In the seat variant, all six by the seat and the bridle.
- **Free:** the tangent in both (nearly free for the seam: s²/2r, and the scene shows the cost); the roll about the barrel; the beam turn where nothing holds it.
- **Driven:** the trim (r, z); the tail winches (seat variant) by hand in the scene.

## What software could command, observe, and what stays manual

- **Command:** trim r and z (±6 mm as eyes-01); tail winches; the line laser.
- **Observe:** corner minus dot, radial and vertical (the eye); in the seat variant a load cell under the cup; an IMU on the shell for pitch and roll (eyes-11, not in the scene). Not observed by anything here: the vertical-axis turn, the incidence angle change, the support's own drift.
- **Manual:** setting the gun at the setup pull; fitting collar, cup, spreader; routing the cable.

## What was tried to break it

**Entry 1. One elastic holds no rotation.**
- Conflict: eyes-01's drift is a translation of the gun. A line to a lug is a ball joint; gravity's restoring stiffness at the housing top is 0.42 N·m/rad against 0.29 N·m from 2 N of pull on a 144 mm lever, so tilt of order 39° (calc/25). In the statics (pivot 70 mm above the lug, elastic 0.5 N/mm, 2 N) the gun settles 29° from the hand-set pose and one more newton moves the dot 1.4 / 4.2 mm (r / z), turns the beam 1.3°; ±6 mm of trim is used up by 1.4 N (elastic 0.2 to 10 N/mm: 1.0 to 1.8 N).
- Assumption: that a support can be soft without saying which of the six motions it restrains.
- Change: hold rotation by the stage base (100 N·m/rad: 0.45 / 1.0 mm per newton, beam 0.02°, 5.8 N fills the trim), or use the seat.
- Leaves uncertain: the real pull, mass and centre of mass; the elastic's real stiffness (a single line has only T/L sideways).

**Entry 2. The drawn elastic cannot carry the weight.**
- Conflict: in eyes-01's drawing the elastic runs about 13° above horizontal (30 mm rise over 132 mm in plan); it carries 11.8 N only at about 53 N tension.
- Change: hang it vertically (the scene does). Nothing else changes.
- Leaves uncertain: where a real overhead support goes over a tube and an operator.

**Entry 3. The cup and the camera want the same barrel.**
- Conflict: with the seat's collar 70 mm behind the tip, stations 70 to 130 mm at clock 0 and the +side are blocked by the cone (34 of 66 stations clear, against 47 of 66 with a rigid lug). At the default camera (85 mm, clock 0) the scene reports *corner not visible: blocked by cone seat* and the same for the line laser.
- Assumption: that the camera can go anywhere on the barrel between 30 and 130 mm (eyes-01's note 1).
- Change: put the camera ahead of the collar (30 to 55 mm, closest to the spatter), or open the cup's ring on the camera side. The drawn rod from the cup to the nose stage also blocks the laser at 50 mm; route it.
- Leaves uncertain: the real cup size (collar radius 12 mm here; at stations above 100 mm the sleeve is 15 mm in radius and needs a bigger collar), and spatter at 30 to 55 mm.

**Entry 4. Friction steps.**
- Conflict: eyes-01 sizes the loop by drift rate (0.1 mm/s). A seat or rail slips in steps; at gain 0.6 and 4 corrections a second a 3 mm step takes 4 corrections to get under 0.1 mm (1 s, 8 mm of bead at 8 mm/s).
- Change: the slider shows the count; a stiffer, rolling, or preloaded support shrinks the step.
- Leaves uncertain: the size of a real slip.

## Branches and combinations

- The **tilt loop** of the seat variant wants an observer: eyes-11's IMU (pitch and roll from gravity) or the line laser's slopes (question in the exchange). The vertical-axis turn is left unobserved by both.
- The **force term** of `freedom-13-map-and-step` reads pull change at the seat's load cell.
- **eyes-02's dome** with the support's own parts as occluders is the camera map here.

## Unresolved problems, and questions that need Derek's observation

- The umbilical's pull at the exit at the working pose (spring scale), the gun's mass and where it balances (thread at two points).
- Whether a cup and camera fit together on a printed shell; try it in print.
- Whether the beam's turn of a degree or two matters to the weld (incidence and the wire approach): nobody has measured what the weld needs.

## Assumptions

- Gun and shell 1.2 kg, COM (0, −18, 178) local, elastic k 0.2 to 10 N/mm, rotation stiffness 0 to 100 N·m/rad, seat 100 N/mm, tail wires 200 N/mm, yaw bungees 0.15 N/mm, trim ±6 mm, loop gain 0.6 at 4 Hz, camera stalk 27 to 30 mm: **illustrative**.
- The eye is exact in the scene (no bias, no noise): those are eyes-01's.
- Line of sight is drawn geometry, not optics.

## Sourcing pointers

`sourcing/freedom.md`: load cell and HX711 (seat load), 1 inch steel balls (the collar), the Newton force meter (Derek's pull measurement).

## Scene

`freedom-11-eye-on-the-seat`.

**Wave 3 note.** borrowed made no remark on this scene. freedom-16 adds a reading to entry 3 of freedom-15 that this scene's pull slider stands in for: the pull at the grip base is a wrench (force, couple, lever) and its line matters more than its size for a support with weak rotation.
