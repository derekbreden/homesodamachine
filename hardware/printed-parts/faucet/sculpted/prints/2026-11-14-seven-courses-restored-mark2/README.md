# Sculpted faucet with short inclined foundations and the restored recipe on Mark2

The [print plate](sculpted-faucet-seven-courses-restored-black-mark2.gcode.3mf) and
[editable project](sculpted-faucet-seven-courses-restored-black-mark2.3mf) hold the complete
black PET-GF faucet with the extended display cover. The [launch receipt](launch.json)
identifies the submitted job, and the [startup spacing](startup-spacing.json) record gives
Mark1's last start before it.

On the base, a level scaffold carries the inclined roof and the part courses parallel to the
mounting face. In each of those courses the show surface's ring is one lap, laid after the
inner rings and fill; in the first course, which bridges the roof's air, it is laid before
them, so the bridge's fill starts on it. It starts and ends at the rear, the slope's low point, and runs the same
way round as the level walls above: it climbs the rim's CAD −x side and comes down its CAD +x
side, which is on the right as you face the faucet. Coming down, the nozzle rides higher by half
the slope's drop across the radius of its flat; it does not rise where the lap climbs, and the
rise follows the slope with no step. The [foundation record](foundation.json) gives the laps and
their most rise.

On the tip, the anchor, plug and support roots start level; the interface and the visible
shoulder follow the bearing plane, and the shoulder's tilted courses lay the mating face. Above
each foundation the level courses keep the
[sloped-underside print's](https://github.com/derekbreden/homesodamachine/tree/c8667107f964589be7dc69f8fb924f69a12729b3/hardware/printed-parts/faucet/sculpted/prints/2026-11-13-sloped-underside-complete-mark2)
wall and rear scarf settings. On the base, and on the tip below its end, the slicer lays walls
at their own speed through its shallow overhang points and slows them from there toward its
steeper points, where the fan comes on; steeper overhangs, bridges and their fan, and the
cover, mounting plate and lever keep the slicer's recipe. [`stage/overhang-scope.py`](stage/overhang-scope.py)
sets that in the slicer's own settings, and the [course record](course-scope.json) reads it
back from the slice.

The tip's end, from the lowest layer the tip-end cooling stage cools to its top, comes from a
slice of the [stopped plate's](https://github.com/derekbreden/homesodamachine/tree/9ebc8ac1b152c1845f673ce2613d9cbbb9f3cd66/hardware/printed-parts/faucet/sculpted/prints/2026-11-14-seven-courses-mark2)
project, so its walls keep the slicer's recipe through the shallow overhang points too. It lays the same beads there, supports included, as this plate's own
slice. The [splice record](tip-end-splice.json) names both slices and the layers taken.

The slice carries the standing slice path's bridge-foundation and tip-end cooling stages. The
bridge-foundation stage lays fresh courses over bridges slower with the part fan on, as on the
sloped-underside print; the [cooling record](cooling.json) gives its recovery moves. The
tip-end stage turns the part fan on over the tip's paths from its dispense face back to just
short of the lip grooves, on both sides, the
[surfaces Derek found rough](https://github.com/derekbreden/homesodamachine/blob/ffe670b3c4a83a970d2e52dd81c75eddb7f12522/hardware/printed-parts/faucet/sculpted/prints/2026-11-12-wing-end-relief-mark1/physical-result/tip-end-surface.json);
the [tip-end record](tip-end-cooling.json) gives the cooled stretch.

Between level course groups the head moves as the slicer's own layer changes do: a spiral up
by the slicer's z-hop over the plastic just laid, the crossing at its travel speed and the drop.
Where a group is tilted, or plastic higher than the group just laid lies under the head, the
transfer keeps the slow lift over all laid plastic. Inside the tip's own courses each crossing
stands only as high as the nozzle and head need over the beads already laid. The plate tells
the printer of each level layer as it climbs, with the layer's progress, its layer-change notice
and a timelapse frame, and once the first layer is laid it turns power-loss recovery on and sets
the regular nozzle temperature without waiting for it. Its percent and time-left come from
the motion estimate, written wherever either changes, as the slicer writes them on its own
plates. The [sequence record](sequence.json) counts the transfers and crossings by kind.

The [motion replay](head-replay.json) and its [approach readings](approaches.json) measure
clearance against the nominal deposited paths. The [estimate](chronology.json) uses the
planner's motion time. The print tests the shoulder and foot joins, the show lap's rear joint
and its descending side, the tip end's surfaces, the support release and the overall finish.

[Reproduce the plate](REPRODUCE.md) with the [retained inputs](run-inputs.zip).
