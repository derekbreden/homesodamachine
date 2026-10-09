# who-moves-what on one-knob-one-parameter (wave 4): knob-wired suspension

My view: every freedom is owned by some body at some rate. Here the question is
which freedoms have to be wires at all, and what that frees.

I worked on `explorers/one-knob-one-parameter/ideas/knob-wired-suspension.md`.
Their search is **vendored** (copied, credited, unmodified except the import
name) as `explorers/who-moves-what/vendored_okop_diagonal_wires.py` and
`vendored_okop_geometry.py`. My runs are `wave4_wire_search.py` and
`wave4_wire_search2.py`, with the same proxy, the same true opening pose (dials
45 / 30 / −15), the same 40,000 samples per variant, and the same collision and
conditioning rejects. Their files are unchanged.

---

## The difficulty, in this variant

The published layout keeps every wire ≥ 5 N in only a handful of 40,000
candidates, with a worst-case minimum of 5.9 N. That is their break 1. My
re-run of their exact search gives **2 of 40,000, best 5.95 N**, matching. With
so little margin, the real gun's mass, centre of mass and umbilical force could
erase it.

## The assumptions behind it

1. **The vertical-axis angle must be a wire knob.** It is one of Derek's three
   dials, so it got a wire (W_vert) with a lead-screw anchor.
2. **W_vert leaves from the grip-base loop, pulling near the hole-axis
   direction.** In `layout()` it is attached at the grip base, with its direction
   within ±35° of the hole axis inside the (grip axis, hole axis) plane. The
   one-knob rule itself asks only that the wire **lie in that plane**: meet both
   the grip axis and the hole axis.
3. **Generic load box**: ±5 N at the dot on every axis, a 5 N trigger push, and
   5 N umbilical pulls in three fixed directions.

## Repairs, with numbers (same search, one assumption relaxed at a time)

| Variant | Change | Feasible of 40,000 | Best worst-case margin | Knobs still single? |
|---|---|---:|---:|---|
| A | theirs, reproduced | 2 | 5.95 N | yes |
| B | load cases from the sequence of use only (see below) | 3 | 6.0 N | yes |
| **C′ (their loads)** | the sixth wire placed **anywhere in the (grip, hole) plane**: attached on the grip axis at s = 60–330 mm, any in-plane direction | **12** | **18.5 N** | **yes** |
| C′ (sequence loads) | same, with B's loads | 25 | 13.9 N | yes |
| C | sixth wire unconstrained (off the plane) | 12 | 28.4 N | **no**: W_hole leaks 0.27° of V per mm |
| D | every wire leans up the corner's escape direction, so a lift slackens all six | 1 | 5.9 N | — |

**R1: free the sixth wire within its own plane.** This is the main repair,
and it applies to their design as it stands.
- With their own load cases it raises the feasible count 6× (2 → 12) and the
  worst-case margin 3× (5.95 → 18.5 N).
- The knob purity is untouched. In the best sequence-load layout, the
  first-order columns are W_grip: G only (+0.581°/mm) and W_hole: H only
  (−0.283°/mm), with zeros elsewhere to three decimals.
- That layout attaches the sixth wire to a **shell boss 112 mm along the grip
  axis**, in the air under the barrel about 36 mm from the gun's surface (my
  wave-1 pin-point table). It pulls almost horizontally toward −X, over the tube
  to an anchor on the far side.
- *Cost:* that wire crosses the loading column, so it gets a hook and V-notch
  like their W_x, W_y and W_vert.
- *Left:* a side constraint keeping W_y and W_z on the cold (−Y, arriving) side.
  The best layout already puts W_y on −Y; W_z is still on +Y above the rim. I did
  not run that constrained search.

**R2: move the vertical-axis knob to the couch (tube symmetry).** This is my
allocation contribution; it removes a knob rather than repairing one.
- Their couch already carries X and Z under the rotator. Add **Y along the
  tangent**. A slide of r·sin φ, with the X correction r(1 − cos φ), turns the
  relative vertical angle by φ at **1.08 mm per degree**, exactly, because the
  seam is a circle on the tube axis. The sixth wire then keeps a **fixed length**:
  a painted turnbuckle, no lead screw.
- *Exact instead of first-order.* Their W_vert moved the dot 0.18–0.30 mm and
  leaked ≤ 0.26° into the other angles for a 5° step, and 0.78–1.3 mm and
  ≤ 1.1° for 10°. The couch leaks **nothing** into grip or hole. Its only
  side-effect is the analytic X correction: 0.04 / 0.24 / 0.94 mm at
  2 / 5 / 10°, which the couch X applies.
- *Range and resolution.* ±25 mm of couch travel is ±23° without re-anchoring,
  against ±6° per neighbourhood by wire. A 0.01 mm division is 0.009°.
- *Nothing above the rim moves for a yaw change.* Wires, umbilical and gun stay
  where they were, so yaw experiments leave the cable loads constant.
- It is their own chain rule carried one step further: translations near
  ground, and here a translation of the work *is* the outermost rotation.
- *Knob count after R1 + R2:* two angle wires (grip, hole) plus three couch
  axes (X, Z, Y = vertical angle). Four wires are fixed calibration. Five weld
  parameters on five knobs; the sixth, position along the seam, doesn't matter.

**R3: load cases from the sequence (tried; a small effect).** B drops the trigger
push (it closes inside the shell) and uses:
- 1.2 and 2.0 kg with the centre of mass ±20 mm;
- the umbilical 5 N along its real exit direction, plus 5 N of sag;
- stuck-wire drag of 5 N in the one direction the table drags (+Y);
- a 3 N wire-touch reaction.

Feasibility barely moves (3 layouts, 6.0 N). **Their margin problem is geometric,
not an artefact of the load box.** That is an honest negative, and it is why R1
matters.

**R4: escape-lean wires (tried; rejected).** If every wire has a positive
component along the corner's escape direction, lifting the gun along it
slackens all six at once and lift-off needs no hooks. Only 1 layout survives, at
5.9 N and 105 µm of dot motion under 5 N (3–5× softer). Their hooks and V-notches
stay.

## Where I would push it next

- **Weight vs location.** Their wires both carry the gun (≈ 38 N of up-pull) and
  locate it, which is the source of the margin fight. A balancer at the centre
  of mass lowers the up-pulling tensions, but the preloads then have to keep the
  horizontal wires taut. Not run; it would be the next variant.
- **Tilting the work** (my `tilt-cradle-escape-rail.md`) changes this idea the
  most. At τ ≈ 32.5° about the station tangent, gravity's torque about the grip
  axis falls from 0.77 N·m (upright, 1.5 kg) to 0.13 N·m, and crosses zero near
  38°. About the vertical axis it is zero at any tilt. **So at the tilt, only the
  hole wire carries gravity, and it is gravity-tensioned; grip and yaw need only
  light locks.** That is the combination in
  `explorers/who-moves-what/ideas/gravity-in-the-gun-plane.md`, which uses their
  hole wire and plane rule directly.

## What their idea does that my arrangements lack

- **A readout per angle with no joints to shift.** Their tension-loaded nuts
  take up their own backlash.
- **The plane rule.** It is the cleanest statement anyone has made of how to make
  a support decoupled, and it is what makes my combination one-knob.
- **The walk test** as a per-session concurrency check.
- **Vibration modes** (31–252 Hz) checked against the wobble frequency: a
  consideration none of my supports has had.
