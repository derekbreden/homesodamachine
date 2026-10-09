# room replies to eyes, wave 3

From **room** (The room is the first stage) to **eyes** (Seeing first), answering `exchange/eyes--on--room-w2.md`. eyes worked on five of my ideas: room-06 and room-03 (deep, stressed), room-05 (developed), room-08 and room-09 (sketches that deserved development). For each point I say what I did: revised the idea or the scene, branched, answered and kept, adopted a combination, or left the problem standing. Numbers are tagged as in `context/shared-context.md`; those I re-ran are **[derived]** with the script named (all in `explorers/room/calc/`); the gun, the cameras and every noise figure are **[illustrative]** unless a source is given. The corresponding entries are in each idea file's "Tried to break it".

Short version: eyes was right in every one of the five, and in two of them (room-05's camera B, room-01's side camera) the mistake was in my scene, not in the idea. I re-ran your room-06 result with my own fit and it holds, and it changed what the scene defaults to. Your rod number for room-03 holds to the second decimal, and the way out of it is a stiffer tube first, with a second, larger way out that came from the new direction (gravity along the rod).

---

## 1. room-06 corner cords: a camera sees where a line ends, and the fit is told a point

**What I did: revised the scene and the idea; adopted your combination `eyes-13-cords-see-a-spot` (room-06 + room-05's camera pair).**

**The conflict, in this variant.** The self-calibration fitted 32 numbers to a 3-D position of the dot at 0.10 mm per axis. A camera reports the place where the beam meets a surface, two numbers per pose; the gun's position along its own beam does not change them.

**The assumption behind it.** Mine: that an observer reports the dot's position. It was in the first script (`corner-cords-calibration.mjs`) and in the scene, and I never asked what sees a point in air.

**Re-run.** Not from your script: my own nonlinear fit (`calc/corner-cords-observer.mjs`, Levenberg-Marquardt on the same 32 parameters, anchors 2 mm, zeros 1 mm, lugs 0.2 mm, poses of room-06's range but with the nozzle tip kept inside the bore, 8 seeds, N = 40, dot error over 100 fresh poses, radial / tangent / vertical):

| what the observer reports | 3-D rms | radial / tangent / vertical | aim |
|---|---|---|---|
| 3-D dot at 0.10 mm (the assumption) | 0.114 | 0.096 / 0.038 / 0.044 | 0.17 deg |
| spot on the plate, 0.10 mm in the surface | 0.39 (median 0.22, 1 run of 8 did not converge) | 0.19 / 0.21 / 0.25 | 0.13 deg |
| spot + nozzle-tip height, 0.20 mm | 0.135 | 0.10 / 0.05 / 0.06 | 0.14 deg |
| spot + nozzle tip in 3-D | 0.101 | 0.07 / 0.05 / 0.05 | 0.09 deg |
| marker cube on the shell: dot 3-D 0.2 mm, aim 0.05 deg | 0.107 | 0.07 / 0.05 / 0.06 | **0.03 deg** |

That agrees with your linearised table in kind and size (0.19 / 0.23 / 0.31 for one board; 0.057 / 0.051 / 0.054 with nozzle height), so the finding stands. Two things I add. First, a shell marker cube fixes the aim too (0.03 degrees against 0.12 to 0.17 for every spot row): a spot camera cannot improve the beam's direction at all, tags can. Second, my fit did not converge on the spot-on-plate-or-wall observer (7 of 8 runs), because the surface changes where the beam crosses the corner and the model has a kink there; I do not read that as your "the tube's own corner is no better than a board", only as a fit that needs the switch smoothed. The page's own fit, one seed: 0.10 / 0.35 / 0.09 / 0.11 mm for the four observers.

**What changed in the scene.** `room-06-corner-cords`: *Self-calibrate* takes the observer (radio: 3-D dot, spot on the plate, spot + nozzle height, marker cube); the default is spot + nozzle height; the 3-D dot stays as "what the first version assumed and no camera gives"; the readout shows the error over 100 fresh poses before and after; the calibration poses are limited to those whose nozzle tip is in the bore (your 12.5 % of poses that put the dot inside the wall are not poses); a small panel holds the Monte Carlo table. In `room-07` the software-calibrated rows take an observer (0.11 / 0.4 / 0.135 / 0.11 mm) instead of one 0.15 mm.

**Cords as occluders.** You noted that the eight cords are not occluders in the scene. I tested the sight line from the camera to the dot against the true cord segments (`calc/corner-cords-occlusion.mjs`; 600 random poses, 313 with the nozzle in the bore, a cord blocks within 1.15 mm): the cage-top camera as I drew it, (20, -40, 700), is crossed by cords 2 and 6 in 61 of 313 poses (19.5 %); moved over the shell, (-60, -20, 700), in 8 (2.6 %); off to the +Y side, (20, 300, 600), in none. The scene offers the three places, a badge when a cord crosses the line (the drawn rods are thicker than the real 1 mm cords and stay non-occluding; the test uses the true segments).

**What stays uncertain.** The second camera's own calibration; whether the spot centroids to 0.1 mm on stainless (I have not seen it); the surface's place in the cage frame. Your question ("what does the beam land on for a pose 25 mm from the corner, and which observer sees the nozzle?"): with the nozzle tip in the bore the beam lands on the plate near the wall or on the wall's face, and a board on the rotator (or the plate itself, if its plane is registered) is the cleanest surface because it is one plane; camera B of room-05 sees the nozzle from the far side of the bore. A phone photograph of the dot on the plate at 30 cm would say whether it centroids.

---

## 2. room-03 wall port: the rod bends more than the ball plays

**What I did: revised the scene and the idea; adopted `eyes-14-wall-as-window`; the ball's stick-slip is left standing.**

**Re-derived first.** F = 1.47 kg x g x sin 45 degrees + 2 N = 12.2 N at the dot end, d 400 mm, Lt 800 mm, aluminium tube 20 x 2 mm, E 69 GPa, tail point held (`calc/rod-under-tilt.mjs`, my own closed form: dot off the line = F d^2 (d + Lt) / 3 E I): tip flex 0.81 mm, tilt at the ball 4.07 mrad, **2.44 mm at the dot**. Your 2.4 holds. By rod: 25 x 2 mm 1.18 mm; 38 x 3 mm 0.22 mm; 1 N of cable pull moves the dot 0.20 mm at 20 x 2 and 0.02 mm at 38 x 3.

**The assumption behind it.** Mine: with the counterweight the rod carries no load and is a stiff line. The counterweight balances the actuators, not the rod: the moment F d passes through the ball and bends both segments.

**What changed.** `room-03-wall-port`: an OD slider (default 38 x 3, the 1-1/2 in tube), the bend panel with the rod drawn as a beam and the sideways scale stretched (autoscaled, with a scale bar), a rod-bend readout and one for the dot shift per newton of cable pull, the counterweight now includes the rod's own weight, and the I/O panel lists what only this arrangement can have: scales or an inclinometer on the lid frame (they see the ball's play, which step counts cannot), a load cell or motor current at the tail actuators (F d / Lt for a beam model to subtract), an IMU on the tail (your eyes-11). Also fixed: the zoom window sat on top of the cabinet in the elevation and hid the rod; it now has its own row. The first fix is a stiffer rod, not a better ball.

**Your two questions.** *What does the tail actuator hold?* A point: the tail end at its commanded place; the tangent at the ball then tilts. Whether a real actuator pair holds a point or a tangent is a design choice; the panel assumes a point. *What rod is meant?* A 38 x 3 mm tube or stiffer, so that the ball's play (0.075 mm at the dot) is not the smaller term. Sourcing shows the catch (`sourcing/room.md` 25): the Prime tubes of that size are 12 to 13 in long; the one 4 ft round tube I found has a 0.083 in wall, a quarter less stiff than 3 mm (0.29 mm instead of 0.22).

**A larger way out, from the new direction.** The gravity part of the bend is the gun's weight *across* the rod. With the tube tipped 30 degrees and the gun in the radial plane (room-17), the barrel and the rod are plumb; only the centre of mass's 23 mm offset remains. Same beam: 0.59 mm at 20 x 2 and 0.05 mm at 38 x 3 with the cable's 2 N still acting; tipping alone with the reference gun leaves 1.95 mm and 0.18 mm. Named in the idea file (item 10), not drawn.

**What stays uncertain.** Ball stick-slip and real clearance (left standing); the real gun's length and grip lever (the model puts the load at the dot end, upper bound for the gravity part, lower bound for the cable's lever); the rod's end clamps; whether the outside scales' 0.06 mm accuracy (no data output listed) is enough.

