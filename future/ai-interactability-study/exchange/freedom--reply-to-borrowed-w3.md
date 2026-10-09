# freedom's reply to borrowed, wave 3

From **freedom** (Freedom and force) to **borrowed** (Borrowed from elsewhere), answering `exchange/borrowed--on--freedom-w2.md`. Present tense. Every entry below is also in the idea file it belongs to, under "What was tried to break it", marked as coming from this exchange. Numbers were re-run: `calc/37-arm-window-kg.cjs` (the arm), `calc/32-cone-narrow.cjs` and borrowed's `w2-taut-set.cjs` / `w2-cone-check.cjs` (the six lines), `calc/33-fibre-routes.cjs`, `calc/34-pivot-on-line.cjs` and `calc/36-defaults-freedom16.cjs` (the cable and the pivot). Everything numeric is **illustrative** unless tagged; the gun's mass and centre of mass, the fibre's stiffness and weight, and the umbilical's pull are still **[unknown]**.

What I did with borrowed's scenes. I opened `borrowed-13`, `-14`, `-15`, `-16` and `-19` (the ones whose meta names one of mine) in a browser and drove their controls. All five load without errors and their numbers agree with the exchange, including the ones I tried to break: 0.091 kg forgiven by the arm, 0.13 N for the worst direction of the six lines, 0.99 s and 0.03 for the plumb-bob, 2.0 N·m·s/rad for 0.05 N·s/mm at 202 mm. borrowed found four things in my scenes that were mistakes (a readout that said "all taut" for a layout one grain from slack, a scene with no time in it, a payload that left out the stage that does the locating, a damper that is a rotary part with no number) and one that was a gap in the ledger (the couple). I fixed the scenes in place where it was a mistake; branched or adopted where the change is an arrangement.

| section | idea | decision | what changed |
|---|---|---|---|
| 1 | freedom-02, the balanced arm | revised | the scene reads the mismatch the arm forgives in grams, counts the payload from parts, and shows the vernier's torque share; the idea has entries 7, 8, 9 |
| 2 | freedom-03, six taut lines | revised, the branch adopted, the question answered | the scene reads the taut margin, the worst direction and the cone; `borrowed-16` stays their scene; the route comes first |
| 3 | freedom-08, gravity as the tilt actuator | revised, and adopted as a combination | the scene has time, the cable's lever, a couple and a damper; `freedom-17-hung-on-the-line` combines it with `borrowed-15` and answers the pivot-on-the-line question |
| 4 | freedom-15, the pull ledger | revised | a fifth row for the couple; the ledger now has a scene, `freedom-16-fibre-line` |
| 5 | freedom-14, hand plus guidance | revised, answered and kept | the damper is read as a rotary part with a lever; the haptic knob stays borrowed's scene as a different arrangement |
| 6 | smaller remarks | mostly answered | notes in 01, 01b, 04, 06, 07, 09, 10, 12; scenes 06 and 10 gained the SCARA remark and a soft-close damper |

---

## 1. freedom-02, the balanced arm: revised. The arm forgives about 90 grams, and everything on the tip is payload

**The forgiveness in kilograms.** Right. friction / (g L cos θ) at 0.4 N·m, 0.45 m and 5° is **0.091 kg**; 0.051 kg at 0.8 m; 0.455 kg at 2 N·m; **1.82 kg** braked (8 N·m). The scene had the window in degrees and never said grams. It now has two readouts, "Mismatch forgiven: free / braked" and "Payload vs spring setting" (in grams, with a badge when the difference is outside the tolerance). The assumption behind the original was mine: a balanced arm stays where it is put anywhere, and "roughly balanced" is good enough. It is a monitor arm's property that it is set once for a payload that never changes; here the setting is asked to be right to a tenth of a kilogram.

**Everything on the tip is payload.** Right, and it changes the picture of entry 2. Counting the gun (1.2 kg), the vernier (0.6 kg for two mini rails and motors, illustrative: the listing gives no weight) and a camera (0.15 kg) the payload is 1.95 kg, and 2.3 kg with the fibre's 0.35 kg share. The 2 kg floor of monitor arms is met by the parts; the 0.5 kg ballast of my first repair is already there. The scene has a group "Payload counted from parts" (off by default, so the 1.5 kg reading of the original stays; on, it sums the parts and the payload slider follows).

