# carry-and-locate — summary entries

**View.** Carrying and locating are different jobs. For every arrangement: what
carries each load, what establishes where the dot and the angles are, and what
"fixed" is fixed to. All numbers are at the true opening pose (grip 45° / hole
dial 30° / vertical −15°) on the scene's proxy gun. Gun mass is assumed at
0.6–1.6 kg; nothing has been built or measured.

## A. Derek's suspension, developed *(from Derek's example)*

`ideas/suspension-original.md` · `sketches/A-suspension-original.svg`

- **Arrangement:** two openable loops on wires, each centred by opposed bungees.
  The tip loop sits on the graduated tube, 56 mm from the dot; the base loop goes
  around the rear collar and the cable. An optional third ring sits high at the
  housing back, and an arm grips the printed shell.
- **Findings:**
  - Bungees on the radial axis, tangent left as the free swing: the joint is a
    circle, so 2 mm along the tangent is only 0.03 mm off it.
  - The tip loop carries 56–68% of the gun.
  - The line through the two loops is 9.4° off Derek's grip axis; a shell
    trunnion on that axis makes the free roll exactly his grip-axis roll.
  - The third ring belongs at the housing back.
- **Breaks:**
  - The bare float is about 0.01–0.1 N/mm sideways, so 1–5 N moves it 10–100 mm.
  - machine-that-learns showed that a camera driving motorised anchors cannot
    hold the weld-start push either. The float must be damped (a copper eddy
    vane is proposed) and then locked.
  - A clamp around the cable twists the fiber by about 0.87× the roll, so the
    loop must stay a loop.
- **Branches:**
  - A-r1: float plus arm.
  - A-r2: hang on the grip axis.
  - A-r3: wire plus bungee preload, which grows into B.
  - A-r4c (machine-that-learns): place soft, clamp at each loop, learn the
    clamp's shift.
  - A-r4d: Derek's bungee seats a V-shoe on a steel rod and a magnet locks it.
  - A-r5: V-contacts in place of round loops.
- **Parts:** grow-light rope ratchets ($11.99, Prime, 50+/month), shock cord
  ($9.99, Prime, 200+/month).
- **Open:** gun mass and centre of mass, the damper, and the size of the cable
  saddle.

## B. Wire-located suspension *(beyond the examples, grown from A-r3)*

`ideas/wire-located-suspension.md` · `sketches/B-wire-located-suspension.svg`

- **Arrangement:** three stainless wires whose lines meet at the dot act as a
  virtual ball joint; three more set the angles; bungees or balancers keep every
  wire taut. The anchor frame is "fixed" and must belong to the rotator's frame.
- **Numbers:**
  - Turning the gun about the dot moves the dot only 0.02–0.05 mm per 2°.
  - Stiffness at the dot is about 64/64/262 N/mm.
  - Lifting the gun slackens the wires; lowering it returns the pose.
- **Breaks and repairs:**
  - The first layout needed wires to push. A layout search found ones that stay
    taut with two preloads of about 38 + 36 N.
  - machine-that-learns ran it as a cable robot and found that plan angle must be
    a tangent translation.
  - Bungee preloads drift with travel, so they become balancers or a seventh
    wire; a camera calibrates the geometry.
  - For one-knob-one-parameter: strictly one wire per angle is impossible, but a
    practical layout exists. One wire sets hole tilt (0.3° per turnbuckle turn)
    and one sets roll, with at least 12.9 N tension margin.
- **Parts:** 1/16 in stainless wire rope ($23.99, Prime, 800+/month), M4
  turnbuckles ($7.99, Prime, 200+/month).
- **Open:** frame stiffness, and clutter around the cable exit and the camera.

## C. Float and dock *(beyond the examples)*

`ideas/float-and-dock.md` · `sketches/C-float-and-dock.svg`

- **Arrangement:** a balancer and cable saddle carry. A metal tongue on the shell
  ends in three balls that drop into hardened-rod V-grooves on an adjustment
  stack beside the tube, pulled home by a switchable magnet.
- **Breaks:**
  - A hand on the trigger unseats it: at 40 N preload the seat holds only about
    5 N at the trigger, so a presser mounted on the shell is required.
  - The umbilical's residual pull uses up half the seat's margin.
- **Parts:** QWORK balancer ($16.97 for 2, Prime, 50+/month), MagJig 95 ($46,
  Prime), G10 balls, 8 mm hardened rods ($9.99, Prime), MG90S servo presser
  ($13.88 for 4, 900+/month).
- **Open:** a stack that rotates about the dot. Like the original E, the seat is
  referenced to the room near the nose.

## D. Rim carriage, with branches D2 and D-s *(beyond the examples)*

`ideas/rim-carriage.md` · `sketches/D-rim-carriage.svg`

- **Arrangement:** a C-ring rides the rim on stainless rollers, with pinch pairs
  at ±30° gripping the 1.65 mm lip (leaking 0.42× the ovality). A soft tether
  resists only the spin, which doesn't affect the dot, and doubles as the
  stuck-wire fuse. A float trims the load on the rim.
- **Finding:** a radial push of only 6–8 N lifts the tube in its nest.
- **Breaks:** it reads the rim, not the joint; the lip is warm; the rollers could
  bond the gun to the work (interlock); the open ring is weak in torsion.
- **Branches:**
  - D2: a shoe on the cap face and bore.
  - D-s (machine-that-learns): a 0.5–1 N stylus that senses while a stage acts,
    and logs runout at the dot on every bead.

