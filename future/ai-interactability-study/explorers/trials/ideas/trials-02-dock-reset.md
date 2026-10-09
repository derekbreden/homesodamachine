# trials-02-dock-reset: the dock is the gun's home between trials

Scene: `scenes/trials-02-dock-reset/index.html` (developed). Calc: `explorers/trials/calc/dock_scale.py`. Sourcing: `sourcing/trials.md` (load cells, HX711).

## Picture it

After every trial the gun-in-shell goes back to a cradle beside the rotator. The shell rests on three seats; a switch says it is seated; three load cells under the seats weigh the gun and the way the umbilical is pulling on it. Only then can the tube be swapped, because the gun stands outside the tube's lift column, locked. The next trial departs from the same physical pose it always did.

## The proposal

A dock with a ramp plate parallel to the shell's axis (so the gun parks in the attitude it works in and the positioner needs no re-orientation), three kinematic seats on the ramp, a contact switch, and a load cell under each seat. It does four jobs, and any one of them is a reason to have it:

1. **Re-anchoring the shell.** Missed steps, backlash, hysteresis in a compliant support, drift in whatever carries the gun: all discarded when the shell drops into the seats. Every trial starts the shell from a physical pose, not a remembered coordinate (the corner is found by the probe on each tube: item 7 below).
2. **Clearing the swap.** A tube (or puck, trials-01) leaves vertically. The gun's body must be outside that column and not able to move: the swap interlock.
3. **Weighing.** The three cell readings give total weight and how it is shared. A sideways umbilical pull cannot change the total but does change the shares (about 45 to 90 g per newton on the most affected cells, for a pull 100 mm above the seats in the placeholder geometry, `dock_scale.py`); a single scale cannot see it, three cells can. The first dock visit sets a baseline; later visits are compared with it. A dragging cable shows up here before it shows up as a strange trial.
4. **A repeatable start for the final approach.** If the corner is always approached from the same direction, friction and backlash add the same offset each time (a constant that can be calibrated); from both sides they split the landing positions in two (last panel of the scene).

## What carries the loads, what establishes position, what stays free

- The cradle carries the shell and part of the umbilical's weight when parked; the cells are between the seats and the base. At the corner the dock carries nothing; whichever arrangement positions the gun carries it.
- Position: three kinematic seats, one per lug on the shell; the seated contact certifies it. The dock re-creates a pose; it does not measure the positioner.
- Free/restrained: docked = fully restrained; departing = the first motion is along the seat normal, then up; the rest is unspecified.

## What software could command, observe, and what stays manual

- Command: the positioner's path dock, hover, corner (whatever it is); the swap interlock; rotator speed.
- Observe: the seated contact; three cell readings versus the baseline; and after the swap the new tube's ID and seat.
- Manual: the swap (or the tool that does it, trials-07), re-exercising a dragging umbilical.

## Tried to break it

