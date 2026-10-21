# Reservoir adhesion observations

The zero-user-trim Mark1 retry, task **1359909015**, has **reported corner curl
and actual water leakage at many places**. Derek stopped it and identified
the [two photographs](../prints/2026-10-21-mark1-right08-z000/physical-result/physical-result.json)
as that most recent article. A distorted band is visible near the floor-to-wall
transition. Raised material reducing nozzle clearance is consistent with the
reported curl; a [solid-floor-to-wall transition](https://help.prusa3d.com/article/the-benchy-hull-line_124745)
can also create a band. The finished shape does not establish a lift layer.

Live observations through UI layer **526** did not detect the reported curl.
They covered exposed body/cap edges and left shadowed, occluded and reflective
underside contact unassessable. There is no complete attached baseline or
onset bracket. The [terminal record](../prints/2026-10-21-mark1-right08-z000/terminal-observation.json)
records cancellation and a failed final camera Play attempt; it supplies no
final chamber image. The task-bound monitor is **paused**.

Derek reports corner lifting on a previous reservoir, with onset guessed from the
finished shape at roughly layers 20–100. That interval is unverified. The
[investigation](investigation.json) identifies two downloaded Mark2 timelapses and
[the left](2026-10-06-left-contact-sheet.jpg) and
[right](2026-10-07-right-contact-sheet.jpg) sampled frames. The low camera angle,
reflections and cap occlusion prevent a reliable onset bracket. Frame numbers
are not established layer numbers. Full clips remain in the ignored
`.cache/reservoir-lifting/` directory with hashes in the investigation.

Mark1 task 1359853920 has a separate
[first-layer adhesion failure](../prints/2026-10-20-mark1-right08/physical-result/physical-result.json),
reported by Derek and documented in three photographs before removal. The
[retry](../prints/2026-10-21-mark1-right08-z000/README.md) uses zero added user Z
trim for clear PETG. First-layer attachment and later corner lifting are separate
observations; neither alone establishes the cause of the other.

## Live observations

Read the exact Mark1 task, layer, temperatures, fans, timelapse and error/HMS
status through `tools/bambu_printer.py`. Use `cua_repl` for Bambu Studio's Device
view and camera; verify the visible printer name and archive. Connect's device
page has status and filament controls but no live camera. Bambu Studio's camera
must be playing before treating its image as a live observation. In Device,
verify Mark1 at the upper left. If the preview is blurred and says it is
temporarily closed, click the green Play control at the lower left of the
camera image, allow initialization, and confirm changing frames. This method
produced updating startup frames for task 1359909015. If the view is unavailable, record that limit and do not substitute MQTT status for vision.

Examine cap and body separately. Record a repeatable underside-to-bed gap,
upward-curved bottom edge, displaced strand or nozzle contact with UTC/Central
time and exact reported layer. Mark glare or obscured edges unassessable.
Retain the last clearly attached and first clearly lifted observations to
bracket onset. Inspect every five minutes through layer 3, every ten minutes through layer
120, and then every thirty minutes if stable; stop the monitor when this specific task ends or
changes. Ordinary unchanged progress does not need a notification.

## Proposed next trial

The [prioritized options](next-trial-options.json) target corner anchorage,
bead packing/fusion and throughput: a forced 10 mm body brim, flow **1.02**,
**255/260 °C** first/subsequent nozzle temperature, scoped early body cooling,
and a **12 mm³/s** speed trial at the retained 0.24 mm layer height. These
settings are proposed; the saved project and executable recipe remain frozen.

The current native G-code emits no brim despite the saved auto-brim setting.
Its [body cooling paths](body-cooling-paths.json) also show **90% fan commands
on the solid floor and early walls**, including layers 4 and 12–16. This
supports reviewing fan inheritance and supported paths, with higher cooling
retained where bridges/unsupported cap features need it. There is no observed
fan-change-to-lift onset link. [Prusa's warping guidance](https://help.prusa3d.com/article/warping_2011)
supports brim/contact and cooling as candidate controls, not a diagnosis of
this article's cause.

The recovered May 30 water-holding recipe used clear PETG, flow **1.02**,
**260 °C** after the first layer and a **21 mm³/s** ceiling through a 0.6 mm
nozzle. It requested **200/300 mm/s** outer/inner walls; these are requested
speeds, not measured motion. This failed recipe requests 30 mm/s with a
6 mm³/s ceiling. The options record binds the historical project hash and
preserves the accepted September 0.97 results. Exact successful sphere
settings are not recovered, so the May recipe is the quantified comparison.

A proposed 25 mm tall full-footprint body base retains the real floor,
fillets, corners and seam. The options specify a flatness check and one-hour
20 mm water-head screen using existing tools. That screen can reject floor
and lower-wall seepage before another full-height print; a pass does not
qualify the full reservoir, cap/gasket seal or cold service.
