# freedom-16: where the fibre lets go of the gun (a boot takes the bend, a straight span leaves on the line through the dot)

Scene: `scenes/freedom-16-fibre-line`. Origin: swarm (wave 3, the new direction "the umbilical and the wire conduit as the design driver"; extends `freedom-15-pull-ledger`, which had no scene). Depth: deep (eight break-and-repair entries, a solver of its own, four routes drawn and compared). Numbers from `calc/cable-rod.js` (a planar elastica, checked against the circular arc and a moment balance), `calc/fibre-line.js` (the kit's gun frame, the routes, the wrench), `calc/33-fibre-routes.cjs` and `calc/36-defaults-freedom16.cjs`. Every stiffness, weight and force is **illustrative** unless tagged; the fibre's bending stiffness EI, weight per metre, torsion stiffness GJ and tension limit are **[unknown]**.

## Picture it

The gun at the reference pose, its grip base 279 mm from the dot on a dashed teal line that continues up and out (the roll axis, 30 degrees above horizontal). A printed tube on the shell tail, translucent amber, turns the fibre and the conduit onto that line in a shallow S; beyond it a straight span 400 mm long ends in a small green collar that hangs from a rail parallel to the span. A blue arrow at the boot exit is the force the cable puts on the gun; a red segment is how far the line of that force passes from the dot: zero for the S-boot. Flip the route radio to A and the boot, rail and collar go, and the fibre leaves along the grip's rake in one arc to a clip on a low post; the red segment is now 127 mm long.

## The proposal

Every scene in the study has one force it cannot get rid of: the cable's pull at the grip base. Stop asking what holds the gun against it. Ask where the fibre lets go of the last rigid part of the shell, because that is where its wrench enters the gun. A rigid boot printed onto the shell lets the shell take the fibre's bend (the recoil is then a load between fibre and boot), and a straight span leaving the boot on the roll axis puts a force along a line through the dot on the gun. A swivel collar riding a rail aligned with the span holds the fibre without a clamp at both ends, so slack and misplacement stop mattering, and makes the roll a rotation about the fibre's own axis.

Four routes are drawn and solved for the same fibre and conduit (bundled: EI 0.11 N·m², 2.5 N/m):

| route | how the fibre leaves | what holds it | release point from the dot |
|---|---|---|---|
| A | along the grip's rake, one designed arc | a clip clamped in the arc's direction, on a post | 279 mm |
| B | straight along the rake | swivel collar on a rail | 279 mm |
| C | a boot turns it parallel to the roll axis, 48 mm off it | swivel collar on a rail | 458 mm |
| D | an S-boot lands it on the roll axis | swivel collar on a rail | 709 mm |

## What carries the loads, what establishes position, what is free or restrained

- **Carries:** the shell carries the boot and the fibre's bend; the rail and post carry the collar and the span's weight share beyond the boot; the gun's own support (not drawn) carries the wrench that gets through.
- **Position of the dot:** not the cable. The scene converts a wrench into a dot shift with a plain support (translational stiffness, rotational stiffness, pivot distance) so the same route can be judged against a stiff and a soft holder.
- **Free:** the collar along the rail and about it (a ball-bearing swivel); the fibre's twist beyond the swivel.
- **Restrained:** the fibre's exit tangent and position by the boot (route C, D) or by the grip base (A, B); the collar's position on the line by the rail (B, C, D) or the fibre's end by the clip (A).
- **Driven:** the roll (a motor, in the automated vision); the aim of the pulley end of the rail (two small axes that carry only a pulley).
- **Changes between states:** at setup the roll is set and the fibre laid untwisted; the rail is aimed along the roll axis (a state); during the weld nothing on the route moves; at bead start the wire feed pushes on the conduit and the far anchor may give.

## What software could command, what it could observe, what stays manual

- **Command:** the roll motor; the two aim axes of the rail's pulley end (a pulley's weight only).
- **Observe:** tension along the line by a load cell in the rail cord; the fibre's turn relative to the gallows by an encoder (AS5600) on the collar; the start of wire feed from the laser unit's status (the timing of the push); the fibre's shape by a stripe and beads (eyes-11b).
- **Manual or unresolved:** printing and fitting the boot; threading the fibre and conduit; clamping the fibre in a cable sock; laying the fibre beyond the collar at 350 mm or more; hanging the rail.

