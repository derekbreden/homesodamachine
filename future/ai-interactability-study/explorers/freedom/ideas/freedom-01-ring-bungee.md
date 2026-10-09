# freedom-01: ring-and-bungee suspension (Derek's original), worked through

Scene: `scenes/freedom-01-ring-bungee`. Origin: Derek's example. Depth: worked deeply (eight break-and-repair rounds, two branch scenes). Numbers below come from `calc/statics.js` + `calc/ringmodel.js` and the scripts named in each entry; every mass, stiffness and force is **illustrative** unless tagged.

## Picture it

The gun sits in a printed shell. One openable loop closes round the barrel near the nozzle, another round the cable pair just past the grip base. Each loop hangs from a wire going straight up and is pulled sideways by a pair of bungees along X or Y. An arm takes hold of the shell at some point along its length. The picture to hold is not "a gun on rubber bands" but "six things each pushing on one direction of one body": which of them wins on which direction is the whole idea.

## The proposal

Derek's text [Derek]: hooks as complete openable loops, one hung from a wire "to be held in Z" and stretched by bungees "in either the X or Y axis, so just two bungees, holding one axis steadyish", one loop at the tip and one around the base (umbilical and wire feed), a shell gripped by the arm "anywhere we like", and a third ring "a number of places" that reduces range of motion (or raises the force needed) while reducing weight further. The scene keeps all of that and adds what each contact allows: **smooth loop** (restrains across its axis only), **rubber loop** (friction holds axial load up to a limit), **seated collar** (a shoulder on the shell rests on the loop), and for the base loop a shell sleeve versus the bare cable. The arm can grip nothing, one point (ball end), or clamp the shell (rigid), at any of five stations.

## What carries the loads, what establishes position, what is free or restrained

- **Weight**: the wires (Z) through the loops, if the loops can transmit it. A loop can only push perpendicular to its axis; on an inclined barrel the wire's axial component needs a seat or friction to push against (round 1).
- **Umbilical pull and trigger**: shared between the base loop (if it picks up the cable), the bungees and the arm.
- **Position**: not the suspension. Position is set by whichever element is stiffest on each axis, and in the arrangements that work that is the arm (round 2, round 3). The suspension sheds load and tames the cable.
- **Free**: sliding along a smooth loop; rolling about the barrel; the roll about the line between the two loops (the "hinge"); sway along any axis a bungee does not hold (a pendulum with stiffness load / wire length).
- **Restrained**: two lateral directions at each loop; the axial direction at a seated collar; the bungee axis, softly.
- **Driven**: arm end X, Y, Z (three stepper or servo axes), optionally winches on the vertical supports.
- **Changes over time**: loops are opened for each tube; setup is with the loops loose, weld with the arm holding; a lock on the loop contact is possible but does not stiffen the suspension (round 4).

## What software could command, observe, and what stays manual

