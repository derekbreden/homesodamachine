# trials-22-reference-pucks: the calibration set rides the same seats as the tubes

Scene: `scenes/trials-22-reference-pucks/index.html` (deep). Origin: combination and branch of `trials-01-puck-swap` and `trials-05-artefact-ladder`, with `datum-19-plate-as-target` (the rim and ports fit), `datum-15-dock-noticing` (the coupon) and `datum-17-yardstick-on-the-twin` (the clear twin). Wave 3, the new direction "calibrating the observation itself". Calc: `calc/reference_pucks_fit.py`, `calc/lens_from_pucks.py` (the scene runs the same Fisher analysis in the page). Sourcing: `sourcing/trials.md`, wave 3.

## Picture it

Beside the rotator stands a rack of six pucks that look like tubes standing on printed flanges. One has a checker grid inside a short wall ring: a printed corner. One is a real 316L corner with nothing printed. One has a window sawn in its wall, one a clear wall over a printed plate, one is a real tube kept as the reference, and the last is the next tube. Each drops onto the same three pairs of dowels as any tube. After a knock, at the start of a session, or between tubes on a schedule, the AI has the board swapped in, parks the gun, reads one frame, and knows where its camera stands against the frame every tube shares.

## The proposal

The artefact ladder of `trials-05` puts its board, coupon, notch tube and zoo on the rotator "by hand", wherever the hand puts them, on a pedestal. Put each rung on a puck (`trials-01`) and three things change.

1. **The target is in the tube's frame.** The seats fix the puck in all six freedoms to about 10 micrometres per landing, so the board's printed grid, its seam ring and its ports are at the tube's coordinates to about 20 micrometres laterally and 4 vertically at the seam (first order; `calc/swap_budget.py`). A camera calibrated on the board is calibrated for the next tube, with that much added.
2. **The board carries what a tube carries.** It has a short wall ring at the real rim height (inner radius 61.85 mm, outer 63.5, 6.35 mm above the plate), the two ports (11.1 mm across, 19.05 mm either side of the axis) and, on the plate, a dense grid, the seam ring and grey patches. The rim-and-ports fit of `datum-19` therefore runs unchanged on the board and on a tube; the board's version has a grid to make it well conditioned and no glare to spoil it.
3. **The tube's own fit gets a prior.** With the camera's pose taken from the board, the next tube's rim and ports need to say only how deep this tube's plate sits: seat depth to 0.05 mm at a camera 300 mm up, where the pose-free fit gives 0.12 (numbers below).

The six pucks and what each is for:

| puck | what the AI reads from it | what it cannot say |
|---|---|---|
| board (matte, printed) | camera pose against the puck frame; scale (the printed pitch, measured once); lens; exposure curve for a matte dot; the dot's place in the gun (the pivot or fixed-point trial, `trials-19`) | glare, real finish, anything about a tube |
| coupon (real 316L corner) | the dot's knee against its stored value at the trial's own station: a change detector for everything but the tube (bench clamp, positioner scale over the travel, the dot in the shell, the camera) | which link moved; a tube's seat depth |
| notch (34 degree window) | camera B sees the dot against the plate edge: the judge's gain by jogging the dot to known offsets | a full lap |
| clear twin | truth through the wall at every azimuth: the hand's true error on a printed plate, the judge's bias against angle | glare on polished steel, fume, a hot bead |
| golden tube | the whole dry cycle against a stored trace (`use-12`) | which link moved |
| the next tube | the work: rim and ports per frame, with the board's pose as a prior | anything about the eye a board would say alone |

## What carries the loads, what establishes position, what stays free or restrained

- Carries: the three ball-and-dowel seats and the printed turntable carry each puck (`trials-01`, whose open question on turntable stiffness stands). The gun is not carried here; it stands at the corner, or is parked in the dock (`trials-02`) for a board run.
- Establishes position: the seats (the puck), the printed grid measured once (the ruler), the rim and ports (the tube).
- Free / restrained: a puck is fully restrained when seated and free in the swap; the camera is fixed (or a PTZ, whose pointing the per-frame fit makes irrelevant, `eyes-16`).

## What software could command, observe, and what stays manual

