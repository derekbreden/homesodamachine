# borrowed-16-taut-cone: which pulls keep six lines from above taut, and what a bought preload changes

Origin: branch of freedom-03-cable-platform, drawn in wave 2 from `exchange/borrowed--on--freedom-w2.md` (section 2). Maturity: developed. Scene: `scenes/borrowed-16-taut-cone/index.html`.

## Picture it

freedom-03's gun in its shell with six thin lines running to a frame plane overhead, the fibre's pull drawn as an arrow at the grip base. Beside it, a picture of the whole sphere of directions that arrow could point in, unrolled into a rectangle: green where the six lines stay taut at the pull set now, red where a line would go slack. In the shipped layout most of the rectangle is red and the green is a small blob around the direction freedom-03 drew the fibre in.

## The proposal

With six lines for six freedoms and only gravity as preload, the six tensions are fixed by the load (t = -A^-1 w) and are all positive only when the load lies inside a cone of wrenches. Map that cone over the direction of the fibre's pull at the grip base: for each direction, how many newtons before the first line reaches zero ("slack pull"). Three layouts, one clearance rule (32 mm off the barrel and housing): freedom-03's as shipped (searched to be taut for three particular pulls), one searched for the largest worst-direction slack pull with gravity alone, one searched with a constant 10 N downward pull at the grip base. A spring balancer under the bench is a bought source of a near-constant pull (5 to 15 N for the 0.5 to 1.5 kg models).

## What carries the loads, establishes position, is free, restrained or driven

Not moving in this scene. Carried: the lines, in tension, by geometry; the frame carries the lines. Position: line lengths from the frame. Restrained: all six freedoms while every line is taut; the moment one slackens, one direction of one motion is free. Driven (freedom-03): six winches; (freedom-09): none.

## Software: command, observe, manual

- Observe: six line tensions (motor current or load cells): the smallest is the margin to slack.
- Manual: laying the fibre so its pull stays inside the cone; hanging the balancer for the preload layout.
- Command: nothing in this scene.

## What was tried to break it

1. **With gravity alone two lines carry 0.3 N.** In the shipped layout the tensions from gravity are 3.6 / 3.8 / 2.8 / 0.3 / 0.4 / 4.8 N. Set freedom-03's scene to 0 N of pull: the panel reads "all taut" with lines 4 and 5 at 0.1 and 0.2 N.
2. **The worst direction slackens a line at 0.13 N.** Over 6000 sampled directions: 58 % slacken a line below 1 N, 82 % below 4 N, 96 % below 8.7 N (freedom-15's top of the range at 240 mm). Along the exit axis blended down it holds to 5.5 N (droop 0), 6.4 (0.5), 6.8 (1). Assumption: gravity is the preload and the fibre pulls along its exit. The layout search optimised for three vectors. **The worst case is a sphere-wide number**: over a cone of pull directions around the drawn exit (droop 0.5, `calc/w2-cone-check.cjs`) the shipped layout's minimum slack pull is 4.2 N within +-15 degrees, 1.6 N within +-30 and 0.39 N within +-45. It is a good layout for a fibre whose direction is known to +-15 degrees and a fragile one for a fibre whose direction is not.
3. **A robustness search gains a factor of twenty in the worst case, and loses at the drawn direction.** Same lugs, same clearance rule, objective the largest worst-direction slack pull: 2.6 N with gravity alone (no direction below 2 N; 55 % of directions below 4 N), from sixteen million random tries: not an optimum. Within +-15 degrees of the drawn exit direction it holds 3.0 N against the shipped layout's 4.2 N; at +-30 degrees it wins (2.7 N against 1.6 N). It buys robustness to an unknown direction, not margin at a known one.
4. **A preload only helps a layout made for it.** 10 N down at the grip base takes the shipped layout to two slack lines (-0.9 and -1.3 N). A layout searched for it gives a worst-direction slack pull of 4.75 N and no direction below 4 N, with line tensions up to 8.9 N with no fibre pull. 76 % of directions still slacken a line below 8.7 N.
5. **Real cable robots close the loop from below.** Hangprinter-class machines pull the effector with lines on both sides; six lines from above are the minimum and their taut set is a cone.

## Branches and combinations

- With freedom-15: the map is what turns one measured number and one direction of the fibre's pull into a check against a layout.
- With borrowed-11 / travel-08: a designed cable route makes the pull cone a design input.
- With freedom-01c: the balancer is a constant-force element (one master per axis), here a preload on no axis in particular.

## Unresolved problems and questions that need Derek

- The fibre's pull direction and size at the working pose, and at bead start (Newton meter along and across the exit; a photo of the route).
- The shell's mass and centre of mass (a thread at two points).
- Whether the balancer's line can reach the grip base past the tube and the bench; its friction and stroke.

## Assumptions

- Illustrative: shell and gun 1.2 kg, COM (0, -18, 178) local, freedom-03's lug positions and clearance rule, frame 600 mm above the bench, pull point at the grip base, preload straight down there. Rigid lines at the reference pose (no stretch, friction or pulley). The layouts' directions are in the scene and in explorers/borrowed/calc/w2-robust-layout.json; searches: calc/w2-robust-layout.cjs; checks on 6000 directions: calc/w2-verify-layouts.cjs and calc/w2-taut-set.cjs. The scene's default reproduces freedom-03's tensions and slack pull at 2 N.
- Hangprinter's line-buildup and flex compensation, and opposing lines, are from the project's documentation via search: unchecked.

## Sourcing pointers

sourcing/freedom.md and sourcing/borrowed.md: Tigon TW-1R spring balancer (0.5 to 1.5 kg, $39.00, Prime).

## Scene

`borrowed-16-taut-cone`