- **Command**: arm end X, Y, Z; vertical-support tension (winch on each wire, or the preload of a balancer); optionally which loops are engaged.
- **Observe**: the force in the arm end (a load cell or motor current) is the natural sensor: it says how much the arm is carrying; wire tension (inline load cell); the dot against the seam by camera. The scene includes an **auto-null** loop: software reads the arm force and adjusts the vertical supports until the arm carries as little as it can. That loop works with soft supports (arm force 3.6 → 1.65 N with a balancer-class support; the remainder is the umbilical's horizontal pull) and does not with a stiff wire (round 2).
- **Manual or unresolved**: hanging and opening the loops; where the shell is gripped; cable routing; the fibre's twist tolerance; whether a loop can be opened and closed by software.

## What was tried to break it

**Round 1. Smooth loop, inclined barrel: it slides.**
- Conflict: with a smooth tip loop, a wire in Z and no arm there is no static equilibrium; with an arm holding the shell the loop rides up the barrel by 3 mm and the wires go slack, so the arm carries 12.0 N of the 11.8 N weight (`calc/09-slide.cjs`, `06-tables.cjs`).
- Assumption behind it: that a hook around the barrel stops the barrel moving through it. A loop restrains only across its axis.
- Change: a **seated collar** (a shoulder on the shell resting on the loop) puts the wire's share at 7.7 N and the arm at 4.7 N; a **rubber loop** with a 4 N axial friction limit gives arm 6.7 N, a 1 N limit gives 10.7 N, 8 N gives 5.1 N (`calc/10-rubber.cjs`). Derek's "rubber coated hook" is this contact.
- Leaves uncertain: the real friction limit (unknown), whether friction is stick-slip, whether a seat is compatible with opening the loop for tube swaps.

**Round 2. One master per axis: the stiff wire is a position, not a force.**
- Conflict: with a 200 N/mm wire and a 5 N/mm arm both restraining Z, a 1 mm arm Z command moves the dot **−0.04 mm**; the wire is the master and the arm only carries the mismatch. With a long bungee (0.2 N/mm) it moves 0.93 mm; with a constant-force balancer (0.02 N/mm) 0.99 mm (`calc/06-tables.cjs`). The auto-null loop asks the stiff wire for 204 N to zero the arm force: a 0.05 mm length change is 10 N, so tension cannot be controlled through length (`calc/05-null.cjs`).
- Assumption: that a wire "holds Z" and the arm can still move Z.
- Change: either assign Z to the wires (they become a Z-and-pitch axis with winches; the arm's Z is redundant), or make the vertical support a force element (long bungee, constant-force balancer) so the arm owns Z. The scene's vertical-support radio shows both.
- Leaves uncertain: the winch precision required if the wires own Z; the real stroke and constancy of a balancer.

**Round 3. The rings alone do not locate.**
- Conflict: with the seat contact, a loop base and no arm, the dot moves 44 / 33 / 0.85 mm per newton (radial / tangent / vertical); with the base loop on the bare cable 23 / 27 / 21 mm/N. A rigid arm alone gives 0.3 to 0.9 mm/N (`calc/06-tables.cjs`). One newton of umbilical pull moves the dot 40 mm if only the bungees and wires hold it.
- Assumption: that "two bungees, holding one axis steadyish" gives position. They give a soft spring on one axis and a pendulum on the others.
- Change: the suspension's job is to shed weight and shape the cable force; the arm locates. That was Derek's own stated purpose for the third ring ("reduce weight further").
- Leaves uncertain: whether the same relief is worth the complexity against a balancer at the arm alone (scene freedom-02).

**Round 4. The two loops define a hinge, and gravity drives it.**
- Conflict: a tip loop and a loop on the cable pair define a line very close to the reference scene's grip axis. The gun swings freely about it. With the illustrative COM 35 to 61 mm off that line depending on where the tip loop sits, gravity wants the COM under the line: about **131° of roll away from the reference roll**; at the reference roll it puts about 0.5 N·m on the hinge (W × 55 mm × sin 131°) that the arm has to hold (`calc/08-hinge-torque.cjs`).
- Assumption: that the roll about the grip axis is a free, harmless adjustment. It is free, and gravity spins it.
- Change: (a) the arm grips off the line with a long lever (a 100 mm lever turns that torque into 5 N); (b) a counterweight that puts the COM on the line: 0.73 kg at 90 mm off the line, a large fraction of the gun's own mass (`calc/07-hinge.cjs`); (c) use the hinge deliberately (freedom-08).
- Leaves uncertain: the real COM (unknown), which decides whether (b) is 0.3 kg or 1 kg.

**Round 5. The base loop is a cable problem.**
- Conflict: a loop on the bare cable 120 mm past the grip base drags the cable through a tighter bend: the scene's illustrative check gives a minimum bend radius of 149 mm against the manual's 240 mm stored / 350 mm emitting [manual p. 20]. The plain route from the cable exit to the floor already sits at about 315 mm.
- Assumption: the base loop is free to sit anywhere.
- Change: the loop belongs near the natural line of the cable from the exit; at 150 mm out the lateral offset allowed by a 350 mm radius is about ℓ²/2R = 32 mm [derived].
- Leaves uncertain: the real cable's stiffness and weight (unknown), and twist: the grip-axis roll is a rotation about the cable's own exit axis, which is a twist input to a fibre the manual says must not be twisted. Whether the route turns it into twist or into a swing of the bend plane is unknown.

**Round 6. Bungees stiffer than the arm become the master.**
- Conflict: raising bungee stiffness from 0.05 to 3 N/mm cuts the arm's tangent gain from 0.96 to 0.24 and the radial gain from 0.98 to 0.92 (`calc/06-tables.cjs`).
- Assumption: bungee stiffness is a free choice.
- Change: keep the bungees an order softer than the arm (arm 5 N/mm here), or accept them as the master and drive the anchor.
- Leaves uncertain: real bungee stiffness and hysteresis.

**Round 7. How the arm grips changes everything.**
- Conflict: a ball-ended grip leaves the orientation to the soft supports: gains 0.4 to 3.4 with cross-coupling (Y command moves the radial 3.35 at the handle middle) and dot compliance 1 to 120 mm/N. A rigid clamp gives gain about 0.93 to 0.99 and compliance 0.3 to 0.9 mm/N wherever it grips: barrel 0.32 / 0.29 / 0.04, housing top 0.47 / 0.44 / 0.04, handle base 0.90 / 0.29 / 0.04 (`calc/03-gain.cjs`).
- Assumption: gripping is a detail. It is the choice that decides whether the suspension matters.
- Change: with a rigid grip the rings do not change the gain or compliance; they change how much the arm carries. Only a ball-ended grip makes the suspension the locator, and then it is a poor one.

**Round 8. Derek's third ring: less range, less weight on the arm.**
- Conflict/opportunity: Derek [Derek] expected a third ring to reduce the range of motion (or raise the force needed to use it) and to reduce weight further. In the model (`calc/28-third-ring.cjs`, a rubber loop on the housing, illustrative) both come out, with a caveat. With a rigid grip at the housing top the arm carries 3.0 N instead of 5.0 N and nothing else changes (compliance 0.46 vs 0.47 mm/N). With a ball-ended grip at the housing back the arm carries 4.0 N instead of 7.3 N, and the third ring's bungee direction shapes the range: bungees along X (radial) cut the arm's radial gain from 0.92 to 0.43; along Y (tangent) they cut the tangent gain from about 0 to −0.24. Firm third-ring bungees (0.6 N/mm) drop the dot compliance under a ball-ended grip from 7.7 / 4.5 to 3.2 / 1.2 mm/N.
- Assumption: a third ring only adds capacity. It also adds a master on whatever axis its bungees hold, and it is one more thing to open for each tube.
- Change: use the third ring for weight relief with soft bungees (arm load down, gain unchanged), or for range limiting with firm bungees on the axis to be restrained.
- Leaves uncertain: how the third loop coexists with the shell, the cable and the arm's own grip on the same housing.

**Round 9 (wave 3, from borrowed's exchange, "smaller remarks": three bought forms and one branch). Decision: answered, with two questions added.**
- Conflict: (a) round 1's friction limit of the rubber-coated loop (1, 4, 8 N, a slider) is an unknown; (b) the "wire held in Z" that round 2 said must be a force element, and the bungee that holds an axis, are unspecified parts; (c) round 4's hinge (two loops define a line, gravity spins the gun about it) is repaired by a counterweight that only nulls the torque.
- Assumption: the friction is a guess; the Z support is an ideal force; the hinge needs a counterweight.
- Change: (a) the openable rubber-coated loop has a bought form, a rubber-cushioned P-clamp (2 inch, 20 pack, $17.99, 6,185 ratings, "100+ bought", Prime; smaller sizes for a 25 to 30 mm sleeve) whose friction limit is set by the screw: pull the sleeve through it with the Newton meter and the slider has a number. (b) The Z support is a spring balancer's cable (a constant force, sourcing/freedom.md); two balancers opposing in X and Y are a zero-stiffness horizontal support where friction is the only stiffness, and Derek's bungee is one of them with a restoring force; a bungee's stiffness is EA/L, so its length is the stiffness knob. (c) The hinge is a sled: the keel of borrowed-15 supplies the spring and defines the equilibrium at the working roll, where the counterweight only nulls the torque; `freedom-17-hung-on-the-line` draws it in the kit's geometry and finds that gravity cannot hold against a cable that lets go far from the pivot. The roll about the grip axis, which this file only flagged as a twist risk, has its own lens now (`freedom-18-roll-into-twist`): in the kit the exit tangent is 30 degrees off the roll axis, so a roll is part twist, part swing.
- Leaves uncertain: the P-clamp's friction limit on a printed sleeve; whether two opposing balancers stay soft in the presence of the cable pull.

## Branches and combinations

- `freedom-01b-nose-seat`: a spherical collar in a cone near the nozzle; the pivot moves next to the dot.
- `freedom-01c-master-per-axis`: bungee as preload with a hard stop; series-elastic anchor.
- `freedom-02-balanced-arm`: the weight path becomes a gas-spring arm; the loops are not needed.
- `freedom-03-cable-platform`: six lines instead of two loops; the same statics with the arm removed.
- `freedom-06-lock-and-release`: lock the contact by state.

## Unresolved problems, and questions that need Derek's observation

- Gun mass and where it balances: hang the gun from a thread at two points and mark the vertical lines. This decides every gravity number here.
- What the umbilical actually does at the exit: pull with a spring scale at the exit in the working pose, then again with the cable in its intended route.
- The friction of a rubber-coated hook on a printed sleeve (pull the sleeve through it with a scale): the bought form is a rubber-cushioned P-clamp whose limit the screw sets (round 9); borrowed asked the same question.
- How much roll about the cable exit axis the cable tolerates in practice.
- Whether a loop can be made to slide freely when wanted and hold when wanted.

## Assumptions

- Gun and shell 1.2 kg, COM (0, −18, 178) local: **illustrative**; gun mass and COM **[unknown]**.
- Kit gun proxy and opening pose (roll 45, hole dial 30, vertical −15): **illustrative** [repo scene]; the barrel is inclined about 45° there [derived].
- Bungee 0.05 / 0.15 / 0.6 N/mm, wire 200 N/mm, loop fit 50 N/mm, arm 5 N/mm (rigid grip 100 N·m/rad): **illustrative**.
- Cable bend radius limits 240 mm stored, 350 mm emitting; twisting forbidden: **[manual]** p. 20.
- The tube and joint: **[repo]** `pressure-vessel.md`.

## Sourcing pointers

`sourcing/freedom.md`: bungee cord roll, UHMWPE braided cord, spring balancers 0.5 to 1.5 kg (Tigon TW-1R, MECCANIXITY, QWORK), load cell with HX711.

## Scene

`freedom-01-ring-bungee`. Rough physics, honest scope: statics of one rigid body with springs, wires that only pull, ring pins, a seat, a friction-limited slide, point pins and a rigid grip. No friction hysteresis, creep, vibration or flexible shell.