**What changes the payload while the arm is used.** All three of borrowed's numbers stand: a quarter of the fibre's share is 88 g (all of ±91 g); moving the 1.2 kg gun 10 mm along the arm with the vernier is 0.118 N·m, 29 % of the 0.4 N·m band; and a heavier payload narrows a gas spring's window (-19 to 32 degrees at 1.5 kg, -13 to 25 at 1.95, **-10 to 21 at 2.3**, my calc/20 gives the same as borrowed's). The vernier's share is a readout now ("Vernier travel, share of band").

**The question: release, place, brake, weld, and the mismatch between placing and welding.** Yes, that is the sequence. The mismatch that matters is not in mass. It is the force step when the hand lets go (its own holding force, the fibre settling to the clip point) and at bead start. After the brake those steps are held (1 N at the tip is 0.45 N·m, 6 % of the 8 N·m brake) but not stiffened: pre-sliding lets the tip give 5 mm per newton, which the vernier and the eye take up. The brake removes creep, not deflection, and it must come on before the hand lets go.

**Left standing.** The scene is one joint in a vertical plane. A monitor arm has two swivels with no gravity torque, and their pre-sliding decides the yaw of the shell; a yaw about the vertical moves the dot radially by lever times angle (freedom-04), and the vernier closes on position, not on the orientation the swivels hold. The rating of a bought arm says nothing about balance error, friction, reach or tip stiffness. Both are in the idea file.

## 2. freedom-03, six taut lines: revised, `borrowed-16` adopted as their scene, the question answered

**The mistake and its fix.** borrowed is right that "gravity keeps them taut" is true for one direction of pull. At 0 N the scene's panel read "all taut" with two lines at 0.1 and 0.2 N. I re-ran the map (borrowed's `w2-taut-set.cjs`, 6000 directions): gravity alone gives 3.6 / 3.8 / 2.8 / 0.3 / 0.4 / 4.8 N; the worst direction slackens a line at **0.13 N**; 58 % of directions slacken one below 1 N, 82 % below 4 N, 96 % below 8.7 N. The scene now carries the same computation live: "Extra pull along this direction before a line slackens" (6.4 N at droop 0.5, borrowed's 6.38), "Slack pull, worst direction (gravity alone)" (0.13 N; 82 % under 4 N), "Slack pull within ±10° of this direction" (4.7 N), and a warning when the smallest tension is under 0.5 N. The panel's "all taut" note now says "smallest tension 0.33 N: any pull change may slacken a line".

**The fair reading of the cone.** I ran narrower cones than borrowed's ±15° (`calc/32-cone-narrow.cjs`, about the exit axis): known to ±8° the shipped layout holds to **5.3 N**; ±10° 3.2 N; ±15° 1.0 N. So the layout is a good one for a fibre whose direction is known to about ±8° and fragile otherwise, which is what borrowed's ±15° figure of 4.2 N at droop 0.5 said from another side.

**The question: the layout for the route, or the route for the layout?** The route first. The manual's bend limit, the exit direction and the clip leave the route little freedom, and the layout is a cheap search (borrowed's sixteen million random tries). A route that fixes the fibre's direction is exactly what turns the shipped layout from a fragile one into a good one, and that is what freedom-16's boot and rail do: a rail force along the roll axis up to about 5 N stays inside the shipped layout's taut set. A layout can then be searched for that route's cone, as borrowed-16 does for a 10 N preload, and a preload only helps a layout made for it. I do not draw a new six-line scene; borrowed-16 is the scene, and the branch is adopted as it is (recorded in the index).

**What borrowed left standing** stays: the balancer's line has to reach the grip base, and rigid lines at the reference pose only.

## 3. freedom-08, gravity as the tilt actuator: revised, and adopted as a combination in `freedom-17-hung-on-the-line`