## E. Switch-locked skate, and E-dome *(beyond the examples)*

`ideas/switch-lock-skate.md` · `sketches/E-switch-lock-skate.svg`

- **Lock-shift classes:**
  - load changing hands at the switch, removed by a float carrying through it;
  - locks that close a gap (clamps, collets, articulated arms): hundredths to
    tenths of a millimetre;
  - locks that only add preload to contacts already touching: about 3 µm.
- **Arrangement:** a MagJig shoe on three balls skates on a steel plate. It holds
  24–39 N sideways, and magnetic stops remember the pose.
- **Critique accepted (work-as-datum):** the plate becomes the dot's reference.
  Their R-B and R-C are recorded.
- **E-dome:** a shoe skating on a sphere centred on the dot.
- **Capability checked:** FISSO central-lock arms publish 30–56 N at the tip;
  Noga and HHIP publish no stiffness.

## E-RA / E-RA+ *(work-as-datum's R-A, plus a roll pad and a spring-seated cup)*

`sketches/E-RA-cup-and-tail.svg`

- **Arrangement:** a cup centred on the dot, on the endcap hanger, holds the dot.
  The tail ball sits in a round bore in the magnet shoe, which sets hole tilt and
  plan angle (0.21° per mm of slide). A second ball on a screw pad sets roll. One
  switch locks everything; the constraint count is 3 + 2 + 1 = 6.
- **What moving the reference buys:** debris and switch twist become hundredths
  of a degree, and tube length becomes a 0.66° angle change instead of a dot
  error.
- **Open:** calibrating the cup's centre onto the dot, heat on the cup pads, and
  nipples in the ports while welding.

## F. Nose and tail

*(Combination: work-as-datum's hung nose and paddle compass,
workspace-as-structure's paddle, machine-that-learns' camera.)*
`ideas/nose-and-tail.md` · `sketches/F-nose-and-tail.svg`

- **Arrangement:**
  - Nose: a V-loop with a sprung jaw on the endcap hanger holds a point 46 mm
    from the dot.
  - Tail: ball transfers on a steel table. The table's height screw is hole tilt
    (0.23°/mm) and its cross-tilt screw is mostly roll.
  - Plan angle: a link to a magnet-braked carriage.
  - Carrying: a float hooked about 85 mm off the centre of mass.
- **Break:** a locked shoe at the tail made 9 constraints, and the nose would
  fight it every revolution. Rolling contacts plus one lockable link give
  exactly 6.
- **Tube length:** +1 mm puts the dot 0.18 mm off; raising the table 1 mm
  cancels it.
- **Relation to E-RA:** the same idea reached from two sides in the same wave —
  the work holds the dot, a table beside the rotator holds the angles, a float
  carries. F's pivot is 46 mm off the dot with numbered screws for angles;
  E-RA's pivot is at the dot with hand-taught angles and one switch. A merged
  form (E-RA's cup with F's screw table) is not yet written.
- **Parts:** stainless ball transfers ($9.99 for 4, Prime, thin stock).

## Branches contributed to others

- **machine-that-learns B (stage-and-arc carriage):**
  - Without a float, the roll drive's load reverses inside the workspace.
  - A float at about 90%, hooked off the centre of mass, keeps every drive loaded
    one way.
  - An open C-ring lets the cable drop in, with the cable's first support riding
    the arc carriage.
  - Sketch: `sketches/X-mtl-B-float-and-open-ring.svg`.
- **machine-that-learns C (hexapod):**
  - A 110–185 N gas spring keeps all six legs in tension.
  - Tr8×2 lead screws ($27.99, Prime) replace the back-driving Tr8×8.
  - Branch C-w: the six-wire hexapod.
  - Sketch: `sketches/X-mtl-C-preloaded-hexapod.svg`.
- **work-as-datum D1 → D1-p:** the nose carries about 4.1 N and its groove is at
  its limit, so a stuck-wire drag or a hand unseats it. The fix is a sprung jaw,
  a bungee pairing the base wire, and a float. The base lines should be anchored
  on the rotator frame, since their motion reaches the dot at 0.165×.

## Transferable pieces

- Soft carriers with stiff locators; bungees preload, they don't locate.
- A float that carries the load through the moment a lock switches.
- Prefer locks that only add preload to contacts already touching.
- Under motors, bias every drive one way: a float just under 100%, hooked off the
  centre of mass.
- The determinacy rule: where a work-referenced contact is combined with a lock on
  the room side, the lock may hold only what the work contact doesn't already set.
- Motion along the tangent equals plan angle.
- Seat by internal preload, never by carried weight.
- Cable: saddle bend radius at least 350 mm; loops must let the cable turn; open
  rings, not closed ones.
- One wire per angle is practical for hole tilt and roll.
- Load facts: a stuck wire bends at 3–5 N while the rotator pulls about 140 N;
  wobble moves a free gun 0.4–8 µm; a 6–8 N radial push lifts the tube.

## Questions only Derek's observation can answer

1. Gun mass and centre of mass.
2. Umbilical pull at the grip, and its real exit direction.
3. Trigger force.
4. Which part of the gun carries the interlock contact, and whether a fixture may
   be bonded to the work lead.
5. Whether nipples may sit in the ports while welding.
6. Tube length spread and rim cut quality.
7. Ceiling and pegboard positions above the rotator.
8. The MagJig's real pull across a 0.2–0.3 mm gap, and its knob torque.