1. **The gun body stands in the lift column.** Conflict: at the swap step the gun's body (projected 134 mm over the bore at the working pose) would block the lift. Assumption: the tube lifts straight up. Change: the dock stands 330 mm from the axis in the scene; move it to 150 mm and the scene shows a LIMIT badge (gun body or ramp in the column). What it costs: about 270 mm of positioner travel every cycle and umbilical slack. Leaves: not every positioner has that reach; in a table-with-side-opening arrangement the tube leaves sideways and the dock can be near.
2. **The umbilical drags differently each time.** Conflict: reproducibility of a trial rests on the cable. Assumption: the drag is visible at the dock. Change: the weigh-in. Leaves: a threshold separating harmless from harmful is **[unknown]**; 10 g is a placeholder; the real pull per pose is unknown.
3. **Kinematic seats on soft cells.** Conflict: a bar cell deflects, softening the seat. Repair not drawn: a hard seat above the cells that takes the shell over the last millimetre and a soft weigh mode (the cells carry the weight only in the weigh state). Leaves: whether a hobby bar cell under a ball stays repeatable; not tested.
4. **Hysteresis from both sides.** Assumption: friction in a compliant support (rings and bungees, Derek's suspension example) is symmetric and repeatable. Change: unidirectional final approach turns the scatter into a constant. Leaves: whether friction hysteresis is in fact repeatable; creep in bungees is not, and drifts across hours.
5. **No index for the tube after the swap.** The rotator counts turned-so-far degrees only **[repo]**. The dock does not fix that; the puck's magnet and Hall sensor (trials-01) or a camera on the plate register hole does.
6. **A dock is not the cheapest home.** A limit switch homes a positioner. The dock adds the weigh-in, the swap interlock and unloading the positioner between trials. Whether that is worth a dock is a judgement; this idea says which benefits the extra part buys.

7. **The dock's coordinates are not what the trial rests on (from datum's exchange, wave 2, section 2).** *Conflict, in this variant:* the dock's first job ("every trial starts from a physical pose, not a remembered coordinate") is true of the shell against the bench. The pose that decides a trial is dot to corner on this tube, and the chain from the dock to the corner has links the dock does not touch: the bench clamp (four Ø10 holes **[repo]**), the positioner's scale over the 330 mm, the seat depth, the dot in the shell, the camera. A 1 mm re-clamp, or 0.1 per cent over 330 mm (0.33 mm), reaches the dot unless a probe on the tube absorbs it, and step 3 finds the corner with the dot probe. *Assumption behind it:* that re-anchoring the shell re-anchors the trial. *Change:* the idea is restated: the dock re-anchors the shell and weighs the cable; the corner is probed on every tube. What only the dock notices is force. *Adopted from `datum-15-dock-noticing`:* a coupon under the docked dot (a toggle in the scene): a shift that shows on the coupon is in the gun or the camera, one that shows only on the tube is outside them. *Leaves uncertain:* one shift in one number cannot say whether the dot or the camera moved; how the dot probe runs at the dock without lifting the shell off its seats; the probe's last approach on the coupon and on the tube must come from the same direction (the one-sided approach here).
8. **Real 316L or printed for the coupon (datum's question, section 2).** Both, as a pair: a printed matte corner and a real steel one under the same dot read the same geometry through two surfaces; the difference of their knees, after a constant subtracted at install, is what the surface does to the judge, and a change in it is a change detector for the lighting and the camera's threshold. A steel coupon's mass and heat do not matter in a dry run (it is cold and off the load cells). *Better still:* put the coupon on a **puck on the rotator** (`trials-22-reference-pucks`): read at the trial's own station it also sees the bench clamp and the positioner's scale, which the dock coupon cannot; the dock coupon then covers the shell and camera alone. *Left standing:* a coupon of real steel and a printed one are not the same corner to a few tens of micrometres until measured.
9. **A dock on a bracket from the rotator's own base (datum's second, smaller branch).** It takes the bench clamp out of the chain, and stands within about 200 mm of the axis, inside this scene's lift column (the LIMIT badge fires at 150 mm). It needs a tube that leaves sideways or down (`room-01`, `room-05`) or a dock that swings clear. Left standing, not drawn.

## Branches and combinations

- Combines with `trials-01-puck-swap` and `trials-07-toolchange-swap` (three docks are three known points: a gantry could fit scale and skew from them).
- **Wave 3:** `datum-15-dock-noticing` (the dock as a control specimen: a coupon under the docked dot and six injected changes) is a branch of this idea; the scene here has its coupon as a toggle and the claim about what the dock rests on corrected (item 7). `trials-22-reference-pucks` puts the coupon on a puck at the trial's own station.
- Transferable: weigh-in as reset check (any suspended or cable-loaded arrangement); unidirectional final approach; swap interlock.
- `trials-15-one-tube-many-poses` is the policy that makes the dock cycle cheap: many trials per load.

- **Wave 2, borrowed from `use-02-swing-head`:** two pieces. (1) The **float that hands over the load**: the carrier keeps pressing through a spring while the seat takes the weight and the arm lets go. It answers item 3 above (kinematic seats on soft cells): a hard seat takes the shell over the last millimetre and a float releases the positioner's load, so the cells sit under the seat and see only the shell and its umbilical share. (2) The **seat amplification**: use-02's calc gives a contact error amplified about 5 times at a 30 mm contact circle and a dot about 130 mm from the seat centre (about 3 times at 60 mm), so a dock's repeatability *at the dot* is five times its contact repeatability; a dock's seat circle should be drawn as wide as the ramp allows. Neither is drawn in the dock scene yet.
- **Wave 2, from `trials-19-fixed-point-cal`:** the dock is the cheap zero check for an encoded arm or a gimbal: return to the seat, read the joint angles, and a shift of the zeros shows without a board.

## Unresolved, and questions for Derek

- Q: What does the X1 Pro weigh (kitchen scale), and where is its centre of gravity (hang it from two points)? The scene's 1.5 kg is a placeholder.
- Q: Which way does the umbilical pull at each working pose, and how hard? A 5 m fibre with a 240 to 350 mm minimum bend radius **[manual p.20]** is not a light thing.
- The dock's height and the ramp attitude depend on the arrangement that positions the gun.

## Assumptions

Tube, recess, rim, wall **[repo]**; 32° beam, 16 mm to the dot, gun profile **[illustrative]** from the reference scene; 253 x 143 x 34 mm envelope **[manual p.17]**; dock position, ramp, seat triangle, tube lift, mass, thresholds **[illustrative]**; cell shares from a static solve (`dock_scale.py`).