- **Command:** which puck is on the rotator (a swap by a hand or a gripper, `trials-07`), the gun to the corner or parked, the rotator, the fit.
- **Observe:** camera pose against the puck frame from the board's features; how many fiducials the gun hides; the tube's seat depth from its rim and ports with the pose known; the coupon's knee against its stored value; the twin's outside view of the dot; the rim-and-ports residual on every frame, which flags a knock.
- **Manual:** making and measuring the printed board once (calipers or the Revopoint scanner); swapping a puck (a person's minute today, illustrative); keeping the coupon and the golden tube clean.

## What was tried to break it

Numbers from `calc/reference_pucks_fit.py` and `calc/lens_from_pucks.py` (linearised, 0.15 pixel feature noise, 1500 pixel focal length, correspondences known) and from the scene; sizes are illustrative.

1. **A target that is not in the tube's frame calibrates the wrong thing.** *Assumption:* a printed board lying on the rotator is where the calibration needs it. *Change:* on the seats the board's frame is the puck frame, and a calibration made on it transfers to any tube puck with 20 micrometres lateral and 4 vertical added (10 micrometres per landing). *Left standing:* whether printed seats in a printed turntable hold that repeatability over hundreds of swaps (`trials-01` item 5).
2. **What the board buys over the tube alone.** Camera 300 mm up: the seam's image is predicted to 6 micrometres from the board (157 of its 169 fiducials visible with the gun at the corner, all with it parked) and to 25 from a tube's rim and ports alone; the tube's seat depth is 0.115 mm alone and 0.051 mm with the board's pose as a prior (allowing 0.05 mm and 0.005 degrees of drift since). At 450 mm: 0.26 alone, 0.07 with the prior. At 150 mm the tube alone already gives 0.03, so the board is worth most for a camera that stands far off. *Assumption behind `datum-19`'s 0.35 mm at 300 mm:* each port is a point. A port is an 11.1 mm circle; fitted from 8 edge points each it lowers the pose-free depth to 0.115 mm (the same model with ports as two points reproduces datum's 0.335). *Left standing:* 0.15 pixel is a clean matte edge; at 0.5 pixel every number here is 3.3 times larger.
3. **A flat board cannot separate focal length from height, but the station does not care.** With the rim ring and a grid across the field a flat board puck pins a point 62 mm off the axis to 7 micrometres with the distortion free; focal length and height trade (sigma 0.5 per cent and 1.5 mm) and leave that point where it is. A board tilted 10 degrees (a wedge puck, one more print) halves both (0.25 per cent, 0.76 mm, 5 micrometres). What depends on the height itself is the rim edge's parallax: 6.35 times r over H squared times 1.5 mm is 6 micrometres. So the wedge puck is optional and kept as a sketch. *Left standing:* distortion (a typical M12 lens: k1 near minus 0.1) is a property the flat board finds and a comparison in a tight frame never needs.
4. **The board is matte and the tube is not.** *Assumption:* a target that is easy to see calibrates what a hard target hides. *Change:* it does not; that is what the coupon puck (real steel, a known corner, nothing printed) and the golden tube are for. The coupon at the trial's own station also sees the bench clamp and the positioner's scale, which the dock coupon of `datum-15` (gun and camera only) cannot. *Left standing:* whether a 316L coupon looks like the tube (the same finish); glare is the one thing the board cannot supply.
5. **The gun hides part of the board.** With the gun at the corner the barrel stands in front of 12 of the board's 169 fiducials (5 of a tube's 64); the scene draws a line of sight, not optics. The loop parks the gun in the dock for a board run, which is why this idea and `trials-02` belong together.
6. **The printed scale is the ruler.** A laser printer scales a page by tenths of a per cent; the grid pitch is measured once (calipers, or the scanner) and stored, or its error becomes every later scale error (1 per cent is 3 micrometres on the knee, 23 on a rim-edge reading, 190 against the ports and 620 against the room: `trials-24`). *Left standing:* a plain printed sheet on a flat disc, or a printed plastic board (the printers do 0.1 mm features): which is flat enough is untested.
7. **The pose is not the reading.** A knock of 0.2 degrees at 300 mm moves the whole picture 1.05 mm; the rim-and-ports fit flags any shift above about 3 sigma of the station prediction (16 micrometres at the defaults), so a knock of 0.01 degree (0.05 mm) is flagged and 0.003 degree (0.016 mm) is below the noise. A comparison made against the wall in the same picture is unchanged by the knock. *Left standing:* pixel noise on real glare.

## Branches and combinations

- Branch and combination of `trials-01` (the seats and swap) and `trials-05` (the rungs). The clear twin is `datum-10`/`datum-17`'s instrument as a puck; the coupon is `datum-15`'s as a puck at the trial's station; the board's fit is `datum-19`'s.
- Feeds `trials-24` (which puck the AI reaches for after which event), `trials-19` (the fixed-point trial runs on the board puck), `trials-18` (the steerable pointer on the coupon puck gives the golden dot), `trials-11` (the yardstick's first entry on the twin), `use-12` (the golden tube).
- Sketch, not drawn: a wedge puck (a board tilted 10 degrees) for the lens; a puck with a fibre-optic light guide that puts a slate in a close-up (`trials-23`).
- Transferable: a printed target with the tube's own fiducials on the tube's own seats; a pose prior that turns a rim edge into a depth gauge; a coupon at the trial's station rather than beside it.

## Unresolved problems and questions that need Derek

- Q (from `datum-19`, still the cheapest photograph): a phone picture of the bore from 300 mm and from 150 mm straight above: are both rim circles and both ports sharp, and does the wall's inner face show as a strip? A steel plate under bench light says more than any number here.
- Q: measure a printed sheet against calipers: how far off is the grid pitch over 100 mm? (If it is 0.3 per cent, the ruler has to be measured.)
- Q: ten lifts and re-seats of any puck-shaped print with the indicator on the flange: is 10 micrometres per landing believable? (`trials-01`.)
- Q: are there scrap tube ends for a coupon and a notch puck? (`trials-05`.)
- Whether a swap is a minute of a person's time or a gripper's, which sets the schedule.

## Assumptions

Tube, rim ring, ports and recess **[repo]**; pinhole camera, 1500 px focal length, 1280 by 960, straight down over the axis, feature noise, correspondences and drift **[illustrative]**; seat effect first order from 10 micrometres per landing **[derived]**; rack and puck outlines **[illustrative]**; the twin's refraction (0.15 mm at 10 degrees off the wall normal through 2.5 mm of acrylic, `datum-10`) is not drawn.

## Sourcing pointers

`sourcing/trials.md`, wave 3: a light-red bandpass filter for a monochrome camera ($121, thin sales evidence) and cameras with a trigger input (for `trials-23`); the Arducam UVC camera of wave 1 already ships a low-distortion M12 lens (its distortion is a calibration item here). The pucks are printed; the board is printed and measured; the coupon is scrap tube and plate on the band saw **[repo]**.

## Scene

`trials-22-reference-pucks`. Controls: which puck is on the seats (state), gun at the corner or parked (state), rotator (state), camera height, feature noise, camera knock, drift since the last board run and seat repeatability (scene edits). Nothing is an actuator.