## What was tried to break it

Every entry: the specific conflict in the specific variant, the assumption behind it, what the change alters, what it leaves uncertain. Entries 1 to 4 came out of `exchange/borrowed--on--freedom-w2.md` (section 4, "the ledger has a column missing, the couple", and section 2, "the fibre's direction is a routing choice nobody has made").

**Entry 1. A clamp at each end is delicate (route A).**
- Conflict: the designed arc (R 500 mm, 60 degrees, turning down) with the clip exactly where the arc ends leaves the fibre stress-free apart from a couple EI/R of 0.22 N·m and its weight: 1.0 N on the gun, tightest bend 491 mm. Move the clip 10 mm off the arc: 2.4 N and 300 mm. Turn it 5 degrees: 2.8 N. Add 20 mm of fibre: 5.6 N and 277 mm, because a clamped fibre with any slack is post-buckled at about 4π²EI/L². The bend limit is broken by the set-up before the force is.
- Assumption: the study's earlier estimate of the pull as EI/R² (0.4 to 4 N) is what the route puts on the gun. It is the floor for a route that is exactly right; a clamp-clamp route is a stiff spring in every misplacement.
- Change: put the far end on a rail with a sliding swivel collar (routes B to D): a pulley end 20 mm off the line changes the force by 0.05 N and the static torque by 57 N·mm, and slack does not exist because the collar slides to where the tension is.
- Leaves uncertain: the fibre's EI (the whole table scales with it); whether a real clip grips rotation and direction as the model's clamp does; friction of the collar on the rail.

**Entry 2. A boot moves the release point away from the dot.**
- Conflict: with the boot the bend is held at 350 mm inside the shell, and the gun keeps only the span's weight share (0.7 N) and a couple of 0.04 N·m. But the release point is 458 (C) or 709 mm (D) from the dot instead of 279, so a sideways force there acts on a longer lever and the span's weight share is a static torque of 0.3 to 0.4 N·m that the support must hold. The boot itself (0.09 g per mm of boot, 40 g for the S-boot) adds 175 N·mm about the dot.
- Assumption: "put the bend in the shell" is free. It is not: it trades a couple and a recoil for a lever.
- Change: the scene shows both sides. 5 mm of anchor movement changes the torque about the dot by 9, 11 and 14 N·mm in B, C and D against 14 for the exact clip: no difference. What the boot buys is tolerance (entry 1), the forces along the line (entry 3) and the roll (entry 5). The arc boot (C) has the shorter lever; a shorter span (150 mm) reduces the weight share.
- Leaves uncertain: the boot's real mass and stiffness (a printed 25 mm tube 0.44 m long, in three or four pieces); whether it clears the hand grip and the wire guide; whether the static torque is small next to the support's capacity (it is next to a rigid grip and not next to a plumb-bob: freedom-17).

**Entry 3. Forces along the line are free, forces across it are not, and the force part is never free.**
- Conflict: a 0.5 N push along the conduit (the wire feeder pushing the liner; 23 mm off the fibre) changes the torque about the dot by 71 N·mm in A and B, 26 in C, 11.5 in D. But the same 0.5 N moves the dot 1 mm through a 0.5 N/mm arm (0.11 mm through the seat, 4 to 18 mm through one elastic with gravity only), whatever the route: the line removes only the torque, not the force.
- Assumption: choosing the line of the pull decides the dot's shift. It decides the torque; the support decides the rest.
- Change: state the result by support. A support with a stiff rotation (the arm preset, the nose seat) makes every route's step a fraction of a millimetre; one with weak rotation makes every step millimetres. The route matters most where the support is softest in rotation.
- Leaves uncertain: the size of the push (nobody has jogged the wire with a dial gauge on the shell); the gas hose, which is not drawn.