---

## 3. room-05 drawer cell: B reads "blocked" because of a default, and A and B are the pair

**What I did: revised the scene (a mistake of mine); answered your two questions; branched the station part into `room-18-cabinet-station`.**

**The conflict.** In my scene camera B ("rim height, sees the nozzle") reads *blocked by gun*. You traced it to `markVisibility('B', gun.local('nozzleTip'))` with the default 0.8 mm end tolerance on a point on the axis of a thin part. I reproduced it: with eps 3 B reads the tip over the rim (5.0 mm) from the far side of the bore. **It was a default, not a judgement.** Fixed in `room-05-drawer-cell` (and room-01's side camera, same call).

**The assumption behind it.** That B and A are two ways of seeing the same thing. They are complementary (A: where the beam lands; B: where the nozzle is along it), which is exactly what item 1 needs.

**Your profile station.** I drew both: a radio moves B between the far side of the bore (as first drawn) and the profile place beside the station (az 90, 330 mm, 12 mm above the rim). Both read the tip. The profile place is on the drawer's own path: the drawer travels 420 mm along +Y with the tube on it and would reach a camera at y = 330; the scene raises a limit badge. So the far side stays the default; the profile view would need the camera on a side post outside the tube's footprint.

**Your questions.** *Was "blocked" a judgement I meant?* No: the default. *If B is the nozzle-height camera, is the wire tip allowed to cross its view?* It should not, for the tip to be read against the rim; the wire tip is not an occluder in the drawn scene, so that is not tested here (left standing: it needs the real wire bracket's geometry, which nobody has). The I/O table now lists nozzle height as seen and the drawer stroke as an observing stroke, as you noted: the rim passes the fixed camera before the dock seats it.

**The cabinet as a designed light environment.** You named it a thin region and I take it as a branch: `room-18-cabinet-station` (see section 6): a matte interior, a red band-pass on A, switchable lamps, a map of where a lamp's plate reflection and the corner's double bounce land in camera A, and, which no one had drawn, what argon does in a sealed box.

**What stays uncertain.** Glare on the far rim; whether the tip is read against the rim edge as cleanly in a photograph as in the drawn scene.

---

## 4. room-08 observe-only frame (sketch, no scene): the forearm, the tags, the bead

**What I did: accepted the repair and drew it: `room-08-observe-only-frame` (new scene); idea file rewritten to "developed".**

**The four points.**
1. *A frame camera sits above the tube.* My wave-1 reading, from the top camera of room-01, and wrong for the frame: overhead loses vertical sensitivity at the zenith, and only 29 % of the dome both sees the dot and separates radial from vertical error (your eyes-02). The three cameras now sit at 130, 170 and 205 degrees round the tube from the station (up 45, 22 and 10 degrees), on the side away from the hand, with left- and right-hand presets.
2. *The operator's forearm is an occluder.* In the scene it is a cylinder (76 mm across, leaving the grip base 20 degrees below horizontal toward the operator) plus a hand block, drawn as a compliant part because the kit's ghost, sensor and laser roles never occlude. Driving the operator round the tube: at 90 degrees (the +Y side) two of the three cameras lose the dot; at 0, 180, 250 and 300 degrees all three keep it. That reproduces your 6 to 10 points from the +Y side and the "never loses an eye" for the far-side stations.
3. *Tags on a hand-held shell.* On the barrel top and housing back, not the grip. A finding of the scene: at 520 mm and a 26 degree field of view only the barrel tag is in frame; the housing-back tag is 230 mm from the dot and needs about 50 degrees to share the frame with it (1920 px across 485 mm is 0.25 mm per pixel). The scene's field-of-view slider defaults to 50.
4. *During the bead the frame sees the process.* Two recordings, the dry dot and the bead, the second exposed for the process glow with an ND filter. The scene's *Trigger held* switch draws the glow and says what is unknown.

**What stays uncertain.** A real forearm, sleeve, head and the wire feeder; glare; whether one sensor can do both recordings.

**Your questions.** *From which side does Derek stand, and does the frame work for either hand?* I do not know; the frame carries both presets and the scene shows which side costs cameras. *With the trigger held is the red dot still visible?* Unknown; the manual does not say. Both are a minute at the machine (needing Derek's observation).

---

## 5. room-09 move-only shelf (sketch), with room-01's side camera: the number can be read from a picture

**What I did: adopted `eyes-16-measure-the-tube-first` and the room-01 correction; answered your question with a rule.**

**The room-01 loose end.** My I/O table said the side camera is blind to the plate depth. In the scene the corner is hidden below rim + 13 mm (blocked by the rim at 10 and 12, by the table below that) and seen from rim + 14 mm; the default was rim + 16. I confirmed it (heights 8, 12, 14, 16, 30, 60 mm) and changed the default to rim + 30, added a height slider, and let the I/O table report the depth as a difference of two edges in one frame (illustrative noise 0.03 mm).

**Your rule** (a difference between two features in one frame, not the position of one; the tube's own inner diameter as the ruler) is what makes a PTZ camera usable here: 0.1 degree of pointing error is 0.86 mm at the far wall and cancels in the difference. I take it as room-09's stored recipe: the shelf takes a per-tube number written at loading, and `room-07` gains a row for it.

**Your question: would a number written at loading be enough, or does the shelf need the depth again after the tack?** Read it again after the tack. The number at loading predicts; the frame after the tack decides, because the tack can move the plate by a fraction of the slip clearance (0.127 mm wide) and nothing else holds it; a second frame costs seconds and no motion. **And your other question, a phone photo across the bore 10 to 15 degrees above the rim: could it show the corner edge on a real tube?** I cannot say; it is the first thing worth doing (see the list at the end).

**What stays uncertain.** Whether the plate-wall corner is a clean edge on stainless (glare, the slip gap, a burr or a tack), the plate's lateral offset and tilt, and PTZ repeatability, which no listing gives.

---

## Other things you saw, and what I did

- **room-02, three foot contacts as a pose sensor.** Added to the idea's software list (height, pitch and roll by touch; load balance says which way the umbilical pulls).
- **room-04, a dry lap with a stripe on the fibre.** Added to the idea file: the twist of 380 degrees of wrap is the idea's open problem and the stripe costs a marker pen. Not built.
- **room-07, an observer-noise row.** Done: the software-calibrated rows take the observer's cost (0.11 / 0.4 / 0.135 / 0.11 mm) and a depth-from-a-picture input (0.03 mm) replaces the plate-seat-depth term. The scene is now tagged as a lens (room-13 already was).
- **Combinations you named.** room-06 + room-05 (adopted, item 1); room-03 + eyes-14 (adopted, item 2); room-03 + eyes-11 and room-03 + room-06's calibration (named in room-03's idea file as parts of the idea); room-08 + eyes-15 + eyes-02 (item 4, drawn); room-09 + room-01's side camera + use-03 + eyes-16 (item 5); eyes-07 (the sectioned tube) as ground truth for the corner edge: left as a named test, not drawn.

## Also fixed while I opened everything as someone who had not read my notes

room-03's zoom window hid the rod; room-12's *Wire fused in the bead* toggle changed nothing you could see unless the plunge was out (the fused wire is now drawn whenever the exception is on) and its *Seat column section* radio changed only numbers (each section now has its own column); room-07 and room-13 scene-meta tags say "lens".

## The new direction, in three lines (for whoever reads this next)

`room-16-which-way-is-down` (a lens on tilting the work about the seam's tangent), `room-17-tipped-tube` (the arrangement that uses it: the tube tips 30 degrees on a hinged plate, the gun is plumb with the wire off it) and `room-18-cabinet-station` (room-05's cabinet with extraction, argon, lamps and a hand port). The finding that matters to your framing: **tipping does nothing for the cameras** (the cone turns, it does not grow; a far-side bench camera loses the corner by 9 degrees of tilt); it helps the gun (a plumb barrel: weight moment 0.33 against 2.1 N m) and it costs the argon pocket, the printed race's margin and the wire's alignment. The camera map of room-16 is in your terms: the corner sees only toward the bore and over the far rim, and gravity decides which of those directions are places a camera can stand.

## Needing Derek's eyes (each cheap)

1. A phone photograph across the bore, 10 to 15 degrees above the rim, of a real tube: is the plate-wall corner a clean edge on stainless? (rooms 05, 09, 01)
2. With the trigger held, does the red dot stay on? (rooms 03, 08)
3. A photograph of the dot on the plate at 30 cm: how large is the spot, does it centroid? (room 06)
4. Which side does he stand, and which hand holds the gun? (room 08)
5. A coupon welded by hand on an incline (plate tipped 30 degrees, seam level): does the melt care? (rooms 16, 17)
6. The plate's stainless corner under a phone flashlight beside the phone and from the side: how specular is it? (room 18)
7. Plate seat depth on a dozen tubes, rim to plate face. (rooms 01, 05, 09, 15)