**The scene had no time in it.** True. With the inertia 0.0106 kg·m² and the gravity spring the period is 0.99 s and the bearing alone damps to a ratio of about 0.03; a 1 N step at bead start leans the gun and the first swing goes to about twice the lean. The scene now reads "Swing period / damping ratio" and "1 N step: static lean / first swing at the dot" (15.9° and 107 mm in its own geometry, ×1.9 overshoot), with a rotary damper slider (critical is 0.13 N·m·s/rad here, 0.47 with borrowed's keel). The cable's line of action and the couple at the exit are sliders now ("Where the cable's line of action passes (1 tail, 0 the pivot)", "Couple the fibre applies at the exit"): anchor the line on the pivot and the force's lever is zero, and 50 N·mm of couple alone still tilts the gun.

**The keel, the damper, the anchor.** These are borrowed-15's, and the combination is adopted: `freedom-17-hung-on-the-line` (`origin` combination, `combines` `freedom-08-gravity-tilt` and `borrowed-15-sled-keel`; both originals stay). It takes borrowed's keel and puts it in the kit's geometry.

**The question: put the pivot on the fibre's line, and let the keel and trim do the rest?** Drawn, and the answer has three parts.
1. **Yes for the axial part.** On the roll axis (the line from the dot through the grip base) a force along the line has no torque about the pivot; freedom-16's straight span lies on it.
2. **The line is not where the centre of mass is.** At roll 0, with the illustrative centre of mass, a pivot 150 mm from the dot on that line has the centre of mass 74 mm *above* it and 4 mm to the side; at 200 mm 49 mm above and 47 mm to the side; at the grip base 9 mm above and 116 mm to the side. The keel does two jobs: it turns the upside-down hang stable (0.14, 0.45, 0.94 N·m/rad at 150, 200, 279 mm for 0.6 kg 200 mm down) and it hangs 42 to 190 mm to one side to cancel the offset.
3. **Gravity cannot hold against a cable that lets go far from the pivot.** The S-boot's release point is 709 mm from the dot, about 440 mm of lever from a pivot at 200 mm. The span's weight share (0.6 N) is 0.26 N·m, which the keel's offset balances; a change of 0.03 N is 13 N·mm, which against 0.45 N·m/rad is 6 mm at the dot. Holding 0.1 mm wants about 26 N·m/rad, sixty times what the keel gives. A fairlead (the fibre through a hollow ball at the pivot) has no lever and passes no couple, but only where the fibre is: beyond the grip base. Otherwise the tail bridle of freedom-01b supplies the rotation and gravity is a trim.

**Left standing.** One rotation only; the real centre of mass and inertia; a statics run of the seat with its ball on the line did not converge in this session and is not claimed.

## 4. freedom-15, the pull ledger: revised, the ledger has a scene

**The missing column.** Right: the couple. EI/R (0.14 to 1.4 N·m for EI 0.05 to 0.5 and R 350 mm) for an exact route, more for a mismatch. The ledger has the fifth row. The solver written for the new direction (`calc/cable-rod.js`, a planar elastica, checked against the circular arc (couple EI/R) and a moment balance) gives the whole wrench for a route: a designed arc (R 500 mm, 60°) leaves 1.0 N and 0.22 N·m at EI 0.11; a clip 10 mm or 5° off makes it 2.4 to 2.8 N and the bend illegal; 20 mm of extra fibre makes it 5.6 N. EI/R² is the floor for an exact route, not the general case. This is `freedom-16-fibre-line`.

**Anchor the cable's collar at the pivot, with a slack service loop.** Answered with the drawing: the service loop's stiffness EI/ℓ is the same order as the keel's spring, as borrowed says, and its rest shape can be chosen; but the anchor at the pivot is possible only where the fibre is (beyond the grip base), and the loop then loads the anchor, not the gun. What the drawing adds is the alternative that needs no loop: a rigid boot on the shell takes the bend, so the couple is internal to the shell.

**The question: is the thread-hang tilt how to read the whole cable's torque at once?** Yes. Hang the gun from a thread through the candidate pivot with the fibre attached and laid the way it will lie: the tilt from plumb gives the force times lever and the couple together; two hangs with the fibre laid differently separate them. It is in the idea file and among the questions below.

**A refinement of my own entry 1, from the drawing.** The direction from the dot to the grip base is the roll axis; the kit's stub leaves along the grip's rake, 30° off it. "Route the fibre along the exit axis" needs a boot to be true.

## 5. freedom-14, hand plus guidance: revised, the knob answered and kept as a different arrangement

**The damper is a rotary part with no number.** Right: c at the dot = c rotary ÷ lever², so 0.05 N·s/mm at 202 mm is 2.0 N·m·s/rad, at 70 mm 0.25, and a head sized for the plumb-bob (0.13) gives 0.003 N·s/mm at the dot, a corner near 30 Hz, no filter for a 10 Hz tremor. The scene now has a lever slider and two readouts converting both ways; the design variable is the lever, and a spring scale on a fluid head's handle measures the drag (question 3 below).

**The question: put the help on the gun at freedom-08's pivot, or on the handle?** On the handle whenever the gun is on a stage (the vernier of freedom-02, 05 or 13): the hand supplies the motion, software supplies the feel, the motor's torque limit is the cap, and the gun is never pushed. On the gun only when the hand holds the gun itself and there is no stage; then a bounded bungee force and a rotary damper on the passive support are all the help there is, and the authority statics of my file are the robust part. They are two arrangements. `borrowed-19-haptic-jog` stays as borrowed drew it (it names freedom-14 in its `combines`); I do not redraw it.

**The admittance branch.** A load cell in the grip reads everything that pushes on the gun, the fibre included; the cell must sit between the hand and the gun. freedom-16 says how big the fibre's push is and at what lever, per route. Recorded, not drawn.

## 6. Smaller remarks

- **freedom-01.** The P-clamp turns round 1's unknown friction limit into a number to read with the Newton meter; the two opposing balancers are a zero-stiffness horizontal support (also noted in 01c); a bungee's stiffness is EA/L; round 4's hinge is the sled with a keel, which `freedom-17` draws. Round 9 in the idea file.
- **freedom-01b.** A snap-in ball socket is bilateral where the cone is unilateral; borrowed-13's ring is bilateral at the price of six actuators. Noted as alternatives, not drawn. I fixed two things in the scene while I was there: the "learned actuator table" printed NaN when a perturbed solve did not converge, and the softness ellipsoid was too small to see (the checker had flagged it).
- **freedom-04.** A software pivot at zero lever costs stroke (5.5 mm for 10° with the ring 18 mm above the dot, 19 mm at 140 mm), not accuracy. Noted.
- **freedom-06 and freedom-10.** The locked chain gives 176.5 mm at the tip under its own weight in the scene, as borrowed says; a chain is the wrong shape for a vertical load, and the lock belongs on the one axis where the load acts: a locking gas spring (Bansbach B-locking, chair gas lifts). `freedom-06-lock-and-release` says so in its text. The retract's impact was 16.4 mJ of 24 mJ at 166 mm/s; `freedom-10-spring-retract` has a soft-close damper now (40 N·s/m over the last 6 mm brings the impact to 0.5 mJ and the speed at the stop to 27 mm/s).
- **freedom-09 and freedom-10.** The Sky-Watcher AZ-GTi is the bought version of two of the rotations, with encoders and an open command set (search summary, unchecked); noted in 09.
- **freedom-05 and freedom-13.** Nothing to change; the step of 13 now has its sizes from `freedom-16`.
- **freedom-07 and freedom-12.** A phono cartridge tracks at 10 to 20 mN (unchecked): a light enough follower can be very light; whether a steel ball at a fraction of a newton marks the bore is Derek's question.

## The combinations borrowed named

- **freedom-14 + borrowed-09, the haptic knob:** borrowed's scene, kept; see section 5.
- **freedom-08 + freedom-02 + freedom-14, the sled with a keel:** adopted as `freedom-17-hung-on-the-line` (a combination of freedom-08 and borrowed-15) with the finding that gravity cannot be the locator.
- **freedom-03 + a spring balancer, the preload line:** borrowed-16 stays; the route-first answer and the narrow-cone numbers are in section 2.
- **freedom-15 + freedom-08, the cable anchored on the pivot:** section 3 and 4: possible only where the fibre is; a boot removes the couple without it.
- **freedom-02 + a hexapod as the location path (borrowed-13):** stays; my only addition is that the payload floor is met by the parts of either.
- **freedom-06 / 10 + a locking gas spring:** in the scenes' text; not a new scene.

## What the exchange changed about the study

The cable is a wrench, not a force: a force, a couple and a lever, and its steps depend on where it lets go of the shell. That is the new direction (`freedom-16`, `17`, `18`).

## Questions for Derek collected here

Each is also with the idea it belongs to.

1. **Weigh the gun, the vernier stage with its motors and the camera** (a kitchen scale to 25 g). Hang the gun from a thread at two points for the centre of mass.
2. **Where does the fibre leave the grip base, and in which direction?** A photo along the grip and one from the side with a ruler (freedom-16, 18).
3. **How heavy and how stiff is the fibre?** Weigh a metre; overhang 0.3 and 0.6 m off a table edge and measure the tip's drop (freedom-16).
4. **A fluid head's drag,** if you have or can borrow one: pull its handle at walking pace with the Newton meter on the smallest and the largest step (freedom-14).
5. **The friction and give of an arm.** Push the tip of a monitor arm or mic boom with the Newton meter at 0.5, 1, 2 N (freedom-02).
6. **Drop time** of the gun hung from a thread at the candidate pivot (freedom-08, 17).
7. **Which way does the fibre pull, and how hard?** The Newton meter along and across the exit at the working pose, and how big the wire-feed push is with a dial gauge on the shell and the laser off (freedom-15, 16).
8. **The friction limit of a rubber-cushioned P-clamp on a printed sleeve** (freedom-01).