**Entry 4. Tension is not what keeps the span straight.**
- Conflict: the first sketch pulled the span taut along the axis with a dead weight over a pulley (a constant-force line through the dot). With EI 0.1 N·m² the span sags 2.4 mm with no tension (12.7 mm at 0.02, 0.5 mm at 0.5), and the gravity sag tilts the pull's line at the boot exit by 4δ/L, moving it 100 mm or more from the dot unless the rail is aimed to compensate. A dead weight only adds a constant force and, through the weight share, a static torque.
- Assumption: a taut fibre is a straight fibre and a constant force is a benefit. Neither is needed.
- Change: the default rail force is zero (the collar just slides). The slider stays (0 to 5 N) as a way to make the axial force a number chosen instead of measured, at the price of a pull the fibre may not tolerate.
- Leaves uncertain: the fibre's tension limit (the manual is silent; an email to the maker is Derek's action, nothing here is sent).

**Entry 5. Roll is part twist, part swing, and only a boot on the axis makes it pure twist.**
- Conflict: the kit's exit tangent is 30.2 degrees off the roll axis (the stub leaves along the grip's rake). 10 degrees of roll is 8.6 degrees of twist and 5.0 degrees of swing of the exit direction. The torque change about the dot is about 90 N·mm for the clip, 120 for the straight span along the rake (the rail's aim stays where it was), 15 for the arc boot and zero for the S-boot with a swivel collar.
- Assumption: the fibre leaves the grip along the roll axis (freedom-15 entry 1 said so); the study's own scene (freedom-01) called the roll "a rotation about the cable's own exit axis". The kit does not draw it that way.
- Change: `freedom-18-roll-into-twist` draws the cone and the twist budget. The twist is not removed by a swivel, it is spread: a swivel turns 25 degrees per metre (a clip 0.4 m out) into 2 degrees per metre (the laser end, about 4.6 m).
- Leaves uncertain: where the real fibre leaves the grip base (photo at the exit); the maker's twist tolerance (the manual says only "strictly forbidden").

**Entry 6. The rail has to follow the roll axis as the gun is placed.**
- Conflict: the roll axis is the line from the dot to the grip base; it moves with the gun's other two rotations. An aim error of 20 mm at the pulley end of a 0.75 m rail is a static torque shift of 57 to 61 N·mm (S-boot, no tension) and 130 N·mm with 3 N of tension, and 1 mm of aim jitter is about 3 N·mm.
- Assumption: the rail is placed once. It is placed per pose.
- Change: two small axes carrying only a pulley (the aim sliders, badged as actuators) keep it on the line; the load cell in the cord and the collar's encoder tell software whether it is. For a single neighbourhood a hand-set rail is enough.
- Leaves uncertain: how the rail itself is held (posts drawn illustratively); whether the required aim accuracy (a few millimetres at 0.75 m) survives a bench.

**Entry 7. The wire conduit is bundled here; it is a separate thing.**
- Conflict: the conduit leaves 23 mm from the fibre and separates to the wire guide. Bundled with the fibre its stiffness and weight add (0.01 N·m², 0.5 N/m assumed); but it also pushes at feed start, and it must not load the guide bracket (2 mm rods in the kit; a plastic bracket 100 mm long gives 0.1 to 1 mm per newton).
- Assumption: the wire's approach to the dot stays right because the guide is fixed to the shell and points at the dot. It does, as long as the conduit's last clamp is on the shell and not on the guide: the conduit gets its own clamp on the shell tail, and the last 150 mm to the guide is a slack service loop.
- Change: the scene's push is the feed push at the conduit's release point; the guide's aim is not affected by the route, and rolling the gun about a line through the dot leaves the wire's tip at the dot and turns its arrival direction with the gun.
- Leaves uncertain: the conduit's own EI, friction and push while feeding.

**Entry 8. The tether pulls the seat out.**
- Conflict: a rail force F along the roll axis has a vertical component F sin 30 degrees upward: 3 N of tension is 1.5 N of lift against 11.8 N of weight. It cuts the seat's margin (freedom-01b: the fibre pulls the seat out at about 6.7 N) by a fifth, and the plumb-bob's stiffness by the same fraction.
- Assumption: the constant force is free. It is a load on the support.
- Change: default zero. If a tension is chosen, count it in the balance (freedom-17 does for the weight share).
- Leaves uncertain: the seat's real pull-out force.

## Branches and combinations

- **freedom-15:** this scene is the ledger's scene. The ledger gets a fifth column (the couple), and the "exit axis passes through the dot" rule (entry 1 there) is refined: it holds for the roll axis, not for the grip's rake.
- **freedom-17:** the pivot on the roll axis, with a keel. The tension line through the dot is the line the pivot sits on.
- **freedom-18:** roll, twist and swing.
- **freedom-03 and borrowed-16:** a route that fixes the fibre's direction turns the shipped six-line layout from a fragile one into a good one: known within 8 degrees of the exit axis it stays taut to 5.3 N (calc/32). The rail's constant force along the roll axis is inside that range up to 5.5 N.
- **travel-08 and borrowed-11 (gallows, festoon):** the rail is the small version of a gallows whose head is aimed along a line, not just placed over the gun.
- **eyes-11b:** stripe and beads on the fibre give the twist the collar's encoder gives, without touching the fibre.
- **freedom-13:** the step it needs is the event table here.

## Unresolved problems, and questions that need Derek's observation

1. **Where does the fibre leave the grip base, and in which direction?** A photo along the grip and one from the side, with a ruler. (Sets the exit-angle slider: 0 to 30 degrees changes the roll story.)
2. **How stiff and how heavy is the fibre?** Weigh a metre of it on the kitchen scale; hang an overhang of 0.3 and 0.6 m off a table edge and measure the tip's drop (two overhangs give EI and weight separately). Or read the cable's data sheet if the maker has one.
3. **Does the maker allow any tension or twist?** The manual says "strictly forbidden" for twist and is silent on tension. (Derek to ask, if he chooses.)
4. **How big is the wire-feed push?** With the laser disabled, jog the wire with a dial gauge on the shell and read the needle (freedom-13 asks the same).
5. **How far does the gun leave the grip base's line when placed?** The line from the dot to the grip base at the working pose: two photos, or the dial values.
6. A boot is a print: an S-shaped tube 0.44 m long in pieces on the H2C, 12 to 14 mm bore, 350 mm radius. Whether the clearance to the hand grip works is a fit test, not a scene.

## Assumptions

- Kit proxy gun at the reference opening pose (roll 45, hole dial 30, vertical -15): roll axis 279 mm, 30 degrees above horizontal; exit tangent 30.2 degrees off it **[repo/kit, illustrative]**. Gun mass and centre of mass are not used.
- Fibre EI 0.1 N·m², 2 N/m, GJ = 0.8 EI; conduit 0.01 N·m², 0.5 N/m (bundled, additive): **illustrative, [unknown]**. Bend limit 350 mm emitting **[manual p. 20]**.
- Support presets (arm 0.5 N/mm and 100 N·m/rad at 200 mm; seat 10 N/mm and 20 N·m/rad at 70 mm; elastic 0.5 N/mm and 0.42 N·m/rad at 140 mm) are round numbers consistent with the statics of 01b and 11: **illustrative**.
- Events (5 mm anchor, 0.5 N feed push, 10 degrees of roll): round numbers.
- The rod is planar, inextensible, second-order in its discretisation; no friction against a hook or a table, no hysteresis, no contact with the bench or the tube.

## Sourcing pointers

`sourcing/freedom.md`, wave 3: cable pulling grip (Southwire WPG1/2, $11.73, 255 ratings; a 9 to 12 mm single, $7.99, 89 ratings), ball-bearing swivel (AMYSPORTS, $10.99, 1,838 ratings), stainless ball-bearing pulley 2-pack ($11.99, 738 ratings), 600 mm MGN12 rail with carriage ($34.99, 10 ratings, thin), constant force springs (thin), lead shot for a dead weight. All Prime, next-day or two-day. The boot is a print.

## Scene

`freedom-16-fibre-line`.
