# datum-16-loops-carry-rim-locates: Derek's loops carry from the room, the arm's base rides the rim

Scene: `scenes/datum-16-loops-carry-rim-locates/index.html`. Depth: developed. Origin: branch of `freedom-01-ring-bungee` (Derek's suspension example), combined with `datum-03-rim-crown`; it is also the crown-side half of the `trials-16` / `trials-04b` combination named in the exchange. Exchange: `exchange/datum--on--trials-w2.md` section 5 and the examples paragraph.

## Picture it

Two openable loops on the gun, one round the barrel and one round the cable pair, hang by wires from an overhead gallows. The loops take a chosen share of the gun's weight. The shell is held by a short boom that stands not on a post on the bench but on a crown: two rings on the tube's rim, the lower turning with the tube and the upper not. Turn the rotator and the tube wobbles, the crown wobbles with it, the wires stay where they are and tilt by a hundredth of a degree, and the dot stays on the seam. Switch the boom to a post on the bench and the tube wobbles under a still gun.

## The proposal

Derek's rings and bungees do one job well: they take the gun's weight and let the cable pull it around. The arm that grips the shell has to know where the corner is. Ask where the arm's *base* stands. On the room, the tube's wobble arrives as a motion the arm chases. On the tube, it never arrives: the runout of 0.125 mm radial and 0.15 mm face at the station is followed for free.

Splitting the two paths puts each load where it is cheap. **Weight** goes to the room through soft, long wires and a balancer: no reference needed. **Location** goes to the rim: the crown carries only what the loops do not, and has to be stiff on the radial and vertical axes and free on the tangent (turning the whole upper assembly about the tube axis does not change gun-to-corner pose).

## What carries the loads, what establishes position, what is free or restrained

- **Wires and loops** (from the gallows): the loops' share of the weight (default 85 per cent), through the tip loop and the cable-pair loop. **Rim, through the crown:** the crown, the boom, the counterweight, and the rest of the gun's weight; plus the cable's horizontal pull, which acts high above the rim.
- **Position:** the rim (height), the outside of the tube (radial), a plunger on the plate face at the station; the loops locate nothing. Seat depth and the plate's tilt against the rim stay in the vertical offset unless trimmed.
- **Free:** the tangent; the roll about the tube axis. **Restrained:** radial and vertical, by the boom. **Driven:** the rotator; an optional crown stage; an optional wire tension.

## What software could command, observe, and what stays manual

- **Command:** the rotator; a crown vertical stage (proposed); the wires' tension or balancer preload and their split (proposed).
- **Observe:** the plunger; an inline cell in each wire (the split and the total); a contact on one crown pad. A change in the two wire tensions when nothing else changed is the cable's pull changing, before the dot moves.
- **Manual:** opening and closing the loops for each tube; setting the loops' share; seating the crown; the boom's roll, pitch and reach.

## What was tried to break it

Numbers are from the scene's statics (illustrative masses: gun and shell 1.15 kg, crown 0.45 kg; cable exit 0.13 m above the rim in the proxy pose) and `freedom-01`'s stiffness set.

1. **The crown's counterweight need moves, it does not vanish.** *Assumption in `datum-03` round 3:* the crown carries the gun. With no loops, the crown's load acts 67 mm from the axis, at the edge of what a ring on the rim supports (66 mm), and about 0.8 kg of counterweight keeps contact all round. With 85 per cent in the wires and their split set for the weights, the load acts 22 mm out and no counterweight is needed: the split moves the weight's moment to the loops. The cable's pull is not moved: 1.5 N at 0.13 m is 0.2 N m; at 6 N the load is 88 mm off and the crown tips. Remedies: a heavier crown (1.1 kg), a festoon that keeps the pull off the gun (`borrowed-11`), or a split retuned for the pull by software reading the two wire tensions (the scene's "also for the pull" branch: zero moment). *Correction to `datum-03`:* the "as heavy as the gun" figure centres the assembly on the axis; stopping a tip needs about 0.23 kg and keeping contact all round about 0.7 (illustrative).
2. **A stiff vertical support fights the rim.** *Assumption:* a wire holds Z. A support anchored in the room and attached to a gun that rides the rim pulls with stiffness times the face wobble: 0.003 N for a 0.02 N/mm balancer, 0.03 N for a 0.2 N/mm long bungee, 6 N for a 40 N/mm braided line, 30 N for a 200 N/mm wire against 7.4 N of crown. The wire lifts the crown off the rim and the gun stops following. The vertical and radial supports must be forces (`freedom-01` round 2, from the other end).
3. **The cable's pull moves the dot as well.** 1.5 N against 0.3 mm/N of boom compliance (`freedom-01`: 0.3 to 0.9 for a rigid grip) is 0.45 mm radial, a constant, not a wobble; a radial trim removes it. It is set from a touch or a dot sweep (`datum-07`, `trials-03`).
4. **The rim is not the plate.** Seat depth is a constant and the plate's tilt against the rim a first harmonic (0.10 mm at the station, illustrative). *Seat trim* compares nobody, a crown stage servoed to the plunger (follows both), and a lift under the tube set from a touch (the constant only: the tilt stays). That last is the combination with `trials-16`: the tube-side stage does the slow part, the crown the fast part. It also answers `trials-16`'s difficulty from the other side: a gun on a *soft* passive support wanders tens of millimetres per newton of cable pull (`freedom-01`: 40 mm/N with bungees and wires only), far outside a tube-side follower's stroke; the passive support has to be stiff on two axes, and a crown is one.
5. **Left standing:** three supports on one printed shell (two soft loops and a lug) without over-constraining it; the loops' lateral stiffness, which adds to the pull the crown sees; whether a balancer of the 0.5 to 1.5 kg class carries this share with the constancy assumed (`sourcing/freedom.md`); ball retention, heat and plunger placement as in `datum-03`.

### Wave 3 note

The crown's radial seat is drawn ideal here (the ring exactly on the outside's centre). `datum-03` now draws it (clearance ring, three pads, six pads or rockers, wall shape) and `datum-21` shows what a ring on the whole circle can and cannot follow: motion, not shape. The weight-from-above half of this idea has a second home at the wall (`datum-23-wall-clip`: a balancer wire carries, a hook on the wall at the station locates), and the plate's depth and tilt can be made by construction (`datum-22-setting-ring`) instead of by the plunger and stage.

## Branches and combinations

- Branch of `freedom-01-ring-bungee` (the anchors of the arm, not of the loops, move to the work). Uses `datum-03`. Relates to `freedom-02` (weight path versus location path), `freedom-15-pull-ledger`, `borrowed-11` (balancer plus festoon), `travel-13` (print to adjust: a shim under the lift), `trials-16` and `trials-04b`.

## Unresolved problems and questions for Derek

- Gun mass and centre of mass; the umbilical's pull at the exit in the working pose (a spring scale at the exit); whether a crown may sit on the rim of a finished tube; how the two loops open for each tube.

## Assumptions

Masses, pull, boom compliance, the 66 mm support radius and the 33 / 66 mm contact limits: illustrative. Runout amplitudes from the rig limits `[repo]`. Statics only: no dynamics, no friction, no wire or bungee mechanics.

## Sourcing pointers

`sourcing/freedom.md`: spring balancers (0.5 to 1.5 kg), bungee cord, load cell with HX711. `sourcing/datum.md`: 6 in lazy Susan (unchecked fit) for the crown's bearing.

## Scene id

`datum-16-loops-carry-rim-locates`.
